"""Read emitted F/B independently; compare all original entries with affine phases."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import json,gzip,sys,importlib.util,argparse
D=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def calculate():
 ce=load('full120_affine_replay_CE',D/'inputs/clifford_exact.py');ao=load('full120_affine_replay_oracle',D/'inputs/affine_oracle.py')
 raw=(D/'inputs/NATIVE120-NATIVE-PROGRAM.json.gz').read_bytes();p=json.loads(gzip.decompress(raw));defs=p['definitions'];n=9;ports=p['port_order'];need(len(set(ports))==120,'all120 main owners')
 def literal(word):
  U=ce.ident(n)
  for e in word:
   if e[0]=='P':V=ce.perm(n,e[1])
   elif e[0]=='D':V=ce.diag(n,e[1],e[2])
   elif e[0]=='X':V=ce.xgate(n,e[1])
   elif e[0]=='C':V=ce.cgate(n,e[1],e[2])
   else:need(e[0]=='phase','known actual gate');V=ce.Op(n,ce.identity(n),[tuple(e)])
   U=U.then(V)
  return U
 ops={k:literal(w)for k,w in defs.items()};R=ce.fourier(n);Q=ce.fourier(n,[0]);G=ce.fourier(n,range(1,n));L={i:ops[k]for i,k in((int(i),k)for i,k in p['normalizer_words'].items())};K={int(i):{int(j):F(a,b)for j,a,b in row}for i,row in p['literal_scalar_K_rows'].items()}
 receipts=[];checks=0;mutant=False
 for orientation in ['forward','backward']:
  rows={(r,i):{(r,i):(F(1),ce.ident(n))}for r in ['X','Y']for i in ports};bill=Counter();charts={}
  for e in p[orientation+'_program']:
   if e[0]=='ADD':
    _,dr,di,sr,si,a,b,ch=e;target=(dr,di);source=(sr,si);need(charts.get(target)==charts.get(source)==ch,'same physical ADD chart')
    for col,(c,U)in rows[source].items():need(col not in rows[target],'no source interference');rows[target][col]=(c*F(a,b),U)
   else:
    field=(e[1],e[2])
    if e[0]=='MONOMIAL':
     U=ops[e[3]];need(not any(w[0]=='C'for w in defs[e[3]]),'ordinary wrapper explicit')
    else:
     need(e[0]=='PAID_PATH','known main-only program grammar');_,_,_,old,new,rec=e
     need(field not in charts or charts[field]==old,'actual chronological chart transition');charts[field]=new
     U=ops[rec['before_monomial']].then(ce.fourier(n,rec['child_axes'])).then(ops[rec['after_monomial']]);need(len(set(rec['child_axes']))==rec['rank'],'actual positive child axes');bill[rec['rank']]+=1
    rows[field]={col:(c,V.then(U))for col,(c,V)in rows[field].items()}
  for role in ['X','Y']:
   for i in ports:
    cross=(orientation=='forward'and role=='Y')or(orientation=='backward'and role=='X');source_role='X'if orientation=='forward'else'Y';expected={(role,i)}|({(source_role,j)for j in K[i]}if cross else set())
    need(set(rows[role,i])==expected,'all240 independent original columns and zero entries')
    for col,(coefficient,U)in rows[role,i].items():
     if col==(role,i):V=G;scalar=F(1)
     else:
      j=col[1];scalar=K[i][j]*(1 if orientation=='forward'else -1)
      V=(Q.adjoint().then(L[j]).then(L[i].adjoint()).then(G)if orientation=='forward'else L[j].then(L[i].adjoint()).then(Q).then(G))
     need(coefficient==scalar,'signed rational owner coefficient once')
     need(ao.canonicalize(U)==ao.canonicalize(V),'independent affine tableau and absolute column phase')
     checks+=1
     if not mutant and col!=(role,i):
      bad=U.then(ce.Op(n,ce.identity(n),[('phase',1)]));need(bad.tab==U.tab and ao.canonicalize(bad)!=ao.canonicalize(V),'same-tableau i phase mutation rejected');mutant=True
  need(bill==Counter({2:120,3:120,5:120,6:120}),'complete literal paid profile')
  receipts.append({'orientation':orientation,'paid_profile':dict(bill),'original_inputs':240,'all_zero_blocks_checked':True})
 need(checks==1440 and mutant,'complete both-orientation coverage')
 return {'status':'PASS_INDEPENDENT_FULL120_NATIVE_AFFINE_REPLAY','canonical_program_sha256':sha256(canon(p)).hexdigest(),'compressed_program_sha256':sha256(raw).hexdigest(),'absolute_phase_operator_blocks':checks,'same_tableau_phase_mutant_rejected':mutant,'orientations':receipts,'source_author_code_imported':False,'shared_exact_compiler':True,'phase_backend':'independent polynomial affine-support oracle','scope':'Entire emitted n9 F/B word on all original main columns. The n25 family and E decoder are separate checks. Tensor lifting follows exact operator equality; no whole multiplication theorem or new kappa.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=json.loads(canon(calculate()));f=D/'AFFINE-REPLAY.json'
 if a.write:f.write_bytes(canon(r))
 else:need(json.loads(f.read_bytes())==r,'read-only independent affine receipt')
 print(json.dumps(r,sort_keys=True))
