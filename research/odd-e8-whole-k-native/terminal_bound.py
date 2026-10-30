"""Actual coefficient/phase audit of the distinct-fresh terminal path lemma.

This is a scoped tensor-path support bound, not a complete-caller no-go.
It checks both central-line orbits of one actual eight-root cube. The
proof extends to the whole K cube from the same orthogonality premise.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from itertools import product
import argparse,gzip,importlib.util,json,sys
from hashlib import sha256
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def need(ok,why):
 if not ok:raise ValueError(why)
def dot(a,b):return(a&b).bit_count()&1
def mvcols(cols,x):
 out=0
 while x:
  bit=x&-x;out^=cols[bit.bit_length()-1];x^=bit
 return out
def transpose(cols):return [sum(((col>>j)&1)<<i for i,col in enumerate(cols))for j in range(len(cols))]
def sparse(word,n,basis):
 values={basis:(1,0)};den=0
 for e in word:
  k=e[0]
  if k=='P':values={sum(dot(row,x)<<j for j,row in enumerate(e[1])):v for x,v in values.items()}
  elif k=='Z':values={x:((-a,-b)if dot(e[1],x)else(a,b))for x,(a,b)in values.items()}
  elif k=='phase':values={x:[(a,b),(-b,a),(-a,-b),(b,-a)][e[1]%4]for x,(a,b)in values.items()}
  else:
   need(k=='C','known sparse primitive');q,sgn=e[1:];out={}
   for x in values.keys()|{x^q for x in values}:
    a,b=values.get(x,(0,0));c,d=values.get(x^q,(0,0));v=(a-sgn*b+c+sgn*d,b+sgn*a+d-sgn*c)
    if v!=(0,0):out[x]=v
   values=out;den+=1
  while den and all(not(a&1)and not(b&1)for a,b in values.values()):den-=1;values={x:(a//2,b//2)for x,(a,b)in values.items()}
 return values,den
def calculate():
 for name,pin in {'NORMALIZERS.json':'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da','clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'}.items():
  need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==pin,'exact input pin '+name)
 normal=json.loads((HERE/'inputs/NORMALIZERS.json').read_bytes());roots=list(zip(*normal['mode_columns']))
 ports=[i for i,r in enumerate(roots)if tuple(j for j,v in enumerate(r)if v)==(0,1,2,3)]
 rawq=[normal['ports'][p]['q']for p in ports]
 W=[[2*int(i==j)-sum(a*b for a,b in zip(roots[ports[i]],roots[ports[j]]))//2 for j in range(8)]for i in range(8)]
 spec=importlib.util.spec_from_file_location('path_term_clifford',HERE/'inputs/clifford_exact.py');ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
 records=[];dense_checks=0;tableau_checks=0;all_paths=[]
 for central in [52,199]:
  need(central!=(1<<9)-1 and dot(central,central)==1 and all(not dot(central,q)for q in rawq),'both central orbits have exact premises')
  def tv(v):return tuple((1<<j)^(v if v>>j&1 else 0)for j in range(9))
  if not central&1:G=tv(central^1)
  else:
   j=next(j for j in range(1,9)if not central>>j&1);A=tv((1<<j)^central);B=tv((1<<j)^1)
   G=tuple(sum(dot(row,col)<<k for k,col in enumerate(ce.transpose(B,9)))for row in A)
  need(ce.mv(G,1)==central,'exact chosen central embedding')
  qs=[ce.mv(ce.transpose(G,9),q)for q in rawq]
  need(all(not q&1 and dot(q,q)==1 for q in qs),'new q0-zero normone labels')
  need(all(not W[i][j]or not dot(qs[i],qs[j])for i,j in product(range(8),repeat=2)),'every actual K edge orthogonal')
  vectors=[1^q for q in qs];eps=[((v.bit_count()//2)-1)&1 for v in vectors]
  for L in [1,2,3]:
   n=1+8*L;Q=ce.fourier(n,[0]);D=ce.fourier(n,range(1,n));R=ce.fourier(n)
   paths=[]
   def extend(stage,owner,initial,cols,h,coefficient,owners):
    if stage==L:paths.append((initial,owner,cols,h,coefficient,owners));return
    for target in range(8):
     if not W[target][owner]:continue
     newcols=list(cols);newh=h
     # M_target,owner=L_target L_owner; each L is involutive.
     for p in [owner,target]:
      v=1|((qs[p]>>1)<<(1+8*stage));epsilon=eps[p]
      for j,col in enumerate(newcols):
       if dot(v,col):newcols[j]^=v;newh^=(epsilon<<j)
     extend(stage+1,target,initial,newcols,newh,coefficient*F(W[target][owner],2),owners+[target])
   for initial in range(8):extend(0,initial,initial,[1<<j for j in range(n)],0,F(1),[initial])
   need(len(paths)==8*4**L,'every literal nonzero K path enumerated')
   coefficient_hist=Counter();seen_v=set();explicit=[]
   for initial,owner,cols,h,c,owners in paths:
    v=cols[0];epsilon=h&1
    expected_v=(qs[initial]>>1)<<1
    need(v==expected_v and not v&1 and dot(v,v)==1 and epsilon==eps[initial],'actual composed path pure-first-fresh Pauli image and absolute sign')
    # Every path M fixes zero and is P_G Z_h, with the scalar K product
    # c outside its tensor lift. No c^f occurs anywhere.
    rows=transpose(cols);M=ce.diag(n,(0,)*n,tuple(2*((h>>j)&1)for j in range(n))).then(ce.perm(n,rows))
    actual=D.then(M).then(Q.adjoint())
    inverse_line=ce.cgate(n,v,1 if epsilon else -1)
    phase=(-epsilon)%4
    rewritten=M.then(inverse_line).then(Q.adjoint()).then(R).then(ce.Op(n,ce.identity(n),[('phase',phase)]))
    need(actual.tab==rewritten.tab,'actual coefficient path signed Clifford equality')
    need(ce.rank([x for x,z,p in actual.tab[n:]])==n-2,'actual per-path terminal Gaussian rank n-2')
    need(M.then(R).tab==R.then(M).tab,'path full-Gaussian signed centralization')
    tableau_checks+=1;coefficient_hist[str(c)]+=1;seen_v.add((v,epsilon))
    explicit.append({'owners':owners,'coefficient':[c.numerator,c.denominator],'G_columns':cols,'Z_before_permutation':h,'terminal_removed_directions':[1,v],'inverse_line_sign':1 if epsilon else -1,'one_copy_scalar_phase':phase})
    if L==1:
     mword=[['Z',h],['P',rows]]
     original=[['C',1<<j,1]for j in range(1,n)]+mword+[['C',1,-1]]
     alternate=mword+[['C',v,1 if epsilon else -1],['C',1,-1]]+[['C',1<<j,1]for j in range(n)]+[['phase',phase]]
     for basis in [0,1,345]:
      need(sparse(original,n,basis)==sparse(alternate,n,basis),'actual path absolute phase sparse column')
      dense_checks+=1
   records.append({'central_original9':central,'distinct_fresh_stages':L,'n':n,'d':n-1,'all_nonzero_paths':len(paths),'actual_coefficient_histogram':dict(coefficient_hist),'distinct_signed_first_fresh_vectors':len(seen_v),'per_term_terminal_rank':n-2})
   all_paths.append({'central_original9':central,'stages':L,'paths':explicit})
 # Bind the generic premise to the committed 512-port word, without
 # importing its generator or replaying its complete native suite.
 program_raw=gzip.decompress((HERE/'K-PROGRAM.json.gz').read_bytes())
 need(sha256(program_raw).hexdigest()=='98941b295d428462b82dae52a369de97dcbf5be1dd7a369f6c495cda5fc6ac8a','committed scientific K payload')
 program=json.loads(program_raw);n=program['axis_dimension'];need(n==25,'published root ambient')
 frames=program['entry_frames'];edge_count=0;images=set();normalizer_coefficients=0
 for owner,frame in frames.items():
  rec=frame['normalizer_proof'];G=rec['G_rows'];z=rec['Z_after_permutation'];columns=transpose(G)
  need(columns[0]==frame['q25'],'published source line normalizer')
  need(all(dot(a,b)==int(i==j)for i,a in enumerate(columns)for j,b in enumerate(columns)),'published orthogonal normalizer')
  for col in columns:
   need((col.bit_count()-1-2*dot(z,col))%4==0,'published absolute R-centralizing sign')
   normalizer_coefficients+=1
 for reader,entries in program['literal_scalar_K_rows'].items():
  r=frames[reader];inverse_rows=transpose(r['normalizer_proof']['G_rows'])
  for source,num,den in entries:
   need(num!=0 and den>0,'nonzero literal dyadic edge')
   q=frames[str(source)]['q25'];v=sum(dot(row,q)<<j for j,row in enumerate(inverse_rows))
   need(not v&1 and dot(v,v)==1,'every published K edge has pure-fresh central image')
   images.add(v);edge_count+=1
 need(edge_count==38912 and len(frames)==512,'all published root edges and owners')
 # An actual diagonal edge violates transversality; an omitted required Z
 # violates absolute Gaussian centralization. Both are executed controls.
 first=next(iter(frames.values()));G=first['normalizer_proof']['G_rows'];q=first['q25']
 diagonal_image=sum(dot(row,q)<<j for j,row in enumerate(transpose(G)))
 need(diagonal_image==1,'diagonal-edge control exhibits failed fresh premise')
 signed=next(frame for frame in frames.values()if frame['normalizer_proof']['Z_after_permutation'])
 columns=transpose(signed['normalizer_proof']['G_rows'])
 need(any((col.bit_count()-1)%4!=0 for col in columns),'omitted-sign control changes the full Gaussian')
 actual_root={'owners':len(frames),'literal_nonzero_edges':edge_count,'normalizer_Z4_coefficients':normalizer_coefficients,'distinct_pure_fresh_images':len(images),'all_edge_image_norms':1,'all_edge_central_bits':0,'diagonal_edge_control_rejected':True,'omitted_sign_control_rejected':True}
 result={'schema':'distinct-fresh-K-terminal-path-rank/v1','status':'PASS_SCOPED_PATH_LEMMA','published_root_premise':actual_root,'records':records,'signed_tableau_and_rank_paths':tableau_checks,'fresh_sparse_absolute_phase_columns':dense_checks,
         'identity':'For every actual B-path c M: Q^-1 M D = i^(-epsilon) R C_-(e0) C_[-(-1)^epsilon](M e0) M, where M X0 M^-1=(-1)^epsilon X_(M e0). Both removed normone directions are orthogonal.',
         'all_widths':'Lift each one-copy address operator by tensor f; scalar owner coefficient c is applied once, and displayed scalar phase lifts to i^(-epsilon*f).',
         'support_bound':'A fixed finite B expansion with T terms has row support <=T*2^((d-1)*f). Left/right ordinary monomial+scalar adapters with at most A ADDs increase T by at most 2^A. More generally require expanded monomial-term count T(f)=2^o(f), not merely subexponential instruction count.',
         'scope':'Distinct fresh stages; exact real orthogonal full-Gaussian centralizing normalizers; fitting K edge qi.qj=0. Single-cohort Gaussian terminal under the stated expanded-term adapter class. No claim for mixed-cohort optimal decoding, arbitrary uniform ordinary algorithms, overlapping stages, or a full-caller lower bound.',
         'changed_premise':'Overlapping stage actions can change the pure-fresh central image. Their actual Gaussian stage product, IDLE implementation and productive ranks must all be charged afresh; recovered central rank is not automatically free.'}
 return result,all_paths
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result,paths=calculate()
 if a.write:
  import gzip
  (HERE/'TERMINAL-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');(HERE/'TERMINAL-PATHS.json.gz').write_bytes(gzip.compress((json.dumps(paths,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
 else:
  need(json.loads((HERE/'TERMINAL-RESULT.json').read_bytes())==json.loads(json.dumps(result)),'read-only path lemma receipt')
  need(json.loads(gzip.decompress((HERE/'TERMINAL-PATHS.json.gz').read_bytes()))==json.loads(json.dumps(paths)),'read-only canonical decompressed coefficient paths')
 print(json.dumps(result,sort_keys=True))
