#!/usr/bin/env python3
"""Coverage, hypothesis and actual CLI controls on private copies. Apache-2.0."""

from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v  # noqa: E402

m = v.m


def rejects(function):
    try:
        function()
    except (ValueError, KeyError):
        return
    raise ValueError('losing control accepted')


def small_spaces():
    checked = 0
    for n in range(1, 6):
        labels = list(range(1 << n))
        ker = m.kernels(labels, [1 << j for j in range(n)])
        for d in range(n + 1):
            observed = list(m.masks(ker, m.annihilators(n, d)))
            # Exhaust all generating subsets; no echelon or annihilator oracle.
            expected = {sum(1 << x for x in m.span(rows))
                        for rows in combinations(range(1, 1 << n), d)
                        if len(set(m.span(rows))) == 1 << d}
            m.require(len(observed) == len(set(observed)) and set(observed) == expected,
                      'small complete primal-versus-dual space domain')
            checked += len(observed)
    return checked


def signed_hypotheses():
    def q8(x):
        return (sum((x >> j & 1) * (x >> (j + 1) & 1) for j in (0, 2, 4, 6))
                + (x >> 6 & 1) + (x >> 7 & 1)) % 2
    def q6(x):
        return (sum((x >> j & 1) * (x >> (j + 1) & 1) for j in (0, 2, 4))
                + (x >> 4 & 1) + (x >> 5 & 1)) % 2
    for q, n in [(q8, 8), (q6, 6)]:
        gram = [sum((q((1 << i) ^ (1 << j)) ^ q(1 << i) ^ q(1 << j)) << j
                    for j in range(n)) for i in range(n)]
        m.require(len(m.basis(gram, n)) == n, 'counterexample polar nondegeneracy')
    m.require(sum(1 - 2*q8(x) for x in range(256)) == -16, 'minus-eight Gauss sign')
    m.require(sum(q8(128 ^ x) for x in m.span([1, 4, 16, 64])) == 16,
              'rank-five minus-sign counterexample')
    m.require(sum(q8(128 ^ x) for x in m.span([1, 2, 4, 16, 64])) == 24,
              'rank-six minus-sign counterexample')
    m.require(sum(1 - 2*q6(x) for x in range(64)) == -8, 'minus-six Gauss sign')
    m.require(sum(q6(x) for x in m.span([1, 4, 16, 32])) == 12,
              'fiber affine-four minus-sign counterexample')
    m.require(sum(q6(x) for x in m.span([2, 4, 8, 16, 32])) == 20,
              'fiber affine-five minus-sign counterexample')


def field_hypotheses(roots, live):
    # The nonzero direction e0+e1 evaluates to zero over F2 on every root.
    h = (1, 1, 0, 0, 0, 0, 0, 0)
    values = [m.dot(r, h) for i, r in enumerate(roots) if live >> i & 1]
    m.require(any(values) and all(x % 2 == 0 for x in values), 'characteristic-two loss')
    f2 = [(a, b) for a in range(2) for b in range(2)]
    m.require(all(any((a*x+b*y) % 2 == 0 for a, b in [(1, 0), (0, 1), (1, 1)])
                  for x, y in f2), 'finite-field hyperplane union covers')
    m.require(not any(a*1+b*2 == 0 for a, b in [(1, 0), (0, 1), (1, 1)]),
              'rational point avoids same three hyperplanes')


def cli_controls(payloads):
    with tempfile.TemporaryDirectory(prefix='inherited-bounds-controls-') as tmp:
        root = Path(tmp)
        package = root / 'research/p112-inherited-bounds-audit'
        package.mkdir(parents=True)
        for name in ['verify.py', 'model.py', 'SOURCES.json', 'RESULT.json']:
            (package / name).write_bytes((HERE / name).read_bytes())
        for name, raw in payloads.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        bad_receipt = json.loads((package / 'RESULT.json').read_bytes())
        bad_receipt['a2']['joint_rank6_bound'] = True
        faults = [(root / v.TABLE, b'fault'), (package / 'SOURCES.json', b'{}'),
                  (package / 'RESULT.json', json.dumps(bad_receipt).encode())]
        for path, mutant in faults:
            original = path.read_bytes()
            path.write_bytes(mutant)
            run = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B',
                                  str(package / 'verify.py')], capture_output=True, text=True,
                                 timeout=180)
            path.write_bytes(original)
            m.require(run.returncode != 0 and 'ValueError' in run.stderr,
                      'actual optimized CLI accepted a fault')


def main():
    payloads = v.authenticate()
    roots, labels, coords, live = m.reconstruct(payloads[v.TABLE], payloads[v.GEOMETRY])
    count = small_spaces()
    basis_cases = 0
    for n, size in [(4, 4), (5, 3)]:
        for rows in combinations(range(1 << n), size):
            generated = set(m.span(rows))
            reduced = m.basis(rows, n)
            m.require(generated == set(m.span(reduced)) and len(generated) == 1 << len(reduced),
                      'binary basis versus complete generating sums')
            basis_cases += 1
    signed_hypotheses()
    field_hypotheses(roots, live)
    changed = payloads[v.TABLE].decode().splitlines()
    first = changed[0].split()
    first[0], first[1] = first[1], first[0]
    changed[0] = ' '.join(first)
    rejects(lambda: m.reconstruct('\n'.join(changed).encode(), payloads[v.GEOMETRY]))
    rejects(lambda: v.chamber(roots[:-1], coords[:-1]))
    rejects(lambda: v.load('{"bound":20,"bound":32}'))
    rejects(lambda: v.quadratic_model([x ^ 2 for x in labels]))
    cli_controls(payloads)
    print(f'PASS_INHERITED_AUDIT_CONTROLS small_spaces={count} basis_cases={basis_cases} negative_Gauss=4 '
          'characteristic_zero_boundaries=2 semantic_rejections=4 optimized_CLI_rejections=3')


if __name__ == '__main__':
    main()
