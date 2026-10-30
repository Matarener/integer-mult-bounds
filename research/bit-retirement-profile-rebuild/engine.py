#!/usr/bin/env python3
"""Independent active658 WORD-to-paid-profile reconstruction over Q.

Credit: ai-nanachi's PR4326 compact retirement, Ross Richardson's PR4183
delayed retirement/logical admission and PR4021, PR3647's compact node, and
the retained Ali Romman, Sagar Thakrar, cheesegrader, commdata2338, CubeJerry,
Jose Manuel and David Arias lineage. Prepared by ToikY with substantial
OpenAI Codex assistance. No producer or predecessor executable is imported.

Integer cross multiplication and primitive-row normalization perform exact
Q elimination: multiplying a row by a nonzero integer and dividing by its
integer gcd preserve its Q span. Each new pivot is independent of earlier
pivots; reduction decides membership without floating-point arithmetic.

This checks geometric frame ranks/nesting and frame/private lease grammar.
Frame zero is not a zero VALUE promise. Numeric COPY/ERASE equality, SOURCE
history, operators, odd-characteristic/native admission, callers, physical
costs, precision and multiplication are deliberately outside this checker.
"""

from collections import Counter
import gzip
import hashlib
import io
import json
from math import gcd
from pathlib import Path
import sys


SOURCE_HEAD = "080f8c218d64c6d231ed6297987e39b7a912a4ef"
INPUTS = {
    "WORD.json.gz": ("69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b",
                     "776ddd13d67b2259e90d39de5b42e4df4b1447f1"),
    "GEOMETRY.json.gz": ("a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
                         "e12a566658a4b2c8b6ae0ecc34fd41290f68f5e8"),
}


class ContractError(ValueError):
    def __init__(self, guard, diagnostic):
        self.guard = guard
        self.diagnostic = diagnostic
        super().__init__(guard + ": " + json.dumps(diagnostic, sort_keys=True))


def need(condition, guard, **diagnostic):
    if not condition:
        raise ContractError(guard, diagnostic)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_inputs():
    directory = Path(__file__).resolve().parent / "source/provider/inputs"
    objects, pins = {}, []
    for name, (sha256, git_blob) in INPUTS.items():
        path = directory / name
        need(path.is_file() and not path.is_symlink(), "input_file", name=name)
        need(path.stat().st_size <= 16_000_000, "compressed_input_bound", name=name)
        raw = path.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
        actual_blob = hashlib.sha1(header + raw, usedforsecurity=False).hexdigest()
        need(actual_sha == sha256 and actual_blob == git_blob, "input_pin", name=name)
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            body = stream.read(16_000_001)
        need(len(body) <= 16_000_000, "decompressed_input_bound", name=name)
        objects[name] = json.loads(body)
        pins.append({"path": "source/provider/inputs/" + name, "git_blob": actual_blob,
                     "sha256": actual_sha, "decoded_bytes": len(body),
                     "decoded_sha256": hashlib.sha256(body).hexdigest()})
    return objects["WORD.json.gz"], objects["GEOMETRY.json.gz"], pins


def primitive(row):
    divisor = 0
    for value in row:
        divisor = gcd(divisor, abs(value))
    if not divisor:
        return row
    result = [value // divisor for value in row]
    if next(value for value in result if value) < 0:
        result = [-value for value in result]
    return result


def reduce_row(row, basis):
    current = list(row)
    for pivot, base in basis:
        if current[pivot]:
            left, right = base[pivot], current[pivot]
            current = primitive([left * x - right * y for x, y in zip(current, base)])
    return current


def rational_basis(rows):
    bank = {}
    for row in rows:
        current = reduce_row(row, sorted(bank.items()))
        pivot = next((i for i, value in enumerate(current) if value), None)
        if pivot is not None:
            bank[pivot] = primitive(current)
    return tuple((pivot, tuple(row)) for pivot, row in sorted(bank.items()))


class Frames:
    def __init__(self, geometry):
        self.h = geometry["h"]
        self.v = geometry["v"]
        need(type(self.h) is int and self.h == 8 and self.v == 111, "local_geometry_domain")
        lines = geometry["lines"]
        need(len(lines) == 111 and all(isinstance(row, list) and len(row) == self.h
             and all(type(value) is int for value in row) for row in lines), "integer_root_rows")
        labels = geometry["frames"]
        need(len(labels) == 636, "actual_frame_catalogue_size")
        self.bases = []
        for frame, members in enumerate(labels):
            need(isinstance(members, list) and len(set(members)) == len(members)
                 and all(type(label) is int and 0 <= label < len(lines) for label in members),
                 "frame_root_members", frame=frame)
            self.bases.append(rational_basis([lines[label] for label in members]))
        self.ranks = [len(basis) for basis in self.bases]
        need(self.ranks[0] == 0, "frame_zero_is_empty_geometry")
        self.containment_cache = {}

    def rank(self, frame):
        need(type(frame) is int and 0 <= frame < len(self.bases), "frame_label", frame=frame)
        return self.ranks[frame]

    def contains(self, high, low):
        self.rank(high)
        self.rank(low)
        key = high, low
        if key not in self.containment_cache:
            self.containment_cache[key] = all(
                not any(reduce_row(row, self.bases[high])) for _, row in self.bases[low])
        return self.containment_cache[key]


def profile(counter):
    return {str(rank): count for rank, count in sorted(counter.items()) if count}


def rebuild(word, frames, reverse=False):
    n = word["namespace"]
    need(type(n) is int and n == 658 and word["active_ordinary_roles"] == n
         and word["physical_helpers"] == n - 2 * frames.v == 436,
         "actual_compact_namespace")
    start, final = word["start"], word["final"]
    need(isinstance(start, list) and isinstance(final, list) and len(start) == len(final) == n,
         "actual_WORD_endpoints")
    for frame in start + final:
        frames.rank(frame)
    records = word["records"]
    need(isinstance(records, list), "literal_records")
    state = list(final if reverse else start) + [None]
    target = list(start if reverse else final) + [None]
    lease = None
    moves, copies, literal_opcodes = Counter(), Counter(), Counter()
    transitions, episodes = [], []
    iterator = reversed(list(enumerate(records))) if reverse else enumerate(records)
    for position, row in iterator:
        need(isinstance(row, list) and len(row) == 6
             and all(type(value) is int for value in row), "six_integer_fields", position=position)
        op, destination, source, coefficient, frame, section = row
        need(op in (0, 1, 2, 3), "literal_opcode", position=position, opcode=op)
        need(0 <= destination < n, "ordinary_destination", position=position, destination=destination)
        literal_opcodes[op] += 1
        if op == 0:
            need(lease is None, "MOVE_during_COPY_lease", position=position,
                 lease_origin=None if lease is None else lease["origin"])
            before, after = (coefficient, source) if reverse else (source, coefficient)
            before_rank, after_rank = frames.rank(before), frames.rank(after)
            need(state[destination] == before, "MOVE_actual_frame", position=position,
                 role=destination, actual=state[destination], declared=before)
            lower, upper = (after, before) if reverse else (before, after)
            increment = frames.rank(upper) - frames.rank(lower)
            need(0 < increment < frames.h, "proper_positive_MOVE_rank", position=position,
                 old_frame=source, new_frame=coefficient, increment=increment)
            need(frame == increment, "MOVE_declared_rank_mismatch", position=position,
                 role=destination, old_frame=source, new_frame=coefficient,
                 old_rank=frames.rank(source), new_rank=frames.rank(coefficient),
                 declared_rank=frame, independently_derived_rank=increment)
            need(frames.contains(upper, lower), "MOVE_not_nested", position=position,
                 role=destination, lower_frame=lower, upper_frame=upper,
                 lower_rank=frames.rank(lower), upper_rank=frames.rank(upper))
            state[destination] = after
            moves[increment] += 1
            transitions.append({"kind": "MOVE", "source_position": position, "role": destination,
                                "from_frame": before, "to_frame": after,
                                "from_rank": before_rank, "to_rank": after_rank,
                                "declared_rank": frame, "derived_paid_rank": increment,
                                "nested_over_Q": True})
        elif op == 1:
            need(0 <= source <= n and source != destination and coefficient in (-1, 1),
                 "signed_ADD_operands", position=position, source=source, destination=destination)
            need(source != n or lease is not None, "private_read_without_COPY", position=position,
                 source=source, destination=destination)
            need(lease is None or destination != lease["origin"], "COPY_origin_written", position=position)
            frames.rank(frame)
            need(state[destination] == state[source] == frame, "ADD_actual_coframe", position=position,
                 destination_frame=state[destination], source_frame=state[source], declared_frame=frame)
        elif op == (3 if reverse else 2):
            need(source == n and lease is None and state[n] is None, "fresh_private_frame_lease",
                 position=position, private=source)
            source_rank = frames.rank(coefficient)
            need(frame == 0 and state[destination] == coefficient, "COPY_actual_source_frame",
                 position=position, origin=destination, actual_frame=state[destination],
                 declared_source_frame=coefficient, private_frame=frame)
            need(0 < source_rank < frames.h, "proper_COPY_source_rank", position=position,
                 source_frame=coefficient, derived_rank=source_rank)
            state[n] = frame
            lease = {"origin": destination, "source_frame": coefficient,
                     "source_rank": source_rank, "opening_source_position": position}
            copies[source_rank] += 1
            transitions.append({"kind": "COPY", "source_position": position, "origin": destination,
                                "source_frame": coefficient, "private_role": n,
                                "private_frame": frame, "derived_paid_rank": source_rank})
        else:
            need(source == n and lease is not None and lease["origin"] == destination,
                 "ERASE_without_matching_COPY", position=position, origin=destination)
            need(state[destination] == coefficient == lease["source_frame"] and state[n] == frame == 0,
                 "ERASE_frame_lease_mismatch", position=position)
            episodes.append({**lease, "closing_source_position": position,
                             "origin_immutable_in_frame_grammar": True,
                             "numeric_ERASE_equality_verified": False})
            state[n] = None
            lease = None
    need(lease is None and state == target, "complete_actual_frame_endpoint")
    move_mass = sum(rank * count for rank, count in moves.items())
    endpoint_progress = sum(frames.rank(b) - frames.rank(a) for a, b in zip(start, final))
    need(move_mass == endpoint_progress, "MOVE_mass_telescoping", move_mass=move_mass,
         endpoint_progress=endpoint_progress)
    paid = moves + copies
    return {"orientation": "reverse" if reverse else "forward", "records_checked": len(records),
            "literal_opcodes": {str(op): count for op, count in sorted(literal_opcodes.items())},
            "MOVE_profile": profile(moves), "COPY_profile": profile(copies),
            "local_profile": profile(paid), "paid_QUERYs": sum(paid.values()),
            "MOVE_rankmass": move_mass,
            "COPY_rankmass": sum(rank * count for rank, count in copies.items()),
            "local_rankmass": sum(rank * count for rank, count in paid.items()),
            "endpoint_rank_progress": endpoint_progress,
            "private_frame_lease_closed": True, "private_numeric_zero_verified": False,
            "COPY_episodes": episodes, "paid_transition_records": transitions,
            "paid_transition_records_sha256": digest(transitions)}


def expect_rejection(word, frames, expected, name, mutation):
    try:
        rebuild(word, frames)
    except ContractError as error:
        need(error.guard == expected, "control_wrong_rejection", control=name,
             expected=expected, actual=error.guard, diagnostic=error.diagnostic)
        return {"name": name, "mutation": mutation, "rejected": True,
                "guard": error.guard, "diagnostic": error.diagnostic}
    raise ValueError("control accepted: " + name)


def controls(word, frames):
    records = word["records"]
    first_move = next(index for index, row in enumerate(records) if row[0] == 0)
    changed = [list(row) for row in records]
    original = changed[first_move][:]
    changed[first_move][4] = original[4] + 1 if original[4] < 7 else original[4] - 1
    rank_control = expect_rejection({**word, "records": changed}, frames,
        "MOVE_declared_rank_mismatch", "wrong_rank_on_actual_legal_MOVE",
        {"source_position": first_move, "original": original, "replacement": changed[first_move],
         "original_frames_unchanged": True})

    opening = next(index for index, row in enumerate(records) if row[0] == 2)
    omitted = records[:opening] + records[opening + 1:]
    missing_copy = expect_rejection({**word, "records": omitted}, frames,
        "private_read_without_COPY", "omit_actual_COPY_opening",
        {"omitted_source_position": opening, "omitted_record": records[opening]})

    for index, row in enumerate(records):
        if row[0] != 0 or frames.rank(row[2]) == 0:
            continue
        replacement = next((frame for frame, rank in enumerate(frames.ranks)
                            if rank == frames.rank(row[3]) and not frames.contains(frame, row[2])), None)
        if replacement is not None:
            changed = [list(record) for record in records]
            changed[index][3] = replacement
            nonnested = expect_rejection({**word, "records": changed}, frames,
                "MOVE_not_nested", "same_rank_noncontaining_actual_MOVE_target",
                {"source_position": index, "original": row, "replacement": changed[index],
                 "declared_increment_unchanged": True})
            break
    else:
        raise ValueError("no actual MOVE admits a same-rank nonnested control")
    return [rank_control, missing_copy, nonnested]


def run():
    word, geometry, pins = load_inputs()
    frames = Frames(geometry)
    forward = rebuild(word, frames)
    reverse = rebuild(word, frames, True)
    need(forward["local_profile"] == reverse["local_profile"], "both_orientation_profiles")
    helper_widths = [frames.rank(frame) for frame in word["final"][2 * frames.v:]]
    need(len(helper_widths) == 436, "ordered_actual_helper_widths")
    negative_controls = controls(word, frames)
    return {"schema_version": 1, "source_head": SOURCE_HEAD,
            "outcome": "complete_local_Q_frame_profile_rebuild",
            "local_profile": forward["local_profile"], "helper_widths": helper_widths,
            "helper_width_histogram": profile(Counter(helper_widths)),
            "helper_width_rankmass": sum(helper_widths),
            "local_QUERYs": forward["paid_QUERYs"], "local_rankmass": forward["local_rankmass"],
            "ordinary_roles": word["namespace"], "private_role": word["namespace"],
            "source_roles": frames.v, "target_roles": frames.v, "helper_roles": len(helper_widths),
            "input_pins": pins, "literal_records_sha256": digest(word["records"]),
            "rational_frame_ranks": frames.ranks,
            "rational_frame_bases_sha256": digest(frames.bases),
            "frames_rebuilt": len(frames.bases),
            "orientation_coverage": "every literal record in forward and reversed/inverted frame grammar",
            "orientations": {"forward": forward, "reverse": reverse},
            "negative_controls": negative_controls,
            "scope": "Q frame dimensions/nesting, paid MOVE/COPY ranks and private frame lease grammar only; no numeric COPY/ERASE/SOURCE/operator/native/physical/caller/outer proof."}


if __name__ == "__main__":
    need(len(sys.argv) == 1, "CLI_no_arguments")
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
