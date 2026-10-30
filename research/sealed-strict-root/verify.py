"""Run the source-closed physical strict-root witness and its controls."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("science", "controls"), default="science")
    args = parser.parse_args()
    with runtime.installed():
        if args.suite == "science":
            import verification

            result = {"schema_version": 1, "cases": verification.run()}
        else:
            import controls

            result = {"schema_version": 1, "controls": controls.run()}
        name = "RESULT.json" if args.suite == "science" else "CONTROLS.json"
        expected = (Path(__file__).resolve().parent / name).read_bytes()
        runtime.require(len(expected) <= 32000, "bounded published receipt")
        runtime.require(
            json.dumps(result, sort_keys=True)
            == json.dumps(json.loads(expected), sort_keys=True),
            "exact typed published receipt",
        )
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
