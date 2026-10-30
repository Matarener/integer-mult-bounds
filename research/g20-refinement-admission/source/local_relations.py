"""Own nine G20 capture relations; retain 649 independent original fields.

The nine-owned-relation method is Ali Romman's PR5421.  The present program
rederives it on the distinct G20 partial436 producer, including its shadow.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from time import process_time
import gzip,json,hashlib,sys
R=Path(__file__).resolve().parent
S=R/'vendor/g20'
sys.path.insert(0,str(S/'provider'))
from local_ir import Geometry
N=658
def need(c,m):
 if not c:raise ValueError(m)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def put(name,obj):
 p=R/name;b=(json.dumps(obj,indent=2)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def bitids(row):return [i for i in range(N+2)if row>>i&1]
def source():return read(S/'inputs/BASELINE-LOCAL.json.gz'),read(S/'inputs/FRAMES.json')['frames'],read(S/'provider/data/INVERSE.json.gz')['records']
def relations(program):
 rows=[1<<i for i in range(N)]+[0,0];caps=[]
 for ix,e in enumerate(program):
  op,d=e[:2]
  if op=='ADD':rows[d]^=rows[e[2]]
  elif op=='COPY':caps.append((ix,rows[e[2]]));rows[d]=rows[e[2]]
  elif op in('CLEAR','TICKET_CLEAR'):rows[d]=0
 basis={}
 for _,row in caps:
  for p,v in sorted(basis.items()):
   if row>>p&1:row^=v
  h=row>>222;need(h,'New helper pivot');p=222+(h&-h).bit_length()-1
  for k in basis:
   if basis[k]>>p&1:basis[k]^=row
  basis[p]=row
 need(len(basis)==9,'Nine independent relations')
 pm=sum(1<<p for p in basis)
 for p,row in basis.items():need(row&pm==1<<p,'Reduced pivot basis')
 return dict(sorted(basis.items()))
def construct(base,frames,program,basis):
 owned=set(basis)|{658,659};rows=[1<<i for i in range(N+2)];st=base['final']+[None,None];out=[];removed=[]
 for d in(658,659):out.append(['ERASE',d,None]);rows[d]=0
 for p,row in basis.items():
  need(base['start'][p]==0 and base['final'][p]==1 and frames['1']['dim']==8,'Debited full rank8 pivot')
  need(all(st[i]==1 for i in bitids(row)),'Every relation term actual full8 entrance')
  out.append(['ERASE',p,1]);rows[p]=0
  for i in bitids(row):
   if i!=p:out.append(['ADD',p,i,1]);rows[p]^=rows[i]
 for ix,e in enumerate(program):
  op,d=e[:2]
  if op=='ADD':rows[d]^=rows[e[2]];out.append(e)
  elif op=='Q':
   need(st[d]==e[2],'Actual input frame')
   if rows[d]:out.append(e)
   else:out.append(['ZERO_Q',d,e[2],e[3],e[4]]);removed.append([ix,'Q',d,e[4]])
   st[d]=e[3]
  elif op=='COPY':
   need(rows[e[2]]==rows[d]==0,'Zero full COPY relation')
   out.append(['ERASE',d,0]);st[d]=0;removed.append([ix,'COPY',d,e[4]])
  elif op=='TICKET_CLEAR':out.append(['ERASE',d,None]);rows[d]=0;st[d]=None
  elif op=='INIT':out.append(e);st[d]=e[2];need(rows[d]==0,'Whole zero shadow INIT')
  else:need(op=='CLEAR','Known opcode');out.append(['ERASE',d,None]);rows[d]=0;st[d]=None
 for d in basis:out.append(['ERASE',d,base['start'][d]])
 need(Counter(x[-1]for x in removed)=={1:9,7:9},'Exactly nine H1 and H7 removed')
 return out,removed,owned
def replay(base,frames,program,owned,modulus=None):
 geom=Geometry(frames);st=base['final']+[None,None];rows=[1<<i for i in range(N+2)];norm=[1]*(N+2);paid=Counter();ops=Counter();peak=1;active=set();livepeak=0
 fields=None
 if modulus:
  point=tuple(v%modulus for v in(1,2,4,8,16,32,64,128,3,5,7,11,13,17,19,23));fields=[{point:1<<i}for i in range(N+2)]
 def transform(field,p):return{geom.move(p,x,modulus):v for x,v in field.items()}
 for ix,e in enumerate(program):
  op,d=e[:2];ops[op]+=1
  if op=='ERASE':
   need(d in owned,'No retained original erasure');rows[d]=norm[d]=0;st[d]=e[2];active.discard(d)
   if fields is not None:fields[d]={}
  elif op=='INIT':need(d in owned and rows[d]==0,'Whole zero INIT');st[d]=e[2]
  elif op=='ADD':
   s,f=e[2:];need(d!=s and st[d]==st[s]==f,'Actual common-frame XOR');rows[d]^=rows[s];norm[d]+=norm[s];peak=max(peak,norm[d])
   if d in owned:active.add(d)
   if fields is not None:
    for x,v in fields[s].items():
     z=fields[d].get(x,0)^v
     if z:fields[d][x]=z
     else:fields[d].pop(x,None)
  elif op in('Q','ZERO_Q'):
   s,t,k=e[2:];need(st[d]==s,'Actual current source FRAME');geom.nested(s,t,k);st[d]=t
   if op=='ZERO_Q':need(rows[d]==0 and(fields is None or not fields[d]),'Free move only whole zero')
   else:
    paid[k]+=1
    if fields is not None:fields[d]=transform(fields[d],geom.residual_mod(s,t,k,modulus))
  else:raise ValueError('Unknown event '+op)
  livepeak=max(livepeak,len(active))
 need(st==base['start']+[None,None],'All final frames')
 expected=[0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(N+2)]
 need(rows==expected,'All660 independent RAW and arbitrary DIRTY entry columns')
 if fields is not None:
  for o,row in enumerate(expected):
   want={}
   for i in bitids(row):
    y=geom.move(geom.project_mod(base['start'][o],modulus),geom.move(geom.project_mod(base['final'][i],modulus),point,modulus),modulus);want[y]=want.get(y,0)^(1<<i)
   need(fields[o]=={x:v for x,v in want.items()if v},'Full physical endpoint all660 symbols at output '+str(o))
 return{'paid':dict(sorted(paid.items())),'operation_counts':dict(ops),'owned_allocated':len(owned),'owned_live_payload_peak':livepeak,'retained_originals':N-len(owned-{658,659}),'positive_majorant_bits':peak.bit_length(),'positive_majorant':str(peak),'native_modulus':modulus}
def run(write=False):
 clock=process_time();base,frames,old=source();basis=relations(old);program,removed,owned=construct(base,frames,old,basis)
 stats=replay(base,frames,program,owned)
 for m in(101,101**2):replay(base,frames,program,owned,m)
 need(stats['paid']=={1:1309,2:1342,3:77,4:40,5:102,6:10,7:9},'Changed actual local invoice')
 bad=program[:];bad.pop(next(i for i,e in enumerate(bad)if e[0]=='ERASE'and e[1]in basis))
 try:replay(base,frames,bad,owned)
 except ValueError:pass
 else:raise ValueError('Missing initial DIRTY clear accepted')
 result={'status':'PASS_G20_NINE_OWNED_RELATIONS_ALL660_COLUMNS','basis':{str(p):bitids(row)for p,row in basis.items()},'removed':removed,'stats':stats,'CPU_seconds':process_time()-clock,'source_inverse_gzip_sha256':hashlib.sha256((S/'provider/data/INVERSE.json.gz').read_bytes()).hexdigest(),'canonical_word_sha256':hashlib.sha256(json.dumps(program,separators=(',',':')).encode()).hexdigest(),'method_credit':'Ali Romman PR5421 head295b00764305694b3c510d3b0bebc2ab024a7809; actual G20 profile differs.'}
 if write:put('LOCAL-RESULT.json',result);put('WORD.json.gz',{'records':program,'owned':sorted(owned),'start':base['final']+[None,None],'final':base['start']+[None,None]})
 return result
if __name__=='__main__':print(json.dumps(run(True),indent=2))
