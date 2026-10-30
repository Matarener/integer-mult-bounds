"""tk decompile WORD [--out F] [--no-forms]   word -> value DAG (see dag.py): ops (MOVE-free), per-op value ids (linear forms over the inputs), carriers, required outputs, schedule (the recorded MOVE hops)."""
import os,time
from tkcommon import *
import dag as D
def main(a):
    path,w=load(a.word); t=time.time()
    d=D.decompile(w,forms=not a.no_forms)
    out=a.out or OUT+'/%s.dag.json.gz'%os.path.basename(a.word).replace('.json.gz','').replace('.json','')
    os.makedirs(os.path.dirname(out),exist_ok=True); D.save(d,out)
    nm=sum(1 for e in w['program'] if e[0]=='MOVE')
    print('decompiled %s: %d regs (X %d, Y %d, helper %d, owned %d), %d value ops (%d program events, %d MOVEs -> %d hop chains), %d distinct values, %.1fs'%(
        a.word,d['meta']['npub'],sum(1 for v in d['regs'].values() if v[0]=='X'),sum(1 for v in d['regs'].values() if v[0]=='Y'),sum(1 for v in d['regs'].values() if v[0]=='helper'),d['meta']['nowned'],
        len(d['ops']),len(w['program']),nm,len(d['schedule']['hops']),len(d['values']),time.time()-t))
    print('delivered outputs equal the contract: %s%s'%(d['delivered_ok'],'' if d['delivered_ok'] else '  bad regs %s'%d['bad_regs'][:12]))
    print('wrote',out)
    return 0 if d['delivered_ok'] else 1
