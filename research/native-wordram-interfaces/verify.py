"""Authenticate and replay four scoped native/Word RAM interfaces. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import json, subprocess, sys, secrets
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok: raise ValueError(msg)

def integrity():
    data=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    expected={r['path']:r for r in data['files']}
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}-{'MANIFEST.json'}
    need(actual==set(expected),'Package inventory differs')
    for name,rec in expected.items():
        q=Path(name)
        need(not q.is_absolute() and '..' not in q.parts,'Unsafe manifest path')
        raw=(ROOT/q).read_bytes()
        need(len(raw)==rec['size'] and sha256(raw).hexdigest()==rec['sha256'],'Changed package bytes: '+name)
    return len(expected)+1

def main():
    count=integrity(); checks=[]
    tasks=[('native/compile_unit.py',not __debug__),('precision/native_recoding.py',not __debug__),('precision/precision_certificate.py',not __debug__),('decoder/verify_terminal.py',False)]
    for name,optimized in tasks:
        cache=ROOT/('.bytecode-'+secrets.token_hex(16))
        need(not cache.exists(),'Fresh bytecode namespace required')
        argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache)]+(['-O'] if optimized else [])+[str(ROOT/name)]
        p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
        if p.returncode:
            sys.stderr.buffer.write(p.stderr);sys.stdout.buffer.write(p.stdout)
            raise RuntimeError('Scientific check failed: '+name)
        result=json.loads(p.stdout.decode('utf-8'))
        if name=='precision/native_recoding.py':
            frozen=json.loads((ROOT/'precision/RECODING-RESULT.json').read_text(encoding='utf-8'))
            need(result==frozen,'Recoding receipt differs')
        checks.append({'component':name,'optimized':optimized,'status':'PASS'})
    print(json.dumps({'status':'PASS_NATIVE_WORDRAM_INTERFACES','authenticated_files':count,'checks':checks,'new_multiplication_kappa_established':False},indent=2))

if __name__=='__main__':main()
