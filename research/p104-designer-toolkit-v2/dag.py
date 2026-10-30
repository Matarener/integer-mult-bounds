"""Value-level DAG of a P104-family word: decompile (word -> DAG) and realise (DAG + schedule -> word).
DAG json (schema tk-dag/1):
  meta   : word-level constants (npub, nowned, live, ports, public, schema) -- everything not in the program
  frames : the frame table (bases), referenced by index; a schedule/op frame may also be an inline basis list [v1,v2..] (added to the table)
  regs   : {r: [role, init_frame, final_frame]}   role X|Y|helper|owned
  ops    : value ops in program order, MOVE-free: [op, dst, src|None, q|None, frame, vid]   (INIT/CLEAR: [op,r,None,None,frame,vid]; SCALE src None)
  values : [[nnz, hash, carriers]]  vid -> the linear form (over the 735 input columns) held by reg after the op, carriers = regs that hold it at the END (Y/X/helper)
  forms  : {vid: sparse form [[col,"q"],..]}   (optional, --forms)
  required: {r: sparse form}  the delivered outputs (contract: reg r = x_r (+ x_{r-112} if r is a Y register); owned 0)
  schedule: {"hops": [[op_index, reg, [f1,f2,..]],..]}  before value-op op_index (len(ops) = end of program) reg walks MOVE by MOVE through f1,f2,..
            (the last frame must be the frame the op needs); absent hops are filled by ONE direct MOVE where the frame differs.
"""
import json,gzip,hashlib,collections
from fractions import Fraction as Q
SCHEMA='tk-dag/1'
def _hash(f):
    return hashlib.blake2b(repr(sorted((c,str(v)) for c,v in f.items())).encode(),digest_size=8).hexdigest()
def role_fn(w):
    live=set(w['live']); n=len(w['initial'])
    def role(r):
        if r in live: return 'X'
        if r-112 in live and r<n: return 'Y'
        return 'helper' if r<n else 'owned'
    return role
def required(meta):
    n=meta['npub']; live=set(meta['live']); req={}
    for r in range(n+meta['nowned']):
        if r>=n: req[r]={}
        else:
            f={r:Q(1)}
            if r-112 in live: f[r-112]=Q(1)
            req[r]=f
    return req
def apply_forms(ops,meta,init_forms=None,on_op=None):
    """symbolic execution of the value ops -> (final forms, per-op vids)"""
    n=meta['npub']; no=meta['nowned']
    F=[{r:Q(1)} for r in range(n)]+[{} for _ in range(no)]
    res=[]
    for i,o in enumerate(ops):
        op,r,s,q=o[0],o[1],o[2],o[3]
        if op=='INIT' or op=='CLEAR': F[r]={}
        else:
            qq=Q(q)
            if op=='SCALE': F[r]={c:v*qq for c,v in F[r].items()}
            else:
                src=F[s]
                if op=='COPY': F[r]={c:v*qq for c,v in src.items()}
                else:
                    d=F[r]
                    for c,v in src.items():
                        t=d.get(c,0)+qq*v
                        if t: d[c]=t
                        else: d.pop(c,None)
        res.append(F[r] if on_op is None else on_op(i,r,F[r]))
    return F,res
def decompile(w,forms=True):
    if w.get('retired_public'): raise SystemExit('decompile: not prepared573-aware (retired public role is owned scratch with several lifetimes)')
    prog=w['program']; role=role_fn(w); n=len(w['initial']); no=w.get('owned_fields',8)     # owned-role count from the word's verifier profile (PR5627 local.py: owned_fields 8..9)
    meta=dict(npub=n,nowned=no,live=list(w['live']),ports=list(w['ports']),public=w.get('public',n),schema=w.get('schema'))
    if 'owned_fields' in w: meta['owned_fields']=w['owned_fields']
    regs={str(r):[role(r),w['initial'][r],w['final'][r]] for r in range(n)}
    for r in range(n,n+no): regs[str(r)]=['owned',None,None]
    ops=[];hops=[];pend=collections.defaultdict(list)    # reg -> frames of MOVEs since its last use
    for e in prog:
        if e[0]=='MOVE': pend[e[1]].append(e[3]); continue
        i=len(ops)
        for r in ([e[1],e[2]] if e[0] in('ADD','COPY') else [e[1]]):
            if pend.get(r): hops.append([i,r,pend.pop(r)])
        if e[0] in('ADD','COPY'): ops.append([e[0],e[1],e[2],e[3],e[4],None])
        elif e[0]=='SCALE': ops.append(['SCALE',e[1],None,e[2],e[3],None])
        else: ops.append([e[0],e[1],None,None,e[2],None])     # INIT / CLEAR
    for r in sorted(pend):
        if pend[r]: hops.append([len(ops),r,pend[r]])
    # the final MOVE of a register before an op is allowed to be a direct hop; keep chains as recorded
    vals={};vlist=[];carriers=collections.defaultdict(list)
    def on_op(i,r,f):
        h=_hash(f)
        if h not in vals: vals[h]=len(vlist); vlist.append([len(f),h,[]])
        ops[i][5]=vals[h]; return f
    F,_=apply_forms(ops,meta,on_op=on_op)
    for r in range(n):
        h=_hash(F[r])
        if h not in vals: vals[h]=len(vlist); vlist.append([len(F[r]),h,[]])
        vlist[vals[h]][2].append(r)
    dag=dict(schema=SCHEMA,meta=meta,frames=w['frames'],regs=regs,ops=ops,values=vlist,schedule=dict(hops=hops))
    req=required(meta); ok={r:F[r]==req[r] for r in range(n+no)}
    dag['required']={str(r):[[c,str(v)] for c,v in sorted(req[r].items())] for r in range(n)}
    dag['delivered_ok']=all(ok.values()); dag['bad_regs']=[r for r in ok if not ok[r]]
    if forms:
        # forms of every distinct value: recompute (cheap) keyed by vid
        fm={}
        def on2(i,r,f):
            v=ops[i][5]
            if v not in fm: fm[v]=[[c,str(x)] for c,x in sorted(f.items())]
            return f
        apply_forms(ops,meta,on_op=on2); dag['forms']={str(k):v for k,v in fm.items()}
    return dag
def _frame_id(dag,f,cache):
    if isinstance(f,int) or f is None: return f
    b=list(f); key=tuple(b)
    if key not in cache:
        dag['frames'].append(b); cache[key]=len(dag['frames'])-1
    return cache[key]
def realise(dag,schedule=None,drop=(),verify=True):
    """DAG + schedule -> (word, report). drop: helper register ids deleted from the DAG (their ops and uses are removed; the slot stays, final:=initial)."""
    import copy
    dag=copy.copy(dag); dag['frames']=list(dag['frames']); fc={}
    meta=dag['meta']; n=meta['npub']; no=meta['nowned']; drop=set(drop)
    rep=dict(dropped=sorted(drop),removed_ops=[],hop_errors=[],value_errors=[],undelivered=[])
    for h in drop:
        if dag['regs'][str(h)][0]!='helper': raise SystemExit('realise: --drop-helper %d is not a helper (role %s)'%(h,dag['regs'][str(h)][0]))
    ops=dag['ops']; keep=[]; remap={}
    for i,o in enumerate(ops):
        if o[1] in drop or (o[2] is not None and o[2] in drop):
            rep['removed_ops'].append((i,o[0],o[1],o[2])); continue
        remap[i]=len(keep); keep.append(o)
    sch=schedule if schedule is not None else dag.get('schedule',{})
    hops=collections.defaultdict(list)
    if sch!='lazy':
        for i,r,fs in sch.get('hops',[]):
            if r in drop: continue
            if i==len(ops): j=len(keep)
            else:
                j=remap.get(i)
                if j is None:       # op removed: hop moves to the next kept op
                    j=next((remap[k] for k in range(i,len(ops)) if k in remap),len(keep))
            hops[j].append((r,fs))
    opf=(sch.get('op_frames',{}) if sch!='lazy' else {})
    initial=[dag['regs'][str(r)][1] for r in range(n)]; final=[dag['regs'][str(r)][2] for r in range(n)]
    for h in drop: final[h]=initial[h]
    initial=[_frame_id(dag,f,fc) for f in initial]; final=[_frame_id(dag,f,fc) for f in final]
    fr=[None]*0; cur=list(initial)+[None]*no; owned=set(); prog=[]
    def mv(r,b,at):
        a=cur[r]
        if a==b: return
        prog.append(['MOVE',r,a,b,1 if r in owned else 0]); cur[r]=b
    for j,o in enumerate(keep):
        for r,fs in hops.get(j,[]):
            for f in fs: mv(r,_frame_id(dag,f,fc),j)
        op,r,s,q,f,_=o; f=_frame_id(dag,opf.get(str(j),f),fc)
        if op=='INIT': prog.append(['INIT',r,f]); owned.add(r); cur[r]=f; continue
        if op=='CLEAR':
            mv(r,f,j); prog.append(['CLEAR',r,f]); owned.discard(r); cur[r]=None; continue
        mv(r,f,j)
        if op=='SCALE': prog.append(['SCALE',r,q,f]); continue
        mv(s,f,j); prog.append([op,r,s,q,f])
    for r,fs in hops.get(len(keep),[]):
        for f in fs: mv(r,_frame_id(dag,f,fc),len(keep))
    for r in range(n): mv(r,final[r],len(keep))
    w=dict(final=final,frames=dag['frames'],initial=initial,live=meta['live'],ports=meta['ports'],program=prog,public=meta['public'],schema=meta['schema'])
    if 'owned_fields' in meta: w['owned_fields']=meta['owned_fields']
    if verify:
        okeep=keep
        recorded=[o[5] for o in keep]; seen=set()
        def on_op(i,r,f):
            h=_hash(f); vid=recorded[i]
            if vid is not None and r not in seen and dag['values'][vid][1]!=h and len(rep['value_errors'])<40: seen.add(r); rep['value_errors'].append((i,keep[i][:5],r))
            return f
        F,_=apply_forms(keep,meta,on_op=on_op)
        req=required(meta)
        for r in range(n+no):
            if F[r]!=req[r]:
                d={c:F[r].get(c,0)-req[r].get(c,0) for c in set(F[r])|set(req[r])}; d={c:v for c,v in d.items() if v}
                rep['undelivered'].append((r,dag['regs'][str(r)][0],{c:str(v) for c,v in sorted(d.items())[:6]},len(d)))
    return w,rep
def save(obj,path):
    (gzip.open(path,'wt') if path.endswith('.gz') else open(path,'w')).write(json.dumps(obj,separators=(',',':')))
def load(path):
    return json.load(gzip.open(path)) if path.endswith('.gz') else json.load(open(path))
