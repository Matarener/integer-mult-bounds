"""Literal 64-bit scalar recoding for the source 112-owner inverse code.
One coordinate of the field; arbitrary field-width repetition is explicit.
ISA subset and interpreter adapted from the preceding Word RAM kernel.
"""
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
import hashlib,json,random

MASK=(1<<64)-1
ZERO,ONE,NEG,ABS,SIGN,QUOT,PARITY,TMP,NTMP,SHARED=range(10,20)
OWNED=set(range(10,20))|set(range(3000,3008))

def need(ok,message):
 if not ok: raise ValueError(message)

def signed(x): return x if x<(1<<63) else x-(1<<64)

def execute(code,initial):
 m={a:v&MASK for a,v in initial.items()};pc=steps=0;writes=set()
 while steps<=len(code):
  op,*args=code[pc];steps+=1;pc+=1
  if op=='accept':return m,steps,writes
  if op=='bltz':
   if signed(m.get(args[0],0))<0:pc=args[1]
  else:
   dst=args[0];writes.add(dst)
   if op=='one':v=1
   elif op=='add':v=m.get(args[1],0)+m.get(args[2],0)
   elif op=='sub':v=m.get(args[1],0)-m.get(args[2],0)
   else:raise ValueError('not an admitted ISA instruction')
   m[dst]=v&MASK
 raise ValueError('nonhalting program')

class Builder:
 def __init__(self):self.code=[];self.labels={};self.fixups=[];self.constants={};self.owned=set(OWNED)
 def emit(self,*args):self.code.append(args)
 def label(self,name):self.labels[name]=len(self.code)
 def branch(self,cell,label):self.fixups.append((len(self.code),label));self.emit('bltz',cell,-1)
 def jump(self,label):self.branch(NEG,label)
 def constant(self,n):
  if n not in self.constants:
   a=4000+len(self.constants);self.constants[n]=a;self.owned.add(a)
   self.emit('one',a)
   for bit in bin(n)[3:]:
    self.emit('add',a,a,a)
    if bit=='1':self.emit('add',a,a,ONE)
  return self.constants[n]
 def divide52(self,src,dst,k):
  tag=f'div{len(self.code)}';self.emit('add',ABS,src,ZERO);self.emit('add',SIGN,src,ZERO)
  self.branch(SIGN,tag+'negative');self.jump(tag+'absdone')
  self.label(tag+'negative');self.emit('sub',ABS,ZERO,ABS);self.label(tag+'absdone')
  self.emit('sub',QUOT,ZERO,ZERO);self.emit('sub',PARITY,ZERO,ZERO)
  for j in range(k,-1,-1):
   threshold=self.constants[52*(1<<j)];power=self.constants[1<<j]
   self.emit('sub',TMP,ABS,threshold);self.branch(TMP,tag+f'skip{j}')
   self.emit('add',ABS,TMP,ZERO);self.emit('add',QUOT,QUOT,power)
   if j==0:self.emit('one',PARITY)
   self.label(tag+f'skip{j}')
  self.emit('sub',TMP,ABS,self.constants[26]);self.branch(TMP,tag+'rounddone')
  self.emit('sub',NTMP,ZERO,TMP);self.branch(NTMP,tag+'increment')
  self.emit('sub',NTMP,ZERO,PARITY);self.branch(NTMP,tag+'increment');self.jump(tag+'rounddone')
  self.label(tag+'increment');self.emit('add',QUOT,QUOT,ONE);self.label(tag+'rounddone')
  self.branch(SIGN,tag+'negout');self.emit('add',dst,QUOT,ZERO);self.jump(tag+'outdone')
  self.label(tag+'negout');self.emit('sub',dst,ZERO,QUOT);self.label(tag+'outdone')
 def finish(self):
  for a in sorted(self.owned):self.emit('sub',a,a,a)
  self.emit('accept')
  for pc,label in self.fixups:self.code[pc]=('bltz',self.code[pc][1],self.labels[label])
  return self.code

def program(columns,k=4,shared=True,inplace=False):
 need(1<=k<=56,'scalar word bound k in [1,56]')
 b=Builder();b.emit('one',ONE);b.emit('sub',ZERO,ONE,ONE);b.emit('sub',NEG,ZERO,ONE)
 for j in range(k,-1,-1):b.constant(52*(1<<j));b.constant(1<<j)
 b.constant(26)
 for j,col in enumerate(columns):
  b.emit('sub',3000+j,ZERO,ZERO)
  for i,c in enumerate(col):
   if c:b.emit('add' if c==1 else 'sub',3000+j,3000+j,1000+i)
 if shared:
  for j in range(8):b.divide52(3000+j,3000+j,k)
 for i in range(112):
  dst=1000+i if inplace else 2000+i
  if not inplace:b.emit('add',dst,1000+i,ZERO)
  for j in range(8):
   c=columns[j][i]
   if c:
    value=3000+j
    if not shared:b.divide52(value,SHARED,k);value=SHARED
    b.emit('sub' if c==1 else 'add',dst,dst,value)
 code=b.finish();return code,b.owned

def nearest_even(x):
 q,r=divmod(x.numerator,x.denominator)
 return q+(2*r>x.denominator or (2*r==x.denominator and q%2==1))

def verify():
 here=Path(__file__).resolve().parent
 data=json.loads((here/'mode_columns.json').read_text(encoding='utf-8'));M=data['mode_columns']
 need(len(M)==8 and all(len(c)==112 for c in M),'matrix dimensions')
 need(all(x in (-1,0,1) for c in M for x in c),'signed modes')
 need(all(sum(x!=0 for x in c)==56 for c in M),'56 per mode')
 need(all(sum(c[i]!=0 for c in M)==4 for i in range(112)),'four per row')
 need(all(sum(M[i][k]*M[j][k] for k in range(112))==56*(i==j) for i in range(8) for j in range(8)),'mode Gram')
 code_raw=(here/'CODE.json').read_bytes()
 need(hashlib.sha256(code_raw).hexdigest()=='8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0','pinned actual producer code')
 source_A=[[F(x) for x in row] for row in json.loads(code_raw)['A']]
 need(all(source_A[i][j]==F(i==j)-sum(F(c[i]*c[j],4) for c in M) for i in range(112) for j in range(112)),'all 12544 actual code entries')
 norms={}
 for den in (4,52):
  A=[[F(i==j)-sum(F(c[i]*c[j],den) for c in M) for j in range(112)] for i in range(112)]
  values={sum(abs(x) for x in row) for row in A}
  need(values=={F(26) if den==4 else F(38,13)},'exact output row norms')
  norms[str(den)]=str(next(iter(values)))
 shared,owned=program(M);control,owned_control=program(M,shared=False)
 need(owned==owned_control,'same scratch ABI')
 rng=random.Random(20261024)
 tests=[[0]*112,[15]*112,[-15]*112,[15*(-1)**i for i in range(112)]]
 tests += [[int(i==j) for i in range(112)] for j in range(112)]
 tests += [[rng.randrange(-16,17) for _ in range(112)] for _ in range(20)]
 dynamic=[];maxerror=F(0)
 for values in tests:
  initial={1000+i:x for i,x in enumerate(values)}
  initial.update({a:rng.randrange(1<<64) for a in owned})
  initial.update({-999:12345,999999:(1<<64)-1})
  a,sa,wa=execute(shared,initial);b,sb,wb=execute(control,initial)
  ta=[sum(c[i]*values[i] for i in range(112)) for c in M]
  exact=[F(values[i])-sum(F(M[j][i]*ta[j],52) for j in range(8)) for i in range(112)]
  expected=[values[i]-sum(M[j][i]*nearest_even(F(ta[j],52)) for j in range(8)) for i in range(112)]
  for i in range(112):
   need(signed(a[2000+i])==signed(b[2000+i])==expected[i],'shared/control output')
   maxerror=max(maxerror,abs(F(expected[i])-exact[i]))
  need(all(a[x]==b[x]==0 for x in owned),'owned cleanup')
  need(all(a[x]==b[x]==v&MASK for x,v in initial.items() if x not in owned),'input/exterior frame')
  need(wa<=owned|set(range(2000,2112)) and wb<=owned|set(range(2000,2112)),'write frame')
  dynamic.append({'shared':sa,'control':sb,'saving':sb-sa})
 need(maxerror<=2,'uniform local 2h error bound')
 db=Builder();db.emit('one',ONE);db.emit('sub',ZERO,ONE,ONE);db.emit('sub',NEG,ZERO,ONE)
 for j in range(4,-1,-1):db.constant(52*(1<<j));db.constant(1<<j)
 db.constant(26);db.divide52(1000,2000,4);division_code=db.finish()
 for numerator in range(-896,897):
  result,_,_=execute(division_code,{1000:numerator})
  need(signed(result[2000])==nearest_even(F(numerator,52)),'exhaustive signed/tie division oracle')
 inplace_code,_=program(M,inplace=True);inplace_control,_=program(M,shared=False,inplace=True)
 need(len(inplace_code)==len(shared)-112 and len(inplace_control)==len(control)-112,'in-place source ABI copy removal')
 inplace_cases=0
 for values in tests[:4]:
  init={1000+i:x for i,x in enumerate(values)};init.update({a:987654321 for a in owned});init[-999]=12345
  ia,_,_=execute(inplace_code,init);ib,_,_=execute(inplace_control,init);fresh,_,_=execute(shared,init)
  need(all(ia[1000+i]==ib[1000+i]==fresh[2000+i] for i in range(112)),'same exact in-place source endpoint')
  need(all(ia[a]==ib[a]==0 for a in owned) and ia[-999]==ib[-999]==12345,'in-place owned/exterior frame')
  inplace_cases+=1
 boundary_cases=0
 for k in (1,8,31,56):
  fused,_=program(M,k=k); duplicate,_=program(M,k=k,shared=False)
  need(len(duplicate)-len(fused)==440*(4*k+24),'static division saving formula')
  for value in (1<<k,-(1<<k)):
   initial={1000+i:(value if i%3 else -value) for i in range(112)}
   initial.update({a:123456789 for a in owned})
   aa,sa,_=execute(fused,initial);bb,sb,_=execute(duplicate,initial)
   need(all(aa[2000+i]==bb[2000+i] for i in range(112)),'word-limit shared/control')
   need(440*(2*k+12)<=sb-sa<=440*(4*k+24),'dynamic saving bound')
   tt=[sum(c[i]*signed(initial[1000+i]&MASK) for i in range(112)) for c in M]
   expected=[signed(initial[1000+i]&MASK)-sum(M[j][i]*nearest_even(F(tt[j],52)) for j in range(8)) for i in range(112)]
   need([signed(aa[2000+i]) for i in range(112)]==expected,'word-limit oracle')
   boundary_cases+=1
 need(all(nearest_even(F(n,52))==-nearest_even(F(-n,52)) for n in range(-1000,1001)),'odd nearest including ties')
 # floor(x+1/2) is not odd at a half step; such an implementation cannot silently hoist signs.
 need((F(26,52)+F(1,2)).__floor__()!=-(F(-26,52)+F(1,2)).__floor__(),'tie-asymmetry control')
 return {'status':'PASS_ACTUAL_INVERSE_MODE_SHARING','source':data['source'],
  'exact_component_infinity_norms':norms,'mode_matrix_shape':[112,8],
  'uniform_local_error_in_lattice_steps':'2','rounding':'nearest ties to even',
  'word_bound':'|input integer numerator|<=2^k; 1<=k<=56; program instances tested k=4',
  'tested_pairs':len(tests),'exhaustive_signed_division_cases':1793,'additional_word_boundary_cases':boundary_cases,'source_all_input_columns':112,'static_shared':len(shared),'static_control':len(control),'inplace_static_shared':len(inplace_code),'inplace_static_control':len(inplace_control),'inplace_checked_cases':inplace_cases,
  'dynamic_shared_min':min(x['shared'] for x in dynamic),'dynamic_shared_max':max(x['shared'] for x in dynamic),
  'dynamic_saving_min':min(x['saving'] for x in dynamic),'dynamic_saving_max':max(x['saving'] for x in dynamic),
  'owned_words':len(owned),'rounded_divisions_shared':8,'rounded_divisions_control':448,
  'signed_add_subtractions_for_modes_and_updates':896,
  'max_observed_error_lattice_steps':str(maxerror),'instructions':['one','add','sub','bltz','accept'],
  'scope':'One actual scalar inverse recoding coordinate with full instruction/setup/cleanup counts; no p19 full native compiler, monomial wrappers, all-size precision tariff or kappa claim'}

if __name__=='__main__':print(json.dumps(verify(),indent=2))




