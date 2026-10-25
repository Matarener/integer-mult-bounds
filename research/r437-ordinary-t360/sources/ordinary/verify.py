"""Run one bounded, source-authenticated coupling check."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predecessor import authenticate, close, require


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True,
                        choices=("certificate", "setup", "runtime", "controls", "source-check"))
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    require(args.archive is None or args.suite == "source-check", "archive override only for source check")
    try:
        if args.suite == "source-check":
            authenticate(args.archive)
            result = {"status": "PASS_RETUNED_SOURCE_BYTES"}
        else:
            import importlib.util
            name = {"certificate": "certificate", "setup": "check_setup",
                    "runtime": "check_runtime", "controls": "test_controls"}[args.suite]
            spec = importlib.util.spec_from_file_location(
                "retuned_suite_" + name, Path(__file__).resolve().parent / (name + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            result = module.run()
        print(json.dumps(result, sort_keys=True))
    finally:
        close()
