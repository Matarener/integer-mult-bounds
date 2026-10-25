#!/usr/bin/env python3
"""Independent finite linear check and actual optimized Git-free CLI controls."""
import gzip,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent

def require(ok,why):
    if not ok:raise SystemExit('FAIL: '+why)
def check_matrices():
    counts={}
    for n in (2,3,4):
        count=0
        for packed in range(1<<(n*n)):
            rows=[(packed>>(n*j))&((1<<n)-1) for j in range(n)]
            span={0}
            for row in rows:span|={x^row for x in tuple(span)}
            if len(span)!=(1<<n):continue
            count+=1
            # Quotient input coordinates are e_92,e_87, then zero borrowed rows.
            out=[r&3 for r in rows];s={0}
            for r in out:s|={x^r for x in tuple(s)}
            require(len(s)==4,'invertible borrowed-bank network lost source rank')
            require(out!=[3,3]+[0]*(n-2),'forbidden output reached')
        counts[n]=count
    require(counts=={2:6,3:168,4:20160},'complete GL census')
    return counts

def main():
    counts=check_matrices()
    word=json.loads(gzip.decompress((P/'inputs/R437-COMPOSED-WORD.json.gz').read_bytes()))
    # Structurally separate one-column propagation for the two witnesses.
    for col in (87,92):
        active={col};before=None;after=None
        for i,(_,d,ss) in enumerate(word['A']):
            if i==1998:before=set(active)
            if sum(s in active for s in ss)%2:
                if d in active:active.remove(d)
                else:active.add(d)
            if i==2000:after=set(active);break
        require((413 in before)==(col==87) and 444 not in before,'independent input columns')
        require(413 in after and 444 in after,'independent target columns')
    controls=[]
    with tempfile.TemporaryDirectory(prefix='r437-cut-export-') as td:
        out=Path(td)/'package';shutil.copytree(P,out,ignore=shutil.ignore_patterns('__pycache__'))
        env=os.environ.copy();env.pop('PYTHONPATH',None)
        def run():
            return subprocess.run([sys.executable,'-I','-O','-B',str(out/'verify.py')],cwd=td,env=env,text=True,capture_output=True,timeout=30)
        r=run();require(r.returncode==0 and 'PASS_R437_CARRIER' in r.stdout,'actual Git-free optimized replay: '+r.stdout+r.stderr)
        for name,path,change in [
            ('changed_source','inputs/R437-COMPOSED-WORD.json.gz',lambda b:b[:-1]+bytes([b[-1]^1])),
            ('changed_certificate','RESULT.json',lambda b:b.replace(b'"initial_rank": 2',b'"initial_rank": 1')),
            ('missing_notice','inputs/UPSTREAM-NOTICE.md',None)]:
            f=out/path;b=f.read_bytes()
            if change is None:f.unlink()
            else:
                new=change(b);require(new!=b,'control changes bytes');f.write_bytes(new)
            r=run();require(r.returncode!=0 and 'FAIL:' in r.stderr,'CLI mutation accepted: '+name)
            f.write_bytes(b);controls.append(name)
    print('PASS_INDEPENDENT_CUT_CHECK',json.dumps({'GL_counts':counts,'single_columns':[87,92],'Git_free_optimized':True,'CLI_controls':controls},sort_keys=True))
if __name__=='__main__':main()
