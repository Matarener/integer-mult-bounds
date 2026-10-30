"""Exact signed error transfer with explicit sites and injection scales.

Adapted from the credited PR5819/5826/5831 transfer method. COPY is an exact
scaled overwrite here. Every omitted physical SCALE has no defect site.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256


def need(ok,message):
    if not ok:raise ValueError(message)


def add(dst,src,q):
    for i,v in src.items():
        z=dst.get(i,F(0))+q*v
        if z:dst[i]=z
        else:dst.pop(i,None)


def hash_row(row):
    h=sha256()
    for j in sorted(row,reverse=True):
        v=row[j];h.update(f'{j}:{v.numerator}/{v.denominator};'.encode())
    return h.hexdigest()


def ideal(word,sites):
    n=word['public']+word['owned_fields'];rows=[{i:F(1)} for i in range(n)];norms=[F(1)]*n;weights=[];peak=F(1)
    for j,e in enumerate(word['program']):
        op,r=e[:2];a,c=norms[r],F(1)
        if op in ('INIT','CLEAR'):rows[r]={}
        elif op=='SCALE':
            q=F(e[-2]);a,c=abs(q)*norms[r],abs(q);rows[r]={i:q*v for i,v in rows[r].items()}
        elif op in ('ADD','COPY'):
            s=e[2];q=F(e[-2])
            if op=='COPY':
                need(not rows[r],'ideal zero COPY destination');rows[r]={i:q*v for i,v in rows[s].items()}
            else:a,c=norms[r]+abs(q)*norms[s],1+abs(q);add(rows[r],rows[s],q)
        else:need(op=='MOVE','known operation')
        norms[r]=sum(map(abs,rows[r].values()),F(0));peak=max(peak,norms[r]);weights.append((a,c) if j in sites else (F(0),F(0)))
    active=set(word['live'])
    for r,row in enumerate(rows):
        expected={r:F(1)} if r<word['public'] else {}
        if r-112 in active:expected[r-112]=F(1)
        need(row==expected,'all arbitrary-input endpoint rows')
    return weights,peak


def trace(word,weights,sites,injections=None,scales=None):
    n=word['public']+word['owned_fields'];rows=[{} for _ in range(n)];scores=[[F(0)]*3 for _ in range(n)];peaks=[dict(value=F(0),cut=0,role=0) for _ in range(3)];witness={};stream=sha256()
    for j,e in enumerate(word['program']):
        op,r=e[:2]
        if op in ('INIT','CLEAR'):rows[r]={};scores[r]=[F(0)]*3
        elif op=='COPY':
            q=F(e[-2]);rows[r]={i:q*v for i,v in rows[e[2]].items()};scores[r]=[abs(q)*v for v in scores[e[2]]]
        elif op=='SCALE':
            q=F(e[-2]);rows[r]={i:q*v for i,v in rows[r].items()};scores[r]=[abs(q)*v for v in scores[r]]
        elif op=='ADD':
            q=F(e[-2])
            for i,v in rows[e[2]].items():
                old=rows[r].get(i,F(0));value=old+q*v;change=abs(value)-abs(old)
                scores[r][0]+=change*weights[i][0];scores[r][1]+=change*weights[i][1];scores[r][2]+=change
                if value:rows[r][i]=value
                else:rows[r].pop(i,None)
        if j in sites:
            v=F(1) if injections is None else injections[j];rows[r][j]=v
            scores[r][0]+=abs(v)*weights[j][0];scores[r][1]+=abs(v)*weights[j][1];scores[r][2]+=abs(v)
        g=F(1) if scales is None else abs(scales[j])
        normalized=[v/g for v in scores[r]]
        stream.update((str(j)+':'+','.join(map(str,normalized))+';').encode())
        for k,v in enumerate(normalized):
            if v>peaks[k]['value']:
                peaks[k]=dict(value=v,cut=j+1,role=r);witness[k]={i:v/(F(1) if scales is None else scales[j]) for i,v in rows[r].items()}
    return dict(peaks=peaks,final_scores=scores,hashes=[hash_row(row) for row in rows],stream_sha256=stream.hexdigest()),witness


def transpose(word,weights,sites,injections=None):
    n=word['public']+word['owned_fields'];columns=[{i:F(1)} for i in range(n)];scores=[[F(0)]*3 for _ in range(n)];hashes=[sha256() for _ in range(n)]
    for j in reversed(range(len(word['program']))):
        e=word['program'][j];op,r=e[:2]
        if j in sites:
            g=F(1) if injections is None else injections[j]
            for i,raw in columns[r].items():
                v=g*raw;scores[i][0]+=abs(v)*weights[j][0];scores[i][1]+=abs(v)*weights[j][1];scores[i][2]+=abs(v)
                hashes[i].update(f'{j}:{v.numerator}/{v.denominator};'.encode())
        if op in ('INIT','CLEAR'):columns[r]={}
        elif op=='SCALE':columns[r]={i:F(e[-2])*v for i,v in columns[r].items()}
        elif op in ('ADD','COPY'):
            add(columns[e[2]],columns[r],F(e[-2]))
            if op=='COPY':columns[r]={}
    return scores,[h.hexdigest() for h in hashes]


def execute(word,initial,errors,cut):
    x=[F(0)]*(word['public']+word['owned_fields'])
    for r,v in initial.items():x[r]=F(v)
    for j,e in enumerate(word['program'][:cut]):
        op,r=e[:2]
        if op in ('INIT','CLEAR'):x[r]=F(0)
        elif op=='COPY':x[r]=F(e[-2])*x[e[2]]
        elif op=='ADD':x[r]+=F(e[-2])*x[e[2]]
        elif op=='SCALE':x[r]*=F(e[-2])
        x[r]+=errors.get(j,F(0))
    return x


def guards(data,public):
    J,K=[v['value'] for v in data['peaks'][:2]]
    prefix=next(g for g in range(150) if J+K<2**g)
    def valid(g):
        u=F(1,2**g)
        return u*K<1 and all(u*(a+b*u*J/(1-u*K))<1 for a,b,_ in data['final_scores'][:public])
    final=next(g for g in range(150) if valid(g));need(not valid(final-1),'previous final guard fails formula')
    return dict(prefix=prefix,final_public=final)
