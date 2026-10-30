#!/usr/bin/env python3
"""Paid finite-state conversion joined to the actual retained Machine.run.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
Fixture setup follows Jose Manuel's credited check_machine.py. Its actual
Machine, bank, parking, leaf and monomial execution bodies are imported after
complete source authentication. Reduced dimension2 uses the declared q=2
ordinary backend and has no production moment claim. No production O73/GL64
execution is asserted. The new conversion loops operate on actual source tapes.
"""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from auth import authenticate,need
from bridge import Bridge

def cold():
 authenticate()
 # Compile authenticated canonical controller bytes directly. An existing
 # timestamp-based .pyc is not an authenticated executable input.
 import importlib.abc,importlib.util
 manifest=json.loads((HERE/'SOURCES.json').read_text())
 entries={Path(r['path']).stem:(ROOT/r['path'],r['sha256']) for r in manifest['files'] if r['usage']=='input' and r['path'].startswith('research/physical-complex-controller/') and r['path'].endswith('.py')}
 class RawLoader(importlib.abc.Loader):
  def __init__(self,path,digest):self.path,self.digest=path,digest
  def create_module(self,spec):return None
  def exec_module(self,module):
   raw=self.path.read_bytes();need(hashlib.sha256(raw).hexdigest()==self.digest,'physical executable integrity:'+str(self.path))
   module.__file__=str(self.path);exec(compile(raw,str(self.path),'exec'),module.__dict__)
 class CanonicalFinder(importlib.abc.MetaPathFinder):
  def find_spec(self,fullname,path=None,target=None):
   if fullname in entries:
    file,digest=entries[fullname]
    return importlib.util.spec_from_file_location(fullname,file,loader=RawLoader(file,digest))
   return None
 sys.meta_path.insert(0,CanonicalFinder())
 sys.path.insert(0,str(ROOT/'research/physical-complex-controller'))
 import cohort
 cohort.activate()
 from cardinal_counts import Count
 from fixture_binding import FixtureBinding
 from machine import Machine
 from macro_code import Code
 from ordinary import Ordinary
 from records import Tape
 from words import BLANK,LEFT
 from types import SimpleNamespace
 return cohort,Count,FixtureBinding,Machine,Code,Ordinary,Tape,BLANK,LEFT,SimpleNamespace

def packet(Tape,raw):
 t=Tape()
 for b in raw:t.append(b)
 t.rewind();return t

def data(t,blank):return bytes(t.cells[1:]).rstrip(bytes([blank]))
def encode(values,bits):return bytes((int(v)>>k)&1 for z in values for v in z for k in range(bits))
def oracle(values,width,rows):
 out=[tuple(map(Q,z)) for z in values];N=1<<width
 for axis in range(width):
  q=1<<axis
  for row in range(rows):
   for j in range(N):
    if j&q:continue
    i=row*N+j;k=i+q;a,b=out[i];c,d=out[k]
    out[i]=((a-b+c+d)/2,(a+b-c+d)/2)
    out[k]=((a+b+c-d)/2,(-a+b+c+d)/2)
 need(all(x.denominator==1 for z in out for x in z),'fixture coarse output grid')
 return out

def run(width=2):
 cohort,Count,Binding,Machine,Code,Ordinary,Tape,blank,left,NS=cold()
 binding=Binding();native=Ordinary(2,NS(codes=NS(q=2)),NS(families=0),(Code((('unreachable',),),0),),capacity=64)
 observed=Counter();reentry_rejected=[]
 def observe(m,event):
  need(not m.pool.live,'recursive boundary empty scratch');observed[event]+=1
  if event=='enter' and not reentry_rejected:
   try:m.run(source,descriptors)
   except ValueError as error:
    need('closed prepared complex entry' in str(error),'reentry rejected before state changes');reentry_rejected.append(True)
   else:raise ValueError('active engine accepted reentrant native invocation')
 engine=Machine(binding,native,binding.catalogue,observe)
 depth=0;e=width
 while e>=2:depth+=1;e//=2
 rows=4**depth;coarse=12;reserve=8*width;wide=coarse+2*reserve+4
 descriptors={n:Count.literal(v) for n,v in dict(prefixes=1,rows=rows,front=0,compact_bits=0,before=0,width=width,after=0,back=0,spacing=1,guard=1,residue=0,component_bits=wide,coefficients=1,root_width=width).items()}
 # No productive array is uniform in address; both components and signs vary.
 values=[(4*((7*i)%11-5),4*((3*i)%7-3)) for i in range(rows*(1<<width))]
 source=packet(Tape,encode(values,coarse));source_image=bytes(source.cells)
 unary=[packet(Tape,[1]*n) for n in (coarse,reserve,wide-coarse-reserve)]
 unary_images=[bytes(t.cells) for t in unary]
 lift=Bridge(Tape,blank,left);project=Bridge(Tape,blank,left)
 lift.prepare(*unary);project.prepare(*unary)
 fine=lift.promote(source)
 need(len(data(fine,blank))==len(values)*2*wide,'full lifted packet')
 desc_images={n:bytes(v.tape.cells) for n,v in descriptors.items()}
 result=engine.run(fine,descriptors)
 need(engine.closed and observed['enter']==observed['return'],'matched recursive calls and returns')
 engine.parking.empty()
 need(all(t.read()==blank for t in engine.parked),'actual machine work empty')
 output=project.project(result);actual=data(output,blank)
 need(actual==encode(oracle(values,width,rows),coarse),'promoted recursive endpoint vs independent rational oracle')
 need(bytes(source.cells)==source_image,'borrowed coarse source unchanged')
 need(all(bytes(v.tape.cells)==desc_images[n] for n,v in descriptors.items()),'actual encoded descriptors unchanged')
 need([bytes(t.cells) for t in unary]==unary_images,'borrowed unary patterns unchanged')
 # Consume every protected return; clean the one reusable wide workspace.
 project.consume();project.erase(result);lift.consume();lift.close();project.close()
 need(all(t.read()==blank for t in (lift.output,lift.pattern,project.output,project.pattern,result)),'all bridge work empty')
 for v in descriptors.values():v.close()
 for t in (source,*unary):t.clear()
 return {'status':'PASS_PROMOTED_ACTUAL_RECURSIVE_MACHINE','active_width':width,'ordinary_q':2,'geometry_dimension':2,'rows':rows,'complex_values':len(values),'coarse_bits':coarse,'reserve':reserve,'actual_backend_bits':wide,'minimum_bits':coarse+2*reserve+1,'recursive_boundaries':dict(observed),'endpoint_sha256':hashlib.sha256(actual).hexdigest(),'lift_cell_actions':lift.cost(),'project_cell_actions':project.cost(),'source_descriptors_preserved':True,'all_work_blank':True,'active_backend_reentry_rejected':bool(reentry_rejected),'scope':'Actual unchanged source Machine/cohort and new tape bridge; reduced dimension2/q2 fixture, not production O73/GL64 or all-depth execution. Height proof and production native/refinement assumptions inherited separately.'}

def signed():
 cohort,Count,Binding,Machine,Code,Ordinary,Tape,blank,left,NS=cold()
 from monomial_packets import MonomialPackets
 from session import erase_marker
 from construction import signed_recipe
 binding=Binding();native=Ordinary(2,NS(codes=NS(q=2)),NS(families=0),(Code((('unreachable',),),0),),capacity=64)
 engine=Machine(binding,native,binding.catalogue)
 wrapper_native=Ordinary(2,NS(codes=NS(q=2)),NS(families=0),(Code((('unreachable',),),0),),capacity=64)
 mono=MonomialPackets(('u','t','v0','v1','b'),('v0','v1'),wrapper_native)
 coarse,reserve,wide,rows=10,8,29,2
 widths=tuple(Count.literal(v) for v in (0,0,1,1,0))
 args=tuple(Count.literal(v) for v in (1,1,1,0,wide,1,rows))
 descriptors={n:Count.literal(v) for n,v in dict(prefixes=1,rows=rows,front=0,compact_bits=0,before=0,width=1,after=1,back=0,spacing=1,guard=1,residue=0,component_bits=wide,coefficients=1,root_width=1).items()}
 values=[(4*(i-4),4*((3*i)%5-2)) for i in range(rows*4)]
 raw=encode(values,coarse);unary=[packet(Tape,[1]*n) for n in (coarse,reserve,wide-coarse-reserve)]
 records=[]
 for sign in (1,-1):
  source=packet(Tape,raw);original=bytes(source.cells)
  lift=Bridge(Tape,blank,left);project=Bridge(Tape,blank,left);lift.prepare(*unary);project.prepare(*unary)
  fine=lift.promote(source);recipe=signed_recipe(3,sign,2)
  mono.select(recipe['right']);right=mono.run(fine,widths,*args)
  c=engine.run(right,descriptors)
  project.erase(right);erase_marker(right)
  mono.select(recipe['left']);left_result=mono.run(c,widths,*args)
  result=project.project(left_result);actual=data(result,blank)
  expected=[]
  for i,(a,b) in enumerate(values):
   c0,d=values[(i//4)*4+((i%4)^3)]
   expected.append(((a-sign*b+c0+sign*d)//2,(b+sign*a+d-sign*c0)//2))
  need(actual==encode(expected,coarse),'actual signed monomial/Machine endpoint')
  need(bytes(source.cells)==original,'signed callback borrowed source preserved')
  need(engine.closed and mono.closed and mono.compact.closed,'closed actual signed engines')
  engine.parking.empty()
  project.consume();project.erase(c);project.erase(left_result);erase_marker(left_result)
  lift.consume();lift.close();project.close();source.clear()
  records.append({'sign':sign,'q':3,'geometry_dimension':2,'active_width':1,'complex_values':len(values),'coarse_bits':coarse,'reserve':reserve,'backend_bits':wide,'endpoint_sha256':hashlib.sha256(actual).hexdigest(),'lift_cell_actions':lift.cost(),'project_cell_actions':project.cost()})
 for v in (*widths,*args,*descriptors.values()):v.close()
 for t in unary:t.clear()
 return {'status':'PASS_ACTUAL_SIGNED_MONOMIAL_MACHINE_BRIDGE','fixtures':records,'scope':'Actual source MonomialPackets right/left and Machine.run with paid new bridge; reduced q3/dimension2/width1, not full production recipe payload.'}

def conversions():
 cohort,Count,Binding,Machine,Code,Ordinary,Tape,blank,left,NS=cold()
 from stream import Counter as Countdown
 from bridge import unary_from_count
 records=[]
 for width,reserve,surplus in ((2,0,0),(3,1,2),(8,3,4),(13,8,1)):
  high=reserve+1+surplus;wide=width+reserve+high
  encoded=[Count.literal(v) for v in (width,reserve,high)]
  before=[v.tape.meter.record() for v in encoded]
  generated=[unary_from_count(v,Tape,Countdown) for v in encoded]
  setup={k:sum(t.meter.record()[k]+r[k]+v.tape.meter.record()[k]-old[k] for (t,r),v,old in zip(generated,encoded,before)) for k in ('reads','writes','moves')}
  unary=[v[0] for v in generated]
  source=packet(Tape,encode([(-(1<<(width-1)),(1<<(width-1))-1),(0,-1)],width));image=bytes(source.cells)
  adapter=Bridge(Tape,blank,left);adapter.prepare(*unary)
  fine=adapter.promote(source);fine_raw=data(fine,blank)
  # Its protected output is copied to a distinct owned wide port; consuming
  # it permits reuse of the same adapter for projection and the next call.
  copied=packet(Tape,fine_raw);adapter.consume()
  got=adapter.project(copied);need(data(got,blank)==data(source,blank),'physical signed extrema roundtrip')
  adapter.consume();adapter.erase(copied);adapter.close()
  need(bytes(source.cells)==image,'conversion source preserved')
  counts=adapter.cost();bound=64*(4*wide+wide+width+reserve+high+1)
  need(sum(counts.values())<=bound,'linear conversion cell upper bound')
  records.append({'coarse_bits':width,'reserve':reserve,'backend_bits':wide,'components':4,'cell_actions':counts,'conservative_cell_bound':bound,'unary_counter_actions':[v[1] for v in generated],'paid_unary_generation_actions':setup})
  source.clear()
  retire_tapes=[*unary,*(v.tape for v in encoded)]
  retire_before=[t.meter.record() for t in retire_tapes]
  for t in unary:t.clear()
  for v in encoded:v.close()
  records[-1]['paid_unary_retirement_actions']={k:sum(t.meter.record()[k]-old[k] for t,old in zip(retire_tapes,retire_before)) for k in ('reads','writes','moves')}
 rejected={}
 def reject(name,raw,project=True,bad_setup=False):
  unary=[packet(Tape,[1]*n) for n in (4,2,3)]
  if bad_setup:unary[0]=packet(Tape,[1,0])
  a=Bridge(Tape,blank,left);source=packet(Tape,raw);original=bytes(source.cells)
  try:
   a.prepare(*unary)
   (a.project if project else a.promote)(source)
  except ValueError as error:
   need(source.head==1 and bytes(source.cells)==original,'rejected source restored')
   need(all(t.head==1 for t in unary),'rejected descriptors restored')
   need(a.output.read()==blank,'rejected output erased')
   a.close();rejected[name]=str(error)
  else:raise ValueError('accepted physical control:'+name)
  source.clear()
  for t in unary:t.clear()
 reject('nonzero low bit',bytes([1]+[0]*17))
 reject('negative nonzero low bit',bytes([1]*18))
 reject('wrong sign extension',bytes([0]*6+[1]+[0]*11))
 reject('short wide suffix',bytes([0]*17))
 reject('odd coarse component',bytes([0]*4),project=False)
 reject('malformed unary setup rollback',bytes([0]*8),project=False,bad_setup=True)
 try:Bridge(Tape,5,left)
 except ValueError:rejected['pattern/alphabet collision']='rejected before execution'
 else:raise ValueError('accepted pattern marker collision')
 return {'status':'PASS_PHYSICAL_CONVERSION_CONTROLS','cases':records,'rejections':rejected,'scope':'Actual source tape/countdown, metered new finite-state adapter. Unary descriptor generation/retirement paid, sources preserved including rejected calls.'}

def cleanup_cohort():
 # Explicitly close the retained archive loaders' own temporary directories.
 # This fixes resource lifetime rather than suppressing ResourceWarning.
 import tempfile
 seen=set()
 for module in list(sys.modules.values()):
  if module is None:continue
  for v in list(vars(module).values()):
   if isinstance(v,tempfile.TemporaryDirectory) and id(v) not in seen:
    seen.add(id(v));v.cleanup()

if __name__=='__main__':
 try:
  mode=sys.argv[1] if len(sys.argv)>1 else '2'
  print(json.dumps(signed() if mode=='signs' else conversions() if mode=='conversion' else run(int(mode)),sort_keys=True))
 finally:cleanup_cohort()
