"""GENSPLICE regression: synth/s2s.py state-to-state window synthesis (empty edit, small windows on #5718/#5756, whole-word compaction on #5774, tamper detection)."""
import sys,os,random
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD)
os.environ['TK_FREE_BOUNDS']='1'
from tkcommon import *
from incr import IncrWord
from synth import s2s
fails=0
def need(c,m):
    global fails
    print(('ok   ' if c else 'FAIL ')+m,flush=True)
    if not c: fails+=1
rng=random.Random(5)
for a in ('5718','5756'):
    import movekit; iw=IncrWord(movekit.pin(load(a)[1])); w=iw.to_word(); n=len(w['program']); k0=iw.kappa; ok=True; saved=0; cnt=0
    for _ in range(12):
        L=rng.choice((200,400)); t0=rng.randrange(0,n-L); ed,st=s2s.resynth(w,t0,t0+L)
        if ed is None: continue
        r=iw.try_edit(ed); cnt+=1; saved+=st['saved']
        ok&=bool(r.legal) and abs(r.dk)<1e-13 and st['events_after']<st['events_before'] and s2s.window_equal(w,ed)
    need(ok and cnt>0,'%s: %d random small windows re-synthesised: legal, kappa identical, fewer events (%d saved), exact end state equal'%(a,cnt,saved))
    ed,st=s2s.resynth(w,0,n,allow_equal=True)       # empty edit: original events allowed -> never costlier
    r=iw.try_edit(ed)
    need(r.legal and abs(r.dk)<1e-13 and st['events_after']<=st['events_before'],'%s: whole-word re-synthesis (original allowed): legal, kappa identical, events %d -> %d'%(a,st['events_before'],st['events_after']))
iw=IncrWord('5774'); w=iw.to_word(); ed,st=s2s.resynth(w)
r=iw.try_edit(ed)
need(r.legal and abs(r.dk)<1e-13 and st['saved']>=3000 and s2s.window_equal(w,ed) and 'selfcheck_failed' not in st['why'],'#5774 whole word: %d events saved, legal, kappa identical, exact forms/frames equal'%st['saved'])
w2=s2s.apply(w,ed); iw2=IncrWord(w2,profile=iw.profile); need(iw2.legal_all and abs(iw2.kappa-iw.kappa)<1e-13,'#5774 compacted word re-loaded from scratch: legal (incl. native pairs), same kappa')
# tamper: a wrong refactoring must fail selfcheck
ms,ev=s2s.analyze(w['program'],0,len(w['program']),len(w['initial'])); evb={x[0]:x for x in ev}
m=next(m for m in ms if not m.skip and m.orig>=5); s2s.matrix(w['program'],m,evb); new=s2s.refactor(m)
bad=[list(e) for e in new]; i=next(i for i,e in enumerate(bad) if e[0]=='ADD'); bad[i][3]='3'
need(new is not None and s2s.selfcheck(m,new) and not s2s.selfcheck(m,bad),'selfcheck accepts the exact factorisation and rejects a tampered coefficient')
print('FAILS',fails); sys.exit(1 if fails else 0)
