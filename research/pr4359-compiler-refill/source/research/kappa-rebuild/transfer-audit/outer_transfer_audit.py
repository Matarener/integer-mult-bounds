#!/usr/bin/env python3
"""Independent directed-rational checks for explicit ranks and outer binding.

The interval arithmetic and parameter derivation below do not import either
the producer's moment engine or either outer ledger. The written companion
audit supplies the functional-interface argument. Apache-2.0; substantial
OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from math import factorial
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GRID=1<<256


def need(ok,message):
    if not ok:
        raise AssertionError(message)


def read(path):
    path=Path(path);raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def down(value):
    return F((value*GRID).__floor__(),GRID)


def up(value):
    return F((value*GRID).__ceil__(),GRID)


def log_unit(x):
    need(1<=x<=2,'Range-reduced rational logarithm')
    t=(x-1)/(x+1);K=96
    low=2*sum((t**(2*j+1)/F(2*j+1) for j in range(K)),F(0))
    tail=2*t**(2*K+1)/((2*K+1)*(1-t*t))
    return down(low),up(low+tail)


def log_integer(k):
    power=k.bit_length()-1;x=F(k,1<<power)
    low,high=log_unit(x);l2,h2=log_unit(F(2))
    return down(low+power*l2),up(high+power*h2)


def exp_small(x):
    need(0<=x<F(1,10),'Small rational exponential')
    K=24
    low=sum((x**j/F(factorial(j)) for j in range(K+1)),F(0))
    first=x**(K+1)/F(factorial(K+1))
    return down(low),up(low+first/(1-x/F(K+2)))


def powers(k,saving):
    l,h=log_integer(k)
    low_exp=exp_small(saving*l)[0]
    high_exp=exp_small(saving*h)[1]
    return down(F(k)/high_exp),up(F(k)/low_exp)


def moment_margin(targets,paid,saving):
    signed=Counter(targets);signed.subtract(paid)
    low=high=F(0)
    for k,count in sorted(signed.items()):
        a,b=powers(k,saving)
        low+=count*(a if count>=0 else b)
        high+=count*(b if count>=0 else a)
    return down(low),up(high)


def explicit_ranks():
    source=read(HERE.parent/'controller/EXPLICIT-TEMPLATE-BOUNDS.json')
    output=[]
    for case in source['cases']:
        paid={int(k):v for k,v in case['paid'].items()}
        targets={int(k):v for k,v in case['targets'].items()}
        r,k,m=max(paid),min(targets),max(targets)
        test,uniform=F(case['tested_mixed_saving']),F(case['uniform_saving'])
        t,z=1-test,1-uniform;z0=(t+z)/2;delta=z0-t
        theta=F(case['theta_upper']);h=1-theta
        need(0<t<z0<z<1 and r<k and h>0,'Strict superpotential and hierarchy')
        low,high=moment_margin(targets,paid,test)
        need(low>0,'Independently enclosed actual superpotential surplus')
        failed=moment_margin(targets,paid,F(1,250))
        need(failed[1]<0,'These actual profiles still reject .004')
        rank_margin=sum(a*b for a,b in targets.items())-sum(a*b for a,b in paid.items())
        need(rank_margin==case['rank_one_surplus']>0,'All paid work, including owned fields, in rank potential')
        need(r**theta.denominator<k**theta.numerator,'Exact logarithmic exit-rank bound')
        need(m**h.numerator<2**h.denominator and 2*r<=16,'Explicit exit coefficient constant')
        need(z0>F(1,2) and exp_small((1-z0)*log_integer(m)[1])[1]<2,
             'eta=z0*m^(z0-1)>1/4')
        H0=((3+4*delta)/(h*delta)).__ceil__()
        H1=(H0*(1-z0)/(z-z0)).__floor__()+1
        need(H0>=m.bit_length() and H1>H0,'Explicit threshold lies beyond the finite base regime')
        need(H0*h*delta>=3+4*delta and H1*(z-z0)>H0*(1-z0),'Complete induction and final strict inequalities')
        need(H0==case['n0']['H0'] and H1==case['N']['H1'],'Independent compressed ranks agree')
        output.append({'family':case['family'],'strict_superpotential_interval':[str(low),str(high)],
                       'rank_one_surplus':rank_margin,'H0':H0,'H1':H1,
                       'N_encoding':'2^H1','uniform_saving':str(uniform),
                       'exact_winning_moment_test':{'P_and_W_power':z.denominator,'N_power':z.numerator},
                       'all_smaller_n_covered_by':'L(n)<=n and A=n0^(1-z0)'})
    return output


def outer():
    receipt=read(HERE.parent/'controller/OUTER-PARAMETERS.json')
    p={key:F(value['rational']) if isinstance(value,dict) and 'rational' in value else value
       for key,value in receipt['outer']['parameters'].items()}
    eps,beta,q,a=p['epsilon'],p['group_beta'],p['q'],p['effective_saving']
    xi=p['cap_xi'];c=(3-p['Strassen_exponent'])/2;kappa=p['kappa']
    need(xi==eps*(1+q)-c+p['layout_slack'],'Boundary and main balance uses the new q')
    own={
        'main_transform':eps*q,
        'global_coordinate_router':a,
        'fused_gaussian':1-eps+q*beta,
        'group_bit_router':1-eps+a*beta,
        'group_scans':1-eps+beta,
        'boundary_algebraic_matrix':c+xi-eps,
        'sparse_union_movement':xi+F(1,2)-eps,
        'polynomial_products':eps,
        'microbox_face_corrections':1-(eps+beta+p['halo_power']-p['core_power']+2)}
    need(all(value>kappa for value in own.values()),'Every inherited outer cost is strictly below the declared running-time exponent')
    need(all(value==F(receipt['outer']['margins'][key]['rational']) for key,value in own.items()),
         'All nine independently recomputed outer rows')
    sigma=1-p['b'];tau=1-a;stop=p['stop']
    internal=tau+(1-stop)*max(sigma-tau,F(0))
    leaf=sigma+stop*(1-sigma)
    checks={
        'new_uniform_complex_above_selected_b':p['complex_uniform_saving']-p['b'],
        'actual_ordinary_BIT_above_effective':p['BIT_saving']-a,
        'selected_complex_above_effective':p['b']-a,
        'lambda_above_actual_internal':p['lambda']-internal,
        'lambda_above_sigma':p['lambda']-sigma,
        'lambda_prime_above_lambda':p['lambda_prime']-p['lambda'],
        'lambda_prime_above_stopped_leaf':p['lambda_prime']-leaf,
        'new_semantic_main_guard':1-eps,
        'new_semantic_group_guard':1-beta,
        'complete_per_axis_neighborhood':1-eps,
        'global_support_reservoir_and_suffix':1-beta,
        'new_BIT_row_stock_sublinear_in_active_group':beta*(1-F(3,1000)),
        'group_strictly_smaller_than_global_dimension':eps-beta,
        'global_gamma_spare_power':1-eps-p['r0'],
        'fine_prime_group_guard':1-(2*xi-2)-p['r0']-beta,
        'polynomial_descriptor_complete_fiber':1-eps,
        'fixed_halo_explicit_metadata_branch':p['core_power']-p['halo_power']-eps-beta-1,
        'member_and_tag_record_budget':1-beta-2*(1-eps),
        'old_full_span_short_record_fallback':eps-a}
    need(all(x>0 for x in checks.values()),'Every newly instantiated functional-support and precision inequality')
    need(kappa==F(23,10000),'Declared conditional research target')
    need(min(own.values())-kappa==F(98849,50000000000),'Exact limiting outer slack')
    return {'kappa':str(kappa),'nine_outer_savings':{k:str(v) for k,v in own.items()},
            'limiting_margin':str(min(own.values())-kappa),
            'functional_interface_gaps':{k:str(v) for k,v in checks.items()},
            'required_global_execution':'Every selected-bit supplier call covers the complete global dyadic stream, restores all labels, removes row padding, then returns before the next coarse-dependent diagonal.',
            'required_deferred_wrapper':'Reserve row/front/back selected chunks without first transforming them; complete them in later shrinking phases.'}


def main():
    ranks=explicit_ranks();assembly=outer()
    paths=[HERE.parent/'controller/EXPLICIT-TEMPLATE-BOUNDS.json',
           HERE.parent/'controller/EXPLICIT-TEMPLATE-BOUNDS.md',
           HERE.parent/'controller/OUTER-PARAMETERS.json',HERE.parent/'controller/outer_parameters.py',
           HERE/'BIT-BRIDGE-AUDIT.json',HERE/'PRECISION-CLOSURE.json',
           HERE/'P3-COVER-AUDIT.json',HERE/'FINITE-TEMPLATE-CLOSURE.md',
           HERE/'OUTER-TRANSFER-AUDIT.md']
    vendor=ROOT/'research/kappa-observation-integration/release-work/current/package'
    paths += [vendor/'outer/FINE-PADDING-COMPOSITION.md',vendor/'outer/GAUGEFREE-INTERIORS.md',
              vendor/'outer/UNION-SCHEDULE.md',
              vendor/'vendor/pr1673/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md',
              vendor/'vendor/pr1673/capped-phase-fusion/SUPPORT-ADVERSARIAL-AUDIT.md',
              vendor/'vendor/pr1673/capped-phase-fusion/TENSOR-COMPILER.md']
    result={'schema':'independent-explicit-template-and-outer-transfer-audit/1',
            'status':'PASS_EXPLICIT_RANKS_NEW_NATIVE_INTERFACES_AND_CONDITIONAL_OUTER_POINT',
            'source_sha256':digest(__file__),'sources':{str(path.relative_to(ROOT)):digest(path) for path in paths},
            'independent_interval_grid_bits':256,'explicit_templates':ranks,
            'conditional_assembly':assembly,
            'proof_boundary':'The companion OUTER-TRANSFER-AUDIT.md closes changed-supplier support, precision, row and weighted interfaces. The pre-existing analytic, ordered-movement, fixed-tape and exact-recovery hypotheses remain conditional.',
            'not_claimed':['A formal theorem-prover certificate.','Materialization or practical performance of the enormous fixed uniform words.','An unconditional integer multiplication theorem.']}
    (HERE/'OUTER-TRANSFER-AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'kappa':assembly['kappa'],'limiting_margin':assembly['limiting_margin'],
                      'explicit_N_exponents':{row['family']:row['H1'] for row in ranks}}))


if __name__=='__main__':
    main()
