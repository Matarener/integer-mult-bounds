"""synth.compact -- value-preserving event/scalar COMPACTION post-pass (GENBUDGET; notes ../module docstring).

compact(word, passes=ALL, verify=True) -> (new_word, stats)      word = tk word dict (program list of ['ADD',dst,src,q,f] / ['MOVE',r,a,b,pv] / INIT / CLEAR / SCALE / COPY)
Passes (each keeps every register's final value and every frame law; `verify` re-runs legal.check with 4 random vectors and requires identical final value matrices + ok):
  moves  consecutive MOVEs a->b, b->c of one register with NO event touching it between, same direction  =>  one MOVE a->c  (paid P is subadditive in rank: never dearer; the new
         (a,c) native pair is checked when numpy/native is available).  Saves events and 1000 scalar units per merged MOVE (pricing routes).
  adds   two ADDs of one (dst,src,frame) with dst not read/scaled and src not written in between  =>  one ADD with the summed coefficient (dropped when the sum is 0).
  cse    maximal run of consecutive ADDs at ONE frame whose dst set is disjoint from its src set is a matrix M (dst rows x src columns); columns with identical row support and proportional
         coefficients form a CLASS; class = host s plus members g with ratios rho_g (dyadic):  accumulate s += rho_g g,  every row j does dst_j += M_js s (1 event instead of |class|),  restore s -= rho_g g.
         Saves (|class|-1)*(rows-2) events per class; exact value preserved (host restored, run order irrelevant by disjointness).  This is the FRONTGEN dim-0 junk-load block (27040 events).
  scale  owned lifetimes (INIT..CLEAR) may be rescaled by 2^e (dst coefficient *2^e, src coefficient /2^e): choose e minimising the exact scalar units (legal.check formula).
Nothing here changes the helper inventory, hop structure or credits -- the pricing-relevant structure (helpers, rank of MOVEs) is only touched by `moves`.
CLI: python -m synth.compact WORD [--out F] [--passes moves,adds,cse,scale] [--profile P]"""
import sys,os,json,gzip,copy,collections
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from tkcommon import *
ALL=('moves','adds','cse','scale')
def qs(q): return str(q)
def cost(q):
    """legal.check scalar units of one ADD/COPY with coefficient q"""
    n,d=abs(q.numerator),q.denominator
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def _span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
def reads(e):
    op=e[0]
    return (e[2],) if op in('ADD','COPY') else ()
def writes(e):
    return e[1]
# ------------------------------------------------------------------------------------------------ moves
def pass_moves(w,st,native=True):
    prog=w['program']; fr=w['frames']; spans={}
    def sp(f):
        if f not in spans: spans[f]=_span(fr[f])
        return spans[f]
    last={}                          # reg -> index (in out) of the last MOVE of reg that is still 'open' (no event touched reg since)
    out=[]; bad=set(); merged=0
    def pair_ok(a,c):
        if not native: return True
        try:
            import accept as A
            return not A.native_pairs(w,pairs={(a,c)})['bad']
        except Exception: return False      # cannot verify the new native pair -> do not merge
    for e in prog:
        if e[0]=='MOVE':
            r=e[1]
            if r in last:
                m=out[last[r]]
                if m is not None and m[4]==e[4] and m[3]==e[2]:
                    a,b,c,pv=m[2],m[3],e[3],e[4]
                    ok=(sp(a)<sp(b)<sp(c)) if not pv else (sp(c)<sp(b)<sp(a))
                    if ok and (a,c) not in bad and pair_ok(a,c):
                        out[last[r]]=['MOVE',r,a,c,pv]; merged+=1; continue
                    if ok: bad.add((a,c))
            out.append(list(e)); last[r]=len(out)-1; continue
        out.append(list(e))
        for r in {e[1]}|set(reads(e)): last.pop(r,None)
    st['moves_merged']=merged
    w['program']=[e for e in out if e is not None]; return w
# ------------------------------------------------------------------------------------------------ adds
def pass_adds(w,st):
    prog=w['program']; out=[]; pending={}          # key (dst,src,f) -> (index in out of the open ADD, W[src], R[dst]) at its creation
    W=collections.Counter(); R=collections.Counter()   # W: any write to reg; R: reads as source + hard writes (COPY/SCALE/INIT/CLEAR/MOVE) of reg
    merged=0; dead=set()
    for e in prog:
        op=e[0]
        if op=='ADD':
            d,s,q,f=e[1],e[2],Q(e[3]),e[4]; k=(d,s,f)
            if k in pending:
                i,ws,rd=pending[k]
                if W[s]==ws and R[d]==rd:
                    nq=Q(out[i][3])+q; merged+=1
                    if nq==0: dead.add(i); del pending[k]
                    else: out[i][3]=qs(nq)
                    continue
            out.append(list(e)); R[s]+=1; W[d]+=1; pending[k]=(len(out)-1,W[s],R[d])
            continue
        out.append(list(e)); r=e[1]
        if op=='COPY': R[e[2]]+=1
        W[r]+=1; R[r]+=1
    st['adds_merged']=merged
    w['program']=[e for i,e in enumerate(out) if i not in dead]; return w
# ------------------------------------------------------------------------------------------------ cse
def pass_cse(w,st,min_gain=8,min_run=64):
    prog=w['program']; out=[]; i=0; n=len(prog); saved=0; classes=0
    while i<n:
        e=prog[i]
        if e[0]!='ADD': out.append(e); i+=1; continue
        f=e[4]; j=i
        while j<n and prog[j][0]=='ADD' and prog[j][4]==f: j+=1
        run=prog[i:j]
        if len(run)<min_run: out.extend(run); i=j; continue
        dsts={x[1] for x in run}; srcs={x[2] for x in run}
        if dsts&srcs: out.extend(run); i=j; continue
        M=collections.defaultdict(lambda:collections.defaultdict(Q))     # dst -> src -> coeff
        for x in run: M[x[1]][x[2]]+=Q(x[3])
        cols=collections.defaultdict(dict)                                # src -> {dst: coeff}
        for d,row in M.items():
            for s,q in row.items():
                if q: cols[s][d]=q
        groups=collections.defaultdict(list)
        for s,col in cols.items():
            ds=sorted(col); q0=col[ds[0]]
            groups[tuple((d,col[d]/q0) for d in ds)].append(s)
        used=set(); plan=[]
        for key,mem in groups.items():
            rows=len(key)
            if len(mem)<2 or rows<3 or (len(mem)-1)*(rows-2)<min_gain: continue
            # host choice: all ratios cols[g][d0]/cols[host][d0] must be dyadic
            d0=key[0][0]
            for host in sorted(mem):
                rho={g:cols[g][d0]/cols[host][d0] for g in mem if g!=host}
                if all(r.denominator&(r.denominator-1)==0 and abs(r)+1<2**16 for r in rho.values()): break
            else: continue
            plan.append((host,rho,sorted(key),(len(mem)-1)*(rows-2)))
        if not plan: out.extend(run); i=j; continue
        covered=set()                                                      # (dst,src) pairs handled by classes
        for host,rho,key,gain in plan:
            for g in [host]+list(rho):
                for d in cols[g]: covered.add((d,g))
        # leftover individual events first (they read hosts in original form), then each class: accumulate, rows, restore
        new=[]
        for d,row in M.items():
            for s,q in row.items():
                if q and (d,s) not in covered: new.append(['ADD',d,s,qs(q),f])
        for host,rho,key,gain in plan:
            for g,r in sorted(rho.items()): new.append(['ADD',host,g,qs(r),f])
            for d,_r in key: new.append(['ADD',d,host,qs(cols[host][d]),f])
            for g,r in sorted(rho.items()): new.append(['ADD',host,g,qs(-r),f])
            saved+=gain; classes+=1
        out.extend(new); i=j
    st['cse_classes']=classes; st['cse_saved_model']=saved
    w['program']=out; return w
# ------------------------------------------------------------------------------------------------ scale
def pass_scale(w,st,erange=range(-8,9)):
    prog=w['program']; pub=w.get('public') or len(w['initial']); lifetimes=[]; open_={}
    for i,e in enumerate(prog):
        if e[0]=='INIT': open_[e[1]]=i
        elif e[0]=='CLEAR' and e[1] in open_: lifetimes.append((e[1],open_.pop(e[1]),i))
    saved=0
    for r,a,b in lifetimes:
        idx=[i for i in range(a+1,b) if prog[i][0] in('ADD','COPY','SCALE') and (prog[i][1]==r or (prog[i][0]!='SCALE' and prog[i][2]==r))]
        if not idx: continue
        def total(e_):
            lam=Q(2)**e_ ; t=0
            for i in idx:
                x=prog[i]; q=Q(x[3] if x[0]!='SCALE' else x[2])
                if x[0]=='SCALE': t+=2*(abs(abs(q.numerator).bit_length()-q.denominator.bit_length())+int(q<0)); continue
                if x[1]==r and x[2]==r: return None
                q2=q*lam if x[1]==r else q/lam
                if abs(q2)+1>=2**16 or q2.denominator&(q2.denominator-1): return None
                t+=cost(q2)
            return t
        base=total(0); best=(base,0)
        for e_ in erange:
            t=total(e_)
            if t is not None and t<best[0]: best=(t,e_)
        if best[1]:
            lam=Q(2)**best[1]
            for i in idx:
                x=prog[i]
                if x[0]=='SCALE': continue
                x[3]=qs(Q(x[3])*lam if x[1]==r else Q(x[3])/lam)
            saved+=base-best[0]
    st['scale_units_saved']=saved; return w
# ------------------------------------------------------------------------------------------------ driver
def _vals(w,K=4):
    rep=legal.check(w,K=K); rep['vals']=legal.check(w,K=K,contract=False)['vals']; return rep
def compact(w,passes=ALL,verify=True,native=True,profile=None):
    w=copy.deepcopy(w); st=dict(events_before=len(w['program']))
    if verify:
        r0=_vals(w); st['scalar_before']=r0['scalar']; st['paid_before']=sum(r0['paid'].values()); st['legal_before']=r0['ok']
    for p in passes:
        if p=='moves': pass_moves(w,st,native)
        elif p=='adds': pass_adds(w,st)
        elif p=='cse': pass_cse(w,st)
        elif p=='scale': pass_scale(w,st)
        else: raise SystemExit('compact: unknown pass %r'%p)
    st['events_after']=len(w['program'])
    if verify:
        r1=_vals(w); st['scalar_after']=r1['scalar']; st['paid_after']=sum(r1['paid'].values()); st['legal_after']=r1['ok']
        st['values_equal']=(r1['vals']==r0['vals']) and r1['violations']==r0['violations']
        if not st['values_equal']: raise AssertionError('compact changed values or violations: %s'%st)
    return w,st
def main(argv=None):
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--out'); ap.add_argument('--passes',default=','.join(ALL)); ap.add_argument('--profile'); ap.add_argument('--no-native',action='store_true')
    a=ap.parse_args(argv); path,w=load(a.word)
    if a.profile: os.environ['TK_PROFILE']=a.profile
    nw,st=compact(w,tuple(a.passes.split(',')),native=not a.no_native); print(json.dumps(st,indent=1))
    if a.out: json.dump(nw,gzip.open(a.out,'wt')); print('wrote',a.out)
if __name__=='__main__': main()
