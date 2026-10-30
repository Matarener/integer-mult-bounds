#!/usr/bin/env python3
"""Finite contact-class cover, without graph/optimizer/predecessor-auditor imports.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
from exact_algebra import literal_replay, programs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/rank7-coupled-586-588-carrier-fold'
MOVABLE = {168: 1196, 150: 772, 56: 802, 115: 1244}
DELETED = {48, 753}
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def span(vectors):
    result = {0}
    for v in vectors:
        require(isinstance(v, int) and 0 <= v < 512, 'invalid F2^9 vector')
        result |= {x ^ v for x in tuple(result)}
    return result


def regs(gate):
    require(gate[0] in ('add', 'scale'), 'unexpected scalar gate')
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def commutes(a, b):
    require(a[0] == 'add' and a[3] != 0, 'expected nonzero movable read')
    d, s = a[1:3]
    if b[0] == 'add':
        e, t = b[1:3]
        require(b[3] != 0 and e != t, 'expected nonzero source transvection')
        return s != e and t != d
    require(b[0] == 'scale', 'unexpected scalar gate')
    return b[1] not in (d, s) or b[2] == b[3]


def classify(w):
    gone = set(MOVABLE.values()) | DELETED
    fixed = [(i, g) for i, g in enumerate(w['B']) if i not in gone]
    gates = {r: ['add', r, 439, -1, 2, []] for r in MOVABLE}
    require(all(commutes(a, b) for a, b in itertools.combinations(gates.values(), 2)),
            'movable reads must commute pairwise')
    require(not any(z[1] in set(MOVABLE) | {439} for z in w['warps']),
            'a native warp touches a movable endpoint')
    require(not any(439 in regs(g) for _, g in fixed), 'unaccounted fixed carrier contact')
    slots, intervals = {}, {}
    for r, at in MOVABLE.items():
        low = high = sum(old < at for old, _ in fixed)
        while low > 0 and commutes(gates[r], fixed[low - 1][1]):
            low -= 1
        while high < len(fixed) and commutes(gates[r], fixed[high][1]):
            high += 1
        contacts = [j for j in range(low, high) if r in regs(fixed[j][1])]
        slots[r] = list(zip([low] + [j + 1 for j in contacts], contacts + [high]))
        intervals[r] = (low, high)
    reps = []
    for choice in itertools.product(*(range(len(slots[r])) for r in MOVABLE)):
        selected = dict(zip(MOVABLE, choice))
        for order in itertools.permutations(MOVABLE):
            previous, cuts = 0, {}
            for r in order:
                lo, hi = slots[r][selected[r]]
                cut = max(previous, lo)
                if cut > hi:
                    break
                cuts[r] = previous = cut
            else:
                reps.append({'order': order, 'cuts': cuts, 'slots': selected})
    require([len(slots[r]) for r in MOVABLE] == [8, 4, 1, 8], 'contact-slot census')
    require(24 * math.prod(map(len, slots.values())) == 6144, 'Cartesian cover')
    require(len(reps) == 1002, 'feasible contact-class census')
    keys = {(tuple(x['slots'].items()), x['order']) for x in reps}
    require(len(keys) == len(reps), 'duplicate contact classes')
    return fixed, gates, intervals, reps


def make_word(original, fixed, gates, rep):
    inserted = {}
    for r in rep['order']:
        j = rep['cuts'][r]
        old = fixed[j][0] if j < len(fixed) else len(original['B'])
        inserted.setdefault(old, []).append(r)
    gone = set(MOVABLE.values()) | DELETED
    w = copy.deepcopy(original)
    b, mapping, chosen = [], {}, {}
    for old in range(len(original['B']) + 1):
        for r in inserted.get(old, []):
            chosen[r] = len(b)
            b.append(copy.deepcopy(gates[r]))
        mapping[old] = len(b)
        if old < len(original['B']) and old not in gone:
            b.append(copy.deepcopy(original['B'][old]))
    w['B'] = b
    for wr in w['warps']:
        wr[0] = mapping[wr[0]]
    require(original['restore'][82][1] == 584, 'restore edit preimage')
    del w['restore'][82]
    w['removed'] = sorted(w['removed'] + [584])
    del w['start_extra']['584']
    del w['helper_final']['584']
    _, cleanup = programs(w)
    w['cleanup'] = [list(g) + [FULL] for g in cleanup]
    return w, chosen


def literal_events(w):
    """Physical events and consecutive-touch edges, without virtual registers."""
    events, refs = [], {}

    def emit(rs, section, index, fixed=None):
        require((section, index) not in refs, 'duplicate literal event reference')
        refs[section, index] = len(events)
        events.append({'registers': rs, 'section': section, 'index': index, 'fixed': fixed})

    for r in range(704):
        frame = [w['ports'][r]] if r < 112 else w.get('start_extra', {}).get(str(r), [])
        emit([r], 'start', r, frame)
    scalar_index = 0
    for i, g in enumerate(w['A']):
        if g[0] == 'warp':
            emit([g[1]], 'warp-A-entry', i, g[3])
            emit([g[1]], 'warp-A-exit', i, g[4])
        else:
            emit(regs(g), 'A', scalar_index)
            scalar_index += 1
    for r, frame in zip(w['centers'], w['center_frames']):
        emit([r], 'cut', r, frame)
    for t in range(112):
        emit([112 + t], 'cut', 112 + t, w.get('target_levels', {}).get(str(t), []))
    bypos = {}
    for op, rec in enumerate(w['warps']):
        bypos.setdefault(rec[0], []).append((op, rec))
    for i in range(len(w['B']) + 1):
        for op, (_, r, _, u, e) in bypos.get(i, []):
            emit([r], 'warp-B-entry', op, u)
            emit([r], 'warp-B-exit', op, e)
        if i < len(w['B']):
            emit(regs(w['B'][i]), 'B', i)
    for i, g in enumerate(w['restore']):
        emit(regs(g), 'restore', i)
    for r in range(704):
        frame = w.get('helper_final', {}).get(str(r), FULL)
        if 112 <= r < 224:
            p = w['ports'][r - 112]
            frame = [v for v in range(512) if (v & p).bit_count() % 2 == 0]
        emit([r], 'end', r, frame)
    next_touch, last = {}, {}
    for i, event in enumerate(events):
        for r in event['registers']:
            if r in last:
                next_touch[last[r], r] = i
            last[r] = i
    return events, refs, next_touch


def check_path(stream, certificate, port_to_target=True):
    events, refs, next_touch = stream
    ids = []
    for supplied in certificate['events']:
        key = supplied['section'], supplied['index']
        require(key in refs, 'path references missing physical event')
        i = refs[key]
        require(events[i]['registers'] == supplied['registers'], 'physical register mismatch')
        ids.append(i)
    require(len(ids) >= 2 and ids == sorted(set(ids)), 'path chronology')
    v = certificate['direction']
    require(v != 0, 'zero obstruction direction')
    first, last = events[ids[0]], events[ids[-1]]
    if port_to_target:
        require(first['section'] == 'start' and first['registers'][0] < 112
                and last['section'] == 'end' and 112 <= last['registers'][0] < 224,
                'path is not input-port to target-output')
    require(first['fixed'] is not None and last['fixed'] is not None, 'unfixed path boundary')
    require(v in span(first['fixed']), 'direction absent at source boundary')
    require(v not in span(last['fixed']), 'direction accepted at endpoint')
    require(all(not events[i]['section'].startswith('warp') for i in ids[1:-1]),
            'path crosses a native warp')
    for a, b in zip(ids, ids[1:]):
        common = set(events[a]['registers']) & set(events[b]['registers'])
        require(any(next_touch.get((a, r)) == b for r in common), 'nonconsecutive physical touches')
    return first['section'], last['section']


def reject(action, expected):
    try:
        action()
    except ValueError as exc:
        require(expected in str(exc), 'control rejected for unintended reason: ' + str(exc))
    else:
        raise ValueError('defective control was accepted: ' + expected)


def main():
    started = time.monotonic()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'live source hash mismatch: ' + row['path'])
    reports = []
    for provider in ('base', 'extra'):
        original = json.loads(gzip.decompress((SOURCE / f'edits/FINAL-WORD-{provider}.json.gz').read_bytes()))
        fixed, gates, intervals, reps = classify(original)
        certificates = json.loads(gzip.decompress((HERE / f'PATHS-{provider}.json.gz').read_bytes()))
        require([x['class'] for x in certificates] == list(range(len(reps))), 'certificate coverage/order')
        endpoint_counts = {}
        for i, (rep, cert) in enumerate(zip(reps, certificates)):
            word, _ = make_word(original, fixed, gates, rep)
            stream = literal_events(word)
            label = ' -> '.join(check_path(stream, cert))
            endpoint_counts[label] = endpoint_counts.get(label, 0) + 1
            if i == 0:
                bad = copy.deepcopy(cert)
                bad['direction'] = 0
                reject(lambda: check_path(stream, bad), 'zero obstruction')
                bad = copy.deepcopy(cert)
                bad['events'][1]['registers'] = [703]
                reject(lambda: check_path(stream, bad), 'physical register mismatch')
                bad = copy.deepcopy(cert)
                bad['events'][1], bad['events'][2] = bad['events'][2], bad['events'][1]
                reject(lambda: check_path(stream, bad), 'path chronology')
                old = json.loads((HERE / f'CONTROL-native-entry-{provider}.json').read_text())
                check_path(stream, old, port_to_target=False)
                reject(lambda: check_path(stream, old), 'path is not input-port to target-output')
                bad = copy.deepcopy(cert)
                del bad['events'][1]
                reject(lambda: check_path(stream, bad), 'nonconsecutive physical touches')
                # An actual added reset between two witnessed B contacts must
                # invalidate the old path, even when its scalar indices stay put.
                a, b = next((a, b) for a, b in zip(cert['events'], cert['events'][1:])
                            if a['section'] == b['section'] == 'B'
                            and a['index'] < b['index'])
                r = min(set(a['registers']) & set(b['registers']))
                reset_word = copy.deepcopy(word)
                reset_word['warps'].append([b['index'], r, [1 << j for j in range(9)], FULL, []])
                reject(lambda: check_path(literal_events(reset_word), cert),
                       'nonconsecutive physical touches')
                accept_word = copy.deepcopy(word)
                accept_word['ports'][cert['events'][-1]['registers'][0] - 112] = 0
                reject(lambda: check_path(literal_events(accept_word), cert),
                       'direction accepted at endpoint')
        cuts = {r: sum(old < at for old, _ in fixed) for r, at in MOVABLE.items()}
        anchor_rep = {'order': sorted(cuts, key=cuts.get), 'cuts': cuts}
        anchor, chosen = make_word(original, fixed, gates, anchor_rep)
        algebra = []
        for label, rep in [('anchor', anchor_rep), ('first-class', reps[0]), ('last-class', reps[-1])]:
            word, _ = make_word(original, fixed, gates, rep)
            for dual in (False, True):
                result = literal_replay(word, dual)
                require(result['pass'] and result['cleanup_matches_independent_derivation'],
                        'exact operator or literal cleanup failed: ' + str(result))
                algebra.append({'case': label, **result})
        bad = copy.deepcopy(anchor)
        bad['B'][chosen[168]][3] *= -1
        require(not literal_replay(bad, False)['pass'], 'wrong-sign control accepted')
        bad = copy.deepcopy(anchor)
        bad['cleanup'] = copy.deepcopy(original['cleanup'])
        result = literal_replay(bad, False)
        require(not result['pass'] and not result['cleanup_matches_independent_derivation'],
                'stale-cleanup control accepted')
        illegal = copy.deepcopy(anchor_rep)
        illegal['cuts'][56] = intervals[56][0] - 1
        illegal['order'] = sorted(illegal['cuts'], key=illegal['cuts'].get)
        bad, _ = make_word(original, fixed, gates, illegal)
        require(not literal_replay(bad, False)['pass'], 'noncommuting-boundary control accepted')
        reports.append({'provider': provider, 'classes': len(reps), 'endpoint_kinds': endpoint_counts,
                        'exact_algebra': algebra, 'rejected_controls': 10})
    print(json.dumps({'status': 'PASS_DIRECT584_COMPLETE_COMMUTING_COVER', 'providers': reports,
                     'literal_path_checks': sum(r['classes'] for r in reports),
                     'seconds': time.monotonic() - started,
                     'scope': 'Four B reads, finite h=9 providers; arbitrary existing native boundaries and helper entrance/end frames; no new kappa.'}, indent=2))


if __name__ == '__main__':
    main()
