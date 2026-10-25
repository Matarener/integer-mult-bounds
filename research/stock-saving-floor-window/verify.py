#!/usr/bin/env python3
"""Exact denominator-unit window of the recorded bootstrap savings.

The twenty-four floor integers in the #2972 cutoff table do not select one
rational saving.  For each frozen branch this verifier computes the largest
integer interval of printed-denominator shifts that preserves every floor
margin and every routing room, proves that interval from the stage-7 slack,
and checks it by walking outward from the recorded saving.

No stock coefficient is chosen.  No kappa claim.
"""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/selected-bootstrap-stock-audit/RESULT.json"
AUDITED_RECEIPT_SHA256 = "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917"

# Published floor(s*L_j - L_{j-1}) and floor((1-s)*L_{j-1}), stages 2..7.
# Native stages 2 and 3 are the earlier published controls; the rest are #2972.
PUBLISHED = {
    "bootstrap": {
        2: (2851485324488315, 4777557234646),
        3: (1015784602045963452130, 1701909188404384116),
        4: (361852943409004062662957360, 606271101174941147673746),
        5: (128902872114845343680818492656976, 215971951161791423920760764122),
        6: (45919069451025819974017753079498485812, 76935687018952933071573623067467882),
        7: (16357749867431357886201881301751734180286423, 27406799379443943425326695785974298689751),
    },
    "conservative_bootstrap": {
        2: (2851485349075174, 4777557267681),
        3: (1015784614274199324771, 1701909205985694510),
        4: (361852949001065216196285881, 606271109508797681506267),
        5: (128902874547204377208495156774925, 215971954868265831114423996024),
        6: (45919070474352818766043006228287526563, 76935688602102847428409756325327327),
        7: (16357750287845003715345973449256621277195623, 27406800037024020153662277717993715829414),
    },
}

# Sharp windows in printed denominator units.  Both ends are stage-7 margins.
EXPECTED = {
    "bootstrap": {"k_min": -2, "k_max": 1, "binding": "margin7"},
    "conservative_bootstrap": {"k_min": -86, "k_max": 15, "binding": "margin7"},
}


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def floor_fraction(value):
    return value.numerator // value.denominator


def load_branch(branch):
    text = branch["common_saving"]
    num_text, den_text = text.split("/")
    numerator, denominator = int(num_text), int(den_text)
    saving = Fraction(numerator, denominator)
    require(saving.denominator == denominator, "printed saving denominator is not reduced")
    cutoffs = [int(stage["cutoff_log2"]) for stage in branch["stages"]]
    require(len(cutoffs) == 7, "expected seven cutoffs")
    gap = Fraction(branch["stages"][0]["gaps"]["stock"])
    require(
        all(Fraction(stage["gaps"]["stock"]) == gap for stage in branch["stages"]),
        "stock gap is not uniform",
    )
    require(saving == 1 - gap, "common_saving is not 1 - gaps.stock")
    require(
        all(stage["actual_stock_coefficient"] is None for stage in branch["stages"]),
        "a stock coefficient is already stored",
    )
    return saving, denominator, cutoffs


def floors(saving, cutoffs):
    table = {}
    for stage in range(2, 8):
        length = cutoffs[stage - 1]
        previous = cutoffs[stage - 2]
        margin = saving * length - previous
        room = (1 - saving) * previous
        table[stage] = (floor_fraction(margin), floor_fraction(room))
    return table


def margin_shift_range(saving, length, previous, denominator):
    """Integer k with floor(s*L - P) fixed, s = saving + k/denominator."""
    margin = saving * length - previous
    lower = margin - floor_fraction(margin)
    upper = floor_fraction(margin) + 1 - margin
    require(0 <= lower < 1 and 0 < upper <= 1, "margin slack left [0, 1)")
    down = lower * denominator / length
    up = upper * denominator / length
    # -lower <= k*L/D < upper.
    k_min = -floor_fraction(down)
    up_floor = floor_fraction(up)
    k_max = up_floor - 1 if up == up_floor else up_floor
    return k_min, k_max


def room_shift_range(saving, previous, denominator):
    """Integer k with floor((1-s)*P) fixed."""
    room = (1 - saving) * previous
    lower = room - floor_fraction(room)
    upper = floor_fraction(room) + 1 - room
    require(0 <= lower < 1 and 0 < upper <= 1, "room slack left [0, 1)")
    # Room falls as k rises: -upper < k*P/D <= lower.
    down = lower * denominator / previous
    up = upper * denominator / previous
    # k <= down.  For a nonnegative rational this is k <= floor(down),
    # whether or not down is an integer.
    k_max = floor_fraction(down)
    # k > -up, so k >= -floor(up) when up is not an integer, else -up + 1.
    up_floor = floor_fraction(up)
    k_min = -up_floor + 1 if up == up_floor else -up_floor
    return k_min, k_max


def constraint_ranges(saving, denominator, cutoffs):
    ranges = []
    for stage in range(2, 8):
        length = cutoffs[stage - 1]
        previous = cutoffs[stage - 2]
        k_min, k_max = margin_shift_range(saving, length, previous, denominator)
        ranges.append((k_min, k_max, f"margin{stage}"))
        k_min, k_max = room_shift_range(saving, previous, denominator)
        ranges.append((k_min, k_max, f"room{stage}"))
    return ranges


def intersect(ranges):
    lower = max(ranges, key=lambda item: (item[0], item[2]))
    upper = min(ranges, key=lambda item: (item[1], item[2]))
    require(lower[0] <= upper[1], "shift constraints have empty intersection")
    # Uniqueness of the binding constraint on each side.
    lower_names = [name for k_min, _, name in ranges if k_min == lower[0]]
    upper_names = [name for _, k_max, name in ranges if k_max == upper[1]]
    require(lower_names == ["margin7"], "stage-7 margin is not the unique lower bind: " + str(lower_names))
    require(upper_names == ["margin7"], "stage-7 margin is not the unique upper bind: " + str(upper_names))
    return lower[0], upper[1], "margin7"


def search_window(saving, denominator, cutoffs, base):
    unit = Fraction(1, denominator)

    def same(shift):
        return floors(saving + shift * unit, cutoffs) == base

    require(same(0), "recorded saving does not reproduce its own floors")
    k_min = 0
    while same(k_min - 1):
        k_min -= 1
        require(k_min > -100000, "downward search did not stop")
    k_max = 0
    while same(k_max + 1):
        k_max += 1
        require(k_max < 100000, "upward search did not stop")
    return k_min, k_max


def failing_stage(saving, denominator, cutoffs, base, shift):
    got = floors(saving + Fraction(shift, denominator), cutoffs)
    stages = [stage for stage in range(2, 8) if got[stage] != base[stage]]
    require(stages, "exterior shift left every floor unchanged")
    return stages[0], got[stages[0]], base[stages[0]]


def check_branch(name, branch):
    saving, denominator, cutoffs = load_branch(branch)
    base = floors(saving, cutoffs)
    for stage, pair in PUBLISHED[name].items():
        require(base[stage] == pair, f"{name} stage {stage} does not match the published floors")
    formula_min, formula_max, binding = intersect(constraint_ranges(saving, denominator, cutoffs))
    search_min, search_max = search_window(saving, denominator, cutoffs, base)
    expected = EXPECTED[name]
    require(formula_min == search_min == expected["k_min"], f"{name} lower window mismatch")
    require(formula_max == search_max == expected["k_max"], f"{name} upper window mismatch")
    require(binding == expected["binding"], f"{name} binding mismatch")
    # Every interior shift, including both endpoints, preserves all twenty-four-branch floors.
    for shift in range(formula_min, formula_max + 1):
        require(
            floors(saving + Fraction(shift, denominator), cutoffs) == base,
            f"{name} interior shift {shift} changed a floor",
        )
    low_stage, _, _ = failing_stage(saving, denominator, cutoffs, base, formula_min - 1)
    high_stage, _, _ = failing_stage(saving, denominator, cutoffs, base, formula_max + 1)
    require(low_stage == 7 and high_stage == 7, f"{name} exterior failure is not stage 7")
    # Stage 7 is necessary for this exact window: without it the interval grows.
    others = [item for item in constraint_ranges(saving, denominator, cutoffs) if item[2] != "margin7"]
    wider_min, wider_max, _ = intersect_loose(others)
    require(wider_min < formula_min and wider_max > formula_max, f"{name} window did not widen without stage 7")
    return formula_min, formula_max


def intersect_loose(ranges):
    lower = max(item[0] for item in ranges)
    upper = min(item[1] for item in ranges)
    require(lower <= upper, "loose intersection empty")
    return lower, upper, "loose"


def main():
    payload = RESULT.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == AUDITED_RECEIPT_SHA256, "receipt bytes drifted")
    receipt = json.loads(payload.decode("utf-8"))
    require(set(receipt["branches"]) == {"bootstrap", "conservative_bootstrap"}, "unexpected branches")
    native = check_branch("bootstrap", receipt["branches"]["bootstrap"])
    conservative = check_branch("conservative_bootstrap", receipt["branches"]["conservative_bootstrap"])
    # A gap-numerator mutation is not a denominator-unit shift and must leave the
    # recorded identity.  Replacing common_saving by the other branch's saving
    # must not keep the native floors.
    native_branch = receipt["branches"]["bootstrap"]
    other = receipt["branches"]["conservative_bootstrap"]["common_saving"]
    swapped = json.loads(payload.decode("utf-8"))
    swapped["branches"]["bootstrap"]["common_saving"] = other
    try:
        check_branch("bootstrap", swapped["branches"]["bootstrap"])
    except SystemExit:
        pass
    else:
        raise SystemExit("cross-branch saving passed the native window check")
    require(native_branch["common_saving"] != other, "branch savings unexpectedly equal")
    native_count = native[1] - native[0] + 1
    conservative_count = conservative[1] - conservative[0] + 1
    print(
        "PASS_STOCK_SAVING_FLOOR_WINDOW "
        f"native_k={native[0]}..{native[1]} native_shifts={native_count} "
        f"conservative_k={conservative[0]}..{conservative[1]} conservative_shifts={conservative_count} "
        "binding=stage7_margin coefficient=unresolved no_new_kappa"
    )


if __name__ == "__main__":
    main()
