#!/usr/bin/env python3
"""Exact Toom-3 tensor and optimistic selected-profile/source-window screen."""
from __future__ import annotations

import bisect
import collections
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PROGRAM_MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
PROGRAM_MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
WORD_MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
SELECTED = ROOT / "certificates/selected-result.json"
SELECTED_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Q(1, 10**15)
TARGET_KAPPA = Q(1, 500)
TARGET_A = Q(1, 499)
BATCH = 9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_objects() -> tuple[dict[str, list], dict]:
    archive = ARCHIVE.read_bytes()
    require(sha256(archive) == ARCHIVE_SHA256, "selected replay archive pin")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        indexed = {entry.name: entry for entry in tar.getmembers()}
        require(PROGRAM_MEMBER in indexed and WORD_MEMBER in indexed,
                "selected provider members present")
        program_raw = tar.extractfile(indexed[PROGRAM_MEMBER]).read()
        word_raw = tar.extractfile(indexed[WORD_MEMBER]).read()
    require(sha256(program_raw) == PROGRAM_MEMBER_SHA256,
            "selected LOCAL-PROGRAMS member pin")
    programs = json.loads(gzip.decompress(program_raw))
    word = json.loads(gzip.decompress(word_raw))
    require(set(programs) == {"forward", "backward"}, "both orientations present")
    return programs, word


def selected_baseline() -> tuple[dict, Q]:
    selected_raw = SELECTED.read_bytes()
    require(sha256(selected_raw) == SELECTED_SHA256, "selected record pin")
    selected = json.loads(selected_raw)
    require(selected["decimal"] == "0.001672660197076918",
            "selected kappa value")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/research_baseline.py")],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    baseline = json.loads(completed.stdout)
    require(baseline["selected_record_sha256"] == SELECTED_SHA256,
            "baseline report binds selected record")
    bit_a = Q(baseline["bit_saving"])
    require(bit_a == Q(1733427039589844234749, 10**24),
            "selected bit saving pin")
    return baseline, bit_a


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "square matrix")
    work = [
        [Q(value) for value in row]
        + [Q(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            raise ValueError("singular interpolation matrix")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [value / scale for value in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[col])
                ]
    return [row[n:] for row in work]


def matrix_rank(matrix: list[list[Q]]) -> int:
    work = [[Q(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows, cols = len(work), len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows)
                      if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def interpolation_matrix(points: tuple[int, ...]) -> list[list[Q]]:
    finite = [[Q(x**power) for power in range(5)] for x in points]
    return finite + [[Q(0), Q(0), Q(0), Q(0), Q(1)]]


def check_toom3() -> dict:
    points = (0, 1, -1, 2)
    interpolation = inverse(interpolation_matrix(points))
    evaluations = [
        [Q(1), Q(0), Q(0)],
        [Q(1), Q(1), Q(1)],
        [Q(1), Q(-1), Q(1)],
        [Q(1), Q(2), Q(4)],
        [Q(0), Q(0), Q(1)],
    ]
    require(matrix_rank(evaluations) == 3, "five evaluation forms span three coefficients")

    basis_pairs = 0
    for left_power in range(3):
        for right_power in range(3):
            products = [
                Q(x**left_power * x**right_power) for x in points
            ] + [Q(int(left_power == 2 and right_power == 2))]
            output = [
                sum(interpolation[k][j] * products[j] for j in range(5))
                for k in range(5)
            ]
            expected = [
                Q(int(k == left_power + right_power)) for k in range(5)
            ]
            require(output == expected, "Toom-3 basis product identity")
            basis_pairs += 1

    duplicate_rejected = False
    try:
        inverse(interpolation_matrix((0, 1, -1, -1)))
    except ValueError:
        duplicate_rejected = True
    require(duplicate_rejected, "duplicate evaluation point rejected")

    wrong_products = [
        Q(0), Q(1), Q(-1), Q(0), Q(0)
    ]
    wrong_output = [
        sum(interpolation[k][j] * wrong_products[j] for j in range(5))
        for k in range(5)
    ]
    require(wrong_output != [Q(0), Q(1), Q(0), Q(0), Q(0)],
            "omitted evaluation product rejected")

    wrong_sign = [Q(0), Q(1), Q(1), Q(2), Q(0)]
    wrong_sign_output = [
        sum(interpolation[k][j] * wrong_sign[j] for j in range(5))
        for k in range(5)
    ]
    require(wrong_sign_output != [Q(0), Q(1), Q(0), Q(0), Q(0)],
            "wrong evaluation sign rejected")

    support = [sum(value != 0 for value in row) for row in interpolation]
    nonunit_scales = sum(
        value not in (0, 1, -1)
        for row in interpolation for value in row
    )
    decoder_adds = sum(max(0, count - 1) for count in support)
    require(support == [1, 5, 4, 5, 1], "interpolation support profile")
    require((decoder_adds, nonunit_scales) == (11, 11),
            "direct interpolation arithmetic count")
    # Per operand: s=a0+a2, then s+a1, s-a1, s+2*a1.
    input_adds, input_scales = 8, 2
    require((input_adds + decoder_adds, input_scales + nonunit_scales)
            == (19, 13), "two-sided evaluation/interpolation count")
    return {
        "basis_pairs": basis_pairs,
        "products": 5,
        "input_evaluation_rank": 3,
        "decoder_support": support,
        "linear_adds_per_block": 19,
        "rational_scales_per_block": 13,
    }


def profile_of(events: list) -> dict[int, int]:
    counts: collections.Counter[int] = collections.Counter()
    for event in events:
        if event[0] == "climb":
            counts[int(event[5])] += 1
        elif event[0] == "center":
            counts[int(event[4])] += 1
    return dict(sorted(counts.items()))


def is_rank_one(event: list) -> bool:
    return event[0] == "climb" and event[5] == 1


def touched(event: list) -> set[tuple[str, int]]:
    tag = event[0]
    if tag == "climb":
        return {("L", event[2])}
    if tag in ("adapter", "residual_adapter"):
        return {("L", event[2])}
    if tag == "center":
        return {("C", event[1])}
    if tag == "scalar":
        operation = event[1]
        registers = {tuple(operation[1])}
        if operation[0] in ("copy", "add"):
            registers.add(tuple(operation[2]))
        return registers
    return set()


def split_phases(events: list) -> list[tuple[list | None, list]]:
    result: list[tuple[list | None, list]] = [(None, [])]
    for event in events:
        if event[0] == "phase":
            result.append((event, []))
        else:
            result[-1][1].append(event)
    return result


def batch_phase(body: list) -> tuple[list, list[list], int]:
    skeleton = [event for event in body if not is_rank_one(event)]
    skeleton_size = len(skeleton)
    climbs = []
    gap = 0
    for event in body:
        if is_rank_one(event):
            climbs.append((len(climbs), gap, event))
        else:
            gap += 1

    touch_positions: dict[tuple[str, int], list[int]] = collections.defaultdict(list)
    for index, event in enumerate(skeleton):
        for register in touched(event):
            touch_positions[register].append(index)

    windows = {}
    original_gap = {}
    event_by_id = {}
    for key, gap, event in climbs:
        positions = touch_positions[("L", event[2])]
        position = bisect.bisect_left(positions, gap)
        lo = positions[position - 1] + 1 if position > 0 else 0
        hi = positions[position] if position < len(positions) else skeleton_size
        windows[key] = (lo, hi)
        original_gap[key] = gap
        event_by_id[key] = event

    same_register_window = collections.Counter(
        (event[2], windows[key]) for key, gap, event in climbs
    )
    movable = [
        key for key, gap, event in climbs
        if same_register_window[(event[2], windows[key])] == 1
    ]
    starts: dict[int, list[int]] = collections.defaultdict(list)
    for key in movable:
        starts[windows[key][0]].append(key)

    available: set[int] = set()
    batches: dict[int, list[list[int]]] = collections.defaultdict(list)
    batched: set[int] = set()
    for gap in range(skeleton_size + 1):
        available.update(starts[gap])
        while (any(windows[key][1] == gap for key in available)
               and len(available) >= BATCH):
            chosen = sorted(available, key=lambda key: (windows[key][1], key))[:BATCH]
            batches[gap].append(chosen)
            batched.update(chosen)
            available.difference_update(chosen)
        available = {
            key for key in available if windows[key][1] > gap
        }

    stays: dict[int, list[int]] = collections.defaultdict(list)
    for key, gap, event in climbs:
        if key not in batched:
            stays[gap].append(key)

    reordered = []
    for gap in range(skeleton_size + 1):
        for group in batches[gap]:
            destinations = [event_by_id[key][2] for key in group]
            require(len(set(destinations)) == BATCH,
                    "batch destinations are distinct")
            reordered.extend(event_by_id[key] for key in group)
        reordered.extend(event_by_id[key] for key in stays[gap])
        if gap < skeleton_size:
            reordered.append(skeleton[gap])

    groups = [
        [event_by_id[key] for key in group]
        for gap in sorted(batches) for group in batches[gap]
    ]
    return reordered, groups, len(climbs)


def frame_contains(frames: list[list[int]], old: int, new: int) -> bool:
    for vector in frames[old]:
        reduced = vector
        for target in frames[new]:
            if reduced >> (target.bit_length() - 1) & 1:
                reduced ^= target
        if reduced:
            return False
    return True


def replay_frames(events: list, word: dict) -> None:
    frames = word["frames"]
    current = list(word["start"])
    phase = None
    phase_order = []
    for event in events:
        tag = event[0]
        if tag == "phase":
            phase = event[1]
            phase_order.append(phase)
        elif tag == "climb":
            _, part, register, old, new, rank = event
            require(part == phase, "climb remains inside its phase")
            require(current[register] == old, "rank-one climb old frame")
            require(frame_contains(frames, old, new), "nested child frame")
            require(rank == len(frames[new]) - len(frames[old]),
                    "child rank equals frame increment")
            current[register] = new
        elif tag == "scalar":
            operation, frame = event[1], event[2]
            registers = [operation[1]]
            if operation[0] in ("copy", "add"):
                registers.append(operation[2])
            for register in registers:
                if register[0] == "L":
                    require(current[register[1]] == frame,
                            "scalar event retains its local frame")
        elif tag == "center":
            require(phase == "centers", "centre events stay in centre phase")
    require(current == word["final"], "terminal frame inventory")


def dependency_window_batches(programs: dict[str, list], word: dict) -> dict:
    receipts = {}
    for orientation, events in programs.items():
        require(len(events) == 24767, orientation + " event count")
        replay_frames(events, word)
        reordered = []
        phase_batches = collections.Counter()
        rank_one_count = sum(is_rank_one(event) for event in events)
        for marker, body in split_phases(events):
            if marker is not None:
                reordered.append(marker)
            new_body, groups, _ = batch_phase(body)
            reordered.extend(new_body)
            if marker is not None:
                phase_batches[marker[1]] += len(groups)
        require(rank_one_count == BASE_PROFILE[1],
                orientation + " rank-one climb count")
        require(
            collections.Counter(json.dumps(event, separators=(",", ":"))
                                for event in reordered)
            == collections.Counter(json.dumps(event, separators=(",", ":"))
                                   for event in events),
            orientation + " event multiset preserved",
        )
        require(
            [event for event in reordered if not is_rank_one(event)]
            == [event for event in events if not is_rank_one(event)],
            orientation + " every non-rank-one event stays ordered",
        )
        replay_frames(reordered, word)
        require(
            {phase: count for phase, count in phase_batches.items() if count}
            == {
                "A": 103, "B": 107, "cleanup_tail": 8, "final": 36,
            },
            orientation + " phase-local batch counts",
        )
        receipts[orientation] = {
            "groups": sum(phase_batches.values()),
            "by_phase": dict(sorted(phase_batches.items())),
        }
    require(receipts["forward"] == receipts["backward"],
            "orientation window schedules agree")
    return receipts


def transformed_profile(blocks: int) -> dict[int, int]:
    require(0 <= blocks <= BASE_PROFILE[1] // 9,
            "Toom block count fits nine original products per block")
    profile = dict(BASE_PROFILE)
    profile[1] -= 4 * blocks
    return dict(sorted(profile.items()))


def ceiling(profile: dict[int, int]) -> tuple[Q, Q]:
    return tuple(C.ceiling(profile, 73, 896, 9, 64, grid=GRID))


def verify_ceilings() -> dict:
    expected = {
        0: (
            Q(52814190909, 31250000000000),
            Q(1690054109089, 10**15),
        ),
        63: (
            Q(886830512167, 500000000000000),
            Q(354732204867, 200000000000000),
        ),
        64: (
            Q(887527462991, 500000000000000),
            Q(1775054925983, 10**15),
        ),
        209: (
            Q(500843727417, 250000000000000),
            Q(2003374909669, 10**15),
        ),
        210: (
            Q(1002576944357, 500000000000000),
            Q(401030777743, 200000000000000),
        ),
        254: (
            Q(260836020423, 125000000000000),
            Q(417337632677, 200000000000000),
        ),
    }
    brackets = {}
    for blocks, wanted in expected.items():
        got = ceiling(transformed_profile(blocks))
        require(got == wanted, "exact ceiling bracket at " + str(blocks))
        brackets[blocks] = got

    five_percent = brackets[0][1] * Q(105, 100)
    require(brackets[63][1] < five_percent, "63 blocks miss five-percent gate")
    require(brackets[64][0] > five_percent, "64 blocks pass five-percent gate")
    require(brackets[209][1] < TARGET_A, "209 blocks miss complex kappa 0.002")
    require(brackets[210][0] > TARGET_A, "210 blocks pass complex kappa 0.002")
    require(brackets[254][0] > TARGET_A, "254 ideal blocks pass complex threshold")
    require(sum(r * n for r, n in transformed_profile(254).items()) == 4570,
            "254-block rank mass")
    return brackets


def main() -> None:
    programs, word = source_objects()
    selected, bit_a = selected_baseline()
    for orientation, events in programs.items():
        require(profile_of(events) == BASE_PROFILE,
                orientation + " selected paid profile")

    toom = check_toom3()
    windows = dependency_window_batches(programs, word)
    brackets = verify_ceilings()
    bit_kappa_cap = bit_a / (1 + bit_a)
    require(bit_kappa_cap < TARGET_KAPPA,
            "unchanged bit side remains below overall target")

    print(
        "PASS_COMPLEX_TOOM3_FIVE_PRODUCT_SCREEN "
        f"basis_pairs={toom['basis_pairs']} products={toom['products']} "
        f"source_groups={windows['forward']['groups']} "
        f"min_blocks_5pct=64 min_blocks_complex_kappa002=210 "
        f"a254_hi={float(brackets[254][1]):.15f} "
        f"complex_kappa254_hi={float(brackets[254][1] / (1 + brackets[254][1])):.15f} "
        f"bit_kappa_cap={float(bit_kappa_cap):.15f} controls=3 no_new_kappa"
    )


if __name__ == "__main__":
    main()
