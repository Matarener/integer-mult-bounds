"""Check a pending-sum trace without a predecessor implementation.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained NOTICE files identify the construction and its predecessors.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def combine(left, right, coefficient=Q(1)):
    result = dict(left)
    for column, value in right.items():
        total = result.get(column, 0) + coefficient * value
        if total:
            result[column] = total
        else:
            result.pop(column, None)
    return result


def scalar(rows, event):
    op, dst = event[:2]
    if op in ('INIT', 'CLEAR'):
        rows[dst] = {}
    elif op == 'SCALE':
        rows[dst] = {k: Q(event[-2]) * v for k, v in rows[dst].items()}
    elif op == 'COPY':
        need(not rows[dst], 'COPY must start with zero')
        rows[dst] = {k: Q(event[-2]) * v for k, v in rows[event[2]].items()}
    elif op == 'ADD':
        rows[dst] = combine(rows[dst], rows[event[2]], Q(event[-2]))
    else:
        need(op == 'MOVE', 'Known operation')


def shape(event):
    """Remove only the frame label from a scalar operation."""
    return tuple(event[:-1])


def groups(before, after):
    first = before['public'] + before['owned_fields']
    last = after['public'] + after['owned_fields']
    need(after['public'] == before['public'] and last > first, 'Added owned roles only')
    result = {}
    for slot in range(first, last):
        uses = [(i, e) for i, e in enumerate(after['program'])
                if e[1] == slot or (e[0] in ('ADD', 'COPY') and e[2] == slot)]
        need(len(uses) >= 6, 'Complete pending-sum lifetime')
        init, *middle, move, delivery, clear = uses
        need(init[1][:2] == ['INIT', slot] and clear[1][:2] == ['CLEAR', slot],
             'Fresh owned sum and final erasure')
        need(all(e[0] == 'ADD' and e[1] == slot for _, e in middle),
             'Only declared sum components')
        a, b = init[1][2], clear[1][2]
        need(move[1] == ['MOVE', slot, a, b, True], 'One directed sum query')
        d = delivery[1][1]
        need(d < before['public'] and delivery[1] == ['ADD', d, slot, '1', b],
             'One unit delivery to the public destination')
        need(all(e[-1] == a and e[2] < first for _, e in middle),
             'Original source operands at the sum frame')
        for i in range(init[0] + 1, delivery[0]):
            e = after['program'][i]
            need(e[1] != d and not (e[0] in ('ADD', 'COPY') and e[2] == d),
                 'No observation or change of a pending destination')
        result[slot] = {'destination': d, 'frame_before': a, 'frame_after': b,
                        'init': init[0], 'adds': [i for i, _ in middle],
                        'move': move[0], 'delivery': delivery[0], 'clear': clear[0]}
    need(len({g['destination'] for g in result.values()}) == len(result),
         'Distinct audited destinations')
    return result


def trace(before, after):
    """Match every scalar read and the exact pending-value relation."""
    blocks = groups(before, after)
    n = before['public'] + before['owned_fields']
    old = [{i: Q(1)} for i in range(n)]
    new = [{i: Q(1)} for i in range(after['public'] + after['owned_fields'])]
    pending, matched, observed, copies = {}, 0, 0, 0
    source_events = [(i, e) for i, e in enumerate(before['program']) if e[0] != 'MOVE']
    digest = sha256()
    original_updates = {slot: [] for slot in blocks}

    def equal_role(role):
        value = dict(new[role])
        for slot, destination in pending.items():
            if destination == role:
                value = combine(value, new[slot])
        need(old[role] == value, 'Exact pending-value relation')

    for index, event in enumerate(after['program']):
        op, role = event[:2]
        if op == 'MOVE':
            continue
        if role in blocks and op == 'INIT':
            scalar(new, event)
            pending[role] = blocks[role]['destination']
            equal_role(pending[role])
            continue
        if role in blocks and op == 'CLEAR':
            need(role not in pending, 'Delivery must precede erasure')
            scalar(new, event)
            continue
        if op == 'ADD' and event[2] in blocks:
            slot = event[2]
            need(pending.pop(slot, None) == role, 'Deliver one live pending sum')
            scalar(new, event)
            equal_role(role)
            continue
        need(matched < len(source_events), 'No extra scalar operation')
        original_index, original = source_events[matched]
        rewritten = list(event)
        if role in blocks:
            need(index in blocks[role]['adds'] and role in pending, 'Declared live component')
            rewritten[1] = pending[role]
            original_updates[role].append(original_index)
        need(shape(original) == shape(rewritten), 'Entire original scalar sequence')
        if op in ('ADD', 'COPY'):
            src = event[2]
            need(old[src] == new[src], 'Same value at every actual source read')
            observed += 1
            if op == 'COPY':
                copies += 1
                data = [original_index, src, [[k, str(v)] for k, v in sorted(old[src].items())]]
                digest.update(json.dumps(data, separators=(',', ':')).encode() + b'\n')
        if op == 'SCALE':
            need(old[role] == new[role], 'Same value at a scale observation')
            observed += 1
        scalar(old, original)
        scalar(new, event)
        equal_role(rewritten[1])
        matched += 1
    need(matched == len(source_events) and not pending, 'Complete matched trace and delivery')
    need(old == new[:n] and all(not row for row in new[n:]), 'All old rows and new dirty returns')
    for slot, indices in original_updates.items():
        need(len(indices) >= 2, 'At least two original updates')
        d = blocks[slot]['destination']
        for i in range(indices[0], indices[-1] + 1):
            e = before['program'][i]
            need(not (e[0] in ('ADD', 'COPY') and e[2] == d), 'No old pending-destination read')
            need(e[1] != d or (i in indices and e[0] == 'ADD'), 'Only selected old writes')
        blocks[slot]['original_updates'] = indices
    return {'groups': blocks, 'matched_scalar_events': matched,
            'source_observations': observed, 'old_copy_values': copies,
            'copy_value_sha256': digest.hexdigest(), 'old_columns': n, 'new_columns': len(new)}


def subspaces(word):
    result = []
    for basis in word['frames']:
        space = {0}
        for vector in basis:
            need(type(vector) is int and 0 < vector < 512 and vector not in space,
                 'Independent nine-axis frame basis')
            space |= {x ^ vector for x in tuple(space)}
        result.append(frozenset(space))
    return result


def inventory(word):
    """Recount the framed word and check every formal input coefficient."""
    p, owned = word['public'], word['owned_fields']
    rows = [{i: Q(1)} for i in range(p + owned)]
    frames = subspaces(word)
    state = word['initial'][:] + [None] * owned
    active, paid, peak, births, scalar_cost = set(), Counter(), 0, 0, 0
    for event in word['program']:
        op, d = event[:2]
        need(type(d) is int and 0 <= d < len(rows), 'Actual destination')
        if op == 'INIT':
            need(d >= p and d not in active and 0 <= event[2] < len(frames), 'Owned birth')
            active.add(d)
            births += 1
            peak = max(peak, len(active))
            state[d] = event[2]
            scalar_cost += 2
        elif op == 'CLEAR':
            need(d in active and state[d] == event[2], 'Owned return at actual frame')
            active.remove(d)
            state[d] = None
            scalar_cost += 2
        elif op == 'MOVE':
            _, _, a, b, reverse = event
            need(type(reverse) is bool and state[d] == a and (d in active) == reverse,
                 'Actual query source and ownership')
            need(frames[b] < frames[a] if reverse else frames[a] < frames[b],
                 'Proper nested native direction')
            paid[abs(len(word['frames'][b]) - len(word['frames'][a]))] += 1
            state[d] = b
        else:
            need(op in ('ADD', 'COPY', 'SCALE') and state[d] == event[-1], 'Actual scalar frame')
            q = Q(event[-2])
            num, den = abs(q.numerator), q.denominator
            need(q != 0 and den & (den - 1) == 0 and abs(q) + 1 < 2**16, 'Bounded dyadic coefficient')
            if op == 'SCALE':
                need(num & (num - 1) == 0, 'Unit dyadic scale')
                scalar_cost += 2 * (abs(num.bit_length() - den.bit_length()) + int(q < 0))
            else:
                s = event[2]
                need(0 <= s < len(rows) and s != d and state[s] == state[d], 'Common source frame')
                if op == 'COPY':
                    need(d in active and not rows[d], 'Owned zero COPY destination')
                scalar_cost += 2 * (3 + num.bit_length() - 1 + num.bit_count() + den.bit_length() - 1)
        scalar(rows, event)
    need(not active and state[:p] == word['final'], 'Complete frame and ownership return')
    live = set(word['live'])
    for i, row in enumerate(rows):
        want = {i: Q(1)} if i < p else {}
        if i - 112 in live:
            want[i - 112] = Q(1)
        need(row == want, 'Every public and dirty input coefficient')
    main = live | {r + 112 for r in live}
    helpers = Counter()
    for r in range(p):
        if r not in main:
            a, b = word['initial'][r], word['final'][r]
            need(frames[a] < frames[b], 'Independent nested helper target')
            helpers[len(word['frames'][b]) - len(word['frames'][a])] += 1
    need(len(live) == len(word['ports']) == 104 and len(main) == 208, 'Fixed main interface')
    return {'paid': dict(paid), 'helpers': dict(helpers), 'public_inputs': p,
            'owned_fields': owned, 'owned_lifetimes': births, 'peak_owned_fields': peak,
            'real_scalar_allowance': scalar_cost, 'endpoint_coefficients': len(rows)**2,
            'paid_rank_mass': sum(k*v for k, v in paid.items())}


def billing(word, counted, published):
    """Use the pinned p16/a7 controller contract; recount every recursive term."""
    p = Counter({k: 18*v for k, v in counted['paid'].items()})
    t = Counter({k: 18*v for k, v in counted['helpers'].items()})
    p[1] += 15*104
    t[145] += 208
    idles, main = Counter(), Counter({145: 208})
    for length in (7, 8):
        for j in range(1, length + 1):
            rank = 8*(j + 1)
            p[rank] += 208
            idles[rank] += 208
            t[rank + 1] += 208
            main[rank + 1] += 208
    c = published['complete_cost']
    need(dict(p) == {int(k): v for k, v in c['paid'].items()}, 'Full paid invoice')
    need(dict(t) == {int(k): v for k, v in c['targets'].items()}, 'Full target invoice and debits')
    physical = published['physical_caller']
    need(dict(idles) == {int(k): v for k, v in physical['whole_idle_jobs'].items()}
         and dict(main) == {int(k): v for k, v in physical['main_targets'].items()}, 'Inherited caller inventory')
    normalizers, adapters = 2*sum(counted['helpers'].values()), 2*len(word['live'])
    route = (sum(counted['paid'].values()) + normalizers + adapters + 4*104
             + 4*counted['owned_lifetimes'])*1000
    need(published['native']['helper_normalizers'] == normalizers
         and published['native']['main_adapters'] == adapters, 'All normalizer and adapter occurrences')
    need(c['nonrecursive']['local_scalar'] == counted['real_scalar_allowance']
         and c['nonrecursive']['local_routes'] == route, 'Positive source tariff inventory')
    need(sum(p.values()) == c['paid_calls'] and sum(t.values()) == c['productive_fields'], 'Full counts')
    surplus = sum(k*v for k, v in t.items()) - sum(k*v for k, v in p.items())
    need(surplus == c['rank_mass_surplus'] == 760, 'Full rank surplus')
    return {'paid': dict(p), 'targets': dict(t), 'paid_calls': sum(p.values()),
            'targets_count': sum(t.values()), 'rank_surplus': surplus,
            'local_scalar_allowance': counted['real_scalar_allowance'], 'local_route_allowance': route}
