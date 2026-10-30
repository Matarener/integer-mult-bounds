"""Cold, read-only entry point for the physical Fourier checks."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fourier_sources import authenticate, opened


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True,
                        choices=("sources", "metadata", "forward", "opposite", "batch", "failures", "budget"))
    args = parser.parse_args()
    if args.suite == "sources":
        authenticate()
    with opened():
        import check_fourier
        result = getattr(check_fourier, args.suite)()
    print(json.dumps({"status": "PASS_PHYSICAL_SYNTHETIC_FOURIER", "suite": args.suite,
                      "evidence": result}, sort_keys=True))


if __name__ == "__main__":
    main()
