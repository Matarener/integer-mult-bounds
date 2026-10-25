"""Bounded export and mutation controls; no Git and no emitter imports."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def run(root, optimized, ok, reason=''):
    command = [sys.executable, '-I'] + (['-O'] if optimized else []) + ['-Werror','-B',str(root/'research/qq16-provider-binding/verify.py')]
    result = subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=80)
    need((result.returncode==0)==ok, result.stdout+result.stderr)
    if reason:
        need(reason in result.stderr,'wrong rejection: '+result.stderr)

with tempfile.TemporaryDirectory(prefix='qq16-provider-binding-') as name:
    export = Path(name)
    package = export/'research/qq16-provider-binding'
    package.mkdir(parents=True)
    for src in HERE.iterdir():
        if src.is_file():
            shutil.copyfile(src,package/src.name)
    manifest = json.loads((HERE/'VERIFY.json').read_text())
    for rel in manifest['inputs']:
        dest = export/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,dest)
    need(not (export/'.git').exists(),'Git-free export')
    files = list(export.rglob('*'))
    hashes = {str(p.relative_to(export)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
    try:
        for p in files:
            p.chmod(0o555 if p.is_dir() else 0o444)
        run(export,False,True)
        run(export,True,True)
        overwrite = subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),'--write'],cwd=export,capture_output=True,text=True,timeout=5)
        need(overwrite.returncode != 0 and 'refusing to overwrite existing RESULT.json' in overwrite.stderr,'existing receipt overwrite accepted')
        need(hashes=={str(p.relative_to(export)):hashlib.sha256(p.read_bytes()).hexdigest() for p in export.rglob('*') if p.is_file()},'read-only export changed')
    finally:
        for p in files:
            p.chmod(0o755 if p.is_dir() else 0o644)
    receipt = package/'RESULT.json'
    original = receipt.read_bytes()
    changed = json.loads(original)
    changed['schema_version'] = True
    receipt.write_text(json.dumps(changed))
    run(export,True,False,'complete typed receipt')
    receipt.write_bytes(original)
    packet = export/'research/joint-query/certificate.json.gz'
    packet.write_bytes(packet.read_bytes()+b'bad')
    run(export,True,False,'source SHA256')
print('PASS Git-free read-only normal/optimized export and source/typed-receipt controls')
