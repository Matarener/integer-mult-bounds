"""Exact finite corroboration of the arbitrary-target Pauli history minimum.

Standard library only. Arithmetic is exact over K = Q(i). Every check raises
an exception on failure and stays active under -O. The written all-width
proof is PROOF.md; this program checks its finite instances and controls.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

PACKAGE = Path(__file__).resolve().parent
SOURCE = "research/pauli-twisted-history-threshold/PROOF.md"
MAX_WIDTH_MATRIX = 5      # full End(V) computations: 32 x 32 matrices
MAX_WIDTH_VECTOR = 9      # tensor-power vector computations: 512 entries
MAX_OWNERS = 6


class Check(Exception):
    pass


def require(condition, label):
    if not condition:
        raise Check(label)


# ---------------------------------------------------------------- Q(i)
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
IU = (Fraction(0), Fraction(1))


def q(re, im=0):
    return (Fraction(re), Fraction(im))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def inv(a):
    n = a[0] * a[0] + a[1] * a[1]
    require(n != 0, "inverse of zero")
    return (a[0] / n, -a[1] / n)


def nz(a):
    return a[0] != 0 or a[1] != 0


# ------------------------------------------------------------ matrices
def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def matmul(a, b):
    n, k, m = len(a), len(b), len(b[0])
    out = [[ZERO] * m for _ in range(n)]
    for i in range(n):
        row = out[i]
        for t in range(k):
            x = a[i][t]
            if not nz(x):
                continue
            bt = b[t]
            for j in range(m):
                if nz(bt[j]):
                    row[j] = add(row[j], mul(x, bt[j]))
    return out


def kron(a, b):
    return [[mul(a[i][j], b[k][l]) for j in range(len(a[0])) for l in range(len(b[0]))]
            for i in range(len(a)) for k in range(len(b))]


def tensor_power(m, f):
    require(1 <= f <= MAX_WIDTH_MATRIX, "matrix width capacity")
    out = [[ONE]]
    for _ in range(f):
        out = kron(out, m)
    return out


def madd(a, b):
    return [[add(x, y) for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def mscale(c, a):
    return [[mul(c, x) for x in r] for r in a]


def transpose(a):
    return [list(r) for r in zip(*a)]


X = [[ZERO, ONE], [ONE, ZERO]]
Z = [[ONE, ZERO], [ZERO, q(-1)]]
XZ = matmul(X, Z)
PAULI = [eye(2), X, Z, XZ]


def algebra(f):
    """Return P, C and the basis I, P, C, PC of R at width f."""
    p, c = tensor_power(X, f), tensor_power(Z, f)
    return p, c, [eye(2 ** f), p, c, matmul(p, c)]


# --------------------------------------------------- sparse echelon span
class Span:
    """Incremental exact row echelon basis over Q(i) for sparse vectors."""

    def __init__(self):
        self.rows = {}          # pivot key -> normalized sparse vector

    def reduce(self, vec):
        v = {k: x for k, x in vec.items() if nz(x)}
        for _ in range(len(self.rows) + 1):
            hit = next((k for k in sorted(v) if k in self.rows), None)
            if hit is None:
                return v
            c = v[hit]
            for k, x in self.rows[hit].items():
                y = sub(v.get(k, ZERO), mul(c, x))
                if nz(y):
                    v[k] = y
                else:
                    v.pop(k, None)
        raise Check("echelon reduction did not terminate")

    def add(self, vec):
        v = self.reduce(vec)
        if not v:
            return False
        pivot = min(v)
        s = inv(v[pivot])
        v = {k: mul(s, x) for k, x in v.items()}
        for key, row in self.rows.items():
            c = row.get(pivot)
            if c is not None and nz(c):
                for k, x in v.items():
                    y = sub(row.get(k, ZERO), mul(c, x))
                    if nz(y):
                        row[k] = y
                    else:
                        row.pop(k, None)
        self.rows[pivot] = v
        return True

    def contains(self, vec):
        return not self.reduce(vec)

    def dim(self):
        return len(self.rows)


def flat(row):
    """A history row is a tuple of N matrices; flatten to a sparse vector."""
    out = {}
    for v, a in enumerate(row):
        for i, r in enumerate(a):
            for j, x in enumerate(r):
                if nz(x):
                    out[(v, i, j)] = x
    return out


def unit_row(n_owners, owner, mat):
    size = len(mat)
    zero = [[ZERO] * size for _ in range(size)]
    return tuple(mat if v == owner else zero for v in range(n_owners))


def left(r, row):
    return tuple(matmul(r, a) for a in row)


def row_add(a, b):
    return tuple(madd(x, y) for x, y in zip(a, b))


# ------------------------------------------- invariants of a target H
def characters(f):
    p, c, _ = algebra(f)
    n = 2 ** f
    out = {}
    for e, h in product((1, -1), repeat=2):
        a = madd(eye(n), mscale(q(e), p))
        b = madd(eye(n), mscale(q(h), c))
        out[(e, h)] = mscale(q(Fraction(1, 4)), matmul(a, b))
    return out


def even_profile(h, f, chars):
    """Characters chi with E_chi H outside K E_chi."""
    out = []
    for key, e in chars.items():
        s = Span()
        s.add(flat((e,)))
        if s.add(flat((matmul(e, h),))):
            out.append(key)
    return tuple(sorted(out, reverse=True))


def odd_excess(h, f, basis):
    """s(H) = (dim(R + R H) - 4) / 2 at odd width."""
    s = Span()
    for r in basis:
        s.add(flat((r,)))
    require(s.dim() == 4, "dim R = 4")
    for r in basis:
        s.add(flat((matmul(r, h),)))
    d = s.dim() - 4
    require(d % 2 == 0, "R-module dimension is even at odd width")
    return d // 2


def minimum(targets, f):
    """The exact history minimum mu of PROOF.md Theorem 1."""
    require(1 <= len(targets) <= MAX_OWNERS, "owner capacity")
    if f % 2 == 0:
        chars = characters(f)
        prof = [even_profile(h, f, chars) for h in targets]
        return max((sum(1 for p in prof if k in p) for k in chars), default=0), prof
    _, _, basis = algebra(f)
    ex = [odd_excess(h, f, basis) for h in targets]
    return (sum(ex) + 1) // 2, ex


# ------------------------------------------------- attaining returns
def even_returns(targets, f):
    chars = characters(f)
    n = len(targets)
    mu, prof = minimum(targets, f)
    returns = []
    for k in range(mu):
        t = unit_row(n, 0, [[ZERO] * 2 ** f for _ in range(2 ** f)])
        for key, e in chars.items():
            owners = [j for j in range(n) if key in prof[j]]
            if k < len(owners):
                j = owners[k]
                t = row_add(t, unit_row(n, j, matmul(e, targets[j])))
        returns.append(t)
    return returns


def odd_returns(targets, f):
    p, c, basis = algebra(f)
    n, size = len(targets), 2 ** f
    e11 = mscale(q(Fraction(1, 2)), madd(eye(size), p))
    e21 = mscale(q(Fraction(1, 2)), matmul(madd(eye(size), mscale(q(-1), p)), c))
    span = Span()
    for v in range(n):
        for r in basis:
            span.add(flat(unit_row(n, v, r)))
    ys = []
    for j, h in enumerate(targets):
        for r in basis:
            y = left(e11, unit_row(n, j, matmul(r, h)))
            if span.add(flat(y)):
                ys.append(y)
    returns = []
    for k in range(0, len(ys), 2):
        t = ys[k] if k + 1 == len(ys) else row_add(ys[k], left(e21, ys[k + 1]))
        returns.append(t)
    return returns


def history_contains_targets(targets, f, returns):
    """Every H_j e_j lies in I0 + sum_k R t_k."""
    _, _, basis = algebra(f)
    n = len(targets)
    span = Span()
    for v in range(n):
        for r in basis:
            span.add(flat(unit_row(n, v, r)))
    for t in returns:
        for r in basis:
            span.add(flat(left(r, t)))
    return all(span.contains(flat(unit_row(n, j, h))) for j, h in enumerate(targets))


def certify_instance(name, targets, f, expected_mu):
    mu, invariant = minimum(targets, f)
    require(mu == expected_mu, f"{name}: formula value")
    returns = even_returns(targets, f) if f % 2 == 0 else odd_returns(targets, f)
    require(len(returns) == mu, f"{name}: construction size")
    require(history_contains_targets(targets, f, returns), f"{name}: attainment")
    if mu > 0:
        require(not history_contains_targets(targets, f, returns[:-1]),
                f"{name}: dropping one return must fail")
    return {"name": name, "width": f, "owners": len(targets), "mu": mu,
            "invariant": [list(x) if isinstance(x, tuple) else x for x in invariant]}


# --------------------------------------------------- named 2 x 2 targets
def m2(a, b, c, d):
    return [[a, b], [c, d]]


Y_LIKE = m2(q(2), q(0, -1), q(0, 1), q(2))            # 2I + Y
TARGETS = {
    "2I+X": m2(q(2), q(1), q(1), q(2)),
    "2I+Y": Y_LIKE,
    "2I+Z": m2(q(3), ZERO, ZERO, q(1)),
    "E11": m2(ONE, ZERO, ZERO, ZERO),
    "(1,1)(1,1)^T": m2(ONE, ONE, ONE, ONE),
    "(1,i)(1,i)^T": m2(ONE, IU, IU, q(-1)),
    "(1,2)(1,0)^T": m2(ONE, ZERO, q(2), ZERO),
    "diag(1,i)": m2(ONE, ZERO, ZERO, IU),
    "generic": m2(q(1, 1), q(2), q(-1, 3), q(0, -2)),
}


def instances():
    t = TARGETS
    cases = [
        ("width2 X,Y,Z types", ["2I+X", "2I+Y", "2I+Z"], 2, 2),
        ("width2 two of each type", ["2I+X", "2I+Y", "2I+Z"] * 2, 2, 4),
        ("width2 predecessor family", ["2I+X"] * 3, 2, 3),
        ("width2 S gate and generic", ["diag(1,i)", "generic"], 2, 2),
        ("width3 two rank-one Pauli eigen", ["E11", "(1,1)(1,1)^T"], 3, 1),
        ("width3 rank-one with invertible", ["E11", "(1,i)(1,i)^T", "2I+X"], 3, 2),
        ("width3 generic rank-one", ["(1,2)(1,0)^T", "E11"], 3, 2),
        ("width3 predecessor family", ["2I+X", "2I+Z"], 3, 2),
        ("width4 rank-one Pauli eigen", ["E11", "(1,1)(1,1)^T", "(1,i)(1,i)^T"], 4, 3),
        ("width4 invertible", ["2I+Y", "generic"], 4, 2),
        ("width5 two rank-one Pauli eigen", ["E11", "(1,i)(1,i)^T"], 5, 1),
    ]
    out = []
    for name, keys, f, mu in cases:
        out.append(certify_instance(name, [tensor_power(t[k], f) for k in keys], f, mu))
    return out


# ------------------------------------------------ width-two classification
FORMS = {(1, 1): eye(2), (1, -1): X, (-1, 1): Z, (-1, -1): m2(ZERO, ONE, q(-1), ZERO)}


def proportional(a, b):
    s = Span()
    s.add(flat((b,)))
    return s.contains(flat((a,)))


def form_profile(m):
    mt = transpose(m)
    return tuple(sorted((k for k, b in FORMS.items()
                         if not proportional(matmul(matmul(mt, b), m), b)), reverse=True))


def projectively_pauli(m):
    return any(proportional(m, s) for s in PAULI)


def width_two_census():
    """All 625 matrices with entries in {0, 1, -1, i, -i}."""
    chars = characters(2)
    vals = [ZERO, ONE, q(-1), IU, q(0, -1)]
    sizes = {}
    for a, b, c, d in product(vals, repeat=4):
        m = m2(a, b, c, d)
        prof = even_profile(tensor_power(m, 2), 2, chars)
        require(prof == form_profile(m), "character profile equals form profile")
        require((-1, -1) not in prof, "singlet character is always ordinary")
        pp = projectively_pauli(m)
        require(pp == (len(prof) == 0), "empty profile iff projectively Pauli")
        require(pp or len(prof) >= 2, "non-Pauli profile has at least two characters")
        sizes[len(prof)] = sizes.get(len(prof), 0) + 1
    return {"matrices": 625, "profile_size_counts": {str(k): sizes[k] for k in sorted(sizes)}}


# ------------------------------------------------ rank-one classification
def vec_power(u, f):
    out = [ONE]
    for _ in range(f):
        out = [mul(x, y) for x in out for y in u]
    return out


def apply2(m, u):
    return [add(mul(m[0][0], u[0]), mul(m[0][1], u[1])),
            add(mul(m[1][0], u[0]), mul(m[1][1], u[1]))]


def pauli_eigen(u):
    for s in PAULI[1:]:
        w = apply2(s, u)
        if not nz(sub(mul(w[0], u[1]), mul(w[1], u[0]))):
            return True
    return False


def rank_one_census():
    vals = [ZERO, ONE, q(-1), IU, q(0, -1), q(2), q(1, 1)]
    us = [[a, b] for a, b in product(vals, repeat=2) if nz(a) or nz(b)]
    counts = {"vectors": len(us), "pauli_eigen": 0, "widths": []}
    for f in range(3, MAX_WIDTH_VECTOR + 1):
        counts["widths"].append(f)
        for u in us:
            span = Span()
            for s in PAULI:
                span.add({k: x for k, x in enumerate(vec_power(apply2(s, u), f))})
            expected = 2 if pauli_eigen(u) else 4
            require(span.dim() == expected, "dim R u^f is 2 iff u is a Pauli eigenvector")
    counts["pauli_eigen"] = sum(1 for u in us if pauli_eigen(u))
    return counts


def rank_one_even_profiles():
    """Predicted two-character profiles for Pauli eigenvectors at even widths."""
    cases = {"E11": [ONE, ZERO], "(1,1)": [ONE, ONE], "(1,i)": [ONE, IU]}
    out = {}
    for f in (4, 6, 8):
        for name, u in cases.items():
            vecs = [vec_power(apply2(s, u), f) for s in PAULI]
            prof = []
            for e, h in product((1, -1), repeat=2):
                coef = [ONE, q(e), q(h), q(e * h)]
                w = [ZERO] * len(vecs[0])
                for a, v in zip(coef, vecs):
                    w = [add(x, mul(a, y)) for x, y in zip(w, v)]
                if any(nz(x) for x in w):
                    prof.append([e, h])
            sign = 1 if f % 4 == 0 else -1
            expected = {"E11": [[1, 1], [-1, 1]], "(1,1)": [[1, 1], [1, -1]],
                        "(1,i)": [[1, 1], [-1, -1]] if sign == 1 else [[1, -1], [-1, 1]]}[name]
            require(prof == expected, f"rank-one even profile {name} width {f}")
            out[f"{name}@{f}"] = prof
    return out


# -------------------------------------------------------------- controls
def controls():
    results = []

    def expect_fail(label, fn):
        try:
            fn()
        except Check:
            results.append(label)
            return
        raise Check(f"control accepted: {label}")

    t = TARGETS
    expect_fail("per-owner count q claimed for the width-two X,Y,Z instance",
                lambda: certify_instance("bad", [tensor_power(t[k], 2) for k in ("2I+X", "2I+Y", "2I+Z")], 2, 3))
    expect_fail("one return claimed for two invertible owners at width three",
                lambda: certify_instance("bad", [tensor_power(t[k], 3) for k in ("2I+X", "2I+Z")], 3, 1))

    def corrupted_return():
        hs = [tensor_power(t[k], 2) for k in ("2I+X", "2I+Y", "2I+Z")]
        rs = even_returns(hs, 2)
        rs[0] = rs[1]
        require(history_contains_targets(hs, 2, rs), "duplicated return")
    expect_fail("first return replaced by a copy of the second", corrupted_return)

    def pauli_target_nonordinary():
        chars = characters(2)
        require(even_profile(tensor_power(XZ, 2), 2, chars) != (), "Pauli target")
    expect_fail("projectively Pauli target declared nonordinary", pauli_target_nonordinary)

    def width_one():
        _, ex = minimum([tensor_power(t["generic"], 1)], 1)
        require(ex[0] > 0, "width one")
    expect_fail("width-one target declared nonordinary", width_one)
    return results


def algebra_checks():
    out = []
    for f in range(1, MAX_WIDTH_MATRIX + 1):
        p, c, basis = algebra(f)
        n = 2 ** f
        require(matmul(p, p) == eye(n) and matmul(c, c) == eye(n), "involutions")
        sign = q(1 if f % 2 == 0 else -1)
        require(matmul(p, c) == mscale(sign, matmul(c, p)), "PC = (-1)^f CP")
        s = Span()
        for r in basis:
            s.add(flat((r,)))
        require(s.dim() == 4, "dim R = 4")
        if f % 2 == 0:
            chars = characters(f)
            total = None
            for e in chars.values():
                require(matmul(e, e) == e, "idempotent")
                total = e if total is None else madd(total, e)
            require(total == eye(n), "character idempotents sum to I")
        out.append(f)
    return out


def file_hashes():
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    src = next(r for r in records if r["path"] == SOURCE)
    digest = sha256((PACKAGE.parents[1] / SOURCE).read_bytes()).hexdigest()
    require(digest == src["sha256"], "cited source proof hash")
    files = sorted(p for p in PACKAGE.iterdir() if p.is_file() and p.suffix in {".md", ".json", ".py"})
    require(len(files) <= 10, "package receipt file capacity")
    return {p.name: sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    receipt = {
        "algebra_widths": algebra_checks(),
        "instances": instances(),
        "width_two_census": width_two_census(),
        "rank_one_dimension_census": rank_one_census(),
        "rank_one_even_profiles": rank_one_even_profiles(),
        "controls": controls(),
        "file_sha256": file_hashes(),
        "marker": "PASS_PAULI_HISTORY_ARBITRARY_TARGETS",
    }
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Check, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
