"""Bounded conformance and a complete cold physical inverse workload."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from physical import fixture, run_case, runtime
from checks import identity, run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", action="store_true")
    parser.add_argument("--engine", choices=("baseline", "candidate"), default="candidate")
    parser.add_argument("--fixture", choices=("dense3", "rational3", "dense4", "identity4"), default="dense3")
    parser.add_argument("--instrument", action="store_true")
    args = parser.parse_args()
    with runtime():
        if args.workload:
            values = fixture(args.fixture)
            result = run_case(args.engine, values, args.instrument)
            identity(values, [[Fraction(v) for v in row] for row in result["output"]])
        else:
            result = run()
            paths = sorted(p for p in Path(__file__).resolve().parent.iterdir() if p.is_file())
            result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
