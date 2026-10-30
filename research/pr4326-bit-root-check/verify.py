#!/usr/bin/env python3
"""Independent certified check of #4326's BIT moment root and majorant constants.

Standard library only; no code from #4326. The record is vendored byte-identically
(vendor/RECORD.json). The profile is transcribed from #4326's independent pricer and
cross-checked against the record's query count and rank mass. Exact rationals: ln by
atanh after reducing by powers of two, exp by Taylor with a Lagrange remainder.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECORD_SHA256 = "11b2446e3d714c366fe69a5c504e74fde4277d321ec3f7808c998bc1e229a180"
# research/bit-compact-carrier-retirement/independent_price.py at #4326 head 080f8c21, constant EXPECTED.
PROFILE = {1: 379872, 2: 400000, 3: 22464, 4: 24416, 5: 29376, 6: 17088, 7: 26496, 10: 32, 42: 672}
M = 64
FALLBACK = Q(32 * M * M, 10**16)   # per paid query, the surcharge of the selected BIT moment


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_ln(x, terms=45):
    z = (x - 1) / (x + 1)
    s = 2 * sum(z ** (2 * k + 1) / (2 * k + 1) for k in range(terms + 1))
    return s, s + 2 * z ** (2 * terms + 3) / ((2 * terms + 3) * (1 - z * z))


def ln_bounds(x):
    k = (x.numerator // x.denominator).bit_length() - 1
    a, b = atanh_ln(Q(2))
    c, d = atanh_ln(x / 2 ** k)
    return k * a + c, k * b + d


def exp_bounds(y, terms=30):
    s, term = Q(0), Q(1)
    for k in range(terms + 1):
        s += term
        term = term * y / (k + 1)
    return s, s + 3 * term


def moment(a, profile, W):
    """sum_r n_r (r/M)^(1-a)/W + fallback * sum n * (1/M)^(1-a)/W, enclosed."""
    lo = hi = Q(0)
    terms = list(profile.items()) + [(1, FALLBACK * sum(profile.values()))]
    for r, n in terms:
        if r == M:
            lo, hi = lo + n, hi + n
            continue
        l_lo, l_hi = ln_bounds(Q(M, r))
        lo += n * Q(r, M) * exp_bounds(a * l_lo)[0]
        hi += n * Q(r, M) * exp_bounds(a * l_hi)[1]
    return lo / W, hi / W


def main():
    raw = (HERE / "vendor/RECORD.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == RECORD_SHA256, "vendored RECORD.json")
    record = json.loads(raw)
    W = record["W"]
    need(sum(PROFILE.values()) == record["query_count"], "profile count = 900,416 paid queries")
    need(sum(r * n for r, n in PROFILE.items()) == record["rankmass"], "profile rank mass = 1,808,352")
    need(max(PROFILE) == 42 and W == 28416, "max child 42, W = 28416")

    lo, hi = Q(record["moment_root"]["lower"]), Q(record["moment_root"]["upper"])
    need(hi - lo == Q(1, 10**24), "adjacent 1e-24 bracket")
    m_lo, m_hi = moment(lo, PROFILE, W), moment(hi, PROFILE, W)
    need(m_lo[1] < 1 < m_hi[0], "moment straddles 1 across the claimed root bracket")

    b = Q(record["logical_b"])
    mu1 = moment(Q(0), PROFILE, W)
    need(mu1[1] < Q(199, 200), "mu_1 < 199/200 gives the 200C linear prefactor")
    mub = moment(b, PROFILE, W)
    need(mub[1] < 1 - Q(1, 10**7), "mu_(1-b) < 1 - 1e-7 gives the 10^7 C prefactor")
    need(b < lo, "separator below the root")

    prev = Q(record["public_predecessor"]["upper"])
    gain = (lo - prev) / prev
    need(gain == Q(record["public_predecessor"]["gain_lower"]), "gain over PR4183 as recorded")
    need(Q(41562, 10**7) < gain, "lower endpoint is more than 0.41562% above PR4183's upper endpoint")

    sel_path = ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json"
    pins = {row["path"]: row["sha256"] for row in json.loads((HERE / "SOURCES.json").read_text())["files"]}
    need(hashlib.sha256(sel_path.read_bytes()).hexdigest() == pins["research/e8-bit-p111-tuned/tune/EXPECTED.json"], "selected BIT pin")
    selected_bit = Q(json.loads(sel_path.read_text())["nine"]["bit_lower"])
    need(lo > selected_bit, "root above the selected BIT saving")

    # Control: crediting the nine private families as W (the author's rejected variant) moves the root.
    need(moment(hi, PROFILE, W + record["private"])[1] < 1, "control: W + 9 private credit would shift the root up")

    print(json.dumps({
        "status": "PASS_PR4326_BIT_ROOT_CHECK",
        "root_bracket": [str(lo), str(hi)],
        "mu_1_upper": f"{float(mu1[1]):.10f}",
        "mu_1_minus_b_gap": f"{float(1 - mub[1]):.4e}",
        "gain_over_pr4183": f"{float(gain):.6%}",
        "over_selected_bit": f"{float((lo - selected_bit) / selected_bit):.4%}",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
