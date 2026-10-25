"""Positive and rejecting controls; no assert, valid under python -O."""
from pathlib import Path
import copy,json,subprocess,sys,tempfile,shutil
import verify as v

def reject(call,why):
    try:call()
    except (ValueError,RuntimeError,v.audit.AuditFailure):return
    raise ValueError('accepted mutation: '+why)

def main():
    root=Path(__file__).resolve().parent;result=v.read(root/'RESULT.json')
    w=v.read(root/'frozen/WORD-base.json.gz');row=result['providers']['base']['candidates'][0]
    x=v.apply(w,row);v.semantics(x)
    bad=copy.deepcopy(row);bad['edits'][0]['new']=[];reject(lambda:v.apply(w,bad),'invalid scalar containment')
    bad=copy.deepcopy(x);e=row['edits'][0];bad[e['section']][e['index']][2]=1
    reject(lambda:v.semantics(bad),'scalar sign changes dirty semantics')
    for kind in ('owner-debit','source-byte'):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'pkg';shutil.copytree(root,target)
            for p in target.rglob('*'):
                if p.is_file():p.chmod(0o600)
                elif p.is_dir():p.chmod(0o700)
            if kind=='owner-debit':
                r=v.read(target/'RESULT.json');r['providers']['base']['candidates'][0]['owner_debit']={};(target/'RESULT.json').write_text(json.dumps(r))
            else:
                p=target/'frozen/WORD-base.json.gz';p.write_bytes(p.read_bytes()+b'!')
            run=subprocess.run([sys.executable,'-O','-B',str(target/'verify.py'),'--quick'],capture_output=True,text=True)
            v.need(run.returncode!=0,'optimized CLI accepted '+kind)
            v.need(('result mismatch' if kind=='owner-debit' else 'frozen source hash') in run.stderr,'wrong rejection '+kind)
    print(json.dumps({'status':'PASS_POSITIVE_AND_4_REJECTIONS','positive':'literal arbitrary-dirty witness','optimized_cli_mutations':2}))
if __name__=='__main__':main()
