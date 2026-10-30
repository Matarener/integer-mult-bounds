#!/usr/bin/env python3
"""Corroborate the two-FULL identity-scratch rank gap. Apache-2.0."""

import hashlib
import random
from pathlib import Path

P = 1_000_003
T = 8
CUTOFF = 2 * T
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EXPECTED = {
    "research/two-full-central-obstruction/PROOF.md":
        "9babe77410543665f197cd1846d71d775d306c97716aedefc6f25f4256f5a699",
    "research/two-full-central-obstruction/grade/PROOF.md":
        "8fd775a9903eca0f53b186d7fb684d9f5f74afc9c105082b3d4981bd950fca33",
}
MARKERS = {
    "research/two-full-central-obstruction/PROOF.md":
        "no theorem here simultaneously grants both extensions",
    "research/two-full-central-obstruction/grade/PROOF.md":
        "additional scratch mixing",
}

# S3 acting on {0,1,2}, indexed so left multiplication is composition.
PERMS = (
    (0, 1, 2),
    (1, 0, 2),
    (2, 1, 0),
    (0, 2, 1),
    (1, 2, 0),
    (2, 0, 1),
)
D = len(PERMS)


def fail(message):
    raise SystemExit("FAIL_TWO_FULL_SCRATCH_MONOMIAL_OBSTRUCTION " + message)


def mul_perm(left, right):
    return tuple(left[right[i]] for i in range(3))


def build_table():
    index = {perm: i for i, perm in enumerate(PERMS)}
    table = [[0] * D for _ in range(D)]
    for i, left in enumerate(PERMS):
        for j, right in enumerate(PERMS):
            table[i][j] = index[mul_perm(left, right)]
    ident = 0
    if any(table[ident][j] != j or table[j][ident] != j for j in range(D)):
        fail("S3 identity")
    seen = {table[1][j] for j in range(D)}
    if len(seen) != D:
        fail("S3 left multiplication is not bijective")
    return table


TABLE = build_table()


def mod(value):
    return value % P


class Elem:
    """Sparse element of K[S3] tensor a nonnegative rank grade."""

    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for grade, coeffs in terms.items():
                self._put(grade, coeffs)

    def _put(self, grade, coeffs):
        if any(coeffs):
            self.terms[grade] = coeffs

    def copy(self):
        return Elem({grade: coeffs[:] for grade, coeffs in self.terms.items()})


def zero():
    return Elem()


def basis(index, grade=0):
    coeffs = [0] * D
    coeffs[index] = 1
    return Elem({grade: coeffs})


def add(left, right):
    out = left.copy()
    for grade, coeffs in right.terms.items():
        acc = out.terms.get(grade, [0] * D)[:]
        for i, value in enumerate(coeffs):
            acc[i] = mod(acc[i] + value)
        if any(acc):
            out.terms[grade] = acc
        else:
            out.terms.pop(grade, None)
    return out


def left_h(h, elem):
    out = zero()
    for grade, coeffs in elem.terms.items():
        acc = [0] * D
        for j, value in enumerate(coeffs):
            if value:
                acc[TABLE[h][j]] = mod(acc[TABLE[h][j]] + value)
        out._put(grade, acc)
    return out


def scale_shift(elem, monomial, shift):
    """Left multiply by one monomial and add `shift` to every grade."""
    coeff, h = monomial
    out = zero()
    for grade, coeffs in elem.terms.items():
        acc = [0] * D
        for j, value in enumerate(coeffs):
            if value:
                acc[TABLE[h][j]] = mod(acc[TABLE[h][j]] + coeff * value)
        out._put(grade + shift, acc)
    return out


def b_mul(poly, elem):
    out = zero()
    for coeff, h in poly:
        out = add(out, scale_shift(elem, (coeff, h), 0))
    return out


def unit(h, shift):
    return (h, shift)


def apply_unit(factor, elem):
    h, shift = factor
    return scale_shift(elem, (1, h), shift)


def poly_id():
    return ((1, 0),)


def poly_h(h):
    return ((1, h),)


def shear(vec, dest, src, central):
    """vec[dest] += central * vec[src]. central is (h, shift) or None."""
    out = [item.copy() for item in vec]
    if central is None:
        return out
    out[dest] = add(out[dest], apply_unit(central, vec[src]))
    return out


def diagonal(vec, factors):
    return [apply_unit(factor, item) if factor else item.copy()
            for factor, item in zip(factors, vec)]


def full(vec, factors, orientation, central):
    if orientation == "upper":
        vec = shear(vec, 0, 1, central)
    elif orientation == "lower":
        vec = shear(vec, 1, 0, central)
    else:
        fail("orientation")
    return diagonal(vec, factors)


def apply_w(matrix, vec):
    out = [zero() for _ in vec]
    for i, row in enumerate(matrix):
        for j, poly in enumerate(row):
            out[i] = add(out[i], b_mul(poly, vec[j]))
    return out


def project(elem, cutoff):
    return Elem({grade: coeffs[:] for grade, coeffs in elem.terms.items()
                 if grade <= cutoff and any(coeffs)})


def pack(vec, cutoff):
    grades = cutoff + 1
    flat = []
    for item in vec:
        projected = project(item, cutoff)
        for grade in range(grades):
            flat.extend(projected.terms.get(grade, [0] * D))
    return flat


def identity_w(n):
    return [[poly_id() if i == j else () for j in range(n)] for i in range(n)]


def permutation_w(n, swap):
    matrix = [[() for _ in range(n)] for _ in range(n)]
    perm = list(range(n))
    i, j = swap
    perm[i], perm[j] = perm[j], perm[i]
    for col, row in enumerate(perm):
        matrix[row][col] = poly_h((col + 1) % D)
    return matrix


def shear_w(n):
    matrix = identity_w(n)
    if n > 2:
        matrix[0][2] = poly_h(3)
    return matrix


def random_w(n, rng):
    matrix = []
    for _ in range(n):
        row = []
        for _ in range(n):
            support = rng.randrange(1, 3)
            row.append(tuple((rng.randrange(1, P), rng.randrange(D))
                             for _ in range(support)))
        matrix.append(row)
    return matrix


def w_is_invertible(matrix):
    n = len(matrix)
    columns = []
    for col in range(n * D):
        owner, index = divmod(col, D)
        vec = [zero() for _ in range(n)]
        vec[owner] = basis(index)
        columns.append(pack(apply_w(matrix, vec), 0))
    return rank_mutable(columns) == n * D


def subspace_images(n, first, second, matrix, central_rank, cutoff,
                    kill_clean=False):
    read = 0 if first == "lower" else 1
    free = 1 - read
    central = (1, central_rank)
    factors = [unit(2, T), unit(4, T)] + [unit(0, 0)] * (n - 2)
    columns = []
    owners = [free] + list(range(2, n))
    clean = 0 if second == "lower" else 1
    for owner in owners:
        for index in range(D):
            vec = [zero() for _ in range(n)]
            vec[owner] = basis(index)
            if owner == read:
                fail("subspace contains the read owner")
            image = full(vec, factors, first, central)
            image = apply_w(matrix, image)
            if second == "upper":
                image = shear(image, 0, 1, central)
            else:
                image = shear(image, 1, 0, central)
            for owner_index, factor in enumerate(factors):
                if kill_clean and owner_index == clean:
                    image[owner_index] = zero()
                else:
                    image[owner_index] = apply_unit(factor, image[owner_index])
            columns.append(pack(image, cutoff))
    return columns


def scratch_only_images(n, first, second, matrix, central_rank, cutoff):
    central = (1, central_rank)
    factors = [unit(2, T), unit(4, T)] + [unit(0, 0)] * (n - 2)
    columns = []
    for owner in range(2, n):
        for index in range(D):
            vec = [zero() for _ in range(n)]
            vec[owner] = basis(index)
            image = full(vec, factors, first, central)
            image = apply_w(matrix, image)
            image = full(image, factors, second, central)
            columns.append(pack(image, cutoff))
    return columns


def target_rank(n):
    columns = []
    for owner in range(2, n):
        for index in range(D):
            vec = [zero() for _ in range(n)]
            vec[owner] = basis(index)
            columns.append(pack(vec, CUTOFF))
    if not columns:
        return 0
    return rank_mutable(columns)


def rank_mutable(columns):
    if not columns:
        return 0
    matrix = [list(column) for column in zip(*columns)]
    width = len(columns)
    pivot = 0
    for row_index, row in enumerate(matrix):
        if pivot >= width:
            break
        source = None
        for col in range(pivot, width):
            if row[col] % P:
                source = col
                break
        if source is None:
            continue
        if source != pivot:
            for values in matrix:
                values[pivot], values[source] = values[source], values[pivot]
            row = matrix[row_index]
        inv = pow(row[pivot] % P, P - 2, P)
        for values in matrix:
            values[pivot] = mod(values[pivot] * inv)
        for other_index, other in enumerate(matrix):
            if other_index == row_index or not other[pivot] % P:
                continue
            factor = other[pivot] % P
            for col in range(pivot, width):
                other[col] = mod(other[col] - factor * row[col])
        pivot += 1
    return pivot


def check_sources():
    for path, digest in EXPECTED.items():
        data = (ROOT / path).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            fail("sha256 " + path)
        text = data.decode("utf-8")
        if MARKERS[path] not in text:
            fail("marker " + path)


def check_dimensions():
    if not (T <= CUTOFF and 8 + 8 <= CUTOFF):
        fail("cutoff does not keep two transverse factors")
    if target_rank(2) != 0 or target_rank(3) != D or target_rank(4) != 2 * D:
        fail("target rank")
    if (3 - 1) * D <= (3 - 2) * D:
        fail("gap arithmetic")


def witness_family(n, rng):
    family = [identity_w(n), shear_w(n), permutation_w(n, (0, 1))]
    if n > 2:
        family.append(permutation_w(n, (1, 2)))
    produced = 0
    while produced < 4:
        candidate = random_w(n, rng)
        if w_is_invertible(candidate):
            family.append(candidate)
            produced += 1
    for matrix in family:
        if not w_is_invertible(matrix):
            fail("structured witness is singular")
    return family


def run():
    check_sources()
    check_dimensions()
    rng = random.Random(5491)
    orientations = ("lower", "upper")
    gaps = []
    witnesses = 0
    for n in (3, 4):
        for matrix in witness_family(n, rng):
            for first in orientations:
                for second in orientations:
                    for central_rank in (0, 1, 30):
                        columns = subspace_images(
                            n, first, second, matrix, central_rank, CUTOFF)
                        got = rank_mutable(columns)
                        expect = (n - 1) * D
                        if got != expect:
                            fail(f"subspace rank {got} != {expect} n={n}")
                        gap = got - (n - 2) * D
                        if gap != D:
                            fail("gap")
                        gaps.append(gap)
                        witnesses += 1
            scratch = scratch_only_images(
                n, "lower", "upper", identity_w(n), 30, CUTOFF)
            if rank_mutable(scratch) != (n - 2) * D:
                fail("scratch-only sharpness")
            killed = subspace_images(
                n, "lower", "upper", identity_w(n), 30, CUTOFF,
                kill_clean=True)
            if rank_mutable(killed) >= (n - 1) * D:
                fail("zero clean transverse factor still looked injective")
    low_cut = subspace_images(3, "lower", "upper", identity_w(3), 1, T - 1)
    if rank_mutable(low_cut) == 2 * D:
        fail("cutoff below 2t unexpectedly preserved the rank")
    print(
        "PASS_TWO_FULL_SCRATCH_MONOMIAL_OBSTRUCTION "
        f"witnesses={witnesses} gap={D} group=S3 "
        f"transverse_rank={T} cutoff={CUTOFF}"
    )


if __name__ == "__main__":
    run()
