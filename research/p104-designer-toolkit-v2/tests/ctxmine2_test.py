#!/usr/bin/env python3
"""CTXMINE2 test: search2 still rediscovers #5827 from #5811; numeric equal-value redirect (RD) on #5827 is value-exact; CS/CM/CJ children are equiv-exact; pscreen/auto_frontier carry the screen."""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.join(HERE,'..'); sys.path.insert(0,TK)
os.environ.setdefault('TK_FREE_BOUNDS','1')
fails=[]
def need(c,what):
    print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
import movekit as M, ctxmine as CM, ctxmine2 as C2
from tkcommon import load
p,w=load('5811'); w=M.pin(w); v=M.View(w)
for _ in range(6): M.quick(v,v.S)
num=C2.Num(v.S,v.n)
r=C2.search2(v,num,12600,12608,depth=3,beam=40,tl=60)
need(bool(r) and abs(M.evaluate(v.rebuild(r[0]['S']))['kappa']-0.003124766815079838)<1e-15,'search2: #5811 -> #5827 rediscovered')
p,w=load('5827'); w=M.pin(w); v=M.View(w)
for _ in range(6): M.quick(v,v.S)
num=C2.Num(v.S,v.n); S=v.S
ids=[i for i,e in enumerate(S) if e[0] in('ADD','COPY') and e[2] in(572,778)]
rd=[c for i in ids for c in C2.children2(S,i-3,i+5,v.n,num,kinds=('RD',))]
need(len(rd)>0 and all(C2.num_equiv(num,S,c[1]) for c in rd[:10]),'RD redirects 572<->778 exist and are numerically value-exact (%d)'%len(rd))
S2=[list(e) for e in S]; e=S2[ids[0]]; S2[ids[0]]=e[:2]+[e[2]+1]+e[3:]
need(not C2.num_equiv(num,S,S2),'num_equiv rejects a wrong redirect')
ch=list(C2.children2(S,3000,3008,v.n,num,kinds=('CS','CM','CJ')))
kinds={c[0][0] for c in ch}
need({'CS','CJ'}<=kinds,'CS and CJ children are generated (%s)'%sorted(kinds))
need(all(CM.equiv(S,c[1]) for c in ch[:300]),'CS/CM/CJ children are symbolically equiv-exact')
need('ctxmine2' in open(os.path.join(TK,'pscreen.py')).read(),'pscreen carries ctxmine2')
print('ALL PASS' if not fails else 'FAILS %d'%len(fails)); sys.exit(1 if fails else 0)
