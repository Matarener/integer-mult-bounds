"""Independent fixed-point rational audit of PR4441's combined arithmetic.

Intervals are integers in units of 10^-60. Every operation rounds outward.
No numerical or source interval implementation is imported.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse, hashlib, importlib.util, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'research/fresh-helper-thinned'
SOURCE_FILES=('README.md','PROOF.md','verify.py','RESULT.json')
S=10**60
def need(ok,why):
    if not ok: raise ValueError(why)
def ceildiv(a,b): return -((-a)//b)
def rat(q):
    q=Q(q);return q.numerator*S//q.denominator,ceildiv(q.numerator*S,q.denominator)
def add(a,b): return a[0]+b[0],a[1]+b[1]
def mul(a,b):
    x=[u*v for u in a for v in b]
    return min(x)//S,ceildiv(max(x),S)
def scale(a,q):
    q=Q(q);x=[v*q.numerator for v in a]
    return min(x)//q.denominator,ceildiv(max(x),q.denominator)
def div(a,b):
    need(a[0]>=0 and b[0]>0,'Positive division')
    return a[0]*S//b[1],ceildiv(a[1]*S,b[0])
def atanh_log(z):
    need(0<=z<=Q(1,3),'Log range reduction')
    zz=rat(z);z2=mul(zz,zz);term=zz;out=(0,0);N=80
    for j in range(N):
        out=add(out,scale(term,Q(2,2*j+1)))
        term=mul(term,z2)
    tail=2*z**(2*N+1)/((2*N+1)*(1-z*z))
    return out[0],out[1]+rat(tail)[1]
@lru_cache(None)
def logn(n):
    if n==1:return 0,0
    k=n.bit_length()-1
    return add(scale(atanh_log(Q(1,3)),k),atanh_log(Q(n-2**k,n+2**k)))
def exp_interval(x):
    if x[1]<=0:
        y=exp_interval((-x[1],-x[0])) if x!=(0,0) else (S,S)
        return S*S//y[1],ceildiv(S*S,y[0])
    need(x[0]>=0 and x[1]<20*S,'Exponential input domain')
    term=(S,S);out=term;N=160
    for j in range(1,N+1):
        term=scale(mul(term,x),Q(1,j));out=add(out,term)
    nxt=ceildiv(term[1]*x[1],S*(N+1))
    tail=ceildiv(nxt*S*(N+2),(N+2)*S-x[1])
    return out[0],out[1]+tail
@lru_cache(None)
def power(n,e):return exp_interval(scale(logn(n),e))
def moment(profile,e):
    out=(0,0)
    for n,count in profile.items():out=add(out,scale(power(n,e),count))
    return out
def show(x):
    def one(n):
        sign='-' if n<0 else '';n=abs(n)
        return sign+str(n//S)+'.'+str(n%S).zfill(60)
    return {'lower':one(x[0]),'upper':one(x[1])}
def overlap(x,entry):
    return max(Q(x[0],S),Q(entry['lower']))<=min(Q(x[1],S),Q(entry['upper']))
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

source_meta=json.loads((HERE.parent/'SOURCES.json').read_text())
for name in SOURCE_FILES:
    path='research/fresh-helper-thinned/'+name
    row=next(r for r in source_meta['files'] if r['path']==path)
    need(hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==row['sha256'],'Exact updated-frontier source: '+name)
r=json.loads((SOURCE/'RESULT.json').read_text())
T={int(k):v for k,v in r['targets'].items()};P={int(k):v for k,v in r['paid'].items()}
own_path=HERE.parent/'controller/P17-DIRECT-CASE.json'
need(hashlib.sha256(own_path.read_bytes()).hexdigest()=='00247ee53b39cf01e176d93b8035bbdb18e7669f969b4ab576130205ae02d0df','Independently constructed controller source pin')
own=json.loads(own_path.read_text())
need(T=={int(k):v for k,v in own['complete_productive_profile'].items()} and P=={int(k):v for k,v in own['complete_paid_profile'].items()},'Published invoice equals independently constructed full controller')
need(sum(T.values())==11560 and sum(P.values())==69273,'All fields and requests')
need(sum(k*v for k,v in T.items())==260798 and sum(k*v for k,v in P.items())==259998,'Both exact masses')
C=Q('.003001052');kappa=Q('.00300105');v=1024;t=1-C
tm=moment(T,t);pm=moment(P,t)
alpha=div(pm,tm)
gamma=div(moment(P,t+Q(1,5)),mul(power(20,Q(1,5)),tm))
delta=div(rat(11560*21),mul(power(20,C),tm))
need(alpha[1]<(S-S//10**9),'Alpha bound')
need(gamma[1]<rat(Q(97,100))[0],'Gamma bound')
need(delta[1]<rat(Q(19,20))[0],'Delta bound')
need(gamma[0]>rat(Q(31,32))[1],'Old gamma bound fails')
for name,x in [('alpha',alpha),('gamma',gamma),('delta',delta)]:
    need(overlap(x,r['strictification'][name]),'Published interval overlap: '+name)
need(Q(97,100)**128<Q(1,16) and Q(19,20)**128<Q(1,16),'Both exact decay blocks')
bound=1/(1+Q(v,10**9))+Q(4,2**32)
need(bound<1 and str(bound)==r['strictification']['normalized_paid_upper'],'Complete paid-tail rational bound')
theta=Q(63,64)
eta=scale(power(153,-v*C),t)
need(20**64<21**63,'Strict rank separation')
need(2*20**(v*64)<=153**(v*63),'Shifted exit capacity')
need(eta[0]>rat(theta**1000)[1],'Complement log-majorant capacity')
need(power(153,v*C)[1]<2**1000*S,'Initial compiler range')
need(overlap(eta,r['compiler']['eta']),'Published eta interval')
gap=(C-kappa)/7;H=r['compiler']['H'];j=r['compiler']['integer_test_exponent']
need(gap==Q(1,3500000000) and H==3500000000*j and H==165315500000000,'Compiler grid')
need((H+1)**1000<2**j,'Final uniform rank inequality')
need((H-3500000000+1)**1000>=2**(j-1),'Preceding compiler grid point rejected')
root_signs={}
for name,c in [('lower',Q('.0030010541830')),('upper',Q('.0030010541834'))]:
    ta,pa=moment(T,1-c),moment(P,1-c)
    margin=(ta[0]-pa[1],ta[1]-pa[0]);root_signs[name]=show(margin)
    need(margin[0]>0 if name=='lower' else margin[1]<0,'Independent root bracket sign')
signed={rank:T.get(rank,0)-P.get(rank,0) for rank in T.keys()|P.keys()}
derivative=[]
for j in range(16):
    left,right=Q(j,320),Q(j+1,320);total=(0,0)
    for rank,count in signed.items():
        total=add(total,scale(mul(power(rank,1-(right if count>0 else left)),logn(rank)),count))
    derivative.append(total[0])
remaining=[]
for j in range(128):
    left,right=Q(1,20)+Q(19*j,2560),Q(1,20)+Q(19*(j+1),2560);total=(0,0)
    for rank,count in signed.items():
        total=add(total,scale(power(rank,1-(left if count>0 else right)),count))
    remaining.append(total[1])
need(min(derivative)>0 and max(remaining)<0,'Fixed-profile ceiling throughout every real0<C<1')
profile_ceiling={'strictly_decreasing_through':'1/20','negative_derivative_upper':show((-min(derivative),)*2),'remaining_interval_upper':show((max(remaining),)*2),'derivative_cells':16,'remaining_cells':128}
bit=r['ordinary_BIT'];atom=Q(bit['atom'])
ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')
need(ordinary==Q(bit['ordinary_saving']) and atom>ordinary>Q(bit['admitted'])>C,'Exact ordinary BIT arithmetic')
ledger_path=ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
need(hashlib.sha256(ledger_path.read_bytes()).hexdigest()=='d097e55f06c3f244f2074ffd7c1a0a5f3c4b4b6a6accf9619d1dde5c0ae85e15','Pinned outer ledger source')
spec=importlib.util.spec_from_file_location('pinned_outer',ledger_path);L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
params={'kappa':kappa,'tested_saving':C,'complex_uniform_saving':kappa+6*gap,'b':kappa+5*gap,'a':kappa+4*gap,'q':kappa+3*gap,'bit_saving':Q(bit['admitted']),'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
outer=L.ledger(params);outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
need(encode(outer)==r['outer'],'Exact outer ledger receipt reproduction')
need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4 and all(q>0 for k in ('strict_checks','functional_checks') for q in outer[k].values()),'All 54+4 inequalities')
refined_alpha=div(moment(P,1-Q('.003001054')),moment(T,1-Q('.003001054')))
need(refined_alpha[1]<S-S//10**10,'Parent refined alpha bound independently holds')
result={'status':'PASS_INDEPENDENT_COMBINED_PR4441_ARITHMETIC','source_head':'5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39','source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (SOURCE/name for name in SOURCE_FILES)},'engine':'Independent outward integer fixed-point intervals in units10^-60; atanh logarithm80terms with exact remainder; exponential160terms with exact geometric remainder. No source interval code imported.','profile_matches_independent_controller':True,'alpha':show(alpha),'gamma':show(gamma),'delta':show(delta),'normalized_paid_bound':str(bound),'eta':show(eta),'compiler_H':H,'root_bracket_signs':root_signs,'fixed_profile_ceiling':profile_ceiling,'ordinary_BIT':str(ordinary),'outer_counts':{'strict':54,'functional':4},'refined_alpha_at_C_003001054':show(refined_alpha),'scope':'Independent arithmetic and written substitution audit, retaining the already audited native source and all-column/physical/analytic/precision/stock/tape/recovery premises. The153 active ambient is not independently reconstructed here; parent keeps conservative281. Full source verifiers are not rerun in this audit.'}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-result',action='store_true')
args=parser.parse_args()
if args.write_result:
    (HERE/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
else:
    need(result==json.loads((HERE/'AUDIT.json').read_text()),'Entire independent frontier audit receipt reproduced')
print(json.dumps({'status':result['status'],'normalized_paid_bound':str(bound),'compiler_H':H,'ordinary_BIT':str(ordinary),'refined_alpha':show(refined_alpha)},indent=2))
