"""Independent chronological checks of each saved nontrivial boundary pair.
Prepared for zxv with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json,sys
def need(ok,why):
 if not ok:raise ValueError(why)
HERE=Path(__file__).resolve().parent
word=Path(sys.argv[1]);w=json.loads(gzip.decompress(word.read_bytes()))
p=json.loads((HERE/'ALL-EVENT-CUT-SCREEN.json').read_bytes())
need(sha256(word.read_bytes()).hexdigest()==p['source_word_sha256'],'Independent boundary receipt check')
need(p['all_snapshots']==p['bounded_snapshots']==sum(p['dimension_counts'].values()),'Independent boundary receipt check')
need(not p['hits'],'Independent boundary receipt check')
def add(row,k,v):
 z=row.get(k,0)+v
 if z:row[k]=z
 else:row.pop(k,None)
def vector(d):return {int(k):Q(v) for k,v in d.items()}
def prefix(a,cut):
 out=a.copy()
 for e in reversed(w['program'][:cut+1]):
  op,r=e[:2]
  if op in ('INIT','CLEAR'):out.pop(r,None)
  elif op=='SCALE':
   if r in out:out[r]*=Q(e[-2])
  elif op in ('ADD','COPY'):
   add(out,e[2],Q(e[-2])*out.get(r,0))
   if op=='COPY':out.pop(r,None)
 return out
def suffix(b,cut):
 out=b.copy()
 for e in w['program'][cut+1:]:
  op,r=e[:2]
  if op in ('INIT','CLEAR'):out.pop(r,None)
  elif op=='SCALE':
   if r in out:out[r]*=Q(e[-2])
  elif op in ('ADD','COPY'):
   val=Q(e[-2])*out.get(e[2],0)
   if op=='COPY':out.pop(r,None)
   add(out,r,val)
 return out
checks=0
for state in p['reports']:
 cut=state['cut_after'];A=[(vector(a),vector(c)) for a,c in state['A']];B=[(vector(b),vector(d)) for b,d in state['B']]
 need(A and B and state['prefix_dimension']==state['suffix_dimension']==1,'Independent boundary receipt check')
 for a,c in A:
  need(prefix(a,cut)==c,'Independent boundary receipt check')
  need(set(c)<=set(p['group']),'Independent boundary receipt check')
 for b,d in B:
  need(suffix(b,cut)==d,'Independent boundary receipt check')
  need(set(d)<=set(p['group']),'Independent boundary receipt check')
 for a,c in A:
  for b,d in B:
   need(sum(q*d.get(r,0) for r,q in c.items())==0,'Independent boundary receipt check')
 checks+=1
need(checks==18,'Independent boundary receipt check')
print('PASS_INDEPENDENT_18_BOUNDARY_PAIRINGS_AND_COMPLETE_SNAPSHOT_COUNTS')
