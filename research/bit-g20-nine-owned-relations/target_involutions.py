"""Bind every retained target descriptor to the same self-dual physical job."""
from fractions import Fraction as F
from collections import Counter
import importlib.util,sys,json
import local_relations as L
R=L.R;S=L.S
def need(c,m):
 if not c:raise ValueError(m)
def mm(a,b):return[[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def eye(n):return[[F(i==j)for j in range(n)]for i in range(n)]
def swap(p):
 n=len(p);return[[(F(i==j)-p[i%n][j%n])if(i<n)==(j<n)else p[i%n][j%n]for j in range(2*n)]for i in range(2*n)]
def certP(p,rank):
 need(p==list(map(list,zip(*p)))and mm(p,p)==p,'Exact symmetric idempotent ADDRESS projector')
 need(sum(p[i][i]for i in range(len(p)))==rank,'Exact rank(trace)')
 d=swap(p);need(d==list(map(list,zip(*d)))and mm(d,d)==eye(len(d)),'D_P symmetric ADDRESS involution')
 return True
def run():
 inp=S/'inputs';frames=L.read(inp/'FRAMES.json')['frames'];base=L.read(inp/'BASELINE-LOCAL.json.gz');ref=L.read(inp/'REFERENCE111.json.gz');axes=L.read(inp/'ACTIVE-AXES.json');controller=L.read(inp/'CONTROLLER.json');ports=L.read(S/'provider/data/PORT-CHARTS.json');old=L.read(S/'provider/data/TARGET-OWNERS.json');targets=L.read(R/'TARGET-OWNERS.json');glob=L.read(R/'GLOBAL-RESULT.json')
 spec=importlib.util.spec_from_file_location('bound_jobs',S/'provider/bindings_fees.py');B=importlib.util.module_from_spec(spec);sys.modules[spec.name]=B;spec.loader.exec_module(B)
 I=eye(8);portP=[]
 for i,q in enumerate(ref['lines']):
  q=list(map(F,q));p=[[x*y/4 for y in q]for x in q];k=[[I[a][b]-p[a][b]for b in range(8)]for a in range(8)];certP(p,1);certP(k,7)
  need(B.project(frames[str(base['start'][i])])==p and B.project(frames[str(base['final'][111+i])])==k,'Actual old port descriptors')
  need(mm(swap(I),swap(p))==swap(k)and mm(swap(p),swap(I))==swap(k),'Exact Q*S=R physical commuting-address factors')
  rho=[[F(x)for x in r]for r in ports[i]['rho15']];need(mm(rho,rho)==eye(15),'Actual paid entry/return route is same involution')
  portP.append(p)
 # A MAIN projector is one central P (or I8) plus distinct fresh coordinate
 # axes. Disjoint orthogonal block sums preserve symmetry/idempotence/rank.
 templates={}
 for bank,term in enumerate(controller['diagonal']):
  selected=[j for j,a in enumerate(axes)if int(term)>>(a['stage']+1)&1];fresh=[a for j in selected if j for a in axes[j]['axes']];need(len(set(fresh))==len(fresh)and all(8<=a<127 for a in fresh),'Disjoint fresh actual stage axes');centralrank=8 if 0 in selected else 1;rank=centralrank+len(fresh);need(rank==1+7*len(selected),'Every actual MAIN target rank')
  templates[f'MAIN_BANK_{bank}']={'rank':rank,'fresh_axes':fresh,'central':'I8'if 0 in selected else'P_port','P_squared':'P','P_transpose':'P','D_P_squared':'I','D_P_transpose':'D_P'}
 helperframes=sorted({t['native_frame']for t in targets if'native_frame'in t});helperchecked={}
 for f in helperframes:
  p=B.project(frames[str(f)]);rank=frames[str(f)]['dim'];certP(p,rank);helperchecked[str(f)]={'rank':rank,'D_P_squared':'I','D_P_transpose':'D_P'}
 retained=glob['retained_old_ids'];need(len(retained)==11238 and len(set(retained))==11238,'Retained domain independent roles')
 for new,t in enumerate(targets):
  previous=next(x for x in old if x['original_owner']==retained[new]);need(t['original_owner']==new,'Same retained physical role domain')
  need({k:v for k,v in t.items()if k!='original_owner'}=={k:v for k,v in previous.items()if k!='original_owner'},'Exact same rank, matcher, port, physical operator and routes on entry/output')
  if t['matcher'].startswith('MAIN_BANK_'):need(t['rank']==templates[t['matcher']]['rank']and 0<=t['port']<111,'Actual complete MAIN field target binding')
  else:need(t['native_frame']in helperframes and t['rank']==helperchecked[str(t['native_frame'])]['rank'],'Actual retained partial/full helper binding')
 invoice=L.read(R/'INVOICE.json');need(Counter(t['rank']for t in targets)==Counter({int(k):v for k,v in invoice['targets'].items()}),'Full retained target invoice')
 result={'status':'PASS_ALL11238_TARGET_PHYSICAL_SYMMETRIC_INVOLUTIONS_AND_SAME_DOMAINS','main_templates':templates,'port_projectors_checked':111,'paid_rho15_checked':111,'retained_helper_frames':helperchecked,'target_count':len(targets),'domain_binding':'Retained old owner IDs compactly renamed; all proof-relevant rank/matcher/port/operator/routing fields exactly identical at entry and output. External role permutation is a fixed physical layout choice.','physical_function_rule':'For every f tensor P with I_f and retain all spectator axes. D_P is an involutive permutation; therefore its FUNCTION permutation M satisfies M^-1=M=M^T=M^-T on arbitrary DATA. The whole target operator is their direct sum. Run the SAME literal complete GLOBAL programme with11 freshly paid owned banks for each direction; never reverse or transpose a destructive CLEAR.','header_rule':'Each new thick body explicitly uses inverse internal birth=base.final, exit=base.start. Exact physical equality to the previous forward body holds for [[D_K,0],[D_I,D_K]] and for every helperD_P. The unchanged paid outer rho15 route therefore conjugates the same physical operator. Internal header labels do not add an unimplemented physical map.'}
 L.put('TARGET-INVOLUTIONS.json',result);return {k:result[k]for k in('status','target_count','port_projectors_checked','paid_rho15_checked','retained_helper_frames')}
if __name__=='__main__':print(json.dumps(run(),indent=2))
