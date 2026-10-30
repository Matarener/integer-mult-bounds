#!/usr/bin/env python3
"""Differential fuzzer for incr.IncrWord (INCR).
usage: incr_fuzz.py [--words 5551,5580,...] [--n EDITS_PER_WORD] [--seed S] [--commit-p 0.3] [--bench] [--native-full K] [--accept K] [--out FILE.jsonl]
Each random edit (legal and illegal, 1-3 composed ops of ~14 classes) is evaluated by IncrWord.try_edit and, independently, by the full path on the edited word:
legal.check (all violations: index+rule), check.native-pair logic (set of bad frame-index pairs), price_exact.invoice (T,P ledgers) and X.kappa.
Equality required: exception flag, violation list [(idx,rule)] (first 50), bad native pair set, ledgers exactly, kappa within 1e-15, legal verdict.
Some edits are committed (then the committed program/frames/finals must equal the reference word exactly).  --native-full K additionally calls the real
`check.native_check` (cold fastnative init, ~10 s) every K edits; --accept K runs `tk accept` on K committed legal words and compares with incr's verdict.
Exit 1 on any mismatch (details to stderr/--out)."""
import sys,os,json,time,random,copy,argparse
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD)
from tkcommon import *
import incr,check as CK
WORDS=[('5551',None),('5580',None),('5599',None),('5660',None),('5718','5718'),('5751','5751')]
NC_WORDS=['5551','5580','5599','5660','5718','5751','5786','5795']      # --native-core default (5786/5795: profile auto-selected by tkcommon.profile_of; 5795 has no alias -> path)
def spec_of(name):
    p=os.path.join(TKD,'words','%s.json.gz'%name)
    try: load(name); return name
    except SystemExit: return os.path.abspath(p)
def basis_span_vecs(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
class Gen:
    def __init__(s,iw,rnd): s.iw=iw; s.r=rnd
    def pos(s,prog,kinds=None,tries=200):
        for _ in range(tries):
            i=s.r.randrange(len(prog))
            if kinds is None or prog[i][0] in kinds: return i
        return s.r.randrange(len(prog))
    def swap(s,prog):
        i=s.r.randrange(len(prog)-1); return [['mv',i,i+1]]
    def mvnear(s,prog):
        i=s.r.randrange(len(prog)); j=min(max(i+s.r.randint(-40,40),0),len(prog)-1); return [['mv',i,j]]
    def mvfar(s,prog):
        i=s.r.randrange(len(prog)); return [['mv',i,s.r.randrange(len(prog))]]
    def retimemove(s,prog):
        i=s.pos(prog,('MOVE',)); j=min(max(i+s.r.choice([-1,1])*s.r.randint(1,300),0),len(prog)-1); return [['mv',i,j]]
    def delete(s,prog):
        i=s.pos(prog,s.r.choice([('ADD',),('MOVE',),('SCALE',),('INIT','CLEAR','COPY'),None])); return [['del',i]]
    def cancelpair(s,prog):
        i=s.pos(prog,('ADD',)); e=list(prog[i]); q=s.r.choice(['1','-1','2','1/2','-1/2','3','1/4','5/8','4','1/3'])
        e1=e[:]; e1[-2]=q; e2=e[:]; e2[-2]=('-'+q) if not q.startswith('-') else q[1:]
        j=min(i+s.r.choice([0,0,1,5,50]),len(prog)); return [['ins',i,e1],['ins',j+1 if j>=i else i+1,e2]]
    def coef(s,prog):
        i=s.pos(prog,('ADD','SCALE')); e=list(prog[i]); e[-2]=s.r.choice(['1','-1','2','-2','1/2','3','1/3','7/4','0']); return [['set',i,e]]
    def retarget(s,prog):
        i=s.pos(prog,s.r.choice([('ADD',),('SCALE',),('MOVE',),('ADD','COPY','SCALE','MOVE')])); n=s.iw.NPUB
        r=s.r.choice([prog[i][1]+s.r.choice([-1,1]),s.r.randrange(n),s.r.randrange(s.iw.NR),s.r.randrange(n+s.iw.NO+2)]); return [['retarget',i,r]]
    def srcchange(s,prog):
        i=s.pos(prog,('ADD',)); e=list(prog[i]); e[2]=s.r.choice([e[2]+1,e[2]-1,s.r.randrange(s.iw.NR)]); return [['set',i,e]]
    def subdivide(s,prog):
        bases=s.iw.ctx.bases
        for _ in range(300):
            i=s.pos(prog,('MOVE',)); e=prog[i]; r,a,b,pv=e[1],e[2],e[3],e[4]
            lo,hi=(b,a) if pv else (a,b)       # span(lo) < span(hi)
            sl=basis_span_vecs(bases[lo]); extra=[v for v in bases[hi] if v not in sl]
            if len(extra)<2: continue
            # extra vectors of hi's basis not already in span(lo): choose a proper non-empty subset
            k=s.r.randint(1,len(extra)-1); sub=s.r.sample(extra,k)
            # make sure basis(lo)+sub is independent and inside span(hi): true since they are hi basis vectors outside span(lo) (greedy independence)
            cb=list(bases[lo]); sp=set(sl)
            for v in sub:
                if v not in sp: cb.append(v); sp|={x^v for x in sp}
            if len(cb)==len(bases[lo]) or len(cb)>=len(bases[hi]): continue
            c=len(bases)
            if pv: m1=['MOVE',r,a,c,pv]; m2=['MOVE',r,c,b,pv]
            else: m1=['MOVE',r,a,c,pv]; m2=['MOVE',r,c,b,pv]
            if pv: cb=cb      # descending move a->b with span(b)<span(a): the chain a->c->b needs span(b)<span(c)<span(a); c built from lo=b upward: fine
            return [['frame_add',cb],['set',i,m1],['ins',i+1,m2]]
        return s.swap(prog)
    def merge(s,prog):
        for _ in range(400):
            i=s.pos(prog,('MOVE',))
            for j in range(i+1,min(i+120,len(prog))):
                f=prog[j]
                if f[0]=='MOVE' and f[1]==prog[i][1]:
                    if f[2]==prog[i][3]:
                        e=prog[i]; return [['del',j],['set',i,['MOVE',e[1],e[2],f[3],e[4]]]]
                    break
        return s.swap(prog)
    def movetarget(s,prog):
        i=s.pos(prog,('MOVE',)); e=list(prog[i]); e[s.r.choice([2,3])]=s.r.choice([s.r.randrange(len(s.iw.ctx.bases)),e[2]+1,e[3]-1,e[3]]); return [['set',i,e]]
    def flipdir(s,prog):
        i=s.pos(prog,('MOVE',)); e=list(prog[i]); e[4]=not e[4]; return [['set',i,e]]
    def framebasis(s,prog):
        bases=s.iw.ctx.bases; f=s.r.randrange(len(bases)); b=list(bases[f])
        if len(b)>=2 and s.r.random()<0.85:
            x,y=s.r.sample(range(len(b)),2); b[x]=b[x]^b[y]                 # same span, other basis
            if s.r.random()<0.3: s.r.shuffle(b)
        elif b and s.r.random()<0.5: b[s.r.randrange(len(b))]=s.r.randrange(1,512)
        else: b.append(s.r.randrange(1,512))
        return [['frame_set',f,b]]
    def finalset(s,prog):
        n=s.iw.NPUB; r=s.r.randrange(n)
        if s.r.random()<0.6: r=s.r.choice([x for x in range(n) if x not in s.iw.main] or [r])
        f=s.r.choice([s.iw.initial[r],s.iw.final[r],s.r.randrange(len(s.iw.ctx.bases)),s.iw.final[s.r.randrange(n)]]); return [[s.r.choice(['final','initial']),r,f]]
    def lifemove(s,prog):
        i=s.pos(prog,('INIT','CLEAR','COPY')); j=min(max(i+s.r.randint(-60,60),0),len(prog)-1); return [['mv',i,j]]
    def spliceblock(s,prog):
        i=s.r.randrange(len(prog)-20); L=s.r.randint(1,12); blk=prog[i:i+L]
        if s.r.random()<0.5: return [['splice',i,i+L,[b for b in reversed(blk)]]]
        return [['splice',i,i+L,[b for b in blk]+[blk[0]]]]
    weird_on=False
    def weird(s,prog):
        """events outside the packed representation (NATIVE arm only: exercises the per-chunk Python fallback; compared against IncrWord, not the reference)"""
        from fractions import Fraction
        i=s.pos(prog,('ADD','SCALE','MOVE','COPY','INIT','CLEAR')); e=list(prog[i]); k=s.r.randrange(12); n=s.iw.NR
        if k==0 and e[0] in('ADD','COPY'): e[-2]='abc'
        elif k==1 and e[0] in('ADD','COPY','SCALE'): e[0]='FOO'
        elif k==2 and e[0]=='MOVE': e=e[:4]
        elif k==3 and e[0] in('ADD','COPY','SCALE'): e[-2]=Fraction(s.r.choice([1,-1,2,3]),s.r.choice([1,2,3,4]))
        elif k==4 and e[0] in('ADD','COPY','SCALE'): e[-1]=1.5
        elif k==5 and e[0]=='MOVE': e[2]=None
        elif k==6: e[1]=s.r.choice([-1,n,10**12,2**40,-2**31,3.0])
        elif k==7 and e[0] in('ADD','COPY','SCALE'): e[-2]=s.r.choice([0.5,2,True,1.0])
        elif k==8 and e[0]=='MOVE': e[s.r.choice([2,3])]=s.r.choice([2**31,-2**31,10**20,-1,-2,len(s.iw.ctx.bases),-len(s.iw.ctx.bases)])
        elif k==9 and e[0] in('ADD','COPY'): e[2]=s.r.choice([e[1],-1,n,10**12,2**33])
        elif k==10 and e[0] in('INIT','CLEAR'): e[2]=s.r.choice([-1,0,1,5,n])
        elif k==11 and e[0]=='MOVE': e[4]=s.r.choice([0,1,2,None,'x',[]])
        else: return s.swap(prog)
        return [['set',i,tuple(e)]]
    def make(s,prog):
        if s.weird_on and s.r.random()<0.08: return dict(ops=s.weird(prog),name='weird')
        gens=[(s.swap,3),(s.mvnear,3),(s.mvfar,1),(s.retimemove,4),(s.delete,1),(s.cancelpair,3),(s.coef,2),(s.retarget,1),(s.srcchange,1),(s.subdivide,6),(s.merge,3),
              (s.movetarget,1),(s.flipdir,1),(s.framebasis,2),(s.finalset,1),(s.lifemove,1),(s.spliceblock,1)]
        g=s.r.choices([g for g,_ in gens],[w for _,w in gens])[0]; ops=g(prog); name=g.__name__
        if s.r.random()<0.2:
            g2=s.r.choices([g for g,_ in gens],[w for _,w in gens])[0]
            if g2.__name__ not in('subdivide','merge','framebasis'):        # secondary ops are index-based: generated against the program as it is after ops
                w2=incr.apply_edit_to_word({'program':[list(e) for e in prog],'frames':[],'initial':[],'final':[]},{'ops':[o for o in ops if o[0] not in('frame_add','frame_set','initial','final')]}) if all(o[0] in('ins','del','set','mv','retarget','splice') for o in ops) else None
                if w2 is not None: ops=ops+g2(w2['program']); name+='+'+g2.__name__
        return dict(ops=ops,name=name)
class FakeN:
    def __init__(s,N,keep): s.N=N; s.keep=keep
    def ok(s,x,y):
        x,y=tuple(x),tuple(y)
        if (x,y) not in s.keep and hash((x,y))%3==0: return (False,'fake')
        return s.N.ok(x,y)
class Ref:
    """full-path reference on a plain word dict (the toolkit's own functions, nothing from incr)"""
    def __init__(s,profile):
        s.profile=profile; s.N=native_mod()
    def native(s,w,prog):
        fr=w['frames']; bad=set(); nb=0; seen={}
        def test(a,b):
            nonlocal nb
            k=(a,b)
            if k not in seen: seen[k]=s.N.ok(tuple(fr[a]),tuple(fr[b]))
            if not seen[k][0]: bad.add(k); nb+=1
        main=set(w['live'])|{r+112 for r in w['live']}
        for e in prog:
            if e[0]=='MOVE': test(e[2],e[3])
        for r in range(len(w['initial'])):
            if r not in main: test(w['initial'][r],w['final'][r])
        return bad,nb
    def run(s,w):
        out=dict(exc=None)
        with use_profile(s.profile):
            try:
                rep=legal.check(w); T,Pp=X.invoice(rep); out.update(viol=[(i,r) for i,r,_ in rep['violations']],ok=rep['ok'],T=T,P=Pp,kappa=X.kappa(T,Pp),rep=rep)
                bad,nb=s.native(w,w['program']); out.update(badpairs=bad,nbad=nb)
            except (IndexError,ValueError,TypeError,KeyError,AttributeError) as ex: out['exc']=type(ex).__name__
        return out
def compare(res,ref,iw,ctx=None):
    errs=[]
    if res.exception or ref['exc']:
        if bool(res.exception)!=bool(ref['exc']): errs.append('exception mismatch incr=%s ref=%s'%(res.exception and res.reason,ref['exc']))
        return errs
    c=res.cand
    iv=[(i,r) for i,r,_ in c.viol[:50]]
    if iv!=ref['viol']: errs.append('violations differ incr=%s ref=%s'%(iv[:4],ref['viol'][:4]))
    if set(c.bad_pairs)!=ref['badpairs']: errs.append('native bad pairs differ incr=%s ref=%s'%(sorted(c.bad_pairs)[:4],sorted(ref['badpairs'])[:4]))
    T,Pp=iw._invoice(c.paid,c.hel)
    if (T,Pp)!=(ref['T'],ref['P']): errs.append('ledger differs')
    if abs(c.kappa-ref['kappa'])>1e-15: errs.append('kappa differs %r vs %r'%(c.kappa,ref['kappa']))
    if res.legal!=(ref['ok'] and ref['nbad']==0): errs.append('verdict differs')
    return errs
def cmp3(res,nres,iw,nw):
    """third arm: NIncrWord result vs IncrWord result for the same edit -- EXACT equality (no tolerance)"""
    e=[]
    if bool(res.exception)!=bool(nres.exception): return ['exception flag python=%s native=%s (%s | %s)'%(res.exception,nres.exception,res.reason,nres.reason)]
    if res.exception:
        if res.reason!=nres.reason: e.append('exception text python=%s native=%s'%(res.reason,nres.reason))
        return e
    if res.legal!=nres.legal: e.append('verdict')
    if res.reason!=nres.reason: e.append('reason %r vs %r'%(res.reason,nres.reason))
    if res.early!=nres.early or res.native_bad!=nres.native_bad: e.append('early/native_bad')
    c,d=res.cand,nres.cand
    if c.viol!=d.viol: e.append('violation list differs python=%s native=%s'%(c.viol[:3],d.viol[:3]))
    if c.bad_pairs!=d.bad_pairs: e.append('bad pairs')
    if (+c.paid)!=(+d.paid) or (+c.hel)!=(+d.hel): e.append('ledger counters')
    if iw._invoice(c.paid,c.hel)!=nw._invoice(d.paid,d.hel): e.append('invoice')
    if c.kappa!=d.kappa or res.dk!=nres.dk: e.append('kappa %r vs %r'%(c.kappa,d.kappa))
    if c.n!=d.n: e.append('event count')
    return e
def cmp_state(iw,nw):
    e=[]
    if iw.program()!=nw.program() or iw.ctx.bases!=nw.ctx.bases or iw.initial!=nw.initial or iw.final!=nw.final: e.append('committed word')
    if iw.viol!=nw.viol or iw.bad_pairs!=nw.bad_pairs or iw.kappa!=nw.kappa or iw.legal_all!=nw.legal_all: e.append('committed viol/kappa')
    if (+iw.paid)!=(+nw.paid) or (+iw.hel)!=(+nw.hel) or +iw.pairs!=+nw.pairs: e.append('committed ledgers')
    if len(iw.chs)!=len(nw.chs) or any(a.viol!=b.viol or a.paid!=b.paid or (a.scalar,a.life,a.peak)!=(b.scalar,b.life,b.peak) for a,b in zip(iw.chs,nw.chs)): e.append('committed chunk records')
    if nw._decode(nw.endstate)!=iw.endstate: e.append('committed end state')
    return e
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--words',default=None); ap.add_argument('--n',type=int,default=300); ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--commit-p',type=float,default=0.3); ap.add_argument('--bench',action='store_true'); ap.add_argument('--fast',action='store_true'); ap.add_argument('--fake-native',action='store_true',help='deterministically fail 1/3 of the NEW native pairs (exercises the pair ledger on replay-legal edits)'); ap.add_argument('--native-full',type=int,default=0); ap.add_argument('--accept',type=int,default=0)
    ap.add_argument('--free-bounds',action='store_true',help='set TK_FREE_BOUNDS=1 (reference and incr both)'); ap.add_argument('--out'); ap.add_argument('--time',type=float,default=0,help='stop a word after this many seconds'); ap.add_argument('--quiet',action='store_true')
    ap.add_argument('--native-core',action='store_true',help='third arm: native.nincr.NIncrWord run in lockstep with IncrWord (same edits/commits); every edit must agree EXACTLY (verdict, reason, full violation list incl. details, ledgers, bad pairs, kappa ==)')
    ap.add_argument('--native-only',action='store_true',help='skip the full-path reference: compare only NIncrWord vs IncrWord (fast dev loop)')
    a=ap.parse_args()
    if a.words is None: a.words=','.join(NC_WORDS if a.native_core else [x for x,_ in WORDS])
    if a.native_only: a.native_core=True
    if a.free_bounds: os.environ['TK_FREE_BOUNDS']='1'
    nincr=None
    if a.native_core:
        sys.path.insert(0,HERE+'/..'); from native import nincr
    prof=dict(WORDS); fails=0; total=0; out=open(a.out,'a') if a.out else None
    for name in a.words.split(','):
        pf=prof.get(name); rnd=random.Random(a.seed*1000+int(name[:4]))
        sp=spec_of(name); iw=incr.IncrWord(sp,profile=pf); ref=Ref(iw.profile); base=iw.to_word(); nw=nincr.NIncrWord(sp,profile=pf) if a.native_core else None
        if nw is not None: print('%s: profile %s, %d events, NR %d'%(name,iw.profile,len(iw.program()),iw.NR),flush=True)
        if a.fake_native:
            if nw is not None: print('--fake-native not supported with --native-core',file=sys.stderr); return 2
            orig_pairs={(iw.ctx.bases[x],iw.ctx.bases[y]) for x,y in iw.pairs}; fakeN=FakeN(ref.N,orig_pairs); ref.N=fakeN; iw._nat.N=fakeN; iw._nat.disk={}
        if nw is not None: nw._nat=iw._nat
        nbadedits=[0,0]; illegal_since=None; orig=iw.to_word(); nfast=cfast=0; tfast=0.0; gen=Gen(iw,rnd); gen.weird_on=a.native_only; stats={}; t_inc=t_ref=0.0; t_pyw=t_nat=0.0; n3=0; t0=time.time(); ncommit=0; nacc=0; wf=0
        for n in range(a.n):
            if a.time and time.time()-t0>a.time: break
            prog=iw.program(); edit=gen.make(prog)
            t=time.perf_counter(); res=iw.try_edit(edit,fast=a.fast and a.bench); dt=time.perf_counter()-t; t_inc+=dt
            st=stats.setdefault(edit['name'],[0,0,0,0.0]); st[0]+=1; st[1]+=bool(res.legal); st[3]+=dt*1e3
            if not res.exception and res.native_bad: nbadedits[0]+=1; nbadedits[1]+=(not res.viol)
            if a.bench: continue
            if nw is not None:
                tp=time.perf_counter(); iw.try_edit(edit); t_pyw+=time.perf_counter()-tp          # warm python timing (native pair verdicts shared and cached)
                tn=time.perf_counter(); nres=nw.try_edit(edit); t_nat+=time.perf_counter()-tn; n3+=1
                e3=cmp3(res,nres,iw,nw)
                if iw.legal_all and n%3==0:
                    r1=iw.try_edit(edit,fast=True); r2=nw.try_edit(edit,fast=True)
                    if (r1.legal,r1.reason,r1.early,r1.exception)!=(r2.legal,r2.reason,r2.early,r2.exception) or (r1.legal and (r1.kappa!=r2.kappa)): e3.append('fast mode python=%s native=%s'%((r1.legal,r1.reason,r1.early),(r2.legal,r2.reason,r2.early)))
                    iw.try_edit(edit); nw.try_edit(edit)
                if e3:
                    wf+=1; fails+=1; st[2]+=1; print('MISMATCH native-core',json.dumps(dict(word=name,n=n,seed=a.seed,edit=edit,errs=e3),default=str)[:1500],file=sys.stderr,flush=True)
                    if out: out.write(json.dumps(dict(word=name,n=n,seed=a.seed,edit=edit,errs=e3,arm='native'),default=str)+'\n'); out.flush()
                if a.native_only:
                    if res.exception: continue
                    do=res.legal and rnd.random()<a.commit_p or (not res.legal and rnd.random()<0.02)
                    if illegal_since is not None and n-illegal_since>=12:
                        iw=incr.IncrWord(orig,profile=pf); nw=nincr.NIncrWord(orig,profile=pf); nw._nat=iw._nat
                        gen=Gen(iw,rnd); gen.weird_on=a.native_only; illegal_since=None; continue
                    if do:
                        iw.commit(edit); nw.commit(edit); ncommit+=1
                        if not iw.legal_all and illegal_since is None: illegal_since=n
                        e4=cmp_state(iw,nw)
                        if ncommit%25==0:
                            nw2=nincr.NIncrWord(iw.to_word(),profile=pf); nw2._nat=iw._nat
                            if nw2.viol!=nw.viol or abs(nw2.kappa-nw.kappa)>1e-15 or +nw2.paid!=+nw.paid or nw2.pairs!=nw.pairs or nw2.endstate!=nw.endstate: e4.append('committed state differs from fresh NIncrWord')
                        if e4: wf+=1; fails+=1; print('MISMATCH native-core commit',name,n,e4,file=sys.stderr,flush=True)
                    continue
            t=time.perf_counter()
            try: w2=incr.apply_edit_to_word(base,edit); r=ref.run(w2)
            except (IndexError,ValueError,TypeError,KeyError) as ex: w2=None; r=dict(exc='apply:'+type(ex).__name__)
            t_ref+=time.perf_counter()-t; total+=1
            if w2 is not None and not r['exc'] and iw.legal_all and n%3==0:
                tf=time.perf_counter(); rf_=iw.try_edit(edit,fast=True); t_fast=getattr(sys.modules[__name__],'T_FAST',0)
                if rf_.legal!=res.legal or (rf_.early and rf_.reason!=(r['rep']['violations'][0][1] if r['rep']['violations'] else None)) or (not rf_.early and (rf_.reason!=res.reason or abs(rf_.kappa-res.kappa)>1e-15 if res.legal else rf_.reason!=res.reason)):
                    wf+=1; fails+=1; print('MISMATCH fast mode',name,n,edit['name'],rf_.reason,res.reason,file=sys.stderr,flush=True)
                st.append(0) if False else None
                nfast+=rf_.early; tfast+=time.perf_counter()-tf; cfast+=1
                iw.try_edit(edit)
            errs=compare(res,r,iw) if w2 is not None or res.exception else (['incr accepted an edit the reference cannot apply'] if not res.exception else [])
            if errs:
                wf+=1; fails+=1; st[2]+=1
                rec=dict(word=name,n=n,seed=a.seed,edit=edit,errs=errs)
                print('MISMATCH',json.dumps(rec,default=str)[:1500],file=sys.stderr,flush=True)
                if out: out.write(json.dumps(rec,default=str)+'\n'); out.flush()
            if res.exception or w2 is None: continue
            do=res.legal and rnd.random()<a.commit_p or (not res.legal and rnd.random()<0.02)
            if illegal_since is not None and n-illegal_since>=12:
                iw=incr.IncrWord(orig,profile=pf)
                if nw is not None: nw=nincr.NIncrWord(orig,profile=pf); nw._nat=iw._nat
                if a.fake_native: iw._nat.N=fakeN; iw._nat.disk={}
                base=orig; gen=Gen(iw,rnd); gen.weird_on=a.native_only; illegal_since=None; continue
            if do:
                iw.commit(edit); base=w2; ncommit+=1
                if nw is not None:
                    nw.commit(edit); e4=cmp_state(iw,nw)
                    if e4: wf+=1; fails+=1; print('MISMATCH native-core commit',name,n,e4,file=sys.stderr,flush=True)
                if not iw.legal_all and illegal_since is None: illegal_since=n
                if [list(map(lambda x:x,e)) for e in iw.program()]!=[list(e) for e in base['program']] or [list(b) for b in iw.ctx.bases]!=[list(b) for b in base['frames']] or iw.initial!=base['initial'] or iw.final!=base['final']:
                    wf+=1; fails+=1; print('MISMATCH committed word differs',name,n,file=sys.stderr,flush=True)
                # state after commit must equal a from-scratch IncrWord on the committed word
                if ncommit%25==0:
                    iw2=incr.IncrWord(base,profile=pf)
                    if (iw2.paid+collections.Counter()!=iw.paid+collections.Counter()) or iw2.viol!=iw.viol or iw2.bad_pairs!=iw.bad_pairs or abs(iw2.kappa-iw.kappa)>1e-15 or iw2.pairs!=iw.pairs:
                        wf+=1; fails+=1; print('MISMATCH committed state differs from fresh IncrWord',name,n,file=sys.stderr,flush=True)
                if a.accept and nacc<a.accept and iw.legal_all and iw.side()['ok']:
                    nacc+=1; ra=iw.accept(); ok_inc=iw.legal_all and iw.side()['ok'] and iw.budgets()['scalar_budget_slack']>0
                    if bool(ra.get('ok'))!=ok_inc: wf+=1; fails+=1; print('MISMATCH accept',name,n,ra.get('stage'),ra.get('error'),file=sys.stderr,flush=True)
                    else: print(' accept agrees (ok=%s) on committed word %s #%d'%(ra.get('ok'),name,n),flush=True)
            if a.native_full and n%a.native_full==a.native_full-1 and w2 is not None:
                p_=tempfile_path(base)
                with use_profile(iw.profile): rr=CK.native_check(base,base['program'],roles(base))
                rf=ref.run(base)
                if (rr['nbad']>0)!=(rf['nbad']>0) : wf+=1; fails+=1; print('MISMATCH native_check vs reference',name,n,file=sys.stderr,flush=True)
        iw.flush()
        if nw is not None and n3: print('  native-core arm: %d edits compared | python cold %.2f ms/edit, python warm %.2f ms/edit, native %.2f ms/edit (x%.2f vs warm python) | fallback chunks %d of %d runs'%(n3,1e3*t_inc/max(1,n3),1e3*t_pyw/n3,1e3*t_nat/n3,t_pyw/max(1e-9,t_nat),nw._fallbacks,nw._nruns),flush=True)
        if cfast: print('  fast mode: %d edits compared, %d early rejects, %.2f ms/edit'%(cfast,nfast,1e3*tfast/cfast))
        if not a.quiet:
            print('%s: %d edits (%d with bad native pairs, %d of them replay-legal), %d mismatches, %d commits | incr %.2f ms/edit%s | classes(n,legal,mismatch,ms): %s'%(name,sum(v[0] for v in stats.values()),nbadedits[0],nbadedits[1],wf,ncommit,1e3*t_inc/max(1,sum(v[0] for v in stats.values())),
                  '' if a.bench else ' | reference %.0f ms/edit | speedup x%.0f'%(1e3*t_ref/max(1,total_w(stats)),t_ref/max(1e-9,t_inc)),
                  {k:(v[0],v[1],v[2],round(v[3]/v[0],1)) for k,v in sorted(stats.items()) if '+' not in k}),flush=True)
        if out: out.write(json.dumps(dict(word=name,summary=dict(edits=sum(v[0] for v in stats.values()),mismatches=wf,commits=ncommit,ms_incr=1e3*t_inc/max(1,sum(v[0] for v in stats.values())),ms_ref=(1e3*t_ref/max(1,total_w(stats))) if not a.bench else None,classes=stats),seed=a.seed))+'\n'); out.flush()
    print('TOTAL mismatches',fails,'over',total,'reference-compared edits')
    return 1 if fails else 0
def total_w(stats): return sum(v[0] for v in stats.values())
def tempfile_path(w): return None
import collections
if __name__=='__main__': sys.exit(main())
