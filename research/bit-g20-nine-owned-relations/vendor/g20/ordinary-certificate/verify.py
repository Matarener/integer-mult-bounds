"""Isolated cold arithmetic/fee/source audit; never modifies frozen inputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import certificate,independent
HERE=Path(__file__).resolve().parent
def need(c,m):
 if not c:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def check_pin(root,row,key='path'):
 p=(root/row[key]).resolve();need(p.is_relative_to(root.resolve())and p.is_file()and p.stat().st_size==row['bytes'],'Local file pin '+row[key]);need(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'Source bytes '+row[key])
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--provider',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();provider=args.provider.resolve();out=args.output.resolve();need(not out.exists()and not out.is_relative_to(provider)and not out.is_relative_to(HERE/'inputs'),'Fresh output outside frozen runtime/input directories');out.mkdir(parents=True)
 start=time.perf_counter();cpu=time.process_time();manifest=read(HERE/'MANIFEST.json')
 for row in manifest['files']:check_pin(HERE,row)
 inputs=read(HERE/'INPUTS.json')
 for row in inputs['files']:check_pin(HERE,row)
 pinned=(HERE/'inputs'/'provider-MANIFEST.json').read_bytes();need((provider/'MANIFEST.json').read_bytes()==pinned,'Sealed native provider exact manifest')
 native=read(provider/'MANIFEST.json')
 for row in native['files']:check_pin(provider.parent,row,'relative_path')
 result=certificate.run();need(result==read(HERE/'RESULT.json'),'Deterministic primary certificate')
 second=independent.audit(provider,result);need(second==read(HERE/'INDEPENDENT.json'),'Deterministic independent census/series/height certificate')
 receipt={'status':'PASS_COLD_CONDITIONAL_G20_ORDINARY_CERTIFICATE','at_utc':datetime.now(timezone.utc).isoformat(),'isolated':sys.flags.isolated,'optimized':sys.flags.optimize,'python':sys.version,'source_inputs':len(inputs['files']),'native_runtime_pins':len(native['files']),'admitted':result['admitted'],'comparator':result['comparator'],'relative_gain':result['relative_gain'],'finite_levels':3,'H0':result['tail']['new_H0'],'H1':result['tail']['new_H1'],'provider_manifest_sha256':hashlib.sha256(pinned).hexdigest(),'certificate_manifest_sha256':hashlib.sha256((HERE/'MANIFEST.json').read_bytes()).hexdigest(),'allfees_status':result['fee_bounds']['status'],'retained_assumptions':result['retained_assumptions'],'whole_kappa':None,'new_PR':False,'CPU_seconds':time.process_time()-cpu,'elapsed_seconds':time.perf_counter()-start}
 (out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
