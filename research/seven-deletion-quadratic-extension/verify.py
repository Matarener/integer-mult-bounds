#!/usr/bin/env python3
"""Check every deletion class and the uniform all-pivot proof premises.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import array
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
MASK = (1 << 120)-1


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((ROOT/'SOURCES.json').read_text())['files']
    inputs = [r for r in rows if r['usage'] == 'input']
    for r in inputs:
        need(hashlib.sha256((REPO/r['path']).read_bytes()).hexdigest() == r['sha256'], 'source hash: '+r['path'])
    return len(inputs)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


s = load('p105_source', 'research/complex-rank8-rigidity-p105/verify.py')


def add3(a, b, c, d):
    z1, z2 = MASK ^ (a | b), MASK ^ (c | d)
    return (z1 & c) | (a & z2) | (b & d), (z1 & d) | (b & z2) | (a & c)


def rank3(pairs, target=121):
    basis = {}
    for a, b in pairs:
        while a | b:
            pivot = (a | b).bit_length()-1
            if pivot not in basis:
                basis[pivot] = (b, a) if (b >> pivot) & 1 else (a, b)
                if len(basis) == target:
                    return target
                break
            c, d = basis[pivot]
            if (a >> pivot) & 1:
                c, d = d, c
            a, b = add3(a, b, c, d)
    return len(basis)


def dense_rank(rows, prime=3):
    basis = {}
    for row in rows:
        v = [x % prime for x in row]
        for j in sorted(basis):
            c = v[j]
            if c:
                v = [(x-c*y) % prime for x, y in zip(v,basis[j])]
        j = next((j for j,x in enumerate(v) if x), None)
        if j is not None:
            inv = pow(v[j],-1,prime)
            basis[j] = [x*inv % prime for x in v]
    return len(basis)


def encode(row):
    return sum(1<<i for i,x in enumerate(row) if x % 3 == 1), sum(1<<i for i,x in enumerate(row) if x % 3 == 2)


def small_orbits(k, gens):
    remaining = set(itertools.combinations(s.P112,k))
    result = []
    while remaining:
        start = min(remaining)
        todo, orbit = [start], {start}
        while todo:
            t = todo.pop()
            for g in gens:
                v = tuple(sorted(g[i] for i in t))
                if v not in orbit:
                    orbit.add(v)
                    todo.append(v)
        need(orbit <= remaining,'orbit partition')
        remaining -= orbit
        result.append(list(start))
    return result


def unit_levels():
    data = json.loads(gzip.decompress(s.UNITS_FILE.read_bytes()))
    small = json.loads((ROOT/'SMALL.json').read_text())
    return {**{int(k):v for k,v in small.items()},4:data['reps4'],5:data['p107'],
            6:data['p106'],7:[r[:7] for r in data['p105']]}


def cover():
    gens = s.stabiliser(s.FRAME0)[::s.GEN_STEP]
    need(len(gens)==8,'eight retained generators')
    frame_set = set(s.FRAMES)
    for g in gens:
        need(sorted(g)==list(range(120)) and {g[i] for i in s.FRAME0}==set(s.FRAME0),'frame stabilizer')
        need(all(tuple(sorted(g[i] for i in frame)) in frame_set for frame in s.FRAMES),'frame transport')
    levels = unit_levels()
    for k in (0,1,2,3):
        need(small_orbits(k,gens)==levels[k],'small orbit cover')
    H=s.closure(gens)
    need(len(H)==172032,'complete generated group')
    torbs=s.triple_orbits(gens)
    need({v for o in torbs for v in o}==set(itertools.combinations(s.P112,3)),'all triples')
    raw=array.array('I');raw.frombytes(gzip.decompress(s.COVER_FILE.read_bytes()))
    if sys.byteorder!='little':raw.byteswap()
    offset=0;prev=[o[0] for o in torbs];stats={}
    for k in (4,5,6,7):
        count=raw[offset];js=raw[offset+1:offset+1+count];ns=raw[offset+1+count:offset+1+2*count]
        offset+=1+2*count
        candidates=sorted({tuple(sorted(tuple(r)+(x,))) for r in prev for x in s.P112 if x not in r})
        need(len(candidates)==count==len(js)==len(ns),'cover lengths')
        need(all(len(set(r))==k and set(r)<=set(s.P112) for r in levels[k]),'valid representatives')
        need(set(js)==set(range(len(levels[k]))),'every unit used')
        for c,j,n in zip(candidates,js,ns):
            need(n<len(H) and tuple(sorted(H[n][y] for y in levels[k][j]))==c,'cover transporter')
        stats[k]={'candidates':count,'units':len(levels[k])}
        prev=levels[k]
    need(offset==len(raw),'no unparsed cover data')
    wrong=list(levels[7][js[0]]);wrong[0]=119
    need(tuple(sorted(H[ns[0]][y] for y in wrong))!=candidates[0],'damaged unit control')
    return {'group':len(H),'levels':stats,'small_units':{k:len(levels[k]) for k in range(4)}}


def check_unit(item):
    k,X=item
    dead=s.F0MASK|sum(1<<i for i in X)
    rows=[r for r in s.FMASK if not r&dead]
    target=112-k-35
    rank=rank3(((r,0) for r in s.chain_first(rows,target)),target)
    need(rank==target,'extension rank fails: '+str(X))
    return k,len(rows),rank


def census(part, jobs):
    i,n=map(int,part.split('/'))
    need(n==2 and i in (1,2) and 1<=jobs<=16,'registered part and worker bounds')
    levels=unit_levels()
    all_units=[(k,tuple(X)) for k in range(8) for X in levels[k]]
    chosen=all_units[i-1::n]
    hist=Counter();minimum=2026;maximum=0;count=0;digest=hashlib.sha256()
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for item,(k,frames,rank) in zip(chosen,pool.map(check_unit,chosen,chunksize=128)):
            hist[k]+=1;count+=1;minimum=min(minimum,frames);maximum=max(maximum,frames)
            digest.update(json.dumps([item,k,frames,rank],separators=(',',':')).encode()+b'\n')
    need(count==len(chosen),'all assigned units checked')
    return {'part':part,'units':count,'levels':dict(hist),'live_frame_range':[minimum,maximum],'certificate_sha256':digest.hexdigest()}


def geometry():
    roots=s.LINES
    need(len(roots)==120 and len(s.FRAMES)==2025,'full E8 geometry')
    need(all(sum(x*x for x in v)==8 for v in roots),'root norm')
    need(all(sum(x*y for x,y in zip(v,w))%4==0 for v in roots for w in roots),'integral source inner product')
    # Check the trace-zero quadratic tight-frame operator on a complete basis.
    forms=[]
    for i,j in itertools.combinations(range(8),2):
        H=[[0]*8 for _ in range(8)];H[i][j]=H[j][i]=1;forms.append(H)
    for i in range(7):
        H=[[0]*8 for _ in range(8)];H[i][i]=1;H[7][7]=-1;forms.append(H)
    for H in forms:
        vals=[sum(H[i][j]*v[i]*v[j] for i in range(8) for j in range(8)) for v in roots]
        need(all(sum(q*v[i]*v[j] for q,v in zip(vals,roots))==192*H[i][j]
                 for i in range(8) for j in range(8)),'quadratic tight frame')
        need(all(sum(vals[i] for i in F)==0 for F in s.FRAMES),'quadratic frame kernel')
    need(all(abs(sum(x*y for x,y in zip(v,w))**2-8)==8
             for j,v in enumerate(roots) for w in roots[j+1:]),'quadratic coherence')
    need(56+16*8<192 and 56+17*8==192,'uniform injectivity through 17 missing roots')
    for ai in s.P112:
        a=roots[ai]
        pairs=[(b,sum(x*y for x,y in zip(a,b))) for j,b in enumerate(roots) if j!=ai]
        pairs=[(b,t) for b,t in pairs if t]
        need(len(pairs)==56 and all(abs(t)==4 for _,t in pairs),'56 nonorthogonal lines')
        projected=[tuple(2*x-(t//4)*y for x,y in zip(b,a)) for b,t in pairs]
        need(all(sum(v[i]*v[j] for v in projected)==192*int(i==j)-24*a[i]*a[j]
                 for i in range(8) for j in range(8)),'projected root tight frame')
        for i,v in enumerate(projected):
            dots=[abs(sum(x*y for x,y in zip(v,w))) for j,w in enumerate(projected) if j!=i]
            need(sum(x==24 for x in dots)==1 and all(x in (8,24) for x in dots),'projected coherence and one twin')
        need(sum(bool(s.G[ai][j]) for j in s.FRAME0)==4,'four removed nonorthogonal lines')
        need(sum(s.G[ai][j]==0 for j in s.FRAME0)==4,'four removed orthogonal lines')
    need(24+24+9*8<192,'seven cross terms stay independent')
    return {'quadratic_basis':35,'quadratic_frame_constant':192,'quadratic_injectivity_missing_limit':17,
            'pivot_roots':112,'projected_frame_constant':192,'missing_projection_bound':120}


def controls():
    rng=random.Random(81668);cases=0
    for n in range(1,9):
        for m in range(1,9):
            for _ in range(8):
                rows=[[rng.randrange(3) for _ in range(n)] for _ in range(m)]
                need(rank3(map(encode,rows))==dense_rank(rows),'packed versus dense F3')
                cases+=1
    for a,b in itertools.product(range(3),repeat=2):
        x,y=add3(*encode([a]),*encode([b]))
        need((x+2*y)%3==(a+b)%3,'all scalar additions')
    boundary=load('boundary_source','research/full-family-g-without-d/verify.py')
    need(boundary.LINES==s.LINES,'boundary line ordering')
    failures=restores=0
    for fx in boundary.FIXTURES:
        X,F,k=fx['X'],fx['F'],fx['k']
        frames,non,odd=boundary.setup(X,F)
        need(all(len(v)==4 for v in odd.values()),'four-coordinate blocks')
        nb,w=boundary.blocks_w(F,non,odd)
        need(nb and w and boundary.condition_g(non,odd,frames),'eight-deletion source premises')
        I,rows,h=boundary.incidence(F,k,non,frames)
        z=[fx['cert'].get(i,0) for i in I]
        need(boundary.kernel_ok(rows,h+[z]),'boundary kernel equations')
        need(boundary.rank_fraction(h+[z])==8,'boundary extra kernel direction')
        need(boundary.rank_fraction(rows)==len(I)-8,'exact boundary defect')
        dead=s.F0MASK|sum(1<<i for i in X)
        global_rows=[r for r in s.FMASK if not r&dead]
        need(rank3(((r,0) for r in global_rows),69)==69,'extension survives at boundary fixture')
        bad=z[:];bad[next(i for i,x in enumerate(bad) if x)]*=-1
        need(not boundary.kernel_ok(rows,[bad]),'damaged boundary certificate')
        failures+=1
        for x in X:
            live,non,odd=boundary.setup(tuple(y for y in X if y!=x),F)
            for j in range(8):
                I,rows,h=boundary.incidence(F,j,non,live)
                need(dense_rank(rows)==len(I)-7 and dense_rank(h)==7,'all restored pivot coordinates')
                restores+=1
    # A deficient frame family must not pass the new global rank boundary.
    need(rank3([(s.FMASK[0],0)],77)==1,'missing-frame rejection')
    return {'dense_F3_comparisons':cases,'scalar_additions':9,'sharp_boundary_fixtures':failures,
            'restored_coordinate_checks':restores,'damaged_certificate_controls':2,'deficient_family_controls':1,
            'boundary_extension_ranks':[69,69]}


def e7():
    q=load('e7_source','research/e7-quadratic-support/verify.py')
    need(q.check_root_transitivity()==120,'E7 root transport')
    roots=tuple(r for r in q.e8_lines() if q.dot(r,q.PIVOT)==0)
    q.validate_domain(roots)
    frames=q.orthogonal_frames(roots);rows=tuple(sum(1<<j for j in frame) for frame in frames)
    basis,free=q.binary_kernel(rows);q.check_witness(roots,frames)
    controls=q.rejection_controls(roots,rows,basis,free)
    visited,minimum=q.full_weight_census(basis)
    need(visited==134217727 and minimum==12,'retained E7 support theorem')
    return {'visited':visited,'minimum':minimum,'controls':controls,'frames':len(frames)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cover',action='store_true');ap.add_argument('--e7',action='store_true');ap.add_argument('--part');ap.add_argument('--jobs',type=int,default=4)
    args=ap.parse_args();authenticate()
    need(sum(bool(x) for x in (args.cover,args.e7,args.part))==1,'select one complete phase')
    if args.cover: result={'coverage':cover(),'geometry':geometry(),'controls':controls()}
    elif args.e7: result={'e7':e7()}
    else: result={'census':census(args.part,args.jobs)}
    key='cover' if args.cover else 'e7' if args.e7 else 'part'+args.part
    expected=json.loads((ROOT/'RESULT.json').read_text())['phases']
    result=json.loads(json.dumps(result))
    need(key in expected and result==expected[key],'committed phase result differs')
    print(json.dumps({'status':'PASS_SEVEN_DELETION_QUADRATIC_EXTENSION',**result},sort_keys=True),flush=True)


if __name__=='__main__':main()
