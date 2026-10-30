#!/usr/bin/env python3
"""Exact tensor-and-target-completion certificate for the native p7 word.

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
EXPONENT = 6240
CUTOFF = 10
TARGET_FLOOR = 11
TESTED_SAVING = Q('0.00268648')
ALPHA_UPPER = 1-Q(1,10**8)
GAMMA_UPPER = Q(4991,5000)
DELTA_UPPER = Q(2,3)
BLOCK = 390
TARGETS = {5:420,6:270,7:840,8:1395,9:3195,
           25:448,41:448,57:448,121:224}
PAID = {1:37305,2:10695,3:3360,4:1530,5:300,
        8:1464,16:448,32:448,48:448}


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(source_root, native_result=None):
    if native_result is None:
        native_result = module('p7_native',HERE/'native_inventory.py').run(source_root)
    targets = {int(k):v for k,v in native_result['targets'].items()}
    paid = {int(k):v for k,v in native_result['paid'].items()}
    need(targets == TARGETS and paid == PAID,'Exact reconstructed p7 native invoice')
    need(native_result['p'] == 7 and native_result['keep'] == 232127,
         'Actual reconstructed controller selection')
    need(native_result['dimension'] == 121,'Actual native ambient rank')
    productive_count = sum(targets.values())
    paid_rank = sum(k*v for k,v in paid.items())
    target_rank = sum(k*v for k,v in targets.items())
    need(productive_count == 7688,'Every independent productive field')
    need((target_rank,paid_rank) == (131723,131115),'Exact rank-one moments')
    need(target_rank-paid_rank == native_result['rank_margin'] > 0,
         'Positive raw rank-one surplus, preserved by completion and splitting')
    engine_path = source_root/'research/kappa-rebuild/architecture/mixed_target_probe.py'
    E = module('p7_source_intervals',engine_path)
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
    need(0 < alpha_hi < ALPHA_UPPER < 1,'Certified alpha < 1-10^-8')
    need(0 < gamma_hi < GAMMA_UPPER < 1,'Certified original-paid tail gamma < 4991/5000')
    need(0 < delta_hi < DELTA_UPPER < 1,'Certified completion tail delta < 2/3')
    need(GAMMA_UPPER**BLOCK < Q(1,2),'Exact finite rational block decay')
    need(EXPONENT % BLOCK == 0,'Complete decay blocks')
    blocks = EXPONENT//BLOCK
    need(DELTA_UPPER**2 < Q(1,2),'Exact two-step completion-tail decay')
    need(EXPONENT//2 >= blocks,'Completion tail is below the conservative block bound')
    bound = 1/(1+EXPONENT*(1-ALPHA_UPPER))+Q(4,2**blocks)
    need(bound < 1,'Complete normalized paid moment, including all target completion')
    need(1 < CUTOFF < TARGET_FLOOR < max(targets) and 0 < TESTED_SAVING < 1,
         'Completion fits the actual ambient space and restores strict rank separation')
    need(CUTOFF**26 < TARGET_FLOOR**25,'theta < 25/26')
    need(CUTOFF < 2**4 and max(targets) < 2**7,'Exact compiler power bounds')
    need(1/(1+BLOCK*(1-ALPHA_UPPER))+Q(4,2) > 1,
         'One decay block is insufficient under these bounds')
    need(1/(1+EXPONENT*(1-ALPHA_UPPER))+2 > 1,
         'An undamped completion tail is rejected')
    # Without completion, every permitted cutoff is below minimum target five.
    # Its rank-one tail is worse than this already failing boundary value.
    _,ln5_hi = E.log_interval(5)
    old_tail_lo = paid_rank/(E.exp_interval(TESTED_SAVING*ln5_hi)[1]*target_hi)
    need(old_tail_lo > 1,'Unpadded rank-one tail condition fails even at cutoff base five')
    return {
        'schema':'p7-paid-target-completion-tensor-certificate/1',
        'status':'PASS_EXACT_P7_TARGET_COMPLETION_STRICTIFICATION',
        'exponent':EXPONENT,'cutoff_base':CUTOFF,'target_floor_base':TARGET_FLOOR,
        'cutoff_encoding':'10^6240','target_floor_encoding':'11^6240',
        'tested_saving':str(TESTED_SAVING),'targets':targets,'paid':paid,
        'productive_fields':productive_count,
        'target_rank_one_moment':target_rank,'paid_rank_one_moment':paid_rank,
        'rank_one_surplus_encoding':str(target_rank)+'^6240-'+str(paid_rank)+'^6240',
        'alpha_upper':str(ALPHA_UPPER),'alpha_interval':E.show((alpha_lo,alpha_hi)),
        'gamma_upper':str(GAMMA_UPPER),'gamma_interval':E.show((gamma_lo,gamma_hi)),
        'delta_upper':str(DELTA_UPPER),'delta_interval':E.show((delta_lo,delta_hi)),
        'decay_block_length':BLOCK,'decay_block_count':blocks,
        'completion_decay_block_length':2,
        'normalized_moment_upper_rational':str(bound),
        'strictification_gap_rational':str(1-bound),
        'strictification_gap':E.show((1-bound,1-bound)),
        'strict_moment_verified':True,'new_min_target_encoding':'11^6240',
        'new_max_target_encoding':'121^6240','theta_upper':'25/26',
        'native_inventory':native_result,
        'source_sha256':{'research/kappa-rebuild/architecture/mixed_target_probe.py':
                         sha256(engine_path.read_bytes()).hexdigest()},
        'controls':{'unpadded_rank_one_tail_rejected':True,
                    'one_decay_block_rejected':True,'undamped_completion_rejected':True},
        'materialized_tensor_or_completed_word':False,
        'scope':'Exact moment bounds for the documented chronological native product, paid target completion and disjoint splitting. Native all-column, precision, storage, analytic and fixed-tape premises remain separate; no full multiplication theorem is formally verified.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,default=HERE/'source')
    parser.add_argument('--native-result',type=Path,
                        help='Use an already audited native receipt instead of rerunning its producer.')
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    native = json.loads(args.native_result.read_text()) if args.native_result else None
    result = run(args.source_root,native)
    if args.out:
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in
                     ('status','exponent','cutoff_encoding','target_floor_encoding',
                      'tested_saving','strictification_gap')},sort_keys=True))
