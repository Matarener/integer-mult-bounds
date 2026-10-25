# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite evidence. Compare a typed receipt without rewriting it."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def compute():
    from runtime import installed

    with installed():
        import science
        import tape_checks

        return dict(
            census=science.census(),
            powers=tape_checks.powers(),
            plans=tape_checks.plans(),
            large_trial=tape_checks.large_trial(),
            large_plan=tape_checks.large_plan(),
            rejections=tape_checks.rejections(),
        )


def main():
    from runtime import read_json, require

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = compute()
    serial = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if args.emit_to:
        with args.emit_to.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = read_json(HERE / "RESULT.json")
        require(
            serial == json.dumps(expected, sort_keys=True, separators=(",", ":")),
            "complete typed science receipt",
        )
    print("PASS_SATURATED_BODY_BORROWING", sha256(serial.encode()).hexdigest())


if __name__ == "__main__":
    main()
