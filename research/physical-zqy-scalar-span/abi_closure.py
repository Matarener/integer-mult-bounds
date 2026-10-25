#!/usr/bin/env python3
"""Fixed physical Z-ABI left-image audit; default replay is read-only.

Predecessors: physical K normalizers/C by the #4933 lineage; the actual
coupled provider and its mode boundaries by Dillon's #5402; Z/W observer ABI
by #5415/#5419; native event/version semantics by Mark (Matarener), #5427.
This finite composed-normalizer audit was prepared for THU New Media Research
Center (@thu-nmrc) with substantial OpenAI Codex assistance. Apache-2.0.

This is a bounded family of independently chosen left images, not closure
under arbitrary products of its generators or an arbitrary-free-control
lower bound. The primary registered verify.py proves the base exact rank.
"""
from pathlib import Path
from array import array
from hashlib import sha256
import argparse,json,sys,struct
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native as N
import monomial as M

INPUTS={
 'normalizers':('research/coded-native-caller/NORMALIZERS.json',
  'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'),
 'provider_interface':('research/native-rank8-helper-provider/PROVIDER.json',
  '676de7551d3364598f4a7e29ae97cae0e4364348786bbe70435b84294ba7dd65')}


def read(name):
 rel,digest=INPUTS[name];raw=(N.ROOT/rel).read_bytes()
 N.need(sha256(raw).hexdigest()==digest,'fixed ABI input bytes '+rel)
 return json.loads(raw)


def row_map(rows,x):
 return sum(((rows[j]&x).bit_count()%2)<<j for j in range(9))


def quadratic(rows,alpha,x):
 phase=sum(alpha[j] for j in range(9)if x>>j&1)
 phase+=2*sum(((rows[j]>>k)&1) for j in range(9)for k in range(j+1,9)
              if (x>>j&1)and(x>>k&1))
 return phase%4


def literal(word):
 """Literal chronological P/D/X/phase monomial, including absolute phase."""
 values=list(M.decode(M.IDENTITY))
 for event in word:
  kind=event[0]
  if kind=='P':
   N.need(len(event[1])==9,'nine-axis P')
   values=[4*row_map(event[1],v//4)+v%4 for v in values]
  elif kind=='D':
   N.need(len(event[1])==len(event[2])==9,'nine-axis D')
   values=[4*(v//4)+(v%4+quadratic(event[1],event[2],v//4))%4 for v in values]
  elif kind=='X':values=[4*((v//4)^event[1])+v%4 for v in values]
  elif kind=='phase':values=[4*(v//4)+(v%4+event[1])%4 for v in values]
  else:raise ValueError('non-monomial ABI event '+repr(kind))
 N.need(sorted(v//4 for v in values)==list(range(512)),'literal monomial permutation')
 return array('H',values).tobytes()


def exact_R_centralizer(operator):
 """Check sufficient exact signed-linear full-Gaussian kernel identities.

K|x>=i^phase(x)|Gx>. Orthogonal G and a real linear sign, together with
phase(x)-wt(x)+wt(Gx)=0 mod4, imply KR=RK for
R[y,x]=alpha*(-i)^wt(x+y). The scalar alpha is retained on both sides.
"""
 values=M.decode(operator)
 N.need(values[0]==0,'ABI zero-address absolute phase')
 columns=[values[1<<j]//4 for j in range(9)]
 phases=[values[1<<j]%4 for j in range(9)]
 N.need(all(z%2==0 for z in phases),'real linear ABI sign')
 for j,a in enumerate(columns):
  for k,b in enumerate(columns):
   N.need((a&b).bit_count()%2==int(j==k),'orthogonal ABI binary map')
 for x,v in enumerate(values):
  N.need(M.linear(columns,x)==v//4,'linear ABI address map')
  phase=sum(phases[j] for j in range(9)if x>>j&1)%4
  N.need(phase==v%4,'linear ABI sign at every address')
  N.need((phase-x.bit_count()+(v//4).bit_count())%4==0,
         'exact full-Gaussian signed kernel commutation')
 return 512


def digest_operators(operators):
 return sha256(b''.join(sorted(struct.pack('<512H',*M.decode(op)) for op in operators))).hexdigest()


def calculate():
 normalizers=read('normalizers');interface=read('provider_interface')
 ports=[literal(row['K_word']) for row in normalizers['ports']]
 mode_rows=interface['mode_boundaries']
 modes=[literal(row['input_K']['literal_word']) for row in mode_rows]
 N.need(len(ports)==112 and len(modes)==8,'112-port/eight-mode ABI')
 N.need([row['mode']for row in mode_rows]==list(range(8)),'ordered mode basis')
 N.need([row['owner']for row in mode_rows]==interface['mode_owners'],'physical mode ownership')
 mode_columns=normalizers['mode_columns']
 N.need(len(mode_columns)==8 and all(len(c)==112 for c in mode_columns),'source mode matrix shape')
 N.need(all(x in (-1,0,1)for c in mode_columns for x in c),'source mode entries')
 N.need(sum(x!=0 for c in mode_columns for x in c)==448,'mode support count')
 for a in range(8):
  for b in range(8):
   N.need(sum(x*y for x,y in zip(mode_columns[a],mode_columns[b]))==56*int(a==b),
          'physical Z/W mode Gram identity')
 anchor_checks=sum(exact_R_centralizer(x)for x in ports+modes)
 N.need(all(M.inverse(x)==x for x in ports+modes),'seed normalizer inverses already present')

 source=N.read('source');provider=N.read('provider');canon=source['canonical'];N.initialize(canon)
 versions,rows,frames,full=N.native_replay(canon,provider['word'],True)
 N.need(len(versions)==4891,'complete provider full-frame history')
 used_indices=sorted({op for row in versions for role,op in row})
 base_operators=[N.operators[i]for i in used_indices]
 N.need(len(base_operators)==59 and len(set(base_operators))==59,'59 literal base operators')
 N.need(all(M.decode(op)[0]==0 for op in base_operators),'base zero anchors')
 # This check consumes the primary registered exact certificate. It does not
 # substitute a modular rank test for that exact base injectivity proof.
 primary=json.loads((HERE/'RESULT.json').read_text())
 base=next(row for row in primary['cases']if row['name']=='provider-backward')
 N.need(base['full_frame_versions']==4891 and
        base['exact_group_rank']==base['exact_group_non_Y_projection_rank']==546,
        'primary exact base-span injectivity certificate')

 raw=[('I',M.IDENTITY)]
 raw += [('Kp_'+str(i),x)for i,x in enumerate(ports)]
 raw += [('Km_'+str(a),x)for a,x in enumerate(modes)]
 raw += [('Km_'+str(a)+'^-1_Kp_'+str(i),M.multiply(M.inverse(km),kp))
         for a,km in enumerate(modes)for i,kp in enumerate(ports)]
 N.need(len(raw)==1017,'declared finite ABI family before deduplication')
 seen=set();family=[]
 for name,operator in raw:
  if operator not in seen:seen.add(operator);family.append((name,operator))
 N.need(len(family)==1012,'1012 distinct concrete ABI left maps')
 N.need(all(M.decode(op)[0]==0 for name,op in family),'left-map absolute zero anchors')
 products=set();zero_anchors=0
 for name,left in family:
  for right in base_operators:
   product=M.multiply(left,right)
   N.need(product not in products,'left-image operator-support collision')
   products.add(product)
   N.need(product[:2]==b'\0\0','product zero anchor and absolute phase')
   zero_anchors+=1
 N.need(len(products)==1012*59==59708,'complete distinct left-image support')
 # At tensor degree n-1, products of separating linear forms give one dual
 # functional per projective point. The common zero anchor lifts to all
 # larger degrees. This is a symbolic theorem, not a huge numerical Gram.
 threshold=len(products)-1
 return {
  'schema':'physical-zqy-fixed-abi-left-images/v1',
  'status':'PASS_FIXED_Z_ABI_LEFT_IMAGES_EVENTUAL_WIDTH_NO_NEW_KAPPA',
  'input_sha256':{name:digest for name,(rel,digest)in INPUTS.items()},
  'provider_full_frame_versions':len(versions),
  'base_exact_rank_from_primary':546,'base_exact_non_Y_projection_rank_from_primary':546,
  'base_operator_count':len(base_operators),'base_operator_set_sha256':digest_operators(base_operators),
  'port_normalizers':112,'mode_normalizers':8,'seed_normalizer_inverse_additions':0,
  'seed_exact_F9_signed_kernel_address_checks':anchor_checks,
  'physical_to_logical_left_transport':'F9^-1 T F9 = T, including absolute phase; all seeds centralize the full nine-axis Gaussian and so do their products.',
  'raw_left_family_size':len(raw),'distinct_left_maps':len(family),
  'left_map_set_sha256':digest_operators(seen),
  'distinct_left_products':len(products),'left_support_collision_count':0,
  'left_product_set_sha256':digest_operators(products),
  'product_exact_zero_anchor_checks':zero_anchors,
  'tensor_independence_degree_bound':threshold,
  'coefficient_scope':'arbitrary complex scalar coefficients, allowed to depend on width',
  'conclusion':'For every f>=59707 the declared finite left-image span has no nonzero pure-Y vector. Thus it cannot supply the nonzero eight-mode b=ZQY by an exact all-width identity within this fixed family.',
  'scope':'Provider-backward whole history; independently chosen left images T in {I,Kp_i,Km_a,Km_a^-1 Kp_i}. No unrestricted products of these generators, no arbitrary monomial left closure, no changed producer or extra correlated data; no small-width nonmembership claim.',
  'target_or_paid_profile_change':False,'new_kappa':False,
  'base_rank_obligation':'The registered primary verify.py must pass; this command authenticates/replays the source and consumes its exact 546/546 certificate, rather than rerunning the large exact elimination.'}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
 result=calculate();encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if args.write:(HERE/'ABI-CLOSURE.json').write_text(encoded)
 else:N.need(json.loads((HERE/'ABI-CLOSURE.json').read_text())==result,'fixed ABI receipt differs')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
