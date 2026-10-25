"""Write the helper-472 staged word (frame-repaired) as a complete BORROW-WORD and audit it."""
import gzip,json,sys,time
from fractions import Fraction as Q
from timeline import *
sys.path.insert(0,PKG)
from audit_verify import semantics
from construct2 import assemble
from repair import repair
for tag in ('base','extra'):
    w=load(tag); ev=events(w)
    # same releases: locate the producer event of 472 in this provider
    prod=next(e['pos'] for e in ev if e['sec']=='B' and e['g'][0]=='add' and e['g'][1]==472)
    cut=next(e['pos'] for e in ev if e['sec']=='B' and e['idx']==283)+1 if False else None
    from construct import exact_fixed
    v={472:Q(1),624:Q(-1),628:Q(-1,2)}
    # latest cut where the identity holds exactly
    c=None
    for p in range(prod,prod-600,-1):
        ok,_=exact_fixed(w,ev,p,v)
        if ok: c=p; break
    print(tag,'producer',prod,'exact cut',c)
    if c is None: continue
    try:
        x,mark=assemble(w,ev,472,C.span((429,51)),c,[(prod,['add',624,472,-1,1]),(prod,['add',628,472,-1,2])])
        x,_=repair(x,mark)
        b,wd,*_=C.frame_bill(x); C.hygiene(x)
    except Exception as e:
        print(tag,'construction fails',e); continue
    t=time.time(); sem=semantics(C,x); print(tag,'semantics',sem['forward'],sem['dual'],round(time.time()-t,1),'s; bill',b,'w7',wd.get(7))
    path=f'words/W472-{tag}.json.gz'
    open(path,'wb').write(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
    print('wrote',path)
