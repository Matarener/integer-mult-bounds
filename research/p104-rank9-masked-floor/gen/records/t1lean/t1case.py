"""T1 hand route -> Lean closure certificate for one framed type (SCHEME §3.2, T1 stage 1/2 values).
Relations from frames INSIDE Z only: rule (a) (t ⊥ s, two terms), rule (c) (triangles of two-term pairs on a
non-orthogonal (t, s)), optionally rule (b).  Edges: all non-orthogonal pairs of Z x Z (diagonal included).
Runs the emitter (emit1.emit), the Python mirrors check_cert / check_glue1, writes t1lean/cert/T1_<k>.json and a
log line.  usage: T1K=0,5 [RULES=ac|abc] python3 t1lean/t1case.py"""
import os, sys, json, time, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BASE, 't2hand', 'rev')); sys.path.insert(0, HERE)
from common import N, OR, FR
import emit1
rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if r['frame']]
RULES = os.environ.get('RULES', 'ac')
os.makedirs(os.path.join(HERE, 'cert'), exist_ok=True)
# stage-3 branch overrides (st3.py): dead mask T1MASK, extra valid frames T1XF (json list of line lists, frames
# leaving the mask: only rows orthogonal to their outside lines use them), target T1TGT, output name T1NAME
EXCL = {tuple(e) for e in json.load(open(os.environ['T1EXCL']))} if os.environ.get('T1EXCL') else set()   # unrefutable zero entries
XF = [tuple(E) for E in json.load(open(os.environ['T1XF']))] if os.environ.get('T1XF') else []
def run(k):
    t0 = time.time()
    mask = int(os.environ['T1MASK']) if os.environ.get('T1MASK') else int(rw[k]['mask'])
    Z = sorted(i for i in range(N) if mask >> i & 1); Zs = set(Z)
    frames = [E for E in FR if all(e in Zs for e in E)]
    fs_ = {frozenset(E) for E in frames}
    frames += [E for E in FR if frozenset(E) in {frozenset(x) for x in XF} and frozenset(E) not in fs_]
    edges = {}
    inF = {x for E in frames for x in E if x in Zs}      # entries between two lines in no inside frame: no zero step, left out
    for x in Z:
        for y in Z:
            if (x, y) in EXCL: continue
            if x == y or (not OR[x][y] and (x in inF or y in inF)): edges[(x, y)] = len(edges)
    RV = []; desc = []; seen = set()
    two = collections.defaultdict(list)          # (t, s) non-orth -> [(pair, frame)]
    for F in frames:
        Fs = set(F)
        outE = [f for f in F if f not in Zs]
        for t in Z:
            if t in Fs: continue
            if any(not OR[t][o] for o in outE): continue
            Tt = [f for f in F if not OR[t][f]]
            for s in Z:
                if s in Fs or s == t: continue
                K = [f for f in Tt if not OR[f][s]]
                if len(K) != 2: continue
                a, b = sorted(K)
                if not all(p in edges for p in ((t, a), (a, s), (t, b), (b, s))): continue
                if OR[t][s]:
                    key = ('a', t, a, s, b)
                    if key in seen: continue
                    seen.add(key)
                    E = edges
                    RV.append({E[(t, a)]: 1, E[(a, s)]: 1, E[(b, b)]: 1, E[(t, b)]: -1, E[(b, s)]: -1, E[(a, a)]: -1})
                    desc.append(('a', (t, a, s, b, tuple(F))))
                elif (t, s) in edges:
                    two[(t, s)].append(((a, b), F))
    nc = nb = 0
    for (t, s), lst in two.items():
        byp = {}
        for pr, F in lst: byp.setdefault(pr, F)
        nbr = collections.defaultdict(set)
        for (a, b) in byp: nbr[a].add(b); nbr[b].add(a)
        tris = set()
        for (a, b) in byp:
            for h in nbr[a] & nbr[b]: tris.add(tuple(sorted((a, b, h))))
        E = edges
        for (f1, f2, f3) in sorted(tris):
            for f, g, h in ((f1, f2, f3), (f2, f1, f3), (f3, f1, f2)):
                Ffg = byp[tuple(sorted((f, g)))]; Ffh = byp[tuple(sorted((f, h)))]; Fgh = byp[tuple(sorted((g, h)))]
                RV.append({E[(t, f)]: 1, E[(f, s)]: 1, E[(t, s)]: -1, E[(f, f)]: -1})
                desc.append(('c', (t, s, f, g, h, tuple(Ffg), tuple(Ffh), tuple(Fgh)))); nc += 1
        if 'b' in RULES:
            for f in nbr:
                ns = sorted(nbr[f])
                for g, h in itertools.combinations(ns, 2):
                    Ffg = byp[tuple(sorted((f, g)))]; Ffh = byp[tuple(sorted((f, h)))]
                    RV.append({E[(t, g)]: 1, E[(g, s)]: 1, E[(h, h)]: 1, E[(t, h)]: -1, E[(h, s)]: -1, E[(g, g)]: -1})
                    desc.append(('b', (t, s, f, g, h, tuple(Ffg), tuple(Ffh)))); nb += 1
    # merge equal relation dicts with opposite orientation issues: keep all (duplicates are harmless)
    t1 = time.time()
    DTREE = bool(os.environ.get('DTREE'))
    TGT = int(os.environ['T1TGT']) if os.environ.get('T1TGT') else None
    need0 = list(range(len(edges))) if TGT is None else [e for (x, y), e in edges.items() if TGT >> x & 1 and TGT >> y & 1]
    cert, st = emit1.emit(edges, RV, Z, need=need0, desc=desc, rows=Z, diagtree=DTREE)
    if not st['ok']:
        # lines with an undetermined entry leave zm (they are pinned by rank 7 in T3: LineH / OL)
        und = [xy for xy, e in edges.items() if str(e) not in {str(q) for q in cert['MK']} and e not in cert['MK']]
        badl = sorted({x for xy in und for x in xy})
        # greedy: drop the line with most undetermined entries until the rest is covered
        und = set(und); drop = set()
        while any(x not in drop and y not in drop for x, y in und):
            c_ = collections.Counter(z for x, y in und if x not in drop and y not in drop for z in (x, y))
            drop.add(c_.most_common(1)[0][0])
        zm = [x for x in Z if x not in drop and (TGT is None or TGT >> x & 1)]
        need = [e for (x, y), e in edges.items() if x in zm and y in zm]
        cert, st = emit1.emit(edges, RV, Z, need=need, desc=desc, rows=Z, diagtree=DTREE)
        st['dropped'] = sorted(drop); st['und'] = len(und)
        if os.environ.get('UNDDUMP'): json.dump(sorted(und), open(os.path.join(HERE, 'cert', 'UND_%d.json' % k), 'w'))
    else:
        zm = Z if TGT is None else [x for x in Z if TGT >> x & 1]
    cert['ZM'] = zm
    t2 = time.time()
    bad = emit1.check_cert(cert) if st['ok'] else ['not ok']
    badg = emit1.check_glue1(cert) if st['ok'] else ['not ok']
    json.dump(cert, open(os.path.join(HERE, 'cert', os.environ.get('T1NAME', 'T1_%d' % k) + '.json'), 'w'))
    print('T1 %d |Z|=%d frames %d edges %d rels %d (a %d, c %d, b %d) | %s | mirror %s glue %s | %.1fs + %.1fs' % (
        k, len(Z), len(frames), len(edges), len(RV), len(RV) - nc - nb, nc, nb, st, 'OK' if not bad else bad[:5],
        'OK' if not badg else badg[:5], t1 - t0, t2 - t1), flush=True)
for k in [int(a) for a in os.environ['T1K'].split(',')]: run(k)
