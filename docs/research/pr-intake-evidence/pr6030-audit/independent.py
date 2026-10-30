"""Independent PR6030 word, invoice, new native maps and funding audit.
Uses Matarener PR5960 replay and Clear1nsight dense interpreter; no author replay/pricing imports.
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
import importlib.util,json,gzip,sys,hashlib
BASE=Path(__file__).resolve().parent
ROOT=BASE/'source'
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def reject(f):
 try:f()
 except ValueError:return True
 raise ValueError('Mutation accepted')
M=load(ROOT/'research/p104-unread-rung-independent-audit/verify.py','independent5960')
P=ROOT/'research/p104-helper470-twin-rung-removal'
w=read(P/'WORD.json.gz');old=read(P/'inputs/pr5907-WORD.json.gz');res=read(P/'RESULT.json')
paid,helpers,spans,replay=M.replay(w,'6030')
p,t=M.invoice(paid,helpers);cost=res['complete_cost']
need(dict(p)=={int(k):v for k,v in cost['paid'].items()},'paid invoice')
need(dict(t)=={int(k):v for k,v in cost['targets'].items()},'target invoice')
need(sum(t.values())==13444 and sum(p.values())==66834,'complete inventory')
need(sum(r*n for r,n in t.items())-sum(r*n for r,n in p.items())==760,'rank surplus')
need(w['frames']==old['frames'] and w['live']==old['live'] and w['ports']==old['ports'],'unchanged frame geometry')
need({str(i):[old['initial'][i],w['initial'][i]] for i in range(w['public']) if old['initial'][i]!=w['initial'][i]}=={'713':[3,76],'736':[424,749]},'initial delta')
need({str(i):[old['final'][i],w['final'][i]] for i in range(w['public']) if old['final'][i]!=w['final'][i]}=={'115':[105,189]},'final delta')
oldpaid=Counter(abs(len(old['frames'][e[3]])-len(old['frames'][e[2]])) for e in old['program'] if e[0]=='MOVE')
need(M.diff(paid,oldpaid)==read(P/'EXPECT.json')['paid_delta'],'paid delta')
need(Counter(tuple(e) for e in w['program'] if e[0] in ('INIT','CLEAR','COPY'))==Counter(tuple(e) for e in old['program'] if e[0] in ('INIT','CLEAR','COPY')),'owned op multiset')
controls={}
for name,index in read(P/'EXPECT.json')['control_sites'].items():
 bad=json.loads(json.dumps(w));bad['program'].pop(index)
 controls[name]=reject(lambda:M.replay(bad,'mutation'))
for name,index in read(P/'EXPECT.json')['sign_sites'].items():
 bad=json.loads(json.dumps(w));bad['program'][index][-2]=str(-Q(bad['program'][index][-2]))
 controls['sign_'+name]=reject(lambda:M.replay(bad,'mutation'))
print('PASS independent word, chronology, endpoint, invoice and mutation checks',flush=True)
new=sorted(M.inventory(w)[0]-M.inventory(old)[0]);M._init(w['frames']);dense=[M.dense_task(task) for task in new]
# Independent dense phase-only negative control on a new paid map.
kind,a,b,_=next(x for x in new if x[0]=='move');C,V,Z=M._M['C'],M._M['V'],M._M['D']
rec,_=C.lower_child(C.canonical_frame(9,tuple(w['frames'][a])).adjoint().then(C.canonical_frame(9,tuple(w['frames'][b]))))
literal=V.adjoint(V.frame(w['frames'][a],9))+V.frame(w['frames'][b],9)
actual=V.recipe(rec);fault=actual+(('phase',1),)
need(V.tableau(actual)==V.tableau(fault) and Z.first_difference(fault,literal) is not None,'phase-only fault')
print('PASS all 512 columns of new native maps',len(dense),flush=True)
def dec(q):
 q=Q(q);return D(q.numerator)/D(q.denominator)
with localcontext() as ctx:
 ctx.prec=90
 k=dec(cost['kappa']);tested=dec(cost['strictification']['tested']);power=lambda r,x:(D(r).ln()*x).exp()
 moment=lambda hist,x:sum(D(n)*power(r,x) for r,n in hist.items())
 margin=lambda x:moment(t,1-x)-moment(p,1-x)
 lo,hi=map(dec,cost['raw_root_interval'])
 need(margin(lo)>D('1e-12') and margin(hi)<-D('1e-12'),'independent decimal root signs')
 target=moment(t,1-tested);alpha=moment(p,1-tested)/target
 gamma=moment(p,1-tested+dec('1/7'))/(power(16,dec('1/7'))*target)
 delta=D(sum(t.values())*17)/(power(16,tested)*target)
 need(alpha<1-D('1e-12') and max(gamma,delta)<dec('125/128'),'funding')
 need(D('.0034')>tested>k and margin(k)>0,'bit and claim slack')
 funding={k:str(v) for k,v in dict(alpha=alpha,gamma=gamma,delta=delta,lower_margin=margin(lo),upper_margin=margin(hi),claim_margin=margin(k)).items()}
# Independent exact integer completion and threshold checks.
need(Q(125,128)**128<Q(1,16),'decay block')
need(1/(1+1024*Q(1,10**12))+Q(4,2**32)<1,'completion')
need(16**64<17**63 and 2*(16**1024)**64<=(145**1024)**63,'splitting/complement')
gap=(Q(cost['strictification']['tested'])-Q(cost['kappa']))/7
H=int(cost['compiler']['H']);j=int(cost['compiler']['integer_test_exponent'])
need(gap.numerator==1 and H==gap.denominator*j,'threshold grid')
need((H+1)**1024<2**j and (gap.denominator*(j-1)+1)**1024>=2**(j-1),'threshold and predecessor')
output={'status':'PASS_INDEPENDENT_6030_WORD_NATIVE_INVOICE_FUNDING','replay':replay,'paid':dict(sorted(p.items())),'targets':dict(sorted(t.items())),'new_native_maps':dense,'controls':controls,'funding_decimal_diagnostic':funding,'compiler_integer_checks':True,'scope':'Own word/invoice checks via independent PR5960 implementation; all new maps densely checked. Decimal funding is corroboration, not replacement of retained exact rational engines. Five framework assumptions retained.'}
(BASE/'independent-result.json').write_text(json.dumps(output,indent=2)+'\n')
print(output['status'])
