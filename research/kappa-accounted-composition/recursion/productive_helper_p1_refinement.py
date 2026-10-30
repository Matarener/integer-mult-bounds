#!/usr/bin/env python3
"""Exact certificate for a smaller p=1 residual invoice.

A numerical MILP proposed the integer pattern. This replay uses no optimizer
and does not assert an exact optimum over other allocations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import productive_helper_forest as B

ROWS=[(18,[5,5,5]),(1,[5,5,8]),(28,[5,9,9]),(54,[6,9,9]),(168,[7,9,9]),(139,[8,8,9])]

def construct():
    hosts=[]
    for count,row in ROWS:
        for shift in range(3):
            v=[row[(s+shift)%3] for s in range(3)]
            hosts.extend({'kind':'productive','capacity':25,'stages':[0,1,2],'widths':v} for _ in range(count))
    r=B.verify_case('p1_concentrated_residual',3,632,25,3,hosts,ROWS)
    assert r['residual_profile_per_controller']=={'1':'54','2':'28','7':'1','10':'18'}
    r['optimality_scope']='A scipy/HiGHS MILP discovery run reported an optimum at C=.004, but this certificate verifies only this exact integer pattern and complete invoice. It is not a rational optimality proof or a native owner emission.'
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    here=Path(__file__).resolve().parent
    r={'status':'PASS','sources':{name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in ['productive_helper_p1_refinement.py','productive_helper_forest.py','PRODUCTIVE-HELPER-FOREST.json']},'case':construct()}
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':r['status'],'name':r['case']['name']}))

if __name__=='__main__':
    main()
