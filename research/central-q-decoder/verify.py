"""Read-only verification of exact central-Q decoder and its real bill."""
from pathlib import Path
from hashlib import sha256
import json, subprocess, sys, secrets
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def integrity():
    records=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf8'))['files']
    expected={r['path']:r for r in records}
    actual={p.relative_to(ROOT).as_posix()for p in ROOT.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}-{'MANIFEST.json'}
    need(actual==set(expected),'Changed package inventory')
    for name,r in expected.items():
        n=Path(name);need(not n.is_absolute()and '..'not in n.parts,'Unsafe path')
        b=(ROOT/n).read_bytes();need(len(b)==r['size']and sha256(b).hexdigest()==r['sha256'],'Changed file: '+name)
    return len(expected)+1

def main():
    count=integrity();saved=json.loads((ROOT/'RESULT.json').read_text(encoding='utf8'));checks=[]
    for name in ['check_decoder.py','check_rounding.py','check_invoice.py']:
        cache=ROOT/('.bytecode-'+secrets.token_hex(12));need(not cache.exists(),'Fresh bytecode namespace')
        argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache)]+(['-O']if not __debug__ else[])+[str(ROOT/name)]
        p=subprocess.run(argv,capture_output=True,timeout=90)
        if p.returncode:
            sys.stderr.buffer.write(p.stderr);raise RuntimeError('Failed scientific replay: '+name)
        got=json.loads(p.stdout);need(got==saved[name],'Changed mathematical receipt: '+name)
        checks.append({'component':name,'status':got['status']})
    print(json.dumps({'status':'PASS_CENTRAL_Q_DECODER','files':count,'optimized_wrapper':not __debug__,'checks':checks,'new_kappa':False},indent=2))
if __name__=='__main__':main()
