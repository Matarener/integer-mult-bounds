"""Joint full-guard header law for orthogonal idempotents of arbitrary rank.

Checks the stage-product formula against two independent finite enumerators:
a complete GL_m(F_q) header census, which also checks the Schur-orthogonality
lemma and conditional uniformity directly, and a row/column-pair census for
larger dimensions. F4 uses F2[x]/(x^2+x+1). Fixed case lists, no recursion.
"""

import itertools
import json
import sys
from fractions import Fraction

MAX_DIM = 6
MAX_CANDIDATES = 1_100_000


class Field:
    """Finite field of order 2, 3, 4 or 5 on the labels 0..q-1."""

    def __init__(self, q):
        if q not in (2, 3, 4, 5):
            raise ValueError(f"unsupported field order {q}")
        self.q = q
        if q == 4:
            self.add = [[a ^ b for b in range(4)] for a in range(4)]
            self.mul = [[_f4_mul(a, b) for b in range(4)] for a in range(4)]
        else:
            self.add = [[(a + b) % q for b in range(q)] for a in range(q)]
            self.mul = [[(a * b) % q for b in range(q)] for a in range(q)]
        self.neg = [next(b for b in range(q) if self.add[a][b] == 0) for a in range(q)]
        self.inv = [0] + [next(b for b in range(q) if self.mul[a][b] == 1) for a in range(1, q)]

    def dot(self, xs, ys):
        acc = 0
        for x, y in zip(xs, ys):
            acc = self.add[acc][self.mul[x][y]]
        return acc

    def matmul(self, a, b):
        cols = list(zip(*b))
        return [[self.dot(row, col) for col in cols] for row in a]

    def rank_and_inverse(self, mat):
        """Gauss-Jordan elimination; returns (rank, inverse or None)."""
        n = len(mat)
        aug = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(mat)]
        rank = 0
        for col in range(len(mat[0])):
            piv = next((r for r in range(rank, n) if aug[r][col]), None)
            if piv is None:
                continue
            aug[rank], aug[piv] = aug[piv], aug[rank]
            scale = self.inv[aug[rank][col]]
            aug[rank] = [self.mul[scale][x] for x in aug[rank]]
            for r in range(n):
                f = aug[r][col]
                if r != rank and f:
                    nf = self.neg[f]
                    aug[r] = [self.add[x][self.mul[nf][y]] for x, y in zip(aug[r], aug[rank])]
            rank += 1
        inverse = [row[n:] for row in aug] if rank == n and n == len(mat[0]) else None
        return rank, inverse

    def leading_minors_nonzero(self, mat, depth):
        """True when the leading principal minors of sizes 1..depth are nonzero."""
        for k in range(1, depth + 1):
            rank, _ = self.rank_and_inverse([row[:k] for row in mat[:k]])
            if rank < k:
                return False
        return True


def _f4_mul(a, b):
    prod = 0
    for bit in range(2):
        if (b >> bit) & 1:
            prod ^= a << bit
    if prod & 4:
        prod ^= 0b111
    return prod


def gl_order(q, n):
    out = 1
    for i in range(n):
        out *= q**n - q**i
    return out


def stage_factor(q, dim, ranks):
    """Exact joint first-pivot fraction for orthogonal requests of positive ranks."""
    k = len(ranks)
    d = dim - sum(ranks)
    if k == 0:
        return Fraction(1)
    if d < 0:
        raise ValueError("ranks exceed the dimension")
    num = 1
    for r in ranks:
        num *= q**r - 1
    num *= (q - 1) ** k * q**d - (-1) ** k
    return Fraction(num, q**k * (q**dim - 1))


def joint_law(q, m, ranks):
    """Stage product: the Schur complements stay orthogonal and uniform."""
    total = Fraction(1)
    for t in range(max(ranks, default=0)):
        active = [r - t for r in ranks if r > t]
        total *= stage_factor(q, m - t, active)
    return total


def blocks(ranks):
    out, start = [], 0
    for r in ranks:
        out.append(list(range(start, start + r)))
        start += r
    return out


def request_matrices(field, rows, cols, ranks, depth):
    """Leading depth x depth blocks of G P_i G^-1 from G's top rows and G^-1's left columns."""
    out = []
    for blk in blocks(ranks):
        a = [[row[j] for j in blk] for row in rows[:depth]]
        b = [cols[j][:depth] for j in blk]
        out.append(field.matmul(a, b))
    return out


def pattern(field, rows, cols, ranks):
    depth = max(ranks)
    mats = request_matrices(field, rows, cols, ranks, depth)
    return tuple(field.leading_minors_nonzero(mt, r) for mt, r in zip(mats, ranks))


def compositions(m, max_part):
    """Ordered tuples of positive ranks with sum at most m and parts at most max_part."""
    out = []
    for k in range(1, m + 1):
        for tup in itertools.product(range(1, max_part + 1), repeat=k):
            if sum(tup) <= m:
                out.append(tup)
    return out


def all_matrices(q, rows, cols):
    if q ** (rows * cols) > MAX_CANDIDATES:
        raise ValueError("candidate scan exceeds the fixed bound")
    for ent in itertools.product(range(q), repeat=rows * cols):
        yield [list(ent[i * cols:(i + 1) * cols]) for i in range(rows)]


def coordinate_projector(m, blk):
    return [[int(i == j and i in blk) for j in range(m)] for i in range(m)]


def schur(field, mat):
    """Schur complement of mat at its nonzero (0,0) entry."""
    ainv = field.inv[mat[0][0]]
    n = len(mat)
    out = []
    for i in range(1, n):
        f = field.neg[field.mul[mat[i][0]][ainv]]
        out.append([field.add[mat[i][j]][field.mul[f][mat[0][j]]] for j in range(1, n)])
    return out


def schur_tuple(field, g, ginv, ranks):
    """Check the lemma on one header with every first pivot nonzero; return the S tuple."""
    m = len(g)
    qs = [field.matmul(field.matmul(g, coordinate_projector(m, blk)), ginv) for blk in blocks(ranks)]
    if any(qm[0][0] == 0 for qm in qs):
        return None
    ss = [schur(field, qm) for qm in qs]
    zero = [[0] * (m - 1) for _ in range(m - 1)]
    for i, si in enumerate(ss):
        if field.matmul(si, si) != si or field.rank_and_inverse(si)[0] != ranks[i] - 1:
            raise AssertionError("Schur complement is not an idempotent of rank r-1")
        for j, sj in enumerate(ss):
            if i != j and field.matmul(si, sj) != zero:
                raise AssertionError("Schur complements are not orthogonal")
    return tuple(tuple(map(tuple, s)) for s in ss)


def orbit_size(q, m, ranks):
    """Number of ordered orthogonal idempotent tuples with the given ranks."""
    denom = gl_order(q, m - sum(ranks))
    for r in ranks:
        denom *= gl_order(q, r)
    return gl_order(q, m) // denom


def check_uniform(q, m, ranks, counter):
    reduced = [r - 1 for r in ranks]
    if not counter:
        if stage_factor(q, m, list(ranks)) != 0:
            raise AssertionError("no first-stage survivor where the law is positive")
        return
    if len(set(counter.values())) != 1 or len(counter) != orbit_size(q, m - 1, reduced):
        raise AssertionError(f"conditional Schur tuple not uniform at q={q} m={m} {ranks}")


def distribution_expected(q, m, ranks):
    """Inclusion-exclusion over subfamilies: exact law of the passing set."""
    k = len(ranks)
    out = {}
    for passing in itertools.product((False, True), repeat=k):
        s = [i for i in range(k) if passing[i]]
        total = Fraction(0)
        for extra in range(k - len(s) + 1):
            for more in itertools.combinations([i for i in range(k) if i not in s], extra):
                sub = [ranks[i] for i in sorted(s + list(more))]
                total += (-1) ** extra * joint_law(q, m, sub)
        out[passing] = total
    return out


def compare(label, q, m, ranks, counts, total):
    expected = distribution_expected(q, m, ranks)
    seen = {p: Fraction(c, total) for p, c in counts.items()}
    for p, frac in expected.items():
        if seen.get(p, Fraction(0)) != frac:
            raise AssertionError(f"{label} q={q} m={m} {ranks} {p}: {seen.get(p)} != {frac}")
    joint = expected[tuple([True] * len(ranks))]
    if joint != joint_law(q, m, ranks):
        raise AssertionError("all-pass entry disagrees with the stage product")
    return joint


def gl_census(q, m, tuples):
    """Complete header scan; also checks the Schur lemma and uniformity for every tuple."""
    field = Field(q)
    counts = {t: {} for t in tuples}
    schur_counts = {t: {} for t in tuples}
    headers = 0
    for g in all_matrices(q, m, m):
        _, ginv = field.rank_and_inverse(g)
        if ginv is None:
            continue
        headers += 1
        for t in tuples:
            p = pattern(field, g, ginv, t)
            counts[t][p] = counts[t].get(p, 0) + 1
            s = schur_tuple(field, g, ginv, t)
            if s is not None:
                schur_counts[t][s] = schur_counts[t].get(s, 0) + 1
    if headers != gl_order(q, m):
        raise AssertionError("GL census size mismatch")
    out = []
    for t in tuples:
        check_uniform(q, m, t, schur_counts[t])
        joint = compare("gl", q, m, t, counts[t], headers)
        if cover_number(counts[t], len(t)) != (2 if joint == 0 else 1):
            raise AssertionError(f"header cover number fails at q={q} m={m} {t}")
        out.append({"q": q, "m": m, "ranks": list(t), "joint": str(joint)})
    return headers, out


def completion(field, x):
    """Invertible m x m matrix whose first rows are x, or None if x is rank deficient."""
    m = len(x[0])
    rank, _ = field.rank_and_inverse(x)
    if rank < len(x):
        return None
    rows = [r[:] for r in x]
    for j in range(m):
        cand = rows + [[int(i == j) for i in range(m)]]
        if field.rank_and_inverse(cand)[0] == len(cand):
            rows = cand
    return rows


def pair_census(q, m, depth, tuples):
    """All pairs (X, Y) with X Y = I_depth, via Y = H^-1 [I; C] for each completion H."""
    field = Field(q)
    counts = {t: {} for t in tuples}
    pairs = 0
    free = m - depth
    for x in all_matrices(q, depth, m):
        h = completion(field, x)
        if h is None:
            continue
        _, hinv = field.rank_and_inverse(h)
        for c in all_matrices(q, free, depth):
            stack = [[int(i == j) for j in range(depth)] for i in range(depth)] + c
            y = field.matmul(hinv, stack)
            pairs += 1
            for t in tuples:
                p = pattern(field, x, y, t)
                counts[t][p] = counts[t].get(p, 0) + 1
    expected_pairs = gl_order(q, m) // gl_order(q, m - depth)
    if pairs != expected_pairs:
        raise AssertionError("pair census size mismatch")
    return pairs, [{"q": q, "m": m, "ranks": list(t), "joint": str(compare("pair", q, m, t, counts[t], pairs))}
                   for t in tuples]


def cover_number(counts, k):
    """Fewest realized passing sets whose union is every request (k <= 4 here)."""
    seen = [p for p, c in counts.items() if c]
    for size in range(1, 3):
        for combo in itertools.combinations(seen, size):
            if all(any(p[i] for p in combo) for i in range(k)):
                return size
    return None


def check_zero_locus_and_cover():
    """J vanishes exactly at q=2, complete, even k; then two headers suffice."""
    checked = 0
    for q in (2, 3, 4, 5, 7, 8, 9):
        for m in range(1, 9):
            for t in compositions(m, m):
                zero = joint_law(q, m, t) == 0
                if zero != (q == 2 and sum(t) == m and len(t) % 2 == 0):
                    raise AssertionError(f"zero locus fails at q={q} m={m} {t}")
                if zero and (joint_law(q, m, t[:-1]) == 0 or joint_law(q, m, t[-1:]) == 0):
                    raise AssertionError("two-header cover argument fails")
                checked += 1
    return checked


def control_rejections():
    """Each control must differ from the proved law or be rejected."""
    rejected = 0
    q, m, t = 3, 3, (2, 1)
    product = joint_law(q, m, t[:1]) * joint_law(q, m, t[1:])
    rejected += product != joint_law(q, m, t)
    fixed_d = Fraction(1)
    for s in range(2):
        active = [r - s for r in (2, 2) if r > s]
        fixed_d *= stage_factor(3, sum(active), active)
    rejected += fixed_d != joint_law(3, 4, (2, 2))
    rejected += nonorthogonal_differs()
    counts = {(True,): 9, (False,): 19}
    try:
        compare("control", 2, 3, (1,), counts, 28)
    except AssertionError:
        rejected += 1
    if rejected != 4:
        raise AssertionError(f"only {rejected} of 4 controls rejected")
    return rejected


def nonorthogonal_differs():
    """P1 = E00 and P2 = e0 (e0+e1)^T share an image, so P1 P2 != 0."""
    field = Field(3)
    p1 = coordinate_projector(3, [0])
    p2 = [[1, 1, 0], [0, 0, 0], [0, 0, 0]]
    both = headers = 0
    for g in all_matrices(3, 3, 3):
        _, ginv = field.rank_and_inverse(g)
        if ginv is None:
            continue
        headers += 1
        a1 = field.matmul(field.matmul(g, p1), ginv)[0][0]
        a2 = field.matmul(field.matmul(g, p2), ginv)[0][0]
        both += bool(a1 and a2)
    return Fraction(both, headers) != stage_factor(3, 3, [1, 1])


def check_predecessor_specializations():
    """k=1 gives #4228's closed form; all-rank-one gives #4239's J(q,m,k)."""
    checked = 0
    for q in (2, 3, 4, 5, 7):
        for m in range(1, 10):
            for r in range(1, m):
                s = m - r
                gauss = Fraction(1)
                for i in range(1, r + 1):
                    gauss *= Fraction(q ** (s + i) - 1, q**i - 1)
                single = Fraction(((q - 1) * q**s + 1) ** r, q**r) / gauss
                rank_one = Fraction((q - 1) ** r * ((q - 1) ** r * q ** (m - r) - (-1) ** r),
                                    q**r * (q**m - 1))
                if joint_law(q, m, (r,)) != single or joint_law(q, m, (1,) * r) != rank_one:
                    raise AssertionError(f"specialization fails at q={q} m={m} r={r}")
                checked += 1
    return checked


GL_CASES = ((2, 3), (3, 3), (2, 4))
PAIR_CASES = (
    (3, 4, 2, ((2, 2), (2, 1), (1, 2, 1), (2, 1, 1))),
    (5, 3, 2, ((2, 1), (1, 2))),
    (4, 3, 2, ((2, 1), (1, 1, 1))),
    (2, 6, 2, ((2, 2, 2), (2, 2, 1), (2, 1, 2, 1))),
)


def run_gl_cases():
    headers, rows = 0, []
    for q, m in GL_CASES:
        n, out = gl_census(q, m, compositions(m, m))
        headers += n
        rows += out
    return headers, rows


def main():
    headers, gl_rows = run_gl_cases()
    pairs, pair_rows = 0, []
    for q, m, depth, tuples in PAIR_CASES:
        n, out = pair_census(q, m, depth, tuples)
        pairs += n
        pair_rows += out
    grid = check_zero_locus_and_cover()
    controls = control_rejections()
    specializations = check_predecessor_specializations()
    if joint_law(3, 4, (2, 2)) != Fraction(88, 1755) or joint_law(2, 6, (2, 2, 2)) != Fraction(15, 6944):
        raise AssertionError("pinned example values changed")
    summary = {"controls": controls, "formula_grid": grid, "gl_headers": headers,
               "gl_rank_tuples": len(gl_rows), "pair_rank_tuples": len(pair_rows), "pairs": pairs,
               "specializations": specializations}
    print("PASS_ORTHOGONAL_CHAIN_HEADER_LAW", json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
