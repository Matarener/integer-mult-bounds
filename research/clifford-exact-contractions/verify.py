"""Exact checks for phase-sensitive Clifford contractions. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import gzip
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import contractions as C
Q = C.Q
ce = C.load_source('contraction_literal', 'clifford_exact.py')
P = C.load_source('contraction_recipes', 'prune_native.py')


def encode(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def literal_inner(left, right):
    a, da = left; b, db = right
    result = (0, 0)
    for x, y in zip(a, b):
        result = C.add(result, Q.multiply(C.conjugate(x), y))
    return F(result[0], 1 << (da + db)), F(result[1], 1 << (da + db))


def literal_trace(op):
    result = (F(0), F(0))
    for j in range(1 << op.n):
        vec, den = op.zero_state(j)
        result = C.add(result, (F(vec[j][0], 1 << den), F(vec[j][1], 1 << den)))
    return result


def random_op(n, rng, length=16):
    op = ce.ident(n)
    for k in range(length):
        if not n or k % 5 == 4:
            gate = ce.Op(n, ce.identity(n), [('phase', rng.randrange(4))])
        elif k % 5 == 0:
            gate = ce.cgate(n, rng.randrange(1 << n), rng.choice((-1, 1)))
        elif k % 5 == 1:
            rows = [0] * n
            for i in range(n):
                for j in range(i, n):
                    if rng.getrandbits(1):
                        rows[i] ^= 1 << j
                        if i != j: rows[j] ^= 1 << i
            gate = ce.diag(n, rows, [(rows[i] >> i & 1) + 2 * rng.randrange(2) for i in range(n)])
        elif k % 5 == 2:
            gate = ce.xgate(n, rng.randrange(1 << n))
        else:
            rows = [1 << i for i in range(n)]
            for _ in range(2 * n):
                a, b = rng.randrange(n), rng.randrange(n)
                if a != b: rows[a] ^= rows[b]
            gate = ce.perm(n, rows)
        op = op.then(gate)
    return op


def algebra_checks(rng):
    systems = sums = 0
    for n in range(4):
        options = list(product(range(1 << n), range(2)))
        for equations in product(options, repeat=3):
            resolved = C.solution(n, equations)
            expected = {x for x in range(1 << n) if all(((a & x).bit_count() & 1) == b for a, b in equations)}
            if resolved is None:
                actual = set()
            else:
                d, forms = resolved
                actual = {sum(((((f >> 1) & x).bit_count() & 1) ^ (f & 1)) << j
                              for j, f in enumerate(forms)) for x in range(1 << d)}
                Q.need(len(actual) == 1 << d, 'Affine parameterization is injective')
            Q.need(actual == expected, 'Complete independent solution set')
            systems += 1
    for n in range(5):
        masks = [1 << j for j in range(n)] + [(1 << i) | (1 << j) for i in range(n) for j in range(i)]
        domains = [range(4)] * n + [(0, 2)] * (len(masks) - n)
        for values in product(*domains):
            p = {m: v for m, v in zip(masks, values) if v}
            for constant in range(4):
                if constant: p[0] = constant
                else: p.pop(0, None)
                expected = (0, 0)
                for x in range(1 << n):
                    expected = C.add(expected, Q.multiply_i((1, 0), Q.value(p, x)))
                Q.need(C.gauss(n, p) == expected, 'Complete literal Gauss sum')
                sums += 1
    for n in range(5, 11):
        for _ in range(32):
            p = {0: rng.randrange(1, 4)}
            for i in range(n):
                Q.term(p, 1 << i, rng.randrange(4))
                for j in range(i): Q.term(p, (1 << i) | (1 << j), 2 * rng.randrange(2))
            expected = (0, 0)
            for x in range(1 << n): expected = C.add(expected, Q.multiply_i((1, 0), Q.value(p, x)))
            Q.need(C.gauss(n, p) == expected, 'Larger literal Gauss sum')
            sums += 1
    return dict(complete_affine_systems=systems, exact_gauss_sums=sums)


def small_checks(rng):
    inner_checks = traces = kernel_checks = 0
    for n in range(6):
        for _ in range(12):
            a, b = random_op(n, rng), random_op(n, rng)
            for initial in range(1 << n):
                sa = Q.signature(n, a.circuit, initial)
                for other in sorted({0, initial, (1 << n) - 1}):
                    sb = Q.signature(n, b.circuit, other)
                    Q.need(C.inner(sa, sb) == literal_inner(a.zero_state(initial), b.zero_state(other)), 'Literal complete state overlap')
                    inner_checks += 1
            Q.need(C.trace(n, a.circuit) == literal_trace(a), 'Literal matrix trace')
            traces += 1
            actual = C.inner(C.choi(n, a.circuit), C.choi(n, b.circuit))
            expected = literal_trace(b.then(a.adjoint()))
            Q.need(actual == (expected[0] / (1 << n), expected[1] / (1 << n)), 'Literal cross trace and conjugation order')
            kernel_checks += 1
    return dict(literal_overlaps=inner_checks, literal_traces=traces, literal_cross_traces=kernel_checks)


def one_axis_group():
    generators = [ce.cgate(1, 1), ce.diag(1, [1]), ce.Op(1, ce.identity(1), [('phase', 1)])]
    def key(op):
        v, d = op.zero_state()
        return op.tab, tuple(v), d
    group = {key(ce.ident(1)): ce.ident(1)}
    queue = list(group.values())
    for op in queue:
        for g in generators:
            other = op.then(g); k = key(other)
            if k not in group:
                group[k] = other; queue.append(other)
    Q.need(len(queue) == 96, 'All exact one-axis lifts')
    states = [C.choi(1, op.circuit) for op in queue]
    count = 0
    for i, a in enumerate(queue):
        for j, b in enumerate(queue):
            expected = literal_trace(b.then(a.adjoint()))
            Q.need(C.inner(states[i], states[j]) == (expected[0] / 2, expected[1] / 2), 'Every exact one-axis phase kernel')
            count += 1
    return dict(exact_lifts=len(queue), complete_kernel_entries=count)


def magnitude_from_paulis(op):
    n = op.n
    columns = [x | (z << n) for x, z, _ in op.tab]
    rows = [sum((((c ^ (1 << j)) >> i) & 1) << j for j, c in enumerate(columns)) for i in range(2 * n)]
    resolved = C.solution(2 * n, [(r, 0) for r in rows])
    d, forms = resolved
    for k in range(d):
        vector = sum(((f >> (k + 1)) & 1) << j for j, f in enumerate(forms))
        x, z = vector & ((1 << n) - 1), vector >> n
        result = ce.apply(op.tab, (x, z, 0))
        Q.need(result[:2] == (x, z), 'Fixed Pauli direction')
        if result[2]:
            Q.need(result[2] == 2, 'Fixed Pauli has a real conjugation sign')
            return 0
    return 1 << d


def native_checks():
    data = json.loads(gzip.decompress((ROOT / 'source/CONSTRUCTION.json.gz').read_bytes()))
    Q.need(len(data['maps']) == json.loads((ROOT / 'source/PHYSICAL.json').read_text())['distinct_literal_maps'], 'Complete retained native map set')
    rows = {}; dense = {}; examples = {}
    for key, recipe in sorted(data['maps'].items()):
        op = P.monomial(ce, recipe['left'], 9)
        if recipe['rank']:
            op = P.monomial(ce, recipe['right'], 9).then(ce.fourier(9, range(recipe['rank']))).then(op)
        else:
            Q.need(recipe['right'] is None, 'Rank-zero map has no child wrapper')
        tr = C.trace(9, op.circuit)
        Q.need(tr[0] ** 2 + tr[1] ** 2 == magnitude_from_paulis(op), 'Independent signed-Pauli trace magnitude')
        rows[key] = [str(x) for x in tr]
        examples.setdefault(recipe['rank'], (key, op))
    for rank, (key, op) in sorted(examples.items()):
        tr = literal_trace(op)
        Q.need(rows[key] == [str(x) for x in tr], 'Full 512-column native trace with absolute phase')
        dense[key] = rows[key]
    return dict(native_maps=len(rows), dense_native_maps=len(dense), native_trace_sha256=sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(), dense_examples=dense)


def residual_checks(rng):
    tests = []
    for n in (0, 1, 3, 9, 32):
        op = random_op(n, rng, 8)
        same = op.then(ce.cgate(n, (1 << n) - 1)).then(ce.cgate(n, (1 << n) - 1, -1))
        result = C.decide(n, [op.circuit, same.circuit], [(1, 0), (-1, 0)])
        Q.need(result['all_positive_widths_zero'], 'Exact identity with different circuit words')
        phases = [op.circuit + [('phase', j)] for j in range(4)]
        for residue in range(4):
            coefficients = [Q.multiply_i((1, 0), -residue * j) for j in range(4)]
            result = C.decide(n, phases, coefficients)
            Q.need(not result['all_positive_widths_zero'], 'Three phase residues cannot certify the fourth')
            Q.need(result['norms'] == [F(16 if f % 4 == residue else 0) for f in result['widths']], 'Exact phase cancellation and tensor scaling')
        tests.append(dict(axes=n, widths=result['widths']))
    large = []
    for n in (16, 32, 64):
        op = ce.fourier(n)
        tr = C.trace(n, op.circuit)
        Q.need(tr == Q.multiply_i(C.power((1, 1), n), 0), 'Large product trace closed form')
        state = C.choi(n, op.circuit)
        Q.need(len(state[2]) == 2 * n, 'Large Choi state has full support')
        Q.need(C.inner(state, state) == (1, 0), 'Large exact norm')
        large.append(dict(axes=n, choi_support_rank=len(state[2]), support_size=str(1 << (2 * n)), trace=[str(x) for x in tr]))
    return dict(four_width_fixtures=tests, large_supports=large)


def projection_checks():
    identity = C.choi(1, [])
    x = C.choi(1, [('X', 1)])
    target = C.choi(1, [('C', 1, 1)])
    records = []
    for width in (1, 2, 3, 4, 8, 40, 257):
        result = C.best_approximation([identity, x, identity], target, width)
        Q.need(result['span_rank'] == 2, 'Dependent sources preserve exact rank')
        Q.need(result['squared_residual'] == 1 - F(1, 1 << (width - 1)), 'Sharp complete two-source approximation at every tested width')
        records.append(dict(width=width, squared_residual=result['squared_residual']))
    return records


def negative_controls():
    invalid = [lambda: C.gauss(-1, {}), lambda: C.gauss(2, {3: 1}),
               lambda: C.gauss(1, {2: 2}), lambda: C.gauss(1, {1: 0}),
               lambda: C.solution(1, [(2, 0)]), lambda: C.solution(1, [(1, 2)]),
               lambda: C.choi(1, [('P', [0])]), lambda: C.choi(1, [('C', 2, 1)]),
               lambda: C.decide(1, [[]], [(0.5, 0)]),
               lambda: C.decide(1, [[]], []),
               lambda: C.residual_norm([[(1, 0)]], [(1, 0)], 0),
               lambda: C.inner(Q.signature(1, []), Q.signature(2, []))]
    for check in invalid:
        try: check()
        except ValueError: pass
        else: raise ValueError('Malformed input was accepted')
    Q.need(C.gauss(1, {1: 2}) == (0, 0), 'Destructive sum is not its absolute row sum')
    Q.need(C.inner(Q.signature(1, []), Q.signature(1, [('X', 1)])) == (0, 0), 'Disjoint affine supports')
    Q.need(C.inner(Q.signature(1, []), Q.signature(1, [('phase', 1)])) == (0, 1), 'Global phase and conjugation order')
    return dict(malformed_rejections=len(invalid), semantic_controls=3)


def run():
    records = json.loads((ROOT / 'INPUTS.json').read_text())
    for row in records:
        Q.need(sha256((ROOT / 'source' / row['local']).read_bytes()).hexdigest() == row['sha256'], 'All frozen source bytes')
    rng = random.Random(57045226)
    result = dict(algebra=algebra_checks(rng), small=small_checks(rng), one_axis=one_axis_group(),
                  native=native_checks(), residuals=residual_checks(rng), projections=projection_checks(), controls=negative_controls(), frozen_inputs=len(records))
    return json.loads(json.dumps(result, default=encode))


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write-result']:
        (ROOT / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        Q.need(not sys.argv[1:], 'No unknown replay flags')
        Q.need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'Entire committed result')
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_EXACT_CLIFFORD_CONTRACTIONS')
