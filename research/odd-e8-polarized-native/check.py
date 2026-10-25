#!/usr/bin/env python3
"""One polarized rectangle: exact common-frame ABI, not a global producer."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from collections import Counter
import argparse,gzip,importlib.util,json,signal,sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
PINS={'NORMALIZERS.json':'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da',
 'POLARIZED-CHANNELS.json.gz':'7304d5d328d5c0b1610755706862f554f7b4c9cf39a09e6d58462e202b38badc',
 'clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def dot(a,b):return(a&b).bit_count()&1
def basis(rows):
 p={}
 for x in rows:
  while x:
   j=x.bit_length()-1
   if j in p:x^=p[j]
   else:p[j]=x;break
 return list(p.values())
def span_contains(B,x):return len(basis(B+[x]))==len(B)
def radical(B):
 values=[]
 for mask in range(1<<len(B)):
  x=0
  for i,b in enumerate(B):
   if mask>>i&1:x^=b
  if all(not dot(x,b)for b in B):values.append(x)
 return basis(values)
def ortho_basis(B):
 out=[];current=basis(B)
 while current:
  odd=[x for x in current if dot(x,x)]
  need(odd,'standard nonalternating residual')
  candidates=odd+[odd[0]^x for x in current if not dot(x,x)]
  for v in candidates:
   if not v or not dot(v,v):continue
   nxt=basis([x^(v if dot(v,x)else 0)for x in current])
   if len(nxt)!=len(current)-1:continue
   if nxt and not any(dot(x,x)for x in nxt):continue
   break
  else:raise ValueError('orthonormal basis candidate')
  out.append(v);current=nxt
 need(all(dot(a,b)==int(i==j)for i,a in enumerate(out)for j,b in enumerate(out)),'actual orthonormal isometry')
 return out
def add(dst,src,q):
 for k,v in src.items():
  x=dst.get(k,F(0))+q*v
  if x:dst[k]=x
  else:dst.pop(k,None)

def calculate():
 for name,digest in PINS.items():need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==digest,'pin '+name)
 data=json.loads((HERE/'inputs/NORMALIZERS.json').read_text());allchannels=json.loads(gzip.decompress((HERE/'inputs/POLARIZED-CHANNELS.json.gz').read_bytes()))
 channel=allchannels['channels'][0]
 labels=[p['q']for p in data['ports']]
 def raw_label(port):
  a=port//112**2;b=port//112%112;c=port%112
  return labels[a]|(labels[b]<<9)|(labels[c]<<18)
 # Explicit nondegenerate 25-space of equal three-block parities.
 U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j))for b in range(3)for j in range(1,9)]
 orthogonal=ortho_basis(U);need(len(orthogonal)==25,'dimension25 physical realization')
 def physical_label(port):
  x=raw_label(port);need(span_contains(U,x),'literal label in original direct-sum space')
  y=sum(dot(x,b)<<i for i,b in enumerate(orthogonal));back=0
  for i,b in enumerate(orthogonal):
   if y>>i&1:back^=b
  need(back==x,'isometry inverse on actual literal port')
  return y
 src=[(port,F(a,b),physical_label(port))for port,a,b in channel['source']]
 read=[(port,F(a,b),physical_label(port))for port,a,b in channel['reader']]
 need(len(src)==len(read)==68 and not(set(x[0]for x in src)&set(x[0]for x in read)),'68+68 disjoint actual ports')
 S=basis(x[2]for x in src);R=basis(x[2]for x in read);D=radical(S)
 need(len(S)==len(R)==8 and len(D)==6,'source8 reader8 common radical6')
 need(len(radical(R))==6 and len(basis(D+radical(R)))==6,'same radical on both sides')
 need(all(not dot(x,y)for x in S for y in R),'entire source/reader spans are orthogonal')
 need(len(basis(S+R))==10 and len(radical(basis(S+R)))==6,'joint10 with radical6')
 need(all(dot(q,q)and not span_contains(S,q)for _,_,q in read),'reader own line not in source prefix')
 need(all(dot(q,q)and span_contains(S,q)for _,_,q in src),'source own lines in source prefix')
 spec=importlib.util.spec_from_file_location('rectangle_clifford',HERE/'inputs/clifford_exact.py');ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
 phase_peak=[1]
 def sparse_zero(op,basis_state=0):
  vec={basis_state:(1,0)};den=0
  for e in op.circuit:
   kind=e[0]
   if kind=='P':vec={ce.mv(e[1],x):v for x,v in vec.items()}
   elif kind=='X':vec={x^e[1]:v for x,v in vec.items()}
   elif kind=='D':vec={x:ce.mul_i(v,ce.qvalue(e[1],e[2],x,op.n))for x,v in vec.items()}
   elif kind=='phase':vec={x:ce.mul_i(v,e[1])for x,v in vec.items()}
   else:
    need(kind=='C','literal phase evaluator gate')
    q,sgn=e[1:];new={}
    for x in set(vec)|{x^q for x in vec}:
     a,b=vec.get(x,(0,0));c,d=vec.get(x^q,(0,0));v=(a-sgn*b+c+sgn*d,b+sgn*a+d-sgn*c)
     if v!=(0,0):new[x]=v
    vec=new;den+=1
   phase_peak[0]=max(phase_peak[0],len(vec));need(len(vec)<=(1<<18),'bounded sparse phase support')
   while den and all(not(a&1)and not(b&1)for a,b in vec.values()):vec={x:(a//2,b//2)for x,(a,b)in vec.items()};den-=1
  return vec,den
 ce.Op.zero_state=sparse_zero
 def exact_monomial(op):
  n=op.n;T=op.tab;need(all(x==0 and p%2==0 for x,z,p in T[n:]),'actual monomial signed tableau')
  G=ce.transpose([x for x,z,p in T[:n]],n);b=ce.mv(G,sum((p//2)<<i for i,(x,z,p)in enumerate(T[n:])))
  gt=ce.transpose(G,n);Q=ce.transpose([ce.mv(gt,z)for x,z,p in T[:n]],n);alpha=[(p-2*dot(b,z))%4 for x,z,p in T[:n]]
  out=ce.diag(n,Q,alpha).then(ce.perm(n,G)).then(ce.xgate(n,b));vec,den=sparse_zero(op)
  need(den==0 and set(vec)=={b},'actual monomial zero column')
  phase=[(1,0),(0,1),(-1,0),(0,-1)].index(vec[b]);out=out.then(ce.Op(n,ce.identity(n),[('phase',phase)]))
  need(out.tab==op.tab and sparse_zero(out)==sparse_zero(op),'exact monomial including absolute phase')
  return out,{'matrix_rows':G,'offset':b,'quadratic_rows':Q,'linear_Z4':alpha,'phase':phase}
 ce.monomial=exact_monomial
 def grank(op):return ce.rank([x for x,z,p in op.tab[25:]])
 frames={'D6':ce.canonical_frame(25,D),'S8':ce.canonical_frame(25,S)}
 two=frames['D6'].adjoint().then(frames['S8']);recipe,compiled=ce.lower_child(two)
 need(recipe['rank']==grank(two)==2 and compiled.tab==two.tab and sparse_zero(compiled)==sparse_zero(two),'actual H2 transition with exact phase')
 # This signed-tableau census is discovery/corroboration of all actual flags;
 # literal phase factorization is retained for the common H2 edge and examples.
 source_ranks=Counter();reader_ranks=Counter()
 for _,_,q in src:source_ranks[grank(ce.canonical_frame(25,[q]).adjoint().then(frames['S8']))]+=1
 for _,_,q in read:reader_ranks[grank(frames['S8'].adjoint().then(ce.canonical_frame(25,basis(S+[q]))))]+=1
 need(source_ranks=={7:68}and reader_ranks=={1:68},'literal actual source/reader nested flag rank census')
 # Full common-frame row protocol, all 137 original columns independently kept.
 index={port:i for i,(port,_,_)in enumerate(src+read)};cache=136
 def scalar_protocol(dirty,broken=None):
  rows=[{i:F(1)}for i in range(137)];ops=[]
  if not dirty:rows[cache]={}
  def emit(dst,source,q):
   add(rows[dst],rows[source],q);ops.append(['ADD',dst,source,str(q),'S8'])
  if dirty and broken!='omit_dirty_subtraction':
   for port,a,q in read:emit(index[port],cache,-a)
  for port,b,q in src:emit(cache,index[port],b)
  for port,a,q in read:emit(index[port],cache,a)
  if broken!='omit_source_uncompute':
   for port,b,q in src:emit(cache,index[port],-b)
  expected=[{i:F(1)}for i in range(137)]
  if not dirty:expected[cache]={}
  for port,a,q in read:
   for source,b,_ in src:add(expected[index[port]],{index[source]:F(1)},a*b)
  return rows==expected,ops,rows
 ok,dirty_program,_=scalar_protocol(True);need(ok,'all independent originals and dirty cache returned')
 ok,zero_adds,_=scalar_protocol(False);need(ok,'owned zero cache exactly uncomputed')
 need(not scalar_protocol(True,'omit_dirty_subtraction')[0]and not scalar_protocol(False,'omit_source_uncompute')[0],'meaningful dirty/cleanup controls')
 owned_program=[['ZERO_RETAG','C0','ground','S8']]+zero_adds+[['CLEAR_ZERO','C0','S8'],['ZERO_RETAG','C0','S8','ground']]
 def frame_receipt(op):
  return {'literal_word':op.circuit,'signed_tableau_sha256':sha256(json.dumps(op.tab,separators=(',',':')).encode()).hexdigest()}
 out={'schema':'polarized-rectangle-one-channel-physical-abi/v1','status':'PASS_CONDITIONAL_COFRAMED_LOCAL_ABI_NOT_GLOBAL_CALLER',
  'source_pins':PINS,'geometry_channel':{'direction':allchannels['direction'],'polarization':channel['polarization'],'half_selector':channel['half_selector'],'source':channel['source'],'reader':channel['reader']},
  'physical_25_axis_realization':{'orthonormal_basis_in_raw27':orthogonal,'map':'q25_j = dot(raw27, orthonormal_basis_j)','dimension':25},
  'subspaces':{'source_basis_25':S,'reader_basis_25':R,'common_radical_basis_25':D,'source_dimension':8,'reader_dimension':8,'shared_radical_dimension':6,'cross_pairing_rank':0,'joint_dimension':10},
  'canonical_frames':{name:frame_receipt(op)for name,op in frames.items()},
  'common_H2_edge':{'input':'D6','output':'S8','physical_operator':'Phi_S8 Phi_D6^-1','literal_word':two.circuit,'exact_compiler_recipe':recipe,'compiled_word':compiled.circuit,'signed_tableau_and_absolute_zero_column_equal':True,'all_width':'Exact one-copy Clifford identity with absolute phase tensor-lifts columnwise; no width-one matrix-sum relation.'},
  'actual_flag_rank_census':{'source_line_to_S8':dict(source_ranks),'S8_to_reader_line_plus_S8':dict(reader_ranks),'scope':'All signed tableaux tested; common H2 transition has explicit exact phase compilation. No global main path emitted.'},
  'scalar_kernel':{'typed_entry':'68 source+68 reader fields already in identical physical canonical S8 chart; their logical originals independent','typed_exit':'source values unchanged; reader_r += a_r sum_s b_s source_s, all in S8; borrowed dirty cache returns its original z in S8','dirty_program':dirty_program,'dirty_ADDs':len(dirty_program),'owned_zero_program':owned_program,'owned_zero_ADDs':len(zero_adds),'owned_zero_CLEARs':1,'owned_zero_zero_retags':2,'all_original_columns_checked':137,'uncompensated_dirty_input_rejected':True,'nonzero_cleanup_rejected':True},
  'invoice_contract':{'additional_Gaussians_inside_coframed_kernel':{},'additional_helper_targets':{},'independent_COPYs':0,'owned_zero_slots':1,'dirty_borrowed_slot_initial_and_final_chart':'S8 (not newly available for free)','if_D6_main_prefix_already_paid':'D6->S8 is one H2 per participating field, not one H2 per complete channel','if_D6_not_present':'The six radical directions remain a genuine Gaussian prefix cost; no H2-only acquisition from ground is claimed. Ground->S8 has rank8.','main_prefix_and_termination':'Every main field must actually reach S8 at the same cut, after each source own-line service and before each reader own-line service; global schedule, transitions, productive targets and complete invoice remain unproved.','dirty_slot_from_ground':'If an independent dirty original z starts and must return at ground, acquiring and undoing its S8 chart requires separately priced transport; the kernel does not fund it. Use the zero-owned variant to avoid that assumption.'},
  'phase_evaluation':{'method':'Fresh sparse exact Gaussian-integer column evaluator for the pinned Clifford compiler; equality of signed tableau and one absolute column fixes global phase.','peak_nonzero_column_support':phase_peak[0],'field_width':'Every positive f under inherited columnwise tensor semantics.'},
  'complete_gaussian_job_targets_claimed':False,'global_flag_compatibility_proved':False,'new_kappa':False}
 return json.loads(json.dumps(out))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('60s one-channel bound')));signal.setitimer(signal.ITIMER_REAL,60)
 out=calculate();signal.setitimer(signal.ITIMER_REAL,0);p=HERE/'RESULT.json'
 if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(p.read_text())==out,'frozen local ABI receipt')
 print(json.dumps({'status':out['status'],'source_ports':68,'reader_ports':68,'source_frame_rank':8,'shared_radical_rank':6,'conditional_edge_rank':2,'dirty_ADDs':out['scalar_kernel']['dirty_ADDs'],'owned_zero_ADDs':out['scalar_kernel']['owned_zero_ADDs'],'owned_zero_retags':2,'new_kappa':False},sort_keys=True))
if __name__=='__main__':main()
