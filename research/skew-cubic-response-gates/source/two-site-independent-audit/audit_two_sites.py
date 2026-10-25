#!/usr/bin/env python3
"""Independent transport/gluing and literal recipe audit, q2/q3, all f.
Apache-2.0; substantial OpenAI Codex assistance. No source generator import.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
from functools import lru_cache
import argparse,hashlib,json,sys,importlib.machinery,py_compile,types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;SOURCE=ROOT/'two-site-continuation'

# Execute the exact source bytes read and hashed, including explicit legacy
# SourceFileLoader imports. Ignore bytecode caches and keep legacy assertions
# active even when this independent parent is run with -O.
EXECUTED={};original_get_code=importlib.machinery.SourceFileLoader.get_code
def source_only(self,fullname):
    path=Path(self.path)
    if str(path).startswith('/Users/ross/git/math/'):
        raw=path.read_bytes();EXECUTED[str(path)]=hashlib.sha256(raw).hexdigest()
        return compile(raw,str(path),'exec',dont_inherit=True,optimize=0)
    return original_get_code(self,fullname)
importlib.machinery.SourceFileLoader.get_code=source_only
sys.path.insert(0,str(ROOT/'fusion-audit'))
import audit_fusions as old
ce,b,mul,need=old.ce,old.b,old.mul,old.need
product,add,scale,from_circuit=old.product,old.sumexpr,old.scale,old.from_circuit
from literal_inverse_binding import serial
from lifted_algebra import G
UNITS=(G(Fraction(1)),G(Fraction(0),Fraction(1)),G(Fraction(-1)),G(Fraction(0),Fraction(-1)))


def loader_controls():
    probe=HERE/'_bytecode_probe.py';cache=Path(importlib.util.cache_from_source(str(probe)))
    need(not probe.exists()and not cache.exists(),'loader control owns fresh scratch paths')
    try:
        probe.write_text('raise RuntimeError("poisoned cached source")\n')
        py_compile.compile(str(probe),cfile=str(cache),doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
        probe.write_text('VALUE="exact source bytes"\ndef check():\n    assert False, "legacy checker remains active"\n')
        loader=importlib.machinery.SourceFileLoader('audit_bytecode_probe',str(probe))
        module=types.ModuleType('audit_bytecode_probe');module.__file__=str(probe);loader.exec_module(module)
        need(module.VALUE=='exact source bytes','poisoned unchecked-hash bytecode ignored')
        try:module.check()
        except AssertionError:pass
        else:raise ValueError('workspace legacy assertions disabled under parent optimization')
        try:ce.diag(2,(2,0),(0,0))
        except AssertionError:pass
        else:raise ValueError('retained exact Clifford source assertion disabled')
    finally:
        probe.unlink(missing_ok=True);cache.unlink(missing_ok=True);EXECUTED.pop(str(probe),None)
        try:cache.parent.rmdir()
        except OSError:pass
    return ['unchecked-hash poisoned bytecode bypassed','workspace source assertions active','retained Clifford assertion active']


@lru_cache(None)
def op_of(circuit,n):return old.circuit_op(json.loads(circuit),n)
def event_op(e,m):
    op=op_of(json.dumps(e['one_coordinate_literal_circuit']),m)
    need(op.tab==tuple(tuple(x)for x in e['one_coordinate_tableau']),'literal event tableau')
    need(b.native_rank(op)==e['rank_per_f'],'literal event native rank')
    need(len(e['extra_global_phase_exponent_by_f_mod4'])==4,'four exact tensor phase residues')
    need(not any(k in e for k in('x_monomial','native_family','phase_exponent')),'no stale operator shadows')
    return op
def xsafe(op):return all(e[0]!='D'or(not any(e[1])and all(x%2==0 for x in e[2]))for e in op.circuit)
@lru_cache(None)
def sparse(circuit,n):return b.sparse_column(op_of(circuit,n))
def equal_op(a,c):
    if a.tab!=c.tab:return False
    if xsafe(a)and xsafe(c):return from_circuit(a,0)==from_circuit(c,0)
    return sparse(json.dumps(a.circuit),a.n)==sparse(json.dumps(c.circuit),c.n)
def old_unary(e,m,inverse=False):
    op=old.event_op(e,m);return from_circuit(op.adjoint()if inverse else op,-e['phase_exponent']if inverse else e['phase_exponent'])
def identity(n,m):
    I=from_circuit(ce.ident(m),0);return[[dict(I)if i==j else{}for j in range(n)]for i in range(n)]
def mm(A,B):return[[sumexpr(product(A[i][k],B[k][j])for k in range(len(A))if A[i][k]and B[k][j])for j in range(len(A))]for i in range(len(A))]
def sumexpr(items):
    out={}
    for x in items:out=add(out,x)
    return out
def replay_old(E,n,m,inverse=False):
    M=identity(n,m)
    for e in reversed(E)if inverse else E:
        typ=e['kind']
        if typ=='ADD':
            d,s=e['dst'],e['src'];c=Fraction(e['coefficient'])*(-1 if inverse else 1)
            M[d]=[add(x,scale(y,c))for x,y in zip(M[d],M[s])]
        elif typ=='SCALE':
            c=Fraction(e['coefficient']);c=1/c if inverse else c
            M[e['bank']]=[scale(x,c)for x in M[e['bank']]]
        elif typ=='BANK_SWAP':i,j=e['banks'];M[i],M[j]=M[j],M[i]
        else:
            U=old_unary(e,m,inverse);M[e['bank']]=[product(U,x)for x in M[e['bank']]]
    return M
def pullback(C,e,m):
    C=[[dict(x)for x in row]for row in C];typ=e['kind']
    if typ=='ADD':
        d,s=e['dst'],e['src'];c=Fraction(e['coefficient'])
        C[d]=[add(x,scale(y,-c))for x,y in zip(C[d],C[s])]
        for row in C:row[s]=add(row[s],scale(row[d],c))
    elif typ=='BANK_SWAP':
        i,j=e['banks'];C[i],C[j]=C[j],C[i]
        for row in C:row[i],row[j]=row[j],row[i]
    elif typ=='SCALE':
        j=e['bank'];c=Fraction(e['coefficient']);C[j]=[scale(x,1/c)for x in C[j]]
        for row in C:row[j]=scale(row[j],c)
    else:
        j=e['bank'];U,Ui=old_unary(e,m),old_unary(e,m,True)
        C[j]=[product(Ui,x)for x in C[j]]
        for row in C:row[j]=product(row[j],U)
    return C
def transported(P,i,j,n,m):
    I=from_circuit(ce.ident(m),0);bank=P[i]['bank']
    col=[dict(I)if x==bank else{}for x in range(n)];row=[dict(x)for x in col]
    for e in P[i+1:j+1]:
        typ=e['kind']
        if typ=='ADD':
            d,s=e['dst'],e['src'];c=Fraction(e['coefficient'])
            col[d]=add(col[d],scale(col[s],c));row[s]=add(row[s],scale(row[d],-c))
        elif typ=='BANK_SWAP':a,c=e['banks'];col[a],col[c]=col[c],col[a];row[a],row[c]=row[c],row[a]
        elif typ=='SCALE':
            x=e['bank'];c=Fraction(e['coefficient']);col[x]=scale(col[x],c);row[x]=scale(row[x],1/c)
        else:
            x=e['bank'];col[x]=product(old_unary(e,m),col[x]);row[x]=product(row[x],old_unary(e,m,True))
    need(sumexpr(product(x,y)for x,y in zip(row,col))==I,'transported row times column equals I')
    return col,row
def to_op(E):
    need(len(E)==1,'one exact old Clifford ray');(key,v),=E.items();n=len(key[0]);out=ce.ident(n)
    for i,a in enumerate(key[2]):
        if a in(1,3):out=out.then(ce.cgate(n,1<<i,1 if a==1 else-1))
        elif a==2:out=out.then(ce.xgate(n,1<<i))
    for i,row in enumerate(key[3]):
        for j in range(i+1,n):
            if row>>j&1:out=out.then(ce.cgate(n,1<<i)).then(ce.cgate(n,1<<j)).then(ce.cgate(n,(1<<i)|(1<<j),-1))
    inv=ce.inv(key[0],n);out=out.then(ce.perm(n,ce.transpose(inv,n)))
    if key[1]:out=out.then(ce.diag(n,[0]*n,[2*((key[1]>>i)&1)for i in range(n)]))
    units=[UNITS.index(x)for x in v];out=out.then(old.phase(n,units[1]))
    need(from_circuit(out,0)=={key:tuple(UNITS[(units[1]*r)%4]for r in range(4))},'independent X-character-to-physical circuit direction/phase')
    return out,[(units[r]-r*units[1])%4 for r in range(4)]


def native_check(e,pool,m,cache):
    op=event_op(e,m)
    if e['kind']!='NATIVE':need(b.native_rank(op)==0,'first emitted free operator is physical monomial');return
    key=e['native_recipe_id'];need(key in pool,'native pointer exists');p=pool[key]
    need(e['extra_global_phase_exponent_by_f_mod4']==p['extra_global_phase_exponent_by_f_mod4'],'native pool phase-vector direction')
    if key not in cache:
        n=len(p['one_coordinate_tableau'])//2;actual=op_of(json.dumps(p['one_coordinate_definition_circuit']),n)
        need(actual.tab==tuple(tuple(x)for x in p['one_coordinate_tableau']),'pool definition tableau')
        compiled=old.compile_recipe(p['selected_native_recipe'],n)
        need(equal_op(compiled,actual),'selected recipe actual Gaussian ray')
        need(b.native_rank(actual)==p['selected_native_recipe']['rank'],'selected recipe rank')
        cache[key]=actual
    need(len(e['recipe_embedding'])==cache[key].n,'recipe embedding dimension')
    embedded=old.circuit_op(old.embedding(cache[key].circuit,e['recipe_embedding'],m),m)
    need(equal_op(embedded,op),'actual event equals selected recipe embedding including phase')
    cap=int(((m*m-1)//2)**0.5)
    need(e['rank_per_f']<=cap and e['rank_per_f']<m,'proper native child cap')


def check(q,current,source,science):
    n,m=current['banks'],current['ambient_arity'];P,T=source['prefix_events'],source['tail_events'];i,j=current['changed_sites']
    removed=set(science['removed_tail_sites']);newT=[e for at,e in enumerate(T)if at not in removed]
    C=mm(replay_old(newT,n,m,True),replay_old(T,n,m))
    for e in reversed(P[j+1:]):C=pullback(C,e,m)
    A,B=transported(P,i,j,n,m);bank=P[j]['bank'];I=identity(n,m)
    need(all(not x for r,x in enumerate(A)if r!=bank)and all(not x for r,x in enumerate(B)if r!=bank),'actual two-sided bank isolation')
    need(all(C[r][c]==I[r][c]for r in range(n)for c in range(n)if(r,c)!=(bank,bank)),'actual tail-deletion correction only one bank')
    need(product(A[bank],B[bank])==I[0][0],'isolated transport inverse orientation')
    L=product(C[bank][bank],product(A[bank],old_unary(P[i],m)))
    R=product(B[bank],old_unary(P[j],m));Lop,lp=to_op(L);Rop,rp=to_op(R)
    E=current['events'];U,W=event_op(E[i],m),event_op(E[j],m)
    need(E==current['full_events']==current['prefix_events']+current['tail_events'],
         'admitted current prefix/tail/full partitions are literal, not inherited shadows')
    need(len(current['prefix_events'])==len(P),'changed prefix keeps current site indices')
    up,wp=E[i]['extra_global_phase_exponent_by_f_mod4'],E[j]['extra_global_phase_exponent_by_f_mod4']
    need(equal_op(mul(Lop,U.adjoint(),Rop),W),'literal W=L U^-1 R exact Gaussian operator')
    need(wp==[(a-c+d)%4 for a,c,d in zip(lp,up,rp)],'W=L U^-1 R all f-mod4 Gaussian units')
    gaugeU=[(x+1)%4 for x in up];gaugeW=[(x-1)%4 for x in wp]
    need(gaugeW==[(a-c+d)%4 for a,c,d in zip(lp,gaugeU,rp)],'equivalent opposite whole-field Gaussian phase gauge accepted')
    ranks=[b.native_rank(x)for x in(Lop,Rop,U,W)]
    need(ranks==([4,2,0,2]if q==2 else[8,6,0,2]),'actual Bruhat rank-distance attainment')
    # No hidden event changes: every unchanged field/operator is bound to
    # the independently verified repaired source. Tail removal is explicit.
    oldE=P+newT;need(len(E)==len(oldE),'only named tail queries removed')
    for at,(a,c)in enumerate(zip(E,oldE)):
        if at in(i,j):continue
        need(a['kind']==c['kind'],'unchanged event kind')
        if a['kind']in('ADD','SCALE','BANK_SWAP'):
            for key in('bank','banks','dst','src','coefficient'):
                if key in c:need(a.get(key)==c[key],'unchanged scalar/bank event')
        else:
            op=event_op(a,m);need(from_circuit(op,0)==from_circuit(old.event_op(c,m),0),'unchanged physical event phase')
            need(a['extra_global_phase_exponent_by_f_mod4']==[(c['phase_exponent']*(1-r))%4 for r in range(4)],'unchanged all-f event unit')
    z,J,F,unused=old.required(q);target=from_circuit(mul(F,J),2*q+2)
    need(replay_old(P+T,n,m)==[[target if r==c else{}for c in range(n)]for r in range(n)],'independent old source all original output columns')
    cache={};pool=current['native_recipe_pool'];inv=current['inverse_events'];need(len(inv)==len(E),'serialized inverse covers every event')
    for e in E+inv:
        if e['kind']not in('ADD','SCALE','BANK_SWAP'):native_check(e,pool,m,cache)
    for a,c in zip(reversed(E),inv):
        need(a['kind']==c['kind'],'literal inverse primitive kind')
        typ=a['kind']
        if typ=='ADD':need(a['dst']==c['dst']and a['src']==c['src']and Fraction(c['coefficient'])==-Fraction(a['coefficient']),'inverse ADD')
        elif typ=='SCALE':need(a['bank']==c['bank']and Fraction(a['coefficient'])*Fraction(c['coefficient'])==1,'inverse SCALE')
        elif typ=='BANK_SWAP':need(a['banks']==c['banks'],'inverse SWAP')
        else:
            need(a['bank']==c['bank']and equal_op(event_op(a,m).adjoint(),event_op(c,m)),'serialized exact literal unary adjoint')
            need(c['extra_global_phase_exponent_by_f_mod4']==[(-x)%4 for x in a['extra_global_phase_exponent_by_f_mod4']],'inverse all-f unit')
    used={e['native_recipe_id']for e in E+inv if e['kind']=='NATIVE'};need(used==set(pool)==set(cache),'used-only complete forward/inverse pool')
    hist=dict(Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE'));mass=sum(k*v for k,v in hist.items())
    need(hist=={2:n*n,4:1}and mass==n*m+4==current['native_mass'],'actual full native histogram')
    need(hist=={int(k):v for k,v in current['histogram'].items()}and current['stock']==n*m
         and current['D']==n*m-mass,'admitted inventory metadata matches current literal events')
    need(current['changed_native_ranks']==[0,2]and current['all_original_columns']==n
         and current['used_only_native_definitions']==len(pool),'admitted domain/recipe counters')
    need(current['every_serialized_unary_checked']==sum(e['kind']not in('ADD','SCALE','BANK_SWAP')for e in E+inv),
         'serialized forward/inverse unary counter')
    negative=[]
    bad=dict(next(e for e in inv if e['kind']=='NATIVE'));k=bad['native_recipe_id'];bad['native_recipe_id']=k[:-3]if k.endswith('inv')else k+'inv'
    try:native_check(bad,pool,m,{})
    except ValueError as error:
        need(str(error)in('native pool phase-vector direction','actual event equals selected recipe embedding including phase'),
             'wrong-direction pointer fails its intended phase/operator check')
        negative.append('opposite-direction inverse native pointer')
    else:raise ValueError('wrong native pointer unexpectedly accepted')
    changed=list(wp);changed[2]=(changed[2]+2)%4
    need(changed[1]==wp[1]and changed!=[(a-c+d)%4 for a,c,d in zip(lp,up,rp)],'f2-only scalar mutation changes required local operator family')
    negative.append('f2-only phase mutant with f1 unchanged')
    need(not equal_op(mul(Lop,Rop),W),'omitting first physical monomial cannot satisfy unique local correction')
    negative.append('omitted first free monomial rejects arbitrary-input correction')
    return {'q':q,'all_original_columns':n,'all_positive_f':'exact source transport, general Clifford local identity and four scalar residues',
            'complete_endpoint':'diag(F_k J)','both_literal_inverse_orders':'PASS_by_complete_primitive_inverse_and_forward_gluing',
            'L_R_U_W_ranks_per_f':ranks,'histogram':hist,'native_mass':mass,'stock':n*m,
            'source_transport_row_and_column':'isolated','all_used_forward_inverse_recipes':len(pool),'native_event_links':sum(e['kind']=='NATIVE'for e in E+inv),
            'negative_controls':negative,'phase_vectors':{'L':lp,'R':rp,'U':up,'W':wp},
            'equivalent_positive_control':'opposite whole-field i/-i gauges on U/W preserve the exact local identity',
            'proof_method':'Independent old X-character bank matrix transport and source all-column replay; emitted general Clifford U/W and selected recipes checked in physical coordinates, no author generator or general tensor algebra imported.'}


def run():
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())['source_pins']
    for x in pins:need(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'],'source pin '+x['path'])
    need(hashlib.sha256((SOURCE/'MANIFEST.json').read_bytes()).hexdigest()=='44f1e264b3087ab8fdb08b4cd6e27befefbba380852b0119321724b7bc41b5da','frozen assigned manifest')
    for x in json.loads((SOURCE/'MANIFEST.json').read_text())['files']:need(hashlib.sha256((SOURCE/x['path']).read_bytes()).hexdigest()==x['sha256'],'manifest file '+x['path'])
    raw=json.loads((SOURCE/'ADMITTED-TWO-SITE-FUSIONS.json').read_text());sources=json.loads((SOURCE/'inputs/REPAIRED-SIMPLIFIED-FUSIONS.json').read_text())
    cases=[]
    for f in raw['fixtures']:
        q=f['q'];s=next(x for x in sources['fixtures']if x['q']==q);science=json.loads((SOURCE/f'ISOLATED-FUSION-Q{q}.json').read_text())
        cases.append(check(q,f,s,science))
    controls=loader_controls()
    return {'status':'PASS_INDEPENDENT_TWO_SITE_TRANSPORT_LITERAL_PHASE_AND_NATIVE_ADMISSION','scientific_pin':old.PIN,
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_pins':pins,'cases':cases,
            'exact_source_execution':EXECUTED,'source_loader':'Workspace Python modules executed from the exact bytes hashed in memory, ignoring bytecode caches; historical workspace assertions explicitly active under parent -O.',
            'source_loader_controls':controls,
            'no_all_q_construction':True,'no_new_kappa':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run()));file=HERE/'AUDIT.json'
    if a.write:file.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(file.read_text())==out,'saved independent two-site audit differs')
    print(out['status'])
