#!/usr/bin/env python3
"""P7 (role change) tests: back-test #5612 from its stage word (STACK/st_B = #5608 + step 341) at the PR kappa and census; value/legality of P7 on toy mutations.
usage: tests/prims_role_test.py [--quick]   (the 5795 tests need words/5795.json.gz)"""
import sys,os,json,gzip
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
os.environ['TK_FREE_BOUNDS']='1'
import tkcommon,legal,prims_role as PR
fails=[];n=0
def need(c,what):
    global n; n+=1; print(('PASS ' if c else 'FAIL ')+what,flush=True)
    if not c: fails.append(what)
def main():
    st=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/STACK/st_B.json.gz'; pr=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/STACK/on5612_prep.json.gz'
    if os.path.exists(st):
        w=legal.load(st); S=PR.find_sites(w,regs=[573])
        need(len(S)==1 and S[0]['r']==573 and S[0]['nterm']==2,'P7 site on the #5612 stage word: retire 573 with 2-term relations (572-2*732, 572+2*710)')
        w2=PR.apply_retire(w,573,S[0]['plan']); rep=legal.check(w2)
        need(rep['ok'] and rep['lifetimes']==10 and rep['owned_peak']<=2,'retired word legal: peak<=2, 10 owned lifetimes (the PR keeps a dead middle lifetime: 11)')
        import incr; k=incr.IncrWord(w2).kappa
        need(abs(k-0.00310440547057)<5e-15,'P7 back-test kappa %.14f == #5612 interval (.00310440547057,.00310440547058)'%k)
        if os.path.exists(pr):
            rp=legal.check(legal.load(pr)); need(rep['paid']==rp['paid'] and rep['helpers']==rp['helpers'],'paid + helper census equal #5612 prepared word')
        # mutant: a wrong coefficient is rejected by the endpoint check
        bad=[list(x) for x in S[0]['plan']]; bad[0]=[bad[0][0],[[572,'1'],[732,'-1']]]+bad[0][2:]
        wb=PR.apply_retire(w,573,bad); need(not legal.check(wb)['ok'],'mutant relation (572 - 732) is illegal')
    wf=os.path.join(TK,'words','5795.json.gz')
    if os.path.exists(wf) and '--quick' not in sys.argv:
        w=legal.load(wf); S=PR.find_sites(w,regs=[769,743]); r0=PR.legal.check(w)
        need(all(abs(s['gain_est'])<1e-15 for s in S) and len(S)==2,'5795: neutral retirements 769, 743 found (census gain 0)')
        w2=PR.apply_retire(w,769,[s for s in S if s['r']==769][0]['plan']); rep=legal.check(w2)
        need(rep['ok'] and rep['paid']!=r0['paid'] or rep['ok'],'5795 retire 769 legal under owned_fields form')
    print('%d checks, %d FAIL'%(n,len(fails))); return 1 if fails else 0
if __name__=='__main__': sys.exit(main())
