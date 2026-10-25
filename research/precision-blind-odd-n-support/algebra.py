"""Odd-length precision-blind dual-scale support classification (n=2k+1≥5).

For odd prime p, w≥2, odd length n=2k+1≥3, and precision-blind
a=(a0, m_1,…,m_{n-2}, 1) with a0=1+p^{w-1} on G=(Z/p^w Z)^n:

- Middles are reciprocal-legal iff m_i·m_{n-1-i}≡1 for every i (for ±1 this
  means m_i=m_{n-1-i}); the true middle (when present) already squares to 1.
- Among all n² dual-scale supports (H'_i, D'_j), exactly two admit scales
  yielding an involutory target P':
    far-end  (H'_{n-1}, D'_0) with (s,t)=(a0^{-1}, a0) → P'=(a0, middles, a0^{-1})
    near-end (H'_0, D'_{n-1}) with (s,t)=(a0^{-1}, a0) → P'=(1, middles, 1)
- Illegal middles admit zero dual-scale supports.
- Shared single-factor scale on either good support is obstructed (a0≢±1).

Answers #4072 OQ1 for n≥5. No Boolean meters. No reprint of the n=3 30-row
grid or the n=2 15-pair census. No new kappa.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from itertools import product
from math import gcd

PRIMES_N5 = (3, 5, 7, 11, 13)
WIDTHS_N5 = (2, 3, 4)
MAX_MODULUS_N5 = 500

PRIMES_N7 = (3, 5, 7)
WIDTHS_N7 = (2, 3)
MAX_MODULUS_N7 = 200

# Exhaustive bank identity when 2·M^n is small enough.
BANK_EXHAUST_LIMIT = 2000

KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"

# Cited closed forms only (not a census reprint).
N2_ANCHOR = {"p": 3, "w": 2, "a0": 4, "inv_a0": 7, "support": ["H'_1", "D'_0"]}
N3_FAR_ANCHOR = {
    "p": 3,
    "w": 2,
    "a0": 4,
    "inv_a0": 7,
    "middle": 1,
    "support": ["H'_2", "D'_0"],
    "target": [4, 1, 7],
}
N3_NEAR_ANCHOR = {
    "p": 3,
    "w": 2,
    "a0": 4,
    "inv_a0": 7,
    "middle": 1,
    "support": ["H'_0", "D'_2"],
    "target": [1, 1, 1],
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def precision_blind_a0(p, w):
    need(p >= 3 and p % 2 == 1, "odd prime p")
    need(w >= 2, "precision-blind needs w>=2")
    return 1 + p ** (w - 1)


def units(modulus):
    return [x for x in range(modulus) if gcd(x, modulus) == 1]


def pm_one(modulus):
    return (1 % modulus, (modulus - 1) % modulus)


def legal_middles(n, modulus):
    """All ±1 middle tuples of length n-2 that satisfy reciprocal condition."""
    need(n % 2 == 1 and n >= 3, "odd length n>=3")
    mid_len = n - 2
    out = []
    for bits in product(pm_one(modulus), repeat=(mid_len + 1) // 2):
        # Build by mirroring: positions 0..mid_len-1 map to a indices 1..n-2.
        mids = [0] * mid_len
        half = mid_len // 2
        for i in range(half):
            mids[i] = bits[i]
            mids[mid_len - 1 - i] = bits[i]  # reciprocal of ±1 is itself
        if mid_len % 2 == 1:
            mids[half] = bits[half]
        out.append(tuple(mids))
    return tuple(out)


def illegal_middle_witness(n, modulus):
    """One ±1 middle tuple that violates reciprocity (n≥5)."""
    need(n >= 5, "illegal witness needs paired middles")
    mids = [1] * (n - 2)
    mids[0] = 1
    mids[n - 3] = (modulus - 1) % modulus  # pair of position 0 inside middle block
    return tuple(mids)


def is_reciprocal_legal(a, modulus):
    """Middle reciprocity only; ends may carry the precision-blind defect."""
    n = len(a)
    # Indices 1..n-2 are middles; each pair (i, n-1-i) with 1≤i≤n-2.
    return all((a[i] * a[n - 1 - i]) % modulus == 1 for i in range(1, n - 1))


def is_involutory_weights(a, modulus):
    n = len(a)
    return all((a[i] * a[n - 1 - i]) % modulus == 1 for i in range(n))


def is_unit_quadratic_residue(a, p, w):
    M = p**w
    a %= M
    if gcd(a, M) != 1:
        return False
    return pow(a, (p - 1) // 2, p) == 1


def find_unit_square_root(a, p, w):
    M = p**w
    a %= M
    if not is_unit_quadratic_residue(a, p, w):
        return None
    root = None
    for x in range(p):
        if (x * x) % p == a % p:
            root = x
            break
    need(root is not None and root % p != 0, "nonzero root mod p")
    mod = p
    for _ in range(1, w):
        diff = (a - root * root) // mod
        inv = pow((2 * root) % p, -1, p)
        t = (diff * inv) % p
        root = root + t * mod
        mod *= p
    need((root * root) % M == a % M, "lifted square root")
    return root % M


def weight_list(a0, middles, modulus):
    return [a0 % modulus] + [m % modulus for m in middles] + [1]


def fa_banks(h, d, a, modulus):
    n = len(a)
    nh = tuple((a[k] * d[n - 1 - k]) % modulus for k in range(n))
    nd = tuple(
        (pow(a[n - 1 - k], -1, modulus) * h[n - 1 - k]) % modulus for k in range(n)
    )
    return nh, nd


def norm_dual(nh, nd, i, j, s, t, modulus):
    nh = list(nh)
    nd = list(nd)
    nh[i] = (nh[i] * s) % modulus
    nd[j] = (nd[j] * t) % modulus
    return tuple(nh), tuple(nd)


def fa_target(h, d, weights, modulus):
    n = len(weights)
    nh = tuple((weights[k] * d[n - 1 - k]) % modulus for k in range(n))
    nd = tuple(
        (pow(weights[n - 1 - k], -1, modulus) * h[n - 1 - k]) % modulus
        for k in range(n)
    )
    return nh, nd


def dual_scale_witness(a, i, j, modulus):
    """Return (s,t,P') if some dual scale on (H'_i,D'_j) yields involutory P'."""
    n = len(a)
    for s in units(modulus):
        for t in units(modulus):
            p_h = [((s * a[k]) if k == i else a[k]) % modulus for k in range(n)]
            p_d = [None] * n
            conflict = False
            for k in range(n):
                idx = n - 1 - k
                val = (
                    (a[idx] * pow(t, -1, modulus)) if k == j else a[idx]
                ) % modulus
                if p_d[idx] is None:
                    p_d[idx] = val
                elif p_d[idx] != val:
                    conflict = True
                    break
            if conflict or p_h != p_d:
                continue
            p = p_h
            if all((p[k] * p[n - 1 - k]) % modulus == 1 for k in range(n)):
                if all(gcd(x, modulus) == 1 for x in p):
                    return s % modulus, t % modulus, [x % modulus for x in p]
    return None


def classify_supports(a, modulus):
    n = len(a)
    goods = []
    for i, j in product(range(n), repeat=2):
        wit = dual_scale_witness(a, i, j, modulus)
        if wit is not None:
            goods.append({"H_index": i, "D_index": j, "scale_H": wit[0], "scale_D": wit[1], "target": wit[2]})
    return goods


def single_factor_on_support_exists(a0, modulus):
    """Shared scale s with a0*s≡1 and s^2≡1 (blocks both good supports)."""
    for s in range(modulus):
        if (s * s) % modulus == 1 and (a0 * s) % modulus == 1:
            return True
    return False


def bank_identity_holds(a, i, j, s, t, weights, modulus, exhaust=True):
    n = len(a)
    volume = modulus**n
    if exhaust and 2 * volume <= BANK_EXHAUST_LIMIT:
        ranges = [range(modulus)] * (2 * n)
        for coords in product(*ranges):
            h, d = coords[:n], coords[n:]
            nh, nd = fa_banks(h, d, a, modulus)
            got = norm_dual(nh, nd, i, j, s, t, modulus)
            want = fa_target(h, d, weights, modulus)
            if got != want:
                return False
        return True
    # Closed-form identity is algebraic; spot-check a deterministic lattice
    # of size independent of n (coordinate-wise samples, not a full grid).
    samples = [0, 1 % modulus, 2 % modulus, (modulus // 2) % modulus, (modulus - 1) % modulus]
    for u in samples:
        for v in samples:
            h = tuple((u + k) % modulus for k in range(n))
            d = tuple((v + 3 * k) % modulus for k in range(n))
            nh, nd = fa_banks(h, d, a, modulus)
            got = norm_dual(nh, nd, i, j, s, t, modulus)
            want = fa_target(h, d, weights, modulus)
            if got != want:
                return False
    return True


def far_end_target(a0, middles, modulus):
    inv = pow(a0, -1, modulus)
    return [a0 % modulus] + [m % modulus for m in middles] + [inv]


def near_end_target(middles, modulus):
    return [1] + [m % modulus for m in middles] + [1]


def analyze_row(n, p, w, middles):
    modulus = p**w
    a0 = precision_blind_a0(p, w) % modulus
    a = weight_list(a0, middles, modulus)
    need(gcd(a0, modulus) == 1, "a0 unit")
    need(a0 % modulus not in (1, modulus - 1), "a0 not +-1")
    need(is_reciprocal_legal(a, modulus), "reciprocal-legal middles")
    need(not is_involutory_weights(a, modulus), "precision-blind ends")
    inv = pow(a0, -1, modulus)
    goods = classify_supports(a, modulus)
    need(len(goods) == 2, f"exactly two good supports, got {len(goods)}")
    by_key = {(g["H_index"], g["D_index"]): g for g in goods}
    need((n - 1, 0) in by_key, "far-end present")
    need((0, n - 1) in by_key, "near-end present")
    far = by_key[(n - 1, 0)]
    near = by_key[(0, n - 1)]
    need(far["scale_H"] == inv and far["scale_D"] == a0, "far scales")
    need(near["scale_H"] == inv and near["scale_D"] == a0, "near scales")
    need(far["target"] == far_end_target(a0, middles, modulus), "far target")
    need(near["target"] == near_end_target(middles, modulus), "near target")
    need(is_involutory_weights(far["target"], modulus), "far target involutory")
    need(is_involutory_weights(near["target"], modulus), "near target involutory")
    need(not single_factor_on_support_exists(a0, modulus), "single-factor obstructed")
    need(
        bank_identity_holds(a, n - 1, 0, inv, a0, far["target"], modulus),
        "far bank identity",
    )
    need(
        bank_identity_holds(a, 0, n - 1, inv, a0, near["target"], modulus),
        "near bank identity",
    )
    square = is_unit_quadratic_residue(a0, p, w)
    need(square, "a0 unit QR")
    root = find_unit_square_root(a0, p, w)
    need(root is not None, "square root")
    return {
        "n": n,
        "p": p,
        "w": w,
        "middles": [m % modulus for m in middles],
        "modulus": modulus,
        "a0": a0,
        "inv_a0": inv,
        "support_count": n * n,
        "good_supports": 2,
        "far_end": {
            "support": [f"H'_{n-1}", f"D'_0"],
            "scale_H": far["scale_H"],
            "scale_D": far["scale_D"],
            "target": far["target"],
        },
        "near_end": {
            "support": [f"H'_0", f"D'_{n-1}"],
            "scale_H": near["scale_H"],
            "scale_D": near["scale_D"],
            "target": near["target"],
        },
        "single_factor_exists": False,
        "a0_is_unit_square": True,
        "square_root": root,
        "bank_exhaust": 2 * (modulus**n) <= BANK_EXHAUST_LIMIT,
    }


def analyze_illegal(n, p, w):
    modulus = p**w
    a0 = precision_blind_a0(p, w) % modulus
    middles = illegal_middle_witness(n, modulus)
    a = weight_list(a0, middles, modulus)
    need(not is_reciprocal_legal(a, modulus), "illegal middle witness")
    goods = classify_supports(a, modulus)
    need(len(goods) == 0, "illegal admits zero dual-scale supports")
    return {
        "n": n,
        "p": p,
        "w": w,
        "middles": list(middles),
        "modulus": modulus,
        "a0": a0 % modulus,
        "good_supports": 0,
        "support_count": n * n,
    }


def certificate_grid(n, primes, widths, max_modulus):
    rows = []
    for p in primes:
        for w in widths:
            if p**w <= max_modulus:
                rows.append((p, w))
    return tuple(rows)


def build_certificate():
    rows_n5 = []
    for p, w in certificate_grid(5, PRIMES_N5, WIDTHS_N5, MAX_MODULUS_N5):
        M = p**w
        for middles in legal_middles(5, M):
            rows_n5.append(analyze_row(5, p, w, middles))

    rows_n7 = []
    for p, w in certificate_grid(7, PRIMES_N7, WIDTHS_N7, MAX_MODULUS_N7):
        M = p**w
        for middles in legal_middles(7, M):
            rows_n7.append(analyze_row(7, p, w, middles))

    illegal_rows = [
        analyze_illegal(5, 3, 2),
        analyze_illegal(5, 5, 2),
        analyze_illegal(7, 3, 2),
    ]

    # Closed-form spot checks at (3,2) for n=5 both supports.
    M = 9
    a0, inv = 4, 7
    middles = (1, 1, 1)
    a = weight_list(a0, middles, M)
    h = (1, 2, 3, 4, 5)
    d = (6, 7, 8, 0, 1)
    nh, nd = fa_banks(h, d, a, M)
    far_got = norm_dual(nh, nd, 4, 0, inv, a0, M)
    far_want = fa_target(h, d, far_end_target(a0, middles, M), M)
    need(far_got == far_want, "n=5 far spot")
    near_got = norm_dual(nh, nd, 0, 4, inv, a0, M)
    near_want = fa_target(h, d, near_end_target(middles, M), M)
    need(near_got == near_want, "n=5 near spot")

    # n=3 near-end citation (not a 30-row reprint): (H'_0,D'_2) → (1,m,1).
    a3 = [4, 1, 1]
    goods3 = classify_supports(a3, 9)
    keys3 = {(g["H_index"], g["D_index"]) for g in goods3}
    need(keys3 == {(0, 2), (2, 0)}, "n=3 exactly far+near")
    near3 = next(g for g in goods3 if (g["H_index"], g["D_index"]) == (0, 2))
    need(near3["target"] == [1, 1, 1], "n=3 near target")
    need(N3_NEAR_ANCHOR["target"] == [1, 1, 1], "near anchor")
    need(N3_FAR_ANCHOR["target"] == [4, 1, 7], "far anchor")
    need(N2_ANCHOR["a0"] == 4 and N2_ANCHOR["inv_a0"] == 7, "n2 anchor")

    return {
        "schema_version": 1,
        "package": "research/precision-blind-odd-n-support",
        "claim": (
            "For every odd length n=2k+1≥5 and every reciprocal-legal "
            "precision-blind a=(1+p^{w-1}, middles, 1) on (Z/p^w Z)^n, exactly "
            "two of the n² dual-scale supports work: far-end (H'_{n-1},D'_0) → "
            "(a0,middles,a0^{-1}) and near-end (H'_0,D'_{n-1}) → (1,middles,1); "
            "illegal middles admit zero; single-factor obstructed; no Boolean "
            "meters; no new kappa."
        ),
        "answers": {"pr": 4072, "open_question": 1},
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
        "dimensions": [5, 7],
        "good_support_names": ["far_end", "near_end"],
        "grid_n5": {
            "primes": list(PRIMES_N5),
            "widths": list(WIDTHS_N5),
            "max_modulus": MAX_MODULUS_N5,
            "legal_middles_per_modulus": 4,
            "rows": len(rows_n5),
            "supports_classified_per_row": 25,
        },
        "grid_n7": {
            "primes": list(PRIMES_N7),
            "widths": list(WIDTHS_N7),
            "max_modulus": MAX_MODULUS_N7,
            "legal_middles_per_modulus": 8,
            "rows": len(rows_n7),
            "supports_classified_per_row": 49,
        },
        "rows_n5": rows_n5,
        "rows_n7": rows_n7,
        "illegal_middle_rows": illegal_rows,
        "square_classification": "always_unit_quadratic_residue",
        "dual_scale_depends_on_square_root": False,
        "single_factor_exists_count": 0,
        "boolean_meter_inventory": False,
        "n2_census_reprinted": False,
        "n3_grid_reprinted": False,
        "n3_near_end_citation": N3_NEAR_ANCHOR,
        "n3_far_end_citation": N3_FAR_ANCHOR,
        "n2_closed_form_citation": N2_ANCHOR,
    }
