"""tk check WORD [--native] [--exact] [--max N] [--json]
Legality oracle with error localisation.  Fast (~1 s): infra/legal.py re-implementation of local.replay + the literal part of native(), ALL violations.
Each violation is reported with: event index, op, register, its ROLE (X source / Y target / helper / owned scratch), the frame it is in, the event that last
moved it, and the rule (the exact `need(..., 'rule')` string of the real local.py).
--native : every distinct MOVE frame pair and helper boundary is run through the real native Gaussian-recipe check (vendored clifford_exact/native_verify), rank == dim gap.
--exact  : run the REAL local.replay / reverse_columns / native on the word and report the first rejection (slow, minutes; use via hq)."""
import sys,os,json,time,collections
from tkcommon import *
def op_in(e): return e[0] in('ADD','COPY','SCALE')
def lastev(prog,r,k=3):
    out=[]
    for i in range(len(prog)-1,-1,-1):
        e=prog[i]
        if e[1]==r or (e[0] in('ADD','COPY') and e[2]==r): out.append((i,e))
        if len(out)>=k: break
    return out
def regs_of(rule,d):
    import re
    d=str(d)
    if rule.startswith('Final frames'): return [int(x) for x in re.findall(r'\((\d+), ',d)]
    if rule.startswith('Endpoint rows'): return [int(x) for x in re.findall(r'\d+',d.split(':',1)[1])] if ':' in d else []
    if rule.startswith(('Helper endpoints','Literal')) and d.strip().isdigit(): return [int(d)]
    return []
def describe(w,prog,role,violations):
    fr=legal.spans(w); dim=lambda f:len(w['frames'][f]) if f is not None else -1
    want={i for i,_,_ in violations if i>=0}
    # one pass: last event that set each register's frame / last event touching it
    last_set={};last_touch={};snap={}
    cur=list(w['initial'])+[None]*8
    for i,e in enumerate(prog):
        if i in want: snap[i]=(dict(last_set),dict(last_touch),list(cur))
        op,r=e[0],e[1]
        last_touch[r]=i
        if op=='MOVE': last_set[r]=i; cur[r]=e[3]
        elif op=='INIT': last_set[r]=i; cur[r]=e[2]
        elif op=='CLEAR': last_set[r]=i; cur[r]=None
        elif op in('ADD','COPY'): last_touch[e[2]]=i
    out=[]
    for i,rule,d in violations:
        rec=dict(event=i,rule=rule,detail=str(d))
        if i>=0:
            e=prog[i]; r=e[1]; ls,lt,cu=snap[i]
            rec.update(op=e[0],reg=r,role=role(r),ev=e)
            ctx=[]
            ctx.append('reg %d is %s, frame now %s'%(r,role(r),dimstr(w,cu[r]) if r<len(cu) else '?'))
            if r in ls: ctx.append('its frame was last set by event %d %s'%(ls[r],prog[ls[r]]))
            else: ctx.append('never moved before (still at declared initial frame)')
            if e[0] in('ADD','COPY'):
                s=e[2]; ctx.append('source reg %d is %s, frame now %s%s'%(s,role(s),dimstr(w,cu[s]),' (set by event %d)'%ls[s] if s in ls else ''))
            if rule.startswith('Nested') and isinstance(d,tuple):
                _,a_,b_,pv=d; A,B=fr[a_],fr[b_]
                if pv: ctx.append('owned (descending) move %d->%d: need span(b) strictly inside span(a); vectors of b not in a: %s'%(a_,b_,sorted(B-A)[:4]))
                else: ctx.append('move %d(dim %d)->%d(dim %d): need span(a) strictly inside span(b); %s'%(a_,dim(a_),b_,dim(b_),'spans equal' if A==B else 'vectors of a not in b: %s'%sorted(A-B)[:4]))
            if rule.startswith('Transport source') and isinstance(d,tuple):
                ctx.append('event expects reg in frame %s (dim %d) but it is in frame %s; owned flag in event=%s'%(d[2],dim(d[2]),d[1],d[3]))
            if rule.startswith(('Scalar destination','Common scalar chart','Dyadic','Fixed scalar')) and op_in(e):
                ctx.append('event declares frame %s (dim %d)'%(e[-1],dim(e[-1])))
            rec['context']=ctx
        else:
            ctx=[]
            for r in regs_of(rule,d)[:6]:
                ctx.append('reg %d is %s; last events touching it: %s'%(r,role(r),[(j,x[0],x[1:]) for j,x in lastev(prog,r)]))
            rec['context']=ctx
        out.append(rec)
    return out
def native_check(w,prog,role,root=None,limit=None):
    root=root or closure_root()
    import native_pair as N
    N.init(root); fr=w['frames']
    bad=[];seen={};t=time.time()
    def test(a,b,where):
        k=(a,b)
        if k not in seen: seen[k]=N.ok(tuple(fr[a]),tuple(fr[b]))
        if not seen[k][0]: bad.append((where,a,b,seen[k][1]))
    main=set(w['live'])|{r+112 for r in w['live']}
    for i,e in enumerate(prog):
        if e[0]=='MOVE': test(e[2],e[3],'event %d MOVE reg %d (%s)'%(i,e[1],role(e[1])))
    for r in range(len(w['initial'])):
        if r not in main: test(w['initial'][r],w['final'][r],'helper boundary reg %d'%r)
    return dict(distinct_pairs=len(seen),bad=bad[:50],nbad=len(bad),seconds=round(time.time()-t,1))
def exact_check(path,wait=False,TL=1800):
    """real local.replay/reverse_columns/native via hq (stage-by-stage; the first rejecting need() message is the localisation)"""
    cc,f=cache_get('exact',path)
    if cc and ('error' in cc or 'native' in cc.get('stages',{})): return cc
    submit('tk_exact_'+sha(path)[:10],TL,[PY,'-B',HERE+'/real.py',path,'--upto','native','--out',f],wait)
    if not wait: return dict(submitted=True,result_file=f)
    return json.load(open(f)) if os.path.exists(f) else dict(error='no result file')
def main(a):
    path,w=load(a.word); prog=w['program']; role=roles(w)
    t=time.time(); rep=legal.check(w,maxviol=a.max); dt=time.time()-t
    desc=describe(w,prog,role,rep['violations'])
    res=dict(word=a.word,legal=rep['ok'],nviolations=len(desc),violations=desc,paid=rep['paid'],helpers=rep['helpers'],seconds=round(dt,2))
    if a.native:
        res['native']=native_check(w,prog,role); res['legal_native']=res['native']['nbad']==0
    if a.exact: res['exact']=exact_check(path,a.wait)
    if a.json: print(json.dumps(res,indent=1,default=str)); return 0 if rep['ok'] else 1
    print('%s: %s (%d regs, %d events, %.1fs)'%(a.word,'LEGAL' if rep['ok'] else 'ILLEGAL',len(w['initial']),len(prog),dt))
    for v in desc:
        print(' - [%s] event %s: %s'%(v['rule'],v['event'],v['detail'][:200]))
        for c in v.get('context',[]): print('      '+c)
    if a.native:
        n=res['native']; print('native: %d distinct frame pairs, %d bad (%.1fs)'%(n['distinct_pairs'],n['nbad'],n['seconds']))
        for b in n['bad'][:10]: print('   ',b)
    if a.exact: print('exact:',json.dumps(res['exact'],default=str))
    return 0 if rep['ok'] and res.get('legal_native',True) else 1
