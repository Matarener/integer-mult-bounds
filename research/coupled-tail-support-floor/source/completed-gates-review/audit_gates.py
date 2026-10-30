#!/usr/bin/env python3
"""Independent identity, invoice and strand audit of two completed gates.
Apache-2.0; substantial OpenAI Codex assistance. No new supplier claim.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import hashlib, importlib.machinery, json, sys, argparse, copy
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; R=HERE.parent
EXECUTED={};original=importlib.machinery.SourceFileLoader.get_code
def source_only(self, name):
    p=Path(self.path)
    if str(p).startswith('/Users/ross/git/math/'):
        raw=p.read_bytes();EXECUTED[str(p)]=hashlib.sha256(raw).hexdigest()
        return compile(raw,str(p),'exec',dont_inherit=True,optimize=0)
    return original(self,name)
importlib.machinery.SourceFileLoader.get_code=source_only
sys.path.insert(0,str(R/'two-site-independent-audit'))
import audit_two_sites as independent
sys.path.insert(0,str(R/'caller-joint'))
import joint_algebra as ja
ce,qc=independent.ce,ja.qc
K=R/'general-clifford-retiming/kernel-search'; T=R/'pauli-caller-retiming'
def need(c,s):
    if not c:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stable(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def rank(vs):
    basis={}
    for v in vs:
        while v:
            bit=v.bit_length()-1
            if bit in basis:v^=basis[bit]
            else:basis[bit]=v;break
    return len(basis)
def eq(a,b):return ja.mono(a)==ja.mono(b)
def native(g):return rank(g.polar())
def scalar(m,p):return qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,p)
def N(m,s):
    a=[0]*m;a[2*s]=3;a[2*s+1]=1
    return qc.Mono(qc.identity(m).rows,3<<(2*s),tuple(a),(0,)*m,0,1)
def P(m,s):
    rows=list(qc.identity(m).rows)
    for d in (0,1):rows[d],rows[2*s+d]=rows[2*s+d],rows[d]
    return qc.Mono(tuple(rows),0,(0,)*m,(0,)*m)
def F(m,s):
    x=qc.identity(m)
    for i in range(1,s+1):x=N(m,i)@x
    return x
def embed(d,m):return qc.Mono(tuple(d['rows'])+tuple(1<<i for i in range(4,m)),d['offset'],tuple(d['alpha'])+(0,)*(m-4),tuple(d['quad'])+(0,)*(m-4),d['constant'],d['global_phase'])
def oldexpr(g):return independent.old.serialized_family(ja.serial(ja.mono(g)))
def kernel_checks():
    manifest=json.loads((K/'MANIFEST.json').read_text())
    for p in manifest['files']:need(sha(K/p['path'])==p['sha256'],'kernel frozen manifest '+p['path'])
    raw=(K/'EXACT-FIXTURES.json').read_bytes();need(raw==(K/'EXACT-FIXTURES-OPTIMIZED.json').read_bytes(),'kernel normal/-O bytes')
    data=json.loads(raw);cases={x['kernel']:x['J_four_axes'] for x in data['fixtures']};rows=[];bindings=[]
    for name,d in cases.items():
        for q in range(2,9):
            k=2*q+1;m=4*q+4;J=embed(d,m);bar=N(m,1)@J@N(m,1).inv()
            B={s:P(m,s)@N(m,0).inv()@J for s in range(1,k+1)}
            Q=J.inv()@B[1]@J
            need(eq(J@J,scalar(m,2)),'all-f skew square')
            need(eq(Q,J@P(m,1)@N(m,0).inv()),'Q simplified with whole-field sign')
            need(eq((N(m,1)@Q.inv()@N(m,1).inv())@(N(m,1)@J),N(m,1)@N(m,0)@P(m,1)),'Q-target exact product')
            transport=P(m,4)@bar;chain=B[4]
            for r in range(3,q+1):
                transport=P(m,2*r)@bar@N(m,2*r-1)@transport
                chain=B[2*r]@B[2*r-1]@chain
            # The displayed ellipsis in the source proof means EVEN indices.
            chain=qc.identity(m)
            for s in range(4,2*q+1,2):chain=B[s]@chain
            need(eq(F(m,2*q).inv()@transport,chain@F(m,3).inv()),'transport exact telescope')
            Du=chain@B[3]@J;C=F(m,2*q)@Du.inv()@F(m,2*q).inv()
            L=C@transport@P(m,3);RR=transport.inv()@P(m,2*q)
            closed=scalar(m,2)
            for s in range(3,2*q+1):closed=N(m,s)@closed
            need(eq(L,closed),'closed L all-f sign and phase')
            a,b,v,w=native(J),native(bar),native(N(m,1)@J),native(N(m,1)@Q.inv()@N(m,1).inv())
            rho=native(RR);ell=native(L)
            need(ell==4*q-4 and rho<=(q-1)*b+2*(q-2),'L transport rank and R upper bound')
            need(w+v>=4 and v<=4 and a>=max(v-2,0) and b>=max(v-2,0),'coupled rank restrictions')
            mass=8*q*q+10*q+2+2*a+3*q*b+w+abs(ell-rho);stock=(2*q+2)*(4*q+v)
            upper=(2*q+3)*v-(4*q+6)-2*a-(2*q+1)*b
            need(stock-mass<=upper<=0,'all-q inequality at exact finite witness')
            rows.append(dict(kernel=name,q=q,a=a,b=b,v=v,w=w,rho=rho,ell=ell,mass=mass,stock=stock,deficit=stock-mass))
            if q<=3:
                case=next(x for x in data['fixtures'] if x['kernel']==name and x['default']['q']==q)
                df,cf=case['default'],case['isolated'];E=df['events'];n=df['banks']
                col,row=independent.transported(df['prefix_events'],*cf['sites'],n,m)
                bank=df['prefix_events'][cf['sites'][1]]['bank']
                need(all(not x for i,x in enumerate(col) if i!=bank) and all(not x for i,x in enumerate(row) if i!=bank),'independent complete forward-column/inverse-row isolation')
                need(col[bank]==oldexpr(transport),'independent all-f actual transported column')
                need(row[bank]==oldexpr(transport.inv()),'independent all-f actual transported inverse row')
                hist=Counter(e['rank_per_f'] for e in cf['events'] if e['kind']=='NATIVE')
                need(sum(r*c for r,c in hist.items())==mass==cf['mass'],'independent retained histogram invoice')
                for e in E:
                    if e['kind'] not in ('ADD','SCALE','BANK_SWAP'):independent.old.event_op(e,m)
                M=independent.replay_old(E,n,m);Mi=independent.replay_old(E,n,m,inverse=True)
                target=oldexpr(F(m,k)@J);need(M==[[target if i==j else{}for j in range(n)]for i in range(n)],'independent full default target every original column all-f')
                need(independent.mm(M,Mi)==independent.identity(n,m)==independent.mm(Mi,M),'independent default literal inverse both orders')
                need(oldexpr(L)==independent.old.serialized_family(cf['L']),'saved L full tensor phase')
                need(oldexpr(RR)==independent.old.serialized_family(cf['R']),'saved R full tensor phase')
                Lop,Lex=independent.to_op(oldexpr(L));Rop,Rex=independent.to_op(oldexpr(RR))
                U=independent.op_of(json.dumps(cf['first_monomial']['literal_circuit']),m);ue=cf['events'][cf['sites'][0]];ve=cf['events'][cf['sites'][1]]
                need(independent.equal_op(U,independent.op_of(json.dumps(ue['one_coordinate_literal_circuit']),m)) and ue['extra_global_phase_exponent_by_f_mod4']==[0]*4,'first actual event equals declared physical monomial family')
                V=independent.op_of(json.dumps(ve['one_coordinate_literal_circuit']),m)
                need(rank(x for x,z,p in U.tab[m:])==0,'first replacement physical monomial')
                need(independent.equal_op(V,independent.mul(Lop,U.adjoint(),Rop)),'independent local V=L U^-1 R Gaussian phase')
                need(ve['extra_global_phase_exponent_by_f_mod4']==[(a+b)%4 for a,b in zip(Lex,Rex)],'local replacement all-f tensor phase')
                need(len(cf['events'])==len(cf['inverse_events']),'complete changed inverse event coverage')
                for ef,ei in zip(cf['events'],reversed(cf['inverse_events'])):
                    need(ef['kind']==ei['kind'],'changed inverse event kind/order')
                    if ef['kind']=='ADD':need((ef['dst'],ef['src'])==(ei['dst'],ei['src']) and Fraction(ef['coefficient'])==-Fraction(ei['coefficient']),'changed inverse ADD sign')
                    elif ef['kind']=='SCALE':need(ef['bank']==ei['bank'] and Fraction(ef['coefficient'])*Fraction(ei['coefficient'])==1,'changed inverse SCALE')
                    elif ef['kind']=='BANK_SWAP':need(ef['banks']==ei['banks'],'changed inverse bank swap')
                    else:
                        of=independent.op_of(json.dumps(ef['one_coordinate_literal_circuit']),m);oi=independent.op_of(json.dumps(ei['one_coordinate_literal_circuit']),m)
                        need(stable(of.adjoint().circuit)==stable(oi.circuit) and of.adjoint().tab==oi.tab,'changed literal inverse unary actual adjoint')
                        need(ei['extra_global_phase_exponent_by_f_mod4']==[(-p)%4 for p in ef['extra_global_phase_exponent_by_f_mod4']],'changed inverse tensor phase sign')
                bindings.append(dict(kernel=name,q=q,actual_original_columns=n,default_full_target_all_f=True,literal_inverse_orders=2,isolated_bank=bank,L_rank=ell,R_rank=rho,mass=mass,stock=stock))
    # Formula controls are sensitive to all-f phase and completed-frame conjugacy.
    need(not eq(L,scalar(m,1)@L),'wrong whole-field phase rejected')
    addr=embed(cases['address_swap_rankzero_J'],12)
    need(native(addr)==0 and native(N(12,1)@addr@N(12,1).inv())==4,'completed J bill cannot use uncompleted arity')
    need(native(embed(cases['odd_rankone_involution'],12))==1,'odd native skew response retained')
    return dict(finite_rank_identity_grid=rows,actual_q2_q3_transport_bindings=bindings,controls=['wrong whole-field phase differs','completed address kernel rank changes 0 to 4','odd native rank one retained'],all_q_scope='Written proof conditional on displayed repeating scalar/isolation transport and fixed two-site edits; no all-q serialized physical compiler or selected-new-native admission.')
def phase_family(op,extra):
    out=independent.from_circuit(op,0)
    units=independent.UNITS
    return {k:tuple(c*units[extra[r]%4] for r,c in enumerate(v))for k,v in out.items()}
def trajectory_checks(cert=None):
    if cert is None:cert=json.loads((T/'TRAJECTORY-CERTIFICATES.json').read_text())
    results=[]
    for f in cert['fixtures']:
        m,n=f['ambient_arity'],f['banks'];src=json.loads((T/f['source']['path']).read_text())
        need(sha(T/f['source']['path'])==f['source']['sha256'],'trajectory source pin')
        sf=next(x for x in src['fixtures'] if x['q']==f['q']);events=sf.get('full_events',sf['events'])
        labels=list(range(n));ops=[ce.ident(m) for _ in range(n)];phase=[(0,)*4 for _ in range(n)]
        for e in events:
            if e['kind']=='BANK_SWAP':
                i,j=e['banks'];labels[i],labels[j]=labels[j],labels[i];ops[i],ops[j]=ops[j],ops[i];phase[i],phase[j]=phase[j],phase[i]
            elif e['kind'] not in ('ADD','SCALE'):
                op=independent.op_of(json.dumps(e['one_coordinate_literal_circuit']),m);b=e['bank'];ops[b]=ops[b].then(op)
                extra=e.get('extra_global_phase_exponent_by_f_mod4',[(e.get('phase_exponent',0)*(1-r))%4 for r in range(4)])
                phase[b]=tuple((a+c)%4 for a,c in zip(phase[b],extra))
        edges=f['edges'];used=[];unaries=[];bound=0
        for path in f['trajectories']:
            at=0;op=ce.ident(m);extra=(0,)*4
            for eid in path['edges']:
                used.append(eid);ed=edges[eid];need(ed['id']==eid and ed['u']==at,'trajectory edge incidence');at=ed['v']
                seg=independent.op_of(json.dumps(ed['one_coordinate_literal_circuit']),m);op=op.then(seg)
                need(seg.tab==tuple(tuple(t)for t in ed['one_coordinate_tableau']),'edge actual signed operator')
                extra=tuple((a+b)%4 for a,b in zip(extra,ed['extra_global_phase_exponent_by_f_mod4']))
                unaries.extend(ed['source_event_ordinals'])
            need(at==0,'path endpoint Z boundary')
            bank=labels.index(path['initial_bank']);need(bank==path['final_bank'],'physical strand transport includes swaps')
            need(op.tab==ops[bank].tab and stable(op.circuit)==stable(ops[bank].circuit) and extra==phase[bank],
                 'independent exact all-f literal holonomy circuit and tensor phase traversal')
            r=rank(x for x,z,p in op.tab[m:]);need(r==path['native_holonomy_arity_per_f'],'independent holonomy native rank')
            Z=tuple(1<<(m+i) for i in range(m));GZ=tuple(x|(z<<m) for x,z,p in op.tab[m:])
            need(rank(Z+GZ)-m==r,'independent Lagrangian distance')
            bound+=r
        need(sorted(used)==list(range(len(edges))),'edge-disjoint exhaustive path partition')
        need(sorted(unaries)==[i for i,e in enumerate(events) if e['kind'] not in ('ADD','SCALE','BANK_SWAP')],'every actual unary assigned to one edge')
        mass=sum(e['rank_per_f'] for e in events if e['kind']=='NATIVE')
        need(bound==f['trajectory_floor_per_f'] and bound<=mass==f['original_native_mass'],'trajectory floor and invoice')
        if f['family'].startswith('PAULI'):need(bound==mass==f['stock'],'sharp Pauli finite bound')
        results.append(dict(family=f['family'],q=f['q'],floor=bound,mass=mass,stock=f['stock'],edges=len(edges),paths=n))
    return results
def controls():
    cert=json.loads((T/'TRAJECTORY-CERTIFICATES.json').read_text());rejected=[]
    try:ce.diag(2,(2,0),(0,0))
    except AssertionError:rejected.append(dict(control='legacy checker live under -O',error='nonsymmetric Clifford phase rejected'))
    else:raise ValueError('retained legacy source assertions disabled')
    bad=copy.deepcopy(cert);bad['fixtures'][0]['trajectories'][0]['edges'].pop(0)
    for name,value in [('omitted trajectory edge',bad)]:
        try:trajectory_checks(value)
        except ValueError as e:rejected.append(dict(control=name,error=str(e)))
        else:raise ValueError('negative control accepted: '+name)
    bad=copy.deepcopy(cert);bad['fixtures'][0]['edges'][0]['extra_global_phase_exponent_by_f_mod4'][2]^=1
    try:trajectory_checks(bad)
    except ValueError as e:rejected.append(dict(control='f2-only wrong holonomy phase',error=str(e)))
    else:raise ValueError('negative control accepted: wrong holonomy tensor phase')
    return rejected
def cubic_checks():
    CUB=R/'general-clifford-retiming/order-three-response'
    manifest=json.loads((CUB/'MANIFEST.json').read_text())
    for x in manifest['files']:need(sha(CUB/x['path'])==x['sha256'],'cubic manifest pin '+x['path'])
    raw=(CUB/'CUBIC.json').read_bytes();need(raw==(CUB/'CUBIC-OPTIMIZED.json').read_bytes(),'cubic normal/-O bytes')
    data=json.loads(raw);zero=(Fraction(0),Fraction(0));one=(Fraction(1),Fraction(0))
    def add(a,b):return a[0]+b[0],a[1]+b[1]
    def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
    def sumg(xs):
        v=zero
        for x in xs:v=add(v,x)
        return v
    def mm(a,b):return [[sumg(mul(a[i][k],b[k][j])for k in range(len(a)))for j in range(len(a))]for i in range(len(a))]
    def eye(n):return [[one if i==j else zero for j in range(n)]for i in range(n)]
    def tensor(a,b):return [[mul(a[i][j],b[k][l])for j in range(len(a))for l in range(len(b))]for i in range(len(a))for k in range(len(b))]
    def matrix(op):
        cols=[]
        for j in range(1<<op.n):
            col,d=op.zero_state(j);cols.append([(Fraction(a,1<<d),Fraction(b,1<<d))for a,b in col])
        return [list(x)for x in zip(*cols)]
    J=[[tuple(Fraction(x)for x in z)for z in row]for row in data['base_matrix']]
    need(sumg(J[i][i]for i in range(2))==(Fraction(-1),Fraction(0)),'cubic base trace')
    need(mm(mm(J,J),J)==eye(2),'cubic base order')
    current=[[one]];rows=[]
    for f in data['fixtures']:
        size=f['f'];current=tensor(current,J)
        op=independent.op_of(json.dumps(f['literal_circuit']),size);need(matrix(op)==current,'independent every-entry cubic tensor circuit')
        need(op.tab==tuple(tuple(t)for t in f['signed_tableau']),'cubic signed tableau')
        need(rank(x for x,z,p in op.tab[size:])==size==f['native_B_rank'],'cubic actual native arity')
        dim=1<<size;A2=mm(current,current);need(mm(A2,current)==eye(dim),'independent tensor cubic order')
        residual=[[sumg((current[i][j],A2[i][j],one if i==j else zero))for j in range(dim)]for i in range(dim)]
        need(all(v==zero for row in residual for v in row)==(size==1),'quadratic fails beyond tensor base')
        if size==2:
            need(sumg(residual[i][i]for i in range(dim))==(Fraction(6),Fraction(0)),'f2 nonzero quadratic trace control')
            wrong=[[mul(v,(Fraction(0),Fraction(-1)))for v in row]for row in current]
            need(mm(mm(wrong,wrong),wrong)!=eye(dim),'wrong single global phase fails actual cubic family')
        rows.append(dict(f=size,native_rank=size,quadratic=(size==1)))
    # Independent rational scalar SWAP matrix and omitted-sign control.
    X=[[Fraction(i==j)for j in range(2)]for i in range(2)]
    for d,s,c in ((0,1,1),(1,0,-1),(0,1,1)):X[d]=[a+c*b for a,b in zip(X[d],X[s])]
    need(X==[[0,1],[-1,0]],'three ADD signed swap');X[1]=[-a for a in X[1]]
    need(X==[[0,1],[1,0]],'sign-complete all-input scalar SWAP')
    return dict(exact_cubic_fixtures=rows,written_trace_gate_review='Q(i) trace forces equal primitive multiplicities; nonzero Pauli fixed-character sum then rank(S-I)=2 and B-rank<=2.',scalar_swap_all_input_matrix=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    out=dict(status='PASS_INDEPENDENT_COMPLETED_GATES_REVIEW',kernel=kernel_checks(),trajectory=trajectory_checks(),negative_controls=controls(),cubic=cubic_checks(),executed_source_hashes=independent.EXECUTED,no_new_kappa=True)
    out=json.loads(json.dumps(out));dest=HERE/'AUDIT.json'
    if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(dest.read_text())==out,'saved independent audit differs')
    print(out['status']);print('kernel actual cases',len(out['kernel']['actual_q2_q3_transport_bindings']),'rank grid',len(out['kernel']['finite_rank_identity_grid']),'trajectory cases',len(out['trajectory']))
if __name__=='__main__':main()
