"""Exact dual screening and finite profile brackets, not outer admission."""
from pathlib import Path
from fractions import Fraction as Q
import json,math
from itertools import product
from collections import defaultdict
from sources import rational_price as R
P=Path(__file__).parent
K=Q('0.001730096363528623534230')
def bracket(profile,lo,hi):
 signed=profile.copy();signed[73]=-896*360
 assert R.interval(signed,Q(lo))[1]<0<R.interval(signed,Q(hi))[0]
 return [lo,hi]
def dual_check():
 c=json.loads((P/'sources/PR3633-ceiling-CEILING.json').read_text())
 widths=c['widths'];caps=c['capacities'];duals=[{int(r):Q(n) for r,n in row.items()} for row in c['dual_by_constraint']]
 patterns=tight=0;minimum=None;cache={}
 for cap in caps:
  for q in product(*(range(cap//w+1) for w in widths)):
   idle=cap-sum(w*n for w,n in zip(widths,q))
   if idle<0:continue
   patterns+=1;co=defaultdict(Q)
   if idle:co[idle]+=1
   col=[int(cap==x) for x in caps]+list(q)
   for n,row in zip(col,duals):
    for r,v in row.items():co[r]-=n*v
   co={r:v for r,v in co.items() if v}
   if not co:tight+=1;continue
   den=math.lcm(*(v.denominator for v in co.values()));key=tuple(sorted((r,int(v*den)) for r,v in co.items()))
   if key not in cache:cache[key]=R.interval(dict(key),K)
   low=cache[key][0]/den;assert low>0
   minimum=low if minimum is None else min(low,minimum)
 assert (patterns,tight)==(2551,12)
 return dict(patterns=patterns,symbolic_tight=tight,minimum_strict_lower=R.compact((minimum,minimum))['lower'],scope='Old capacity and pattern alphabet, evaluated at stated K; not a dual for arbitrary changed widths.')
def main():
 # Per-call unchanged-inventory LP sensitivity: no capacity RHS delta.
 delta={1:-2,2:-2,3:2};assert sum(r*n for r,n in delta.items())==0
 change=R.interval(delta,K);assert change[1]<0
 # Prior PR3605 calibration, times20 to keep integer coefficients.
 shadow=R.interval({5:-5,48:1,3:-1},K)
 old=R.interval({1:60,2:20,3:-41,5:-5,48:1},K) #10*(6H1+2H2-4H3 +2shadow/20)
 assert old[1]<0
 h={int(r):n for r,n in json.loads((P/'sources/T360-PRICE.json').read_text())['profile'].items()}
 for r,n in delta.items():h[r]+=9*360*n
 out=dict(dual=dual_check(),status='PASS_EXACT_LOCAL_AND_FIXED_ALLOCATION_PRICE',k=str(K),local_delta=R.compact(change),width8_to7_shadow_times20=R.compact(shadow),prior_staged_net_times10=R.compact(old),profile=h,root_interval=bracket(h,'0.001730418899766071163804','0.001730418899766071163805'),scope='Exact finite paid profile using unchanged T360 idle and private stock. No native, physical ordinary/outer admission follows from these inequalities.')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
