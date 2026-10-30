# SPDX-License-Identifier: Apache-2.0
"""Replay the scoped Count refinement and compare exact typed evidence."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks
import reference
from source import installed, require


def wire_integer(raw):
    number = int(raw)
    return raw if abs(number) > 2**53 - 1 else number


def wire(value):
    # JSON handles the bounded receipt structure; booleans never call parse_int.
    return json.loads(json.dumps(value), parse_int=wire_integer)


def science():
    with installed():
        result = dict(
            integer=reference.census(),
            plans=checks.plans(),
            thresholds=checks.thresholds(),
            large=checks.large_plan(),
            rejections=checks.rejections(),
        )
    return wire(result)


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "known bounded replay arguments")
    actual = science()
    if sys.argv[1:] != ["--emit"]:
        expected = json.loads((Path(__file__).parent / "RESULT.json").read_text())
        require(
            json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "typed complete strict-selector receipt",
        )
    print(
        json.dumps(
            dict(status="PASS_STRICT_COUNT_SELECTOR", result=actual), sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
