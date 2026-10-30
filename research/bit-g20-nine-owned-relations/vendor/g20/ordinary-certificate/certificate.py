"""Exact new-P/T tails and three acyclic completed ordinary backends."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,importlib.util,json,sys
from fee_bounds import certify as certify_fees
HERE=Path(__file__).resolve().parent
def need(c,m):
 if not c:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def encode(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [encode(v)for v in x]
 return x
def ceil(x):return -((-x.numerator)//x.denominator)
PARAMS={'tested':F('.00347611041'),'uniform':F('.00347611040'),'cover_gap':F(1,2**36)+F(1,10**20),'alpha_gap':F(1,2**39),'prime_coefficient':2**45,'rho':F(1,100),'v':1024,'cutoff':17,'floor':18,'u':F(1,5),'grid':10**12}
def run(params=None):
 p=dict(PARAMS if params is None else params);inp=HERE/'inputs';invoice=read(inp/'provider-INVOICE.json');fees=read(inp/'provider-FULL-FEES.json');native=read(inp/'provider-RESULT.json');old=read(inp/'PR4814-RESULT.json')
 need(native['status']=='PASS_PRIVATE_NATIVE_CANDIDATE_READY_FOR_ORDINARY_CERTIFICATE','Sealed actual provider required')
 T={int(k):v for k,v in invoice['targets'].items()};P={int(k):v for k,v in invoice['paid'].items()};need(sum(T.values())==invoice['originals']==11400 and sum(P.values())==57321,'Complete original/helper/owned paid invoice')
 need(P[1]==25389 and P[3]==1386 and P[4]==720 and T[4]==72 and T[8]==7776,'New exact retiming/partial-helper invoice')
 E=load('g20_credited_intervals',inp/'credited_intervals.py');t=1-p['tested'];target=E.moment(T,t);paid=E.moment(P,t)
 alpha=E.divide(paid,target);gamma=E.divide(E.moment(P,t+p['u']),E.mul(E.power(p['cutoff'],p['u']),target));delta=E.divide((F(sum(T.values())*p['floor']),)*2,E.mul(E.power(p['cutoff'],p['tested']),target))
 need(alpha[1]<1-p['alpha_gap']and gamma[1]<F(31,32)and delta[1]<F(19,20),'All three charged tails')
 need(F(31,32)**128<F(1,16)and F(19,20)**128<F(1,16),'Both exact decay blocks')
 surplus=1-F(1)/(1+p['v']*p['alpha_gap'])-F(4,2**32);need(surplus>0,'Contraction includes original and both completion tails')
 need(p['cutoff']**64<p['floor']**63 and max(T)<256,'Charged completion/splitting strict ranks')
 h=F(1,64);z=1-p['uniform'];z0=(t+z)/2;gap=z0-t;need(gap>0,'Fresh uniform strict gap')
 H0=ceil((gap*(5+8*h)*p['v']+1+8*p['v']*(1-z0))/(h*gap));H1=(H0*(1-z0)/(z-z0)).__floor__()+1
 need(H0>=8*p['v']and H0*h*gap>=gap*(5+8*h)*p['v']+1+8*p['v']*(1-z0)and H1*(z-z0)>H0*(1-z0),'New effective integer compiler')
 C1=p['uniform']-p['cover_gap'];need(p['tested']>p['uniform']>C1>0 and F(p['prime_coefficient'])*p['cover_gap']>256,'Positive uniform and full cover fallback gaps')
 need(F(old['admitted'])==F(1737729,500000000),'Completed PR4814 base supplier, not raw root')
 backend=F(old['admitted']);levels=[]
 for j in range(1,4):
  a=(1-p['rho'])*C1+p['rho']*backend;scaled=a*p['grid'];b=F(scaled.__floor__(),p['grid'])
  need(backend<b<a<C1<p['rho']<1-a,'Finite bootstrap/adapter/stock strict gaps')
  levels.append({'level':j,'completed_backend':backend,'ordinary_exact':a,'admitted':b,'margins':{'adapter':p['rho']-a,'stock':1-p['rho']-a,'relaxation':a-b},'algorithm_order':'Freeze A_(j-1), then compile A_j with new fixed source/tape/height/ROW constants; never call A_j as its own atom backend.'});backend=b
 bounds=certify_fees(fees,invoice,H1,p['v']);comparator=F(1737729,500000000)
 return encode({'status':'PASS_CONDITIONAL_G20_ORDINARY_THREE_FINITE_LEVELS','native_runtime_manifest':native['runtime_manifest'],'invoice':invoice,'params':p,'tail':{'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),'ratios_exact_intervals':{'alpha':alpha,'gamma':gamma,'delta':delta},'normalized_surplus_lower':surplus,'target_completion':'Every product target below18^1024 gets a paid complementary job on that SAME owner','paid_splitting':'Every old and added paid job split at17^1024, all pieces charged','new_H0':H0,'new_H1':H1,'new_N':'2^'+str(H1),'scope':'Rank-compiler bounds; positive machine/ROW/stock thresholds are newly generated separately.'},'C1':C1,'finite_backend_levels':levels,'admitted':backend,'comparator':comparator,'relative_gain':backend/comparator-1,'relative_gain_percent':100*(backend/comparator-1),'qualifies_0_1_percent_public_guard':backend/comparator-1>=F(1,1000),'fee_bounds':bounds,'whole_kappa':None,'publication':'Private candidate only; no new PR or modifications of published/frozen trees.','retained_assumptions':'Same completed arbitrary-input/all-width ROW/spectator/weighted-leaf/native/finite-compiler/precision/fixed-tape contracts as PR4760/4814. Final astronomical uniform programme not materialized.'})
if __name__=='__main__':print(json.dumps(run(),indent=2))
