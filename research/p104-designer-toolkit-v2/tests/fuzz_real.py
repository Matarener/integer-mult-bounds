#!/usr/bin/env python3
"""Mutation fuzz: `tk check` (infra/legal.py) versus the REAL verifier stack (unmodified local.replay, reverse_columns, native).
usage: fuzz_real.py WORD --mode single|multi --n N [--seed S] [--out DIR] [--deadline SEC] [--native-cap K]
Per mutant: tk verdict = legal.check(w)['ok']; real verdict = replay AND reverse_columns AND native all accept (native result memoised by the
set of (frame-pair) charts it depends on, so only mutants that introduce NEW MOVE pairs pay the ~140 s).
Appends one JSON line per mutant to DIR/fuzz_<word>_<mode>.jsonl (resumable: finished mutant indices are skipped); every disagreement
is minimised (greedy removal of mutation ops) and appended to DIR/DISAGREEMENTS.jsonl with a repro (word alias + op list + apply with tests/fuzz_real.py --repro).
Not covered here: price.run (tail side constraints / budgets) -- see backtest.py part A."""
import sys,os,json,gzip,copy,random,time,hashlib,traceback
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.join(HERE,'..'); sys.path.insert(0,TKD); sys.dont_write_bytecode=True
from tkcommon import *
import real as R
COEF=['1','-1','1/2','-1/2','2','-2','1/4','3','1/3']
def mutate_once(w,rng,nearby):
    """apply one random mutation in place; return op descriptor (JSON-serialisable, replayable by apply_op)"""
    prog=w['program']; nf=len(w['frames']); NR=len(w['initial'])+8
    for _ in range(50):
        k=rng.random(); i=rng.randrange(len(prog)); e=prog[i]; op=e[0]
        if k<0.10:   return ['del',i]
        if k<0.18:   return ['dup',i]
        if k<0.34:   return ['swap',i]
        if k<0.40:   return ['final',rng.randrange(len(w['initial'])),rng.randrange(nf)]
        if k<0.44:   return ['init',rng.randrange(len(w['initial'])),rng.randrange(nf)]
        if op=='MOVE':
            c=rng.random()
            if c<0.4: return ['set',i,3,rng.randrange(nf)]
            if c<0.6: return ['set',i,3,prog[nearby(i)][-1] if prog[nearby(i)][0] in('ADD','COPY','SCALE') else rng.randrange(nf)]
            if c<0.75: return ['set',i,2,rng.randrange(nf)]
            if c<0.9: return ['set',i,4,not e[4]]
            return ['set',i,1,rng.randrange(NR)]
        if op in('ADD','COPY'):
            c=rng.random()
            if c<0.35: return ['set',i,2,prog[nearby(i)][1]]          # source of a nearby event: often same frame, wrong value
            if c<0.55: return ['set',i,3,rng.choice(COEF)]
            if c<0.75: return ['set',i,4,rng.randrange(nf)]
            if c<0.9: return ['set',i,1,prog[nearby(i)][1]]
            return ['set',i,2,rng.randrange(NR)]
        if op=='SCALE':
            return ['set',i,2,rng.choice(COEF)] if rng.random()<.5 else ['set',i,3,rng.randrange(nf)]
        if op in('INIT','CLEAR'): return ['set',i,2,rng.randrange(nf)]
    return ['del',0]
def apply_op(w,o):
    p=w['program']
    if o[0]=='del': p.pop(o[1]%len(p))
    elif o[0]=='dup': i=o[1]%len(p); p.insert(i,copy.deepcopy(p[i]))
    elif o[0]=='swap': i=o[1]%(len(p)-1); p[i],p[i+1]=p[i+1],p[i]
    elif o[0]=='final': w['final'][o[1]]=o[2]
    elif o[0]=='init': w['initial'][o[1]]=o[2]
    elif o[0]=='set':
        e=p[o[1]%len(p)]
        if o[2]<len(e): e[o[2]]=o[3]
def mutant(base,ops):
    w=copy.deepcopy(base)
    for o in ops: apply_op(w,o)
    return w
_native_memo={}
def native_key(w):
    pairs=sorted({(tuple(w['frames'][e[2]]),tuple(w['frames'][e[3]])) for e in w['program'] if e[0]=='MOVE'})
    main=set(w['live'])|{r+112 for r in w['live']}
    hb=sorted({(tuple(w['frames'][w['initial'][r]]),tuple(w['frames'][w['final'][r]])) for r in range(len(w['initial'])) if r not in main})
    ad=[(tuple(w['frames'][w['initial'][r]]),tuple(w['frames'][w['final'][r+112]]),q) for r,q in zip(w['live'],w['ports'])]
    return hashlib.sha1(json.dumps([pairs,hb,ad],default=str).encode()).hexdigest()
def real_verdict(L,w,native_budget):
    """-> (ok, stage, message).  native_budget: list [remaining uncached native runs]"""
    try: L.replay(w)
    except BaseException as e: return False,'replay',(str(e) or repr(e))[:120]
    try: L.reverse_columns(w)
    except BaseException as e: return False,'reverse_columns',(str(e) or repr(e))[:120]
    k=native_key(w)
    if k not in _native_memo:
        if native_budget[0]<=0: return None,'native-skipped','native cap reached'
        native_budget[0]-=1
        try: L.native(w); _native_memo[k]=(True,'')
        except BaseException as e: _native_memo[k]=(False,(str(e) or repr(e))[:120])
    ok,m=_native_memo[k]; return ok,'native',m
def tk_verdict(w):
    try:
        rep=legal.check(w,maxviol=5); return rep['ok'],sorted({v[1] for v in rep['violations']})
    except BaseException as e: return False,['TK-CRASH '+repr(e)[:80]]
def main():
    A=sys.argv[1:]; word=A[0]
    g=lambda f,d:(A[A.index(f)+1] if f in A else d)
    mode=g('--mode','single'); N=int(g('--n','20')); seed=int(g('--seed','0')); out=g('--out',os.path.join(HERE,'..','ext','TKAUDIT','fuzz'))
    deadline=time.time()+float(g('--deadline','1e9')); cap=[int(g('--native-cap','1000'))]
    os.makedirs(out,exist_ok=True)
    path=resolve(word); base=legal.load(path); n=len(base['initial']); L=R.local_for(n)
    prog=base['program']; rng_n=random.Random(7)
    nearby=lambda i:min(len(prog)-1,max(0,i+random.Random(i).randrange(-150,151)))
    f=os.path.join(out,'fuzz_%s_%s.jsonl'%(word,mode)); done=set()
    if os.path.exists(f):
        for l in open(f):
            try: done.add(json.loads(l)['i'])
            except Exception: pass
    # control: the unmutated word must be accepted by both
    ok0=tk_verdict(base)[0]; r0=real_verdict(L,base,cap)
    print('control',word,'tk',ok0,'real',r0,flush=True)
    nag=nd=0
    with open(f,'a') as fo, open(os.path.join(out,'DISAGREEMENTS.jsonl'),'a') as fd:
        for i in range(N):
            if i in done: continue
            if time.time()>deadline: print('deadline reached at',i); break
            rng=random.Random('%s|%s|%d|%d'%(word,mode,seed,i))
            nops=1 if mode=='single' else rng.randrange(2,7)
            w=copy.deepcopy(base); ops=[]
            for _ in range(nops):
                o=mutate_once(w,rng,nearby); apply_op(w,o); ops.append(o)
            t,rules=tk_verdict(w); rv=real_verdict(L,w,cap)
            if rv[0] is None: rec=dict(word=word,mode=mode,seed=seed,i=i,ops=ops,tk=t,real=None,note=rv[2]); fo.write(json.dumps(rec)+'\n'); fo.flush(); continue
            agree=(t==rv[0]); rec=dict(word=word,mode=mode,seed=seed,i=i,ops=ops,tk=t,tk_rules=rules,real=rv[0],real_stage=rv[1],real_msg=rv[2],agree=agree)
            fo.write(json.dumps(rec)+'\n'); fo.flush(); nd+=1
            if not agree:
                nag+=1; cur=list(ops)
                changed=True
                while changed and len(cur)>1:       # greedy minimisation of the op list keeping the disagreement
                    changed=False
                    for j in range(len(cur)):
                        c=cur[:j]+cur[j+1:]; w2=mutant(base,c); t2,_=tk_verdict(w2); r2=real_verdict(L,w2,cap)
                        if r2[0] is not None and t2!=r2[0]: cur=c; changed=True; break
                fd.write(json.dumps(dict(word=word,mode=mode,seed=seed,i=i,minimal_ops=cur,tk=t,tk_rules=rules,real=rv[0],real_stage=rv[1],real_msg=rv[2],
                                        repro='tests/fuzz_real.py --repro %s <ops json>'%word))+'\n'); fd.flush()
    print('done',word,mode,'new mutants',nd,'disagreements',nag,flush=True)
if __name__=='__main__':
    if '--repro' in sys.argv:       # fuzz_real.py --repro WORD 'OPS_JSON'
        a=sys.argv; word=a[a.index('--repro')+1]; ops=json.loads(a[a.index('--repro')+2]); base=legal.load(resolve(word)); w=mutant(base,ops)
        L=R.local_for(len(base['initial'])); print('tk',tk_verdict(w),'real',real_verdict(L,w,[1])); sys.exit(0)
    main()
