"""bitworker: run a BIT package's OWN verifier pipeline on a candidate word, in an isolated process (python3.12 -I -B, scrubbed env, temp dir, no network by construction).
usage:  python3.12 -I -B bitworker.py PKGCOPY_DIR RECIPE PATCHED(0|1) [WORD.json.gz]      -> prints @@RESULT@@ {json}
recipe 'conj' (PR #5708 layout): native.replay (+moduli 101,10201) of the candidate -> LOCAL-RESULT.json -> global_retirement.py -> ordinary.py -> independent.py.
PATCHED=1: the claim literals of ordinary.py / independent.py (tested, uniform, raw interval, final admitted) are re-derived from the candidate's own invoice (recorded in the result);
PATCHED=0: nothing is patched (the published word must reproduce the published receipts byte-for-byte)."""
import sys,os,json,gzip,subprocess,time,re
from fractions import Fraction as F
def nine(D,patched,res,HERE,t0):
    """recipe 'nine' (PR #5512 layout).  unpatched: the package's own verify.py + independent.py (cold replays, authenticate() included).  patched: native replay of the candidate (local_relations.replay, moduli 101 and 101^2)
    -> LOCAL-RESULT.json -> global_relations.py -> target_involutions.py -> ordinary.py (claim literals re-derived from the candidate invoice)."""
    def run(name,*flags):
        p=subprocess.run([sys.executable,'-B']+list(flags)+[D+'/'+name],cwd=D,capture_output=True,text=True,timeout=400,env={'PATH':'/usr/bin:/bin','HOME':D,'PYTHONDONTWRITEBYTECODE':'1'})
        if p.returncode: raise ValueError(name+' failed: '+(p.stderr or p.stdout)[-1500:])
        return p.stdout
    if not patched:
        res['stage']='verify.py'; res['verify']=run('verify.py').strip()[-300:]
        res['stage']='independent.py'; res['independent_run']=run('independent.py').strip()[-300:]
        o=json.load(open(D+'/ORDINARY-RESULT.json')); res['admitted']=o['admitted']; res['local_paid']=json.load(open(D+'/LOCAL-RESULT.json'))['stats']['paid']; res['ok']=True; res['stage']='done'; return
    sys.path.insert(0,D); import local_relations as LR
    word=LR.read(LR.R/'WORD.json.gz'); base,frames,old=LR.source(); owned=set(word['owned'])
    res['stage']='local replay'
    stats=LR.replay(base,frames,word['records'],owned)
    for m in (101,101**2): LR.replay(base,frames,word['records'],owned,m)
    LR.put('LOCAL-RESULT.json',dict(status='PASS_G20_NINE_OWNED_RELATIONS_ALL660_COLUMNS',stats=stats)); res['local_paid']=stats['paid']
    sub=open(D+'/global_relations.py').read()
    new="[P.__setitem__(k,P.get(k,0)+18*(nl[k]-rl[k])) for nl,rl in [(Counter({int(a):b for a,b in read(R/'LOCAL-RESULT.json')['stats']['paid'].items()}),Counter(e[4] for e in L.source()[2] if e[0] in('Q','COPY')))] for k in set(nl)|set(rl)];P={k:v for k,v in P.items() if v}"
    if 'P[1]-=162;P[7]-=162' not in sub: raise ValueError('global_relations.py patch anchor missing')
    open(D+'/global_relations.py','w').write(sub.replace('P[1]-=162;P[7]-=162',new))
    res['stage']='global_relations'; run('global_relations.py'); res['stage']='target_involutions'; run('target_involutions.py')
    inv=json.load(open(D+'/INVOICE.json')); res['invoice']=inv
    T={int(k):v for k,v in inv['targets'].items()}; P={int(k):v for k,v in inv['paid'].items()}
    raw=crossing(T,P)
    tested=F(int(raw*10**8),10**8); uniform=tested-F(1,10**8); lo=F(int(raw*10**13),10**13); hi=lo+F(1,10**13)
    def lit(x,d): return '.'+str(x.numerator*10**d//x.denominator).rjust(d,'0')
    o=open(D+'/ordinary.py').read()
    for a,b in [("sum(P.values())==56997 and ",""),(" and P[7]==162",""),("M==56997 and ",""),("tested=F('.00348398')","tested=F('%s')"%lit(tested,8)),("uniform=F('.00348397')","uniform=F('%s')"%lit(uniform,8)),("raw_lo=F('.0034839853304');raw_hi=F('.0034839853305')","raw_lo=F('%s');raw_hi=F('%s')"%(lit(lo,13),lit(hi,13)))]:
        if a not in o: raise ValueError('ordinary.py patch anchor missing: '+a)
        o=o.replace(a,b)
    open(D+'/ordinary.py','w').write(o); res['claims']=dict(tested=str(tested),uniform=str(uniform),raw_lo=str(lo),raw_hi=str(hi))
    res['stage']='ordinary'; run('ordinary.py')
    o=json.load(open(D+'/ORDINARY-RESULT.json')); res['admitted']=o['admitted']; res['tail']=o['tail']; res['ok']=True; res['stage']='done'

class Done(Exception): pass
def crossing(T,P,lo='0.0001',hi='0.02'):
    """raw crossing sum T r^(1-k) = sum P r^(1-k) by Decimal bisection (python3.12 stdlib only; = bitval.crossing)"""
    import decimal; D=decimal.Decimal; decimal.getcontext().prec=60
    def f(k):
        t=1-k; return sum(c*D(r)**t for r,c in T.items())-sum(c*D(r)**t for r,c in P.items())
    a,b=D(lo),D(hi); fa=f(a)
    for _ in range(150):
        m=(a+b)/2; fm=f(m)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return (a+b)/2

def main():
    D,recipe,patched=sys.argv[1],sys.argv[2],sys.argv[3]=='1'
    HERE=os.environ.get('BITTK_HERE') or os.path.dirname(os.path.abspath(__file__))
    res=dict(ok=False,stage='start',recipe=recipe,patched=patched); t0=time.time()
    try:
        sys.path.insert(0,D); os.chdir(D)
        if recipe=='nine': nine(D,patched,res,HERE,t0); raise Done()
        if recipe!='conj': raise ValueError('recipe %s not implemented'%recipe)
        res['stage']='load'
        import integration as L, native
        word=L.read(L.R/'WORD.json.gz'); base=L.read(L.R/'prior/WORD.json.gz'); _,frames,_=L.source()
        L.need(word['start']==base['start'] and word['final']==base['final'] and word['owned']==base['owned'],'Unchanged target and owned contracts')
        res['stage']='native.replay'
        physical=dict(final=word['start'],start=word['final']); owned=set(word['owned'])
        stats=native.replay(physical,frames,word['records'],owned)
        moduli=[native.replay(physical,frames,word['records'],owned,m)['native_modulus'] for m in (101,10201)]
        L.put('LOCAL-RESULT.json',dict(status='PASS_G20_CONJUGATION_ALL685_COLUMNS',stats=stats,native_moduli=moduli))
        res['local_paid']=stats['paid']
        def run(name):
            p=subprocess.run([sys.executable,'-I','-B','-W','error',D+'/'+name],cwd=D,capture_output=True,text=True,timeout=200)
            if p.returncode: raise ValueError(name+' failed: '+(p.stderr or p.stdout)[-1500:])
        res['stage']='global_retirement'; run('global_retirement.py')
        inv=json.load(open('INVOICE.json')); res['invoice']=inv
        if patched:
            T={int(k):v for k,v in inv['targets'].items()}; P={int(k):v for k,v in inv['paid'].items()}
            raw=crossing(T,P); n=int(raw*10**14)
            tested=F(n-4,10**14); uniform=F(n-5,10**14); lo=F(n-2,10**14); hi=F(n+2,10**14)
            new=dict(tested=tested,uniform=uniform,lo=lo,hi=hi)
            def dec(x): return ('%.14f'%float(x)) if False else format(x.numerator*10**14//x.denominator,'015d').rjust(15,'0')
            def lit(x,d=14): s=str(x.numerator*10**d//x.denominator).rjust(d,'0'); return '.'+s
            sub={'.00350771905977':lit(tested),'.00350771905976':lit(uniform),'.00350771905979':lit(lo),'.00350771905983':lit(hi)}
            for fn in ('ordinary.py','independent.py'):
                s=open(fn).read()
                for a,b in sub.items(): s=s.replace(a,b)
                s=s.replace("need(backend==F(3507719059749,10**15) and backend>old,","need(backend>old,").replace('L.need(backend==F(3507719059749,10**15),"Complete ordinary saving")',"L.need(backend>F(L.read(L.R/'prior/ORDINARY-RESULT.json')['admitted']),'Complete ordinary saving')")
                s=s.replace('M==56223 and ','').replace('sum(P.values())==56223 and ','').replace('56223','sum(paid.values())' if fn=='independent.py' else '56223')
                s=s.replace("cmax=F('.00351')","cmax=F('%s')"%lit(F(-(-int(raw*10**5)//1)-0+1 if False else (int(raw*10**5)+1),10**5),5))
                open(fn,'w').write(s)
            res['claims']={k:str(v) for k,v in new.items()}
        res['stage']='ordinary'; run('ordinary.py')
        res['stage']='independent'; run('independent.py')
        o=json.load(open('ORDINARY-RESULT.json')); res['admitted']=o['admitted']; res['raw_independent']={k:o['raw_crossing_independent_exact'][k]['saving'] for k in o['raw_crossing_independent_exact']}
        res['tail']=o['tail']; res['independent']=json.load(open('INDEPENDENT-RESULT.json'))['ordinary']
        res['ok']=True; res['stage']='done'
    except Done: pass
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        res['error']=(str(e) or repr(e))[-1800:]
    res['seconds']=round(time.time()-t0,1)
    print('@@RESULT@@'+json.dumps(res,default=str))
main()
