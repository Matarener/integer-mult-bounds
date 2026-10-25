"""Exact dependency poset of the PR4610 round-three local scalar program.

Ops = every non-climb, non-marker event (scalar add/scale/copy/clear, warp, centre).
Per register R each op touching R is typed:
  T : ADD with target R          (T,T commute: a+=cb, a+=de)
  S : ADD/copy with source R     (S,S commute)
  X : anything else on R (scale, warp, clear, copy target, centre, C-frame ops) - exclusive.
Two ops conflict iff they share a register with types not in {(T,T),(S,S)}.
This is exactly the commutation relation of the ops as linear maps on generic data
(warps/scales assumed generic) -- ADD a+=cb vs d+=ef commute iff a!=f and d!=b.
Group structure: per register consecutive maximal runs of one commuting type;
every op of group k depends on every op of group k-1 (stored via hub nodes).
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from load import *

def reg_types(e):
    """[(reg, type)] with reg = ('L',i) / ('C',i)."""
    k = e[0]
    if k == 'scalar':
        g = e[1]
        if g[0] == 'add':
            return [(tuple(g[1]), 'T'), (tuple(g[2]), 'S')]
        if g[0] == 'copy':
            return [(tuple(g[1]), 'X'), (tuple(g[2]), 'S')]
        return [(tuple(g[1]), 'X')]
    if k == 'warp':
        return [(tuple(e[1]), 'X')]
    if k == 'center':
        return [(('C', e[1]), 'X')]
    return []

def build(w, side='forward'):
    p = [e for e in w['programs'][side] if e[0] not in ('climb', 'phase', 'adapter', 'residual_adapter')]
    groups = defaultdict(list)          # reg -> list of [type, [op ids]]
    for i, e in enumerate(p):
        for r, t in reg_types(e):
            g = groups[r]
            if g and g[-1][0] == t and t != 'X':
                g[-1][1].append(i)
            else:
                g.append([t, [i]])
    return p, groups

def preds_succs(p, groups):
    """Immediate-group dependency lists: for op i, list of (reg, group index)."""
    pos = defaultdict(dict)  # op -> reg -> group index
    for r, gl in groups.items():
        for k, (t, ops) in enumerate(gl):
            for i in ops:
                pos[i][r] = k
    return pos

def basis_of(vecs):
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    return piv

def join(*bases):
    piv = {}
    for b in bases:
        for v in b:
            while v:
                h = v.bit_length() - 1
                if h in piv:
                    v ^= piv[h]
                else:
                    piv[h] = v
                    break
    return tuple(sorted(piv.values()))

def meet(a, b):
    sa, sb = span(a), span(b)
    return join(sa & sb)

def bounds(w, p, groups, relax_warps=True):
    """Subspace lower/upper bound for every op frame valid for EVERY linear extension.
    Warps: if relax_warps, warp output/input frames are free of the same dim (dims only
    propagate through them). Ops touching C are pinned to their current frames."""
    c = w['canonical']; fr = c['frames']
    pos = preds_succs(p, groups)
    FULL = tuple(1 << i for i in range(9))
    n = len(p)
    pinned = {}
    for i, e in enumerate(p):
        if e[0] == 'center' or (e[0] == 'scalar' and any(r[0] == 'C' for r, _ in reg_types(e))):
            f = e[2] if e[0] == 'scalar' else None
            if f is not None:
                pinned[i] = tuple(fr[f])
    lows = [None]*n; lowd = [0]*n      # for warps lows = input frame bound
    for i, e in enumerate(p):
        parts = []; d = 0
        for r, k in pos[i].items():
            if r[0] == 'C':
                continue
            if k == 0:
                parts.append(tuple(fr[c['start'][r[1]]]))
            else:
                for j in groups[r][k-1][1]:
                    if p[j][0] == 'warp' and relax_warps:
                        d = max(d, lowd[j])
                    elif p[j][0] == 'warp':
                        parts.append(tuple(fr[p[j][4]]))
                    else:
                        parts.append(lows[j])
        if i in pinned:
            parts.append(pinned[i])
        lows[i] = join(*parts); lowd[i] = max(d, len(lows[i]))
    ups = [None]*n; upd = [9]*n
    for i in range(n-1, -1, -1):
        e = p[i]; cur = FULL; d = 9
        for r, k in pos[i].items():
            if r[0] == 'C':
                continue
            gl = groups[r]
            if k == len(gl)-1:
                cur = meet(cur, tuple(fr[c['final'][r[1]]]))
            else:
                for j in gl[k+1][1]:
                    if p[j][0] == 'warp' and relax_warps:
                        d = min(d, upd[j])
                    elif p[j][0] == 'warp':
                        cur = meet(cur, tuple(fr[p[j][3]]))
                    else:
                        cur = meet(cur, ups[j])
        if i in pinned:
            cur = meet(cur, pinned[i])
        ups[i] = cur; upd[i] = min(d, len(cur))
    return lows, lowd, ups, upd, pinned

def cur_frame_dim(w, e):
    fr = w['canonical']['frames']
    if e[0] == 'scalar':
        return len(fr[e[2]])
    if e[0] == 'warp':
        return len(fr[e[3]])
    return None
