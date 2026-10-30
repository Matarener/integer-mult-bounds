#!/usr/bin/env python3
"""Source-bound rational-cutoff tensor certificate for the all-fresh p6 word.

Apache-2.0. Substantial OpenAI/Codex assistance. The source native controller
and interval engine are PR4359; its compiler uses Sussman's Theorem 1G.
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
EXPONENT = 150000
CUTOFF = Q(19,4)
TESTED_SAVING = Q("0.00267988")
ALPHA_UPPER = 1-Q(1,10**8)
GAMMA_UPPER = Q(9999,10000)
BLOCK = 10000
TARGETS = {5:364, 6:234, 7:728, 8:1209, 9:2769,
           25:448, 41:448, 57:224, 105:224}
PAID = {1:32331, 2:9269, 3:2912, 4:1326, 5:260,
        8:1224, 16:448, 32:448, 48:224}


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(source_root, native_result=None):
    if native_result is None:
        native_result = module("p6_native_inventory", HERE/"native_inventory.py").run(source_root)
    targets = {int(k):v for k,v in native_result["targets"].items()}
    paid = {int(k):v for k,v in native_result["paid"].items()}
    need(targets == TARGETS and paid == PAID, "Exact all-fresh p6 native invoice")
    need(native_result["p"] == 6 and native_result["keep"] == 25279,
         "Actual reconstructed controller selection")
    need(native_result["dimension"] == 105 and native_result["rank_margin"] == 512,
         "Actual native ambient rank and rank-one surplus")
    engine_path = source_root/"research/kappa-rebuild/architecture/mixed_target_probe.py"
    E = module("p6_source_intervals", engine_path)
    target_lo, target_hi = E.moment(targets,TESTED_SAVING)
    paid_lo, paid_hi = E.moment(paid,TESTED_SAVING)
    paid_rank = sum(k*v for k,v in paid.items())
    target_rank = sum(k*v for k,v in targets.items())
    need((target_rank,paid_rank) == (108769,108257), "Exact rank-one masses")
    alpha_lo, alpha_hi = paid_lo/target_hi, paid_hi/target_lo
    ln_num = E.log_interval(CUTOFF.numerator)
    ln_den = E.log_interval(CUTOFF.denominator)
    logbase_lo, logbase_hi = ln_num[0]-ln_den[1], ln_num[1]-ln_den[0]
    base_power_lo = E.exp_interval(TESTED_SAVING*logbase_lo)[0]
    base_power_hi = E.exp_interval(TESTED_SAVING*logbase_hi)[1]
    gamma_lo = Q(paid_rank)/(base_power_hi*target_hi)
    gamma_hi = Q(paid_rank)/(base_power_lo*target_lo)
    need(0 < alpha_hi < ALPHA_UPPER < 1, "Certified alpha < 1-10^-8")
    need(0 < gamma_hi < GAMMA_UPPER < 1, "Certified rational-cutoff tail gamma < 9999/10000")
    need(GAMMA_UPPER**BLOCK < Q(1,2), "Exact finite rational block decay")
    need(EXPONENT % BLOCK == 0, "Tensor power consists of complete decay blocks")
    blocks = EXPONENT//BLOCK
    bound = 1/(1+EXPONENT*(1-ALPHA_UPPER))+Q(4,2**blocks)
    need(bound < 1, "Full normalized moment including floor-cutoff surcharge")
    need(19**32 < 4**32*5**31, "theta < 31/32 for the rational cutoff")
    need(19**4 < 4**4*2**9 and 105 < 2**7, "Exact explicit-compiler power bounds")
    need(1 < CUTOFF < min(targets) and 0 < TESTED_SAVING < 1,
         "Floor cutoff restores strict separation at every positive tensor power")
    need(1/(1+BLOCK*(1-ALPHA_UPPER))+Q(4,2) > 1,
         "One decay block fails this sufficient bound")
    need(1/(1+EXPONENT*(1-ALPHA_UPPER))+4 > 1,
         "An undamped rank-one tail is rejected")
    # An integer cutoff base of four fails the extra tail condition here.
    ln4_lo, ln4_hi = E.log_interval(4)
    gamma4_lo = Q(paid_rank)/(E.exp_interval(TESTED_SAVING*ln4_hi)[1]*target_hi)
    need(gamma4_lo > 1, "Do not reuse the p3 integer cutoff base")
    return {
        "schema": "p6-rational-cutoff-tensor-certificate/1",
        "status": "PASS_EXACT_P6_RATIONAL_CUTOFF_STRICTIFICATION",
        "exponent": EXPONENT, "cutoff_numerator": CUTOFF.numerator,
        "cutoff_denominator": CUTOFF.denominator,
        "cutoff_encoding": "floor((19/4)^150000)",
        "tested_saving": str(TESTED_SAVING), "targets": targets, "paid": paid,
        "target_rank_one_moment": target_rank, "paid_rank_one_moment": paid_rank,
        "alpha_upper": str(ALPHA_UPPER), "alpha_interval": E.show((alpha_lo,alpha_hi)),
        "gamma_upper": str(GAMMA_UPPER), "gamma_interval": E.show((gamma_lo,gamma_hi)),
        "decay_block_length": BLOCK, "decay_block_count": blocks,
        "normalized_moment_upper_rational": str(bound),
        "strictification_gap_rational": str(1-bound),
        "strictification_gap": E.show((1-bound,1-bound)),
        "strict_moment_verified": True,
        "new_min_target_encoding": "5^150000", "new_max_target_encoding": "105^150000",
        "theta_upper": "31/32", "native_inventory": native_result,
        "source_sha256": {"research/kappa-rebuild/architecture/mixed_target_probe.py":
                          sha256(engine_path.read_bytes()).hexdigest()},
        "controls": {"integer_cutoff_four_rejected": True,
                     "one_decay_block_rejected": True, "undamped_tail_rejected": True},
        "materialized_tensor_word": False,
        "scope": "Exact sufficient moment inequalities for the documented finite native substitution and floor-cutoff construction. The native audit and inherited all-column, precision, storage, analytic and fixed-tape premises remain separate; no full multiplication theorem is formally verified."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE/"source")
    parser.add_argument("--native-result", type=Path,
                        help="Use an already audited native receipt instead of rerunning its producer.")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    native = json.loads(args.native_result.read_text()) if args.native_result else None
    result = run(args.source_root,native)
    if args.out:
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({key:result[key] for key in
                     ("status","exponent","cutoff_encoding","tested_saving","strictification_gap")},
                     sort_keys=True))
