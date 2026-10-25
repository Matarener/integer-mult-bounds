#!/usr/bin/env python3
"""Exact slot-derivative certificate for the retained eight-stream graph.

This checks a scoped obstruction, not a multiplication lower bound. Its
proof is SLOT-PROJECTOR-RIGIDITY.md. The graph and Fourier operator originate
in PR3187 (Nick Petalas), using the credited nine-stage construction; PR3296
and PR4046 supply subsequent source-bound audits. New nilpotent-ring argument
and certificate with substantial OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
TEMPLATE=HERE.parent/'operator-audit/checkout/research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz'


def derivative(template):
    matrix=[[int(i==j) for j in range(8)] for i in range(8)]
    D=[[[0]*8 for _ in range(8)] for _ in range(20)]
    local={e['stage']:e for e in template['recipe'] if e['kind']=='local'}
    slots=[];events=[]
    def shear(d,s):
        matrix[d]=[a^b for a,b in zip(matrix[d],matrix[s])]
        for X in D:X[d]=[a^b for a,b in zip(X[d],X[s])]
        events.append(['shear',d,s])
    for event in template['execution_schedule']:
        k=event['kind']
        if k=='local_cover_sweep':
            l=local[event['stage']];x=2*l['pair']
            if l['reverse']:shear(x,x+1)
            else:shear(x+1,x)
        elif k=='bridge':
            s,d=event['src'],event['dst']
            shear(2*d,2*s);shear(2*s+1,2*d+1)
        elif k=='idle_cover_sweep':
            for side,c in enumerate(event['child_indices']):
                stream=2*event['pair']+side
                assert c not in slots
                slots.append(c)
                D[c][stream]=[a^b for a,b in zip(D[c][stream],matrix[stream])]
                events.append(['slot',c,stream])
        elif k=='terminal':
            for p in range(event['pairs']):
                matrix[2*p],matrix[2*p+1]=matrix[2*p+1],matrix[2*p]
                for X in D:X[2*p],X[2*p+1]=X[2*p+1],X[2*p]
                events.append(['swap',2*p,2*p+1])
        else:
            assert k in ('terminal_Y_translations','bank_padding_cover_sweep','translate_every_live_family')
    assert sorted(slots)==list(range(20))
    assert matrix==[[int(i==j) for j in range(8)] for i in range(8)]
    columns=[sum(X[i][j]<<(8*i+j) for i in range(8) for j in range(8)) for X in D]
    return columns,events


def left_inverse(columns):
    # Reduce the64 rows of the64x20 map. Row-operation masks give an
    # explicit left inverse: each of20 slot bits is recovered from output
    # matrix entries by the corresponding64-bit mask.
    rows=[sum(((columns[c]>>bit)&1)<<c for c in range(20)) for bit in range(64)]
    provenance=[1<<bit for bit in range(64)]
    rank=0;pivots=[]
    for c in range(20):
        p=next((i for i in range(rank,64) if rows[i]>>c&1),None)
        assert p is not None,('dependent slot column',c)
        rows[rank],rows[p]=rows[p],rows[rank]
        provenance[rank],provenance[p]=provenance[p],provenance[rank]
        for i in range(64):
            if i!=rank and rows[i]>>c&1:
                rows[i]^=rows[rank];provenance[i]^=provenance[rank]
        pivots.append(c);rank+=1
    assert rows[:20]==[1<<c for c in range(20)]
    answer=provenance[:20]
    assert all((answer[i]&columns[j]).bit_count()%2==int(i==j) for i in range(20) for j in range(20))
    return answer


def projector(axes):
    return [sum(((sum(((a>>i)&1)*((a>>j)&1) for a in axes))%2)<<j for j in range(3)) for i in range(3)]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'SLOT-PROJECTOR-RIGIDITY.json')
    args=ap.parse_args()
    template=json.loads(gzip.decompress(TEMPLATE.read_bytes()))
    columns,events=derivative(template);inverse=left_inverse(columns)
    old,new=[1,2,4],[7]
    assert __import__('functools').reduce(int.__xor__,old)==__import__('functools').reduce(int.__xor__,new)==7
    assert all((a&b).bit_count()%2==int(i==j) for axes in (old,new) for i,a in enumerate(axes) for j,b in enumerate(axes))
    P,Q=projector(old),projector(new)
    assert P!=Q
    z=3
    old_exponent=sum((z&a).bit_count()%2 for a in old)%4
    new_exponent=sum((z&a).bit_count()%2 for a in new)%4
    assert old_exponent==2 and new_exponent==0
    result={'status':'PASS_RANK20_SLOT_DERIVATIVE_AND_FIXED_GRAPH_PROJECTOR_RIGIDITY',
        'dimension':73,'streams':8,'idle_slots':20,'rank_over_F2':20,
        'flattening':'matrix entry(i,j) maps to bit8*i+j',
        'columns':[str(x) for x in columns],
        'left_inverse_rows':[str(x) for x in inverse],
        'left_inverse_identity_entries_checked':400,
        'scalar_graph_mod2':events,
        'quotient_ring':'Z[i]/(i-1)^3; epsilon=i-1, epsilon^3=0, epsilon^2=2, 2*epsilon=0',
        'fixed_graph_conclusion':'Under the stated Fourier operator, arbitrary simultaneous replacements of the20 idle orthonormal frames preserving the full operator, with any inserted linear translations and sign controls, must preserve the orthogonal projector and rank of every slot. With hosted widths fixed, every residual rank is unchanged.',
        'nonstandard_basis_control':{'original_axes':old,'replacement_axes':new,'common_xor':7,
            'original_projector_rows':P,'replacement_projector_rows':Q,
            'character':z,'original_phase_exponent_mod4':old_exponent,
            'replacement_phase_exponent_mod4':new_exponent,
            'result':'First-order XOR agreement does not pass the second-order projector condition.'},
        'outside_scope':['new slot times or additional slots','changed local or scalar graph','shear coefficients multiplied by i rather than only sign changes','changed helper widths or local supplier','nonlinear Fourier-phase corrections','per-stream coordinate changes that change the normalized scalar/local operator'],
        'new_kappa':False,
        'source_pins':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (TEMPLATE,Path(__file__))}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'rank',20,'left_inverse_checks',400)


if __name__=='__main__':main()
