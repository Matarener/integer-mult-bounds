"""Literal owned E correction, inverse contact snapshots and transpose.

The four independent main fields have two address axes. All16 arbitrary
main input columns are propagated simultaneously over Q(i), with exact
absolute phases. This fixture does not stand in for the global phase proof.
"""
import argparse,hashlib,json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import importlib.util,sys
_spec=importlib.util.spec_from_file_location("owned_e_exact",Path(__file__).with_name("e_adapter.py"));_ea=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=_ea;_spec.loader.exec_module(_ea)
for _name in ["C","cv","zeros","ident","add","scale","mul","prod","block","diag","lower","upper","need"]:globals()[_name]=getattr(_ea,_name)
HERE=Path(__file__).resolve().parent
MAIN=['X0','X1','Y0','Y1'];N=4
I4=ident(4);P=zeros(4)
for x in range(4):P[((x&1)<<1)|((x>>1)&1)][x]=C(1)
def translation(q):
 O=zeros(4)
 for x in range(4):O[x^q][x]=C(1)
 return O
def gate(q,s=1):return add(scale(C(F(1,2),F(s,2)),I4),scale(C(F(1,2),F(-s,2)),translation(q)))
MAP={'I':I4,'P':P,**{'X'+str(q):translation(q)for q in [1,2,3]},'C0':gate(1),'C1':gate(2),'R':mul(gate(1),gate(2))}
def left(A,B):return [[sum((A[i][k]*B[k][j]for k in range(len(A))),C())for j in range(len(B[0]))]for i in range(len(A))]
def ownzero():return [[C()for j in range(16)]for i in range(4)]
def coded(bank,a,b,label):
 f,g=bank;u,v=label+'a',label+'b'
 return [['COPY',u,f],['COPY',v,g],['SCALE',f,a.numerator,a.denominator],['SCALE',g,a.numerator,a.denominator],['ADD',f,v,b.numerator,b.denominator,'P'],['ADD',g,u,b.numerator,b.denominator,'P'],['CLEAR',u],['CLEAR',v]]
def modes(lam,sign,label):
 # FC=(lambda/2)[I;-P][I,-P]. Source Y is read before any overwrite.
 g=label+'g'
 return [['OWN_ZERO',g],['ADD',g,'Y0',1,1,'I'],['ADD',g,'Y1',-1,1,'P'],['PAID',g,'R',2],['ADD','X0',g,(sign*F(lam,2)).numerator,(sign*F(lam,2)).denominator,'I'],['ADD','X1',g,(-sign*F(lam,2)).numerator,(-sign*F(lam,2)).denominator,'P'],['CLEAR',g]]
def nativeB():
 # Exact inverse-transpose of F=[[D,0],[Pswap,D]], with ordinary X powers.
 out=[['MONO',f,'X1']for f in ['X0','X1']]
 for f in ['Y0','Y1']:out.extend([['PAID',f,'C1',1],['MONO',f,'X2']])
 out.extend([['ADD','X0','Y1',-1,1,'P'],['ADD','X1','Y0',-1,1,'P']])
 for f in ['X0','X1']:out.extend([['PAID',f,'C1',1],['MONO',f,'X2']])
 out.extend([['MONO',f,'X3']for f in ['X0','X1']]);out.extend([['MONO',f,'X2']for f in ['Y0','Y1']])
 return out
def programs(lam):
 ei_a=F(lam,2);ei_b=1-ei_a;e_a=F(lam,2*(lam-1));e_b=F(lam-2,2*(lam-1))
 # Gather and transform the original Y mode first; retain it across nativeB.
 q=modes(lam,-1,'back_mode_');split=4
 back=q[:split]+coded(['Y0','Y1'],ei_a,ei_b,'by')+nativeB()+q[split:-1]+coded(['X0','X1'],ei_a,ei_b,'bx')+q[-1:]
 inv=coded(['X0','X1'],e_a,e_b,'ix')
 inv.extend([['MONO',f,'X2']for f in ['Y0','Y1']])
 inv.extend([['COPY','cache0','Y0'],['COPY','cache1','Y1']])
 inv.extend([['PAID',f,'C1',1]for f in ['Y0','Y1']])
 inv+=coded(['Y0','Y1'],e_a,e_b,'iy')+modes(lam,1,'inverse_mode_')
 inv.extend([['MONO',f,'X3']for f in ['X0','X1']]);inv.extend([['PAID',f,'C1',1]for f in ['X0','X1']])
 inv.extend([['ADD','X0','cache1',1,1,'P'],['ADD','X1','cache0',1,1,'P']])
 inv.extend([['MONO',f,'X1']for f in ['X0','X1']]);inv.extend([['CLEAR','cache0'],['CLEAR','cache1']])
 tr=[]
 for e in reversed(inv):
  if e[0]=='COPY':tr.extend([['ADD',e[2],e[1],1,1,'I'],['CLEAR',e[1]]])
  elif e[0]=='CLEAR':tr.append(['OWN_ZERO',e[1]])
  elif e[0]=='OWN_ZERO':tr.append(['CLEAR',e[1]])
  elif e[0]=='ADD':tr.append(['ADD',e[2],e[1],e[3],e[4],e[5]]) # I,P are symmetric.
  elif e[0]=='SCALE':tr.append(list(e))
  else:need(e[0]in ['MONO','PAID'],True,'transpose known symmetric fixture primitive');tr.append(list(e))
 forward=[['MONO',f,'X1']for f in ['X0','X1']]+tr+[['MONO',f,'X3']for f in ['X0','X1']]+[['MONO',f,'X2']for f in ['Y0','Y1']]
 return back,inv,tr,forward

def run(program,initial=None):
 vals={f:[[C(int(4*j+i==k))for k in range(16)]for i in range(4)]for j,f in enumerate(MAIN)}if initial is None else{f:[list(r)for r in initial[4*j:4*j+4]]for j,f in enumerate(MAIN)}
 live=set(MAIN);peak=0;paid=Counter();ops=Counter()
 for e in program:
  op=e[0];ops[op]+=1
  if op in ['OWN_ZERO','COPY']:
   f=e[1];need(f not in live and f not in MAIN,True,'owned destination must be fresh and zero')
   if op=='COPY':need(e[2]in live,True,'COPY source initialized');vals[f]=[list(r)for r in vals[e[2]]]
   else:vals[f]=ownzero()
   live.add(f);peak=max(peak,len(live)-4)
  elif op=='CLEAR':need(e[1]in live and e[1]not in MAIN,True,'owned only CLEAR after use');vals[e[1]]=ownzero();live.remove(e[1])
  elif op=='SCALE':need(e[1]in live,True,'SCALE initialized');vals[e[1]]=scale(F(e[2],e[3]),vals[e[1]])
  elif op=='ADD':
   f,g=e[1:3];need(f in live and g in live,True,'ADD initialized owned/source');vals[f]=add(vals[f],scale(F(e[3],e[4]),left(MAP[e[5]],vals[g])))
  else:
   need(op in ['MONO','PAID']and e[1]in live,True,'known initialized unary');vals[e[1]]=left(MAP[e[2]],vals[e[1]])
   if op=='PAID':paid[e[3]]+=1
 need(live,set(MAIN),'all owned temporaries cleaned')
 return sum([vals[f]for f in MAIN],[]),{'paid':dict(sorted(paid.items())),'ordinary':dict(sorted((k,v)for k,v in ops.items()if k!='PAID')),'peak_owned_fields':peak}
def matrix_json(M):return [[[str(z.a),str(z.b)]for z in r]for r in M]
def targets(lam):
 Q=diag(gate(1),gate(1));Qi=diag(gate(1,-1),gate(1,-1));D=diag(gate(2),gate(2));I=ident(8);Z=zeros(4)
 K=block(Z,P,P,Z);Pm=scale(F(1,2),add(I,scale(-1,K)));FC=scale(lam,Pm);A=add(I,scale(-1,FC));Ai=add(I,scale(F(lam,1-lam),Pm));E=mul(K,Ai);Ei=mul(K,A)
 HF=diag(E,prod(Qi,E,Q));HB=diag(Ei,prod(Qi,Ei,Q));WF=mul(HF,mul(diag(D,D),lower(Qi)));WB=mul(HB,mul(diag(D,D),upper(scale(-1,Q))))
 return WF,WB

def calculate():
 cases=[];payload=[]
 for lam in [15,F(225,2),-1350]:
  back,inv,tr,forward=programs(lam);B,bi=run(back);Bi,ii=run(inv);T,ti=run(tr);FF,fi=run(forward);WF,WB=targets(lam)
  need(B,WB,'literal owned backward E adapter all16 input columns and phases')
  need(mul(Bi,B),ident(16),'literal owned inverse left all16columns')
  need(mul(B,Bi),ident(16),'literal owned inverse right all16columns')
  need(T,list(map(list,zip(*Bi))),'literal owned transpose all256 operatorentries')
  need(FF,WF,'literal owned forward E adapter all16 inputcolumns absolutephase')
  need(bi['paid'],{1:4,2:1},'back paid native4H1 +rH2')
  need(ii['paid'],bi['paid'],'inverse same Gaussian paidprofile');need(fi['paid'],bi['paid'],'forward same Gaussian paidprofile')
  controls={}
  bad=[e for e in back if not(e[0]=='PAID'and e[2]=='R')];controls['missing_owned_R_query_rejected']=run(bad)[0]!=WB
  bad=[list(e)for e in forward];bad[-4]=['MONO','X0','X1'];controls['wrong_forward_Dsquare_boundary_rejected']=run(bad)[0]!=WF
  bad=[list(e)for e in inv];i=next(i for i,e in enumerate(bad)if e[0]=='COPY'and e[1]=='cache0');bad[i]=['OWN_ZERO','cache0'];controls['lost_actual_source_contact_rejected']=run(bad)[0]!=Bi
  bad=[list(e)for e in tr];i=next(i for i,e in enumerate(bad)if e[0]=='ADD');bad[i]=list(bad[i]);bad[i][3]=-bad[i][3];controls['wrong_transpose_ADD_sign_rejected']=run(bad)[0]!=T
  bad=[list(e)for e in inv];i=next(i for i,e in enumerate(bad)if e[0]=='ADD'and e[2]=='cache0');bad.insert(i,['CLEAR','cache0'])
  try:run(bad)
  except ValueError:controls['owned_source_early_CLEAR_rejected']=True
  need(all(controls.values())and len(controls)==5,True,'all physical/phase/owned controls')
  cases.append({'lambda':str(lam),'backward':bi,'inverse':ii,'transpose':ti,'forward':fi,'all16_arbitrary_main_columns_exact':True,'absolute_phases_exact':True,'all256_transpose_operator_entries_exact':True,'controls':controls,'backward_matrix_sha256':hashlib.sha256(json.dumps(matrix_json(B),separators=(',',':')).encode()).hexdigest(),'forward_matrix_sha256':hashlib.sha256(json.dumps(matrix_json(FF),separators=(',',':')).encode()).hexdigest()})
  payload.append({'lambda':str(lam),'backward':back,'inverse':inv,'transpose':tr,'forward':forward})
 result={'schema':'owned-E-adapter-fulloperator-fixture/v1','status':'PASS_LITERAL_BOTH_ORIENTATIONS_WITH_OWNED_SOURCE_CHECKPOINT','field_width':1,'address_axes':2,'arbitrary_independent_main_fields':4,'main_operator_dimension':16,'cases':cases,'scope':'Exact complete small noncommuting-Q full operators, with original source acquisition, same paid profiles, owned lifecycle and absolute phase. Global all-port implementation uses separate actual root512 native checkpoint proof and rational spectral mode theorem. No negative E terminal decoding or complete caller claimed.'}
 return json.loads(json.dumps(result)),json.loads(json.dumps(payload))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate();rpath=HERE/'OWNED-E.json';ppath=HERE/'OWNED-E-PROGRAM.json'
 if a.write:rpath.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');ppath.write_text(json.dumps(p,sort_keys=True,indent=2)+'\n')
 else:need(r,json.loads(rpath.read_bytes()),'read-only owned E receipt');need(p,json.loads(ppath.read_bytes()),'read-only owned E program')
 print(json.dumps(r,sort_keys=True))
