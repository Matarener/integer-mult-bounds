#!/usr/bin/env python3
"""Independent exact finite corroboration; no predecessor executable imports.
JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
"""
from itertools import product, combinations_with_replacement
import json
import random


def need(x, why):
    if not x:
        raise ValueError(why)


def bits(x):
    while x:
        t = x & -x
        yield t.bit_length()-1
        x ^= t


def rank(cols):
    pivots = {}
    for x in cols:
        while x:
            k = x.bit_length()-1
            if k not in pivots:
                pivots[k] = x
                break
            x ^= pivots[k]
    return len(pivots)


def lin(cols, x):
    y = 0
    for i in bits(x):
        y ^= cols[i]
    return y


def matmul(a, b, m, modulus=2):
    return tuple(sum(a[r*m+k]*b[k*m+c] for k in range(m)) % modulus
                 for r in range(m) for c in range(m))


def eye(m):
    return tuple(int(r == c) for r in range(m) for c in range(m))


def unit(d, k):
    return tuple(int(i == k) for i in range(d))


def inv(a, m):
    rows = [list(a[r*m:(r+1)*m])+list(eye(m)[r*m:(r+1)*m]) for r in range(m)]
    for c in range(m):
        p = next((r for r in range(c, m) if rows[r][c] % 2), None)
        need(p is not None, 'invertible mod4')
        rows[c], rows[p] = rows[p], rows[c]
        v = pow(rows[c][c], -1, 4)
        rows[c] = [v*x % 4 for x in rows[c]]
        for r in range(m):
            if r != c:
                v = rows[r][c]
                rows[r] = [(x-v*y) % 4 for x,y in zip(rows[r], rows[c])]
    return tuple(x for row in rows for x in row[m:])


def transform(pair, a, m, modulus=4):
    return matmul(matmul(pair[0], a, m, modulus), pair[1], m, modulus)


def maps(m):
    gl = [a for a in product(range(2), repeat=m*m)
          if rank([sum(a[r*m+c]<<r for r in range(m)) for c in range(m)]) == m]
    out = set()
    for l,r in product(gl, repeat=2):
        out.add(tuple(sum(v<<i for i,v in enumerate(transform((l,r),unit(m*m,k),m,2)))
                      for k in range(m*m)))
    return sorted(out)


def monomials(d):
    return [()] + [(i,) for i in range(d)] + list(combinations_with_replacement(range(d),2))


def quadratic(a, b, d):
    pairs = {p:i for i,p in enumerate(combinations_with_replacement(range(d),2))}
    y = 0
    for i in bits(a):
        for j in bits(b):
            y ^= 1 << pairs[tuple(sorted((i,j)))]
    return y


def relation(a, u, d):
    if a[0]^a[1]^a[2]:
        return False
    for k in range(d):
        if quadratic(a[0],u[0][k],d)^quadratic(a[1],u[1][k],d)^quadratic(a[2],u[2][k],d):
            return False
    return True


def toggle(s, x):
    if x in s:
        s.remove(x)
    else:
        s.add(x)


def project_group(s, d):
    """Expand independent binomial products [a]=prod(1+t_i)^a_i, degrees<=2."""
    mons = monomials(d)
    index = {p:i for i,p in enumerate(mons)}
    result = 0
    for address in s:
        result ^= 1
        for i,a in enumerate(address):
            if a & 1:
                result ^= 1 << index[(i,)]
            if a & 2:
                result ^= 1 << index[(i,i)]
        for i in range(d):
            for j in range(i+1,d):
                if address[i]&address[j]&1:
                    result ^= 1 << index[(i,j)]
    return result


def call(state, spec, m):
    """Actual sparse F2[(Z/4)^(m*m)] operator; never truncates during the word."""
    x,y,a,t = spec
    out = [set(s) for s in state]
    for r in range(3):
        if not x[r]:
            continue
        ar = transform(t[r], a, m)
        for s in range(3):
            if not y[s]:
                continue
            inverse_pair = (inv(t[s][0],m), inv(t[s][1],m))
            for h in state[s]:
                g = transform(t[r],transform(inverse_pair,h,m),m)
                toggle(out[r],g)
                toggle(out[r],tuple((v+w)%4 for v,w in zip(g,ar)))
    return out


def first(specs, m):
    d=m*m
    result=[[0]*3 for _ in range(3)]
    for x,y,a,t in specs:
        for r in range(3):
            ar=sum((v%2)<<i for i,v in enumerate(transform(t[r],a,m)))
            for s in range(3):
                if x[r] and y[s]:result[r][s]^=ar
    return result


def dirty_formula(specs, m, source, k):
    d=m*m
    out=[0]*3
    out[source] = 1 << (1+k)
    for x,y,a,t in specs:
        if not y[source]:continue
        inverse_pair=(inv(t[source][0],m),inv(t[source][1],m))
        for r in range(3):
            if not x[r]:continue
            ar=sum((v%2)<<i for i,v in enumerate(transform(t[r],a,m)))
            z=transform(t[r],transform(inverse_pair,unit(d,k),m),m)
            zr=sum((v%2)<<i for i,v in enumerate(z))
            out[r]^=quadratic(ar,zr,d) << (1+d)
    return out


def witness():
    m=3;d=9;ident=eye(m);standard=[(ident,ident)]*3;ones=(1,1,1)
    specs=[(ones,ones,unit(d,0),standard),(ones,ones,unit(d,1),standard)]
    left=list(ident);left[3]=1
    swap=(0,1,0,1,0,0,0,0,1)
    right=list(ident);right[1]=1
    for s in range(3):
        twists=[(ident,tuple(right))]*3;twists[s]=(tuple(left),swap)
        specs.append((ones,unit(3,s),unit(d,0),twists))
    for s in range(3):specs.append((unit(3,s),unit(3,s),unit(d,8),standard))
    return specs


def main():
    us=maps(2);ident=(1,2,4,8)
    need(len(us)==36,'GL2 two-sided maps')
    distances={}
    for u,v in product(us,repeat=2):
        r=rank([a^b for a,b in zip(u,v)])
        distances[r]=distances.get(r,0)+1
        need(u==v or r>=2,'rank distance')
    # Normalize U3 to identity by changing the input z. The class is a group.
    solutions=checks=0
    for a,b in product(range(1,16),repeat=2):
        if a==b:continue
        forms=(a,b,a^b)
        for u,v in product(us,repeat=2):
            checks+=1
            if relation(forms,(u,v,ident),4):
                solutions+=1
                need(u==v==ident,'three-term rigidity')
    need(solutions==210,'all and only common transports')
    zero_cases=0
    for a in range(1,16):
        for u in us:
            for zero_slot in range(3):
                forms=[a,a,a];transports=[u,ident,ident]
                forms[zero_slot]=0
                active=[i for i in range(3) if i!=zero_slot]
                transports[active[0]]=u;transports[active[1]]=ident
                need(relation(forms,transports,4)==(u==ident), 'two active terms')
                zero_cases+=1
    need(relation((0,0,0),(us[0],us[1],us[2]),4), 'all zero reductions')
    # The rank-distance hypothesis is essential: arbitrary GL(V) admits rank1 gaps.
    u=list(ident);u[2]^=2
    v=list(ident);v[2]^=1
    need(rank(u)==rank(v)==4 and relation((1,2,3),(u,v,ident),4), 'general GL counterexample')
    need(tuple(u)!=ident and rank([a^b for a,b in zip(u,ident)])==1,'rank1 escape')
    specs=witness();expected=[[0]*3 for _ in range(3)]
    for s in range(3):expected[s][s]=273 # E00+E11+E22
    need(first(specs,3)==expected,'eight nonzero calls pass first order')
    rng=random.Random(19173175);orders=[list(range(8)),list(reversed(range(8)))]
    for _ in range(10):
        order=list(range(8));rng.shuffle(order);orders.append(order)
    oracle_cases=0;obstructions=0
    for order in orders:
        for source,k in [(0,0),(1,1),(2,3)]:
            state=[set(),set(),set()];state[source]={unit(9,k),(0,)*9}
            for j in order:state=call(state,specs[j],3)
            got=[project_group(s,9) for s in state]
            need(got==dirty_formula(specs,3,source,k),'sparse group vs independent dirty jet')
            need(any(got[r] for r in range(3) if r!=source),'dirty obstruction')
            obstructions+=1;oracle_cases+=1
    # Direct nine-call positive control, full sparse operator on independent dirty inputs.
    standard=[(eye(3),eye(3))]*3
    direct=[(unit(3,s),unit(3,s),unit(9,4*k),standard) for s in range(3) for k in range(3)]
    for source in range(3):
        state=[set(),set(),set()];state[source]={unit(9,1),(0,)*9}
        for spec in direct:state=call(state,spec,3)
        target=tuple(eye(3));expected_state=[set(),set(),set()]
        expected_state[source]={target,tuple((a+b)%4 for a,b in zip(target,unit(9,1)))}
        need(state==expected_state,'nine-call exact positive');oracle_cases+=1
    # Squaring cannot be discarded; [2E]-1 projects to t_E^2.
    square=project_group({(2,)+(0,)*8,(0,)*9},9)
    need(square==1 << monomials(9).index((0,0)),'squares retained')
    # Explicit falsification controls do not use assert (optimization safe).
    controls=0
    for good,why in [(solutions==211,'wrong solution count'),
                     (first(specs,3)!=expected,'wrong first order'),
                     (square==0,'square-free quotient'),
                     (all(r>=3 for r in distances if r),'false rank3 floor')]:
        try:need(good,why)
        except ValueError:controls+=1
        else:raise ValueError('control did not reject: '+why)
    need(controls==4,'controls complete')
    return {'status':'PASS_THREE_TERM_TWIST_RIGIDITY','two_sided_maps_m2':36,
            'rank_distance_histogram':distances,'normalized_three_term_cases':checks,
            'normalized_solutions':solutions,'zero_reduction_cases':zero_cases+1,'full_sparse_oracle_cases':oracle_cases,
            'first_order_feasible_eight_call_obstructions':obstructions,
            'orders_sampled':len(orders),'rejection_controls':controls,
            'arbitrary_GL_counterexample':True,'quantified_result':'written proof; finite checks corroborate',
            'new_kappa':False}

if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
