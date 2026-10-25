#!/usr/bin/env python3
"""Fixed three-mark canonical-source floor: all441 support tariffs."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse,json
HERE=Path(__file__).resolve().parent
PINS={'research/p112-rational-decoder-gate/CANDIDATE.json':'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b','research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}
TARGETS=[[0,67],[7,64],[1,75]]
GROUPS=[17,18,29,30,31,32]
def need(b,m):
 if not b:raise ValueError(m)
def rank(vs):
 pivots={}
 for v in vs:
  while v:
   j=v.bit_length()-1
   if j in pivots:v^=pivots[j]
   else:pivots[j]=v;break
 return len(pivots)
def main():
 pa=argparse.ArgumentParser();pa.add_argument('--repo-root',type=Path,default=HERE.parents[1]);pa.add_argument('--write-receipt',action='store_true');args=pa.parse_args()
 objs=[]
 for path,h in PINS.items():
  raw=(args.repo_root/path).read_bytes();need(sha256(raw).hexdigest()==h,'inputhash');objs.append(json.loads(raw))
 c,d=objs;owner={p:i for i,g in enumerate(c['groups'])for p in g};v={r['port']:r['q']for r in d['recipes']}
 need(all(t in c['factor_supports']for t in TARGETS),'canonicalmarks')
 need([owner[p]for t in TARGETS for p in t]==GROUPS,'sixdistinctphysicalgroups')
 groups=[c['groups'][i]for i in GROUPS]
 need(all(len(g)==3 for g in groups),'ordinarytriads')
 need(len({p for g in groups for p in g})==18,'disjointphysicalgroups')
 for j in range(3):
  ps=groups[2*j]+groups[2*j+1]
  need(all((v[p]&v[q]).bit_count()%2==int(p==q)for p in ps for q in ps),'pairedroleorthonormality')
 def price(s,t):
  ps=[p for j in range(3)if s>>j&1 for g in groups[2*j:2*j+2]for p in g]
  qs=[p for j,g in enumerate(groups)if t>>j&1 for p in g]
  return rank(sum(((v[p]&v[q]).bit_count()%2)<<k for k,q in enumerate(qs))for p in ps)
 rows=[[s,t,price(s,t)]for s in range(1,8)for t in range(1,64)]
 low=[row for row in rows if row[2]<3]
 need(low==[[2,32,2]],'uniqueprice2type')
 need(all(t.bit_count()==1 for s,t,b in rows if b<=3),'allcheapreadersaresingletons')
 need(sum(b==3 for s,t,b in rows)==41,'41price3types')
 need(min(b for s,t,b in rows if t.bit_count()>=2)==4,'multiple-readerfloor4')
 # Check all physical masks directly, including fixed-source subadditivity
 # used to merge parallel axial terms; union can cancel only by shrinking.
 for s in [1,2,4]:
  for t in range(64):
   for u in range(64):need(price(s,t|u)<=price(s,t)+price(s,u),'axialmergeranksubadditivity')
 baseline=[price(1<<j,3<<(2*j))for j in range(3)]
 need(baseline==[6,6,6],'canonicalbaseline')
 out={'status':'PASS_FIXED_THREE_MARK_CANONICAL_SOURCE_GEOMETRY','inputs':PINS,'targets':TARGETS,'physical_groups':GROUPS,'coefficient_support_count':7,'reader_support_count':63,'support_types':441,'tariff_histogram':dict(sorted(Counter(b for s,t,b in rows).items())),'only_cost_below3':low,'all_cost_at_most3_have_single_reader':True,'minimum_two_or_more_readers':4,'axial_subadditivity_checks':3*64*64,'canonical_term_costs':baseline,'table_sha256':sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),'proof_scope':'After readerrestriction and axialmerge, everycost<=17factorization has atmost5terms; priorfive-termtheorem is a separate cited premise for universal18floor'}
 payload=json.dumps(out,indent=2)+'\n';p=HERE/'fixed-three-mark-source-span.json'
 if args.write_receipt:p.write_text(payload,encoding='utf-8',newline='\n')
 else:need(p.read_text(encoding='utf-8')==payload,'receiptmatch')
 print(json.dumps(out))
if __name__=='__main__':main()
