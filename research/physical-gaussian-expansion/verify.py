"""Cold entry point for physical Gaussian expansion checks."""
import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from expansion_sources import opened, require


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    require(args.suite in ("sources", "budget", "geometry", "block", "tile_overlap", "tile_wrap", "ownership", "production"), "declared expansion check")
    with opened():
        name = "expansion_check_tile" if args.suite.startswith("tile_") else "expansion_check_" + args.suite
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == Path(__file__).resolve().parent / (name + ".py"),
                "package-local expansion checker")
        evidence = module.run(args.suite.removeprefix("tile_")) if args.suite.startswith("tile_") else module.run()
        print(json.dumps({"status": "PASS_PHYSICAL_GAUSSIAN_EXPANSION", "suite": args.suite,
                          "evidence": evidence}, sort_keys=True))


if __name__ == "__main__":
    main()
