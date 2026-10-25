"""Exhaustive small-ring check of PR4100's NORMAL-FORM.md conjugation identity.

Code-disjoint from the retained elimination: every matrix below is built from
the written formulas in NORMAL-FORM.md. The vendor module is imported only for
the stated agreement comparison. Standard library only.
Nick Petalas. Apache-2.0.
"""
import itertools
import json
import random
import sys
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "research/selected-bit-recursive-closure/vendor"

# (q, w, m): every m-by-m matrix over Z/q^w is enumerated.
EXHAUSTIVE = ((3, 1, 2), (5, 1, 2), (7, 1, 2), (3, 2, 2), (5, 2, 2),
              (3, 3, 2), (3, 1, 3))
# (q, w, m, charts): seeded random charts, all axis sets of each size.
SAMPLED = ((3, 2, 3, 300), (3, 3, 4, 60), (5, 2, 4, 60), (3, 2, 5, 20))
SEED = 4100


def fail(message):
    raise SystemExit(f"FAIL_NORMAL_FORM_AUDIT: {message}")


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, mod):
    return [[sum(x * y for x, y in zip(row, col)) % mod for col in zip(*b)]
            for row in a]


def sub(a, b, mod):
    return [[(x - y) % mod for x, y in zip(r, s)] for r, s in zip(a, b)]


def rev(m):
    return [[int(i + j == m - 1) for j in range(m)] for i in range(m)]


def inv(a, mod):
    """Gauss-Jordan over a local ring Z/q^w; None when not invertible."""
    n = len(a)
    rows = [list(r) + e for r, e in zip(a, eye(n))]
    for j in range(n):
        p = next((i for i in range(j, n) if gcd(rows[i][j], mod) == 1), None)
        if p is None:
            return None
        rows[j], rows[p] = rows[p], rows[j]
        u = pow(rows[j][j], -1, mod)
        rows[j] = [u * x % mod for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x - c * y) % mod for x, y in zip(rows[i], rows[j])]
    return [r[n:] for r in rows]


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def rank_mod_q(p, q):
    a = [[x % q for x in r] for r in p]
    rank, n = 0, len(a)
    for j in range(n):
        piv = next((i for i in range(rank, n) if a[i][j]), None)
        if piv is None:
            continue
        a[rank], a[piv] = a[piv], a[rank]
        u = pow(a[rank][j], -1, q)
        a[rank] = [u * x % q for x in a[rank]]
        for i in range(n):
            if i != rank and a[i][j]:
                c = a[i][j]
                a[i] = [(x - c * y) % q for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank


def northeast(p, r, q, mod):
    """Unit-pivot northeast elimination T = L P C R0; None on a non-unit pivot.

    Returns L, R0 (unit lower triangular), the pivots delta and whether the
    remaining Schur block of the eliminated matrix is zero over Z/q^w.
    """
    m = len(p)
    a = mul(p, rev(m), mod)
    left, right, delta = eye(m), eye(m), []
    for k in range(r):
        col = m - 1 - k
        piv = a[k][col]
        if gcd(piv, q) != 1:
            return None
        delta.append(piv)
        pinv = pow(piv, -1, mod)
        for i in range(k + 1, m):
            c = -a[i][col] * pinv % mod
            a[i] = [(x + c * y) % mod for x, y in zip(a[i], a[k])]
            left[i] = [(x + c * y) % mod for x, y in zip(left[i], left[k])]
        for j in range(col):
            c = -a[k][j] * pinv % mod
            for i in range(m):
                a[i][j] = (a[i][j] + c * a[i][col]) % mod
                right[i][j] = (right[i][j] + c * right[i][col]) % mod
    schur_zero = all(a[i][j] == 0 for i in range(r, m) for j in range(m - r))
    return left, right, delta, schur_zero


def unit_lower(a):
    n = len(a)
    return all(a[i][i] == 1 for i in range(n)) and all(
        a[i][j] == 0 for i in range(n) for j in range(i + 1, n))


def normal_form(p, r, q, mod):
    """Return None (bad packet) or the dict of NORMAL-FORM.md matrices."""
    m = len(p)
    got = northeast(p, r, q, mod)
    if got is None:
        return None
    left, right, delta, schur_zero = got
    if not schur_zero:
        fail("split rank did not force a zero Schur block")
    if not (unit_lower(left) and unit_lower(right)):
        fail("elimination factors are not unit lower triangular")
    c, i_m = rev(m), eye(m)
    e = [[int(i == j and i < r) for j in range(m)] for i in range(m)]
    d = [[(delta[i] if i < r else 1) if i == j else 0 for j in range(m)]
         for i in range(m)]
    dinv = inv(d, mod)
    li, ri = inv(left, mod), inv(right, mod)
    t = mul(mul(mul(left, p, mod), c, mod), right, mod)
    if t != mul(mul(e, d, mod), c, mod):
        fail("T != E D C")
    u = mul(mul(left, p, mod), li, mod)
    s0 = mul(mul(ri, c, mod), li, mod)
    j = mul(mul(c, dinv, mod), e, mod)
    return dict(m=m, P=p, C=c, I=i_m, E=e, D=d, L=left, R0=right, Li=li,
                Ri=ri, T=t, U=u, S0=s0, J=j, delta=delta)


def written_x(nf, mod):
    return sub(mul(nf["S0"], nf["E"], mod), mul(nf["J"], nf["U"], mod), mod)


def conjugated(nf, x, mod):
    m, z = nf["m"], [[0] * nf["m"] for _ in range(nf["m"])]
    p, c, i_m = nf["P"], nf["C"], nf["I"]
    n_p = block(sub(i_m, p, mod), mul(p, c, mod), mul(c, p, mod),
                sub(i_m, mul(mul(c, p, mod), c, mod), mod))
    q_mat = mul(block(i_m, z, x, i_m), block(nf["L"], z, z, nf["Ri"]), mod)
    q_inv = inv(q_mat, mod)
    if q_inv is None:
        fail("Q is not invertible")
    return mul(mul(q_mat, n_p, mod), q_inv, mod), n_p, m


def target(nf, mod):
    i_m, e, t, j = nf["I"], nf["E"], nf["T"], nf["J"]
    return block(sub(i_m, e, mod), t, j, sub(i_m, mul(j, t, mod), mod))


def check_instance(nf, mod, stats):
    """Every written equality, the identity and two mutation controls."""
    stats["checked"] += 1
    m, t, u, s0, j, e = nf["m"], nf["T"], nf["U"], nf["S0"], nf["J"], nf["E"]
    eqs = {"TS0=U": mul(t, s0, mod) == u, "TJ=E": mul(t, j, mod) == e,
           "ET=T": mul(e, t, mod) == t, "UT=T": mul(u, t, mod) == t,
           "EU=U": mul(e, u, mod) == u, "UE=E": mul(u, e, mod) == e}
    for name, ok in eqs.items():
        if not ok:
            fail(f"written equality {name}")
    x = written_x(nf, mod)
    if mul(t, x, mod) != sub(e, u, mod):
        fail("TX != E-U")
    got, _, _ = conjugated(nf, x, mod)
    want = target(nf, mod)
    if got != want:
        fail("Q N(P) Q^-1 != [[I-E,T],[J,I-JT]]")
    # The target is one weighted reversed r-coordinate child.
    r = len(nf["delta"])
    for k in range(m):
        for c in range(m):
            head_tail = want[k][m + c]
            tail_head = want[m + c][k]
            if k < r and c == m - 1 - k:
                ok = (head_tail == nf["delta"][k]
                      and tail_head == pow(nf["delta"][k], -1, mod))
            else:
                ok = head_tail == 0 and tail_head == 0
            if not ok:
                fail("target is not a weighted reversed child")
    # Mutations: the cancellation the note warns about, and a dropped U.
    for name, mutant in (("X=S0E-J", sub(mul(s0, e, mod), j, mod)),
                         ("X=S0E-UJ", sub(mul(s0, e, mod), mul(u, j, mod), mod))):
        if conjugated(nf, mutant, mod)[0] != want:
            stats["mutant_rejections"][name] += 1
    return x


def idempotents_exhaustive(q, w, m):
    mod = q ** w
    for entries in itertools.product(range(mod), repeat=m * m):
        p = [list(entries[i * m:(i + 1) * m]) for i in range(m)]
        if mul(p, p, mod) == p:
            yield p


def gl_order(q, w, m):
    out = q ** ((w - 1) * m * m)
    for i in range(m):
        out *= q ** m - q ** i
    return out


def expected_idempotents(q, w, m, r):
    """|GL_m| / (|GL_r| |GL_(m-r)|) over the local ring Z/q^w."""
    return gl_order(q, w, m) // (gl_order(q, w, r) * gl_order(q, w, m - r))


def vendor_agreement(cn, chart, axes, q, w, nf, x, mod, rng):
    """Compare written X with vendor `cross` (built from its a0=-U[:r] and
    b=-S0[:,:r]) and the executed weighted address map."""
    m, r = len(chart), len(axes)
    low = tuple(tuple(v % q for v in row) for row in chart)
    high = tuple(tuple(v // q for v in row) for row in chart)
    weights = tuple(rng.choice([u for u in range(1, mod) if gcd(u, q) == 1])
                    for _ in range(m))
    prefix = cn.ParentPrefix(q, w, low, high, weights, 1)
    prep = cn.prepare(prefix, tuple(axes))
    if list(prep.pivots) != nf["delta"]:
        return "pivots"
    if [row[:] for row in prep.cross] != x:
        return "cross"
    # Executed map on every basis address equals B N(P) B^-1, B=diag(A,I).
    _, n_p, _ = conjugated(nf, x, mod)
    b = [[(weights[i] if i < m else 1) if i == j else 0 for j in range(2 * m)]
         for i in range(2 * m)]
    want = mul(mul(b, n_p, mod), inv(b, mod), mod)
    for col in range(2 * m):
        vec = [int(i == col) for i in range(2 * m)]
        head, tail = cn.execute_addresses(prep, vec[:m], vec[m:])
        if list(head) + list(tail) != [want[i][col] for i in range(2 * m)]:
            return "executed weighted map"
    return None


def load_vendor():
    sys.path.insert(0, str(VENDOR))
    import controlled_normalizer as cn  # noqa: E402
    return cn


def main():
    cn = load_vendor()
    rng = random.Random(SEED)
    stats = {"checked": 0, "mutant_rejections": {"X=S0E-J": 0, "X=S0E-UJ": 0}}
    rows = []
    for q, w, m in EXHAUSTIVE:
        mod = q ** w
        found = {r: 0 for r in range(1, m)}
        good = {r: 0 for r in range(1, m)}
        for p in idempotents_exhaustive(q, w, m):
            r = rank_mod_q(p, q)
            if not 1 <= r < m:
                continue
            found[r] += 1
            nf = normal_form(p, r, q, mod)
            if nf is None:
                continue
            good[r] += 1
            check_instance(nf, mod, stats)
        for r in range(1, m):
            if found[r] != expected_idempotents(q, w, m, r):
                fail(f"idempotent census q={q} w={w} m={m} r={r}")
            rows.append({"q": q, "w": w, "m": m, "r": r, "mode": "exhaustive",
                         "idempotents": found[r], "good": good[r]})
    vendor_checked = 0
    for q, w, m, charts in SAMPLED + tuple((q, w, m, 0) for q, w, m in EXHAUSTIVE):
        mod = q ** w
        tally = {}
        drawn = 0
        # Every exhaustive domain also gets vendor agreement on 40 charts.
        budget = charts or 40
        while drawn < budget:
            chart = [[rng.randrange(mod) for _ in range(m)] for _ in range(m)]
            ci = inv(chart, mod)
            if ci is None:
                continue
            drawn += 1
            for r in range(1, m):
                for axes in itertools.combinations(range(m), r):
                    p = mul([[row[k] for k in axes] for row in chart],
                            [ci[k] for k in axes], mod)
                    if mul(p, p, mod) != p or rank_mod_q(p, q) != r:
                        fail("chart projector is not a rank-r idempotent")
                    nf = normal_form(p, r, q, mod)
                    key = tally.setdefault(r, [0, 0])
                    key[0] += 1
                    if nf is None:
                        try:
                            cn.prepare(cn.ParentPrefix(
                                q, w, tuple(tuple(v % q for v in row) for row in chart),
                                tuple(tuple(v // q for v in row) for row in chart),
                                (1,) * m, 1), axes)
                        except ValueError as exc:
                            if "nongeneric low class" not in str(exc):
                                fail(f"vendor rejected a bad packet for {exc}")
                            continue
                        fail("vendor accepted a packet with a non-unit pivot")
                    key[1] += 1
                    x = check_instance(nf, mod, stats)
                    why = vendor_agreement(cn, chart, axes, q, w, nf, x, mod, rng)
                    if why:
                        fail(f"vendor disagreement ({why}) q={q} w={w} m={m}")
                    vendor_checked += 1
        if charts:
            for r, (seen, ok) in sorted(tally.items()):
                rows.append({"q": q, "w": w, "m": m, "r": r, "mode": "sampled",
                             "projectors": seen, "good": ok})
    checked = stats["checked"]
    for name, hits in stats["mutant_rejections"].items():
        if hits == 0:
            fail(f"mutation control {name} never rejected")
    print(json.dumps({"rows": rows, "good_instances_checked": checked,
                      "vendor_agreements": vendor_checked,
                      "mutant_rejections": stats["mutant_rejections"]},
                     indent=1))
    print("PASS_NORMAL_FORM_EXHAUSTIVE_AUDIT")


if __name__ == "__main__":
    main()
