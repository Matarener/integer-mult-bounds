"""handoff6030_test (SPEED, Oct 28): `tk eval 6030 --screens handoff` runs the hand-off screen WITHOUT error (rc 0).
Before the fix, handoff.enumerate_B crashed on every frontier word since #5811 (owned registers get frames from INIT, which the B-class frame tracker
ignored -> fr[None] TypeError), so `tk eval` silently recorded 'no applied word' and the screen never contributed.  ~60 s.  usage: handoff6030_test.py"""
import sys,os,json,glob,subprocess,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
from tkcommon import OUT,PY
def main():
    out=OUT+'/regress_handoff6030'; shutil.rmtree(out,ignore_errors=True)
    r=subprocess.run([PY,'-B',TK+'/tk.py','eval','6030','--screens','handoff','--rounds','1','--accept','fast','--no-accept-each','--out',out,'--force'],capture_output=True,text=True,timeout=3000)
    recs=glob.glob(out+'/records/*.json'); fails=[]
    if r.returncode!=0 or not recs: fails.append('eval rc %d, records %d: %s'%(r.returncode,len(recs),(r.stderr or r.stdout)[-300:]))
    else:
        rec=json.load(open(recs[0])); st=[s for s in rec.get('steps',[]) if s.get('screen')=='handoff']
        logs=glob.glob(out+'/work/*/*/r0_handoff.log'); lg=open(logs[0]).read() if logs else ''
        ok=bool(st) and st[0].get('info',{}).get('rc')==0 and 'Traceback' not in lg and not rec.get('errors')
        print('handoff step:',json.dumps(st[0] if st else None,default=str)[:300])
        if not ok: fails.append('handoff screen did not run cleanly: %s'%lg[-400:])
    for f in fails: print('FAIL',f)
    print('ALL PASS' if not fails else 'FAIL'); return 1 if fails else 0
if __name__=='__main__': sys.exit(main())
