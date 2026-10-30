#!/usr/bin/env python3
"""Review controls for the P104 fixed-cover support cut (PR3259) and its contract.

Standard library only.  Shares no code with PR3182, PR3252, PR3259 or PR3427.
Frames are GF(2) subspaces of F_2^n held as canonical reduced-echelon keys.

  P104   rebuilds frames, covers, the 2,309-edge pool and the 4,992 required
         entries; runs the channel word exactly (Y increment = G/2); replays
         PR3259's layered relaxation with a literal frame-hosting index
         (control) and evaluates the path-nested one-helper criterion (sharp
         untimed support) by two loop orders and by an independent full-memory
         recurrence in the manner of PR3252.
  ORACLE seeded random small instances: an exhaustive untimed reachability per
         instance, an explicit checked program for every reachable helper pair,
         and two random programs (one directed, run in the checked
         interpreter; one uniform, legal by construction), all with exact
         Fraction coefficients.
  ROWS   single-relaxation support rows (unpriced; operations counted).
  RANK   a maximum unsupported principal block of C (rank(U-I) >= 23 under
         PR3427's contract) and the matching number of the missing entries.
"""

import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    "research/p104-joint-unit-flags/CERTIFICATE.json":
        "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json":
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/inputs/P104-FIXTURE.json":
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
}


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


def axpy(dst, c, src):
    """dst += c * src on sparse Fraction vectors."""
    for k, v in list(src.items()):
        dst[k] = dst.get(k, 0) + c * v
        if dst[k] == 0:
            del dst[k]


# ---------------------------------------------------------------- GF(2) keys
def key(vectors):
    """Canonical reduced row-echelon basis (descending pivots) of a span."""
    rows = []
    for v in vectors:
        for r in rows:
            v = min(v, v ^ r)
        if v:
            rows = [min(r, r ^ v) for r in rows] + [v]
    return tuple(sorted(rows, reverse=True))


def le(small, big):
    """small <= big as subspaces (both canonical keys)."""
    return len(key(big + small)) == len(big)


def span_add(k, v):
    return key(k + (v,))


def subspaces(dim_space, k):
    """All k-dim subspaces of F_2^dim_space as tuples of basis vectors (RREF)."""
    out = []
    for piv in combinations(range(dim_space), k):
        free = [(i, j) for i, p in enumerate(piv) for j in range(p)
                if j not in piv]
        for code in range(1 << len(free)):
            rows = [1 << p for p in piv]
            for bit, (i, j) in enumerate(free):
                if code >> bit & 1:
                    rows[i] |= 1 << j
            out.append(tuple(rows))
    return out


# ---------------------------------------------------------------- P104 inputs
def load():
    data = {}
    for rel, digest in INPUTS.items():
        raw = (ROOT / rel).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, "input hash " + rel)
        data[rel] = json.loads(raw)
    return [data[r] for r in INPUTS]


def frame_paths(word):
    paths = {n: [key(b)] for n, b in word["initial_frames"].items()
             if n[0] in "XY"}
    for ev in word["program"]:
        if ev[0] == "transport" and ev[1][0] in "XY":
            old, new = key(ev[2]), key(ev[3])
            need(paths[ev[1]][-1] == old and le(old, new) and
                 len(new) == len(old) + ev[4], "monotone transport " + ev[1])
            paths[ev[1]].append(new)
    for n, b in word["final_frames"].items():
        need(n not in paths or paths[n][-1] == key(b), "final frame " + n)
    need(len(paths) == 208, "104 X and 104 Y paths")
    return paths


def channel_run(word, C):
    """Exact Fraction run of the channel word.  Checks that every add is at
    equal current frames, that each Y increment is X -> G/2 = I - C on the
    sorted ports with all helper dirt cancelled, and records which sources
    have a nonzero coefficient in each register at each of its frames."""
    frame, val, hist = {}, {}, {}

    def record(n):
        h = hist.setdefault(n, {})
        h[frame[n]] = h.get(frame[n], 0) | sum(
            1 << int(k[1:]) for k in val[n] if k[0] == "X")
    for n, b in word["initial_frames"].items():
        frame[n], val[n] = key(b), {n: Fraction(1)}
        record(n)
    first = None
    for i, ev in enumerate(word["program"]):
        op, n = ev[0], ev[1]
        if op == "transport":
            need(frame[n] == key(ev[2]), "channel transport from its frame")
            frame[n] = key(ev[3])
        elif op == "add":
            need(frame[n] == frame[ev[2]] == key(ev[4]),
                 "channel add at equal frames")
            axpy(val[n], Fraction(ev[3]), val[ev[2]])
            if first is None and n == "Y71" and "X102" in val[n]:
                first = [i, str(val[n]["X102"]), ev[2], len(frame[n])]
        elif op == "copy":
            need(frame[ev[2]] == key(ev[3]), "channel copy at its frame")
            frame[n], val[n] = key(ev[3]), dict(val[ev[2]])
        elif op == "zero":
            frame[n], val[n] = key(ev[2]), {}
        else:  # erase discards the private copy; it is never read again
            need(op == "erase", "known channel event")
            frame[n], val[n] = key(ev[2]), {}
            continue
        record(n)
    for t in range(104):
        inc = dict(val["Y%d" % t])
        axpy(inc, Fraction(-1), {"Y%d" % t: Fraction(1)})
        want = {"X%d" % s: Fraction(int(t == s)) - C[t][s]
                for s in range(104)}
        need(inc == {k: x for k, x in want.items() if x},
             "Y%d increment is exactly G/2 with dirt cancelled" % t)
    return hist, first


def channel_roles(word):
    """X is never written and Y never read by the original channel."""
    writes, reads = set(), set()
    for ev in word["program"]:
        if ev[0] in ("add", "copy"):
            writes.add(ev[1][0])
            reads.add(ev[2][0])
        elif ev[0] in ("zero", "erase"):
            writes.add(ev[1][0])
    need("X" not in writes and "Y" not in reads, "immutable X / unread Y")
    return sorted(writes), sorted(reads)


def hyperplane_of(cap, functional):
    vals = [(v & functional).bit_count() & 1 for v in cap]
    j = vals.index(1)
    return key([v ^ (cap[j] if vals[i] else 0)
                for i, v in enumerate(cap) if i != j])


def covers(cert, paths):
    L = [paths["X%d" % i][0] for i in range(104)]
    H = [paths["Y%d" % i][-1] for i in range(104)]
    need(all(len(x) == 1 for x in L) and all(len(h) == 8 for h in H), "ends")
    A = [span_add(L[a // 2], v) for a, v in enumerate(
        v for row in cert["forms"]["departure"] for v in row)]
    B = [hyperplane_of(H[b // 2], f) for b, f in enumerate(
        f for row in cert["forms"]["arrival"] for f in row)]
    need(len(A) == len(B) == 208, "208 slots")
    need(all(len(x) == 2 for x in A) and all(len(x) == 7 for x in B), "dims")
    edges = [(a, b) for a in range(208) for b in range(208) if le(A[a], B[b])]
    need(len(edges) == 2309, "2,309 compatible pairs")
    return L, A, B, H, edges


def e8_ports(fixture):
    """Positive E8 roots in doubled coordinates (first nonzero > 0)."""
    roots = []
    for v in product((-2, 0, 2), repeat=8):
        if sum(x * x for x in v) == 8:
            roots.append(v)
    for v in product((-1, 1), repeat=8):
        if v.count(-1) % 2 == 0:
            roots.append(v)
    roots = [r for r in roots if next(x for x in r if x) > 0]
    need(len(roots) == 120, "120 positive roots")
    drop = {tuple(r) for k in ("F0", "C")
            for r in fixture["section4_explicit_P104"][k]}
    ports = sorted(set(roots) - drop)
    need(len(ports) == 104, "104 ports")
    return ports


def required(ports):
    """C = I - G/8 (doubled roots): support and exact values."""
    n = len(ports)
    C = [[Fraction(int(t == s)) - Fraction(sum(
        x * y for x, y in zip(ports[t], ports[s])), 8) for s in range(n)]
        for t in range(n)]
    need(C[71][102] == Fraction(-1, 2), "C[71,102] = -1/2")
    need(sum(c != 0 for row in C for c in row) == 4992, "4,992 required")
    return C


# ------------------------------------------------- per-dimension intervals
def interval(L, A, B, H, edge, d):
    a, b = edge
    return {1: (L[a // 2], L[a // 2]), 2: (A[a], A[a]),
            7: (B[b], B[b]), 8: (H[b // 2], H[b // 2])}.get(d, (A[a], B[b]))


def admits(lo, hi, frame):
    return len(frame) >= len(lo) and len(frame) <= len(hi) and \
        le(lo, frame) and le(frame, hi)


def flats_between(lo, hi, d):
    """All d-dim keys F with lo <= F <= hi (literal enumeration)."""
    if lo == hi:
        return [lo]
    comp, cur = [], lo
    for v in hi:
        nxt = span_add(cur, v)
        if len(nxt) > len(cur):
            comp.append(v)
            cur = nxt
    need(cur == hi, "complement")
    out = []
    for sub in subspaces(len(comp), d - len(lo)):
        vecs = []
        for row in sub:
            w = 0
            for i in range(len(comp)):
                if row >> i & 1:
                    w ^= comp[i]
            vecs.append(w)
        out.append(key(lo + tuple(vecs)))
    return out


# --------------------------------------- PR3259 layered relaxation (control)
def layered(geo, paths):
    L, A, B, H, edges = geo
    n = len(edges)
    direct = [sum(1 << s for s in range(104)
                  if set(paths["X%d" % s]) & set(paths["Y%d" % t]))
              for t in range(104)]
    out, state, hist, rel, wr = direct[:], [0] * n, [], [], []
    for d in range(1, 9):
        ivs = [interval(L, A, B, H, e, d) for e in edges]
        hosts, mine = {}, []
        for i, (lo, hi) in enumerate(ivs):
            fl = flats_between(lo, hi, d)
            mine.append(fl)
            for f in fl:
                hosts[f] = hosts.get(f, 0) | 1 << i
        adj = []
        for fl in mine:
            m = 0
            for f in fl:
                m |= hosts[f]
            adj.append(m)
        reads = [0] * n
        writes = [0] * n
        for kind, acc in (("X", reads), ("Y", writes)):
            for s in range(104):
                for f in paths[kind + str(s)]:
                    if len(f) == d and f in hosts:
                        m = hosts[f]
                        while m:
                            low = m & -m
                            acc[low.bit_length() - 1] |= 1 << s
                            m ^= low
        seeded = [st | r for st, r in zip(state, reads)]
        state = seeded[:]
        for i in range(n):
            if seeded[i]:
                m = adj[i]
                while m:
                    low = m & -m
                    state[low.bit_length() - 1] |= seeded[i]
                    m ^= low
        for i in range(n):
            w = writes[i]
            while w:
                low = w & -w
                out[low.bit_length() - 1] |= state[i]
                w ^= low
        hist.append(sum(1 << i for i in range(n) if state[i] >> 102 & 1))
        rel.append(adj)
        wr.append(writes)
    back = sum(1 << i for i in range(n) if wr[7][i] >> 71 & 1)
    for d in (7, 6, 5):
        grown = back
        for i in range(n):
            if back >> i & 1:
                grown |= rel[d][i]
        back = grown
    return out, [bin(h).count("1") for h in hist], back, hist[4]


# ------------------------------------ path-nested one-helper criterion (sharp)
def endpoint_masks(geo):
    L, A, B, H, edges = geo
    dep, arr = [0] * 208, [0] * 208
    for i, (a, b) in enumerate(edges):
        dep[a] |= 1 << i
        arr[b] |= 1 << i
    return dep, arr


def admit_mask(geo, masks, f):
    """Helper types whose fixed-cover flag can pass through frame f."""
    L, A, B, H, edges = geo
    dep, arr = masks
    d = len(f)
    if d in (1, 2):
        low = L if d == 1 else A
        return sum_or(dep[a] for a in range(208)
                      if (low[a // 2] if d == 1 else low[a]) == f)
    if d in (7, 8):
        return sum_or(arr[b] for b in range(208)
                      if (B[b] if d == 7 else H[b // 2]) == f)
    if 3 <= d <= 6:
        return sum_or(dep[a] for a in range(208) if le(A[a], f)) & \
            sum_or(arr[b] for b in range(208) if le(f, B[b]))
    return 0


def sum_or(masks):
    m = 0
    for x in masks:
        m |= x
    return m


def sharp_by_frames(geo, paths, nested=True):
    """Method 1 (RREF keys): pair snapshots V <= W sharing a helper type.
    nested=False drops the containment V <= W (a probe, not a test)."""
    masks = endpoint_masks(geo)
    frames = {f for k in "XY" for i in range(104) for f in paths[k + str(i)]}
    adm = {f: admit_mask(geo, masks, f) for f in frames}
    out = []
    for t in range(104):
        m = 0
        ys = paths["Y%d" % t]
        for s in range(104):
            xs = paths["X%d" % s]
            if set(xs) & set(ys) or any(
                    adm[v] & adm[w] and (le(v, w) or not nested)
                    for v in xs for w in ys):
                m |= 1 << s
        out.append(m)
    return out


def points(k):
    """Point-set bitmap of a span (512-bit integer)."""
    pts = [0]
    for v in k:
        pts += [p ^ v for p in pts]
    return sum(1 << p for p in pts)


def sharp_by_edges(geo, paths):
    """Method 2 (point bitmaps): per helper type, admitted read/write pairs."""
    L, A, B, H, edges = geo
    bm = {n: [points(f) for f in fs] for n, fs in paths.items()}
    Lp, Ap = [points(x) for x in L], [points(x) for x in A]
    Bp, Hp = [points(x) for x in B], [points(x) for x in H]
    snaps = [(p, n) for n in bm if n[0] in "XY" for p in bm[n]
             if 2 <= p.bit_count() <= 256]
    out = [0] * 104
    for t in range(104):
        for s in range(104):
            if set(bm["X%d" % s]) & set(bm["Y%d" % t]):
                out[t] |= 1 << s
    for a, b in edges:
        flag = {2: Lp[a // 2], 4: Ap[a], 128: Bp[b], 256: Hp[b // 2]}
        ok = []
        for p, n in snaps:
            c = p.bit_count()
            if (flag.get(c) == p) if c in flag else (
                    Ap[a] & p == Ap[a] and p & Bp[b] == p):
                ok.append((p, n))
        for v, sn in ok:
            if sn[0] != "X":
                continue
            for w, tn in ok:
                if tn[0] == "Y" and v & w == v:
                    out[int(tn[1:])] |= 1 << int(sn[1:])
    return out


def full_memory(geo, paths):
    """Method 3: PR3252's full-memory recurrence, reimplemented over the whole
    pool.  Carry old memories; insert each admitted source snapshot; relay only
    old memories S over contacts as S + L(h,d) + L(w,d) when it fits both
    upper bounds; output a source at a target snapshot containing a memory.
    Memories are grouped by subspace key with a source bitmask."""
    L, A, B, H, edges = geo
    n = len(edges)
    out = [sum(1 << s for s in range(104)
               if set(paths["X%d" % s]) & set(paths["Y%d" % t]))
           for t in range(104)]
    snaps = {"X": {}, "Y": {}}
    for k in "XY":
        for i in range(104):
            for f in paths[k + str(i)]:
                snaps[k][f] = snaps[k].get(f, 0) | 1 << i
    mem = [{} for _ in range(n)]
    for d in range(1, 9):
        ivs = [interval(L, A, B, H, e, d) for e in edges]
        hosts, mine = {}, []
        for i, (lo, hi) in enumerate(ivs):
            fl = flats_between(lo, hi, d)
            mine.append(fl)
            for f in fl:
                hosts[f] = hosts.get(f, 0) | 1 << i
        nxt = [dict(m) for m in mem]
        for h in range(n):
            nb = 0
            for f in mine[h] if mem[h] else ():
                nb |= hosts[f]
            nb &= ~(1 << h)
            while nb:
                w = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                for S, sm in mem[h].items():
                    T = key(S + ivs[h][0] + ivs[w][0])
                    if len(T) <= d and le(T, ivs[h][1]) and le(T, ivs[w][1]):
                        nxt[w][T] = nxt[w].get(T, 0) | sm
        for f, sm in snaps["X"].items():
            m = hosts.get(f, 0) if len(f) == d else 0
            while m:
                i = (m & -m).bit_length() - 1
                m &= m - 1
                nxt[i][f] = nxt[i].get(f, 0) | sm
        mem = [prune(m) for m in nxt]
        for f, tm in snaps["Y"].items():
            m = hosts.get(f, 0) if len(f) == d else 0
            while m:
                i = (m & -m).bit_length() - 1
                m &= m - 1
                src = sum_or(sm for S, sm in mem[i].items() if le(S, f))
                for t in range(104):
                    if tm >> t & 1:
                        out[t] |= src
    return out


def prune(m):
    """Keep, per source, only subset-minimal memories (outputs unchanged)."""
    keep = {}
    for S in sorted(m, key=len):
        sm = m[S]
        for S2, sm2 in keep.items():
            if len(S2) < len(S) and le(S2, S):
                sm &= ~sm2
        if sm:
            keep[S] = sm
    return keep


def missing(C, support):
    return [(t, s) for t in range(104) for s in range(104)
            if C[t][s] != 0 and not support[t] >> s & 1]


def p104():
    cert, word, fixture = load()
    paths = frame_paths(word)
    roles = channel_roles(word)
    geo = covers(cert, paths)
    C = required(e8_ports(fixture))
    need(len(word["program"]) == 4058, "4,058 channel events")
    hist, first = channel_run(word, C)
    lay, fwd, back, f5 = layered(geo, paths)
    miss_l = missing(C, lay)
    need(miss_l == [(71, 102)], "layered relaxation misses only (71,102)")
    need(fwd == [16, 25, 52, 365, 1725, 2283, 2285, 2297], "forward cone")
    need(bin(back).count("1") == 37 and back & f5 == 0, "backward 37, disjoint")
    sharp = sharp_by_frames(geo, paths)
    need(sharp == sharp_by_edges(geo, paths), "sharp criterion: two loop orders")
    need(sharp == full_memory(geo, paths), "PR3252 full-memory test = sharp")
    need(all(sharp[t] & ~lay[t] == 0 for t in range(104)), "sharp <= layered")
    # A target path that reaches FULL would share it with every source.
    need(all(len(paths["X%d" % s][-1]) == 9 for s in range(104)),
         "every X path ends at FULL")
    need(not any(set(paths["X%d" % s]) & set(paths["Y%d" % t])
                 for s in range(104) for t in range(104)),
         "no X path shares a frame with a Y path")
    # Containment is never decisive here: dropping it changes no pair.
    need(sharp_by_frames(geo, paths, nested=False) == sharp,
         "containment not decisive at P104")
    # Structure: the sharp support is the 2,309 compatible slot pairs read as
    # port pairs (target b//2, source a//2) plus one extra pair.
    own = {(b // 2, a // 2) for a, b in geo[4]}
    need(len(own) == 2309 and all(C[t][s] != 0 for t, s in own),
         "2,309 distinct required own port pairs")
    sup = {(t, s) for t in range(104) for s in range(104) if sharp[t] >> s & 1}
    need(sup == own | {(73, 83)} and C[73][83] != 0,
         "sharp support = own port pairs + (73,83)")
    # Routes, not just the set: the pool types admitting each supported pair.
    masks, adm = endpoint_masks(geo), {}
    for f in {f for k in "XY" for i in range(104) for f in paths[k + str(i)]}:
        adm[f] = admit_mask(geo, masks, f)
    idx = {(b // 2, a // 2): i for i, (a, b) in enumerate(geo[4])}
    tys = {(t, s): sum_or(adm[v] & adm[w] for v in paths["X%d" % s]
                          for w in paths["Y%d" % t] if le(v, w))
           for t, s in sup}
    other = {p for p, m in tys.items()
             if m & ~(1 << idx[p] if p in idx else 0)}
    i83 = geo[4].index((17, 147))
    need(all(tys[p] >> i & 1 for p, i in idx.items()) and len(other) == 32
         and (73, 83) in other and tys[(73, 83)] == 1 << i83 and
         [(len(v), len(w)) for v in paths["X83"] for w in paths["Y73"]
          if le(v, w) and (adm[v] & adm[w]) >> i83 & 1] == [(4, 8)],
         "routes: 31 own pairs also via another type; (73,83) only via "
         "type (17,147), X83's dim-4 frame to Y73's cap")
    return {"roles": roles, "geo": geo, "paths": paths, "C": C,
            "layered": lay, "sharp": sharp, "missing_layered": miss_l,
            "missing_sharp": missing(C, sharp), "forward": fwd,
            "non_own_type_pairs": len(other),
            "backward": bin(back).count("1"),
            "hist": hist, "first_Y71_X102": first}


# ------------------------------------------------ sensitivity rows (support)
def rows(r):
    geo, paths, ms = r["geo"], r["paths"], set(r["missing_sharp"])
    masks, adm = endpoint_masks(geo), {}

    def hop(v, w):
        for f in (v, w):
            if f not in adm:
                adm[f] = admit_mask(geo, masks, f)
        return v == w or (adm[v] & adm[w] and le(v, w))

    def count(sup):
        return sum(1 for t, s in ms if sup[t] >> s & 1), bool(sup[71] >> 102 & 1)

    hist = r["hist"]  # actual nonzero channel coefficients per frame
    ys = [(t, j, w) for t in range(104) for j, w in enumerate(paths["Y%d" % t])]
    xin = {(t, j): sum(1 << s for s in range(104) if any(
        hop(v, w) for v in paths["X%d" % s])) for t, j, w in ys}

    def relay(seed, ordered=True):
        # ordered: content written into Y_u at snapshot kk is readable only
        # at snapshots k >= kk (Y_u's frames ascend in time).
        inn = dict(seed)
        changed = True
        while changed:
            changed = False
            for u, k, wu in ys:
                avail = 0
                for kk in range(k + 1 if ordered else len(paths["Y%d" % u])):
                    avail |= inn[(u, kk)]
                for t, j, wt in ys:
                    if t != u and avail & ~inn[(t, j)] and hop(wu, wt):
                        inn[(t, j)] |= avail
                        changed = True
        sup = [0] * 104
        for (t, j), m in inn.items():
            sup[t] |= m
        return sup

    r1 = relay(xin)
    r1u = relay(xin, ordered=False)
    arrivals = {}
    for t, j, w in ys:
        if xin[(t, j)]:
            cap = j == len(paths["Y%d" % t]) - 1
            arrivals[(len(w), cap)] = arrivals.get((len(w), cap), 0) + \
                bin(xin[(t, j)]).count("1")
    lower = {}  # target snapshots below the cap that receive content
    for t, j, w in ys:
        if xin[(t, j)] and j < len(paths["Y%d" % t]) - 1:
            lower[len(w)] = lower.get(len(w), 0) + 1
    need(all(xin[(t, len(paths["Y%d" % t]) - 1)] == r["sharp"][t]
             for t in range(104)), "every supported pair arrives at the cap")
    need(len({paths["Y%d" % t][-1] for t in range(104)}) == 104,
         "104 distinct target caps")
    r1c = relay({(t, j): xin[(t, j)] | hist["Y%d" % t].get(w, 0)
                 for t, j, w in ys})
    free = [sum(1 << s for s in range(104) if any(
        1 <= len(v) <= len(w) <= 8 and le(v, w)
        for v in paths["X%d" % s] for w in paths["Y%d" % t]))
        for t in range(104)]
    old = [(n, f, m) for n, h in hist.items() if n[0] not in "XY"
           for f, m in h.items() if m]
    r3 = [0] * 104
    for n, f, m in old:
        for t in range(104):
            if any(hop(f, w) for w in paths["Y%d" % t]):
                r3[t] |= m
    w2 = [(len(v), len(w)) for v in paths["X102"] for w in paths["Y71"]
          if 1 <= len(v) <= len(w) <= 8 and le(v, w)]
    w3 = sorted({(n, len(f)) for n, f, m in old if m >> 102 & 1 and
                 any(hop(f, w) for w in paths["Y71"])})
    # target feedback: first Y71 snapshot whose channel increments hold X102
    w1c = [len(f) for f in paths["Y71"]
           if hist["Y71"].get(f, 0) >> 102 & 1][:1]
    return {"R1_correction_only_Y_relay": count(r1),
            "R1u_without_target_order": count(r1u),
            "R1_arrivals_dim_cap": sorted(arrivals.items()),
            "R1_lower_snapshots_by_dim": sorted(lower.items()),
            "R1c_Y_relay_with_channel_content": count(r1c),
            "R2_free_nested_flags": count(free),
            "R3_old_channel_helper_reads": count(r3),
            "R2_witness_dims": w2, "R3_witness_states": w3,
            "R1c_witness_reads": w1c}


# ------------------------------------------- consequence for PR3427's rank
def frac_rank(rows):
    a, rk = [list(r) for r in rows], 0
    for c in range(len(a[0]) if a else 0):
        p = next((i for i in range(rk, len(a)) if a[i][c] != 0), None)
        if p is None:
            continue
        a[rk], a[p] = a[p], a[rk]
        for i in range(len(a)):
            if i != rk and a[i][c] != 0:
                f = a[i][c] / a[rk][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[rk])]
        rk += 1
    return rk


def bareiss_det(m):
    """Exact integer determinant by fraction-free elimination."""
    a, n, sign, prev = [r[:] for r in m], len(m), 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            p = next((i for i in range(k + 1, n) if a[i][k]), None)
            if p is None:
                return 0
            a[k], a[p], sign = a[p], a[k], -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def max_clique(adj):
    """Exact maximum clique size: branch and bound with a greedy colouring
    bound (vertex sets are bitmasks)."""
    best = [0]

    def expand(size, P):
        order, U, col = [], P, 0
        while U:
            col, Q = col + 1, U
            while Q:
                v = (Q & -Q).bit_length() - 1
                Q &= ~adj[v] & ~(1 << v)
                U &= ~(1 << v)
                order.append((col, v))
        for col, v in reversed(order):
            if size + col <= best[0]:
                return
            if P & adj[v]:
                expand(size + 1, P & adj[v])
            best[0] = max(best[0], size + 1)
            P &= ~(1 << v)
    expand(0, (1 << len(adj)) - 1)
    return best[0]


def max_clique_bk(adj):
    """Second exact method: Bron-Kerbosch with pivoting and a size bound."""
    best = [0]

    def bk(size, P, X):
        if not P:
            best[0] = max(best[0], size)
            return
        if size + bin(P).count("1") <= best[0]:
            return
        piv = max((v for v in range(len(adj)) if (P | X) >> v & 1),
                  key=lambda v: bin(P & adj[v]).count("1"))
        cand = P & ~adj[piv]
        while cand:
            v = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            bk(size + 1, P & adj[v], X & adj[v])
            P &= ~(1 << v)
            X |= 1 << v
    bk(0, (1 << len(adj)) - 1, 0)
    return best[0]


MIS_BLOCK = (8, 11, 17, 18, 23, 30, 34, 37, 42, 50, 51, 58, 59, 63, 70, 71,
             78, 80, 84, 87, 91, 96, 100)


def rank_consequence(r):
    """Any D = U^-1 - G/2 vanishes on unsupported pairs, so on an unsupported
    rectangle (U^-1 - I)[R,S] = -C[R,S] and rank(U - I) >= rank C[R,S].
    A principal block C[S,S] is unsupported exactly when S is independent in
    the undirected support graph (diagonal pairs are never supported)."""
    sharp, C, S = r["sharp"], r["C"], MIS_BLOCK
    need(all(not sharp[t] >> s & 1 for t in S for s in S),
         "principal block unsupported")
    free = [sum(1 << s for s in range(104) if s != t and not (
        sharp[t] >> s & 1 or sharp[s] >> t & 1)) for t in range(104)]
    need(max_clique(free) == max_clique_bk(free) == len(S) == 23,
         "maximum independent set has size 23 by two exact searches")
    rk = frac_rank([[C[t][s] for s in S] for t in S])
    det = bareiss_det([[int(2 * C[t][s]) for s in S] for t in S])
    need(rk == 23 and det == 2 ** 30,
         "rank 23 by elimination and det(2C[S,S]) = 2^30")
    # Rectangle ceiling: C[R,S] = I[R,S] - (G/2)[R,S] with R & S independent.
    g = frac_rank([[int(t == s) - C[t][s] for s in range(104)]
                   for t in range(104)])
    need(g == 8, "rank G/2 = 8")
    return rk, det, g


def matching_number(pairs, n=104):
    """Maximum bipartite matching (Kuhn); equals the minimum vertex cover."""
    adj, match = [[] for _ in range(n)], [-1] * n
    for t, s in pairs:
        adj[t].append(s)

    def augment(t, seen):
        for s in adj[t]:
            if s not in seen:
                seen.add(s)
                if match[s] < 0 or augment(match[s], seen):
                    match[s] = t
                    return True
        return False
    return sum(augment(t, set()) for t in range(n))


# ------------------------------------------------- small-domain oracle
class Rng:
    """Deterministic LCG so the oracle needs no stdlib random state."""

    def __init__(self, seed):
        self.x = seed

    def below(self, n):
        self.x = (self.x * 6364136223846793005 + 1442695040888963407) % 2**64
        return (self.x >> 33) % n

    def coef(self):
        return Fraction(self.below(19) + 1, self.below(7) + 1) * (
            -1 if self.below(2) else 1)


def grow(rng, n, low, high, d):
    """Random d-dim key between low and high (low <= high)."""
    cur = low
    while len(cur) < d:
        v = rng.below(1 << n)
        if le((v,), high):
            cur = span_add(cur, v)
    return cur


def instance(rng, n, nx=3, ny=3, nt=3, rigid=False, pooled=False):
    """Random small domain.  pooled=True mirrors P104: departure chains fix
    dims 1..p, arrival chains fix dims q..n-1, and the type list is every
    compatible (departure, arrival) pair, so it is closed under recombination."""
    full = key([1 << i for i in range(n)])
    zero = ()

    def chain(start_dim, end_dim):
        out = [grow(rng, n, zero, full, start_dim)]
        while len(out[-1]) < end_dim:
            step = 1 + rng.below(end_dim - len(out[-1]))
            out.append(grow(rng, n, out[-1], full, len(out[-1]) + step))
        return out
    xs = [chain(1, n) for _ in range(nx)]
    ys = [chain(0, n - 1) for _ in range(ny)]
    if pooled:
        return n, xs, ys, pool_types(rng, n, xs, ys)
    types = []
    pairs = [(a, b) for c in xs for a in c for e in ys for b in e
             if 1 <= len(a) < len(b) and le(a, b)]
    for _ in range(nt):
        flag = [zero]
        if pairs and rng.below(2):  # thread the flag through a read/write pair
            a, b = pairs[rng.below(len(pairs))]
            while len(flag[-1]) < len(a):
                flag.append(grow(rng, n, flag[-1], a, len(flag[-1]) + 1))
            while len(flag[-1]) < len(b):
                flag.append(grow(rng, n, flag[-1], b, len(flag[-1]) + 1))
        for d in range(len(flag), n + 1):
            flag.append(grow(rng, n, flag[-1], full, d))
        fixed = {0: zero, n: full}
        for d in range(1, n):
            if rigid or rng.below(2):
                fixed[d] = flag[d]
        types.append(fixed)
    return n, xs, ys, types


def pool_types(rng, n, xs, ys):
    full = key([1 << i for i in range(n)])
    p = 1 + rng.below(n - 2)
    q = p + 1 + rng.below(n - 1 - p)
    deps, arrs = [], []
    for _ in range(3):
        line = xs[rng.below(len(xs))][0] if rng.below(3) else \
            grow(rng, n, (), full, 1)
        dep = [line]
        while len(dep) < p:
            dep.append(grow(rng, n, dep[-1], full, len(dep) + 1))
        deps.append(dep)
    for k in range(3):
        if k == 0 or rng.below(2):  # grow upward from a departure: compatible
            arr = [grow(rng, n, deps[rng.below(3)][-1], full, q)]
            while len(arr[-1]) < n - 1:
                arr.append(grow(rng, n, arr[-1], full, len(arr[-1]) + 1))
        else:  # descend from a target cap or a random hyperplane
            arr = [ys[rng.below(len(ys))][-1] if rng.below(3) else
                   grow(rng, n, (), full, n - 1)]
            while len(arr[0]) > q:
                arr.insert(0, grow(rng, n, (), arr[0], len(arr[0]) - 1))
        arrs.append(arr)
    types = []
    for dep in deps:
        for arr in arrs:
            if le(dep[-1], arr[0]):
                fixed = {0: (), n: full}
                fixed.update({len(f): f for f in dep + arr})
                types.append(fixed)
    need(types, "pool has a compatible pair")
    return types


def type_interval(fixed, d):
    lo = max((k for k in fixed if k <= d))
    hi = min((k for k in fixed if k >= d))
    return fixed[lo], fixed[hi]


def small_admit(fixed, f):
    lo, hi = type_interval(fixed, len(f))
    return le(lo, f) and le(f, hi)


def small_sharp(inst, nested=True):
    """nested=False drops the containment V <= W (a probe, not a test)."""
    n, xs, ys, types = inst
    sup = set()
    for s, xc in enumerate(xs):
        for t, yc in enumerate(ys):
            if set(xc) & set(yc) or any(
                    (le(v, w) or not nested) and any(
                        small_admit(ty, v) and small_admit(ty, w)
                        for ty in types)
                    for v in xc for w in yc if 1 <= len(v) <= len(w) <= n - 1):
                sup.add((t, s))
    return sup


def small_layered(inst):
    n, xs, ys, types = inst
    sup = {(t, s) for s, xc in enumerate(xs) for t, yc in enumerate(ys)
           if set(xc) & set(yc)}
    state = [set() for _ in types]
    for d in range(1, n):
        fl = [set(flats_between(*type_interval(ty, d), d)) for ty in types]
        reads = [{s for s, xc in enumerate(xs) if fl[i] & set(xc)}
                 for i in range(len(types))]
        seeded = [state[i] | reads[i] for i in range(len(types))]
        state = [set().union(*(seeded[j] for j in range(len(types))
                               if fl[i] & fl[j])) for i in range(len(types))]
        for i in range(len(types)):
            for t, yc in enumerate(ys):
                if fl[i] & set(yc):
                    sup |= {(t, s) for s in state[i]}
    return sup


def helper_flag(rng, inst, ty):
    """Random full flag through the type's fixed members, biased toward
    X/Y snapshot frames so that contacts actually occur."""
    n, xs, ys, _ = inst
    snaps = {f for c in xs + ys for f in c}
    flag = [()]
    for d in range(1, n + 1):
        lo, hi = type_interval(ty, d)
        base = key(flag[-1] + lo)
        hits = sorted(f for f in snaps if len(f) == d and le(base, f)
                      and le(f, hi))
        if hits and rng.below(8):
            flag.append(hits[rng.below(len(hits))])
        else:
            flag.append(grow(rng, n, base, hi, d))
    return flag


def run_program(rng, inst, steps, violate=None, direct=True):
    """Random straight-line program choosing uniformly among the operations
    legal at each moment; returns its nonzero source->target pairs."""
    n, xs, ys, types = inst
    full = key([1 << i for i in range(n)])
    nh = 4
    tys = [{0: (), n: full} if violate == "offcover"
           else types[rng.below(len(types))] for _ in range(nh)]
    flags = [helper_flag(rng, inst, ty) for ty in tys]
    pos, xp, yp = [0] * nh, [0] * len(xs), [0] * len(ys)
    hv = [{("D", h): Fraction(1)} for h in range(nh)]
    yv = [{} for _ in ys]
    relay = [set() for _ in range(nh)]  # sources received across two types
    via = [set() for _ in ys]
    extra = None
    if violate == "oldstate":
        f = [c for c in xs + ys for c in c if 1 <= len(c) < n]
        extra = (f[rng.below(len(f))], {("X", rng.below(len(xs))): Fraction(1)})

    for _ in range(steps):
        fr = [flags[h][pos[h]] for h in range(nh)]
        xf = [xs[i][xp[i]] for i in range(len(xs))]
        yf = [ys[j][yp[j]] for j in range(len(ys))]
        acts = [("xadv", i) for i in range(len(xs)) if xp[i] + 1 < len(xs[i])]
        acts += [("yadv", j) for j in range(len(ys)) if yp[j] + 1 < len(ys[j])]
        for h in range(nh):
            ups = range(pos[h] + 1, n + 1)
            if violate == "descent":
                ups = [p for p in range(n + 1) if p != pos[h]]
            if ups:  # one transport action per helper; target drawn later
                acts.append(("tr", h, list(ups)))
            acts += [("read", h, i) for i in range(len(xs)) if fr[h] == xf[i]]
            acts += [("write", h, j) for j in range(len(ys)) if fr[h] == yf[j]]
            acts += 3 * [("mix", h, g) for g in range(nh) if g != h and (
                fr[h] == fr[g] or violate == "crossframe")]
            if violate == "yread":
                acts += [("yread", h, j) for j in range(len(ys))
                         if fr[h] == yf[j]]
            if extra and fr[h] == extra[0]:
                acts.append(("old", h))
        acts += [("direct", i, j) for i in range(len(xs))
                 for j in range(len(ys)) if direct and xf[i] == yf[j]]
        act = acts[rng.below(len(acts))]
        c = rng.coef()
        if act[0] == "xadv":
            xp[act[1]] += 1
        elif act[0] == "yadv":
            yp[act[1]] += 1
        elif act[0] == "tr":
            pos[act[1]] = act[2][rng.below(len(act[2]))]
            hv[act[1]] = {k: c * v for k, v in hv[act[1]].items()}
        elif act[0] == "read":
            axpy(hv[act[1]], c, {("X", act[2]): Fraction(1)})
        elif act[0] == "write":
            axpy(yv[act[2]], c, hv[act[1]])
            via[act[2]] |= relay[act[1]]
        elif act[0] == "mix":
            axpy(hv[act[2]], c, hv[act[1]])
            relay[act[2]] |= relay[act[1]]
            if tys[act[1]] != tys[act[2]]:
                relay[act[2]] |= {k[1] for k in hv[act[1]] if k[0] == "X"}
        elif act[0] == "yread":
            axpy(hv[act[1]], c, yv[act[2]])
        elif act[0] == "old":
            axpy(hv[act[1]], c, extra[1])
        else:
            axpy(yv[act[2]], c, {("X", act[1]): Fraction(1)})
    got = {(t, k[1]) for t in range(len(ys)) for k in yv[t] if k[0] == "X"}
    run_program.cross_type = {(t, s) for t, s in got if s in via[t]}
    return got


def meet(a, b):
    """Intersection of two subspaces (small domains: enumerate a's points)."""
    pts = [0]
    for x in a:
        pts += [p ^ x for p in pts]
    return key([p for p in pts if p and le((p,), b)])


def flag_through(rng, inst, ty, must):
    """Random full flag of type ty passing through every frame in must
    (a nested list), or None when the type cannot host them."""
    n = inst[0]
    flag = [()]
    for d in range(1, n + 1):
        lo, hi = type_interval(ty, d)
        base = key(flag[-1] + lo)
        above = [f for f in must if len(f) >= d]
        cap = meet(hi, above[0]) if above else hi
        if len(base) > d or len(cap) < d or not le(base, cap):
            return None
        flag.append(grow(rng, n, base, cap, d))
    return flag


def execute(inst, helpers, ops, yread=False):
    """Run an explicit straight-line program, checking every contract rule:
    flags of the helper's type, monotone transports, equal-frame reads,
    mixes and writes, monotone frozen X/Y schedules.  Exact Fractions.
    yread=True admits one contract violation: helpers may read a target."""
    n, xs, ys, _ = inst
    for ty, fl in helpers:
        need(all(small_admit(ty, f) for f in fl[1:n]) and all(
            le(a, b) for a, b in zip(fl, fl[1:])), "helper flag of its type")
    pos, xp, yp = [0] * len(helpers), [0] * len(xs), [0] * len(ys)
    hv = [{("D", h): Fraction(1)} for h in range(len(helpers))]
    yv = [{} for _ in ys]

    for op, a, b, c in ops:
        fr = [helpers[h][1][pos[h]] for h in range(len(helpers))]
        if op == "x":
            need(b >= xp[a], "X schedule monotone")
            xp[a] = b
        elif op == "y":
            need(b >= yp[a], "Y schedule monotone")
            yp[a] = b
        elif op == "tr":
            need(b >= pos[a], "transport ascends")
            pos[a] = b
            hv[a] = {k: c * x for k, x in hv[a].items()}
        elif op == "read":
            need(fr[a] == xs[b][xp[b]], "read at equal frame")
            axpy(hv[a], c, {("X", b): Fraction(1)})
        elif op == "mix":
            need(fr[a] == fr[b] and a != b, "mix at equal frame")
            axpy(hv[b], c, hv[a])
        elif op == "yread":
            need(yread, "targets are never read")
            need(fr[a] == ys[b][yp[b]], "Y read at equal frame")
            axpy(hv[a], c, yv[b])
        else:
            need(op == "write", "known operation")
            need(fr[a] == ys[b][yp[b]], "write at equal frame")
            axpy(yv[b], c, hv[a])
    return {(t, k[1]) for t in range(len(ys)) for k in yv[t] if k[0] == "X"}


def y_relay_counterexample():
    """Minimal F_2^3 program: reading a target relays X0 outside both tests.

    e1,e2,e3 = 1,2,4.  X0: <e1> -> FULL.  Y0: 0 -> <e1> -> <e1,e2>.
    Y1: 0 -> <e1,e2>.  Type T1 fixes <e1> < <e1,e3>; type T2 fixes
    <e2> < <e1,e2>.  h1 (T1) reads X0 at <e1> and writes Y0 there; Y0 is
    transported by the frozen channel; h2 (T2, dim-2 frame <e1,e2>) reads
    Y0 and writes Y1.  Four scalar operations, run by the checked
    interpreter with the one rule it breaks (a Y read) enabled.
    """
    full = key([1, 2, 4])
    t1 = {0: (), 1: key([1]), 2: key([1, 4]), 3: full}
    t2 = {0: (), 1: key([2]), 2: key([1, 2]), 3: full}
    inst = (3, [[key([1]), full]], [[(), key([1]), key([1, 2])],
                                     [(), key([1, 2])]], [t1, t2])
    helpers = [(t1, [(), key([1]), key([1, 4]), full]),
               (t2, [(), key([2]), key([1, 2]), full])]
    c = [Fraction(2), Fraction(-3), Fraction(5, 7), Fraction(-1, 2)]
    ops = [("x", 0, 0, None), ("y", 0, 1, None), ("tr", 0, 1, Fraction(1)),
           ("read", 0, 0, c[0]), ("write", 0, 0, c[1]),
           ("y", 0, 2, None), ("tr", 1, 2, Fraction(1)),
           ("yread", 1, 0, c[2]), ("y", 1, 1, None), ("write", 1, 1, c[3])]
    need(rejected(lambda: execute(inst, helpers, ops)),
         "Y read is rejected by the contract interpreter")
    got = execute(inst, helpers, ops, yread=True)
    need((1, 0) in got, "nonzero relayed coefficient")
    sharp, lay = small_sharp(inst), small_layered(inst)
    need((1, 0) not in sharp and (1, 0) not in lay and
         (1, 0) not in small_exact(inst)[0], "Y relay escapes")
    return (1, True)


def rejected(fn):
    """True when the checked interpreter rejects the program."""
    try:
        fn()
    except SystemExit:
        return True
    return False


def small_frames(n, cache={}):
    """Every proper nonzero subspace of F_2^n as a canonical key."""
    if n not in cache:
        cache[n] = [key(b) for d in range(1, n) for b in subspaces(n, d)]
    return cache[n]


def small_exact(inst):
    """Exhaustive untimed reachability (no lemma assumed).  A frame is reached
    when a helper of some type can hold the source there; a helper of type ty
    moves up between two nested frames that ty admits (a flag of ty passes
    both); helpers at equal frames mix.  Returns the support and, for each
    helper-only pair, one witness path (frames, type of each step)."""
    n, xs, ys, types = inst
    up = {}
    for i, ty in enumerate(types):
        fs = [f for f in small_frames(n) if small_admit(ty, f)]
        for f in fs:
            for g in fs:
                if len(f) < len(g) and le(f, g):
                    up.setdefault(f, {}).setdefault(g, i)
            up.setdefault(f, {})
    sup = {(t, s) for s, xc in enumerate(xs) for t, yc in enumerate(ys)
           if set(xc) & set(yc)}
    wit = {}
    for s, xc in enumerate(xs):
        par = {v: None for v in xc if v in up}
        todo = list(par)
        while todo:
            f = todo.pop()
            for g, i in up[f].items():
                if g not in par:
                    par[g] = (f, i)
                    todo.append(g)
        for t, yc in enumerate(ys):
            w = next((w for w in yc if w in par), None)
            if w is not None and (t, s) not in sup:
                sup.add((t, s))
                frames, steps = [w], []
                while par[frames[-1]] is not None:
                    f, i = par[frames[-1]]
                    frames.append(f)
                    steps.append(i)
                wit[(t, s)] = (frames[::-1], steps[::-1])
    return sup, wit


def realize(rng, inst, pair, witness):
    """Turn a reachability witness into an explicit program (one helper per
    step, mixing at the shared frames) and run it in the checked
    interpreter.  True when the pair gets a nonzero coefficient."""
    n, xs, ys, types = inst
    (t, s), (frames, steps) = pair, witness
    helpers, ops = [], [("x", s, xs[s].index(frames[0]), None)]
    for k, i in enumerate(steps):
        fl = flag_through(rng, inst, types[i], frames[k:k + 2])
        need(fl is not None, "witness step admitted by its type")
        helpers.append((types[i], fl))
        ops += [("tr", k, fl.index(frames[k]), rng.coef()),
                ("read", k, s, rng.coef()) if k == 0 else
                ("mix", k - 1, k, rng.coef()),
                ("tr", k, fl.index(frames[k + 1]), rng.coef())]
    ops += [("y", t, ys[t].index(frames[-1]), None),
            ("write", len(steps) - 1, t, rng.coef())]
    return pair in execute(inst, helpers, ops)


def directed_program(rng, inst, hops):
    """Legal program along a random path: read X_s at V, relay through
    `hops` further helpers of random types at shared frames, write Y_t.
    Returns (pairs, number of distinct helper types used)."""
    n, xs, ys, types = inst
    s = rng.below(len(xs))
    xi = rng.below(len(xs[s]) - 1)  # never the full space
    v = xs[s][xi]
    targets = [(t, j) for t in range(len(ys)) for j in range(len(ys[t]))
               if len(ys[t][j]) >= len(v) and le(v, ys[t][j])]
    if not targets:
        return set(), 0
    t, j = targets[rng.below(len(targets))]
    w = ys[t][j]
    helpers, ops, cur = [], [("x", s, xi, None)], v
    for hop in range(hops + 1):
        last = hop == hops
        must = sorted({cur, w} if last else {cur}, key=len)
        fl = None
        for _ in range(8):
            ty = types[rng.below(len(types))]
            fl = flag_through(rng, inst, ty, must)
            if fl:
                break
        if not fl:
            return set(), 0
        h = len(helpers)
        helpers.append((ty, fl))
        ops.append(("tr", h, fl.index(cur), rng.coef()))
        if hop == 0:
            ops.append(("read", h, s, rng.coef()))
        else:
            ops.append(("mix", h - 1, h, rng.coef()))
        if last:
            ops += [("y", t, j, None), ("tr", h, fl.index(w), rng.coef()),
                    ("write", h, t, rng.coef())]
        else:
            ups = [p for p in range(fl.index(cur), n)
                   if 1 <= len(fl[p]) and le(fl[p], w)]
            p = ups[rng.below(len(ups))]
            ops.append(("tr", h, p, rng.coef()))
            cur = fl[p]
    return execute(inst, helpers, ops), len({id(ty) for ty, _ in helpers})


def unpooled_relay_example():
    """F_2^4, types not closed under recombination: a legal two-type relay
    lies inside PR3259's layered test but outside the single-type criterion.

    T1 fixes <e1> < <e1,e2> < <e1,e2,e4>; T2 fixes <e2> < <e1,e2> <
    <e1,e2,e3>.  h1 (T1) reads X0 at <e1>, rises to <e1,e2>, adds into h2
    (T2) there; h2 rises to W = <e1,e2,e3> and writes Y0.  Run by the
    checked interpreter (which also checks that each type is a flag)."""
    full = key([1, 2, 4, 8])
    t1 = {0: (), 1: key([1]), 2: key([1, 2]), 3: key([1, 2, 8]), 4: full}
    t2 = {0: (), 1: key([2]), 2: key([1, 2]), 3: key([1, 2, 4]), 4: full}
    inst = (4, [[key([1]), full]], [[(), key([1, 2, 4])]], [t1, t2])
    helpers = [(t, [t[d] for d in range(5)]) for t in (t1, t2)]
    ops = [("x", 0, 0, None), ("tr", 0, 1, Fraction(1)),
           ("read", 0, 0, Fraction(3)), ("tr", 0, 2, Fraction(-2, 5)),
           ("tr", 1, 2, Fraction(1)), ("mix", 0, 1, Fraction(7)),
           ("tr", 1, 3, Fraction(1, 3)), ("y", 0, 1, None),
           ("write", 1, 0, Fraction(1))]
    need((0, 0) in execute(inst, helpers, ops),
         "legal two-type relay delivers a nonzero coefficient")
    need((0, 0) not in small_sharp(inst) and (0, 0) in small_layered(inst)
         and (0, 0) in small_exact(inst)[0],
         "pooling is needed for the one-helper criterion")
    return True


ORACLE_TRIALS = ((3, 3000), (4, 1500))


def oracle(seed=20261018, trials=ORACLE_TRIALS, steps=120):
    """Seeded random small instances, each checked three ways: an exhaustive
    untimed reachability (small_exact), an explicit checked program for every
    reachable helper pair (realize), and two random legal programs
    (directed: run by execute; uniform: legal by construction, never run by
    execute).  Pooled instances (P104-like): the exhaustive support equals
    the one-helper test.
    Unpooled rigid instances: it lies in PR3259's layered test (no pooling
    needed there) and its escapes from the one-helper test are counted."""
    rng, wrng = Rng(seed), Rng(seed + 1)
    c = dict.fromkeys(("programs", "nonzero_coefficients", "helper_mediated",
                       "cross_type_relayed", "directed_multi_type",
                       "strict_gap", "strict_gap_pairs",
                       "exact_helper_pairs_realized", "unpooled_programs",
                       "unpooled_coefficients", "unpooled_multi_type",
                       "unpooled_single_type_escapes",
                       "unpooled_exact_helper_pairs_realized",
                       "unpooled_exact_escapes", "unpooled_escape_instances"),
                      0)
    for n, count in trials:
        for _ in range(count):
            inst = instance(rng, n, pooled=True)
            sharp, lay = small_sharp(inst), small_layered(inst)
            need(sharp <= lay, "oracle: sharp support inside layered")
            c["strict_gap"] += sharp < lay
            c["strict_gap_pairs"] += len(lay - sharp)
            exact, wit = small_exact(inst)
            need(exact == sharp, "oracle: exhaustive untimed support differs "
                 "from the one-helper test on a pooled instance")
            need(all(realize(wrng, inst, p, w) for p, w in wit.items()),
                 "oracle: reachable pair not realized by a checked program")
            c["exact_helper_pairs_realized"] += len(wit)
            # Direct X->Y adds are seeded identically by both tests; omit
            # them so every coefficient is carried by helper paths.
            got = run_program(rng, inst, steps, direct=False)
            cross = run_program.cross_type
            path, ntypes = directed_program(rng, inst, 1 + rng.below(3))
            need(got | path <= sharp, "oracle: legal coefficient outside "
                 "the one-helper test")
            c["programs"] += 2
            c["nonzero_coefficients"] += len(got) + len(path)
            c["helper_mediated"] += sum(not set(inst[1][s]) & set(
                inst[2][t]) for t, s in got | path)
            c["cross_type_relayed"] += len(cross)
            c["directed_multi_type"] += len(path) if ntypes > 1 else 0
            inst = instance(rng, n, nt=6, rigid=True)
            exact, wit = small_exact(inst)
            need(exact <= small_layered(inst),
                 "oracle: exhaustive support outside the layered test")
            need(all(realize(wrng, inst, p, w) for p, w in wit.items()),
                 "oracle: reachable pair not realized by a checked program")
            c["unpooled_exact_helper_pairs_realized"] += len(wit)
            escapes = exact - small_sharp(inst)
            c["unpooled_exact_escapes"] += len(escapes)
            c["unpooled_escape_instances"] += bool(escapes)
            got = run_program(rng, inst, steps, direct=False)
            path, ntypes = directed_program(rng, inst, 1 + rng.below(3))
            need(got | path <= exact,
                 "oracle: legal coefficient outside the exhaustive support")
            c["unpooled_programs"] += 2
            c["unpooled_coefficients"] += len(got) + len(path)
            c["unpooled_multi_type"] += len(path) if ntypes > 1 else 0
            c["unpooled_single_type_escapes"] += len(
                (got | path) - small_sharp(inst))
    escapes = {"yread": y_relay_counterexample(),
               "unpooled": unpooled_relay_example()}
    for bad in ("descent", "crossframe", "offcover", "oldstate"):
        found = None
        for attempt in range(1, 4001):
            inst = instance(rng, 3 + attempt % 2, pooled=True)
            got = run_program(rng, inst, steps, bad)
            if not got <= small_sharp(inst):
                found = (attempt, not got <= small_layered(inst))
                break
        need(found is not None, "negative control has no teeth: " + bad)
        escapes[bad] = found
    return c, escapes


PR3427_SOURCE_MASKS = (  # published per-source target masks, sources 0..3
    0x15088a1021120142242d061684, 0x1504102110011204022d109084,
    0x1b0000480c4084800021001083, 0x2a889524212d01425a52a06020)


def main():
    r = p104()
    sharp = r["sharp"]
    for s, mask in enumerate(PR3427_SOURCE_MASKS):
        need(sum(1 << t for t in range(104) if sharp[t] >> s & 1) == mask,
             "PR3427 four-column support masks")
    ms = r["missing_sharp"]
    need(len(ms) == 2682 and (71, 102) in ms, "2,682 sharp-missing entries")
    need(len({t for t, _ in ms}) == 104 and len({s for _, s in ms}) == 104,
         "every row and column has a sharp-missing entry")
    need(sum(bin(m).count("1") for m in sharp) == 2310 and
         sum(bin(m).count("1") for m in r["layered"]) == 10815, "support sizes")
    C, lay = r["C"], r["layered"]
    by_value = {}
    for t, s in ms:
        by_value[str(C[t][s])] = by_value.get(str(C[t][s]), 0) + 1
    need(by_value == {"-1/2": 1801, "1/2": 881}, "sign split 1,801/881")
    reopened = sum(1 for t, s in ms if lay[t] >> s & 1)
    need(reopened == 2681, "PR3259's test grants 2,681 sharp-missing entries")
    pairs = [(t, s) for t in range(104) for s in range(104)]
    need(sum(not sharp[t] >> s & 1 for t, s in pairs) == 8506, "8,506 unsupported")
    need(all(C[t][s] != 0 and t != s for t, s in pairs if sharp[t] >> s & 1),
         "every sharp-supported pair is an off-diagonal required entry")
    zero_off = [(t, s) for t, s in pairs if t != s and C[t][s] == 0]
    need(len(zero_off) == 5720 and all(lay[t] >> s & 1 for t, s in zero_off)
         and all(lay[t] >> t & 1 for t in range(104)),
         "PR3259's test grants all 5,720 zero off-diagonal and 104 diagonal pairs")
    need(sum(1 for t, s in ms if s < 4) == 92 and all(
        lay[t] >> s & 1 for t, s in ms if s < 4),
        "PR3427's masks exclude 92 required entries that PR3259's test grants")
    rows_hit = [sum(1 for t, _ in ms if t == u) for u in range(104)]
    cols_hit = [sum(1 for _, s in ms if s == u) for u in range(104)]
    cover = matching_number(ms)
    need(cover == 104 and min(rows_hit) == 14 and min(cols_hit) == 9,
         "missing entries: perfect matching (vertex cover 104), "
         "row min 14, column min 9")
    need(r["backward"] == 37, "backward cone 37")
    need(r["first_Y71_X102"] == [3378, "1/2", "D11", 5],
         "channel's first X102 delivery into Y71")
    rw = rows(r)
    need(rw["R1_correction_only_Y_relay"] == (0, False), "R1")
    need(rw["R1u_without_target_order"] == (2682, True), "R1u")
    need(rw["R1_arrivals_dim_cap"] == [((5, False), 31), ((6, False), 24),
                                       ((8, True), 2310)], "R1 arrivals")
    need(rw["R1_lower_snapshots_by_dim"] == [(5, 19), (6, 7)],
         "R1 lower arrivals sit on 19 + 7 target snapshots")
    need(rw["R1c_Y_relay_with_channel_content"] == (2682, True), "R1c")
    need(rw["R2_free_nested_flags"] == (2682, True), "R2")
    need(rw["R3_old_channel_helper_reads"] == (2682, True), "R3")
    need(rw["R2_witness_dims"] == [(1, 8)], "R2 witness")
    need(rw["R3_witness_states"] == [("D11", 5)], "R3 witness")
    need(rw["R1c_witness_reads"] == [5], "R1c feedback witness")
    rk, det, g_rank = rank_consequence(r)
    checked, escapes = oracle()
    need(checked == ORACLE_EXPECTED, "oracle receipt %r" % (checked,))
    need(escapes == ESCAPES_EXPECTED, "negative controls %r" % (escapes,))
    print(json.dumps({"channel_roles": r["roles"], "layered_missing":
                      r["missing_layered"], "forward_cone": r["forward"],
                      "channel_first_Y71_X102": r["first_Y71_X102"],
                      "rank_bound": rk, "mis_block": MIS_BLOCK,
                      "det_2C_block": det,
                      "sharp_missing": len(ms), "sharp_missing_by_value":
                      by_value, "layered_grants_sharp_missing": reopened,
                      "counts": {
                          "pairs": len(pairs), "required_entries": 4992,
                          "channel_events": 4058,
                          "sharp_supported_pairs": 2310,
                          "layered_supported_pairs": 10815,
                          "unsupported_pairs": 8506,
                          "own_port_pairs": 2309, "extra_pair": [73, 83],
                          "non_own_type_pairs": r["non_own_type_pairs"],
                          "rank_G_half": g_rank,
                          "rectangle_rank_cap": 23 + g_rank,
                          "layered_zero_off_diagonal": len(zero_off),
                          "layered_diagonal": 104, "backward_cone":
                          r["backward"], "pr3427_cols_0_3_missing": 92,
                          "missing_vertex_cover": cover,
                          "missing_row_min": min(rows_hit),
                          "missing_col_min": min(cols_hit)},
                      "rows": rw,
                      "oracle": checked, "negative_controls": escapes},
                     sort_keys=True))
    print("PASS_P104_FIXED_COVER_CUT_REVIEW layered_missing=1 "
          "sharp_missing=2682 of 4992 pr3427_masks=4 rank_U_minus_I>=23 "
          "vertex_cover=104 rows=5 oracle_instances=%d oracle_programs=%d no_kappa" % (
              sum(n for _, n in ORACLE_TRIALS) * 2,
              checked["programs"] + checked["unpooled_programs"]))


ORACLE_EXPECTED = {
    "programs": 9000, "nonzero_coefficients": 1043, "helper_mediated": 604,
    "cross_type_relayed": 13, "directed_multi_type": 620, "strict_gap": 54,
    "strict_gap_pairs": 75, "exact_helper_pairs_realized": 4264,
    "unpooled_programs": 9000, "unpooled_coefficients": 1887,
    "unpooled_multi_type": 1112, "unpooled_single_type_escapes": 0,
    "unpooled_exact_helper_pairs_realized": 8978,
    "unpooled_exact_escapes": 33, "unpooled_escape_instances": 26}
ESCAPES_EXPECTED = {"yread": (1, True), "unpooled": True, "descent": (1, True),
                    "crossframe": (6, True), "offcover": (131, True),
                    "oldstate": (159, True)}

if __name__ == "__main__":
    main()
