# SPDX-License-Identifier: Apache-2.0
"""A2 graph change, jointly framed, with exact chronological invoices.
Chris R / Clear1nsight; substantial OpenAI Codex assistance.
PR3886 tracing/subspace representation is credited reuse, not independent code.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import hashlib,json,types,itertools
P=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok: raise ValueError(msg)

def module(name,path):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
R=module('retained_retiming',P/'vendor/retiming.py')

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def chain(g,h):
    return g[0]==h[0]=='add' and len(set(g[1:3]+h[1:3]))==3 and (g[1]==h[2] or g[2]==h[1])

def expand(g,h,position):
    require(chain(g,h),'not an A2 chain');require(position in (0,1,2),'central position')
    a,b=Q(g[3],g[4]),Q(h[3],h[4])
    # Chronological composition acts on column vectors on the left.
    if g[2]==h[1]: t,s,c=g[1],h[2],-a*b
    else: t,s,c=h[1],g[2],a*b
    central=['add',t,s,c.numerator,c.denominator,[]]
    out=[deepcopy(h),deepcopy(g)];out.insert(position,central);return out

def matrix(gates):
    regs=sorted({r for g in gates for r in g[1:3]});index={r:i for i,r in enumerate(regs)}
    rows=[[Q(i==j) for j in range(len(regs))] for i in range(len(regs))]
    for g in gates:
        require(g[0]=='add','matrix ADD domain');t,s=index[g[1]],index[g[2]]
        require(t!=s,'self ADD');a=Q(g[3],g[4]);rows[t]=[x+a*y for x,y in zip(rows[t],rows[s])]
    return regs,rows

@lru_cache(None)
def frames(low,high):
    if not R.contained(low,high):return ()
    require(R.rank(high)-R.rank(low)<=4,'frame quotient resource cap')
    seen={low};todo=[low]
    while todo:
        u=todo.pop()
        for v in range(1,512):
            if high>>v&1 and not u>>v&1:
                z=R.join(u,R.span((v,)))
                if z not in seen:seen.add(z);todo.append(z)
    return tuple(sorted(seen))

def boundary(nodes,where,word,section,index,length=2):
    gates=word[section][index:index+length];bounds={};old=Counter()
    for r in sorted({r for g in gates for r in R.touched(g)}):
        indices=[i for i in range(index,index+length) if r in R.touched(word[section][i])]
        seq=nodes[r];a=where[((section,indices[0]),r)];b=where[((section,indices[-1]),r)]
        require(seq[b+1][1]!='map','missing fixed warp-entry check')
        bounds[r]=(seq[a][2],seq[b+1][3])
        for k in range(a,b+2):old[R.rank(seq[k][3])-R.rank(seq[k][2])]+=1
    return bounds,old

def apply(word,section,index,gates,C,old_length=2):
    out=deepcopy(word);out[section][index:index+old_length]=deepcopy(gates)
    if section=='B':
        for rec in out['warps']:
            if rec[0]>=index+old_length:rec[0]+=len(gates)-old_length
    out['cleanup']=C.derive_cleanup(out)
    return out

def invoice(bounds,gates):
    cur={r:p for r,(p,q) in bounds.items()};bill=Counter()
    for g in gates:
        u=R.span(tuple(g[-1]))
        for r in R.touched(g):
            require(R.contained(cur[r],u) and R.contained(u,bounds[r][1]),'illegal frame')
            bill[R.rank(u)-R.rank(cur[r])]+=1;cur[r]=u
    for r,(p,q) in bounds.items():bill[R.rank(q)-R.rank(cur[r])]+=1
    return bill

def enumerate_flags(bounds,gates,intervals):
    def visit(t,cur,chosen):
        if t==len(gates):yield chosen;return
        a,b=gates[t][1:3];low=R.join(cur[a],cur[b]);high=bounds[a][1]&bounds[b][1]
        intervals.add((low,high))
        for u in frames(low,high):
            nextcur=cur.copy();nextcur[a]=nextcur[b]=u
            yield from visit(t+1,nextcur,chosen+[u])
    yield from visit(0,{r:p for r,(p,q) in bounds.items()},[])

def relaxed(bounds,gates,old):
    count=optimistic=0
    for dims in itertools.product(range(10),repeat=3):
        cur={r:R.rank(p) for r,(p,q) in bounds.items()};bill=Counter();ok=True
        for g,d in zip(gates,dims):
            for r in R.touched(g):
                if not cur[r]<=d<=R.rank(bounds[r][1]):ok=False;break
                bill[d-cur[r]]+=1;cur[r]=d
            if not ok:break
        if ok:
            for r,(p,q) in bounds.items():bill[R.rank(q)-cur[r]]+=1
            delta=[0]+[bill[r]-old[r] for r in range(1,10)];count+=1
            optimistic+=not R.all_power_nonnegative(delta)
    return count,optimistic

def inverse_sites(word):
    found=[]
    for section in ('A','B','restore'):
        for lo,hi in R.segments(word,section):
            for i in range(lo,hi-2):
                block=word[section][i:i+3]
                if not all(g[0]=='add' for g in block):continue
                for pos in (0,1,2):
                    remaining=[g for j,g in enumerate(block) if j!=pos]
                    g,h=remaining[::-1]
                    if chain(g,h):
                        expected=expand(g,h,pos)
                        if all(a[:3]==b[:3] and Q(a[3],a[4])==Q(b[3],b[4]) for a,b in zip(block,expected)):
                            found.append([section,i,pos])
    return found

def compute(word,C):
    nodes,where,baseline=R.tracing(word);hist=Counter();records=[];intervals=set();motifs=[];inverse=[]
    rejected=[];optimistic=Counter();matrix_count=0;inverse=inverse_sites(word)
    for section in ('A','B','restore'):
        for lo,hi in R.segments(word,section):
            for i in range(lo,hi-1):
                g,h=word[section][i:i+2]
                if not chain(g,h):continue
                bounds,old=boundary(nodes,where,word,section,i);motifs.append([section,i])
                for pos in (0,1,2):
                    new=expand(g,h,pos);require(matrix([g,h])==matrix(new),'A2 matrix identity');matrix_count+=1
                    rc,ro=relaxed(bounds,new,old);optimistic['dimension_triples']+=rc;optimistic['uncertified_triples']+=ro
                    for flag in enumerate_flags(bounds,new,intervals):
                        gates=deepcopy(new)
                        for gate,u in zip(gates,flag):gate[-1]=list(R.basis(u))
                        local=invoice(bounds,gates);delta=tuple([0]+[local[r]-old[r] for r in range(1,10)])
                        require(R.all_power_nonnegative(delta),'uncertified exact signed profile')
                        moved=apply(word,section,i,gates,C)
                        try: bill,widths,*_=C.frame_bill(moved)
                        except C.AuditFailure as e:
                            rejected.append([section,i,pos,[list(R.basis(u)) for u in flag],str(e)]);continue
                        C.hygiene(moved)
                        require(all(bill.get(r,0)-baseline.get(r,0)==delta[r] for r in range(1,10)),'whole invoice mismatch')
                        require(matrix([g,h])==matrix(gates),'dirty frame assignment')
                        # The inverse cleanup projected to non-target registers is checked
                        # separately: target reads cannot feed non-targets under hygiene.
                        projected_before=[x for x in [g,h] if not C.is_target(x[1])]
                        projected_after=[x for x in gates if not C.is_target(x[1])]
                        regs=sorted({r for x in [g,h]+gates for r in x[1:3]})
                        require(embedded_matrix(projected_before,regs)==embedded_matrix(projected_after,regs),'projected cleanup matrix')
                        hist[delta]+=1
                        records.append({'section':section,'index':i,'central_position':pos,'gates':gates,'delta':list(delta),'cleanup_length':len(moved['cleanup']),
                                        'profile':bill,'central_scalar':[new[pos][3],new[pos][4]]})
    return {'motifs':motifs,'matrix_identity_checks':matrix_count,'inverse_contractions':inverse,
            'optimistic_dimension_relaxation':dict(optimistic),'compatible_flags':sum(hist.values())+len(rejected),'legal_flags':len(records),
            'fixed_boundary_rejections':rejected,'profiles':[{'delta':list(d),'count':n} for d,n in sorted(hist.items())],
            'intervals':[[str(l),str(h)] for l,h in sorted(intervals)],'records':records,
            'contractions':contract(word,C,inverse,nodes,where,baseline)}

def embedded_matrix(gates,regs):
    rows={r:{s:Q(r==s) for s in regs} for r in regs}
    for g in gates:
        t,s=g[1:3];a=Q(g[3],g[4]);rows[t]={r:rows[t][r]+a*rows[s][r] for r in regs}
    return rows


def contract(word,C,inverse,nodes,where,baseline):
    rows=[];intervals=set()
    for section,i,pos in inverse:
        block=word[section][i:i+3]
        remainder=[g for j,g in enumerate(block) if j!=pos]
        gates=[deepcopy(remainder[1]),deepcopy(remainder[0])]
        require(matrix(block)==matrix(gates),'inverse A2 matrix')
        bounds,old=boundary(nodes,where,word,section,i,3)
        for flag in enumerate_flags(bounds,gates,intervals):
            candidate=deepcopy(gates)
            for g,u in zip(candidate,flag):g[-1]=list(R.basis(u))
            bill=invoice(bounds,candidate);delta=tuple([0]+[bill[r]-old[r] for r in range(1,10)])
            require(R.all_power_nonnegative(delta),'profitable inverse contraction: retain witness')
            moved=apply(word,section,i,candidate,C,3)
            profile,widths,*_=C.frame_bill(moved);C.hygiene(moved)
            require(all(profile.get(r,0)-baseline.get(r,0)==delta[r] for r in range(1,10)),'inverse invoice')
            regs=sorted({r for g in block for r in g[1:3]})
            require(embedded_matrix([g for g in block if not C.is_target(g[1])],regs)==embedded_matrix([g for g in candidate if not C.is_target(g[1])],regs),'inverse projected cleanup')
            rows.append({'section':section,'index':i,'central_position':pos,'gates':candidate,'delta':list(delta),'profile':profile,'cleanup_length':len(moved['cleanup']),'canonical_word_sha256':digest(moved),
                         'cleanup_sha256':digest(moved['cleanup']),'post_contraction_inverse_sites':inverse_sites(moved)})
    return {'records':rows,'intervals':[[str(l),str(h)] for l,h in sorted(intervals)]}
