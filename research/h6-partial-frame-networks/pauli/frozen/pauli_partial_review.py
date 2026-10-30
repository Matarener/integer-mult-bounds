#!/usr/bin/env python3
"""Independent partial-Pauli geometry, dirty word and complete-cost review.

No complex-alternative producer is imported. Binary frame identities are
checked in intrinsic unimodular E8 pairing coordinates; the fixed canonical
17-bit fit is an isometry of this bilinear space. No physical adapters are
executed or declared free. Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
SCALE = 10**35


def need(ok,message):
    if not ok:
        raise ValueError(message)


def xor_all(values):
    out = 0
    for value in values:
        out ^= value
    return out


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length()-1
        value ^= low


def basis(rows):
    out = {}
    for row in rows:
        for j in sorted(out,reverse=True):
            if row >> j & 1:
                row ^= out[j]
        if row:
            j = row.bit_length()-1
            for k in list(out):
                if out[k] >> j & 1:
                    out[k] ^= row
            out[j] = row
    return tuple(out[j] for j in sorted(out,reverse=True))


def included(a,b):
    return len(basis(a+b)) == len(b)


def inverse(rows):
    n = len(rows)
    rows = [row | (1 << (n+j)) for j,row in enumerate(rows)]
    for j in range(n):
        p = next(p for p in range(j,n) if rows[p] >> j & 1)
        rows[p],rows[j] = rows[j],rows[p]
        for p in range(n):
            if p != j and rows[p] >> j & 1:
                rows[p] ^= rows[j]
    return [row >> n for row in rows]


def nullspace(rows,n=17):
    rows = list(rows)
    pivots,k = [],0
    for j in range(n):
        p = next((p for p in range(k,len(rows)) if rows[p] >> j & 1),None)
        if p is None:
            continue
        rows[k],rows[p] = rows[p],rows[k]
        for p in range(len(rows)):
            if p != k and rows[p] >> j & 1:
                rows[p] ^= rows[k]
        pivots.append(j)
        k += 1
    return basis((1 << f) | sum(((rows[i] >> f)&1) << p for i,p in enumerate(pivots))
                 for f in range(n) if f not in pivots)


def roots():
    all_roots = []
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            row = [0]*8
            row[i],row[j] = a,b
            all_roots.append(tuple(row))
    all_roots += [r for r in product((-1,1),repeat=8) if sum(r)%4 == 0]
    return sorted({r if next(x for x in r if x) > 0 else tuple(-x for x in r) for r in all_roots})


def dot(a,b):
    raw = sum(x*y for x,y in zip(a,b))
    need(raw%4 == 0,'actual integral E8 root pairing')
    return raw//4


def geometry():
    rr = roots()
    gram = [sum((dot(a,b)&1) << j for j,b in enumerate(rr)) for a in rr]
    chosen,span = [],()
    for i,row in enumerate(gram):
        grown = basis(span+(row,))
        if len(grown) > len(span):
            chosen.append(i)
            span = grown
    need(len(chosen) == 8,'E8 pairing rank8')
    small = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(chosen)) for i in chosen]
    b = inverse(small)
    coords = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(chosen)) for i in range(120)]
    def pairing8(x,y):
        return (xor_all(b[j] for j in bits(x)) & y).bit_count()&1
    need(all(pairing8(coords[i],coords[j]) == (gram[i] >> j)&1 for i in range(120) for j in range(120)),
         'all14400 intrinsic/actual root pairing bindings')
    form = tuple(b+[row << 8 for row in b]+[1 << 16])
    def pairing(x,y):
        return (xor_all(form[j] for j in bits(x)) & y).bit_count()&1
    def orthogonal(frame):
        return nullspace([xor_all(form[j] for j in bits(row)) for row in frame])
    q = [sum((-1 if j&1 else 1)*x*x for j,x in enumerate(r)) for r in rr]
    selected = [j for j,value in enumerate(q) if value]
    need(len(selected) == 24 and {q[j] for j in selected} == {-8,8},'Pauli24-line support')
    ports = []
    for i in range(120):
        for j in selected:
            for sign in (-1,1):
                p = coords[i] | (coords[j] << 8) | (1 << 16)
                ports.append((i,j,sign,p,tuple(x*q[j] for x in rr[i])))
    need(len(ports) == 5760,'physical signed support size')
    u = basis(p[3] for p in ports)
    w = orthogonal(u)
    need(len(u) == 15 and len(w) == 2 and included(w,u),'coisotropic U15 with radical2')
    need(all(included((p[3],),u) and pairing(p[3],p[3]) == 1
             and all(not pairing(p[3],r) for r in w) for p in ports),'all supported source lines and target caps')
    for c in range(8):
        need(Counter(abs(p[4][c]) for p in ports if p[4][c]) == {8:3072,16:672},'complete feature incidence census')
    # An independent actual fixture contains a rank15 frame witness plus
    # coordinate-root witnesses and two actual zero-feature ports.
    fixture,span = [],()
    for p in ports:
        grown = basis(span+(p[3],))
        if len(grown) > len(span):
            fixture.append(p)
            span = grown
        if len(span) == 15:
            break
    for c in range(8):
        fixture.append(next(p for p in ports if abs(p[4][c]) == 16))
    zero_b = next(j for j,value in enumerate(q) if not value)
    for i in (0,1):
        fixture.append((i,zero_b,1,coords[i] | (coords[zero_b] << 8) | (1 << 16),(0,)*8))
    fixture = list(dict.fromkeys(fixture))
    return rr,form,u,w,ports,fixture,orthogonal


def fixture_replay(fixture,u,w,orthogonal,dual=False,omit=None):
    n = len(fixture)
    labels = [p[3] for p in fixture]
    e = [p[4] for p in fixture]
    names = [f'x{i}' for i in range(n)]+[f'y{i}' for i in range(n)]+[f'c{i}' for i in range(8)]
    rows = {name:[Q(int(i == j)) for j in range(len(names))] for i,name in enumerate(names)}
    frames = {name:(basis((labels[i],)) if name.startswith('x') else ())
              for i,name in enumerate(names)}
    full = basis(1 << i for i in range(17))
    paths = Counter()
    def climb(name,frame,tag):
        if tag == omit:
            return
        need(included(frames[name],frame),'independent monotone frame inclusion')
        rank = len(frame)-len(frames[name])
        if rank:
            paths[rank] += 1
        frames[name] = frame
    def add(name,source,c,tag,dualize=True):
        if not c or tag == omit:
            return
        if dual and dualize:
            name,source,c = source,name,-c
        need(frames[name] == frames[source],'independent actual common frame')
        rows[name] = [a+c*b for a,b in zip(rows[name],rows[source])]
    for i in range(n):
        for c in range(8):
            add(f'y{i}',f'c{c}',-Q(e[i][c],8192),'prefix')
    for i in range(n):
        if any(e[i]):
            climb(f'x{i}',u,'source_U')
    for c in range(8):
        climb(f'c{c}',u,'centre_U')
        for i in range(n):
            add(f'c{c}',f'x{i}',Q(e[i][c]),'gather')
    for i in range(n):
        climb(f'x{i}',full,'source_FULL')
        if any(e[i]):
            climb(f'y{i}',w,'target_W')
    private_rank = 0
    for c in range(8):
        if omit == 'private':
            continue
        need(frames[f'c{c}'] == u and included(w,u),'private nested partial frame')
        rows['private'] = [Q(0)]*len(names)
        frames['private'] = w if dual else u
        private_rank += len(u)-len(w)
        if dual:
            for i in range(n):
                add('private',f'y{i}',Q(e[i][c],8192),'readout',False)
            immutable_readout = rows['private'][:]
            frames['private'] = u
            add(f'c{c}','private',Q(-1),'dual_scatter',False)
            need(rows['private'] == immutable_readout,'dual immutable readout lifetime')
        else:
            rows['private'] = rows[f'c{c}'][:]
            frames['private'] = w
            for i in range(n):
                add(f'y{i}','private',Q(e[i][c],8192),'scatter',False)
            need(rows['private'] == rows[f'c{c}'],'original centre snapshot ERASE')
        del rows['private'],frames['private']
    for c in range(8):
        climb(f'c{c}',full,'centre_FULL')
        for i in range(n):
            add(f'c{c}',f'x{i}',-Q(e[i][c]),'cleanup')
    for i in range(n):
        climb(f'y{i}',orthogonal((labels[i],)),'target_cap')
    for i,name in enumerate(names):
        expected = [Q(int(i == j)) for j in range(len(names))]
        if (name.startswith('y') and not dual) or (name.startswith('x') and dual):
            target = int(name[1:])
            for j in range(n):
                coefficient = Q(sum(a*b for a,b in zip(e[target],e[j])),8192)
                expected[n+j if dual else j] += -coefficient if dual else coefficient
        need(rows[name] == expected,'all independent source/target/dirty centre columns')
    return {'ordinary_input_columns':len(names),'fixture_ports':n,'private_rank':private_rank,
            'ordinary_path_histogram':dict(sorted(paths.items())),'all_input_shear':True}


@lru_cache(None)
def rational_power(r,exponent):
    numerator,degree = exponent.numerator,exponent.denominator
    target = r**numerator*SCALE**degree
    # A floating seed is only a speed hint. Exact powers certify the upper
    # starting point and exact neighboring powers certify the final interval.
    x = int(r**float(exponent)*SCALE)+SCALE//10**12
    while x**degree < target:
        x *= 2
    while True:
        y = ((degree-1)*x+target//x**(degree-1))//degree
        if y >= x:
            break
        x = y
    while x**degree > target:
        x -= 1
    while (x+1)**degree <= target:
        x += 1
    need(x**degree <= target < (x+1)**degree,'exact rational-power enclosure')
    return Q(x,SCALE),Q(x+1,SCALE)


def cost(radical,beta,shared=False):
    delta = Counter({15:8,2:8,17:-16})
    delta[13 if radical else 15] += 8
    if not shared:
        for count in (5760,)*(2 if radical else 1):
            delta.update({14:count,2:count,16:-count})
    need(sum(r*n for r,n in delta.items()) == (-32 if radical else -16),'complete rank-mass differential')
    lo = hi = Q(0)
    for r,n in delta.items():
        a,b = rational_power(r,1-beta)
        lo += n*(a if n >= 0 else b)
        hi += n*(b if n >= 0 else a)
    # Exponent beta+10^-24 changes the normalized delta by less than this
    # bound, because |d r^(1-beta)/d beta|<=r log r<3r for r<=17,beta>=0.
    perturbation = Q(3*sum(abs(n)*r for r,n in delta.items()),10**24)
    need(hi+perturbation < 0 if shared else lo-perturbation > 0,'complete moment sign')
    ml,mh = rational_power(49,beta)
    actual_lo = lo*(ml if lo >= 0 else mh)
    actual_hi = hi*(mh if hi >= 0 else ml)
    return {'radical':radical,'beta':str(beta),'shared_data_visits':shared,
            'profile_delta':dict(sorted(delta.items())),
            'normalized_delta_interval':list(map(str,(lo,hi))),
            'm49_delta_interval':list(map(str,(actual_lo,actual_hi))),
            'tiny_exponent_perturbation_bound':str(perturbation),
            'sign':'improves conditionally' if shared else 'worsens with new data visits'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    rr,form,u,w,ports,fixture,orthogonal = geometry()
    cases,controls = [],[]
    for radical,frame in ((False,()),(True,w)):
        forward = fixture_replay(fixture,u,frame,orthogonal)
        dual = fixture_replay(fixture,u,frame,orthogonal,True)
        for omit in ('prefix','gather','cleanup','source_U','private'):
            try:
                fixture_replay(fixture,u,frame,orthogonal,omit=omit)
            except ValueError as error:
                controls.append(str(error))
            else:
                raise ValueError('independent omission control accepted')
        if radical:
            try:
                fixture_replay(fixture,u,frame,orthogonal,omit='target_W')
            except ValueError as error:
                controls.append(str(error))
            else:
                raise ValueError('unpaid radical target visit accepted')
        cases.append({'radical':radical,'forward':forward,'dual':dual,
                      'full_K_private_bill':13840 if radical else 13856,
                      'costs':[cost(radical,beta,shared) for beta in map(Q,('.002','.003','.005')) for shared in (False,True)]})
    primary = [REPO/'research/niemeier-lattices/code/e8_cubed.py',
               REPO/'research/niemeier-lattices/code/e8_sections.py']
    primitive = 8*(2*(3072*7+672*8)+2*(3072*14+672*13)+3)
    need(primitive == 1258008,'selected component primitive bill')
    result = {'status':'PASS_INDEPENDENT_PARTIAL_PAULI_GEOMETRY_DIRTY_WORD_AND_COMPLETE_COST',
              'primary_sources':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in primary},
              'reviewed_producer_sha256':sha256((HERE.parent/'complex-alternative/partial_pauli.py').read_bytes()).hexdigest(),
              'physical_supported_ports':len(ports),'feature_incidence_each':3744,
              'feature_columns':[120+44*i for i in range(8)],'coefficient_denominator':8192,
              'intrinsic_bilinear_form':form,'intrinsic_U':u,'intrinsic_U_perp':w,
              'all_support_source_and_target_inclusions':True,
              'full_component_forward_primitive_bound':primitive,'full_component_dual_primitive_bound':primitive+24,
              'all_input_written_law':'c=d+E^T x; y=y0-E d/8192+E(d+E^T x)/8192=y0+E E^T x/8192; c restored by-E^T x. Dual phases give x-=E E^T y/8192 with d restored.',
              'fixture_ports':[[i,j,s] for i,j,s,p,e in fixture], 'cases':cases,'controls':controls,
              'frame_binding':'Intrinsic pairing coordinates use the actual E8 Gram inverse. The canonical17-bit fit is an isometry of this nondegenerate bilinear space; dimensions, inclusions and orthogonal complements therefore transfer to its fixed actual labels. No new free physical permutation is asserted.',
              'all_arity_sign_proof':'Delta moment=m^beta sum_r delta_H[r] r^(1-beta). The parent factor m^beta is positive for every arity; the exact enclosed signs are independent of m.',
              'limits':['full5760 support geometry and an all-parameter written arbitrary-input factor identity; bounded actual-port fixture is not dense fullK replay',
                        'private snapshot/readout erasure uses the inherited exact centre-copy and same-order dual interface',
                        'physical Clifford phases/adapters, coefficient temporary lowering, approximate children, precision and tape remain separate',
                        'conditional sharing requires already-paid identical U and Uperp visits in a compatible chronology; none is supplied here',
                        'no completed H6 supplier or kappa gain']}
    path = HERE/'PARTIAL-PAULI-REVIEW.json'
    if args.write:
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == json.loads(json.dumps(result)),'complete independent partial Pauli receipt differs')
    print(result['status'])
    print('U15, radical2, supported5760; standalone worsens .002/.003/.005 at every arity')


if __name__ == '__main__':
    main()
