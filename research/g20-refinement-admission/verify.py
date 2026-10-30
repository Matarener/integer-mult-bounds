"""Rebuild the complete G20 admission from authenticated inputs in a fresh copy."""
from hashlib import sha256
from pathlib import Path
import gzip,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
OUTPUTS=['WORD.json.gz','MATCHER.json','LOCAL-RESULT.json','GLOBAL.jsonl.gz','GLOBAL-RESULT.json',
         'INVOICE.json','CALLS.json','PRIVATE-EPISODES.json','TARGET-OWNERS.json','SOURCE-DESCRIPTORS.json.gz',
         'ORDINARY-RESULT.json','INDEPENDENT-RESULT.json']


def need(ok,message):
    if not ok:raise ValueError(message)


def snapshot(root):
    return {str(f.relative_to(root)):sha256(f.read_bytes()).hexdigest() for f in root.rglob('*')
            if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc'}


def payload(path):
    raw=path.read_bytes()
    if path.suffix=='.gz':raw=gzip.decompress(raw)
    if path.name=='GLOBAL.jsonl.gz':return raw
    x=json.loads(raw)
    if path.name=='GLOBAL-RESULT.json':x.pop('CPU_seconds')
    return x


def main():
    before=snapshot(R)
    inputs=json.loads((R/'INPUTS.json').read_text())
    for item in inputs:need(before[item['local']]==item['sha256'],'Frozen input '+item['local'])
    need((R/'WORD.json.gz').read_bytes()==(R/'audited/WORD.json.gz').read_bytes(),'Exact audited word bytes')
    with tempfile.TemporaryDirectory(prefix='g20-refinement-admission-') as name:
        root=Path(name)/'package';shutil.copytree(R,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in OUTPUTS:(root/name).unlink()
        for name in ['integration.py','global_retirement.py','ordinary.py','independent.py']:
            args=[sys.executable,'-I','-B','-W','error','-X','pycache_prefix='+str(Path(name).name+'.fresh-cache')]
            if sys.flags.optimize:args.append('-O')
            completed=subprocess.run(args+[str(root/name)],cwd=root,text=True,capture_output=True,timeout=130)
            need(completed.returncode==0,name+' failed:\n'+completed.stdout[-2000:]+completed.stderr[-3000:])
            print('PASS_REBUILT',name,flush=True)
        for name in OUTPUTS:need(payload(root/name)==payload(R/name),'Exact rebuilt output '+name)
        need((root/'WORD.json.gz').read_bytes()==(root/'audited/WORD.json.gz').read_bytes(),'Exact rebuilt word bytes')
        for item in inputs:need(sha256((root/item['local']).read_bytes()).hexdigest()==item['sha256'],'Frozen input changed')
    need(snapshot(R)==before,'Replay changed source or result files')
    print('PASS_G20_REFINEMENT_COMPLETE_ORDINARY_003497804579519',flush=True)


if __name__=='__main__':main()
