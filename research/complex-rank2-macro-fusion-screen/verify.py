#!/usr/bin/env python3
"""Screen direct rank-1-pair to rank-2 macro substitutions in the selected trace."""
from __future__ import annotations

import collections
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PROGRAM_MEMBER = (
    "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
)
PROGRAM_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
RECIPE_MEMBER = (
    "candidate/strict/global/base/providers/gauge44/CLIFFORD-RECIPES.json"
)
RECIPE_SHA256 = "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731"
WORD_MEMBER = (
    "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
)
WORD_SHA256 = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
SELECTED = ROOT / "certificates/selected-result.json"
SELECTED_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
SELECTED_KAPPA = "0.001672660197076918"
RESULT = Path(__file__).with_name("RESULT.json")
EXPECTED_TOUCH_HISTOGRAM = {1: 10, 2: 5, 5: 20}
EXPECTED_PHASE_PAIRS = {
    ("A", "A"): 20,
    ("B", "B"): 8,
    ("cleanup_tail", "final"): 7,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_sources() -> tuple[dict[str, list], list[dict], dict, str]:
    archive_bytes = ARCHIVE.read_bytes()
    require(digest(archive_bytes) == ARCHIVE_SHA256, "selected archive pin")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        names = {member.name for member in archive.getmembers()}
        require(PROGRAM_MEMBER in names, "selected local program present")
        require(RECIPE_MEMBER in names, "selected child recipes present")
        require(WORD_MEMBER in names, "selected canonical word present")
        program_bytes = archive.extractfile(PROGRAM_MEMBER).read()
        recipe_bytes = archive.extractfile(RECIPE_MEMBER).read()
        word_bytes = archive.extractfile(WORD_MEMBER).read()
    require(digest(program_bytes) == PROGRAM_SHA256, "local program member pin")
    require(digest(recipe_bytes) == RECIPE_SHA256, "child recipe member pin")
    require(digest(word_bytes) == WORD_SHA256, "canonical word member pin")
    programs = json.loads(gzip.decompress(program_bytes))
    recipes = json.loads(recipe_bytes)["children"]
    word = json.loads(gzip.decompress(word_bytes))
    require(set(programs) == {"forward", "backward"}, "both orientations present")
    require(len(recipes) == 2896, "selected recipe inventory")

    keys = [(entry["old"], entry["new"], entry["rank"]) for entry in recipes]
    require(len(set(keys)) == len(keys), "child recipe transitions are unique")

    selected_bytes = SELECTED.read_bytes()
    require(digest(selected_bytes) == SELECTED_SHA256, "selected record pin")
    selected = json.loads(selected_bytes)
    require(selected["decimal"] == SELECTED_KAPPA, "selected kappa record")
    return programs, recipes, word, selected["decimal"]


def frame_contains(frames: list[list[int]], old: int, new: int) -> bool:
    for vector in frames[old]:
        reduced = vector
        for target in frames[new]:
            if target and (reduced >> (target.bit_length() - 1)) & 1:
                reduced ^= target
        if reduced:
            return False
    return True


def gaussian_add(left: tuple[Q, Q], right: tuple[Q, Q]) -> tuple[Q, Q]:
    return left[0] + right[0], left[1] + right[1]


def gaussian_mul(left: tuple[Q, Q], right: tuple[Q, Q]) -> tuple[Q, Q]:
    return (left[0] * right[0] - left[1] * right[1],
            left[0] * right[1] + left[1] * right[0])


def gaussian_phase(value: tuple[Q, Q], exponent: int) -> tuple[Q, Q]:
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[exponent % 4]


def monomial_value(recipe: dict, value: int) -> tuple[int, int]:
    """Apply one pinned affine-Clifford monomial, retaining its exact phase."""
    rows = recipe["matrix_rows"]
    target = recipe["offset"] ^ sum(
        ((row & value).bit_count() & 1) << index
        for index, row in enumerate(rows)
    )
    exponent = recipe["phase"] + sum(
        recipe["linear_Z4"][index]
        for index in range(len(rows)) if value >> index & 1
    )
    exponent += 2 * sum(
        1 for i in range(len(rows)) for j in range(i + 1, len(rows))
        if value >> i & 1 and value >> j & 1
        and recipe["quadratic_rows"][i] >> j & 1
    )
    return target, exponent % 4


def child_operator(recipe: dict) -> list[dict[int, tuple[Q, Q]]]:
    """Build all exact columns of left * C^rank * right over Q(i)."""
    rank = recipe["rank"]
    left, right = recipe["left"], recipe["right"]
    dimension = len(right["matrix_rows"])
    require(len(left["matrix_rows"]) == dimension, "child monomial dimensions")
    columns = []
    for source in range(1 << dimension):
        middle, right_phase = monomial_value(right, source)
        column: dict[int, tuple[Q, Q]] = {}
        for flip in range(1 << rank):
            coefficient = (Q(1), Q(0))
            for axis in range(rank):
                gate_coefficient = (Q(1, 2), Q(1, 2) if not (flip >> axis & 1)
                                    else Q(-1, 2))
                coefficient = gaussian_mul(coefficient, gate_coefficient)
            target, left_phase = monomial_value(left, middle ^ flip)
            value = gaussian_phase(coefficient, right_phase + left_phase)
            column[target] = gaussian_add(column.get(target, (Q(0), Q(0))), value)
        columns.append({target: value for target, value in column.items()
                        if value != (Q(0), Q(0))})
    return columns


def compose_operators(after: list[dict], before: list[dict]) -> list[dict]:
    """Return after * before as exact sparse columns."""
    require(len(after) == len(before), "operator dimensions")
    result = []
    for column in before:
        output: dict[int, tuple[Q, Q]] = {}
        for middle, left_value in column.items():
            for target, right_value in after[middle].items():
                output[target] = gaussian_add(
                    output.get(target, (Q(0), Q(0))),
                    gaussian_mul(right_value, left_value),
                )
        result.append({target: value for target, value in output.items()
                       if value != (Q(0), Q(0))})
    return result


def operator_digest(columns: list[dict[int, tuple[Q, Q]]]) -> str:
    canonical = [
        [[target, str(value[0]), str(value[1])]
         for target, value in sorted(column.items())]
        for column in columns
    ]
    return digest(json.dumps(canonical, separators=(",", ":")).encode())


def verify_exact_macro_candidate(programs: dict[str, list], recipes: list[dict]) -> dict:
    """Test the rank-1 pair composition and retain the intervening ADD obligation."""
    expected_climbs = (
        ["climb", "B", 195, 0, 2, 1],
        ["climb", "B", 195, 2, 252, 1],
    )
    expected_adds = {
        "forward": ["scalar", ["add", ["L", 195], ["L", 521], 1, 2], 2],
        "backward": ["scalar", ["add", ["L", 521], ["L", 195], -1, 2], 2],
    }
    interval_counts = {}
    for orientation, events in programs.items():
        first_index, second_index = 12806, 13402
        require(events[first_index] == expected_climbs[0],
                orientation + " exact first candidate event")
        require(events[second_index] == expected_climbs[1],
                orientation + " exact second candidate event")
        require(events[first_index + 1] == expected_adds[orientation],
                orientation + " exact intervening ADD")
        window = events[first_index:second_index + 1]
        tags = collections.Counter(event[0] for event in window)
        require(tags == {"climb": 139, "scalar": 458},
                orientation + " complete candidate window")
        for register, expected_indices in ((195, [first_index, first_index + 1,
                                                  second_index]),
                                          (521, [first_index + 1])):
            touches = [first_index + offset for offset, event in enumerate(window)
                       if local_register_touched(event, register)]
            require(touches == expected_indices,
                    orientation + f" exact L{register} window touches")
        interval_counts[orientation] = {
            "events": len(window),
            "climbs": tags["climb"],
            "scalar_events": tags["scalar"],
            "first_child": first_index,
            "intervening_add": first_index + 1,
            "second_child": second_index,
        }

    by_key = {(entry["old"], entry["new"], entry["rank"]): entry
              for entry in recipes}
    first = child_operator(by_key[(0, 2, 1)])
    second = child_operator(by_key[(2, 252, 1)])
    direct = child_operator(by_key[(0, 252, 2)])
    composed = compose_operators(second, first)
    require(len(composed) == len(direct) == 512,
            "complete 512-vector basis covered")
    mismatches = [index for index, (left, right) in enumerate(zip(composed, direct))
                  if left != right]
    require(not mismatches,
            "successive rank-one operators equal the direct rank-two recipe")

    # The equality contracts only the product of the two child maps. The ADD
    # consumes an intermediate value: forward it injects B*y into L195; backward
    # it emits A*x into L521. A single-output direct recipe omits that block.
    require(all(second[column] for column in range(512)),
            "forward add-source contribution is nonzero on every basis vector")
    require(all(first[column] for column in range(512)),
            "backward intermediate tap is nonzero on every basis vector")
    return {
        "status": "PASS_RANK1_PAIR_EQUALS_RANK2_BUT_ADD_TAP_BLOCKS_DIRECT_REPLACEMENT",
        "source_archive_sha256": ARCHIVE_SHA256,
        "selected_kappa": SELECTED_KAPPA,
        "candidate": {
            "path": [0, 2, 252],
            "child_rank": 1,
            "event_indices": {"first": 12806, "add": 12807, "second": 13402},
            "windows_per_orientation": interval_counts,
        },
        "operator_dimension": 512,
        "basis_columns_checked": len(composed),
        "composition_equals_direct_rank2": True,
        "first_recipe": [0, 2, 1],
        "second_recipe": [2, 252, 1],
        "direct_recipe": [0, 252, 2],
        "operator_sha256": {
            "first_rank1": operator_digest(first),
            "second_rank1": operator_digest(second),
            "direct_rank2": operator_digest(direct),
            "composed_rank1_pair": operator_digest(composed),
        },
        "max_nonzeros_per_column": {
            "first_rank1": max(map(len, first)),
            "second_rank1": max(map(len, second)),
            "direct_rank2": max(map(len, direct)),
        },
        "unabsorbed_intermediate": {
            "forward": {
                "required_block": "(1/2)*second_rank1*L521",
                "nonzero_basis_inputs": 512,
                "max_nonzeros_per_basis_column": max(map(len, second)),
                "absent_from_direct_rank2_input": True,
            },
            "backward": {
                "required_tap": "(-1/2)*first_rank1*L195 into L521",
                "nonzero_basis_inputs": 512,
                "max_nonzeros_per_basis_column": max(map(len, first)),
                "emitted_by_direct_rank2_recipe": False,
            },
        },
        "ideal_charge_screen": {
            "original_rank_profile": [1, 1],
            "split_rank2_plus_rank1_tap_profile": [2, 1],
            "comparison_for_0_lt_a_lt_1": "2^(1-a)+1 > 2",
            "multioutput_rank2_tap": "changed provider interface; not in pinned recipes or priced",
        },
    }


def replay_frames(events: list, word: dict) -> None:
    """Check climb order and the frame required by every scalar operation."""
    frames = word["frames"]
    current = list(word["start"])
    phase = None
    for event in events:
        tag = event[0]
        if tag == "phase":
            phase = event[1]
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
    require(current == word["final"], "terminal frame inventory")


def local_register_touched(event: list, register: int) -> bool:
    tag = event[0]
    if tag in ("climb", "adapter", "residual_adapter"):
        return event[2] == register
    if tag != "scalar":
        return False

    operation = event[1]
    kind = operation[0]
    require(kind in ("scale", "add", "copy", "clear"), "known scalar event")
    touched = {tuple(operation[1])}
    if kind in ("add", "copy"):
        touched.add(tuple(operation[2]))
    return ("L", register) in touched


def screen_orientation(
    events: list,
    recipe_keys: set[tuple[int, int, int]],
    target_rank: int = 2,
    word: dict | None = None,
) -> dict:
    if word is not None:
        replay_frames(events, word)
    last_by_register: dict[int, tuple[int, str, int, int, int, int]] = {}
    rank_one_successors = 0
    candidates = []

    for index, event in enumerate(events):
        if event[0] != "climb":
            continue
        _, phase, register, old, new, rank = event
        previous = last_by_register.get(register)
        if previous is not None and previous[4] == old:
            if previous[5] == 1 and rank == 1:
                rank_one_successors += 1
                if (previous[3], new, target_rank) in recipe_keys:
                    intervening = [
                        events[j]
                        for j in range(previous[0] + 1, index)
                        if local_register_touched(events[j], register)
                    ]
                    candidates.append({
                        "first_index": previous[0],
                        "second_index": index,
                        "first_phase": previous[1],
                        "second_phase": phase,
                        "register": register,
                        "old": previous[3],
                        "middle": old,
                        "new": new,
                        "intervening_touches": intervening,
                    })
        last_by_register[register] = (index, phase, register, old, new, rank)

    touch_histogram = collections.Counter(
        len(candidate["intervening_touches"]) for candidate in candidates
    )
    phase_pairs = collections.Counter(
        (candidate["first_phase"], candidate["second_phase"])
        for candidate in candidates
    )
    return {
        "rank_one_successors": rank_one_successors,
        "candidates": candidates,
        "touch_histogram": dict(sorted(touch_histogram.items())),
        "phase_pairs": dict(sorted(phase_pairs.items())),
        "directly_fusible": sum(not candidate["intervening_touches"]
                                 for candidate in candidates),
        "intervening_adds": [
            (candidate, event)
            for candidate in candidates
            for event in candidate["intervening_touches"]
            if event[0] == "scalar" and event[1][0] == "add"
        ],
    }


def main() -> None:
    programs, recipes, word, selected_kappa = load_sources()
    recipe_keys = {
        (entry["old"], entry["new"], entry["rank"])
        for entry in recipes
    }

    receipts = {
        orientation: screen_orientation(events, recipe_keys, word=word)
        for orientation, events in programs.items()
    }
    for orientation, receipt in receipts.items():
        rank_one_climbs = sum(
            event[0] == "climb" and event[5] == 1
            for event in programs[orientation]
        )
        require(rank_one_climbs == 2412,
                orientation + " selected rank-one child count")
        require(receipt["rank_one_successors"] == 1441,
                orientation + " rank-one successor count")
        require(len(receipt["candidates"]) == 35,
                orientation + " direct rank-two recipe candidates")
        require(receipt["touch_histogram"] == EXPECTED_TOUCH_HISTOGRAM,
                orientation + " scalar-interference histogram")
        require(receipt["phase_pairs"] == EXPECTED_PHASE_PAIRS,
                orientation + " candidate phase pairs")
        require(receipt["directly_fusible"] == 0,
                orientation + " no conflict-free direct substitution")
        require(all(
            event[0] == "scalar"
            for candidate in receipt["candidates"]
            for event in candidate["intervening_touches"]
        ), orientation + " all candidate conflicts are scalar events")

    require(receipts["forward"]["touch_histogram"]
            == receipts["backward"]["touch_histogram"],
            "orientation screens agree")

    # Linearity suggests moving the post-add climb to the add's source. Check
    # whether that register already receives the exact same child transition.
    partner_matches = {"forward": [], "backward": []}
    for orientation, events in programs.items():
        climb_keys_by_register = collections.defaultdict(set)
        for event in events:
            if event[0] == "climb" and event[5] == 1:
                climb_keys_by_register[event[2]].add((event[3], event[4]))
        for candidate, event in receipts[orientation]["intervening_adds"]:
            operation = event[1]
            target, source = operation[1], operation[2]
            require(candidate["middle"] == event[2],
                    orientation + " addition uses the middle frame")
            require(target[0] == source[0] == "L",
                    orientation + " addition uses local data registers")
            partner = source[1] if target[1] == candidate["register"] else target[1]
            transition = (event[2], candidate["new"])
            partner_matches[orientation].append(
                transition in climb_keys_by_register[partner]
            )
    require(len(partner_matches["forward"]) == 100,
            "forward candidate/add instances")
    require(len(partner_matches["backward"]) == 100,
            "backward candidate/add instances")
    require(not any(partner_matches["forward"] + partner_matches["backward"]),
            "no add source has a reusable same-key rank-one transition")

    macro = verify_exact_macro_candidate(programs, recipes)
    require(RESULT.is_file(), "exact macro result record exists")
    require(json.loads(RESULT.read_text()) == macro,
            "exact macro result matches full-basis replay")

    # Positive control: this exact endpoint pair has a direct rank-two recipe.
    witness = (0, 27, 2)
    require(witness in recipe_keys, "rank-two endpoint positive control")
    witness_count = sum(
        candidate["old"] == witness[0] and candidate["new"] == witness[1]
        for candidate in receipts["forward"]["candidates"]
    )
    require(witness_count == 2, "rank-two witness multiplicity in the forward trace")

    # Negative controls: wrong target rank rejects all candidates; deleting the
    # one positive-control recipe rejects exactly its two occurrences.
    wrong_rank = screen_orientation(
        programs["forward"], recipe_keys, target_rank=3, word=word
    )
    require(not wrong_rank["candidates"], "wrong-rank control rejects candidates")
    mutated_keys = recipe_keys - {witness}
    mutated = screen_orientation(programs["forward"], mutated_keys, word=word)
    require(len(mutated["candidates"]) == 33,
            "removed-recipe control rejects exactly two candidates")

    print(
        "PASS_COMPLEX_RANK2_MACRO_FUSION_SCREEN "
        "orientations=2 rank1_climbs=2412 rank1_successors=1441 "
        "direct_rank2_candidates=35 intervening_adds=100 "
        "reusable_same_key_partners=0 "
        "blocked_by_scalar=35 directly_fusible=0 "
        "touch_histogram=1:10,2:5,5:20 controls=3 "
        f"pair_composition_equals_rank2={macro['basis_columns_checked']}/512 "
        "intermediate_add_outputs=unabsorbed "
        f"selected_kappa={selected_kappa} no_new_kappa"
    )


if __name__ == "__main__":
    main()
