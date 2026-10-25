#!/usr/bin/env python3
"""Exact conservative outer parameters for the changed recursive family.

This checks arithmetic and source binding, not informal proof validity.
The source-bound native words and finite-precompilation/cover proofs are
separate admission gates. No selected frontier file is changed.

Outer formulas: Vlado Vojdanovski PR1673, Chafik Boukhalfa PR1758/1786,
the retained radix-union/Strassen/fine-prime ledger and its credited lineage.
The changed supplier bindings and conservative parameter choice here are
Apache-2.0, with substantial OpenAI assistance.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import ast
import gzip
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'architecture'))
import mixed_target_probe as E

OLD = ROOT/'research/kappa-observation-integration/release-work/current/package/outer/check_ledger.py'
COMPLEX = HERE/'P3-NATIVE-COVER.json.gz'
BIT = HERE.parent/'bit/MIXED-PRODUCTIVE-BIT.json'
BASELINE = Q('0.001730970419199163702738')


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def display(value):
    value = Q(value)
    with localcontext() as context:
        context.prec = 70
        return {'rational':str(value),'decimal':str(Decimal(value.numerator)/Decimal(value.denominator))}


def encode(value):
    if isinstance(value,Q):
        return display(value)
    if isinstance(value,dict):
        return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [encode(v) for v in value]
    return value


def supplier_checks():
    complex_data,bit_data = read(COMPLEX),read(BIT)
    cover = complex_data['cover']
    bit = next(case for case in bit_data['candidates'] if case['pairs'] == 3 and case['keep_idle_mask'] == 43)
    rows = {}
    for name,paid,targets,precompile in (
            ('complex',cover['paid'],cover['targets'],Q('0.002304')),
            ('bit',bit['paid'],bit['targets'],Q('0.00276'))):
        paid = {int(rank):int(count) for rank,count in paid.items()}
        targets = {int(rank):int(count) for rank,count in targets.items()}
        need(max(paid) < min(targets), 'Actual strict child/target separation')
        signed = Counter(targets); signed.subtract(paid)
        margin = E.moment(signed,precompile)
        need(margin[0] > 0, 'Exact strict mixed moment at the selected precompilation exponent')
        fail = E.moment(signed,Q('0.004'))
        need(fail[1] < 0, 'The current complete identity supplier does not support .004')
        rows[name] = {'targets':targets,'paid':paid,'precompilation_saving':precompile,
                      'strict_mixed_margin':E.show(margin),
                      'margin_at_004':E.show(fail),
                      'uniform_template_definition':'First finite N in the specified exact compiler for which P_N/B_N < N^(1-C). Existence and native closure require the separate written proofs.'}
    bare,covered,atom = Q('0.00276'),Q('0.00275'),Q(3,1000)
    old = Q(384599,10**10)
    bit_saving = (1-atom)*covered+atom*old
    admitted = Q(27,10000)
    gap = bare-covered
    need(bit_saving == Q(27418653797,10**13), 'Exact BIT atom conversion')
    need(atom > bit_saving > admitted and atom < 1-bit_saving, 'All ordinary BIT conversion terms fit')
    # For every N>=2, lnN >= ln2 >1/2, so N^gap >1+gap/2.
    # q >256*N^5/gap gives 64*N^5/q <gap/4. This funds all bad
    # local-ring fallback calls before applying the ordinary atom conversion.
    fallback_ratio_bound = (1+gap/4)/(1+gap/2)
    need(fallback_ratio_bound < 1, 'Uniformly strict complete fallback moment')
    rows['bit']['ordinary_conversion'] = {
        'saving_before_cover':bare,'saving_after_cover':covered,
        'old_leaf_saving':old,'atom_power':atom,'exact_ordinary_saving':bit_saving,
        'declared_BIT_saving':admitted,'linear_adapter_margin':atom-bit_saving,
        'borrowed_stock_margin':1-atom-bit_saving,
        'prime_requirement':'q > 25,600,000*N^5, odd, avoiding every fixed native/matcher denominator and rank witness',
        'prime_coefficient':Q(256)/gap,'fallback_moment_upper_bound':fallback_ratio_bound,
        'row_reserve':'For the new finite N and role/word constants, log_q S(e,w)=O(w log e); w=ceil(e^(3/1000)).'}
    return rows


def ledger(epsilon=Q(99999,100000), beta=Q(99997,100000),
           kappa=Q(23,10000), bit_saving=Q(27,10000), layout=Q(1,10**6)):
    b,q,a = Q('0.002303'),Q('0.002302'),Q('0.0023025')
    r0,stop = Q(1,10**6),Q(1,10**8)
    tau,sigma = 1-a,1-b
    internal = tau+(1-stop)*max(sigma-tau,Q(0))
    leaf = sigma+stop*(1-sigma)
    lam = 1-(q+a)/2
    matrix_exponent = Q(45,16)
    c = (3-matrix_exponent)/2
    xi = epsilon*(1+q)-c+layout
    key = beta+1-epsilon
    margins = {
        'main_transform':epsilon*q,
        'global_coordinate_router':a,
        'fused_gaussian':1-epsilon+q*beta,
        'group_bit_router':1-epsilon+a*beta,
        'group_scans':1-epsilon+beta,
        'boundary_algebraic_matrix':c+xi-epsilon,
        'sparse_union_movement':xi+Q(1,2)-epsilon,
        'polynomial_products':epsilon,
        'microbox_face_corrections':1-(epsilon+beta+48-128+2),
    }
    checks = {
        'actual_bit_above_effective':bit_saving-a,
        'complex_above_effective':b-a,
        'q_positive':q,'complex_endpoint':b-q,'q_below_effective':a-q,
        'stop_positive':stop,'stop_below_one':1-stop,
        'leaf_saving_above_effective':(1-stop)*b-a,
        'q_below_internal':1-internal-q,'q_below_leaf':1-leaf-q,
        'lambda_above_tau':lam-tau,'lambda_above_sigma':lam-sigma,
        'lambda_above_internal':lam-internal,'lambda_prime_above_lambda':1-q-lam,
        'lambda_prime_above_leaf':1-q-leaf,
        'epsilon_positive':epsilon,'epsilon_below_one':1-epsilon,
        'cap_above_band':xi-Q(1,2),'cap_below_cell':epsilon-xi,
        'group_positive':beta,'group_below_dimension':epsilon-beta,
        'support_router_span':1-beta,
        'group_gauge_power_slack':1-(2*xi-2)-r0-beta,
        'actual_logarithmic_group_guard':1-(2*xi-2)-beta,
        'global_gamma_power_slack':1-epsilon-r0,
        'actual_logarithmic_gamma_guard':1-epsilon,
        'alpha_logarithm_absorption':r0,
        'group_key_fits_record':1-key,
        'membership_arithmetic_fits_record':1-beta-2*(1-epsilon),
        'microbox_halo_volume':128-48-beta,
        'positive_layout_slack':layout,
        'short_record_fallback':epsilon-a,
        'complex_below_one_over_32':Q(1,32)-b,
        'strassen_integer_power_gap':Q(2**45-7**16),
        'theta_positive_polynomial_power':Q(2),
        'cap_below_phase_cell_power':2-xi,
        'halo_covers_generic_inverse_radius':Q(48-43),
        'union_tag_work_per_visit_fits_record':1-beta,
        'union_header_fits_record':1-beta,
        'source_axis_superpolynomial':1-epsilon,
        'gaussian_above_main':margins['fused_gaussian']-margins['main_transform'],
    }
    checks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    checks['new_complex_uniform_saving_above_b'] = Q('0.002304')-b
    checks['improvement_over_user_baseline'] = kappa-BASELINE
    checks['new_semantic_guard_with_C1_one'] = 1-epsilon
    checks['fine_prime_halo_umbrella'] = 10-(2*2+2+Q(1,2))
    return {'parameters':{'kappa':kappa,'complex_uniform_saving':Q('0.002304'),
              'BIT_saving':bit_saving,'b':b,'q':q,'effective_saving':a,
              'epsilon':epsilon,'group_beta':beta,'cap_xi':xi,'layout_slack':layout,
              'r0':r0,'stop':stop,'lambda':lam,'lambda_prime':1-q,
              'Strassen_exponent':matrix_exponent,'theta_power':2,'halo_power':48,'core_power':128},
            'margins':margins,'strict_checks':checks}


def inherited_crosscheck(ours):
    """Execute only the previously reviewed parameter function as a second oracle.

    The old native geometry checks are neither changed nor called. Its m=73
    supplier cannot be used to admit the new family. New native gates are
    explicit separate inputs to this package.
    """
    source = ast.parse(OLD.read_text())
    function = next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name == 'ledger')
    constants = [node for node in source.body if isinstance(node,ast.Assign)
                 and any(isinstance(target,ast.Name) and target.id.startswith('KAPPA_') for target in node.targets)]
    env = {'Q':Q,'R0':Q(1,10**6),'ZETA':Q(1,10**8),'SLACK':Q(1,10**6),
           'GAP':Q(1,10**6),'STOP':Q(1,10**8),'FLOOR':10**6,'BACKOFF':Q(1,10**6),
           'EPS':Q(99999,100000),'BETA':Q(99997,100000),'THETA_POWER':Q(2),
           'HALO_POWER':48,'CORE_POWER':128,'STRASSEN_TAU':Q(45,16),
           'b':Q('0.002303'),'q':Q('0.002302'),'a':Q('0.0023025'),
           'bit':Q('0.0027'),'online':BASELINE,'old':BASELINE}
    module = ast.fix_missing_locations(ast.Module(body=constants+[function],type_ignores=[]))
    exec(compile(module,str(OLD),'exec'),env)
    original = env['ledger']('new_uniform_supplier_conservative_parameters')
    need(original['kappa'] == Q(23,10000), 'Inherited floor/backoff produces the same rational target')
    need(original['margins'] == ours['margins'], 'Every inherited outer cost row independently agrees')
    common = set(original['strict_checks']).intersection(ours['strict_checks'])
    need(all(original['strict_checks'][key] == ours['strict_checks'][key] for key in common),
         'All common strict predicates independently agree')
    need(all(value > 0 for value in original['strict_checks'].values()), 'All63 inherited arithmetic checks pass')
    return {'matched_cost_rows':len(original['margins']),
            'matched_named_checks':len(common),'all_inherited_checks':len(original['strict_checks']),
            'native_admission_not_inferred_from_parameter_function':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'OUTER-PARAMETERS.json')
    args = parser.parse_args()
    suppliers = supplier_checks()
    chosen = ledger()
    need(all(value > 0 for value in chosen['strict_checks'].values()), 'Every declared strict condition')
    need(min(chosen['margins'].values()) == chosen['margins']['main_transform'], 'Main transform is limiting')
    independent = inherited_crosscheck(chosen)
    controls = {}
    for label,options in [('unfunded_004',{'kappa':Q(1,250)}),
                          ('epsilon_one',{'epsilon':Q(1)}),
                          ('zero_layout_slack',{'layout':Q(0)}),
                          ('old_BIT_baseline_is_insufficient',{'bit_saving':BASELINE})]:
        invalid = ledger(**options)
        failed = {key:value for key,value in invalid['strict_checks'].items() if value <= 0}
        need(failed, 'Deliberately invalid parameter set is rejected: '+label)
        controls[label] = failed
    paths = [Path(__file__),COMPLEX,BIT,OLD,HERE.parent/'architecture/mixed_target_probe.py']
    result = {'schema':'changed-family-conservative-outer-parameter-certificate/1',
              'status':'PASS_EXACT_ARITHMETIC_AND_SOURCE_BOUND_MIXED_MOMENTS',
              'suppliers':suppliers,'outer':chosen,'inherited_parameter_crosscheck':independent,
              'controls':controls,'source_sha256':{str(path.relative_to(ROOT)):digest(path) for path in paths},
              'scope':'Exact rational arithmetic. Native closure and the finite-program existence proof remain distinct gates. This is not a claim that the incumbent m73 admission script accepted a different supplier.',
              'conditional_hypotheses':['The source-bound finite words have the supplied all-column native interpretation.',
                 'Finite precompilation and delayed BIT cover have their stated arbitrary-input, ownership, storage and routing closure.',
                 'The new uniform templates use replacement semantic precision and row/stock constants.',
                 'The inherited fine-prime padding, gauge-free interior, fixed-tape and outer analytic framework hypotheses.'],
              'new_conditional_kappa_claimed_by_this_arithmetic_file':False}
    args.out.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'target':str(Q(23,10000)),
                      'strict_checks':len(chosen['strict_checks']),
                      'inherited_crosscheck':independent,
                      'smallest_cost_margin':display(min(chosen['margins'].values())-Q(23,10000)),
                      'source_sha256':digest(args.out)},sort_keys=True))


if __name__ == '__main__':
    main()
