"""Reject changed mathematical evidence and a changed source bill.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]

def require(value,message):
    if not value:raise ValueError(message)

def main():
    for kind,expected in [('certificate','Free-algebra certificate'),('query','Query rank and square'),('source','Source digest:'),('receipt','Committed result differs'),('mixed','Full-word trap must fail')]:
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);package=root/'research/crossed-connector-caller';shutil.copytree(PACKAGE,package,ignore=shutil.ignore_patterns('__pycache__'))
            source=root/'research/p104-helper-subspace-splits/RESULT.json';source.parent.mkdir(parents=True);shutil.copyfile(ROOT/'research/p104-helper-subspace-splits/RESULT.json',source)
            if kind=='certificate':
                path=package/'PAIR-CERTIFICATES.json';x=json.loads(path.read_text());x[0]['terms']=[];path.write_text(json.dumps(x))
            elif kind=='query':
                path=package/'ESCAPE-WORD.json';x=json.loads(path.read_text());x['calls'][6]['r']=[0]*8;path.write_text(json.dumps(x))
            elif kind=='source':source.write_text(source.read_text()+' ')
            elif kind=='mixed':shutil.copyfile(package/'ESCAPE-WORD.json',package/'MIXED-ONLY-CANDIDATE.json')
            else:(package/'RESULT.json').write_text('{}\n')
            result=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],cwd=root,capture_output=True,text=True,timeout=30)
            require(result.returncode!=0 and expected in result.stderr,'Mutation was not rejected: '+kind)
    print('PASS_CONNECTOR_MUTATIONS: 5 corrupted packages rejected')
if __name__=='__main__':main()
