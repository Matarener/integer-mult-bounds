"""Behavioural controls for the admissible-region package.

Every control either accepts the unmodified computation or must reject a
corrupted one.  Standard library only.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name="region_under_test"):
    spec = importlib.util.spec_from_file_location(name, ROOT / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def must_reject(module, label):
    try:
        module.verify()
    except ValueError:
        return
    raise ValueError("control did not reject: " + label)


def control_positive():
    module = load("region_positive")
    receipt = module.verify()
    require(receipt["region"]["shapes_checked"] == 90, "shape count")
    require(receipt["region"]["shapes_where_region_beats_parity_rounded"] == 10,
            "strict shape count")
    require(receipt["floor_effect_at_ten"]["4,0"]["removed_by_floor"] == [[0, 10], [2, 8]],
            "(4,0) removal")
    require(receipt["floor_effect_at_ten"]["2,2"]["admissible"] ==
            [[2, 8], [4, 6], [6, 4], [8, 2]], "(2,2) splits")
    require(receipt["three_targets"]["2,1"]["region_min"] == 7, "mixed triple region")
    require(receipt["three_targets"]["3,0"]["delivered_minimum"] == 9, "triple truth")
    require(receipt["equality"]["boundary_cases"] == 8, "boundary case count")
    require(receipt["fixture_2_8"]["matches_forced_boundary"] is True, "fixture profile")
    require(receipt["fixture_2_8"]["is_a_word"] is False, "fixture scope label")
    return receipt


def control_floorless_region():
    module = load("region_floorless")
    original = module.splits

    def no_floor(t_i, t_j, n, floor=True):
        return original(t_i, t_j, n, False)

    module.splits = no_floor
    must_reject(module, "region without the rank floor")


def control_parityless_region():
    module = load("region_parityless")
    original = module.splits

    def no_parity(t_i, t_j, n, floor=True):
        require(floor, "control expects the floor")
        out = []
        for n_i in range(n + 1):
            n_j = n - n_i
            if n_i < t_i or n_j < t_j:
                continue
            t = t_i + t_j
            if 2 * n + n_i < 6 * t - t_i:
                continue
            if 2 * n + n_j < 6 * t - t_j:
                continue
            out.append((n_i, n_j))
        return out

    module.splits = no_parity
    must_reject(module, "region without parity classes")


def control_zero_rank():
    module = load("region_zero_rank")
    module.rank_f2 = lambda rows, columns: 0
    must_reject(module, "constant-zero rank routine")


def control_corrupt_fixture():
    module = load("region_corrupt_fixture")
    original = module.fixture_2_8

    def dropped_column():
        x_i, y_i, x_j, y_j = original()
        return x_i[:1], y_i[:1], x_j, y_j

    module.fixture_2_8 = dropped_column
    must_reject(module, "fixture with a dropped minority column")


def control_range_and_shape():
    module = load("region_ranges")
    try:
        module.rank_f2([1 << 5], 4)
    except ValueError:
        pass
    else:
        raise ValueError("out-of-range F2 row was accepted")
    for bad in ((-1, 1), (1, -1)):
        try:
            module.splits(*bad, 4)
        except ValueError:
            continue
        raise ValueError("invalid shape was accepted")
    try:
        module.splits(0, 0, 4)
    except ValueError:
        pass
    else:
        raise ValueError("empty shape was accepted")


def control_receipt_round_trip():
    path = ROOT / "RESULT.json"
    require(path.exists(), "receipt is missing")
    data = json.loads(path.read_text())
    again = json.loads(json.dumps(data, indent=1, sort_keys=True))
    require(data == again, "receipt round trip")
    require(data["region"]["shapes_checked"] == 90, "receipt shape count")


def main():
    receipt = control_positive()
    control_floorless_region()
    control_parityless_region()
    control_zero_rank()
    control_corrupt_fixture()
    control_range_and_shape()
    control_receipt_round_trip()
    require(receipt["three_targets"]["3,0"]["region_min"] == 7, "final recheck")
    print("PASS admissible-region behavioural controls")
    return 0


if __name__ == "__main__":
    sys.exit(main())
