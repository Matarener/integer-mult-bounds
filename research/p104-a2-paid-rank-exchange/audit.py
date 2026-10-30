"""Independent scoped audit of the proposed P104 A2 paid exchange.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
The transport agent supplies the construction; all source P104 credit remains.
This checks the exact local rewrite and invoice, not the full inherited theorem.
"""
from fractions import Fraction as Q
from collections import Counter
from pathlib import Path
from hashlib import sha256
import gzip,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'inputs/pr5627-WORD.json.gz'
CANDIDATE=HERE/'WORD.json.gz'
def need(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def add(row,other,q):
 for k,v in other.items():
  z=row.get(k,0)+q*v
  if z:row[k]=z
  else:row.pop(k,None)
def matrix(events):
 rows={r:{r:Q(1)} for r in (340,388,715)}
 for e in events:add(rows[e[1]],rows[e[2]],Q(e[-2]))
 return rows
def span(b):
 s={0}
 for v in b:s|={x^v for x in tuple(s)}
 return s
w,v=read(SOURCE),read(CANDIDATE)
old=[['ADD',388,715,'-4',825],['ADD',340,388,'1',825]]
new=[['ADD',340,715,'-4',396],['ADD',340,388,'1',825],['ADD',388,715,'-4',127]]
a=[e for e in w['program'] if e[0]!='MOVE'];b=[e for e in v['program'] if e[0]!='MOVE'];matches=[i for i in range(len(a)-1) if a[i:i+2]==old]
need(len(matches)==1,'Unique adjacent scalar motif');k=matches[0]
need(b==a[:k]+new+a[k+2:],'Only the exact three-register scalar rewrite')
need(matrix(old)==matrix(new),'All three arbitrary-input columns')
need(all(w[k]==v[k] for k in ('public','owned_fields','initial','final','ports','live','frames')),'Every boundary and physical inventory retained')
chain=[598,396,825,127]
need(all(span(w['frames'][a])<span(w['frames'][b]) for a,b in zip(chain,chain[1:])),'Strict nested retimed source chain')
need([len(w['frames'][x]) for x in chain]==[1,3,6,9],'Exact source itinerary dimensions')
def price(word):
 return Counter(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]])) for e in word['program'] if e[0]=='MOVE')
d=price(v);d.subtract(price(w));delta={r:c for r,c in d.items() if c}
need(delta=={2:1,3:-1,5:-1,6:1},'Complete paid H3+H5 to H2+H6 exchange')
need([e for e in a if e[0]in('COPY','INIT','CLEAR')]==[e for e in b if e[0]in('COPY','INIT','CLEAR')],'No changed owned erasure or copy contract')
controls={}
for name,bad in [('omitted_direct_shear',new[1:]),('omitted_last_shear',new[:-1]),('wrong_direct_sign',[['ADD',340,715,'4',396]]+new[1:])]:
 controls[name]=matrix(old)!=matrix(bad);need(controls[name],'Control rejects '+name)
result={'status':'PASS_INDEPENDENT_A2_IDENTITY_AND_PRICE_AUDIT','source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),'candidate_sha256':sha256(CANDIDATE.read_bytes()).hexdigest(),'old_gates':old,'new_gates':new,'old_itinerary_dimensions':[1,6,9],'new_itinerary_dimensions':[1,3,9],'paid_delta':delta,'controls':controls,'scope':'Exact three-column scalar identity; only scalar motif replacement; unchanged physical boundaries/owned instructions; strict source frame chain; complete paid-profile delta. Native, physical caller and outer replays supplied separately by root.'}
expected=json.loads((HERE/'INDEPENDENT-AUDIT.json').read_bytes())
need(json.loads(json.dumps(result))==expected,'Exact saved independent receipt');print(result['status'])
