"""Portable independent rational boundary checker for the eight owned blocks.

Only stdlib imports; no side effects on import. The caller supplies the decoded
word and owns source pinning. This is not a complete native/funding verifier.
"""
from fractions import Fraction as Q
import copy

# Literal public boundary specification, independently transcribed from the
# frozen source. Source byte/hash provenance belongs to the caller.
SPECS = {
    735: (173, [704,705,706], ['1/2']*3),
    736: (151, [707,708,733], ['1/2']*3),
    737: (146, [709,732], ['-1/2']*2),
    738: (133, [159,203,148,710,734], ['1/2','-1','-1','-1/2','-1/2']),
    739: (256, [712,713,714,715,716], ['1/4']*5),
    740: (92, [717,718,719,720,721], ['1/4']*5),
    741: (9, [722,723,724,725,726], ['1/4']*5),
    742: (240, [727,728,729,730,731], ['-1/4']*5),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(row, source, coefficient):
    out = dict(row)
    for k, x in source.items():
        value = out.get(k, Q(0)) + coefficient*x
        if value:
            out[k] = value
        else:
            out.pop(k, None)
    return out


def apply(rows, event):
    op, dst = event[:2]
    if op == 'MOVE':
        return
    if op in ('INIT', 'CLEAR'):
        rows[dst] = {}
    elif op == 'SCALE':
        rows[dst] = {k: Q(event[2])*x for k, x in rows[dst].items()}
    elif op == 'COPY':
        rows[dst] = {k: Q(event[3])*x for k, x in rows[event[2]].items()}
    elif op == 'ADD':
        rows[dst] = add(rows[dst], rows[event[2]], Q(event[3]))
    else:
        raise ValueError('unknown scalar event')


def rational_rank(rows):
    pivots = {}
    for row in rows:
        row = dict(row)
        while row:
            p = min(row)
            if p not in pivots:
                divisor = row[p]
                pivots[p] = {k: x/divisor for k, x in row.items()}
                break
            row = add(row, pivots[p], -row[p])
    return len(pivots)


def binary_rank(vectors):
    pivots = {}
    for x in vectors:
        while x:
            p = x.bit_length()-1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def jsonrow(row):
    return {str(k): str(x) for k, x in sorted(row.items())}


def add_hist(hist, degree):
    hist[degree] = hist.get(degree, 0)+1


def verify(w):
    """Check the eight fixed public boundary blocks; return a JSON-safe receipt.

    The input is a decoded WORD object. No input mutation or filesystem access
    occurs. This is not a complete native character or funding verifier.
    """
    events, frames, public = w['program'], w['frames'], w['public']
    n = public+8
    need(public == 735, 'frozen role count')
    intervals = {}
    for owned in range(public, n):
        starts_found = [i for i, e in enumerate(events) if e[:2] == ['INIT', owned]]
        stops_found = [i+1 for i, e in enumerate(events) if e[:2] == ['CLEAR', owned]]
        need(len(starts_found) == len(stops_found) == 1, 'one INIT/CLEAR per owned lifetime')
        start, stop = starts_found[0], stops_found[0]
        need(start < stop, 'INIT before CLEAR')
        intervals[owned] = (start, stop)
    need(all(intervals[r][1] == intervals[r+1][0] for r in range(735, 742)), 'consecutive blocks')

    rows = [{i: Q(1)} for i in range(public)]+[{} for _ in range(8)]
    chart = list(w['initial'])+[None for _ in range(8)]
    snapshots = {}
    starts = {x[0]: r for r, x in intervals.items()}
    ends = {x[1]: r for r, x in intervals.items()}
    for i, e in enumerate(events):
        if i in starts:
            snapshots[(starts[i], 'before')] = ([dict(row) for row in rows], list(chart))
        op, dst = e[:2]
        if op == 'INIT':
            need(dst >= public and chart[dst] is None, 'INIT requires inactive private field')
            chart[dst] = e[2]
        elif op == 'MOVE':
            need(chart[dst] is not None and chart[dst] == e[2], 'declared old frame matches active frame')
            need(e[4] == (dst >= public), 'MOVE ownership flag matches role')
            a, b = frames[e[2]], frames[e[3]]
            need(binary_rank(a+b) == max(len(a),len(b)), 'MOVE charts nested')
            need((len(a) >= len(b)) if e[4] else (len(a) <= len(b)), 'MOVE follows ownership direction')
            chart[dst] = e[3]
        elif op == 'CLEAR':
            need(dst >= public and chart[dst] is not None and chart[dst] == e[2], 'CLEAR active private frame')
            chart[dst] = None
        elif op == 'SCALE':
            need(chart[dst] is not None and chart[dst] == e[3], 'SCALE common frame')
        elif op in ('ADD','COPY'):
            need(chart[dst] is not None and chart[e[2]] is not None and chart[dst] == chart[e[2]] == e[4], 'ADD/COPY common frame')
            if op == 'COPY':
                need(dst >= public and rows[dst] == {}, 'COPY requires zero private destination')
        else:
            raise ValueError('unknown opcode')
        apply(rows, e)
        if i+1 in ends:
            snapshots[(ends[i+1], 'after')] = ([dict(row) for row in rows], list(chart))

    results = []
    for owned, (start, stop) in intervals.items():
        block = events[start:stop]
        copies = [e for e in block if e[0] == 'COPY']
        need(len(copies) == 1 and copies[0][1] == owned, 'single source copy')
        source = copies[0][2]
        expected_source, expected_recipients, expected_coefficients = SPECS[owned]
        need(source == expected_source, 'fixed local source role')
        recipients = [e[1] for e in block if e[0] == 'ADD']
        need(recipients == expected_recipients, 'fixed local recipient roles')
        need(len(set(recipients)) == len(recipients), 'one delivery per recipient')
        need(all(e[2] == owned for e in block if e[0] == 'ADD'), 'owned source at deliveries')
        roles = [source]+recipients
        controls = roles+[owned]
        before, entry = snapshots[(owned, 'before')]
        after, exit_frames = snapshots[(owned, 'after')]
        prefix_rank = rational_rank([before[r] for r in roles])
        need(prefix_rank == len(roles), 'public local prefix coordinates independent')
        need(after[source] == before[source], 'source unchanged')
        need(after[owned] == {}, 'owned exit zero')
        need(all(before[r] == after[r] for r in range(public) if r not in recipients),
             'no outside public scalar row changed')
        local = [{} for _ in range(n)]
        for j, r in enumerate(controls):
            local[r] = {j: Q(1)}
        for e in block:
            apply(local, e)
        transfers = {}
        for j, r in enumerate(recipients, 1):
            need(set(local[r]) == {0, j} and local[r][j] == 1, 'exact local delivery form')
            transfers[r] = local[r][0]
            need(transfers[r] == Q(expected_coefficients[j-1]), 'fixed local transfer coefficient')
            need(after[r] == add(before[r], before[source], transfers[r]), 'actual prefix delivery')
        need(local[source] == {0: Q(1)} and local[owned] == {}, 'local source and zero exit')
        suffix = [{} for _ in range(n)]
        for j, r in enumerate(controls):
            suffix[r] = {j: Q(1)}
        for e in events[stop:]:
            apply(suffix, e)
        suffix_rank = rational_rank(suffix[:public])
        need(suffix_rank == len(roles), 'fixed suffix observes every public local coordinate')
        need(all(len(roles) not in row for row in suffix[:public]), 'retired owned has no public suffix influence')
        last_add = max(i for i in range(start, stop) if events[i][0] == 'ADD')
        healthy = [{} for _ in range(n)]
        damaged = [{} for _ in range(n)]
        for j, r in enumerate(controls):
            healthy[r] = damaged[r] = {j: Q(1)}
        for i in range(start, len(events)):
            apply(healthy, events[i])
            if i != last_add:
                apply(damaged, events[i])
        different = [r for r in range(public) if healthy[r] != damaged[r]]
        need(bool(different), 'omitted delivery negative control observed')
        paid, private_paid, public_paid = {}, {}, {}
        for e in block:
            if e[0] == 'MOVE':
                a, b = frames[e[2]], frames[e[3]]
                need(binary_rank(a+b) == max(len(a), len(b)), 'source move charts nested')
                degree = abs(len(a)-len(b))
                add_hist(paid, degree)
                add_hist(private_paid if e[4] else public_paid, degree)
        support = before[source]
        entry_vectors = [v for r in support for v in frames[w['initial'][r]]]
        star = all(len(frames[entry[r]]) == 0 and len(frames[exit_frames[r]]) == 1 for r in recipients)
        if star:
            need(private_paid == {7: 1} and public_paid == {1: len(recipients)}, 'tight uniform star tariff')
            need(all(before[r] == {r: Q(1)} for r in recipients), 'star recipients independent original symbols')
            need(len(frames[entry[source]]) == 8, 'star source dimension eight')
        result = {
            'owned': owned, 'events_half_open': [start, stop], 'source': source,
            'source_role': 'live' if source in w['live'] else 'helper',
            'recipients': recipients, 'transfers_from_source': {str(r): str(c) for r, c in transfers.items()},
            'entry_frames': {str(r): entry[r] for r in roles},
            'exit_frames': {str(r): exit_frames[r] for r in roles},
            'entry_dimensions': {str(r): len(frames[entry[r]]) for r in roles},
            'exit_dimensions': {str(r): len(frames[exit_frames[r]]) for r in roles},
            'local_matrix': [jsonrow(local[r]) for r in controls],
            'actual_prefix_rank': prefix_rank, 'public_suffix_rank': suffix_rank,
            'owned_exit_zero': True, 'owned_public_suffix_column_zero': True,
            'source_prefix_nonzeros': len(support), 'source_entry_support_span_dimension': binary_rank(entry_vectors),
            'support_to_recipient_exit_dimension_gaps': {str(r): binary_rank(entry_vectors+frames[exit_frames[r]])-len(frames[exit_frames[r]]) for r in recipients},
            'local_paid_histogram': paid, 'public_paid_histogram': public_paid,
            'owned_paid_histogram': private_paid, 'omitted_delivery_event': last_add,
            'corruption_changed_public_outputs': different,
            'tight_fixed_boundary_star_theorem_applies': star,
            'no_gain_scope': ('Exact local public boundary charts and map; arbitrary private zero auxiliaries; no outside side information, changed productive targets or credits.' if star else 'No tight local cost floor claimed: delivery charts have several levels.')}
        results.append(result)
    need(sum(r['tight_fixed_boundary_star_theorem_applies'] for r in results) == 7, 'seven tight star blocks')
    result = {'status': 'PASS_EIGHT_OWNED_BOUNDARIES_SEVEN_TIGHT_STARS',
              'lifetimes': results, 'new_kappa': False,
              'global_claim_excluded': 'Per-row owned-preparation floors cannot be added when private work or lost subspaces are shared.'}
    return result


def mutation_controls(word):
    """Require rejection of three local semantic corruptions of a passing word."""
    verify(word)
    cases = []
    for name in ('wrong_delivery_sign', 'zeroed_owned_producer', 'wrong_delivery_frame'):
        damaged = copy.deepcopy(word)
        events = damaged['program']
        if name == 'zeroed_owned_producer':
            event = next(e for e in events if e[:2] == ['COPY',735])
            event[3] = '0'
        else:
            event = next(e for e in events if e[:3] == ['ADD',704,735])
            if name == 'wrong_delivery_sign':
                event[3] = '-1'
            else:
                event[4] = 559
        try:
            verify(damaged)
        except ValueError as error:
            cases.append({'mutation': name, 'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError('semantic corruption escaped: '+name)
    return cases
