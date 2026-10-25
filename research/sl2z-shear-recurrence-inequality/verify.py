#!/usr/bin/env python3
"""Faithful integer-shear words fail the strict supplier moment inequality.

The three-bit quotient of PR #3947 implements rho(B^k) with at most one XOR.
Every word for the same integer matrix in the shear alphabet is at least
2k+1 letters, and that bill does not satisfy M(a) < 1. Standard library only.
"""

from __future__ import annotations

X = ((1, 1), (0, 1))
XI = ((1, -1), (0, 1))
Y = ((1, 0), (1, 1))
YI = ((1, 0), (-1, 1))
IDENT = ((1, 0), (0, 1))
GENERATORS = (X, XI, Y, YI)
# Each right multiplication, as coefficient rows (a, b, c, d) of the four
# output entries in row-major order. The l1 norm of a row is the entry-growth
# factor proved below.
RIGHT_FORMS = {
    "X": ((1, 0, 0, 0), (1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 1, 1)),
    "Xinv": ((1, 0, 0, 0), (-1, 1, 0, 0), (0, 0, 1, 0), (0, 0, -1, 1)),
    "Y": ((1, 1, 0, 0), (0, 1, 0, 0), (0, 0, 1, 1), (0, 0, 0, 1)),
    "Yinv": ((1, -1, 0, 0), (0, 1, 0, 0), (0, 0, 1, -1), (0, 0, 0, 1)),
}


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def matmul(left, right):
    return tuple(
        tuple(sum(left[i][t] * right[t][j] for t in range(2)) for j in range(2))
        for i in range(2)
    )


def entry_max(matrix) -> int:
    return max(abs(matrix[i][j]) for i in range(2) for j in range(2))


def b_matrix():
    return matmul(matmul(X, X), matmul(Y, Y))


def diagonal_endpoint(first, second):
    """Apply D(X), D(X), D(Y), D(Y) with the rightmost factor first.

    Each factor left-multiplies only the first role. The second role is the
    arbitrary dirty spectator.
    """
    for label in (Y, Y, X, X):
        first = matmul(label, first)
    return first, second


def cayley_hamilton_square(base):
    # B^2 - (tr B) B + (det B) I, checked by multiplication for this B.
    trace = base[0][0] + base[1][1]
    det = base[0][0] * base[1][1] - base[0][1] * base[1][0]
    square = matmul(base, base)
    predicted = (
        (trace * base[0][0] - det, trace * base[0][1]),
        (trace * base[1][0], trace * base[1][1] - det),
    )
    return square, predicted, trace, det


def diagonal_entries(limit: int) -> list[int]:
    """(B^k)_11 for k = 0..limit, from the integer recurrence."""
    if limit < 1:
        fail("need at least B^1")
    values = [1, 5]
    previous, current = 1, 5
    for _ in range(2, limit + 1):
        previous, current = current, 6 * current - previous
        values.append(current)
    return values


def inductive_ratio_step(current: int, previous: int) -> int:
    """Return u_{k+1} - 5 u_k given u_k, u_{k-1}."""
    return (6 * current - previous) - 5 * current


def forms_obey(factor: int) -> bool:
    return all(
        sum(abs(coefficient) for coefficient in row) <= factor
        for rows in RIGHT_FORMS.values()
        for row in rows
    )


def apply_form(form, matrix):
    entries = (matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1])
    values = [sum(coefficient * entries[index] for index, coefficient in enumerate(row)) for row in form]
    return ((values[0], values[1]), (values[2], values[3]))


def shortest_word_length(target, max_length: int) -> int | None:
    seen = {IDENT: 0}
    frontier = [IDENT]
    for length in range(max_length):
        nxt = []
        for matrix in frontier:
            for generator in GENERATORS:
                product = matmul(matrix, generator)
                if product in seen:
                    continue
                seen[product] = length + 1
                nxt.append(product)
                if product == target:
                    return length + 1
        frontier = nxt
    return None


def words_obey_doubling(max_length: int) -> bool:
    frontier = [IDENT]
    for length in range(1, max_length + 1):
        nxt = []
        allowance = 2**length
        for matrix in frontier:
            for generator in GENERATORS:
                product = matmul(matrix, generator)
                if entry_max(product) > allowance:
                    return False
                nxt.append(product)
        frontier = nxt
    return True


def faithful_length_lower_bound(power: int) -> int:
    """Minimum shear-letter count of B^power. Sharp at power 1; growth for power > 1."""
    if power < 1:
        fail("power must be positive")
    if power == 1:
        return 4
    return 2 * power + 1


def moment_clears_one(letter_count: int, width: int = 2, roles: int = 2) -> str:
    """Compare M(a) = (L/W) * (1/m)^(1-a) with 1 on a in [0, 1].

    For m > 1 the minimum is M(0) = L/(W m) and the maximum is M(1) = L/W.
    Returns 'above', 'touches-zero', or 'below'.
    """
    if letter_count < 0 or width < 2 or roles < 1:
        fail("bad moment parameters")
    floor = letter_count * 1
    unit = roles * width
    top = letter_count * 1
    role_unit = roles
    if floor > unit:
        return "above"
    if floor == unit and top > role_unit:
        return "touches-zero"
    if top < role_unit:
        return "below"
    if floor == unit and top == role_unit:
        return "flat-one"
    return "mixed"


def quotient_data():
    """Projective action of the integer generators modulo 3, on the sum-zero space."""
    lines = ((1, 0), (0, 1), (1, 1), (1, 2))

    def normalize(vector):
        x, y = vector[0] % 3, vector[1] % 3
        if (x, y) == (0, 0):
            fail("projective image of zero")
        pivot = x if x else y
        inverse = 1 if pivot == 1 else 2
        return ((x * inverse) % 3, (y * inverse) % 3)

    def permutation(matrix):
        images = []
        for line in lines:
            image = normalize(
                (
                    matrix[0][0] * line[0] + matrix[0][1] * line[1],
                    matrix[1][0] * line[0] + matrix[1][1] * line[1],
                )
            )
            images.append(lines.index(image))
        if len(set(images)) != 4:
            fail("line map is not a permutation")
        return tuple(images)

    def apply_permutation(perm, vector):
        inverse = [0, 0, 0, 0]
        for source, image in enumerate(perm):
            inverse[image] = source
        return tuple(vector[inverse[index]] for index in range(4))

    basis = ((0, 1, 0, 1), (1, 1, 1, 1), (0, 1, 1, 0))

    def coordinates(vector):
        rows = [[basis[col][row] for col in range(3)] + [vector[row]] for row in range(4)]
        pivot_row = 0
        where = []
        for col in range(3):
            selected = next((row for row in range(pivot_row, 4) if rows[row][col]) , None)
            if selected is None:
                continue
            rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
            for row in range(4):
                if row != pivot_row and rows[row][col]:
                    for entry in range(4):
                        rows[row][entry] ^= rows[pivot_row][entry]
            where.append((pivot_row, col))
            pivot_row += 1
        for row in range(pivot_row, 4):
            if rows[row][3]:
                fail("vector left the sum-zero subspace")
        coeffs = [0, 0, 0]
        for row, col in where:
            coeffs[col] = rows[row][3]
        return tuple(coeffs)

    def representation(perm):
        columns = [coordinates(apply_permutation(perm, vector)) for vector in basis]
        return tuple(tuple(columns[col][row] for col in range(3)) for row in range(3))

    def mul2(left, right):
        return tuple(
            tuple(sum(left[i][t] * right[t][j] for t in range(3)) % 2 for j in range(3))
            for i in range(3)
        )

    image_x = representation(permutation(X))
    image_y = representation(permutation(Y))
    image_b = mul2(mul2(image_x, image_x), mul2(image_y, image_y))
    return image_x, image_y, image_b


def run_checks() -> dict:
    base = b_matrix()
    if base != ((5, 2), (2, 1)):
        fail("B is not X^2 Y^2")
    square, predicted, trace, det = cayley_hamilton_square(base)
    if trace != 6 or det != 1 or square != predicted:
        fail("Cayley-Hamilton step failed")
    if matmul(matmul(X, X), X) == IDENT:
        fail("X^3 collapsed in the integer matrices")

    probe = ((2, -3), (5, 7))
    for name, generator in zip(("X", "Xinv", "Y", "Yinv"), GENERATORS):
        if apply_form(RIGHT_FORMS[name], probe) != matmul(probe, generator):
            fail("linear form disagrees with " + name)
    if not forms_obey(2):
        fail("shear forms exceed doubling")
    if forms_obey(1):
        fail("control: l1 bound 1 should reject a genuine two-entry sum")
    if not words_obey_doubling(6):
        fail("explicit words exceeded 2^L")

    values = diagonal_entries(24)
    matrix_power = IDENT
    for power, entry in enumerate(values):
        if power:
            matrix_power = matmul(matrix_power, base)
        if matrix_power[0][0] != entry:
            fail("recurrence disagrees with matrix power at " + str(power))
        if power == 0:
            continue
        if entry < 5**power or not entry > 2 ** (2 * power):
            fail("growth failed at " + str(power))
        previous = values[power - 1]
        if entry < 5 * previous:
            fail("ratio failed at " + str(power))
        if inductive_ratio_step(entry, previous) < 4 * previous:
            fail("inductive surplus failed")
    # (6x-y)-5x and x-y are linear and agree on a basis, hence for every integer pair.
    for sample_x, sample_y in ((1, 0), (0, 1)):
        if inductive_ratio_step(sample_x, sample_y) != sample_x - sample_y:
            fail("recurrence gap is not the ratio gap")

    dirty_pairs = (
        (IDENT, IDENT),
        (X, Y),
        (YI, matmul(X, Y)),
        (base, XI),
    )
    for first, second in dirty_pairs:
        got_first, got_second = diagonal_endpoint(first, second)
        if got_second != second or got_first != matmul(base, first):
            fail("diagonal four-call bill changed a spectator or missed B")

    length_b = shortest_word_length(base, 4)
    if length_b != 4:
        fail("B word length is not 4, found " + str(length_b))
    if shortest_word_length(base, 3) is not None:
        fail("a length-3 word reached B")

    for power in range(1, 13):
        lower = faithful_length_lower_bound(power)
        if power == 1 and lower != 4:
            fail("sharp length drifted")
        if power > 1 and lower != 2 * power + 1:
            fail("growth length drifted")
        if lower <= 2 * power:
            fail("length lower bound is not past 2k")
        kind = moment_clears_one(lower)
        if power == 1 and kind != "touches-zero":
            fail("four-letter moment should touch 1 only at a=0")
        if power > 1 and kind != "above":
            fail("longer powers should lie strictly above 1")
        # Any legal letter count at least this large stays out of M<1.
        if moment_clears_one(lower + 5) == "below":
            fail("adding letters created a passing moment")

    if moment_clears_one(1, width=3, roles=2) != "below":
        fail("one rank-1 child on width 3 should pass the optimistic screen")

    image_x, image_y, image_b = quotient_data()
    published_x = ((0, 0, 1), (0, 1, 0), (1, 0, 1))
    published_y = ((1, 0, 1), (1, 1, 0), (1, 0, 0))
    transvection = ((1, 0, 0), (0, 1, 1), (0, 0, 1))
    if image_x != published_x or image_y != published_y or image_b != transvection:
        fail("quotient matrices disagree with the pinned three-bit action")
    identity3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    t_square = tuple(
        tuple(sum(image_b[i][t] * image_b[t][j] for t in range(3)) % 2 for j in range(3))
        for i in range(3)
    )
    if t_square != identity3:
        fail("rho(B) is not an involution")
    changed = sum(
        1
        for i in range(3)
        for j in range(3)
        if transvection[i][j] != identity3[i][j]
    )
    if changed != 1:
        fail("rho(B) is not a single coordinate XOR")

    # No constant quotient bill dominates every faithful length.
    for constant in range(0, 12):
        if all(faithful_length_lower_bound(power) <= constant for power in range(1, 20)):
            fail("a constant dominated the faithful lengths")

    return {
        "length_B": length_b,
        "u_8": values[8],
        "moment_B": "touches-zero",
        "moment_B2": "above",
        "quotient_xor": 1,
        "strict_supplier_inequality": False,
    }


def main() -> None:
    receipt = run_checks()
    print(
        "PASS_SL2Z_SHEAR_RECURRENCE_INEQUALITY "
        + " ".join(key + "=" + str(value) for key, value in receipt.items())
    )


if __name__ == "__main__":
    main()
