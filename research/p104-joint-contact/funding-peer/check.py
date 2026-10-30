"""Independent full-invoice recount and rational moment sign sanity proof.

No import from either pricing engine, native checker, or candidate constructor.
"""
from pathlib import Path,PurePosixPath
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
from io import BytesIO
import argparse,ast,gzip,json,tarfile
ROOT=Path(__file__).resolve().parent;IN=ROOT/'inputs'
def need(ok,why):
 if not ok:raise ValueError(why)
def read(n):return json.loads((IN/n).read_bytes())
def ctr(x):return Counter({int(k):v for k,v in x.items()})
def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return[encode(v)for v in x]
 return x
def source_closure():
 pins=read('SOURCES.json')['retained_source'];raw=(IN/'pr5545-source-closure.tar.gz').read_bytes()
 need(sha256(raw).hexdigest()==pins['sha256'],'capsule pin')
 with tarfile.open(fileobj=BytesIO(gzip.decompress(raw)),mode='r:')as t:
  ms=t.getmembers();names=[m.name for m in ms]
  need(len(names)==len(set(names))and all(m.isfile()and not PurePosixPath(m.name).is_absolute()and '..'not in PurePosixPath(m.name).parts for m in ms),'regular unique members')
  blobs={m.name:t.extractfile(m).read()for m in ms}
 manifest=blobs.pop('.research-export.json');need(sha256(manifest).hexdigest()==pins['export_manifest_sha256'],'export pin');m=json.loads(manifest)
 need(m['commit']==pins['commit']and len(m['files'])==33==pins['files'],'source head and count')
 need(set(blobs)=={x['path']for x in m['files']},'exact source closure')
 for x in m['files']:need(len(blobs[x['path']])==x['size']and sha256(blobs[x['path']]).hexdigest()==x['sha256'],'source payload '+x['path'])
 return dict(files=33,commit=pins['commit'],capsule_sha256=pins['sha256'],export_sha256=pins['export_manifest_sha256'])
class Funding(ast.NodeTransformer):
 def visit_Module(self,n):
  n=self.generic_visit(n)
  if isinstance(n.body[0],ast.Expr)and isinstance(n.body[0].value,ast.Constant)and isinstance(n.body[0].value.value,str):n.body.pop(0)
  return n
 def visit_Assign(self,n):
  names={x.id for t in n.targets for x in ast.walk(t)if isinstance(x,ast.Name)}
  if names in ({'KAPPA','TESTED'},{'PREVIOUS'}):n.value=ast.Constant('CLAIM_PARAMETERS')
  return self.generic_visit(n)
 def visit_Dict(self,n):
  n=self.generic_visit(n)
  for i,k in enumerate(n.keys):
   if isinstance(k,ast.Constant)and k.value=='kappa_decimal':n.values[i]=ast.Constant('CLAIM_DECIMAL')
   if isinstance(k,ast.Constant)and k.value in ('previous_open_pr5544','previous_open_pr5545'):n.keys[i]=ast.Constant('PREVIOUS_PR_LABEL')
  return n
def normalized_code(p):return ast.dump(Funding().visit(ast.parse(p.read_text())),include_attributes=False)
# Fresh elementary rational interval engine. Log uses atanh series; exp(-x)
# uses alternating Taylor bounds. Both are unrelated to retained suppliers.
S=1<<128;NLOG=50

def qfloor(x):return x.numerator//x.denominator
def qceil(x):return -((-x.numerator)//x.denominator)
def logunit(z):
 z=Q(z);s=Q(0);power=z
 for k in range(NLOG):s+=2*power/(2*k+1);power*=z*z
 rem=2*power/((2*NLOG+1)*(1-z*z))
 return Q(qfloor(s*S),S),Q(qceil((s+rem)*S),S)
LOG2=logunit(Q(1,3))
def logrank(r):
 e=r.bit_length()-1;u=1<<e;l,h=logunit(Q(r-u,r+u))
 return l+e*LOG2[0],h+e*LOG2[1]
def eminus_point(x,n):
 t=Q(1);s=t
 for j in range(1,n+1):t*=(-x)/j;s+=t
 return s

def power(r,k):
 l,h=logrank(r);lo,hi=k*l,k*h
 need(0<=lo<=hi<1,'alternating exponential range')
 # odd degree15 underestimates exp(-hi); even degree14 overestimates exp(-lo).
 return r*eminus_point(hi,15),r*eminus_point(lo,14)
def moment(hist,k):
 low,high=Q(0),Q(0)
 for r,n in hist.items():
  l,h=power(r,k);low+=n*l;high+=n*h
 return low,high

def calculate():
 closure=source_closure()
 need(normalized_code(IN/'predecessor_pricing.py')==normalized_code(IN/'successor_pricing.py'),'unchanged executable funding logic after explicit claim/output-label substitutions')
 l=read('local.json');n=read('native.json');c=read('controller.json');p=read('physical.json');cost=read('complete_cost.json');peer=read('local-peer-RECEIPT.json')
 public=read('PUBLIC-RESULT.json')
 need(public['local']==l and public['native']==n and public['physical_caller']==p and public['complete_cost']==cost,'public receipt is the exact audited local/native/caller/price output')
 decode_word=lambda name:json.loads(gzip.decompress((IN/name).read_bytes()))
 need(sha256((IN/'AUDITED-CANDIDATE-WORD.json.gz').read_bytes()).hexdigest()==peer['source_pins']['CANDIDATE-WORD.json.gz'],'independent integer peer word pin')
 need(decode_word('PUBLIC-WORD.json.gz')==decode_word('AUDITED-CANDIDATE-WORD.json.gz'),'public emitted word semantic equality despite serialization')
 need(ctr(l['paid'])==ctr(peer['after']['paid'])and ctr(l['helpers'])==ctr(peer['after']['helpers']),'independently audited local paid and target rows')
 need(l['peak_owned_fields']==peer['after']['owned_peak']==1 and l['owned_lifetimes']==peer['after']['owned_lifetimes']==8,'unchanged stock')
 need(l['helpers']==n['helpers'],'all helper normalizers')
 T=Counter();P=Counter();events=Counter();main=Counter();idle=Counter()
 for e in c['physical_events']:
  events[e[0]]+=1
  if e[0]=='LOCAL':need(e[3]is False,'forward local');T.update(ctr(l['helpers']));P.update(ctr(l['paid']))
  elif e[0]=='QUERY_SHEAR':P[1]+=104
  elif e[0]=='IDLE':r=8*len(e[2]);P[r]+=208;idle[r]+=208
 for t in c['diagonal']:main[1+8*sum(t[1:])]+=104
 T.update(main)
 need((events['LOCAL'],events['QUERY_SHEAR'],events['IDLE'])==(18,15,15),'complete service census')
 need(main==ctr(p['main_targets'])and idle==ctr(p['whole_idle_jobs']),'physical rank targets and every idle')
 # Separately count all banks by the two complete path lengths.
 T2=Counter({r:18*x for r,x in ctr(l['helpers']).items()});P2=Counter({r:18*x for r,x in ctr(l['paid']).items()})
 T2[145]+=208;P2[1]+=15*104
 for length in (7,8):
  for j in range(1,length+1):T2[1+8*(j+1)]+=208;P2[8*(j+1)]+=208
 need((T,P)==(T2,P2)==(ctr(cost['targets']),ctr(cost['paid'])),'independent complete histogram joins')
 need(sum(T.values())==12814 and sum(P.values())==69912 and sum(r*x for r,x in T.items())-sum(r*x for r,x in P.items())==760,'complete counts and rank surplus')
 probes={}
 for name,k in [('claimed',Q('.00304153')),('tested',Q('.0030415305')),('raw_lower',Q('.00304153116714')),('raw_upper',Q('.00304153116715'))]:
  tlo,thi=moment(T,k);plo,phi=moment(P,k);m=(tlo-phi,thi-plo)
  need(m[1]<0 if name=='raw_upper'else m[0]>0,'independent exact moment sign '+name)
  probes[name]=dict(kappa=k,margin=m,interval_width=m[1]-m[0])
 need(sum(ctr(l['paid']).values())==3624 and sum(r*x for r,x in ctr(l['paid']).items())==5894,'unchanged local route and Gaussian mass')
 routes=(3624+n['helper_normalizers']+n['main_adapters']+4*104+4*8)*1000
 boundary=sum(len(c['boundaries'][s+'_program'])for s in ('left','right'))
 raw=18*10**7+15*1664+32*104*(len(c['physical_events'])+boundary)+32*104*(26+1000)
 need(routes==cost['nonrecursive']['local_routes']==5334000 and l['real_scalar_allowance']+routes<10**7,'all local ordinary route allowance')
 need(raw==cost['nonrecursive']['raw_scalar_upper']==184647552 and raw<10**9,'complete ordinary allowance')
 gap=(Q('.0030415305')-Q('.00304153'))/7
 need(gap==Q(1,14000000000)and cost['compiler']['gap']==str(gap),'integer compiler gap')
 need(len(cost['outer']['strict_checks'])==54 and len(cost['outer']['functional_checks'])==4 and all(Q(x)>0 for family in ('strict_checks','functional_checks')for x in cost['outer'][family].values()),'all cached outer conditions positive')
 return encode(dict(status='PASS_SCOPED_CONDITIONAL_ADMISSION_AUDIT',input_pins={str(p.relative_to(IN)):sha256(p.read_bytes()).hexdigest()for p in sorted(IN.rglob('*'))if p.is_file()},source_closure=closure,price_funding_code='Executable logic unchanged except claimed/tested/comparison values and output labels',targets=T,paid=P,fields=sum(T.values()),calls=sum(P.values()),rank_surplus=760,independent_rational_moment_engine=dict(log_atanh_terms=NLOG,log_rounding_bits=128,exponential_bounds=[15,14],probes=probes),ordinary=dict(local_routes=routes,local_scalars=l['real_scalar_allowance'],whole_raw=raw,local_rankmass=5894,owned_peak=1,lifetimes=8),inherited_assumptions=['Native implementation at every column','Owned erasure','Uniform compiler','Precision and tape costs','Analytic recovery'],scope='Independent source authentication, static funding-code comparison, full histogram recount and fresh rational moment signs. Uses separately executed author native/caller/outer receipts; does not independently implement those frameworks or claim human/proof-kernel admission.'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();r=json.loads(json.dumps(calculate(),sort_keys=True));p=ROOT/'RECEIPT.json'
 if args.write:p.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(read_receipt(p)==r,'frozen review receipt')
 print(json.dumps(dict(status=r['status'],science_sha256=sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest(),fields=r['fields'],calls=r['calls']),sort_keys=True))
def read_receipt(p):return json.loads(p.read_bytes())
if __name__=='__main__':main()
