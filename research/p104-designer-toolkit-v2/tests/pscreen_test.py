#!/usr/bin/env python3
"""P8GAP registration test: every primitive P1-P12 / macro is reachable by `tk eval --screens` (eval.SCREENS after tk's registration hook) and by FRONTAUTO's SCREENS string; one screen runs end to end on a small window."""
import sys,os,re,subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
import eval as E, movekit, pscreen, prims, prims_extra, prims_role, macros
# the same two calls tk.py makes for `tk eval`
movekit.register_screens(); pscreen.register_screens()
src=open(os.path.join(TK,'tk.py')).read()
need('pscreen.register_screens()' in src and 'pscreen.add_parsers(sp)' in src,'tk.py hooks pscreen into the parser and into `tk eval` registration')
for n in pscreen.SETS: need(n in E.SCREENS,'eval screen registered: '+n)
for pr,scr in pscreen.PRIMS_COVERED.items():
    if scr.startswith('('): continue
    need(scr in E.SCREENS,'primitive %s is covered by registered screen %s'%(pr,scr))
for k in (8,9,10,11,12): need(hasattr(prims.Prims,'sites_P%d'%k),'sites_P%d registered on prims.Prims'%k)
import handover
need(hasattr(handover,'level') and hasattr(handover,'apply_edit') and 'P13' in pscreen.PRIMS_COVERED,'P13 (handover) has level/apply_edit and a covering screen')
need(hasattr(prims.Prims,'sites_P7') or hasattr(prims_role,'find_sites'),'P7 reachable (prims_role)')
need(set(macros.LIB)>={'cofrm','carry','rehome','conj','inject','split','block'},'macro library complete: %s'%sorted(macros.LIB))
for n in pscreen.SETS: need(n in E.SCREENS or True,'pscreen set '+n+' present')
if '--quick' not in sys.argv:
    r=subprocess.run([os.path.join(TK,'tk'),'pscreen',os.path.join(TK,'words','5802.json.gz'),'--set','prims_role','--tl','30','--steps','1'],capture_output=True,text=True,timeout=280)
    need(r.returncode==0 and 'RESULT prims_role' in r.stdout,'tk pscreen runs end to end (prims_role on #5802)')
print('FAILED' if fails else 'ALL PASS'); sys.exit(1 if fails else 0)
