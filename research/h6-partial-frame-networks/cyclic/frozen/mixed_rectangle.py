#!/usr/bin/env python3
"""Actual four-port H6 mixed-source compensation: complete all-input word.

The physical Clifford/adapter compiler is inherited, not executed here.
All ordinary frames, arbitrary dirt and both chronological orientations
are checked exactly. This is a bounded construction, not a full H6 supplier.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from collections import Counter
import hashlib
import json
import copy

HERE = Path(__file__).resolve().parent
H = 17
FULL = tuple(1 << i for i in reversed(range(H)))


def need(ok, label):
    if not ok: raise ValueError(label)


def basis(words):
    piv = {}
    for v in words:
        for k in sorted(piv, reverse=True):
            if v >> k & 1: v ^= piv[k]
        if v:
            k = v.bit_length()-1
            for j in list(piv):
                if piv[j] >> k & 1: piv[j] ^= v
            piv[k] = v
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def included(a,b): return len(basis(a+b)) == len(b)


def perp(v):
    k = (v & -v).bit_length()-1
    return basis((1 << i) ^ ((1 << k) if v >> i & 1 else 0) for i in range(H) if i != k)


def mm(a,b):
    return [xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a]


def xor(xs):
    z = 0
    for x in xs: z ^= x
    return z


def tr(a,n): return [sum(((row >> j) & 1) << i for i,row in enumerate(a)) for j in range(n)]


def inv(a):
    n = len(a); work = [row | (1 << (n+i)) for i,row in enumerate(a)]
    for j in range(n):
        p = next(i for i in range(j,n) if work[i] >> j & 1)
        work[j],work[p] = work[p],work[j]
        for i in range(n):
            if i != j and work[i] >> j & 1: work[i] ^= work[j]
    need([r & ((1<<n)-1) for r in work] == [1<<i for i in range(n)], "binary inverse")
    return [r >> n for r in work]


def cong(t,m): return mm(mm(t,m),tr(t,len(t)))


def symp(m):
    n = len(m); t = [1<<i for i in range(n)]; work = list(m)
    for k in range(0,n,2):
        a,b = next((a,b) for a in range(k,n) for b in range(k,n) if work[a] >> b & 1)
        for cur,dst in ((a,k),(b if b != k else a,k+1)):
            t[cur],t[dst] = t[dst],t[cur]
        work = cong(t,m)
        for i in range(k+2,n):
            left,right = (work[i] >> (k+1)) & 1,(work[i] >> k) & 1
            if left: t[i] ^= t[k]
            if right: t[i] ^= t[k+1]
        work = cong(t,m)
    need(work == [1 << (i^1) for i in range(n)], "symplectic congruence")
    return t


def canonical_roots():
    roots = []
    for i,j in combinations(range(8),2):
        for x,y in product((-2,2),repeat=2):
            a = [0]*8; a[i],a[j] = x,y; roots.append(tuple(a))
    roots.extend(a for a in product((-1,1),repeat=8) if sum(a) % 4 == 0)
    return sorted({a if next(x for x in a if x) > 0 else tuple(-x for x in a) for a in roots})


def dot(a,b):
    z = sum(x*y for x,y in zip(a,b))
    need(z % 4 == 0, "integral E8 pairing")
    return z//4


def actual_labels(ports):
    # Source-faithful bit implementation of e8_cubed.py::binary_labels.
    roots = canonical_roots()
    gram = [sum((dot(a,b)&1)<<j for j,b in enumerate(roots)) for a in roots]
    work = list(gram); av = list(range(120)); sel = []
    while any(work[a] >> b & 1 for a in av for b in av):
        a,b = next((a,b) for a in av for b in av if work[a] >> b & 1)
        sel.extend((a,b)); left,right = work[a],work[b]
        work = [r ^ (right if left >> i & 1 else 0) ^ (left if right >> i & 1 else 0) for i,r in enumerate(work)]
        av.remove(a); av.remove(b)
    need(len(sel) == 8, "binary E8 basis size")
    qq = [roots[i] for i in sel]
    small = [sum(((gram[i]>>j)&1)<<k for k,j in enumerate(sel)) for i in sel]
    inverse = inv(small)
    form = inverse + [r << 8 for r in inverse]
    eg = [((1<<16)-1) ^ (1<<i) for i in range(16)]
    change = mm(inv(symp(form)),symp(eg))
    need(cong(change,eg) == form, "standard-dot isometry")
    eb = [(1 << i) | (1 << 16) for i in range(16)]
    mapping = mm(change,eb)
    packed = []
    for p in ports:
        c = sum((dot(p[8*b:8*(b+1)],q)&1) << (8*b+j) for b in range(2) for j,q in enumerate(qq))
        packed.append(((1<<17)-1) ^ mm([c],mapping)[0])
    for i,p in enumerate(ports):
        for j,q in enumerate(ports):
            need((packed[i]&packed[j]).bit_count()%2 == (1+dot(p,q))%2, "actual H6 address identity")
    return packed, [2160+roots.index(p[:8])*240+2*roots.index(p[8:]) for p in ports]


def fixture():
    a = (2,-2,0,0,0,0,0,0)
    c = (2,0,-2,0,0,0,0,0)
    bb = [a,(0,0,2,-2,0,0,0,0),(0,0,0,0,2,-2,0,0),(0,0,0,0,0,0,2,-2)]
    ports = [a+bb[0],a+bb[1],c+bb[2],c+bb[3]]
    labels,indices = actual_labels(ports)
    u = [basis(labels[:2]),basis(labels[2:])]
    need(list(map(len,u)) == [2,2] and len(basis(u[0]+u[1])) == 3, "actual intersecting planes")
    need(not included(u[0],u[1]) and not included(u[1],u[0]), "incomparable mixing planes")
    k = [[F(dot(p,q)**3-4*dot(p,q),48) for q in ports] for p in ports]
    aa = [[F(int(i == j))-k[i][j] for j in range(4)] for i in range(4)]
    need(aa == [[F(1,16) if (i<2)!=(j<2) else F(0) for j in range(4)] for i in range(4)], "actual rank-two compensation")
    starts = {f'x{i}':basis([labels[i]]) for i in range(4)}
    starts.update({f'y{i}':() for i in range(4)})
    starts.update({f'c{i}':() for i in range(4)})
    starts.update({'h0':(),'h1':()})
    ends = {r:FULL for r in starts}
    ends.update({f'y{i}':perp(labels[i]) for i in range(4)})
    ev = []
    def add(dst,src,q,tag): ev.append({'op':'add','dst':dst,'src':src,'q':str(q),'tag':tag})
    def climb(r,f,tag): ev.append({'op':'climb','register':r,'frame':list(f),'tag':tag})
    # Every target remains at zero through all dirt prefixes and K scatters.
    for i in range(4):
        add(f'y{i}',f'h{1 if i<2 else 0}',-F(1,16),'comp_prefix')
        for j in range(4):
            if k[i][j]: add(f'y{i}',f'c{j}',-k[i][j],'K_prefix')
    for g in range(2):
        for i in range(2*g,2*g+2): climb(f'x{i}',u[g],'source_plane')
        climb(f'h{g}',u[g],'mixed_gather_plane')
        for i in range(2*g,2*g+2): add(f'h{g}',f'x{i}',F(1),'comp_gather')
    for i in range(4): climb(f'x{i}',FULL,'source_full')
    for i in range(4):
        climb(f'c{i}',FULL,'K_center_full')
        add(f'c{i}',f'x{i}',F(1),'K_gather')
    for j in range(4):
        ev.append({'op':'private','center':f'c{j}','targets':[[f'y{i}',str(k[i][j])] for i in range(4) if k[i][j]],'tag':'K_private'})
    for i in range(4): add(f'c{i}',f'x{i}',-F(1),'K_restore')
    for i in range(4): climb(f'y{i}',u[1 if i<2 else 0],'target_plane')
    for i in range(4): add(f'y{i}',f'h{1 if i<2 else 0}',F(1,16),'comp_scatter')
    for i in range(4): climb(f'y{i}',perp(labels[i]),'target_cap')
    for g in range(2):
        climb(f'h{g}',FULL,'mixed_restore_full')
        for i in range(2*g,2*g+2): add(f'h{g}',f'x{i}',-F(1),'comp_restore')
    return {'ports_doubled':ports,'source_indices':indices,'labels':labels,'planes':[list(x) for x in u],
            'K':[[str(q) for q in r] for r in k],
            'starts':{r:list(f) for r,f in starts.items()},'ends':{r:list(f) for r,f in ends.items()},'events':ev}


def replay(fix,dual=False,omit=None):
    frames = {r:tuple(f) for r,f in fix['starts'].items()}
    cols = list(frames); n = len(cols)
    rows = {r:[F(int(i == j)) for j in range(n)] for i,r in enumerate(cols)}
    paths = {r:[] for r in rows}; peak = F(1); depth = 0; adds = 0; primitives = 0
    def accumulate(dst,src,q):
        nonlocal peak,depth,adds,primitives
        need(frames[dst] == frames[src], 'equal current frames')
        rows[dst] = [x+q*y for x,y in zip(rows[dst],rows[src])]
        peak = max(peak,sum(map(abs,rows[dst])))
        depth = max(depth,max(v.denominator.bit_length()-1 for v in rows[dst]))
        adds += 1
        a,b = abs(q.numerator),q.denominator
        primitives += 0 if not a else 3+a.bit_length()-1+a.bit_count()+b.bit_length()-1
    for event in fix['events']:
        if event['tag'] == omit: continue
        if event['op'] == 'climb':
            r = event['register']; f = tuple(event['frame'])
            need(f == basis(f) and included(frames[r],f), 'monotone canonical frame')
            if len(f) != len(frames[r]): paths[r].append(len(f)-len(frames[r]))
            frames[r] = f
        elif event['op'] == 'add':
            dst,src,q = event['dst'],event['src'],F(event['q'])
            if dual: dst,src,q = src,dst,-q
            accumulate(dst,src,q)
        else:
            c = event['center']; targets = [(r,F(q)) for r,q in event['targets']]
            need(frames[c] == FULL and all(frames[r] == () for r,q in targets), 'private entrance')
            r = 'private'; rows[r] = [F(0)]*n; frames[r] = () if dual else FULL
            primitives += 1  # initial clear
            if dual:
                for y,q in targets: accumulate(r,y,q)
                frames[r] = FULL
                accumulate(c,r,-F(1))
            else:
                rows[r] = list(rows[c]); primitives += 1  # paid copy
                peak = max(peak,sum(map(abs,rows[r])))
                frames[r] = ()
                for y,q in targets: accumulate(y,r,q)
            primitives += 1  # final clear
            del rows[r]; del frames[r]
    need(frames == {r:tuple(f) for r,f in fix['ends'].items()}, 'every endpoint frame')
    for i,r in enumerate(cols):
        expected = [F(int(i == j)) for j in range(n)]
        if (not dual and r.startswith('y')) or (dual and r.startswith('x')):
            wanted = ('x' if not dual else 'y')+r[1:]
            expected[cols.index(wanted)] += -1 if dual else 1
        need(rows[r] == expected, 'all-column exact identity with arbitrary dirt')
    profile = Counter(r for path in paths.values() for r in path)
    private_count = sum(event['op'] == 'private' for event in fix['events'])
    profile[17] += private_count  # separate from ordinary center climbs
    return {'orientation':'dual' if dual else 'forward','paths':paths,
            'private_episodes':private_count,'private_rank':17*private_count,'profile':dict(sorted(profile.items())),
            'rank_mass':sum(r*n for r,n in profile.items()),'scalar_adds':adds,
            'scalar_primitives_before_real_doubling':primitives,'logical_prefix_row_l1':str(peak),
            'logical_prefix_denominator_depth':depth}


def main():
    fix = fixture(); out = [replay(fix),replay(fix,True)]
    need(out[0]['scalar_primitives_before_real_doubling'] == 300, 'forward complete scalar bill')
    need(out[1]['scalar_primitives_before_real_doubling'] == 312, 'dual complete scalar bill')
    rejected = []
    for tag in ('comp_prefix','comp_gather','comp_scatter','comp_restore','K_prefix','K_gather','K_private','K_restore','source_plane','target_plane'):
        for dual in (False,True):
            try: replay(fix,dual,tag)
            except ValueError as e: rejected.append({'omit':tag,'dual':dual,'gate':str(e)})
            else: raise ValueError('control was not rejected: '+tag)
    bad = copy.deepcopy(fix)
    # A single helper cannot visit both source-mixing planes monotonically.
    event = next(e for e in bad['events'] if e['tag'] == 'mixed_restore_full' and e['register'] == 'h0')
    event['frame'] = fix['planes'][1]
    try: replay(bad)
    except ValueError as e: rejected.append({'mutant':'unpaid_plane_reuse','gate':str(e)})
    else: raise ValueError('incomparable plane reuse accepted')
    source = Path('/Users/ross/git/math/integer-mult-bounds/research/niemeier-lattices/code/e8_cubed.py')
    result = {'status':'PASS_ACTUAL_H6_MIXED_RECTANGLE_ALL_INPUT_WORD_NO_NEW_KAPPA',
              'canonical_head':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
              'actual_geometry_source':str(source),'actual_geometry_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'fixtures':fix,'orientations':out,'rejected_controls':rejected,
              'ordinary_comp_helpers':2,'edge_baseline_helpers':8,
              'cost_limitation':'Four full-width K centers have private rank68, so this four-port finite supplier has negative all-stage coverage even before compensation. The full30960-port H6 K factor has816 centers and C13872; no composition of these rectangles or full-domain loading/chronology is constructed.',
              'remaining':'Frame Clifford phases/adapters, coefficient temporary streams, approximate-child precision, actual banks/controller/tape and full-domain composition are not independently verified.'}
    (HERE/'MIXED-RECTANGLE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+' ports=4 helpers=2_vs8 controls='+str(len(rejected))+' primitives=300/312')


if __name__ == '__main__': main()
