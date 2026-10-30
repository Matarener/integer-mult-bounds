"""Independent contact-path accounting and sparse Laurent replay.

Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor Python module is imported. This checks a finite invoice, not
physical Clifford lowering, arbitrary-column native action or admission.
"""
from collections import Counter
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


class Frames:
    def __init__(self, frames):
        self.frames = frames
        self.dimensions = []
        self.cache = {}
        for basis in frames:
            require(all(type(x) is int and 0 < x < 512 for x in basis),
                    'invalid nine-axis frame vector')
            rank = binary_rank(basis)
            require(rank == len(basis), 'dependent frame basis')
            self.dimensions.append(rank)

    def width(self, before, after):
        require(type(before) is int and type(after) is int and
                0 <= before < len(self.frames) and 0 <= after < len(self.frames),
                'invalid frame index')
        if before == after:
            return 0
        key = before, after
        if key not in self.cache:
            delta = self.dimensions[after] - self.dimensions[before]
            require(delta > 0 and binary_rank(self.frames[before] + self.frames[after])
                    == self.dimensions[after], 'nonascending or nonnested contact path')
            self.cache[key] = delta
        return self.cache[key]


def scalar_roles(gate):
    require(gate[0] in ('add', 'copy', 'scale', 'clear'), 'unknown native scalar')
    return gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]


def patched_endpoints(canonical, changes, frames):
    starts, ends = list(canonical['start']), list(canonical['final'])
    require(len(starts) == len(ends) == 632, 'persistent field inventory')
    for key, values in (('entrances', starts), ('exits', ends)):
        seen = set()
        for role, old, new in changes[key]:
            require(type(role) is int and 224 <= role < 632 and role not in seen,
                    'duplicate or nonhelper boundary patch')
            require(values[role] == old, 'boundary old-frame pin')
            require(type(new) is int and 0 <= new < len(frames.frames), 'invalid new boundary')
            seen.add(role)
            values[role] = new
    helpers = Counter()
    for role in range(224, 632):
        width = frames.width(starts[role], ends[role])
        require(width > 0, 'unproductive helper')
        helpers[width] += 1
    return starts, ends, helpers


def audit_orientation(canonical, program, changes, frames):
    starts, ends, helpers = patched_endpoints(canonical, changes, frames)
    patch = {}
    for phase, ordinal, old, new in changes['gates']:
        key = phase, ordinal
        require(key not in patch, 'duplicate scalar-frame patch')
        patch[key] = old, new

    # Extract each role's ordered demands, independently of the emitted climbs.
    paths = [[] for _ in starts]
    original_state = list(canonical['start'])
    original_paid = Counter()
    phase, ordinal = None, 0
    used = set()
    contacts = {}
    centers = []
    warp_dimension_changes = [0] * len(starts)
    event_counts = Counter()
    for position, event in enumerate(program):
        kind = event[0]
        event_counts[kind] += 1
        if kind == 'phase':
            phase, ordinal = event[1], 0
        elif kind == 'climb':
            _, _, role, old, new, declared = event
            require(original_state[role] == old, 'source climb chronology')
            width = frames.width(old, new)
            require(width > 0 and width == declared, 'source climb tariff')
            original_paid[width] += 1
            original_state[role] = new
        elif kind == 'scalar':
            gate, old = event[1:]
            roles = scalar_roles(gate)
            new = old
            if all(role[0] == 'L' for role in roles):
                key = phase, ordinal
                ordinal += 1
                require(key not in contacts, 'repeated phase/ordinal')
                contacts[key] = gate, old
                if key in patch:
                    expected, new = patch[key]
                    require(old == expected, 'scalar old-frame pin')
                    used.add(key)
            for bank, role in roles:
                require(bank in ('L', 'C'), 'unknown native bank')
                if bank == 'L':
                    require(original_state[role] == old, 'source scalar contact')
                    paths[role].append(('contact', new, position))
        elif kind == 'warp':
            _, bank_role, _, old, new = event
            bank, role = bank_role
            require(bank == 'L' and original_state[role] == old, 'source warp contact')
            paths[role].append(('contact', old, position))
            paths[role].append(('warp', new, position))
            warp_dimension_changes[role] += frames.dimensions[new] - frames.dimensions[old]
            original_state[role] = new
        elif kind == 'center':
            centers.append((position, event))
        elif kind not in ('adapter', 'residual_adapter'):
            raise ValueError('unknown native event: ' + kind)
    require(used == set(patch), 'unconsumed scalar-frame patch')
    require(original_state == canonical['final'], 'source final frames')
    require(len(centers) == 16, 'eight complete owned center jobs required')
    # Each adjacent 3+5 pair is one rank-eight job in the source unsplit model.
    for (pos, first), (next_pos, second) in zip(centers[::2], centers[1::2]):
        require(next_pos == pos + 1 and first[1] == second[1] == 0 and
                first[3] == second[2] and sorted((first[4], second[4])) == [3, 5],
                'owned center pair must be contiguous and complete')
        for item in (first, second):
            require(abs(frames.dimensions[item[3]] - frames.dimensions[item[2]]) == item[4],
                    'center dimension tariff')
    original_paid[8] += len(centers) // 2
    paid = Counter({8: len(centers) // 2})
    role_paid = []
    for role, demands in enumerate(paths):
        current = starts[role]
        bill = Counter()
        for kind, target, _ in demands + [('contact', ends[role], len(program))]:
            if kind == 'contact':
                width = frames.width(current, target)
                if width:
                    bill[width] += 1
            current = target
        role_paid.append(bill)
        paid.update(bill)
        # A second, order-independent mass check. Warps are fixed contacts,
        # not newly credited paid climbs; their dimension jumps must be removed.
        telescope = (frames.dimensions[ends[role]] - frames.dimensions[starts[role]]
                     - warp_dimension_changes[role])
        require(sum(width * count for width, count in bill.items()) == telescope,
                'per-role rank mass does not telescope')
    return {'helpers': helpers, 'paid': paid, 'original_paid': original_paid,
            'contacts': contacts, 'role_paid': role_paid, 'events': event_counts,
            'contact_count': sum(len(path) for path in paths)}


def local_invoice(canonical, native, changes):
    frames = Frames(canonical['frames'])
    require(set(native) == {'forward', 'backward'}, 'both native orientations required')
    results = {direction: audit_orientation(canonical, program, changes, frames)
               for direction, program in native.items()}
    forward, backward = results['forward'], results['backward']
    for key in ('helpers', 'paid', 'original_paid', 'role_paid'):
        require(forward[key] == backward[key], 'orientation mismatch: ' + key)
    require(forward['contacts'].keys() == backward['contacts'].keys(),
            'orientation scalar inventories differ')
    for key, (gate, frame) in forward['contacts'].items():
        other, other_frame = backward['contacts'][key]
        if gate[0] == 'add':
            expected = ['add', gate[2], gate[1], -gate[3], gate[4]]
        else:
            require(gate[0] == 'scale', 'unexpected persistent scalar')
            expected = ['scale', gate[1], gate[3], gate[2]]
        require(other == expected and frame == other_frame, 'inverse-transpose scalar correspondence')
    return forward, results


def add_row(target, source, coefficient=1):
    result = dict(target)
    for term, value in source.items():
        result[term] = result.get(term, 0) + coefficient * value
        if not result[term]:
            del result[term]
    return result


def shift_row(row, q=0, stages=(), coefficient=1):
    result = {}
    for term, value in row.items():
        shifted = list(term)
        shifted[1] += q
        for stage in stages:
            shifted[stage + 2] += 1
        key = tuple(shifted)
        result[key] = result.get(key, 0) + coefficient * value
    return {key: value for key, value in result.items() if value}


def identity_rows(size, stages):
    return [{(role, 0) + (0,) * stages: Fraction(1)} for role in range(size)]


def scalar_program(rows, program):
    for event in program:
        op = event[0]
        if op == 'ADD':
            _, dst, src, c = event
            rows[dst] = add_row(rows[dst], rows[src], Fraction(c))
        elif op == 'SCALE':
            _, dst, c = event
            rows[dst] = shift_row(rows[dst], coefficient=Fraction(c))
        elif op == 'SWAP':
            _, dst, src = event
            rows[dst], rows[src] = rows[src], rows[dst]
        else:
            raise ValueError('unknown boundary gate: ' + op)
    return rows


def controller_invoice(controller, helpers, local_paid):
    require(controller['kind'] == 'complex', 'complex controller required')
    pairs = controller['pairs']
    size, stages = 2 * pairs, 2 * pairs + 1
    for side in ('left', 'right'):
        rows = scalar_program(identity_rows(size, stages), controller['boundaries'][side + '_program'])
        matrix = controller['boundaries'][side]
        for i in range(size):
            expected = {(j, 0) + (0,) * stages: Fraction(matrix[i][j])
                        for j in range(size) if Fraction(matrix[i][j])}
            require(rows[i] == expected, 'boundary program/matrix disagreement: ' + side)
    rows = scalar_program(identity_rows(size, stages), controller['boundaries']['right_program'])
    paid, targets, idles = Counter(), Counter(), Counter()
    event_counts = Counter()
    local_stages, query_stages = [], []
    for event in controller['physical_events']:
        op = event[0]
        event_counts[op] += 1
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, backward = event
            require(0 <= stage < stages and 0 <= pair < pairs and type(backward) is bool,
                    'invalid local/query event')
            x, y = 2 * pair, 2 * pair + 1
            if backward:
                x, y = y, x
            rows[y] = add_row(rows[y], shift_row(rows[x], q=1 if backward else -1),
                              -1 if backward else 1)
            if op == 'LOCAL':
                local_stages.append(stage)
                targets.update(helpers)
                paid.update(local_paid)
                for role in (x, y):
                    rows[role] = shift_row(rows[role], stages=(stage,))
            else:
                query_stages.append(stage)
                paid[1] += 112
        elif op == 'IDLE':
            _, pair, active = event
            require(0 <= pair < pairs and active and len(active) == len(set(active)) and
                    all(0 <= s < stages for s in active), 'invalid whole idle event')
            idles[8 * len(active)] += 224
            paid[8 * len(active)] += 224
            for role in (2 * pair, 2 * pair + 1):
                rows[role] = shift_row(rows[role], stages=active)
        elif op == 'ADD':
            _, dst, src, c = event
            rows[dst] = add_row(rows[dst], rows[src], Fraction(c))
        elif op in ('SWAP', 'SIGNED_SWAP'):
            _, x, y = event
            rows[x], rows[y] = rows[y], shift_row(rows[x], coefficient=-1 if op == 'SIGNED_SWAP' else 1)
        else:
            raise ValueError('unknown controller event: ' + op)
    require(sorted(local_stages + query_stages) == list(range(stages)),
            'every controller stage must be present exactly once')
    rows = scalar_program(rows, controller['boundaries']['left_program'])
    diagonal, main = [], Counter()
    for role, row in enumerate(rows):
        require(len(row) == 1, 'controller endpoint is not one monomial')
        (term, coefficient), = row.items()
        require(term[0] == role and coefficient == 1 and term[1] in (-1, 1) and
                all(power in (0, 1) for power in term[2:]), 'invalid diagonal endpoint')
        require(all(not power or stage in local_stages for stage, power in enumerate(term[2:])),
                'thin stage receives productive credit')
        diagonal.append(list(term[1:]))
        main[1 + 8 * sum(term[2:])] += 112
    require(diagonal == controller['diagonal'], 'declared diagonal differs from literal replay')
    targets.update(main)
    return {'targets': targets, 'paid': paid, 'main': main, 'whole_idle': idles,
            'event_counts': event_counts, 'local_stages': local_stages,
            'query_stages': query_stages, 'diagonal': diagonal}
