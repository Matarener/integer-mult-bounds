"""Bounded independent literal oracles and complete consumer conformance."""
import argparse
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from fast_gauss import gauss, require

UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def literal(n, poly):
    real, imaginary = 0, 0
    for x in range(1 << n):
        phase = sum(c for mask, c in poly.items() if x & mask == mask) % 4
        a, b = UNITS[phase]
        real, imaginary = real + a, imaginary + b
    return real, imaginary


def exhaustive():
    count = 0
    for n in range(5):
        masks = [1 << i for i in range(n)] + [
            (1 << i) | (1 << j) for i in range(n) for j in range(i)]
        domains = [range(4)] * n + [(0, 2)] * (len(masks) - n)
        for values in product(*domains):
            poly = {mask: value for mask, value in zip(masks, values) if value}
            base = literal(n, poly)
            for constant in range(4):
                if constant:
                    poly[0] = constant
                else:
                    poly.pop(0, None)
                a, b = base
                expected = ((a, b), (-b, a), (-a, -b), (b, -a))[constant]
                require(gauss(n, poly) == expected, "Complete literal quadratic sum")
                count += 1
    return count


def larger():
    rng, count = random.Random(102932), 0
    for n in range(5, 13):
        for _ in range(8):
            poly = {1 << i: rng.randrange(1, 4) for i in range(n)}
            for i in range(n):
                for j in range(i):
                    if rng.randrange(2):
                        poly[(1 << i) | (1 << j)] = 2
            require(gauss(n, poly) == literal(n, poly), "Larger literal sum")
            count += 1
    for n in (0, 1, 2, 4, 8, 16, 32, 64, 128, 256):
        for a in range(4):
            poly = {(1 << i) | (1 << j): 2 for i in range(n) for j in range(i)}
            if a:
                poly.update({1 << i: a for i in range(n)})
            real = imaginary = 0
            for weight in range(n + 1):
                x, y = UNITS[(a * weight + weight * (weight - 1)) % 4]
                real += comb(n, weight) * x
                imaginary += comb(n, weight) * y
            require(gauss(n, poly) == (real, imaginary), "Independent binomial dense sum")
            count += 1
    return count


def controls():
    invalid = [(-1, {}), (257, {}), (True, {}), (1, []),
               (1, {2: 2}), (1, {True: 1}), (1, {1: 0}),
               (1, {1: True}), (2, {3: 1}), (3, {7: 2})]
    for n, poly in invalid:
        try:
            gauss(n, poly)
        except ValueError:
            pass
        else:
            raise ValueError("Invalid polynomial was accepted")
    witnesses = [(1, {1: 2}, (0, 0)), (1, {1: 3}, (1, -1)),
                 (2, {3: 2}, (2, 0)), (0, {0: 3}, (0, -1))]
    for n, poly, expected in witnesses:
        require(gauss(n, poly) == expected, "Cancellation, odd sign, pair and phase controls")
    return len(invalid), len(witnesses)


def consumer(program, mode):
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if sys.flags.optimize:
        command.append("-O")
    command += [str(ROOT / program), "--mode", mode]
    result = subprocess.run(command, check=False, capture_output=True, timeout=120)
    require(result.returncode == 0, result.stderr.decode())
    return dict(stdout_sha256=sha256(result.stdout).hexdigest(), work=json.loads(result.stderr))


def main(quick):
    result = dict(exhaustive=exhaustive(), larger=larger(), controls=controls())
    result["projection"] = consumer("run_projection.py", "differential")
    require(result["projection"]["work"]["gauss_calls"] == 25, "Complete projection work")
    if not quick:
        result["complete_replay"] = consumer("run_replay.py", "differential")
        require(result["complete_replay"]["work"]["gauss_calls"] == 82237,
                "Complete differential replay work")
    benchmark = json.loads((ROOT / "BENCHMARK.json").read_text())
    for name, digest in benchmark["source_hashes"].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "Changed benchmark implementation: " + name)
    require(all(row["stdout_sha256"] == result["projection"]["stdout_sha256"]
                for row in benchmark["samples"]), "Timed complete projection output")
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(ROOT.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_BITSET_GAUSS_ELIMINATION")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    main(parser.parse_args().quick)
