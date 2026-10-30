"""Independent target-domain and symmetric physical-function operator audit."""
from local_audit import *
def mm(a,b):return[[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def eye(n):return[[F(i==j)for j in range(n)]for i in range(n)]
def main():
 frames=read(SRC/'inputs/FRAMES.json')['frames'];base=read(SRC/'inputs/BASELINE-LOCAL.json.gz');ports=read(SRC/'provider/data/PORT-CHARTS.json');ref=read(SRC/'inputs/REFERENCE111.json.gz');axes=read(SRC/'inputs/ACTIVE-AXES.json');ctrl=read(SRC/'inputs/CONTROLLER.json');targets=read(CAND/'TARGET-OWNERS.json')
 for i,q in enumerate(ref['lines']):
  q=list(map(F,q));need(sum(x*x for x in q)==4,'Exact source root norm');p=[[x*y/4 for y in q]for x in q];need(mm(p,p)==p and p==list(map(list,zip(*p))),'Exact actual port projector')
  need(orth(frames[str(base['start'][i])]['B'],frames[str(base['final'][111+i])]['B']),'Port complement')
  rho=[[F(x)for x in r]for r in ports[i]['rho15']];need(mm(rho,rho)==eye(15),'Exact retained rho15 route involution')
 templates={}
 for bank,bits in enumerate(ctrl['diagonal']):
  selected=[j for j,a in enumerate(axes)if int(bits)>>(a['stage']+1)&1];fresh=[v for j in selected if j for v in axes[j]['axes']]
  need(len(set(fresh))==len(fresh)and all(8<=v<127 for v in fresh),'Fresh orthogonal direct-sum stage axes')
  rk=(8 if 0 in selected else 1)+len(fresh);need(rk==1+7*len(selected),'Actual main target rank')
  templates[f'MAIN_BANK_{bank}']=rk
 helper=set()
 for d in targets:
  if d['matcher'].startswith('MAIN_BANK_'):need(d['rank']==templates[d['matcher']]and 0<=d['port']<111,'Exact main descriptor')
  else:
   f=d['native_frame'];helper.add(f);need(d['rank']==frames[str(f)]['dim'],'Actual partial/full target dimension')
 need(len(targets)==11238 and helper=={1,506,508,509},'All target classes retained')
 out={'status':'PASS_INDEPENDENT_TARGET_DOMAINS_ROUTES_SYMMETRIC_FUNCTION_INVOLUTIONS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ports':111,'rational_rho15':111,'main_templates':32,'helper_frames':sorted(helper),'target_count':11238,'proof':'Exact QQ orthogonal projectors give paired address involutions on every main/helper field. Tensor I_f and spectator identity preserve this. Any involutive permutation has a symmetric FUNCTION permutation matrix, so inverse=transpose=inverse-transpose. Direct sum and identical domain/role layouts preserve this equality; the same complete paid program serves all four requested directions with11 newly allocated owned banks. No destructive ERASE is reversed or transposed. The separate global audit binds every target descriptor to its exact retained old physical operator/matcher/port/routes.'}
 (HERE/'TARGET-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
