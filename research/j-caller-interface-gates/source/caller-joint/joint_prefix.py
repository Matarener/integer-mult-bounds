#!/usr/bin/env python3
"""Literal all-q phase-correct J prefix with diagonal pivot continuation.
Apache-2.0; substantial OpenAI Codex assistance. No cleanup saving claimed.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse,hashlib,json
from joint_algebra import *
HERE=Path(__file__).resolve().parent

def build(q,omit_raw_a_restore=False,continue_wrong_carrier=False):
 need(q>=2,'at least two public pairs')
 n,k,m=2*q+2,2*q+1,4*q+4
 W=Word(n,m);N=n_pair(m,0);J=j_operator(m);stage=0
 def query(bank,s,inverse=False,label=''):
  f=prefix(m,s);g=f@J@f.inv()
  if inverse:g=g.inv()
  need(qc.rank(g.polar())==2,'source J query has native rank2 per coordinate')
  W.unary(bank,g,label,True,{'kind':'J','completed':s,'inverse':inverse})
 def source_swap(bank,s,label):W.unary(bank,plane_swap(m,0,s),label)
 def progress(src,s,dst=None):
  for bank in range(n):
   if bank!=src:W.unary(bank,n_pair(m,s),f'query{s} target fresh'if bank==dst else f'query{s} idle fresh',True,{'kind':'N','plane':s,'inverse':False})
 for r in range(2,q+1):W.add(2*r+1,3,1,'raw c basis')
 query(1,0,label='shared initial J exposure');W.add(2,1,1,'shared initial J fanout');query(1,0,True,'shared initial J inverse')
 _,ops=skeleton(q,[1]+[0]*(q-1))
 for typ,d,s,z in ops:
  if typ=='a':
   if z[1]:need(stage==0 and d==2 and s==1 and z[1]==1,'only initial J-valued bridge is shared')
   else:W.add(d,s,z[0],'initial nested scalar bridge')
  elif typ=='s':W.swap(d,s,'initial nested permutation')
  else:
   stage+=1;u=retraction(q,stage)
   if stage==4:
    for bank,(aa,bb)in enumerate(u):
     if bank!=s:W.add(bank,s,-aa,'query4 scalar entrance')
    break
   for bank,(aa,bb)in enumerate(u):
    if bank!=s:W.add(bank,s,-aa,f'query{stage} scalar entrance')
   query(s,stage-1,label=f'query{stage} source J')
   for bank,(aa,bb)in enumerate(u):
    if bank!=s:W.add(bank,s,-bb,f'query{stage} source pre-delivery fanout')
   W.add(d,s,1,f'query{stage} delivery')
   source_swap(s,stage,f'query{stage} source swap');progress(s,stage,d)
   if stage==3:
    for bank,(aa,bb)in enumerate(u):
     if bank!=s:W.add(bank,s,-bb,'query3 source pre-continuation fanout')
    query(s,stage,label='query3 retained source continuation')
   for bank,(aa,bb)in enumerate(u):
    if bank!=s:W.add(bank,s,aa,f'query{stage} scalar exit')
 if not omit_raw_a_restore:
  for r in range(3,q+1):W.add(0,2*r,-1,'restore independent raw a')
 W.add(3,0,-1,'held source subtract raw a')
 for r in range(2,q+1):W.add(3,2*r,-1,'held source subtract future raw b')
 for r in range(2,q+1):
  e,o,b,c=2*r,2*r+1,2*r,2*r+1
  query(1,e-1,label=f'query{e} source J');W.add(1,3,-1,'even isolate c difference');W.swap(1,3,'even source handoff')
  source_swap(1,e,f'query{e} source swap');progress(1,e,3);W.swap(3,c,'move completed c difference')
  query(b,o-1,label=f'query{o} source J')
  for ell in range(r+1,q+1):W.add(2*ell+1,b,1,'odd future-c first fanout')
  W.add(3,b,1,'odd delivery');W.swap(b,3,'odd source handoff')
  W.add(2,b,-1,'odd b accumulator')
  for ell in range(r+1,q+1):W.add(2*ell+1,b,-1,'odd future-c second fanout')
  source_swap(b,o,f'query{o} source swap');progress(b,o,3)
  if r<q:
   nextc=2*r+3
   W.add(2,b,1,'diagonal continuation retain V in b accumulator')
   for ell in range(r+2,q+1):
    W.add(2*ell+1,nextc,-1,'diagonal continuation next c difference')
    W.add(2*ell+1,b,1,'diagonal continuation future V reader')
   W.add(nextc,1,1,'diagonal continuation combine U and next delta')
   query(b if continue_wrong_carrier else 1,o,label='diagonal retained J continuation on U')
   W.swap(1,nextc,'diagonal t and held move');W.swap(nextc,b,'diagonal dirty V move');W.swap(b,3,'diagonal completed b move')
  else:W.swap(b,3,'final completed b move')
 query(0,k,label='final independent a J query');W.add(2,0,-1,'final b accumulator isolation')
 for r in range(3,q+1):W.add(2*r+1,2*r-1,1,'triangular public c decode')
 return W

def original_formula(q):
 n,k,m=2*q+2,2*q+1,4*q+4
 I,N,J=mono(qc.identity(m)),mono(n_pair(m,0)),mono(j_operator(m))
 A=product(adjoint(N),J);B={s:product(mono(plane_swap(m,0,s)),A)for s in range(1,k+1)}
 Q1=product(product(adjoint(J),B[1]),J)
 K=[[summ((B[2],Q1,scale(I,-1))),add(I,scale(B[2],-1))],[add(Q1,scale(I,-1)),I]]
 E=I
 for r in range(2,q+1):E=product(B[2*r],E)
 D={r:product(B[2*r+1],J)for r in range(2,q+1)}
 T=I
 for r in range(2,q):T=product(scale(D[r],-1),T)
 T=product(D[q],T)
 Du=product(product(E,B[3]),J)
 H=[[product(Du,x)for x in K[1]],[product(T,x)for x in K[0]]]
 L=[[{}for _ in range(n)]for _ in range(2)]
 uS=product(product(E,B[3]),add(B[1],scale(I,-2)))
 uB=product(E,B[3])
 vS=product(T,summ((scale(J,3),scale(product(J,B[1]),-1),scale(product(B[2],J),-1))))
 for bank in[0]+[2*r for r in range(1,q+1)]:L[0][bank]=dict(uS);L[1][bank]=dict(vS)
 L[0][2]=add(L[0][2],uB);L[1][2]=add(L[1][2],scale(product(T,J),-1))
 R={q:scale(D[q],-1)}
 for r in range(2,q):
  rr=D[r]
  for j in range(r+1,q):rr=product(scale(D[j],-1),rr)
  R[r]=product(D[q],rr)
 for r in range(2,q+1):L[1][2*r]=add(L[1][2*r],product(R[r],J))
 M=eye(n,m)
 for i in range(n):M[i]=[J if i==j else{}for j in range(n)]
 for row,bank in enumerate((1,3)):
  M[bank]=list(L[row]);M[bank][1]=H[row][0];M[bank][3]=H[row][1]
 return {'matrix':M,'H':H,'L_original_columns':L,'K':K,'Du':Du,'Dv':T,'B':B,'Q1':Q1,'R':R}

def native_pool():
 z=Model(1,1);_,J=kernels(z);Jc=mul(z.T[0],J,z.T[0].adjoint())
 pool={}
 for name,op,exponent in(('N',z.N,1),('J0',J,1),('Jcompleted',Jc,1)):
  for inv in(False,True):
   literal=op.adjoint()if inv else op;rec,compiled=ce.lower_child(literal);same(compiled,literal,'selected native query actual Gaussian phase')
   need(rec['rank']==2,'one native2 query')
   pool[name+('inv'if inv else'')]={'one_coordinate_tableau':[list(t)for t in literal.tab],'one_coordinate_definition_circuit':literal.circuit,
        'selected_native_recipe':rec,'phase_exponent':-exponent if inv else exponent,
        'all_f_phase':'i^(phase_exponent*(1-f)) times coordinatewise tensor; selected-native child and both monomial adapters are literal and all arbitrary data are retained'}
 return pool

def metadata(events,q):
 m=4*q+4;z=Model(1,2*q+1);_,J=kernels(z)
 for e in events:
  if e['kind']in('ADD','BANK_SWAP'):continue
  fam=e['native_family']
  if fam:
   inv=fam.get('inverse',False)
   if fam['kind']=='N':
    i=fam['plane'];op=z.N if i==0 else z.T[i-1];dummy=1 if i==0 else 0
    key='N';embedding=[2*i,2*i+1,2*dummy,2*dummy+1]
   else:
    completed=fam['completed'];op=mul(z.T[0],J,z.T[0].adjoint())if completed else J
    key='Jcompleted'if completed else'J0';embedding=[0,1,2,3]
   if inv:op=op.adjoint();key+='inv'
   e['native_recipe_id']=key;e['recipe_embedding']=embedding;e['phase_exponent']=-1 if inv else 1
  else:
   # The only free unary in this prefix is a literal whole-plane ADDRESS.
   rows=qc.decode(e,m).rows
   # Plane swaps are symmetric involutions, so X and ordinary address rows coincide.
   op=ce.perm(m,rows);e['phase_exponent']=0
  e['one_coordinate_literal_circuit']=op.circuit
  e['one_coordinate_tableau']=[list(t)for t in op.tab]
  check_literal_family(e,m)

@lru_cache(None)
def inverse_transpose(rows):
 r=qc.inverse(rows);n=len(rows)
 return tuple(sum(((r[j]>>i)&1)<<j for j in range(n))for i in range(n))

def literal_x(circuit,n,x):
 phase=0
 for e in circuit:
  if e[0]=='P':x=qc.linear(inverse_transpose(tuple(e[1])),x)
  elif e[0]=='C':phase+=e[2]*qc.parity(e[1]&x)
  elif e[0]=='X':phase+=2*qc.parity(e[1]&x)
  elif e[0]=='D':
   need(not any(e[1])and all(v%2==0 for v in e[2]),'literal source phase is explicitly Pauli')
   x^=sum(((v//2)&1)<<i for i,v in enumerate(e[2]))
  elif e[0]=='phase':phase+=e[1]
  else:raise ValueError('uncovered literal event '+e[0])
 return x,phase%4

def check_literal_family(e,m):
 g=qc.decode(e,m);circuit=e['one_coordinate_literal_circuit'];exp=e['phase_exponent']
 _,c0=literal_x(circuit,m,0)
 for x in[0,(1<<m)-1]+[1<<i for i in range(m)]+[(1<<i)|(1<<j)for i in range(m)for j in range(i+1,m)]:
  y,p=literal_x(circuit,m,x)
  need(y==g.act(x),'actual source/ADDRESS circuit X-character map')
  for f in(1,2,3,4):
   need((exp*(1-f)+p+(f-1)*c0)%4==(g.global_phase+g.q(x)+(f-1)*g.q(0))%4,
        'actual source/ADDRESS all-f Gaussian phase')

def prove(q):
 W=build(q);n,k,m=W.n,2*q+1,W.m
 need(mm(W.M,W.Mi)==mm(W.Mi,W.M)==eye(n,m),'every independent original input and both literal inverse orders')
 need(qc.replay(W.events,n,m)==W.M,'separate direct all-f event replay matches incremental operator matrix')
 f=prefix(m,k);ret=[[product(mono(f.inv()),x)for x in row]for row in W.M]
 formula=original_formula(q)
 need(ret==formula['matrix'],'source-bound original-input H/L formula matches every physical prefix column')
 target=mono(f@j_operator(m));public=[i for i in range(n)if i not in(1,3)]
 need(all(W.M[i]==[target if j==i else{}for j in range(n)]for i in public),'all public outputs equal actual F_k J on their independent original inputs')
 hist=Counter(e['rank_per_f']for e in W.events if e['kind']=='NATIVE')
 need(hist=={2:n*k+q+2},'full source/query/idle/continuation histogram')
 need(qc.rank((f@j_operator(m)).polar())==m,'actual output F_k J full native arity')
 metadata(W.events,q)
 inverse_events=W.inverse_events()
 for e in inverse_events:
  if e['kind']not in('ADD','BANK_SWAP'):check_literal_family(e,m)
 need(qc.replay(inverse_events,n,m)==W.Mi,'literal reversed physical word matches full inverse on every column')
 # Original t0 output versus the current V carrier is a fixed, single
 # Clifford inverse entry, independent of all public L readers.
 Cactual=product(target,W.Mi[1][3])
 predicted=product(mono(f),product(mono(j_operator(m)),product(adjoint(formula['Q1']),product(adjoint(formula['B'][2]),product(adjoint(formula['Dv']),mono(f.inv()))))))
 need(Cactual==predicted and len(Cactual)==1,'original-t inverse coefficient binds unfactored joint H/L')
 need(qc.rank(next(iter(Cactual)).polar())==2*q+4,'actual F_k J inverse coefficient native arity')
 return {'q':q,'width':n,'banks':n,'ambient_arity':m,'stages':k,'events':W.events,'inverse_events':W.inverse_events(),
         'histogram':dict(hist),'native_rank_mass':2*hist[2],'stock_if_pivots_complete':n*m,'D_before_cleanup':2*q,
         'public_rows':public,'pivot_rows':[1,3],'physical_matrix':sm(W.M),'physical_inverse':sm(W.Mi),
         'retarded_matrix':sm(ret),'H':sm(formula['H']),'L_original_columns':sm(formula['L_original_columns']),
         'core_K':sm(formula['K']),'Du':serial(formula['Du']),'Dv':serial(formula['Dv']),
         'original_t_from_current_V_correction':serial(Cactual),'original_t_from_current_V_native_arity_per_f':2*q+4,
         'native_recipe_pool':native_pool(),
         'all_input_domain':'Every original input, including t0,k0 and all c fields, arbitrary and independent; all positive f via exact tensor phase polynomials.',
         'limits':['Prefix only; joint cleanup not included.','Actual output is F_k J, with its right gauge retained; it is not silently E.','No independent helper stock is credited from a coupled H.']}

def produce():
 fixtures=[prove(q)for q in(2,3)]
 wrong=build(3,omit_raw_a_restore=True)
 need(wrong.M!=build(3).M,'omitted raw-a restoration changes original columns')
 wrong=build(3,continue_wrong_carrier=True)
 need(wrong.M!=build(3).M,'continuing V instead of U changes original columns')
 return {'status':'PASS_J_DIAGONAL_PHYSICAL_PREFIX_ALL_ORIGINAL_COLUMNS_ALL_F',
         'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','fixtures':fixtures,
         'negative_controls':['Omitted independent raw-a restoration rejected.','Continued V instead of U rejected.'],
         'source_pins':[{'path':str(OLD/p),'sha256':h}for p,h in PINS.items()]+[{'path':str(HERE/'joint_algebra.py'),'sha256':hashlib.sha256((HERE/'joint_algebra.py').read_bytes()).hexdigest()}],
         'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_new_kappa':True}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
 out=json.loads(json.dumps(produce()));path=HERE/'JOINT-PREFIX.json'
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved joint physical prefix differs')
 print(out['status'])
if __name__=='__main__':main()
