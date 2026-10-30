"""Exact coupled-owned-block boundary certificate for the frozen PR5580 word.

The theorem is a fixed 41-public-coordinate boundary theorem. It does not
charge original input frames as though they were eight-dimensional registers.
"""
from fractions import Fraction as Q
from collections import Counter
import copy


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(row, source, coefficient):
    result = dict(row)
    for key, value in source.items():
        out = result.get(key, Q(0)) + coefficient * value
        if out:
            result[key] = out
        else:
            result.pop(key, None)
    return result


def apply(rows, event):
    op, dst = event[:2]
    if op == 'MOVE':
        return
    if op in ('INIT', 'CLEAR'):
        rows[dst] = {}
    elif op == 'ADD':
        rows[dst] = add(rows[dst], rows[event[2]], Q(event[3]))
    elif op == 'SCALE':
        rows[dst] = {key: Q(event[2])*value for key, value in rows[dst].items()}
    elif op == 'COPY':
        rows[dst] = {key: Q(event[3])*value for key, value in rows[event[2]].items()}
    else:
        raise ValueError('unknown scalar opcode')


def rank(rows):
    pivots = {}
    for row in rows:
        row = dict(row)
        while row:
            col = min(row)
            if col not in pivots:
                a = row[col]
                pivots[col] = {key: value/a for key, value in row.items()}
                break
            row = add(row, pivots[col], -row[col])
    return len(pivots)


def span(basis):
    result = {0}
    for vector in basis:
        result |= {x ^ vector for x in tuple(result)}
    need(len(result) == 1 << len(basis), 'binary basis independent')
    return result


def observations_rank(observations):
    return rank([{int(k):Q(v) for k,v in row.items()} for row in observations])


def verify(word):
    public, events, frames = word['public'], word['program'], word['frames']
    need(public == 735, 'frozen public inventory')
    n = public+8
    copies = [(i,e) for i,e in enumerate(events) if e[0] == 'COPY']
    need([e[1] for _,e in copies] == list(range(735,743)), 'eight owned producers')
    sources = [e[2] for _,e in copies]
    need(sources == [173,151,146,133,256,92,9,240], 'frozen source order')
    start = next(i for i,e in enumerate(events) if e[0] == 'INIT')
    stop = 1+max(i for i,e in enumerate(events) if e[0] == 'CLEAR')
    block = events[start:stop]
    deliveries = [(start+i,e) for i,e in enumerate(block) if e[0] == 'ADD']
    recipients = [e[1] for _,e in deliveries]
    need(len(recipients) == len(set(recipients)) == 33, '33 distinct recipients')
    roles = sources+recipients
    need(len(set(roles)) == 41, '41 distinct public boundary coordinates')
    need(all(e[1] in roles or e[1] >= public for e in block), 'no outside destination')
    need(all(e[2] in roles or e[2] >= public for e in block if e[0] in ('ADD','COPY')),
         'no outside public read')

    rows = [{i:Q(1)} for i in range(public)]+[{} for _ in range(8)]
    current = list(word['initial'])+[None]*8
    spans = [span(f) for f in frames]
    active = set()
    entry, exit_frames, prefix = None, None, None
    for i,e in enumerate(events):
        if i == start:
            entry = list(current)
            prefix = [dict(rows[r]) for r in roles]
        op,r = e[:2]
        if op == 'MOVE':
            need(current[r] == e[2] and e[4] == (r in active), 'MOVE frame and ownership')
            need(spans[e[3]] < spans[e[2]] if e[4] else spans[e[2]] < spans[e[3]], 'nested MOVE direction')
            current[r] = e[3]
        elif op == 'INIT':
            need(r >= public and r not in active, 'fresh owned field')
            current[r] = e[2]
            active.add(r)
        elif op == 'CLEAR':
            need(r in active and current[r] == e[2], 'owned CLEAR frame')
            current[r] = None
            active.remove(r)
        else:
            need(Q(e[-2]) != 0 and current[r] == e[-1], 'nonzero scalar at current chart')
            if op in ('ADD','COPY'):
                need(e[2] != r and current[e[2]] == current[r], 'common scalar chart')
            if op == 'COPY':
                need(r in active and not rows[r], 'COPY into zero owned field')
        apply(rows,e)
        if i+1 == stop:
            exit_frames = list(current)
    need(not active and current[:public] == word['final'], 'full frame exit')
    for r,row in enumerate(rows):
        expected = {r:Q(1)} if r < public else {}
        if r-112 in word['live']:
            expected[r-112] = Q(1)
        need(row == expected, 'full arbitrary-input scalar exit')
    need(rank(prefix) == 41, 'independent actual local entry coordinates')

    local = [{} for _ in range(n)]
    for j,r in enumerate(roles):
        local[r] = {j:Q(1)}
    for e in block:
        apply(local,e)
    need(all(local[r] == {j:Q(1)} for j,r in enumerate(sources)), 'all eight producers unchanged')
    need(all(local[r] == {} for r in range(public,n)), 'all private exits zero')
    need(all(len(frames[entry[r]]) == len(frames[exit_frames[r]]) == 8 for r in sources),
         'producer entry and exit dimensions eight')
    target_sources = {}
    for j,r in enumerate(recipients,8):
        need(local[r].get(j) == 1 and len(local[r]) == 2, 'recipient keeps arbitrary input plus one producer')
        source = next(k for k in local[r] if k != j)
        need(source < 8 and local[r][source] != 0, 'nonzero original producer transfer')
        target_sources[r] = source
    observed_roles = []
    observed = []
    for s in range(8):
        role = next((r for r in recipients if target_sources[r] == s and len(frames[exit_frames[r]]) == 1), None)
        need(role is not None, 'one one-dimensional observation per producer')
        observed_roles.append(role)
        observed.append({str(k):str(v) for k,v in local[role].items() if k < 8})
    need(observations_rank(observed) == 8, 'eight independent low-dimensional producer observations')
    for k in range(2,9):
        need(all(len(frames[entry[r]]) >= k for r in sources), 'no producer coordinate initially below threshold')
        need(all(len(frames[exit_frames[r]]) < k for r in observed_roles), 'all observations below threshold')

    suffix = [{} for _ in range(n)]
    for j,r in enumerate(roles):
        suffix[r] = {j:Q(1)}
    for e in events[stop:]:
        apply(suffix,e)
    need(rank(suffix[:public]) == 41, 'fixed suffix observes every local public coordinate')

    public_hist, owned_hist = Counter(), Counter()
    threshold_crossings = {k:0 for k in range(2,9)}
    for e in block:
        if e[0] != 'MOVE':
            continue
        a,b = len(frames[e[2]]),len(frames[e[3]])
        (owned_hist if e[4] else public_hist)[abs(a-b)] += 1
        if e[4]:
            for k in threshold_crossings:
                threshold_crossings[k] += b < k <= a
    need(public_hist == {1:31}, 'source public histogram 31H1')
    need(owned_hist == {7:7,1:2,2:1,3:1}, 'source owned histogram 7H7+2H1+H2+H3')
    need(all(count == 8 for count in threshold_crossings.values()), 'source attains each threshold crossing rank')
    public_rank = sum(len(frames[exit_frames[r]])-len(frames[entry[r]]) for r in roles)
    need(public_rank == 31, 'public entry-exit rank change 31')
    need(all(len(frames[exit_frames[r]])-len(frames[entry[r]]) in (0,1) for r in roles),
         'each physical public field requires at most one rank of ascent')
    corrupted = copy.deepcopy(observed)
    corrupted[-1] = dict(corrupted[0])
    need(observations_rank(corrupted) == 7, 'duplicate observation reduces the rank bound')
    return {
        'status':'PASS_JOINT_41_ROLE_OWNED_MOMENT_FLOOR',
        'events_half_open':[start,stop], 'public_roles':roles,
        'sources':sources,'recipients':recipients,
        'prefix_rank':41,'suffix_rank':41,
        'source_entry_dimensions':[len(frames[entry[r]]) for r in sources],
        'observed_roles':observed_roles,'producer_projection_at_observations':observed,
        'threshold_crossing_count':{str(k):v for k,v in threshold_crossings.items()},
        'public_paid_histogram':{str(k):v for k,v in sorted(public_hist.items())},
        'owned_paid_histogram':{str(k):v for k,v in sorted(owned_hist.items())},
        'theorem_floor':'31 H1(t) + 8 H7(t), 0<t<=1',
        'maximum_possible_local_saving':'2 H1(t) + H2(t) + H3(t) - H7(t)',
        'duplicate_observation_scope_control_rank':7,
        'scope':'Fixed 41 independent public entry/exit rows and frames; arbitrary private auxiliaries and cross-block sharing; no outside public side information, changed helper credits or earlier public preparation.',
        'new_bound':False,
    }


