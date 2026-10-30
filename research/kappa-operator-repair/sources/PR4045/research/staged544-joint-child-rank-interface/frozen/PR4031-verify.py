#!/usr/bin/env python3
"""Verify a scoped rank-4 block-retiming screen on the pinned gauge44 trace."""

from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
CANONICAL_MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PROGRAM_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
WORD_SHA256 = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
EXPECTED_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_TARGETS = {
    **{frame: 7 for frame in range(415, 423)},
    431: 4, 432: 4, 433: 4, 434: 4, 436: 4, 437: 4,
}
MODEL = (73, 896, 9, 64)
GRID = Q(1, 10**13)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_json_gzip(raw):
    return json.loads(gzip.decompress(raw))


def lregisters(operation):
    """Return the L-registers read or written by a local scalar macro."""
    require(operation[0] == "add", f"unexpected retimed scalar macro: {operation}")
    require(operation[1][0] == "L" and operation[2][0] == "L",
            f"rank-4 retiming is not confined to L registers: {operation}")
    return {operation[1][1], operation[2][1]}


def linear_state(events):
    """Symbolically execute child outputs and rational ADDs on arbitrary L state."""
    state = {}

    def get(reg):
        return state.get(reg, {f"x{reg}": Q(1)})

    def add_scaled(left, right, scale):
        out = dict(left)
        for symbol, coefficient in right.items():
            out[symbol] = out.get(symbol, Q(0)) + scale * coefficient
            if out[symbol] == 0:
                del out[symbol]
        return out

    for position, event in enumerate(events):
        if event[0] == "climb":
            reg = event[2]
            state[reg] = {f"q{id(event)}": Q(1)}
        else:
            require(event[0] == "scalar", f"unexpected event in block window: {event}")
            operation = event[1]
            lregisters(operation)
            destination, source = operation[1][1], operation[2][1]
            scale = Q(operation[3], operation[4])
            state[destination] = add_scaled(get(destination), get(source), scale)
    return state


def verify_batch(events, call_indices, block_side):
    """Check a zero-charge retiming and the linear context around a block."""
    calls = [events[index] for index in call_indices]
    require(len(calls) in (3, 4), "a block must contain three or four rank-4 calls")
    require(all(call[0] == "climb" and call[-1] == 4 for call in calls),
            "a block contains a non-rank-4 child")
    require(len({call[1] for call in calls}) == 1, "mixed operand phase in one block")
    require(len({call[4] for call in calls}) == 1, "mixed target frame in one block")
    registers = [call[2] for call in calls]
    require(len(set(registers)) == len(registers), "block child outputs alias")
    require(sum(call[-1] for call in calls) == block_side, "wrong direct-sum side")

    lo, hi = call_indices[0], call_indices[-1]
    interval = events[lo:hi + 1]
    interval_calls = [lo + j for j, event in enumerate(interval) if event[0] == "climb"]
    require(interval_calls == call_indices, "another child occurs inside the proposed block")
    for event in interval:
        if event[0] == "scalar":
            lregisters(event[1])
        else:
            require(event[0] == "climb", f"non-scalar event inside block: {event}")

    # A scalar reference to a later child register would observe a different value
    # after the calls are moved before the ADDs. Exclude every such hazard.
    for position in range(lo, hi + 1):
        event = events[position]
        if event[0] != "scalar":
            continue
        future = {call[2] for call_index, call in zip(call_indices, calls)
                  if call_index > position}
        require(not (lregisters(event[1]) & future),
                f"retiming changes a future child's input at event {position}")

    original = interval
    retimed = [events[index] for index in call_indices]
    retimed.extend(event for event in interval if event[0] == "scalar")
    require(linear_state(original) == linear_state(retimed),
            "moving the ADDs after independent child calls changes the exact linear map")
    return {
        "target_frame": calls[0][4],
        "phase": calls[0][1],
        "source_frames": [call[3] for call in calls],
        "output_registers": registers,
        "event_interval": [lo, hi],
        "retimed_scalar_events": sum(event[0] == "scalar" for event in interval),
        "block_side": block_side,
    }


def verify_direct_sum_identity(blocks):
    """Exhaustively compare all entries in diag(A_i)diag(B_i)."""
    side = 4 * blocks

    def matrix_entry(operand, row, column):
        if row // 4 != column // 4:
            return None
        return f"{operand}{row // 4}_{row % 4}_{column % 4}"

    for row in range(side):
        for column in range(side):
            actual = Counter()
            for inner in range(side):
                left = matrix_entry("a", row, inner)
                right = matrix_entry("b", inner, column)
                if left is not None and right is not None:
                    actual[(left, right)] += 1
            expected = Counter()
            if row // 4 == column // 4:
                block = row // 4
                for inner in range(4):
                    expected[(f"a{block}_{row % 4}_{inner}",
                              f"b{block}_{inner}_{column % 4}")] += 1
            require(actual == expected,
                    f"block-diagonal multiplication identity failed at {(row, column)}")


def decimal(q):
    with localcontext() as context:
        context.prec = 30
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def as_profile(counter):
    return {str(rank): counter[rank] for rank in sorted(counter) if counter[rank]}


def ceiling(profile):
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling as engine
    return engine.ceiling(profile, *MODEL, grid=GRID)[1]


def main(write=False):
    archive_bytes = ARCHIVE.read_bytes()
    require(hashlib.sha256(archive_bytes).hexdigest() == ARCHIVE_SHA256,
            "selected replay archive SHA-256 mismatch")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        program_bytes = archive.extractfile(MEMBER).read()
        word_bytes = archive.extractfile(CANONICAL_MEMBER).read()
    require(hashlib.sha256(program_bytes).hexdigest() == PROGRAM_SHA256,
            "local program member SHA-256 mismatch")
    require(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA256,
            "canonical word member SHA-256 mismatch")

    programs = read_json_gzip(program_bytes)
    canonical = read_json_gzip(word_bytes)
    selected_profile = {int(rank): int(count)
                        for rank, count in canonical["local_profile"].items()}
    require(selected_profile == EXPECTED_PROFILE, "canonical local profile changed")
    require(sum(rank * count for rank, count in selected_profile.items()) == 5586,
            "selected paid rank mass changed")

    orientation_results = {}
    first_orientation_batches = None
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        profile = Counter(event[-1] for event in events
                          if event[0] == "climb" or event[0] == "center")
        require(dict(profile) == EXPECTED_PROFILE,
                f"{orientation} event profile differs from the pinned word")

        by_target = defaultdict(list)
        for index, event in enumerate(events):
            if event[0] == "climb" and event[-1] == 4:
                by_target[event[4]].append(index)
        eligible = {frame: indices for frame, indices in by_target.items()
                    if len(indices) >= 4}
        require({frame: len(indices) for frame, indices in eligible.items()} == EXPECTED_TARGETS,
                f"{orientation} rank-4 target-frame census changed")

        batches = []
        for frame in sorted(eligible):
            indices = eligible[frame]
            sizes = [4, 3] if len(indices) == 7 else [4]
            offset = 0
            for size in sizes:
                chunk = indices[offset:offset + size]
                offset += size
                batches.append(verify_batch(events, chunk, size * 4))
            require(offset == len(indices), "target-frame calls were not fully partitioned")
        require(len(batches) == 22, "unexpected number of direct-sum blocks")
        require(Counter(batch["block_side"] for batch in batches) == {12: 8, 16: 14},
                "unexpected block-side distribution")
        if first_orientation_batches is None:
            first_orientation_batches = batches
        else:
            require(batches == first_orientation_batches,
                    "forward and backward retiming schedules differ")
        orientation_results[orientation] = {
            "rank4_calls": profile[4],
            "eligible_target_frames": {str(frame): len(indices)
                                        for frame, indices in sorted(eligible.items())},
            "blocks": len(batches),
            "grouped_calls": sum(len(batch["output_registers"]) for batch in batches),
            "grouped_rank_mass": sum(batch["block_side"] for batch in batches),
            "block_sides": {str(side): count for side, count in
                            sorted(Counter(batch["block_side"] for batch in batches).items())},
            "retimed_scalar_events": sum(batch["retimed_scalar_events"] for batch in batches),
        }

    verify_direct_sum_identity(3)
    verify_direct_sum_identity(4)

    candidate = dict(selected_profile)
    candidate[4] -= 80
    candidate[12] = candidate.get(12, 0) + 8
    candidate[16] = candidate.get(16, 0) + 14
    require(candidate[4] == 62, "candidate rank-4 count mismatch")
    require(sum(rank * count for rank, count in candidate.items()) == 5586,
            "rank-4 fusion changed paid rank mass")

    mixed_result = json.loads((ROOT / "research/complex-mixed-rank-diagonal-seed8433/RESULT.json")
                              .read_text())
    mixed_profile = {int(rank): int(count)
                     for rank, count in mixed_result["selected_profile"].items()}
    require(sum(rank * count for rank, count in mixed_profile.items()) == 5586,
            "pinned rank-2/3 profile does not preserve selected mass")
    require(mixed_profile.get(4, 0) >= 80,
            "rank-2/3 comparison profile lacks disjoint rank-4 calls")
    combined = dict(mixed_profile)
    combined[4] -= 80
    combined[12] = combined.get(12, 0) + 8
    combined[16] = combined.get(16, 0) + 14
    require(sum(rank * count for rank, count in combined.items()) == 5586,
            "composed zero-charge profile changes paid mass")

    baseline_hi = ceiling(selected_profile)
    candidate_hi = ceiling(candidate)
    mixed_hi = ceiling(mixed_profile)
    combined_hi = ceiling(combined)
    kappa = lambda alpha: alpha / (1 + alpha)
    result = {
        "status": "PASS_COMPLEX_RANK4_RETIMED_BLOCKS",
        "source": {
            "archive_sha256": ARCHIVE_SHA256,
            "local_program_sha256": PROGRAM_SHA256,
            "canonical_word_sha256": WORD_SHA256,
            "selected_profile": as_profile(Counter(selected_profile)),
        },
        "per_orientation": orientation_results,
        "direct_sum_identity": {
            "tested_block_counts": [3, 4],
            "child_side_4_to_block_side": {"3": 12, "4": 16},
            "identity": "diag(A_1,...,A_t) diag(B_1,...,B_t) = diag(A_1 B_1,...,A_t B_t)",
        },
        "rank4_candidate": {
            "grouped_calls": 80,
            "new_blocks": {"12": 8, "16": 14},
            "profile": as_profile(Counter(candidate)),
            "rank_mass": 5586,
            "charges_waived": [
                "physical input gathering and block-diagonal layout",
                "output routing and storage",
                "frame/interface conversion",
                "hosting and precision",
                "arbitrary-dirty restoration",
            ],
            "ceiling_a_hi": str(candidate_hi),
            "kappa_cap_hi": str(kappa(candidate_hi)),
            "ceiling_gain_percent_over_selected": decimal(100 * (candidate_hi / baseline_hi - 1)),
            "five_percent_gate_passed_alone": candidate_hi >= baseline_hi * Q(105, 100),
        },
        "joint_zero_charge_screen": {
            "predecessor": "research/complex-mixed-rank-diagonal-seed8433/RESULT.json",
            "predecessor_profile": as_profile(Counter(mixed_profile)),
            "composed_profile": as_profile(Counter(combined)),
            "composed_ceiling_a_hi": str(combined_hi),
            "composed_kappa_cap_hi": str(kappa(combined_hi)),
            "ceiling_gain_percent_over_selected": decimal(100 * (combined_hi / baseline_hi - 1)),
            "five_percent_gate_passed_under_zero_charge_only": combined_hi >= baseline_hi * Q(105, 100),
            "new_supplier_or_kappa": False,
        },
        "baseline_ceiling_a_hi": str(baseline_hi),
        "mixed_rank23_ceiling_a_hi": str(mixed_hi),
        "scope_wall": "The frozen trace authenticates child ranks, target frames and scalar register context, but does not specify a physical block-input/output ownership contract or complete gathering, routing, hosting, precision and dirty-restoration bill for a fused rank-12/rank-16 call.",
    }

    result_path = PACKAGE / "RESULT.json"
    if write:
        result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        recorded = json.loads(result_path.read_text(encoding="utf-8"))
        require(recorded == result, "RESULT.json differs from the independently recomputed screen")

    print("PASS_COMPLEX_RANK4_RETIMED_BLOCKS")
    print(json.dumps({
        "forward_backward_batches": len(first_orientation_batches),
        "grouped_calls": 80,
        "new_block_sides": {"12": 8, "16": 14},
        "candidate_ceiling_a_hi": str(candidate_hi),
        "combined_zero_charge_ceiling_a_hi": str(combined_hi),
        "combined_five_percent_gate": result["joint_zero_charge_screen"]["five_percent_gate_passed_under_zero_charge_only"],
        "new_kappa": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main(write="--write" in sys.argv[1:])
