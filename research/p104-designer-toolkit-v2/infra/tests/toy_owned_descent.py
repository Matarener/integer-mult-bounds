"""COUNTEREXAMPLE to 'no transport / Lemma H: a register that ever held x_k can never feed a Y whose final frame excludes p_k'
(FRAMECHK sec.1 'descent is not a legal paid step, re-anchoring needs a same-frame source').
Toy over F2^3 frames, rules exactly as local.py replay (checked by DESIGNER/infra/legal.py, contract=False):
  S holds x2 history at frame <2> ; owned o is INIT/COPY'd from S at <1,2>?  -> we use S at frame A=<e1,e2>, copy to owned o,
  private MOVE o: A -> B=<e1> (descent, rank 1, uncredited), then ADD o into Y at B.  Y's chain: 0 -> B -> T=<e1,e4>.
  p_2 = e2 not in T, so Lemma H says S (history includes e2) cannot ever reach Y.  The rules accept it.  Price: one uncredited rank-1 job."""
import sys; sys.path.insert(0,__file__.rsplit('/',2)[0])
import legal
e1,e2,e4=1,2,4
fr=[[],[e1],[e1,e2],[e1,e4]]          # 0:{0} 1:<e1> 2:<e1,e2> 3:<e1,e4>
# regs: 0=X2 (init <e2>?) -> use S: init frame 2 (dim2) already holds 'x2 history' by construction; 1=Y init 0 final 3 ; owned 2
w=dict(frames=[[],[e1],[e1,e2],[e1,e4]],initial=[2,0],final=[2,3],live=[],ports=[],public=2,
 program=[['INIT',2,2],['COPY',2,0,1,2],['MOVE',2,2,1,True],['MOVE',1,0,1,False],['ADD',1,2,1,1],['MOVE',1,1,3,False],['CLEAR',2,1]])
r=legal.check(w,contract=False)
print('violations:',r['violations'],'paid:',r['paid'],'-> ACCEPTED' if r['ok'] else '-> REJECTED')
# negative control: same without the private descent (S direct into Y at frame 2 is impossible: Y never at frame 2 and cannot be, final 3 excludes e2)
w2=dict(w); w2['program']=[['MOVE',1,0,2,False]]
print('control (Y climbs to frame <e1,e2>, outside T):',legal.check(w2,contract=False)['ok'],'(frame law accepts; only final-frame contract can reject)')
w3=dict(w); w3['program']=[['INIT',2,2],['COPY',2,0,1,2],['MOVE',2,2,1,False]]
print('control (owned ascends instead of descending, wrong direction):',legal.check(w3,contract=False)['violations'][:1])
