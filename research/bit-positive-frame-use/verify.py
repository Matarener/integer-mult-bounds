"""Source binding and algebraic checks for the all-length positive-frame proof.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    declared = json.loads((PACKAGE / 'VERIFY.json').read_text())['inputs']
    count = 0
    for row in manifest['files']:
        if row['usage'] == 'input':
            require(row['path'] in declared, 'undeclared source input')
            require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'source hash changed: ' + row['path'])
            count += 1
    require(count == 3, 'three canonical predecessor sources')
    return count


A = ((F(1), F(0)), (F(0), F(0)))
B = ((F(0), F(0)), (F(0), F(1)))
P = ((F(1,2), F(1,2)), (F(1,2), F(1,2)))
Q = ((F(1,2), F(-1,2)), (F(-1,2), F(1,2)))
OLD = (A, B, P, Q)


def add(left, right):
    return tuple(tuple(a + b for a,b in zip(lrow,rrow)) for lrow,rrow in zip(left,right))


def scale(value, matrix):
    return tuple(tuple(value*x for x in row) for row in matrix)


def multiply(left, right):
    return tuple(tuple(sum(left[i][k]*right[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def conjugate(matrix, basis, inverse):
    return multiply(basis, multiply(matrix,inverse))


TARGETS = tuple(add(OLD[i],OLD[j]) for i,j in ((0,2),(0,3),(1,2),(1,3)))


def algebra_checks():
    circles = 0
    for n in range(8):
        radius = 8-n
        points = {(d,e) for d in range(-n,n+1) for e in range(-n,n+1)
                  if abs(d)+abs(e)<=n and d*d+e*e==radius*radius}
        require(points == (set() if n<4 else {(radius,0),(-radius,0),(0,radius),(0,-radius)}),
                'all possible positive residual circles')
        circles += 1
    J = ((F(0),F(1)),(F(1),F(0)))
    H = ((F(1),F(1)),(F(1),F(-1)))
    identity = ((F(1),F(0)),(F(0),F(1)))
    for basis, inverse, frame_perm, target_perm in (
        (J,J,(1,0,2,3),(2,3,0,1)),
        (H,scale(F(1,2),H),(2,3,0,1),(0,2,1,3)),
    ):
        require(multiply(basis,inverse) == identity == multiply(inverse,basis), 'exact rational inverse')
        require(tuple(conjugate(x,basis,inverse) for x in OLD) == tuple(OLD[i] for i in frame_perm),
                'old alphabet symmetry')
        require(tuple(conjugate(x,basis,inverse) for x in TARGETS) == tuple(TARGETS[i] for i in target_perm),
                'endpoint symmetry with active-role permutation')
    # Verify characters on generators. They vanish on the whole rational
    # added line, not merely on the old frame modulo two.
    for direction, extra_line in enumerate(OLD):
        character = ((lambda x: 2*x[0][1]) if direction<2
                     else (lambda x: x[0][0]-x[1][1]))
        require(character(extra_line) == 0, 'annihilate rational line exactly')
        require(all(character(x).denominator == 1 for x in OLD), 'old-label integrality')
        require(all(int(character(x)) % 2 == 1 for x in TARGETS), 'rank-four demand')
        for c in (F(1,3),F(2,7),F(17,5)):
            require(character(scale(c,extra_line)) == 0, 'fractional added-line control')
    old_character = lambda x: x[0][0]+x[1][1]-2*x[0][1]
    require(tuple(int(old_character(x)) % 2 for x in OLD) == (1,1,0,0), 'old character')
    require(sum(int(old_character(x)) % 2 for x in TARGETS) == 4, 'm=1 rank-four demand')
    require(sum(n*b for n,b in zip((0,1,3,3,1),(1,1,0,0,1))) == 2, 'm=1 third-profile rank capacity')
    # The tempting old-lattice functional trace-2offdiag is NOT integral
    # on Q/3; reducing it mod2 would silently change the proof's lattice.
    bad = scale(F(1,3),Q)
    require((bad[0][0]+bad[1][1]-2*bad[0][1]) == F(2,3), 'nonintegral-character control')
    profiles = {(a,4-s,s,s,4-s-a) for s in range(4) for a in range(4-s) if 2*s>=4}
    require(profiles == {(1,2,2,2,1),(0,2,2,2,2),(0,1,3,3,1)}, 'symbolic residual patterns')
    # A positive old A count leaves only residual scale1; otherwise A+P
    # support forces an integral reciprocal directly, as proved in PROOF.md.
    require(all(a == 0 or (a,b,p,q,d)==(1,2,2,2,1) for a,b,p,q,d in profiles),
            'positive-A branch requires r*c=1')
    return circles


def main():
    source_count = sources()
    circles = algebra_checks()
    namespace = {'__name__':'independent_positive_frame_certificate'}
    path = PACKAGE / 'independent.py'
    exec(compile(path.read_bytes(),str(path),'exec'), namespace)
    result = namespace['run']()
    # A manual noncommuting product fixes matrix order independently of the
    # (commuting) subdivision constructions.
    N = ((1,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
    M = ((1,1,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
    paid, prod = namespace['paid_factor'], namespace['polynomial_product']
    zero, a, b = namespace['ZERO'], namespace['A'], namespace['B']
    ab = namespace['plus'](a,b)
    zero_forward = ((0,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))
    middle = ((0,1,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0))
    zero_backward = ((0,1,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))
    require(prod(paid(a,N),paid(b,M)) == {zero:zero_forward,a:middle,ab:M}, 'ordered product oracle')
    require(prod(paid(b,M),paid(a,N)) == {zero:zero_backward,b:middle,ab:N}, 'reverse product oracle')
    # Positivity is essential: append an A,-A cancellation pair to a valid word.
    word, _ = namespace['replace_word'](0,1,4,1)
    # The independent construction returns (address, projector) records.
    negative_loop = [(a,N),(namespace['times'](-1,a),N)]
    require(namespace['replay'](word+negative_loop,4) == namespace['endpoint'](4), 'negative boundary witness')
    require(result['rank_survivors'] == 12, 'independent family count')
    print('PASS_POSITIVE_FRAME_USE_CLASSIFICATION '
          f'live_sources={source_count} integer_circle_domains={circles} '
          'alphabet_symmetries=2 lattice_characters=4 noncommuting_oracles=2 negative_boundary=1 m1_third_profile_excluded=1')


if __name__ == '__main__':
    main()
