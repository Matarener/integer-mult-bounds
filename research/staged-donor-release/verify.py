"""Bounded exact local replay and source/receipt authentication.
Full native/global/outer regeneration uses the separate full_replay.py CLI.
"""
from pathlib import Path
from contextlib import redirect_stdout
import gzip,hashlib,io,json,subprocess,sys,tempfile
from delay_release import build
import price
P=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def main():
 need(__debug__,'assertions required by historical engines')
 for row in read(P/'SOURCE-PINS.json'):need(sha(P/row['retained'])==row['sha256'],'source pin '+row['retained'])
 for tag in ('base','extra'):
  x,r=build(read(P/'sources'/f'STAGED644-660-{tag}.json.gz'));need(x==read(P/'lead1-words'/f'DELAYED-{tag}.json.gz'),'frozen candidate semantics')
  need(r['bill']=={1:2437,2:724,3:226,4:102,5:20,8:8},'local profile')
  native=read(P/'evidence'/('native-'+tag)/'RESULT.json');need(native['word_sha256']==sha(P/'lead1-words'/f'DELAYED-{tag}.json.gz'),'actual native input')
  need([s['step'] for s in native['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in native['steps']),'all five native stages')
 buf=io.StringIO()
 with redirect_stdout(buf):price.main()
 need(json.loads(buf.getvalue())==read(P/'LEAD1-PRICE.json'),'exact price receipt')
 result=subprocess.run([sys.executable,'-B',str(P/'reviews/lead1/check.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 need(result.returncode==0,'independent structural replay '+result.stderr.decode())
 need(json.loads(result.stdout)['status']=='PASS_INDEPENDENT_STRUCTURAL_CERTIFICATE','independent status')
 archive=read(P/'REPLAY-INPUTS.json');need(sha(P/'REPLAY-INPUTS.tar.gz')==archive['archive_sha256'],'self-contained source archive')
 # Fresh endpoint mutation checks operate only in an external temporary folder.
 from full_replay import extract
 with tempfile.TemporaryDirectory(prefix='four-kappa-finite-') as td:
  source=extract(Path(td)/'inputs')
  from owner_transfer import check as transfer
  need(transfer(source)['profile']==read(P/'LEAD1-PRICE.json')['profile'],'explicit owner transfer')
  transport=source/'source/new/fastnative/vendor/native/new/code/borrow/bw_transport.py'
  r=subprocess.run([sys.executable,'-B',str(P/'controls.py'),'--transport',str(transport)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  need(r.returncode==0,'semantic controls '+r.stderr.decode());need(read(P/'LEAD1-CONTROLS.json')['transport_sha256']==sha(transport),'original semantic engine')
  controls=json.loads(r.stdout);need(controls['status']=='PASS_SOURCE_BOUND_ENDPOINT_CONTROLS' and len(controls['checks'])==10,'control coverage')
 if (P/'evidence/complete/RESULT.json').exists():
  from evidence_check import check
  check()
 from wrapper_evidence import check as check_wrapper
 check_wrapper()
 print('PASS_BOUNDED_DELAYED_RELEASE_LOCAL_PRICE_AND_AUTHENTICATED_EVIDENCE')
if __name__=='__main__':main()
