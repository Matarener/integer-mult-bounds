"""Exact corroboration of the new production Gaussian gap inequalities.

Produced by Nick Petalas. Apache-2.0.
The universal result is the written proof; no predecessor replay is run.

Rule 3 deviation: Fraction and JSON require managed allocation. The fixed
fixtures stream one row at a time; live source payloads are capped at 200000
bytes and arithmetic fixture inputs at p=65536. The registered checks exercise
these bounds. Any future configurable fixture inventory must validate its
capacity before iteration. No persistent resource or mutable shared state is used.
"""
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MAX_SOURCE_BYTES = 200_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(inputs) == 5, "five declared live source pins")
    for row in inputs:
        source = ROOT / row["path"]
        require(source.stat().st_size <= MAX_SOURCE_BYTES, "source size bound")
        payload = source.read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "source hash mismatch: " + row["path"])
    return len(inputs)


def rational_gap(p, u):
    require(type(p) is int and type(u) is int, "integer production parameters")
    require(101 <= p <= 65_536 and 1 <= u <= p, "finite fixture domain")
    require(u >= (8 * p - 1).bit_length(), "concentration guard")
    v = u * u
    tail = Fraction(5, (8 * p) ** 6)
    lower = Fraction(3 * v, 2 * p + 3 * v) - tail
    ideal = Fraction(v, p + v)
    difference = Fraction(p * v, (2 * p + 3 * v) * (p + v))
    require(lower - ideal == difference - tail, "new gap identity")
    require(difference >= Fraction(1, 10 * p ** 3), "uniform reserve")
    require(tail < Fraction(1, 10 * p ** 3), "tail fits reserve")
    require(lower > ideal, "new ideal gap")
    return ideal / 2


def algebra_cases():
    count = 0
    digest = hashlib.sha256()
    for p in range(101, 513):
        for u in range((8 * p - 1).bit_length(), p + 1):
            value = rational_gap(p, u)
            digest.update(f"{p},{u},{value}\n".encode())
            count += 1
    for p in range(513, 4097):
        minimum = (8 * p - 1).bit_length()
        for u in sorted({minimum, minimum + 1, max(minimum, isqrt(p)), p // 2, p}):
            value = rational_gap(p, u)
            digest.update(f"{p},{u},{value}\n".encode())
            count += 1
    return {"cases": count, "sha256": digest.hexdigest()}


def nearest(s, t, i):
    q = (2 * t * i + s) // (2 * s)
    return q, Fraction(t * i, s) - q


def geometry_cases():
    count = ties = wrapped = 0
    for s in (8, 16, 33, 64, 127):
        for t in sorted({s + 1, s + 2, s + 5}):
            rho = Fraction(t, s)
            for i in range(s):
                qi, bi = nearest(s, t, i)
                ties += int(bi == Fraction(-1, 2))
                for h in (-3, -1, 1, 3):
                    j = (i + h) % s
                    _, bj = nearest(s, t, j)
                    lifted_q, lifted_beta = nearest(s, t, i + h)
                    require(lifted_beta == bj, "physical-period beta identity")
                    exponent = (rho * h + bi) ** 2 - bj ** 2
                    d = lifted_q - qi
                    require(exponent == d * (d + 2 * bj), "original coordinates")
                    require(exponent > 0, "positive off-diagonal exponent")
                    wrapped += int(i + h != j)
                    count += 1
    require(ties > 0 and wrapped > 0, "ties and physical cuts exercised")
    return {"pairs": count, "tie_rows": ties, "wrapped_pairs": wrapped}


def proof_constants():
    require(32768 - 16 == 32752 > 7, "production rounding exponent")
    require(50 < 8 ** 6, "strict uniform tail reserve")
    require(7 - 2 >= 5, "linear exponent comparison for p >= 1")
    # p <= 2^p and p+1 <= 2^p have base p=1 and inductive ratio <=2.
    for p in range(1, 1025):
        require(32 * p * (p + 1) <= 2 ** (7 * p), "rounded error budget")
    example = rational_gap(16384, 32)
    require(1 / example == 34, "published metadata specialization")
    return {"induction_fixtures": 1024, "example_inverse_bound": str(1 / example),
            "predecessor_inverse_bound": 8 * 16384}


def rejection_controls():
    rejected = 0
    for p, u in ((100, 32), (101, 1), (101, 102), (101, 0), (101, 1.5)):
        try:
            rational_gap(p, u)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid parameter accepted")
    # Removing u*d<=p permits theta this small, at a nearest-index tie.
    p, u, s, t = 16384, 32, 10 ** 10, 10 ** 10 + 1
    _, beta = nearest(s, t, s // 2)
    _, next_beta = nearest(s, t, s // 2 + 1)
    exponent = (Fraction(t, s) + beta) ** 2 - next_beta ** 2
    require(beta == Fraction(-1, 2) and exponent == Fraction(2, s),
            "small-theta counterexample geometry")
    # gap <= 1-exp(-pi*u*exponent) < 4*u*exponent < claimed gap.
    require(4 * u * exponent < rational_gap(p, u), "similarity is essential")
    return {"rejected_domains": rejected, "removed_similarity_counterexamples": 1}


def main():
    result = {"status": "PASS_PRODUCTION_GAUSSIAN_ROWGAP",
              "claim_type": "scoped written proof with finite corroboration",
              "live_sources": authenticate_sources(),
              "algebra": algebra_cases(), "geometry": geometry_cases(),
              "constants": proof_constants(), "controls": rejection_controls()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
