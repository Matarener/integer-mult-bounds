"""Dual-scale Norm existence for every odd-prime-power precision-blind pair.

For odd prime p and w>=2, a=(1+p^{w-1},1) on G=(Z/p^w Z)^2:

- no shared single-factor scale s on (H'_1, D'_0) yields an involutory P';
- dual scales (s_H1, s_D0)=(a0^{-1}, a0) realize Norm o F_a = F_{(a0,a0^{-1})}
  with (P')^2 = I (Theorem 1 of weighted-wrapper-contract);
- a0 is always a unit quadratic residue mod p^w; dual-scale existence uses
  invertibility, not an explicit square root.

Answers #4063 OQ1. No Boolean meter inventory. No new kappa.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from math import gcd

# Certificate grid: every odd prime p in PRIMES with every w in WIDTHS such that
# p^w <= MAX_MODULUS (keeps single-factor scans and bank checks cheap).
PRIMES = (3, 5, 7, 11, 13, 17, 19, 23)
WIDTHS = (2, 3, 4, 5)
MAX_MODULUS = 2000
# Exhaustive (H,D) bank identity when M^2 is small enough.
BANK_EXHAUST_LIMIT = 400  # M^2 pairs; M<=20

KAPPA_DECIMAL = "0.001672660197076918"
KAPPA_FRACTION = "836330098538459/500000000000000000"

# #4063 pinned cross-check (p=3,w=2): dual scales (7,4), target (4,7).
CROSSCHECK_P3W2 = {
    "p": 3,
    "w": 2,
    "modulus": 9,
    "a0": 4,
    "inv_a0": 7,
    "scale_H1": 7,
    "scale_D0": 4,
    "target_weights": [4, 7],
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


def is_unit_quadratic_residue(a, p, w):
    """Unit a is a square mod p^w iff it is a square mod p (p odd)."""
    M = p**w
    a %= M
    if gcd(a, M) != 1:
        return False
    return pow(a, (p - 1) // 2, p) == 1


def find_unit_square_root(a, p, w):
    """Return one square root of unit a mod p^w, or None."""
    M = p**w
    a %= M
    if not is_unit_quadratic_residue(a, p, w):
        return None
    # Find root mod p.
    root = None
    for x in range(p):
        if (x * x) % p == a % p:
            root = x
            break
    need(root is not None and root % p != 0, "nonzero root mod p")
    # Hensel lift x^2 = a from p^k to p^{k+1}.
    mod = p
    for _ in range(1, w):
        # Solve (root + t*mod)^2 ≡ a mod (mod*p): 2*root*t ≡ (a-root^2)/mod mod p.
        diff = (a - root * root) // mod
        inv = pow((2 * root) % p, -1, p)
        t = (diff * inv) % p
        root = root + t * mod
        mod *= p
    need((root * root) % M == a % M, "lifted square root")
    return root % M


def single_factor_norm_involutory_exists(a0, modulus):
    """Shared scale s on (H'_1,D'_0): need a0*s≡1 and s^2≡1."""
    for s in range(modulus):
        if (s * s) % modulus == 1 and (a0 * s) % modulus == 1:
            return True
    return False


def dual_scales(a0, modulus):
    inv = pow(a0, -1, modulus)
    return inv, a0  # (s_H1, s_D0)


def target_weights(a0, modulus):
    inv = pow(a0, -1, modulus)
    return a0 % modulus, inv


def fa_banks(h, d, a0, modulus):
    """One-bank F_a for a=(a0,1): H'=(a0 d1, d0), D'=(h1, inv(a0) h0)."""
    inv = pow(a0, -1, modulus)
    h0, h1 = h
    d0, d1 = d
    nh = ((a0 * d1) % modulus, d0 % modulus)
    nd = (h1 % modulus, (h0 * inv) % modulus)
    return nh, nd


def norm_dual(nh, nd, s_h1, s_d0, modulus):
    """Scale H'_1 by s_H1 and D'_0 by s_D0 (same two-coordinate support)."""
    return (nh[0], (nh[1] * s_h1) % modulus), ((nd[0] * s_d0) % modulus, nd[1])


def fa_target(h, d, weights, modulus):
    p0, p1 = weights
    inv0 = pow(p0, -1, modulus)
    inv1 = pow(p1, -1, modulus)
    h0, h1 = h
    d0, d1 = d
    nh = ((p0 * d1) % modulus, (p1 * d0) % modulus)
    nd = ((h1 * inv1) % modulus, (h0 * inv0) % modulus)
    return nh, nd


def bank_identity_holds(a0, modulus, exhaust=True):
    s_h1, s_d0 = dual_scales(a0, modulus)
    weights = target_weights(a0, modulus)
    need((weights[0] * weights[1]) % modulus == 1, "target involutory")
    need((s_h1 * s_d0) % modulus == 1, "scale reciprocity")
    if exhaust and modulus * modulus <= BANK_EXHAUST_LIMIT:
        for h0 in range(modulus):
            for h1 in range(modulus):
                for d0 in range(modulus):
                    for d1 in range(modulus):
                        h, d = (h0, h1), (d0, d1)
                        nh, nd = fa_banks(h, d, a0, modulus)
                        got = norm_dual(nh, nd, s_h1, s_d0, modulus)
                        want = fa_target(h, d, weights, modulus)
                        if got != want:
                            return False
        return True
    # Coordinate closed form: Norm o F_a expands to F_(a0,inv) identically.
    # Spot-check a deterministic lattice of residues.
    step = max(1, modulus // 7)
    for h0 in range(0, modulus, step):
        for h1 in range(0, modulus, step):
            for d0 in range(0, modulus, step):
                for d1 in range(0, modulus, step):
                    h, d = (h0, h1), (d0, d1)
                    nh, nd = fa_banks(h, d, a0, modulus)
                    got = norm_dual(nh, nd, s_h1, s_d0, modulus)
                    want = fa_target(h, d, weights, modulus)
                    if got != want:
                        return False
    return True


def analyze_pair(p, w):
    modulus = p**w
    a0 = precision_blind_a0(p, w) % modulus
    need(gcd(a0, modulus) == 1, "a0 unit")
    need(a0 % modulus not in (1, modulus - 1), "a0 not +-1")
    need((a0 * a0) % modulus != 1, "a0^2 != 1 (blocks shared P'=(a0,a0))")
    inv = pow(a0, -1, modulus)
    s_h1, s_d0 = dual_scales(a0, modulus)
    tw = target_weights(a0, modulus)
    single = single_factor_norm_involutory_exists(a0, modulus)
    need(not single, "single-factor obstructed")
    square = is_unit_quadratic_residue(a0, p, w)
    need(square, "a0 always unit QR for odd p")
    root = find_unit_square_root(a0, p, w)
    need(root is not None, "explicit square root")
    need(bank_identity_holds(a0, modulus), "dual-scale bank identity")
    return {
        "p": p,
        "w": w,
        "modulus": modulus,
        "a0": a0,
        "inv_a0": inv,
        "scale_H1": s_h1,
        "scale_D0": s_d0,
        "target_weights": list(tw),
        "single_factor_exists": False,
        "a0_is_unit_square": True,
        "square_root": root,
        "bank_exhaust": modulus * modulus <= BANK_EXHAUST_LIMIT,
    }


def build_certificate():
    grid = []
    for p, w in certificate_grid():
        grid.append(analyze_pair(p, w))
    # Cross-check the published #4063 (3,2) dual scales.
    row32 = next(r for r in grid if r["p"] == 3 and r["w"] == 2)
    need(row32["a0"] == CROSSCHECK_P3W2["a0"], "p=3,w=2 a0")
    need(row32["inv_a0"] == CROSSCHECK_P3W2["inv_a0"], "p=3,w=2 inv")
    need(row32["scale_H1"] == CROSSCHECK_P3W2["scale_H1"], "p=3,w=2 s_H1")
    need(row32["scale_D0"] == CROSSCHECK_P3W2["scale_D0"], "p=3,w=2 s_D0")
    need(list(row32["target_weights"]) == list(CROSSCHECK_P3W2["target_weights"]), "target")
    return {
        "schema_version": 1,
        "package": "research/precision-blind-dual-scale-existence",
        "claim": (
            "Every odd-prime-power precision-blind a=(1+p^{w-1},1) admits dual-scale "
            "Norm on (H'_1,D'_0) into reciprocal (a0,a0^{-1}); single-factor never; "
            "a0 always unit QR; no Boolean meters; no new kappa."
        ),
        "answers": {"pr": 4063, "open_question": 1},
        "kappa_decimal": KAPPA_DECIMAL,
        "kappa_fraction": KAPPA_FRACTION,
        "no_new_kappa": True,
        "grid": {
            "primes": list(PRIMES),
            "widths": list(WIDTHS),
            "max_modulus": MAX_MODULUS,
            "pairs": len(grid),
        },
        "pairs": grid,
        "square_classification": "always_unit_quadratic_residue",
        "dual_scale_depends_on_square_root": False,
        "single_factor_exists_count": 0,
        "boolean_meter_inventory": False,
        "crosscheck_4063_p3w2": CROSSCHECK_P3W2,
    }
