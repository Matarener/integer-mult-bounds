"""Source-bound exact checks for the scoped proof in README.md.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def source_checks():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    manifest = json.loads((PACKAGE / 'VERIFY.json').read_text())
    count = 0
    for row in sources['files']:
        if row['usage'] == 'input':
            need(row['path'] in manifest['inputs'], 'undeclared live source')
            data = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'],
                 'predecessor source changed: ' + row['path'])
            count += 1
    need(count == 3, 'three predecessor inputs')
    return count


def main():
    sources = source_checks()
    # Compile the package-local source bytes rather than trusting cached pyc.
    namespace = {'__name__': 'independent_certificate'}
    path = PACKAGE / 'independent.py'
    exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
    independent = namespace['run']()
    # Independently check the integer-circle step in the written proof.
    circles = {}
    for n in range(7):
        radius = 8 - n
        points = {(d, e) for d in range(-n, n + 1) for e in range(-n, n + 1)
                  if abs(d) + abs(e) <= n and d*d + e*e == radius*radius}
        expected = set() if n < 4 else {(radius,0),(-radius,0),(0,radius),(0,-radius)}
        need(points == expected, 'integer-circle reduction')
        circles[n] = points
    old, targets = namespace['OLD'], namespace['TARGETS']
    add, scale = namespace['add'], namespace['scale']
    expected_pairs = ((0,2),(0,3),(1,2),(1,3))
    for target, expected in zip(targets, expected_pairs):
        pairs = {(i,j) for i in range(4) for j in range(i,4) if add(old[i],old[j]) == target}
        need(pairs == {expected}, 'unique old-pair support')
    replay, coordinate = namespace['replay'], namespace['coordinate']
    endpoint, A = namespace['endpoint'], old[0]
    word = [(old[i],coordinate(5,j)) for j,pair in enumerate(expected_pairs) for i in pair]
    # A negative frame may occur in longer words; do not certify a false ban.
    loop = [(A,coordinate(5,0)), (scale(-1,A),coordinate(5,0))]
    need(replay(word + loop,5) == endpoint(5), 'negative-frame identity padding')
    broken = word + [loop[0], (scale(-2,A),coordinate(5,0))]
    need(replay(broken,5) != endpoint(5), 'broken negative loop accepted')
    # Replacing one A call by two A/2 calls gives a legal nine-call word.
    half = (scale(Fraction(1,2), A),coordinate(5,0))
    need(replay([half,half] + word[1:],5) == endpoint(5), 'subdivided frame witness')
    leaked = word + [(A,coordinate(5,4))]
    need(replay(leaked,5) != endpoint(5), 'dirty auxiliary not restored')
    # A hand-computed noncommuting pair detects a reversed product engine.
    N, M = (1,0,0,0), (3,0,0,0)
    paid, multiply = namespace['paid'], namespace['algebra_product']
    zero, B = namespace['ZERO'], old[1]
    forward = multiply(paid(A,N), paid(B,M))
    backward = multiply(paid(B,M), paid(A,N))
    need(forward == {zero:(0,2,4,8), A:(2,0,0,0), add(A,B):(3,0,0,0)},
         'literal ordered noncommuting coefficients')
    need(backward == {zero:(2,2,4,8), B:(2,0,0,0), add(A,B):(1,0,0,0)},
         'literal reversed noncommuting coefficients')
    need(forward != backward, 'reversed product mutation accepted')
    need(independent['survivors'] == 4 and independent['mutations_rejected'] == 49,
         'independent certificate totals')
    print('PASS_SINGLE_SCALED_FRAME_MINIMUM_8 '
          f'live_sources={sources} circle_domains={len(circles)} unique_target_pairs=4 '
          'longer_words=2 extra_failure_controls=3 noncommuting_products=2 finite_widths=4,5,7')


if __name__ == '__main__':
    main()
