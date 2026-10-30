#!/usr/bin/env python3
"""Maximal legal entrance of the native event immediately after warp 0.

The backward-capacity rules are the ones proved for this word in PR #3933.
This file recomputes them for warp array index 13. It does not import that
package. No new kappa is claimed.
"""
import copy
import gzip
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE / "vendor"))
import audit_core as audit  # noqa: E402

BASE_SHA256 = "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699"
BILL_SHA256 = "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951"
TARGET = 13
CALLER_FIELDS = (
    "ports", "start_extra", "helper_final", "target_levels", "cut",
    "precondition", "compensation", "centers", "center_frames",
    "initial_corrections", "A", "restore", "removed", "prelude_events",
)


def need(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basis_of(mask):
    out, acc = [], audit.ZERO
    rank = audit.dim(mask)
    for point in range(1, 512):
        if ((mask >> point) & 1) and ((acc >> point) & 1) == 0:
            out.append(point)
            acc = audit.span(tuple(out))
            if len(out) == rank:
                break
    need(audit.span(tuple(out)) == mask, "basis does not span the mask")
    return out


def join(left, right):
    if left & ~right == 0:
        return right
    if right & ~left == 0:
        return left
    return audit.span(tuple(basis_of(left) + basis_of(right)))


def preimage(images, mask):
    acc = 0
    for source, image in enumerate(images):
        if (mask >> image) & 1:
            acc |= 1 << source
    return acc


def terminal_caps(word):
    removed = set(word["removed"])
    end = {}
    for register in range(audit.N):
        if register in removed:
            continue
        if register < audit.V:
            end[register] = audit.FULL
        elif register < 2 * audit.V:
            end[register] = audit.hyperplane(word["ports"][register - audit.V])
        else:
            end[register] = audit.FULL
    for name, frame in word["helper_final"].items():
        end[int(name)] = audit.span(frame)
    return end


def events_of(word):
    at = defaultdict(list)
    for index, record in enumerate(word["warps"]):
        at[record[0]].append(index)
    events = []
    for position in range(len(word["B"]) + 1):
        for index in at.get(position, ()):
            events.append(("warp", index))
        if position < len(word["B"]):
            events.append(("B", position))
    for index in range(len(word["restore"])):
        events.append(("restore", index))
    return events


def maximal_entrance(word, target):
    """Unique maximal legal seed for one warp, with the prefix frozen."""
    cap = terminal_caps(word)
    events = events_of(word)
    start = events.index(("warp", target))
    for kind, index in reversed(events[start + 1 :]):
        if kind == "warp":
            _, lender, columns, entrance, _exit = word["warps"][index]
            allowed = preimage(audit.warp_images(columns), cap[lender])
            need(audit.span(entrance) & ~allowed == 0, "later warp floor fails at " + str(index))
            cap[lender] = allowed
        else:
            gate = word[kind][index]
            allowed = audit.FULL
            for register in audit.touched(gate):
                allowed &= cap[register]
            need(audit.span(gate[-1]) & ~allowed == 0, "scalar floor fails at " + kind + " " + str(index))
            for register in audit.touched(gate):
                cap[register] = allowed
    _pos, lender, columns, entrance, _exit = word["warps"][target]
    allowed = preimage(audit.warp_images(columns), cap[lender])
    original = audit.span(entrance)
    need(original & ~allowed == 0, "original entrance is outside its capacity")
    return allowed


def initial_frames(word):
    removed = set(word["removed"])
    current = {}
    for register in range(audit.N):
        if register in removed:
            continue
        if register < audit.V:
            current[register] = audit.span((word["ports"][register],))
        else:
            current[register] = audit.ZERO
    for name, frame in word["start_extra"].items():
        current[int(name)] = audit.span(frame)
    for gate in word["A"]:
        if gate[0] == "warp":
            current[gate[1]] = audit.span(gate[4])
        else:
            frame = audit.span(gate[-1])
            for register in audit.touched(gate):
                current[register] = frame
    return current


def replay_prefix(word, events, stop, current):
    for kind, index in events[:stop]:
        if kind == "warp":
            _pos, lender, _columns, entrance, exit_frame = word["warps"][index]
            need(current[lender] == audit.span(entrance), "frozen prefix misses warp " + str(index))
            current[lender] = audit.span(exit_frame)
        else:
            gate = word[kind][index]
            frame = audit.span(gate[-1])
            for register in audit.touched(gate):
                current[register] = frame
    return current


def least_assignment(word, target, seed):
    """Least-join frames on the suffix. Returns assigned masks, or None if illegal."""
    events = events_of(word)
    start = events.index(("warp", target))
    current = replay_prefix(word, events, start, initial_frames(word))
    images = [audit.warp_images(record[2]) for record in word["warps"]]
    _pos, lender, _columns, entrance, _exit = word["warps"][target]
    if current[lender] != audit.span(entrance):
        return None
    if audit.span(entrance) & ~seed:
        return None
    assigned = {("warp", target): seed}
    current[lender] = audit.image_mask(images[target], seed)
    caps = terminal_caps(word)
    for kind, index in events[start + 1 :]:
        if kind == "warp":
            lender = word["warps"][index][1]
            entrance = join(audit.span(word["warps"][index][3]), current[lender])
            assigned[("warp", index)] = entrance
            current[lender] = audit.image_mask(images[index], entrance)
        else:
            gate = word[kind][index]
            frame = audit.span(gate[-1])
            for register in audit.touched(gate):
                frame = join(frame, current[register])
            assigned[(kind, index)] = frame
            for register in audit.touched(gate):
                current[register] = frame
    for register, frame in current.items():
        if frame & ~caps[register]:
            return None
    return assigned


def compile_least(word, target, seed, assigned):
    compiled = copy.deepcopy(word)
    images = [audit.warp_images(record[2]) for record in word["warps"]]
    at = defaultdict(list)
    for index, record in enumerate(word["warps"]):
        at[record[0]].append(index)
    current = initial_frames(word)
    out = []
    scales = []
    for position in range(len(word["B"]) + 1):
        for index in at.get(position, ()):
            record = word["warps"][index]
            lender = record[1]
            if ("warp", index) not in assigned:
                entrance, exit_mask = audit.span(record[3]), audit.span(record[4])
                need(current[lender] == entrance, "prefix compile mismatch at warp " + str(index))
                compiled["warps"][index] = [
                    len(out), lender, copy.deepcopy(record[2]), list(record[3]), list(record[4])
                ]
                current[lender] = exit_mask
            else:
                entrance = assigned[("warp", index)]
                exit_mask = audit.image_mask(images[index], entrance)
                need(current[lender] & ~entrance == 0, "entrance would shrink warp " + str(index))
                if current[lender] != entrance:
                    scales.append(lender)
                    out.append(["scale", lender, 1, 1, basis_of(entrance)])
                compiled["warps"][index] = [
                    len(out), lender, copy.deepcopy(record[2]),
                    basis_of(entrance), basis_of(exit_mask),
                ]
                current[lender] = exit_mask
        if position < len(word["B"]):
            gate = copy.deepcopy(word["B"][position])
            if ("B", position) in assigned:
                gate[-1] = basis_of(assigned[("B", position)])
            out.append(gate)
            frame = audit.span(gate[-1])
            for register in audit.touched(gate):
                current[register] = frame
    for index, gate in enumerate(word["restore"]):
        if ("restore", index) not in assigned:
            continue
        if audit.span(compiled["restore"][index][-1]) != assigned[("restore", index)]:
            rewritten = copy.deepcopy(compiled["restore"][index])
            rewritten[-1] = basis_of(assigned[("restore", index)])
            compiled["restore"][index] = rewritten
    compiled["B"] = out
    compiled["cleanup"] = audit.derive_cleanup(compiled)
    audit.hygiene(compiled)
    return compiled, scales


def end_climbs(chain):
    counts = Counter()
    for events in chain.values():
        for event in events:
            if len(event) == 3 and event[0] == ("end",) and event[1]:
                counts[event[1]] += 1
    return dict(counts)


def delta_of(new, old):
    change = Counter(new)
    change.subtract(old)
    return {rank: count for rank, count in sorted(change.items()) if count}


def quotient_lines(original):
    """One representative of each line of F_2^9 / original."""
    lines = []
    seen = set()
    rank = audit.dim(original)
    for point in range(1, 512):
        if (original >> point) & 1:
            continue
        seed = join(original, audit.span((point,)))
        if audit.dim(seed) != rank + 1 or seed in seen:
            continue
        seen.add(seed)
        lines.append(point)
    need(len(lines) == (1 << (9 - rank)) - 1, "quotient line count")
    return lines


def cleanup_insert(old, new, lender):
    if len(new) != len(old) + 1:
        return False
    old_index = new_index = found = 0
    while old_index < len(old) and new_index < len(new):
        if old[old_index] == new[new_index]:
            old_index += 1
            new_index += 1
        elif found == 0 and new[new_index][:4] == ["scale", lender, 1, 1]:
            found = 1
            new_index += 1
        else:
            return False
    return found == 1 and old_index == len(old) and new_index == len(new)


def load():
    base_path = PACKAGE / "inputs" / "BASE-WORD.json.gz"
    bill_path = PACKAGE / "vendor" / "audit_core.py"
    need(sha256(base_path) == BASE_SHA256, "base word bytes")
    need(sha256(bill_path) == BILL_SHA256, "frame-bill bytes")
    with gzip.open(base_path, "rt", encoding="utf-8") as handle:
        return json_load(handle)


def json_load(handle):
    import json
    return json.load(handle)


def main():
    word = load()
    need(len(word["warps"]) == 72, "warp count")
    events = events_of(word)
    warp0 = events.index(("warp", 0))
    target_at = events.index(("warp", TARGET))
    need(target_at == warp0 + 1, "warp 13 is not the next native event")
    record = word["warps"][TARGET]
    need(record[0] == 916 and record[1] == 349, "warp 13 address")
    need(record[3] == [416, 70, 19, 13], "warp 13 original entrance")

    original_profile, _, original_chain, _, _ = audit.frame_bill(word, lagrangian=True)
    need(original_profile == {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}, "original profile")

    # Control: the same backward pass recovers PR #3933's warp-0 entrance.
    warp0_seed = maximal_entrance(word, 0)
    warp0_original = audit.span(word["warps"][0][3])
    need(warp0_seed == join(warp0_original, audit.span((7,))), "warp 0 capacity is not U+span(7)")
    warp0_assigned = least_assignment(word, 0, warp0_seed)
    need(warp0_assigned is not None, "warp 0 maximal seed rejected")
    warp0_word, warp0_scales = compile_least(word, 0, warp0_seed, warp0_assigned)
    warp0_profile, _, _, _, _ = audit.frame_bill(warp0_word, lagrangian=True)
    need(warp0_scales == [243], "warp 0 scale lender")
    need(delta_of(warp0_profile, original_profile) == {1: 27, 2: -14, 3: -1, 4: 1}, "warp 0 canonical delta")

    seed = maximal_entrance(word, TARGET)
    original = audit.span(record[3])
    need(seed == join(original, audit.span((7,))), "warp 13 capacity is not U+span(7)")
    need(audit.dim(seed) == 5, "warp 13 capacity dimension")
    lines = quotient_lines(original)
    admitted = []
    for point in lines:
        line_seed = join(original, audit.span((point,)))
        if least_assignment(word, TARGET, line_seed) is not None:
            admitted.append(line_seed)
    need(admitted == [seed], "admitted quotient seeds are not exactly U+span(7)")
    need(least_assignment(word, TARGET, original) is not None, "original entrance rejected")
    rejected = next(
        join(original, audit.span((point,)))
        for point in lines
        if join(original, audit.span((point,))) != seed
    )
    need(least_assignment(word, TARGET, join(seed, rejected)) is None, "dimension-6 seed survived")

    assigned = least_assignment(word, TARGET, seed)
    compiled, scales = compile_least(word, TARGET, seed, assigned)
    profile, _inventory, chain, _, _ = audit.frame_bill(compiled, lagrangian=True)
    change = delta_of(profile, original_profile)
    need(scales == [349], "entrance scale is not the one identity on lender 349")
    need(change == {1: 28, 2: -16, 3: -4, 4: 4}, "histogram delta")
    need(sum(rank * count for rank, count in profile.items()) == 5134, "rank mass")
    need(end_climbs(chain) == end_climbs(original_chain) == {1: 289, 2: 77, 3: 54}, "terminal end-climbs")
    for name in CALLER_FIELDS:
        need(compiled[name] == word[name], "caller field changed: " + name)
    need(cleanup_insert(word["cleanup"], compiled["cleanup"], 349), "cleanup is not one added inverse scale")
    # Integer endpoints of f(q) = 28 - 16*2^q - 4*3^q + 4*4^q.
    need(28 - 16 - 4 + 4 == 12, "f(0)")
    need(28 - 32 - 12 + 16 == 0, "f(1)")
    # A swapped exit on the same entrance is not a transported frame.
    bad = copy.deepcopy(compiled)
    bad["warps"][TARGET][4] = list(record[4])
    try:
        audit.frame_bill(bad, lagrangian=True)
    except audit.AuditFailure:
        pass
    else:
        raise SystemExit("FAIL: swapped exit was accepted")

    print(
        "PASS_LATER_WARP_MAXIMAL_ENTRANCE "
        "warp=13 lender=349 next_native_after_warp0 "
        "C=U+span(7) dim=5 admitted_line=7 "
        "entrance=+1H1 terminal_end_climbs=0 caller_fields=0 "
        "histogram=+28H1-16H2-4H3+4H4 mass=5134 "
        "power_tariff_strict_for_q_in_[0,1) no_new_kappa"
    )


if __name__ == "__main__":
    main()
