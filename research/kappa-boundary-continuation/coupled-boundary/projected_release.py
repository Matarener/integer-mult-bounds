#!/usr/bin/env python3
"""Find exact protected-output-preserving delayed dirty helper releases.

Searches a literal BORROW-WORD in the free algebra of its actual warp symbols.
The protected projection comprises all 112 Y ports and all 91 hyperplane-ended
helpers. A candidate is not a completed native word: its FULL endpoint error
must still be repaired and compiled. Apache-2.0; substantial OpenAI assistance.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys

from retime_return import read, basis, regs, add, native_profile, column_prefix


def suffix_columns(w, cuts):
    protected = list(range(112, 224)) + sorted(map(int, w['helper_final']))
    cols = [{} for _ in range(704)]
    for r in protected:
        cols[r] = {(r, ()): Q(1)}

    def backward(e):
        nonlocal cols
        if e[0] == 'add':
            r, s, a, b = e[1:5]
            cols[s] = cols[s].copy()
            add(cols[s], cols[r], Q(a, b))
        elif e[0] == 'scale':
            r, a, b = e[1:4]
            cols[r] = {k: v*Q(a, b) for k, v in cols[r].items()}
        elif e[0] == 'warp':
            r, op = e[1:3]
            cols[r] = {(s, v[:-1] if v and v[-1] == -op else v+(op,)): q
                       for (s, v), q in cols[r].items()}
        else:
            raise ValueError(e[0])

    for e in reversed(w['restore']):
        backward(e)
    warps = defaultdict(list)
    for op, (p, r, G, f0, f1) in enumerate(w['warps'], 1):
        warps[p].append(['warp', r, op, f0, f1])
    out = {}
    for p in range(len(w['B']), -1, -1):
        if p < len(w['B']):
            backward(w['B'][p])
        for e in reversed(warps[p]):
            backward(e)
        if p in cuts:
            out[p] = cols.copy()
    return out, protected


def next_frames(w):
    full = basis(1 << k for k in range(9))
    nxt = [full]*704
    for r in range(112, 224):
        nxt[r] = basis(x for x in range(512) if not ((x & w['ports'][r-112]).bit_count() % 2))
    for r, f in w['helper_final'].items():
        nxt[int(r)] = basis(f)
    for e in reversed(w['restore']):
        for r in regs(e):
            if r < 704:
                nxt[r] = basis(e[-1])
    warps = defaultdict(list)
    for op, (p, r, G, f0, f1) in enumerate(w['warps'], 1):
        warps[p].append((r, f0))
    out = {}
    for p in range(len(w['B']), -1, -1):
        if p < len(w['B']):
            for r in regs(w['B'][p]):
                if r < 704:
                    nxt[r] = basis(w['B'][p][-1])
        for r, f0 in reversed(warps[p]):
            nxt[r] = basis(f0)
        out[p] = nxt.copy()
    return out


def solution(columns, target):
    """An exact sparse column-basis solve, retaining a rational witness."""
    piv = {}
    for r, c in columns:
        c, expr = c.copy(), {r: Q(1)}
        while c:
            k = max(c)
            if k not in piv:
                q = c[k]
                c = {j: v/q for j, v in c.items()}
                expr = {j: v/q for j, v in expr.items()}
                piv[k] = c, expr
                break
            q = c[k]
            b, ex = piv[k]
            add(c, b, -q)
            add(expr, ex, -q)
    c, answer = target.copy(), {}
    while c:
        k = max(c)
        if k not in piv:
            return None
        q = c[k]
        b, ex = piv[k]
        add(c, b, -q)
        add(answer, ex, q)
    return answer


def pair_solutions(columns, target):
    coeffs = [Q(1,4),Q(-1,4),Q(1,2),Q(-1,2),Q(1),Q(-1),Q(2),Q(-2),Q(4),Q(-4)]
    def key(c):
        return tuple(sorted(c.items()))
    scaled = defaultdict(list)
    for r,c in columns:
        for q in coeffs:
            scaled[key({k:q*v for k,v in c.items()})].append((r,q))
    seen = set()
    for r,q in scaled.get(key(target),[]):
        seen.add(((r,q),))
        yield {r:q}
    for r,c in columns:
        for q in coeffs:
            residual = target.copy()
            add(residual,c,-q)
            for s,t in scaled.get(key(residual),[]):
                if s == r:
                    continue
                signature = tuple(sorted([(r,q),(s,t)]))
                if signature not in seen:
                    seen.add(signature)
                    yield dict(signature)


def eligible(w):
    for h in range(224, 704):
        if h in w['removed']:
            continue
        old = basis(w['start_extra'].get(str(h), []))
        if not old:
            continue
        if any(h in regs(e) for part in ('A', 'precondition', 'compensation') for e in w[part]):
            continue
        if any(h in (x['source'], x['target']) for x in w['initial_corrections']):
            continue
        first = next((i for i, e in enumerate(w['B']) if e[1] == h), None)
        if first is None:
            continue
        early = [i for i, e in enumerate(w['B'][:first]) if e[0] == 'add' and e[2] == h]
        if early:
            yield h, old, first, early


def target_for(h, col, suffix):
    target = {}
    for r, row in enumerate(col):
        row = row.copy()
        if r == h:
            add(row, {(h, ()): Q(1)}, Q(-1))
        for (hh, word), q in row.items():
            assert hh == h
            for (out, sw), v in suffix[r].items():
                # The released input h follows the B-prefix operator word.
                joined = list(sw)
                for op in word:
                    if joined and joined[-1] == -op:
                        joined.pop()
                    else:
                        joined.append(op)
                key = out, tuple(joined)
                target[key] = target.get(key, Q(0)) + q*v
                if not target[key]:
                    del target[key]
    return target


def mutate(w, h, old, first, early, cut, frame, release, snapshots, drop_reads=False):
    z = deepcopy(w)
    z['start_extra'][str(h)] = list(frame)
    gates = [['add', r, h, q.numerator, q.denominator, list(frame)]
             for r, q in sorted(release.items()) if q]
    if drop_reads:
        gone = set(early)
        z['B'] = [e for i,e in enumerate(z['B']) if i not in gone]
        new_cut = cut-sum(i<cut for i in gone)
        z['B'][new_cut:new_cut] = gates
        for e in z['warps']:
            e[0] = e[0]-sum(i<e[0] for i in gone) + (len(gates) if e[0]>=cut else 0)
    else:
        for i in early:
            e = z['B'][i]
            z['B'][i] = ['scale', e[1], 1, 1, e[-1]]
        z['B'][cut:cut] = gates
        for e in z['warps']:
            if e[0] >= cut:
                e[0] += len(gates)
    profile, _ = native_profile(z)
    z['report']['local_profile'] = profile
    return z, gates, profile


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word', type=Path)
    ap.add_argument('--followup', type=Path)
    ap.add_argument('--all-cuts', action='store_true')
    ap.add_argument('--any-cut', action='store_true')
    ap.add_argument('--same-entry', action='store_true')
    ap.add_argument('--helper', type=int)
    ap.add_argument('--drop-reads', action='store_true')
    ap.add_argument('--exact-entry', action='store_true')
    ap.add_argument('--pair-only', action='store_true')
    ap.add_argument('--full-ended-only', action='store_true')
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'projected-release')
    a = ap.parse_args()
    source = a.word or a.followup/'artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz'
    w = read(source)
    profile, snapshots = native_profile(w)
    candidates = list(eligible(w))
    if a.helper is not None:
        candidates = [x for x in candidates if x[0] == a.helper]
    if a.full_ended_only:
        candidates = [x for x in candidates if str(x[0]) not in w['helper_final']]
    cuts = {p for _, _, first, early in candidates for p in (range(0 if a.any_cut else max(early)+1, first+1) if a.all_cuts else [first])}
    suffixes, protected = suffix_columns(w, cuts)
    nexts = next_frames(w)
    print('ELIGIBLE', len(candidates), 'CUTS', len(cuts), 'PROTECTED', len(protected), flush=True)
    a.out.mkdir(parents=True, exist_ok=True)
    found, tried = [], 0
    removed = set(w['removed'])
    for h, old, first, early in candidates:
        first_frame = basis(w['B'][first][-1])
        helper_snapshots, helper_nexts = snapshots, nexts
        if a.drop_reads:
            shadow = deepcopy(w)
            for i in early:
                # Geometry-only no-op on an absent scratch, preserving B
                # indices. This shadow is never emitted as a native word.
                shadow['B'][i] = ['scale', 704, 1, 1, []]
            try:
                _, helper_snapshots = native_profile(shadow)
                helper_nexts = next_frames(shadow)
            except ValueError:
                pass
        helper_cuts = range(0 if a.any_cut else max(early)+1, first+1) if a.all_cuts else [first]
        col = column_prefix(w, h, first)
        if col[h] != {(h, ()): Q(1)}:
            continue
        target = target_for(h, col, suffixes[first])
        for cut in reversed(list(helper_cuts)):
            # h is never written before first. Removing every early h read
            # changes only the h column. A donor r != h never feeds h before
            # first, so its suffix column is unchanged by those deletions.
            del_reads = early
            allowed = first_frame
            suffix = suffixes[cut]
            frames = {basis(old+(x,)) for x in _span(allowed)}
            frames.add(allowed)
            if a.exact_entry:
                frames = {old}
            if not a.same_entry:
                frames.discard(old)
            groups = {}
            for f in frames:
                if len(f) < len(old) or (len(f) == len(old) and not a.same_entry):
                    continue
                donors = [r for r, cur in enumerate(helper_snapshots[cut])
                          if r != h and r not in removed and basis(cur+f) == f
                          and basis(f+helper_nexts[cut][r]) == helper_nexts[cut][r]]
                def phi(n):
                    return n**(1-0.0017305784372662468) if n else 0.0
                donors.sort(key=lambda r: (phi(len(f)-len(helper_snapshots[cut][r]))
                            + phi(len(helper_nexts[cut][r])-len(f))
                            - phi(len(helper_nexts[cut][r])-len(helper_snapshots[cut][r])), r))
                groups[f] = donors
            if not target:
                groups[allowed] = []
            for frame, donors in sorted(groups.items(), key=lambda x: (-len(x[0]), len(x[1]))):
                tried += 1
                if a.pair_only:
                    releases = list(pair_solutions([(r,suffix[r]) for r in donors],target))
                    ranked = []
                    for release in releases:
                        try:
                            z,gates,new_profile = mutate(w,h,old,first,del_reads,cut,frame,release,snapshots,a.drop_reads)
                        except ValueError:
                            continue
                        bill = sum(n*r**(1-0.0017305784372662468) for r,n in new_profile.items())
                        ranked.append((bill,release))
                    if not ranked:
                        continue
                    release = min(ranked,key=lambda x:x[0])[1]
                else:
                    release = solution([(r, suffix[r]) for r in donors], target)
                    if release is None or any(q.denominator & (q.denominator-1) for q in release.values()):
                        continue
                # Check the equation independently of the elimination witness.
                check = {}
                for r, q in release.items():
                    add(check, suffix[r], q)
                assert check == target
                try:
                    z, gates, new_profile = mutate(w, h, old, first, del_reads, cut, frame, release, snapshots, a.drop_reads)
                except ValueError:
                    continue
                if frame == old and sum(n*r**(1-0.0017305784372662468) for r,n in new_profile.items()) >= sum(n*r**(1-0.0017305784372662468) for r,n in profile.items())-1e-9:
                    continue
                kept = [r for r in range(224, 704) if r not in removed]
                info = dict(helper=h, native_role=224+kept.index(h), cut=cut,
                    first_producer=first, deleted_reads=del_reads, old_frame=list(old), new_frame=list(frame),
                    inserted_gates=gates, profile=new_profile, projected_target_terms=len(target),
                    protected_outputs=protected, release={str(r): str(q) for r,q in release.items()},
                    status='PASS_PROTECTED_PROJECTION_ONLY_FULL_REPAIR_NOT_YET_EMITTED')
                stem = f'RELEASE-{h}-{cut}-{len(found)}'
                dest = a.out/f'{stem}.json.gz'
                dest.write_bytes(gzip.compress(json.dumps(z, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
                info['word'] = str(dest)
                found.append(info)
                (a.out/f'{stem}-WITNESS.json').write_text(json.dumps(info, indent=2, sort_keys=True)+'\n')
                print('FOUND', json.dumps(info, sort_keys=True), flush=True)
                # One best frame at one cut per helper is enough for downstream
                # completion. Every hit is checked again by the native compiler.
                break
            else:
                continue
            break
    result = dict(status='PASS_EXACT_PROTECTED_RELEASE_SCREEN', input_word=str(source),
        eligible_helpers=[h for h, _, _, _ in candidates], all_cuts=a.all_cuts,
        groups_tried=tried, candidates=found, protected_outputs=protected,
        scope='Only the protected projection and literal monotone frame bill are checked. FULL cleanup completion, native replay, physical allocation and kappa are not asserted.')
    (a.out/'SCREEN.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('DONE', len(found), 'candidates', tried, 'groups', flush=True)


def _span(vs):
    out = {0}
    for v in vs:
        out |= {x^v for x in out}
    return out


if __name__ == '__main__':
    main()
