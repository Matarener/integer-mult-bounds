#!/usr/bin/env python3
"""Dyadic Smith obstruction and explicit560-row repair existence certificate.

Source-bound to the exact H6 spectrum/moment proof, not a dense Smith
computation or a physical coding circuit. No arbitrary rational inverse.
"""
import argparse
import types
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
m=types.ModuleType('smith_geometry')
exec(compile((HERE/'geometry.py').read_bytes(),str(HERE/'geometry.py'),'exec'),m.__dict__)
need=m.need
REPO=HERE.parents[1]
PIN='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
EDGES=[(76,115),(57,101),(3,12),(39,42),(72,114),(37,86),(0,32),(68,104),
       (50,75),(30,37),(82,104),(27,57),(17,101),(17,100),(5,54),(34,37),
       (7,86),(33,112),(17,103),(11,19),(39,96),(76,117),(9,100),(104,116),
       (64,92),(41,52),(22,105),(4,106),(4,108),(19,72),(52,62),(84,99),
       (60,85),(12,103),(21,38),(110,113),(36,64),(16,74),(50,79),(6,28),
       (12,39),(35,82),(90,103),(62,80),(56,93),(49,55),(12,91),(66,69),
       (38,85),(55,118),(24,100),(16,21),(54,86),(34,52),(21,24),(6,93),
       (68,90),(4,77),(11,66),(67,87),(16,96),(43,90),(64,69),(73,113),
       (19,83),(50,113),(70,108),(95,101),(61,63),(77,115),(93,102),(51,75),
       (85,111),(66,67),(16,105),(103,119),(7,36),(112,117),(0,107),(64,70)]


def modular_rank(rows,prime):
    rows=[[x%prime for x in row] for row in rows]
    width=len(rows[0]);rank=0;det=1;columns=[]
    for col in range(width):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:continue
        if pivot!=rank:rows[rank],rows[pivot]=rows[pivot],rows[rank];det=-det
        v=rows[rank][col];det=det*v%prime
        inverse=pow(v,-1,prime);rows[rank]=[x*inverse%prime for x in rows[rank]]
        reference=rows[rank]
        for i in range(rank+1,len(rows)):
            v=rows[i][col]
            if v:rows[i][col:]=[(x-v*y)%prime for x,y in zip(rows[i][col:],reference[col:])]
        columns.append(col);rank+=1
        if rank==len(rows):break
    return rank,det%prime if rank==width==len(rows) else None,columns


def mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out


def evaluate(poly,x):
    out=0
    for a in reversed(poly):out=out*x+a
    return out


def valuation(n,p):
    count=0
    while n%p==0:count+=1;n//=p
    return count


def spectral_certificate():
    sources={}
    for path in ('research/h6-independent-audit/spectral/results.json',
                 'research/h6-independent-audit/spectral/README.md',
                 'research/h6-independent-audit/spectral/audit.py',
                 'research/niemeier-lattices/workbench/helper-routes/compensation_rank.py',
                 'research/niemeier-lattices/code/e8_cubed.py',
                 'research/h6-compensation-network/k_encoder/README.md'):
        raw=(REPO/path).read_bytes()
        sources[path]=hashlib.sha256(raw).hexdigest()
        if path.endswith('results.json'):result=json.loads(raw)
    need(result['kernel_rank']==816 and result['compensation_rank_over_real_numbers']==30960,
         'pinned exact full H6 spectrum')
    spectrum=result['kernel_spectrum']
    need([x['multiplicity'] for x in spectrum if 'multiplicity' in x]==[224,560,30144],
         'pinned harmonic/mixed/null multiplicities')
    need(any(x.get('multiplicity_each')==16 for x in spectrum),'pinned radial multiplicities')
    factors=[([0,1],30144),([-39,1],224),([-45,1],560),([-6075,186,1],16)]
    annihilator=[1]
    for poly,multiplicity in factors:annihilator=mul(annihilator,poly)
    derivative=[i*x for i,x in enumerate(annihilator)][1:]
    nullities={}
    for prime,wanted in ((11,560),(19,224),(23,16)):
        need(evaluate(annihilator,1)%prime==0
             and evaluate(derivative,1)%prime!=0,'eigenvalue1 simple in reduced annihilator')
        multiplicity=sum(n for poly,n in factors if evaluate(poly,1)%prime==0)
        need(multiplicity==wanted,'reduced characteristic multiplicity')
        nullities[prime]=wanted
    need(1+186-6075==-5888 and 5888==2**8*23,'radial determinant factor')
    need((224+560+16)%2==0,'positive determinant sign')
    need(all((F(t**3-4*t,48).denominator & (F(t**3-4*t,48).denominator-1))==0
             for t in range(-4,5)),'every attainable integer Gram coefficient is dyadic')
    determinant={2:224+2*560+8*16,11:560,19:224,23:16}
    need(determinant[2]==1472,'dyadic determinant valuation')
    need(all(determinant[p]==nullities[p] for p in nullities),
         'all nonunit elementary divisors have exponent1')
    smith=[(1,30400),(11,336),(209,208),(4807,16)]
    need(sum(n for d,n in smith)==30960,'all Smith factors covered')
    need(all(sum(n*valuation(d,p) for d,n in smith)==nullities[p] for p in nullities),
         'localized Smith prime valuations')
    missing_radial=[(1,30400),(11,336),(209,224)]
    need(sum(n*valuation(d,23) for d,n in missing_radial)!=nullities[23],
         'omitted radial torsion corruption rejected')
    need(224!=nullities[11] and 560!=nullities[19],
         'swapped odd-prime nullity corruption rejected')
    return sources,annihilator,determinant,nullities,smith


def physical_row_certificate():
    roots=m.canonical_roots()
    need(len(EDGES)==len(set(EDGES))==80,'explicit80 physical pair edges')
    S=[(i,i) for i in range(120)]+[pair for i,j in EDGES for pair in ((i,j),(j,i))]
    need(len(S)==len(set(S))==280 and set(S)=={(j,i) for i,j in S},
         'symmetric280-pair row set containing all diagonals')
    quadratics=[[a[i]*a[j] for i,j in combinations(range(8),2)]
                +[a[i]*a[i]-a[7]*a[7] for i in range(7)] for a in roots]
    mixed=[[x*y for x in roots[i] for y in quadratics[j]] for i,j in S]
    rank,det,pivots=modular_rank(mixed,11)
    need(rank==280 and det,'explicit280 mixed feature minor modulo11')
    # Symmetry of S gives the swapped35x8 mixed feature minor. Both b signs
    # form a560x560 block, separated by the invertible Hadamard pair matrix.
    harmonic=[]
    monomials=list(combinations_with_replacement(range(8),3))
    for a in roots:
        norm=sum(x*x for x in a);row=[]
        for triple in monomials:
            counts=Counter(triple)
            value=10*a[triple[0]]*a[triple[1]]*a[triple[2]]
            if len(counts)==1:value-=3*norm*a[triple[0]]
            elif len(counts)==2:
                single=next(i for i,n in counts.items() if n==1)
                value-=norm*a[single]
            row.append(value)
        harmonic.append(row)
    hrank,_,hpivots=modular_rank(harmonic,19)
    need(hrank==112,'integer harmonic root restrictions rank112 mod19')
    lrank,_,lpivots=modular_rank(roots,23)
    need(lrank==8,'integer radial root restrictions rank8 mod23')
    M=[[9,-240],[-18,-195]]
    radial=[1,10]
    need(all((sum(M[i][j]*radial[j] for j in range(2))-radial[i])%23==0
             for i in range(2)),'radial1-eigenvector modulo23, nonzero root coefficient10')
    rows=sorted(2160+240*i+2*j+sign for i,j in S for sign in (0,1))
    need(len(rows)==len(set(rows))==560,'literal physical row support560')
    # Strong negative controls on the actual small arithmetic certificates.
    duplicate=list(mixed);duplicate[-1]=duplicate[0]
    need(modular_rank(duplicate,11)[0]<280,'duplicate physical mixed row rejected')
    raw=[[a[i]*a[j]*a[k] for i,j,k in monomials] for a in roots]
    need(modular_rank(raw,19)[0]==120,'unprojected cubics differ from harmonic112')
    return {'root_pairs':S,'physical_rows':rows,'mixed_mod11_rank':rank,'mixed_mod11_det':det,
            'harmonic_mod19_rank':hrank,'harmonic_pivot_columns':hpivots,
            'radial_mod23_rank':lrank,'radial_pivot_columns':lpivots,
            'radial_source_action':M,'radial_mod23_eigenvector':radial,
            'kernel_restriction_ranks':{11:560,19:224,23:16},
            'consequence':'The untouched30400 physical rows of C are independent modulo every odd prime, hence generate a primitive free row submodule over Z[1/2]. They admit an algebraic unimodular completion by replacing only these560 rows. Completion coefficients and a native physical ADD realization are not supplied.'}


def completion():
    blocks=[]
    for value,count in ((11,336),(209,208),(4807,16)):
        rows=[[1,0],[0,1]]
        for dst,src,q in ((0,1,1),(1,0,-1),(0,1,1),(0,1,-value)):
            rows[dst]=[x+q*y for x,y in zip(rows[dst],rows[src])]
        need(rows==[[value,1],[-1,0]] and rows[0][0]*rows[1][1]-rows[0][1]*rows[1][0]==1,
             'explicit four-ADD unit completion block')
        primitive=12+3+value.bit_length()-1+value.bit_count()
        blocks.append({'d':value,'count':count,'matrix':rows,'component_primitives':primitive})
    return blocks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    sources,annihilator,determinant,nullities,smith=spectral_certificate()
    physical=physical_row_certificate()
    blocks=completion()
    out={'status':'PASS_H6_DYADIC_SMITH_AND_SHARP560_PHYSICAL_ROW_REPAIR_EXISTENCE_NO_NEW_KAPPA',
         'source_pin':PIN,'source_sha256':sources,'ring':'Z[1/2]','N':30960,
         'K_annihilator_low_coefficients':annihilator,
         'annihilator_proof':'K is a rational symmetric matrix. The pinned exact moment/sector proof gives its complete real spectrum; orthogonal diagonalization therefore implies the displayed monic rational annihilator identity. Its entries are dyadic on every attainable Gram value, so polynomial identities and characteristic factors reduce modulo odd primes.',
         'sector_source_boundary':'The complete sector polynomial actions are inherited from the written spherical-moment proof, not inferred from representative probes. Pinned spectral/audit.py defines radial basis R=[x*single,x*rootroot] and checks num@R=48R@M, fixing the rootproduct coefficient10 of eigenvector(1,10) modulo23. The pinned source audits are not freshly replayed here.',
         'C_determinant_prime_valuations':determinant,'C_mod_prime_nullities':nullities,
         'localized_Smith_factors':[{'factor':d,'count':n} for d,n in smith],
         'minimal_rank_repair':560,'minimal_physical_rows_replaced_algebraically':560,
         'minimal_stable_auxiliary_directions':560,'physical_row_certificate':physical,
         'unit_extension_Smith_blocks':blocks,
         'Smith_block_component_primitives_before_basis_cost':sum(z['count']*z['component_primitives'] for z in blocks),
         'dirty_contract':'The unit block sends(x,h) to(d*x+h,-x). Helper output is changed and top output contains arbitrary helper dirt. Restored-helper exact(x,h)->(C*x,h) has determinant detC and is impossible as a dyadic unimodular map. No clean/cancelled endpoint interface follows from stable completion.',
         'elementary_ADD_caveat':'ADD-only networks have determinant1, a stronger condition than being a dyadic unit. The algebraic row completion can be normalized to determinant1 by rescaling one replaced row by a dyadic unit. Stable completion can normalize one auxiliary output similarly. This is an algebraic existence statement, not a paid implementation of the Smith bases or physical transports.',
         'negative_controls':['duplicate one actual mixed evaluation row','use unprojected cubics in place of harmonic cubics'],
         'arithmetic_counterchecks':['omit the23-primary radial Smith factors','swap the11 and19 nullity assignments'],
         'proposed_consumer_boundary':{'current_native_clean_response':'K*x, rank816, in the existing canonical H6 source/output frame conventions',
                                      'minimum_row_repair_if_coding_K_itself':30960-816,
                                      'C_is':'The full-rank compensation operator I-K, not the current native clean response.',
                                      'missing_consumer':'A new cheap producer of the complement response C*x with specified source/output gauges and residue lifecycle. The existing fullC edge-helper word is far too costly and does not discharge this gate.',
                                      'gauges':'All row IDs and coefficients use the pinned canonical physical ports. No new coded source/output frame representative or physical gauge realization is supplied. Invertible pre/post gauges preserve the rank deficiency of K.'},
         'scope':'Source-bound exact Smith/localization theorem and literal560-row algebraic completion certificate for C=I-K, which is not the current native K response. The full30960 matrix is not constructed or Smith-reduced. Polynomial sector proofs are inherited; small modular feature minors and explicit unit blocks are freshly checked. Native complement producer, source/output gauges, basis-change work, input/auxiliary dirt compensation, restoration, physical banks/copies, phase/precision/tape, controller and outer multiplier are unresolved. No new kappa.'}
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' nullities=560/224/16 physical_rows=560 auxiliary_floor=560')
    print('mixed minor det mod11',physical['mixed_mod11_det'],'Smith-block primitives',out['Smith_block_component_primitives_before_basis_cost'])


if __name__=='__main__':main()
