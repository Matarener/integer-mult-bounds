"""Geometry for the 56-plane decoder clique programme (certificate generation only; not the verifier)."""
import json, os, tarfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MATCHING = ROOT / 'research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json'
CACHE = Path(os.environ.get('PLANE_PORT_CACHE', '/tmp/plane-port-clique-floor-141'))


def dot(x, y):
    return bin(x & y).count('1') & 1


def planes():
    with tarfile.open(ARCHIVE) as a:
        labels = [r['q'] for r in json.loads(a.extractfile(a.getmember(MEMBER)).read())['recipes']]
    matching = json.loads(MATCHING.read_text())['matching']
    pl = [(labels[a], labels[b]) for a, b in matching]
    pel = [{0, x, y, x ^ y} for x, y in pl]
    orth = np.array([[i != j and all(dot(x, y) == 0 for x in pel[i] for y in pel[j]) for j in range(56)]
                     for i in range(56)])
    return pl, pel, orth


def census(pl):
    idx = np.arange(512)
    frontier = {}
    for x, y in pl:
        m = np.zeros(512, bool); m[[0, x, y, x ^ y]] = True; frontier[m.tobytes()] = m
    seen = dict(frontier)
    while frontier:
        F = np.array(list(frontier.values())); new = {}
        for x, y in pl:
            G = F | F[:, idx ^ x] | F[:, idx ^ y] | F[:, idx ^ x ^ y]
            for g in G:
                k = g.tobytes()
                if k not in seen:
                    seen[k] = g; new[k] = g
        frontier = new
    return np.array(sorted(seen.values(), key=lambda m: (m.sum(), m.tobytes())))


def load():
    """inside (n x 56 bool), tariff (n x n int8), orth (56 x 56 bool)"""
    CACHE.mkdir(parents=True, exist_ok=True)
    pl, pel, orth = planes()
    f = CACHE / 'geom.npz'
    if f.exists():
        z = np.load(f)
        return z['inside'], z['T'], orth
    S = census(pl)
    dim = np.log2(S.sum(1)).round().astype(np.int64)
    pmask = np.zeros((56, 512), bool)
    for i, e in enumerate(pel):
        pmask[i, list(e)] = True
    inside = (S.astype(np.int32) @ pmask.T.astype(np.int32)) == 4
    Dm = np.array([[dot(x, y) for y in range(512)] for x in range(512)], dtype=np.float32)
    perp = (S.astype(np.float32) @ Dm) == 0
    cnt = S.astype(np.float32) @ perp.T.astype(np.float32)          # |A meet R^perp|, exact (<= 512)
    T = (dim[:, None] - np.log2(cnt).round().astype(np.int64)).astype(np.int8)
    np.savez(f, inside=inside, T=T)
    return inside, T, orth
