#!/usr/bin/env python3
"""Independent exact current-input suffix, native and support witness audit.
Apache-2.0; substantial OpenAI Codex assistance. No new supplier claim.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse,copy,hashlib,json,sys,types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent;SOURCE=R/'coupled-tail-escape'
p=R/'completed-gates-review/audit_gates.py';a=types.ModuleType('frozen_review_algebra');a.__file__=str(p)
exec(compile(p.read_bytes(),str(p),'exec',dont_inherit=True,optimize=0),a.__dict__)
ind=a.independent;ja,qc=a.ja,a.qc
def unary(e,m):
    clean={k:v for k,v in e.items()if k!='x_monomial'};op=ind.event_op(clean,m)
    family=ind.from_circuit(op,0);ex=e['extra_global_phase_exponent_by_f_mod4'];units=ind.UNITS
    family={k:tuple(c*units[ex[r]%4]for r,c in enumerate(v))for k,v in family.items()}
    symbolic=ind.old.serialized_family([dict(x_monomial=e['x_monomial'],coefficients_by_f_mod4=[['1','0']for _ in range(4)])])
    a.need(family==symbolic,'literal unary and symbolic source all-f phases agree')
    return family
def replay(E,n,m):
    M=ind.identity(n,m)
    for e in E:
        if e['kind']=='ADD':
            d,s=e['dst'],e['src'];M[d]=[ind.add(x,ind.scale(y,Fraction(e['coefficient'])))for x,y in zip(M[d],M[s])]
        elif e['kind']=='SCALE':M[e['bank']]=[ind.scale(x,Fraction(e['coefficient']))for x in M[e['bank']]]
        elif e['kind']=='BANK_SWAP':i,j=e['banks'];M[i],M[j]=M[j],M[i]
        else:
            U=unary(e,m);M[e['bank']]=[ind.product(U,x)for x in M[e['bank']]]
    return M
def family_entry(entry,m):
    op=ind.op_of(json.dumps(entry['one_coordinate_literal_circuit']),m);E=ind.from_circuit(op,0);ex=entry['extra_global_phase_exponent_by_f_mod4']
    return op,{k:tuple(c*ind.UNITS[ex[r]%4]for r,c in enumerate(v))for k,v in E.items()}
def check(f,admitted):
    q=f['q'];n,m=f['banks'],f['ambient_arity'];cut=f['cut_event_ordinal'];E=f['events'];Ei=f['inverse_events'];pool=f['native_recipe_pool'];cache={}
    source=next(x for x in admitted['fixtures']if x['q']==q)
    a.need(cut==({2:69,3:119}[q])and source['events'][cut]['label']=='final independent a J query','actual cut before final independent a query')
    a.need([{k:v for k,v in e.items()if k!='x_monomial'}for e in E]==source['events'][cut:],'entire local word exact admitted-source slice')
    a.need([{k:v for k,v in e.items()if k!='x_monomial'}for e in Ei]==source['inverse_events'][:len(E)],'entire serialized inverse exact source slice')
    used=set()
    for e in E+Ei:
        if e['kind']in('ADD','SCALE','BANK_SWAP'):continue
        clean={k:v for k,v in e.items()if k!='x_monomial'};ind.native_check(clean,pool,m,cache);unary(e,m)
        if e['kind']=='NATIVE':used.add(e['native_recipe_id'])
    a.need(used==set(pool),'native pool is used-only in forward/inverse')
    M,Mi=replay(E,n,m),replay(Ei,n,m)
    a.need(ind.mm(M,Mi)==ind.identity(n,m)==ind.mm(Mi,M),'both full arbitrary-current-input inverse orders')
    a.need(M==[[ind.old.serialized_family(x)for x in row]for row in f['complete_local_matrix']],'saved complete local matrix')
    a.need(Mi==[[ind.old.serialized_family(x)for x in row]for row in f['complete_local_inverse']],'saved complete local inverse')
    F=a.F(m,2*q+1);J=ja.j_operator(m);Q=J.inv()@a.P(m,1)@a.N(m,0).inv()@J@J;A=F@J@F.inv();W=F@Q.inv()@F.inv()
    reverse=[e for e in E if (e['label'].startswith('w reverse')and e['kind']not in('ADD','SCALE','BANK_SWAP'))or e['label']=='final extraction D_final inverse sign']
    RR=qc.identity(m)
    for e in reverse:RR=qc.decode(e,m)@RR
    expected=a.oldexpr(W@RR);a.need(M[1][3]==expected,'single exact input3/output1 WR coefficient all-f phase')
    entry=f['unavoidable_entry'];op,fam=family_entry(entry,m)
    a.need(fam==expected==ind.old.serialized_family(entry['operator']),'literal support witness and current-input coefficient coincide')
    rank=a.rank(x for x,z,p in op.tab[m:]);a.need(rank==2*q+2==entry['native_arity_per_f'],'actual coefficient native B-rank')
    recipe=entry.get('support_witness_selected_native_recipe',entry.get('support_witness_recipe'))
    lowered=ind.old.compile_recipe(recipe,m);a.need(recipe['rank']==rank and ind.equal_op(lowered,op),'support-only Bruhat recipe actual Gaussian phase')
    a.need(a.eq(W,a.N(m,1)@Q.inv()@a.N(m,1).inv()),'W support is confined to original planes0/1')
    if q==2:
        I=a.oldexpr(qc.identity(m));AA,WW,RRR=a.oldexpr(A),a.oldexpr(W),a.oldexpr(RR);IW=ind.add(I,ind.scale(WW,-1));target=[[{}for _ in range(n)]for _ in range(n)]
        target[0][0]=AA;target[1][0]=ind.scale(ind.product(WW,AA),-1);target[1][2]=IW;target[1][3]=expected;target[1][4]=IW
        target[2][0]=ind.scale(AA,-1);target[2][2]=I
        target[3][0]=ind.scale(ind.product(AA,ind.product(WW,AA)),-1);target[3][1]=AA;target[3][2]=ind.product(AA,IW);target[3][3]=ind.product(AA,ind.product(ind.scale(IW,-1),RRR));target[3][4]=ind.scale(ind.product(AA,WW),-1)
        target[4][4]=I;target[5][5]=I;a.need(M==target,'entire independent q2 six-row symbolic matrix')
        # Independently assemble the prose inverse from its y-coordinate
        # equations, rather than merely multiplying the saved inverse.
        e0=[I if j==0 else{}for j in range(n)];e1=[I if j==1 else{}for j in range(n)];e2=[I if j==2 else{}for j in range(n)];e3=[I if j==3 else{}for j in range(n)];e4=[I if j==4 else{}for j in range(n)];e5=[I if j==5 else{}for j in range(n)]
        x0=[ind.product(a.oldexpr(A.inv()),x)for x in e0];x2=[ind.add(x,y)for x,y in zip(e2,e0)];x4=e4
        z=[ind.add(ind.product(a.oldexpr(W.inv()),ind.add(ind.add(y,ind.scale(b,-1)),ind.scale(c,-1))),ind.add(ind.add(d,b),c))for y,b,c,d in zip(e1,x2,x4,e0)]
        x3=[ind.product(a.oldexpr(RR.inv()),x)for x in z]
        x1=[ind.add(ind.add(ind.product(a.oldexpr(A.inv()),d),zj),ind.add(ind.scale(y,-1),c))for d,zj,y,c in zip(e3,z,e1,x4)]
        a.need(Mi==[x0,x1,x2,x3,x4,e5],'explicit q2 inverse formulas every current column')
    hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE');local=sum(r*c for r,c in hist.items());prefix=sum(e['rank_per_f']for e in source['events'][:cut]if e['kind']=='NATIVE')
    prefix_hist=Counter(e['rank_per_f']for e in source['events'][:cut]if e['kind']=='NATIVE');a.need(prefix_hist=={2:{2:33,3:60}[q]},'actual fixed-prefix rank2 profile for moment bridge')
    a.need((prefix,local)==({2:(66,10),3:(120,12)}[q])and prefix==f['unchanged_prefix_native_mass']and local==f['local_native_mass'],'complete prefix and suffix invoice from actual native events')
    a.need(prefix+local==source['native_mass']and source['stock']-prefix==rank,'exact stock deficit threshold')
    # Controls operate on the actual local word, never a clean-state promise.
    bad=[e for e in E if e['label']!=('w reverse2 selected native2')];MB=replay(bad,n,m)
    a.need(MB!=M and MB[1][3]!=expected,'omitted actual reverse query changes required coefficient')
    a.need(len(MB[1][3])==1,'omitted-query control retains a single ray')
    key=next(iter(MB[1][3]));a.need(a.native(qc.Mono(key[0],key[1],key[2],key[3]))==2*q,'omitted-query spuriously drops support rank by2')
    modified=copy.deepcopy(E);u=next(e for e in modified if e['kind']=='NATIVE');u['extra_global_phase_exponent_by_f_mod4'][2]^=1
    try:replay(modified,n,m)
    except ValueError as ex:a.need('phases agree'in str(ex),'specific all-f phase mutation rejection')
    else:raise ValueError('f2-only phase mutation accepted')
    return dict(q=q,cut=cut,banks=n,all_current_columns=n,literal_inverse_orders=2,used_native_recipes=len(used),prefix_native_histogram=dict(prefix_hist),prefix_native_mass=prefix,local_histogram=dict(hist),local_native_mass=local,whole_native_mass=prefix+local,stock=source['stock'],single_entry_arity=rank,controls=['actual reverse-query omission rejected','f2-only native phase mutant rejected'],single_entry_row_support='2^('+str(rank)+'f) in every row; exact Bruhat factors are monomial/native/monomial')
def run():
    a.need(a.sha(SOURCE/'MANIFEST.json')=='f3c5b9829e61866988b0843e5bcb637fb0ae37434e2f8e6ef74bdeef079e126e','assigned frozen manifest')
    for x in json.loads((SOURCE/'MANIFEST.json').read_text())['files']:a.need(a.sha(SOURCE/x['path'])==x['sha256'],'frozen source file '+x['path'])
    admitted=json.loads((R/'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json').read_text());cases=[check(json.loads((SOURCE/p).read_text()),admitted)for p in('LOCAL-BLOCK.json','Q3-LOCAL-BLOCK.json')]
    grid=[]
    for q in range(2,11):
        m=4*q+4;k=2*q+1;F=a.F(m,k);J=ja.j_operator(m);Q=J.inv()@a.P(m,1)@a.N(m,0).inv()@J@J;W=F@Q.inv()@F.inv();Ns=qc.identity(m);Ps=qc.identity(m)
        for s in range(5,k+1,2):Ns=Ns@a.N(m,s);Ps=Ps@a.P(m,s)
        a.need(a.native(W)==4 and a.native(W@Ns@Ps)==2*q+2,'disjoint-support conditional tail arity')
        grid.append(dict(q=q,coefficient_rank=2*q+2))
    return dict(status='PASS_INDEPENDENT_COUPLED_TAIL_ENTRY_PHASE_INVOICE_AND_SUPPORT_REVIEW',cases=cases,conditional_tail_rank_grid=grid,no_new_kappa=True,scope='Exact q2/q3 current-input suffixes, all-f phases; conditional all-q tail pattern only. Support inequality charges every elementary binary ADD and same-volume full-bank native macro. No pointwise native-only floor or partial-volume claim.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=json.loads(json.dumps(run()));dest=HERE/'AUDIT.json'
    if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:a.need(json.loads(dest.read_text())==out,'saved independent audit')
    print(out['status']);print([(x['q'],x['prefix_native_mass'],x['local_native_mass'],x['single_entry_arity'])for x in out['cases']])
