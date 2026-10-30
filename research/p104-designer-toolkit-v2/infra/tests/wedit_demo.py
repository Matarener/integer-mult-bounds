"""Demo/test: (1) fresh c=1 helper (rank 4) is price-neutral; (2) relay_add on a real ADD is legal, +3 events, kappa unchanged
(S = that fresh helper, positioned at the ADD's frame); (3) a deliberately wrong relay is rejected."""
import os
import sys; sys.path.insert(0,__file__.rsplit('/',2)[0])
import wedit,legal
W=wedit.Word.load(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/ext/P104POLISH/src/research/p104-full-frame-contact/WORD.json.gz')
b=W.verify(); print('base kappa %.13f events %d'%(b['kappa'],b['events']))
w=W.w; prog=w['program']; fr=w['frames']
# find an ADD at a frame F with dim<=5 and make a fresh helper whose initial frame is F and final is F+1 more dim
i=next(i for i,e in enumerate(prog) if e[0]=='ADD' and e[1]<735 and e[2]<735 and 3<=len(fr[e[-1]])<=6)
F=prog[i][-1]; Fb=fr[F]
extra=next(v for v in range(1,512) if v not in legal.spans({'frames':[Fb+[v]]})[0] or True)
import itertools
sp=legal.spans(w)[F]; v=next(x for x in range(1,512) if x not in sp)
F2=W.frame(Fb+[v]); W1,h=W.copy(),None
W1=wedit.Word(W.copy().w); W1.w['frames']=W.w['frames']
W2,h=W1.add_helper(F,F2)   # helper starts at F (dim d), single climb to dim d+1, at the end of the program
v2=W2.verify(); print('fresh c=1 helper: legal',v2['legal'],'dkappa %.2e'%(v2['kappa']-b['kappa']),'events',v2['events'])
# relay: put the helper's MOVE at the end (already); relay the ADD at i (event index may shift: no, add_helper inserts at end)
W3=W2.relay_add(i,h); v3=W3.verify()
print('relay_add on ADD #%d via helper %d: legal %s  dkappa %.2e  events %d -> %d'%(i,h,v3['legal'],v3['kappa']-b['kappa'] if v3['legal'] else float('nan'),v2['events'],v3['events']),v3['violations'][:1])
# wrong relay: omit the restoring subtract
bad=W2.replace(i,[['ADD',h,prog[i][2],prog[i][3],F],['ADD',prog[i][1],h,1,F]]); vb=bad.verify()
print('wrong relay (no restore): legal',vb['legal'],vb['violations'][:2])
