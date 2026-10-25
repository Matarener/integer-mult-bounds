"""Independent model of the paid-call register word problem in F_2[UT_3(F_4)].

Written from the published formal statement, not from any package source:

  H = UT_3(F_4), F_4 = F_2[w]/(w^2 + w + 1),
  (a,b,c)(a',b',c') = (a+a', b+b', c+c' + a b').
  A paid call is D_N(g) = I + ([g] + [1]) N in F_2[H] tensor M_r(F_2),
  with N a rank-one idempotent of M_r(F_2) and g one of the six axis labels
  X_1, X_w, X_{w^2}, Y_1, Y_w, Y_{w^2}.
  Target on r >= 3 registers:
  diag([Z_1], [Z_w], [Z_{w^2}], [1], ..., [1]), Z_c = (0,0,c).

Two layers are provided.

Group layer.  Elements of F_2[H] are 64-bit masks over an explicit product
table; H is built from the F_4 multiplication table.  Used for the group-law
and idempotent-count checks.

Matrix layer.  rho is the 6-dimensional regular representation of F_2[H]
(hence injective), so equality of words in F_2[H] tensor M_r(F_2) is
equivalent to equality of their images under rho tensor id, i.e. to equality
of 6r x 6r binary matrices, which are stored as row bitmasks.  Used for the
witness, deletion and search checks.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# F_4 arithmetic.  Element (x1, x0) is x1*w + x0, encoded as 2*x1 + x0.
# --------------------------------------------------------------------------


def f4_mul(x: int, y: int) -> int:
    x1, x0 = x >> 1, x & 1
    y1, y0 = y >> 1, y & 1
    c1 = x1 * (y1 ^ y0) ^ x0 * y1
    c0 = x1 * y1 ^ x0 * y0
    return (c1 << 1) | c0


def f4_add(x: int, y: int) -> int:
    return x ^ y


# --------------------------------------------------------------------------
# H = UT_3(F_4), order 64.  Index (a << 4) | (b << 2) | c.
# --------------------------------------------------------------------------


def h_index(a: int, b: int, c: int) -> int:
    return (a << 4) | (b << 2) | c


def h_components(i: int) -> tuple[int, int, int]:
    return (i >> 4) & 3, (i >> 2) & 3, i & 3


def h_mul(i: int, j: int) -> int:
    a, b, c = h_components(i)
    d, e, f = h_components(j)
    return h_index(a ^ d, b ^ e, c ^ f ^ f4_mul(a, e))


H_ORDER = 64
H_MUL = [[h_mul(i, j) for j in range(H_ORDER)] for i in range(H_ORDER)]
H_IDENTITY = h_index(0, 0, 0)

X_LABELS = (("X_1", h_index(1, 0, 0)), ("X_w", h_index(2, 0, 0)),
            ("X_w2", h_index(3, 0, 0)))
Y_LABELS = (("Y_1", h_index(0, 1, 0)), ("Y_w", h_index(0, 2, 0)),
            ("Y_w2", h_index(0, 3, 0)))
Z_LABELS = (h_index(0, 0, 1), h_index(0, 0, 2), h_index(0, 0, 3))

# Letter tag: 0 = X-type, 1 = Y-type.
LETTERS = tuple([(name, el, 0) for name, el in X_LABELS]
                + [(name, el, 1) for name, el in Y_LABELS])
LETTER_NAME = tuple(name for name, _el, _t in LETTERS)
LETTER_ELEMENT = tuple(el for _n, el, _t in LETTERS)
LETTER_TYPE = tuple(t for _n, _el, t in LETTERS)


def h_inverse(i: int) -> int:
    for j in range(H_ORDER):
        if H_MUL[i][j] == H_IDENTITY:
            return j
    raise AssertionError("no inverse")


def commutator(i: int, j: int) -> int:
    return H_MUL[H_MUL[i][j]][h_inverse(H_MUL[j][i])]


# --------------------------------------------------------------------------
# Group-algebra masks over H (cite: product table above).
# --------------------------------------------------------------------------


def ga_basis(i: int) -> int:
    return 1 << i


def ga_mul(left: int, right: int) -> int:
    acc = 0
    bits = right
    while bits:
        low = bits & -bits
        j = low.bit_length() - 1
        bits ^= low
        src = left
        while src:
            slow = src & -src
            i = slow.bit_length() - 1
            src ^= slow
            acc ^= 1 << H_MUL[i][j]
    return acc


# --------------------------------------------------------------------------
# The six paid labels and the regular-representation matrix layer.
# --------------------------------------------------------------------------


def f4_reg(alpha: int) -> list[int]:
    """2x2 rows of left multiplication by alpha on the basis (1, w)."""
    col0 = f4_mul(alpha, 1)
    col1 = f4_mul(alpha, 2)
    rows = [0, 0]
    for out_row in range(2):
        bit = 0
        for in_col, value in enumerate((col0, col1)):
            if (value >> out_row) & 1:
                bit |= 1 << in_col
        rows[out_row] = bit
    return rows


def rho(h: int) -> list[int]:
    """6x6 binary rows of the regular representation of h in F_2[H]."""
    a, b, c = h_components(h)
    blocks = [[None, None, None], [None, None, None], [None, None, None]]
    blocks[0][1] = f4_reg(a)
    blocks[1][2] = f4_reg(b)
    blocks[0][2] = f4_reg(c)
    rows = [0] * 6
    for br in range(3):
        for bc in range(3):
            blk = blocks[br][bc]
            if blk is None:
                continue
            for r in range(2):
                for ccol in range(2):
                    if (blk[r] >> ccol) & 1:
                        rows[2 * br + r] |= 1 << (2 * bc + ccol)
    for i in range(6):
        rows[i] ^= 1 << i
    return rows


def kron_block_rows(base6: list[int], n: int, r: int) -> list[int]:
    """Row bitmasks of base6 (6x6) tensor N, with N a bit-matrix on r bits."""
    out = [0] * (6 * r)
    for i in range(6):
        for j in range(6):
            if (base6[i] >> j) & 1:
                for p in range(r):
                    for q in range(r):
                        if (n[p] >> q) & 1:
                            out[6 * p + i] |= 1 << (6 * q + j)
    return out


def identity_rows(size: int) -> list[int]:
    return [1 << i for i in range(size)]


def mat_mul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * len(a)
    for i, row in enumerate(a):
        acc = 0
        bits = row
        while bits:
            low = bits & -bits
            k = low.bit_length() - 1
            bits ^= low
            acc ^= b[k]
        out[i] = acc
    return out


def call_matrix(letter: int, n: list[int], r: int) -> list[int]:
    """D_N(g) = I + (rho(g) + I) tensor N as a 6r x 6r binary matrix."""
    base = [row ^ (1 << i) for i, row in enumerate(rho(LETTER_ELEMENT[letter]))]
    out = kron_block_rows(base, n, r)
    for i in range(6 * r):
        out[i] ^= 1 << i
    return out


def target_matrix(r: int) -> list[int]:
    """Image of diag([Z_1],[Z_w],[Z_w^2],[1],...,[1]) under rho tensor id."""
    out = identity_rows(6 * r)
    for reg in range(3):
        block = [row ^ (1 << i) for i, row in enumerate(rho(Z_LABELS[reg]))]
        for i in range(6):
            for j in range(6):
                if (block[i] >> j) & 1:
                    out[6 * reg + i] |= 1 << (6 * reg + j)
    return out


def word_product(word: list[tuple[int, list[int]]], r: int) -> list[int]:
    acc = identity_rows(6 * r)
    for letter, n in word:
        acc = mat_mul(call_matrix(letter, n, r), acc)
    return acc


def realizes(word: list[tuple[int, list[int]]], r: int) -> bool:
    return word_product(word, r) == target_matrix(r)


# --------------------------------------------------------------------------
# Rank-one idempotents of M_r(F_2).
# --------------------------------------------------------------------------


def bit_matrix_rows(bits: int, r: int) -> list[int]:
    return [(bits >> (r * i)) & ((1 << r) - 1) for i in range(r)]


def mat_entry(n: list[int], i: int, j: int) -> int:
    return (n[i] >> j) & 1


def mat_product(a: list[int], b: list[int]) -> list[int]:
    out = [0] * len(a)
    for i, row in enumerate(a):
        acc = 0
        for k in range(len(a)):
            if (row >> k) & 1:
                acc ^= b[k]
        out[i] = acc
    return out


def is_idempotent(n: list[int]) -> bool:
    return mat_product(n, n) == n


def dot(u: int, v: int) -> int:
    return (u & v).bit_count() & 1


def rank_one_idempotents(r: int) -> list[list[int]]:
    """All N = u v^T with v.u = 1 and u != 0."""
    found = []
    for u in range(1, 1 << r):
        for v in range(1 << r):
            if dot(v, u) != 1:
                continue
            n = [0] * r
            for i in range(r):
                if (u >> i) & 1:
                    n[i] = v
            found.append(n)
    return found


def projector(r: int, index: int) -> list[int]:
    return [1 << index if i == index else 0 for i in range(r)]
