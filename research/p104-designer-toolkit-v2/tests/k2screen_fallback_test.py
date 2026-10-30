#!/usr/bin/env python3
"""GEN2POLISH: k2/screen.py convention fallback.  A `tk accept --native-ref` refusal caused ONLY by the public/owned inventory literal falls back to `tk check --native` under TK_FREE_BOUNDS=1
(instead of discarding a legal SA gain); any other refusal, an ILLEGAL word ('LEGAL' is a substring of 'ILLEGAL') or a bad native pair must still reject.
usage: tests/k2screen_fallback_test.py [--fast]"""
import sys,os,subprocess,types
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
from k2 import screen as S
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
need('TK_FREE_BOUNDS' not in os.environ,'importing k2.screen leaves env untouched')
need(S.inventory_only(dict(ok=False,error='Public inventory bound: 968 outside [750, 760]')),'inventory_only: public-inventory refusal is convention-only')
need(S.inventory_only(dict(ok=False,error='Owned inventory bound')),'inventory_only: owned-inventory refusal is convention-only')
need(not S.inventory_only(dict(ok=True,error=None)),'inventory_only: accepted word is not a refusal')
need(not S.inventory_only(dict(ok=False,error='native pair bad at event 5')),'inventory_only: other refusal is NOT convention-only')
need(not S.inventory_only(dict(ok=False,error=None)),'inventory_only: unparseable/None error is NOT convention-only')
real=subprocess.run
def fake(rc,out):
    def f(*a,**k): return types.SimpleNamespace(returncode=rc,stdout=out,stderr='')
    return f
try:
    for rc,out,want,msg in((0,'w: LEGAL (968 regs, 25203 events, 0.1s)\nnative: 2942 distinct frame pairs, 0 bad (10.6s)\n',True,'legal + 0 bad -> accepted'),
                            (1,'w: ILLEGAL (968 regs, 25203 events, 0.1s)\n - [rule] event 3: x\nnative: 2942 distinct frame pairs, 0 bad (10.6s)\n',False,'ILLEGAL with 0 bad native pairs -> rejected (the substring bug)'),
                            (0,'w: ILLEGAL (1 regs, 2 events, 0.1s)\nnative: 1 distinct frame pairs, 0 bad (1s)\n',False,'ILLEGAL even with rc 0 -> rejected'),
                            (1,'w: LEGAL (968 regs, 25203 events, 0.1s)\nnative: 2942 distinct frame pairs, 3 bad (10.6s)\n',False,'LEGAL but 3 bad native pairs -> rejected'),
                            (1,'Traceback ...\n',False,'crash -> rejected')):
        S.subprocess.run=fake(rc,out); need(bool(S.native_check_free('x.json.gz'))==want,'native_check_free: '+msg)
finally: S.subprocess.run=real
env_seen={}
def spy(cmd,**k): env_seen.update(k.get('env') or {}); return types.SimpleNamespace(returncode=0,stdout='w: LEGAL (1 regs, 1 events, 0s)\nnative: 1 distinct frame pairs, 0 bad (1s)\n',stderr='')
S.subprocess.run=spy
try: S.native_check_free('x'); 
finally: S.subprocess.run=real
need(env_seen.get('TK_FREE_BOUNDS')=='1' and 'TK_FREE_BOUNDS' not in os.environ,'fallback child runs with TK_FREE_BOUNDS=1, parent env untouched')
if '--fast' not in sys.argv:
    w=os.path.join(TK,'words','5660.json.gz'); need(S.native_check_free(w),'real `tk check --native` under free bounds accepts word #5660')
print('ALL PASS' if not fails else 'FAILED: %s'%fails); sys.exit(1 if fails else 0)
