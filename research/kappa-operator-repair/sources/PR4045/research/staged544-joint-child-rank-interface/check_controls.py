"""Production-CLI rejecting controls, Apache-2.0, Chris R with OpenAI Codex."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json
P=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def main():
    for optimized in (False,True):
        for mutation in ('source-byte','retained-rank'):
            with tempfile.TemporaryDirectory(prefix='joint-child-control-') as tmp:
                dst=Path(tmp)/'package';shutil.copytree(P,dst,ignore=shutil.ignore_patterns('__pycache__'))
                if mutation=='source-byte':
                    f=dst/'frozen/WORD-base.json.gz';f.chmod(0o644);d=bytearray(f.read_bytes());d[-1]^=1;f.write_bytes(d)
                    expected='frozen source changed'
                else:
                    f=dst/'RESULT.json';f.chmod(0o644);j=json.loads(f.read_text());j['providers']['base']['calls'][0]['rank']=16;f.write_text(json.dumps(j));expected='retained result differs'
                argv=[sys.executable]+(['-O'] if optimized else [])+['-B',str(dst/'verify.py')]
                p=subprocess.run(argv,capture_output=True,text=True,timeout=90)
                need(p.returncode!=0 and expected in p.stderr,'production mutation accepted or wrong reason')
    print('PASS_PRODUCTION_CLI_CONTROLS: source corruption and stale rank receipt reject in normal/optimized Python')

if __name__=='__main__':main()
