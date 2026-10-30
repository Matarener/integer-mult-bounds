"""synth.k2search_validate -- K2SEARCH lane (../module docstring).  Scope [toolkit synth, SA/LNS search on k2net rendezvous programs].

Independent python check of a net written by the C++ search engine (ext/KERNEL2/k2search.inc, K2_SEARCH=walk|sa|census):
  net -> word (realise: MOVE sources/ownership derived, finals = last frames, new helpers appended after the public block, owned renumbered after them),
  then from scratch: infra legal.check (frame law, nesting, owned, dyadic, endpoint rows by random evaluation), kernel2net R0 (chain taxes), price_exact kappa (float + Decimal-50),
  EXACT Fraction replay of the value contract (every public register ends e_r, Y ends e_r + e_{r-112}, owned 0), and compares R0/kappa with the C++ header line.
usage: python -B synth/k2search_validate.py NET BASEWORD [OUT.json.gz] [--no-exact]
No side effects at import.
"""
import sys,os,gzip,json,math
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
for p in (TK,HERE,os.path.join(os.path.dirname(TK),'infra')):
    if p not in sys.path: sys.path.insert(0,p)
def parse_net(path):
    F=[];R={};ev=[];hdr={}
    for ln in open(path):
        t=ln.split()
        if not t: continue
        k=t[0]
        if k=='NET': hdr['n'],hdr['nown'],hdr['nf'],hdr['ne']=map(int,t[1:5])
        elif k=='#K2S': hdr.update({t[i]:float(t[i+1]) for i in range(1,len(t)-1,2)})
        elif k=='F': F.append([int(x) for x in t[3:]])
        elif k=='R': R[int(t[1])]=(t[2],int(t[3]))
        elif k=='M': ev.append(('M',int(t[1]),int(t[2])))
        elif k in('A','C'): ev.append((k,int(t[1]),int(t[2]),t[3],int(t[4])))
        elif k=='S': ev.append(('S',int(t[1]),t[2],int(t[3])))
        elif k in('I','X'): ev.append((k,int(t[1]),int(t[2])))
    return hdr,F,R,ev
def realise(net,base):
    hdr,F,R,ev=net; n0,no=hdr['n'],hdr['nown']
    newh=sorted(r for r in R if r>=n0+no and R[r][0]!='O')
    used={e[1] for e in ev}|{e[2] for e in ev if e[0] in('A','C')}
    newo=sorted(r for r in R if r>=n0+no and R[r][0]=='O' and r in used)      # K2FRAMES: owned registers created by the search (helper->owned relays), numbered after the input's owned block
    mp={r:r for r in range(n0)}
    for k,r in enumerate(newh): mp[r]=n0+k
    for r in range(n0,n0+no): mp[r]=r+len(newh)
    npub=n0+len(newh)
    for k,r in enumerate(newo): mp[r]=npub+no+k
    owned={mp[r] for r in range(n0,n0+no)}|{mp[r] for r in newo}
    init=[None]*npub
    for r,(ro,f) in R.items():
        if r in mp and mp[r]<npub: init[mp[r]]=f
    cur={r:init[r] for r in range(npub)}; prog=[]
    for e in ev:
        k=e[0]
        if k=='M': r=mp[e[1]]; prog.append(['MOVE',r,cur[r],e[2],r in owned]); cur[r]=e[2]
        elif k in('A','C'): prog.append(['ADD' if k=='A' else 'COPY',mp[e[1]],mp[e[2]],e[3],e[4]])
        elif k=='S': prog.append(['SCALE',mp[e[1]],e[2],e[3]])
        elif k=='I': r=mp[e[1]]; prog.append(['INIT',r,e[2]]); cur[r]=e[2]
        elif k=='X': r=mp[e[1]]; prog.append(['CLEAR',r,e[2]]); cur[r]=None
    w={k:v for k,v in base.items() if k not in('program','frames','initial','final')}
    w['frames']=F; w['initial']=init; w['final']=[cur[r] for r in range(npub)]; w['program']=prog
    if 'public' in w: w['public']=npub
    if w.get('verifier_profile') and 'public' in w['verifier_profile'] and newh: w['verifier_profile']=dict(w['verifier_profile'],public=npub)
    retarget_owned(w,base,no+len(newo))
    return w,len(newh)
def retarget_owned(w,base,nown_new):
    """K2FRAMES: an owned relay changes the package's inventory literals (owned_fields, owned lifetime census), exactly as the swarm PRs #5802/#5811 retarget them.
    The realised word then carries its own pins in verifier_profile (owned_fields, lifetimes, owned_range upper bound); peak is NOT retargeted (the engine caps it at the input's peak).
    No change when the owned inventory and lifetime count are the input's."""
    import legal
    lt=sum(1 for e in w['program'] if e[0]=='INIT'); lt0=sum(1 for e in base['program'] if e[0]=='INIT')
    if 'owned_fields' not in base or (nown_new==legal.nown(base) and lt==lt0): return
    PP=legal.profile_params(base); lo,hi=PP['owned_range']
    w['owned_fields']=nown_new
    w['verifier_profile']=dict(w.get('verifier_profile') or {},owned_fields=nown_new,lifetimes=lt,owned_range=[lo,max(hi,nown_new)])
def exact_contract(w):
    import kernel2net as K
    fm=K.replay(w); n=len(w['initial']); live=set(w['live']); bad=[]
    for r in range(n):
        ex={r:Q(1)}
        if r-112 in live: ex[r-112]=Q(1)
        if fm.get(r,{})!=ex: bad.append(r)
    for r,f in fm.items():
        if r>=n and f: bad.append(r)
    return bad
def validate(netpath,basespec,out=None,exact=True):
    import tkcommon,legal,price_exact as X,kernel2net as K
    _,base=tkcommon.load(basespec)
    net=parse_net(netpath); w,nnew=realise(net,base)
    out=out or netpath+'.json.gz'
    tkcommon.save_canonical(w,out)      # HYGIENE: bool private flags, sorted/indent-2/mtime-0 (PKGPREP normalise.py form)
    w2=legal.load(out)     # K2FRAMES: no re-activation -- the BASE word's verifier profile stays in force (a retargeted owned inventory would select another family)
    rep=legal.check(w2); T,P=X.invoice(rep); kf=X.kappa(T,P); kd=X.kappa_dec(T,P)
    by,tot=K.r0(w2); r0=sum(v for k,v in by.items() if k!='O')
    res=dict(word=out,new_helpers=nnew,events=len(w2['program']),legal_ok=rep['ok'],violations=rep['violations'][:6],kappa=kf,kappa_dec=str(kd)[:22],R0=r0,
             cpp_kappa=net[0].get('kappa'),cpp_R0=net[0].get('R0'),rendezvous_viol=K.check_rendezvous(w2))
    res['kappa_match']=res['cpp_kappa'] is None or abs(res['cpp_kappa']-kf)<1e-13
    res['R0_match']=res['cpp_R0'] is None or abs(res['cpp_R0']-r0)<1e-4
    if exact: bad=exact_contract(w2); res['exact_contract_bad']=bad[:10]; res['exact_ok']=not bad
    return res
if __name__=='__main__':
    a=[x for x in sys.argv[1:] if not x.startswith('--')]
    r=validate(a[0],a[1],a[2] if len(a)>2 else None,exact='--no-exact' not in sys.argv)
    print(json.dumps(r,default=str))
