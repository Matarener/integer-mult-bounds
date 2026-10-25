"""Rejecting controls for the single-hub charge audit."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_verify():
    spec = importlib.util.spec_from_file_location("single_hub_verify", ROOT / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_error(function):
    try:
        function()
    except ValueError:
        return
    raise SystemExit("control failed to reject")


def main():
    verify = load_verify()
    result = verify.audit()
    if result["charge"] != 48 or result["excess"] != 8:
        raise SystemExit("audit totals moved")

    witness = verify.json.loads((ROOT / "WITNESS.json").read_text(encoding="utf-8"))
    broken = verify.json.loads(verify.json.dumps(witness))
    row = next(item for item in broken["rows"] if item["kind"] == "reader" and item["premise"] == "dxy" and item["mark"] == 0)
    row["u"] = ["1", "0", "0"]
    row["alive"] = "d"
    row["cost"] = 1
    expect_error(lambda: verify.check_record(row))

    expect_error(lambda: verify.gf4_transfer(replace_y=[(1, 0), (0, 0), (0, 0), (0, 0)]))

    # The coordinate count on dthx is three, and the relaxed minimum is one.
    if verify.bearing_count(0, "dthx") != 3:
        raise SystemExit("strict count")
    relaxed = next(item for item in witness["rows"] if item["premise"] == "dthx" and item["mark"] == 0)
    if relaxed["cost"] != 1:
        raise SystemExit("relaxed dthx")
    print("PASS_SINGLE_HUB_TWO_BEARING_CONTROLS")


if __name__ == "__main__":
    main()
