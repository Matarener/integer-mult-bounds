"""Bounded source, instruction and complete-state checks for the carry join.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged frontend and rotation retain their predecessor credit.
No predecessor verifier or mathematical supplier replay is invoked.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
import adapter

HERE = Path(__file__).resolve().parent
WEIGHTS = (-1, 0, -2, 0, -1, 0, 0, 0)
PRIVATE = (2, 3, 8, 9, 10, 11, 12, 13, 14, 15)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def exported(program):
    return json.loads(json.dumps(dict(tapes=program.tapes, entry=program.entry,
                                     instructions=program.instructions)))


def source_column(bundle, reverse_add=False):
    catalogue = json.loads(bundle['raw']['research/runtime-quarter-carry/inputs/route-RESULT.json'])
    route = next(row for row in catalogue['ports'] if row['port'] == 9)
    matrix = [[F(i == j) for j in range(8)] for i in range(8)]
    for operation in route['inverse']:
        coefficient = F(operation[-1])
        if operation[0] == 'ADD':
            source, target = operation[1:3]
            if reverse_add:
                source, target = target, source
            for row in matrix:
                row[target] += coefficient * row[source]
        else:
            need(operation[0] == 'SCALE', 'known exact route operation')
            for row in matrix:
                row[operation[1]] *= coefficient
    column = tuple(row[1] for row in matrix)
    need(column == tuple(F(x, 4) for x in WEIGHTS),
         'actual port9 inverse column1, with right-product ADD convention')
    return column


def arithmetic(values, modulus):
    numerator = sum(a * b for a, b in zip(WEIGHTS, values[:8]))
    low = numerator * pow(4, -1, 5) % 5
    code, remainder = divmod(numerator - 4 * low, 5)
    need(remainder == 0 and -6 <= code <= 0, 'integer source quarter code')
    return low, code, code * pow(4, -1, modulus) % modulus


def fixture(bundle, shape, values, payload):
    dense = bundle['dense']
    origins = [13 * tape - 79 for tape in range(19)]
    bank = [({o - 9: dense.ONE, o: dense.MARK, o + 11: dense.ZERO}, o) for o in origins]
    bank[0] = dense.marked([dense.ONE if b else dense.ZERO for b in payload], origins[0])
    for tape, extent in zip((4, 5, 7), shape):
        bank[tape] = dense.binary(extent, origins[tape])
    for tape in PRIVATE + (18,):
        bank[tape] = ({}, origins[tape])
    need(len(values) == 64 and all(type(x) is int and 0 <= x < 5 for x in values),
         'complete canonical 64-digit input fixture')
    bits = [(value >> bit) & 1 for value in values for bit in range(3)]
    cells = {origins[17] + j: dense.ONE if b else dense.ZERO for j, b in enumerate(bits)}
    cells.update({origins[17] + 192: dense.RIGHT,
                  origins[17] - 9: dense.MARK, origins[17] + 207: dense.ONE})
    bank[17] = (cells, origins[17])
    return bank


def raw_low(dense, value, origin):
    return ({origin + j: dense.ONE if value >> j & 1 else dense.ZERO for j in range(3)}, origin)


def native_run(bundle, program, bank, cap):
    machine = bundle['modules']['machine']
    result = machine.Machine(program, [machine.Tape(c, h) for c, h in bank]).run(cap)
    state = [(dict(tape.cells), tape.head) for tape in result.tapes]
    intervals = [(min(v or {t.head}), max(v or {t.head})) for t, v in zip(result.tapes, result.visits)]
    return state, result.steps, sum(hi - lo + 1 for lo, hi in intervals), intervals


def dense_run(bundle, table, bank, cap):
    tapes, steps = bundle['dense'].execute(table, bank, cap)
    return ([(t.snapshot(), t.head) for t in tapes], steps,
            sum(t.high - t.low + 1 for t in tapes), [(t.low, t.high) for t in tapes])


def expected_frontend(bundle, bank, values, modulus):
    low, code, offset = arithmetic(values, modulus)
    target = deepcopy(bank)
    target[18] = raw_low(bundle['dense'], low, bank[18][1])
    target[14] = bundle['dense'].binary(offset + 1, bank[14][1])
    return target, code


def check_composition(bundle, observation, bank, shape, values, payload, inverse):
    p, q, s = shape
    low, code, offset = arithmetic(values, q)
    sign = -1 if inverse else 1
    expected = [payload[(a * q + (x - sign * offset) % q) * s + z]
                for a, x, z in product(range(p), range(q), range(s))]
    target = deepcopy(bank)
    target[0] = bundle['dense'].marked(
        [bundle['dense'].ONE if b else bundle['dense'].ZERO for b in expected], bank[0][1] - 1)
    target[18] = raw_low(bundle['dense'], low, bank[18][1])
    need(observation[0] == target, 'every cell, head, borrowed input and declared output')
    need(observation[1] <= 393 * len(payload) + 600 * q.bit_length() + 30000,
         'complete composition transition bound')
    need(observation[2] <= 43 * len(payload) + 8 * q.bit_length() + 500,
         'complete composition visited-interval bound')
    return code, offset


def relocated(row, start, continuation=None):
    if row[0] == 'branch':
        return ('branch', row[1], tuple((s, t + start) for s, t in row[2]), row[3] + start)
    if row[0] == 'goto':
        return ('goto', row[1] + start)
    if row[0] == 'halt' and continuation is not None:
        return ('goto', continuation)
    return tuple(row)


def check_frontend_structure(bundle, program, metadata):
    source, starts = bundle['source_frontend'], metadata['row_starts']
    need(source['q'] == 5 and source['weights'] == list(WEIGHTS)
         and source['positions'] == list(range(8)) and source['cells'] == 64,
         'fixed actual source decoder parameters')
    tapes, m = (17, 18, 9, 5, 14), bundle['modules']['machine']
    symbols = {None:m.BLANK, 0:m.ZERO, 1:m.ONE, 2:m.RIGHT, 3:m.LEFT}
    need(tuple(metadata['tape_map']) == tapes and metadata['symbol_map'] == symbols,
         'declared tape and alphabet maps')
    need(program.instructions[:2] == (('move', 14, 1), ('goto', starts[source['start']])),
         'paid descriptor-origin alignment and source entry')
    cursor = 2
    for pc, row in enumerate(source['code']):
        need(starts[pc] == cursor, 'complete contiguous source instruction embedding')
        op = row[0]
        if op == 'branch':
            expected = [('branch', tapes[row[1]], tuple((symbols[s], starts[t]) for s, t in row[2]), starts[row[3]])]
        elif op in ('move', 'write'):
            value = row[2] if op == 'move' else symbols[row[2]]
            expected = [(op, tapes[row[1]], value), ('goto', starts[row[3]])]
        elif op == 'goto':
            expected = [('goto', starts[row[1]])]
        elif op == 'halt':
            expected = [('halt',)]
        else:
            need(op == 'reject' and program.instructions[cursor][0] == 'reject', 'source rejecting terminal')
            expected = [program.instructions[cursor]]
        need(program.instructions[cursor:cursor + len(expected)] == tuple(expected),
             'every source opcode, branch, successor and local operation is retained')
        cursor += len(expected)
    need(cursor == len(program.instructions), 'no undeclared frontend instructions')


def check_composition_structure(bundle, program, metadata, inverse):
    parts, programs = metadata['components'], metadata['component_programs']
    names = ('frontend', 'generic', 'cleanup')
    need(program.entry == parts['frontend']['entry'], 'composed entry')
    for index, name in enumerate(names):
        part, component = parts[name], programs[name]
        need(part['stop'] - part['start'] == len(component.instructions), 'component boundaries')
        continuation = parts[names[index + 1]]['entry'] if index < 2 else None
        expected = tuple(relocated(row, part['start'], continuation) for row in component.instructions)
        need(program.instructions[part['start']:part['stop']] == expected, 'literal linkage: ' + name)
    need(exported(programs['generic']) == bundle['tables']['generic:' + str(inverse)],
         'every retained generic consumer row and entry')
    need(parts['cleanup']['stop'] == len(program.instructions), 'complete final component')
    bundle['dense'].validate(exported(program))


def rejected(label, action, message, error_type=ValueError):
    try:
        action()
    except ValueError as error:
        need(type(error) is error_type and str(error) == message,
             'unexpected negative-control exception: ' + label + ': ' + repr(error))
        return label
    raise ValueError('negative control accepted: ' + label)


def program_with(bundle, program, index, row):
    rows = list(program.instructions)
    rows[index] = row
    return bundle['modules']['machine'].Program(tuple(rows), program.tapes, program.entry)


def controls(bundle, programs, metadata, front, bank, values, payload):
    program, shape, cap = programs[False], (1, 125, 1), 100000
    rejection = bundle['modules']['machine'].Rejected
    source_error = 'retained low-cache frontend rejected'
    state_error = 'every cell, head, borrowed input and declared output'
    bad = deepcopy(bank)
    for j, bit in enumerate((1, 0, 1)):
        bad[17][0][bad[17][1] + j] = bundle['dense'].ONE if bit else bundle['dense'].ZERO
    outcomes = [rejected('selected cache digit5', lambda: native_run(bundle, front, bad, cap),
                         source_error, rejection)]
    bad_end = deepcopy(bank)
    bad_end[17][0][bad_end[17][1] + 192] = bundle['dense'].ZERO
    outcomes.append(rejected('missing cache endpoint', lambda: native_run(bundle, front, bad_end, cap),
                             source_error, rejection))
    wrong = program_with(bundle, program, 0, ('goto', 1))
    outcomes.append(rejected('omitted descriptor origin alignment', lambda: check_composition(
        bundle, native_run(bundle, wrong, bank, cap), bank, shape, values, payload, False), state_error))
    generic = metadata[False]['component_programs']['generic']
    halt = next(i for i, row in enumerate(generic.instructions) if row[0] == 'halt')
    missing = program_with(bundle, program, metadata[False]['components']['generic']['start'] + halt, ('halt',))
    outcomes.append(rejected('omitted owned coefficient cleanup', lambda: check_composition(
        bundle, native_run(bundle, missing, bank, cap), bank, shape, values, payload, False), state_error))
    outcomes.append(rejected('wrong source ADD orientation', lambda: source_column(bundle, True),
                             'actual port9 inverse column1, with right-product ADD convention'))
    observation = native_run(bundle, program, bank, cap)
    outcomes.append(rejected('wrong fixed carry orientation', lambda: check_composition(
        bundle, observation, bank, shape, values, payload, True), state_error))
    corrupted = deepcopy(observation)
    corrupted[0][14][0][bank[14][1] + 777] = bundle['dense'].ONE
    outcomes.append(rejected('residual private cell beyond returned head', lambda: check_composition(
        bundle, corrupted, bank, shape, values, payload, False), state_error))
    nonlocal_table = exported(program)
    nonlocal_table['instructions'][0][2] = 2
    outcomes.append(rejected('nonlocal movement', lambda: bundle['dense'].validate(nonlocal_table),
                             'literal unit motion'))
    return outcomes


def run():
    bundle = adapter.load()
    column = source_column(bundle)
    front, front_metadata = adapter.frontend(bundle)
    check_frontend_structure(bundle, front, front_metadata)
    bundle['dense'].validate(exported(front))
    programs, metadata, tables = {}, {}, {}
    for inverse in (False, True):
        programs[inverse], metadata[inverse] = adapter.build(inverse, bundle)
        check_composition_structure(bundle, programs[inverse], metadata[inverse], inverse)
        tables[inverse] = exported(programs[inverse])
    digest = sha256()
    representatives, counts, front_steps, front_spans = {}, {}, [], []
    for index, (a, b, c) in enumerate(product(range(5), repeat=3)):
        values = [(index * 3 + j * 2 + 1) % 5 for j in range(64)]
        values[0], values[2], values[4] = a, b, c
        bank = fixture(bundle, (1, 125, 1), values, [0] * 125)
        observation = native_run(bundle, front, bank, 40000)
        target, code = expected_frontend(bundle, bank, values, 125)
        need(observation[0] == target, 'frontend exact outputs, complete source and every head')
        need(observation[1] <= 2 * (64 * 64 * 3 + 256 * 7 + 2048) + 2,
             'translated frontend transition bound')
        need(observation[2] <= 2 * 64 * 3 + 4 * 7 + 32 + 16, 'frontend visited-interval bound')
        representatives.setdefault(code, values)
        counts[code] = counts.get(code, 0) + 1
        front_steps.append(observation[1]); front_spans.append(observation[2])
        digest.update(canonical([values, observation[1:], code, target[18][0], target[14][0]]))
    need(counts == {-6:4, -5:18, -4:32, -3:30, -2:28, -1:12, 0:1}, 'complete relevant triple domain')
    rows = []

    def composed(values, shape, inverse, label):
        size = shape[0] * shape[1] * shape[2]
        payload = [int((j * j + 3 * j + j // 7 + 2) % 11 in (0, 1, 4, 7)) for j in range(size)]
        bank = fixture(bundle, shape, values, payload)
        cap = 393 * size + 600 * shape[1].bit_length() + 30001
        native = native_run(bundle, programs[inverse], bank, cap)
        dense = dense_run(bundle, tables[inverse], bank, cap)
        need(native == dense, 'independent interpreters agree on every cell, head and meter')
        code, offset = check_composition(bundle, native, bank, shape, values, payload, inverse)
        row = dict(label=label, shape=list(shape), inverse=inverse, code=code,
                   offset=offset, steps=native[1], visited=native[2],
                   visited_intervals=[list(interval) for interval in native[3]])
        rows.append(row)
        digest.update(canonical([row, native[0]]))
        return bank, payload

    for code in range(-6, 1):
        for inverse in (False, True):
            composed(representatives[code], (1, 125, 1), inverse, 'coordinate_leaf')
    for modulus in (5, 25):
        for inverse in (False, True):
            composed(representatives[-3], (2, modulus, 3), inverse, 'prefix_and_spectator')
    witness = [int(i == j) for i in range(8) for j in range(8)]
    witness[:8] = [2, 3, 2, 1, 1, 1, 0, 0]
    need(witness[0] == 2 and all(witness[8*i+j] == int(i == j) for i in range(1, 8) for j in range(8)),
         'source witness extends to GL8(F5), determinant2')
    need(arithmetic(witness, 125) == (2, -3, 93), 'published source witness arithmetic')
    for inverse in (False, True):
        witness_bank, witness_payload = composed(witness, (1, 125, 1), inverse, 'source_witness_leaf')
    negative = controls(bundle, programs, metadata, front, witness_bank, witness, witness_payload)
    return dict(status='PASS_PORT9_LOW_CACHE_CARRY',
                source=dict(port=9, direction='inverse', column=1, low_modulus=5, fixed_row=0,
                    cache_digits=64, column_entries=[str(x) for x in column], quarter_weights=list(WEIGHTS),
                    witness_low=witness[:8], witness_new_low=2, witness_code=-3,
                    witness_modulus=125, witness_offset=93),
                frontend_cases=125, code_counts={str(k):v for k,v in counts.items()},
                frontend_steps=[min(front_steps), max(front_steps)],
                frontend_visited=[min(front_spans), max(front_spans)],
                complete_compositions=len(rows), separate_interpreter_compositions=len(rows),
                compositions=rows, rejected_controls=negative,
                literal_tables={str(sign):dict(rows=len(programs[sign].instructions),
                    sha256=sha256(canonical(tables[sign])).hexdigest()) for sign in (False, True)},
                frontend_rows=len(front.instructions),
                input_sha256={p:sha256(raw).hexdigest() for p,raw in sorted(bundle['raw'].items())},
                oracle_sha256=digest.hexdigest(),
                uniform_bounds=dict(transitions='393V+600L+30000', visited='43V+8L+500',
                                    V='P*Q*S', L='bit_length(Q)'),
                limits=['P=S=1,Q=125 is a coordinate leaf, not the actual high-matrix layout.',
                        'Actual cell1 shape P=Q,S=Q^62*Z is not materialized.',
                        'The old64-digit cache and complete owner/extents are supplied.',
                        'New-low18 is an owned output; repeated calls need its paid preparation.',
                        'Inverse negates this fixed carry, not the opposite matrix route.',
                        'Whole-T cache, homogeneous routing, low commit, ROW and full invoice remain open.'])


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--write']), 'replay or explicit receipt generation')
    result = run()
    target = HERE / 'RESULT.json'
    if sys.argv[1:]:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        need(result == json.loads(target.read_text(encoding='utf-8')), 'exact retained deterministic receipt')
    print('PASS_PORT9_LOW_CACHE_CARRY')
    print(json.dumps({k:result[k] for k in ('frontend_cases', 'complete_compositions',
                                          'separate_interpreter_compositions', 'rejected_controls')}, sort_keys=True))
