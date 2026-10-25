#!/usr/bin/env python3
"""Independent literal circuit and metadata audit of the folded fusions.
Apache-2.0; substantial OpenAI Codex assistance. No caller algebra import.
"""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
from collections import Counter
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FUSION=HERE.parent/'folded-fusion'
sys.path.insert(0,str(HERE.parent/'joint-native'))
from joint_coefficient_gate import Model,kernels,mul,phase,b,ce,need,PIN,left_gamma,f
from literal_inverse_binding import from_circuit,circuit_op,product,sumexpr,scale,serial,act,qval
from lifted_algebra import G


@lru_cache(None)
def definition(circuit,n):
    return circuit_op(json.loads(circuit),n)


def event_op(e,n):
    op=definition(json.dumps(e['one_coordinate_literal_circuit']),n)
    need(op.tab==tuple(tuple(t)for t in e['one_coordinate_tableau']),'recompiled event signed tableau')
    need(b.native_rank(op)==e['rank_per_f'],'event actual rank differs from metadata')
    record={'x_monomial':e['x_monomial'],'coefficients_by_f_mod4':[['1','0']for _ in range(4)]}
    need(serialized_family([record])==from_circuit(op,e['phase_exponent']),
         'event X-character metadata matches independent literal all-f phase')
    return op


@lru_cache(None)
def family(circuit,n,exponent):
    return from_circuit(definition(circuit,n),exponent)


def replay(E,n,m):
    I=from_circuit(ce.ident(m),0)
    M=[[dict(I)if i==j else{}for j in range(n)]for i in range(n)]
    for e in E:
        typ=e['kind']
        if typ=='ADD':
            d,s=e['dst'],e['src'];M[d]=[sumexpr(x,scale(y,Fraction(e['coefficient'])))for x,y in zip(M[d],M[s])]
        elif typ=='SCALE':M[e['bank']]=[scale(x,Fraction(e['coefficient']))for x in M[e['bank']]]
        elif typ=='BANK_SWAP':
            i,j=e['banks'];M[i],M[j]=M[j],M[i]
        else:
            event_op(e,m)
            U=family(json.dumps(e['one_coordinate_literal_circuit']),m,e['phase_exponent'])
            M[e['bank']]=[product(U,x)for x in M[e['bank']]]
    return M


def compile_monomial(rec,n):
    return circuit_op([('D',rec['quadratic_rows'],rec['linear_Z4']),('P',rec['matrix_rows']),
                       ('X',rec['offset']),('phase',rec['phase'])],n)


def compile_recipe(rec,n):
    L=compile_monomial(rec['left'],n)
    return L if not rec['rank'] else compile_monomial(rec['right'],n).then(ce.fourier(n,range(rec['rank']))).then(L)


def embedding(circuit,index,n):
    d=len(index);need(len(set(index))==d and all(0<=x<n for x in index),'native embedding injective')
    def bits(x):return sum(((x>>i)&1)<<index[i]for i in range(d))
    out=[]
    for e in circuit:
        if e[0]=='P':
            rows=[1<<i for i in range(n)]
            for i,j in enumerate(index):rows[j]=bits(e[1][i])
            out.append(('P',rows))
        elif e[0]=='D':
            rows=[0]*n;alpha=[0]*n
            for i,j in enumerate(index):rows[j]=bits(e[1][i]);alpha[j]=e[2][i]
            out.append(('D',rows,alpha))
        elif e[0]in('C','X'):out.append((e[0],bits(e[1]),*e[2:]))
        else:need(e[0]=='phase','covered embedded primitive');out.append(e)
    return out


def exact_recipe_phase(compiled,actual):
    """One matrix element fixes the Gaussian ray after signed-tableau equality.

    The selected recipe has only rank-many C gates, so its physical zero
    column is sparse. The definition's matrix element is computed by an
    exact Walsh sum of its independently derived X-character phase.
    """
    need(compiled.tab==actual.tab,'selected recipe tableau')
    sparse,depth=b.sparse_column(compiled)
    row=min(sparse);numerator=G(*sparse[row])
    expr=from_circuit(actual,0);need(len(expr)==1,'native definition is X-character monomial')
    (key,coeff),=expr.items();s=[0,0,0,0]
    for w in range(1<<actual.n):s[(qval(key,w)+2*((act(key,w)&row).bit_count()&1))%4]+=1
    total=G(Fraction(s[0]-s[2]),Fraction(s[1]-s[3]))*coeff[1]
    need(total*G(Fraction(1<<depth))==numerator*G(Fraction(1<<actual.n)),
         'selected recipe actual Gaussian phase, not just tableau')


def check_recipes(fixture):
    m=fixture['ambient_arity'];pool=fixture['native_recipe_pool'];done={};links=0
    used={e['native_recipe_id']for e in fixture['events']+fixture['inverse_events']if e['kind']=='NATIVE'}
    audited=used|{key for key in pool if key.startswith('fusion')}
    for key in sorted(audited):
        need(key in pool,'every forward/inverse native recipe pointer exists')
        p=pool[key];n=len(p['one_coordinate_tableau'])//2
        actual=definition(json.dumps(p['one_coordinate_definition_circuit']),n)
        need(actual.tab==tuple(tuple(t)for t in p['one_coordinate_tableau']),'pool definition tableau')
        need('selected_native_recipe'in p,'selected native lowering exists')
        compiled=compile_recipe(p['selected_native_recipe'],n)
        exact_recipe_phase(compiled,actual)
        need(b.native_rank(actual)==p['selected_native_recipe']['rank'],'pool native arity')
        done[key]=(p,actual)
    for e in fixture['events']+fixture['inverse_events']:
        if e['kind']!='NATIVE':continue
        p,op=done[e['native_recipe_id']]
        need(e['phase_exponent']==p['phase_exponent'],'event/pool all-f tensor unit')
        need(len(e['recipe_embedding'])==op.n,'recipe embedding matches pool dimension')
        embedded=embedding(op.circuit,e['recipe_embedding'],m)
        actual=event_op(e,m)
        need(from_circuit(circuit_op(embedded,m),e['phase_exponent'])==from_circuit(actual,e['phase_exponent']),
             'embedded selected native definition equals event, including phase')
        links+=1
    return {'used_pool_entries':len(used),'audited_pool_entries':len(audited),'forward_inverse_recipe_links':links,
            'new_recipe_keys':[x for x in sorted(audited)if x.startswith('fusion')]}


def required(q):
    z=Model(1,2*q+1);_,J=kernels(z);A=mul(z.N.adjoint(),J)
    Q=mul(J.adjoint(),z.P[0],A,J);Dv=z.I
    for r in range(2,q+1):Dv=mul(z.P[2*r],z.N,Dv)
    Dv=mul(phase(z.n,2*(q-2)),Dv);F=z.prefix(2*q+1)
    C=mul(F,Q.adjoint(),Dv.adjoint(),F.adjoint())
    return z,J,F,C


def inverse_owner_row(P,n,m,original=1):
    I=from_circuit(ce.ident(m),0);row=[{}for _ in range(n)];row[original]=I
    for e in P:
        if e['kind']=='ADD':row[e['src']]=sumexpr(row[e['src']],scale(row[e['dst']],-Fraction(e['coefficient'])))
        elif e['kind']=='SCALE':row[e['bank']]=scale(row[e['bank']],1/Fraction(e['coefficient']))
        elif e['kind']=='BANK_SWAP':
            i,j=e['banks'];row[i],row[j]=row[j],row[i]
        else:
            op=event_op(e,m)
            row[e['bank']]=product(row[e['bank']],from_circuit(op.adjoint(),-e['phase_exponent']))
    return row


def serialized_family(records):
    U=(G(Fraction(1)),G(Fraction(0),Fraction(1)),G(Fraction(-1)),G(Fraction(0),Fraction(-1)))
    out={}
    for record in records:
        x=record['x_monomial'];key=(tuple(x['rows']),x['offset'],tuple(x['alpha']),tuple(x['quad']))
        v=tuple(G(Fraction(a),Fraction(b))*U[(x.get('global_phase',0)+r*x.get('constant',0))%4]
                for r,(a,b)in enumerate(record['coefficients_by_f_mod4']))
        out=sumexpr(out,{key:v})
    return out


def formal_rewrites():
    I,Z,J,Ji=f.I,f.Z,f.N,f.inv(f.N)
    M0=[[I,Z],[J,I]];M1=[[J,Z],[f.neg(I),I]]
    need(M1==f.mm(M0,[[J,Z],[Z,I]]),'all-parameter J^2 preload matrix identity')
    Q,Du,Dv=f.mono((1,)),f.mono((2,)),f.mono((3,))
    Qi,Ui,Vi=f.inv(Q),f.inv(Du),f.inv(Dv)
    H=[[f.prod(Du,f.add(Q,f.neg(I)),J),Du],[f.prod(Dv,Q,J),Z]]
    Hi=[[Z,f.prod(Ji,Qi,Vi)],[Ui,f.prod(f.add(Qi,f.neg(I)),Vi)]]
    need(f.mm(H,Hi)==f.mm(Hi,H)==f.eye(2),'changed homogeneous endpoint inverse in both orders')
    corrected=[[f.mul(J,x)for x in row]for row in Hi]
    need(corrected[0]==[Z,f.prod(Qi,Vi)],'new t inverse coefficient omits old J')
    # Every affine/public term is retained as an independent free word.
    n,p=6,4;L=[[f.mono((20+4*i+j,))for j in range(p)]for i in range(2)]
    M=f.eye(n)
    for i in range(p):M[i][i]=J
    for i in range(2):M[p+i]=L[i]+H[i]
    W=f.eye(n)
    for i in range(2):
        for j in range(p):W[p+i][j]=f.neg(f.prod(J,f.summ(f.mul(Hi[i][r],L[r][j])for r in range(2)),Ji))
        for j in range(2):W[p+i][p+j]=corrected[i][j]
    need(f.mm(W,M)==[[J if i==j else Z for j in range(n)]for i in range(n)],
         'unfactored joint inverse with all independent original owner/public columns')
    U=f.mono((7,));uniform=[[U if i==j else Z for j in range(n)]for i in range(n)]
    star=f.eye(n)
    for i in(3,5):star[i][1]=f.neg(I)
    need(f.mm(star,uniform)==f.mm(uniform,star),'uniform source/fresh operator commutes scalar star')
    return {'preload_identity':'M1=M0 diag(J,I), using J^2=-I',
            'generic_original_columns':n,'independent_public_couplings':8,
            'changed_t_inverse_coefficient':'Q1^-1 Dv^-1 in retarded target gauge',
            'full_homogeneous_inverse_both_orders':'PASS',
            'uniform_stage_star_commutation':'PASS'}


def check_fixture(name,f):
    q,n,m=f['q'],f['banks'],f['ambient_arity'];z,J,F,C=required(q)
    target=from_circuit(mul(F,J),2*q+2)
    T=[[target if i==j else{}for j in range(n)]for i in range(n)]
    A=replay(f['events'],n,m);need(A==T,'every original input reaches its actual FJ output')
    inv=replay(f['inverse_events'],n,m)
    Ti=from_circuit(mul(F,J).adjoint(),-2*q-2)
    need(inv==[[Ti if i==j else{}for j in range(n)]for i in range(n)],
         'serialized literal inverse restores every input; both orders follow')
    need(f['events']==f['prefix_events']+f['tail_events']==f['full_events'],'current event partitions')
    hist=dict(Counter(e['rank_per_f']for e in f['events']if e['kind']=='NATIVE'))
    phist=dict(Counter(e['rank_per_f']for e in f['prefix_events']if e['kind']=='NATIVE'))
    need(hist=={int(r):v for r,v in f['histogram'].items()},'current complete histogram')
    mass=sum(r*v for r,v in hist.items());margin=n*m-sum(r*v for r,v in phist.items())
    need(mass==n*m+8==f['native_mass'],'complete native charge')
    row=inverse_owner_row(f['prefix_events'],n,m)
    tv=product(target,row[3]);tu=product(target,row[1]);expected=from_circuit(C,5-3*q)
    need(tv==expected and not tu,'current original-t inverse coefficient and phase')
    need(b.native_rank(C)==2*q+2,'new inverse coefficient native arity')
    metadata=[]
    if f.get('prefix_D')!=margin:metadata.append({'field':'prefix_D','stored':f.get('prefix_D'),'actual':margin})
    if f.get('prefix_histogram')!={str(r):v for r,v in phist.items()}:metadata.append({'field':'prefix_histogram','stored':f.get('prefix_histogram'),'actual':phist})
    if f.get('original_t_current_V_arity_per_f')!=2*q+2:metadata.append({'field':'original_t_current_V_arity_per_f','stored':f.get('original_t_current_V_arity_per_f'),'actual':2*q+2})
    if serialized_family(f.get('original_t_current_V_correction',[]))!=tv:metadata.append({'field':'original_t_current_V_correction','reason':'serialized operator differs from independent current inverse'})
    inherited=['physical_prefix_matrix','physical_prefix_inverse','retarded_H','retarded_L','core_Knew','P2tilde','original_t_current_V_correction','reader_identity']
    # These fields are inherited byte-for-byte from the old folded fixture,
    # hence cannot be current after P2tilde=I and the right J preload.
    old=json.loads((FUSION/'inputs/DUAL-CORE.json').read_text())
    source=next(x for x in old['fixtures']if x['q']==q and x['name']=='folded-dual')
    for field in inherited:
        if f.get(field)==source.get(field):metadata.append({'field':field,'reason':'unchanged old-source field after changed core/input preload; not current evidence'})
    if 'current_original_owner_inverse_coefficients'in f:
        owner3=inverse_owner_row(f['prefix_events'],n,m,3)
        for i,rw in((1,row),(3,owner3)):
            for j in(1,3):
                need(serialized_family(f['current_original_owner_inverse_coefficients'][str(i)][str(j)])==product(target,rw[j]),
                     'fresh serialized original-owner inverse coefficient')
        need(f['D']==n*m-mass and f['prefix_native_mass']==n*m-margin,'fresh mass fields')
        need(f['tail_native_mass']==sum(e['rank_per_f']for e in f['tail_events']if e['kind']=='NATIVE'),'fresh tail bill')
    negative=[]
    for label in('fusion replace shared initial J by minus identity','fusion stage2 uniform fresh on former source'):
        at=next(i for i,e in enumerate(f['events'])if e.get('label')==label)
        wrong=f['events'][:at]+f['events'][at+1:]
        need(replay(wrong,n,m)!=T,'actual changed-event omission negative control')
        negative.append(label)
    return {'artifact':name,'q':q,'all_original_columns':n,'all_positive_f':'literal circuits and exact tensor phase vectors',
            'forward_endpoint_and_serialized_inverse':'PASS','actual_histogram':hist,'actual_mass':mass,'stock':n*m,
            'actual_prefix_histogram':phist,'actual_prefix_margin':margin,'current_tV_arity_per_f':2*q+2,
            'current_tV':serial(tv),'recipe_validation':check_recipes(f),'negative_controls':negative,
            'stale_metadata_rejected':metadata,'metadata_admission':'REJECT_INHERITED_FIELDS_UNTIL_REGENERATED'if metadata else'PASS_REGENERATED_CURRENT_METADATA'}


def run():
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())['source_pins']
    for x in pins:need(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'],'audit source pin '+x['path'])
    manifest=json.loads((FUSION/'MANIFEST.json').read_text())
    for x in manifest['files']:need(hashlib.sha256((FUSION/x['path']).read_bytes()).hexdigest()==x['sha256'],'contribution manifest '+x['path'])
    input_pins=json.loads((FUSION/'INPUT-PINS.json').read_text())
    for x in input_pins['files']:
        need(hashlib.sha256(Path(x['frozen_copy']).read_bytes()).hexdigest()==x['sha256'],'copied immutable input '+x['frozen_copy'])
    for x in input_pins['imported_dependency_pins']:
        need(hashlib.sha256(Path(x['source']).read_bytes()).hexdigest()==x['sha256'],'predecessor import '+x['source'])
    cases=[]
    for name in('SIMPLIFIED-FUSIONS.json','THREE-FUSIONS.json'):
        cases.extend(check_fixture(name,x)for x in json.loads((FUSION/name).read_text())['fixtures'])
    ranks=[]
    for q in range(2,17):
        z,J,F,C=required(q);g=left_gamma(C)
        expected=[0]*z.n
        for h in(0,1):
            expected[h]=(1<<h)|(1<<(2+h));expected[2+h]=1<<h
            for s in range(5,2*q+2,2):expected[2*s+h]=1<<(2*s+h)
        need(g==tuple(expected)and b.native_rank(C)==2*q+2,'all-q fixed core-plus-odd-diagonal formula')
        A=mul(z.N.adjoint(),J);Q=mul(J.adjoint(),z.P[0],A,J)
        Du=mul(z.P[2],z.N)
        for r in range(2,q+1):Du=mul(z.P[2*r-1],A,Du)
        Urec=mul(F,Du.adjoint(),F.adjoint());Qrec=mul(F,Q.adjoint(),F.adjoint())
        Jrec=mul(F,J,F.adjoint());fused=mul(Urec,z.T[-1])
        need([b.native_rank(op)for op in(Urec,Qrec,Jrec,fused)]==[6,4,2,8],
             'native tail widths and optional disjoint fresh fusion for every checked q')
        ranks.append({'q':q,'arity_per_f':2*q+2,'default_prefix_margin':2*q+2,
                      'U_recovery':6,'Q1_recovery':4,'J_recovery':2,'U_fresh_fusion':8,
                      'optional_prefix_margin':2*q-4})
    return {'status':'PASS_LITERAL_FUSION_WORDS_WITH_STALE_METADATA_REJECTED'if any(x['stale_metadata_rejected']for x in cases)else'PASS_LITERAL_FUSION_WORDS_AND_CURRENT_METADATA',
            'scientific_pin':PIN,'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins':pins,'cases':cases,'all_q_coefficient_checks':ranks,
            'formal_all_parameter_rewrites':formal_rewrites(),
            'scope':'Independent actual event/phase/recipe/operator audit at q2/q3. Written all-q local identities and conditional source interface are assessed separately. Stale inherited fields are explicitly rejected, not repaired in the contribution.',
            'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run()));file=HERE/'AUDIT.json'
    if a.write:file.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(file.read_text())==out,'saved independent audit differs')
    print(out['status'])
