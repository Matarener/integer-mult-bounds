#!/usr/bin/env python3
"""Exact cover-owner fixture for paired helpers with overlapping spectators.

Checks the complete declared finite cyclic-cover domain. The general cover
argument and missing supplier premises are in PAIRED-HELPER-OWNERS.md.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json

HERE=Path(__file__).resolve().parent
M=36

def need(v,msg):
    if not v:
        raise ValueError(msg)

def swap_axes(xs):
    p=list(range(2*M))
    for j in xs:
        p[j],p[M+j]=p[M+j],p[j]
    return p

def compose(a,b):
    return [a[j] for j in b]

def local_residual(slot,omit_entry=False):
    block={(6*slot+j)%M for j in range(6)}
    entrance={(6*slot+j)%M for j in (6,7)}
    need(block.isdisjoint(entrance),'local footprint is eight distinct axes')
    physical=swap_axes(block|entrance)
    if not omit_entry:
        physical=compose(physical,swap_axes(entrance))
    need(omit_entry or physical==swap_axes(block),'actual D_U D_E inverse is width6')
    return physical,block,entrance

def run(omit_entry=False,omit_role=False,duplicate_adapter=False):
    owners=[list(range(2*M)) for _ in range(6)]
    events=[]
    for d in range(6):
        assigned=set()
        for role in range(5 if omit_role else 6):
            slot=0 if duplicate_adapter and role==1 else role
            g=(d-slot)%6
            need(g not in assigned,'one physical family per role at one invocation')
            assigned.add(g)
            op,block,entrance=local_residual(slot,omit_entry)
            # Conjugate by the owner chart g: simultaneous cyclic shift of
            # both address halves. The direction is fixed and checked here.
            chart=[(j+6*g)%M for j in range(M)]
            chart+= [M+(j+6*g)%M for j in range(M)]
            inverse=[0]*(2*M)
            for i,j in enumerate(chart):
                inverse[j]=i
            routed=compose(chart,compose(op,inverse))
            owners[g]=compose(routed,owners[g])
            events.append({'invocation':d,'role':role,'owner':g,
                           'slot_axes':sorted(block),'entrance_axes':sorted(entrance)})
    return owners,events

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    owners,events=run()
    full=swap_axes(range(M))
    need(all(p==full for p in owners),'every independent coordinate at every owner has full swap')
    need(any(set(a['entrance_axes']) & set(b['slot_axes'])
             for a in events[:6] for b in events[:6] if a['role']!=b['role']),
         'fixture actually overlaps spectator and another residual block')
    need(any(p!=full for p in run(omit_entry=True)[0]),'ignoring paired entrance changes owner output')
    need(any(p!=full for p in run(omit_role=True)[0]),'missing role leaves unpaid owner residual')
    try:
        run(duplicate_adapter=True)
    except ValueError:
        alias_control=True
    else:
        raise ValueError('duplicated adapter must alias the same physical family')
    stock=Q(318,6)+Q(111,4)
    helper_mass=318*6+111*8
    need(helper_mass+111==36*stock,'coordinate E2 dedicated helper mass with complete padding')
    out={'status':'PASS_PAIRED_HELPER_DEDICATED_COVER_OWNER_FIXTURE',
         'no_new_kappa':True,'m':M,'cover':'six cyclic shifts by6 axes',
         'physical_owners':6,'roles_per_invocation':6,'invocations':6,
         'all72_coordinate_columns_per_owner':True,'events':events,
         'controls':{'ignored_entrance_fails':True,'missing_role_fails':True,
                     'same_call_family_alias_rejected':alias_control},
         'E2_helper_inventory_only':{'replicas':12,'width6_banks':636,'width8_banks':333,
                                    'stock_per_call':str(stock),'padding_per_call':{'4':str(Q(111,4))},
                                    'local_helper_rank_mass':helper_mass,'padding_rank_mass_per_call':111},
         'scope':'Finite exact arbitrary-coordinate fixture for the dedicated bank theorem. It does not replay a local supplier or authorize recycling a public family. The actual local dirty cancellation, native wrappers, source/target stock and paid machine costs remain required.'}
    out=json.loads(json.dumps(out))
    dest=HERE/'PAIRED-HELPER-OWNERS.json'
    if args.write:
        dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(dest.read_text())==out,'saved owner fixture differs')
    print(out['status'])
    print('6 owners,36 roles,72 coordinate columns,3 defects; E2 helper-only stock',stock)

if __name__=='__main__':
    main()
