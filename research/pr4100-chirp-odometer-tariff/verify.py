#!/usr/bin/env python3
"""Literal head travel and rounding error of #4100 PROOF.md's cached chirp odometer.

Standard library only. A four-tape model (tables, prefix cache, counter, output)
counts every head move of the cached prefix-product enumeration described in
PROOF.md's "Chirp tables" section and compares it with the written amortized
bounds in README.md. Rounding is toward zero at P fractional bits against a
60-digit reference. Finite corroboration, not an all-size proof.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/unconditional-batched-crt"
getcontext().prec = 60
SQRT2 = Decimal(2).sqrt()


def need(condition, message):
    if not condition:
        raise AssertionError(message)


# --- 0. Source binding ---------------------------------------------------------

PHRASES = [
    "Enumerate the tensor in lexicographic order. Cache the product for every",
    "suffix of those cached products, then emit the full product. No division",
    "sum_{j>=0}(j+1)/2^j, a constant. In the actual radices it is smaller.",
    "All t_i differ by at most a factor two.",
    "costs O(j*t_min*p) such travel and occurs at most O(T/t_min^j) times.",
    "Each emitted chirp is obtained from at most d rounded factors and d",
    "O(d 2^-P) at P working fractional bits.",
    "Their values have modulus at most1 after toward-zero component truncation.",
]


def check_sources():
    pins = {row["path"]: row["sha256"]
            for row in json.loads((Path(__file__).parent / "SOURCES.json").read_text())["files"]}
    for rel in ("research/unconditional-batched-crt/PROOF.md",
                "research/unconditional-batched-crt/evidence/composition-controls.json"):
        need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == pins[rel], f"pin {rel}")
    text = (SOURCE / "PROOF.md").read_text()
    for phrase in PHRASES:
        need(phrase in text, f"source phrase missing: {phrase}")
    ledger = json.loads((SOURCE / "evidence/composition-controls.json").read_text())
    kappa = Fraction(ledger["kappa_candidate"])
    eps = Fraction(ledger["parameters"]["epsilon"])
    rejected = Fraction(ledger["rejected_routes"]["old_per_record_d_chirp"])
    # A per-record d-scan costs O(V d) = O(V p^eps): power eps against the target 1-kappa.
    need(rejected == (1 - kappa) - eps and rejected < 0, "ledger rejects a per-record d chirp scan")
    need(Fraction(ledger["cost_slacks"]["cached_phases_and_recovery"]) == 1 - kappa,
         "cached phases are charged at power 0")
    return len(PHRASES), float(rejected)


# --- 1. Four-tape model of the cached odometer -----------------------------------

class Tape:
    def __init__(self):
        self.pos = 0
        self.moves = 0

    def goto(self, x):
        self.moves += abs(x - self.pos)
        self.pos = x

    def sweep(self, n):
        self.moves += n
        self.pos += n


def simulate(radices, P, naive=False):
    """Enumerate prod Z_t lexicographically (axis 0 fastest), emitting one chirp per record.

    Table tape: tables for axes 0..d-1 in axis order, t_i entries of P cells.
    Cache tape: prefix products pi_k = prod_{i>=k} a_i(x_i), slot k at k*P.
    Counter tape: the mixed-radix address as one binary number (all t_i are powers of two).
    """
    d = len(radices)
    need(all(t >= 2 and t & (t - 1) == 0 for t in radices), "dyadic radices")
    bits = [t.bit_length() - 1 for t in radices]
    off = [0]
    for t in radices:
        off.append(off[-1] + t * P)
    tab, cache, ctr, out = Tape(), Tape(), Tape(), Tape()
    x = [0] * d
    mults = 0

    def read_table(k):
        tab.goto(off[k] + x[k] * P)
        tab.sweep(P)

    def recompute(k):
        nonlocal mults
        read_table(k)
        if k + 1 < d:
            cache.goto((k + 1) * P)
            cache.sweep(P)
            mults += 1
        cache.goto(k * P)
        cache.sweep(P)

    T = math.prod(radices)
    if not naive:
        for k in reversed(range(d)):
            recompute(k)
    field_of_bit = [k for k, b in enumerate(bits) for _ in range(b)]
    counter = [0] * sum(bits)
    carries = [0] * (d + 1)
    for record in range(T):
        if naive:
            for k in reversed(range(d)):
                read_table(k)
                mults += k + 1 < d
            out.sweep(P)
        else:
            cache.goto(0)
            cache.sweep(P)
            out.sweep(P)
        if record == T - 1:
            break
        i = 0
        while counter[i]:
            counter[i] = 0
            i += 1
        counter[i] = 1
        ctr.goto(i + 1)
        ctr.goto(0)
        j = field_of_bit[i]
        for k in range(j):
            x[k] = 0
        x[j] += 1
        carries[j] += 1
        if not naive:
            for k in range(j, -1, -1):
                recompute(k)
    return dict(T=T, d=d, tab=tab.moves, cache=cache.moves, ctr=ctr.moves, out=out.moves,
                mults=mults, carries=carries)


def table_bound(radices, P):
    """Written bound: T P [1 + sum_{j>=1} N_j * 2(j+1)(t_max+1) / T], N_j <= T / prod_{i<j} t_i."""
    T, tmax = math.prod(radices), max(radices)
    total = Fraction(T * P)
    for j in range(1, len(radices)):
        total += Fraction(T, math.prod(radices[:j])) * 2 * (j + 1) * (tmax + 1) * P
    return total


def cache_bound(radices, P):
    """Emit: 2P per record. A step whose carry stops at axis j >= 0 recomputes pi_j..pi_0;
    each recomputation costs <= (j+3)P travel plus 2P sweeps. At most T/prod_{i<j} t_i steps
    stop at axis j or above."""
    T, d = math.prod(radices), len(radices)
    total = Fraction(2 * T * P) + 2 * d * (d + 2) * P  # emits plus the initial fill
    for j in range(d):
        total += Fraction(T, math.prod(radices[:j])) * (j + 1) * (j + 5) * P
    return total


UNIFORM_TABLE_CONSTANT = 31   # 1 + 12 (t_max+1)/t_min <= 31 when t_min >= 2 and t_max <= 2 t_min


def check_tapes():
    P = 8
    rows = []
    families = [("all-2", lambda d: [2] * d, range(1, 13)),
                ("all-4", lambda d: [4] * d, range(1, 9)),
                ("2/4 mixed", lambda d: [2 if i % 2 else 4 for i in range(d)], range(1, 11)),
                ("4/8 mixed", lambda d: [8 if i % 3 == 0 else 4 for i in range(d)], range(1, 7))]
    for name, make, ds in families:
        for d in ds:
            radices = make(d)
            need(max(radices) <= 2 * min(radices), "factor-two premise")
            sim = simulate(radices, P)
            T = sim["T"]
            tb, cb = table_bound(radices, P), cache_bound(radices, P)
            need(sim["tab"] <= tb, f"table travel within the written bound {name} d={d}")
            need(sim["tab"] <= UNIFORM_TABLE_CONSTANT * T * P, f"uniform constant {name} d={d}")
            need(sim["cache"] <= cb, f"cache travel within bound {name} d={d}")
            need(sim["ctr"] <= 4 * T, f"counter travel {name} d={d}")
            need(sim["out"] == T * P, "one P-cell output per record")
            # Exact count: pi_k is (re)computed T/prod_{i<k} t_i times (setup included);
            # pi_{d-1} is a table entry and costs no product.
            exact = sum(T // math.prod(radices[:k]) for k in range(d - 1))
            need(sim["mults"] == exact, f"exact multiplication count {name} d={d}")
            need(sim["mults"] <= d + 2 * T, "fewer than two products per record (plus setup)")
            need(sim["mults"] <= d + 4 * T, "PROOF.md's sum (j+1)/2^j bound")
            rows.append(dict(family=name, d=d, T=T, table_per_TP=round(sim["tab"] / (T * P), 4),
                             cache_per_TP=round(sim["cache"] / (T * P), 4),
                             mults_per_T=round(sim["mults"] / T, 4)))
    # Uniformity in d: the largest-d ratio is no larger than the bound, and grows by < 1% over the last
    # three d values in each family.
    for name in {r["family"] for r in rows}:
        series = [r["table_per_TP"] for r in rows if r["family"] == name]
        need(series[-1] - series[-3] < 0.01 * series[-1], f"table travel flat in d for {name}: {series}")
    return rows


def check_controls():
    P = 8
    # Control 1: a per-record d-factor scan grows linearly in d and passes the uniform constant.
    naive = []
    for d in range(1, 13):
        sim = simulate([2] * d, P, naive=True)
        naive.append(sim["tab"] / (sim["T"] * P))
        need(sim["mults"] == (d - 1) * sim["T"], "naive multiplies d-1 times per record")
    need(naive[-1] > UNIFORM_TABLE_CONSTANT and all(b > a for a, b in zip(naive, naive[1:])),
         "control: per-record d scan is not uniform in d")
    # Control 2: without t_max <= 2 t_min the cached schedule loses uniformity.
    skew = simulate([2, 512], P)
    skew_ratio = skew["tab"] / (skew["T"] * P)
    need(skew_ratio > UNIFORM_TABLE_CONSTANT, "control: the factor-two radix premise is load-bearing")
    return [round(v, 2) for v in naive], round(skew_ratio, 2)


# --- 2. Rounding error of the prefix chain ------------------------------------------

def dec_pi():
    getcontext().prec += 4
    three = Decimal(3)
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    getcontext().prec -= 4
    return +s


PI = dec_pi()


def cos_sin(x):
    x = x % (2 * PI)
    if x > PI:
        x -= 2 * PI
    c = s = Decimal(0)
    term, k = Decimal(1), 0
    while abs(term) >= Decimal(10) ** -70:
        if k % 4 == 0:
            c += term
        elif k % 4 == 1:
            s += term
        elif k % 4 == 2:
            c -= term
        else:
            s -= term
        k += 1
        term = term * x / k
    return c, s


def trunc(v, P):
    """Toward-zero to P fractional bits, as an exact Fraction."""
    scaled = v * (1 << P)
    n = int(scaled)  # int() truncates toward zero for Decimal and Fraction
    return Fraction(n, 1 << P)


def chirp_entry(s, t, x, P, mode="trunc"):
    c, sn = cos_sin(-PI * s * x * x / t)
    if mode == "trunc":
        return trunc(c, P), trunc(sn, P)
    return (Fraction(round(c * (1 << P)), 1 << P), Fraction(round(sn * (1 << P)), 1 << P))


def cmul_trunc(a, b, P):
    re = a[0] * b[0] - a[1] * b[1]
    im = a[0] * b[1] + a[1] * b[0]
    return trunc(re, P), trunc(im, P)


def modulus_sq(z):
    return z[0] * z[0] + z[1] * z[1]


def check_rounding():
    rng = random.Random(4320)
    worst_ratio = Fraction(0)
    checked = 0
    for d, t, P in ((2, 8, 16), (4, 4, 20), (6, 8, 24), (8, 4, 32), (10, 4, 24)):
        s = [rng.randrange(1, t, 2) for _ in range(d)]  # odd, hence coprime to the dyadic t
        tables = [[chirp_entry(si, t, xv, P) for xv in range(t)] for si in s]
        for tab in tables:
            need(all(modulus_sq(z) <= 1 for z in tab), "table entries have modulus <= 1")
        T = t ** d
        records = range(T) if T <= 4096 else rng.sample(range(T), 1500)
        bound = (2 * d - 1) * SQRT2 * Decimal(2) ** -P
        for rec in records:
            xs = [(rec // t ** k) % t for k in range(d)]
            pi = tables[d - 1][xs[d - 1]]
            for k in range(d - 2, -1, -1):
                pi = cmul_trunc(tables[k][xs[k]], pi, P)
                need(modulus_sq(pi) <= 1, "prefix products stay in the unit disk")
            angle = -PI * sum(Decimal(si) * xv * xv / t for si, xv in zip(s, xs))
            c, sn = cos_sin(angle)
            err = ((Decimal(pi[0].numerator) / pi[0].denominator - c) ** 2 +
                   (Decimal(pi[1].numerator) / pi[1].denominator - sn) ** 2).sqrt()
            need(err <= bound, f"chirp error within (2d-1) sqrt2 2^-P: d={d} P={P}")
            worst_ratio = max(worst_ratio, Fraction(str(err / bound)))
            checked += 1
    return checked, float(worst_ratio)


def check_rounding_controls():
    # Control: round-to-nearest can leave the unit disk, which the toward-zero rule prevents.
    P = 6
    escaped = sum(modulus_sq(chirp_entry(s, 64, x, P, mode="nearest")) > 1
                  for s in (1, 3, 5, 7) for x in range(64))
    need(escaped > 0, "control: nearest rounding leaves the unit disk for some entries")
    # Control: a running product updated by unit ratios drifts with the number of records,
    # unlike recomputation from cached prefixes.
    d, t, P = 2, 64, 12
    s = [3, 5]
    tables = [[chirp_entry(si, t, xv, P) for xv in range(t)] for si in s]
    run = cmul_trunc(tables[0][0], tables[1][0], P)
    prev = [0, 0]
    worst = Decimal(0)
    for rec in range(1, t * t):
        xs = [rec % t, rec // t]
        for k in range(d):
            if xs[k] != prev[k]:
                old = tables[k][prev[k]]
                run = cmul_trunc(cmul_trunc(run, (old[0], -old[1]), P), tables[k][xs[k]], P)
        prev = xs
        c, sn = cos_sin(-PI * sum(Decimal(si) * xv * xv / t for si, xv in zip(s, xs)))
        err = ((Decimal(run[0].numerator) / run[0].denominator - c) ** 2 +
               (Decimal(run[1].numerator) / run[1].denominator - sn) ** 2).sqrt()
        worst = max(worst, err)
    bound = (2 * d - 1) * SQRT2 * Decimal(2) ** -P
    need(worst > bound, "control: ratio updates drift beyond the cached-prefix error bound")
    return escaped, float(worst / bound)


def main():
    phrases, rejected = check_sources()
    rows = check_tapes()
    naive, skew = check_controls()
    rounding_checked, worst_ratio = check_rounding()
    escaped, drift = check_rounding_controls()
    worst_table = max(r["table_per_TP"] for r in rows)
    worst_cache = max(r["cache_per_TP"] for r in rows)
    print(json.dumps({
        "status": "PASS_PR4100_CHIRP_ODOMETER_FINITE",
        "source_phrases": phrases,
        "ledger_rejects_per_record_d_chirp": rejected,
        "tape_cases": len(rows),
        "max_table_travel_per_TP": worst_table,
        "uniform_table_constant": UNIFORM_TABLE_CONSTANT,
        "max_cache_travel_per_TP": worst_cache,
        "max_products_per_record": max(r["mults_per_T"] for r in rows),
        "largest_d": max(r["d"] for r in rows),
        "control_naive_table_per_TP_d1_to_12": naive,
        "control_skewed_radices_table_per_TP": skew,
        "rounding_records_checked": rounding_checked,
        "rounding_worst_error_over_bound": round(worst_ratio, 4),
        "control_nearest_rounding_escapes": escaped,
        "control_ratio_update_drift_over_bound": round(drift, 2),
        "per_family_rows": rows,
        "all_size_theorem_claimed": False,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
