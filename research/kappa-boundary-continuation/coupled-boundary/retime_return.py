#!/usr/bin/env python3
"""Exact incoming-helper releases through a returning B-prefix excursion.

The source is the frozen PR3734 BORROW-WORD. Only a fixed-prefix identity is
claimed here; native compilation and the complete owner invoice are separate.
Apache-2.0. Substantial OpenAI assistance; predecessor attribution is retained.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def basis(vs):
    piv = {}
    for x in vs:
        for k in sorted(piv, reverse=True):
            if x >> k & 1:
                x ^= piv[k]
        if x:
            k = x.bit_length()-1
            for j in piv:
                if piv[j] >> k & 1:
                    piv[j] ^= x
            piv[k] = x
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def span(bs):
    out = {0}
    for x in bs:
        out |= {v ^ x for v in out}
    return out


def regs(e):
    return e[1:3] if e[0] == 'add' else [e[1]]


def add(a, b, q):
    for k, v in b.items():
        a[k] = a.get(k, Q(0)) + q*v
        if not a[k]:
            del a[k]


def warp(row, op):
    return {(s, w[1:] if w and w[0] == -op else (op,)+w): v
            for (s, w), v in row.items()}


def native_profile(w):
    full = tuple(1 << j for j in range(8, -1, -1))
    cur = [basis([p]) for p in w['ports']] + [()] * 592
    for h, f in w['start_extra'].items():
        cur[int(h)] = basis(f)
    paid = Counter()

    def climb(h, f):
        if h >= 704:
            return
        f = basis(f)
        if basis(cur[h]+f) != f:
            raise ValueError(('nonmonotone', h, cur[h], f))
        if cur[h] != f:
            paid[len(f)-len(cur[h])] += 1
            cur[h] = f

    def event(e):
        if e[0] == 'warp':
            _, h, op, f0, f1 = e
            if cur[h] != basis(f0):
                raise ValueError(('warp start', h, cur[h], f0))
            cur[h] = basis(f1)
        else:
            for h in regs(e):
                climb(h, e[-1])

    for e in w['A']:
        event(e)
    for h, f in zip(w['centers'], w['center_frames']):
        served = {basis(w['target_levels'].get(str(e[1]-112), []))
                  for e in w['cut'] if e[2] == h}
        old = basis(f)
        for f1 in sorted(served, key=lambda x: -len(x)):
            if old != f1:
                paid[len(old)-len(f1)] += 1
                old = f1
    warps = {}
    for op, (p, h, G, f0, f1) in enumerate(w['warps'], 1):
        warps.setdefault(p, []).append(['warp', h, op, f0, f1])
    snapshots = []
    for p in range(len(w['B'])+1):
        snapshots.append(cur.copy())
        for e in warps.get(p, []):
            event(e)
        if p < len(w['B']):
            event(w['B'][p])
    for e in w['restore']:
        event(e)
    for h in range(704):
        if h in w['removed']:
            continue
        f = full if h < 112 or h >= 224 else basis(x for x in range(512) if not ((x & w['ports'][h-112]).bit_count() % 2))
        if str(h) in w['helper_final']:
            f = w['helper_final'][str(h)]
        climb(h, f)
    return dict(sorted(paid.items())), snapshots


def column_prefix(w, h, end):
    rows = [{} for _ in range(704)]
    rows[h] = {(h, ()): Q(1)}
    warps = {}
    for op, (p, r, G, f0, f1) in enumerate(w['warps'], 1):
        warps.setdefault(p, []).append((r, op))
    for p in range(end):
        for r, op in warps.get(p, []):
            rows[r] = warp(rows[r], op)
        e = w['B'][p]
        if e[0] == 'add':
            add(rows[e[1]], rows[e[2]], Q(e[3], e[4]))
        elif e[0] == 'scale':
            rows[e[1]] = {k: v*Q(e[2], e[3]) for k, v in rows[e[1]].items()}
        else:
            raise ValueError(e[0])
    return rows


def candidate(w, h, snapshots):
    if any(h in regs(e) for part in ('A', 'precondition', 'compensation') for e in w[part]):
        return None
    if any(h in (x['source'], x['target']) for x in w['initial_corrections']):
        return None
    first = next((i for i, e in enumerate(w['B']) if e[1] == h), None)
    if first is None:
        return None
    early = [i for i, e in enumerate(w['B'][:first]) if e[0] == 'add' and e[2] == h]
    if not early:
        return None
    col = column_prefix(w, h, first)
    if col[h] != {(h, ()): Q(1)}:
        return None
    image = {}
    for r, row in enumerate(col):
        if r == h or not row:
            continue
        if set(row) != {(h, ())}:
            return None
        image[r] = row[h, ()]
    if not image:
        return None
    intersection = span(w['B'][first][-1])
    for r in image:
        intersection &= span(snapshots[first][r])
    joined = basis(intersection)
    old = basis(w['start_extra'].get(str(h), []))
    if len(joined) <= len(old) or basis(old+joined) != joined:
        return None
    changed = deepcopy(w)
    changed['start_extra'][str(h)] = list(joined)
    inserted = [['add', r, h, q.numerator, q.denominator, list(snapshots[first][r])]
                for r, q in sorted(image.items())]
    # Preserve the old recipient climbs with identity scales. This avoids
    # silently changing a later warp entrance when removing an early read.
    for i in early:
        old_event = changed['B'][i]
        changed['B'][i] = ['scale', old_event[1], 1, 1, old_event[-1]]
    changed['B'][first:first] = inserted
    for e in changed['warps']:
        if e[0] >= first:
            e[0] += len(inserted)
    profile, _ = native_profile(changed)
    changed['report']['local_profile'] = profile
    kept = [r for r in range(224, 704) if r not in w['removed']]
    widths = Counter(9-len(basis(changed['start_extra'].get(str(r), []))) if str(r) not in changed['helper_final'] else
                     len(basis(changed['helper_final'][str(r)]))-len(basis(changed['start_extra'].get(str(r), []))) for r in kept)
    changed['report']['width_inventory'] = dict(sorted(widths.items()))
    # Exact endpoint agreement of the affected column; all other columns are
    # unchanged because h is unchanged throughout the retimed prefix.
    after = column_prefix(changed, h, first+len(inserted))
    if after != col:
        raise ValueError(('prefix disagreement', h))
    return changed, dict(helper=h, native_role=224+kept.index(h), first_producer=first,
        deleted_reads=early, old_frame=list(old), new_frame=list(joined),
        inserted_gates=inserted, profile=profile,
        source_width=9-len(old), new_width=9-len(joined),
        exact_prefix_column_restored=True, image_support=len(image))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--followup', required=True, type=Path)
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'retiming')
    ap.add_argument('--parity', type=int, default=0)
    args = ap.parse_args()
    source = args.followup/'artifact/live-source/research/staged544-producer-return/words'
    w = read(source/'BORROW-WORD-43base.json.gz')
    profile, snapshots = native_profile(w)
    assert profile == {int(r): n for r, n in w['report']['local_profile'].items()}, (profile, w['report']['local_profile'])
    args.out.mkdir(parents=True, exist_ok=True)
    found = []
    eligible = []
    for h in range(448+args.parity, 704, 2):
        if h in w['removed']:
            continue
        eligible.append(h)
        try:
            answer = candidate(w, h, snapshots)
        except ValueError as ex:
            print('REJECT', h, str(ex), flush=True)
            continue
        if answer is None:
            continue
        changed, info = answer
        info['providers'] = {}
        for tag in ('base', 'extra'):
            src = source/f'BORROW-WORD-43{tag}.json.gz'
            other = read(src)
            _, other_snaps = native_profile(other)
            mutation = candidate(other, h, other_snaps)
            assert mutation is not None, ('other provider', h)
            out_word, other_info = mutation
            payload = json.dumps(out_word, sort_keys=True, separators=(',', ':')).encode()
            dest = args.out/f'RETIMED-{h}-{tag}.json.gz'
            dest.write_bytes(gzip.compress(payload, mtime=0))
            info['providers'][tag] = dict(input_sha256=sha256(src.read_bytes()).hexdigest(),
                payload_sha256=sha256(payload).hexdigest(), word=str(dest), profile=other_info['profile'])
        found.append(info)
        print('CANDIDATE', h, 'native', info['native_role'], info['old_frame'], '->', info['new_frame'],
              'support', info['image_support'], 'profile', info['profile'], flush=True)
    result = dict(status='PASS_EXACT_RETURNING_PREFIX_SCREEN', parity=args.parity,
        eligible_helpers=eligible, candidates=found,
        scope='Exact local prefix release and monotone frame/profile screen; full native compilation and owner invoice remain separate.')
    (args.out/'SCREEN.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('CANDIDATES', len(found), flush=True)


if __name__ == '__main__':
    main()
