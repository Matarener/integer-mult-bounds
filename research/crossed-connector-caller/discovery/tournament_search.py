"""Test the projected chronology equations without connector matrices.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json,itertools
from pathlib import Path
import free_algebra as F,gap_search as G
MODE='rows';SPLITS=2

def equations(g,order):
 m=SPLITS;names=[];aa=[];eq=[]
 for j in range(g):
  row=[];last=F.ONE
  for h in range(m-1):row.append(F.var(len(names)));names.append(f'A{j}_{h}');last^=row[-1]
  row.append(last);aa.append(row)
  for h,k in itertools.product(range(m),repeat=2):
   v=F.prod(row[h],row[k])^(row[h] if h==k else F.ZERO)
   if v:eq.append((f'A{j}:{h},{k}',v))
 s={}
 for j,k in itertools.permutations(range(g),2):
  v=F.ZERO
  for i,(c,h) in enumerate(order):
   if c!=j:continue
   for d,l in order[i+1:]:
    if d==k:v^=F.prod(aa[j][h],aa[k][l])
  s[j,k]=v
 for j in range(g):
  k,l=[i for i in range(g) if i!=j]
  if MODE in ('rows','both'):eq.append((f'row {j}',s[j,k]^s[j,l]))
  if MODE in ('cols','both'):eq.append((f'col {j}',s[k,j]^s[l,j]))
 return names,eq

def main():
 global MODE
 F.equations=equations;out={}
 for MODE in ('rows','cols','both'):
  records=[]
  for o in G.orders():
   r=F.certificate(3,o,4);records.append(r)
  print(MODE,len(records),sum('one' in r['certificates'] for r in records),flush=True);out[MODE]=records
 Path(__file__).with_name('TOURNAMENT-SEARCH.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
