"""evalincr -- the default evaluator of the word search (SEARCHPERF): incr.IncrWord behind  evaluate(cand, base=base).
    try_word(base, cand)  diff_edit(base, cand) -> IncrWord.try_edit (fast mode: stops at the first violation); the dict has legal/kappa/ok (side + budgets of the CANDIDATE state)
    adopt(w)              the walk moved to w: commit the last tried edit (if w is that candidate) else rebind (IncrWord init ~0.1 s)
    resync                every `resync` commits and on demand: full movekit.evaluate of the committed word must agree with IncrWord (legal, kappa to 1e-15) -- else RuntimeError
Words are compared by identity (the driver passes the very objects it holds).  --relax is honoured through the patched price_exact.side (always ok)."""
import sys,os,time
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
import movekit as M, incr
import price_exact as X
from tkcommon import side_of

def _lcp_gallop(A,B,n):
    """length of the common prefix of A[:n], B[:n] -- galloping over C-speed slice comparisons (the original implementation; kept as the reference for the tests)"""
    if A[:n]==B[:n]: return n
    lo,hi=0,n                   # A[:lo]==B[:lo], A[:hi]!=B[:hi]
    while hi-lo>64:
        mid=(lo+hi)//2
        if A[:mid]==B[:mid]: lo=mid
        else: hi=mid
    while lo<hi and A[lo]==B[lo]: lo+=1
    return lo
_BLK=1024
def _lcp(A,B,n):
    """length of the common prefix of A[:n], B[:n]: one forward pass of C-speed block compares (identity-shared events compare in a pointer test), then a bisection inside the first differing block.
    Same value as _lcp_gallop (O(prefix) instead of O(n log n) slice copies)."""
    i=0
    while i<n:
        j=i+_BLK
        if j>n: j=n
        if A[i:j]==B[i:j]: i=j; continue
        lo,hi=i,j                       # A[i:lo]==B[i:lo]; A[lo:hi]!=B[lo:hi]
        while hi-lo>16:
            mid=(lo+hi)//2
            if A[lo:mid]==B[lo:mid]: lo=mid
            else: hi=mid
        while lo<hi and A[lo]==B[lo]: lo+=1
        return lo
    return n
def _lcs(A,B,n):
    """length k<=n of the common suffix of A and B (A[len(A)-k:]==B[len(B)-k:]); block compares from the end, no reversed copies.  Equals _lcp_gallop(A[::-1],B[::-1],n)."""
    la,lb=len(A),len(B); k=0
    while k<n:
        m=k+_BLK
        if m>n: m=n
        if A[la-m:la-k]==B[lb-m:lb-k]: k=m; continue
        lo,hi=k,m                       # suffix of length lo matches; length hi does not
        while hi-lo>16:
            mid=(lo+hi)//2
            if A[la-mid:la-lo]==B[lb-mid:lb-lo]: lo=mid
            else: hi=mid
        while lo<hi and A[la-1-lo]==B[lb-1-lo]: lo+=1
        return lo
    return n
def fast_diff_edit(old,new):
    """incr.diff_edit with C-speed prefix/suffix search (the python per-event loop costs ~6 ms on 26k events); same edit format.  Elements compare as given (list vs tuple unequal
    just makes the splice bigger, never wrong)."""
    A=old['program']; Bp=new['program']; n=min(len(A),len(Bp)); i=_lcp(A,Bp,n)
    j=_lcs(A,Bp,n-i)                                   # common suffix (not overlapping the prefix)
    ops=[]; fo,fn=old['frames'],new['frames']
    if len(fn)<len(fo): raise ValueError('frames shrink')
    for f in range(len(fo)):
        if list(fo[f])!=list(fn[f]): ops.append(['frame_set',f,list(fn[f])])
    for f in range(len(fo),len(fn)): ops.append(['frame_add',list(fn[f])])
    if i<len(A)-j or i<len(Bp)-j: ops.append(['splice',i,len(A)-j,[tuple(e) for e in Bp[i:len(Bp)-j]]])
    io,in_,fo_,fn_=old['initial'],new['initial'],old['final'],new['final']
    if io!=in_ or fo_!=fn_:
        for r in range(len(io)):
            if io[r]!=in_[r]: ops.append(['initial',r,in_[r]])
            if fo_[r]!=fn_[r]: ops.append(['final',r,fn_[r]])
    return dict(ops=ops)
def _make_iw(word):
    """IncrWord, or under TK_NATIVE_CORE=1 the bit-identical C-kernel subclass (native/nincr.py; falls back to the Python class if the kernel cannot be built)"""
    if os.environ.get('TK_NATIVE_CORE')=='1':
        from native.nincr import make_incr
        return make_incr(word)
    return incr.IncrWord(word)
class IncrEvaluator:
    name='incr'      # TK_NATIVE_CORE=1: same evaluator on native.nincr.NIncrWord
    def __init__(s,resync=200,log=print):
        s.iw=None; s.word=None; s._pend=None; s.commits=0; s.resync_every=resync; s.nresync=0; s.nfull=0; s.ntry=0; s.nbind=0; s.log=log; s.t_try=0.0
    def bind(s,word):
        s.iw=_make_iw(word); s.word=word; s._pend=None; s.nbind+=1
    def _ok_of(s,c):
        """side + budgets of the candidate state c (incr _Cand) -> dict"""
        iw=s.iw; T,P=iw._invoice(c.paid,c.hel); sd=side_of(T,P,iw.pr)
        rep=dict(nevents=sum(len(ch.evs) for ch in c.chs),helpers=dict(c.hel),paid=dict(c.paid),scalar=sum(ch.scalar for ch in c.chs),lifetimes=sum(ch.life for ch in c.chs))
        b=X.budgets(rep)
        return dict(side_ok=sd['ok'],ev_slack=b['event_slack'],sc_slack=b['scalar_budget_slack'],ok=bool(sd['ok'] and b['event_slack']>=0 and b['scalar_budget_slack']>=0))
    def try_word(s,base,cand):
        if s.word is not base: s.bind(base)
        s.ntry+=1; t=time.time()
        try: ie=fast_diff_edit(base,cand)
        except (ValueError,IndexError,KeyError):
            s._pend=None; return dict(ok=False,legal=False,why='diff_edit',incr=True)
        r=s.iw.try_edit(ie,fast=bool(s.iw.legal_all)); s.t_try+=time.time()-t
        if not r[0]:
            s._pend=None; return dict(ok=False,legal=False,why=r[2],incr=True)
        o=dict(legal=True,kappa=r.kappa,incr=True,**s._ok_of(r.cand)); s._pend=(cand,ie,o); return o
    def try_sedit(s,base,se):
        """REALISEFIX: as try_word for an explicit window edit (sedit.SEdit against the View of `base`): no candidate word, no diff.  Call bind_cand(se, word) once the word is built to make adopt() commit it."""
        if s.word is not base: s.bind(base)
        s.ntry+=1; t=time.time()
        try: r=s.iw.try_edit(se,fast=bool(s.iw.legal_all))
        except (ValueError,IndexError,KeyError):
            s._pend=None; s._pend_se=None; return dict(ok=False,legal=False,why='sedit',incr=True)
        s.t_try+=time.time()-t
        if not r[0]:
            s._pend=None; s._pend_se=None; return dict(ok=False,legal=False,why=r[2],incr=True)
        o=dict(legal=True,kappa=r.kappa,incr=True,**s._ok_of(r.cand)); s._pend=None; s._pend_se=(se,o); return o
    def bind_cand(s,se,word):
        p=getattr(s,'_pend_se',None)
        if p is not None and p[0] is se: s._pend=(word,se,p[1])
    def evaluate(s,word,edit=None,base=None):
        if base is not None: return s.try_word(base,word)
        s.nfull+=1; return M.evaluate(word)             # arbitrary word (start word, screen output): full path, state untouched
    def adopt(s,w):
        if s.word is w: return
        p=s._pend
        if p is not None and p[0] is w and p[2].get('legal'):
            s.iw.commit(p[1]); s.word=w; s._pend=None; s.commits+=1
            if s.resync_every and s.commits%s.resync_every==0: s.check_sync()
        else: s.bind(w)
    def check_sync(s,log=None):
        """full check of the committed word vs the incremental state (the periodic resync + at every new best)"""
        o=M.evaluate(s.word); s.nresync+=1
        if not o.get('legal') or abs(o['kappa']-s.iw.kappa)>1e-15 or not s.iw.legal_all:
            raise RuntimeError('INCR/FULL MISMATCH: full legal=%s kappa=%r (%s) incr kappa=%r legal_all=%s'%(o.get('legal'),o.get('kappa'),o.get('why'),s.iw.kappa,s.iw.legal_all))
        return o
