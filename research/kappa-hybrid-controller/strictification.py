#!/usr/bin/env python3
"""Exact tensor-and-target-completion certificate for the p17 native/direct word.

Apache-2.0. Substantial OpenAI/Codex assistance. Native controller and interval
engine: zxv's PR4359. Integer compiler: Jacob Alan Sussman's Theorem 1G.
"""
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent/'pr4359-p7-padding/source'
_parameter_spec = importlib.util.spec_from_file_location('hybrid_parameters_strict', HERE/'parameters.py')
PARAMETERS = importlib.util.module_from_spec(_parameter_spec)
_parameter_spec.loader.exec_module(PARAMETERS)
for _name in ('EXPONENT', 'CUTOFF', 'TARGET_FLOOR', 'TESTED_SAVING',
              'ALPHA_UPPER', 'GAMMA_UPPER', 'DELTA_UPPER', 'BLOCK', 'TARGETS', 'PAID',
              'COMPLETION_BLOCK', 'THETA_DENOMINATOR', 'CUTOFF_LOG2_UPPER', 'AMBIENT_LOG2_UPPER'):
    globals()[_name] = getattr(PARAMETERS, _name)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(source_root, native_result=None, retimed_source_root=None):
    if native_result is None:
        native_result = module('hybrid_native',HERE/'native_inventory.py').run(source_root,retimed_source_root=retimed_source_root)
    targets = {int(k):v for k,v in native_result['targets'].items()}
    paid = {int(k):v for k,v in native_result['paid'].items()}
    need(targets == TARGETS and paid == PAID,'Exact reconstructed p17 native/direct invoice')
    need(native_result['p'] == PARAMETERS.PAIRS and native_result['keep'] == PARAMETERS.KEEP
         and native_result['native_mask'] == PARAMETERS.NATIVE_MASK,
         'Actual reconstructed controller selection')
    need(native_result['dimension'] == PARAMETERS.AMBIENT,'Actual native ambient rank')
    productive_count = sum(targets.values())
    paid_rank = sum(k*v for k,v in paid.items())
    target_rank = sum(k*v for k,v in targets.items())
    need(productive_count == PARAMETERS.PRODUCTIVE_FIELDS,'Every independent productive field')
    need((target_rank,paid_rank) == (PARAMETERS.TARGET_MASS,PARAMETERS.PAID_MASS),'Exact rank-one moments')
    need(target_rank-paid_rank == native_result['rank_margin'] > 0,
         'Positive raw rank-one surplus, preserved by completion and splitting')
    engine_path = source_root/'research/kappa-rebuild/architecture/mixed_target_probe.py'
    E = module('hybrid_source_intervals',engine_path)
    target_lo,target_hi = E.moment(targets,TESTED_SAVING)
    paid_lo,paid_hi = E.moment(paid,TESTED_SAVING)
    alpha_lo,alpha_hi = paid_lo/target_hi,paid_hi/target_lo
    log_lo,log_hi = E.log_interval(CUTOFF)
    power_lo = E.exp_interval(TESTED_SAVING*log_lo)[0]
    power_hi = E.exp_interval(TESTED_SAVING*log_hi)[1]
    gamma_lo = paid_rank/(power_hi*target_hi)
    gamma_hi = paid_rank/(power_lo*target_lo)
    delta_lo = productive_count*TARGET_FLOOR/(power_hi*target_hi)
    delta_hi = productive_count*TARGET_FLOOR/(power_lo*target_lo)
    need(0 < alpha_hi < ALPHA_UPPER < 1,'Certified alpha has the stated exact positive gap')
    need(0 < gamma_hi < GAMMA_UPPER < 1,'Certified original-paid tail below its stated rational bound')
    need(0 < delta_hi < DELTA_UPPER < 1,'Certified completion tail below its stated rational bound')
    need(GAMMA_UPPER**BLOCK < Q(1,2),'Exact finite rational block decay')
    need(EXPONENT % BLOCK == 0,'Complete decay blocks')
    blocks = EXPONENT//BLOCK
    need(DELTA_UPPER**COMPLETION_BLOCK < Q(1,2),'Exact finite completion-tail decay')
    need(EXPONENT//COMPLETION_BLOCK >= blocks,'Completion tail is below the conservative block bound')
    bound = 1/(1+EXPONENT*(1-ALPHA_UPPER))+Q(4,2**blocks)
    need(bound < 1,'Complete normalized paid moment, including all target completion')
    need(1 < CUTOFF < TARGET_FLOOR < max(targets) and 0 < TESTED_SAVING < 1,
         'Completion fits the actual ambient space and restores strict rank separation')
    need(CUTOFF**THETA_DENOMINATOR < TARGET_FLOOR**(THETA_DENOMINATOR-1),
         'Strict logarithmic compiler rank separation')
    need(CUTOFF < 2**CUTOFF_LOG2_UPPER and PARAMETERS.AMBIENT < 2**AMBIENT_LOG2_UPPER,'Exact compiler power bounds')
    need(1/(1+BLOCK*(1-ALPHA_UPPER))+Q(4,2) > 1,
         'One decay block is insufficient under these bounds')
    need(1/(1+EXPONENT*(1-ALPHA_UPPER))+2 > 1,
         'An undamped completion tail is rejected')
    # Without completion, every permitted cutoff is below the raw minimum target.
    # Its rank-one tail is worse than this already failing boundary value.
    _,lnmin_hi = E.log_interval(min(targets))
    old_tail_lo = paid_rank/(E.exp_interval(TESTED_SAVING*lnmin_hi)[1]*target_hi)
    need(old_tail_lo > 1,'Unpadded rank-one tail condition fails even at the raw target minimum')
    return {
        'schema':'hybrid-p17-paid-completion-certificate/1',
        'status':'PASS_EXACT_HYBRID_P17_TARGET_COMPLETION_STRICTIFICATION',
        'exponent':EXPONENT,'cutoff_base':CUTOFF,'target_floor_base':TARGET_FLOOR,
        'cutoff_encoding':str(CUTOFF)+'^'+str(EXPONENT),'target_floor_encoding':str(TARGET_FLOOR)+'^'+str(EXPONENT),
        'tested_saving':str(TESTED_SAVING),'targets':targets,'paid':paid,
        'productive_fields':productive_count,
        'target_rank_one_moment':target_rank,'paid_rank_one_moment':paid_rank,
        'rank_one_surplus_encoding':str(target_rank)+'^'+str(EXPONENT)+'-'+str(paid_rank)+'^'+str(EXPONENT),
        'alpha_upper':str(ALPHA_UPPER),'alpha_interval':E.show((alpha_lo,alpha_hi)),
        'gamma_upper':str(GAMMA_UPPER),'gamma_interval':E.show((gamma_lo,gamma_hi)),
        'delta_upper':str(DELTA_UPPER),'delta_interval':E.show((delta_lo,delta_hi)),
        'decay_block_length':BLOCK,'decay_block_count':blocks,
        'completion_decay_block_length':COMPLETION_BLOCK,
        'normalized_moment_upper_rational':str(bound),
        'strictification_gap_rational':str(1-bound),
        'strictification_gap':E.show((1-bound,1-bound)),
        'strict_moment_verified':True,'new_min_target_encoding':str(TARGET_FLOOR)+'^'+str(EXPONENT),
        'new_max_target_encoding':str(max(targets))+'^'+str(EXPONENT),
        'ambient_rank_encoding':str(PARAMETERS.AMBIENT)+'^'+str(EXPONENT),
        'theta_upper':str(Q(THETA_DENOMINATOR-1,THETA_DENOMINATOR)),
        'native_inventory':native_result,'parameters_sha256':sha256((HERE/'parameters.py').read_bytes()).hexdigest(),
        'source_sha256':{'research/kappa-rebuild/architecture/mixed_target_probe.py':
                         sha256(engine_path.read_bytes()).hexdigest()},
        'controls':{'unpadded_rank_one_tail_rejected':True,
                    'one_decay_block_rejected':True,'undamped_completion_rejected':True},
        'materialized_tensor_or_completed_word':False,
        'scope':'Exact moment bounds for the documented chronological native product, paid target completion and disjoint splitting. Native all-column, precision, storage, analytic and fixed-tape premises remain separate; no full multiplication theorem is formally verified.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--native-result',type=Path,
                        help='Use an already audited native receipt instead of rerunning its producer.')
    parser.add_argument('--out',type=Path)
    parser.add_argument('--retimed-source-root',type=Path)
    args = parser.parse_args()
    native = json.loads(args.native_result.read_text()) if args.native_result else None
    result = run(args.source_root,native,args.retimed_source_root)
    if args.out:
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in
                     ('status','exponent','cutoff_encoding','target_floor_encoding',
                      'tested_saving','strictification_gap')},sort_keys=True))
