#!/usr/bin/env python3
"""Separate integer-matrix check; imports no primary or predecessor executable."""
import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
SCALE=65536
ORDER=[f'{p}{i}' for p,n in [('X',104),('Y',104),('Q',8),('G',32),('D',32)] for i in range(n)]
J=[0,1,3,6,22,31,93,103]
N=[n for n in range(104) if n not in J]
TF=[[2,2,2,-2,0,0,0,0],[0,0,2,2,2,-2,0,0],[0,0,0,0,2,-2,-2,2],
    [2,2,2,2,0,0,0,0],[2,2,-2,-2,0,0,0,0],[0,-2,0,-2,2,0,-2,0],
    [-2,2,-2,2,0,0,0,0],[0,-2,2,0,-2,0,0,-2]]


def check(ok,message):
    if not ok: raise ValueError(message)


def read(path,digest):
    b=path.read_bytes()
    check(hashlib.sha256(b).hexdigest()==digest,'independent source pin')
    return json.loads(b)


def data():
    g=read(ROOT/'inputs/PR3882_geometry.json','8212331ef435650469b6fca71448bcc2915a0cab46562acc41c5fc2a3dfa56c7')
    roots=set()
    for a in range(8):
        for b in range(a):
            for x,y in itertools.product((-2,2),repeat=2):
                r=[0]*8;r[a],r[b]=x,y
                if next(t for t in r if t)<0:r=[-t for t in r]
                roots.add(tuple(r))
    for r in itertools.product((-1,1),repeat=8):
        if sum(r)%4==0:
            roots.add(r if r[0]>0 else tuple(-x for x in r))
    remove=set(map(tuple,g['F0']+g['C']))
    roots=sorted(roots-remove)
    check(len(roots)==104,'independent roots')
    gram8=[[sum(x*y for x,y in zip(r,s)) for s in roots] for r in roots]
    twiceB=[[gram8[j][n]//4 for n in N] for j in J]
    check(all(gram8[j][n]%4==0 for j in J for n in N),'independent half alphabet')
    return g,gram8,twiceB


def add(s,target,source,numerator,denominator=1):
    donor=s[source][:]
    vals=[numerator*v for v in donor]
    check(all(v%denominator==0 for v in vals),'exact integer-scaled division')
    s[target]=[a+v//denominator for a,v in zip(s[target],vals)]


def identity():
    return {n:[SCALE*int(i==j) for j in range(280)] for i,n in enumerate(ORDER)}


def dense_digest(s):
    rows=[[str(Fraction(v,SCALE)) for v in s[n]] for n in ORDER]
    b=(json.dumps(rows,sort_keys=True,separators=(',',':'))+'\n').encode()
    return hashlib.sha256(b).hexdigest()


def frame_key(vectors):
    """Reduced binary pivot rows, independent of the primary span enumerator."""
    pivots={}
    for value in vectors:
        check(type(value) is int and 0<value<512,'independent binary vector')
        for bit in sorted(pivots,reverse=True):
            if value & (1<<bit): value ^= pivots[bit]
        check(value!=0,'independent frame basis')
        new=value.bit_length()-1
        for bit in list(pivots):
            if pivots[bit] & (1<<new):pivots[bit] ^= value
        pivots[new]=value
    return tuple(pivots[k] for k in sorted(pivots,reverse=True))


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--algebra-only',action='store_true')
    a=args.parse_args()
    geom,g,b=data()
    pred=read(ROOT/'inputs/PR3882_RESULT.json','33eaae6c77c10bed705d76b7950e7f8a6d5e09cd5727eadcde6f853c37be3f2b')
    s=identity()
    # Suffix reconstructed through block multiplication, not primary sparse code.
    cleanup=[[0]*104 for _ in range(8)]
    for k in range(8):
        for t,j in enumerate(J):cleanup[k][j]=TF[k][t]
        for v,n in enumerate(N):
            z=sum(TF[k][t]*b[t][v] for t in range(8))
            check(z%2==0,'cleanup integral');cleanup[k][n]=z//2
    check(sum(x!=0 for r in cleanup for x in r)==416,'cleanup support')
    if a.algebra_only:
        for i in range(104):s[f'Y{i}'][:104]=[SCALE*x//8 for x in g[i]]
        for k in range(8):s[f'Q{k}'][:104]=[-SCALE*x for x in cleanup[k]]
    else:
        word=read(REPO/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json',
                  '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e')
        fixture=read(REPO/'research/p104-native-channel/inputs/P104-FIXTURE.json',
                     '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4')
        check(all(fixture['section4_explicit_P104'][k]==geom[k] for k in ('F0','C')),'independent extraction')
        check(len(word['program'])==4058,'word extent')
        actual=[[0]*104 for _ in range(8)]
        for e in word['program'][3642:]:
            check(e[0]=='add' and e[1].startswith('Q') and e[2].startswith('X'),'suffix opcode')
            c=Fraction(e[3]);check(c.denominator==1,'suffix integer')
            actual[int(e[1][1:])][int(e[2][1:])]+=c.numerator
        check(actual==cleanup,'independent literal cleanup factor')
        frames={k:frame_key(v) for k,v in word['initial_frames'].items()}
        paid=[]
        for e in word['program'][:3642]:
            op,r=e[:2]
            if op=='transport':
                check(frames[r]==frame_key(e[2]),'independent source frame')
                paid.append(abs(len(e[2])-len(e[3])))
                check(paid[-1]==e[4],'independent tariff')
                frames[r]=frame_key(e[3])
            elif op=='add':
                check(frames[r]==frames[e[2]]==frame_key(e[4]),'independent ADD chart')
                c=Fraction(e[3]);add(s,r,e[2],c.numerator,c.denominator)
            elif op=='zero':
                check(r=='C' and r not in s,'independent private lifetime')
                s[r]=[0]*280;frames[r]=frame_key(e[2])
            elif op=='copy':
                check(r=='C' and not any(s[r]) and frames[r]==frames[e[2]]==frame_key(e[3]),'independent private copy')
                s[r]=s[e[2]][:]
            else:
                check(op=='erase' and r=='C' and frames[r]==frame_key(e[2]),'independent owned erase')
                del s[r];del frames[r]
        check(frames=={k:frame_key(v) for k,v in word['final_frames'].items()},'independent cut frames')
        check(len(paid)==1410 and sum(paid)==2368,'independent whole-prefix tariff')
        check(set(s)==set(ORDER),'independent bank inventory')
        for k in range(8):
            want=[0]*280;want[208+k]=SCALE;want[:104]=[-SCALE*x for x in cleanup[k]]
            check(s[f'Q{k}']==want,'independent dirty-Q cut')
    # Different block order from the primary literal half/unit/double schedule.
    # These are exact coefficient additions; the primary tests literal tariffs.
    for t,j in enumerate(J):
        for v,n in enumerate(N):
            add(s,f'Y{j}',f'X{n}',-b[t][v],2)
            add(s,f'X{j}',f'X{n}',b[t][v],2)
    for v,n in enumerate(N):
        for t,j in enumerate(J):add(s,f'X{n}',f'X{j}',-b[t][v],2)
        add(s,f'X{n}',f'Y{n}',1)
    for k in range(8):
        for t,j in enumerate(J):add(s,f'Q{k}',f'X{j}',TF[k][t])
    check(dense_digest(s)==pred['endpoint_sha256'],'independent full endpoint')
    for k in range(208,280):
        check(s[ORDER[k]]==[SCALE*int(i==k) for i in range(280)],'independent dirty restoration')
    # Independently execute the constructive legacy adapter.
    for v,n in enumerate(N):
        for t,j in enumerate(J):add(s,f'Y{n}',f'X{j}',-b[t][v],2)
        add(s,f'X{n}',f'Y{n}',-1)
        add(s,f'Y{n}',f'X{n}',1)
    for t,j in enumerate(J):
        for v,n in enumerate(N):add(s,f'X{j}',f'X{n}',-b[t][v],2)
    for i in range(104):
        check(s[f'X{i}']==[SCALE*int(k==i) for k in range(280)],'independent original source')
        check(s[f'Y{i}']==[SCALE*int(k in (i,104+i)) for k in range(280)],'independent retained sum')
    mode='ALGEBRA_ONLY' if a.algebra_only else 'SOURCE_BOUND'
    print('PASS_P104_RESIDUAL_CONSUMER_INDEPENDENT_'+mode+' columns=280 helpers=72 legacy_sources=104')

if __name__=='__main__':main()
