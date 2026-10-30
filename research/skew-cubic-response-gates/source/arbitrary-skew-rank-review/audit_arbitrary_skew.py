#!/usr/bin/env python3
"""Independent native-rank, all-f transport and inventory review.
Apache-2.0; substantial OpenAI Codex assistance. No search or admission.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,sys,types,copy
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent
old=R/'completed-gates-review/audit_gates.py';a=types.ModuleType('review_pinned_algebra');a.__file__=str(old)
exec(compile(old.read_bytes(),str(old),'exec',dont_inherit=True,optimize=0),a.__dict__)
ja,qc=a.ja,a.qc
def embed(d,m):
    n=len(d['rows']);return qc.Mono(tuple(d['rows'])+tuple(1<<i for i in range(n,m)),d['offset'],tuple(d['alpha'])+(0,)*(m-n),tuple(d['quad'])+(0,)*(m-n),d['constant'],d['global_phase'])
def stage_objects(q,J):
    k=2*q+1;m=4*q+4;F=a.F(m,k);B={s:a.P(m,s)@a.N(m,0).inv()@J for s in range(1,k+1)}
    Q=J.inv()@B[1]@J;Du=qc.identity(m)
    for s in range(4,2*q+1,2):Du=B[s]@Du
    Du=Du@B[3]@J
    return F,B,Q,Du
def convert(source,J,q):
    k=2*q+1;m=4*q+4;F,B,Q,Du=stage_objects(q,J)
    maps={'tail-Du-recovery':F@Du.inv()@F.inv(),'tail-Q1-recovery':F@Q.inv()@F.inv(),'tail-J':F@J@F.inv()}
    out=[]
    for e in source:
        if e['kind']in('ADD','SCALE','BANK_SWAP'):out.append(e);continue
        label=e['label'];fam=e.get('native_family');g=None
        if fam and fam['kind']=='N':g=a.N(m,fam['plane'])
        elif fam and fam['kind']=='J':
            fs=a.F(m,fam['completed']);g=fs@J@fs.inv()
            if fam.get('inverse'):g=g.inv()
        elif label=='fusion stage2 uniform fresh on former source':g=a.N(m,2)
        elif e.get('native_recipe_id')in maps:g=maps[e['native_recipe_id']]
        elif label.startswith('query')and label.endswith('source swap'):g=a.P(m,int(label.split()[0][5:]))
        elif label.startswith('w reverse')and label.endswith('ADDRESS'):g=a.P(m,2*int(label.split()[1][7:])+1)
        elif label in('fusion replace shared initial J by minus identity','final extraction D_final inverse sign'):g=a.scalar(m,2)
        a.need(g is not None,'covered actual source unary '+label)
        op,ex=a.independent.to_op(a.oldexpr(g));a.need(ex==[(g.global_phase*(1-r))%4 for r in range(4)],'full-field phase convention')
        out.append(dict(kind='NATIVE'if a.native(g)else'ADDRESS_OR_UNIT',bank=e['bank'],label=label,x_monomial=g.data(),rank_per_f=a.native(g),one_coordinate_literal_circuit=op.circuit,one_coordinate_tableau=op.tab,phase_exponent=g.global_phase))
    return out
def inspect(d,q,source=None,claimed=None,name=''):
    k=2*q+1;n=2*q+2;m=4*q+4;J=embed(d,m);F,B,Q,Du=stage_objects(q,J)
    a.need(a.eq(J@J,a.scalar(m,2)),'arbitrary-support exact skew square')
    JS={s:a.F(m,s)@J@a.F(m,s).inv()for s in range(k+1)}
    ar={s:a.native(g)for s,g in JS.items()};r=a.native(F@J);dd=r-2*k;W=F@Q.inv()@F.inv();w=a.native(W)
    for s in range(k+1):
        a.need(a.eq((F@a.F(m,s).inv())@JS[s]@a.F(m,s),F@J),'chronological parent factorization')
        a.need(ar[s]>=dd,'chronological J rank lower bound')
    a.need(a.eq(Q,J@a.P(m,1)@a.N(m,0).inv()),'Q exact sign')
    a.need(a.eq(W@(F@J),F@a.N(m,0)@a.P(m,1)),'Q-target exact all-f phase')
    a.need(a.native(F@a.N(m,0)@a.P(m,1))==m and w+r>=m,'full Q-target product and rank inequality')
    T=a.P(m,4)@JS[3];even=B[4]
    for t in range(3,q+1):
        step=a.P(m,2*t)@JS[2*t-1]@a.N(m,2*t-1)
        a.need(a.eq(a.F(m,2*t).inv()@step,B[2*t]@a.F(m,2*t-2).inv()),'noncommuting dynamic transport induction')
        T=step@T;even=B[2*t]@even
    a.need(a.eq(a.F(m,2*q).inv()@T,even@a.F(m,3).inv()),'even-index telescope no support assumption')
    C=a.F(m,2*q)@Du.inv()@a.F(m,2*q).inv();L=C@T@a.P(m,3);closed=a.scalar(m,2)
    for s in range(3,2*q+1):closed=a.N(m,s)@closed
    a.need(a.eq(L,closed) and a.native(L)==4*q-4,'universal L exact phase/rank')
    selected=[2*t-1 for t in range(2,q+1)];rho=a.native(T)
    a.need(rho<=sum(ar[s]for s in selected)+2*(q-2),'transport rank triangle')
    counts={s:0 for s in range(k+1)};counts[0]=2
    for s in range(2,k+1):counts[s]=1 if s%2==0 else 2
    original=dict(counts)
    for s in selected:a.need(counts[s]>0,'selected occurrence paid');counts[s]-=1
    a.need(sum(original.values())==3*q+2 and sum(counts.values())==n+1,'complete and remaining J counts')
    A=n*(2*k-1);distance=max(0,4*q-4-rho)
    mass=A+sum(original[s]*ar[s]for s in original)+w+abs(4*q-4-rho)
    intermediate=A+2*q+sum(counts[s]*ar[s]for s in counts)+w
    coarse=A+2*q+(n+1)*dd+w
    a.need(mass>=intermediate>=coarse>=n*r,'complete tariff chain including negative d')
    if source is not None:
        a.need(a.stable(source['full_events'])==a.stable(source['prefix_events']+source['tail_events']),'source full/prefix/tail event mirrors agree')
        # Counts come from actual semantic source tags, including rank-zero J.
        actual=Counter()
        for e in source['full_events']:
            fam=e.get('native_family')
            if fam and fam.get('kind')=='J':actual[fam['completed']]+=1
            elif e.get('native_recipe_id')=='tail-J':actual[k]+=1
        a.need(dict(actual)=={s:c for s,c in original.items()if c},'actual q2/q3 complete J inventory')
        PP=convert(source['prefix_events'],J,q);TT=convert(source['tail_events'],J,q);E=PP+TT
        default_mass=sum(e['rank_per_f']for e in E if e['kind']=='NATIVE');du_rank=a.native(F@Du.inv()@F.inv())
        a.need(default_mass-du_rank==A+sum(original[s]*ar[s]for s in original)+w,'actual complete N-only and J/Q inventory')
        a.need(default_mass-du_rank+abs(4*q-4-rho)==mass,'saved optimized bill from actual default events and isolated replacement')
        M=a.independent.replay_old(E,n,m);Mi=a.independent.replay_old(E,n,m,inverse=True);target=a.oldexpr(F@J)
        a.need(M==[[target if i==j else{}for j in range(n)]for i in range(n)],'independent all-original-column default FJ target')
        a.need(a.independent.mm(M,Mi)==a.independent.identity(n,m)==a.independent.mm(Mi,M),'independent literal inverse both orders')
        i=next(t for t,e in enumerate(PP)if e['label']=='query3 source swap');j=next(t for t,e in enumerate(PP)if e['label']==f'query{2*q} source swap')
        col,row=a.independent.transported(PP,i,j,n,m);bank=PP[j]['bank']
        a.need(all(not e for s,e in enumerate(col)if s!=bank)and all(not e for s,e in enumerate(row)if s!=bank),'actual complete two-sided isolation')
        a.need(col[bank]==a.oldexpr(T) and row[bank]==a.oldexpr(T.inv()),'actual noncommuting all-f transport')
        removed=[t for t,e in enumerate(TT)if e['label']=='joint U coordinate recovery'];a.need(len(removed)==1,'one whole deleted Du recovery')
        newtail=[e for t,e in enumerate(TT)if t not in removed]
        CC=a.independent.mm(a.independent.replay_old(newtail,n,m,inverse=True),a.independent.replay_old(TT,n,m))
        for e in reversed(PP[j+1:]):CC=a.independent.pullback(CC,e,m)
        I=a.independent.identity(n,m)
        a.need(all(CC[s][t]==I[s][t]for s in range(n)for t in range(n)if(s,t)!=(bank,bank))and CC[bank][bank]==a.oldexpr(C),'actual all-column current deletion defect and Gaussian phase')
    if claimed is not None:
        for key,val in [('chronological_arities',{str(s):v for s,v in ar.items()}),('remaining_J_multiplicity',{str(s):v for s,v in counts.items()}),('L_rank',4*q-4),('R_rank',rho),('Q_rank',w),('parent_rank',r),('intermediary_lower_bound',intermediate),('stock',n*r),('complete_mass',mass)]:
            a.need(claimed[key]==val,'saved finite fixture field '+key)
    return dict(case=name,q=q,parent_rank=r,d=dd,Q_rank=w,chronological_arities=ar,remaining_multiplicity=counts,transport_rank=rho,complete_mass=mass,intermediate=intermediate,coarse=coarse,stock=n*r,actual_binding=source is not None)
def run():
    root=R/'root-joint';data=json.loads((root/'ARBITRARY-SKEW-GATE.json').read_text());a.need(len(data['fixtures'])==36,'36 saved finite fixtures')
    old=json.loads((R/'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())['fixtures'];out=[]
    stale_transport=[]
    for c in data['fixtures']:
        out.append(inspect(c['J'],c['q'],next(f for f in old if f['q']==c['q']),c,c['case']))
        m=4*c['q']+4;J=embed(c['J'],m)
        if not a.eq(a.P(m,4)@(a.F(m,3)@J@a.F(m,3).inv()),a.P(m,4)@(a.F(m,1)@J@a.F(m,1).inv())):stale_transport.append(c['case'])
    a.need(stale_transport,'stale two-plane completed chart is detected on wider support')
    extremes=[]
    for q in range(2,9):
        m=4*q+4;k=2*q+1
        extremes.append(inspect(a.F(m,k).inv().data(),q,name='zero-target-extreme-negative-d'))
        extremes.append(inspect(a.N(m,0).data(),q,name='full-target-equality-d2'))
    bad=copy.deepcopy(old[0]);bad['full_events'].pop(0)
    try:inspect(data['fixtures'][0]['J'],2,source=bad,name='stale-event-mirror-control')
    except ValueError as e:a.need(str(e)=='source full/prefix/tail event mirrors agree','specific stale metadata rejection');rejection=str(e)
    else:raise ValueError('stale source event mirror accepted')
    return dict(status='PASS_INDEPENDENT_ANY_SUPPORT_SKEW_RANK_REVIEW',finite_bindings=out,rank_extremes=extremes,controls=dict(stale_source_mirror_rejected=rejection,stale_two_plane_transport_fails_for=sorted(set(stale_transport))),proof_domain='Written all-q conditional transport/inventory tariff; actual all-input q2/q3 bindings. Clifford B-rank and separately charged sites, not an arbitrary scalar/coupled topology theorem.',source_sha256=a.sha(root/'arbitrary_skew_gate.py'),receipt_sha256=a.sha(root/'ARBITRARY-SKEW-GATE.json'),no_new_kappa=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=json.loads(json.dumps(run()));dest=HERE/'AUDIT.json'
    if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:a.need(json.loads(dest.read_text())==out,'saved arbitrary-support audit')
    print(out['status']);print('finite actual cases',len(out['finite_bindings']),'rank extremes',len(out['rank_extremes']))
