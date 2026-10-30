"""Independent audit of the common scalar skeleton and typed frame lowering.

Prepared for zxv with substantial OpenAI Codex assistance; Apache-2.0.
This is a scoped composition audit, not independent human or kernel review.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,json
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def need(ok,why):
 if not ok:raise ValueError(why)
def scalar(w):return[e for e in w['program']if e[0]!='MOVE']
def span(b):
 s={0}
 for v in b:s|={x^v for x in tuple(s)}
 return s
source=read(HERE/'inputs/pr5643/inputs/pr5627-WORD.json.gz')
a2=read(HERE/'inputs/pr5643/WORD.json.gz')
cleanup=read(HERE/'inputs/pr5644/WORD.json.gz')
composed=read(HERE/'WORD.json.gz')
old=[['ADD',388,715,'-4',825],['ADD',340,388,'1',825]]
new=[['ADD',340,715,'-4',396],['ADD',340,388,'1',825],['ADD',388,715,'-4',127]]
def replace(w):
 seq=scalar(w);hits=[i for i in range(len(seq)-1)if seq[i:i+2]==old]
 need(len(hits)==1,'One source A2 motif survives cleanup');i=hits[0]
 return seq[:i]+new+seq[i+2:]
need(scalar(a2)==replace(source),'Exact original A2 scalar replacement')
need(scalar(composed)==replace(cleanup),'Common scalar skeleton equals A2 applied after cleanup')
# Reconstruct typed monotone paths independently from this common skeleton.
frames=[span(b)for b in cleanup['frames']]
current=cleanup['initial']+[None]*cleanup['owned_fields'];active=set();events=[]
def move(r,f):
 a=current[r]
 if a==f:return
 need(a is not None and (frames[f]<frames[a]if r in active else frames[a]<frames[f]),'Legal strict nested chart path')
 events.append(['MOVE',r,a,f,r in active]);current[r]=f
for e in replace(cleanup):
 op,r=e[:2]
 if op=='INIT':
  need(current[r]is None,'Fresh owned role');active.add(r);current[r]=e[2]
 elif op=='CLEAR':
  move(r,e[2]);active.remove(r);current[r]=None
 else:
  move(r,e[-1])
  if op!='SCALE':move(e[2],e[-1])
 events.append(e)
for r,f in enumerate(cleanup['final']):move(r,f)
need(events==composed['program'],'Reverse construction order gives identical chronological native/scalar word')
need(all(composed[k]==source[k]for k in ('initial','final','frames','ports','live','public','owned_fields')),'All physical boundary data unchanged')
def matrix(seq):
 rows={r:{r:Q(1)}for r in (340,388,715)}
 for e in seq:
  dst,src,q=e[1],e[2],Q(e[-2])
  for j,x in rows[src].items():
   z=rows[dst].get(j,0)+q*x
   if z:rows[dst][j]=z
   else:rows[dst].pop(j,None)
 return rows
need(matrix(old)==matrix(new),'A2 acts identically on every possible prefix triple')
def paid(w):return Counter(abs(len(w['frames'][e[3]])-len(w['frames'][e[2]]))for e in w['program']if e[0]=='MOVE')
def delta(a,b):
 d=paid(a);d.subtract(paid(b));return{r:n for r,n in d.items()if n}
need(delta(composed,cleanup)=={2:1,3:-1,5:-1,6:1},'Exact full A2 paid delta after cleanup')
need(delta(composed,a2)=={1:-3,5:-3,6:3},'Exact full cleanup paid delta after A2')
# Incorrectly replacing the old pair by only its first two proposed gates fails
# for arbitrary values even when all helper-cleanup identities are retained.
need(matrix(old)!=matrix(new[:-1]),'Missing final shear fails the composed functional identity')
result={'status':'PASS_INDEPENDENT_COMPOSITION_ORDER_AND_FRAME_AUDIT','candidate_events':len(events),'scalar_events':len(scalar(composed)),'commuting_edit_scope':'After all three cleanup replacements, the unique original A2 motif remains; replacing it and independently reconstructing all typed monotone paths gives the identical complete emitted program.','delta_vs_pr5644':delta(composed,cleanup),'delta_vs_pr5643':delta(composed,a2),'scope':'Exact common scalar skeleton, three-column A2 identity for arbitrary prefix values, reverse-order full chart-path reconstruction, fixed physical boundary data and complete paid histogram. Native phases and caller/compiler evidence remain separate.'}
print(json.dumps(result,sort_keys=True,indent=2))
