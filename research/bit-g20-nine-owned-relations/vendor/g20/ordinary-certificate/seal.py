"""Create fresh exact receipts and freeze this successor, never old manifests."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import certificate,independent
HERE=Path(__file__).resolve().parent
def need(c,m):
 if not c:raise ValueError(m)
def put(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 need(not(HERE/'MANIFEST.json').exists(),'Successor already sealed')
 for row in json.loads((HERE/'INPUTS.json').read_bytes())['files']:
  p=HERE/row['path'];need(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'Input drift '+row['path'])
 result=certificate.run();second=independent.audit(HERE.parent/'provider',result);put('RESULT.json',result);put('INDEPENDENT.json',second);put('FEE-BOUNDS.json',result['fee_bounds'])
 put('RESTART.json',{'status':'PRIVATE_CONDITIONAL_ORDINARY_GATE_READY_FOR_ROOT_REVIEW','native_provider':'../provider','native_manifest_sha256':hashlib.sha256((HERE.parent/'provider'/'MANIFEST.json').read_bytes()).hexdigest(),'admitted':result['admitted'],'comparison_to':result['comparator'],'relative_gain':result['relative_gain'],'whole_kappa':None,'publication':'No newPR; below0.1percent guard; published/frozen trees unchanged.','review_first':['PROOF.md','FEE-BOUNDS.json','RESULT.json','INDEPENDENT.json'],'next_concrete_gate':'Root independently checks exact tails, new H0/H1, original/currentSOURCE ABI, explicit large positive fees, live-unit stock and finite completed-backend type. Only after that may this be used as a private future bundle input.','do_not_repeat':['More decimal tightening','Oldretimingwindow/sourcebasis exclusions','Publishing subthreshold rawroot as ordinary saving'],'bounds_not_materialized':['Astronomical final uniform WORD','N=2^H1 or new q as a literal integer','Absolute source primitive TM constants; retained fixed implementation premises remain conditional']})
 files=sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.md'))+[HERE/n for n in('INPUTS.json','RESULT.json','INDEPENDENT.json','FEE-BOUNDS.json','RESTART.json')]+sorted((HERE/'inputs').glob('*'))
 put('MANIFEST.json',{'schema':'g20-ordinary-private-runtime/1','at_utc':datetime.now(timezone.utc).isoformat(),'files':[pin(p)for p in files]});print(json.dumps({'status':result['status'],'admitted':result['admitted'],'manifest_sha256':hashlib.sha256((HERE/'MANIFEST.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()
