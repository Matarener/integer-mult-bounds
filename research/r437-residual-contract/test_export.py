"""Run the actual optimized quick CLI outside Git, then corrupt its inputs."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def run():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='r437-residual-gitfree-') as temporary:
        root=Path(temporary);package=root/'research/r437-residual-contract'
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for row in sources['files']:
            target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],target)
        def cli():
            env=os.environ.copy();env.pop('PYTHONPATH',None)
            return subprocess.run([sys.executable,'-I','-B','-O',str(package/'verify.py'),'--quick'],cwd=root,env=env,capture_output=True,text=True,timeout=70)
        result=cli()
        if result.returncode:raise ValueError('Git-free positive control: '+result.stderr[-2000:])
        cases=[('changed_callback',root/'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/controller.py','changed'),('missing_template',package/'inputs/template.json.gz','missing'),('symlinked_word',package/'inputs/word.json.gz','symlink'),('false_preparation_count',package/'EXPECTED.json','receipt')]
        for label,path,kind in cases:
            original=path.read_bytes()
            if kind=='changed':path.write_bytes(original+b'\n# changed input\n')
            elif kind=='missing':path.unlink()
            elif kind=='symlink':
                alternate=root/'same-bytes';alternate.write_bytes(original);path.unlink();path.symlink_to(alternate)
            else:
                data=json.loads(original);data['add_pass'][0]['preparations']=[2,1,2];path.write_text(json.dumps(data))
            try:
                result=cli()
                if result.returncode==0:raise ValueError('accepted '+label)
            finally:
                if path.is_symlink():path.unlink()
                path.write_bytes(original)
        return {'status':'PASS_GITFREE_QUICK','rejected':[x[0] for x in cases]}
