#!/usr/bin/env python3
"""FASTSITES quick regression (regress --quick): delta quick == full quick, incremental rebuild == full rebuild, ratio-form proxy_sites == reference, indexed merge == old merge, incremental proxy pool == full,
first-order screen recall.  Small samples on #5660 (the full differential gate is tests/dq_diff.py over 5660/5678/5718/5795/5802).  usage: tests/fastsites_test.py"""
import sys,os,subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); fails=0
def run(args,ok):
    global fails
    r=subprocess.run([sys.executable,'-B']+args,capture_output=True,text=True,env=dict(os.environ,CHAIN='3',QUICK='1')); good=r.returncode==0 and ok in r.stdout
    print(('PASS ' if good else 'FAIL ')+' '.join(a.replace(HERE+'/','') for a in args[:3]),flush=True)
    if not good: print(r.stdout[-600:],r.stderr[-400:]); fails+=1
run([HERE+'/dq_diff.py','5660','--macros','conj,cofrm','--prims','P1,P2,P3','--max','150'],'MISMATCHES 0')
run([HERE+'/rebuild_diff.py','5660','--n','150'],'MISMATCHES 0')
run([HERE+'/ibase_fast_test.py','5660'],'FAILS 0')
run([HERE+'/sedit_diff.py','5660','--stride','11','--max','40','--incr-every','5'],'MISMATCHES 0')      # REALISEFIX: edit-emitting path == list path
print('FAILS',fails); sys.exit(1 if fails else 0)
