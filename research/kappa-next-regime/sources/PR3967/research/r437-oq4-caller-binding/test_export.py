"""Exercise the actual optimized verifier outside Git, with source controls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def run():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='oq4-gitfree-') as temporary:
        root=Path(temporary);package=root/'research/r437-oq4-caller-binding'
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for row in sources['files']:
            if row['usage']!='input':continue
            target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],target)
        def cli():
            with tempfile.TemporaryDirectory(prefix='oq4-bytecode-') as cache:
                env=os.environ.copy();env.pop('PYTHONPATH',None);env.pop('PYTHONOPTIMIZE',None)
                return subprocess.run([sys.executable,'-I','-B','-O','-X','pycache_prefix='+cache,
                                       str(package/'verify.py'),'--suite','catalogue'],cwd=root,env=env,
                                      capture_output=True,text=True,timeout=80)
        result=cli()
        if result.returncode:raise ValueError('Git-free positive control: '+result.stderr[-2000:])
        mutations=[]
        cases=[('changed_word',package/'inputs/word.json.gz','bytes'),
               ('missing_template',package/'inputs/template.json.gz','missing'),
               ('symlinked_runtime',root/'research/selected-bit-physical-caller/macro_machine.py','symlink'),
               ('obsolete_request_digest',package/'adapter.py','digest'),
               ('falsified_full_payload_receipt',package/'PHYSICAL.json','receipt')]
        for label,path,kind in cases:
            original=path.read_bytes()
            if kind=='bytes':path.write_bytes(original+b'corruption')
            elif kind=='missing':path.unlink()
            elif kind=='symlink':
                alternate=root/'same-bytes.py';alternate.write_bytes(original);path.unlink();path.symlink_to(alternate)
            elif kind=='digest':
                path.write_bytes(original.replace(b'cbfea55f5cd0b74a2a0d4292ad0139d2b5bb73127951127698030bc90c73c532',
                                                  b'0fb70d6838583f2f439a8704eb5dba84ce9dbd231d91f140da13440b680d73aa'))
            else:
                data=json.loads(original);data['complete_GL64_payload_executed']=True
                path.write_text(json.dumps(data))
            try:
                result=cli()
                if result.returncode==0:raise ValueError('mutated CLI accepted '+label)
                mutations.append(label)
            finally:
                if path.is_symlink():path.unlink()
                path.write_bytes(original)
        return {'status':'PASS_ACTUAL_OPTIMIZED_GITFREE_CLI','rejected_controls':mutations,
                'scope':'Exported source/record checker, not a repeated physical payload run'}
