#!/usr/bin/env python3
"""Exact finite controls for the written orbitwise partial-fusion theorem.
Source recipe decoder adapted from Clear1nsight PR3989/PR4009, Apache-2.0.
Substantial OpenAI Codex assistance. No finite test proves the all-f theorem.
"""
from pathlib import Path
from decimal import Decimal, localcontext
import gzip, hashlib, io, json, sys, tarfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import exact as g
F=g.F; ONE=g.ONE
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
a=(F(1,2),F(1,2)); b=(F(1,2),F(-1,2))
ALPHA=F(67018507072324140917,40000000000000000000000)
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
def kernel(v,j):
 return g.plus(g.scaled(v,a),g.scaled({x^(1<<j):c for x,c in v.items()},b))
def product(v,indices):
 for j in indices:v=kernel(v,j)
 return v

def partial(x,y,f,k,mutant=None):
 pre=list(range(0,2*f,2))+list(range(1,2*k,2))
 if mutant=='omit-pre':pre=list(range(0,2*f,2))
 x=product(x,pre)
 correction=product(y,range(1,2*k,2)) if mutant!='omit-transfer' else dict(y)
 x=g.plus(x,g.scaled(correction,(F(1) if mutant=='wrong-half' else F(1,2),F(0))))
 if mutant!='omit-post':x=product(x,range(2*k+1,2*f,2))
 return x,dict(y)
def expected(x,y,f):
 return g.plus(product(x,range(2*f)),g.scaled(product(y,range(1,2*f,2)),(F(1,2),F(0)))),dict(y)
def direct_channels(y,k):
 result={}
 for s in range(1<<k):
  coefficient=ONE;mask=0
  for j in range(k):
   coefficient=g.mul(coefficient,b if s>>j&1 else a)
   if s>>j&1:mask ^= 1<<(2*j+1)
  result=g.plus(result,g.scaled({x^mask:c for x,c in y.items()},coefficient))
 return result

def bind_source():
 for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
  if row['usage']=='input':require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'input pin')
 with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz','r:gz') as archive:
  prefix='candidate/strict/global/base/providers/gauge44/'
  word_raw=archive.extractfile(prefix+'LOCAL-PROGRAMS.json.gz').read()
  recipe_raw=archive.extractfile(prefix+'CLIFFORD-RECIPES.json').read()
  require(hashlib.sha256(word_raw).hexdigest()=='241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a','word member pin')
  require(hashlib.sha256(recipe_raw).hexdigest()=='d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731','recipe member pin')
  assembly=json.loads(archive.extractfile('candidate/strict/ASSEMBLY.json').read())
  require(F(assembly['complex_lower'])==ALPHA,'selected exponent')
 events=json.loads(gzip.decompress(word_raw))['forward']
 recipes={(r['old'],r['new']):r for r in json.loads(recipe_raw)['children']}
 require(events[12806]==['climb','B',195,0,2,1] and events[13402]==['climb','B',195,2,252,1],'literal native events')
 def touches(e):
  return (e[0] in ('climb','adapter','residual_adapter') and e[2] in (195,521)) or (e[0]=='scalar' and any(['L',r] in e[1] for r in (195,521)))
 require([(i,e) for i,e in enumerate(events[12807:13402],12807) if touches(e)]==[(12807,['scalar',['add',['L',195],['L',521],1,2],2])],'entire intervening dependency region')
 ra,rb,rc=[recipes[e] for e in ((0,2),(2,252),(0,252))]
 require([r['rank'] for r in (ra,rb,rc)]==[1,1,2],'literal ranks')
 orbits=set()
 for t in range(512):
  e={t:ONE};r={t^30:g.phase(ONE,3+2*((t&14).bit_count()%2))};p={t^224:g.phase(ONE,2*((t&96).bit_count()%2))}
  require(g.apply(e,ra)==g.plus(g.scaled(e,a),g.scaled(r,b)),'literal A phase')
  require(g.apply(e,rb)==g.plus(g.scaled(e,a),g.scaled(p,b)),'literal B phase')
  require(g.apply(e,rc)==g.apply(g.apply(e,ra),rb),'literal C composition')
  orbit=frozenset((t,t^30,t^224,t^30^224));orbits.add(orbit)
  require(set(g.apply(e,rc))==orbit,'literal full orbit support')
 require(len(orbits)==128 and all(len(o)==4 for o in orbits),'joint orbit partition')
 return {'literal_source_columns':1536,'joint_orbits':128,'intervening_events':595}

def evaluate():
 out=bind_source(); counts=[]; total=0
 for f in range(1,5):
  count=0
  for k in range(f+1):
   for t in range(1<<(2*f)):
    e={t:ONE}
    for x,y in ((e,{}),({},e)):
     require(partial(x,y,f,k)==expected(x,y,f),'partial-fusion complete basis')
     count+=1
    require(direct_channels(e,k)==product(e,range(1,2*k,2)),'direct monomial expansion')
    require(len(product(e,range(1,2*k,2)))==1<<k,'transfer support')
  total+=count;counts.append({'f':f,'k_values':f+1,'two_payload_basis_inputs':count})
 # Different native widths in disjoint orbit blocks, retaining arbitrary input dimensions.
 heterogeneous=0;f=2
 for block,k in enumerate((0,1,2)):
  for t in range(16):
   for register in range(2):
    states=[({}, {}) for _ in range(3)];e={t:ONE};states[block]=(e,{}) if register==0 else ({},e)
    actual=[partial(x,y,f,j) for j,(x,y) in enumerate(states)]
    wanted=[expected(x,y,f) for x,y in states]
    require(actual==wanted,'heterogeneous orbit blocks');heterogeneous+=1
 controls=0
 for mutation in ('omit-pre','omit-transfer','wrong-half','omit-post'):
  require(any(partial(x,y,2,1,mutation)!=expected(x,y,2) for t in range(16) for x,y in (({t:ONE},{}),({},{t:ONE}))), 'mutation was not rejected: '+mutation)
  controls+=1
 # Integer support checks remain exact under -O; analytic proof covers all k.
 for k in range(65):
  require((1<<k)+1 > 1<<k and (1<<k)+1 <= 1<<(k+1),'k+1 shear bound')
 # Numerical controls of the proved chord inequality, not a proof by rounding.
 with localcontext() as ctx:
  ctx.prec=70
  alpha=Decimal(ALPHA.numerator)/Decimal(ALPHA.denominator);p=1-alpha
  delta=2-Decimal(2)**p;checks=0
  for f in range(1,129):
   for k in range(f+1):
    d=2*Decimal(f)**p-Decimal(f+k)**p-(Decimal(f-k)**p if f!=k else 0)
    bound=delta*Decimal(k)*Decimal(f)**(-alpha)
    require(d>=Decimal('-1e-60') and d<=bound+Decimal('1e-60'),'convex chord control');checks+=1
  for f,ks,vs in ((9,(0,1,9),(1,5,2)),(32,(3,12,31),(7,2,1)),(128,(0,4,128),(8,3,5))):
   # Weights are orbit multiplicities; common positive orbit size cancels.
   w=sum(v*k for v,k in zip(vs,ks));s=sum(Decimal(v)*(2*Decimal(f)**p-Decimal(f+k)**p-(Decimal(f-k)**p if k!=f else 0)) for v,k in zip(vs,ks))
   require(s<=delta*Decimal(f)**(-alpha)*w+Decimal('1e-60'),'heterogeneous charge aggregation')
 out.update({'fractional_fusion_basis_cases':counts,'basis_cases_total':total,'heterogeneous_basis_cases':heterogeneous,'negative_controls':controls,'support_integer_controls':65,'convexity_numeric_controls':checks,'new_kappa':False,'theorem':'extra arithmetic >= W; recursive saving <= A delta f^(-alpha) W','scope':'fixed orbit blocks; two native calls; block-wide middle feedback; exact restored donor and auxiliaries'})
 return out
if __name__=='__main__':
 result=evaluate()
 if '--write-result' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 else:require(result==json.loads((HERE/'RESULT.json').read_text()),'frozen RESULT mismatch')
 print('PASS_NATIVE_ORBIT_PARTIAL_FUSION',json.dumps(result,sort_keys=True))
