"""Bounded check of PR #3647's R437 hosted template against the audited word and records.

The hosting rule is taken from the selected chain's idle-axis hosting module on main
(research/e8-bit-carrier-skeleton/code/hub/idle-axis-hosting/hosting_core.py, docstrings of
windows() and expand()).  This module is written separately for the audit and imports nothing
from it.

Rule: an idle child (idx, pair p, rank r) may host a whole width-w helper residual of a local
invocation at stage s only when that invocation lies strictly between the last touch of pair p
(a local invocation on p, or a bridge naming p) and the idle child, and is not on p itself.
Each of the 2v (side, port) data families of p receives one copy of the child; a hosted residual
owns coordinates [off, off + w) of one copy, and that child keeps the remaining rank.
"""
import hashlib
import json
from collections import Counter, defaultdict

from wordsem import need


def nine_stage_schedule(K=4):
    """Parent recipe of the selected nine-stage caller (global_k.py on main: recipe(K) and its
    idle-child insertion after each local stage), with idle children numbered in order."""
    ev = [dict(kind='local_cover_sweep', stage=0, pair=0, reverse=False)]
    stage = 1
    for j in range(K):
        ev.append(dict(kind='local_cover_sweep', stage=stage, pair=j, reverse=True))
        stage += 1
        if j < K - 1:
            ev.append(dict(kind='bridge', dst=j, src=j + 1, coefficient=1))
        ev.append(dict(kind='local_cover_sweep', stage=stage, pair=j, reverse=False))
        stage += 1
        if j < K - 1:
            ev.append(dict(kind='bridge', dst=j, src=j + 1, coefficient=-1))
    for j in reversed(range(K - 1)):
        ev.append(dict(kind='bridge', dst=j + 1, src=j, coefficient=1))
    ev.append(dict(kind='exchange'))
    out, levels, idx = [], [-1] * K, 0
    for e in ev:
        out.append(e)
        if e['kind'] != 'local_cover_sweep':
            continue
        s, p = e['stage'], e['pair']
        levels[p] = s
        new = []
        if s % 2 == 1 and s <= 2 * K - 3:
            j = (s + 1) // 2
            new.append((j, 7 * (s + 1), -1, s))
            levels[j] = s
        elif s % 2 == 0 and 2 <= s <= 2 * K - 2:
            new.append((s // 2, 7, s - 1, s))
            levels[s // 2] = s
        elif s == 2 * K:
            for j in range(K):
                new.append((j, 7 * (2 * K - levels[j]), levels[j], 2 * K))
                levels[j] = 2 * K
        for j, rank, lo, hi in new:
            out.append(dict(kind='idle', idx=idx, pair=j, rank=rank, source_level=lo, target_level=hi))
            idx += 1
    return out


def windows(schedule):
    last, out, local = {}, {}, []
    for pos, e in enumerate(schedule):
        k = e['kind']
        if k == 'local_cover_sweep':
            local.append((pos, e['stage'], e['pair']))
            last[e['pair']] = pos
        elif k == 'bridge':
            last[e['dst']] = pos
            last[e['src']] = pos
        elif k == 'idle':
            p, lo = e['pair'], last.get(e['pair'], -1)
            out[e['idx']] = (p, e['rank'], sorted(s for q, s, pp in local if lo < q < pos and pp != p))
        else:
            need(k == 'exchange', 'unknown schedule event %r' % k)
    return out


def events_from_records(records, reverse):
    """Expected local-program events of one orientation, from the record stream, following the
    event layout of the selected nine-stage caller (global_k.py on main)."""
    out = []
    rank = {x: z for op, x, y, c, f, z in records if op == 2}
    for op, x, y, c, f, z in (reversed(records) if reverse else records):
        r = int(reverse)
        if op == 0:
            old, new = (c, y) if reverse else (y, c)
            out.append([0, x, old, new, f, r])
        elif op == 1:
            out.append([1, x, y, -c if reverse else c, f, r])
        elif op == (3 if reverse else 2):
            out.append([2, x, y, c, f, rank[x], r])
        else:
            out.append([3, x, y, c, f, z, r])
    return out


def check(template, word, geo, records, local_profile):
    v, R = word['v'], word['R']
    V2, n = 2 * v, 2 * v + R
    res = {}
    need(template['stages'] == 9 and template['replicas'] == 32 and template['h'] == 8, 'template shape')
    stages, replicas = template['stages'], template['replicas']
    pairs = 4
    fam_per_replica = pairs * V2
    sched = template['schedule']
    sweeps = {e['stage']: e for e in sched if e['kind'] == 'local_cover_sweep'}
    need(sorted(sweeps) == list(range(stages)), 'one local sweep per stage')

    # 1. the template's parent schedule equals main's recipe; windows by the selected hosting rule
    res['schedule_equals_main_recipe'] = sched == nine_stage_schedule()
    win = windows(sched)
    published = {int(k): (p, r, sorted(st)) for k, (p, r, st) in template['hosting']['windows'].items()}
    res['windows_rederived_equal'] = {k: x for k, x in win.items() if x[1] > 0} == published
    res['windows'] = {k: list(x) for k, x in sorted(win.items())}

    # 2. helper widths from the literal word (8 - start-frame dimension; all end at FULL)
    widths = [8 - geo.dim[word['start'][2 * v + h]] for h in range(R)]
    need(all(geo.dim[word['final'][2 * v + h]] == 8 for h in range(R)), 'a helper does not end at FULL')

    # 3. slot list: every (stage, helper) occurrence exactly once, legal window, disjoint offsets
    slots = template['hosting']['slots']
    seen = Counter((s, h) for idx, cp, off, w, s, h in slots)
    res['slots'] = len(slots)
    res['every_occurrence_once'] = (set(seen) == {(s, h) for s in range(stages) for h in range(R)}
                                    and all(c == 1 for c in seen.values()))
    used = defaultdict(list)
    ok_window = ok_width = ok_copy = True
    for idx, cp, off, w, s, h in slots:
        ok_window &= idx in win and s in win[idx][2]
        ok_width &= w == widths[h]
        ok_copy &= 0 <= cp < V2
        used[idx, cp].append((off, w))
    disjoint = True
    for (idx, cp), segs in used.items():
        segs.sort()
        end = 0
        for off, w in segs:
            disjoint &= off >= end and off + w <= win[idx][1]
            end = off + w
    res['stage_inside_window'] = ok_window
    res['width_matches_word'] = ok_width
    res['copy_in_range'] = ok_copy
    res['offsets_disjoint_within_rank'] = disjoint

    # 4. remainders: every copy of every positive-rank child keeps rank - used
    rem = Counter()
    per_idx = {}
    for idx, (p, r, st) in win.items():
        if r == 0:
            continue
        hist = Counter(r - sum(w for _, w in used.get((idx, cp), [])) for cp in range(V2))
        per_idx[idx] = {k: x for k, x in sorted(hist.items()) if k}
        rem.update({k: x for k, x in hist.items() if k})
    published_rem = {int(k): {int(a): b for a, b in x.items()} for k, x in template['hosting']['remainders'].items()}
    res['remainders_equal_published'] = per_idx == published_rem
    res['idle_children_per_replica'] = dict(sorted(rem.items()))

    # 5. calls: 9 stages x 32 replicas, owners agree with slots and the data blocks; no banks
    slot_of = {(s, h): (idx, cp, off, w) for idx, cp, off, w, s, h in slots}
    calls = template['calls']
    res['calls'] = len(calls)
    good_calls = len(calls) == stages * replicas and sorted({(c['stage'], c['replica']) for c in calls}) == [
        (s, r) for s in range(stages) for r in range(replicas)]
    hosted = 0
    for c in calls:
        s, rep, p = c['stage'], c['replica'], c['pair']
        sw = sweeps[s]
        good_calls &= p == sw['pair'] and c['orientation'] == ('reverse' if sw['reverse'] else 'forward')
        own = c['owners']
        good_calls &= len(own) == n
        block = rep * fam_per_replica + p * V2
        data_fams = []
        for reg, (fam, route) in enumerate(own):
            if reg < V2:
                # data route of the selected caller: side flips in a reverse sweep
                side = (reg // v) ^ int(sw['reverse'])
                good_calls &= route == ['data', s, reg % v] and fam == block + side * v + reg % v
                data_fams.append(fam)
            elif (s, reg - V2) not in slot_of:
                good_calls = False
            else:
                idx, cp, off, w = slot_of[s, reg - V2]
                pidx = win[idx][0]
                good_calls &= (route == ['hosted', idx, off, w] and fam == rep * fam_per_replica + pidx * V2 + cp
                               and pidx != p)
                hosted += 1
        good_calls &= sorted(data_fams) == list(range(block, block + V2))
    res['owners_match_slots_and_blocks'] = good_calls
    res['hosted_occurrences'] = hosted
    # template bank counters (a count read from the template; the owners check already implies none)
    res['banks'] = sum(template['banks_per_stage'].values()) + sum(template['hosting']['banks_per_stage'].values())
    res['emitted_local_events_count'] = len(calls) * len(records)

    # 6. local programs bound to the audited record stream (both orientations), and every call
    # bound to the program of its orientation by its local_hash
    lp = template['local_programs']
    res['local_programs_equal_records'] = all(lp[k] == events_from_records(records, k == 'reverse')
                                              for k in ('forward', 'reverse'))
    digest = {k: hashlib.sha256(json.dumps(lp[k], separators=(',', ':')).encode()).hexdigest() for k in lp}
    res['calls_bound_to_local_programs'] = all(c['local_hash'] == digest[c['orientation']] for c in calls)

    # 7. whole paid profile = calls x local profile + replicas x idle remainders
    whole = Counter()
    for k, x in local_profile.items():
        whole[int(k)] += stages * replicas * x
    for k, x in rem.items():
        whole[k] += replicas * x
    res['whole_profile'] = dict(sorted(whole.items()))
    res['rank_mass'] = sum(k * x for k, x in whole.items())
    res['deficit'] = template['m'] * template['live'] - res['rank_mass']
    return res
