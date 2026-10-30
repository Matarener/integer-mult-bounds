#!/usr/bin/env python3
"""Independent441-type tariff audit for the fixed three-mark source-span floor."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
PINS={
 'research/p112-rational-decoder-gate/CANDIDATE.json':'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
TARGETS=[[0,67],[7,64],[1,75]]
GROUPS=[17,18,29,30,31,32]

def need(ok,message):
 if not ok:raise ValueError(message)

def main():
 pa=argparse.ArgumentParser(description=__doc__)
 pa.add_argument('--repo-root',type=Path,default=HERE.parents[1])
 pa.add_argument('--write-receipt',action='store_true')
 ar=pa.parse_args();objects=[]
 for path,digest in PINS.items():
  raw=(ar.repo_root/path).read_bytes()
  need(sha256(raw).hexdigest()==digest,'inputpin '+path);objects.append(json.loads(raw))
 c,d=objects;groups=c['groups'];labels={r['port']:r['q'] for r in d['recipes']}
 owner={p:g for g,ports in enumerate(groups) for p in ports}
 need(all(t in c['factor_supports'] for t in TARGETS),'canonical targets')
 need([owner[p] for t in TARGETS for p in t]==GROUPS,'fixed physical embedding')
 need(len(set(GROUPS))==6 and all(len(groups[g])==3 for g in GROUPS),'six distinct triads')
 spans=[];ann=[]
 for mask in range(64):
  generators=[labels[p] for i,g in enumerate(GROUPS) if mask>>i&1 for p in groups[g]]
  space={0}
  for v in generators:space|={w^v for w in tuple(space)}
  spans.append(sum(1<<v for v in space))
  ann.append(sum(1<<v for v in range(512) if all((v&w).bit_count()%2==0 for w in generators)))
 def dim(space):
  size=space.bit_count();need(size>0 and size&(size-1)==0,'subspace cardinality')
  return size.bit_length()-1
 rows=[]
 for sigma in range(1,8):
  source=sum(3<<(2*j) for j in range(3) if sigma>>j&1)
  for reader in range(1,64):
   cost=dim(spans[reader])-dim(spans[reader]&ann[source])
   rows.append([sigma,reader,cost])
 need(len(rows)==441,'complete441types')
 hist=Counter(cost for sigma,reader,cost in rows)
 cheap2=[[sigma,reader] for sigma,reader,cost in rows if cost==2]
 cheap3=[[sigma,reader] for sigma,reader,cost in rows if cost==3]
 need(min(hist)==2,'nonzero tariff floor2')
 need(cheap2==[[2,32]],'unique2costtype b to c-right')
 need(len(cheap3)==41 and all(reader.bit_count()==1 for sigma,reader in cheap3),'all41cost3types have singleton readers')
 need(all(cost>=4 for sigma,reader,cost in rows if reader.bit_count()>=2),'multiple-reader tariff floor4')
 need(all(sigma==2 for sigma,reader in cheap2),'only one axial query ray can cost2')
 canonical=[next(cost for sigma,reader,cost in rows if sigma==1<<j and reader==3<<(2*j)) for j in range(3)]
 need(canonical==[6,6,6],'canonical equality18')
 # Coefficient-independent obstruction: sole query on b at c-right cannot
 # span the marked c axis. This checks the support labels, not a sample value.
 sigma,reader=cheap2[0]
 reader_target=(reader.bit_length()-1)//2
 need(sigma!=(1<<reader_target),'uniquecheap2term mismatches its target axis')
 result={'status':'PASS_INDEPENDENT_FIXED_SOURCE_SPAN_TARIFF_SCREEN',
 'scientific_inputs':PINS,'targets':TARGETS,'physical_groups':GROUPS,
 'complete_nonzero_types':len(rows),'cost_histogram':dict(sorted(hist.items())),
 'cost2_types':cheap2,'cost3_types':cheap3,'all_cost3_readers_singleton':True,
 'multiple_reader_minimum':min(cost for sigma,reader,cost in rows if reader.bit_count()>=2),
 'canonical_term_costs':canonical,'ordered441rows_sha256':sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
 'method':'Exact binary span sets and annihilator intersections; no producer imports or Gram elimination',
 'scope':'Finite441type tariff facts; normalized arbitrary-term proof is written; <=5branch uses retained theorem'}
 payload=json.dumps(result,indent=2)+'\n';dest=HERE/'INDEPENDENT-FIXED-SOURCE-SPAN-RESULT.json'
 if ar.write_receipt:dest.write_text(payload,encoding='utf-8',newline='\n')
 else:need(dest.read_text(encoding='utf-8')==payload,'immutable receipt mismatch')
 print(json.dumps({k:result[k] for k in ['status','complete_nonzero_types','cost_histogram','cost2_types','multiple_reader_minimum','canonical_term_costs']}))
if __name__=='__main__':main()
