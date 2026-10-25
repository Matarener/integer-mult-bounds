# SPDX-License-Identifier: Apache-2.0
"""Independent exact square-root/series oracles and semantic rejecting controls."""
from fractions import Fraction as F
from math import isqrt
from itertools import product
from pathlib import Path
import json, tempfile, shutil, subprocess, sys
from certificate import budget,admissible,need
from verify import result
ROOT=Path(__file__).resolve().parent

def reject(fn):
    try: fn()
    except ValueError: return
    raise RuntimeError('invalid certificate accepted')

def log_interval(n):
    k=0
    while n >= 2**(k+1): k+=1
    def unit(a,b):
        t=F(a-b,a+b);N=48
        s=2*sum((t**(2*j+1)/F(2*j+1) for j in range(N)),F(0))
        return s,s+2*t**(2*N+1)/(F(2*N+1)*(1-t*t))
    lo,hi=unit(n,2**k);l2,u2=unit(2,1)
    return lo+k*l2,hi+k*u2

def raw_power_interval(r,a):
    if r==0:return F(0),F(0)
    lo,hi=log_interval(r);lo*=a;hi*=a
    need(0<=lo<=hi<F(1,2),'oracle small argument')
    def alt(x,N):
        term=F(1);s=term
        for j in range(1,N+1):term*= -x/j;s+=term
        return s
    return r*alt(hi,25),r*alt(lo,26)

def gap_interval(old,new,a):
    lo=hi=F(0)
    for r,(o,n) in enumerate(zip(old,new)):
        l,u=raw_power_interval(r,a);d=o-n
        lo+=d*(l if d>=0 else u);hi+=d*(u if d>=0 else l)
    return lo,hi

def main():
    data=result()
    for row in data['axes']:
        h=row['h'];a,b=[json.loads((ROOT/'inputs'/f'pair-{k}-{h}-receipt.json').read_text())['profile']['blocks'] for k in ('original','ranked')]
        for saving in (F(17,10000),F(7,4000),F(18,10000)):
            lo,hi=gap_interval(a,b,saving)
            need(lo>F(row['rank_one_credit']),'independent raw-power lower bound')
        reject(lambda:admissible(a,b,F(17,10000),F(18,10000),{1:row['maximum_strict_integer_charge']+1}))
        reject(lambda:budget(b,a,F(17,10000),F(18,10000)))
        altered=list(b);altered[1]+=1
        reject(lambda:budget(a,altered,F(17,10000),F(18,10000)))
    # Independently price the exact current full-profile target at three savings.
    current=json.loads((ROOT/'inputs/staged544-profile.json').read_text(encoding='utf-8'))
    a=[current.get(str(r),0) for r in range(49)];b=list(a)
    b[1]+=1775;b[2]-=3550;b[3]+=1775
    for saving in (F(17,10000),F(7,4000),F(18,10000)):
        lo,hi=gap_interval(a,b,saving)
        need(lo>F(data['current_staged_pricing_target']['rank_one_credit']),
             'current-profile independent raw-power lower bound')
    # Exhaustive small equal-mass profiles: exact radical enclosures at a=1/2.
    profiles=[[0,*v] for v in product(range(3),repeat=4)]
    checked=0
    for old in profiles:
        for new in profiles:
            if sum(r*n for r,n in enumerate(old))!=sum(r*n for r,n in enumerate(new)):continue
            try:c=budget(old,new,F(1,2),F(1,2))
            except ValueError:continue
            S=10**24;gap=F(0)
            for r,(o,n) in enumerate(zip(old,new)):
                z=isqrt(r*S*S);l,u=F(z,S),F(z+1,S);d=o-n
                gap+=d*(l if d>=0 else u)
            need(gap+F(100,S)>=F(c['rank_one_credit']),'independent radical enclosure')
            # Check the entire linear decomposition at a non-power concave function.
            f=[F(0),F(7),F(12),F(16),F(19)]
            left=sum((n-o)*f[r] for r,(o,n) in enumerate(zip(old,new)))
            right=sum(c['caps'][k]*(2*f[k]-f[k-1]-f[k+1]) for k in range(1,4))
            need(left==right,'independent min-basis exact identity')
            checked+=1
    old=[0,0,2,0,0];new=[0,1,0,1,0]
    for lo,hi in [(F(0),F(1,2)),(F(1,2),F(1)),(F(3,4),F(1,2))]:reject(lambda:budget(old,new,lo,hi))
    reject(lambda:admissible(old,new,F(1,4),F(1,2),{0:1}))
    reject(lambda:budget([0,True,0],[0,0,0],F(1,4),F(1,2)))
    # Actual standalone CLI must reject altered immutable input and result bytes.
    with tempfile.TemporaryDirectory() as temporary:
        copied=Path(temporary)/'package'
        shutil.copytree(ROOT,copied,ignore=shutil.ignore_patterns('__pycache__'))
        command=[sys.executable,'-B',str(copied/'verify.py')]
        need(subprocess.run(command,capture_output=True).returncode==0,'export positive control')
        target=copied/'inputs/pair-ranked-23-receipt.json'
        original=target.read_bytes();target.write_bytes(original+b' ')
        need(subprocess.run(command,capture_output=True).returncode!=0,'source-byte tamper accepted')
        target.write_bytes(original)
        target=copied/'RESULT.json';original=target.read_bytes()
        value=json.loads(original);value['axes'][0]['pays_rank_one_children']+=1
        target.write_text(json.dumps(value),encoding='utf-8')
        need(subprocess.run(command,capture_output=True).returncode!=0,'result tamper accepted')
    print('PASS_CHARGED_CONTROLS' ,checked,'exhaustive profile pairs; 9 interval signs; malformed, reversed, mass and unpaid-overhead controls')
if __name__=='__main__':main()
