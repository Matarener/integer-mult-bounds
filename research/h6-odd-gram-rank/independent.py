#!/usr/bin/env python3
"""Independent characteristic-zero review of the H6 odd-Gram rank claim.

Does not import the producer. Derives spectra from entrywise powers and
checks canonical root-product actions against all28800 input columns.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations,product
import json
from math import comb,lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def roots():
    out = []
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            q = [0]*8
            q[i],q[j] = a,b
            out.append(tuple(q))
    out += [q for q in product((-1,1),repeat=8) if sum(q)%4 == 0]
    return sorted(out)


def spectra(j,sector):
    # Derived from H_j=S+(2^j-2)(I-A), j odd, and
    # H_j=R+(2^j-4)(I+A), j positive even. H_0=J.
    s = (0,60,0,0,0)[sector]
    r = (120,0,24,0,0)[sector]
    antipode = (1,-1,1,-1,1)[sector]
    if j == 0:
        return 240 if sector == 0 else 0
    return s+(2**j-2)*(1-antipode) if j%2 else r+(2**j-4)*(1+antipode)


def forms():
    # Solve f(2)=0,f(4)=1 symbolically, with free a5=u,a7=v.
    a3 = [Q(1,48),Q(-20),Q(-336)]
    a1 = [-4*x+y for x,y in zip(a3,[Q(0),Q(-16),Q(-64)])]
    coeff = {1:a1,3:a3,5:[Q(0),Q(1),Q(0)],7:[Q(0),Q(0),Q(1)]}
    dimensions = [1,8,35,112,84]
    out = []
    for odd,even in product((1,3),(0,2,4)):
        f = [Q(0)]*3
        for degree,c in coeff.items():
            eigen = Q(sum(comb(degree,k)*spectra(k,odd)*spectra(degree-k,even)
                          for k in range(degree+1)),2)
            f = [x+eigen*y for x,y in zip(f,c)]
        out.append((odd,even,2*dimensions[odd]*dimensions[even],f))
    out.sort(key=lambda t:({(1,0):0,(3,0):1,(1,2):2,(3,2):3,(1,4):4,(3,4):5}[t[:2]]))
    need(sum(d for a,b,d,f in out) == 28800,'odd simultaneous-antipode dimension')
    return coeff,out


def evaluate(form,u,v):
    return form[0]+form[1]*u+form[2]*v


def direct_actions(q,s,coeff,all_forms,scale=1):
    features = [[1]*240,[a[0] for a in q],
                [a[0]**2-a[1]**2 for a in q],
                [a[0]*a[1]*a[2] for a in q],
                [a[0]*a[1]*a[2]*a[3] for a in q]]
    canonical = [i for i,a in enumerate(q) if next(x for x in a if x) > 0]
    need(len(canonical) == 120,'actual120 canonical a-lines')
    count = 0
    for u,v in ((Q(0),Q(0)),(Q(1,608),Q(0)),(-Q(1,160),Q(1,2800))):
        cs = {j:evaluate(c,u,v) for j,c in coeff.items()}
        denominator = lcm(*(c.denominator for c in cs.values()))
        values = {t:int(denominator*sum(c*t**j for j,c in cs.items())) for t in range(-4,5)}
        need(values[2] == 0 and values[4] == denominator,'independent interpolation constraints')
        for a,b,d,form in all_forms:
            ia = next(i for i in canonical if features[a][i])
            ib = next(i for i in range(240) if features[b][i])
            actual = sum(values[s[ia][i]+s[ib][j]]*features[a][i]*features[b][j]
                         for i in canonical for j in range(240))
            expected = denominator*scale*evaluate(form,u,v)*features[a][ia]*features[b][ib]
            need(actual == expected,'independent canonical28800-column action')
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    q = roots()
    need(len(q) == len(set(q)) == 240 and all(sum(x*x for x in a) == 8 for a in q),'standard doubled E8 roots')
    need(all(sum(a[i]*a[j] for a in q) == 240*(i == j) for i in range(8) for j in range(8)),'root second moment')
    s = [[sum(x*y for x,y in zip(a,b))//4 for b in q] for a in q]
    need(all(sum(x*y for x,y in zip(a,b))%4 == 0 for a in q for b in q),'ordinary Gram normalization')
    ones = [sum(1 << j for j,x in enumerate(row) if abs(x) == 1) for row in s]
    fours = [sum(1 << j for j,x in enumerate(row) if abs(x) == 2) for row in s]
    for i,j in product(range(240),repeat=2):
        square = ((ones[i]&ones[j]).bit_count()+4*(ones[i]&fours[j]).bit_count()
                  +4*(fours[i]&ones[j]).bit_count()+16*(fours[i]&fours[j]).bit_count())
        need(square == 24*s[i][j]**2+48,'all57600 R-squared entries')
    # trace S=480,S^2=60S gives8 odd linear directions. Even/odd parts
    # each have120 dimensions. traceR=960 and eigenvalue120 on constants,
    # with R^2=24R+48J, give35 traceless quadratics. Complements give112,84.
    ranks = [1,480//60,(960-120)//24,120-480//60,120-1-(960-120)//24]
    need(ranks == [1,8,35,112,84],'independent projector rank derivation')
    coeff,all_forms = forms()
    actions = direct_actions(q,s,coeff,all_forms)
    cubic = sum(d for a,b,d,f in all_forms if evaluate(f,0,0))
    uzeros = [-f[0]/f[1] for a,b,d,f in all_forms[:3]]
    need(len(set(uzeros)) == 3 and Q(1,608) in uzeros,'distinct quintic old-sector zeros')
    quintic = 7840+1344+800-max(16,224,560)
    vzeros = [-f[0]/(f[2]-Q(35,2)*f[1]) for a,b,d,f in all_forms[:3]]
    need(vzeros == [Q(13,30576),Q(1,3192),Q(1,2800)] and len(set(vzeros)) == 3,'complete septic affine intersections')
    septic = 18816+1344+800-max(16,224,560)
    need(cubic == 800 and quintic == 9424 and septic == 20400,'claimed exact rank minima')
    need(sum(d for a,b,d,f in all_forms if evaluate(f,Q(1,608),0)) == quintic,'quintic witness')
    need(sum(d for a,b,d,f in all_forms if evaluate(f,-Q(1,160),Q(1,2800))) == septic,'septic witness')
    try:
        direct_actions(q,s,coeff,all_forms,scale=2)
    except ValueError as error:
        control = str(error)
    else:
        raise ValueError('missing canonical quotient factor accepted')
    source = REPO/'research/niemeier-lattices/code/e8_cubed.py'
    claims = json.loads(args.producer.read_bytes())
    claimed = [(x['sectors'][0],x['sectors'][1],x['dimension'],list(map(Q,x['constant_u_v']))) for x in claims['eigenforms']]
    need(claimed == all_forms,'independent forms disagree with claimed result')
    result = {'status':'PASS_INDEPENDENT_ODD_GRAM_SIX_FORMS_AND_ALL_COMPLEX_MINIMA',
              'primary_geometry_source':str(source),'primary_geometry_sha256':sha256(source.read_bytes()).hexdigest(),
              'reviewed_producer_sha256':sha256((HERE/'derive.py').read_bytes()).hexdigest(),
              'projector_ranks':ranks,'association_square_entries':57600,'canonical_input_columns_per_action':28800,
              'direct_actions':actions,'forms':[{'sectors':[a,b],'dimension':d,'constant_u_v':list(map(str,f))} for a,b,d,f in all_forms],
              'rank_minima':[cubic,quintic,septic],'quintic_old_zero_u':list(map(str,uzeros)),
              'septic_old_zero_v_on_7840_zero_line':list(map(str,vzeros)),
              'canonical_quotient_negative_control':control,
              'all_complex_proof':'For v=0,u!=0, both new sectors survive and the three old zeros are distinct. For v!=0, either7840 survives, already giving26656, or u=-35v/2; then1344 survives and three distinct old zeros remove at most560. These alternatives exhaust C², not just rational sample points.',
              'root_product_binding':'Primary e8_shells uses exactly two nonzero doubled entries +/-2 and half-root signs summing0 mod4; these equal the freshly generated240 signed roots. construct_shell uses120 first-nonzero-positive a representatives times both signs of every one of120 b representatives. The selected two-block shell therefore has this canonical28800 principal block, plus2160 single-block ports.',
              'limits':['written primary geometry/source binding, not an independently rerun NumPy shell generator',
                        'rank minima over characteristiczero only; characteristic2 is excluded',
                        'cost consequence applies only to full-width scalar factor return episodes, not general restored helpers, partial frames, nonisotropic kernels or operator-valued circuits',
                        'no physical supplier, rounded precision, ownership, tape or kappa claim']}
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
