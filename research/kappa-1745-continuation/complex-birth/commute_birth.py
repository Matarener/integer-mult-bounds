#!/usr/bin/env python3
"""Move first helper ADD contacts to their earliest exact commutation boundary.

All integer/dyadic coefficients and the full dirty scalar operator are retained.
The complex wrapped endpoints and COPY anchors use the actual supplier schema.
Credit PR4067's chronological lead, the continuation BIT birth construction,
and the retained adaptive complex supplier/frame optimizer. OpenAI; Apache-2.0.
"""
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


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'research/kappa-adaptive-continuation/native-alternatives'
sys.path.insert(0, str(OLD))
import fanout_search as F
import opt_frames as O
F.phi = O.phi = lambda r: r ** (1 - 0.001745) if r else 0.0
FULL = F.basis(tuple(1 << i for i in range(9)))


def canonical(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def trace(w, snapshots=False):
    live = set(range(704)) - set(w['removed'])
    current = {r: F.basis((w['ports'][r],)) if r < 112 else
               F.basis(tuple(w['start_extra'].get(str(r), []))) for r in live}
    paid = Counter()
    states = []
    def advance(r, frame):
        frame = F.basis(tuple(frame))
        assert F.contains(current[r], frame), (r, current[r], frame)
        jump = len(frame) - len(current[r])
        if jump:
            paid[jump] += 1
        current[r] = frame
    for section, events in F.expand(w).items():
        for event in events:
            if snapshots and section == 'A':
                states.append(dict(current))
            if event[0] == 'warp':
                advance(event[1], event[3])
                current[event[1]] = F.basis(tuple(event[4]))
            else:
                for r in F.regs(event):
                    advance(r, event[-1])
        if section == 'A':
            states.append(dict(current))
            for r, frame in zip(w['centers'], w['center_frames']):
                advance(r, frame)
            for t in range(112):
                advance(112 + t, w['target_levels'].get(str(t), []))
    for r in live:
        if str(r) in w['helper_final']:
            final = w['helper_final'][str(r)]
        elif 112 <= r < 224:
            final = tuple(x for x in range(512) if not ((x & w['ports'][r - 112]).bit_count() & 1))
        else:
            final = FULL
        advance(r, final)
    for r, frame in zip(w['centers'], w['center_frames']):
        frame = F.basis(tuple(frame))
        levels = {F.basis(tuple(w['target_levels'].get(str(e[1] - 112), [])))
                  for e in w['cut'] if e[2] == r}
        for level in sorted(levels, key=lambda f: -len(f)):
            assert F.contains(level, frame)
            if frame != level:
                paid[len(frame) - len(level)] += 1
            frame = level
    return paid, states


def candidates(w):
    baseline, states = trace(w, True)
    assert dict(sorted(baseline.items())) == {int(r): c for r, c in w['report']['local_profile'].items()}
    contacted = set()
    last_write = {}
    for index, event in enumerate(w['A']):
        if event[0] == 'add':
            _, helper, source, numerator, denominator, old_frame = event
            if helper >= 224 and helper not in contacted and index >= w['prelude_events']:
                earliest = max(w['prelude_events'], last_write.get(source, -1) + 1)
                if earliest < index:
                    # Every crossed gate commutes exactly with this ADD.
                    assert all(helper not in F.regs(e) for e in w['A'][earliest:index])
                    assert all(e[1] != source for e in w['A'][earliest:index])
                    new_frame = F.basis(states[earliest][helper] + states[earliest][source])
                    changed = deepcopy(w)
                    moved = ['add', helper, source, numerator, denominator, list(new_frame)]
                    changed['A'] = w['A'][:earliest] + [moved] + w['A'][earliest:index] + w['A'][index + 1:]
                    profile, _ = trace(changed)
                    F.derive_cleanup(changed)
                    changed['report']['local_profile'] = {str(r): c for r, c in sorted(profile.items())}
                    delta = profile.copy()
                    delta.subtract(baseline)
                    yield changed, {'helper': helper, 'source': source, 'old_index': index,
                                    'new_index': earliest, 'old_event': event, 'new_event': moved,
                                    'wrapped_helper': str(helper) in w['helper_final'],
                                    'profile': dict(profile), 'delta': {r: c for r, c in delta.items() if c},
                                    'saving': -sum(c * F.phi(r) for r, c in delta.items())}
        contacted.update(F.regs(event))
        last_write[event[1]] = index


def raw_A(w):
    live = set(range(704)) - set(w['removed'])
    rows = {r: {r: Q(1)} for r in live}
    for event in w['A'][w['prelude_events']:]:
        d = event[1]
        if event[0] == 'add':
            s, q = event[2], Q(event[3], event[4])
            for k, value in tuple(rows[s].items()):
                v = rows[d].get(k, Q(0)) + q * value
                if v:
                    rows[d][k] = v
                else:
                    rows[d].pop(k, None)
        elif event[0] == 'scale':
            q = Q(event[2], event[3])
            rows[d] = {k: q * value for k, value in rows[d].items() if q * value}
        else:
            raise ValueError(event[0])
    return rows


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--variant', choices=('base', 'extra'), default='base')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--optimize-all', action='store_true')
    args = ap.parse_args()
    source = OLD / f'candidate/BORROW-WORD-43{args.variant}.json.gz'
    word = F.read(source)
    args.output.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    rows = []
    positives = []
    started = monotonic()
    original_operator = None
    for candidate, row in candidates(word):
        stats['commutable_first_contacts'] += 1
        if args.optimize_all or row['saving'] > 1e-10:
            try:
                candidate, optimization = O.optimize(candidate)
                stats['joint_frames_solved'] += 1
            except ValueError as exc:
                row['optimization_rejected'] = str(exc)
                stats['joint_frames_rejected'] += 1
            else:
                profile, _ = trace(candidate)
                baseline = Counter({int(r): c for r, c in word['report']['local_profile'].items()})
                delta = profile.copy(); delta.subtract(baseline)
                row['optimization'] = optimization
                row['optimized_delta'] = {r: c for r, c in delta.items() if c}
                row['optimized_saving'] = -sum(c * F.phi(r) for r, c in delta.items())
        saving = row.get('optimized_saving', row['saving'])
        if saving > 1e-10:
            if original_operator is None:
                original_operator = raw_A(word)
            assert raw_A(candidate) == original_operator
            name = f"WORD-helper{row['helper']}.json.gz"
            payload = canonical(candidate)
            (args.output / name).write_bytes(gzip.compress(payload, mtime=0))
            row.update(word=name, word_content_sha256=sha256(payload).hexdigest(),
                       exact_all_dirty_A_columns_equal=True, native_admission=False)
            positives.append(row)
            stats['positive'] += 1
            print('POSITIVE', row['helper'], saving, row.get('optimized_delta', row['delta']), flush=True)
        rows.append(row)
        if stats['commutable_first_contacts'] % 25 == 0:
            print('PROGRESS', dict(stats), monotonic() - started, flush=True)
    paths = [source, Path(__file__), OLD / 'fanout_search.py', OLD / 'opt_frames.py']
    result = {'status': 'EXACT_SIGNED_FIRST_CONTACT_COMMUTATION_SCREEN', 'variant': args.variant,
              'stats': dict(stats), 'candidates': rows, 'positives': positives,
              'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths},
              'seconds': monotonic() - started, 'new_kappa': False,
              'scope': 'First A contacts commute through gates touching neither the helper nor writes to its donor. '
                       'All signed coefficients and complete dirty A operator are preserved. Existing compensation remains exact; '
                       'literal inverse cleanup is regenerated. Positive profiles require native admission on both variants.'}
    (args.output / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('DONE', dict(stats), monotonic() - started, flush=True)


if __name__ == '__main__':
    main()
