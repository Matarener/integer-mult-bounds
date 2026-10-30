"""Native replay adapted from ai-nanachi PR5512 for two extra owned banks.

All source geometry and coframe checks are retained. Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import baseline as B
Geometry=B.SOURCE.Geometry
need=B.need
bitids=B.SOURCE.bitids
N=658
def replay(base,frames,program,owned,modulus=None):
 geom=Geometry(frames);st=base['final']+[None]*4;rows=[1<<i for i in range(N+4)];norm=[1]*(N+4);paid=Counter();ops=Counter();peak=1;active=set();livepeak=0
 fields=None
 if modulus:
  point=tuple(v%modulus for v in(1,2,4,8,16,32,64,128,3,5,7,11,13,17,19,23));fields=[{point:1<<i}for i in range(N+4)]
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
 need(st==base['start']+[None]*4,'All final frames')
 expected=[0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(N+4)]
 need(rows==expected,'All662 independent RAW and arbitrary DIRTY entry columns')
 if fields is not None:
  for o,row in enumerate(expected):
   want={}
   for i in bitids(row):
    y=geom.move(geom.project_mod(base['start'][o],modulus),geom.move(geom.project_mod(base['final'][i],modulus),point,modulus),modulus);want[y]=want.get(y,0)^(1<<i)
   need(fields[o]=={x:v for x,v in want.items()if v},'Full physical endpoint all662 symbols at output '+str(o))
 return{'paid':dict(sorted(paid.items())),'operation_counts':dict(ops),'owned_allocated':len(owned),'owned_live_payload_peak':livepeak,'retained_originals':N-len(owned-{658,659,660,661}),'positive_majorant_bits':peak.bit_length(),'positive_majorant':str(peak),'native_modulus':modulus}
