"""Exact identity space of mixed positive-Q8 call-space compressions.

Standard library only. Prints PASS_Q8_MIXED_SHEAR_IDENTITY_SPACE on success.
"""
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
UNITS = "1ijk"
UNIT_TABLE = {  # (left, right) -> (sign bit, unit)
    "11": (0, "1"), "1i": (0, "i"), "1j": (0, "j"), "1k": (0, "k"),
    "i1": (0, "i"), "ii": (1, "1"), "ij": (0, "k"), "ik": (1, "j"),
    "j1": (0, "j"), "ji": (1, "k"), "jj": (1, "1"), "jk": (0, "i"),
    "k1": (0, "k"), "ki": (0, "j"), "kj": (1, "i"), "kk": (1, "1"),
}
ONE, I_EL, J_EL = 1, 1 << 1, 1 << 2
ZI, ZJ = 1 << 5, 1 << 6          # group elements -i and -j (index 4*sign+unit)
TARGET_CODE = {"zi": ZI, "zj": ZJ, "1": ONE}
LABEL = {"i": I_EL, "j": J_EL}
DEG = 3                          # monomials E L E ... L E with at most DEG factors L


def check(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)


def gmul(a, b):
    sa, ua = divmod(a, 4)
    sb, ub = divmod(b, 4)
    s, u = UNIT_TABLE[UNITS[ua] + UNITS[ub]]
    return 4 * ((sa + sb + s) % 2) + UNITS.index(u)


def amul(x, y):
    """Product in F2[Q8]; elements are 8-bit masks over group indices."""
    r = 0
    for a in range(8):
        if x >> a & 1:
            for b in range(8):
                if y >> b & 1:
                    r ^= 1 << gmul(a, b)
    return r


ALPHA, BETA = ONE ^ I_EL, ONE ^ J_EL


def word_element(w):
    r = ONE
    for c in w:
        r = amul(r, ALPHA if c == "i" else BETA)
    return r


BASIS_NAMES = ["1", "a", "b", "aa", "ab", "aaa", "aab", "aaab"]
BASIS = [word_element(w) for w in ("", "i", "j", "ii", "ij", "iii", "iij", "iiij")]


def coords(x):
    for mask in range(256):
        y = 0
        for t in range(8):
            if mask >> t & 1:
                y ^= BASIS[t]
        if y == x:
            return mask
    raise SystemExit("FAIL: element outside basis span")


MONS = ["".join(p) for d in range(1, DEG + 2) for p in itertools.product("ij", repeat=d)]
COLS = MONS + ["Pi", "Pj"]
NCOL = len(COLS)


def coefficient_equations():
    """Basis coefficient e of the endpoint: sum_w [x_w]_e X M_w Y = [target]_e."""
    eqs = {}
    for e in range(1, 8):
        c = 0
        for k, m in enumerate(MONS):
            if coords(word_element(m)) >> e & 1:
                c |= 1 << k
        if coords(ZI) >> e & 1:
            c |= 1 << len(MONS)
        if coords(ZJ) >> e & 1:
            c |= 1 << (len(MONS) + 1)
        eqs[BASIS_NAMES[e]] = c
    return eqs


def dot(a, b):
    return bin(a & b).count("1") & 1


def endpoint(target_len, calls):
    """Exact matrix product D_{n-1}...D_0 over F2[Q8]."""
    r = target_len
    w = [[ONE if p == q else 0 for q in range(r)] for p in range(r)]
    for g, u, v in calls:
        check(dot(u, v) == 1, "call is not an idempotent projector")
        x = ONE ^ LABEL[g]
        new = [row[:] for row in w]
        for p in range(r):
            if u >> p & 1:
                for q in range(r):
                    acc = 0
                    for s in range(r):
                        if v >> s & 1:
                            acc ^= w[s][q]
                    new[p][q] ^= amul(x, acc)
        w = new
    return w


def is_exact(target, calls):
    diag = [TARGET_CODE[c] for c in target]
    w = endpoint(len(diag), calls)
    return all(w[p][q] == (diag[p] if p == q else 0)
               for p in range(len(diag)) for q in range(len(diag)))


def compression_rows(target, calls):
    """One row per active (p,q): bits of (X M Y)_{pq} per monomial, then Pi, Pj."""
    act = [p for p, c in enumerate(target) if c != "1"]
    n = len(calls)
    labs = [c[0] for c in calls]
    ymask = [sum(((calls[l][2] >> q) & 1) << k for k, q in enumerate(act)) for l in range(n)]
    chain = {}
    for m in sorted(MONS, key=len):
        if len(m) == 1:
            chain[m] = [ymask[l] if labs[l] == m else 0 for l in range(n)]
            continue
        sub = chain[m[1:]]
        vals = []
        for l in range(n):
            x = 0
            if labs[l] == m[0]:
                for a in range(l):
                    if dot(calls[l][2], calls[a][1]):
                        x ^= sub[a]
            vals.append(x)
        chain[m] = vals
    rows = []
    for p in act:
        ent = [0] * len(MONS)
        for k, m in enumerate(MONS):
            for l in range(n):
                if calls[l][1] >> p & 1:
                    ent[k] ^= chain[m][l]
        for kq, q in enumerate(act):
            row = sum(((ent[k] >> kq) & 1) << k for k in range(len(MONS)))
            if p == q:
                row |= 1 << (len(MONS) + (0 if target[p] == "zi" else 1))
            rows.append(row)
    return rows


def rref(vectors, basis=None):
    basis = dict(basis or {})
    for v in vectors:
        for piv in sorted(basis, reverse=True):
            if v >> piv & 1:
                v ^= basis[piv]
        if v:
            piv = v.bit_length() - 1
            for k in list(basis):
                if basis[k] >> piv & 1:
                    basis[k] ^= v
            basis[piv] = v
    return basis


def in_span(v, basis):
    for piv in sorted(basis, reverse=True):
        if v >> piv & 1:
            v ^= basis[piv]
    return v == 0


# ---- polynomials in the label blocks E_a L E_b (sets of label words) ----
IDENT = frozenset({"i", "j"})


def pmul(p, q):
    out = set()
    for u in p:
        for v in q:
            if u[-1] == v[0]:
                out ^= {u + v[1:]}
    return frozenset(out)


def padd(*ps):
    out = set()
    for p in ps:
        out ^= set(p)
    return frozenset(out)


def pvec(p):
    """Compression vector of X p Y, or None if p leaves the degree-DEG calculus."""
    if any(len(w) > DEG + 1 for w in p):
        return None
    return sum(1 << MONS.index(w) for w in p)


def check_identity_space(eqs, witnesses):
    rows = []
    for item in witnesses:
        check(is_exact(item["target"], item["calls"]), "witness word is not exact")
        rows.extend(compression_rows(item["target"], item["calls"]))
    for name, c in eqs.items():
        check(all(dot(c, r) == 0 for r in rows), "equation %s fails on a witness" % name)
    eq_basis = rref(eqs.values())
    row_basis = rref(rows)
    check(len(eq_basis) == 7, "coefficient equations are not independent")
    check(len(row_basis) == NCOL - 7, "witness rank is %d" % len(row_basis))
    return eq_basis, rows


def shear_classes(eq_basis):
    strict = [m for m in MONS if 2 <= len(m) <= 3]
    shears = []
    for k in range(1, len(strict) + 1):
        for sub in itertools.combinations(strict, k):
            h = frozenset(sub)
            if in_span(pvec(padd(IDENT, h)), eq_basis):
                shears.append(h)
    products = 0
    for m1, m2 in itertools.product(shears, repeat=2):
        v = pvec(pmul(padd(IDENT, m1), padd(IDENT, m2)))
        if v is None:
            continue
        products += 1
        check(not in_span(v, eq_basis), "a shear product is an identity")
    return shears, products


def block_matrix(calls, poly):
    """Call-space operator for a block polynomial, as row bitmasks."""
    n = len(calls)
    labs = [c[0] for c in calls]
    lmat = [[dot(calls[l][2], calls[a][1]) if l > a else 0 for a in range(n)] for l in range(n)]
    out = [0] * n
    for w in poly:
        for chain in itertools.combinations(range(n - 1, -1, -1), len(w)):
            if all(labs[chain[k]] == w[k] for k in range(len(w))) and \
               all(lmat[chain[k]][chain[k + 1]] for k in range(len(w) - 1)):
                out[chain[0]] ^= 1 << chain[-1]
    return out


def rank(vs):
    return len(rref(vs))


def images(target, calls, polys):
    act = [p for p, c in enumerate(target) if c != "1"]
    n = len(calls)
    ucols = [sum(((calls[l][2] >> q) & 1) << l for l in range(n)) for q in act]
    xrows = [sum(((calls[l][1] >> p) & 1) << l for l in range(n)) for p in act]
    out = {}
    for name, poly in polys.items():
        mat = block_matrix(calls, poly)
        img = [sum((dot(mat[l], u)) << l for l in range(n)) for u in ucols]
        check(rank(img) == len(act), "shear image lost rank")
        check(all(dot(x, v) == 0 for x in xrows for v in img), "shear image not in ker X")
        out[name] = img
    return out


# ---- complete meet-in-the-middle census of exact words ----
def ginv(a):
    return next(b for b in range(8) if gmul(a, b) == 0)


def call_matrix(r, x, u, v):
    return tuple(tuple(x if (u >> p & 1 and v >> q & 1) else 0 for q in range(r)) for p in range(r))


def mat_mul(a, b, r):
    out = []
    for p in range(r):
        row = []
        for q in range(r):
            acc = 0
            for s in range(r):
                if a[p][s] and b[s][q]:
                    acc ^= amul(a[p][s], b[s][q])
            row.append(acc)
        out.append(tuple(row))
    return tuple(out)


def factor(r, g, u, v, inverse):
    elem = 1 << (ginv(LABEL[g].bit_length() - 1) if inverse else LABEL[g].bit_length() - 1)
    m = call_matrix(r, ONE ^ elem, u, v)
    return tuple(tuple(m[p][q] ^ (ONE if p == q else 0) for q in range(r)) for p in range(r))


def census(r, n1, n2):
    """All exact words of length n1+n2 on r roles, every diagonal target in {zi,zj,1}^r."""
    opts = [(g, u, v) for g in "ij" for u in range(1, 1 << r) for v in range(1, 1 << r) if dot(u, v)]
    ident = tuple(tuple(ONE if p == q else 0 for q in range(r)) for p in range(r))
    targets = {}
    for diag in itertools.product(["zi", "zj", "1"], repeat=r):
        if diag.count("1") == r:
            continue
        targets[diag] = tuple(tuple(TARGET_CODE[diag[p]] if p == q else 0 for q in range(r))
                              for p in range(r))
    tabs = {d: {} for d in targets}
    for w in itertools.product(opts, repeat=n1):
        pinv = ident
        for g, u, v in w:                      # D_0^-1 D_1^-1 ... D_{n1-1}^-1
            pinv = mat_mul(pinv, factor(r, g, u, v, True), r)
        for d, t in targets.items():
            tabs[d].setdefault(mat_mul(t, pinv, r), []).append(w)
    found = {d: [] for d in targets}
    for w2 in itertools.product(opts, repeat=n2):
        s2 = ident
        for g, u, v in w2:
            s2 = mat_mul(factor(r, g, u, v, False), s2, r)
        for d in targets:
            for w1 in tabs[d].get(s2, []):
                found[d].append(list(w1 + w2))
    return found


SHEARS = {
    "K1": padd(IDENT, {"ii", "ji", "jj"}),
    "K2": padd(IDENT, {"ii", "ij", "jj"}),
    "Q1": padd(IDENT, {"iii", "iij", "ijj", "jii", "jji", "jjj"}),
    "Q2": padd(IDENT, {"ij", "ji", "iii", "iij", "ijj", "jii", "jji", "jjj"}),
}


def four_span_census(cases):
    report = []
    for r, n1, n2 in cases:
        found = census(r, n1, n2)
        total = mixed = 0
        excess = {}
        for d, ws in found.items():
            for w in ws:
                check(is_exact(list(d), w), "census word is not exact")
                total += 1
                if len({c[0] for c in w}) < 2:
                    continue
                mixed += 1
                img = images(list(d), w, SHEARS)
                e = rank(sum(img.values(), [])) - 2 * (r - list(d).count("1"))
                check(e >= 0, "four shear images span less than 2t")
                excess[e] = excess.get(e, 0) + 1
        report.append({"roles": r, "length": n1 + n2, "exact_words": total,
                       "mixed_label_words": mixed, "span_minus_2t": dict(sorted(excess.items()))})
    return report


def pair_witnesses():
    """Every pair of shear images meets on some exact one-role three-call word."""
    out = {}
    for labs in itertools.product("ij", repeat=3):
        calls = [[g, 1, 1] for g in labs]
        for tgt in ("zi", "zj"):
            if not is_exact([tgt], calls) or len(set(labs)) < 2:
                continue
            img = images([tgt], calls, SHEARS)
            for a, b in itertools.combinations(sorted(SHEARS), 2):
                if rank(img[a] + img[b]) < 2 and (a + "," + b) not in out:
                    out[a + "," + b] = {"target": tgt, "labels": "".join(labs)}
    check(len(out) == 6, "some shear pair is disjoint on every three-call word")
    return out


def controls(eqs, eq_basis, rows):
    check(not is_exact(["zj"], [["i", 1, 1]] * 3), "control: iii accepted as zj")
    check(is_exact(["zi"], [["i", 1, 1]] * 3), "control: direct iii rejected")
    cyclic_k2 = pvec(padd(IDENT, {"".join(w) for w in itertools.product("ij", repeat=3)}))
    check(not in_span(cyclic_k2, eq_basis), "control: cyclic K^2 identity entered the span")
    check(any(dot(cyclic_k2, r) for r in rows), "control: cyclic K^2 identity not refuted")
    broken = eqs["aaa"] ^ (1 << MONS.index("iji"))
    check(any(dot(broken, r) for r in rows), "control: altered aaa equation not refuted")
    homog = images(["zi", "zi"], [["i", 1, 1]] * 3 + [["i", 2, 2]] * 3, SHEARS)
    check(rank(homog["K1"] + homog["Q1"]) == 4, "control: homogeneous K, K^2 images meet")


def main(argv):
    full = "--full" in argv
    eqs = coefficient_equations()
    witnesses = json.loads((HERE / "WITNESS.json").read_text())["identity_witnesses"]
    eq_basis, rows = check_identity_space(eqs, witnesses)
    shears, products = shear_classes(eq_basis)
    check(sorted(map(sorted, shears)) == sorted(sorted(p - IDENT) for p in SHEARS.values()),
          "shear classification differs")
    pairs = pair_witnesses()
    controls(eqs, eq_basis, rows)
    cases = [(1, 1, 2), (2, 2, 3), (2, 3, 3), (2, 3, 4)] + ([(2, 4, 4)] if full else [])
    report = four_span_census(cases)
    result = {
        "monomial_columns": NCOL, "witness_rank": NCOL - 7, "identity_space_dim": 7,
        "equations": {k: " + ".join(COLS[i] for i in range(NCOL) if c >> i & 1) for k, c in eqs.items()},
        "shears": {k: sorted(v - IDENT, key=lambda w: (len(w), w)) for k, v in SHEARS.items()},
        "shear_products_checked": products, "pair_witnesses": pairs, "census": report,
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    print("PASS_Q8_MIXED_SHEAR_IDENTITY_SPACE")


if __name__ == "__main__":
    main(sys.argv[1:])
