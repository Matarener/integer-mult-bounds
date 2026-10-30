"""Complete signed paid/target invoices and declared ordinary obligations."""
from emit import *

def whole(local,controller):
 paid=Counter();targets=Counter()
 for e in controller['physical_events']:
  if e[0]=='LOCAL':paid.update(local['paid']);targets.update(local['targets'])
  elif e[0]=='QUERY_SHEAR':paid[1]+=104
  elif e[0]=='IDLE':paid[8*len(e[2])]+=208
 for term in controller['diagonal']:targets[1+8*sum(term[1:])]+=104
 return dict(paid=dict(sorted(paid.items())),targets=dict(sorted(targets.items())))

def main():
 controls=json.loads((HERE/'results/controls.json').read_text());local={k:{int(r):v for r,v in controls['source'][k].items()} for k in ('paid','targets')}
 controller=json.loads((HERE/'inputs/controller5718.json').read_text());need(hashlib.sha256((HERE/'inputs/controller5718.json').read_bytes()).hexdigest()=='a84f6bbd547379597464e56c420cc665f96bc43a9a1351eed4b7cd0fce3cc4b9','controller source hash')
 base=whole(local,controller);need(sum(base['paid'].values())==66348 and sum(base['targets'].values())==12976,'complete baseline counts')
 proposed=deepcopy(base);proposed['targets'][9]-=18;proposed['targets'][4]+=18;proposed['targets'][5]+=18
 need(sum(r*n for r,n in base['targets'].items())-sum(r*n for r,n in base['paid'].items())==760,'complete rank surplus')
 out=dict(source_sha256=PINS['word5718.json.gz'],base=base,unrealized_680_split=proposed,delta_paid={},delta_targets={4:18,5:18,9:-18},signed_delta_paid_minus_targets={4:-18,5:-18,9:18},proof='18*(9^t-4^t-5^t)<0 for 0<t<1 by strict subadditivity; no surviving endpoint implements this proposed invoice',ordinary=dict(source_local_scalar=controls['source']['scalar'],retiming_added_scalar=0,retiming_added_paid_moves=0,input_and_retirement_scalar_by_cut={1196:16,1199:32,1200:24},four_ADD_upper=40,terminal_normalization='unknown: no candidate passes even the favorable rational endpoint test',new_helper_routes_allocation_cleanup='unknown: no candidate emitted',compiler_and_outer='unrun: no survivor'),kappa_status='NO_NEW_KAPPA; selected .00310045; source pending PR5718 claims .00311024570')
 (HERE/'results/invoice.json').write_text(json.dumps(fmt(out),indent=2)+'\n');print(dict(paid=sum(base['paid'].values()),targets=sum(base['targets'].values()),rank_surplus=760,source_scalar=controls['source']['scalar'],delta_targets=out['delta_targets']))
if __name__=='__main__':main()
