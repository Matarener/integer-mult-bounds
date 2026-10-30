#!/usr/bin/env python3
"""Finite corroboration for the linear lower bound on the Clifford threshold.

Checks, all in exact integer or Gaussian-integer arithmetic:

1. Code lemma: for n = 2, 3, 4 no zero-phase multiset of at most 2n points
   of F2^n has full affine span (exhaustive), and the explicit length-(4n+1)
   tuple has zero phase and full affine span for n = 2..64.
2. Cuspidal cancellation input at n = 2, 3: every coset of every hyperplane
   pointwise stabilizer has zero character sum.
3. Two-qubit transfer, literally: the 3072 monomial matrices are Clifford
   (they normalize the Pauli group) and give 768 projective classes. At every
   width f = 1..4 the residual P_(f mod 4) gives a nonzero class vector v with
   H_f v = 0 for the exact class Gram (tr(U_a^* U_b))^f. The same residual is
   visible at widths 9..12 on the explicit full-span tuple.
4. Rejection controls: the trivial character, the sign with its order-three
   values negated, and a single perturbed coefficient each give H_4 v != 0.
"""

from itertools import combinations_with_replacement, product

MARKER = "PASS_CLIFFORD_THRESHOLD_LINEAR_LOWER"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


# ---------------------------------------------------------------- F2 helpers

def rank_f2(rows):
    rows = [r for r in rows if r]
    rank = 0
    while rows:
        pivot = rows.pop()
        rank += 1
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rank


def full_affine_span(points, n):
    """Points are n-bit ints; full span iff rank of (1, x) columns is n + 1."""
    return rank_f2([(x << 1) | 1 for x in points]) == n + 1


def zero_phase(points, n):
    for j in range(n):
        if sum((x >> j) & 1 for x in points) % 4:
            return False
    for j in range(n):
        for k in range(j + 1, n):
            if sum((x >> j) & (x >> k) & 1 for x in points) % 2:
                return False
    return True


def check_code_lemma():
    counted = {}
    for n in (2, 3, 4):
        zero_count = 0
        for f in range(1, 2 * n + 1):
            for tup in combinations_with_replacement(range(1 << n), f):
                if zero_phase(tup, n):
                    zero_count += 1
                    require(not full_affine_span(tup, n),
                            f"full-span zero-phase tuple n={n} f={f}: {tup}")
        counted[n] = zero_count
    for n in range(2, 65):
        tup = [0] + [1 << j for j in range(n) for _ in range(4)]
        require(len(tup) == 4 * n + 1, "explicit tuple length")
        require(zero_phase(tup, n), f"explicit tuple phase n={n}")
        require(full_affine_span(tup, n), f"explicit tuple span n={n}")
    return counted


# ------------------------------------------------------------- GL(n,2) data

def gl_maps(n):
    """Invertible maps as column tuples; g(x) = XOR of columns at set bits."""
    cols = range(1, 1 << n)
    out = []
    for c in product(cols, repeat=n):
        if rank_f2(list(c)) == n:
            out.append(c)
    return out


def apply(cols, x):
    y = 0
    for j, c in enumerate(cols):
        if (x >> j) & 1:
            y ^= c
    return y


def compose(a, b):
    """(a o b) as columns."""
    return tuple(apply(a, c) for c in b)


def order(cols, n):
    ident = tuple(1 << j for j in range(n))
    g, k = cols, 1
    while g != ident:
        g, k = compose(cols, g), k + 1
    return k


def psi(cols, n):
    """Sum of cuspidal characters of GL(n,2), n = 2, 3 (Green; see PROOF.md).

    n = 2: GL(2,2) = S3 and the cuspidal character is the sign.
    n = 3: the two degree-3 characters sum to 6, -2, 0, 2, -1 on classes of
    order 1, 2, 3, 4, 7.
    """
    o = order(cols, n)
    if n == 2:
        return {1: 1, 2: -1, 3: 1}[o]
    return {1: 6, 2: -2, 3: 0, 4: 2, 7: -1}[o]


def check_cuspidal_cosets():
    checked = 0
    for n in (2, 3):
        maps = gl_maps(n)
        ident = tuple(1 << j for j in range(n))
        transvection = None
        for phi in range(1, 1 << n):          # hyperplane V = ker(phi . x)
            stab = [g for g in maps
                    if all(apply(g, x) == x for x in range(1 << n)
                           if bin(phi & x).count("1") % 2 == 0)]
            require(len(stab) == 1 << (n - 1), "stabilizer size")
            for h in stab:
                if h != ident:
                    require(rank_f2([apply(h, 1 << j) ^ (1 << j)
                                     for j in range(n)]) == 1,
                            "stabilizer element is a transvection")
                    transvection = h
            for g in maps:
                require(sum(psi(compose(g, h), n) for h in stab) == 0,
                        f"coset sum n={n}")
                checked += 1
        d = 1
        for i in range(1, n):
            d *= 2 ** i - 1
        orbits = {2: 1, 3: 2}[n]                 # phi(2^n - 1) / n
        d *= orbits
        require(psi(ident, n) == d, "cuspidal degree")
        require(psi(transvection, n) * (2 ** (n - 1) - 1) == -d,
                "transvection value")
    return checked


# ----------------------------------------------- two-qubit monomial group

N_AXES = 2
DIM = 1 << N_AXES


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def gpow(a, e):
    r = (1, 0)
    for _ in range(e):
        r = gmul(r, a)
    return r


IPOW = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def monomial_group():
    """Elements U(g,t,q): e_x -> i^q(x) e_(g x + t). Returns list of dicts."""
    elems = []
    for lin in gl_maps(N_AXES):
        for t in range(DIM):
            for c in range(4):
                for a in product(range(4), repeat=N_AXES):
                    for b in range(2):
                        ph = []
                        for x in range(DIM):
                            x0, x1 = x & 1, (x >> 1) & 1
                            ph.append((c + a[0] * x0 + a[1] * x1
                                       + 2 * b * x0 * x1) % 4)
                        perm = tuple(apply(lin, x) ^ t for x in range(DIM))
                        elems.append({"lin": lin, "t": t, "c": c,
                                      "perm": perm, "ph": tuple(ph)})
    return elems


def dense(e):
    m = [[(0, 0)] * DIM for _ in range(DIM)]
    for x in range(DIM):
        m[e["perm"][x]][x] = IPOW[e["ph"][x]]
    return m


def matmul(a, b):
    n = len(a)
    out = [[(0, 0)] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] != (0, 0):
                for j in range(n):
                    if b[k][j] != (0, 0):
                        p = gmul(a[i][k], b[k][j])
                        o = out[i][j]
                        out[i][j] = (o[0] + p[0], o[1] + p[1])
    return out


def adjoint(m):
    n = len(m)
    return [[(m[j][i][0], -m[j][i][1]) for j in range(n)] for i in range(n)]


def kron(a, b):
    return [[gmul(a[i // len(b)][j // len(b)], b[i % len(b)][j % len(b)])
             for j in range(len(a) * len(b))] for i in range(len(a) * len(b))]


def paulis():
    i2 = [[(1, 0), (0, 0)], [(0, 0), (1, 0)]]
    x = [[(0, 0), (1, 0)], [(1, 0), (0, 0)]]
    z = [[(1, 0), (0, 0)], [(0, 0), (-1, 0)]]
    singles = {"I": i2, "X": x, "Z": z, "XZ": matmul(x, z)}
    table = {}
    for a, b in product(singles, repeat=2):
        table[(a, b)] = kron(singles[b], singles[a])   # qubit 0 is low bit
    return table


def is_clifford(e, pauli_table):
    u = dense(e)
    ud = adjoint(u)
    targets = []
    for p in pauli_table.values():
        targets.append(p)
    for p in pauli_table.values():
        img = matmul(matmul(u, p), ud)
        ok = False
        for q in targets:
            for s in IPOW:
                if all(img[i][j] == gmul(s, q[i][j])
                       for i in range(DIM) for j in range(DIM)):
                    ok = True
                    break
            if ok:
                break
        if not ok:
            return False
    return True


def class_key(e):
    """Projective class: strip the constant phase c."""
    return (e["perm"], tuple((p - e["c"]) % 4 for p in e["ph"]))


def sign_psi(lin):
    return psi(lin, 2)


def residual(elems, r, coeff_fn):
    """Integer-scaled P_r = |D| * A E_r as {element index: Gaussian int}."""
    out = {}
    for idx, e in enumerate(elems):
        w = coeff_fn(e["lin"])
        if w == 0:
            continue
        s = IPOW[(-r * e["c"]) % 4]
        out[idx] = (w * s[0], w * s[1])
    return out


def class_vector(elems, coeffs, f):
    """Combine scalar lifts at width f: U = i^c U0 gives i^(c f) U0^(x f)."""
    v = {}
    for idx, w in coeffs.items():
        e = elems[idx]
        k = class_key(e)
        term = gmul(w, IPOW[(e["c"] * f) % 4])
        o = v.get(k, (0, 0))
        v[k] = (o[0] + term[0], o[1] + term[1])
    return {k: w for k, w in v.items() if w != (0, 0)}


def trace_star(ka, kb):
    """tr(U_a^* U_b) for class representatives (constant phase zero)."""
    perm_a, ph_a = ka
    perm_b, ph_b = kb
    tot = (0, 0)
    for x in range(DIM):
        if perm_a[x] == perm_b[x]:
            p = IPOW[(ph_b[x] - ph_a[x]) % 4]
            tot = (tot[0] + p[0], tot[1] + p[1])
    return tot


def gram_apply(classes, v, f):
    """Return max |(H_f v)_a| witness: list of nonzero entries (exact)."""
    bad = 0
    for ka in classes:
        acc = (0, 0)
        for kb, w in v.items():
            t = trace_star(ka, kb)
            if t == (0, 0):
                continue
            term = gmul(gpow(t, f), w)
            acc = (acc[0] + term[0], acc[1] + term[1])
        if acc != (0, 0):
            bad += 1
    return bad


def diagonal_entry(elems, coeffs, tup):
    """<tup| rho_f(P) |tup> computed from the literal monomial action."""
    acc = (0, 0)
    fixers = set()
    for idx, w in coeffs.items():
        e = elems[idx]
        if all(e["perm"][x] == x for x in tup):
            fixers.add((e["lin"], e["t"]))
            p = IPOW[sum(e["ph"][x] for x in tup) % 4]
            term = gmul(w, p)
            acc = (acc[0] + term[0], acc[1] + term[1])
    return acc, fixers


def check_two_qubit():
    elems = monomial_group()
    require(len(elems) == 6 * 4 * 128, "monomial group size")
    table = paulis()
    require(all(is_clifford(e, table) for e in elems),
            "every monomial element normalizes the Pauli group")
    classes = sorted({class_key(e) for e in elems})
    require(len(classes) == 768, "projective class count")

    full_tuple = [0] + [1 << j for j in range(N_AXES) for _ in range(4)]
    results = {}
    for f in range(1, 2 * N_AXES + 1):
        r = f % 4
        p = residual(elems, r, sign_psi)
        v = class_vector(elems, p, f)
        require(len(v) > 0, f"nonzero class vector f={f}")
        require(gram_apply(classes, v, f) == 0, f"H_f v = 0 at f={f}")
        results[f] = len(v)
    visible = {}
    for f in range(4 * N_AXES + 1, 4 * N_AXES + 5):
        r = f % 4
        p = residual(elems, r, sign_psi)
        tup = full_tuple + [0] * (f - len(full_tuple))
        entry, fixers = diagonal_entry(elems, p, tup)
        require(len(fixers) == 1, "only the identity affine map fixes tuple")
        require(entry == (128, 0), f"visible diagonal entry at f={f}")
        visible[f] = entry[0]

    # Rejection controls.
    trivial = residual(elems, 0, lambda lin: 1)
    require(gram_apply(classes, class_vector(elems, trivial, 4), 4) > 0,
            "control: trivial character must fail")
    def not_a_character(lin):
        return -1 if lin != tuple(1 << j for j in range(N_AXES)) else 1
    broken = class_vector(elems, residual(elems, 0, not_a_character), 4)
    require(gram_apply(classes, broken, 4) > 0,
            "control: sign with order-three values negated must fail")
    mutated = dict(residual(elems, 0, sign_psi))
    first = min(mutated)
    w = mutated[first]
    mutated[first] = (w[0] + 1, w[1])
    require(gram_apply(classes, class_vector(elems, mutated, 4), 4) > 0,
            "control: perturbed coefficient must fail")
    return results, visible


def main():
    counted = check_code_lemma()
    cosets = check_cuspidal_cosets()
    support, visible = check_two_qubit()
    print("zero-phase multisets of size <= 2n (all lack full span):",
          {n: counted[n] for n in sorted(counted)})
    print("explicit full-span zero-phase tuples of length 4n+1: n=2..64")
    print("cuspidal coset sums checked (n=2,3):", cosets)
    print("two-qubit class-vector support sizes with H_f v = 0:",
          {f: support[f] for f in sorted(support)})
    print("two-qubit visible diagonal entries (scaled by |D|=128):",
          {f: visible[f] for f in sorted(visible)})
    print("rejection controls: trivial character, negated order-three values, "
          "perturbed coefficient")
    print(MARKER)


if __name__ == "__main__":
    main()
