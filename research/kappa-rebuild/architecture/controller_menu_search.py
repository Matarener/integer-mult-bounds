#!/usr/bin/env python3
"""Optimize finite helper packings for already enumerated Laurent controllers.

Floating LP discovers patterns; every emitted profile is reconstructed over
the rationals and checked independently. A displayed floating root is a
screening statistic, never an exact certificate or an outer kappa claim.
Use controller_tariff.py to produce a source-bound exact chosen receipt.
Apache-2.0; substantial OpenAI assistance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

sys.dont_write_bytecode=True
import mixed_forest_search as F
import mixed_target_probe as E

HERE=Path(__file__).resolve().parent


def floating_root(signed):
    lo,hi=0.0,.01
    for _ in range(65):
        mid=(lo+hi)/2
        if E.numerical_value(signed,mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=HERE/'sources/COMPLEX-CONTROLLER-FACTOR-p1-p5.json')
    parser.add_argument('--output',type=Path,default=HERE/'CONTROLLER-MENU-SEARCH.json')
    parser.add_argument('--min-p',type=int,default=4)
    parser.add_argument('--max-p',type=int,default=5)
    parser.add_argument('--minimums',default='6,9')
    parser.add_argument('--C',default='0.0024')
    parser.add_argument('--no-groups',action='store_true')
    args=parser.parse_args()
    data=json.loads(args.input.read_text())
    rows=[];failed=[]
    for formal in data['cases']:
        p=formal['pairs'];keep=formal['keep_idle_mask']
        if not(args.min_p<=p<=args.max_p):continue
        windows=[{'name':str(w['index'])+'_'+w['kind']+str(w['pair']),
                  'capacity':w['rank'],'stages':w['stages'],
                  'field_count':112 if 'field' in w else 224}
                 for w in formal['retained_idle_windows']]
        targets={int(r):int(n) for r,n in formal['endpoint_after_stated_free_Pauli_normalization'].items()}
        current=[]
        for minimum in map(int,args.minimums.split(',')):
            if minimum>min(targets):continue
            try:
                solution,discovery=F.discover(p,minimum,float(args.C),fresh_groups=not args.no_groups,
                                              custom_windows=windows,custom_targets=targets)
                case=F.verify(p,minimum,solution,'identity',fresh_groups=not args.no_groups,
                              custom_windows=windows,custom_targets=targets)
            except (AssertionError,ValueError) as error:
                failed.append({'p':p,'keep':keep,'minimum':minimum,'error':str(error)})
                continue
            record={k:v for k,v in case.items() if k!='signed'}
            record.update(keep=keep,discovery=discovery,
                          floating_root_for_discovery_only=floating_root(case['signed']),
                          discovery_margin_float=E.numerical_value(case['signed'],float(args.C)))
            current.append(record);rows.append(record)
        if current:
            best=max(current,key=lambda x:x['floating_root_for_discovery_only'])
            print(json.dumps({'p':p,'keep':keep,'best_minimum':best['minimum_target_parameter'],
                              'floating_root':best['floating_root_for_discovery_only'],
                              'lift':best['replica_lift']}),flush=True)
        out={'schema':'finite-Laurent-controller-tariff-screen/1',
             'status':'EXACT_FEASIBLE_PROFILES_FLOATING_OBJECTIVE_SCREEN',
             'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
             'forest_source_sha256':sha256((HERE/'mixed_forest_search.py').read_bytes()).hexdigest(),
             'input':str(args.input),'input_sha256':sha256(args.input.read_bytes()).hexdigest(),
             'C_discovery':args.C,'minimum_menu':args.minimums,'cases':rows,
             'failed_discoveries_not_waived':failed,'new_kappa':False}
        args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
