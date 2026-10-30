# SPDX-License-Identifier: Apache-2.0
"""Independent exact radical/power checks and rejecting controls."""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import json,subprocess,sys,tempfile,shutil
from certificate import stencil,credit,certify,capped_sums,need
from oracle import gap_interval
from verify import result
ROOT=Path(__file__).resolve().parent

def reject(fn):
    try:fn()
    except ValueError:return
    raise RuntimeError('invalid input accepted')

def main():
    data=result();S=10**50;cases=0;refinements=0
    for order in range(2,9):
        for start in range(1,4):
            for step in (1,2):
                d=stencil(order,start,step)
                for power in range(order):
                    need(sum(v*r**power for r,v in d.items())==0,'lower polynomial moments')
                gap=F(0)
                for r,v in d.items():
                    z=isqrt(r*S*S);lo,hi=F(z,S),F(z+1,S)
                    gap+= -v*(hi if v>0 else lo)
                previous=F(0)
                for boxes in (1,2,4,8):
                    L=credit(order,start,step,F(1,2),F(1,2),boxes)
                    need(0<L<=gap,'independent exact sqrt lower bound')
                    need(L>=previous,'nested lower-grid refinement')
                    previous=L;refinements+=1
                cases+=1
    source={int(r):n for r,n in json.loads((ROOT/'inputs/current-profile.json').read_text()).items()}
    for row in data['examples']:
        move=row['moves'][0];n=move['order'];N=move['copies']
        size=max(source)+1;old=[source.get(r,0) for r in range(size)];new=list(old)
        for r,v in stencil(n).items():new[r]+=N*v
        for a in (F(17,10000),F(7,4000),F(18,10000)):
            lo,hi=gap_interval(old,new,a)
            need(lo>F(row['total_raw_credit'])>1,'independent actual paid-power sign')
        # A positive capped sum gives an explicit concave cost that gets worse.
        caps=capped_sums(stencil(n));k=next(k for k,c in caps.items() if c>0)
        need(sum(v*min(r,k) for r,v in stencil(n).items())>0,'outside the all-concave cone')
        over=row['largest_inventory_feasible_copies']+1
        reject(lambda:certify(source,73,[{'order':n,'start':1,'step':1,'copies':over}],F(17,10000),F(18,10000)))
        reject(lambda:certify(source,73,[{'order':n,'start':1,'step':1,'copies':N}],F(17,10000),F(18,10000),{1:2}))
    for n in (1,13,True):reject(lambda:stencil(n))
    reject(lambda:stencil(3,0,1));reject(lambda:stencil(3,1,0))
    reject(lambda:credit(3,1,1,F(0),F(1,2)))
    reject(lambda:credit(3,1,1,F(1,2),F(1)))
    reject(lambda:credit(3,1,1,F(3,4),F(1,4)))
    reject(lambda:credit(3,1,1,F(1,4),F(1,2),0))
    reject(lambda:certify(source,73,[],F(1,4),F(1,2)))
    reject(lambda:certify(source,73,[{'order':3,'start':1,'step':1,'copies':-1}],F(1,4),F(1,2)))
    reject(lambda:certify(source,73,[{'order':3,'start':71,'step':1,'copies':1}],F(1,4),F(1,2)))
    reject(lambda:certify(source,73,[{'order':3,'start':1,'step':1,'copies':1}],F(1,4),F(1,2),{0:1}))
    # Read-only exported CLI and proof-relevant input/result corruption controls.
    with tempfile.TemporaryDirectory() as temporary:
        copied=Path(temporary)/'package';shutil.copytree(ROOT,copied,ignore=shutil.ignore_patterns('__pycache__'))
        command=[sys.executable,'-B',str(copied/'verify.py')]
        need(subprocess.run(command,capture_output=True).returncode==0,'standalone positive CLI')
        target=copied/'inputs/current-profile.json';raw=target.read_bytes();target.write_bytes(raw+b' ')
        need(subprocess.run(command,capture_output=True).returncode!=0,'changed input accepted');target.write_bytes(raw)
        target=copied/'RESULT.json';value=json.loads(target.read_text());value['examples'][0]['net_raw_credit']='100'
        target.write_text(json.dumps(value),encoding='utf-8')
        need(subprocess.run(command,capture_output=True).returncode!=0,'false paid credit accepted')
    print('PASS_HIGHER_ORDER_CONTROLS',cases,'radical cases,',refinements,'grid bounds, 6 exact-power signs, inventory/overhead/domain and CLI controls')

if __name__=='__main__':main()
