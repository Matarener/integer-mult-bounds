#!/usr/bin/env python3
"""SPLITRETIRE screen tests: exact ceiling numbers on #5795 (needs words/5795.json.gz).  usage: tests/splitretire_test.py [--quick]"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
import tkcommon,legal
fails=[]
def need(c,m):
    print(('PASS ' if c else 'FAIL ')+m,flush=True)
    if not c: fails.append(m)
def main():
    wf=os.path.join(TK,'words','5795.json.gz')
    if not os.path.exists(wf) or '--quick' in sys.argv: print('skipped (quick or no word)'); return 0
    import splitretire as SR
    w=legal.load(wf); R=SR.screen(w)
    c=R['ceiling_by_missing_hops']
    need(c[1][0]==102 and abs(R['one_hop_gross']-1.6572e-4)<1e-7,'one-hop-missing: 102 helpers, gross ceiling 1.6572e-4')
    need(R['hop_cost_rank1']<-7.4e-5,'an added paid rank-1 hop costs -7.44e-5 (>> any P7 ceiling)')
    need(not R['census_free_completions'],'no census-free (retime) completion for any positive one-hop-missing helper')
    print('%d FAIL'%len(fails)); return 1 if fails else 0
sys.exit(main())
