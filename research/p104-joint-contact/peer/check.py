"""Independent exact scalar/frame audit; no import from the constructor/checkers."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
import argparse,gzip,json
ROOT=Path(__file__).resolve().parent
PINS={'SOURCE-WORD.json.gz':'a1e416add9d2bb44fce923111ebc50513e5d845e56aabe214f2f0bc7d5f2b45d','CANDIDATE-WORD.json.gz':'535106a3caee2bc849b5d14438282ee211bafd31fc3d28e10137647673bbd15c'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(name):
 raw=(ROOT/'inputs'/name).read_bytes()
 if name in PINS:need(sha256(raw).hexdigest()==PINS[name],name+' byte pin')
 return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
def span(b):
 s={0}
 for v in b:
  need(type(v) is int and 0<v<512 and v not in s,'independent frame')
  s|={x^v for x in tuple(s)}
 return frozenset(s)
def scalar(e):return e[:-1]
def trailing(n):return (abs(n)&-abs(n)).bit_length()-1
def normalize(row,exp):
 if not row:return {},0
 t=min(trailing(v) for v in row.values())
 if t:
  row={k:v>>t for k,v in row.items()};exp-=t
 if exp<0:row={k:v<<(-exp) for k,v in row.items()};exp=0
 return row,exp
def audit(w):
 spaces=[span(b) for b in w['frames']];dims=[len(b) for b in w['frames']]
 n=len(w['initial'])+8;need(n==743 and w['public']==735,'input dimensions')
 rows=[{r:1} for r in range(n)];exp=[0]*n;cur=w['initial'][:]+[None]*8
 owned=set();peak=0;lifetimes=0;paid=Counter();scalar_count=Counter();snapshots=[]
 for i,e in enumerate(w['program']):
  op,r=e[:2];need(0<=r<n,'role')
  if op=='MOVE':
   _,r,a,b,private=e
   need(cur[r]==a and private==(r in owned),'MOVE entry and ownership')
   need(spaces[b]<spaces[a] if private else spaces[a]<spaces[b],'strict nested MOVE')
   paid[abs(dims[a]-dims[b])]+=1;cur[r]=b
  elif op=='INIT':
   need(r>=735 and r not in owned,'owned init');owned.add(r);peak=max(peak,len(owned));lifetimes+=1
   rows[r]={};exp[r]=0;cur[r]=e[2]
  elif op=='CLEAR':
   need(r in owned and cur[r]==e[2],'owned clear');owned.remove(r);rows[r]={};exp[r]=0;cur[r]=None
  else:
   q=Fraction(e[-2]);f=e[-1]
   need(q and cur[r]==f,'destination chart')
   qe=q.denominator.bit_length()-1;need(q.denominator==1<<qe,'dyadic')
   if op=='SCALE':
    rows[r],exp[r]=normalize({k:q.numerator*v for k,v in rows[r].items()},exp[r]+qe)
   else:
    need(op in ('ADD','COPY'),'opcode');s=e[2]
    need(s!=r and 0<=s<n and cur[s]==f,'source chart')
    if op=='COPY':
     need(r in owned and not rows[r],'owned COPY zero destination')
     rows[r],exp[r]=normalize({k:q.numerator*v for k,v in rows[s].items()},exp[s]+qe)
    else:
     lev=max(exp[r],exp[s]+qe);a=1<<(lev-exp[r]);b=q.numerator<<(lev-exp[s]-qe)
     out={k:a*v for k,v in rows[r].items()}
     for k,v in rows[s].items():
      v=out.get(k,0)+b*v
      if v:out[k]=v
      else:out.pop(k,None)
     rows[r],exp[r]=normalize(out,lev)
  scalar_count[op]+=1
 need(not owned and cur[:735]==w['final'] and cur[735:]==[None]*8,'all exit charts and ownership')
 live=set(w['live']);need(len(live)==104,'104 productive ports')
 for r in range(n):
  expected={r:1} if r<735 else {}
  if r-112 in live:expected[r-112]=1
  need(exp[r]==0 and rows[r]==expected,'exact endpoint row '+str(r))
 main=live|{r+112 for r in live}
 helpers=Counter(dims[w['final'][r]]-dims[w['initial'][r]] for r in range(735) if r not in main)
 need(min(helpers)>0 and sum(helpers.values())==527,'all productive helper inputs')
 digest=sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return dict(paid=dict(sorted(paid.items())),helpers=dict(sorted(helpers.items())),owned_peak=peak,owned_lifetimes=lifetimes,endpoint_rows=n,endpoint_scalar_entries=n*n,endpoint_digest=digest,opcodes=dict(sorted(scalar_count.items())))
def histories(w,roles):
 out={r:[] for r in roles};ordinal=0
 for i,e in enumerate(w['program']):
  if e[0]=='MOVE':
   if e[1] in out:out[e[1]].append(dict(event=i,before_scalar=ordinal,source=e[2],target=e[3],rank=abs(len(w['frames'][e[3]])-len(w['frames'][e[2]])),private=e[4]))
  else:ordinal+=1
 return out
def calculate():
 s=read('SOURCE-WORD.json.gz');w=read('CANDIDATE-WORD.json.gz');c=read('CANDIDATE.json')
 need(set(s)==set(w),'schema fields')
 for k in s:
  if k!='program':need(s[k]==w[k],'fixed boundary '+k)
 old=[(i,e) for i,e in enumerate(s['program']) if e[0]!='MOVE'];new=[(i,e) for i,e in enumerate(w['program']) if e[0]!='MOVE']
 need([scalar(e) for i,e in old]==[scalar(e) for i,e in new],'all scalar and owned operations in exact chronological order')
 changes=[]
 for ordinal,((oi,oe),(ni,ne)) in enumerate(zip(old,new)):
  if oe!=ne:changes.append(dict(scalar_ordinal=ordinal,source_event=oi,candidate_event=ni,before=oe,after=ne))
 add_changes=[x for x in changes if x['before'][0]=='ADD']
 need(len(add_changes)==6 and {x['source_event'] for x in add_changes}=={10461,10462,13970,15479,15639,15640},'exact six ADD chart edits')
 need(len(changes)==21 and sum(x['before'][0]=='SCALE' for x in changes)==15,'fifteen additional SCALE chart retimings')
 roles=sorted({r for x in changes for r in (x['before'][1:3] if x['before'][0]=='ADD' else x['before'][1:2])})
 a=audit(s);b=audit(w);need(a['helpers']==b['helpers'] and a['endpoint_digest']==b['endpoint_digest'],'same productive operator')
 delta=Counter(b['paid']);delta.subtract(a['paid']);delta={k:v for k,v in sorted(delta.items()) if v}
 need(delta=={1:2,2:-3,3:1,4:-1,5:1},'literal paid histogram delta')
 # Real mutants exercise typing, scalar coefficient, and overwrite/clear lifecycle.
 from copy import deepcopy
 mutants=[]
 for name,which,update in [('wrong_scalar',changes[0]['candidate_event'],lambda e:e.__setitem__(3,'2')),('wrong_chart',changes[0]['candidate_event'],lambda e:e.__setitem__(-1,335))]:
  bad=deepcopy(w);update(bad['program'][which])
  try:audit(bad)
  except ValueError as exc:mutants.append(dict(name=name,rejected=True,reason=str(exc)))
  else:raise ValueError('mutant accepted '+name)
 bad=deepcopy(w);j=next(i for i,e in enumerate(bad['program']) if e[0]=='CLEAR');bad['program'].pop(j)
 try:audit(bad)
 except ValueError as exc:mutants.append(dict(name='omit_owned_clear',rejected=True,reason=str(exc)))
 else:raise ValueError('owned mutant accepted')
 return dict(schema='p104-alpha-peer/1',status='PASS_SCALAR_AND_TYPED_BOUNDARIES_NOT_NATIVE_PHASE_OR_COMPLETE_PRICE',source_pins=PINS,before=a,after=b,paid_delta=delta,changes=changes,transport_histories={'before':histories(s,roles),'after':histories(w,roles)},mutation_controls=mutants,allwidth_scope='Each field stores Phi_frame^{tensor f} times its logical row. Exact chart-changing native MOVE interfaces and same-chart ADD/SCALE/COPY imply every positive field width with owner coefficients applied once. Native absolute-phase lowering is verified separately by the parent; this checker does not grant it or complete caller pricing.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result=json.loads(json.dumps(calculate(),sort_keys=True));encoded=json.dumps(result,sort_keys=True,indent=2)+'\n';receipt=ROOT/'RECEIPT.json'
 if a.write:receipt.write_text(encoded)
 else:need(json.loads(receipt.read_text())==result,'frozen receipt')
 print(json.dumps({'status':'PASS','science_sha256':sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'paid_delta':result['paid_delta'],'rows':result['after']['endpoint_rows'],'native_phase':'SEPARATE_PARENT_CHECK','full_pricing':'SEPARATE_PARENT_CHECK'},sort_keys=True))
if __name__=='__main__':main()
