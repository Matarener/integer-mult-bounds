"""Integer T360 owner fill for a given clock (construction provenance; not run by verify.py).

Requires numpy, scipy and highspy (see ../README.md). Comments are in French.
Usage from the repository root:
  python construction/build_fill.py research/staged544-clock-ceiling/inputs/ORDER.json --out DIR --distinct 40

Rangement entier T360 pour une horloge donnée, puis contrôle par owner_audit.py.

1. PL de Hall (hall_lp) : motifs par classe ; on exige une solution entière (sinon arrêt).
2. Cases : les 224 cases d'une classe reçoivent les motifs de la classe, dans l'ordre.
3. Objets, instant par instant : chaque objet de largeur w va à la classe ouverte d'échéance
   la plus proche (EDF) qui a encore une place de largeur w dans une case que cet appel n'a pas
   encore touchée (un objet par appel et par case). Les cases d'une classe sont parcourues en
   tourniquet pour étaler les appels.
4. FILL (colonnes, ordre (t, h), décalage chronologique), ORDER et PROFILE écrits dans une copie
   du paquet ; owner_audit.py y est rejoué tel quel.
"""
import argparse
import gzip
import heapq
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import hall_mixed as H  # noqa: E402

PKG = Path('/tmp/claude-0/rs/research/staged544-mixed-fourth-entry')
sys.path.insert(0, str(PKG)); sys.argv_saved = sys.argv; sys.argv = ['x']
import owner_verify as OV
from verify import read as vread
sys.argv = sys.argv_saved


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def rank(U):
    piv = {}
    for x in U:
        while x:
            b = x.bit_length()
            if b in piv:
                x ^= piv[b]
            else:
                piv[b] = x
                break
    return len(piv)


def windows_for(order, template, children):
    """Fenêtres (cap, lo, hi) par (propriétaire, enfant), avec la logique d'owner_audit."""
    clock = {tuple(v): i for i, v in enumerate(order)}
    win = {}
    for owner in range(H.T):
        touched = {}
        t = None
        for ev in template['execution_schedule']:
            k = ev['kind']
            if k in ('bank_padding_cover_sweep', 'translate_every_live_family'):
                continue
            if k == 'local_cover_sweep':
                t = clock[ev['stage'], owner]
                touched[next(x['pair'] for x in template['recipe'] if x['kind'] == 'local' and x['stage'] == ev['stage'])] = t
            elif k == 'bridge':
                touched[ev['src']] = t
                touched[ev['dst']] = t
            elif k == 'idle_cover_sweep':
                for c in ev['child_indices']:
                    if c in children:
                        win[owner, c] = (children[c], touched.get(ev['pair'], -1), t)
    return win


def build(order_path, out_dir, seed=0, distinct=0):
    order = H.read_order(order_path)
    template = read(PKG / 'owner/TEMPLATE.json.gz')
    children = {c['child']: c['rank'] for c in template['idle_children']}
    win = windows_for(order, template, children)
    four = json.load(open(SEL)); H.set_selector(four)
    # per-provider widths from the exact words (owner_verify logic)
    I = OV.I; widths = {}
    for kind in ('THREE', 'FOUR'):
        w = vread(PKG / f'inputs/{kind}-base.json.gz'); origin = vread(PKG / 'owner/old-NATIVE-base.json.gz')['helper_origin']
        widths[kind] = [len(I.b(w['helper_final'].get(str(r), I.FULL))) - len(I.b(w['start_extra'].get(str(r), []))) for r in origin]
        w2 = vread(PKG / f'inputs/{kind}-extra.json.gz'); origin2 = vread(PKG / 'owner/old-NATIVE-extra.json.gz')['helper_origin']
        assert [len(I.b(w2['helper_final'].get(str(r), I.FULL))) - len(I.b(w2['start_extra'].get(str(r), []))) for r in origin2] == widths[kind]
    lp = H.HallLP(order, a=0.0017309791156708, verbose=False)
    if distinct:
        lp.add_distinct(range(H.N - distinct, H.N))
    lp.run()
    r_lp = H.root(lp.profile())
    print(f'PL : racine {r_lp:.16f}', flush=True)
    y = lp.x[lp.first_y:]
    pats = defaultdict(list)                           # classe -> liste de motifs (224)
    for (k, j), v in zip(lp.cols, y):
        n = int(round(v))
        if abs(v - n) > 1e-6:
            raise SystemExit(f'solution fractionnaire en classe {k}')
        if n:
            pats[k] += [tuple(int(a) for a in H.PATS[lp.cap[k]][0][j])] * n
    assert all(len(pats[k]) == H.BINS for k in range(lp.K))

    # classe du PL -> enfants (deux enfants de 112 ports chacun)
    key_of = {(k // 9, int(lp.cap[k]), int(lp.lo[k]), int(lp.hi[k])): k for k in range(lp.K)}
    kids = defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        kids[key_of[o, cap, lo, hi]].append(c)
    assert all(len(v) == 2 for v in kids.values()) and len(kids) == lp.K
    for k in kids:
        kids[k].sort()

    W = list(H.W)
    K = lp.K
    lo_k = np.array([int(lp.lo[k]) for k in range(K)])
    hi_k = np.array([int(lp.hi[k]) for k in range(K)])
    free = np.zeros((K, H.BINS, 6), dtype=np.int16)      # places libres par case et largeur
    for k in range(K):
        free[k] = np.array(pats[k], dtype=np.int16)
    demand = free.sum(1).astype(np.int64)                 # places libres par classe et largeur
    ftot = free.sum(2).astype(np.int64)                   # places libres par case
    used_by = np.full((K, H.BINS), -1, dtype=np.int32)   # dernier appel ayant touché la case
    placed = defaultdict(list)                            # (k, b) -> [(t, h, w)]
    closing = defaultdict(list)
    for k in range(K):
        closing[int(hi_k[k])].append(k)
    pool = np.where(lo_k < 0)[0]                          # classes (-1, hi] : réservoir du début
    in_pool = np.zeros(len(pool), dtype=bool)
    pool_pos = {int(k): i for i, k in enumerate(pool)}
    heaps = [[] for _ in range(6)]
    hof = {kind: [[h for h in range(408) if widths[kind][h] == w] for w in W] for kind in widths}
    rng = np.random.default_rng(seed)
    jitter = rng.random((K, H.BINS)) * 0.5                # départage des cases à égalité

    def take(k, bins, t, wi, hs):
        for b, h in zip(bins, hs):
            free[k, b, wi] -= 1
            ftot[k, b] -= 1
            used_by[k, b] = t
            placed[k, int(b)].append((t, h, W[wi]))
        demand[k, wi] -= len(bins)

    # À rebours : une classe devient disponible à t = hi et doit être servie avant t = lo.
    for t in range(H.N - 1, -1, -1):
        for k in closing.get(t, ()):
            if lo_k[k] < 0:
                in_pool[pool_pos[k]] = True
            else:
                for wi in range(6):
                    if demand[k, wi]:
                        heapq.heappush(heaps[wi], (-int(lo_k[k]), int(hi_k[k]), k))
        for wi in range(6):
            hs = list(hof['FOUR' if four[t] else 'THREE'][wi])
            hp = heaps[wi]
            aside = []
            while hs and hp:
                neglo, _, k = hp[0]
                if demand[k, wi] == 0:
                    heapq.heappop(hp)
                    continue
                if -neglo >= t:
                    raise SystemExit(f'échéance manquée : classe {k} largeur {W[wi]} reste {demand[k, wi]} à t={t}')
                elig = np.where((free[k, :, wi] > 0) & (used_by[k] != t))[0]
                n = min(len(hs), int(demand[k, wi]), len(elig))
                if n == 0:
                    aside.append(heapq.heappop(hp))
                    continue
                pick = elig[np.argsort(-(ftot[k, elig] + jitter[k, elig]))[:n]]
                take(k, pick, t, wi, hs[:n])
                hs = hs[n:]
                if demand[k, wi] and hs:
                    aside.append(heapq.heappop(hp))
            for item in aside:
                heapq.heappush(hp, item)
            if hs:
                ks = pool[in_pool]
                fr = free[ks, :, wi]
                ok = (fr > 0) & (used_by[ks] != t)
                score = np.where(ok, ftot[ks] + jitter[ks], -1.0)
                flat = score.ravel()
                n = len(hs)
                if (flat >= 0).sum() < n:
                    raise SystemExit(f'réservoir à court : t={t} largeur {W[wi]} besoin {n}')
                top = np.argpartition(-flat, n - 1)[:n]
                by_class = defaultdict(list)
                for f in top:
                    by_class[int(ks[f // H.BINS])].append(int(f % H.BINS))
                pos = 0
                for k, bins in by_class.items():
                    take(k, bins, t, wi, hs[pos:pos + len(bins)])
                    pos += len(bins)
        for k in np.where(lo_k == t)[0]:
            if demand[k].any():
                raise SystemExit(f'classe {k} fermée incomplète à t={t} : {demand[k]}')
    assert demand.sum() == 0
    rows = [None] * (H.N * 408)
    load = np.zeros((K, H.BINS), dtype=np.int16)
    for (k, b), items in placed.items():
        z = 0
        for t, h, w in sorted(items):
            rows[t * 408 + h] = [int(t), int(h), int(k) // 9, int(kids[k][b // 112]), int(b) % 112, int(z)]
            z += w
        load[k, b] = z
    assert demand.sum() == 0 and all(r is not None for r in rows)

    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / 'FILL.json.gz').write_bytes(gzip.compress(json.dumps({'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'dispatch_overrides': [], 'rows': rows}).encode(), mtime=0))
    idle = Counter()
    caps = np.array([lp.cap[k] for k in range(K)])
    left = caps[:, None] - load
    for v in left.ravel():
        if v:
            idle[int(v)] += 1
    n4 = int(sum(four)); prof = Counter({r: (H.N - n4) * H.LOC3.get(r, 0) + n4 * H.LOC4.get(r, 0) for r in set(H.LOC3) | set(H.LOC4)})
    prof.update(idle)
    (out / 'PROFILE.json').write_text(json.dumps({str(r): n for r, n in sorted(prof.items())}))
    r_int = H.root(dict(prof))
    print(f'entier : racine {r_int:.16f}  restes inactifs {dict(sorted(idle.items()))}', flush=True)
    return out, r_int


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('order')
    ap.add_argument('--out', required=True)
    ap.add_argument('--distinct', type=int, default=0)
    ap.add_argument('--sel', required=True)
    args = ap.parse_args(); SEL = args.sel
    out, r = build(args.order, args.out, distinct=args.distinct)
