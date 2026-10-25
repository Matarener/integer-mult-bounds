#!/usr/bin/env python3
"""Bind an exact Laurent controller to a complete mixed-output tariff.

The source-bound receipt checks actual local words, the integral Laurent
identity, all helper inventories, strict recursive separation, and exact
moments. Native global frame placement and the outer transfer remain
separate proof obligations. Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'bit'))
import complex_controller_factor as C
import mixed_forest_search as F
import mixed_target_probe as E
import identity_mixed_certificate as I


def geometry(p,keep):
    coefficients,events,idles=C.controller(p,keep)
    factored=C.factor(coefficients)
    E.need(factored is not None,'Exact rational Laurent simultaneous diagonalization')
    formal=C.serialize_case(p,keep,coefficients,events,idles,factored)
    windows=[{'name':str(w['index'])+'_'+w['kind']+str(w['pair']),
              'capacity':w['rank'],'stages':w['stages']}
             for w in idles if w['retained']]
    targets={int(r):int(n) for r,n in formal['endpoint_after_stated_free_Pauli_normalization'].items()}
    return windows,targets,formal


def simple_p3():
    """An integer packing; its selection requires no optimization library."""
    return [dict(family=f,pattern=[a,b],count=str(n))
            for f in (0,3) for n,a,b in I.PAIRS]+[
            dict(family=f,pattern=[a],count=str(n))
            for f in (1,2) for n,a in I.MIDDLE]


def certify(p,keep,minimum,solution,groups=False,discovery=None):
    windows,targets,formal=geometry(p,keep)
    native=I.source_binding()
    data=json.loads(I.NATIVE.read_text())
    for provider in ('THREE-base','THREE-extra'):
        for direction in ('forward','backward'):
            actual=data['providers'][provider]['unsplit_replays'][direction]['paid_profile']
            E.need({int(r):int(n) for r,n in actual.items()}==dict(F.IDENTITY),
                   'The actual unsplit native profile is charged')
    case=F.verify(p,minimum,solution,'identity',fresh_groups=groups,
                  custom_windows=windows,custom_targets=targets)
    invoice=F.serialize(case,('0.001730970419199163702738','0.001745','0.002','0.0022',
                            '0.0023','0.0025','0.003','0.004'))
    invoice['root_bracket']=I.root_bracket(case['signed'])
    extra_sources=[Path(__file__),HERE/'mixed_forest_search.py',HERE/'mixed_target_probe.py',
                   HERE/'identity_mixed_certificate.py',HERE.parent/'bit/complex_controller_factor.py',
                   HERE.parent/'bit/mixed_productive_bit.py']
    sources={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in extra_sources}
    # Explicit negative controls exercise ownership and changed target credit.
    bad=[dict(row) for row in solution]
    bad[0]=dict(bad[0],count=str(Q(bad[0]['count'])+1))
    rejected=False
    try:
        F.verify(p,minimum,bad,'identity',fresh_groups=groups,custom_windows=windows,custom_targets=targets)
    except AssertionError:rejected=True
    E.need(rejected,'Duplicating one displayed owner is rejected')
    unsupported=dict(targets)
    first=min(unsupported)
    unsupported[first]-=1
    unsupported[first+1]=unsupported.get(first+1,0)+1
    rejected_rank=False
    try:
        F.verify(p,minimum,solution,'identity',fresh_groups=groups,
                 custom_windows=windows,custom_targets=unsupported)
    except AssertionError:rejected_rank=True
    E.need(rejected_rank,'A free extra target axis is rejected')
    return {'schema':'source-bound-Laurent-controller-mixed-tariff/1',
            'status':'PASS_EXACT_LAURENT_IDENTITY_LOCAL_SOURCE_BOUND_TARIFF',
            'source_sha256':sources,'native_source_sha256':native,
            'controller':formal,'invoice':invoice,'discovery':discovery,
            'controls':{'duplicate_owner_rejected':rejected,
                        'unearned_extra_target_axis_rejected':rejected_rank},
            'owned_storage':'Every simultaneous native call owns a center C0; none is credited as a productive output.',
            'not_proved':['The actual local native forward/backward maps satisfy this Laurent input contract in every global stage.',
                          'All displayed helper owners admit phase-correct global adapters in the retained windows.',
                          'All output monomials admit the stated legal free normalizations.',
                          'Finite precompilation, precision/stock induction, and the outer integer-multiplication transfer.'],
            'new_kappa':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--p',type=int,default=3)
    parser.add_argument('--keep',type=int,default=43)
    parser.add_argument('--minimum',type=int,default=6)
    parser.add_argument('--discover',action='store_true')
    parser.add_argument('--groups',action='store_true')
    parser.add_argument('--C',default='0.0023')
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'P3-CONTROLLER-TARIFF-CERTIFICATE.json')
    args=parser.parse_args()
    if args.replay:
        old=json.loads(args.replay.read_text())
        p,keep=old['controller']['pairs'],old['controller']['keep_idle_mask']
        minimum=old['invoice']['minimum_target_parameter']
        solution=old['invoice']['patterns'];groups=old['invoice']['fresh_groups']
        discovery={'replayed_receipt':str(args.replay),'receipt_sha256':sha256(args.replay.read_bytes()).hexdigest()}
    else:
        p,keep,minimum,groups=args.p,args.keep,args.minimum,args.groups
        windows,targets,_=geometry(p,keep)
        if args.discover:
            solution,discovery=F.discover(p,minimum,float(args.C),fresh_groups=groups,
                                          custom_windows=windows,custom_targets=targets)
        else:
            E.need((p,keep,minimum,groups)==(3,43,6,False),'The built-in integer construction is p3 keep43 K6')
            solution=simple_p3();discovery={'method':'Explicit integer pattern table'}
    out=certify(p,keep,minimum,solution,groups,discovery)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'root':out['invoice']['root_bracket'],
                      'targets':out['invoice']['targets'],'paid':out['invoice']['paid']},sort_keys=True))


if __name__=='__main__':main()
