"""Independent finite corroboration of positive rank-one address usability.

Exact rational determinant families and literal subset support are checked here;
finite parameter and workspace grids are not a universal proof. The written
proof supplies the reduction for arbitrary positive rational R and all finite
restored dirty workspaces. No predecessor executable is imported.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from itertools import product

F = Fraction
ZERO = (F(0), F(0), F(0))
A = (F(1), F(0), F(0))
B = (F(0), F(1), F(0))
P = (F(1, 2), F(1, 2), F(1, 2))
Q = (F(1, 2), F(1, 2), F(-1, 2))
LABELS = (A, B, P, Q)
TOTAL = (F(4), F(4), F(0))


def require(test, message):
    if not test:
        raise ValueError(message)


def plus(left, right):
    return tuple(a + b for a, b in zip(left, right))


def times(coefficient, address):
    return tuple(coefficient * entry for entry in address)


def difference(left, right):
    return plus(left, times(-1, right))


def total_address(counts, labels):
    result = ZERO
    for count, label in zip(counts, labels):
        result = plus(result, times(count, label))
    return result


TARGETS = (plus(A, P), plus(A, Q), plus(B, P), plus(B, Q))


def determinant(address):
    x, y, z = address
    return x*y - z*z


def multiple_of(address, base):
    """Exact rational ratio, or None if the full matrices are not parallel."""
    for entry, denominator in zip(address, base):
        if denominator:
            ratio = entry / denominator
            return ratio if times(ratio, base) == address else None
    raise ValueError('zero base in ratio computation')


def old_count_domain():
    """Every old multiplicity quadruple of total strictly less than eight."""
    for a in range(8):
        for b in range(8 - a):
            for p in range(8 - a - b):
                for q in range(8 - a - b - p):
                    yield a, b, p, q


def derive_families():
    families = []
    visited = 0
    for counts in old_count_domain():
        visited += 1
        residual = difference(TOTAL, total_address(counts, LABELS))
        if determinant(residual) != 0 or residual[0] + residual[1] <= 0:
            continue
        n = sum(counts)
        d = counts[0] - counts[1]
        e = counts[2] - counts[3]
        require(d*d + e*e == (8 - n)**2, 'determinant circle identity')
        require(abs(d) + abs(e) <= n, 'count difference constraint')
        require(4 <= n <= 7 and d*e == 0, 'axial integral circles')
        matched = [(j, multiple_of(residual, label)) for j, label in enumerate(LABELS)]
        matched = [(j, ratio) for j, ratio in matched if ratio is not None and ratio > 0]
        require(len(matched) == 1, 'unique old direction derived from raw entries')
        direction, scale = matched[0]
        require(scale == 8 - n and scale.denominator == 1, 'positive integer residual scale')
        families.append((counts, residual, direction, int(scale)))
    require(visited == 330, 'complete old-count domain')
    require(len(families) == 40, 'forty all-length determinant families')
    require({residual for _, residual, _, _ in families} ==
            {times(d, label) for d in range(1, 5) for label in LABELS},
            'sixteen residual matrices')
    require([sum(direction == j for _, _, direction, _ in families) for j in range(4)]
            == [10, 10, 10, 10], 'ten families per direction')
    return families, visited


def perpendicular_character(direction, address):
    """Integer-valued on each relevant lattice, even with fractional R.

    For A/B, twice the off-diagonal entry annihilates the added line.
    For P/Q, the diagonal difference annihilates that line. Each functional
    is integral on the old labels, hence on their lattice plus any R there.
    """
    x, y, z = address
    value = 2*z if direction < 2 else x-y
    require(value.denominator == 1, 'character integrality')
    return int(value) % 2


def rank_capacity(counts, direction):
    demand = sum(perpendicular_character(direction, target) for target in TARGETS)
    capacity = sum(n * perpendicular_character(direction, label)
                   for n, label in zip(counts, LABELS))
    require(demand == 4, 'all four targets detected')
    return capacity, demand


def subset_representations(target, counts, extra, extra_count):
    """Enumerate old subset multiplicities; solve extra multiplicity exactly.

    This compares rational matrix entries directly. It assumes neither a
    distinguished coordinate system nor the claimed reciprocal classification.
    """
    witnesses = []
    for old in product(*(range(bound + 1) for bound in counts)):
        remainder = difference(target, total_address(old, LABELS))
        multiplicity = multiple_of(remainder, extra)
        if multiplicity is not None and multiplicity.denominator == 1:
            integer = int(multiplicity)
            if 0 <= integer <= extra_count:
                witnesses.append(old + (integer,))
    return witnesses


def parameter_grid(families):
    rank_survivors = [(counts, residual, direction, d)
                      for counts, residual, direction, d in families
                      if rank_capacity(counts, direction)[0] >= 4]
    require(len(rank_survivors) == 12, 'three rank-compatible families per direction')
    a_families = {counts: d for counts, _, direction, d in rank_survivors if direction == 0}
    require(a_families == {(1, 2, 2, 2): 1, (0, 2, 2, 2): 2, (0, 1, 3, 3): 1},
            'three canonical residual profiles')
    checked = supported = 0
    for counts, residual, direction, d in families:
        for r in range(1, 25):
            extra = times(F(1, r), residual)
            require(perpendicular_character(direction, extra) == 0,
                    'rational added frame killed by character')
            capacity, demand = rank_capacity(counts, direction)
            supports = [subset_representations(target, counts, extra, r) for target in TARGETS]
            checked += 4
            accepted = capacity >= demand and all(supports)
            expected = capacity >= demand and r % d == 0
            require(accepted == expected, 'support forces a reciprocal old frame')
            if accepted:
                supported += 1
                m = r // d
                require(extra == times(F(1, m), LABELS[direction]), 'reciprocal parameter')
                require(sum(counts) + r >= m + 7, 'required-use tariff lower bound')
    require(checked == 3840 and supported == 240, 'finite parameter grid coverage')
    return rank_survivors, checked, supported


def symbolic_support(rank_survivors):
    """Finite rational weights certify the unbounded integer parameter step.

    Write rR=dF. A target subset has remainder alpha*F after its old calls;
    its extra-call multiplicity is alpha*r/d. Enumerating alpha, rather than
    r, is finite because all old count profiles have already been derived.
    """
    target_checks = 0
    for counts, _, direction, d in rank_survivors:
        weights_by_target = []
        for target in TARGETS:
            weights = set()
            for old in product(*(range(bound + 1) for bound in counts)):
                remainder = difference(target, total_address(old, LABELS))
                alpha = multiple_of(remainder, LABELS[direction])
                if alpha is not None and 0 <= alpha <= d:
                    weights.add(alpha)
            require(weights and weights <= {F(0), F(1)}, 'exact remaining-weight alphabet')
            weights_by_target.append(weights)
            target_checks += 1
        require(d in (1, 2), 'rank-compatible residual coefficients')
        if d == 2:
            require({F(1)} in weights_by_target, 'some target forces r/2 integer')
        # For d=1 every nonempty subset above gives integral multiplicity.
        # For d=2 integrality of r/2 is necessary by the singleton witness,
        # and sufficient for every weight set above. This is an exact finite
        # certificate of the support reduction, not a bounded r search.
    require(target_checks == 48, 'unbounded parameter support certificates')
    return target_checks


def necessary_profiles(extra, families):
    """No bound on r: determinant residual divided by the given R determines it."""
    require(determinant(extra) == 0 and extra[0] + extra[1] > 0,
            'positive nonzero rank-one input')
    accepted = []
    for counts, residual, direction, _ in families:
        r = multiple_of(residual, extra)
        if r is None or r <= 0 or r.denominator != 1:
            continue
        r = int(r)
        require(perpendicular_character(direction, extra) == 0, 'added-line character')
        if rank_capacity(counts, direction)[0] < 4:
            continue
        if all(subset_representations(target, counts, extra, r) for target in TARGETS):
            accepted.append(counts + (r,))
    return accepted


def rational_fixtures(families):
    scales = {F(n, d) for n in range(1, 11) for d in range(1, 11)}
    reciprocal = rejected = 0
    for label in LABELS:
        for scale in sorted(scales):
            profiles = necessary_profiles(times(scale, label), families)
            require(bool(profiles) == (scale.numerator == 1), 'rational scale classification')
            if scale.numerator == 1:
                m = scale.denominator
                require(len(profiles) == 3, 'exactly three necessary global profiles')
                require(min(map(sum, profiles)) == m + 7, 'finite minimum tariff')
                require(set(map(sum, profiles)) == {m + 7, 2*m + 6},
                        'necessary total-length spectrum')
                reciprocal += 1
            else:
                rejected += 1
    rotated = 0
    for u, v in ((1, 2), (2, 1), (1, -2), (2, -3), (1, 3)):
        for scale in (F(1, 7), F(2, 3), F(1), F(5, 2)):
            frame = times(scale, (F(u*u), F(v*v), F(u*v)))
            require(not necessary_profiles(frame, families), 'rotated frame passed determinant obstruction')
            rotated += 1
    return reciprocal, rejected, rotated


# Dense matrices over F2 are independent of the address-count computations.
def identity(width):
    return tuple(tuple(int(i == j) for j in range(width)) for i in range(width))


def zero_matrix(width):
    return tuple((0,) * width for _ in range(width))


def matrix_add(left, right):
    return tuple(tuple(a ^ b for a, b in zip(lrow, rrow))
                 for lrow, rrow in zip(left, right))


def matrix_multiply(left, right):
    width = len(left)
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(width)) % 2
                       for j in range(width)) for i in range(width))


def matrix_rank(matrix):
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(len(rows)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i][column]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def polynomial_product(left, right):
    coefficients = {}
    for exponent_left, matrix_left in left.items():
        for exponent_right, matrix_right in right.items():
            exponent = plus(exponent_left, exponent_right)
            coefficient = matrix_multiply(matrix_left, matrix_right)
            coefficients[exponent] = matrix_add(
                coefficients.get(exponent, zero_matrix(len(matrix_left))), coefficient)
    return {exponent: coefficient for exponent, coefficient in coefficients.items()
            if any(any(row) for row in coefficient)}


def projector(width, role):
    return tuple(tuple(int(i == j == role) for j in range(width)) for i in range(width))


def paid_factor(address, projection):
    require(address != ZERO, 'nonzero paid address')
    require(matrix_rank(projection) == 1, 'rank-one paid projector')
    require(matrix_multiply(projection, projection) == projection, 'idempotent paid projector')
    return {ZERO: matrix_add(identity(len(projection)), projection), address: projection}


def replay(word, width):
    result = {ZERO: identity(width)}
    for address, projection in word:
        result = polynomial_product(result, paid_factor(address, projection))
    return result


def endpoint(width):
    result = {}
    for role in range(width):
        address = TARGETS[role] if role < 4 else ZERO
        result[address] = matrix_add(result.get(address, zero_matrix(width)), projector(width, role))
    return result


def transvection(width, destination, source):
    matrix = [list(row) for row in identity(width)]
    matrix[destination][source] ^= 1
    return tuple(map(tuple, matrix))


def replace_word(direction, m, width, replacements):
    pairs = ((A, P), (A, Q), (B, P), (B, Q))
    word = []
    replaced = 0
    named_counts = [0] * 5
    extra_indices = []
    for role, pair in enumerate(pairs):
        for label in pair:
            projection = projector(width, role)
            if label == LABELS[direction] and replaced < replacements:
                extra_indices.extend(range(len(word), len(word) + m))
                word.extend([(times(F(1, m), label), projection)] * m)
                named_counts[4] += m
                replaced += 1
            else:
                word.append((label, projection))
                named_counts[LABELS.index(label)] += 1
    expected = [2] * 4 + [m * replacements]
    expected[direction] -= replacements
    require(replaced == replacements and named_counts == expected,
            'labelled counts, including the duplicate-frame case m=1')
    require(len(word) == 8 - replacements + m * replacements, 'replacement tariff')
    require(len(extra_indices) == m * replacements, 'explicit extra-label uses')
    return word, extra_indices


def word_fixtures():
    words = conjugated = mutants = 0
    m_grid = (1, 2, 3, 4, 5, 7, 8, 12)
    for width in (4, 6):
        first = transvection(width, 0, 1)
        second = transvection(width, 2, width - 1)
        third = transvection(width, width-1, 1) if width > 4 else identity(width)
        mixing = matrix_multiply(third, matrix_multiply(first, second))
        unmixing = matrix_multiply(second, matrix_multiply(first, third))
        require(matrix_multiply(mixing, unmixing) == identity(width), 'free inverse')
        for direction, m, replacements in product(range(4), m_grid, (1, 2)):
            word, extra_indices = replace_word(direction, m, width, replacements)
            result = replay(word, width)
            require(result == endpoint(width), 'exact attaining word')
            words += 1
            transformed = [(address, matrix_multiply(mixing, matrix_multiply(N, unmixing)))
                           for address, N in word]
            require(any(N not in [projector(width, j) for j in range(width)]
                        for _, N in transformed), 'non-coordinate projectors exercised')
            segment = replay(transformed, width)
            if width > 4:
                require(any(matrix[-1] != (identity(width)[-1] if address == ZERO else (0,)*width)
                            for address,matrix in segment.items()), 'temporary dirty-role write fixture')
            restored = polynomial_product({ZERO: unmixing},
                        polynomial_product(segment, {ZERO: mixing}))
            require(restored == endpoint(width), 'conjugated endpoint and dirty-role restoration')
            conjugated += 1
            index = extra_indices[0]
            require(replay(word[:index] + word[index + 1:], width) != endpoint(width),
                    'one fewer required call mutant survived')
            require(replay(word + [word[index]], width) != endpoint(width),
                    'one extra call mutant survived')
            wrong = list(word)
            wrong[index] = (times(F(1, m + 1), LABELS[direction]), wrong[index][1])
            require(replay(wrong, width) != endpoint(width), 'incorrect fraction mutant survived')
            wrong = list(word)
            wrong[index] = (times(F(1, m), LABELS[(direction + 1) % 4]), wrong[index][1])
            require(replay(wrong, width) != endpoint(width), 'wrong direction mutant survived')
            mutants += 4
            if width > 4:
                dirty_corruption = polynomial_product(result, {ZERO: transvection(width, 4, 0)})
                require(dirty_corruption != endpoint(width), 'unrestored dirty role mutant survived')
                mutants += 1
    nilpotent = ((0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    require(matrix_rank(nilpotent) == 1, 'nilpotent rank-one fixture')
    try:
        paid_factor(A, nilpotent)
    except ValueError:
        mutants += 1
    else:
        raise ValueError('rank-one non-idempotent mutant survived')
    return words, conjugated, mutants


def run():
    families, visited = derive_families()
    rank_survivors, support_checks, supported = parameter_grid(families)
    symbolic_checks = symbolic_support(rank_survivors)
    reciprocal, nonreciprocal, rotated = rational_fixtures(families)
    words, conjugated, mutants = word_fixtures()
    result = {'old_profiles': visited, 'determinant_families': len(families),
              'rank_survivors': len(rank_survivors), 'parameter_support_checks': support_checks,
              'symbolic_support_checks': symbolic_checks,
              'parameter_survivors': supported, 'reciprocal_fixtures': reciprocal,
              'nonreciprocal_rejections': nonreciprocal, 'rotated_rejections': rotated,
              'attaining_words': words, 'conjugated_words': conjugated,
              'mutants_rejected': mutants}
    print('PASS_POSITIVE_FRAME_INDEPENDENT ' + ' '.join(f'{key}={value}' for key, value in result.items()))
    return result


if __name__ == '__main__':
    run()
