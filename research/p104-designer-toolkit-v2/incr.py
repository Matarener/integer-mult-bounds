"""incr: incremental evaluation of local edits to a P104-family word (INCR.

    iw = IncrWord('5580')                     # alias / path / word dict;  profile=None -> tkcommon.profile_of
    r  = iw.try_edit(edit)                    # -> Result (tuple (legal, delta_kappa, reason) with attributes), the word is NOT changed
    iw.commit(edit)                           # adopt the edit (re-uses the evaluation of the last try_edit of the same object)
    iw.kappa, iw.kappa_exact(), iw.to_word(), iw.accept()

Design.  The word's program is a list of CHUNKS (~128 events).  Every chunk stores the replay state before/after it (frames per register,
owned set, K=2 random value vectors mod 2^61-1 -- exactly the state of infra/legal.check), its violations, its paid-rank census, its scalar cost,
its owned lifetimes/peak, and its native MOVE pairs.  An edit builds a new chunk list (unchanged chunks are shared), replays the touched chunks
and the following ones only until the replay state coincides again with the stored state ("convergence"), and then updates
  * the violation list (chunk violations + the global exit/endpoint/helper rules, recomputed from the end state only when it changed),
  * the paid / helper ledgers (exact integer Counters -> invoice -> Newton root; `kappa_exact()` = Decimal-50 root on demand),
  * the native pair ledger (refcounts of frame-index pairs; only pairs entering the set, or touching a changed frame, are tested by fastnative).
The replay loop is a line-for-line copy of infra/legal.check, so verdicts, reason classes, violation indices and the ledgers are identical to
`legal.check` + `check.native_check` + `price_exact.invoice` (tests/incr_fuzz.py differential-fuzzes this).

EDIT SCHEMA (JSON; positions are in the program as it is when the op is applied, ops are applied in order)
    {'ops': [op, ...], 'name': str?}  or just a list of ops
    ['splice', i, j, [ev, ...]]       replace program[i:j] by the events          ['ins', i, ev]   ['del', i]   ['set', i, ev]
    ['mv', i, j]                      event i is moved so that it ends at index j of the resulting program
    ['retarget', i, r]                register of event i (ev[1]) := r
    ['frame_add', basis]              append a frame (index = current number of frames)       ['frame_set', f, basis]  replace frame f's basis
    ['initial', r, f]  ['final', r, f]   declared frames of public register r
`diff_edit(old_word, new_word)` converts a plugin's output word (TKMOVES apply()) into such an edit."""
import sys,os,json,copy,collections,random,decimal,math,glob,time
from fractions import Fraction as Q
from bisect import bisect_right
from tkcommon import *
P=(1<<61)-1
K=2
B=128                      # chunk size
_SP={}
def _span(b):
    """span of a frame basis (tuple); same validation as legal.spans"""
    s=_SP.get(b)
    if s is None:
        s={0}
        for v in b:
            if not(type(v) is int and 0<v<512 and v not in s): raise ValueError('dependent basis '+str(list(b)))
            s|={x^v for x in s}
        s=_SP[b]=frozenset(s)
    return s
_COEF={}
_SUB={}
_HYP={}
def _coef(x):
    c=_COEF.get(x)
    if c is None:
        q=Q(x); n,d=abs(q.numerator),q.denominator
        qm=(q.numerator%P)*pow(d,P-2,P)%P
        c=(q,n,d,qm,bool(d&(d-1)),not abs(q)+1<2**16,bool(n&(n-1)),
           2*(abs(n.bit_length()-d.bit_length())+int(q<0)),2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1))
        if len(_COEF)<100000: _COEF[x]=c
    return c
class Ctx:
    """frame table view of one candidate: bases (tuples), dims, spans on demand"""
    __slots__=('bases','dim','ver')
    def __init__(s,bases,ver=0): s.bases=bases; s.dim=[len(b) for b in bases]; s.ver=ver
    def span(s,f): return _span(s.bases[f])
class Chunk:
    __slots__=('evs','start','end','viol','paid','scalar','life','peak','pairs','used')
    def __init__(s,evs):
        s.evs=evs; s.start=None; s.end=None
        pr=collections.Counter(); used=set()
        for e in evs:
            if e[0]=='MOVE': pr[(e[2],e[3])]+=1; used.add(e[2]); used.add(e[3])
        s.pairs=pr; s.used=frozenset(used)
    def fresh(s):
        c=Chunk.__new__(Chunk); c.evs=s.evs; c.pairs=s.pairs; c.used=s.used; c.start=None; c.end=None; return c
class Result(tuple):
    """(legal, delta_kappa, reason); legal = legal.check ok AND no bad native pair (== `tk check --native`)"""
    def __new__(cls,legal,dk,reason,**kw):
        o=tuple.__new__(cls,(legal,dk,reason)); o.__dict__.update(kw); o.legal=legal; o.dk=dk; o.reason=reason; return o
class _Cand: pass
class _Early(Exception): pass
def pnorm(edit):
    if isinstance(edit,dict): return edit.get('ops',[])
    return edit
class IncrWord:
    def __init__(self,word,profile=None,chunk=B,native=True):
        if isinstance(word,str): self.path,w=load(word)
        else: self.path=None; w=word
        self.profile=profile or profile_of(w)[0]
        self.B=chunk; self.use_native=native
        with use_profile(self.profile):
            self.PP=legal.profile_params(w); self.EC=self.PP['event_cap']
            _,pr=profile_of(w,self.profile); self.decay=pr['decay']; self.reserve=pr.get('reserve',1e-10); self.pr=pr
            self.NPUB=len(w['initial']); self.NO=legal.nown(w); self.NR=self.NPUB+self.NO; self.OF=legal.has_of(w)
            self.RET=frozenset(legal.retired_of(w)); self.OWN=frozenset(legal.owned_set(w)); self.prepared=bool(self.RET)
        self.w0={k:v for k,v in w.items() if k not in('program','frames','initial','final')}
        self.live=list(w['live']); self.ports=list(w['ports']); self.main=set(self.live)|{r+112 for r in self.live}
        rnd=random.Random(1); self.v0=[[rnd.randrange(P) for _ in range(self.NR)] for _ in range(K)]
        ctx=Ctx([tuple(b) for b in w['frames']])
        for f in range(len(ctx.bases)): ctx.span(f)
        self.ctx=ctx; self.initial=list(w['initial']); self.final=list(w['final'])
        self.pre_static=self._pre_static()
        prog=[tuple(e) if False else e for e in w['program']]
        self.chs=[Chunk(prog[i:i+chunk]) for i in range(0,len(prog),chunk)]
        c=self._replay_all(self.chs,ctx,self.initial_state(self.initial),0,len(self.chs))
        self._adopt_chain(self.chs)
        self._finish_init()
    # ------------------------------------------------------------------ state
    def initial_state(self,initial):
        cur=list(initial)+[None]*self.NO
        for r in self.RET:
            if 0<=r<self.NPUB: cur[r]=None
        return (tuple(cur),frozenset(),tuple(tuple(x) for x in self.v0))
    def _pre_static(self):
        V=[]; NPUB,NO=self.NPUB,self.NO
        PLO,PHI=self.PP['public_range']; OLO,OHI=self.PP['owned_range']
        if self.OF:
            if not(type(NO) is int and OLO<=NO<=OHI): V.append((-1,'Owned inventory bound',NO))
            if not(PLO<=NPUB<=PHI): V.append((-1,'Public inventory bound',NPUB))
        if self.prepared:
            w=self.w0
            iface=(w.get('fields')==self.NR and sorted(self.RET)==legal.PREPARED['retired'] and w.get('independent_public')==[r for r in range(NPUB) if r not in self.RET]
                   and w.get('owned_roles')==sorted(self.RET)+list(range(NPUB,self.NR)))
            if not iface: V.append((-1,'Exact independent and owned interface','public %d fields %s retired %s'%(NPUB,w.get('fields'),sorted(self.RET))))
        return V
    # ------------------------------------------------------------------ the replay (copy of legal.check's event loop)
    def _run(self,evs,state,ctx):
        NR=self.NR; OWN=self.OWN; fr=ctx.span; dim=ctx.dim
        cur=list(state[0]); owned=set(state[1]); val=[list(x) for x in state[2]]
        V=[]; paid={}; scalar=0; life=0; peak=0
        for i,e in enumerate(evs):
            op,r=e[0],e[1]
            if not(0<=r<NR): V.append((i,'Role index',r)); continue
            if op=='MOVE':
                _,r,a,b,pv=e
                if cur[r]!=a or ((r in owned)!=bool(pv)): V.append((i,'Transport source and ownership',(r,cur[r],a,pv)))
                ok=(fr(b)<fr(a)) if pv else (fr(a)<fr(b))
                if not ok: V.append((i,'Nested chronological transport',(r,a,b,pv)))
                k=abs(dim[b]-dim[a]); paid[k]=paid.get(k,0)+1; cur[r]=b
            elif op=='INIT':
                if not(r in OWN and r not in owned): V.append((i,'Owned initialization',r))
                life+=1; owned.add(r); n_=len(owned)
                if n_>peak: peak=n_
                for x in val: x[r]=0
                cur[r]=e[2]; scalar+=2
            elif op=='CLEAR':
                if not(r in owned and cur[r]==e[2]): V.append((i,'Owned erasure at declared frame',r))
                for x in val: x[r]=0
                cur[r]=None; owned.discard(r); scalar+=2
            else:
                q,n,d,qm,dy,grow,unit,cs,ca=_coef(e[-2]); f=e[-1]
                if not q or cur[r]!=f: V.append((i,'Scalar destination and coefficient',(r,cur[r],f))); continue
                if dy: V.append((i,'Dyadic scalar coefficient',q))
                if grow: V.append((i,'Fixed scalar growth bound',q))
                if op=='SCALE':
                    if unit: V.append((i,'Dyadic unit SCALE',q))
                    for x in val: x[r]=x[r]*qm%P
                    scalar+=cs
                else:
                    s=e[2]
                    if not(s!=r and 0<=s<NR and cur[s]==f): V.append((i,'Common scalar chart',(r,s,cur[s] if 0<=s<NR else None,f))); continue
                    if op=='COPY':
                        if not(r in owned and all(x[r]==0 for x in val)): V.append((i,'COPY into cleared owned field',r))
                        for x in val: x[r]=x[s]*qm%P
                    elif op=='ADD':
                        for x in val: x[r]=(x[r]+qm*x[s])%P
                    else: V.append((i,'Scalar opcode',op)); continue
                    scalar+=ca
        end=(tuple(cur),frozenset(owned),tuple(tuple(x) for x in val))
        return end,V,paid,scalar,life,peak
    def _fill(self,ch,state,ctx):
        end,V,paid,scalar,life,peak=self._run(ch.evs,state,ctx)
        ch.start=state; ch.end=end; ch.viol=V; ch.paid=paid; ch.scalar=scalar; ch.life=life; ch.peak=peak
    def _replay_all(self,chs,ctx,st,lo,hi):
        for k in range(lo,hi):
            self._fill(chs[k],st,ctx); st=chs[k].end
        return st
    def _adopt_chain(self,chs): pass
    def _finish_init(self):
        self.endstate=self.chs[-1].end if self.chs else self.initial_state(self.initial)
        # ledgers
        self.paid=collections.Counter()
        for ch in self.chs:
            for k,v in ch.paid.items(): self.paid[k]+=v
        self.pairs=collections.Counter()
        for ch in self.chs: self.pairs.update(ch.pairs)
        self.hpairs=self._hpairs(self.initial,self.final)
        for p,c in self.hpairs.items(): self.pairs[p]+=c
        self.hel=self._hel(self.ctx,self.initial,self.final)
        self.static_post=self._static_post(self.ctx,self.initial,self.final)
        self.bad_pairs=set()
        if self.use_native:
            self._nat=_Native()
            for p in self.pairs:
                if not self._nat.ok(self.ctx,p): self.bad_pairs.add(p)
        self.post_cache=None
        res=self._assemble(self.chs,self.ctx,self.initial,self.final,self.endstate,self.paid,self.hel,self.static_post,reuse=None)
        self.viol=res['viol']; self.post_cache=res['post']
        self.kappa=self._kappa(self.paid,self.hel,None)[0]
        self.legal_all=not self.viol and not self.bad_pairs
        self._lastcand=None
    # ------------------------------------------------------------------ ledgers / static rules
    def _hpairs(self,initial,final):
        return collections.Counter((initial[r],final[r]) for r in range(self.NPUB) if r not in self.main)
    def _hel(self,ctx,initial,final):
        dim=ctx.dim
        return collections.Counter(dim[final[r]]-dim[initial[r]] for r in range(self.NPUB) if r not in self.main and r not in self.RET)
    def _static_post(self,ctx,initial,final):
        """violations of the rules that depend on frames/initial/final only"""
        V=[]; fr=ctx.span; hel=self._hel(ctx,initial,final); live=self.live
        if not(len(live)==len(self.ports)==104 and len(self.main)==208 and (not hel or min(hel)>0)): V.append((-1,'Independent productive inputs',(len(live),len(self.main),min(hel) if hel else None)))
        bs=ctx.bases
        for r in range(self.NPUB):
            if r not in self.main and r not in self.RET:
                k=(bs[initial[r]],bs[final[r]]); s=_SUB.get(k)
                if s is None: s=_SUB[k]=fr(initial[r])<=fr(final[r])
                if not s: V.append((-1,'Helper endpoints not nested',r))
        for r,q in zip(live,self.ports):
            if bs[initial[r]]!=(q,): V.append((-1,'Literal central port',r))
            h=_HYP.get(q)
            if h is None: h=_HYP[q]=frozenset(x for x in range(512) if not (x&q).bit_count()%2)
            if fr(final[r+112])!=h: V.append((-1,'Literal output hyperplane',r))
            if len(ctx.bases[final[r]])!=9: V.append((-1,'Main X final frame (SPEC: full 9-dim space)',(r,len(bs[final[r]]))))     # FRAMEGAP: mirrors legal.check
            if len(bs[initial[r+112]])!=0: V.append((-1,'Main Y initial frame (SPEC: 0-dim)',(r+112,len(bs[initial[r+112]]))))
        return V
    def _assemble(self,chs,ctx,initial,final,end,paid,hel,static_post,reuse):
        """global violation list in legal.check order -> dict(viol, post=cached end-state rules)"""
        V=[]
        n=sum(len(c.evs) for c in chs)
        if n>=self.EC: V.append((-1,'Fixed operation bound','%d>=%d'%(n,self.EC)))
        V.extend(self.pre_static)
        off=0
        for ch in chs:
            if ch.viol: V.extend((off+i,r,d) for i,r,d in ch.viol)
            off+=len(ch.evs)
        peak=max((c.peak for c in chs),default=0); life=sum(c.life for c in chs)
        post=None
        key=(end,tuple(final),peak,life)
        if reuse is not None and reuse[0]==key: post=reuse[1]
        else: post=self._post(end,final,peak,life)
        V.extend(post); V.extend(static_post)
        return dict(viol=V,post=(key,post),n=n)
    def _post(self,end,final,peak,life):
        cur,owned,val=end; V=[]; NPUB,NO,RET=self.NPUB,self.NO,self.RET; PP=self.PP; prepared=self.prepared; OF=self.OF
        wantpeak=PP['peak'] if prepared else 1
        if OF and not prepared:
            if owned or not(0<peak<=PP['peak']): V.append((-1,'All public and owned exits','owned=%s peak=%d (need 1..%d)'%(sorted(owned),peak,PP['peak'])))
        elif owned or peak!=wantpeak: V.append((-1,'All public and owned exits','owned=%s peak=%d (need %d)'%(sorted(owned),peak,wantpeak)))
        if prepared and life!=PP['lifetimes']: V.append((-1,'Complete owned lifetime census','%d lifetimes (need %d)'%(life,PP['lifetimes'])))
        if OF and not prepared and (NPUB,NO,life,peak)!=(PP['public'],PP['owned_fields'],PP['lifetimes'],PP['peak']):
            V.append((-1,'Complete public and owned inventories','(public,owned_fields,lifetimes,peak)=%s need %s'%((NPUB,NO,life,peak),tuple(PP.values()))))
        if [cur[r] for r in range(NPUB) if r not in RET]!=[final[r] for r in range(NPUB) if r not in RET]:
            V.append((-1,'Final frames','%d registers differ: %s'%(sum(1 for r,(a,b) in enumerate(zip(cur,final)) if a!=b and r not in RET),[(i,a,b) for i,(a,b) in enumerate(zip(cur,final)) if a!=b and i not in RET][:12])))
        live=set(self.live); v0=self.v0; nbad=0; badr=[]
        for r in range(self.NR):
            for k in range(K):
                ex=v0[k][r] if (r<NPUB and r not in RET) else 0
                if r-112 in live and r<NPUB: ex=(ex+v0[k][r-112])%P
                if val[k][r]!=ex: nbad+=1; badr.append(r); break
        if nbad: V.append((-1,'Endpoint rows (random evaluation)','%d rows differ: %s'%(nbad,badr[:12])))
        return V
    # ------------------------------------------------------------------ pricing
    def _invoice(self,paid,hel):
        return X.invoice(dict(paid=dict(sorted((k,v) for k,v in paid.items() if v)),helpers=dict(sorted(hel.items()))))
    def _kappa(self,paid,hel,guess):
        T,Pp=self._invoice(paid,hel)
        if guess is not None and min(min(T),min(Pp))>=0:
            k=guess
            for _ in range(20):
                e=1-k; F=dF=0.0
                for r,n in T.items():
                    if r>0: t=n*r**e; F+=t; dF-=t*math.log(r)
                for r,n in Pp.items():
                    if r>0: t=n*r**e; F-=t; dF+=t*math.log(r)
                if dF==0: break
                nk=k-F/dF
                if not(1e-5<nk<0.02): break
                if abs(nk-k)<3e-16: return nk,T,Pp
                k=nk
        return X.kappa(T,Pp),T,Pp
    def kappa_exact(self,prec=50):
        T,Pp=self._invoice(self.paid,self.hel); return X.kappa_dec(T,Pp,prec)
    def crossing(self):
        """the 1e-14 crossing interval as `tk price` prints it"""
        kd=self.kappa_exact(); D=decimal.Decimal
        lo=(kd*10**14).to_integral_value(rounding=decimal.ROUND_FLOOR)/D(10**14); return format(lo,'.14f'),format(lo+D(1)/D(10**14),'.14f')
    def ledger(self): return self._invoice(self.paid,self.hel)
    def side(self):
        T,Pp=self.ledger(); return side_of(T,Pp,self.pr)
    def admit(self,best=False):
        """exact admissibility (admit.py): per-constraint slack at the profile literals, or best=True the best free literals + 'does any choice admit'"""
        import admit as A
        return A.best(self) if best else A.check(self)
    def budgets(self):
        rep=dict(nevents=sum(len(c.evs) for c in self.chs),helpers=dict(self.hel),paid=dict(self.paid),scalar=sum(c.scalar for c in self.chs),lifetimes=sum(c.life for c in self.chs))
        return X.budgets(rep)
    # ------------------------------------------------------------------ edits
    def _locate(self,chs,i):
        """-> (chunk index, offset of chunk) of event position i"""
        off=0
        for k,c in enumerate(chs):
            if i<off+len(c.evs): return k,off
            off+=len(c.evs)
        return len(chs)-1,off-len(chs[-1].evs) if chs else 0
    def _splice(self,chs,i,j,evs):
        total=sum(len(c.evs) for c in chs)
        if not(0<=i<=j<=total): raise IndexError('splice %d:%d of %d events'%(i,j,total))
        if not chs:
            ne=list(evs)
            if ne: chs.extend(Chunk(ne[x:x+self.B]) for x in range(0,len(ne),self.B))
            return
        ci,oi=self._locate(chs,i)
        cj,oj=self._locate(chs,j) if j<total else (len(chs)-1,total-len(chs[-1].evs))
        if cj<ci: cj=ci
        merged=chs[ci].evs[:i-oi]+list(evs)+chs[cj].evs[j-oj:]
        if not merged: new=[]
        elif len(merged)<=2*self.B: new=[Chunk(merged)]
        else: new=[Chunk(merged[x:x+self.B]) for x in range(0,len(merged),self.B)]
        chs[ci:cj+1]=new
    def _get(self,chs,i):
        k,off=self._locate(chs,i); return chs[k].evs[i-off]
    def _eval(self,edit,fast=False):
        ops=pnorm(edit)
        fast=fast and self.legal_all
        chs=list(self.chs); bases=self.ctx.bases; frames_changed=False; initial=self.initial; final=self.final; init_changed=fin_changed=False
        fset=set(); ctxver=self.ctx.ver
        for op in ops:
            t=op[0]
            if t=='splice': self._splice(chs,op[1],op[2],[tuple(e) if False else e for e in op[3]])
            elif t=='ins': self._splice(chs,op[1],op[1],[op[2]])
            elif t=='del': self._splice(chs,op[1],op[1]+1,[])
            elif t=='set': self._splice(chs,op[1],op[1]+1,[op[2]])
            elif t=='retarget':
                e=list(self._get(chs,op[1])); e[1]=op[2]; self._splice(chs,op[1],op[1]+1,[e])
            elif t=='mv':
                e=self._get(chs,op[1]); self._splice(chs,op[1],op[1]+1,[]); self._splice(chs,op[2],op[2],[e])
            elif t=='frame_add':
                if not frames_changed: bases=list(bases); frames_changed=True
                b=tuple(op[1]); _span(b); bases.append(b)
            elif t=='frame_set':
                if not frames_changed: bases=list(bases); frames_changed=True
                b=tuple(op[2]); _span(b); bases[op[1]]=b; fset.add(op[1])
            elif t=='initial':
                if not init_changed: initial=list(initial); init_changed=True
                initial[op[1]]=op[2]
            elif t=='final':
                if not fin_changed: final=list(final); fin_changed=True
                final[op[1]]=op[2]
            else: raise ValueError('unknown edit op %r'%(t,))
        ctx=Ctx(bases,ctxver+1) if frames_changed else self.ctx
        if init_changed and chs: chs[0]=chs[0].fresh()      # chunk 0's start state changes
        if fset:
            for k,c in enumerate(chs):
                if c.start is not None and not fset.isdisjoint(c.used): chs[k]=c.fresh()
        # --- replay from the first fresh chunk until the state converges
        st0=self.initial_state(initial)
        fresh=[k for k,c in enumerate(chs) if c.start is None or (k==0 and init_changed)]
        end=None
        if chs:
            if fresh:
                lo=fresh[0]; last=fresh[-1]
                st=st0 if lo==0 else chs[lo-1].end
                if lo==0 and not init_changed and chs[0].start is not None: pass
                for k in range(lo,len(chs)):
                    c=chs[k]
                    if c.start is not None and c.start==st:
                        if k>=last: st=None; break
                        st=c.end; continue
                    if c.start is not None: c=chs[k]=c.fresh()
                    self._fill(c,st,ctx); st=c.end
                    if fast and c.viol and not self.pre_static and sum(len(x.evs) for x in chs)<self.EC: raise _Early(c.viol[0][1])
                end=chs[-1].end
            else:
                end=chs[-1].end
        else: end=st0
        cand=_Cand(); cand.chs=chs; cand.ctx=ctx; cand.initial=initial; cand.final=final; cand.end=end
        # --- ledgers by chunk delta
        newids={id(c) for c in chs}; oldids={id(c) for c in self.chs}
        removed=[c for c in self.chs if id(c) not in newids]; added=[c for c in chs if id(c) not in oldids]
        paid=collections.Counter(self.paid); pd=collections.Counter()
        for c in removed:
            for k,v in c.paid.items(): paid[k]-=v
            for p,v in c.pairs.items(): pd[p]-=v
        for c in added:
            for k,v in c.paid.items(): paid[k]+=v
            for p,v in c.pairs.items(): pd[p]+=v
        cand.paid=paid
        if frames_changed or init_changed or fin_changed:
            cand.hel=self._hel(ctx,initial,final); cand.static_post=self._static_post(ctx,initial,final)
            if init_changed or fin_changed:
                hp=self._hpairs(initial,final)
                for p,v in self.hpairs.items(): pd[p]-=v
                for p,v in hp.items(): pd[p]+=v
                cand.hpairs=hp
            else: cand.hpairs=self.hpairs
        else: cand.hel=self.hel; cand.static_post=self.static_post; cand.hpairs=self.hpairs
        # --- native pair bookkeeping
        cand.pair_delta={p:v for p,v in pd.items() if v}
        bad=set(self.bad_pairs); nat_new=0
        if self.use_native:
            nat=self._nat
            force=[p for p in self.pairs if p[0] in fset or p[1] in fset] if fset else []     # pairs touching a changed frame are re-tested even if their count did not change
            todo=[(p,dv) for p,dv in pd.items() if dv]+[(p,0) for p in force if not pd.get(p)]
            for p,dv in todo:
                cnt=self.pairs.get(p,0)+dv
                if cnt>0:
                    if not nat.ok(ctx,p): bad.add(p)
                    else: bad.discard(p)
                else: bad.discard(p)
        cand.bad_pairs=bad
        # --- violations
        res=self._assemble(chs,ctx,initial,final,end,paid,cand.hel,cand.static_post,reuse=self.post_cache)
        cand.viol=res['viol']; cand.post=res['post']; cand.n=res['n']
        T=self._kappa(paid,cand.hel,self.kappa); cand.kappa=T[0]
        return cand
    def try_edit(self,edit,fast=False):
        """-> Result; the word is not modified.  fast=True (only if the current word is fully legal): stop at the first violation found in the replayed region
        (-> Result(False,None,rule,early=True); same rule as the first violation of the full list); otherwise identical to the full evaluation."""
        ce=edit
        if hasattr(edit,'to_incr'):          # REALISEFIX: sedit.SEdit (explicit scalar-window edit) -> ordinary splice ops on the program with MOVEs; else the word route + diff
            try: ce=edit.to_incr()
            except (ValueError,NotImplementedError):
                v=edit.view
                if v is None: raise
                ce=diff_edit(v.w,v.rebuild_edit(edit))
        try: c=self._eval(ce,fast)
        except _Early as ex:
            self._lastcand=None
            return Result(False,None,str(ex),viol=[],exception=False,early=True,native_bad=None)
        except (IndexError,ValueError,TypeError,KeyError,AttributeError) as ex:
            self._lastcand=None
            return Result(False,None,'exception: %s: %s'%(type(ex).__name__,str(ex)[:80]),viol=[],exception=True,early=False,native_bad=0)
        self._lastcand=(edit,c,None)
        legal_ok=not c.viol and not c.bad_pairs
        if c.viol: reason=c.viol[0][1]
        elif c.bad_pairs: reason='Native boundary rank / phase'
        else: reason=''
        res=Result(legal_ok,c.kappa-self.kappa,reason,viol=c.viol[:50],kappa=c.kappa,native_bad=len(c.bad_pairs),exception=False,early=False,cand=c)
        self._lastcand=(edit,c,res); return res
    def commit(self,edit):
        """adopt the edit; -> Result of the evaluation.  Illegal edits can be committed too (the state is then the illegal word)."""
        lc=self._lastcand
        if lc is None or lc[0] is not edit: self.try_edit(edit); lc=self._lastcand
        if lc is None: raise ValueError('edit is malformed; not committed')
        r=lc[2]
        c=lc[1]
        self.chs=c.chs; self.ctx=c.ctx; self.initial=c.initial; self.final=c.final; self.endstate=c.end; self.paid=c.paid
        for p,dv in c.pair_delta.items():
            n=self.pairs.get(p,0)+dv
            if n>0: self.pairs[p]=n
            else: self.pairs.pop(p,None)
        self.hpairs=c.hpairs; self.hel=c.hel; self.static_post=c.static_post; self.bad_pairs=c.bad_pairs
        self.viol=c.viol; self.post_cache=c.post; self.kappa=c.kappa; self.legal_all=not c.viol and not c.bad_pairs; self._lastcand=None
        return r
    # ------------------------------------------------------------------ views
    def program(self): return [e for c in self.chs for e in c.evs]
    def to_word(self):
        w=dict(self.w0); w['program']=[list(e) for e in self.program()]; w['frames']=[list(b) for b in self.ctx.bases]; w['initial']=list(self.initial); w['final']=list(self.final); return w
    def accept(self):
        import accept as A,tempfile,gzip
        f=tempfile.mktemp(suffix='.json.gz'); json.dump(self.to_word(),gzip.open(f,'wt'))
        with use_profile(self.profile): r=A.accept(f)
        os.unlink(f); return r
    def flush(self):
        if self.use_native: self._nat.flush()
class _Native:
    """native pair verdicts keyed by the frame bases (shared persistent cache with tk accept: CACHE/nativepairs/*.json)"""
    def __init__(self):
        self.N=native_mod(); self._real=self.N; self.mem={}; self.new={}; self.disk=None; self.nfresh=0
    def _load(self):
        d=CACHE+'/nativepairs'; self.disk={}
        for f in glob.glob(d+'/*.json'):
            try: self.disk.update(json.load(open(f)))
            except Exception: pass
    def ok(self,ctx,p):
        a,b=ctx.bases[p[0]],ctx.bases[p[1]]; k=(a,b); v=self.mem.get(k)
        if v is None:
            if self.disk is None: self._load()
            ks=','.join(map(str,a))+'|'+','.join(map(str,b)); d=self.disk.get(ks)
            if d is None:
                d=self.disk[ks]=list(self.N.ok(a,b)); self.new[ks]=d; self.nfresh+=1
            v=self.mem[k]=bool(d[0])
        return v
    def flush(self):
        if self.N is not self._real or os.environ.get('TK_NATIVE_CACHE_RO'):   # never persist verdicts from a substituted (fake/test) checker
            self.new.clear(); return
        if self.new:
            d=CACHE+'/nativepairs'; os.makedirs(d,exist_ok=True); f='%s/incr_%d_%d.json'%(d,os.getpid(),int(time.time()*1000)); json.dump(self.new,open(f+'.tmp','w')); os.replace(f+'.tmp',f); self.new.clear()
def diff_edit(old,new):
    """edit turning word `old` into word `new` (dicts): one splice over the differing program middle + frame/initial/final ops (frames may only grow)"""
    A=old['program']; Bp=new['program']; n=min(len(A),len(Bp)); i=0
    while i<n and list(A[i])==list(Bp[i]): i+=1
    j=0
    while j<n-i and list(A[-1-j])==list(Bp[-1-j]): j+=1
    ops=[]
    fo,fn=old['frames'],new['frames']
    if len(fn)<len(fo): raise ValueError('frames shrink')
    for f in range(len(fo)):
        if list(fo[f])!=list(fn[f]): ops.append(['frame_set',f,list(fn[f])])
    for f in range(len(fo),len(fn)): ops.append(['frame_add',list(fn[f])])
    if i<len(A)-j or i<len(Bp)-j: ops.append(['splice',i,len(A)-j,[tuple(e) for e in Bp[i:len(Bp)-j]]])
    for r in range(len(old['initial'])):
        if old['initial'][r]!=new['initial'][r]: ops.append(['initial',r,new['initial'][r]])
        if old['final'][r]!=new['final'][r]: ops.append(['final',r,new['final'][r]])
    return dict(ops=ops)
def apply_edit_to_word(w,edit):
    """reference application of an edit to a plain word dict (deep copy) -- used by the fuzzer and by tools that want the full word"""
    w=copy.deepcopy(w); P_=w['program']
    for op in pnorm(edit):
        t=op[0]
        if t=='splice': P_[op[1]:op[2]]=[list(e) for e in op[3]]
        elif t=='ins': P_.insert(op[1],list(op[2]))
        elif t=='del': del P_[op[1]]
        elif t=='set': P_[op[1]]=list(op[2])
        elif t=='retarget': P_[op[1]][1]=op[2]
        elif t=='mv': e=P_.pop(op[1]); P_.insert(op[2],e)
        elif t=='frame_add': w['frames'].append(list(op[1]))
        elif t=='frame_set': w['frames'][op[1]]=list(op[2])
        elif t=='initial': w['initial'][op[1]]=op[2]
        elif t=='final': w['final'][op[1]]=op[2]
        else: raise ValueError(t)
    return w
