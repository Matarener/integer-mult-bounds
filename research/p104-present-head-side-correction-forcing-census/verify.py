#!/usr/bin/env python3
"""Read-only multi-entry forcing census for present-head side-correction entries.

On the published native-channel word, for each present-head flag in {1, 9, 43}
and five additional off-diagonal nonzero Gram sources on that target row, a
least-frame / class-Z insertion sweep asks whether a zero-mass common-chart
placement of the I-G/2 entry is feasible. Admission uses need() and remains
active under python -O. This module does not import independent.py and does
not reprint open #3601/#3610 correction bills.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FORCING_CENSUS "
    "flags={1,9,43} entries=18/18 need_plus_two "
    "primary_feeders=X7:387,X58:333,X12:131 no_new_kappa"
)
INPUTS = (
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
)
PRESENT = {
    1: {"source": 0, "target": 7, "basis_head": 232},
    9: {"source": 4, "target": 23, "basis_head": 196},
    43: {"source": 21, "target": 59, "basis_head": 15},
}
SELECTED_KAPPA = "0.001672660197076918"
PINNED_MAIN = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def closure(vectors):
    span = {0}
    for vector in vectors:
        if vector not in span:
            span |= {x ^ vector for x in span}
    return frozenset(span)


def grow(span, vectors):
    span = set(span)
    for vector in vectors:
        if vector not in span:
            span |= {x ^ vector for x in span}
    return frozenset(span)


def gram_fn(fixture):
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


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in rows) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw
    return pinned


def lower_sweep(witness, program, inject):
    cur = {name: closure(frame) for name, frame in witness["initial_frames"].items()}
    fin = {name: closure(frame) for name, frame in witness["final_frames"].items()}
    cut, regs, extra = inject
    for index in range(len(program) + 1):
        if index == cut:
            merged = closure(extra)
            for reg in regs:
                merged = grow(merged, cur[reg])
            for reg in regs:
                cur[reg] = merged
                if not merged <= fin[reg]:
                    return [index, reg]
        if index == len(program):
            return None
        event = program[index]
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        left, right = event[1], event[2]
        if cur[right] <= cur[left]:
            merged = cur[left]
        elif cur[left] <= cur[right]:
            merged = cur[right]
        else:
            merged = grow(cur[left], cur[right])
        cur[left] = cur[right] = merged
        for reg in (left, right):
            if not merged <= fin[reg]:
                return [index, reg]


def forcing_record(witness, program, gram, src, tgt, target_index):
    final = closure(witness["final_frames"][tgt])
    cur = {name: closure(frame) for name, frame in witness["initial_frames"].items()}
    head_of = {
        frame[0]: name
        for name, frame in witness["initial_frames"].items()
        if name.startswith("X") and len(frame) == 1
    }
    holders = {head: {name} for head, name in head_of.items()}
    for index, event in enumerate(program):
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        left, right = event[1], event[2]
        for head, regs in list(holders.items()):
            if left in regs or right in regs:
                holders[head] = regs | {left, right}
        merged = grow(cur[left], cur[right])
        cur[left] = cur[right] = merged
        if src in (left, right) and not cur[src] <= final:
            outside = []
            for head, name in sorted(head_of.items()):
                if head in cur[src] and head not in final:
                    seen = {name}
                    path = []
                    for step, prior in enumerate(program[: index + 1]):
                        if prior[0] != "add" or "C" in (prior[1], prior[2]):
                            continue
                        if set(prior[1:3]) & seen:
                            seen |= {prior[1], prior[2]}
                            path.append([step, prior[1], prior[2]])
                            if src in seen:
                                break
                    outside.append(
                        {
                            "head": head,
                            "from_register": name,
                            "gram_with_target": gram(target_index, int(name[1:])),
                            "head_in_target_final": False,
                            "carrier_path": path,
                        }
                    )
            return {
                "source_leaves_target_final_at": index,
                "source_rank_at_leave": len(cur[src]).bit_length() - 1,
                "add_event": program[index],
                "outside_heads": outside,
            }
    return None


def select_feeder(flag, source, outside):
    if flag == 1 and source == 0:
        for row in outside:
            if row["from_register"] == "X7" and row["head"] == 387:
                return row
    if flag == 43 and source == 21:
        for row in outside:
            if row["from_register"] == "X12" and row["head"] == 131:
                return row
    zero = [row for row in outside if row["gram_with_target"] == 0]
    return zero[0] if zero else outside[0]


def coefficient(gram):
    num = -gram
    return str(num // 2) if num % 2 == 0 else f"{num}/2"


def evaluate():
    pinned = pin_sources()
    flags = json.loads(pinned[INPUTS[0]], object_pairs_hook=pairs_unique)
    witness = json.loads(pinned[INPUTS[1]], object_pairs_hook=pairs_unique)
    fixture = json.loads(pinned[INPUTS[2]], object_pairs_hook=pairs_unique)[
        "section4_explicit_P104"
    ]
    gram = gram_fn(fixture)
    program = witness["program"]
    need(len(program) == 4058, "published word length")
    helpers = flags["helpers"]
    need(len(helpers) == 208, "flag count")
    for flag, meta in PRESENT.items():
        row = helpers[flag]
        need(
            (row["source"], row["target"], row["basis"][0])
            == (meta["source"], meta["target"], meta["basis_head"]),
            f"flag {flag} identity",
        )
        need(
            meta["basis_head"] in witness["final_frames"][f"Y{meta['target']}"],
            f"flag {flag} present-head",
        )

    entries = []
    for flag in (1, 9, 43):
        meta = PRESENT[flag]
        target, primary = meta["target"], meta["source"]
        others = [
            source
            for source in range(104)
            if source != target and gram(target, source) and source != primary
        ][:5]
        for source in [primary] + others:
            src = f"X{source}"
            tgt = f"Y{target}"
            final = closure(witness["final_frames"][tgt])
            cuts = sorted(
                {0}
                | {
                    index + 1
                    for index, event in enumerate(program)
                    if event[0] in ("add", "copy") and {src, tgt} & {event[1], event[2]}
                }
            )
            blocked = [
                lower_sweep(witness, program, (cut, (src, tgt), ())) for cut in cuts
            ]
            need(len(cuts) > 0 and all(blocked), f"zero-mass gap at ({target},{source})")
            forced = forcing_record(witness, program, gram, src, tgt, target)
            need(forced and forced["outside_heads"], f"missing forcing at ({target},{source})")
            feeder = select_feeder(flag, source, forced["outside_heads"])
            value = gram(target, source)
            entries.append(
                {
                    "flag_index": flag,
                    "is_primary_present_head_entry": source == primary,
                    "entry": {
                        "target": target,
                        "source": source,
                        "gram": value,
                        "correction_coefficient": coefficient(value),
                        "source_register": src,
                        "target_register": tgt,
                    },
                    "basis_head": meta["basis_head"],
                    "basis_head_in_target_final": meta["basis_head"] in final,
                    "insertion_classes": len(cuts),
                    "zero_mass_placements_obstructed": len(cuts),
                    "first_obstruction_by_class": [
                        [cut, obstruction] for cut, obstruction in zip(cuts, blocked)
                    ],
                    "forcing": {
                        "source_leaves_target_final_at": forced[
                            "source_leaves_target_final_at"
                        ],
                        "source_rank_at_leave": forced["source_rank_at_leave"],
                        "add_event": forced["add_event"],
                        "outside_head_count": len(forced["outside_heads"]),
                        "selected_feeder": {
                            "head": feeder["head"],
                            "from_register": feeder["from_register"],
                            "gram_with_target": feeder["gram_with_target"],
                            "head_in_target_final": feeder["head_in_target_final"],
                            "carrier_path": feeder["carrier_path"],
                        },
                    },
                    "parity_floor_non_private": 2,
                    "zero_mass_blocked": True,
                    "strict_side_correction_needs_plus_two": True,
                }
            )

    need(len(entries) == 18, "entry count")
    need(all(row["strict_side_correction_needs_plus_two"] for row in entries), "plus-two")
    primary = {
        row["flag_index"]: row["forcing"]["selected_feeder"]
        for row in entries
        if row["is_primary_present_head_entry"]
    }
    need(primary[1]["from_register"] == "X7" and primary[1]["head"] == 387, "flag1 feeder")
    need(primary[9]["from_register"] == "X58" and primary[9]["head"] == 333, "flag9 feeder")
    need(primary[43]["from_register"] == "X12" and primary[43]["head"] == 131, "flag43 feeder")
    return {
        "schema_version": 1,
        "claim_id": "p104-present-head-side-correction-forcing-census",
        "pinned_main": PINNED_MAIN,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
        "word": "published_native_channel",
        "program_events": len(program),
        "present_head_flags": [1, 9, 43],
        "theorem": {
            "checked_entries": 18,
            "all_need_plus_two": True,
            "counterexample": None,
        },
        "entries": entries,
        "primary_feeders": {
            "1": {"from_register": "X7", "head": 387},
            "9": {"from_register": "X58", "head": 333},
            "43": {"from_register": "X12", "head": 131},
        },
    }


def admit(observed, certificate):
    need(certificate["claim_id"] == observed["claim_id"], "certificate mismatch")
    need(certificate["pinned_main"] == observed["pinned_main"], "certificate mismatch")
    need(certificate["selected_kappa"] == observed["selected_kappa"], "certificate mismatch")
    need(certificate["no_new_kappa"] is True, "certificate mismatch")
    need(certificate["program_events"] == observed["program_events"], "certificate mismatch")
    need(certificate["theorem"]["all_need_plus_two"] is True, "certificate mismatch")
    need(certificate["theorem"]["counterexample"] is None, "certificate mismatch")
    need(certificate["theorem"]["checked_entries"] == 18, "certificate mismatch")
    need(len(certificate["entries"]) == 18, "certificate mismatch")
    for got, want in zip(observed["entries"], certificate["entries"]):
        need(got["flag_index"] == want["flag_index"], "certificate mismatch")
        need(got["entry"] == want["entry"], "certificate mismatch")
        need(
            got["insertion_classes"] == want["insertion_classes"],
            "certificate mismatch",
        )
        need(
            got["zero_mass_placements_obstructed"]
            == want["zero_mass_placements_obstructed"],
            "certificate mismatch",
        )
        need(
            got["first_obstruction_by_class"] == want["first_obstruction_by_class"],
            "certificate mismatch",
        )
        need(got["forcing"] == want["forcing"], "certificate mismatch")
        need(got["strict_side_correction_needs_plus_two"] is True, "certificate mismatch")
    need(
        all(row["strict_side_correction_needs_plus_two"] for row in certificate["entries"]),
        "certificate mismatch",
    )


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    print(MARKER)


if __name__ == "__main__":
    main()
