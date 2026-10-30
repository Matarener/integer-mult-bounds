"""Compare the exact representation with literal vectors and algebra.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
import random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import quadratic as Q
import binding
from pins import authenticate, load


def random_gate(ce, rng, n, kind):
    if kind == 0:
        return ce.cgate(n, rng.randrange(1 << n), rng.choice([-1, 1]))
    if kind == 1:
        return ce.xgate(n, rng.randrange(1 << n))
    if kind == 2:
        rows = [0] * n
        for i in range(n):
            for j in range(i, n):
                if rng.getrandbits(1):
                    rows[i] ^= 1 << j
                    if i != j:
                        rows[j] ^= 1 << i
        return ce.diag(n, rows, [(rows[i] >> i & 1) + 2 * rng.randrange(2) for i in range(n)])
    if kind == 3:
        rows = [1 << i for i in range(n)]
        for _ in range(3 * n):
            a, b = rng.randrange(n), rng.randrange(n)
            if a != b:
                rows[a] ^= rows[b]
        return ce.perm(n, rows)
    return ce.Op(n, ce.identity(n), [('phase', rng.randrange(4))])


def polynomial_checks(rng):
    affine_cases = product_cases = substitution_cases = 0
    for n in range(5):
        for left in range(1 << (n + 1)):
            for coefficient in range(4):
                p = {}; Q.affine(p, left, coefficient)
                for x in range(1 << n):
                    expected = coefficient * (((left >> 1 & x).bit_count() & 1) ^ (left & 1)) % 4
                    Q.need(Q.value(p, x) == expected, 'Literal affine phase lift')
                    affine_cases += 1
            for right in range(1 << (n + 1)):
                p = {}; Q.product(p, left, right)
                for x in range(1 << n):
                    a = ((left >> 1 & x).bit_count() & 1) ^ (left & 1)
                    b = ((right >> 1 & x).bit_count() & 1) ^ (right & 1)
                    Q.need(Q.value(p, x) == 2 * a * b, 'Literal twice-product lift')
                    product_cases += 1
    for n in range(1, 8):
        for _ in range(24):
            p = {0: rng.randrange(4)}
            for i in range(n):
                Q.term(p, 1 << i, rng.randrange(4))
                for j in range(i):
                    Q.term(p, (1 << i) | (1 << j), 2 * rng.randrange(2))
            forms = [rng.randrange(1 << (n + 1)) for _ in range(n)]
            changed = Q.substitute(p, forms)
            for x in range(1 << n):
                old = sum(((((f >> 1 & x).bit_count() & 1) ^ (f & 1))) << i
                          for i, f in enumerate(forms))
                Q.need(Q.value(changed, x) == Q.value(p, old), 'Independent phase substitution')
                substitution_cases += 1
    return dict(affine_assignments=affine_cases, product_assignments=product_cases,
                substitution_assignments=substitution_cases)


def literal_checks(ce, tables, rng):
    states = amplitudes = adjoints = 0
    counters = {}; digest = sha256()
    for n in range(10):
        for trial in range(8):
            op = ce.ident(n)
            for step in range(18):
                gate = random_gate(ce, rng, n, step % 5) if n else ce.Op(0, (), [('phase', step)])
                op = op.then(gate)
                initial_values = range(1 << n) if n <= 4 else sorted({0, 1, (1 << n) - 1, rng.randrange(1 << n)})
                for initial in initial_values:
                    state = Q.signature(n, op.circuit, initial, counters)
                    literal, den = op.zero_state(initial)
                    Q.need((literal, den) == tables.zero_state(op, initial), 'Credited table evaluator and literal vectors')
                    for index, pair in enumerate(literal):
                        actual, power = Q.amplitude(state, index)
                        Q.need((actual[0] << den, actual[1] << den) == (pair[0] << power, pair[1] << power),
                               'Every exact amplitude and zero entry')
                        amplitudes += 1
                    digest.update(json.dumps(state, separators=(',', ':')).encode())
                    states += 1
            inverse = op.adjoint()
            Q.need(Q.equal_operators(op.then(inverse), ce.ident(n)), 'Exact inverse including global phase')
            Q.need(Q.equal_operators(inverse.then(op), ce.ident(n)), 'Reverse exact inverse')
            adjoints += 2
    for name in ('independent_root', 'odd_elimination', 'even_restriction'):
        Q.need(counters.get(name, 0) > 0, 'Every reachable root branch is exercised')
    return dict(states=states, amplitudes=amplitudes, exact_inverse_checks=adjoints,
                state_digest=digest.hexdigest(), root_branches=counters)


def large_checks(ce, rng):
    records = []
    for n in (16, 32, 64):
        # These circuits have full support. Their state vector has 2^n entries.
        op = ce.fourier(n)
        diagonal = [1 << i for i in range(n)]
        for i in range(n - 1):
            diagonal[i] ^= 1 << (i + 1); diagonal[i + 1] ^= 1 << i
        op = op.then(ce.diag(n, diagonal))
        rows = [1 << i for i in range(n)]
        for i in range(n - 1):
            rows[i] ^= rows[i + 1]
        op = op.then(ce.perm(n, rows)).then(ce.xgate(n, (1 << n) - 1))
        state = Q.signature(n, op.circuit)
        Q.need(len(state[2]) == n, 'Large example has full exponential support')
        same = op.then(ce.cgate(n, 3)).then(ce.cgate(n, 3, -1))
        Q.need(Q.equal_operators(op, same), 'Large inverse insertion')
        Q.need(Q.equal_operators(op.then(op.adjoint()), ce.ident(n)), 'Large complete inverse')
        phase = same.then(ce.Op(n, ce.identity(n), [('phase', 1)]))
        Q.need(phase.tab == op.tab and not Q.equal_operators(op, phase), 'Large absolute-phase rejection')
        records.append(dict(width=n, support_rank=n, circuit_gates=len(op.circuit),
                            phase_terms=len(state[3]), canonical_digest=sha256(repr(state).encode()).hexdigest()))
    return records


def rejecting_checks(ce):
    binding.run()
    rejected = []
    invalid = [('negative_width', -1, [], 0), ('boolean_width', True, [], 0),
               ('bad_basis', 2, [], 4), ('empty_gate', 2, [()], 0),
               ('unknown_gate', 2, [('H', 1)], 0),
               ('singular_permutation', 2, [('P', (1, 1))], 0),
               ('permutation_width', 2, [('P', (1,))], 0),
               ('negative_translation', 2, [('X', -1)], 0),
               ('root_sign', 2, [('C', 1, 0)], 0),
               ('root_width', 2, [('C', 4, 1)], 0),
               ('nonsymmetric_phase', 2, [('D', (2, 0), (0, 0))], 0),
               ('wrong_diagonal_lift', 2, [('D', (1, 2), (0, 0))], 0),
               ('phase_not_integer', 2, [('phase', 0.5)], 0)]
    for name, n, circuit, initial in invalid:
        try:
            Q.signature(n, circuit, initial)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Accepted malformed circuit: ' + name)
    original = ce.fourier(3).then(ce.diag(3, (3, 3, 4)))
    changed = original.then(ce.Op(3, ce.identity(3), [('phase', 1)]))
    Q.need(original.tab == changed.tab and not Q.equal_operators(original, changed), 'Same tableau, wrong scalar phase')
    z = ce.diag(3, (0, 0, 0), (2, 0, 0))
    changed = z.then(original)
    Q.need(Q.signature(3, original.circuit) == Q.signature(3, changed.circuit), 'Zero-column trap positive premise')
    Q.need(not Q.equal_operators(original, changed), 'Retain the full tableau, not only the zero state')
    state = Q.signature(3, original.circuit)
    mutations = {'phase': state[:4] + (-state[5], state[4], state[6]),
                 'denominator': state[:-1] + (state[-1] + 1,),
                 'support': (state[0], state[1], state[2][:-1]) + state[3:]}
    witnesses = {}
    for name, bad in mutations.items():
        for index in range(8):
            a, d = Q.amplitude(state, index); b, e = Q.amplitude(bad, index)
            if (a[0] << e, a[1] << e) != (b[0] << d, b[1] << d):
                witnesses[name] = index
                break
        Q.need(name in witnesses, 'A changed certificate must change a literal amplitude: ' + name)
    integration_rejections = []
    for filename, old, new in [
        ('replay.py', "O.need(recipe['rank'] == abs(len(c['frames'][b])-len(c['frames'][a])), 'Literal coframe Gaussian grade')", 'pass'),
        ('verify_source.py', 'tail_transfer=tail_checks(old,new)', 'tail_transfer={}')]:
        text = (ROOT / filename).read_text()
        Q.need(text.count(old) == 1, 'Unique omitted-check control site')
        try:
            binding.run({filename: text.replace(old, new)})
        except ValueError:
            integration_rejections.append(filename)
        else:
            raise ValueError('Accepted an omitted source proof obligation')
    return dict(integration_rejections=integration_rejections, malformed=rejected, semantic=['same_tableau_wrong_phase', 'same_zero_column_wrong_tableau',
                                            'canonical_phase', 'canonical_denominator', 'canonical_support'], amplitude_witnesses=witnesses)


def run():
    sources = authenticate()
    ce = load('literal_clifford', ROOT / 'source/source/clifford_exact.py')
    tables = load('literal_tables', ROOT / 'tables/fast_state.py')
    rng = random.Random(20261026)
    return dict(status='PASS_EXACT_CLIFFORD_QUADRATIC_REPLAY', source_files=sources,
                polynomial=polynomial_checks(rng), literal=literal_checks(ce, tables, rng),
                large=large_checks(ce, rng), controls=rejecting_checks(ce))


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (ROOT / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        Q.need(not sys.argv[1:], 'No unknown arguments')
        Q.need(result == json.loads((ROOT / 'RESULT.json').read_text()), 'Complete saved engine evidence')
    print(result['status'])
