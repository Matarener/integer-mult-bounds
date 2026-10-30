"""Bounded standard-library replay of the changed word, owners and exact price.
Full native/global/outer evidence is authenticated, not rerun by this command.
"""
from pathlib import Path
from fractions import Fraction as Q
import gzip,hashlib,json,subprocess,sys,tarfile,copy
import rational_price as R
from owner_audit import audit,controls
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def authenticate():
 pins=read(P/'PINS.json')
 for name,digest in pins.items():
  need(not Path(name).is_absolute() and '..' not in Path(name).parts,'relative input')
  file=P/name;need(file.is_file() and not file.is_symlink() and sha(file)==digest,'input digest '+name)
 return pins

def check_release(release,endpoint,profile,source_manifest):
 need(release['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','full conditional release status')
 need(release['source_manifest_sha256']==source_manifest,'full release source binding')
 need(Q(release['kappa'])==endpoint,'full outer endpoint equality')
 need(release['profile']=={str(r):n for r,n in profile.items()},'full release profile')
 need(release['comparison_pr']==3682 and release['comparison_head']=='431e6c6023ef352c41696469de7fb614cd4ded8c','current comparator')
 need([s['name'] for s in release['stages']]==['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'] and all(s['exit_code']==0 for s in release['stages']),'all full admission stages')


def main():
 need(__debug__,'assertions enabled');pins=authenticate()
 for script in ['check_identity.py','review_staged544.py','replay_outer.py']:
  subprocess.run([sys.executable,'-B',str(P/script)],check=True)
 owner=audit();need(owner['physical']==323069,'complete physical stock');need(len(controls())==3,'constructive owner controls')
 price=read(P/'PRICE.json');profile={int(r):n for r,n in price['profile'].items()}
 need(profile=={int(r):n for r,n in owner['profile'].items()},'actual owner profile')
 low=Q(price['root_lower']);high=Q(price['root_upper']);signed=profile.copy();signed[73]=-896*360
 need(R.interval(signed,low)[1]<0<R.interval(signed,high)[0],'exact root signs')
 baseline=read(P/'inputs/PR3682-CLAIM.json');old=Q(baseline['kappa']);need(old==Q(baseline['kappa_rational']),'baseline exact expression')
 endpoint=low-Q(1,10**46)-Q(1,10**70);need(endpoint>old,'strict gain over3682')
 ledger=read(P/'outer-replay/outer/LEDGER.json')
 need({int(r):n for r,n in ledger['profile'].items()}==profile,'outer ledger actual profile')
 need(Q(ledger['complex_lower_pinned']['rational'])==low,'outer ledger exact complex lower')
 need(Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])==endpoint,'recomputed outer endpoint')
 archive=read(P/'REPLAY-INPUTS.json');need(sha(P/'REPLAY-INPUTS.tar.gz')==archive['archive_sha256'],'source archive bytes')
 with tarfile.open(P/'REPLAY-INPUTS.tar.gz') as t:
  receipt_raw=t.extractfile('NATIVE-RECEIPT.json').read()
 need(hashlib.sha256(receipt_raw).hexdigest()==archive['files']['NATIVE-RECEIPT.json'],'archived native receipt')
 receipt=json.loads(receipt_raw)
 need(receipt['manifest_sha256']==archive['files']['source/MANIFEST.json'],'native source manifest')
 sources=None
 for tag in ('base','extra'):
  native=read(P/'evidence'/f'NATIVE-{tag}.json');need(native['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','complete native evidence')
  need(native['word_sha256']==sha(P/'words'/f'BORROW-WORD-43{tag}.json.gz'),'native evidence binds new word')
  binding=receipt['providers'][tag];need(binding['word_sha256']==native['word_sha256'],'archive binds new provider')
  need(binding['complete_native_files']['local/CANONICAL-WORD.json.gz']==sha(P/'inputs'/f'NATIVE-{tag}.json.gz'),'actual native canonical frames')
  for name,digest in native['source_sha256'].items():need(archive['files']['source/new/fastnative/vendor/'+name]==digest,'native scientific engine '+name)
  need([s['step'] for s in native['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in native['steps']),'native phase coverage')
  need(sources is None or sources==native['source_sha256'],'same native scientific sources');sources=native['source_sha256']
 release=read(P/'evidence/RELEASE.json')
 check_release(release,endpoint,profile,receipt['manifest_sha256'])
 package_manifest=read(P/'evidence/PACKAGE-MANIFEST.json')
 need(sha(P/'evidence/PACKAGE-MANIFEST.json')==release['package_manifest_sha256'],'actual admitted package manifest')
 for file in (P/'outer-replay').rglob('*'):
  if file.is_file():need(sha(file)==package_manifest[file.relative_to(P/'outer-replay').as_posix()],'admitted outer replay input')
 for kind in ('missing_stage','wrong_endpoint','wrong_source'):
  bad=copy.deepcopy(release)
  if kind=='missing_stage':bad['stages'].pop()
  elif kind=='wrong_endpoint':bad['kappa']=str(endpoint+Q(1,10**80))
  else:bad['source_manifest_sha256']='0'*64
  try:check_release(bad,endpoint,profile,receipt['manifest_sha256'])
  except ValueError:pass
  else:raise ValueError('release evidence mutant accepted '+kind)
 need(authenticate()==pins,'input drift')
 print('PASS_STAGED544_CHANGED_CONSTRUCTION_AND_CONDITIONAL_GAIN',price['lower_decimal'],flush=True)
if __name__=='__main__':main()
