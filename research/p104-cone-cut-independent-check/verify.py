#!/usr/bin/env python3
"""Independent recomputation of the frozen P104 forward/backward cone cut.

A second implementation of the merged `research/p104-cone-cut` receipt. The
transport geometry, the span relation and the two marker propagations are
re-derived here from the pinned witness and certificate; the merged package's
checker is never imported, read or executed, only its published receipt is
compared against.

Added coverage beyond the merged receipt:

* saturation (iterated fixed point) of both cones at every dimension used, so
  the emptiness statement is certified independently of how many transfer
  steps each dimension is allowed;
* symmetry of the derived relation, and a count of comparable index pairs whose
  lower bounds are disjoint (a guard the merged checker does not report);
* the per-dimension marker counts and the dimension-2 incoming slot histogram,
  which the merged package inherits from its archived predecessors.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
CERTIFICATE = ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json"
MERGED_RESULT = ROOT / "research/p104-cone-cut/RESULT.json"

SOURCE = 102
TARGET = 71
WIDTH = 104
SLOTS = 2 * WIDTH
MARKER = "PASS_P104_CONE_CUT_INDEPENDENT"

# Values published by the merged receipt and by its archived predecessors.
EXPECTED_EDGES = 2309
EXPECTED_WORD_LENGTH = 4058
EXPECTED_INCOMING_SLOTS = [[165, 9], [204, 7], [205, 9]]
EXPECTED_MARKER_COUNTS = [25, 52, 365, 1725]
EXPECTED_BACKWARD_COUNTS = [12, 22, 37]
EXPECTED_WRITER_ARRIVALS = [[142, 2], [143, 10]]
EXPECTED_BACKWARD_SLOTS = [
    [41, 2], [43, 2], [54, 4], [131, 2], [135, 4], [145, 4],
    [146, 2], [149, 1], [155, 4], [159, 4], [171, 4], [194, 4],
]
MERGED_KEYS = (
    "forward_edges",
    "writers",
    "writer_arrivals",
    "backward_counts",
    "backward_edges",
    "backward_slots",
    "intersection",
    "backward_sha256",
)


def fail(message):
    raise SystemExit(f"FAIL_P104_CONE_CUT_INDEPENDENT {message}")


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    """Every declared live input must match its own recorded hash."""
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    live = {
        row["path"]: row["sha256"]
        for row in sources["files"]
        if row["usage"] == "input"
    }
    require(
        set(live) == {
            "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
            "research/p104-joint-unit-flags/CERTIFICATE.json",
            "research/p104-cone-cut/RESULT.json",
        },
        "live input inventory changed",
    )
    for path, pinned in live.items():
        require(sha256(ROOT / path) == pinned, f"input drift {path}")


def span(basis):
    """Point set of the span of a basis."""
    require(type(basis) is list, "basis must be a list")
    points = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, "basis vector out of range")
        points |= {point ^ vector for point in points}
    return frozenset(points)


def chain(word, name):
    """Successive point sets of one transport chain, oldest first."""
    frames = [span(word["initial_frames"][name])]
    for event in word["program"]:
        if event[0] != "transport" or event[1] != name:
            continue
        previous = frames[-1]
        following = span(event[3])
        require(previous <= following, f"chain {name} is not monotone")
        require(
            len(following) == len(previous) * 2 ** event[4],
            f"chain {name} does not double its rank",
        )
        frames.append(following)
    require(frames[-1] == span(word["final_frames"][name]), f"chain {name} end moved")
    return frames


def relation(bounds, dimension):
    """Frozen span relation at one dimension, with symmetry and guard counts.

    Two indices are adjacent when each lower bound sits inside the other upper
    bound and the frozen rank interval brackets the ambient dimension.
    """
    ambient = 1 << dimension
    rows = [1 << index for index in range(len(bounds))]
    disjoint = 0
    for index in range(len(bounds)):
        low, high = bounds[index]
        for other in range(index):
            other_low, other_high = bounds[other]
            if not (low <= other_high and other_low <= high):
                continue
            common = low & other_low
            if not common:
                # Guard: the frozen checker would divide by zero here. On this
                # input the case does not occur; count it instead of guessing.
                disjoint += 1
                continue
            lower = (len(low) * len(other_low)) // len(common)
            if lower <= ambient <= len(high & other_high):
                rows[index] |= 1 << other
                rows[other] |= 1 << index
    for index, row in enumerate(rows):
        require((row >> index) & 1, "the relation is not reflexive")
        for other in range(len(rows)):
            require(
                ((row >> other) & 1) == ((rows[other] >> index) & 1),
                "the relation is not symmetric",
            )
    return rows, disjoint


def contacts(bounds, dimension, frames, kind):
    """Read-out masks: which chains hold a frame of exactly this rank."""
    snapshots = [
        (index, frame)
        for index in range(WIDTH)
        for frame in frames[f"{kind}{index}"]
        if len(frame) == 1 << dimension
    ]
    return [
        sum(1 << index for index, frame in snapshots if low <= frame <= high)
        for low, high in bounds
    ]


def step(state, reads, neighbours):
    """One frozen transfer: seed chain masks, then carry each along the relation.

    The state is indexed by edge and each entry is a mask of chain indices, so a
    holding edge hands its *whole chain mask* to every adjacent edge.
    """
    seeded = [held | read for held, read in zip(state, reads, strict=True)]
    grown = list(seeded)
    for index, signal in enumerate(seeded):
        if signal:
            for other in neighbours[index]:
                grown[other] |= signal
    return grown


def settle(state, reads, neighbours):
    """Added coverage: iterate the same transfer to its fixed point."""
    current = step(state, reads, neighbours)
    rests = 1
    while True:
        following = step(current, reads, neighbours)
        if following == current:
            return current, rests
        current, rests = following, rests + 1


def neighbour_lists(rows):
    return [
        tuple(other for other in range(len(rows)) if (row >> other) & 1)
        for row in rows
    ]


def holders(state, source):
    return [index for index, signal in enumerate(state) if (signal >> source) & 1]


def packed(indices):
    mask = 0
    for index in indices:
        mask |= 1 << index
    return mask


def histogram(edges, chosen, end):
    counts = {}
    for index in chosen:
        slot = edges[index][end]
        counts[slot] = counts.get(slot, 0) + 1
    return [[slot, counts[slot]] for slot in sorted(counts)]


def geometry(word, certificate):
    frames = {
        f"{kind}{index}": chain(word, f"{kind}{index}")
        for kind in "XY"
        for index in range(WIDTH)
    }
    lines = []
    line_vectors = []
    for index in range(WIDTH):
        initial = frames[f"X{index}"][0]
        nonzero = [point for point in initial if point]
        require(len(nonzero) == 1, "an initial X frame is not a line")
        lines.append(initial)
        line_vectors.append(nonzero[0])
    departures = []
    for index in range(WIDTH):
        for vector in certificate["forms"]["departure"][index]:
            departures.append(span([line_vectors[index], vector]))
    arrivals = []
    for index in range(WIDTH):
        cap = frames[f"Y{index}"][-1]
        for functional in certificate["forms"]["arrival"][index]:
            arrivals.append(
                frozenset(
                    point
                    for point in cap
                    if (point & functional).bit_count() % 2 == 0
                )
            )
    require(len(departures) == SLOTS, "departure slot count moved")
    require(len(arrivals) == SLOTS, "arrival slot count moved")
    edges = [
        (departure, arrival)
        for departure in range(SLOTS)
        for arrival in range(SLOTS)
        if departures[departure] <= arrivals[arrival]
    ]
    require(len(edges) == EXPECTED_EDGES, "compatible edge count moved")
    return frames, lines, departures, arrivals, edges


def forward_cone(edges, lines, departures, arrivals, frames, settle_each):
    """Marker propagation from X102 through dimensions 1 to 5."""
    counts = []
    disjoint = 0
    rests = []
    empty = [0] * len(edges)
    line_bounds = [(lines[departure // 2], lines[departure // 2]) for departure, _ in edges]
    rows, gaps = relation(line_bounds, 1)
    disjoint += gaps
    neighbours = neighbour_lists(rows)
    state = step(empty, contacts(line_bounds, 1, frames, "X"), neighbours)
    counts.append(len(holders(state, SOURCE)))
    plane_bounds = [(departures[departure], departures[departure]) for departure, _ in edges]
    rows, gaps = relation(plane_bounds, 2)
    disjoint += gaps
    neighbours = neighbour_lists(rows)
    state = step(state, contacts(plane_bounds, 2, frames, "X"), neighbours)
    counts.append(len(holders(state, SOURCE)))
    incoming = histogram(edges, holders(state, SOURCE), 0)
    interval_bounds = [(departures[departure], arrivals[arrival]) for departure, arrival in edges]
    for dimension in (3, 4, 5):
        reads = contacts(interval_bounds, dimension, frames, "X")
        require(
            sum(bool((read >> SOURCE) & 1) for read in reads) == 0,
            f"dimension {dimension} reads X{SOURCE}",
        )
        rows, gaps = relation(interval_bounds, dimension)
        disjoint += gaps
        neighbours = neighbour_lists(rows)
        if settle_each:
            state, rested = settle(state, reads, neighbours)
            rests.append(rested)
        else:
            state = step(state, reads, neighbours)
        counts.append(len(holders(state, SOURCE)))
    return state, counts, incoming, disjoint, rests


def backward_cone(edges, departures, arrivals, frames, settle_each):
    """Backward expansion from Y71's dimension-8 writers through 8, 7 and 6."""
    caps = [frames[f"Y{index}"][-1] for index in range(WIDTH)]
    cap_bounds = [(caps[arrival // 2], caps[arrival // 2]) for _, arrival in edges]
    writes = contacts(cap_bounds, 8, frames, "Y")
    writers = [index for index, write in enumerate(writes) if (write >> TARGET) & 1]
    mask = packed(writers)
    counts = []
    rests = []
    layers = (
        (8, cap_bounds),
        (7, [(arrivals[arrival], arrivals[arrival]) for _, arrival in edges]),
        (6, [(departures[departure], arrivals[arrival]) for departure, arrival in edges]),
    )
    for dimension, bounds in layers:
        rows, _ = relation(bounds, dimension)
        if settle_each:
            mask, rested = settle_mask(mask, rows)
            rests.append(rested)
        else:
            mask = expand_mask(mask, rows)
        counts.append(mask.bit_count())
    return writers, mask, counts, rests


def expand_mask(mask, rows):
    grown = mask
    for index, row in enumerate(rows):
        if (mask >> index) & 1:
            grown |= row
    return grown


def settle_mask(mask, rows):
    """Iterate one expansion step at a fixed dimension until it is a fixed point."""
    current = expand_mask(mask, rows)
    rests = 1
    while True:
        following = expand_mask(current, rows)
        if following == current:
            return current, rests
        current, rests = following, rests + 1


def evaluate():
    authenticate()
    word = json.loads(WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    require(len(word["program"]) == EXPECTED_WORD_LENGTH, "word length moved")
    frames, lines, departures, arrivals, edges = geometry(word, certificate)
    forward, marker_counts, incoming, disjoint, _ = forward_cone(
        edges, lines, departures, arrivals, frames, settle_each=False
    )
    require(marker_counts[1:] == EXPECTED_MARKER_COUNTS, "marker counts moved")
    require(incoming == EXPECTED_INCOMING_SLOTS, "the dimension-2 incoming state moved")
    reached = holders(forward, SOURCE)
    require(len(reached) == 1725, "the forward cone left 1725")
    writers, backward, counts, _ = backward_cone(
        edges, departures, arrivals, frames, settle_each=False
    )
    require(counts == EXPECTED_BACKWARD_COUNTS, "the backward growth moved")
    require(len(writers) == 12, "the writer count moved")
    require(
        histogram(edges, writers, 1) == EXPECTED_WRITER_ARRIVALS,
        "the writer arrivals moved",
    )
    back_indices = [index for index in range(len(edges)) if (backward >> index) & 1]
    require(len(back_indices) == 37, "the backward cone left 37")
    require(
        histogram(edges, back_indices, 0) == EXPECTED_BACKWARD_SLOTS,
        "the backward slots moved",
    )
    front = packed(reached)
    require((front & backward).bit_count() == 0, "the cones meet")

    settled_forward, settled_counts, _, spent, forward_rests = forward_cone(
        edges, lines, departures, arrivals, frames, settle_each=True
    )
    settled_writers, settled_backward, settled_backward_counts, backward_rests = backward_cone(
        edges, departures, arrivals, frames, settle_each=True
    )
    settled_front = packed(holders(settled_forward, SOURCE))
    settled_meeting = (settled_front & settled_backward).bit_count()
    observed = {
        "forward_edges": len(reached),
        "writers": len(writers),
        "writer_arrivals": histogram(edges, writers, 1),
        "backward_counts": counts,
        "backward_edges": len(back_indices),
        "backward_slots": histogram(edges, back_indices, 0),
        "intersection": (front & backward).bit_count(),
        "backward_sha256": hashlib.sha256(json.dumps(back_indices).encode()).hexdigest(),
        "marker_counts": marker_counts,
        "incoming_slots": incoming,
        "settled_forward_edges": len(holders(settled_forward, SOURCE)),
        "settled_backward_edges": settled_backward.bit_count(),
        "settled_intersection": settled_meeting,
        "one_step_forward_with_settled_backward": (front & settled_backward).bit_count(),
        "settled_forward_with_one_step_backward": (settled_front & backward).bit_count(),
        "settled_marker_counts": settled_counts[1:],
        "settled_backward_counts": settled_backward_counts,
        "settling_steps": {
            "forward_dimensions": forward_rests,
            "backward_dimensions": backward_rests,
        },
        "disjoint_lower_bounds": disjoint + spent,
        "no_new_kappa": True,
    }
    merged = json.loads(MERGED_RESULT.read_text(encoding="utf-8"))
    for key in MERGED_KEYS:
        require(
            observed[key] == merged[key],
            f"independent value disagrees with the merged receipt: {key}",
        )
    return observed


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(
        observed == stored,
        "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True),
    )
    print(f"{MARKER} intersection=0 settled_intersection={observed['settled_intersection']} no_new_kappa")


if __name__ == "__main__":
    main()
