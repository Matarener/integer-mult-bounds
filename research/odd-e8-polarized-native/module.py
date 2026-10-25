#!/usr/bin/env python3
"""One 512x512 H_ab block: emitted 25D paths and exact owned lifecycle.

This is a typed local side-map module, not an entire Gaussian-job caller.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter,defaultdict
import argparse,gzip,importlib.util,json,signal,sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def canonical(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:p[x.bit_length()-1]=x
 for j in sorted(p):
  for k in p:
   if k!=j and p[k]>>j&1:p[k]^=p[j]
 return tuple(p[j]for j in sorted(p,reverse=True))
def calculate():
 base=load('rectangle_single',HERE/'check.py');tools=load('rectangle_frames',HERE/'frame_tools.py')
 for name,digest in base.PINS.items():need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==digest,'source pin '+name)
 normal=json.loads((HERE/'inputs/NORMALIZERS.json').read_text());payload=json.loads(gzip.decompress((HERE/'inputs/POLARIZED-CHANNELS.json.gz').read_bytes()));channels=payload['channels']
 labels=[p['q']for p in normal['ports']];n=25
 U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j))for b in range(3)for j in range(1,9)]
 orthogonal=base.ortho_basis(U)
 def qlabel(port):
  a=port//112**2;b=port//112%112;c=port%112;x=labels[a]|(labels[b]<<9)|(labels[c]<<18)
  need(base.span_contains(U,x),'literal actual port in U25')
  return sum(base.dot(x,v)<<j for j,v in enumerate(orthogonal))
 ce=load('rectangle_module_clifford',HERE/'inputs/clifford_exact.py');peak=[1];sparse,monomial=tools.install(ce,need,peak)
 def grank(op):return ce.rank([x for x,z,p in op.tab[n:]])
 definitions={}
 def word_id(word):
  word=json.loads(json.dumps(word));raw=json.dumps(word,separators=(',',':')).encode();key=sha256(raw).hexdigest();definitions.setdefault(key,word);return key
 def prefix_only(word):need(all(e[0]in('P','D','X','phase')for e in word),'Gaussian hidden in a monomial wrapper')
 def path(prefix,axes,post,expected):
  prefix_only(prefix);prefix_only(post);op=ce.ident(n)
  for part in [literal(prefix),ce.fourier(n,axes),literal(post)]:op=op.then(part)
  need(op.tab==expected.tab and grank(op)==len(axes),'paid path exact signed tableau and stated Fourier width: equal='+str(op.tab==expected.tab)+' actual_rank='+str(grank(op))+' child='+str(len(axes)))
  return {'before_monomial':word_id(prefix),'child_axes':list(axes),'rank':len(axes),'after_monomial':word_id(post),'phase_proof':'Every low-rank gauge compiled by absolute sparse zero-column; native full conjugates use the proved exact anchor formula; all other factors cancel as literal inverse words.'}
 def literal(word):
  out=ce.ident(n)
  for e in word:
   if e[0]=='P':a=ce.perm(n,e[1])
   elif e[0]=='D':a=ce.diag(n,e[1],e[2])
   elif e[0]=='X':a=ce.xgate(n,e[1])
   elif e[0]=='phase':a=ce.Op(n,ce.identity(n),[tuple(e)])
   else:need(e[0]=='C','literal Clifford word');a=ce.cgate(n,e[1],e[2])
   out=out.then(a)
  return out
 groups={};port_source_group={};port_reader_group={}
 for ci,ch in enumerate(channels):
  S=canonical(qlabel(p)for p,a,b in ch['source']);R=canonical(qlabel(p)for p,a,b in ch['reader']);key=(S,R)
  need(len(S)==len(R)==8 and all(not base.dot(a,b)for a in S for b in R),'orthogonal8+8 rectangle')
  g=groups.setdefault(key,{'S':S,'R':R,'channels':[],'source':set(),'reader':set()});g['channels'].append(ci)
  for name,lookup in [('source',port_source_group),('reader',port_reader_group)]:
   for p,a,b in ch[name]:
    need(p not in lookup or lookup[p]==key,'each actual field has one coframe group')
    lookup[p]=key;g[name].add(p)
 need(len(groups)==4 and len(port_source_group)==len(port_reader_group)==512,'four groups cover512+512 fields')
 need(not(set(port_source_group)&set(port_reader_group)),'source/reader originals disjoint')
 allfields=sorted(set(port_source_group)|set(port_reader_group));rows={p:{p:F(1)}for p in allfields};rows['C0']={};charts={p:('line:'+str(qlabel(p))if p in port_source_group else'ground')for p in allfields};charts['C0']='ground'
 expected={p:{p:F(1)}for p in allfields};expected['C0']={}
 for ch in channels:
  for r,a,b in ch['reader']:
   for s,c,d in ch['source']:base.add(expected[r],{s:F(1)},F(a,b)*F(c,d))
 paid=Counter();ordinary=Counter();program=[];group_records=[];anchors=[];source_entry_paths={};source_entry_frames={};reader_exit_paths={};common_paths={};endpoint_frames={};first_phase_reference=None;first_channel_program=None;frame_mutation_rank=None
 Rfull=ce.fourier(n)
 def apply_path(field,target,record):
  program.append(['PAID_PATH',field,charts[field],target,record]);paid[record['rank']]+=1
  for key in ['before_monomial','after_monomial']:
   ordinary.update(e[0]for e in definitions[record[key]])
  charts[field]=target
 def execute_ADD(values,where,dst,src,q):
  need(where[dst]==where[src],'actual scalar COPY/read charts equal');base.add(values[dst],values[src],q)
 def scalar(dst,src,q):
  execute_ADD(rows,charts,dst,src,q);program.append(['ADD',dst,src,q.numerator,q.denominator,charts[dst]]);ordinary['ADD']+=1
 for gi,(key,g)in enumerate(sorted(groups.items())):
  S=list(g['S']);D=base.radical(S);need(len(D)==6 and all(base.span_contains(list(g['R']),v)for v in D),'shared radical6 retained')
  need(len(g['channels'])==16 and len(g['source'])==len(g['reader'])==128,'16channels/128+128 fields per group')
  Phi=ce.canonical_frame(n,S);chart='S8:'+str(gi);fullcols=ce.basis_extend(S,n);K=tools.native_K(ce,fullcols)
  if frame_mutation_rank is None:frame_mutation_rank=grank(Phi.adjoint().then(ce.canonical_frame(n,list(g['R']))));need(frame_mutation_rank>0,'wrong reader R8 frame cannot be an ordinary S8 ADD')
  need(K.adjoint().then(ce.fourier(n,range(8))).then(K).tab==Phi.tab,'canonical source coframe construction')
  T,anchor=tools.native_full_conjugate(ce,need,monomial,fullcols);anchors.append(anchor)
  full_exit=path(K.adjoint().circuit,range(8,n),T.circuit,Phi.adjoint().then(Rfull))
  reader_entry=path(K.adjoint().circuit,range(8),K.circuit,Phi)
  common_paths[str(gi)]={'reader_ground_to_S8':reader_entry,'source_S8_to_full25':full_exit,'S8_frame':word_id(Phi.circuit),'S8_basis25':S,'shared_radical6_basis25':D}
  # Input source line is the actual canonical line frame. Its own service
  # precedes the gather, and every reader's own service remains after it.
  for p in sorted(g['source']):
   q=qlabel(p);qframe=ce.canonical_frame(n,[q]);cols=ce.basis_extend(list(canonical([q]+S)),n)
   # Preserve q as the first flag vector, then fill the remaining S basis.
   flag=[q]
   for v in S:
    if len(base.basis(flag+[v]))>len(flag):flag.append(v)
   need(len(flag)==8,'source q nested inS8');cols=ce.basis_extend(flag,n);Ks=tools.native_K(ce,cols)
   small=tools.flag_frame(ce,cols,1);wide=tools.flag_frame(ce,cols,8)
   before=monomial(qframe.adjoint().then(small));after=monomial(wide.adjoint().then(Phi))
   record=path(before.circuit+Ks.adjoint().circuit,range(1,8),Ks.circuit+after.circuit,qframe.adjoint().then(Phi))
   if first_phase_reference is None:
    reference=literal(definitions[record['before_monomial']]).then(ce.fourier(n,record['child_axes'])).then(literal(definitions[record['after_monomial']]))
    wrong=reference.then(ce.Op(n,ce.identity(n),[('phase',1)]));need(wrong.tab==reference.tab and sparse(wrong)!=sparse(reference),'actual phase mutation rejected despite equal signed tableau')
    first_phase_reference={'same_signed_tableau':True,'absolute_column_differs':True,'mutant':'append physical global phase i to a source H7 path'}
   source_entry_frames[str(p)]={'q25':q,'literal_frame_word':word_id(qframe.circuit)}
   source_entry_paths[str(p)]=record;apply_path(p,chart,record)
  for p in sorted(g['reader']):apply_path(p,chart,reader_entry)
  need(not rows['C0']and charts['C0']=='ground','owned zero birth at original chart');program.append(['ZERO_RETAG','C0','ground',chart]);ordinary['ZERO_RETAG']+=1;charts['C0']=chart
  for ci in g['channels']:
   ch=channels[ci]
   start=len(program)
   for p,a,b in ch['source']:scalar('C0',p,F(a,b))
   for p,a,b in ch['reader']:scalar(p,'C0',F(a,b))
   for p,a,b in ch['source']:scalar('C0',p,-F(a,b))
   need(not rows['C0'],'owned cache exactly zero after each actual channel')
   if first_channel_program is None:first_channel_program=program[start:]
  program.append(['CLEAR_ZERO','C0',chart]);ordinary['CLEAR_ZERO']+=1
  program.append(['ZERO_RETAG','C0',chart,'ground']);ordinary['ZERO_RETAG']+=1;charts['C0']='ground'
  for p in sorted(g['source']):apply_path(p,'full25',full_exit)
  for p in sorted(g['reader']):
   q=qlabel(p);V=list(S)
   for v in ce.nullspace((q,),n):
    if len(base.basis(V+[v]))>len(V):V.append(v)
   need(len(V)==24 and all(not base.dot(q,v)for v in V),'actual qperp24 flag contains sourceS8')
   cols=ce.basis_extend(V,n);Kv=tools.native_K(ce,cols);low=tools.flag_frame(ce,cols,8);target=tools.flag_frame(ce,cols,24)
   before=monomial(Phi.adjoint().then(low));record=path(before.circuit+Kv.adjoint().circuit,range(8,24),Kv.circuit,Phi.adjoint().then(target))
   reader_exit_paths[str(p)]=record;endpoint_frames[str(p)]={'q25':q,'qperp24_basis25':V,'literal_frame_word':word_id(target.circuit)};apply_path(p,'qperp24:'+str(p),record)
  group_records.append({'group':gi,'channels':g['channels'],'source_ports':sorted(g['source']),'reader_ports':sorted(g['reader']),'S8_basis25':S,'R8_basis25':list(g['R']),'common_radical6_basis25':D})
 need(rows==expected,'all1024 independent input columns: exact H_ab logical side map and owned return')
 need(charts['C0']=='ground'and all(charts[p]=='full25'for p in port_source_group)and all(charts[p]=='qperp24:'+str(p)for p in port_reader_group),'full typed endpoints and exact owned chart restoration')
 need(paid=={7:512,8:512,16:512,17:512},'literal complete Gaussian histogram')
 need(ordinary['ADD']==13056 and ordinary['ZERO_RETAG']==8 and ordinary['CLEAR_ZERO']==4,'complete gather lifecycle counts')
 def replay_kernel(seq):
  values={p:{p:F(1)}for p in allfields};values['C0']={};where={p:'sameS8'for p in values}
  for kind,dst,src,a,b,chart in seq:need(kind=='ADD','kernel primitive');execute_ADD(values,where,dst,src,F(a,b))
  return values
 need(not replay_kernel(first_channel_program)['C0'],'actual complete kernel replay clears cache')
 need(bool(replay_kernel(first_channel_program[:-1])['C0']),'actual omitted-uncompute program leaves nonzero cache')
 mutation_results={'phase':first_phase_reference,'frame':{'mutant':'replace common source S8 chart by the distinct reader R8 chart','Gaussian_transport_rank':frame_mutation_rank,'ordinary_transport_rejected':True},'cleanup':{'mutant':'delete final source-uncompute ADD in emitted first channel','actual_interpreter_replay_nonzero_owned_residual':True}}
 scalar_endpoints={'source_identity_fields':sorted(port_source_group),'reader_rows':{str(p):[[s,q.numerator,q.denominator]for s,q in sorted(rows[p].items())]for p in sorted(port_reader_group)},'owned_C0':[]}
 payload_out={'schema':'polarized-Hab-25D-emitted-program/v1','axis_dimension':25,'orthonormal_basis_in_raw27':orthogonal,'groups':group_records,'field_roles':{str(p):['X'if p in port_source_group else'Y',p]for p in allfields},'monomial_and_frame_definitions':definitions,'common_paths':common_paths,'source_entry_paths':source_entry_paths,'source_entry_frames':source_entry_frames,'reader_exit_paths':reader_exit_paths,'reader_endpoint_frames':endpoint_frames,'native_full_conjugate_anchors':anchors,'program':program,'logical_endpoint_rows':scalar_endpoints}
 canonical_payload=(json.dumps(payload_out,sort_keys=True,separators=(',',':'))+'\n').encode();encoded=gzip.compress(canonical_payload,mtime=0)
 summary={'schema':'polarized-Hab-25D-physical-module/v1','status':'PASS_EXACT_TYPED_LOCAL_SIDE_MODULE_NOT_COMPLETE_CALLER','axis_dimension':25,'source_pins':base.PINS,'source_fields':512,'reader_fields':512,'channels':64,'coframe_groups':4,'channels_per_group':16,'source_fields_per_group':128,'reader_fields_per_group':128,
  'paid_profile':dict(sorted(paid.items())),'ordinary_literal_gate_histogram':dict(sorted(ordinary.items())),'owned_zero_cells':1,'independent_helper_inputs':0,'independent_COPY_operations':0,'all_original_inputs_kept':1024,
  'entry_contract':{'sources':'x_s arbitrary independent, physically canonical Phi_[q_s] x_s at its actual line chart','readers':'y_r arbitrary independent, physical ground chart','owned_C0':'zero at ground chart; no independent original input or productive target is assigned'},
  'exit_contract':{'sources':'canonical R25 x_s, original x_s unchanged','readers':'explicit ordered-flag Phi_(q_r^perp)(y_r + sum_s H_ab[r,s] x_s), target frame literal word supplied separately for every reader','owned_C0':'exact zero at original ground chart','H_ab':'The exact sum of all64 polarized channel columns times rows from the pinned geometry; no current-value renaming.'},
  'phase_contract':{'native_full_conjugation':'Exact signed tableau plus proved analytic zero-column phase; independently corroborated by root small-n dense tests.','other_monomial_gauges':'Exact low-rank sparse Gaussian-integer zero-column evaluation.','all_positive_widths':'Each literal one-copy Clifford equality includes absolute phase and tensor-lifts columnwise; scalar ADD identities hold for every address width.','phase_opcode_lift':'A one-copy phase theta acts as scalar i^(f theta) at width f.','sparse_peak_support':peak[0]},
  'program_payload_sha256':sha256(canonical_payload).hexdigest(),'proof_relevant_digest':sha256(canonical_payload).hexdigest(),'environment_metadata':{'program_container_sha256':sha256(encoded).hexdigest(),'program_container_bytes':len(encoded)},'additional_408_helper_banks':0,'additional_helper_target_credit':{},
  'mutation_controls':mutation_results,'compilation_coverage':{'unique_source_entry_paths':512,'unique_reader_exit_paths':512,'common_source_exit_paths':4,'common_reader_entry_paths':4,'paid_path_applications':2048,'low_rank_monomial_gauges_with_exact_absolute_phase':1536,'native_full_conjugates_with_proved_analytic_absolute_phase':4,'phase_complete_by_literal_composition':True},
  'limits':'Local H_ab side primitive only. No K-core shared chronology, reciprocal block schedule, full nonlinear caller, autonomous reader Gaussian targets, precision/storage allowance, whole-caller moment or kappa is claimed. Source input line services are provided inputs of this ABI and must be paid once by any complete caller. The eight-dimensional main prefixes and every endpoint path are explicitly charged; pairing rank zero is not used as a Gaussian-copy tariff.',
  'new_kappa':False,'global_caller_emitted':False}
 return json.loads(json.dumps(summary)),encoded,canonical_payload
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('60s module bound')));signal.setitimer(signal.ITIMER_REAL,60)
 result,program,canonical_payload=calculate();signal.setitimer(signal.ITIMER_REAL,0)
 if args.write:(HERE/'MODULE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');(HERE/'PROGRAM.json.gz').write_bytes(program)
 else:
  stored=json.loads((HERE/'MODULE.json').read_text());stored.pop('environment_metadata',None);science=dict(result);science.pop('environment_metadata',None)
  actual=json.loads(gzip.decompress((HERE/'PROGRAM.json.gz').read_bytes()));actual_payload=(json.dumps(actual,sort_keys=True,separators=(',',':'))+'\n').encode()
  need(stored==science and actual_payload==canonical_payload,'frozen scientific module and canonical decompressed program; container bytes are environment metadata')
 print(json.dumps({k:result[k]for k in ['status','source_fields','reader_fields','paid_profile','ordinary_literal_gate_histogram','program_payload_sha256','new_kappa']},sort_keys=True))
if __name__=='__main__':main()
