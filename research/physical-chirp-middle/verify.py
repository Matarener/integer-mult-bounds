"""Cold entry point for the complete physical chirp consumer checks."""
import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chirp_sources import opened, require


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    require(args.suite in ("kernel", "odometer", "middle", "failures", "sources", "budget", "phases"),
            "registered chirp suite")
    with opened():
        name = "chirp_check_" + args.suite
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == Path(__file__).resolve().parent / (name + ".py"),
                "package-local chirp checker")
        result = module.run()
    print(json.dumps({"status": "PASS_PHYSICAL_CHIRP_MIDDLE", "suite": args.suite,
                      "evidence": result}, sort_keys=True))


if __name__ == "__main__":
    main()
