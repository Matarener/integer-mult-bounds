#!/usr/bin/env python3
"""Actual CLI baseline-before-fault controls, including read-only export copies."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    faults=('false_saving','float','boolean','duplicate','source_changed','source_missing','predecessor_changed')
    total=0
    for fault in faults:
        with tempfile.TemporaryDirectory(prefix='full-chart-control-') as td:
            root=Path(td);p=root/'research/p104-full-chart-joint'
            shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            for x in root.rglob('*'):x.chmod(0o755 if x.is_dir() else 0o644)
            for name in json.loads((HERE/'VERIFY.json').read_text())['inputs']:
                dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
            def run(opt):
                return subprocess.run([sys.executable,'-I','-B',*opt,'-X','pycache_prefix='+str(root/'cache'),str(p/'verify.py')],cwd=root,capture_output=True,text=True,timeout=40)
            for opt in ([],['-O']):
                good=run(opt);need(good.returncode==0,'positive fixture '+fault+good.stderr[-300:]);total+=1
            receipt=p/'RESULT.json';x=json.loads(receipt.read_text())
            if fault=='false_saving':x['native_rank_saved']+=1;receipt.write_text(json.dumps(x))
            if fault=='float':x['new_route']['positive_rank_one_transforms']=21632.0;receipt.write_text(json.dumps(x))
            if fault=='boolean':x['new_route']['private_copies']=False;receipt.write_text(json.dumps(x))
            if fault=='duplicate':receipt.write_text(receipt.read_text().replace('{','{"schema_version":1,',1))
            source=root/'research/p104-native-channel/NATIVE-RECIPES.json.gz'
            if fault=='source_changed':source.write_bytes(source.read_bytes()+b' ')
            if fault=='source_missing':source.unlink()
            if fault=='predecessor_changed':
                q=p/'inputs/pr3978-RESULT.json';q.write_bytes(q.read_bytes()+b' ')
            for opt in ([],['-O']):
                bad=run(opt);need(bad.returncode!=0,'fault accepted '+fault);need('PASS full-chart' not in bad.stdout,'false pass '+fault);total+=1
    print('PASS controls: '+str(total)+' actual CLI runs, seven faults after positive baselines, normal and optimized')
if __name__=='__main__':main()
