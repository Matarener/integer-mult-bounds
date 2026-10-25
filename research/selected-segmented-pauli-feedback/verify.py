#!/usr/bin/env python3
"""Exact selected signed-pair synthesis and paid coordinate-volume certificate."""
import collections,gzip,hashlib,io,json,sys,tarfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import exact as g
F=g.F;ONE=g.ONE;ZERO=g.ZERO
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
A=(F(1,2),F(1,2));B=(F(1,2),F(-1,2))
def require(c,m):
 if not c:raise RuntimeError(m)
def enc(v):return [[i,str(a),str(b)] for i,(a,b) in sorted(v.items())]
def signed_P(v):return {x^224:g.phase(a,2*((x&96).bit_count()%2)) for x,a in v.items()}
def R(v):return {x^30:g.phase(a,3+2*((x&14).bit_count()%2)) for x,a in v.items()}
def pair_gates(s):
 return [('add',0,1,F(s)),('add',1,0,F(-s,2)),('phase',0,1),('add',1,0,F(-s,2)),('phase',0,3),('phase',1,1),('add',0,1,F(-s))]
def inverse(gs):
 return [('add',e[1],e[2],-e[3]) if e[0]=='add' else ('phase',e[1],(-e[2])%4) for e in reversed(gs)]
def pair_run(v,gs,states=False):
 v=list(v);trace=[list(v)]
 for e in gs:
  if e[0]=='add':_,t,s,c=e;v[t]=g.add(v[t],g.mul((c,F(0)),v[s]))
  else:_,t,p=e;v[t]=g.phase(v[t],p)
  trace.append(list(v))
 return (v,trace) if states else v

def pair_addresses(size,j,literal=False):
 pivot=9*j+7 if literal else 2*j+1
 mask=224<<(9*j) if literal else 1<<pivot
 lowmask=(1<<pivot)-1
 for q in range(size//2):
  t=(q&lowmask)|((q>>pivot)<<(pivot+1));u=t^mask
  s=1-2*(((t>>(9*j+5))^(t>>(9*j+6)))&1) if literal else 1
  yield t,u,s

def stage(v,size,j,undo=False,literal=False,mutant=None):
 out=dict(v)
 for t,u,s in pair_addresses(size,j,literal):
  if t not in out and u not in out:continue # checker-only zero-state shortcut; ledger counts every scheduled pair
  gs=pair_gates(s)
  if mutant=='wrong-sign':gs=pair_gates(-s)
  if mutant=='missing-phase':gs=gs[:5]+gs[6:]
  if undo:gs=inverse(gs) if mutant!='wrong-inverse' else list(reversed(gs))
  a,b=pair_run([out.get(t,ZERO),out.get(u,ZERO)],gs)
  if a==ZERO:out.pop(t,None)
  else:out[t]=a
  if b==ZERO:out.pop(u,None)
  else:out[u]=b
 return out

def transfer(y,size,f,literal=False,undo=False,mutant=None):
 for j in (reversed(range(f)) if undo else range(f)):y=stage(y,size,j,undo,literal,mutant)
 return y

def macro(x,y,size,f,child,literal=False):
 x=child(x)
 y=transfer(y,size,f,literal)
 x=g.plus(x,g.scaled(y,(F(1,2),F(0))))
 y=transfer(y,size,f,literal,True)
 return x,y

def kernel(v,j):
 return g.plus(g.scaled(v,A),g.scaled({x^(1<<j):a for x,a in v.items()},B))
def canonical(v,f,b_only=False):
 for j in range(f):
  if not b_only:v=kernel(v,2*j)
  v=kernel(v,2*j+1)
 return v

def source():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for r in pins['files']:
  if r['usage']=='input':require(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'input hash '+r['path'])
 with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
  b=t.extractfile('candidate/strict/ASSEMBLY.json').read();require(hashlib.sha256(b).hexdigest()=='1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045','assembly pin');require(json.loads(b)['complex_lower']=='67018507072324140917/40000000000000000000000','exponent')
  data={}
  for name,h in [('LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),('CLIFFORD-RECIPES.json','d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731')]:
   b=t.extractfile('candidate/strict/global/base/providers/gauge44/'+name).read();require(hashlib.sha256(b).hexdigest()==h,'member pin');data[name]=json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
 return data['LOCAL-PROGRAMS.json.gz']['forward'],{(r['old'],r['new']):r for r in data['CLIFFORD-RECIPES.json']['children']}

def touched(e,r):return e[2]==r if e[0]=='climb' else ['L',r] in e[1]
def evaluate():
 events,rd=source();rA,rB,rC=[rd[k] for k in [(0,2),(2,252),(0,252)]]
 region=events[12806:13403]
 require(all(e[0] in ['climb','scalar'] for e in region),'region alphabet')
 require(all(e[1][0]=='add' for e in region if e[0]=='scalar'),'region scalar alphabet')
 require(events[12806]==['climb','B',195,0,2,1] and events[13402]==['climb','B',195,2,252,1],'actual children')
 require([(i,e) for i,e in enumerate(events[12807:13402],12807) if touched(e,195) or touched(e,521)]==[(12807,['scalar',['add',['L',195],['L',521],1,2],2])],'full region dependency')
 pair_columns=0
 for s in [-1,1]:
  for e in [[ONE,ZERO],[ZERO,ONE]]:
   ans=pair_run(e,pair_gates(s));bs=g.mul((F(s),F(0)),B)
   require(ans==[g.add(g.mul(A,e[0]),g.mul(bs,e[1])),g.add(g.mul(bs,e[0]),g.mul(A,e[1]))],'signed formal pair matrix')
   require(pair_run(ans,inverse(pair_gates(s)))==e,'inverse exact');pair_columns+=1
 # Exact induced-norm controls for every pair prefix and inverse. The all-f
 # direct-sum/unitarity argument is written in PROOF.md.
 prefix_controls=0
 for sign in [-1,1]:
  for sequence in [pair_gates(sign),inverse(pair_gates(sign))]:
   for k in range(len(sequence)+1):
    for gs in [sequence[:k],inverse(sequence[:k])]:
     cols=[pair_run(e,gs) for e in [[ONE,ZERO],[ZERO,ONE]]]
     abs_upper=lambda z:abs(z[0])+abs(z[1])
     norm1=max(sum(abs_upper(z) for z in c) for c in cols)
     norminf=max(sum(abs_upper(cols[j][i]) for j in range(2)) for i in range(2))
     require(norm1*norminf<=81,'pair-prefix spectral-norm upper control')
     prefix_controls+=1
 # Address sets cover every physical coordinate once per stage; signs exactly P.
 addr=list(pair_addresses(512,0,True));require(sorted([t for t,u,s in addr]+[u for t,u,s in addr])==list(range(512)),'physical coordinate partition')
 for t,u,s in addr:require(signed_P({t:ONE})=={u:(F(s),F(0))} and signed_P({u:ONE})=={t:(F(s),F(0))},'physical pair sign')
 literal=[]
 for i in range(512):
  e={i:ONE};av=g.apply(e,rA);bv=g.apply(e,rB);cv=g.apply(e,rC)
  require(av==g.plus(g.scaled(e,A),g.scaled(R(e),B)),'actual A')
  require(bv==g.plus(g.scaled(e,A),g.scaled(signed_P(e),B)),'actual B')
  require(g.apply(av,rB)==cv,'BA=C with global phase')
  yd=transfer(e,512,1,True);require(yd==bv,'literal compute')
  yr=transfer(yd,512,1,True,True);require(yr==e,'arbitrary donor restore')
  # x-only and y-only columns of full two-payload boundary.
  for x,y,expected in [(e,{},(cv,{})),({},e,(g.scaled(bv,(F(1,2),F(0))),e))]:
   actual=macro(x,y,512,1,lambda v:g.apply(v,rC),True)
   require(actual==expected,'complete literal macro boundary')
   literal.append([enc(v) for v in actual])
 seen=set();orbits=0
 for t in range(512):
  if t in seen:continue
  orbit={t,t^30,t^224,t^254};require(len(orbit)==4 and not(seen&orbit),'independent orbit');seen|=orbit
  chart=[]
  for ab in range(4):
   v={t:ONE}
   if ab&1:v=R(v)
   if ab&2:v=signed_P(v)
   chart.append(v)
  for ab,v in enumerate(chart):require(R(v)==chart[ab^1] and signed_P(v)==chart[ab^2],'complete tensor chart')
  orbits+=1
 tensor=[]
 for f in [1,2,3]:
  n=4**f
  for i in range(n):
   e={i:ONE};y=transfer(e,n,f)
   require(y==canonical(e,f,True),'complete tensor donor column')
   require(transfer(y,n,f,undo=True)==e,'tensor restoration')
   for x,donor,expected in [(e,{},(canonical(e,f),{})),({},e,(g.scaled(y,(F(1,2),F(0))),e))]:
    require(macro(x,donor,n,f,lambda v:canonical(v,f))==expected,'complete reduced macro boundary')
  # Scheduler counts, including inverse visits and central ADD, on all coords.
  counts=collections.Counter()
  for undo in [False,True]:
   for j in range(f):
    for t,u,s in pair_addresses(n,j):
     for gate in pair_gates(s):counts[gate[0]]+=1
  counts['add']+=n
  require(counts=={'add':(4*f+1)*n,'phase':3*f*n},'coordinate volume ledger')
  tensor.append({'f':f,'basis_inputs':2*n,'volume':n,'rational_coordinate_adds':counts['add'],'unit_phase_coordinate_maps':counts['phase']})
 # Exact dyadic grid and intermediate norm envelope, using a nontrivial vector.
 precision=[]
 for f in [1,2,3]:
  n=4**f;y=g.clean({i:(F((i%7)-3,8),F((i%5)-2,8)) for i in range(n)});original=dict(y)
  maxden=1
  for undo in [False,True]:
   js=list(reversed(range(f))) if undo else list(range(f))
   for j in js:
    # During undo j+1 tensor factors remain; during compute j do.
    before=j+1 if undo else j
    for t,u,s in pair_addresses(n,j):
     ans,trace=pair_run([y.get(t,ZERO),y.get(u,ZERO)],inverse(pair_gates(s)) if undo else pair_gates(s),True)
     for state in trace:
      for z in state:
       for q in z:require((q*(1<<(3+before+1))).denominator==1,'intermediate dyadic precision');maxden=max(maxden,q.denominator)
     for k,z in zip([t,u],ans):
      if z==ZERO:y.pop(k,None)
      else:y[k]=z
  require(y==original,'precision fixture restoration')
  precision.append({'f':f,'input_grid_bits':3,'max_denominator':maxden,'bound_grid_bits':3+f+1})
 controls=[];e={0:ONE};correct=transfer(e,512,1,True)
 for defect in ['wrong-sign','missing-phase']:
  controls.append(transfer(e,512,1,True,mutant=defect)!=correct)
 controls.append(transfer(correct,512,1,True,True,'wrong-inverse')!=e)
 controls.append(g.scaled(correct,(F(1),F(0)))!=g.scaled(correct,(F(1,2),F(0))))
 require(all(controls),'all defect controls reject')
 return {'literal_boundary_inputs':1024,'literal_boundary_sha256':hashlib.sha256(json.dumps(literal,separators=(',',':')).encode()).hexdigest(),'signed_pair_columns':pair_columns,'source_orbits':orbits,'tensor_checks':tensor,'precision_checks':precision,'rational_coordinate_add_volume':'(4f+1)V','unit_phase_coordinate_volume':'3fV','additional_vector_helpers':0,'live_payload':'2V','scalar_scratch':'O(1) coordinate temporaries; no vector register','native_children':[{'rank':'2f','operand_volume':'V'}],'outer_prefix_condition_bound':'729/4','pair_prefix_norm_controls':prefix_controls,'negative_controls':len(controls),'uniform_sub_fV':False,'new_kappa':False}
def main():
 r=evaluate();require(r==json.loads((HERE/'RESULT.json').read_text()),'result equality');print('PASS_SELECTED_SEGMENTED_PAULI_FEEDBACK literal_basis=1024 tensor_basis=168 adds=(4f+1)V phases=3fV vector_helpers=0 controls=4 no_new_kappa')
if __name__=='__main__':main()
