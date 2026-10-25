"""Exact coefficient-norm certificates for four chronological owner recoders."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse,gzip,json
HERE=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def transpose(word):
 return [['ADD',e[2],e[1],e[3],e[4]]if e[0]=='ADD'else e[:]for e in reversed(word)]
def measure(word,target):
 n=120;A=[[F(i==j)for j in range(n)]for i in range(n)];rows=[F(1)]*n;cols=[F(1)]*n;rowpeak=colpeak=productpeak=F(1);denbit=1;worst=-1
 for step,e in enumerate(word):
  if e[0]=='SWAP':
   i,j=e[1:];A[i],A[j]=A[j],A[i];rows[i],rows[j]=rows[j],rows[i];changed=[]
  else:
   i=e[1];old=A[i]
   if e[0]=='SCALE':v=F(e[2],e[3]);new=[v*x for x in old]
   else:j=e[2];v=F(e[3],e[4]);new=[x+v*y for x,y in zip(old,A[j])]
   A[i]=new;rows[i]=sum(map(abs,new));cols=[a+abs(y)-abs(x)for a,x,y in zip(cols,old,new)];changed=[i]
  r=max(rows);c=max(cols);p=r*c
  rowpeak=max(rowpeak,r);colpeak=max(colpeak,c)
  if p>productpeak:productpeak=p;worst=step
  for i in changed:denbit=max(denbit,max(x.denominator.bit_length()for x in A[i]))
 need(A==target,'full chronological elementary word equals target')
 endproduct=max(rows)*max(cols);axisbound=max(F(1),productpeak,endproduct)
 return {'operations':len(word),'max_prefix_row_l1':str(rowpeak),'max_prefix_column_l1':str(colpeak),'max_prefix_row_times_column':str(productpeak),'max_product_step_zero_based':worst,'endpoint_row_l1':str(max(rows)),'endpoint_column_l1':str(max(cols)),'endpoint_row_times_column':str(endproduct),'max_denominator_bitlength':denbit,'whole_three_axis_l2_amplification_squared_upper':str(axisbound*max(F(1),endproduct)**2)}
def calculate():
 raw=gzip.decompress((HERE/'KERNEL-PROGRAM.json.gz').read_bytes());p=json.loads(raw);T=[[F(x)for x in row]for row in p['T120']];Ti=[[F(x)for x in row]for row in p['T_inverse120']]
 cases=[('to_modal',p['to_modal_kernel_word'],Ti),('from_modal',p['from_modal_kernel_word'],T),('to_modal_transpose',transpose(p['to_modal_kernel_word']),[list(x)for x in zip(*Ti)]),('from_modal_transpose',transpose(p['from_modal_kernel_word']),[list(x)for x in zip(*T)])]
 return {'schema':'full120-owner-prefix-norm-peer/v1','program_canonical_sha256':sha256(canon(p)).hexdigest(),'status':'PASS_FOUR_EXACT_PREFIX_ORIENTATIONS','orientations':{name:measure(word,target)for name,word,target in cases},'scope':'Coefficient matrices on120 independent common-chart fields. Bounds are for field-l2 additive errors, independent of address width. Three-axis batches act on disjoint120-field blocks within each owner axis. No coordinate rounding allocation, source acquisition, Gaussian decoder, runtime theorem or exponent claim.'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');args=a.parse_args();r=calculate()
 if args.write:(HERE/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 else:need(json.loads((HERE/'RECEIPT.json').read_bytes())==r,'readonly exact prefix receipt')
 print(r['status']);print(json.dumps(r['orientations'],sort_keys=True))
