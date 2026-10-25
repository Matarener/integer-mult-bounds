"""Read-only strict ordinary replay; no Git or network in scientific execution."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import HERE, installed, require


def science():
    with installed():
        from controls import run_controls
        from count_ownership import audited_counts
        from fixtures import run_cases
        from node_check import run_node

        with audited_counts() as observation:
            result = {
                "cases": run_cases(),
                "controls": run_controls(),
                "source_toys": [run_node(n) for n in (2, 3)],
            }
        result["outside_runtime_count_ownership"] = observation
    return result


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "known replay arguments")
    result = science()
    if sys.argv[1:] != ["--emit"]:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "complete typed strict ordinary receipt",
        )
    print(
        json.dumps(
            {"status": "PASS_STRICT_ORDINARY_CONSUMER", "result": result},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
