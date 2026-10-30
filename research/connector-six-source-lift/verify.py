"""Six-source integer lift and complete dirty connector endpoints. Apache-2.0."""
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
from random import Random
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,msg):
    if not ok:raise ValueError(msg)


def lifted(w,cut,b):
    k=len(cut);cnt=[0]*k;out=[tuple(cnt)]
    need(Counter(w)==Counter({j:b for j in range(k)}),'balanced template')
    need(all(0<=a<b for a in cut),'cuts')
    for j in w:
        cnt[j]+=1
        out.append(tuple(x if x<=cut[i] else x-b for i,x in enumerate(cnt)))
    need(out[-1]==(0,)*k,'restored lift')
    return out


def witnesses(lp):
    k=len(lp[0]);found={}
    for t,u in combinations_with_replacement(range(len(lp)),2):
        v=tuple(x+y for x,y in zip(lp[t],lp[u]))
        if all(x in(0,1) for x in v) and any(v):
            found.setdefault(sum(x<<j for j,x in enumerate(v)),[t,u])
    need(set(found)==set(range(1,1<<k)),'complete binary-mask cover')
    return found


def expand(w,cut,b,c):
    need(c>=b-1,'nonnegative expanded run')
    seen=[0]*len(cut);out=[];tau=[0]
    for j in w:
        seen[j]+=1
        out.extend([j]*(c-b+1 if seen[j]==cut[j]+1 else 1))
        tau.append(len(out))
    return out,tau


def prefixes(w,k,c):
    cnt=[0]*k;out=[tuple(cnt)]
    for j in w:
        cnt[j]=(cnt[j]+1)%c;out.append(tuple(cnt))
    return out


def reads_for_block(cert,c):
    w,tau=expand(cert['walk'],cert['cut'],cert['base_count'],c)
    reads={int(m):[tau[t] for t in pair]+[0]*(c-2)
           for m,pair in cert['readouts'].items()}
    return w,reads


def simulate(w,reads,k,c):
    need(Counter(w)==Counter({j:c for j in range(k)}),'balanced physical source calls')
    need(set(reads)==set(range(1,1<<k)),'all outputs')
    at=[[] for _ in range(len(w)+1)]
    for m,ts in reads.items():
        need(len(ts)==c and all(0<=t<=len(w) for t in ts),'readout count/range')
        for t in ts:at[t].append(m)
    z=[1]+[0]*k
    out={m:[1]+[0]*(k+1) for m in reads}
    for t,bucket in enumerate(at):
        for m in bucket:
            for j,x in enumerate(z):out[m][j+1]=(out[m][j+1]+x)%c
        if t<len(w):z[w[t]+1]=(z[w[t]+1]+1)%c
    need(z==[1]+[0]*k,'connector arbitrary dirt restored')
    for m,row in out.items():
        need(row==[1,0]+[(m>>j)&1 for j in range(k)],'complete dirty output')
    need(len(w)+sum(map(len,reads.values()))==c*(k+(1<<k)-1),'full call floor')
    return len(w)+sum(map(len,reads.values()))


def compose(cert,c,blocks=None,odd=None):
    if blocks is None:blocks=c//2
    if odd is None:odd=c%2
    need(2*blocks+odd<=c,'depth budget')
    base,tau=expand(cert['walk'],cert['cut'],cert['base_count'],c)
    w=[];parts=[]
    for b in range(blocks):
        off=len(w);w.extend(j+6*b for j in base)
        parts.append((6*b,6,{int(m):[off+tau[t] for t in pair]
                              for m,pair in cert['readouts'].items()}))
    if odd:
        off=len(w);j=6*blocks
        w.extend([j,j+1]+[j]*(c-1)+[j+1]*(c-1))
        parts.append((j,2,{1:[off+1],3:[off+2],2:[off+c+1]}))
    return w,parts,6*blocks+2*odd


def read_mask(m,parts,c):
    out=[]
    for j,k,table in parts:
        local=(m>>j)&((1<<k)-1)
        if local:out.extend(table[local])
    need(len(out)<=c,'available readouts')
    return sorted(out+[0]*(c-len(out)))


def mv(a,x,c):return tuple(sum(u*v for u,v in zip(row,x))%c for row in a)
def plus(a,b,c):return tuple((x+y)%c for x,y in zip(a,b))


def matrix_control(w,reads,k,c):
    rng=Random(6035+c)
    mat=lambda:tuple(tuple(rng.randrange(c) for _ in range(2)) for _ in range(2))
    vec=lambda:tuple(rng.randrange(c) for _ in range(2))
    bs=[mat() for _ in range(k)];xs=[vec() for _ in range(k)]
    aa={m:mat() for m in reads};ys={m:vec() for m in reads};initial=ys.copy()
    need(any(mv(a,mv(b,e,c),c)!=mv(b,mv(a,e,c),c)
             for a in aa.values() for b in bs for e in ((1,0),(0,1))),
         'matrix fixture really has noncommuting maps')
    z=vec();dirty=z;at=[[] for _ in range(len(w)+1)]
    for m,ts in reads.items():
        for t in ts:at[t].append(m)
    for t,bucket in enumerate(at):
        for m in bucket:ys[m]=plus(ys[m],mv(aa[m],z,c),c)
        if t<len(w):j=w[t];z=plus(z,mv(bs[j],xs[j],c),c)
    need(z==dirty,'matrix dirty connector')
    for m in reads:
        expected=initial[m]
        for j in range(k):
            if (m>>j)&1:expected=plus(expected,mv(aa[m],mv(bs[j],xs[j],c),c),c)
        need(ys[m]==expected,'noncommuting matrix endpoint')


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    cert=json.loads((HERE/'CERTIFICATE.json').read_text())
    need((cert['base_count'],cert['sources'],cert['depth'],cert['minimum_characteristic'])==(9,6,2,8),'claim data')
    lp=lifted(cert['walk'],cert['cut'],9)
    found=witnesses(lp)
    need(found=={int(m):pair for m,pair in cert['readouts'].items()},'canonical integer witnesses')
    old=json.loads((ROOT/'research/connector-five-halves-growth/CERTIFICATE.json').read_text())
    need(len(witnesses(lifted(old['template_walk'],old['template_cut'],6)))==31,'credited five-source positive control')
    expanded=0;literal_calls=0
    for c in range(8,41):
        w,tau=expand(cert['walk'],cert['cut'],9,c)
        need(Counter(w)==Counter({j:c for j in range(6)}),'expanded counts')
        qs=prefixes(w,6,c)
        for t,v in enumerate(lp):need(qs[tau[t]]==tuple(x%c for x in v),'integer-lift transfer')
        for m,pair in found.items():
            v=tuple((qs[tau[pair[0]]][j]+qs[tau[pair[1]]][j])%c for j in range(6))
            need(v==tuple((m>>j)&1 for j in range(6)),'expanded mask')
        expanded+=1
    for c in (8,9,10,11):
        w,rs=reads_for_block(cert,c);literal_calls+=simulate(w,rs,6,c)
        matrix_control(w,rs,6,c)
    w,parts,k=compose(cert,8,blocks=2,odd=0)
    literal_calls+=simulate(w,{m:read_mask(m,parts,8) for m in range(1,1<<k)},k,8)
    sampled=0;rng=Random(6054)
    for c in range(8,21):
        w,parts,k=compose(cert,c)
        need(k==2*c+2*(c//2),'source bound')
        qs=prefixes(w,k,c)
        masks=[1<<j for j in range(k)]+[(1<<k)-1]
        masks.extend(rng.randrange(1,1<<k) for _ in range(64))
        for m in masks:
            ts=read_mask(m,parts,c)
            got=tuple(sum(qs[t][j] for t in ts)%c for j in range(k))
            need(got==tuple((m>>j)&1 for j in range(k)),'composed mask')
            sampled+=1
    rejected(lambda:expand(cert['walk'],cert['cut'],9,7))
    rejected(lambda:compose(cert,8,blocks=5,odd=0))
    bad=cert['walk'].copy();bad[0]=bad[1]
    rejected(lambda:lifted(bad,cert['cut'],9))
    w,rs=reads_for_block(cert,8);bad={m:t[:] for m,t in rs.items()};bad[1].pop()
    rejected(lambda:simulate(w,bad,6,8))
    bad={m:t[:] for m,t in rs.items()};bad[1][0]=(bad[1][0]+1)%(len(w)+1)
    rejected(lambda:simulate(w,bad,6,8))
    print(json.dumps(dict(status='PASS_SIX_SOURCE_CONNECTOR_LIFT',integer_masks=len(found),
                         expanded_characteristics=expanded,literal_calls_checked=literal_calls,
                         composed_masks_checked=sampled,minimum_characteristic=8,
                         scope='uniform abstract connector construction; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
