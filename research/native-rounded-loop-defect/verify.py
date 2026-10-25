"""Literal native-loop lifting obstruction. JoyboyBrian/OpenAI, Apache-2.0."""
import gzip,hashlib,importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
p=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
for pin in json.loads((p/'PINS.json').read_text()):
 need(hashlib.sha256((p/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source authentication '+pin['path'])
def load(name):
 spec=importlib.util.spec_from_file_location(name,p/'source'/(name+'.py'));mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
ce=load('clifford_exact');lift=load('lifting')
STEPS=((0,True),(1,False),(2,False),(3,True))

def mono(rec):
 return ce.diag(9,tuple(rec['quadratic_rows']),tuple(rec['linear_Z4'])).then(ce.perm(9,tuple(rec['matrix_rows']))).then(ce.xgate(9,rec['offset'])).then(ce.Op(9,ce.identity(9),[('phase',rec['phase'])]))
def equal(a,b):return a.tab==b.tab and a.zero_state()==b.zero_state()
def rotate(z,k):
 a,b=z
 if k%4==0:return a,b
 if k%4==1:return -b,a
 if k%4==2:return -a,-b
 return b,-a

def wrapper(v,rec,inverse=False):
 # Independently interpret signed affine recipe; no lifting plan is called.
 out=[None]*512
 for x in range(512):
  y=rec['offset']
  for j,row in enumerate(rec['matrix_rows']):y^=((row&x).bit_count()%2)<<j
  phase=rec['phase']+sum(((x>>j)&1)*rec['linear_Z4'][j]for j in range(9))
  phase+=2*sum(((x>>j)&1)*((x>>k)&1)*((rec['quadratic_rows'][j]>>k)&1)for j in range(9)for k in range(j+1,9))
  if inverse:out[x]=rotate(v[y],-phase)
  else:out[y]=rotate(v[x],phase)
 need(all(z is not None for z in out),'independent wrapper bijection')
 return out

def independent(v,rec,inverse=False,ideal=False):
 v=wrapper(v,rec['left' if inverse else 'right'],inverse)
 for x in range(0,512,2):
  a,b=v[x],v[x+1];d=(a[0]-b[0],a[1]-b[1])
  half=lambda z:F(z,2) if ideal else z//2
  s=(b[0]+half(d[0]),b[1]+half(d[1]));e=rotate(d,-1 if inverse else 1)
  b=(s[0]-half(e[0]),s[1]-half(e[1]));a=(b[0]+e[0],b[1]+e[1]);v[x],v[x+1]=a,b
 return wrapper(v,rec['right' if inverse else 'left'],inverse)

def main():
 word=json.loads(gzip.decompress((p/'source/ACTUAL-WORD.json.gz').read_bytes()));program=word['programs']['forward'];frames=word['canonical']['frames']
 cert=json.loads(gzip.decompress((p/'source/graph-certificate.json.gz').read_bytes()))['forward']
 expected={8160:['climb','warp_retimed',230,0,29,1],8148:['climb','warp_retimed',224,0,2,1],8196:['climb','warp_retimed',0,2,341,1],8197:['climb','warp_retimed',27,29,341,1]}
 for i,e in expected.items():need(program[i]==e,'literal event binding')
 need(all(i in cert['forest_event_ids']for i in (8160,8148,8196)) and 8197 in cert['chord_event_ids'],'fundamental cycle binding')
 need([frames[i]for i in (0,29,2,341)]==[[],[38],[11],[38,11]],'literal frames')
 recipes=[];ops=[]
 for a,b in ((0,29),(0,2),(2,341),(29,341)):
  op=ce.canonical_frame(9,frames[a]).adjoint().then(ce.canonical_frame(9,frames[b]));rec,_=ce.lower_child(op)
  need(rec['rank']==1,'actual paid rank1');decoded=mono(rec['right']).then(ce.fourier(9,[0])).then(mono(rec['left']))
  need(equal(op,decoded),'signed native recipe exact including phase');recipes.append(rec);ops.append(op)
 need(json.dumps(recipes,sort_keys=True)==json.dumps(json.loads((p/'RECIPES.json').read_text()),sort_keys=True),'native recipe receipt')
 product=ce.ident(9)
 for j,inv in STEPS:product=product.then(ops[j].adjoint()if inv else ops[j])
 need(equal(product,ce.ident(9)),'ideal closed walk identity with absolute phase')
 plans=[(lift.plan(q['left']),lift.plan(q['right']))for q in recipes]
 start=[(0,0)]*512;start[1]=(1,0);v=start[:];ref=start[:];ideal=start[:];meter=dict(pairs=0,wrapper_values=0);cuts=[]
 for j,inv in STEPS:
  before=v[:];lift.kernel(v,1,*plans[j],inverse=inv,meter=meter);ref=independent(ref,recipes[j],inv);ideal=independent(ideal,recipes[j],inv,True)
  need(v==ref,'independent floor and wrapper replay')
  back=v[:];lift.kernel(back,1,*plans[j],inverse=not inv);need(back==before,'same child exact inverse')
  cuts.append([[i,list(z)]for i,z in enumerate(v)if z!=(0,0)])
 expected_output=[[1,[0,1]],[10,[1,0]],[39,[1,0]]]
 need(cuts[-1]==expected_output,'exact nonzero holonomy');need(ideal==start,'independent rational loop identity')
 need(v!=start,'flatness falsified')
 for j,inv in reversed(STEPS):lift.kernel(v,1,*plans[j],inverse=not inv)
 need(v==start,'whole literal reverse restores witness')
 # Grid-translation positive control: even enough input makes all floors exact.
 v=[(a*16,b*16)for a,b in start]
 for j,inv in STEPS:lift.kernel(v,1,*plans[j],inverse=inv)
 need(v==[(a*16,b*16)for a,b in start],'aligned lattice positive control')
 # Altering one global phase is invisible to a tableau-only check, but rejected here.
 changed=json.loads(json.dumps(recipes[0]));changed['left']['phase']=(changed['left']['phase']+1)%4
 bad=mono(changed['right']).then(ce.fourier(9,[0])).then(mono(changed['left']))
 need(bad.tab==ops[0].tab and not equal(bad,ops[0]),'absolute phase fault detection')
 result=dict(events=[8160,8148,8196,8197],directions=['inverse','forward','forward','inverse'],frames=[29,0,2,341,29],witness_input=[[1,[1,0]]],witness_output=expected_output,defect_squared_norm=4,cuts=cuts,meter=meter,claim='Every dyadic grid has a scaled witness; exact child inverses do not imply native graph flatness.')
 need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((p/'RESULT.json').read_text()),sort_keys=True),'receipt equality');print('PASS_NATIVE_ROUNDED_LOOP_DEFECT '+json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
