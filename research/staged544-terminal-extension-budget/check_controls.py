"""Real optimized-CLI mutations of the production checker; standard library."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    cases=[]
    with tempfile.TemporaryDirectory(prefix='terminal-budget-controls-') as d:
        for name in ['dual','capacity','missing_empty_bin','source_bytes']:
            p=Path(d)/name;shutil.copytree(ROOT,p)
            for f in p.rglob('*'):
                if f.is_file():f.chmod(0o600)
            if name=='dual':
                f=p/'verify.py';s=f.read_text();needle='48:Q(1,20),3:Q(-1,20),5:Q(-1,4)';need(s.count(needle)==1,'dual mutation anchor');f.write_text(s.replace(needle,'48:Q(1,10),3:Q(-1,20),5:Q(-1,4)'))
            elif name in ('capacity','missing_empty_bin'):
                f=p/'OWNER-PATTERNS.json';v=json.loads(f.read_text())
                if name=='capacity':v['patterns'][0][0]+=1
                else:v['patterns']=[r for r in v['patterns'] if any(r[1])]
                f.write_text(json.dumps(v))
            else:
                f=p/'frozen/PROFILE.json';f.write_bytes(f.read_bytes()+b' ')
            r=subprocess.run([sys.executable,'-O','-B',str(p/'verify.py')],capture_output=True,text=True,timeout=180)
            need(r.returncode!=0,'mutation accepted '+name)
            expected={'dual':'dual infeasibility','capacity':'pattern capacity','missing_empty_bin':'complete bin counts','source_bytes':'frozen source'}[name]
            need(expected in r.stderr,'wrong rejection '+name+': '+r.stderr[-1000:]);cases.append(name)
    print(json.dumps({'status':'PASS_PRODUCTION_CLI_MUTATIONS','rejected':cases}))
if __name__=='__main__':main()
