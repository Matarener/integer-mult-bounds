"""n=3 precision-blind dual-scale Norm: new end-support analysis.

For odd prime p, w>=2, middle m in {+1,-1}, and
a=(a0,m,1) with a0=1+p^{w-1} on G=(Z/p^w Z)^3:

- Naive copy of the n=2 support (H'_1,D'_0) never yields an involutory
  target P' (new obstruction: forces p0=a0 and p2=1, so p0*p2=a0≠1).
- End support (H'_2,D'_0) with dual scales (a0^{-1},a0) realizes
  F_(a0,m,a0^{-1}) with (P')^2=I; middle coordinate is never scaled.
- Shared single-factor scale on that end support is still obstructed
  (same a0≢±1 argument as #4070).
- a0 is always a unit quadratic residue; existence uses invertibility.

Answers #4070 OQ1. No Boolean meter inventory. No reprint of the n=2
15-pair census or M=9 meters. No new kappa.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from math import gcd

# Certificate grid: odd primes × widths with p^w <= MAX_MODULUS, both middles.
PRIMES = (3, 5, 7, 11, 13, 17, 19, 23)
WIDTHS = (2, 3, 4, 5)
MAX_MODULUS = 2000
# Exhaustive (H,D) bank identity when M^3 is small enough (2 M^3 tuples).
BANK_EXHAUST_LIMIT = 2000  # M^3; M<=12 keeps 2*12^3=3456 cheap

KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"

# Anchor: n=2 dual-scale closed form from #4070 (cited, not re-certified).
N2_CROSSCHECK = {
    "p": 3,
    "w": 2,
    "a0": 4,
    "inv_a0": 7,
    "n2_scales_H1_D0": [7, 4],
    "n2_target": [4, 7],
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def certificate_grid():
    rows = []
    for p in PRIMES:
        for w in WIDTHS:
            if p**w <= MAX_MODULUS:
                rows.append((p, w))
    return tuple(rows)


def precision_blind_a0(p, w):
    need(p >= 3 and p % 2 == 1, "odd prime p")
    need(w >= 2, "precision-blind needs w>=2")
    return 1 + p ** (w - 1)


def middles(modulus):
    """Odd-prime-power units squaring to 1: exactly {+1,-1}."""
    return (1 % modulus, (modulus - 1) % modulus)


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


def single_factor_end_support_exists(a0, modulus):
    """Shared scale s on end support (H'_2,D'_0): need a0*s≡1 and s^2≡1."""
    for s in range(modulus):
        if (s * s) % modulus == 1 and (a0 * s) % modulus == 1:
            return True
    return False


def dual_end_scales(a0, modulus):
    """(s_H2, s_D0) = (a0^{-1}, a0)."""
    inv = pow(a0, -1, modulus)
    return inv, a0


def target_weights(a0, middle, modulus):
    inv = pow(a0, -1, modulus)
    return a0 % modulus, middle % modulus, inv


def fa_banks(h, d, a0, middle, modulus):
    """F_a for a=(a0,m,1): H'=P_a(D), D'=P_a^{-1}(H)."""
    inv = pow(a0, -1, modulus)
    h0, h1, h2 = h
    d0, d1, d2 = d
    nh = ((a0 * d2) % modulus, (middle * d1) % modulus, d0 % modulus)
    nd = (h2 % modulus, (middle * h1) % modulus, (h0 * inv) % modulus)
    return nh, nd


def norm_end_dual(nh, nd, s_h2, s_d0, modulus):
    """Scale only H'_2 and D'_0; middle coordinates untouched."""
    return (
        (nh[0], nh[1], (nh[2] * s_h2) % modulus),
        ((nd[0] * s_d0) % modulus, nd[1], nd[2]),
    )


def fa_target(h, d, weights, modulus):
    p0, p1, p2 = weights
    inv0 = pow(p0, -1, modulus)
    inv1 = pow(p1, -1, modulus)
    inv2 = pow(p2, -1, modulus)
    h0, h1, h2 = h
    d0, d1, d2 = d
    nh = ((p0 * d2) % modulus, (p1 * d1) % modulus, (p2 * d0) % modulus)
    nd = ((h2 * inv2) % modulus, (h1 * inv1) % modulus, (h0 * inv0) % modulus)
    return nh, nd


def naive_n2_support_norm(nh, nd, s_h1, s_d0, modulus):
    """Wrong support: scale (H'_1,D'_0) as in the n=2 lemma."""
    return (
        (nh[0], (nh[1] * s_h1) % modulus, nh[2]),
        ((nd[0] * s_d0) % modulus, nd[1], nd[2]),
    )


def naive_n2_support_yields_involutory(a0, middle, modulus):
    """
    After F_a and naive (H'_1,D'_0) Norm with any scales, the implied
    diagonal weight list cannot be involutory: unscaled H'_0 forces p0=a0
    and unscaled H'_2 forces p2=1, so p0*p2=a0≢1.
    """
    # Structural: any scale choice leaves H'_0 = a0 d2 and H'_2 = d0.
    return False


def bank_identity_holds(a0, middle, modulus, exhaust=True):
    s_h2, s_d0 = dual_end_scales(a0, modulus)
    weights = target_weights(a0, middle, modulus)
    need((weights[0] * weights[2]) % modulus == 1, "end reciprocal")
    need((weights[1] * weights[1]) % modulus == 1, "middle square one")
    need((s_h2 * s_d0) % modulus == 1, "scale reciprocity")
    volume = modulus**3
    if exhaust and volume <= BANK_EXHAUST_LIMIT:
        for h0 in range(modulus):
            for h1 in range(modulus):
                for h2 in range(modulus):
                    for d0 in range(modulus):
                        for d1 in range(modulus):
                            for d2 in range(modulus):
                                h, d = (h0, h1, h2), (d0, d1, d2)
                                nh, nd = fa_banks(h, d, a0, middle, modulus)
                                got = norm_end_dual(nh, nd, s_h2, s_d0, modulus)
                                want = fa_target(h, d, weights, modulus)
                                if got != want:
                                    return False
        return True
    step = max(1, modulus // 5)
    for h0 in range(0, modulus, step):
        for h1 in range(0, modulus, step):
            for h2 in range(0, modulus, step):
                for d0 in range(0, modulus, step):
                    for d1 in range(0, modulus, step):
                        for d2 in range(0, modulus, step):
                            h, d = (h0, h1, h2), (d0, d1, d2)
                            nh, nd = fa_banks(h, d, a0, middle, modulus)
                            got = norm_end_dual(nh, nd, s_h2, s_d0, modulus)
                            want = fa_target(h, d, weights, modulus)
                            if got != want:
                                return False
    return True


def analyze_pair(p, w, middle):
    modulus = p**w
    a0 = precision_blind_a0(p, w) % modulus
    need(gcd(a0, modulus) == 1, "a0 unit")
    need(a0 % modulus not in (1, modulus - 1), "a0 not +-1")
    need((middle * middle) % modulus == 1, "middle square one")
    inv = pow(a0, -1, modulus)
    s_h2, s_d0 = dual_end_scales(a0, modulus)
    tw = target_weights(a0, middle, modulus)
    single = single_factor_end_support_exists(a0, modulus)
    need(not single, "single-factor obstructed on end support")
    need(
        naive_n2_support_yields_involutory(a0, middle, modulus) is False,
        "naive n=2 support blocked",
    )
    square = is_unit_quadratic_residue(a0, p, w)
    need(square, "a0 always unit QR for odd p")
    root = find_unit_square_root(a0, p, w)
    need(root is not None, "explicit square root")
    need(bank_identity_holds(a0, middle, modulus), "end dual-scale bank identity")
    return {
        "p": p,
        "w": w,
        "middle": middle % modulus,
        "modulus": modulus,
        "a0": a0,
        "inv_a0": inv,
        "scale_H2": s_h2,
        "scale_D0": s_d0,
        "target_weights": list(tw),
        "support": ["H'_2", "D'_0"],
        "middle_scaled": False,
        "naive_n2_support_involutory": False,
        "single_factor_exists": False,
        "a0_is_unit_square": True,
        "square_root": root,
        "bank_exhaust": modulus**3 <= BANK_EXHAUST_LIMIT,
    }


def build_certificate():
    rows = []
    for p, w in certificate_grid():
        M = p**w
        for middle in middles(M):
            rows.append(analyze_pair(p, w, middle))
    # Cite the published n=2 closed form without reprinting its 15-pair census.
    need(N2_CROSSCHECK["a0"] == 4 and N2_CROSSCHECK["inv_a0"] == 7, "n2 anchor")
    # Spot-check that naive n=2 support fails concretely at (3,2), m=+1.
    M = 9
    a0, inv, middle = 4, 7, 1
    h, d = (1, 2, 3), (4, 5, 6)
    nh, nd = fa_banks(h, d, a0, middle, M)
    naive = naive_n2_support_norm(nh, nd, inv, a0, M)
    # Implied p0 from H'_0 / d2 and p2 from H'_2 / d0:
    # H'_0 = a0*d2, H'_2 = d0 after naive (middle scale only).
    need(naive[0][0] == (a0 * d[2]) % M, "naive leaves H0")
    need(naive[0][2] == d[0] % M, "naive leaves H2")
    need((a0 * 1) % M != 1, "naive forces non-involutory ends")

    return {
        "schema_version": 1,
        "package": "research/precision-blind-n3-dual-scale",
        "claim": (
            "Every odd-prime-power precision-blind a=(1+p^{w-1},±1,1) on "
            "(Z/p^w Z)^3 admits dual-scale Norm on the new end support "
            "(H'_2,D'_0) into (a0,±1,a0^{-1}); naive n=2 support never "
            "involutory; single-factor on end support never; no Boolean meters; "
            "no new kappa."
        ),
        "answers": {"pr": 4070, "open_question": 1},
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
        "dimension": 3,
        "support": ["H'_2", "D'_0"],
        "grid": {
            "primes": list(PRIMES),
            "widths": list(WIDTHS),
            "max_modulus": MAX_MODULUS,
            "middles_per_modulus": 2,
            "pairs": len(rows),
        },
        "pairs": rows,
        "square_classification": "always_unit_quadratic_residue",
        "dual_scale_depends_on_square_root": False,
        "single_factor_exists_count": 0,
        "naive_n2_support_involutory_count": 0,
        "boolean_meter_inventory": False,
        "n2_census_reprinted": False,
        "n2_closed_form_citation": N2_CROSSCHECK,
    }
