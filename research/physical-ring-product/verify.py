"""Cold entry point for the complete normalized-product consumer checks."""

import argparse
import importlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ring_sources import opened


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("words", "twiddles", "fft", "product", "convolution", "failures", "sources", "budget"), required=True)
    args = parser.parse_args()
    with opened():
        name = "ring_check_" + args.suite
        module = importlib.import_module(name)
        if Path(module.__file__).resolve() != Path(__file__).resolve().parent / (name + ".py"):
            raise ValueError("package-local registered checker: " + name)
        result = module.run()
    print(json.dumps({"status": "PASS_PHYSICAL_RING_PRODUCT", "suite": args.suite,
                      "evidence": result}, sort_keys=True))


if __name__ == "__main__":
    main()
