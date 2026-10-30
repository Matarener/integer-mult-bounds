"""All3375 actual full120 odd3 q/common-frame geometry, no phase sampling."""
from pathlib import Path
from itertools import product
from collections import Counter
from hashlib import sha256
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
def need(a,b):
 if not a:raise ValueError(b)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def basis(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:p[x.bit_length()-1]=x
 return tuple(p[j]for j in sorted(p,reverse=True))
def dot(a,b):return(a&b).bit_count()&1
def calculate():
 d=json.loads((HERE/'inputs/NORMALIZERS.json').read_bytes());cover=json.loads((HERE/'inputs/COVER.json').read_bytes());q=[p['q']for p in d['ports']];records=cover['cover15'];need(len(q)==120 and len(set(q))==120 and len(basis(q))==9,'all actual base120 unique/fullspan')
 geo=load('new120geometry',HERE/'geometry_tools.py');U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j))for b in range(3)for j in range(1,9)];orth=geo.ortho_basis(U);need(len(orth)==25 and all(dot(a,b)==int(i==j)for i,a in enumerate(orth)for j,b in enumerate(orth)),'one actual global orthonormal U25 basis')
 physical={};patterns=Counter();contractions=0;classes=0;total=0;dig=sha256()
 for cube in product(range(15),repeat=3):
  chosen=[records[i]for i in cube];ports=[r['ports']for r in chosen];color=[{p:j for j,side in enumerate(r['source_parity_classes'])for p in side}for r in chosen];sides=[[],[]]
  for t in product(*ports):
   raw=q[t[0]]|(q[t[1]]<<9)|(q[t[2]]<<18);side=sum(color[j][t[j]]for j in range(3))&1
   need(raw.bit_count()%2==1 and raw!=(1<<27)-1,'actual global odd/noncharacteristic raw q')
   # The basis is a single global physical choice, identical for all3375
   # cubes. No cube-local-to-global adapter is granted.
   p=sum(dot(raw,b)<<j for j,b in enumerate(orth));need(dot(p,p)==1 and p!=(1<<25)-1,'actual physical I25 normone/noncharacteristic')
   sides[side].append(p);dig.update(p.to_bytes(4,'little'));total+=1
  bs=[basis(side)for side in sides];need([len(x)for x in sides]==[256,256]and[len(b)for b in bs]==[9,9],'actual256port9spaces bothparities')
  need(all(not dot(a,b)for a in bs[0]for b in bs[1]),'actual all source/read basis crossorth')
  for side in [0,1]:
   br=[sum(dot(a,b)<<j for j,b in enumerate(bs[side]))for a in bs[side]];need(len(basis(br))==1,'actual restricted9space pairingrank1')
   for p in sides[1-side]:
    need(all(not dot(p,a)for a in bs[side]),'every actual reader q-perp contains the common S9');contractions+=9
   classes+=1
  patterns[len(basis(bs[0]+bs[1]))]+=1;need(len(basis(bs[0]+bs[1]))==10,'actual joint cube span10')
 need(total==120**3 and classes==2*15**3,'all global owner labels and sourceclasses covered once by actual cube partition')
 return {'schema':'full120-odd3-all-cube-physical-geometry/v1','status':'PASS_ALL3375_ACTUAL_FULL120_ODD3_PHYSICAL_CUBES','base_q_count':120,'cube_count':15**3,'original_source_owners':total,'ambient_axes':25,'orthonormal_basis_raw27':orth,'parity_classes':classes,'actual_q_vs_opposite_source_basis_dot_checks':contractions,'source_class_dimension':9,'reader_perp_dimension':24,'joint_opposite_class_span_histogram':dict(patterns),'restricted_class_pairing_rank':1,'restricted_class_radical_dimension':8,'native_paid_profile_whole':{'8':120**3,'9':120**3,'15':120**3,'16':120**3},'physical_q_stream_sha256':dig.hexdigest(),'C_rank':22016,'C_rank_per_owner':'43/3375','source_pins':{f:sha256((HERE/f).read_bytes()).hexdigest()for f in ['inputs/NORMALIZERS.json','inputs/COVER.json','geometry_tools.py']},'phase_scope':'Full-family geometry only. Phase-complete literal product cube000 is separately emitted by core.py; generic native frame/phase proof remains required for the forall-family template. No terminal decoder, caller admission or kappa is asserted.','new_kappa':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();d=json.loads(canon(calculate()));p=HERE/'FAMILY-GEOMETRY120.json'
 if a.write:p.write_bytes(canon(d))
 else:need(json.loads(p.read_bytes())==d,'read-only all3375 geometry')
 print(json.dumps(d,sort_keys=True))
