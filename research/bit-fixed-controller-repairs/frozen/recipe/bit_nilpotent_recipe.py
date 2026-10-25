#!/usr/bin/env python3
"""Fixed routed recipe over F2[N]/(N^2-1); not a changed-caller obstruction.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse,ast,json
from hashlib import sha256
from pathlib import Path
from bit_seeded_star import mul,plus,scale,ident,need
HERE=Path(__file__).resolve().parent
SOURCE=Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py')
def rank(rows):
 d={}
 for x in rows:
  while x:
   k=x.bit_length()-1
   if k in d:x^=d[k]
   else:d[k]=x;break
 return len(d)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 raw=SOURCE.read_bytes();t=ast.parse(raw);f=next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name=='recipe');env={};exec(compile(ast.Module(body=[f],type_ignores=[]),str(SOURCE),'exec'),env)
 cases=[]
 for B in range(1,7):
  n=2*B;z=ident(n);events=env['recipe'](B)
  for e in events:
   if e['kind']=='local':
    i=2*e['pair'];x,y=z[i],z[i+1]
    if e['reverse']:z[i]=plus(scale(x,2),y)
    else:z[i+1]=plus(x,scale(y,2))
   elif e['kind']=='bridge':
    d,s=e['dst'],e['src'];z[2*d]=plus(z[2*d],z[2*s]);z[2*s+1]=plus(z[2*s+1],z[2*d+1])
   elif e['kind']=='exchange':z=[r for j in range(B)for r in(z[2*j+1],z[2*j])]
  need(all(((x&1)^(x>>1))==int(i==j)for i,r in enumerate(z)for j,x in enumerate(r)),'constant epsilon0 endpoint I')
  A=[[x>>1 for x in r]for r in z];M=[[x^int(i==j)for j,x in enumerate(r)]for i,r in enumerate(A)]
  rA=rank([sum(x<<j for j,x in enumerate(r))for r in A]);rM=rank([sum(x<<j for j,x in enumerate(r))for r in M]);trace=sum(M[i][i]for i in range(n))%2
  cases.append({'B':B,'events':events,'raw_endpoint_ring_entries':z,'epsilon_matrix_A':A,'relative_to_common_N_defect_M':M,'rank_A':rA,'rank_defect_M':rM,'trace_defect':trace})
 need([c['rank_defect_M']for c in cases]==[2,3,6,7,10,11],'fixed recipe defect ranks')
 out={'status':'PASS_FIXED_RECIPE_NILPOTENT_DEFECT_MATRICES','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','source_recipe_sha256':sha256(raw).hexdigest(),'cases':cases,
 'ring':'F2[N]/(N^2-1), epsilon=N+1, epsilon^2=0. F=[[1,0],[1,N]], B=[[N,1],[0,1]]. All old bridges and terminal bank exchange are literally retained.',
 'rank_repair_bound':'For this fixed evaluated word R=I+epsilon A, its defect relative common parent N I is I+epsilon(A+I). Repair gates consisting of a scalar-GL-conjugated single-bank N have first-order rank1; k such added gates sum at most rankk. Thus repairing the fixed B4 word needs at least7 such extra N events (777 rank1 for111ports). This statement is not about a redesigned scalar controller that changes existing query pullbacks.',
 'parity':'Each such repair projector has trace1. The fixed defect trace is1, so the number of repair N events is odd. At B1 rank2 plus trace1 gives minimum at least3.',
 'all_size_scope':'Polynomial identity for every nonidentity involution N over characteristic2. No finite Fourier kernel expansion is used.',
 'limits':['Changed bank pairing, shared native stages, source normalization and altered scalar controls can change A and are outside this fixedrecipe bound.','No all-caller lower bound or negative kappa claim follows.','The seeded-star construction is an explicit changed topology and is deliberately outside this screen.']}
 out=json.loads(json.dumps(out));p=HERE/'BIT-NILPOTENT-RECIPE.json'
 if a.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(p.read_bytes())==out,'stored nilpotent recipe differs')
 print(out['status']);print('B1..6 defectranks2,3,6,7,10,11')
if __name__=='__main__':main()
