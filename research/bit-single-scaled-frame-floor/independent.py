"""Independent exact certificate for one extra symmetric rank-one address.

No predecessor executable is imported. Rational matrix entries determine the
finite determinant candidates before any alignment assumption. Group-algebra
coefficients are binary matrices; literal paid-factor multiplication checks the
attaining word at selected dirty-role widths and with free basis changes.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product

A = (Q(1), Q(0), Q(0))
B = (Q(0), Q(1), Q(0))
P = (Q(1, 2), Q(1, 2), Q(1, 2))
QFRAME = (Q(1, 2), Q(1, 2), Q(-1, 2))
OLD = (A, B, P, QFRAME)
ZERO = (Q(0),) * 3
TOTAL = (Q(4), Q(4), Q(0))


def need(value, message):
    if not value:
        raise ValueError(message)


def add(*frames):
    return tuple(sum(frame[j] for frame in frames) for j in range(3))


def scale(c, frame):
    return tuple(c * x for x in frame)


TARGETS = (add(A, P), add(A, QFRAME), add(B, P), add(B, QFRAME))


def det(frame):
    x, y, z = frame
    return x * y - z * z


def enumerate_candidates():
    """All nonnegative five-label counts <=7 with the new label used.

    Derive the putative new address directly from the determinant identity.
    Symmetric 2x2 rank-one is exactly nonzero matrix and determinant zero;
    signs, slopes and scaling are not restricted in this candidate filter.
    """
    candidates, visited = [], 0
    for old_counts in product(range(8), repeat=4):
        for r in range(1, 8 - sum(old_counts)):
            visited += 1
            remaining = add(TOTAL, *(scale(-n, frame) for n, frame in zip(old_counts, OLD)))
            frame = scale(Q(1, r), remaining)
            if frame != ZERO and det(frame) == 0:
                candidates.append((old_counts + (r,), frame))
    need(visited == 462, 'count-domain coverage')
    need(len(candidates) == 40, 'forty determinant-compatible count profiles')
    need(len({frame for _, frame in candidates}) == 20, 'twenty derived frames')
    expected_frames = {scale(c, f) for f in OLD for c in (Q(4), Q(3), Q(2), Q(3, 2), Q(4, 3))}
    need({frame for _, frame in candidates} == expected_frames, 'derived frame set')
    for counts, frame in candidates:
        need(add(*(scale(n, f) for n, f in zip(counts, OLD + (frame,)))) == TOTAL,
             'literal determinant equation')
    return candidates, visited


def representations(target, frames, bounds):
    return [powers for powers in product(*(range(n + 1) for n in bounds))
            if add(*(scale(n, f) for n, f in zip(powers, frames))) == target]


def old_coordinates(frame):
    x, y, z = frame
    return x - z, y - z, 2 * z


def parity(value):
    need(value.denominator == 1, 'integral old-lattice coordinate required')
    return int(value) % 2


def support_and_rank(candidates):
    survivors, decisions = [], 0
    representations_with_extra = 0
    for counts, frame in candidates:
        supports = [representations(t, OLD + (frame,), counts) for t in TARGETS]
        decisions += len(supports)
        representations_with_extra += sum(n[-1] > 0 for rows in supports for n in rows)
        if all(supports):
            survivors.append((counts, frame))
    need(representations_with_extra == 0, 'no target representation may use extra frame')
    need(len(survivors) == 4, 'four support-compatible profiles')
    expected = {((1, 3, 1, 1, 1), scale(2, A)),
                ((3, 1, 1, 1, 1), scale(2, B)),
                ((1, 1, 1, 3, 1), scale(2, P)),
                ((1, 1, 3, 1, 1), scale(2, QFRAME))}
    need(set(survivors) == expected, 'residual count identities')
    witnesses = []
    for counts, frame in survivors:
        label_parities = [tuple(map(parity, old_coordinates(f))) for f in OLD + (frame,)]
        target_parities = [tuple(map(parity, old_coordinates(t))) for t in TARGETS]
        need(label_parities[-1] == (0, 0, 0), 'doubled frame vanishes to first order')
        found = []
        for functional in product(range(2), repeat=3):
            label_bits = [sum(a*b for a,b in zip(functional, f)) % 2 for f in label_parities]
            target_bits = [sum(a*b for a,b in zip(functional, t)) % 2 for t in target_parities]
            available_rank = sum(n*b for n,b in zip(counts, label_bits))
            needed_rank = sum(target_bits)
            if needed_rank > available_rank:
                found.append((functional, available_rank, needed_rank))
        need(any(cap == 2 and rank == 4 for _, cap, rank in found), 'rank-two versus rank-four certificate')
        witnesses.append((counts, found))
    return survivors, decisions, witnesses


# Binary matrices are tuples of row bit masks, with bit j indicating column j.
def eye(n):
    return tuple(1 << j for j in range(n))


def bxor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def bmul(a, b):
    out = []
    for row in a:
        result = 0
        for j in range(len(b)):
            if row >> j & 1:
                result ^= b[j]
        out.append(result)
    return tuple(out)


def brank(matrix):
    pivots = {}
    for original in matrix:
        row = original
        while row:
            j = row.bit_length() - 1
            if j in pivots:
                row ^= pivots[j]
            else:
                pivots[j] = row
                break
    return len(pivots)


def clean(poly):
    return {f: matrix for f, matrix in poly.items() if any(matrix)}


def algebra_product(left, right):
    """Full coefficientwise matrix product in F2[Sym_2(Q)]."""
    out = {}
    for f, a in left.items():
        for g, b in right.items():
            address = add(f, g)
            value = bmul(a, b)
            out[address] = bxor(out.get(address, (0,) * len(a)), value)
    return clean(out)


def paid(frame, projector):
    n = len(projector)
    need(frame != ZERO, 'nonzero paid address')
    need(brank(projector) == 1, 'paid projector rank one')
    need(bmul(projector, projector) == projector, 'paid projector idempotent')
    return clean({ZERO: bxor(eye(n), projector), frame: projector})


def coordinate(n, j):
    return tuple((1 << j) if i == j else 0 for i in range(n))


def endpoint(n):
    out = {}
    for j in range(n):
        address = TARGETS[j] if j < 4 else ZERO
        out[address] = bxor(out.get(address, (0,) * n), coordinate(n, j))
    return clean(out)


def scalar(matrix):
    return {ZERO: matrix}


def shear(n, dst, src):
    need(dst != src, 'distinct shear indices')
    matrix = list(eye(n)); matrix[dst] ^= 1 << src
    return tuple(matrix)


def replay(word, n):
    result = scalar(eye(n))
    for frame, projector in word:
        result = algebra_product(result, paid(frame, projector))
    return result


def formal_controls():
    constructions = mutations = noncoordinate = 0
    pairs = ((A, P), (A, QFRAME), (B, P), (B, QFRAME))
    for n in (4, 5, 7):
        word = [(frame, coordinate(n, j)) for j, pair in enumerate(pairs) for frame in pair]
        need(replay(word, n) == endpoint(n), 'direct eight-call endpoint')
        constructions += 1
        # Each transvection is its own inverse. Conjugate all projectors by H,
        # then undo that free role basis at the two ends of the word.
        mixers = [shear(n, 0, 1), shear(n, 2, n-1)]
        if n > 4:
            mixers.append(shear(n, n-1, 1))
        H, Hinv = eye(n), eye(n)
        for M in mixers:
            H = bmul(M, H)
            Hinv = bmul(Hinv, M)
        need(bmul(H, Hinv) == eye(n) == bmul(Hinv, H), 'binary free-mixing inverse')
        transformed = [(f, bmul(H, bmul(N, Hinv))) for f,N in word]
        noncoordinate += sum(brank(N) == 1 and N not in [coordinate(n,j) for j in range(n)]
                             for _,N in transformed)
        prod = replay(transformed, n)
        if n > 4:
            need(any(matrix[-1] != ((1 << (n-1)) if address == ZERO else 0)
                     for address, matrix in prod.items()),
                 'paid segment must transiently modify a dirty role')
        restored = algebra_product(scalar(Hinv), algebra_product(prod, scalar(H)))
        need(restored == endpoint(n), 'free-conjugated word restores every dirty role')
        constructions += 1
        for index in range(8):
            need(replay(word[:index] + word[index+1:], n) != endpoint(n), 'dropped-call mutant survived')
            mutations += 1
        for index in range(8):
            changed = list(word)
            changed[index] = (scale(2, changed[index][0]), changed[index][1])
            need(replay(changed, n) != endpoint(n), 'scaled-label mutant survived')
            mutations += 1
    need(noncoordinate > 0, 'noncoordinate projectors exercised')
    # A rank-one nilpotent is not a paid idempotent.
    nilpotent = (2, 0, 0, 0)
    need(brank(nilpotent) == 1 and bmul(nilpotent,nilpotent) != nilpotent, 'nilpotent fixture')
    try:
        paid(A, nilpotent)
    except ValueError:
        mutations += 1
    else:
        raise ValueError('non-idempotent call accepted')
    return constructions, mutations, noncoordinate


def run():
    candidates, profiles = enumerate_candidates()
    survivors, support_checks, ranks = support_and_rank(candidates)
    constructions, mutations, noncoordinate = formal_controls()
    print('PASS_SCALED_FRAME_INDEPENDENT '
          f'count_profiles={profiles} determinant_candidates={len(candidates)} distinct_frames=20 '
          f'target_support_checks={support_checks} survivors={len(survivors)} '
          f'rank_obstructions={len(ranks)} formal_words={constructions} '
          f'noncoordinate_paid_factors={noncoordinate} mutations_rejected={mutations}')
    return {'count_profiles': profiles, 'candidates': len(candidates), 'frames': 20,
            'target_support_checks': support_checks, 'survivors': len(survivors),
            'rank_obstructions': len(ranks), 'formal_words': constructions,
            'noncoordinate_paid_factors': noncoordinate, 'mutations_rejected': mutations}


if __name__ == '__main__':
    run()
