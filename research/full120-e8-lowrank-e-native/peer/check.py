"""Separate exact physical base120 macro replay on six original columns.

No author script is imported. A shared signed-tableau primitive and separate
polynomial affine phase oracle interpret actual literal address words.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
from itertools import product
import argparse,gzip,importlib.util,json,sys
D=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def calculate():
 ce=load('physical120_macro_ce',D/'inputs/clifford_exact.py');ao=load('physical120_macro_affine',D/'inputs/affine_oracle.py');n=9
 def data(name):return json.loads(gzip.decompress((D/'inputs'/name).read_bytes()))
 p=data('MACROS120-PROGRAM.json.gz');native=data('NATIVE120-NATIVE-PROGRAM.json.gz');kernel=data('KERNEL-PROGRAM.json.gz')
 need(sha256(canon(p)).hexdigest()=='bea35cef68dc0fc09b7c8fbb590a2f84e63929ca2fd3057d6df00867fa376560','actual literal macro science pin')
 need(sha256(canon(native)).hexdigest()=='87d7cad7133ed0a2950b1d4fa2397e20e3c7bcedb90db95a15130aa03da543ae','native science pin')
 need(sha256(canon(kernel)).hexdigest()=='0b526f1a38a73a82ae66e1b0182ed2fa8c14e16d703cd38fff4dc491d3b7c15b','owner kernel science pin')
 need(p['native_science_sha256']==sha256(canon(native)).hexdigest(),'macro binds actual native')
 def literal(w):
  U=ce.ident(n)
  for e in w:
   if e[0]=='P':V=ce.perm(n,e[1])
   elif e[0]=='D':V=ce.diag(n,e[1],e[2])
   elif e[0]=='X':V=ce.xgate(n,e[1])
   elif e[0]=='C':V=ce.fourier(n,e[1]) if isinstance(e[1],list) else ce.cgate(n,e[1],e[2])
   else:need(e[0]=='phase','literal primitive');V=ce.Op(n,ce.identity(n),[tuple(e)])
   U=U.then(V)
  return U
 ops={k:literal(w)for k,w in p['definitions'].items()}
 L={int(i):literal(native['definitions'][k])for i,k in native['normalizer_words'].items()}
 G=ce.fourier(n,list(range(1,n)));Q=ce.fourier(n,[0]);R=ce.fourier(n)
 M=kernel['root_M120x8'];K={(int(i),j):F(a,b)for i,row in native['literal_scalar_K_rows'].items()for j,a,b in row}
 C={(i,j):sum(F(a)*F(b)for a,b in zip(M[i],M[j]))/4 for i in range(120)for j in range(120)}
 coefficients={False:{(i,j):K.get((i,j),F())+C[i,j]/14 for i in range(120)for j in range(120)},True:{(i,j):K.get((i,j),F())+C[i,j]for i in range(120)for j in range(120)}}
 # Operators with equal signed tableau differ by a global mu4 phase. Fold
 # that phase into exact rational complex coefficients to permit cancellation.
 registry={};phasecache={};composition={}
 def reg(U):
  tab=tuple(tuple(r)for r in U.tab)
  ck=canon(U.circuit)
  if ck not in phasecache:
   need(ao.tableau_from_word(U.circuit,n)==tab,'independent literal signed tableau')
   phasecache[ck]=ao.anchor(U)['mu4_phase']
  phase=phasecache[ck]
  if tab not in registry:registry[tab]=(U,phase)
  return tab,(phase-registry[tab][1])%4
 def turn(z,k):
  a,b=z;return [(a,b),(-b,a),(-a,-b),(b,-a)][k%4]
 def plus(dst,src,q=F(1)):
  for k,(a,b)in src.items():
   x,y=dst.get(k,(F(),F()));z=(x+q*a,y+q*b)
   if z==(0,0):dst.pop(k,None)
   else:dst[k]=z
 def unary(src,U,uid):
  out={}
  for k,z in src.items():
   pair=(uid,k)
   if pair not in composition:composition[pair]=reg(registry[k][0].then(U))
   t,phase=composition[pair];a,b=turn(z,phase*width);x,y=out.get(t,(F(),F()));out[t]=(a+x,b+y)
  return{k:z for k,z in out.items()if z!=(0,0)}
 iid,ip=reg(ce.ident(n));need(ip==0,'identity phase')
 main=[tuple(f)for f in p['main']]
 def replay(word,column):
  vals={f:({iid:(F(1),F())}if f==column else{})for f in main};bill=Counter();peak=0
  for e in word:
   op=e[0];f=tuple(e[1]);need(f in vals or op in['OWN_ZERO','COPY'],'initialized field')
   if op in['OWN_ZERO','COPY']:
    need(f not in vals and f not in main,'fresh owned allocation');vals[f]={}if op=='OWN_ZERO'else dict(vals[tuple(e[2])]);peak=max(peak,len(vals)-len(main))
   elif op=='CLEAR':need(f not in main,'owned-only clear');del vals[f]
   elif op=='SWAP':g=tuple(e[2]);vals[f],vals[g]=vals[g],vals[f]
   elif op=='SCALE':q=F(e[2],e[3]);vals[f]={k:(q*a,q*b)for k,(a,b)in vals[f].items()if q}
   elif op=='ADD':plus(vals[f],vals[tuple(e[2])],F(e[3],e[4]))
   else:
    need(op=='U','known macro grammar');vals[f]=unary(vals[f],ops[e[2]],e[2]);bill.update([e[3]]if e[3]else[])
  need(set(vals)==set(main),'owned fields all discharged')
  return vals,bill,peak
 def term(q,U):
  if not q:return{}
  k,ph=reg(U);return{k:turn((q,F()),ph*width)}
 tested=[];blocks=0;zero=0
 for width,orientation,role,j in product([1,2,3,4],['backward','forward'],['X','Y'],[0,112,119]):
  column=(role,j);vals,bill,peak=replay(p[orientation],column);need(bill==Counter({2:120,3:120,5:120,6:120,9:8}),'actual complete paid invoice')
  for outrole,i in main:
   q=F();U=ce.ident(n)
   if orientation=='backward':
    q=coefficients[True][i,j]
    if outrole=='X'and role=='X':U=G.then(L[j]).then(L[i].adjoint())
    elif outrole=='X'and role=='Y':q=-q;U=R.then(L[j]).then(L[i].adjoint())
    elif outrole=='Y'and role=='Y':U=L[j].then(L[i].adjoint()).then(G)
    else:q=F()
   else:
    q=coefficients[False][i,j]
    if outrole=='X'and role=='X':U=G.then(L[j]).then(L[i].adjoint())
    elif outrole=='Y'and role=='X':U=Q.adjoint().then(L[j]).then(L[i].adjoint()).then(G)
    elif outrole=='Y'and role=='Y':U=L[j].then(L[i].adjoint()).then(G)
    else:q=F()
   need(vals[outrole,i]==term(q,U),'complete physical macro block '+str((width,orientation,column,(outrole,i))))
   blocks+=bool(q);zero+=not bool(q)
  tested.append({'width_residue':width%4,'orientation':orientation,'original_column':list(column),'peak_owned':peak,'paid':dict(bill)})
 # A final phase-i change has exactly the same signed tableau, but fails the
 # independent absolute phase comparison on an actual nonzero returned block.
 k=next(iter(registry));U=registry[k][0];bad=U.then(ce.Op(n,ce.identity(n),[('phase',1)]));kb,ph=reg(bad);need(kb==k and ph==1,'same tableau absolute-phase mutant detected')
 return {'status':'PASS_SEPARATE_PHYSICAL_BASE120_E_MACRO_COLUMNS','macro_science_sha256':sha256(canon(p)).hexdigest(),'tests':tested,'nonzero_blocks':blocks,'zero_blocks':zero,'original_columns':6,'orientations':2,'width_residues':[0,1,2,3],'phase_i_mutant_rejected':True,'author_scripts_imported':False,'shared_Clifford_primitive':True,'independent_phase_backend':'polynomial affine support','scope':'Full literal forward/backward macro on six selected actual original inputs (old root0 and added roots112,119 in both banks). All240 returned fields and owned lifetimes checked for each, in all four tensor width phase residues; owner scalar coefficients apply once. Not all240 input columns, no dense address matrix, no independent n25 or whole-caller proof.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=json.loads(canon(calculate()));path=D/'RESULT.json'
 if a.write:path.write_bytes(canon(r))
 else:need(json.loads(path.read_bytes())==r,'read-only peer receipt')
 print(json.dumps(r,sort_keys=True))
