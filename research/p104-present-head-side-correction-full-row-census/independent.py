#!/usr/bin/env python3
"""Independent set-accumulation replay of the full-row present-head forcing census.

Imports neither verify.py nor any open side-correction bill builder. Frames are
XOR-closed frozensets. Insertion classes are rebuilt from touch events; the
least-frame obstruction is recomputed by a separate forward sweep; forcing
chains are rebuilt by carrier BFS from each initial X-head. Receipts are
compared against CERTIFICATE.json. Extends #3614's method to all 48
off-diagonal nonzero Gram sources per present-head target row.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FULL_ROW_CENSUS_INDEPENDENT "
    "flags={1,9,43} entries=144/144 need_plus_two "
    "primary_feeders=X7:387,X58:333,X12:131 no_new_kappa"
)
PINS = {
    "research/p104-joint-unit-flags/CERTIFICATE.json": (
        "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128"
    ),
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json": (
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
    ),
    "research/p104-native-channel/inputs/P104-FIXTURE.json": (
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
    ),
}
PRESENT = {
    1: (0, 7, 232),
    9: (4, 23, 196),
    43: (21, 59, 15),
}
SAMPLE_3614_SOURCES = {
    1: (0, 1, 2, 8, 9, 10),
    9: (4, 3, 5, 6, 13, 14),
    43: (21, 1, 2, 3, 4, 7),
}
EXPECTED_ENTRIES = 144


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + str(key))
        out[key] = value
    return out


def read(root, rel):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "pin: " + rel)
    return json.loads(raw, object_pairs_hook=strict)


def frame_set(vectors):
    """Independent XOR closure (set accumulation, not list-grow)."""
    span = {0}
    for vector in vectors:
        if vector in span:
            continue
        span |= {prior ^ vector for prior in span}
    return frozenset(span)


def merge_frames(left, right):
    if right <= left:
        return left
    if left <= right:
        return right
    span = set(left)
    for vector in right:
        if vector not in span:
            span |= {prior ^ vector for prior in span}
    return frozenset(span)


def gram_rows(fixture):
    lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            vector = [0] * 8
            vector[i], vector[j] = 2, 2 * sign
            lines.add(tuple(vector))
    for signs in itertools.product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.add((1,) + signs)
    gone = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    ports = [row for row in sorted(lines) if row not in gone]
    need(len(ports) == 104, "104 ports")
    return lambda t, s: sum(x * y for x, y in zip(ports[t], ports[s])) // 4


def touch_cuts(program, regs):
    hits = [0]
    wanted = set(regs)
    for index, event in enumerate(program):
        if event[0] not in ("add", "copy"):
            continue
        if wanted & {event[1], event[2]}:
            hits.append(index + 1)
    return sorted(set(hits))


def obstructed(witness, program, cut, regs):
    cur = {name: frame_set(frame) for name, frame in witness["initial_frames"].items()}
    fin = {name: frame_set(frame) for name, frame in witness["final_frames"].items()}
    for index in range(len(program) + 1):
        if index == cut:
            merged = frame_set(())
            for reg in regs:
                merged = merge_frames(merged, cur[reg])
            for reg in regs:
                cur[reg] = merged
                if not merged <= fin[reg]:
                    return index, reg
        if index == len(program):
            return None
        event = program[index]
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        left, right = event[1], event[2]
        merged = merge_frames(cur[left], cur[right])
        cur[left] = cur[right] = merged
        for reg in (left, right):
            if not merged <= fin[reg]:
                return index, reg


def carrier_path(program, start_reg, stop_reg, stop_event):
    seen = {start_reg}
    path = []
    for index, event in enumerate(program[: stop_event + 1]):
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        if set(event[1:3]) & seen:
            seen |= {event[1], event[2]}
            path.append([index, event[1], event[2]])
            if stop_reg in seen:
                break
    return path


def first_exit(witness, program, gram, src, tgt, target_index):
    final = frame_set(witness["final_frames"][tgt])
    cur = {name: frame_set(frame) for name, frame in witness["initial_frames"].items()}
    heads = {
        frame[0]: name
        for name, frame in witness["initial_frames"].items()
        if name.startswith("X") and len(frame) == 1
    }
    for index, event in enumerate(program):
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        left, right = event[1], event[2]
        merged = merge_frames(cur[left], cur[right])
        cur[left] = cur[right] = merged
        if src not in (left, right) or cur[src] <= final:
            continue
        outside = []
        for head, name in sorted(heads.items()):
            if head in cur[src] and head not in final:
                outside.append(
                    {
                        "head": head,
                        "from_register": name,
                        "gram_with_target": gram(target_index, int(name[1:])),
                        "head_in_target_final": False,
                        "carrier_path": carrier_path(program, name, src, index),
                    }
                )
        return {
            "source_leaves_target_final_at": index,
            "source_rank_at_leave": len(cur[src]).bit_length() - 1,
            "add_event": program[index],
            "outside_heads": outside,
        }
    return None


def pick_feeder(flag, source, outside):
    if flag == 1 and source == 0:
        for row in outside:
            if row["from_register"] == "X7" and row["head"] == 387:
                return row
    if flag == 9 and source == 4:
        for row in outside:
            if row["from_register"] == "X58" and row["head"] == 333:
                return row
    if flag == 43 and source == 21:
        for row in outside:
            if row["from_register"] == "X12" and row["head"] == 131:
                return row
    zero = [row for row in outside if row["gram_with_target"] == 0]
    return zero[0] if zero else outside[0]


def row_sources(gram, target, primary):
    others = [
        source
        for source in range(104)
        if source != target and gram(target, source) and source != primary
    ]
    return [primary] + others


def main(root=ROOT):
    witness = read(root, "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    fixture = read(root, "research/p104-native-channel/inputs/P104-FIXTURE.json")[
        "section4_explicit_P104"
    ]
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    gram = gram_rows(fixture)
    program = witness["program"]
    need(len(program) == 4058, "word length")
    need(cert["theorem"]["all_need_plus_two"] is True, "theorem")
    need(cert["theorem"]["counterexample"] is None, "no counterexample")
    need(cert["theorem"]["checked_entries"] == EXPECTED_ENTRIES, "entry count theorem")
    need(cert["selected_kappa"] == "0.001672660197076918", "kappa")
    need(cert["no_new_kappa"] is True, "no new kappa")

    rebuilt = []
    for flag in (1, 9, 43):
        source0, target, head = PRESENT[flag]
        helper = flags["helpers"][flag]
        need(
            (helper["source"], helper["target"], helper["basis"][0])
            == (source0, target, head),
            f"flag {flag}",
        )
        need(head in frame_set(witness["final_frames"][f"Y{target}"]), "present head")
        sources = row_sources(gram, target, source0)
        need(len(sources) == 48, f"row {flag}")
        need(tuple(sources[:6]) == SAMPLE_3614_SOURCES[flag], f"sample {flag}")
        for source in sources:
            src, tgt = f"X{source}", f"Y{target}"
            cuts = touch_cuts(program, (src, tgt))
            table = []
            for cut in cuts:
                hit = obstructed(witness, program, cut, (src, tgt))
                need(hit is not None, f"feasible zero-mass at {flag} ({target},{source})")
                table.append([cut, list(hit)])
            forced = first_exit(witness, program, gram, src, tgt, target)
            need(forced and forced["outside_heads"], "forcing missing")
            feeder = pick_feeder(flag, source, forced["outside_heads"])
            rebuilt.append(
                {
                    "flag_index": flag,
                    "entry": (target, source),
                    "classes": len(cuts),
                    "table": table,
                    "leave": forced["source_leaves_target_final_at"],
                    "feeder": (
                        feeder["from_register"],
                        feeder["head"],
                        feeder["gram_with_target"],
                    ),
                    "path": feeder["carrier_path"],
                    "in_sample": source in SAMPLE_3614_SOURCES[flag],
                }
            )

    need(len(rebuilt) == EXPECTED_ENTRIES == len(cert["entries"]), "entry counts")
    need(sum(1 for row in rebuilt if row["in_sample"]) == 18, "sample coverage")
    for got, want in zip(rebuilt, cert["entries"]):
        need(got["flag_index"] == want["flag_index"], "flag drift")
        need(
            got["entry"]
            == (want["entry"]["target"], want["entry"]["source"]),
            "entry drift",
        )
        need(got["classes"] == want["insertion_classes"], "class count")
        need(
            got["classes"] == want["zero_mass_placements_obstructed"],
            "obstruction count",
        )
        need(got["table"] == want["first_obstruction_by_class"], "obstruction table")
        need(
            got["leave"] == want["forcing"]["source_leaves_target_final_at"],
            "leave event",
        )
        feeder = want["forcing"]["selected_feeder"]
        need(
            got["feeder"]
            == (
                feeder["from_register"],
                feeder["head"],
                feeder["gram_with_target"],
            ),
            "feeder",
        )
        need(got["path"] == feeder["carrier_path"], "carrier path")
        need(want["strict_side_correction_needs_plus_two"] is True, "plus two")
        need(want["parity_floor_non_private"] == 2, "parity floor")
        need(got["in_sample"] == want["in_pr3614_sample"], "sample flag")

    primaries = {
        row["flag_index"]: row["forcing"]["selected_feeder"]
        for row in cert["entries"]
        if row["is_primary_present_head_entry"]
    }
    need(primaries[1]["head"] == 387 and primaries[1]["from_register"] == "X7", "flag1")
    need(primaries[9]["head"] == 333 and primaries[9]["from_register"] == "X58", "flag9")
    need(primaries[43]["head"] == 131 and primaries[43]["from_register"] == "X12", "flag43")
    # Known leave-alone sample citations (do not re-derive bills).
    need(primaries[43]["gram_with_target"] == 0, "flag43 feeder Gram 0 as in #3601")
    need(primaries[1]["gram_with_target"] == 2, "flag1 feeder Gram 2 as in #3610")
    need(primaries[9]["gram_with_target"] == 0, "flag9 feeder Gram 0 as in #3614/#3618")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
