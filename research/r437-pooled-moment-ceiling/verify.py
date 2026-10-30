"""Exact moment ceilings for the pooled R437 C/D profiles of PR #4176.

The fixed moment contract is ToikY's PR #5810 (research/r437-unpooled-budget-
obstruction): M(c) = sum_r n_r * r/(64*28416) * (64/r)**c, with every added
nonnegative charge omitted. The pooled C and D profiles are read, without
executing any predecessor code, from Chris R / Clear1nsight's PR #4176
research/r437-carrier-integration/numerical.py. The unpooled #4067 profile is
read from the #5810 README as a comparison row.

All bounds use exact rational interval arithmetic with outward rounding.
Nick Petalas. Apache-2.0.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NUMERICAL = ROOT / "research/r437-carrier-integration/numerical.py"
UNPOOLED_README = ROOT / "research/r437-unpooled-budget-obstruction/README.md"
RESULT = HERE / "RESULT.json"

PINS = {
    NUMERICAL: "83f2b60a90ab2d0354c5c84f48af246ab416605c3ae4bd62368bbe5f23bb53bb",
    UNPOOLED_README: "f41669bda70e75a91471539303011766b7348353e88a3ef9774865d3dd24e512",
}

DIM = 64
SCALE = 2**256  # outward-rounding grid for every interval endpoint
TARGET = Fraction(17, 5000)  # admitted BIT saving of the selected record

# Claimed crossing brackets (lo, hi): M(lo) < 1 < M(hi).
BRACKETS = {
    "U": ("0.0017366903544672", "0.0017366903544673"),
    "C": ("0.0017367386530996", "0.0017367386530997"),
    "D": ("0.0017367829682417", "0.0017367829682418"),
}
# #4067's reported rational moment-grid point for the unpooled host.
GRID_4067 = "0.001736690352456612377607"
# Rohan Arun's #3959 reported pooled crossing (closed PR), compared to C.
REPORTED_3959 = "0.001736738651088946052684"


class Fail(Exception):
    pass


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise Fail(msg)


# ---------- inputs ----------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_assignments(path: Path) -> dict[str, object]:
    """Module-level literal assignments, read through ast only."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                try:
                    out[target.id] = ast.literal_eval(node.value)
                except ValueError:
                    pass
            elif isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                for name, val in zip(target.elts, node.value.elts):
                    if isinstance(name, ast.Name):
                        out[name.id] = ast.literal_eval(val)
    return out


def unpooled_profile(path: Path) -> dict[int, int]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"paid profile:\s*```\s*(\{[^`]*\})\s*```", text)
    need(match is not None, "unpooled profile block in #5810 README")
    body = re.sub(r"\s+", "", match.group(1))
    return {int(k): int(v) for k, v in (kv.split(":") for kv in body[1:-1].split(","))}


def load_inputs() -> tuple[dict[str, dict[int, int]], int]:
    for path, digest in PINS.items():
        need(sha256(path) == digest, f"pinned bytes: {path.relative_to(ROOT)}")
    lits = literal_assignments(NUMERICAL)
    need(lits.get("W") == 28416 and lits.get("M") == DIM, "#4176 normalization W=28416, M=64")
    need(lits.get("REQUESTS") == 903456, "#4176 request count")
    profiles = {"U": unpooled_profile(UNPOOLED_README), "C": lits["PROFILE_C"], "D": lits["PROFILE_D"]}
    for name, prof in profiles.items():
        need(sum(prof.values()) == 903456, f"{name}: paid calls 903456")
        need(sum(r * n for r, n in prof.items()) == 1808352, f"{name}: rank mass 1808352")
        need(all(1 <= r < DIM and n > 0 for r, n in prof.items()), f"{name}: ranks below 64")
    return profiles, lits["W"]


# ---------- outward-rounded rational intervals ----------

def down(x: Fraction) -> Fraction:
    return Fraction(math.floor(x * SCALE), SCALE)


def up(x: Fraction) -> Fraction:
    return Fraction(math.ceil(x * SCALE), SCALE)


def atanh_inv(q: int) -> tuple[Fraction, Fraction]:
    """Interval for atanh(1/q), q >= 3: alternating-free positive series."""
    y = Fraction(1, q)
    total, term, k = Fraction(0), y, 0
    while True:
        total += term / (2 * k + 1)
        k += 1
        term *= y * y
        tail = term / (2 * k + 1) / (1 - y * y)  # bounds the remaining sum
        if tail < Fraction(1, SCALE):
            return down(total), up(total + tail)


def log_intervals() -> dict[int, tuple[Fraction, Fraction]]:
    """log p for the primes needed by ranks <= 42 (and 26 = 2*13)."""
    def add(*parts):
        return down(sum(p[0] for p in parts)), up(sum(p[1] for p in parts))

    def scale(k, iv):
        return (k * iv[0], k * iv[1]) if k >= 0 else (k * iv[1], k * iv[0])

    a3, a5, a9, a15, a25 = (atanh_inv(q) for q in (3, 5, 9, 15, 25))
    log2 = scale(2, a3)                                   # log 2 = 2 atanh(1/3)
    log3 = add(log2, scale(2, a5))                        # log(3/2) = 2 atanh(1/5)
    log5 = add(scale(2, log2), scale(2, a9))              # log(5/4) = 2 atanh(1/9)
    log7 = add(scale(3, log2), scale(-2, a15))            # log(8/7) = 2 atanh(1/15)
    log13 = add(scale(2, log2), log3, scale(2, a25))      # log(13/12) = 2 atanh(1/25)
    return {2: log2, 3: log3, 5: log5, 7: log7, 13: log13}


def log_ratio(r: int, logs) -> tuple[Fraction, Fraction]:
    """Interval for log(64/r)."""
    lo = 6 * logs[2][0]
    hi = 6 * logs[2][1]
    n = r
    for p in (2, 3, 5, 7, 13):
        while n % p == 0:
            n //= p
            lo -= logs[p][1]
            hi -= logs[p][0]
    need(n == 1, f"rank {r} factors over 2,3,5,7,13")
    return down(lo), up(hi)


def exp_interval(tl: Fraction, th: Fraction) -> tuple[Fraction, Fraction]:
    """exp on [tl, th] with 0 <= tl <= th <= 1/2."""
    need(0 <= tl <= th <= Fraction(1, 2), "exp argument range")
    lo = hi = Fraction(0)
    tlk = thk = Fraction(1)
    k = 0
    while True:
        lo += tlk
        hi += thk
        k += 1
        tlk = tlk * tl / k
        thk = thk * th / k
        if 2 * thk < Fraction(1, SCALE):
            return down(lo), up(hi + 2 * thk)  # Lagrange tail < 2 * th^k / k!


def moment(profile: dict[int, int], c: Fraction, width: int, logs) -> tuple[Fraction, Fraction]:
    """Interval for sum n_r * r/(64*width) * exp(c * log(64/r))."""
    lo = hi = Fraction(0)
    for r, n in profile.items():
        ll, lh = log_ratio(r, logs)
        el, eh = exp_interval(c * ll, c * lh)
        lo += n * r * el
        hi += n * r * eh
    denom = DIM * width
    return down(lo / denom), up(hi / denom)


# ---------- certificate ----------

def certify(profiles, width, logs) -> dict[str, object]:
    out: dict[str, object] = {"normalization": f"64*{width}", "target": "17/5000", "profiles": {}}
    brackets = {}
    for name in ("U", "C", "D"):
        prof = profiles[name]
        lo_s, hi_s = BRACKETS[name]
        lo, hi = Fraction(lo_s), Fraction(hi_s)
        need(0 < lo < hi, f"{name}: ordered bracket")
        m_lo = moment(prof, lo, width, logs)
        m_hi = moment(prof, hi, width, logs)
        need(m_lo[1] < 1, f"{name}: M(lo) < 1")
        need(m_hi[0] > 1, f"{name}: M(hi) > 1")
        m_t = moment(prof, TARGET, width, logs)
        need(m_t[0] > 1, f"{name}: M(17/5000) > 1")
        # smallest productive width W' with M(17/5000; W') <= 1
        s_lo, s_hi = m_t[0] * width, m_t[1] * width
        need(math.floor(s_hi) == math.floor(s_lo), f"{name}: width threshold resolved")
        w_min = math.floor(s_lo) + 1
        m0_exact = Fraction(sum(r * n for r, n in prof.items()), DIM * width)
        m0 = moment(prof, Fraction(0), width, logs)
        need(m0[0] <= m0_exact <= m0[1] and m0_exact < 1, f"{name}: M(0) < 1")
        brackets[name] = (lo, hi)
        out["profiles"][name] = {
            "profile": {str(r): n for r, n in sorted(prof.items())},
            "M0": str(m0_exact),
            "crossing_bracket": [lo_s, hi_s],
            "M_at_target_interval_decimal": [f"{float(m_t[0]):.15f}", f"{float(m_t[1]):.15f}"],
            "min_productive_width_at_target": w_min,
            "extra_productive_columns": w_min - width,
        }
    gain_dc = (brackets["D"][0] - brackets["C"][1], brackets["D"][1] - brackets["C"][0])
    gain_cu = (brackets["C"][0] - brackets["U"][1], brackets["C"][1] - brackets["U"][0])
    need(gain_dc[0] > 0 and gain_cu[0] > 0, "strict ceiling order U < C < D")
    out["ceiling_gain_D_minus_C"] = [str(gain_dc[0]), str(gain_dc[1])]
    out["ceiling_gain_C_minus_U"] = [str(gain_cu[0]), str(gain_cu[1])]
    # Reported passing values include surcharges, so each must lie below the ceiling.
    for key, value, name in (("reported_4067_unpooled_grid_point", GRID_4067, "U"),
                             ("reported_3959_pooled_crossing", REPORTED_3959, "C")):
        point = Fraction(value)
        need(point < brackets[name][0], f"{key} below the {name} ceiling")
        out[key] = {"value": value, "below_ceiling_of": name,
                    "gap_to_bracket_lo": str(brackets[name][0] - point)}
    return out


def controls(profiles, width, logs) -> list[str]:
    """Each mutation must make certify() reject."""
    passed = []
    cases = {
        "D bracket applied to C": ({**profiles, "D": profiles["C"]}, width),
        "physical width 28425 instead of productive 28416": (profiles, 28425),
        "one D rank-42 call moved to rank 1": (
            {**profiles, "D": {**profiles["D"], 42: profiles["D"][42] - 1, 1: profiles["D"][1] + 1}},
            width),
        "carrier delta reversed on D": (
            {**profiles, "D": {**profiles["D"], 1: profiles["D"][1] - 288,
                               2: profiles["D"][2] + 576, 3: profiles["D"][3] - 288}},
            width),
    }
    for label, (prof, w) in cases.items():
        try:
            certify(prof, w, logs)
        except Fail:
            passed.append(label)
            continue
        raise Fail(f"control accepted: {label}")
    # interval sanity against floating point
    for r in (1, 2, 3, 5, 7, 14, 26, 42):
        lo, hi = log_ratio(r, logs)
        need(lo <= Fraction(math.log(64 / r)) + Fraction(1, 10**12) and
             Fraction(math.log(64 / r)) - Fraction(1, 10**12) <= hi and hi - lo < Fraction(1, 10**60),
             f"log interval sanity r={r}")
    passed.append("log intervals tight and consistent with float log")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--emit", action="store_true", help="print the recomputed RESULT.json and exit")
    args = parser.parse_args()
    try:
        profiles, width = load_inputs()
        logs = log_intervals()
        result = certify(profiles, width, logs)
        result["controls_rejected"] = controls(profiles, width, logs)
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.emit:
            sys.stdout.write(text)
            return 0
        need(RESULT.read_text(encoding="utf-8") == text, "RESULT.json matches recomputation")
    except Fail as exc:
        print(f"FAIL: {exc}")
        return 1
    d = result["profiles"]["D"]
    print("PASS_R437_POOLED_MOMENT_CEILING "
          f"D_bracket={d['crossing_bracket'][0]}..{d['crossing_bracket'][1]} "
          f"min_width_at_17/5000={d['min_productive_width_at_target']} no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
