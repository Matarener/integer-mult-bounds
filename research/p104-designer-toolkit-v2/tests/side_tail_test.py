"""TKHYG2 regression: every X.side caller must pass the adopted (c,b,u) tail.  Verdict on #5907 and #5827 must be ok on every path;
plus a static guard: no direct X.side(...) call in toolkit code except inside tkcommon.side_of / explicit legacy infra."""
import sys,os,re,glob
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK); sys.path.insert(0,TK+'/wsearch')
sys.dont_write_bytecode=True
import tkcommon as t, movekit as M, incr, legalize, split
bad=[]
def need(c,m):
    print(('ok   ' if c else 'FAIL ')+m)
    if not c: bad.append(m)
for a in('5907','5827'):
    path,w=t.load(a); pr=t.profile_of(w)[1]; need(bool(pr.get('tail')),'%s profile has a tail'%a)
    need(M.evaluate(w)['side_ok'],'%s movekit.evaluate side ok'%a)
    need(incr.IncrWord(w).side()['ok'],'%s incr.IncrWord.side ok'%a)
    rep=t.legal.check(w); T,P=t.X.invoice(rep)
    need(t.side_of(T,P,pr)['ok'],'%s tkcommon.side_of ok'%a)
    need(not t.X.side(T,P,decay=pr['decay'],reserve=pr.get('reserve',1e-10))['ok'],'%s test is sensitive: legacy-tail X.side FAILs (the bug)'%a)
    need(legalize.side_budget(w,rep,decay=pr['decay'])['delta']<pr['decay'],'%s legalize.side_budget delta<decay at profile tail'%a)
    import copy; r=split.kappa_of(copy.deepcopy(w),pr and t.profile_of(w)[0]); need(r['side_ok'],'%s split.kappa_of side ok'%a)
    import evalincr as E
    iw=E._make_iw(w) if hasattr(E,'_make_iw') else None
    if iw is not None:
        need(t.side_of(*iw._invoice(iw.paid0,iw.hel0) if hasattr(iw,'paid0') else (T,P),iw.pr)['ok'],'%s evalincr iw.pr carries tail'%a)
# static guard
pat=re.compile(r'\bX\.side\(|\bpe\.side\(')
for f in glob.glob(TK+'/*.py')+glob.glob(TK+'/wsearch/*.py')+glob.glob(TK+'/synth/*.py'):
    for i,l in enumerate(open(f,errors='ignore'),1):
        if pat.search(l) and '**' not in l and 'side_of' not in l and not l.lstrip().startswith('#') and 'c=c,b=b,u=u' not in l:
            need(False,'direct X.side without tail: %s:%d'%(os.path.basename(f),i))
sys.exit(1 if bad else 0)
