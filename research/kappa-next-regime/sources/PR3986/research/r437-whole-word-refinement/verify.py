"""Authenticated, read-only replay; works without Git in a source export."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def regular(path):
    need(path.is_file(),'missing regular input: '+str(path))
    for p in (path,*path.parents):need(not p.is_symlink(),'symlinked input: '+str(p))


def authenticate(root=ROOT,here=HERE):
    manifest=json.loads((here/'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=root/row['path'];regular(path);data=path.read_bytes()
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'canonical input hash: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'canonical input blob: '+row['path'])
    for row in manifest['retained']:
        path=here/row['path'];regular(path);data=path.read_bytes()
        need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'] and
             hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'retained input identity: '+row['path'])
    need({str(p.relative_to(here)) for p in (here/'inputs').rglob('*') if p.is_file()}==
         {row['path'] for row in manifest['retained']},'complete retained inventory')
    return manifest


def export_controls():
    manifest=authenticate();outcomes={}
    with tempfile.TemporaryDirectory(prefix='r437-word-export-') as temp:
        root=Path(temp);here=root/'research'/HERE.name
        shutil.copytree(HERE,here,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for row in manifest['files']:
            if row['usage']=='input':
                dst=root/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/row['path'],dst)
        result=subprocess.run([sys.executable,'-I','-B',str(here/'verify.py'),'--quick'],capture_output=True,text=True,timeout=60)
        need(result.returncode==0 and 'PASS_R437_WORD_QUICK' in result.stdout,'Git-free quick export: '+result.stderr)
        cases=[('changed_compiler',root/'research/selected-bit-physical-caller/macro_code.py','change'),
               ('changed_current_template',here/'inputs/template.json.gz','change'),
               ('missing_word',here/'inputs/word.json.gz','missing'),
               ('symlinked_dispatcher',root/'research/selected-bit-physical-caller/macro_machine.py','symlink')]
        for name,path,kind in cases:
            original=path.read_bytes()
            try:
                if kind=='change':path.write_bytes(original+b'\n')
                elif kind=='missing':path.unlink()
                else:
                    target=root/'saved-dispatcher';target.write_bytes(original);path.unlink();path.symlink_to(target)
                try:authenticate(root,here)
                except ValueError:outcomes[name]='REJECTED'
                else:raise ValueError('accepted source mutation: '+name)
            finally:
                if path.is_symlink():path.unlink()
                path.write_bytes(original)
    return outcomes


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group()
    group.add_argument('--quick',action='store_true');group.add_argument('--export',action='store_true')
    args=parser.parse_args();authenticate();sys.path.insert(0,str(HERE));import check
    if args.export:
        print(json.dumps({'status':'PASS_R437_WORD_EXPORT','controls':export_controls()},sort_keys=True));return
    if args.quick:
        result=dict(controls=check.controls(),guard_gap=check.guard_gap(),run_loop=check.run_control())
        print(json.dumps({'status':'PASS_R437_WORD_QUICK','result':result},sort_keys=True));return
    result=check.run();expected=json.loads((HERE/'EXPECTED.json').read_bytes())
    need(result==expected,'complete symbolic receipt unchanged')
    print(json.dumps({'status':'PASS_R437_WHOLE_WORD_REFINEMENT','residuals':result['residuals'],
        'checkpoints':result['checkpoints'],'scope':'Conditional translation theorem; source-reuse symbolic check; no physical primitive or production-payload proof'},sort_keys=True))


if __name__=='__main__':main()
