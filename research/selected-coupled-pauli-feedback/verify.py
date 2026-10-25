#!/usr/bin/env python3
"""Literal selected Pauli binding and reversible elementary-network certificate."""
from pathlib import Path
import collections,gzip,hashlib,io,json,sys,tarfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import exact as g
F=g.F;ONE=g.ONE;ZERO=g.ZERO
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
A=(F(1,2),F(1,2));B=(F(1,2),F(-1,2))
PINS={'LOCAL-PROGRAMS.json.gz':'241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a','CLIFFORD-RECIPES.json':'d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731'}
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def encode(v):return [[i,str(a),str(b)] for i,(a,b) in sorted(v.items())]
def pauli(v,j=0,literal=False):
 if literal:return {x^224:g.phase(a,2*((x&96).bit_count()%2)) for x,a in v.items()}
 return {x^(1<<(2*j+1)):a for x,a in v.items()}
def source_R(v):return {x^30:g.phase(a,3+2*((x&14).bit_count()%2)) for x,a in v.items()}
def kernel(v,j,inverse=False):
 return g.plus(g.scaled(v,B if inverse else A),g.scaled({x^(1<<j):a for x,a in v.items()},A if inverse else B))
def Bf(v,f,inverse=False):
 for j in range(f):v=g.plus(g.scaled(v,B if inverse else A),g.scaled(pauli(v,j),A if inverse else B))
 return v

def gaussian_compute(f):
 # Application order is right-to-left in the displayed elementary identity.
 out=[]
 for j in range(f):
  out += [(2,1,j,False,g.neg(A)),(2,1,j,True,g.neg(B)),
          (1,2,j,False,g.neg(A)),(1,2,j,True,A),
          (2,1,j,False,ONE),(1,2,j,False,g.neg(B)),(1,2,j,True,B)]
 return out

def native_compile(gates):
 out=[]
 for t,s,j,p,c in gates:
  if p:out.append(('pauli',s,j))
  if c[0]:out.append(('add',t,s,c[0]))
  if c[1]:out += [('phase',s,1),('add',t,s,c[1]),('phase',s,3)]
  if p:out.append(('pauli',s,j))
 return out

def full_native(f):
 comp=gaussian_compute(f);uncomp=[(t,s,j,p,g.neg(c)) for t,s,j,p,c in reversed(comp)]
 return native_compile(comp)+[('add',0,1,F(1,2))]+native_compile(uncomp)

def execute(state,gates,literal=False):
 state=[dict(v) for v in state]
 for event in gates:
  if event[0]=='pauli':_,s,j=event;state[s]=pauli(state[s],j,literal)
  elif event[0]=='phase':_,s,p=event;state[s]={x:g.phase(a,p) for x,a in state[s].items()}
  else:
   _,t,s,c=event;state[t]=g.plus(state[t],g.scaled(state[s],(c,F(0))))
 return state

def canonical_C(v,f):
 for j in range(2*f):v=kernel(v,j)
 return v

def source_load():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for r in pins['files']:
  if r.get('usage')=='input':require(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'source input pin '+r['path'])
 raw=(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz').read_bytes()
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
  assembly_raw=t.extractfile('candidate/strict/ASSEMBLY.json').read()
  require(hashlib.sha256(assembly_raw).hexdigest()=='1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045','selected assembly member pin')
  require(json.loads(assembly_raw)['complex_lower']=='67018507072324140917/40000000000000000000000','selected exponent source')
  data={}
  for name,pin in PINS.items():
   b=t.extractfile('candidate/strict/global/base/providers/gauge44/'+name).read();require(hashlib.sha256(b).hexdigest()==pin,'member pin '+name)
   data[name]=json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
 return data['LOCAL-PROGRAMS.json.gz']['forward'],{(r['old'],r['new']):r for r in data['CLIFFORD-RECIPES.json']['children']}

def touched(e,r):return (e[0] in ('climb','adapter','residual_adapter') and e[2]==r) or (e[0]=='scalar' and ['L',r] in e[1])

def ring_add(x,y):return tuple(g.add(a,b) for a,b in zip(x,y))
def ring_mul(x,y):return (g.add(g.mul(x[0],y[0]),g.mul(x[1],y[1])),g.add(g.mul(x[0],y[1]),g.mul(x[1],y[0])))
def ring_matmul(X,Y):
 return [[ring_add(ring_mul(X[i][0],Y[0][j]),ring_mul(X[i][1],Y[1][j])) for j in range(2)] for i in range(2)]
def ring_identity():return [[(ONE,ZERO),(ZERO,ZERO)],[(ZERO,ZERO),(ONE,ZERO)]]
def shear(t,s,c):
 e=ring_identity();e[t][s]=c;return e

def evaluate():
 events,rd=source_load();rA,rB,rC=[rd[k] for k in [(0,2),(2,252),(0,252)]]
 require([r['rank'] for r in [rA,rB,rC]]==[1,1,2],'actual source ranks')
 require(all(e[0] in ('climb','scalar') for e in events[12806:13403]),'complete region alphabet')
 require(all(e[1][0]=='add' for e in events[12806:13403] if e[0]=='scalar'),'complete region scalar semantics')
 require(events[12806]==['climb','B',195,0,2,1] and events[13402]==['climb','B',195,2,252,1],'literal caller')
 require([(i,e) for i,e in enumerate(events[12807:13402],12807) if touched(e,195) or touched(e,521)]==[(12807,['scalar',['add',['L',195],['L',521],1,2],2])],'complete literal dependency boundary')
 # The 2x2 identity is checked in Q(i)[P]/(P^2-1), without sampling P.
 u=(A,B);ui=(B,A);one=(ONE,ZERO);zero=(ZERO,ZERO)
 require(ring_mul(u,ui)==one,'formal unit inverse')
 factors=[shear(0,1,(g.neg(B),B)),shear(1,0,one),shear(0,1,(g.neg(A),A)),shear(1,0,(g.neg(A),g.neg(B)))]
 mat=ring_identity()
 for e in factors:mat=ring_matmul(mat,e)
 require(mat==[[u,zero],[zero,ui]],'formal four elementary matrix identity')
 # Every literal 512-dimensional source column and all three payload inputs.
 literal_gates=full_native(1);columns=[]
 for i in range(512):
  e={i:ONE};av=g.apply(e,rA);bv=g.apply(e,rB);cv=g.apply(e,rC)
  require(av==g.plus(g.scaled(e,A),g.scaled(source_R(e),B)),'actual A Pauli identity')
  require(bv==g.plus(g.scaled(e,A),g.scaled(pauli(e,literal=True),B)),'actual B Pauli identity')
  require(g.apply(av,rB)==cv,'exact BA=C')
  require(source_R(pauli(e,literal=True))==pauli(source_R(e),literal=True),'Paulis commute')
  require(source_R(source_R(e))==e and pauli(pauli(e,literal=True),literal=True)==e,'both Paulis involutory')
  require(len(cv)==4 and all(a*a+b*b==F(1,4) for a,b in cv.values()),'rank2 normalized entry bound')
  for reg in range(3):
   state=[{}, {}, {}];state[reg]=cv if reg==0 else e
   actual=execute(state,literal_gates,True)
   expected=[cv,{},{}] if reg==0 else [g.scaled(bv,(F(1,2),F(0))),e,{}] if reg==1 else [{},{},e]
   require(actual==expected,'all literal dirty-helper boundary columns')
   columns.append([encode(v) for v in actual])
 # Monomial orbit charts: 128 four-coordinate source blocks reduce A,B to
 # independent coordinate kernels, hence f-fold lifts to 4^f blocks.
 seen=set();orbits=[]
 for x in range(512):
  if x in seen:continue
  orbit={x,x^30,x^224,x^254};require(len(orbit)==4 and not(seen&orbit),'independent Pauli translation orbits');seen |=orbit
  chart=[]
  for ab in range(4):
   v={x:ONE}
   if ab&1:v=source_R(v)
   if ab&2:v=pauli(v,literal=True)
   chart.append(v)
  for ab,v in enumerate(chart):
   require(source_R(v)==chart[ab^1] and pauli(v,literal=True)==chart[ab^2],'source monomial chart')
  orbits.append(x)
 require(len(orbits)==128 and len(seen)==512,'all source orbit blocks')
 reduced=[]
 for f in [1,2,3]:
  gates=full_native(f);counts=collections.Counter(e[0] for e in gates)
  require(counts=={'add':26*f+1,'pauli':12*f,'phase':24*f},'complete native gate counts')
  for reg in range(3):
   for i in range(1<<(2*f)):
    e={i:ONE};state=[{},{},{}];state[reg]=canonical_C(e,f) if reg==0 else e
    actual=execute(state,gates)
    expected=[canonical_C(e,f),{},{}] if reg==0 else [g.scaled(Bf(e,f),(F(1,2),F(0))),e,{}] if reg==1 else [{},{},e]
    require(actual==expected,'complete reduced tensor basis')
  reduced.append({'f':f,'basis_inputs':3*(4**f),'rational_adds':counts['add'],'signed_pauli_maps':counts['pauli'],'unit_phase_maps':counts['phase']})
 # The all-f lower bound is proved analytically; exact inequalities provide
 # finite controls and demonstrate why f-1 is excluded, while f is permitted.
 for f in range(1,257):
  require((1<<(f-1))*((1<<f)+1)<(1<<(2*f)), 'f-1 lower bound fails')
  require((1<<f)*((1<<f)+1)>=(1<<(2*f)), 'f is not excluded by uncertainty')
 # Controls intentionally break inverse order, coefficient, and dirty recovery.
 sample=[{}, {0:ONE},{1:ONE}]
 good=execute(sample,full_native(1))
 mutants=[]
 bad=full_native(1)[:-1];mutants.append(execute(sample,bad)!=good)
 bad=list(full_native(1));at=next(i for i,e in enumerate(bad) if e[0]=='add' and e[1]==0);bad[at]=('add',0,1,F(1));mutants.append(execute(sample,bad)!=good)
 bad=list(reversed(full_native(1)));mutants.append(execute(sample,bad)!=good)
 bad=list(full_native(1));at=next(i for i,e in enumerate(bad) if e[0]=='phase');bad[at]=('phase',bad[at][1],3);mutants.append(execute(sample,bad)!=good)
 require(all(mutants),'all substantive controls reject')
 return {'literal_boundary_inputs':1536,'literal_boundary_sha256':digest(columns),'source_orbits':128,'reduced_tensor_checks':reduced,'formal_ring_identity':True,'paulis':{'A':{'xor':30,'sign_mask':14,'phase':3},'B':{'xor':224,'sign_mask':96,'phase':0}},'one_child_rank':'2f','child_operand_volume':'V','payloads':3,'extra_arbitrary_dirty_payloads':1,'restored_donor_and_helper':True,'gaussian_shears':'14f+1','rational_adds':'26f+1','signed_pauli_maps':'12f','unit_phase_maps':'24f','support_lower_bound':'k>=f','ordinary_fourier_uncertainty':'support(v)*support(Qv)>=4^f','lower_bound_integer_controls':256,'negative_controls':len(mutants),'new_kappa':False}

def main():
 r=evaluate();require(r==json.loads((HERE/'RESULT.json').read_text()),'committed result equality')
 print('PASS_SELECTED_COUPLED_PAULI_FEEDBACK literal_basis=1536 tensor_basis=252 lower_bound=k>=f rational_adds=26f+1 controls=4 no_new_kappa')
if __name__=='__main__':main()
