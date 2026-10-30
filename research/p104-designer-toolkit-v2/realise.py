"""tk realise DAG [--schedule exact|lazy|FILE] [--drop-helper H[,H..]] [--out F] [--no-verify] [--no-price]
DAG + schedule -> word JSON (price/check format), then legal.check with the localised report and the exact kappa.
Schedule: exact = the DAG's recorded MOVE hops (default); lazy = one direct MOVE wherever a register's frame differs from the frame its next op needs;
FILE = json {"hops": [[op_index, reg, [frames]],..], "op_frames": {"op_index": frame}} (frames: table index or inline basis list).
Value-level report (before legality): ops removed, ops whose result form differs from the DAG's recorded value, delivered outputs that differ from the contract."""
import os,json,time
from tkcommon import *
import dag as D
import check as CK
def main(a):
    dg=D.load(a.dag if os.path.exists(a.dag) else OUT+'/%s.dag.json.gz'%a.dag)
    sch='lazy' if a.schedule=='lazy' else (None if a.schedule=='exact' else json.load(open(a.schedule)))
    drop=[int(x) for x in a.drop_helper.split(',')] if a.drop_helper else []
    t=time.time(); w,rep=D.realise(dg,sch,drop,verify=not a.no_verify)
    out=a.out or OUT+'/realised_%s.json.gz'%os.path.basename(a.dag).replace('.dag.json.gz','').replace('.json.gz','')
    os.makedirs(os.path.dirname(out),exist_ok=True); D.save(w,out)
    print('realised %d events, %d regs -> %s (%.1fs)'%(len(w['program']),len(w['initial']),out,time.time()-t))
    if rep['dropped']:
        print('DROPPED helpers %s: %d ops removed; first: %s'%(rep['dropped'],len(rep['removed_ops']),rep['removed_ops'][:4]))
        by={}
        for i,op,r,s in rep['removed_ops']:
            other=r if s in rep['dropped'] else s
            if r not in rep['dropped']: by.setdefault(r,[]).append(i)
        print('  registers that lost an incoming term: %s'%sorted(by)[:20])
    if rep['value_errors']:
        print('VALUE ERRORS (first op per register whose result form differs from the DAG record; later ops inherit it), first %d:'%min(5,len(rep['value_errors'])))
        for i,o,r in rep['value_errors'][:5]: print('  value-op %d %s on reg %d (%s)'%(i,o,r,dg['regs'][str(r)][0]))
    if rep['undelivered']:
        print('UNDELIVERED outputs: %d registers differ from the required form'%len(rep['undelivered']))
        for r,ro,d,nn in rep['undelivered'][:8]: print('  reg %d (%s): off by %d terms, e.g. %s'%(r,ro,nn,d))
    # legality + localisation
    role=roles(w); r2=legal.check(w,maxviol=a.max)
    desc=CK.describe(w,w['program'],role,r2['violations'])
    print('check: %s (%d violations)'%('LEGAL' if r2['ok'] else 'ILLEGAL',len(desc)))
    for v in desc:
        print(' - [%s] event %s: %s'%(v['rule'],v['event'],v['detail'][:200]))
        for c in v.get('context',[]): print('      '+c)
    if r2['ok'] and not a.no_price:
        T,P=X.invoice(r2); import decimal
        print('kappa = %s'%str(X.kappa_dec(T,P,50))[:20])
    return 0 if r2['ok'] and not rep['undelivered'] and not rep['value_errors'] else 1
