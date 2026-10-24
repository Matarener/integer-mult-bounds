import io, json, tarfile, itertools
from pathlib import Path
import numpy as np
H = Path(__file__).parent / 'inputs'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
def load_geometry():
    with tarfile.open(H/'selected-replay.tar.gz') as a: data = json.loads(a.extractfile(a.getmember(MEMBER)).read())
    pairs = json.loads((H/'PR1825-CERTIFICATE.json').read_text())['matching']
    labels = [r['q'] for r in data['recipes']]
    return labels, pairs
dot = lambda x, y: (x & y).bit_count() & 1
def lead(b): return 1 << (b.bit_length() - 1)
def reduce(basis, v):
    for b in basis:
        if v & lead(b): v ^= b
    return v
def add(basis, v):
    basis = list(basis); v = reduce(basis, v)
    if not v: return tuple(basis)
    L = lead(v); basis = [b ^ v if b & L else b for b in basis] + [v]
    return tuple(sorted(basis, reverse=True))
def span(vs):
    s = ()
    for v in vs: s = add(s, v)
    return s
def contains(s, v): return reduce(s, v) == 0
def pair_rank(A, B):
    """rank over F2 of the pairing matrix between bases A and B"""
    rows = [sum(dot(x, y) << k for k, y in enumerate(B)) for x in A]
    r = 0
    for bit in range(len(B)):
        piv = next((i for i in range(r, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None: continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> bit & 1: rows[i] ^= rows[r]
        r += 1
    return r
