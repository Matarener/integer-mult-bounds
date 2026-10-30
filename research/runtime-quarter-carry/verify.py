"""Check literal carry rotation, runtime dispatch and the full source envelope."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import lcm
from pathlib import Path
import gzip
import json
import random
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash: '+row['path'])


def module(name, path):
    out = types.ModuleType(name)
    out.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), out.__dict__)
    return out


def load():
    authenticate()
    modules = {}
    try:
        for name in ['machine', 'counters', 'shear']:
            need(name not in sys.modules, 'no preloaded retained macro')
            modules[name] = module(name, P/'inputs'/f'{name}.py')
            sys.modules[name] = modules[name]
    finally:
        for name in modules:
            sys.modules.pop(name, None)
    return (modules, module('dense', P/'inputs/independent.py'),
            module('descriptor', P/'inputs/descriptor.py'),
            module('quarter', P/'inputs/offset.py'), module('kernel', P/'kernel.py'))


def export(program):
    return json.loads(json.dumps(dict(tapes=program.tapes, entry=program.entry,
                                     instructions=program.instructions)))


def execute(modules, dense, program, bank, cap, engine='dense'):
    if engine == 'dense':
        tapes, steps = dense.execute(export(program), bank, cap)
        state = [dict(cells=t.snapshot(), head=t.head, span=t.high-t.low+1) for t in tapes]
        return state, steps
    m = modules['machine']
    out = m.Machine(program, [m.Tape(c, h) for c, h in bank]).run(cap)
    state = [dict(cells=dict(t.cells), head=t.head,
                  span=max(v or {t.head})-min(v or {t.head})+1)
             for t, v in zip(out.tapes, out.visits)]
    return state, out.steps


def fixture(dense, kernel, shape, payload, value, quarter=False):
    origins = [7*t-39 for t in range(19)]
    bank = [({o-5:dense.ONE, o:dense.MARK, o+4:dense.RIGHT}, o) for o in origins]
    bank[0] = dense.marked([dense.ONE if b else dense.ZERO for b in payload], origins[0])
    for t, n in zip((4, 5, 7), shape):
        bank[t] = dense.binary(n, origins[t])
    for t in kernel.WORK:
        bank[t] = ({}, origins[t])
    if quarter:
        bank[14] = ({}, origins[14])
        bank[16] = dense.marked([dense.ONE if (value+16)>>j & 1 else dense.ZERO
                                for j in range(5)], origins[16])
    else:
        bank[14] = dense.binary(value+1, origins[14])
    return bank


def check(state, steps, bank, dense, kernel, shape, payload, value, inverse, quarter=False):
    p, q, s = shape
    offset = value*pow(4, -1, q) % q if quarter else value
    sign = -1 if inverse else 1
    expected = [payload[(a*q+(x-sign*offset)%q)*s+z]
                for a, x, z in product(range(p), range(q), range(s))]
    cells, head = dense.marked([dense.ONE if b else dense.ZERO for b in expected], bank[0][1]-1)
    need(state[0]['cells'] == cells and state[0]['head'] == head, 'complete original-owner rotation')
    private = set(kernel.WORK) | ({14} if quarter else set())
    for t, row in enumerate(state):
        if t in private:
            need(not row['cells'] and row['head'] == bank[t][1], 'whole private cells and heads return')
        elif t != 0:
            need(row['cells'] == bank[t][0] and row['head'] == bank[t][1], 'all descriptors and spectators return')
    span = sum(row['span'] for row in state)
    need(steps <= (468 if quarter else 393)*len(payload), 'sharp uniform transition bound')
    need(span <= (49 if quarter else 43)*len(payload), 'sharp uniform visited-cell bound')
    if not quarter:
        extents = (p, q, s, offset+1)
        convert = sum(24*n-7*n.bit_count()+15*n.bit_length()+12 for n in extents)
        exact_steps = convert+36*len(payload)+20*p*q+29*p+s+7*q+31*offset+124
        exact_span = (2*len(payload)+p+s+q+2*offset+max(n.bit_length() for n in extents)
                      +sum(n.bit_length() for n in extents)+33)
        need(steps == exact_steps and span == exact_span, 'exact all-size physical ledger')
    return expected, span


def matrix(word):
    out = [[F(i == j) for j in range(8)] for i in range(8)]
    for op in word:
        c = F(op[-1])
        need(c.denominator in (1, 2, 4), 'source dyadic operation')
        if op[0] == 'ADD':
            for row in out:
                row[op[2]] += c*row[op[1]]
        else:
            need(op[0] == 'SCALE', 'source operation')
            for row in out:
                row[op[1]] *= c
    return out


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def envelope():
    source = json.loads((P/'inputs/route-RESULT.json').read_text())
    rng = random.Random(5846)
    rows, cases, witness = [], 0, None
    identity = [[F(i == j) for j in range(8)] for i in range(8)]
    digest = sha256()
    for key in ('ports', 'scale_free_ports'):
        need([r['port'] for r in source[key]] == list(range(111)), 'all source ports')
        for row in source[key]:
            matrices = {name:matrix(row[name]) for name in ('forward', 'inverse')}
            need(multiply(matrices['forward'], matrices['inverse']) == identity and
                 multiply(matrices['inverse'], matrices['forward']) == identity, 'both exact route products')
            for direction, mat in matrices.items():
                for j, col in enumerate(zip(*mat)):
                    d = lcm(*(x.denominator for x in col))
                    need(d in (1, 4), 'whole-word denominator class')
                    coefficients = [int(d*x) for x in col]
                    negative = sum(min(a, 0) for a in coefficients)
                    positive = sum(max(a, 0) for a in coefficients)
                    lower = (negative-d+1)*4//d
                    upper = (positive-1 if positive else 0)*4//d
                    need(-16 <= lower <= upper <= 12, 'uniform complete source carry envelope')
                    rows.append([key, row['port'], direction, j, d, lower, upper])
                    for q in [3, 5, 25, 2**89-1]:
                        lows = [[rng.randrange(q) for _ in range(8)],
                                [q-1 if a < 0 else 0 for a in coefficients],
                                [q-1 if a > 0 else 0 for a in coefficients]]
                        for low in lows:
                            n = sum(x*a for x, a in zip(low, coefficients))
                            target = n*pow(d, -1, q) % q
                            quotient, remainder = divmod(n-d*target, q)
                            need(remainder == 0, 'integer carry after q cancellation')
                            code = F(4*quotient, d)
                            need(code.denominator == 1 and lower <= code <= upper, 'actual quarter code')
                            if code == -3 and q == 5 and witness is None:
                                witness = dict(basis=key, port=row['port'], direction=direction,
                                    column=j, low=low, q=q, code=int(code), high_modulus=125,
                                    residue=int(code)*pow(4, -1, 125) % 125)
                            # Check the rational split at a full modulus, apart from the envelope bound.
                            high = [rng.randrange(q*q) for _ in range(8)]
                            values = [a+q*b for a, b in zip(low, high)]
                            whole = sum(x*a for x, a in zip(values, coefficients))*pow(d, -1, q**3) % (q**3)
                            high_image = (sum(x*a for x, a in zip(high, coefficients))+quotient)*pow(d, -1, q*q) % (q*q)
                            need(target+q*high_image == whole, 'independent full-width carry identity')
                            digest.update(canonical([key, row['port'], direction, j, str(q), int(code), str(whole)]))
                            cases += 1
    need(witness is not None and witness['residue'] == 93, 'source-bound nonzero quarter witness')
    return dict(routes=444, columns=len(rows), code_bounds=[min(r[-2] for r in rows), max(r[-1] for r in rows)],
                column_bounds=rows, full_width_cases=cases, oracle_sha256=digest.hexdigest(), witness=witness)


def reject(label, fn):
    try:
        fn()
    except (ValueError, RuntimeError):
        return label
    raise ValueError('accepted control: '+label)


def run(write=False):
    modules, dense, descriptor, quarter, kernel = load()
    programs = {}
    for inv in (False, True):
        programs['generic:'+str(inv)] = kernel.build(modules, inv)
        programs['quarter:'+str(inv)] = kernel.quarter_program(modules, descriptor, quarter, inv)
    tables = {key:export(program) for key, program in programs.items()}
    for key, table in tables.items():
        dense.validate(table)
        untouched = {1, 6, 9, 17, 18} | ({16} if key.startswith('generic') else set())
        need(not any(r[0] in ('branch', 'write', 'move') and r[1] in untouched
                     for r in table['instructions']), 'unused banks are never touched')
    if write:
        (P/'TABLE.json.gz').write_bytes(gzip.compress(canonical(tables)+b'\n', mtime=0))
    else:
        need(canonical(json.loads(gzip.decompress((P/'TABLE.json.gz').read_bytes()))) == canonical(tables),
             'all fixed compiled tables')
    digest = sha256()
    counts = dict(generic_cases=0, quarter_cases=0, payload_bits=0, inverse_pairs=0)
    peaks = dict(generic_steps_per_bit=F(0), quarter_steps_per_bit=F(0),
                 generic_span_per_bit=F(0), quarter_span_per_bit=F(0))

    def case(shape, payload, value, inv, is_quarter, roundtrip=False):
        name = 'quarter' if is_quarter else 'generic'
        bank = fixture(dense, kernel, shape, payload, value, is_quarter)
        observations = []
        for engine in ('sparse', 'dense'):
            state, steps = execute(modules, dense, programs[name+':'+str(inv)], bank,
                                   1024*len(payload)+1, engine)
            expected, span = check(state, steps, bank, dense, kernel, shape, payload, value, inv, is_quarter)
            observations.append((state, steps))
        need(observations[0] == observations[1], 'all cells, heads and meters agree between interpreters')
        if roundtrip:
            current = [(r['cells'], r['head']) for r in state]
            back, paid = execute(modules, dense, programs[name+':'+str(not inv)], current, 1024*len(payload)+1)
            check(back, paid, current, dense, kernel, shape, expected, value, not inv, is_quarter)
            need(all(r['cells'] == b[0] and r['head'] == b[1] for r, b in zip(back, bank)), 'whole-bank inverse identity')
            counts['inverse_pairs'] += 1
        counts[name+'_cases'] += 1
        counts['payload_bits'] += len(payload)
        peaks[name+'_steps_per_bit'] = max(peaks[name+'_steps_per_bit'], F(steps, len(payload)))
        peaks[name+'_span_per_bit'] = max(peaks[name+'_span_per_bit'], F(span, len(payload)))
        digest.update(canonical([name, shape, value, inv, steps, span, expected]))

    for q in range(1, 10):
        for value in range(q):
            payloads = list(product((0, 1), repeat=q)) if q <= 4 else [tuple(int(j == i) for j in range(q)) for i in range(q)]
            for payload in payloads:
                for inv in (False, True):
                    case((1, q, 1), payload, value, inv, False)
            shape = (2, q, 3)
            payload = [(j*7+j//5+value) & 1 for j in range(6*q)]
            for inv in (False, True):
                case(shape, payload, value, inv, False, True)
    for shape, value in [((17, 1, 1), 0), ((1, 1, 17), 0), ((1, 255, 1), 254), ((1, 2, 17), 1)]:
        size = shape[0]*shape[1]*shape[2]
        for inv in (False, True):
            case(shape, [int(j == size//2) for j in range(size)], value, inv, False, True)
    for value in range(-16, 13):
        for q in (1, 3, 5, 7, 9, 17, 125):
            shape = (1, 1, 1) if q == 1 else (2, q, 3)
            payload = [(j*7+j//3+value) & 1 for j in range(shape[0]*q*shape[2])]
            for inv in (False, True):
                case(shape, payload, value, inv, True, q in (1, 5, 125))
        for payload in ([0], [1]):
            for inv in (False, True):
                case((1, 1, 1), payload, value, inv, True)
    source = envelope()
    case((1, 125, 1), [int(j == 7) for j in range(125)], source['witness']['code'], False, True, True)
    need(peaks == dict(generic_steps_per_bit=F(393), quarter_steps_per_bit=F(468),
                      generic_span_per_bit=F(43), quarter_span_per_bit=F(49)), 'all four uniform bounds attained')

    controls = []
    good = fixture(dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], 2)
    for q, c in [(0, 0), (5, 5), (5, 6)]:
        bank = deepcopy(good)
        bank[5] = dense.binary(q, bank[5][1]-1)
        bank[14] = dense.binary(c+1, bank[14][1]-1)
        controls.append(reject('invalid extent or offset '+str((q, c)),
            lambda b=bank:execute(modules, dense, programs['generic:False'], b, 20000)))
    for value in [13, 14, 15]:
        bank = fixture(dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], value, True)
        controls.append(reject('unused runtime code '+str(value+16),
            lambda b=bank:execute(modules, dense, programs['quarter:False'], b, 20000)))
    bank = fixture(dense, kernel, (1, 4, 1), [0, 1, 0, 0], 1, True)
    controls.append(reject('even quarter modulus', lambda:execute(modules, dense, programs['quarter:False'], bank, 20000)))
    bank = fixture(dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], 1, True)
    bad = deepcopy(bank)
    bad[16] = dense.marked([dense.ONE]*6, bad[16][1]-1)
    controls.append(reject('wrong runtime packet length', lambda:execute(modules, dense, programs['quarter:False'], bad, 20000)))
    state, steps = execute(modules, dense, programs['generic:False'], good, 20000)
    controls.append(reject('wrong sign with valid permutation', lambda:check(state, steps, good, dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], 2, True)))
    wrong = deepcopy(tables['generic:False'])
    next(r for r in wrong['instructions'] if r[0] == 'move')[2] = 2
    controls.append(reject('nonlocal head move', lambda:dense.validate(wrong)))
    # An omitted descriptor eraser leaves a correct payload but a wrong private state.
    omitted = descriptor.link(modules, [descriptor.prepare(modules, quarter, 1), programs['generic:False']])
    state, steps = execute(modules, dense, omitted, bank, 20000)
    controls.append(reject('omit owned coefficient erasure', lambda:check(state, steps, bank, dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], 1, False, True)))
    state, steps = execute(modules, dense, programs['quarter:False'], bank, 20000)
    state[2]['cells'][bank[2][1]+200] = dense.ONE
    controls.append(reject('residual outside returned head', lambda:check(state, steps, bank, dense, kernel, (1, 5, 1), [0, 1, 0, 0, 0], 1, False, True)))
    return dict(source=source, **counts, peak_ratios={k:str(v) for k, v in peaks.items()},
        literal_tables={key:len(t['instructions']) for key, t in tables.items()},
        uniform_bounds=dict(generic=[393, 43], quarter=[468, 49], volume='P*Q*S', tight_for_these_tables=True),
        oracle_sha256=digest.hexdigest(), rejected_controls=controls,
        limits=['The caller supplies the declared complete stream and extent descriptors.',
                'The runtime code packet is supplied; its low-cache production and selection are not proved.',
                'Whole-T staging, type commit, full ROW heads, stock/P3 and supplier admission remain open.',
                'No selected frontier or kappa change.'])


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--write']), 'replay or explicit regeneration')
    result = run(sys.argv[1:] == ['--write'])
    if sys.argv[1:]:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((P/'RESULT.json').read_text()), 'exact retained receipt')
    print('PASS_RUNTIME_QUARTER_CARRY')
    print(json.dumps({k:result[k] for k in ('generic_cases', 'quarter_cases', 'payload_bits', 'inverse_pairs', 'peak_ratios', 'literal_tables')}, sort_keys=True))
