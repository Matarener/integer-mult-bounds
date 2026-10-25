# SPDX-License-Identifier: Apache-2.0
"""Fresh exact aggregate, literal owner and arithmetic checks; authenticate full release.
The complete conditional release is separately reproducible with full_replay.py.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy,gzip,hashlib,json,subprocess,sys,tarfile,types,tempfile
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def authenticate():
 pins=read(P/'PINS.json')
 for name,digest in pins.items():
  f=P/name;need(not Path(name).is_absolute() and '..' not in Path(name).parts,'relative pin')
  need(f.is_file() and not f.is_symlink() and sha(f)==digest,'source digest '+name)
 return pins

def check_release(release,endpoint,profile,source_manifest,native_digest):
 need(release['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete release status')
 need(release['source_manifest_sha256']==source_manifest,'unchanged source binding')
 need(release['native_receipt_sha256']==native_digest,'exact native receipt binding')
 need(Q(release['kappa'])==endpoint,'released endpoint')
 need(release['profile']=={str(r):n for r,n in profile.items()},'released paid profile')
 need(release['replicas']==488 and release['actual_expected_helpers']==408,'released stock')
 need(release['comparison_pr']==3734 and release['comparison_head']=='fa041037a3374eaa08feeca0b26a5d6893194147','frontier comparison')
 need(release['comparison_claim_sha256']==sha(P/'source3734/CLAIM.json'),'full comparison claim')
 for field,name in [('fill_sha256','FILL.json.gz'),('order_sha256','ORDER.json'),('dispatch_sha256','DISPATCH.json')]:need(release[field]==sha(P/'inputs'/name),'admitted literal '+name)
 need([s['name']for s in release['stages']]==['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'] and all(s['exit_code']==0 for s in release['stages']),'all admission stages')

def check_final_receipt(rr,release,endpoint):
 need(rr['status']=='PASS_RELEASE','final receipt status')
 need(Q(rr['kappa_decimal'])==endpoint,'final receipt endpoint')
 need(rr['manifest_sha256']==release['package_manifest_sha256'],'final receipt manifest')

def main():
 need(__debug__,'assertions enabled');pins=authenticate()
 subprocess.run([sys.executable,'-B',str(P/'check_aggregate.py'),'--certificate',str(P/'inputs/AGGREGATE.json.gz')],check=True)
 with tempfile.TemporaryDirectory(prefix='t488-owner-')as tmp:
  report=Path(tmp)/'owner.json';subprocess.run([sys.executable,'-B',str(P/'owner_check.py'),'--output',str(report)],check=True);owner=read(report)
 positive=owner['positive'];need(positive['roles']==1791936 and positive['physical']==437757,'complete physical stock')
 need(set(owner['controls'])=={'same_call_family','duplicate_helper','unpaid_hole'},'owner controls')
 price=read(P/'evidence/PRICE.json');profile={int(r):n for r,n in price['profile'].items()}
 need(profile=={int(r):n for r,n in positive['profile'].items()},'physical profile equality')
 R=types.ModuleType('exact_price');f=P/'rational_price.py';exec(compile(f.read_bytes(),str(f),'exec'),R.__dict__)
 lo,hi=Q(price['root_lower']),Q(price['root_upper']);signed=profile.copy();signed[73]=-896*488
 need(R.interval(signed,lo)[1]<0<R.interval(signed,hi)[0],'exact rational root bracket')
 endpoint=lo-Q(1,10**46)-Q(1,10**70);baseline=read(P/'source3734/CLAIM.json');need(Q(baseline['kappa'])==Q(baseline['kappa_rational'])<endpoint,'strict gain over full frontier')
 prior=read(P/'source3734/PRICE.json')['profile'];delta={r:45*profile.get(r,0)-61*prior.get(str(r),0)for r in set(profile)|set(map(int,prior))};need({r:n for r,n in delta.items()if n}=={1: -95352, 5: 59776, 48: -766, 3: -54936, 32: -61},'equal-replica allocation difference')
 arc=read(P/'source3734/REPLAY-INPUTS.json');need(sha(P/'source3734/REPLAY-INPUTS.tar.gz')==arc['archive_sha256'],'immutable replay archive')
 with tarfile.open(P/'source3734/REPLAY-INPUTS.tar.gz')as t:
  raw=t.extractfile('NATIVE-RECEIPT.json').read()
 need(hashlib.sha256(raw).hexdigest()==arc['files']['NATIVE-RECEIPT.json'],'native receipt bytes');native=json.loads(raw)
 need(native['manifest_sha256']==arc['files']['source/MANIFEST.json'],'native source manifest')
 for tag in ['base','extra']:
  ev=read(P/'source3734'/f'NATIVE-EVIDENCE-{tag}.json');binding=native['providers'][tag]
  need(ev['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and ev['word_sha256']==binding['word_sha256'],'retained provider evidence')
  need(binding['complete_native_files']['local/CANONICAL-WORD.json.gz']==sha(P/'source3734'/f'NATIVE-{tag}.json.gz'),'canonical native frames')
  need([s['step']for s in ev['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in ev['steps']),'retained phase and orientation coverage')
  for name,digest in ev['source_sha256'].items():need(arc['files']['source/new/fastnative/vendor/'+name]==digest,'native engine binding')
 release=read(P/'evidence/RELEASE.json');check_release(release,endpoint,profile,native['manifest_sha256'],hashlib.sha256(raw).hexdigest())
 manifest=read(P/'evidence/PACKAGE-MANIFEST.json');need(sha(P/'evidence/PACKAGE-MANIFEST.json')==release['package_manifest_sha256'],'admitted package manifest')
 rr=read(P/'evidence/RELEASE-RECEIPT.json');need(sha(P/'evidence/RELEASE-RECEIPT.json')==release['release_receipt_sha256'],'final receipt bytes');check_final_receipt(rr,release,endpoint)
 for f in (P/'outer-replay').rglob('*'):
  if f.is_file():need(sha(f)==manifest[f.relative_to(P/'outer-replay').as_posix()],'admitted outer artifact')
 subprocess.run([sys.executable,'-B',str(P/'replay_outer.py')],check=True)
 ledger=read(P/'outer-replay/outer/LEDGER.json');need({int(r):n for r,n in ledger['profile'].items()}==profile,'outer ledger profile');need(Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])==endpoint,'outer ledger endpoint')
 for kind in ['missing_stage','wrong_endpoint','wrong_source','wrong_fill','wrong_native_receipt']:
  bad=copy.deepcopy(release)
  if kind=='missing_stage':bad['stages'].pop()
  elif kind=='wrong_endpoint':bad['kappa']=str(endpoint+Q(1,10**80))
  elif kind=='wrong_fill':bad['fill_sha256']='0'*64
  elif kind=='wrong_native_receipt':bad['native_receipt_sha256']='0'*64
  else:bad['source_manifest_sha256']='0'*64
  try:check_release(bad,endpoint,profile,native['manifest_sha256'],hashlib.sha256(raw).hexdigest())
  except ValueError:pass
  else:raise ValueError('accepted release corruption '+kind)
 for field,value in [('manifest_sha256','0'*64),('status','PREPARED'),('kappa_decimal',str(endpoint+Q(1,10**80)))]:
  bad=copy.deepcopy(rr);bad[field]=value
  try:check_final_receipt(bad,release,endpoint)
  except ValueError:pass
  else:raise ValueError('accepted final receipt corruption '+field)
 need(authenticate()==pins,'input drift');print('PASS_STAGED544_T488_CONDITIONAL_GAIN',str(endpoint),flush=True)
if __name__=='__main__':main()
