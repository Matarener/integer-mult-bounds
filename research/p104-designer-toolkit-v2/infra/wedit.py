"""EXACTNESS-PRESERVING WORD EDITOR (value-DAG level) for P104-family words.  Every edit returns a NEW Word; nothing is
trusted: call .verify() -> (legal report, exact kappa, tail/budget side checks)  [legal.py + price_exact.py, ~0.3 s].
Primitives:
  W.add_helper(init_frame, final_frame)  -> (W2, idx)   fresh independent register (owned ids shift by 1; identity until events added)
  W.insert(i, ev) / W.delete(i) / W.replace(i, evs)    raw event edits (ev lists as in local.py: ['ADD',dst,src,coef,frame] ...)
  W.frame(basis)                          -> frame id for a basis (adds to the table if new)
  W.relay_add(i, S)                       -> rewrite ADD(d,a,q,F)@i into  S+=q a ; d+=S ; S-=q a ; d-=S   at the same frame F
                                             (S = fresh/any helper sitting at F at that time; net map identical; +3 ADDs; the 'restore-then-subtract' cost)
  W.move_event(i, j)                      -> reposition (legal only if commuting; verify() decides)
Frames are lists of ints<512 (bases).  add_frame keeps dedup by span."""
import copy,gzip,json,sys
import legal,price_exact as X
class Word:
    def __init__(s,w): s.w=w
    @classmethod
    def load(cls,p): return cls(legal.load(p))
    def copy(s): return Word(copy.deepcopy(s.w))
    def save(s,p): json.dump(s.w,gzip.open(p,'wt'))
    def frame(s,basis):
        sp=lambda b: frozenset(legal.spans({'frames':[b]})[0])
        t=sp(basis)
        for i,b in enumerate(s.w['frames']):
            if sp(b)==t: return i
        s.w['frames'].append(list(basis)); return len(s.w['frames'])-1
    def add_helper(s,init,final):
        w2=s.copy(); w=w2.w; NH=len(w['initial'])
        sh=lambda r: r+1 if r>=NH else r
        for e in w['program']:
            e[1]=sh(e[1])
            if e[0] in('ADD','COPY'): e[2]=sh(e[2])
        w['initial'].append(init); w['final'].append(final); w['public']=NH+1
        if init!=final: w['program'].insert(_firstuse(w),['MOVE',NH,init,final,False])
        return w2,NH
    def insert(s,i,ev): w2=s.copy(); w2.w['program'].insert(i,ev); return w2
    def delete(s,i): w2=s.copy(); del w2.w['program'][i]; return w2
    def replace(s,i,evs): w2=s.copy(); w2.w['program'][i:i+1]=evs; return w2
    def relay_add(s,i,S):
        e=s.w['program'][i]; assert e[0]=='ADD'; _,d,a,q,F=e
        neg=str(-__import__('fractions').Fraction(q)) 
        return s.replace(i,[['ADD',S,a,q,F],['ADD',d,S,1,F],['ADD',S,a,neg,F],['ADD',d,S,-1,F]])
    def move_event(s,i,j):
        w2=s.copy(); p=w2.w['program']; e=p.pop(i); p.insert(j,e); return w2
    def verify(s):
        rep=legal.check(s.w); out=dict(legal=rep['ok'],violations=rep['violations'][:4],events=rep['nevents'])
        if rep['ok']:
            T,P=X.invoice(rep); out['kappa']=X.kappa(T,P); out['side']=X.side(T,P); out['budget']=X.budgets(rep)
        return out
def _firstuse(w): return len(w['program'])   # fresh helper with no events: its MOVE goes at the end
if __name__=='__main__':
    W=Word.load(sys.argv[1]); print('base',W.verify()['kappa'])
