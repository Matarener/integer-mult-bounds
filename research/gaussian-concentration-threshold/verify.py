"""Exact finite controls for the Gaussian concentration threshold.

Produced by Nick Petalas. Apache-2.0.
The all-size theorem is in PROOF.md; no transcendental oracle is used here.
"""

from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json


BITS = 192
UNIT = 1 << BITS
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def times(left, right):
    """Outward multiplication of nonnegative UNIT-grid intervals."""
    require(0 <= left[0] <= left[1] <= UNIT, "left interval domain")
    require(0 <= right[0] <= right[1] <= UNIT, "right interval domain")
    return (left[0] * right[0] // UNIT,
            (left[1] * right[1] + UNIT - 1) // UNIT)


def root(interval):
    require(0 <= interval[0] <= interval[1] <= UNIT, "root interval domain")
    lower = isqrt(interval[0] * UNIT)
    upper = isqrt(interval[1] * UNIT)
    upper += upper * upper != interval[1] * UNIT
    return lower, upper


def power(interval, exponent):
    require(isinstance(exponent, int) and 0 <= exponent < 1 << 24,
            "bounded nonnegative interval power")
    result = (UNIT, UNIT)
    base = interval
    for _ in range(exponent.bit_length()):
        if exponent & 1:
            result = times(result, base)
        exponent >>= 1
        base = times(base, base)
    require(exponent == 0, "power consumes every exponent bit")
    return result


def decay(k, exponent):
    """Enclose exp(-a*exponent), a=k*log(2), for dyadic exponent."""
    require(isinstance(k, int) and 1 <= k <= 16, "dyadic decay parameter")
    require(isinstance(exponent, Fraction) and exponent >= 0,
            "nonnegative exact decay exponent")
    exponent *= k
    whole, remainder = divmod(exponent.numerator, exponent.denominator)
    denominator = exponent.denominator
    require(denominator <= 1 << 24 and denominator & (denominator - 1) == 0,
            "bounded power-of-two exponent denominator")
    if whole >= BITS:
        return (1, 1) if whole == BITS and remainder == 0 else (0, 1)
    base = (UNIT // 2, UNIT // 2)
    for _ in range(denominator.bit_length() - 1):
        base = root(base)
    low, high = power(base, remainder)
    shift = 1 << whole
    return low // shift, (high + shift - 1) // shift


def offset(s, index):
    rho = Fraction(s + 1, s)
    nearest = (2 * (s + 1) * index + s) // (2 * s)
    beta = rho * index - nearest
    require(-Fraction(1, 2) <= beta < Fraction(1, 2), "half-up offset range")
    return beta


def exponent(s, index, displacement):
    rho = Fraction(s + 1, s)
    result = ((rho * displacement + offset(s, index)) ** 2
              - offset(s, index + displacement) ** 2)
    require(displacement == 0 or result > 0, "strict off-diagonal decay")
    return result


def upper(k, s, tail_count=2):
    """Universal majorant in the proof, with rational tail terms."""
    require(tail_count in (1, 2), "explicit tail coefficient control")
    z = decay(k, Fraction(2, s))
    q = Fraction(1, 1 << k)
    tail = tail_count * q ** 2 + 2 * q ** 6 / (1 - q ** 6)
    return Fraction(z[0], UNIT) + tail, Fraction(z[1], UNIT) + tail


def lower(k, s):
    """Three actual entries in the half-tie row, including h=+2."""
    theta = Fraction(1, s)
    terms = [decay(k, value) for value in
             (2 * theta, 2 + 4 * theta, 2 + 8 * theta)]
    return (Fraction(sum(value[0] for value in terms), UNIT),
            Fraction(sum(value[1] for value in terms), UNIT))


def check_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = {}
    require(len(manifest["files"]) == 4, "bounded source inventory")
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source hash: " + row["path"])
            pins[row["path"]] = digest
    require(len(pins) == 2, "both mathematical source conventions are pinned")
    return pins


def check_arithmetic():
    require(root((UNIT // 4, UNIT // 4)) == (UNIT // 2, UNIT // 2),
            "exact square root positive fixture")
    value = root((UNIT // 2, UNIT // 2))
    require(value[0] ** 2 <= UNIT ** 2 // 2 <= value[1] ** 2,
            "irrational square root enclosure")
    require(power((UNIT // 2, UNIT // 2), 3) == (UNIT // 8, UNIT // 8),
            "exact interval cube")
    require(decay(2, Fraction(3, 2)) == (UNIT // 8, UNIT // 8),
            "fractional decay with integral product")
    require(decay(1, Fraction(BITS + 1)) == (0, 1), "bounded underflow enclosure")
    rejected = 0
    for k, value in ((0, Fraction(1)), (17, Fraction(1)),
                     (1, Fraction(-1)), (1, Fraction(1, 3))):
        try:
            decay(k, value)
        except ValueError:
            rejected += 1
    require(rejected == 4, "all invalid arithmetic domains rejected")
    return rejected


def check_geometry():
    checked = 0
    for s in (8, 16, 32, 64, 128, 256):
        i = s // 2
        require(offset(s, i) == -Fraction(1, 2), "literal half-up tie")
        theta = Fraction(1, s)
        for h, expected in ((1, 2 * theta), (-1, 2 + 4 * theta),
                            (2, 2 + 8 * theta)):
            require(exponent(s, i, h) == expected, "three-entry lower identity")
            checked += 1
        for j in range(s):
            require(offset(s, j + s) == offset(s, j), "physical period offsets")
            checked += 1
    return checked


def check_complete_rows():
    rows = entries = 0
    for s in (8, 16, 32):
        for k in (2, 3, 4):
            bound = upper(k, s)[1]
            for w in (2, s // 2 - 1):
                tie_low = None
                for i in range(s):
                    low = high = 0
                    for h in range(-w, w + 1):
                        if h:
                            left, right = decay(k, exponent(s, i, h))
                            low += left
                            high += right
                            entries += 1
                    require(Fraction(high, UNIT) <= bound, "complete row below majorant")
                    if i == s // 2:
                        tie_low = Fraction(low, UNIT)
                    rows += 1
                require(tie_low is not None and tie_low >= lower(k, s)[0],
                        "actual half-tie row contains lower witness")
    return rows, entries


def check_transition_controls():
    admitted = excluded = unresolved = 0
    for log_s in range(4, 25):
        s = 1 << log_s
        for k in range(2, 13):
            lo, hi = lower(k, s)
            left, right = upper(k, s)
            require(lo <= hi and left <= right and lo <= right,
                    "consistent independent upper/lower enclosures")
            if right < 1:
                admitted += 1
            elif lo > 1:
                excluded += 1
            else:
                unresolved += 1
    s, k = 1 << 19, 8
    bad = lower(k, s)[0]
    wrong = upper(k, s, tail_count=1)[1]
    require(wrong < 1 < bad, "omitting one leading tail gives a false admission")
    require(upper(9, 1 << 20)[1] < 1 < lower(8, 1 << 20)[0],
            "same-period positive and negative concentration controls")
    require(admitted + excluded + unresolved == 231, "complete bounded scan")
    return {"admitted": admitted, "excluded": excluded, "unresolved": unresolved,
            "omitted_tail_false_admission": {"s": s, "k": k},
            "same_period_bracket": {"s": 1 << 20, "bad_k": 8, "good_k": 9}}


def main():
    sources = check_sources()
    rejected = check_arithmetic()
    geometry = check_geometry()
    rows, entries = check_complete_rows()
    require((geometry, rows, entries) == (522, 336, 4368),
            "complete registered geometry and row coverage")
    transitions = check_transition_controls()
    files = sorted(PACKAGE.glob("*"))
    require(len(files) == 6 and all(path.is_file() for path in files),
            "six regular package artifacts")
    result = {"status": "PASS_GAUSSIAN_CONCENTRATION_THRESHOLD",
              "arithmetic_rejections": rejected, "geometry_equalities": geometry,
              "complete_rows": rows, "complete_entries": entries,
              "transition_controls": transitions, "source_sha256": sources,
              "package_sha256": {path.name: sha256(path.read_bytes()).hexdigest()
                                 for path in files},
              "scope": "Exact finite controls; the uniform asymptotic claim is a written proof."}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
