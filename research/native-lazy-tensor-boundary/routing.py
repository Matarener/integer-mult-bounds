"""Uniform tensor routing. JoyboyBrian, OpenAI Codex assistance; Apache-2.0."""
from math import lcm


def need(ok, why):
    if not ok: raise ValueError(why)


def decode(rec):
    rows, q, a = rec['matrix_rows'], rec['quadratic_rows'], rec['linear_Z4']
    n=len(rows); out=[]; phases=[]
    for x in range(1<<n):
        out.append(rec['offset'] ^ sum(((x&r).bit_count()%2)<<i for i,r in enumerate(rows)))
        phases.append((rec['phase']+sum(a[i] for i in range(n) if x>>i&1)+
            2*sum((q[i]>>j)&1 for i in range(n) for j in range(i+1,n) if x>>i&1 and x>>j&1))%4)
    need(sorted(out)==list(range(1<<n)), 'source bijection')
    return tuple(out),tuple(phases)


def compose(a,b):
    p,q=a; r,s=b
    return tuple(p[x] for x in r),tuple((s[i]+q[r[i]])%4 for i in range(len(r)))


def order(p):
    seen=set(); lengths=[]
    for x in range(len(p)):
        if x in seen: continue
        y=x; length=0
        while y not in seen: seen.add(y); y=p[y]; length+=1
        need(y==x,'permutation orbit'); lengths.append(length)
    return lcm(*lengths)


def tables(m):
    p,q=m; cur=list(range(len(p))); out=[]
    for k in range(order(p)):
        out.append(tuple((x,q[x]) for x in cur))
        cur=[p[x] for x in cur]
    return out


def odometer(lanes,f,bits,bill):
    """Yield packed lane values and phase sums; working lists reused after yield."""
    need(type(f) is int and f>=1 and bits>=1,'positive width')
    base=1<<bits; mask=base-1; N=1<<(bits*f); d=len(lanes)
    need(d>0 and all(len(t)==base for t in lanes),'table dimensions')
    digits=[0]*f; positions=[0]*d; phases=[0]*d
    for k,t in enumerate(lanes):
        for j in range(f):
            positions[k] |= t[0][0]<<(bits*j); phases[k]=(phases[k]+t[0][1])&3
            bill['initial_lane_digits']=bill.get('initial_lane_digits',0)+1
    for x in range(N):
        yield x,positions,phases
        if x==N-1: break
        j=0
        while True:
            old=digits[j]; new=(old+1)&mask; digits[j]=new
            for k,t in enumerate(lanes):
                u,a=t[old]; v,b=t[new]
                positions[k] ^= (u^v)<<(bits*j)
                phases[k]=(phases[k]-a+b)&3
                bill['lane_digit_updates']=bill.get('lane_digit_updates',0)+1
            bill['digit_increments']=bill.get('digit_increments',0)+1
            if new: break
            j+=1


def rotate(z,q):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[q]


def cycle_apply(v,m,f,bits,bill,targets=None):
    lanes=tables(m); d=len(lanes)
    for x,pos,phase in odometer(lanes,f,bits,bill):
        bill['leader_comparisons']=bill.get('leader_comparisons',0)+d-1
        if min(pos)!=x: continue
        length=next((j for j in range(1,d) if pos[j]==x),d)
        if targets is None and length==1 and phase[0]==0: continue
        saved=v[x]
        for k in range(length):
            y=pos[(k+1)%length]; following=v[y] if k+1<length else None
            z=rotate(saved,phase[k]); v[y]=z
            bill['complex_stores']=bill.get('complex_stores',0)+1
            if targets is not None:
                for target,sign in zip(targets,(-1,-1,1)):
                    a,b=target[y]; target[y]=(a+sign*z[0],b+sign*z[1])
            saved=following


def consumers(v,targets,m,f,bits,bill):
    lane=[tuple(zip(*m))]
    for x,pos,phase in odometer(lane,f,bits,bill):
        y=pos[0]; z=rotate(v[x],phase[0])
        for target,sign in zip(targets,(-1,-1,1)):
            a,b=target[y]; target[y]=(a+sign*z[0],b+sign*z[1])


def boundary(arrays,M,R,f,bits,lazy):
    v,*targets=[list(x) for x in arrays]; bill={}
    if lazy:
        consumers(v,targets,M,f,bits,bill)
        cycle_apply(v,compose(R,M),f,bits,bill)
    else:
        cycle_apply(v,M,f,bits,bill,targets)
        cycle_apply(v,R,f,bits,bill)
    return [v,*targets],bill


def invoice(f):
    need(type(f) is int and f>=1,'positive width')
    N=512**f; U=sum((N-1)//512**j for j in range(f))
    return dict(width=f,N=N,digit_increments_per_scan=U,
        materialized_route_lanes=36,lazy_route_lanes=29,
        materialized_initial_lane_digits=36*f,lazy_initial_lane_digits=29*f,
        materialized_lane_digit_updates=36*U,lazy_lane_digit_updates=29*U,
        materialized_leader_comparisons=34*N,lazy_leader_comparisons=27*N,
        materialized_source_real_reads=4*N,lazy_source_real_reads=4*N,
        materialized_source_real_writes=4*N,lazy_source_real_writes=2*N,
        common_consumer_real_reads=6*N,common_consumer_real_writes=6*N,
        common_consumer_adds=6*N,common_consumer_negations=2*N,
        common_second_pass_negations=N,
        setup_orbit_table_entries_materialized=36*512,setup_orbit_table_entries_lazy=29*512,
        extra_composition_table_reads=1024,extra_composition_table_writes=512,
        extra_composition_phase_adds=512)
