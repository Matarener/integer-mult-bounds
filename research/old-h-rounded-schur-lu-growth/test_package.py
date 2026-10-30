"""Cheap receipt/source controls; no encoded producer replay."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def main():
    spec=importlib.util.spec_from_file_location('receipt_contract',HERE/'verify.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    need(v.canonical({'x':True})!=v.canonical({'x':1}),'boolean/integer receipt identity')
    need(v.canonical({'x':1})!=v.canonical({'x':1.0}),'integer/float receipt identity')
    with tempfile.TemporaryDirectory(prefix='lu-growth-controls-') as temp:
        root=Path(temp);package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__'))
        rows=json.loads((HERE/'SOURCES.json').read_text())['files']
        for row in rows:
            if row['usage']=='input':
                destination=root/row['path'];destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],destination)
        receipt=(package/'RESULT.json').read_bytes()
        target=root/'research/physical-gaussian-core/gaussian_window.py'
        original=target.read_bytes()
        count=0
        for optimization in ([],['-O']):
            command=[sys.executable,'-I','-B',*optimization,str(package/'verify.py'),'--algebra-only']
            def call(ok,fragment):
                result=subprocess.run(command,cwd=root,text=True,capture_output=True,timeout=10,
                                      env={**os.environ,'PATH':''})
                need((result.returncode==0)==ok and fragment in result.stdout+result.stderr,
                     'control result '+fragment+': '+result.stdout+result.stderr)
            call(True,'PASS_OLD_H_ROUNDED_SCHUR_LU_GROWTH_ALGEBRA');count+=1
            (package/'RESULT.json').unlink()
            call(False,'FileNotFoundError');count+=1
            (package/'RESULT.json').write_bytes(receipt)
            altered=json.loads(receipt);altered['algebra']['systems']+=1
            (package/'RESULT.json').write_text(json.dumps(altered))
            call(False,'complete typed receipt mismatch');count+=1
            (package/'RESULT.json').write_bytes(receipt)
            target.write_bytes(original+b'\nraise RuntimeError("MUTATED SOURCE EXECUTED")\n')
            call(False,'source hash research/physical-gaussian-core/gaussian_window.py');count+=1
            target.write_bytes(original)
    print('PASS_PACKAGE_CONTROLS '+str(count)+' subprocess controls plus typed JSON distinctions')


if __name__=='__main__':main()
