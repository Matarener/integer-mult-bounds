"""Exact complete baseline invoice; unrealized target allowance is not earned."""
from relax import *
import importlib.util
spec=importlib.util.spec_from_file_location('predecessor_invoice',ROOT/'vendor/invoice.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)

def run():
 w=load('word5718.json.gz');local=audit(w)
 controller=json.loads((HERE/'inputs/controller5718.json').read_text())
 whole=prior.whole(local,controller)
 need(sum(whole['paid'].values())==66348 and sum(whole['targets'].values())==12976,'complete source inventory')
 surplus=sum(r*n for r,n in whole['targets'].items())-sum(r*n for r,n in whole['paid'].items())
 need(surplus==760,'rank surplus')
 return dict(source_local=local,complete_source=whole,rank_surplus=surplus,local_calls=18,
             prospective_delta_paid={},prospective_delta_targets={4:18,5:18,9:-18},
             prospective_signed_delta='18*(9^t-4^t-5^t)<0 for 0<t<1',
             earned_delta_targets={},kappa_status='NO_NEW_KAPPA',selected_kappa='0.00310045',
             source_claim='0.00311024570; PR5718 archived/merged, not selected',
             ordinary=dict(source_local_scalar=local['scalar'],retiming_added=0,
             input_basis_and_retirement={1196:16,1199:32,1200:24},
             new_local_program='none: exact obstruction',terminal_normalization='unimplemented; not priced at zero',
             new_helper_routes_allocation_cleanup='unimplemented; not priced at zero',
             additional_recursive_bridge='none constructed; not priced at zero',
             compiler_caller_outer='unrun: no complete local survivor'))

if __name__=='__main__':
 out=run();(ROOT/'results/invoice.json').write_text(json.dumps(fmt(out),indent=2)+'\n');print(json.dumps(fmt(out)))
