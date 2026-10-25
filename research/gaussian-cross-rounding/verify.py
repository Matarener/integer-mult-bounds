#!/usr/bin/env python3
"""Exact controls for the across-cell coefficient lemma; not a solver replay.

Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
The subtract-two-ulps repair is credited predecessor work; see README.md.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def floor(x):
    return x.numerator // x.denominator


def ceil(x):
    return -floor(-x)


def phase(s, t, i):
    """Exact nearest integer, including negative indices and half-integer ties."""
    q = (2 * t * i + s) // (2 * s)
    return q, t * i - s * q


def exponent_ratio(s, t, u, i, h):
    """Return j/k for exp(-pi*j/k), with the physical unwrapped offset h."""
    require(all(type(v) is int for v in (s, t, u, i, h)), "integer phase inputs required")
    require(s > 0 and t > s and u > 0, "require s>0, t>s, u>0")
    _, b = phase(s, t, i)
    _, c = phase(s, t, i + h)
    numerator = u * ((t * h + b) ** 2 - c ** 2)
    require(numerator >= 0, "negative Gaussian exponent")
    return F(numerator, s * s)


def repair(q, eta):
    require(eta > 0, "positive grid spacing required")
    require((q / eta).denominator == 1, "oracle output must be on the grid")
    return max(F(0), q - 2 * eta)


def check_bound(stored, lo, hi, eta):
    require(0 <= stored <= lo and hi - stored < 4 * eta, "downward/error bound")


def rejects_bound(stored, value, eta):
    try:
        check_bound(stored, value, value, eta)
    except ValueError:
        return
    raise ValueError("invalid output accepted by bound check")


def atan_bounds(inv, bits):
    """Consecutive alternating sums enclose atan(1/inv)."""
    total, power, sign, k = F(0), F(1, inv), 1, 0
    target = F(1, 2 ** bits)
    while True:
        term = power / (2 * k + 1)
        previous = total
        total += sign * term
        if term < target:
            return min(total, previous), max(total, previous)
        power /= inv * inv
        sign = -sign
        k += 1


@lru_cache(None)
def pi_bounds(bits):
    """Machin identity, with outward dyadic endpoints."""
    a, b = atan_bounds(5, bits + 8)
    c, d = atan_bounds(239, bits + 8)
    scale = 2 ** bits
    return F(floor((16 * a - 4 * d) * scale), scale), F(ceil((16 * b - 4 * c) * scale), scale)


def exp_minus_bounds(x, bits):
    """Alternating Taylor on [0,1/2], then outward-rounded squaring."""
    require(x >= 0, "nonnegative argument required")
    y, squarings = x, 0
    while y > F(1, 2):
        y /= 2
        squarings += 1
    scale = 2 ** bits
    target = F(1, scale)
    total, term, k = F(1), F(1), 0
    while True:
        k += 1
        previous = total
        term *= y / k
        total += (-1 if k % 2 else 1) * term
        if term < target:
            lo = F(floor(min(previous, total) * scale), scale)
            hi = F(ceil(max(previous, total) * scale), scale)
            break
    for _ in range(squarings):
        lo = F(floor(lo * lo * scale), scale)
        hi = min(F(1), F(ceil(hi * hi * scale), scale))
    return lo, hi


@lru_cache(None)
def gaussian_bounds(ratio, precision):
    """Separate rational enclosure oracle, not an implementation of HvH 2.13."""
    require(type(precision) is int and precision >= 2 and ratio >= 0, "invalid enclosure domain")
    eta = F(1, 2 ** precision)
    if ratio >= precision:
        # pi > 1 and e > 2 imply exp(-pi*ratio) < 2^-precision.
        return F(0), eta
    bits = precision + 32
    while True:
        pl, ph = pi_bounds(bits)
        lo, _ = exp_minus_bounds(ph * ratio, bits)
        _, hi = exp_minus_bounds(pl * ratio, bits)
        require(0 <= lo <= hi <= 1, "invalid exponential enclosure")
        if hi - lo < eta / 8:
            return lo, hi
        bits *= 2


def source_check():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    count = 0
    for entry in sources["files"]:
        if entry["usage"] == "input":
            raw = (ROOT / entry["path"]).read_bytes()
            require(sha256(raw).hexdigest() == entry["sha256"], "source hash mismatch: " + entry["path"])
            count += 1
    return count


def verify():
    pins = source_check()
    # Exact boundary models, not complete fine-prime multiplier instances.
    families = ((4, 5, 1, 1), (7, 8, 1, 2), (31, 32, 4, 3), (31, 34, 1, 3), (127, 128, 9, 4))
    records = []
    counts = dict(coefficients=0, positive=0, clipped=0, period_cuts=0, cell_cuts=0, ties=0,
                  unrepaired_overshoots=0, phase_identities=0, oracle_boundary_cases=0)
    for s, t, u, width in families:
        for i in range(s):
            qi, bi = phase(s, t, i)
            for h in range(-width, width + 1):
                qj, bj = phase(s, t, i + h)
                ratio = exponent_ratio(s, t, u, i, h)
                # Independent form uses the nearest-index jump.
                jump = qj - qi
                require(ratio == u * jump * (jump + F(2 * bj, s)), "phase identity")
                require(-s <= 2 * bi < s and -s <= 2 * bj < s, "nearest-index range")
                require((ratio == 0) == (h == 0), "strict exponent sign")
                counts["phase_identities"] += 1
                if h == 0:
                    continue  # Store the matrix diagonal as exactly one.
                period_cut = i // s != (i + h) // s
                cell_cut = qi - i != qj - (i + h)
                if not (period_cut or cell_cut):
                    continue
                for precision in (24, 64, 128):
                    eta = F(1, 2 ** precision)
                    lo, hi = gaussian_bounds(ratio, precision)
                    q = floor((lo + hi) / (2 * eta) + F(1, 2)) * eta
                    require(max(abs(q - lo), abs(q - hi)) < 2 * eta, "oracle error contract")
                    stored = repair(q, eta)
                    check_bound(stored, lo, hi, eta)
                    counts["coefficients"] += 1
                    counts["positive" if stored else "clipped"] += 1
                    counts["period_cuts"] += int(period_cut)
                    counts["cell_cuts"] += int(cell_cut)
                    counts["ties"] += int(2 * bi == -s or 2 * bj == -s)
                    counts["unrepaired_overshoots"] += int(q > hi)
                    records.append([s, t, u, i, h, precision, str(ratio), str(stored)])
    # Exhaust permitted oracle numerators on a rational test mesh, including
    # negative outputs and both sides of the clipping point.
    eta = F(1, 32)
    for n16 in range(513):
        value = n16 * eta / 16
        for m in range(floor(value / eta) - 3, ceil(value / eta) + 4):
            q = m * eta
            if abs(q - value) < 2 * eta:
                out = repair(q, eta)
                check_bound(out, value, value, eta)
                counts["oracle_boundary_cases"] += 1
    # Rational counterexamples to weakening each stated requirement.
    rejects_bound(3 * eta, F(3, 2) * eta, eta)  # no subtraction
    rejects_bound(3 * eta - eta, F(3, 2) * eta, eta)  # only one ulp
    rejects_bound(-2 * eta, eta / 4, eta)  # no clipping
    rejects_bound(repair(2 * eta, eta), 4 * eta, eta)  # nonstrict oracle error
    coarse = 2 * eta
    rerounded = floor(repair(3 * eta, eta) / coarse + F(1, 2)) * coarse
    rejects_bound(rerounded, F(3, 2) * eta, eta)  # later nearest-grid rounding
    wrong_ratio = F(5, 4)  # #4442's bare-kernel substitution.
    right_ratio = exponent_ratio(4, 5, 1, 1, 1)
    require(right_ratio == 2, "cross-cell square-gap witness")
    wl, wh = gaussian_bounds(wrong_ratio, 64)
    _, right_upper = gaussian_bounds(right_ratio, 64)
    unit = F(1, 2 ** 64)
    wrong_stored = repair(floor((wl + wh) / (2 * unit) + F(1, 2)) * unit, unit)
    require(wrong_stored > right_upper, "wrong kernel must violate the upper bound")
    for args in ((0, 1, 1, 0, 1), (4, 4, 1, 1, 1), (4, 5, 0, 1, 1), (4, 5, 1, 1, F(1, 2))):
        try:
            exponent_ratio(*args)
        except ValueError:
            pass
        else:
            raise ValueError("invalid domain accepted")
    require(all(counts[k] > 0 for k in counts), "missing positive/boundary coverage")
    return {"source_files": pins, **counts, "failure_controls": 10,
            "record_sha256": sha256(json.dumps(records, separators=(",", ":")).encode("ascii")).hexdigest()}


if __name__ == "__main__":
    result = verify()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2))
    else:
        require(not sys.argv[1:], "usage: verify.py [--emit]")
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(result == expected, "receipt mismatch")
        print("PASS_GAUSSIAN_CROSS_ROUNDING " + json.dumps(result, sort_keys=True))
