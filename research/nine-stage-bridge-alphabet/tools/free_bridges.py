#!/usr/bin/env python3
"""Search for K extra "free" bridges inserted into the simple-riding designs of one idle alphabet.

A bridge between pairs i, j inserted before stage g is free (creates no new idle child) when both pairs
can be presented at a common level that is their current level (last touch) or the entry level of
their next touch. Every combination of K such bridges (coefficient +-1) is inserted and tested with
the exact closure test. Recorded runs: evidence/free-bridges-k1.log, evidence/free-bridges-k2*.log.

  python3 -B tools/free_bridges.py --k 1 --alphabet 8,8,8,8,16,32,40,48,48 [--start N] [--workers W]
Long run (K=2 is about 2.6 million closure tests); progress is appended to the log and --start resumes.
"""
import argparse, itertools, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bridges as B  # noqa: E402


def touches(d):
    T = {p: [] for p in range(4)}
    riders = {s: [] for s in range(9)}
    for p, ss in enumerate(d['riders']):
        for s in ss:
            riders[s].append(p)
    for s in range(9):
        T[d['owners'][s]].append((s + 0.5, s - 1, s))
        for r in riders[s]:
            T[r].append((s + 0.5, s - 1, s - 1)); T[r].append((s + 0.6, s, s))
    return T


def free_options(d):
    T = touches(d); opts = []
    for g in range(9):
        lv = {}
        for p in range(4):
            past = [t for t in T[p] if t[0] < g]; fut = [t for t in T[p] if t[0] > g]
            lv[p] = {past[-1][2] if past else -1, fut[0][1] if fut else 8}
        for i in range(4):
            for j in range(4):
                if i != j and lv[i] & lv[j]:
                    opts += [(g, i, j, 1), (g, i, j, -1)]
    return opts


def build_with(d, extra):
    rec = []
    riders = {s: [] for s in range(9)}
    for p, ss in enumerate(d['riders']):
        for s in ss:
            riders[s].append(p)
    for s in range(9):
        rec += [{'kind': 'bridge', 'dst': i, 'src': j, 'coefficient': q} for (g, i, j, q) in extra if g == s]
        o = d['owners'][s]; rev = bool(d['dirs'][s])

        def br(r, q):
            return ({'kind': 'bridge', 'dst': r, 'src': o, 'coefficient': q} if rev
                    else {'kind': 'bridge', 'dst': o, 'src': r, 'coefficient': q})
        rec += [br(r, 1) for r in riders[s]]
        rec.append({'kind': 'local', 'stage': s, 'pair': o, 'reverse': rev})
        rec += [br(r, -1) for r in reversed(riders[s])]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--k', type=int, default=1)
    ap.add_argument('--alphabet', default='8,8,8,8,16,32,40,48,48')
    ap.add_argument('--start', type=int, default=0)
    a = ap.parse_args()
    target = tuple(map(int, a.alphabet.split(',')))
    ds = [d for s, d in B.designs() if s == target]
    print(f'{len(ds)} designs with alphabet {target}', flush=True)
    tried = 0
    for i, d in enumerate(ds):
        if i < a.start:
            continue
        for extra in itertools.combinations(free_options(d), a.k):
            tried += 1
            if B.closure(build_with(d, list(extra))) is not None:
                print(f'FOUND design {i} extra {extra}', flush=True); return
        print(time.strftime('%H:%M:%S'), f'design {i} done, {tried} insertions tried', flush=True)
    print(f'none ({tried} insertions tried)')


if __name__ == '__main__':
    main()
