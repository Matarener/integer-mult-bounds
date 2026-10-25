#!/usr/bin/env python3
"""Exact signed SOURCE birth resynthesis with explicit complex dirty repair."""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
from time import monotonic
from commute_birth import ROOT, HERE, OLD, F, O, FULL, trace, canonical
from exact_rows import add, execute, replay, expected, repair

sys.path.insert(0, str(HERE.parent))
from complex_projection_screen import combination


def source_start(word):
    return {r: {(r, ()): Q(1)} if r < 112 else {}
            for r in set(range(704)) - set(word['removed'])}


def early_schedule(word):
    rows = source_start(word)
    seen = set()
    births = []
    allowed = set(range(224, 704)) - set(word['removed']) - set(map(int, word['start_extra'])) - set(map(int, word['helper_final']))
    for index, event in enumerate(word['A']):
        if event[0] == 'add':
            d, donor = event[1:3]
            q = Q(event[3], event[4])
            increment = {key: q * v for key, v in rows[donor].items() if q * v}
            if index >= word['prelude_events'] and d in allowed and d not in seen and len(increment) == 1:
                (source, operators), coefficient = next(iter(increment.items()))
                if source < 112 and not operators and F.basis(tuple(event[-1])) == F.basis((word['ports'][source],)):
                    new = ['add', d, source, coefficient.numerator, coefficient.denominator, event[-1]]
                    births.append((index, new))
        execute(rows, event)
        seen.update(F.regs(event))
    ids = {i for i, e in births}
    out = deepcopy(word)
    p = word['prelude_events']
    out['A'] = word['A'][:p] + [e for i, e in births] + [e for i, e in enumerate(word['A'][p:], p) if i not in ids]
    return out, births


def prefix_candidate(word, helper, position='last_write', all_prefixes=False):
    writes = []
    observer = len(word['A'])
    for index, event in enumerate(word['A']):
        if event[0] == 'add' and event[2] == helper:
            observer = index
            break
        if event[1] == helper:
            writes.append(index)
    if len(writes) < (1 if all_prefixes else 2):
        raise ValueError('short_prefix')
    if writes[0] < word['prelude_events']:
        raise ValueError('prelude_contact')
    end = writes[-1] if position == 'last_write' else observer
    frame = F.basis(tuple(word['A'][end][-1] if end < len(word['A']) else word['A'][writes[-1]][-1]))
    if not all_prefixes and len({tuple(word['A'][i][-1]) for i in writes}) < 2:
        raise ValueError('single_frame_prefix')
    rows = source_start(word)
    live = set(rows)
    current = {r: F.basis((word['ports'][r],)) if r < 112 else
               F.basis(tuple(word['start_extra'].get(str(r), []))) for r in live}
    deleted = set(writes)
    stop = end + 1 if position == 'last_write' else end
    for index, event in enumerate(word['A'][:stop]):
        execute(rows, event)
        if index in deleted:
            continue
        if event[0] == 'warp':
            current[event[1]] = F.basis(tuple(event[4]))
        else:
            for r in F.regs(event):
                current[r] = F.basis(tuple(event[-1]))
    wanted = rows[helper]
    assert not current[helper]
    caps = {r: None for r in live}
    def contact(event):
        for r in F.regs(event):
            if caps[r] is None:
                caps[r] = F.basis(tuple(event[3] if event[0] == 'warp' else event[-1]))
    for event in word['A'][stop:]:
        contact(event)
    for r, cap in zip(word['centers'], word['center_frames']):
        if caps[r] is None:
            caps[r] = F.basis(tuple(cap))
    for event in F.expand(word)['B'] + word['restore']:
        contact(event)
    for r in live:
        if caps[r] is None:
            caps[r] = F.basis(tuple(word['helper_final'].get(str(r), FULL)))
    available = [r for r in live if r != helper and not 112 <= r < 224 and rows[r]
                 and F.contains(current[r], frame) and F.contains(frame, caps[r])]
    def cost(r):
        return (F.phi(len(frame) - len(current[r])) + F.phi(len(caps[r]) - len(frame))
                - F.phi(len(caps[r]) - len(current[r])))
    available.sort(key=lambda r: (cost(r), len(rows[r]), r))
    support = combination(wanted, available, rows)
    if not support:
        raise ValueError('no_dyadic_SOURCE_span')
    new = [['add', helper, r, coefficient.numerator, coefficient.denominator, list(frame)]
           for r, coefficient in sorted(support.items()) if coefficient]
    out = deepcopy(word)
    out['A'] = []
    for index, event in enumerate(word['A']):
        if index == end:
            out['A'].extend(new)
        if index not in deleted:
            out['A'].append(event)
    if end == len(word['A']):
        out['A'].extend(new)
    F.derive_cleanup(out)
    return out, {'helper': helper, 'position': position, 'deleted_A_indices': writes, 'new_birth': new,
                 'compatible_donors': len(available),
                 'SOURCE_projection': [[r, list(operators), str(q)] for (r, operators), q in sorted(wanted.items())]}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--variant', choices=('base', 'extra'), default='base')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--early', action='store_true')
    ap.add_argument('--position', choices=('last_write', 'first_observer'), default='last_write')
    ap.add_argument('--all-prefixes', action='store_true')
    args = ap.parse_args()
    source = OLD / f'candidate/BORROW-WORD-43{args.variant}.json.gz'
    original = F.read(source)
    baseline = Counter({int(r): c for r, c in original['report']['local_profile'].items()})
    assert replay(original)[0] == expected(original)
    args.output.mkdir(parents=True, exist_ok=True)
    word = original
    schedule = None
    if args.early:
        word, births = early_schedule(original)
        try:
            correction = repair(word)
            word, optimization = O.optimize(word)
            assert replay(word)[0] == expected(word)
        except (ValueError, AssertionError) as exc:
            schedule = {'births': births, 'rejected': str(exc)}
            word = original
        else:
            schedule = {'births': births, 'correction': correction, 'optimization': optimization}
            (args.output / 'SCHEDULED.json.gz').write_bytes(gzip.compress(canonical(word), mtime=0))
        print('EARLY_SCHEDULE', len(births), {k: v for k, v in schedule.items() if k != 'births'}, flush=True)
    allowed = sorted(set(range(224, 704)) - set(word['removed']) - set(map(int, word['start_extra'])) - set(map(int, word['helper_final'])))
    stats = Counter(); cases = []; positives = []; started = monotonic()
    for helper in allowed:
        stats['helpers_considered'] += 1
        try:
            candidate, identity = prefix_candidate(word, helper, args.position, args.all_prefixes)
        except ValueError as exc:
            stats[str(exc.args[0])] += 1
            continue
        stats['SOURCE_prefix_rebuilt'] += 1
        try:
            candidate, optimization = O.optimize(candidate)
        except ValueError as exc:
            stats['frame_rejected'] += 1
            cases.append({'helper': helper, 'rejected': str(exc)})
            continue
        stats['joint_frames_solved'] += 1
        profile, _ = trace(candidate)
        delta = profile.copy(); delta.subtract(baseline)
        saving = -sum(c * F.phi(r) for r, c in delta.items())
        case = {'helper': helper, 'saving': saving, 'delta': {r: c for r, c in delta.items() if c}, 'optimization': optimization}
        if saving > 1e-10:
            try:
                correction = repair(candidate)
            except (ValueError, AssertionError) as exc:
                stats['dirty_repair_rejected'] += 1
                case['dirty_rejection'] = str(exc)
            else:
                payload = canonical(candidate)
                name = f'WORD-helper{helper}.json.gz'
                (args.output / name).write_bytes(gzip.compress(payload, mtime=0))
                case.update(identity=identity, correction=correction, word=name,
                            word_content_sha256=sha256(payload).hexdigest(), native_admission=False)
                positives.append(case); stats['positive_exact_word'] += 1
                print('POSITIVE_EXACT', helper, saving, case['delta'], correction, flush=True)
        cases.append(case)
        if stats['SOURCE_prefix_rebuilt'] % 20 == 0:
            print('PROGRESS', dict(stats), monotonic() - started, flush=True)
    result = {'status': 'SIGNED_COMPLEX_SOURCE_PREFIX_RESYNTHESIS', 'variant': args.variant,
              'position': args.position, 'all_prefixes': args.all_prefixes,
              'schedule': schedule, 'stats': dict(stats), 'cases': cases, 'positives': positives,
              'seconds': monotonic() - started, 'new_kappa': False,
              'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in (source, Path(__file__), HERE / 'exact_rows.py', HERE / 'commute_birth.py',
                                          HERE.parent / 'complex_projection_screen.py', OLD / 'fanout_search.py', OLD / 'opt_frames.py')},
              'scope': 'Unwrapped zero-entrance/full-exit helper prefixes before their first observation; exact signed SOURCE rows, '
                       'joint frames, and restricted full free-operator dirty correction. No new controller or native/outer admission is asserted.'}
    (args.output / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('DONE', dict(stats), monotonic() - started, flush=True)


if __name__ == '__main__':
    main()
