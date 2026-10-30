"""Second all-depth range certificate, using exact positive polynomials.

Chris R / Clear1nsight with OpenAI assistance; Apache-2.0.
Derived independently during adversarial review; imports no range.py or predecessor.
"""
from fractions import Fraction as Q
from math import comb
import hashlib,json
F = (Q(445),Q(28230),Q(96),Q(142272))
def need(ok,why):
 if not ok:raise ValueError(why)
def plus(a,b,c=Q(1)):
 out=[Q(0)]*max(len(a),len(b))
 for i,v in enumerate(a):out[i]+=v
 for i,v in enumerate(b):out[i]+=c*v
 while len(out)>1 and not out[-1]:out.pop()
 return tuple(out)
def mulx(a,c):return (Q(0),)+tuple(c*v for v in a)
def shifted(a):
 return tuple(sum(a[i]*comb(i,j) for i in range(j,len(a))) for j in range(len(a)))
def dominates(bound,value):return all(c>=0 for c in shifted(plus(bound,value,-1)))
def audit(word,bound=F):
 state={s+str(p):(Q(1),) for s in ('X','Y') for p in range(112)}
 owned={s+str(p) for s in ('Z','W') for p in range(112)}
 active=set();observations=[];peaks=[]
 def obs(i,name,value):
  need(dominates(bound,value),'polynomial envelope understated at '+str(i)+' '+name)
  observations.append([i,name,list(map(str,value))])
  if value==bound:peaks.append([i,name])
 for i,e in enumerate(word):
  op=e[0]
  if op=='begin':
   need(not active and e[2] in (8,16),'private overlap')
   active={s+str(k) for s in (('F','G') if e[2]==16 else ('F',)) for k in range(8)}
   for n in active:state.pop(n,None)
  elif op=='end':
   need(len(active)==e[2] and all(state.get(n)==(Q(0),) for n in active),'private return')
   for n in active:state.pop(n)
   active=set()
  elif op=='checkpoint':need(not active,'active checkpoint')
  else:
   name=e[1];need(name in owned|active,'write borrowed')
   if op=='clear':state[name]=(Q(0),)
   elif op=='add':
    c=abs(Q(e[3]));need(c in (1,Q(1,4)) and name!=e[2],'coefficient/alias')
    need(name in state and e[2] in state,'dirty read')
    state[name]=plus(state[name],state[e[2]],c)
   elif op=='line':
    need(not active and name in state,'native boundary')
    obs(i,'native cross '+name,mulx(state[name],4))
    state[name]=mulx(state[name],2)
   elif op=='map':need(not active and name in state,'map boundary')
   else:raise ValueError('opcode')
   obs(i,'post '+name,state[name])
 need(not active and all(n in state for n in owned),'outputs incomplete')
 return {'variable':'x=2^(lambda-1)>=1','envelope_coefficients':list(map(str,bound)),
         'proof':'Every F-observation has nonnegative coefficients after x=1+y; F(1)=171043 and degree3 give F(x)<=171043*x^3.',
         'observations':len(observations),'peaks':peaks,
         'observation_sha256':hashlib.sha256(json.dumps(observations,separators=(',',':')).encode()).hexdigest()}
def compare(candidate,baseline):
 a,b=audit(candidate),audit(baseline)
 need(a['observations']==3932 and b['observations']==4032,'observation census')
 need(sum(F)==171043 and len(F)==4,'fixed polynomial')
 bad=list(F);bad[3]-=1
 for w in (candidate,baseline):
  try:audit(w,tuple(bad))
  except ValueError:pass
  else:raise ValueError('accepted understated cubic envelope')
 return {'candidate':a,'baseline':b,'negative_control':'Understate cubic coefficient142272 by1: both inductive certificates reject. Not a minimum-physical-width lower bound.'}
