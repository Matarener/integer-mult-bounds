"""Exact finite Gaussian-array circuits and explicit operational ledger.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
This is a declared f=1 RAM microcontract, not the supplier's missing tariff.
"""
from collections import Counter

N=512

def need(ok,message):
    if not ok:raise ValueError(message)

def cycles(p):
    need(sorted(p)==list(range(N)),'permutation domain')
    seen=set();out=[]
    for start in range(N):
        if start in seen:continue
        row=[];x=start
        while x not in seen:seen.add(x);row.append(x);x=p[x]
        need(x==start,'closed permutation cycle');out.append(row)
    return out

def compose(a,b):
    """Apply b then a; phases are attached to input columns."""
    ap,aq=a;bp,bq=b
    return tuple(ap[x]for x in bp),tuple((bq[x]+aq[bp[x]])%4 for x in range(N))

def inverse(m):
    p,q=m;back=[0]*N;phase=[0]*N
    for x,y in enumerate(p):back[y]=x;phase[y]=-q[x]%4
    return tuple(back),tuple(phase)

def neg(x,bill):bill['real_negations']+=1;return -x
def add(x,y,bill):bill['real_additions']+=1;return x+y
def sub(x,y,bill):return add(x,neg(y,bill),bill)

def rotate(z,q,bill):
    a,b=z
    if q==0:return a,b
    if q==1:return neg(b,bill),a
    if q==2:return neg(a,bill),neg(b,bill)
    return b,neg(a,bill)

def load(v,i,bill):bill['caller_real_reads']+=2;return v[i]
def store(v,i,z,bill):bill['caller_real_writes']+=2;v[i]=z

def monomial(v,m,bill):
    """One in-place cycle pass; identity fixed points do not touch data."""
    p,q=m
    for cyc in cycles(p):
        bill['cycle_leader_reads']+=1
        bill['routing_entry_reads']+=len(cyc)
        if len(cyc)==1 and q[cyc[0]]==0:continue
        saved=load(v,cyc[0],bill)
        for x in cyc:
            y=p[x];following=load(v,y,bill)if y!=cyc[0]else None
            store(v,y,rotate(saved,q[x],bill),bill);saved=following

def consumers(v,targets,m,bill,undo=False):
    """Three adjacent distinct consumers share each source load.

    Both signs of each real source component are prepared once. The phase
    chooses already prepared operands; it is not an uncharged Pauli pass.
    """
    if m is None:p=tuple(range(N));q=(0,)*N
    else:p,q=m;bill['routing_entry_reads']+=N
    coeffs=(2,2,0)if not undo else(0,0,2)
    for x in range(N):
        a,b=load(v,x,bill);na,nb=neg(a,bill),neg(b,bill)
        choices=((a,b),(nb,a),(na,nb),(b,na))
        for target,sign in zip(targets,coeffs):
            u,w=choices[(q[x]+sign)%4];c,d=load(target,p[x],bill)
            store(target,p[x],(add(c,u,bill),add(d,w,bill)),bill)

def materialized_consumers(v,targets,m,bill):
    """Stronger baseline: consume each saved value during M's cycle pass.

    Reuse both prepared signs for M's own store as well as all consumers.
    This fairly removes the naive baseline's extra source load and M NEG.
    """
    p,q=m
    for cyc in cycles(p):
        bill['cycle_leader_reads']+=1;bill['routing_entry_reads']+=len(cyc)
        saved=load(v,cyc[0],bill)
        for x in cyc:
            y=p[x];following=load(v,y,bill)if y!=cyc[0]else None
            a,b=saved;na,nb=neg(a,bill),neg(b,bill)
            choices=((a,b),(nb,a),(na,nb),(b,na))
            store(v,y,choices[q[x]],bill)
            for target,sign in zip(targets,(2,2,0)):
                u,w=choices[(q[x]+sign)%4];c,d=load(target,y,bill)
                store(target,y,(add(c,u,bill),add(d,w,bill)),bill)
            saved=following

def child(v,bill,adjoint=False):
    """C_0 or C_0 adjoint. Returned integer numerators have denominator2.

    This finite f=1 butterfly does not replace a general-f recursive child.
    """
    for x in range(0,N,2):
        a,b=load(v,x,bill);c,d=load(v,x+1,bill)
        sr,si=add(a,c,bill),add(b,d,bill)
        dr,di=sub(a,c,bill),sub(b,d,bill)
        if not adjoint:
            left=(sub(sr,di,bill),add(si,dr,bill))
            right=(add(sr,di,bill),sub(si,dr,bill))
        else:
            left=(add(sr,di,bill),sub(si,dr,bill))
            right=(sub(sr,di,bill),add(si,dr,bill))
        store(v,x,left,bill);store(v,x+1,right,bill)
        bill['exact_halves']+=4

def execute(arrays,M,R,L,fused=False,undo=False,joint=False):
    """Four arbitrary complex arrays; no array starts clean or is discarded.

    Forward returns denominator exponents(1,0,0,0). Inverse expects those
    exponents and returns all four arrays with denominator4.
    """
    v,*targets=[list(z)for z in arrays];bill=Counter()
    bill['private_real_words']=8;bill['private_word_clears']=16
    if undo:
        monomial(v,inverse(L),bill);child(v,bill,True)
        # The second exact half leaves source denominator4. Align destinations.
        targets=[[(a*4,b*4)for a,b in z]for z in targets]
        if fused:
            monomial(v,inverse(compose(R,M)),bill)
            consumers(v,targets,M,bill,True)
        else:
            monomial(v,inverse(R),bill);consumers(v,targets,None,bill,True)
            monomial(v,inverse(M),bill)
        return [v,*targets],2,dict(bill)
    if joint:materialized_consumers(v,targets,M,bill)
    else:
        if not fused:monomial(v,M,bill)
        consumers(v,targets,M if fused else None,bill)
    monomial(v,compose(R,M)if fused else R,bill)
    child(v,bill);monomial(v,L,bill)
    return [v,*targets],1,dict(bill)

def metadata(M,R,L):
    F=compose(R,M)
    # Three 512-entry tables retain all 9-bit destinations and 2-bit phases.
    # The fused route retains M for its consumers; it cannot delete its tags.
    return dict(route_table_bits=3*N*11,
                reference_cycle_leader_bits=9*sum(len(cycles(m[0]))for m in (M,R,L)),
                fused_cycle_leader_bits=9*sum(len(cycles(m[0]))for m in (F,L)),
                additional_fusion_preparation=dict(table_entry_reads=2*N,
                    table_entry_writes=N,table_entry_bits=11,
                    two_bit_mod4_additions=N,cycle_decomposition_work='One new 512-point permutation; cycle metadata is rebound, not free.',
                    temporary_composition_table_bits=N*11,visited_bits=N))
