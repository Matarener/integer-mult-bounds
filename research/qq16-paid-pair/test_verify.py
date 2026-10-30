"""Export integrity and discriminating controls, without Git or predecessors' code."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def need(ok,message):
    if not ok: raise ValueError(message)

def run(root,optimized=True,ok=True,reason='',extra=()):
    command = [sys.executable,'-I']+(['-O']if optimized else [])+['-Werror','-B',str(root/'research/qq16-paid-pair/verify.py'),*extra]
    p = subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=90)
    need((p.returncode==0)==ok,p.stdout+p.stderr)
    if reason: need(reason in p.stderr,'wrong rejection: '+p.stderr)

with tempfile.TemporaryDirectory(prefix='qq16-paid-pair-export-') as name:
    root = Path(name)
    pkg = root/'research/qq16-paid-pair'
    shutil.copytree(HERE,pkg,ignore=shutil.ignore_patterns('__pycache__'))
    for rel in json.loads((HERE/'VERIFY.json').read_text())['inputs']:
        dest = root/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,dest)
    need(not (root/'.git').exists(),'Git-free export')
    paths = list(root.rglob('*'))
    before = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    try:
        for p in paths: p.chmod(0o555 if p.is_dir() else 0o444)
        run(root,False)
        run(root,True)
        run(root,True,False,'refusing to overwrite existing RESULT.json',('--write',))
        after = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
        need(before==after,'read-only export changed')
    finally:
        for p in paths: p.chmod(0o755 if p.is_dir() else 0o644)
    receipt = pkg/'RESULT.json'; original = receipt.read_bytes()
    obj = json.loads(original); obj['schema_version'] = True
    receipt.write_text(json.dumps(obj)); run(root,True,False,'complete typed receipt')
    receipt.write_bytes(original)
    for rel in ('research/joint-query/certificate.json.gz','research/qq16-paid-pair/vendor/PR4015-WORD.json','research/qq16-paid-pair/PREDECESSORS.json'):
        path = root/rel; original = path.read_bytes(); path.write_bytes(original+b'bad')
        run(root,True,False,'manifest SHA256' if path.name=='PREDECESSORS.json' else 'source SHA256')
        path.write_bytes(original)
print('PASS_GIT_FREE_READ_ONLY_NORMAL_OPTIMIZED_SOURCE_TYPED_RECEIPT_OVERWRITE_CONTROLS')
