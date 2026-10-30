"""A fixed complete 64-axis, four-source Clifford projection calculation."""
import argparse
import json
import random
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from fast_gauss import gauss, require
from run_replay import authenticate, SOURCE


def circuits(n=64):
    require(type(n) is int and 1 <= n <= 64, "Workload width in 1..64")
    rng, result = random.Random(932 + n), []
    for _ in range(5):
        rows = [0] * n
        for i in range(n):
            for j in range(i + 1):
                if rng.randrange(2):
                    rows[i] ^= 1 << j
                    if i != j:
                        rows[j] ^= 1 << i
        linear = tuple((rows[i] >> i & 1) + 2 * rng.randrange(2) for i in range(n))
        result.append([("C", 1 << i, 1) for i in range(n)] +
                      [("D", tuple(rows), linear)])
    return result


def run(mode):
    authenticate()
    source = runpy.run_path(str(SOURCE / "verify.py"), run_name="projection_source")
    engine, original = source["C"], source["C"].gauss
    counts = {"gauss_calls": 0, "maximum_dimension": 0}

    def replacement(n, poly):
        counts["gauss_calls"] += 1
        counts["maximum_dimension"] = max(counts["maximum_dimension"], n)
        value = original(n, poly) if mode == "baseline" else gauss(n, poly)
        if mode == "differential":
            require(value == original(n, poly), "Projection Gauss differential")
        return value

    engine.gauss = replacement
    states = [engine.choi(64, circuit) for circuit in circuits()]
    result = engine.best_approximation(states[:4], states[4], 1)
    require(result["span_rank"] == 4, "Four independent source operators")
    print(json.dumps(result, default=source["encode"], sort_keys=True))
    print("PASS_BITSET_GAUSS_PROJECTION")
    print(json.dumps(dict(mode=mode, **counts), sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "bitset", "differential"), required=True)
    run(parser.parse_args().mode)
