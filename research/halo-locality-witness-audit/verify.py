"""Exact audit of the HALO.md polynomial locality witness (PR4100).

HALO.md, used by GAUSSIAN.md "Core locality and explicit enumeration of
corrections", states for a periodic banded H with spectrum of H*H in
[c^-2, c^2] (c = p^10 there) and bandwidth W:

  P = c^-2 sum_{j<J} Q^j H*,  Q = I - c^-2 H*H,
  (1) P has bandwidth <= (2J+1)W;
  (2) ||P - H^-1||_2 <= c exp(-J c^-4);
  (3) a row at distance >= A > bandwidth from a section edge equals the
      corresponding row of the global P exactly.

This script checks those statements in exact rational arithmetic on
scaled instances (small c, J, W), with two rejecting controls, and checks
the integer parameter inequalities HALO.md uses at its real parameters
for every p in a bounded range. It is a finite certificate for the stated
instances; the all-size argument is the written proof in README.md.

Author: Nick Petalas. Apache-2.0.
"""
from fractions import Fraction
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/unconditional-batched-crt/HALO.md"
# Exact HALO.md phrases whose parameters this script checks.
BOUND_PHRASES = (
    "Put Q_i=I-p^-20 H_i^* H_i and J=ceil(p^42).",
    "has physical bandwidth <=(2J+1)W<p^45 eventually",
    "||P_i-H_i^-1||_2 <= p^10 exp(-p^2).",
    "For any row at distance A=ceil(p^48) from a section",
    "Choose dyadic core side L=2^ceil(400 log2 p).",
    "g p^(10g) exp(-p^2),",
)

MAX_N = 32


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def zeros(n):
    return [[Fraction(0)] * n for _ in range(n)]


def eye(n):
    out = zeros(n)
    for i in range(n):
        out[i][i] = Fraction(1)
    return out


def matmul(a, b):
    n, k, m = len(a), len(b), len(b[0])
    out = [[Fraction(0)] * m for _ in range(n)]
    for i in range(n):
        row = a[i]
        for t in range(k):
            x = row[t]
            if x:
                bt = b[t]
                for j in range(m):
                    if bt[j]:
                        out[i][j] += x * bt[j]
    return out


def transpose(a):
    return [list(r) for r in zip(*a)]


def sub(a, b):
    return [[x - y for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(a, s):
    return [[x * s for x in r] for r in a]


def inverse(a):
    n = len(a)
    rows = [list(r) + e for r, e in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j] != 0), None)
        need(pivot is not None, "singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        inv = 1 / rows[j][j]
        rows[j] = [x * inv for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                c = rows[i][j]
                rows[i] = [x - c * y for x, y in zip(rows[i], rows[j])]
    return [r[n:] for r in rows]


def positive_definite(a):
    """Exact LDL^T without pivoting: a symmetric matrix is PD iff all pivots > 0."""
    n = len(a)
    m = [list(r) for r in a]
    for k in range(n):
        if m[k][k] <= 0:
            return False
        for i in range(k + 1, n):
            if m[i][k]:
                f = m[i][k] / m[k][k]
                for j in range(k, n):
                    m[i][j] -= f * m[k][j]
    return True


def cyclic_distance(i, j, n):
    d = abs(i - j) % n
    return min(d, n - d)


def bandwidth(a, n):
    return max((cyclic_distance(i, j, n) for i in range(n) for j in range(n) if a[i][j]), default=0)


def banded_h(n, w, rng):
    """H = I - E, E cyclic band w, entries k/(8w) with |k| <= 1: row sum of |E| <= 1/4."""
    h = eye(n)
    for i in range(n):
        for d in range(-w, w + 1):
            if d:
                h[i][(i + d) % n] -= Fraction(rng.choice((-1, 1)), 8 * w)
    return h


def spectrum_inside(h, c2):
    """c^-2 I < H^T H < c^2 I, strictly, decided exactly."""
    g = matmul(transpose(h), h)
    n = len(h)
    upper = sub(scale(eye(n), c2), g)
    lower = sub(g, scale(eye(n), 1 / c2))
    return positive_definite(upper) and positive_definite(lower)


def witness(h, c2, j_terms):
    """Return P, Q^J for the Neumann polynomial of HALO.md."""
    n = len(h)
    ht = transpose(h)
    q = sub(eye(n), scale(matmul(ht, h), 1 / c2))
    term = ht
    total = zeros(n)
    for _ in range(j_terms):
        total = [[x + y for x, y in zip(r, s)] for r, s in zip(total, term)]
        term = matmul(q, term)
    qj = eye(n)
    for _ in range(j_terms):
        qj = matmul(q, qj)
    return scale(total, 1 / c2), qj


def section(a, idx):
    return [[a[i][j] for j in idx] for i in idx]


def check_instance(n, w, j_terms, seed, c2):
    need(n <= MAX_N, "instance size bound")
    rng = random.Random(seed)
    h = banded_h(n, w, rng)
    need(spectrum_inside(h, c2), "global spectral hypothesis")
    p, qj = witness(h, c2, j_terms)
    hinv = inverse(h)
    # Exact error identity P - H^-1 = -Q^J H^-1.
    err = sub(p, hinv)
    need(err == scale(matmul(qj, hinv), -1), "error identity")
    # ||Q^J H^-1||_2^2 < c^2 (1 - c^-4)^(2J): exact PD certificate.
    m = matmul(qj, hinv)
    bound = c2 * (1 - 1 / (c2 * c2)) ** (2 * j_terms)
    need(positive_definite(sub(scale(eye(n), bound), matmul(transpose(m), m))), "error bound")
    # Bandwidth: exactly (2J-1)W, within HALO.md's (2J+1)W.
    bw = bandwidth(p, n)
    need(bw == (2 * j_terms - 1) * w, f"bandwidth {bw}")
    # Section rows. The section omits two adjacent cyclic positions.
    idx = list(range(n - 2))
    hs = section(h, idx)
    need(spectrum_inside(hs, c2), "section spectral hypothesis")
    ps, _ = witness(hs, c2, j_terms)
    radius = (2 * j_terms - 1) * w
    exact_rows = differing_at_radius = 0
    for a, r in enumerate(idx):
        dist = min(cyclic_distance(r, o, n) for o in (n - 2, n - 1))
        same = ps[a] == [p[r][c] for c in idx] and all(p[r][o] == 0 for o in (n - 2, n - 1))
        if dist > radius:
            need(same, f"row {r} at distance {dist} differs")
            exact_rows += 1
        elif dist == radius and not same:
            differing_at_radius += 1
    need(exact_rows > 0, "no interior rows tested")
    # Sharpness control: one step closer, exactness fails.
    need(differing_at_radius > 0, "radius not sharp on this instance")
    return {"n": n, "W": w, "J": j_terms, "seed": seed, "bandwidth": bw,
            "exact_rows": exact_rows, "rows_differing_at_radius": differing_at_radius}


def control_small_c(n, w, j_terms, seed):
    """Control: with c^2 = 1 the spectral hypothesis is rejected."""
    h = banded_h(n, w, random.Random(seed))
    need(not spectrum_inside(h, Fraction(1)), "c^2 = 1 must be rejected")


def control_unbanded(n):
    """Control: E[i,0] = 1/4 (INVERSE-CONDITIONING.md's example) gives a full-width P."""
    h = eye(n)
    for i in range(1, n):
        h[i][0] -= Fraction(1, 4)
    p, _ = witness(h, Fraction(5), 2)
    need(bandwidth(p, n) == n // 2, "unbanded control should fill the cyclic band")


def check_parameters(p_max):
    """HALO.md integer inequalities at J=ceil(p^42), W<=p-1, A=ceil(p^48), L=2^ceil(400 log2 p)."""
    checked = 0
    for p in range(2, p_max + 1):
        j_terms = p ** 42
        w = p - 1
        a_halo = p ** 48
        log2_ceil = (p - 1).bit_length()
        need(2 ** (log2_ceil - 1) < p <= 2 ** log2_ceil, "ceil log2")
        l_core = 2 ** (400 * log2_ceil)
        need((2 * j_terms + 1) * w < p ** 45, "bandwidth below p^45")
        need((2 * j_terms + 1) * w < a_halo, "halo radius exceeds bandwidth")
        need(l_core > 4 * a_halo and l_core >= p ** 400, "core side")
        checked += 1
    # Sparse exponents: epsilon + beta + 3*48 - 400 and epsilon + 48 + 2 - 400 for epsilon, beta < 1.
    need(1 + 1 + 3 * 48 - 400 < 0 and 1 + 48 + 2 - 400 < 0, "sparse exponents")
    return checked


def check_source():
    text = SOURCE.read_text(encoding="utf-8")
    for phrase in BOUND_PHRASES:
        need(phrase in text, f"HALO.md no longer states: {phrase}")
    return len(BOUND_PHRASES)


def main():
    phrases = check_source()
    c2 = Fraction(5)
    cases = [(16, 1, 2, 1), (16, 1, 3, 2), (20, 1, 4, 3), (24, 2, 2, 4), (26, 2, 3, 5)]
    results = [check_instance(n, w, j, s, c2) for n, w, j, s in cases]
    for r in results:
        print("INSTANCE", r)
    control_small_c(16, 1, 2, 1)
    control_unbanded(12)
    checked = check_parameters(64)
    print(f"PASS_HALO_LOCALITY_WITNESS source_phrases={phrases} instances={len(results)} controls=3 parameter_p=2..64 ({checked}) no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
