#!/usr/bin/env python3
"""A restored or newly written third bank does not add an unpaid coordinate.

The selected nested contract starts at one coordinate. Fourier rank equals the
dimension difference, so unpaid count equals the initial dimension. A third
bank is not a second initial direction. Charging its excursion on the selected
word also fails the current saving.
"""

import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = (
    "PASS_THREE_BANK_RESTORED_UNPAID restored_adds_unpaid=false "
    "one_step_exceeds_selected=true no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_THREE_BANK_RESTORED_UNPAID " + message)


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
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "certificates/selected-result.json",
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/levers.py",
        "research/multipair-schedule-bound/README.md",
        "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def gaussian_rank(masks):
    rows = [mask for mask in masks if mask]
    rank = 0
    width = max((mask.bit_length() for mask in rows), default=0)
    for bit in range(width):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for other in range(len(rows)):
            if other != rank and (rows[other] >> bit) & 1:
                rows[other] ^= rows[rank]
        rank += 1
    return rank


def nested(initial, final):
    host = gaussian_rank(final)
    return all(gaussian_rank(list(final) + [vector]) == host for vector in initial)


def frame_account(initial, final):
    """Nested frames: unpaid is the initial dimension, and the climb is the difference."""
    require(nested(initial, final), "frame account requires a nested initial frame")
    initial_dim = gaussian_rank(initial)
    final_dim = gaussian_rank(final)
    return {
        "unpaid": initial_dim,
        "acquired": final_dim - initial_dim,
        "nested": True,
    }


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_ceiling", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fraction_pair(value):
    low, high = value
    return [f"{low.numerator}/{low.denominator}", f"{high.numerator}/{high.denominator}"]


def evaluate():
    authenticate()
    geometry = " ".join(
        (ROOT / "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt").read_text(
            encoding="utf-8").split())
    schedule = " ".join(
        (ROOT / "research/multipair-schedule-bound/README.md").read_text(encoding="utf-8").split())
    levers = (ROOT / "research/complex-local-word-ceiling/levers.py").read_text(encoding="utf-8")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require("The construction below has m=73" in geometry, "selected width moved")
    require("X_(-1)=C_q, Y_(-1)=I" in geometry, "initial level moved")
    require("The final Y endpoint is C_all C_q^(-1)." in geometry, "final endpoint moved")
    require(
        "a nested transition has Fourier rank equal to the dimension difference" in geometry,
        "nested rank rule moved",
    )
    require(
        "Can a cycle `X → Y → Z` leave more than one unpaid coordinate per family?" in schedule,
        "third-bank question moved",
    )
    require("WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}" in levers, "selected profile moved")
    require(selected["decimal"] == "0.001672660197076918", "selected decimal moved")
    kappa = Fraction(selected["kappa"])
    require(kappa == Fraction(836330098538459, 500000000000000000), "selected kappa moved")
    saving = kappa / (1 - kappa)

    full = [1 << bit for bit in range(73)]
    selected_frame = frame_account([1], full)
    require(selected_frame == {"unpaid": 1, "acquired": 72, "nested": True}, "selected frame count moved")

    # Dirty restored bank: same subspace at exit, no acquired data direction.
    restored = frame_account([0b010, 0b100], [0b010, 0b100])
    require(restored["acquired"] == 0 and restored["unpaid"] == 2, "restored bank was charged")
    # Those two directions are the bank's own frame, not the family's initial datum.
    family_after_restored_bank = frame_account([0b001], full)
    require(family_after_restored_bank["unpaid"] == 1, "restored bank raised the family count")

    # Copying the datum into a second bank acquires a paid direction. It does not
    # create a second initial coordinate.
    copied = frame_account([0b001], [0b001, 0b010])
    require(copied == {"unpaid": 1, "acquired": 1, "nested": True}, "copy changed the unpaid count")

    # Clearing the source and writing another bank erases the initial direction.
    require(not nested([0b001], [0b010]), "a cleared source was treated as nested")
    require(gaussian_rank([0b001, 0b010]) == 2, "erased and new directions were dependent")

    # Two unpaid coordinates are exactly a two-dimensional initial frame.
    plane = frame_account([0b001, 0b010], full)
    require(plane == {"unpaid": 2, "acquired": 71, "nested": True}, "plane count moved")
    require(plane["unpaid"] != copied["unpaid"], "copy was mistaken for a plane")

    ceiling = load_ceiling()
    word = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    width, families, stages, centre = 73, 896, 9, 64
    grid = Fraction(1, 10 ** 12)
    per_call = Fraction(families, stages)
    base = ceiling.ceiling(word, width, families, stages, centre, grid=grid, unpaid=1)
    two_unpaid = ceiling.ceiling(word, width, families, stages, centre, grid=grid, unpaid=2)
    one_step_word = dict(word)
    one_step_word[1] += per_call
    two_step_word = dict(word)
    two_step_word[1] += 2 * per_call
    one_step = ceiling.ceiling(one_step_word, width, families, stages, centre, grid=grid, unpaid=1)
    two_step = ceiling.ceiling(two_step_word, width, families, stages, centre, grid=grid, unpaid=1)
    base_model = ceiling.model(word, width, families, stages, centre, unpaid=1)
    one_model = ceiling.model(one_step_word, width, families, stages, centre, unpaid=1)
    two_model = ceiling.model(word, width, families, stages, centre, unpaid=2)
    two_step_model = ceiling.model(two_step_word, width, families, stages, centre, unpaid=1)
    require(base_model["deficit"] == one_model["deficit"] == Fraction(320, 9), "deficit changed without unpaid")
    require(two_model["deficit"] == Fraction(1216, 9), "two-unpaid deficit moved")
    require(base_model["local_mass"] == 5586, "local mass moved")
    require(base_model["idle_mass"] == 1646, "base idle mass moved")
    require(one_model["idle_mass"] == two_model["idle_mass"] == Fraction(13918, 9), "shared idle mass moved")
    require(two_step_model["idle_mass"] == Fraction(13022, 9), "two-step idle mass moved")
    require(one_model["idle_mass"] >= 0, "one-step excursion exceeds the coverage budget")
    require(one_step[1] < base[1] and two_step[1] < one_step[1], "excursion did not lower the ceiling")
    require(two_unpaid[1] > base[1], "two-unpaid lever did not raise the ceiling")
    ratio = two_unpaid[1] / base[1]
    require(f"{float(ratio):.2f}" == "3.77", "two-unpaid lever ratio moved")
    base_at_selected = ceiling.relax(word, width, families, stages, centre, saving, unpaid=1)
    one_at_selected = ceiling.relax(one_step_word, width, families, stages, centre, saving, unpaid=1)
    two_at_selected = ceiling.relax(two_step_word, width, families, stages, centre, saving, unpaid=1)
    require(base_at_selected[1] < 1, "selected word is not under its ceiling at the selected saving")
    require(one_at_selected[0] > 1 and two_at_selected[0] > 1, "excursion still meets the selected saving")

    # Rejection controls: the false claims this package exists to stop.
    require(not (restored["acquired"] > 0), "control failed to reject a charged restoration")
    require(copied["unpaid"] != 2, "control failed to reject a copied second unpaid coordinate")
    require(one_at_selected[0] > 1, "control failed to reject a free one-step excursion")

    return {
        "selected_unpaid": selected_frame["unpaid"],
        "selected_acquired": selected_frame["acquired"],
        "restored_bank_acquired": restored["acquired"],
        "family_unpaid_after_restored_bank": family_after_restored_bank["unpaid"],
        "copied_second_bank_unpaid": copied["unpaid"],
        "copied_second_bank_acquired": copied["acquired"],
        "cleared_source_nested": False,
        "plane_unpaid": plane["unpaid"],
        "deficit": "320/9",
        "two_unpaid_deficit": "1216/9",
        "selected_saving": f"{saving.numerator}/{saving.denominator}",
        "base_idle": "1646",
        "one_step_idle": "13918/9",
        "two_step_idle": "13022/9",
        "two_unpaid_idle": "13918/9",
        "base_ceiling": fraction_pair(base),
        "two_unpaid_ceiling": fraction_pair(two_unpaid),
        "two_unpaid_ratio": f"{ratio.numerator}/{ratio.denominator}",
        "one_step_ceiling": fraction_pair(one_step),
        "two_step_ceiling": fraction_pair(two_step),
        "one_step_exceeds_selected": True,
        "two_step_exceeds_selected": True,
        "restored_adds_unpaid": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
