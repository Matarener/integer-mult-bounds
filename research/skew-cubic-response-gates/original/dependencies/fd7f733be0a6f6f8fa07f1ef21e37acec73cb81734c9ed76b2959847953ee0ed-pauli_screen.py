#!/usr/bin/env python3
"""Pauli-response kernels and exact two-site isolated-bank composition.
Apache-2.0. Substantial OpenAI Codex assistance. No kappa admission.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent.parent
for pin in json.loads((HERE/'SOURCE-PINS.json').read_text())['read_only_sources']:
    if hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('source pin '+pin['path'])
sys.path.insert(0,str(R/'caller-joint'));sys.path.insert(0,str(R/'two-site-continuation'));sys.path.insert(0,str(R/'root-joint'))
from joint_algebra import *
from joint_prefix import check_literal_family
from lower_retimed_word import literal
from two_site import inverse,pullback,pair_columns,unitary_clifford
from native_model import b


def N(m,s):return n_pair(m,s)
def P(m,s):return plane_swap(m,0,s)
def J(m):return qc.Mono(qc.identity(m).rows,1,(0,)*m,(0,)*m,0,1)
def FF(m,k):
    out=qc.identity(m)
    for s in range(1,k+1):out=N(m,s)@out
    return out
def phase(m,p):return ce.Op(m,ce.identity(m),[('phase',p%4)])


def monomial_no_phase(op):
    n,T=op.n,op.tab;need(all(x==0 and p%2==0 for x,z,p in T[n:]),'physical monomial tableau')
    G=ce.transpose([x for x,z,p in T[:n]],n);bv=ce.mv(G,sum((p//2)<<i for i,(x,z,p)in enumerate(T[n:])))
    gt=ce.transpose(G,n);Q=ce.transpose([ce.mv(gt,z)for x,z,p in T[:n]],n);alpha=[(p-2*ce.parity(bv&z))%4 for x,z,p in T[:n]]
    out=ce.diag(n,Q,alpha).then(ce.perm(n,G)).then(ce.xgate(n,bv));need(out.tab==T,'actual monomial signed tableau')
    return out,{'matrix_rows':G,'offset':bv,'quadratic_rows':Q,'linear_Z4':alpha,'phase':0}


def lower_ray(op,align=False):
    n=op.n;B=[x for x,z,p in op.tab[n:]];r=ce.rank(B)
    if not r:
        compiled,rec=monomial_no_phase(op);result={'rank':0,'left':rec,'right':None}
    else:
        G=ce.transpose(ce.basis_extend(B,n),n);A=ce.inv(G,n);PA=ce.perm(n,A);part=op.then(PA)
        B=[x for x,z,p in part.tab[n:]];D=[z for x,z,p in part.tab[n:]];picks=[];selected=[]
        for j,x in enumerate(B):
            if ce.rank(selected+[x])>len(selected):picks.append(j);selected.append(x)
        Bi=ce.inv(ce.transpose(selected,r),r);Dr=ce.transpose([D[j]&((1<<r)-1)for j in picks],r)
        Qsmall=tuple(sum(ce.parity(row&col)<<j for j,col in enumerate(ce.transpose(Bi,r)))for row in Dr);DQ=ce.diag(n,Qsmall+(0,)*(n-r))
        V=part.then(DQ).then(ce.hadamard(n,range(r)));Vmon,_=monomial_no_phase(V)
        S=ce.diag(n,tuple(1<<i if i<r else 0 for i in range(n)))
        left=S.adjoint().then(DQ.adjoint()).then(PA.adjoint());right=Vmon.then(S.adjoint()).then(ce.xgate(n,(1<<r)-1))
        lmon,lrec=monomial_no_phase(left);rmon,rrec=monomial_no_phase(right)
        compiled=rmon.then(ce.fourier(n,range(r))).then(lmon);result={'rank':r,'left':lrec,'right':rrec}
    need(compiled.tab==op.tab,'tableau Bruhat lowering')
    if align:
        actual,ad=b.sparse_column(op);got,gd=b.sparse_column(compiled);need(set(actual)==set(got),'sparse Gaussian ray support')
        found=None
        for p in range(4):
            if all(b.gaussian_unit(v,p)[0]*(1<<ad)==actual[x][0]*(1<<gd)and b.gaussian_unit(v,p)[1]*(1<<ad)==actual[x][1]*(1<<gd)for x,v in got.items()):found=p;break
        need(found is not None,'exact sparse Gaussian unit alignment')
        result['left']['phase']=found;compiled=compiled.then(phase(n,found))
    return result,compiled


def compile_mon(rec,n):return ce.diag(n,rec['quadratic_rows'],rec['linear_Z4']).then(ce.perm(n,rec['matrix_rows'])).then(ce.xgate(n,rec['offset'])).then(phase(n,rec['phase']))


def build(f):
    q,n=f['q'],f['banks'];k=2*q+1;m=2*(k+1);jj=J(m);ff=FF(m,k);A=N(m,0).inv()@jj;B={s:P(m,s)@A for s in range(1,k+1)}
    Q=jj.inv()@B[1]@jj;Du=qc.identity(m)
    for r in range(2,q+1):Du=B[2*r]@Du
    Du=Du@B[3]@jj
    maps={'tail-Du-recovery':ff@Du.inv()@ff.inv(),'tail-Q1-recovery':ff@Q.inv()@ff.inv(),'tail-J':ff@jj@ff.inv()}
    def convert(e):
        if e['kind']in('ADD','BANK_SWAP','SCALE'):return{k:e[k]for k in e if k in('kind','dst','src','coefficient','banks','bank','label')}
        fam=e.get('native_family');label=e['label'];g=None
        if fam and fam['kind']=='N':g=N(m,fam['plane'])
        elif fam and fam['kind']=='J':
            fs=FF(m,fam['completed']);g=fs@jj@fs.inv()
            if fam.get('inverse'):g=g.inv()
        elif label=='fusion stage2 uniform fresh on former source':g=N(m,2)
        elif e.get('native_recipe_id')in maps:g=maps[e['native_recipe_id']]
        elif label.startswith('query')and label.endswith('source swap'):g=P(m,int(label.split()[0][5:]))
        elif label.startswith('w reverse')and label.endswith('ADDRESS'):g=P(m,2*int(label.split()[1][7:])+1)
        elif label in('fusion replace shared initial J by minus identity','final extraction D_final inverse sign'):
            g=qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
        need(g is not None,'covered Pauli-response actual operator '+label)
        r=qc.rank(g.polar());op=literal(g)
        need(ce.rank(x for x,z,p in op.tab[m:])==r,'actual Pauli-response Clifford B rank')
        return {'kind':'NATIVE'if r else'ADDRESS_OR_UNIT','bank':e['bank'],'label':label,'x_monomial':g.data(),'rank_per_f':r,
                'one_coordinate_literal_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab],
                'phase_exponent':g.global_phase,'extra_global_phase_exponent_by_f_mod4':[(g.global_phase*(1-h))%4 for h in range(4)]}
    PP=[convert(e)for e in f['prefix_events']];TT=[convert(e)for e in f['tail_events']];E=PP+TT;M=qc.replay(E,n,m);Mi=qc.replay(inverse(E,m),n,m);out=mono(ff@jj)
    need(M==[[out if i==j else{}for j in range(n)]for i in range(n)],'Pauli-response complete actual FJ every independent original column')
    need(mm(M,Mi)==mm(Mi,M)==eye(n,m),'Pauli-response complete literal inverse both orders')
    hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE');mass=sum(r*c for r,c in hist.items());parent=qc.rank((ff@jj).polar())
    return{'q':q,'banks':n,'ambient_arity':m,'parent_arity':parent,'prefix_events':PP,'tail_events':TT,'events':E,'histogram':dict(hist),
           'mass':mass,'optimistic_stock':n*parent,'all_original_columns':n,'inverse_orders':2,'Du_rank':qc.rank(maps['tail-Du-recovery'].polar()),'Q_rank':qc.rank(maps['tail-Q1-recovery'].polar())}


def isolate(f):
    q,n,m=f['q'],f['banks'],f['ambient_arity'];PP,TT=f['prefix_events'],f['tail_events']
    i=next(i for i,e in enumerate(PP)if e['label']=='query3 source swap')
    j=next(i for i,e in enumerate(PP)if e['label']==f'query{2*q} source swap')
    removed={i for i,e in enumerate(TT)if e['label']=='joint U coordinate recovery'};newT=[e for i,e in enumerate(TT)if i not in removed]
    C=mm(qc.replay(inverse(newT,m),n,m),qc.replay(TT,n,m))
    for at in range(len(PP)-1,j,-1):C=pullback(C,PP[at],m)
    Acol,Brow=pair_columns(PP,i,j,n,m);bank=PP[j]['bank'];I=eye(n,m)
    need(not any(Acol[r]for r in range(n)if r!=bank)and not any(Brow[c]for c in range(n)if c!=bank),'Pauli-response transported row and column both isolated')
    need(all(C[r][c]==I[r][c]for r in range(n)for c in range(n)if(r,c)!=(bank,bank)),'Pauli-response tail defect is only current isolated bank')
    need(unitary_clifford(Acol[bank])and unitary_clifford(C[bank][bank]),'actual unitary isolated families')
    L=product(C[bank][bank],product(Acol[bank],mono(qc.decode(PP[i],m))));RR=product(adjoint(Acol[bank]),mono(qc.decode(PP[j],m)))
    def coordinate(value):
        g,v=next(iter(value.items()));units=((1,0),(0,1),(-1,0),(0,-1));p=units.index((v[2],v[3]));return literal(g).then(phase(m,p))
    Lop,Rop=coordinate(L),coordinate(RR);lr,_=lower_ray(Lop);rr,_=lower_ray(Rop)
    U=mul(compile_mon(rr['left'],m),compile_mon(lr['right'],m));V=mul(Lop,U.adjoint(),Rop);rank=ce.rank(x for x,z,p in V.tab[m:])
    need(ce.rank(x for x,z,p in U.tab[m:])==0 and rank==abs(lr['rank']-rr['rank']),'actual Pauli-response physical monomial and rank-distance fusion')
    # Full all-input identity: the transported first edit is F(U Gi^-1)F^-1.
    # With V=L U^-1 R, its product with the later edit is exactly C.
    # Each n-by-n block outside the isolated bank has already been checked.
    def extras(value):
        v=next(iter(value.values()));units=((1,0),(0,1),(-1,0),(0,-1));ps=[units.index((v[2*h],v[2*h+1]))for h in range(4)]
        return[(ps[h]-h*ps[1])%4 for h in range(4)]
    exL,exR=extras(L),extras(RR);vp=[(a+b)%4 for a,b in zip(exL,exR)]
    old_first=literal(qc.decode(PP[i],m));need(U.tab!=old_first.tab,'omitting first changed physical monomial has a nonidentity actual defect')
    iC={g:rotate(v,0,1)for g,v in C[bank][bank].items()};need(iC!=C[bank][bank],'wrong whole-field Gaussian phase changes required correction')
    newE=[]
    for at,e in enumerate(PP+newT):
        if at in(i,j):
            op=U if at==i else V;r=0 if at==i else rank
            newE.append({'kind':'NATIVE'if r else'ADDRESS_OR_UNIT','bank':e['bank'],'label':'Pauli-response two-site replacement of '+e['label'],
                         'rank_per_f':r,'one_coordinate_literal_circuit':op.circuit,'one_coordinate_tableau':[list(t)for t in op.tab],
                         'extra_global_phase_exponent_by_f_mod4':[0]*4 if at==i else vp})
        else:newE.append(e)
    hist=Counter(e['rank_per_f']for e in newE if e['kind']=='NATIVE');mass=sum(r*c for r,c in hist.items())
    reverse=[]
    for e in reversed(newE):
        e=dict(e)
        if e['kind']=='ADD':e['coefficient']=str(-F(e['coefficient']))
        elif e['kind']=='SCALE':e['coefficient']=str(1/F(e['coefficient']))
        elif e['kind']!='BANK_SWAP':
            op=ce.Op(m,tuple(tuple(t)for t in e['one_coordinate_tableau']),e['one_coordinate_literal_circuit']).adjoint()
            e['one_coordinate_literal_circuit']=op.circuit;e['one_coordinate_tableau']=[list(t)for t in op.tab]
            e['extra_global_phase_exponent_by_f_mod4']=[(-p)%4 for p in e['extra_global_phase_exponent_by_f_mod4']]
            if 'phase_exponent'in e:e['phase_exponent']=-e['phase_exponent']
            e.pop('x_monomial',None)
            need(ce.rank(x for x,z,p in op.tab[m:])==e['rank_per_f'],'every serialized actual inverse native rank')
        reverse.append(e)
    out={'q':q,'banks':n,'ambient_arity':m,'parent_arity':f['parent_arity'],'optimistic_stock':f['optimistic_stock'],'default_mass':f['mass'],
         'sites':[i,j],'site_labels':[PP[i]['label'],PP[j]['label']],'removed_tail_labels':[TT[x]['label']for x in removed],
         'L_rank':lr['rank'],'R_rank':rr['rank'],'new_site_ranks':[0,rank],'histogram':dict(hist),'mass':mass,'D_optimistic':f['optimistic_stock']-mass,
         'events':newE,'inverse_events':reverse,'first_monomial':{'literal_circuit':U.circuit,'tableau':U.tab},'L':serial(L),'R':serial(RR),'later_extra_phase_by_f_mod4':vp,
         'isolated_forward_column_entry':serial(Acol[bank]),'isolated_inverse_row_entry':serial(Brow[bank]),'required_current_correction':serial(C[bank][bank]),
         'all_original_columns':n,'isolation_contract':'both transported column and inverse row have only one current bank; all other n-by-n defect blocks identity',
         'exact_word_identity':'V=C F Gi U^-1 F^-1 Gj = L U^-1 R; every original-column coefficient follows from verified full isolated-bank matrix equation',
         'all_f_scope':'all positive f via explicit tensor powers and Gaussian-unit vectors; no finite-f extrapolation',
         'inverse_scope':'literal complete changed word reversed gate-by-gate, all unitary circuits adjointed and all f-residue phases negated; both inverse orders follow exactly',
         'negative_controls':['Unchanged original first source post has a different signed tableau and cannot satisfy the unique isolated-bank equation.',
                              'Multiplying the later f-family by an extra global i changes its nonzero required correction.'],
         'selected_new_native_lowering':False,'no_new_kappa':True}
    if mass<f['optimistic_stock']:
        recipes={}
        for inv in(False,True):
            op=V.adjoint()if inv else V;rec,compiled=lower_ray(op,align=True)
            need(rec['rank']==rank,'actual selected new child arity')
            recipes['Pauli-response-later'+('inv'if inv else'')]={'selected_native_recipe':rec,'definition_circuit':op.circuit,'definition_tableau':op.tab}
        out['new_native_recipe_pool']=recipes;out['selected_new_native_lowering']=True
    return out


def main():
    source=HERE/'inputs/SOURCE-SIMPLIFIED.json';data=json.loads(source.read_text());results=[];isolation=[]
    suffix=''if __debug__ else'-OPTIMIZED'
    for f in data['fixtures']:
        x=build(f);results.append(x);(HERE/('DEFAULT'+suffix+'.json')).write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fixtures':results,'no_new_kappa':True},indent=2,sort_keys=True)+'\n')
        print('PAULI_RESPONSE_DEFAULT',x['q'],x['mass'],'stock',x['optimistic_stock'],flush=True)
        y=isolate(x);isolation.append(y);(HERE/('ISOLATED'+suffix+'.json')).write_text(json.dumps({'fixtures':isolation,'no_new_kappa':True},indent=2,sort_keys=True)+'\n')
        print('PAULI_RESPONSE_ISOLATED',y['q'],y['mass'],'stock',y['optimistic_stock'],'ranks',y['L_rank'],y['R_rank'],y['new_site_ranks'],flush=True)


if __name__=='__main__':main()
