"""Actual pooled specification -> complete bounded preparation interval.
Apache-2.0. Chris R / Clear1nsight, substantial OpenAI Codex assistance.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import hashlib,importlib.util,itertools,json,sys,tempfile
HERE=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def actions(m):return {k:getattr(m,k) for k in ('reads','writes','moves')}
def minus(a,b):return {k:a[k]-b[k] for k in a}
def add(rows):return {k:sum(r[k] for r in rows) for k in ('reads','writes','moves')}
def load(name,path):
 m=NS(__file__=str(path));exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def authenticate_vendor(base):
 pins=json.loads((HERE/'PREDECESSORS.json').read_text())
 need(sha((HERE/'POOLED-SOURCES.json').read_bytes())==pins['pooled_manifest_sha256'],'exact pooled source manifest')
 rows=json.loads((HERE/'POOLED-SOURCES.json').read_text());expected={r['path']:r['sha256'] for r in rows}
 need(len(rows)==len(expected)==154,'unique complete pooled source inventory')
 expected_dirs=set()
 for name in expected:
  path=Path(name);need(not path.is_absolute() and '..' not in path.parts,'relative retained source path')
  expected_dirs.update(str(x) for x in path.parents if str(x)!='.')
 need(base.is_dir() and not base.is_symlink(),'regular vendor root')
 observed_files=set();observed_dirs=set()
 for path in base.rglob('*'):
  need(not path.is_symlink(),'no retained source links')
  relative=path.relative_to(base).as_posix()
  if path.is_dir():observed_dirs.add(relative)
  else:
   need(path.is_file(),'regular retained source file');observed_files.add(relative)
 need(observed_files==set(expected) and observed_dirs==expected_dirs,'exact materialized source inventory')
 for name,digest in expected.items():
  need(sha((base/name).read_bytes())==digest,'authenticated pooled source '+name)
 return rows

def sources(destination):
 pins=json.loads((HERE/'PREDECESSORS.json').read_text())
 for name,pin in pins['files'].items():
  raw=(HERE/name).read_bytes();need(sha(raw)==pin['sha256'],'exact predecessor adapter/source '+name)
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'predecessor Git blob '+name)
 rows=authenticate_vendor(HERE/'vendor')
 for row in rows:
  target=destination/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes((HERE/'vendor'/row['path']).read_bytes())
 sys.path.insert(0,str(destination/'research/r437-pooled-native-interface'))
 import replica_catalogue as rc
 cat,top=rc.load()
 from catalogue import Specifications
 from sources import identity
 specs=Specifications(cat)
 low=tuple(tuple(map(int,row)) for row in identity(64))
 handle=rc.source_handle(cat,896352,False,low);spec=rc.resolve_handle(cat,specs,handle)
 need(spec.template.rank==14 and not spec.good and cat.codes.bits==6512,'actual pooled IDLE specification')
 old_handle=rc.source_handle(cat,1603,True,low);old_spec=rc.resolve_handle(cat,specs,old_handle)
 need(cat.requests[1603].kind=='COPY' and old_spec.template.rank==7,'actual old COPY source context')
 plan=specs.plan(handle.code);command=plan.commands[0]
 need(command.kind=='child' and command.reference.kind=='unit','actual first fallback UNIT child')
 prior=load('prior4025',HERE/'predecessor4025/verify.py');prior.authenticate()
 import words,records,directory,counts,cardinality,stream
 for name,module in [('words',words),('records',records),('directory',directory),('counts',counts),('cardinality',cardinality),('stream',stream)]:
  need(sha(Path(module.__file__).read_bytes())==prior.PINS[name+'.py'][0],'same complete predecessor runtime '+name)
 return NS(cat=cat,specs=specs,handle=handle,spec=spec,plan=plan,prior=prior,source_identity=cat.source_identity,old_handle=old_handle,old_spec=old_spec)

def run_case(source,h,B,shared,cursor,mutation=None):
 import words as w,records as r,directory as d,counts,controller,macro_binding,packet,cardinality
 import forward_fields
 registry=[];old_init=r.Tape.__init__
 def register(t):old_init(t);registry.append(t)
 r.Tape.__init__=register
 original_callback=macro_binding.Callback;original_dir=d.high_power;original_counts=counts.high_power
 if cursor:macro_binding.Callback=forward_fields.install(controller.Callback,r,Path(controller.__file__),vars(controller))
 if shared:
  replacement=lambda value,ring,q,dimension:source.prior.high_power_shared(value,ring,q,dimension,cardinality.radix_power)
  d.high_power=counts.high_power=replacement
 Q=source.cat.codes.bits;L=3;root=2048*64**h;I=root.bit_length()+1
 ia=w.Arena(I,128);ra=w.Arena(L,4200);modulus=ra.literal(3);ring=w.Ring(modulus)
 code=source.handle.code
 history_codes=[source.old_handle.code if i%2==0 else code for i in range(h)]
 program=r.Program.fixture(ia,ra,root,2,[(2,c,source.specs[c].template.rank,0,False,False) for c in history_codes],Q)
 high=[[0]*64 for _ in range(64)]
 old_fields=r.Fields.fixture(ia,ra,[(c,high) for c in history_codes],Q)
 old=r.Tape();old.cells=bytearray([w.LEFT])+old_fields.tape.cells[1:]*B;old_fields.tape.clear()
 old_count=counts.Count.literal(B);depth=ia.literal(h)
 spectator=ra.literal(1);spectator.head=2;ispectator=ia.literal(1);ispectator.head=2
 protected_tapes=[program.tape,old,old_count.tape]
 protected=[(x,bytes(x.cells),x.head) for x in [ra.template,ia.template]+[ra.words[i] for i in ra.live]+[ia.words[i] for i in ia.live]+protected_tapes]
 live=(set(ra.live),set(ia.live));base_slots=(len(ra.words),len(ia.words))
 before_tapes=set(map(id,registry)); phases={}
 def snapshot():return {'record':add([actions(x.meter) for x in registry]),'residue':actions(ra.meter),'index':actions(ia.meter)}
 def phase(name,fun):
  before=snapshot();v=fun();after=snapshot();phases[name]={lane:minus(after[lane],before[lane]) for lane in before};return v
 original_inspect=w.Word.inspect
 w.Word.inspect=lambda self:(_ for _ in ()).throw(ValueError('runtime Word decoding forbidden'))
 before=snapshot();ra.meter.peak_live=len(ra.live);ia.meter.peak_live=len(ia.live)
 if mutation=='skip_context_share':counts.high_power=original_counts
 context=phase('context_create',lambda:d.Context(ring,source.cat.codes))
 if shared:counts.high_power=d.high_power
 size,fields=phase('frame_controls',lambda:(ia.literal(2048),ia.literal(h+1)))
 runtime=NS(indices=ia,arena=ra,context=context,program=program,binding=NS(codes=source.cat.codes),size=size,depth=depth)
 # size is part of the owned preparation interval and is released below.
 binding=object.__new__(macro_binding.SelectedBinding);binding.specifications=source.specs
 definition=NS(code=code);event=NS(child_kind='unit',field=0,reverse=False,half=False)
 if mutation=='stale_code':definition.code=code^1
 directory,prefixes=phase('directory_produce',lambda:d.produce(old,depth,old_count,code,context))
 def validate():
  first=packet.read_prefix(directory,fields);directory.rewind()
  try:binding.validate_residual(runtime,definition,first)
  finally:first.clear()
 phase('read_validate_clear',lambda:None) if mutation=='skip_validation' else phase('read_validate_clear',validate)
 def child():
  first=packet.read_prefix(directory,fields);directory.rewind()
  try:return binding.child_program(runtime,definition,event,first)
  finally:first.clear()
 output=phase('read_child_clear',child)
 out_sha=sha(bytes(output.cells));dir_sha=sha(bytes(directory.cells))
 # Independent mathematical serialization, external to runtime control.
 def field(value,width):return [(value>>i)&1 for i in range(width)]+[5]
 expected=[w.LEFT,7]+field(root,I)+field(2,L)+field(h+1,I)+[6]
 parent=root
 for c in history_codes+[code]:
  child=parent//64;rank=source.specs[c].template.rank
  expected += [8]
  for j,value in enumerate((2,c,rank,0,0,0)):expected += field(value,Q if j==1 else 16)
  expected += field(parent,I)+field(child,I)+[6];parent=child
 need(parent==32 and bytes(output.cells)==bytes(expected),'independent full child bytes and 2048-to32 extent')
 need(len(directory.cells)==1+B*(h+1)*(Q+2+4096*(L+1)),'complete cap1 directory extent and duplicate prefixes')
 need(all(bytes(x.cells)==raw and x.head==head for x,raw,head in protected),'all borrowed bytes and heads protected')
 need(directory.head==output.head==prefixes.tape.head==1,'all returned heads')
 def dispose():
  output.clear();directory.clear();prefixes.close();ia.free_many(fields,runtime.size);context.close()
 phase('dispose_context_and_outputs',dispose)
 after=snapshot();total={lane:minus(after[lane],before[lane]) for lane in before}
 need(live==(set(ra.live),set(ia.live)),'full interval numerical ownership restored')
 need(all(add([p[lane] for p in phases.values()])==total[lane] for lane in total),'phase invoice partitions complete interval')
 need(all(bytes(x.cells)==raw and x.head==head for x,raw,head in protected),'teardown protected bytes and heads')
 need(all(t.head==1 and all(c==w.BLANK for c in t.cells[1:]) for t in registry if id(t) not in before_tapes),'all new record tapes cleared')
 need(all(word.head==1 and all(c==w.BLANK for c in word.cells[1:]) for bank in (ra,ia) for i,word in enumerate(bank.words) if i not in bank.live),'all released numerical backing erased')
 result=dict(h=h,B=B,Q=Q,I=I,L=L,shared=shared,cursor=cursor,phases=phases,total=total,output_sha256=out_sha,directory_sha256=dir_sha,
  created_record_tapes=sum(id(t) not in before_tapes for t in registry),additional_residue_peak=ra.meter.peak_live-len(live[0]),additional_index_peak=ia.meter.peak_live-len(live[1]),
  new_residue_slots=len(ra.words)-base_slots[0],new_index_slots=len(ia.words)-base_slots[1],protected_state_restored=True,
  source_request=896352,source_rank=14,source_good=False,child_kind='unit',parent_width=2048,child_width=32)
 w.Word.inspect=original_inspect
 macro_binding.Callback=original_callback;d.high_power=original_dir;counts.high_power=original_counts;r.Tape.__init__=old_init
 return result

def audit():
 with tempfile.TemporaryDirectory() as td:
  source=sources(Path(td));pairs=[]
  for h,B in [(0,1),(2,2)]:
   variants=[run_case(source,h,B,s,c) for s,c in itertools.product((False,True),repeat=2)]
   a,b,c,d=variants
   need(len({x['output_sha256'] for x in variants})==len({x['directory_sha256'] for x in variants})==1,'four-way identical output')
   for lane in ('record','index','residue'):
    need(minus(a['total'][lane],d['total'][lane])==add([minus(a['total'][lane],b['total'][lane]),minus(a['total'][lane],c['total'][lane])]),'exact independent additive saving '+lane)
   need(a['total']['record']==c['total']['record'],'radix sharing preserves complete record invoice')
   need(a['total']['residue']==b['total']['residue'],'cursor preserves complete residue invoice')
   for field in ('additional_residue_peak','additional_index_peak','created_record_tapes','new_residue_slots','new_index_slots'):
    need(len({x[field] for x in variants})==1,'same full lifecycle storage '+field)
   # Every interval has two independent 64^2 radix families: Context and producer.
   for phase in ('context_create','directory_produce'):
    delta=minus(a['phases'][phase]['residue'],c['phases'][phase]['residue'])
    need(delta=={'reads':2141685,'writes':389025,'moves':2276820},'exact 4095 removed validated radix traversals')
   pairs.append(dict(variants=variants,saved={lane:minus(a['total'][lane],d['total'][lane]) for lane in ('record','residue','index')}))
  return dict(status='PASS_ACTUAL_POOLED_PREPARATION_COMPOSITION',source_identity=source.source_identity,cases=pairs,
   full_Pi_closed=False,physical_payload_executed=False,selected_kappa_changed=False)
if __name__=='__main__':
 result=audit()
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 else:need(result==json.loads((HERE/'RESULT.json').read_text()),'exact complete receipt')
 print(result['status'])
