"""Pinned real Callback and SelectedBinding.child_program; no payload execution."""
import ast, importlib.util, json, sys
from pathlib import Path
from types import SimpleNamespace as NS
from hashlib import sha256
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
CALLER=ROOT/'research/selected-bit-physical-caller'; V=CALLER/'inputs/pr2753/predecessor/vendor'
def need(x,m):
 if not x: raise ValueError(m)
def authenticate():
 for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
  if r['usage']=='input':need(sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'changed source: '+r['path'])
def load(name):
 s=importlib.util.spec_from_file_location(name,V/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[name]=m;exec(compile((V/(name+'.py')).read_bytes(),str(V/(name+'.py')),'exec'),m.__dict__);return m
def setup(adapted=False):
 authenticate();w=load('words');r=load('records');load('matrices');c=load('controller');ch=load('children');p=load('plan')
 class ObservedTape(r.Tape):
  created=[]
  def __init__(self):
   super().__init__();self.visited={0,1};self.created.append(self)
  def read(self):self.visited.add(self.head);return super().read()
  def write(self,x):self.visited.add(self.head);return super().write(x)
  def step(self,x):
   self.visited.add(self.head);super().step(x);self.visited.add(self.head)
 r.Tape=ObservedTape
 c.semantic_trace=[]
 original_step=c.Callback.step
 def observed_step(self,level):
  result=original_step(self,level)
  metadata,parent,child,f=result
  c.semantic_trace.append([list(metadata),parent.inspect(),child.inspect(),f.inspect()])
  return result
 c.Callback.step=observed_step
 if adapted:
  import forward_fields
  c.Callback=forward_fields.install(c.Callback,r,V/'controller.py',vars(c))
 tree=ast.parse((CALLER/'macro_binding.py').read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='SelectedBinding')
 nodes=[next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='view'),next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='child_program')]
 env=dict(Callback=c.Callback,Fields=r.Fields,extend=ch.extend,Request=p.Request)
 exec(compile(ast.Module(nodes,type_ignores=[]),'<unchanged selected child_program>','exec'),env)
 return w,r,c,env['child_program']
def meter(m):return {k:getattr(m,k) for k in ('reads','writes','moves')}
def case(h,kind='unit',half=False,Q=4,L=5,adapted=False,mutation=None):
 w,r,c,producer=setup(adapted);root=64**(h+2);I=root.bit_length()+1
 ia=w.Arena(I,128);ra=w.Arena(L,128);mod=ra.input(1<<(L-2));ring=w.Ring(mod)
 specs={0:NS(code=0,good=False,template=NS(q=2,rank=7)),1:NS(code=1,good=True,template=NS(q=2,rank=7))}
 history=[(2,0,7,0,False,False)]*h
 program=r.Program.fixture(ia,ra,root,1,history,Q)
 code=int(kind=='good');high=[[0]*64 for _ in range(64)]
 fields=r.Fields.fixture(ia,ra,[(0,high)]*h+[(code,high)],Q)
 if mutation is not None:mutation(w,r,program,fields)
 original=(bytes(program.tape.cells),bytes(fields.tape.cells));live=(set(ia.live),set(ra.live))
 ia.meter=w.Meter();ra.meter=w.Meter();program.tape.meter=w.Meter();fields.tape.meter=w.Meter()
 for tape in r.Tape.created:tape.visited={tape.head}
 runtime=NS(indices=ia,arena=ra,context=NS(ring=ring),program=program,binding=NS(codes=NS(bits=Q)))
 binding=NS(specifications=specs);event=NS(child_kind=kind,field=0,reverse=False,half=half)
 try:out=producer(binding,runtime,NS(code=code),event,fields.tape)
 except ValueError as error:
  need(live==(set(ia.live),set(ra.live)),'rejected admission numerical cleanup')
  need(program.tape.head==fields.tape.head==1,'rejected admission restored heads')
  if mutation is not None:return dict(rejected=str(error),unchanged=original==(bytes(program.tape.cells),bytes(fields.tape.cells)))
  raise
 need(mutation is None,'malformed admission unexpectedly accepted')
 need(original==(bytes(program.tape.cells),bytes(fields.tape.cells)),'borrowed program/fields unchanged')
 need(live==(set(ia.live),set(ra.live)),'all temporary numerical words freed')
 need(program.tape.head==fields.tape.head==out.head==1,'all public tape heads restored')
 rr=2*I+L+5;cc=Q+2*I+90;ff=Q+2+4096*(L+1)
 need(len(out.cells)==1+rr+(h+1)*cc,'actual child program exact extent')
 n=h+1;D=rr+n*cc
 expected_program=dict(reads=8*rr+1+h*(3*rr+2*I)+cc*(3*h*(h+1)//2+5*h)-h*(h+1)//2,writes=0,moves=6*rr+10+h*(2*rr+2)+cc*(h*h+5*h))
 expected_fields=(dict(reads=n*(3*ff-Q-2)+3,writes=0,moves=2*n*ff+4) if adapted else dict(reads=(3*ff-1)*n*(n+1)//2+n*(2*Q+4)+3,writes=0,moves=ff*n*(n+1)+n*(2*Q+6)+4))
 if adapted:expected_program=dict(reads=5*(rr+h*cc)+2*h*I+1,writes=0,moves=4*(rr+h*cc)+8)
 need(meter(program.tape.meter)==expected_program,'exact complete program scans')
 need(meter(fields.tape.meter)==expected_fields,'exact complete field scans')
 need(meter(out.meter)==dict(reads=2*D+1,writes=D,moves=2*D+2),'exact output construction')
 numerical=sum(meter(ia.meter).values())+sum(meter(ra.meter).values())
 upper=100000*((h+2)**2*(I+1)+(h+2)*(I+1)**2+(L+1)**3)
 need(numerical<=upper,'source-derived conservative numerical action envelope')
 need(len(ia.words)<=64 and len(ra.words)<=len(live[1])+64,'conservative numerical backing')
 need(h<2*(I-1),'accepted root-history shrink coupling')
 need(program.tape.visited==set(range(rr+h*cc+2)),'program lifetime visited span')
 need(fields.tape.visited==set(range(n*ff+2)),'fields lifetime visited span')
 need(out.visited==set(range(D+2)),'output lifetime visited span')
 need(len(r.Tape.created)==7,'exact record tape inventory')
 need(sum(len(t.visited) for t in r.Tape.created)==rr+h*cc+D+n*ff+14,'complete producer record footprint')
 return dict(chronological_trace=c.semantic_trace,record_visited_cells=sum(len(t.visited) for t in r.Tape.created),adapted=adapted,output_sha256=sha256(bytes(out.cells)).hexdigest(),numerical_actions=numerical,numerical_upper=upper,h=h,I=I,L=L,Q=Q,kind=kind,half=half,r=rr,c=cc,F=ff,program=meter(program.tape.meter),fields=meter(fields.tape.meter),output=meter(out.meter),index=meter(ia.meter),residue=meter(ra.meter),index_backing=len(ia.words),residue_backing=len(ra.words),output_cells=len(out.cells))
if __name__=='__main__':
 print(json.dumps([case(h) for h in range(5)],indent=2))

def leaf_case(h,adapted):
 w,r,c,_=setup(adapted);Q,L=5,5;root=64**(h+2);I=root.bit_length()+1
 ia=w.Arena(I,128);ra=w.Arena(L,128);mod=ra.input(8);ring=w.Ring(mod)
 specs={0:NS(code=0,good=False,template=NS(q=2,rank=7))}
 program=r.Program.fixture(ia,ra,root,1,[(2,0,7,0,False,False)]*h,Q)
 fields=r.Fields.fixture(ia,ra,[(0,[[0]*64 for _ in range(64)])]*h,Q)
 before=bytes(program.tape.cells),bytes(fields.tape.cells);live=set(ia.live),set(ra.live)
 program.tape.meter=w.Meter();fields.tape.meter=w.Meter()
 cb=c.Callback(ring,ia,program,fields,specs,0,allow_fallback=True,leaf=True)
 need(cb.program is program,'original random-access Program identity restored')
 state=[cb.root_size.inspect(),cb.root_unit.inspect(),cb.depth.inspect(),cb.final_size.inspect()]
 cb.close();need(live==(set(ia.live),set(ra.live)),'leaf admission cleanup')
 need(before==(bytes(program.tape.cells),bytes(fields.tape.cells)),'leaf borrowed bytes')
 need(program.tape.head==fields.tape.head==1,'leaf restored public heads')
 rr=2*I+L+5;cc=Q+2*I+90;F=Q+2+4096*(L+1);P=rr+h*cc;n=h
 fm=(dict(reads=n*(3*F-Q-2)+3,writes=0,moves=2*n*F+4) if adapted else dict(reads=(3*F-1)*n*(n+1)//2+n*(2*Q+4)+3,writes=0,moves=F*n*(n+1)+n*(2*Q+6)+4))
 need(meter(fields.tape.meter)==fm,'leaf h-field exact scan')
 if adapted:need(meter(program.tape.meter)==dict(reads=3*rr+2*h*cc+2*h*I-2,writes=0,moves=2*P+4),'leaf program scan')
 return dict(h=h,state=state,trace=c.semantic_trace,fields=meter(fields.tape.meter),program=meter(program.tape.meter))

def projected_case(adapted):
 """Peer-derived exact definition projection; no source-plan reconstruction."""
 w,r,c,producer=setup(adapted);low=load('low_codes');codes=low.LowCodes(3,64,28233)
 projection=json.loads((HERE/'SOURCE_PROJECTION.json').read_text())
 need(codes.bits==projection['code_bits']==6507,'current GL code width')
 defs=projection['definitions'];specs={}
 for d in defs:
  ident,common,matrix=codes.decode(d['code'])
  need((ident,common)==(d['request_id'],d['label']=='good'),'projected exact source/view code')
  digest=sha256(json.dumps(matrix,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  need(digest==d['low_sha256'],'projected GL low identity')
  specs[d['code']]=NS(code=d['code'],good=d['good'],template=NS(q=d['q'],rank=d['rank']))
 a,b=defs;I,L,Q=13,5,codes.bits;h=1;n=2
 ia=w.Arena(I,128);ra=w.Arena(L,128);ring=w.Ring(ra.input(9))
 program=r.Program.fixture(ia,ra,2048,2,[(0,a['code'],26,0,False,False)],Q)
 high=[[int(i==j) for j in range(64)] for i in range(64)]
 fields=r.Fields.fixture(ia,ra,[(a['code'],high),(b['code'],high)],Q)
 before=bytes(program.tape.cells),bytes(fields.tape.cells);live=set(ia.live),set(ra.live)
 for tape in r.Tape.created:tape.meter=w.Meter();tape.visited={tape.head}
 ia.meter=w.Meter();ra.meter=w.Meter()
 runtime=NS(indices=ia,arena=ra,context=NS(ring=ring),program=program,binding=NS(codes=NS(bits=Q)))
 out=producer(NS(specifications=specs),runtime,NS(code=b['code']),NS(child_kind='good',field=0,reverse=False,half=False),fields.tape)
 need(before==(bytes(program.tape.cells),bytes(fields.tape.cells)),'projected borrowed bytes')
 need(live==(set(ia.live),set(ra.live)),'projected numerical ownership')
 need(program.tape.head==fields.tape.head==out.head==1,'projected heads')
 rr=2*I+L+5;cc=Q+2*I+90;F=Q+2+4096*(L+1);P=rr+h*cc;D=rr+n*cc
 fm=(dict(reads=n*(3*F-Q-2)+3,writes=0,moves=2*n*F+4) if adapted else dict(reads=(3*F-1)*n*(n+1)//2+n*(2*Q+4)+3,writes=0,moves=F*n*(n+1)+n*(2*Q+6)+4))
 need(meter(fields.tape.meter)==fm,'projected complete Fields invoice')
 need(len(out.cells)==D+1,'projected serialized extent')
 returned=object.__new__(r.Program);returned.index_arena=ia;returned.residue_arena=ra;returned.code_bits=Q;returned.tape=out
 level=ia.input(2);metadata,parent,child=returned.step(level)
 need(metadata==(0,b['code'],7,0,0,0) and parent.inspect()==832 and child.inspect()==91,'actual projected 2048->832->91 history')
 ia.free_many(level,parent,child)
 return dict(output_sha256=sha256(bytes(out.cells)).hexdigest(),field_actions=sum(fm.values()),chronological_trace=c.semantic_trace,
             source_projection_sha256=sha256((HERE/'SOURCE_PROJECTION.json').read_bytes()).hexdigest(),
             source_plan_independently_reconstructed=False,code_bits=Q,root=2048,parent=832,child=91)
