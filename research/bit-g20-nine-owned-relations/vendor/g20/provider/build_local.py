"""Freeze local forward, independently correct inverse and physical rawdual."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone
from time import process_time
import gzip,hashlib,json
from local_ir import N,EXPECTED,need,Geometry,replay,baseline_program,ad_inverse,transpose_rows,rowproduct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;INPUT=ROOT/'inputs';DATA=HERE/'data'
def read(p):return json.loads(gzip.decompress(p.read_bytes()))if p.suffix=='.gz'else json.loads(p.read_bytes())
def put(p,x):
 b=(json.dumps(x,indent=2)+'\n').encode();p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def verify_inputs():
 pins=read(ROOT/'INPUT-PINS.json')
 for p in pins['files']:
  source=ROOT/p['relative_path'];need(source.is_file()and hashlib.sha256(source.read_bytes()).hexdigest()==p['sha256'],'Readonlyinputpin '+p['relative_path'])
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def project(frame):
 b=[[F(x)for x in r]for r in frame['B']]
 if not b:return [[F(0)]*8 for _ in range(8)]
 def inv(a):
  n=len(a);w=[r[:]+[F(i==j)for j in range(n)]for i,r in enumerate(a)]
  for j in range(n):
   k=next(i for i in range(j,n)if w[i][j]);w[j],w[k]=w[k],w[j];x=w[j][j];w[j]=[v/x for v in w[j]]
   for i in range(n):
    if i!=j:
     x=w[i][j];w[i]=[v-x*z for v,z in zip(w[i],w[j])]
  return [r[n:]for r in w]
 bt=list(map(list,zip(*b)));return mm(mm(bt,inv(mm(b,bt))),b)
def main():
 clock=process_time();verify_inputs();DATA.mkdir(exist_ok=True);base=read(INPUT/'BASELINE-LOCAL.json.gz');forward=read(INPUT/'FORWARD.json.gz');inverse=read(INPUT/'INVERSE.json.gz');frames=read(INPUT/'FRAMES.json')['frames'];geom=Geometry(frames)
 need(forward['start']==base['start']and forward['final']==base['final']and inverse['start']==base['final']and inverse['final']==base['start'],'Exact old entry/exit flags')
 dual,retags=ad_inverse(inverse['records'],base['start'],base['final']);rawdual={'namespace':N,'allocated_slots':660,'owned_indices':[658,659],'start':base['start'],'final':base['final'],'records':dual,'definition':'Physical FUNCTION transpose of independently correct trueinverse, withpaidzero-mapCLEAR andzero-onlyreheaders. NotADDRESSinverse-transpose.'}
 result={};rows={}
 for name,payload in [('FORWARD',forward),('INVERSE',inverse),('RAW-DUAL',rawdual)]:
  out,stats,_=replay(payload['records'],payload['start'],payload['final'],geom);need(stats['paid']==EXPECTED,'New complete localinvoice '+name);need(stats['private_peak']<=2,'Two explicit private banks')
  for modulus in(101,101**2):
   nr,ns,_=replay(payload['records'],payload['start'],payload['final'],geom,modulus);need(nr==out,'All658nativecolumns '+name)
  rows[name]=out;result[name]=stats
  if name!='RAW-DUAL':
   src=INPUT/(name+'.json.gz');(DATA/(name+'.json.gz')).write_bytes(src.read_bytes())
  else:put(DATA/'RAW-DUAL.json.gz',payload)
 oldrows,oldstats,_=replay(baseline_program(base),base['start'],base['final'],geom);oldinv,_,_=replay(baseline_program(base,True),base['final'],base['start'],geom)
 need(rows['FORWARD']==oldrows and rows['INVERSE']==oldinv,'Both original operators unchanged, all658RAW')
 identity=[1<<i for i in range(N)];need(rowproduct(rows['FORWARD'],rows['INVERSE'])==rowproduct(rows['INVERSE'],rows['FORWARD'])==identity,'Both independent original inverse orders')
 need(rows['RAW-DUAL']==transpose_rows(rows['INVERSE']),'Decodedall658rawinverse-transpose; FRAMElemma suppliesallfunctions')
 controls={}
 for mutation in('wrong_rank4','omit_shadow_clear','wrong_shadow_frame'):
  try:replay(forward['records'],forward['start'],forward['final'],geom,mutant=mutation)
  except ValueError:controls[mutation]=True
  else:raise ValueError('Mutantnotrejected '+mutation)
 try:replay(forward['records']+[['CLEAR',0]],forward['start'],forward['final'],geom)
 except ValueError:controls['original_CLEAR']=True
 else:raise ValueError('Original erasure not rejected')
 requests=read(INPUT/'G22-FRESH-REQUESTS.json');I=[[F(i==j)for j in range(8)]for i in range(8)]
 for req in requests:
  lo,hi=req['old_frame'],req['new_frame'];r=req['rank'];geom.nested(lo,hi,r);p=[[x-y for x,y in zip(a,b)]for a,b in zip(project(frames[str(hi)]),project(frames[str(lo)]))];stored=[[F(x)for x in row]for row in req['projector']];s=[[F(x)for x in row]for row in req['matcher_S']];si=[[F(x)for x in row]for row in req['matcher_inverse']];qr=[[F(i==j and i<r)for j in range(8)]for i in range(8)];need(stored==p and mm(p,p)==p and sum(p[i][i]for i in range(8))==r and mm(s,si)==mm(si,s)==I and mm(mm(s,qr),si)==p,'FreshproperQQ SOURCE matcher, notoldticket')
 put(DATA/'LOCAL-INVOICE.json',{'directions':result,'baseline_paid':oldstats['paid'],'originals':N,'owned':2,'owned_original_credit':0,'BIT_VALUE':'All VALUE operations are exact F2 XOR. Cancellation-free positive integer majorants are bounds, not a claim of integer-valued endpoint identity.','rawdual_zero_reheaders':retags,'controls':controls,'CPU_seconds':process_time()-clock})
 put(DATA/'LOCAL-ROWS.json.gz',{k:[hex(x)for x in v]for k,v in rows.items()})
 print(json.dumps({'status':'PASS_PORTABLE_LOCAL3_DIRECTIONS_ALL658_RAW_AND_FULL_FUNCTION_CONTROLS','directions':{k:{'mass':v['rankmass'],'majorant_bits':v['majorant_bits'],'private_peak':v['private_peak']}for k,v in result.items()},'CPU_seconds':process_time()-clock}))
if __name__=='__main__':main()
