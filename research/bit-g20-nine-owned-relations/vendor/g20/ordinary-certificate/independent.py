"""Separate census and exact rational series; does not import certificate.py.

Retained exact_series supplies a different positive-series engine. Every
tail, compiler integer and finite backend separator is rederived here.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
def need(c,m):
 if not c:raise ValueError(m)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def series():
 p=HERE/'inputs'/'separate_series.py';s=importlib.util.spec_from_file_location('g20_separate_positive_series',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def check_arithmetic(T,P,params):
 X=series();c,u0,gap,ag,rho=[F(params[k])for k in('tested','uniform','cover_gap','alpha_gap','rho')];u=F(params['u']);v=params['v'];cut=params['cutoff'];floor=params['floor'];t=1-c
 target=X.moment(T,t);paid=X.moment(P,t);alpha=X.div(paid,target);gamma=X.div(X.moment(P,t+u),X.mul(X.power(cut,u),target));delta=X.div((F(sum(T.values())*floor),)*2,X.mul(X.power(cut,c),target))
 need(alpha[1]<1-ag and gamma[1]<F(31,32)and delta[1]<F(19,20),'Independent complete three-tail price')
 need(F(31,32)**128<F(1,16)and F(19,20)**128<F(1,16),'Both exact decay blocks')
 surplus=1-F(1)/(1+v*ag)-F(4,2**32);need(surplus>0,'Independent sum of original and completion tails')
 z=1-u0;z0=(t+z)/2;d=z0-t;h=F(1,64);need(d>0,'Positive finite compiler gap');H0=X.ceil((d*(5+8*h)*v+1+8*v*(1-z0))/(h*d));H1=X.floor(H0*(1-z0)/(z-z0))+1
 need(H0>=8*v and H0*h*d>=d*(5+8*h)*v+1+8*v*(1-z0)and H1*(z-z0)>H0*(1-z0),'Independent finite rank compiler')
 need(cut**64<floor**63 and max(T)<256,'After completion and splitting strict source/exit ranks')
 C1=u0-gap;need(c>u0>C1>0 and F(params['prime_coefficient'])*gap>256,'Full fallback prime allowance')
 backend=F(1737729,500000000);levels=[]
 for j in range(3):
  a=(1-rho)*C1+rho*backend;b=F(X.floor(a*params['grid']),params['grid'])
  need(backend<b<a<C1<rho<1-a,'Independent causal bootstrap and root costs')
  levels.append((backend,a,b));backend=b
 return {'alpha':alpha,'gamma':gamma,'delta':delta,'surplus':surplus,'H0':H0,'H1':H1,'C1':C1,'levels':levels,'admitted':backend,'relative_gain':backend/F(1737729,500000000)-1}
def inverse(a):
 n=len(a);w=[r[:]+[F(i==j)for j in range(n)]for i,r in enumerate(a)]
 for j in range(n):
  p=next(i for i in range(j,n)if w[i][j]);w[j],w[p]=w[p],w[j];x=w[j][j];w[j]=[v/x for v in w[j]]
  for i in range(n):
   if i!=j:
    x=w[i][j];w[i]=[v-x*z for v,z in zip(w[i],w[j])]
 return [r[n:]for r in w]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def base_height(provider):
 frames=read(provider.parent/'inputs'/'FRAMES.json')['frames'];maxbits=0;projectors=0
 def account(x):
  nonlocal maxbits
  x=F(x);maxbits=max(maxbits,abs(x.numerator).bit_length(),x.denominator.bit_length())
 for f in frames.values():
  b=[[F(x)for x in r]for r in f['B']]
  if not b:continue
  p=mm(mm(list(map(list,zip(*b))),inverse(mm(b,list(map(list,zip(*b)))))),b)
  for row in b+p:
   for x in row:account(x)
  projectors+=1
 for req in read(provider.parent/'inputs'/'G22-FRESH-REQUESTS.json'):
  for k in('projector','matcher_S','matcher_inverse'):
   for row in req[k]:
    for x in row:account(x)
 for port in read(provider/'data'/'PORT-CHARTS.json'):
  for row in port['rho15']:
   for x in row:account(x)
 for f in read(provider/'data'/'PARTIAL-JOB-MATCHERS.json').values():
  for k in('native_P','S_Q4_to_native','S_inverse'):
   for row in f[k]:
    for x in row:account(x)
 # Residuals subtract two frame projectors. Rational subtraction at most
 # doubles the per-entry height plus2; the raw VALUE envelope has485bits.
 bound=max(2*maxbits+2,485);need(bound<1024,'New base matrix/envelope rational height below1024bits')
 return {'frame_projectors':projectors,'largest_checked_rational_entry_bits':maxbits,'residual_and_VALUE_envelope_bits_upper':bound,'charged_base_height_bits':1024}
def audit(provider,result):
 provider=Path(provider);P=Counter()
 with gzip.open(provider/'data'/'GLOBAL.jsonl.gz','rb')as file:
  for line in file:
   e=json.loads(line);k=e[0]
   if k=='LOCAL_QUERY':P[e[5]]+=1
   elif k=='LOCAL_COPY_QUERY':P[e[6]]+=1
   elif k=='PAID_WHOLE_IDLE':P[e[3]]+=1
   elif k=='THIN_PAID_QUERY':P[e[4]]+=1
 owners=read(provider/'data'/'TARGET-OWNERS.json');need(len(owners)==len({r['original_owner']for r in owners})==11400,'All original target owners')
 T=Counter(r['rank']for r in owners);need(sum(P.values())==57321 and P==Counter({int(k):v for k,v in result['invoice']['paid'].items()})and T==Counter({int(k):v for k,v in result['invoice']['targets'].items()}),'Independent literal native stream P and actual target T')
 p=result['params'];ar=check_arithmetic(dict(T),dict(P),p);need(ar['H0']==result['tail']['new_H0']and ar['H1']==result['tail']['new_H1']and str(ar['C1'])==result['C1']and str(ar['admitted'])==result['admitted'],'Independent compiler and exact saving')
 for name in('alpha','gamma','delta'):
  display=result['tail'][name];need(F(display['lower'])<=ar[name][0]<=ar[name][1]<=F(display['upper']),'Independent outward interval within credited display '+name)
 for i,(backend,a,b)in enumerate(ar['levels']):
  saved=result['finite_backend_levels'][i];need(tuple(map(F,(saved['completed_backend'],saved['ordinary_exact'],saved['admitted'])))==(backend,a,b),'All exact finite stage quantities')
 negatives={}
 for name,changes in [('unfunded_alpha',{'alpha_gap':'1/10000000'}),('underfunded_prime',{'prime_coefficient':2**30})]:
  try:check_arithmetic(dict(T),dict(P),dict(p,**changes))
  except ValueError as error:negatives[name]=str(error)
  else:raise ValueError('Independent mutation survived '+name)
 need(F('.00347611042')>ar['C1'],'Raw root overclaim would exceed covered body saving');negatives['rawroot_as_ordinary']='REJECT: exceeds even covered body C1'
 old=read(HERE/'inputs'/'PR4814-RESULT.json');oldH0=old['new_H0'];t=1-F(p['tested']);z=1-F(p['uniform']);z0=(t+z)/2;d=z0-t
 need(oldH0*F(1,64)*d<d*(5+F(8,64))*p['v']+1+8*p['v']*(1-z0),'Old H0 no longer passes new compiler induction');negatives['old_compiler_threshold']='REJECT'
 fb=result['fee_bounds'];counts=fb['base_counts'];need(counts['parent_parking_FIELD_passes']==4*11402*57321>10**9 and counts['coarse_base_primitive_descriptions_including_local_dimension_work']<2**64,'Positive parking exceeds old cap, new explicit envelope')
 return {'status':'PASS_INDEPENDENT_LITERAL_P_T_THREE_TAILS_BOOTSTRAP_AND_BASE_HEIGHT','all_originals':sum(T.values()),'actual_queries':sum(P.values()),'H0':ar['H0'],'H1':ar['H1'],'admitted':str(ar['admitted']),'relative_gain':str(ar['relative_gain']),'rational_height':base_height(provider),'negative_controls':negatives,'not_materialized':'Astronomical uniform programme and new fixed machine threshold; retained source assumptions are explicit.'}
