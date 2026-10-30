"""legalize -- LEGALIZE: word -> word pass that makes a generated word legal under the swarm's standard profile (p5660: public 735..750, tail decay .975)
with NO new literals.  usage: python -B legalize.py WORD [--out F] [--json]
Passes (each value-checked with legal.check; random-evaluation endpoint):
  1. liveness: every PUBLIC register is an independent input row that must be returned (endpoint rows = identity on helpers), so its live interval is the whole
     program and interval colouring cannot merge two of them: lower bound on the public count = the count itself (only OWNED scratch is reusable, and it already is).
  2. dead-helper prune (the only value-preserving register removal): a helper index >= 224 that no op reads is deleted with its writes; registers renumbered.
  3. side-check budget: maximum helper count / rank mix allowed by delta<D (fields count) and gamma<D (P moment), at the word's kappa.
Returns (word, report).  Exit status 1 when the word is still illegal (the usual outcome for the RELAYTOP words:."""
import sys,os,json,collections
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,HERE+'/infra')
import legal, price_exact as X

STD=dict(public_range=(735,750),decay=0.975,c=17,b=18,u=0.2,reserve=1e-12)

def roles(w):
    live=set(w['live']); main=live|{r+112 for r in live}
    N=len(w['initial']); return N,main,[r for r in range(N) if r not in main]

def reads_writes(w):
    rd=collections.Counter(); wr=collections.Counter()
    for e in w['program']:
        if e[0] in('ADD','COPY'): rd[e[2]]+=1
        if e[0] in('ADD','COPY','SCALE'): wr[e[1]]+=1
    return rd,wr

def prune_dead_helpers(w):
    """iterate: helper r>=224 never read -> drop all ops writing r, drop the register (renumber).  Main indices (<224) are never touched."""
    w=json.loads(json.dumps(w)); removed=[]
    while True:
        N,main,hel=roles(w); rd,_=reads_writes(w)
        dead={r for r in hel if r>=224 and rd[r]==0}
        if not dead: break
        removed+=sorted(dead)
        keep=[r for r in range(N) if r not in dead]; m={r:i for i,r in enumerate(keep)}; no=w.get('owned_fields',8)
        for j in range(no): m[N+j]=len(keep)+j
        prog=[]
        for e in w['program']:
            if e[1] in dead or (e[0] in('ADD','COPY') and e[2] in dead): continue
            e=list(e); e[1]=m[e[1]]
            if e[0] in('ADD','COPY'): e[2]=m[e[2]]
            prog.append(e)
        w['program']=prog; w['initial']=[w['initial'][r] for r in keep]; w['final']=[w['final'][r] for r in keep]
        w['public']=len(keep)
        vp=w.get('verifier_profile')
        if isinstance(vp,dict): vp['public']=len(keep)
    return w,removed

def _tail(w):
    """(c,b,u) of the word's adopted profile tail if it has one (TKHYG2), else the legacy standard STD literals"""
    from tkcommon import profile_of
    t=profile_of(w)[1].get('tail')
    return (t['c'],t['b'],t['u']) if t else (STD['c'],STD['b'],STD['u'])
def side_budget(w,rep,decay=STD['decay']):
    """at the word's own kappa: how many helpers of rank r the delta bound allows (outer part fixed), and the gamma moment ratio"""
    T,P=X.invoice(rep); k=X.kappa(T,P); t=1-k; c,b,u=_tail(w)
    To={r:n for r,n in T.items() if r not in rep['helpers']}; Tout=dict(px_out(rep))
    mo=sum(n*r**t for r,n in Tout.items()); so=sum(Tout.values())
    s=X.side(T,P,k-1e-9,c=c,b=b,u=u,decay=decay)
    out=dict(kappa=k,gamma=s['gamma'],delta=s['delta'],sumT=s['sumT'],momT=s['momT'])
    num=decay*c**k*mo-b*so
    out['max_rank9_helpers_delta']=int(num/(18*(b-decay*c**k*9**t))) if num>0 else 0
    mp_u=sum(n*r**(t+u) for r,n in P.items()); out['P_u_moment']=mp_u
    out['gamma_needs_T_moment']=mp_u/(c**u*decay)   # momT must be >= this
    out['avg_T_rank_needed_for_delta']=b/(decay*c**k)
    return out
def px_out(rep):
    T=collections.Counter(X.TOUT); return dict(T)

def legalize(w,profile_range=STD['public_range']):
    rep0=legal.check(w); N0,main,hel=roles(w)
    w2,removed=prune_dead_helpers(w)
    rep=legal.check(w2); T,P=X.invoice(rep)
    N,_,hel2=roles(w2); lo,hi=profile_range
    r=dict(public_before=N0,public_after=N,helpers=len(hel2),removed=removed,
           public_lower_bound=N, max_live_public=N,
           reason='each public register is an independent input row returned unchanged (helpers) or combined (mains): live for the whole program',
           need_public=(lo,hi),excess=max(0,N-hi),
           kappa_before=X.kappa(*X.invoice(rep0)),kappa_after=X.kappa(T,P),
           legal_value=rep['ok'],violations=[list(map(str,v)) for v in rep['violations'][:5]],
           side=side_budget(w2,rep))
    r['legal_standard']=bool(rep['ok'] or all(v[1]=='Public inventory bound' for v in rep['violations'])) and lo<=N<=hi and r['side']['gamma']<STD['decay'] and r['side']['delta']<STD['decay']
    return w2,r

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--out'); ap.add_argument('--json',action='store_true'); a=ap.parse_args()
    w=legal.load(a.word); w2,r=legalize(w)
    if a.out:
        import gzip
        (gzip.open if a.out.endswith('.gz') else open)(a.out,'wt').write(json.dumps(w2))
    if a.json: print(json.dumps(r,default=str,indent=1))
    else:
        s=r['side']
        print('public %d -> %d (removed dead helpers: %d); lower bound %d (%s)'%(r['public_before'],r['public_after'],len(r['removed']),r['public_lower_bound'],r['reason']))
        print('standard profile needs %s: excess %d registers'%(r['need_public'],r['excess']))
        print('kappa %.13f -> %.13f'%(r['kappa_before'],r['kappa_after']))
        print('side @decay %.3f: gamma %.4f delta %.4f; delta allows <= %d rank-9 helpers at this kappa; gamma needs momT >= %.0f (has %.0f); delta needs avg T rank >= %.1f'%(STD['decay'],s['gamma'],s['delta'],s['max_rank9_helpers_delta'],s['gamma_needs_T_moment'],s['momT'],s['avg_T_rank_needed_for_delta']))
        print('LEGAL under standard profile:',r['legal_standard'])
    sys.exit(0 if r['legal_standard'] else 1)
