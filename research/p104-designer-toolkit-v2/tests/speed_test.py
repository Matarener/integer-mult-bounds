"""speed_test (SPEED, Oct 28): the performance changes are exact.  ~20 s, single core + up to 4 short nativepar workers.
  1. fingerprint index: exact_alias(w) == the old _fingerprints().get(word_fingerprint(w)) path on every words/ alias + 2 non-alias words; disk index == fresh fingerprints
  2. native pairs: accept.compute_pairs (parallel nativepar workers) == serial N.ok on 400 pairs incl. >= 60 failing ones (verdict and reason text), cache bypassed
  3. fast adapters: the 6030 profile's own native() on the pair-free copy with fastnative kernels == untouched kernels (full dict incl. recipe_payload_sha256)
  4. kappa_dec (ln hoisted) == the original implementation on 6 words at prec 50
  5. price.run memo key: changes with the invoice/literals, stable for identical inputs
prints ALL PASS / FAIL lines.  usage: speed_test.py"""
import sys,os,json,gzip,decimal,random
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path.insert(0,TK)
import tkcommon,legal,price_exact as X,accept as A,tkstack
fails=[]
def need(c,what): print(('PASS ' if c else 'FAIL ')+what,flush=True); c or fails.append(what)
def main():
    OTHER=[os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/B0POLISH/best_px.json.gz',os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/SKELGEN/runs/p1oF.json.gz']
    OTHER=[p for p in OTHER if os.path.exists(p)]
    # 1
    old={}
    for al in tkcommon.DATA_PROFILES:
        wf=TK+'/words/%s.json.gz'%al
        if os.path.exists(wf):
            try: old[tkcommon.word_fingerprint(json.load(gzip.open(wf)))]=al
            except Exception: pass
    ok=True;n=0
    for wf in [TK+'/words/%s.json.gz'%al for al in tkcommon.DATA_PROFILES if os.path.exists(TK+'/words/%s.json.gz'%al)]+OTHER:
        w=json.load(gzip.open(wf)); n+=1
        ok&=tkcommon.exact_alias(w)==old.get(tkcommon.word_fingerprint(w))
    fp=tkcommon._fingerprints()
    need(ok and {k:v for k,v in fp.items() if k!='_done'}==old,'fingerprint index: exact_alias == old path on %d words; index == fresh fingerprints (%d)'%(n,len(old)))
    # 2
    os.environ['TK_NATIVE_PAIRCACHE']='0'
    C=A._load_pairs() if os.path.isdir(tkcommon.CACHE+'/nativepairs') else {}
    def parse(k): a,b=k.split('|'); return tuple(map(int,a.split(','))) if a else (),tuple(map(int,b.split(','))) if b else ()
    items={}
    w=legal.load(TK+'/words/6030.json.gz'); fr=w['frames']
    for e in w['program']:
        if e[0]=='MOVE' and len(items)<340: k=A._key(fr[e[2]],fr[e[3]]); items[k]=(k,tuple(fr[e[2]]),tuple(fr[e[3]]))
    rnd=random.Random(7)
    for k in [k for k,v in sorted(C.items()) if not v[0]][:60]: items[k]=(k,)+parse(k)
    for _ in range(20):      # random (mostly illegal) pairs: reasons must match too
        a=tuple(sorted(rnd.sample(range(1,512),rnd.randint(1,4)))); b=tuple(sorted(rnd.sample(range(1,512),rnd.randint(1,5)))); k=A._key(a,b); items[k]=(k,a,b)
    os.environ['TK_NATIVE_JOBS']='4'; par=A.compute_pairs(list(items.values()))
    N=tkcommon.native_mod(); ser={k:[bool(o),v] for k,a,b in items.values() for o,v in [N.ok(a,b)]}
    nf=sum(1 for v in ser.values() if not v[0])
    need(par==ser and nf>=10,'native pairs: parallel compute_pairs == serial N.ok on %d pairs (%d failing, reasons equal)'%(len(ser),nf))
    os.environ.pop('TK_NATIVE_JOBS'); os.environ.pop('TK_NATIVE_PAIRCACHE')
    # 3
    prof=tkstack.profile('6030'); S=prof['stack']; root=tkcommon.closure_root(); d=tkstack.pdir(prof)
    n0=len(w['initial']); main=set(w['live'])|{r+112 for r in w['live']}
    w2=json.loads(json.dumps(w)); w2['program']=[e for e in w2['program'] if e[0]!='MOVE']
    for r in range(n0):
        if r not in main: w2['final'][r]=w2['initial'][r]
    res=[]
    for fast in (False,True):
        base=tkstack.load_module(d+S['base']['file'],'local',root); undo=tkstack._fast_adapters(base,A) if fast else (lambda:None)
        try: res.append(base.native(w2))
        finally: undo()
    need(res[0]==res[1] and 'recipe_payload_sha256' in res[0],'fast adapters: profile 6030 native() on the pair-free copy identical to untouched kernels (incl. recipe_payload_sha256)')
    # 4
    def kd_orig(T,P,prec=50):
        decimal.getcontext().prec=prec; D=decimal.Decimal
        def g(k):
            e=1-k
            return sum(n*(D(r).ln()*e).exp() for r,n in T.items())-sum(n*(D(r).ln()*e).exp() for r,n in P.items())
        lo,hi=D('0.00001'),D('0.02')
        for _ in range(150):
            m=(lo+hi)/2
            if g(m)>0: lo=m
            else: hi=m
        return lo
    ok=True
    for p in [TK+'/words/%s.json.gz'%a for a in ('6030','5907','5827','5551')]+OTHER:
        ww=legal.load(p); T,P=X.invoice(legal.check(ww)); ok&=str(kd_orig(T,P))==str(X.kappa_dec(T,P))
    need(ok,'kappa_dec (ln hoisted) == original implementation on %d words'%(4+len(OTHER)))
    # 5
    _old=os.environ.get('TK_PRICERUN_CACHE'); os.environ['TK_PRICERUN_CACHE']='1'      # regress.py disables the memo; the key itself is what is tested here
    loc=dict(paid={1:3},helpers={9:2}); nat=dict(helpers={9:2},main_adapters=208)
    k1=tkstack._pricerun_key(prof,'src',loc,nat,w,root); k2=tkstack._pricerun_key(prof,'src',dict(loc),dict(nat),w,root)
    k3=tkstack._pricerun_key(prof,'src2',loc,nat,w,root); k4=tkstack._pricerun_key(prof,'src',dict(paid={1:4},helpers={9:2}),nat,w,root)
    k5=tkstack._pricerun_key(prof,'src',dict(paid={'1':3},helpers={9:2}),nat,w,root)
    need(k1 and k1==k2 and len({k1,k3,k4,k5})==4,'price.run memo key: stable for equal inputs, distinct for changed source / invoice / key type')
    if _old is None: os.environ.pop('TK_PRICERUN_CACHE',None)
    else: os.environ['TK_PRICERUN_CACHE']=_old
    print('ALL PASS' if not fails else '%d FAIL'%len(fails)); return 1 if fails else 0

if __name__=='__main__': sys.exit(main())
