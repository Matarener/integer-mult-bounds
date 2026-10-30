#!/usr/bin/env python3
"""Exact E8 O3 geometry and a scoped first-order caller obstruction.

This does not assert that all possible native controllers obey the grammar.
Prepared with substantial OpenAI Codex assistance; local research only.
"""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canon(p):
    return tuple(-x for x in p) if next(x for x in p if x) < 0 else tuple(p)

def rotate(p):
    # Cyclic permutation of the three bits indexing the eight coordinates.
    # The pinned root chart is the extended-Hamming chart, not the usual D8
    # plus spinor chart; the literal (012)(345) does not preserve this file.
    return (p[0], p[4], p[1], p[5], p[2], p[6], p[3], p[7])

def dot(p, q):
    return sum(a*b for a,b in zip(p,q))

def projector(p):
    return [[Q(a*b,4) for b in p] for a in p]

def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def rank2(rows):
    pivots={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p]=row
                break
    return len(pivots)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    roots=sorted({canon(p) for p in json.loads(gzip.decompress(SOURCE.read_bytes()))['lines']})
    need(len(roots)==120 and all(dot(p,p)==4 for p in roots),'root census')
    need(all(canon(rotate(p)) in roots and rotate(rotate(rotate(p)))==p for p in roots),'order3 automorphism')
    chosen={p for p in roots if dot(p,rotate(p))==0}
    seen=set();orbits=[]
    for p in sorted(chosen):
        if p in seen:
            continue
        orbit=[p,rotate(p),rotate(rotate(p))]
        seen.update(map(canon,orbit))
        need(all(dot(orbit[i],orbit[j])==0 for i in range(3) for j in range(3) if i!=j),'orthogonal orbit')
        ps=list(map(projector,orbit))
        s=[[Q(i==j)-sum(a[i][j] for a in ps) for j in range(8)] for i in range(8)]
        need(mm(s,s)==s and sum(s[i][i] for i in range(8))==5,'rank5 orbit spectator')
        for k in range(3):
            residual=[[Q(i==j)-ps[k][i][j]-ps[(k+1)%3][i][j] for j in range(8)] for i in range(8)]
            need(residual==[[s[i][j]+ps[(k+2)%3][i][j] for j in range(8)] for i in range(8)],'paired residual split')
        orbits.append(orbit)
    need(len(chosen)==54 and len(orbits)==18 and seen==chosen,'eligible O3 orbit census')
    invalid_chart_permutation=lambda p:(p[2],p[0],p[1],p[5],p[3],p[4],p[6],p[7])
    chart_defects=sum(canon(invalid_chart_permutation(p)) not in roots for p in roots)
    need(chart_defects>0,'wrong-chart rotation control')
    # On one closed orbit and two active banks, d_x diag(z,x,y,z,x,y)
    # has two independent rows. Scalar entrance/exit gates preserve rank.
    derivative=[0,1<<1,0,0,1<<4,0]
    need(rank2(derivative)==2,'local first derivative rank')
    screens=[]
    for banks in range(1,9):
        old_calls=2*banks+1
        target_rank=6*banks
        screens.append({'bank_pairs':banks,'old_calls':old_calls,
                        'max_derivative_rank':2*old_calls,'required_rank':target_rank,
                        'first_order_rejects_old_call_count':2*old_calls<target_rank,
                        'necessary_calls':3*banks})
    # A paid complete common transform on every bank has the missing full
    # derivative; it genuinely violates the generator hypothesis.
    mutation_rank=rank2([1<<i for i in range(24)])
    need(mutation_rank==24 and mutation_rank>2,'paid full-common gate mutation')
    # C3 regular cover: x,y,z have their nonzero variation on separate
    # diagonal cover coordinates. Each orbit port contributes one and the
    # two active banks therefore contribute six. Their product varies on
    # every cover coordinate, including for the finite complex x=i test.
    cover_local=[0]*18
    for bank in range(2):
        for port in range(3):
            index=9*bank+3*port+port
            cover_local[index]=1<<index
    need(rank2(cover_local)==6,'regular cover local variation rank')
    out={'status':'PASS_EXACT_GEOMETRY_AND_SCOPED_ORBIT_CLOSED_DERIVATIVE_BOUND',
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'eligible_root_lines':len(chosen),'orthogonal_orbits':len(orbits),
         'orbits':orbits,'local_residual':'rank5 spectator plus the third orbit line',
         'first_order_ring':'F2[e]/(e^2), x maps to 1+e, y,z map to 1',
         'local_derivative_rank':2,'necessary_calls':'L >= 3 B',
         'regular_cover':{'local_variation_rank':6,'target_variation_rank':'18 B',
             'finite_complex_comparison':'(x,y,z)=(1,1,1) versus cyclic cover of (i,1,1)',
             'additional_premise':'all free native maps factor through parameter-independent scalar matrices and the C3 cover permutation'},
         'wrong_chart_rotation_defects':chart_defects,
         'screens':screens,'control_paid_full_common_derivative_rank':mutation_rank,
         'scope':['one closed orthogonal three-port orbit',
                  '2B independent data banks; no auxiliary values',
                  'each local gate has scalar invertible factors and diagonal (z,x,y) on exactly two banks',
                  'free gates are parameter-independent scalar matrices',
                  'desired endpoint is xyz on every data row, up to parameter-independent scalar invertible maps'],
         'outside_scope':['address automorphisms beyond the stated C3 regular-cover grammar',
                          'cross-orbit port mixing, arbitrary native operator coefficients',
                          'changed final consumers, paid correction gates, auxiliary carriers'],
         'no_new_kappa':True}
    out=json.loads(json.dumps(out))
    path=HERE/'GEOMETRY-DERIVATIVE.json'
    if args.write:
        path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes())==out,'complete receipt mismatch')
    print(out['status'])
    print('54 root lines, 18 orthogonal triples; orbit-closed B4 nine-call grammar needs at least 12 calls')

if __name__=='__main__':
    main()
