#!/usr/bin/env python3
"""Fail-closed exact Fourier-operator gate for the retained global data graph.

The positive theorem is for every character, not only coordinate characters.
Local endpoint/native/hosting admission remains a separate required interface.
No all-size multiplication theorem or native repair tariff is claimed here.

Sources: the Rohan Arun et al. nine-stage construction; Nick Petalas / PR3187
operator semantics; PR3955 MOVES; PR4046 and the independent dense audit.
New symbolic gauge reduction and exhaustive gate: substantial OpenAI assistance.
Apache-2.0. All predecessor files are read-only.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

# Read-only imports of frozen reference implementations must not create cache
# files in their source directories.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = REPO / 'research/kappa-1745-continuation'
TEMPLATE = OLD / 'operator-audit/checkout/research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz'
PHASES = OLD / 'operator-audit/checkout/research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
MOVES = REPO / 'research/kappa-next-regime/sources/PR3959/research/rank7-idle-frame-select/MOVES.json.gz'
DENSE = OLD / 'operator-audit/independent_witness.py'
CELL = OLD / 'complex/CELLMAP-INVARIANCE.json'
PINS = {
    TEMPLATE: '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e',
    PHASES: 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    MOVES: '01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b',
    DENSE: 'de44470a6680252090246eafbc6e0544784f31d30f64c21c79c1321e2f5c43bf',
    CELL: '32a10aff786f3a673ca19ef5189c98e8a2a32708a0dc73a47eeee2bd44fd100b',
}
N = 8
DIM = 73
ZERO, ONE = (0, 0), (1, 0)
UNITS = (ONE, (0, 1), (-1, 0), (0, -1))
QZERO = ((0,) * DIM, 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    for path, digest in PINS.items():
        require(sha(path) == digest, 'source pin mismatch: ' + str(path))
    cell = read(CELL)
    require(cell['hosted_rows_checked'] == 2717280, 'hosted chronology coverage')
    for path, digest in cell['source_pins'].items():
        require(sha(REPO / path) == digest, 'retained chronology source changed: ' + path)


@lru_cache(None)
def parity_form(axis):
    """χ_axis(x) modulo 4: sum x_j - 2 sum_{j<k} x_j x_k."""
    require(type(axis) is int and 0 <= axis < (1 << DIM), '73-bit axis')
    support = [j for j in range(DIM) if (axis >> j) & 1]
    linear = tuple((axis >> j) & 1 for j in range(DIM))
    quadratic = 0
    for j in support:
        for k in support:
            if j < k:
                quadratic ^= 1 << (DIM * j + k)
    return linear, quadratic


def qadd(a, b):
    return tuple((x + y) % 4 for x, y in zip(a[0], b[0])), a[1] ^ b[1]


def qscale(a, scale):
    return tuple((scale * x) % 4 for x in a[0]), a[1] if scale % 2 else 0


def qsum(axes, translation=0):
    result = qscale(parity_form(int(translation)), 2)
    for axis in axes:
        result = qadd(result, parity_form(int(axis)))
    return result


def level(stage, side, q):
    if stage == -1:
        return parity_form(q) if side == 0 else QZERO
    require(0 <= stage <= 8, 'stage range')
    coordinate = (tuple(int(j < 9 + 8 * stage) for j in range(DIM)), 0)
    return qadd(coordinate, qscale(parity_form(q), -side))


def identity():
    return [[ONE if i == j else ZERO for j in range(N)] for i in range(N)]


def gadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def gmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def matmul(a, b):
    out = [[ZERO] * N for _ in range(N)]
    for i in range(N):
        for k in range(N):
            if a[i][k] != ZERO:
                for j in range(N):
                    if b[k][j] != ZERO:
                        out[i][j] = gadd(out[i][j], gmul(a[i][k], b[k][j]))
    return out


def scale_row(matrix, row, scalar):
    matrix[row] = [gmul(scalar, x) for x in matrix[row]]


def add_row(matrix, dst, src, coefficient):
    matrix[dst] = [gadd(a, (coefficient * b[0], coefficient * b[1]))
                   for a, b in zip(matrix[dst], matrix[src])]


def scalar_action(matrix, event, inverse=False):
    kind = event[0]
    if kind == 'add':
        _, dst, src, coefficient = event
        add_row(matrix, dst, src, -coefficient if inverse else coefficient)
    elif kind == 'terminal':
        for p in range(4):
            x, y = matrix[2 * p], matrix[2 * p + 1]
            if inverse:
                matrix[2 * p], matrix[2 * p + 1] = [(-a, -b) for a, b in y], x
            else:
                matrix[2 * p], matrix[2 * p + 1] = y, [(-a, -b) for a, b in x]
    else:
        raise ValueError('unrecognized scalar event: ' + str(event))


def normalize(template, recipe):
    """Prove P_t = D_t M_t D_initial^-1 as exact Z4 phase polynomials.

    Hosted factors are collapsed only using the separately pinned complete
    chronology certificate. Local canonical endpoint formulas are the declared
    source interface; this function does not reprove the local invocation.
    """
    q = int(recipe['q'])
    initial = [level(-1, s, q) for _ in range(4) for s in range(2)]
    gauges = list(initial)
    matrix = identity()
    local = {e['stage']: e for e in template['recipe'] if e['kind'] == 'local'}
    events, prefixes, checks = [], {}, 0

    def shear(dst, src, coefficient):
        nonlocal checks
        require(gauges[dst] == gauges[src], 'unequal exact gauges across scalar edge')
        checks += 1
        event = ('add', dst, src, coefficient)
        scalar_action(matrix, event)
        events.append(event)

    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            stage = event['stage']
            record = local[stage]
            pair = record['pair']
            for side in range(2):
                stream = 2 * pair + side
                require(gauges[stream] == level(stage - 1, side, q), 'local entrance phase')
                checks += 1
                gauges[stream] = QZERO
            if record['reverse']:
                shear(2 * pair, 2 * pair + 1, -1)
            else:
                shear(2 * pair + 1, 2 * pair, 1)
            for side in range(2):
                gauges[2 * pair + side] = level(stage, side, q)
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                stream = 2 * event['pair'] + side
                require(child not in prefixes, 'duplicate child slot')
                require(gauges[stream] == level(event['from_level'], side, q), 'idle entrance phase')
                record = recipe['idle_children'][child]
                require(record['rank'] == len(record['orthogonal_axes']), 'child rank')
                gauges[stream] = qadd(gauges[stream], qsum(record['orthogonal_axes'], record['translation_after']))
                require(gauges[stream] == level(event['to_level'], side, q), 'idle exact phase including translation')
                checks += 2
                prefixes[child] = {'stream': stream, 'prefix': [list(row) for row in matrix],
                                   'history': list(events)}
                events.append(('slot', child, stream))
        elif kind == 'bridge':
            d, s, c = event['dst'], event['src'], event['coefficient']
            require(type(c) is int, 'integer bridge')
            shear(2 * d, 2 * s, c)
            shear(2 * s + 1, 2 * d + 1, -c)
        elif kind == 'terminal_Y_translations':
            for pair in event['pairs']:
                gauges[2 * pair + 1] = qadd(gauges[2 * pair + 1], qscale(parity_form(q), 2))
        elif kind == 'terminal':
            require(event['pairs'] == 4, 'four pairs')
            for pair in range(4):
                gauges[2 * pair], gauges[2 * pair + 1] = gauges[2 * pair + 1], gauges[2 * pair]
            scalar_action(matrix, ('terminal',))
            events.append(('terminal',))
        else:
            require(kind in ('bank_padding_cover_sweep', 'translate_every_live_family'), 'unknown event')
    all_phase = ((1,) * DIM, 0)
    require(gauges == [qadd(all_phase, entry) for entry in initial], 'global target phase')
    require(matrix == identity(), 'full signed scalar controller identity')
    require(sorted(prefixes) == list(range(20)), 'twenty actual slots')
    return {'events': events, 'prefixes': prefixes, 'phase_identities': checks + 8,
            'initial': initial, 'q': q}


def phase_edits(moves):
    edits = defaultdict(list)
    for donor, receiver, axis in moves:
        require(type(donor) is type(receiver) is type(axis) is int, 'integer move schema')
        require(0 <= donor < 20 and 0 <= receiver < 20 and donor != receiver, 'distinct slots')
        require(0 < axis < (1 << DIM), 'nonzero 73-bit axis')
        edits[donor].append((axis, -1))
        edits[receiver].append((axis, 1))
    return edits


def row_basis(vectors):
    """Independent linear forms and coordinates of every requested form."""
    pivots, basis = {}, []
    for original in vectors:
        value, coordinates = original, 0
        for pivot in sorted(pivots, reverse=True):
            row, mask = pivots[pivot]
            if value >> pivot & 1:
                value ^= row
                coordinates ^= mask
        if value:
            index = len(basis)
            basis.append(original)
            pivots[value.bit_length() - 1] = value, coordinates ^ (1 << index)
    result = {}
    for original in vectors:
        value, mask = original, 0
        for pivot in sorted(pivots, reverse=True):
            row, coordinates = pivots[pivot]
            if value >> pivot & 1:
                value ^= row
                mask ^= coordinates
        require(value == 0, 'linear form reconstruction')
        result[original] = mask
    return basis, result


def normalized_replay(normal, edits, values, repair=False):
    result = identity()
    for event in normal['events']:
        if event[0] == 'slot':
            _, child, stream = event
            phase = sum(sign * values[axis] for axis, sign in edits.get(child, ()))
            scale_row(result, stream, UNITS[phase % 4])
        else:
            scalar_action(result, event)
    if repair:
        # Apply the literal inverse event sequence to compute the inverse
        # discrepancy. No phase/translation is dropped and no zero dirt assumed.
        inverse = identity()
        for event in reversed(normal['events']):
            if event[0] == 'slot':
                _, child, stream = event
                phase = -sum(sign * values[axis] for axis, sign in edits.get(child, ()))
                scale_row(inverse, stream, UNITS[phase % 4])
            else:
                scalar_action(inverse, event, inverse=True)
        require(matmul(inverse, result) == identity(), 'exact inverse correction')
        return result, inverse
    return result


def tensor_phase_group(axes, max_rank=12, max_states=65536):
    """Every phase vector achievable by some positive tensor multiplicity.

    One tensor factor contributes (χ_a(x))_a in Z4^J. The finite additive
    subgroup generated by these vectors is exactly their nonnegative monoid,
    because each generator has order dividing four. No finite-only minimal
    polynomial (C-I)(C-iI)=0 is silently lifted to arbitrary tensor powers.
    """
    basis, coordinates = row_basis(axes)
    require(len(basis) <= max_rank, 'unexhausted active subspace')
    zero = (0,) * len(axes)
    states = {zero}
    for assignment in range(1 << len(basis)):
        generator = tuple((assignment & coordinates[axis]).bit_count() % 2 for axis in axes)
        if generator in states:
            continue
        enlarged = {tuple((a + step * b) % 4 for a, b in zip(state, generator))
                    for state in states for step in range(4)}
        require(len(enlarged) <= max_states, 'unexhausted tensor phase group: fail closed at state cap')
        states = enlarged
    return sorted(states)


def exhaustive(normal, moves, max_rank=12, force_tensor=False):
    edits = phase_edits(moves)
    axes = sorted({axis for pairs in edits.values() for axis, _ in pairs})
    basis, coordinates = row_basis(axes)
    require(len(basis) <= max_rank, 'unexhausted active subspace: fail closed above configured rank cap')
    changed, first, maximum = 0, None, 0
    for character in range(1 << len(basis)):
        values = {axis: (character & mask).bit_count() % 2 for axis, mask in coordinates.items()}
        matrix = normalized_replay(normal, edits, values)
        differences = [[i, j, list(matrix[i][j]), list(identity()[i][j])]
                       for i in range(N) for j in range(N) if matrix[i][j] != identity()[i][j]]
        if differences:
            changed += 1
            maximum = max(maximum, len(differences))
            if first is None:
                first = {'active_assignment': character, 'entry_differences': differences}
    tensor_changed, tensor_count, tensor_first = None, None, None
    if changed == 0 or force_tensor:
        states = tensor_phase_group(axes, max_rank)
        tensor_count, tensor_changed = len(states), 0
        for values_tuple in states:
            matrix = normalized_replay(normal, edits, dict(zip(axes, values_tuple)))
            if matrix != identity():
                tensor_changed += 1
                if tensor_first is None:
                    tensor_first = list(values_tuple)
    admitted = changed == 0 and tensor_changed == 0
    return {'admitted': admitted, 'independent_active_forms': list(map(str, basis)),
            'all_active_characters': 1 << len(basis), 'nonidentity_characters': changed,
            'maximum_changed_entries': maximum, 'first_counterexample': first,
            'all_2_to_73_characters_decided': True,
            'uniform_tensor_operator_admitted': admitted,
            'tensor_phase_states_exhausted': tensor_count,
            'tensor_nonidentity_states': tensor_changed,
            'first_tensor_counterexample': tensor_first,
            'tensor_scope': 'All positive tensor multiplicities of the declared eight-stream phase/scalar network; all-size native cost and precision admission remain separate.'}


def import_dense():
    spec = importlib.util.spec_from_file_location('read_only_independent_dense', DENSE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dense_check(template, recipe, normal, moves):
    dense = import_dense()
    original = {child: list(map(int, record['orthogonal_axes']))
                for child, record in enumerate(recipe['idle_children'])}
    final = {child: list(axes) for child, axes in original.items()}
    for donor, receiver, axis in moves:
        require(axis in final[donor] and axis not in final[receiver], 'literal full-child axis move')
        final[donor].remove(axis)
        final[receiver].append(axis)
    edits = phase_edits(moves)
    active = sorted({axis for _, _, axis in moves})
    characters = sorted(set([0, 1, 11, (1 << DIM) - 1, int(recipe['q'])] + active
                            + [a ^ b for a in active for b in active]))
    checked = 0
    for character in characters:
        context = {'template': template, 'recipe': recipe}
        direct = dense.identity()
        for event in template['execution_schedule']:
            if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
                continue
            for matrix in dense.event_matrices(event, context, final, character):
                direct = dense.multiply(matrix, direct)
        values = {axis: (axis & character).bit_count() % 2 for axis in active}
        normalized = normalized_replay(normal, edits, values)
        qbit = (character & int(recipe['q'])).bit_count() % 2
        predicted = [list(row) for row in normalized]
        # D_final N D_initial^-1 = C_all D_initial N D_initial^-1.
        for i in range(N):
            scale_row(predicted, i, UNITS[(character.bit_count() + (qbit if i % 2 == 0 else 0)) % 4])
            for j in range(N):
                predicted[i][j] = gmul(predicted[i][j], UNITS[(-qbit if j % 2 == 0 else 0) % 4])
        require(predicted == direct, 'independent dense / gauge disagreement')
        checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--moves', type=Path, help='admit this literal overlay; default is self-test')
    parser.add_argument('--output', type=Path, default=HERE / 'FULL-OPERATOR.json')
    parser.add_argument('--max-rank', type=int, default=12)
    args = parser.parse_args()
    authenticate()
    template, phases = read(TEMPLATE), read(PHASES)
    require(phases['m'] == 73 and len(phases['recipes']) == 112, 'source dimensions')
    normals = [normalize(template, recipe) for recipe in phases['recipes']]
    require(all(n['events'] == normals[0]['events'] for n in normals), 'port-independent normalized graph')
    baseline = exhaustive(normals[0], [], args.max_rank)
    require(baseline['admitted'], 'valid baseline admission')
    source = read(args.moves if args.moves else MOVES)
    require(source['columns'] == ['replica', 'port', 'donor_child', 'receiver_child', 'axis'], 'move columns')
    groups = defaultdict(list)
    for owner, port, donor, receiver, axis in source['moves']:
        require(type(owner) is type(port) is int and 0 <= owner < 740 and 0 <= port < 112, 'owner/port')
        groups[owner, port].append((donor, receiver, int(axis)))
    reports = []
    for (owner, port), moves in sorted(groups.items()):
        check = exhaustive(normals[port], moves, args.max_rank, force_tensor=(args.moves is None))
        reports.append({'owner': owner, 'port': port, 'moves': len(moves), **check})
        # Exact rejection needs one actual direct summand; accepting requires
        # exhausting every nonempty group. Never accept an omitted group.
        if not check['admitted']:
            break
    admitted = all(r['admitted'] for r in reports)
    literal = groups.get((0, 0), [])
    agreement = dense_check(template, phases['recipes'][0], normals[0], literal)
    if args.moves is None:
        require(not admitted and reports[0]['owner'] == reports[0]['port'] == 0, 'actual prior MOVES rejection')
    receipt = {
        'status': ('ADMITTED_EXACT_FOURIER_OPERATOR' if admitted else 'REJECTED_CHANGED_EXACT_FOURIER_OPERATOR')
                  if args.moves else 'PASS_FAIL_CLOSED_FULL_OPERATOR_SELF_TEST',
        'candidate_admitted': admitted, 'baseline_admitted': baseline['admitted'],
        'baseline_ports_proved_symbolically': len(normals),
        'exact_Z4_polynomial_identities': sum(n['phase_identities'] for n in normals),
        'baseline_all_2_to_73_characters': True,
        'baseline_uniform_tensor_operator': True,
        'normalization': 'P_t=D_t M_t D_initial^-1; arbitrary character phase polynomials checked exactly at every scalar edge and idle endpoint',
        'complete_signed_scalar_events': normals[0]['events'],
        'overlay_total_groups': len(groups), 'overlay_total_moves': len(source['moves']),
        'overlay_groups_decided': reports,
        'remaining_groups_required_after_rejection': False,
        'independent_dense_agreement_characters': agreement,
        'scope': 'Complete eight-stream canonical Fourier operator on arbitrary dirty inputs, including global phase. The active-form quotient is exhaustive for all characters; positive admission also exhausts the generated Z4 phase subgroup for every tensor multiplicity. Pinned hosted chronology justifies collapsing each original child. Local canonical endpoint identities, local native admission and all-size recurrence interfaces are retained obligations.',
        'not_claimed': ['all-size native admission of a proposed correction', 'new supplier or kappa',
                        'arbitrary changed chronology or changed local endpoint interface'],
        'input_files': {str(p.relative_to(REPO)): sha(p) for p in PINS},
        'source_sha256': sha(Path(__file__)),
    }
    if args.moves:
        receipt['candidate_file'] = str(args.moves)
        receipt['candidate_sha256'] = sha(args.moves)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(receipt['status'], 'symbolic_ports', len(normals), 'groups', len(groups), 'dense', agreement)
    return 0 if args.moves is None or admitted else 1


if __name__ == '__main__':
    raise SystemExit(main())
