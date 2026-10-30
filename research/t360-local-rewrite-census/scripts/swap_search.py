#!/usr/bin/env python3
"""Commutation (retiming) search: move one scalar gate across a block of gates
it commutes with exactly (over arbitrary dirty inputs), so that some register's
chronological frame chain is reordered; then re-solve all frames with
opt_frames.optimize and report any strict local-profile saving.

Commutation of e1 = (t1 += c1 s1) and e2 = (t2 += c2 s2): exact iff t1 != s2
and t2 != s1.  Scale gates and warps commute with gates not touching their
register.  Only moves that change some register's chain order are tried.
"""
import argparse, json, gzip, time
from copy import deepcopy
from pathlib import Path
from collections import Counter
from fanout_search import read, expand, regs
from opt_frames2 import optimize


def commute(e, f):
    if e[0] == 'warp' or f[0] == 'warp' or e[0] == 'scale' or f[0] == 'scale':
        re_ = {e[1]} if e[0] != 'add' else set(e[1:3])
        rf = {f[1]} if f[0] != 'add' else set(f[1:3])
        return not (re_ & rf)
    return e[1] != f[2] and f[1] != e[2]


def touch(e):
    return set(e[1:3]) if e[0] == 'add' else {e[1]}


def rebuild(w, name, es):
    out = deepcopy(w)
    if name == 'B':
        out['B'] = []
        for e in es:
            if e[0] == 'warp':
                out['warps'][e[2] - 1][0] = len(out['B'])
            else:
                out['B'].append(e)
    else:
        out[name] = es
    return out


def moves(es, lo_bound, kmax):
    n = len(es)
    for i in range(lo_bound, n):
        e = es[i]
        if e[0] != 'add':
            continue
        for direction in (1, -1):
            k = 0
            j = i + direction
            while lo_bound <= j < n:
                f = es[j]
                if not commute(e, f):
                    break
                if touch(e) & touch(f):
                    k += 1
                    yield i, j, direction
                    if k >= kmax:
                        break
                j += direction


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--word', type=Path, required=True)
    ap.add_argument('--section', choices=('A', 'B', 'restore'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--kmax', type=int, default=3)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--stride', type=int, default=1)
    a = ap.parse_args()
    w = read(a.word)
    sec = expand(w)
    es = sec[a.section]
    lo_bound = w['prelude_events'] if a.section == 'A' else 0
    a.out.mkdir(parents=True, exist_ok=True)
    stats = Counter(); found = []; t0 = time.monotonic(); seen = set()
    allmoves = list(moves(es, lo_bound, a.kmax))
    print('MOVES', len(allmoves), flush=True)
    for idx, (i, j, d) in enumerate(allmoves):
        if idx % a.stride != a.start:
            continue
        new = list(es)
        g = new.pop(i)
        new.insert(j, g)  # forward: after original j (indices shift); backward: before original j
        key = tuple(map(lambda x: json.dumps(x), new[min(i, j):max(i, j) + 1]))
        if key in seen:
            continue
        seen.add(key)
        nw = rebuild(w, a.section, new)
        stats['attempted'] += 1
        try:
            nw, res = optimize(nw)
        except (ValueError, AssertionError) as exc:
            stats['fail'] += 1
            continue
        stats['feasible'] += 1
        if res['saving'] > 1e-9:
            ident = f'{a.section}-{i}-{j}'
            rec = dict(id=ident, i=i, j=j, gate=es[i], across=es[j], delta=res['delta'], saving=res['saving'])
            found.append(rec)
            (a.out / f'WORD-{ident}.json.gz').write_bytes(gzip.compress(json.dumps(nw, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
            print('FOUND', json.dumps(rec), flush=True)
        if stats['attempted'] % 100 == 0:
            print('PROGRESS', idx, dict(stats), round(time.monotonic() - t0, 1), flush=True)
    (a.out / f'RESULT-{a.start}.json').write_text(json.dumps(dict(stats=dict(stats), found=found, moves=len(allmoves)), indent=1))
    print('DONE', dict(stats), 'found', len(found), flush=True)


if __name__ == '__main__':
    main()
