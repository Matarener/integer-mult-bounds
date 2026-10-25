"""Fresh bounded release for the compact source-bound logical BIT supplier."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args();start=time.monotonic()
    pins=json.loads((H/'FILES.json').read_bytes())['files']
    def check():
        for name,digest in pins.items():
            p=(H/name).resolve();need(p.is_relative_to(H),'source path scope')
            need(hashlib.sha256(p.read_bytes()).hexdigest()==digest,'input source '+name)
    check();reports={}
    with tempfile.TemporaryDirectory(prefix='bit-compact-carrier-')as t:
        work=Path(t)
        commands=[('SOURCE',[H/'independent_source.py','--provider',H/'provider','--output',work/'SOURCE.json']),
                  ('PRICE',[H/'independent_price.py','--provider',H/'provider','--output',work/'PRICE.json']),
                  ('CALLER',[H/'provider/verify_rehost.py','--output',work/'caller'])]
        for name,args in commands:
            env=os.environ.copy();env['PYTHONPYCACHEPREFIX']=str(work/('pycache-'+name))
            cmd=[sys.executable,'-B']+(['-O']if sys.flags.optimize else[])+list(map(str,args))
            p=subprocess.run(cmd,capture_output=True,env=env,timeout=300)
            need(p.returncode==0,name+' failed: '+p.stderr.decode(errors='replace')[-5000:])
            reports[name]={'exit':0,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
                           'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()}
        source=json.loads((work/'SOURCE.json').read_bytes());price=json.loads((work/'PRICE.json').read_bytes())
        caller=json.loads((work/'caller/RESULT.json').read_bytes())
        need(caller['status']=='PASS_REGISTERED_ACTIVE658_COMPACT_GL_DEADROLE_REHOST','caller status')
        need(Q(caller['root']['lower'])==Q(1744853764761145849274,10**24),'exact new moment')
        need(Q(caller['convenient_proved_b'])==Q(174481,10**8),'actual logical separator')
        need(sum(caller['complete_profile'].values())==900416,'complete paid requests')
        need(len(caller['negative_controls'])==6,'live owner/source controls')
        check()
        result={'status':'PASS_COMPACT_CARRIER_LOGICAL_BIT_RELEASE','at_utc':datetime.now(timezone.utc).isoformat(),
          'python':sys.version,'optimized':bool(sys.flags.optimize),'runs':reports,
          'source_status':source.get('status'),'price_status':price.get('status'),'caller_status':caller['status'],
          'moment_lower':caller['root']['lower'],'logical_b':caller['convenient_proved_b'],
          'whole_kappa_changed':False,'seconds':time.monotonic()-start}
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(result,indent=2))
if __name__=='__main__':main()
