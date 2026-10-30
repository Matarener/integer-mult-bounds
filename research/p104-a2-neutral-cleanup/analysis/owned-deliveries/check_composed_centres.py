"""Source-bound same-frame owned-delivery screen; zxv with OpenAI Codex assistance. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json
HERE=Path(__file__).resolve().parent
src=HERE.parents[1]/'WORD.json.gz'
w=json.loads(gzip.decompress(src.read_bytes()))
n=w['public']+w['owned_fields']; rows=[{i:Q(1)}for i in range(n)]
frames=w['initial']+[None]*w['owned_fields'];active=set();probed=set();copies=[];checks=[]
def add(a,b,q):
 for k,v in b.items():
  z=a.get(k,0)+q*v
  if z:a[k]=z
  else:a.pop(k,None)
def basis(vectors):
 out={}
 for row in vectors:
  row=dict(row)
  while row:
   p=min(row)
   if p not in out:
    q=row[p];out[p]={k:v/q for k,v in row.items()};break
   add(row,out[p],-row[p])
 return out
def residue(row,b):
 row=dict(row)
 while row:
  p=min(row)
  if p not in b:break
  add(row,b[p],-row[p])
 return row
for i,e in enumerate(w['program']):
 op,r=e[:2]
 if op=='INIT':rows[r]={};frames[r]=e[2];active.add(r);probed.discard(r)
 elif op=='CLEAR':rows[r]={};frames[r]=None;active.remove(r)
 elif op=='MOVE':frames[r]=e[3]
 else:
  q=Q(e[-2]);f=e[-1]
  if op=='SCALE':rows[r]={k:q*v for k,v in rows[r].items()}
  else:
   s=e[2]
   if s in active and s not in probed:
    avail=[j for j in range(w['public']) if frames[j]==f]
    b=basis(rows[j]for j in avail)
    rem=residue(rows[s],b)
    checks.append({'event':i,'owned':s,'frame':f,'dimension':len(w['frames'][f]),'available_public_rows':len(avail),'public_span_rank':len(b),'owned_value_support':len(rows[s]),'free_public_reconstructible':not rem,'nonzero_residual_support':len(rem)})
    probed.add(s)
   if op=='COPY':
    rows[r]={k:q*v for k,v in rows[s].items()}
    if r in active and r<751:copies.append({'event':i,'owned':r,'source':s,'row':dict(rows[r])})
   else:add(rows[r],rows[s],q)
for r,row in enumerate(rows):
 expected={r:Q(1)}if r<w['public']else{}
 if r-112 in w['live']:expected[r-112]=Q(1)
 if row!=expected:raise ValueError('Independent endpoint mismatch on row '+str(r))
if active or frames[:w['public']]!=w['final']:raise ValueError('Final chart/owned lifetime mismatch')
out={'all_endpoint_rows_checked':len(rows),'scope':'Exact scalar reference-coordinate necessity for replacing each first owned read by ordinary operations on public registers at the SAME literal frame; no new paid transports, ownership changes, or multi-frame/native maps are allowed. Not a global impossibility proof.','source_sha256':sha256(src.read_bytes()).hexdigest(),'checks':checks,'eight_centre_source_rank':len(basis(x['row']for x in copies)),'eight_centre_sources':[{'event':x['event'],'owned':x['owned'],'source':x['source'],'support':len(x['row'])}for x in copies]}
(HERE/'COMPOSED-CENTRE-RECONSTRUCTION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
