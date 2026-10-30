"""Forward causal defect budgets with exact upward dyadic rounding.

The signed coefficient rows remain exact. Only the upper bounds on defect
magnitudes are rounded, always upwards. No stability denominator is assumed.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F


def need(ok,message):
    if not ok:raise ValueError(message)


def ceil_fraction(v):return -(-v.numerator//v.denominator)


def setup(word):
    count=word['public']+word['owned_fields'];degrees=[0]*count;E=0;ops=[]
    for e in word['program']:
        op,r=e[:2];q=F(e[-2]) if op in ('ADD','COPY','SCALE') else F(1)
        need(q.denominator & (q.denominator-1)==0,'dyadic coefficient')
        k=q.denominator.bit_length()-1;s=e[2] if op in ('ADD','COPY') else None
        if op in ('INIT','CLEAR'):degrees[r]=0
        elif op=='SCALE':degrees[r]+=k
        elif op=='COPY':degrees[r]=degrees[s]+k
        elif op=='ADD':degrees[r]=max(degrees[r],degrees[s]+k)
        E=max(E,degrees[r]);ops.append((op,r,q,s))
    return count,1<<E,ops


def scaled(v,q):
    z=v*q.numerator;need(z%q.denominator==0,'exact coefficient division');return z//q.denominator


def bound(word,weights,sites,guard,grid_bits=96):
    n,S,ops=setup(word);Z=1<<grid_bits;u=F(1,1<<guard)
    rows=[{} for _ in range(n)];scores=[0]*n;deltas={};peak=0;peak_at=None
    for j,(op,r,q,s) in enumerate(ops):
        if j in sites:
            feedback=F(scores[r])
            if op=='ADD':feedback+=abs(q)*scores[s]
            elif op=='SCALE':feedback*=abs(q)
            else:need(op=='MOVE','declared relative defect site')
            exact=u*(weights[j][0]*Z+feedback/S)
            delta=ceil_fraction(exact)
            need(F(delta)>=exact and F(delta)-exact<1,'directed rounding')
        else:delta=0
        if op in ('INIT','CLEAR'):rows[r]={};scores[r]=0
        elif op=='COPY':rows[r]={i:scaled(v,q) for i,v in rows[s].items()};scores[r]=scaled(scores[s],abs(q))
        elif op=='SCALE':rows[r]={i:scaled(v,q) for i,v in rows[r].items()};scores[r]=scaled(scores[r],abs(q))
        elif op=='ADD':
            for i,v in rows[s].items():
                old=rows[r].get(i,0);value=old+scaled(v,q);scores[r]+=(abs(value)-abs(old))*deltas[i]
                if value:rows[r][i]=value
                else:rows[r].pop(i,None)
        if j in sites:rows[r][j]=S;deltas[j]=delta;scores[r]+=S*delta
        if scores[r]>peak:peak=scores[r];peak_at=[j+1,r]
    return dict(guard=guard,grid_bits=grid_bits,coefficient_scale_bits=S.bit_length()-1,
                peak=F(peak,S*Z),peak_at=peak_at,final=[F(v,S*Z) for v in scores],sites=len(deltas))


def rational_oracle(word,weights,sites,guard):
    # Independent small-domain oracle: direct rational substitution, with no
    # incremental score or fixed-scale coefficient representation.
    n=word['public']+word['owned_fields'];rows=[{} for _ in range(n)];delta={};u=F(1,1<<guard)
    def norm(row):return sum((abs(v)*delta[i] for i,v in row.items()),F(0))
    for j,e in enumerate(word['program']):
        op,r=e[:2];q=F(e[-2]) if op in ('ADD','COPY','SCALE') else F(1)
        if j in sites:
            feedback=norm(rows[r])
            if op=='ADD':feedback+=abs(q)*norm(rows[e[2]])
            elif op=='SCALE':feedback*=abs(q)
            delta[j]=u*(weights[j][0]+feedback)
        if op in ('INIT','CLEAR'):rows[r]={}
        elif op=='COPY':rows[r]={i:q*v for i,v in rows[e[2]].items()}
        elif op=='SCALE':rows[r]={i:q*v for i,v in rows[r].items()}
        elif op=='ADD':
            for i,v in rows[e[2]].items():
                value=rows[r].get(i,F(0))+q*v
                if value:rows[r][i]=value
                else:rows[r].pop(i,None)
        if j in sites:rows[r][j]=F(1)
    return [norm(row) for row in rows]
