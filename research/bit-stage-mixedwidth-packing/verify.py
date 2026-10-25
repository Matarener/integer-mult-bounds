#!/usr/bin/env python3
"""Bounded Git-free cold release for the new source-bound BIT packing."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
    started=time.time();manifest=json.loads((H/'FILES.json').read_bytes())
    for name,digest in manifest['files'].items():
        p=(H/name).resolve();need(p.is_relative_to(H),'input path scope')
        need(hashlib.sha256(p.read_bytes()).hexdigest()==digest,'committed input '+name)
    reports={}
    with tempfile.TemporaryDirectory(prefix='bit-stage-packing-')as temp:
        work=Path(temp)
        commands=[('SOURCE',[H/'independent_source.py','--provider',H/'provider','--output',work/'SOURCE.json']),
                  ('PRICE',[H/'independent_price.py','--provider',H/'provider','--output',work/'PRICE.json']),
                  ('CALLER',[H/'provider/verify_rehost.py','--output',work/'caller'])]
        for name,arguments in commands:
            env=os.environ.copy();env['PYTHONPYCACHEPREFIX']=str(work/('pycache-'+name))
            cmd=[sys.executable,'-B']+(['-O']if sys.flags.optimize else[])+list(map(str,arguments))
            p=subprocess.run(cmd,capture_output=True,env=env,timeout=300)
            need(p.returncode==0,name+' cold replay failed: '+p.stderr.decode('utf-8',errors='replace')[-4000:])
            reports[name]={'exit':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
                           'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
        source=json.loads((work/'SOURCE.json').read_bytes());price=json.loads((work/'PRICE.json').read_bytes())
        caller=json.loads((work/'caller/RESULT.json').read_bytes())
        need(caller['status']=='PASS_REGISTERED_INTEGER_MIXED_WIDTH_REHOST','caller status')
        need(caller['convenient_proved_b']=='871/500000','logical separator')
        need(caller['root']['lower']=='1743059363170060183941/1000000000000000000000000','exact moment root')
        need(len(caller['negative_controls'])==6,'scientific/source controls')
        for name,digest in manifest['files'].items():
            need(hashlib.sha256((H/name).read_bytes()).hexdigest()==digest,'post-replay source drift '+name)
        result={'status':'PASS_STAGE_ELIGIBLE_MIXED_WIDTH_BIT_RELEASE',
                'at_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
                'optimized':bool(sys.flags.optimize),'runs':reports,
                'SOURCE_status':source.get('status'),'PRICE_status':price.get('status'),
                'caller_status':caller['status'],'negative_controls':caller['negative_controls'],
                'moment_c_lower':caller['root']['lower'],'logical_b':caller['convenient_proved_b'],
                'whole_kappa_changed':False,'wall_seconds':time.time()-started}
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
if __name__=='__main__':main()
