"""Shared loader for the PR4610 round-three native word (run from ~/imb-r13)."""
import gzip, json
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path.home()/'imb-r13'
WORD = ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'

def load():
    w = json.loads(gzip.decompress(WORD.read_bytes()))
    return w

def span(basis):
    s = {0}
    for v in basis:
        if v not in s:
            s |= {x ^ v for x in tuple(s)}
    return frozenset(s)

def roles(e):
    if e[0] == 'scalar':
        g = e[1]
        return [r[1] for r in (g[1:3] if g[0] in ('add', 'copy') else g[1:2]) if r[0] == 'L']
    return [e[1][1]] if e[0] == 'warp' else []
