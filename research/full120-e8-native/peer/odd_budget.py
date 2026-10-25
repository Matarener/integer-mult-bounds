"""Exact rational price screen for a declared odd-factor native/caller hypothesis."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
from hashlib import sha256
import json,argparse,importlib.util,sys
D=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('full120_price_bounds',D/'check.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def calculate():
 records=[]
 for k in [3,5,7,9]:
  n=8*k+1;target=24*k+1;t=(k+1)//2;p=F(1,15);rho=sum((F(comb(k,j))*p**j*(1-p)**(k-j)for j in range(t,k+1)),F())
  L,U=m.power(target);L*=F(2,3);U*=F(2,3);profile=[3*k-1,3*k,5*k,5*k+1]
  for r in profile:
   a,b=m.power(r);L-=b;U-=a
  a,b=m.power(n);L-=rho*b;U-=rho*a
  eig={j:2*sum((F(comb(j,l))*F(15,2)**l*F(-13,2)**(j-l)for l in range(t,j+1)),F())for j in range(k+1)}
  m.need(all(eig[j]==0 for j in range(t))and all(eig[j]not in[0,1]for j in range(t,k+1)),'spectral rank and invertible I-C')
  rec={'odd_factors':k,'local_axes':n,'three_stage_target_axes':target,'declared_native_profile_per_owner_per_call':profile,'C_rank_over_V':str(rho),'C_spectral_eigenvalues_by_active_factors':{str(j):str(v)for j,v in eig.items()},'conditional_margin_per_owner_per_call':m.rounded((L,U)),'status':'POSITIVE_CONDITIONAL_MARGIN'if L>0 else'NEGATIVE_EVEN_WITH_ZERO_EXTRA_DECODER_COST'}
  if L>0:
   lo,hi=3*L/rho,3*U/rho;rec['whole_N3_H1_allowance_per_mode']=m.rounded((lo,hi));a,b=m.power(n);rec['full_Hn_query_integer_allowance_per_mode']=(lo/b).__floor__();m.need(hi/a<rec['full_Hn_query_integer_allowance_per_mode']+1,'strict fullquery threshold')
  else:m.need(U<0,'strict negative sign')
  records.append(rec)
 m.need(records[1]['full_Hn_query_integer_allowance_per_mode']==3,'k5 conditional allowance threeH41')
 return {'schema':'full120-odd-factor-conditional-budget/v1','status':'PASS_EXACT_RATIONAL_DECLARED_PROFILE_SCREEN','kappa':'605457647/200000000000','records':records,'native_k5_or_k7_program_executed':False,'negative_paid_decoder_constructed':False,'scope':'Only the declared 3-call main targets, native profile and mode-rank formula are priced. The n25/k3 primitive has separate emitted evidence. This file does not supply k5/k7 physical native templates, their E input acquisition/precision, a decoder, productive target admission or a new kappa.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=json.loads(canon(calculate()));p=D/'ODD-BUDGET.json'
 if a.write:p.write_bytes(canon(r))
 else:m.need(json.loads(p.read_bytes())==r,'read-only exact budget')
 print(json.dumps({'status':r['status'],'scientific_payload_sha256':sha256(canon(r)).hexdigest(),'k5_conditional_extra_H41_per_mode':3,'negative_decoder_constructed':False},sort_keys=True))
