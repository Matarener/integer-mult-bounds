#!/usr/bin/env python3
"""Real optimized CLI controls on private writable copies. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def need(ok,msg):
    if not ok:raise ValueError(msg)

def main():
    cases=('valid','false_mass','boolean_count','float_count','duplicate_receipt','source_changed','source_missing')
    for case in cases:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);package=root/'research/p104-joint-compensation'
            shutil.copytree(HERE,package)
            for item in json.loads((HERE/'VERIFY.json').read_text())['inputs']:
                dst=root/item;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/item,dst)
            for path in root.rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
            r=package/'RESULT.json';data=json.loads(r.read_text())
            if case=='false_mass':data['gate']['constructed_joint_excess']-=1;r.write_text(json.dumps(data))
            if case=='boolean_count':data['joint_route']['peak_additional_private_arrays']=True;r.write_text(json.dumps(data))
            if case=='float_count':data['minimum_fixed_owner_shear_layers']=3.0;r.write_text(json.dumps(data))
            if case=='duplicate_receipt':r.write_text(r.read_text().replace('{','{"schema_version":1,',1))
            source=root/'research/p104-native-channel/inputs/P104-FIXTURE.json'
            if case=='source_changed':source.write_bytes(source.read_bytes()+b' ')
            if case=='source_missing':source.unlink()
            for optimize in ([],['-O']):
                run=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(root/'private-cache'),*optimize,str(package/'verify.py')],cwd=root,capture_output=True,text=True,timeout=30)
                need((run.returncode==0)==(case=='valid'),case+' accepted/rejected incorrectly '+run.stderr[-400:])
    print('PASS controls: 14 actual CLI runs, six mutations in normal and optimized Python')
if __name__=='__main__':main()
