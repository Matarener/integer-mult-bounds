#!/usr/bin/env python3
"""Exact moment certificate for synchronized native tensor strictification.

Apache-2.0. Substantial OpenAI/Codex assistance. The source native word and
interval engine are PR4359; its compiler uses Jacob Alan Sussman's Theorem 1G.
The native tensor construction and cutoff argument are written in TENSOR.md.
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
EXPONENT = 15000
CUTOFF_BASE = 4
TESTED_SAVING = Q("0.00247756")
ALPHA_UPPER = 1-Q(1,10**9)
GAMMA_UPPER = Q(999,1000)
TARGETS = {5:196, 6:126, 7:392, 8:651, 9:1491, 25:448, 57:224}
PAID = {1:17409, 2:4991, 3:1568, 4:714, 5:140, 8:504, 16:448}


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def upper_moment(exponent, alpha=ALPHA_UPPER, gamma=GAMMA_UPPER):
    """Use a rational Bernoulli bound on alpha^n, retaining gamma^n exactly."""
    return 1/(1+exponent*(1-alpha))+2*gamma**exponent


def run(source_root):
    native = module("tensor_native_inventory", HERE/"native_inventory.py").run(source_root)
    targets = {int(k):v for k,v in native["targets"].items()}
    paid = {int(k):v for k,v in native["paid"].items()}
    need(targets == TARGETS and paid == PAID, "Exact authenticated native inventory")
    engine_path = source_root/"research/kappa-rebuild/architecture/mixed_target_probe.py"
    E = module("tensor_source_intervals", engine_path)
    target_lo, target_hi = E.moment(targets, TESTED_SAVING)
    paid_lo, paid_hi = E.moment(paid, TESTED_SAVING)
    paid_rank = sum(k*v for k,v in paid.items())
    target_rank = sum(k*v for k,v in targets.items())
    need((paid_rank,target_rank) == (46851,47075), "Exact rank-one invoice")
    alpha_lo, alpha_hi = paid_lo/target_hi, paid_hi/target_lo
    logbase_lo, logbase_hi = E.log_interval(CUTOFF_BASE)
    base_power_lo = E.exp_interval(TESTED_SAVING*logbase_lo)[0]
    base_power_hi = E.exp_interval(TESTED_SAVING*logbase_hi)[1]
    gamma_lo = Q(paid_rank)/(base_power_hi*target_hi)
    gamma_hi = Q(paid_rank)/(base_power_lo*target_lo)
    need(0 < alpha_hi < ALPHA_UPPER < 1, "Certified alpha <= 1-10^-9")
    need(0 < gamma_hi < GAMMA_UPPER < 1, "Certified gamma < 999/1000")
    bound = upper_moment(EXPONENT)
    need(bound < 1, "Full tensor and cutoff moment, including every paid chunk")
    need(4**8 < 5**7, "Strict paid/target logarithmic separation theta < 7/8")
    need(max(paid) >= min(targets), "Raw native tariff needs strictification")
    need(upper_moment(EXPONENT, gamma=Q(1)) > 1, "Tail condition is essential")
    need(upper_moment(10000) > 1, "This conservative certificate rejects a smaller trial power")
    need(E.moment(targets,Q("0.003"))[1] < E.moment(paid,Q("0.003"))[0],
         "Unsupported raw saving .003 is rejected")
    return {
        "schema": "native-tensor-cutoff-strictification/1",
        "status": "PASS_SOURCE_BOUND_TENSOR_STRICTIFICATION",
        "exponent": EXPONENT, "cutoff_base": CUTOFF_BASE,
        "tested_saving": str(TESTED_SAVING), "targets": targets, "paid": paid,
        "target_rank_one_moment": target_rank, "paid_rank_one_moment": paid_rank,
        "alpha_upper": str(ALPHA_UPPER), "alpha_interval": E.show((alpha_lo,alpha_hi)),
        "gamma_upper": str(GAMMA_UPPER), "gamma_interval": E.show((gamma_lo,gamma_hi)),
        "normalized_strict_moment_upper": E.show((bound,bound)),
        "strictification_gap": E.show((1-bound,1-bound)),
        "strict_moment_verified": True,
        "new_min_target_encoding": "5^15000", "new_max_paid_encoding": "4^15000",
        "new_max_target_encoding": "57^15000", "theta_upper": "7/8",
        "native_inventory": native,
        "source_sha256": {"research/kappa-rebuild/architecture/mixed_target_probe.py":
                          sha256(engine_path.read_bytes()).hexdigest()},
        "controls": {"unstrictified_native_tariff_rejected": True,
                     "gamma_one_rejected": True,
                     "power_10000_fails_this_conservative_bound": True,
                     "raw_saving_003_rejected": True},
        "materialized_tensor_word": False,
        "scope": "The exact finite construction is specified by synchronized native substitution and paid-axis splitting. This receipt proves its sufficient moment and separation inequalities, conditional on the documented native interfaces; it is not a formal whole-word or multiplication-theorem verification."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE/"source")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.source_root)
    if args.out:
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({key:result[key] for key in
                     ("status","exponent","cutoff_base","tested_saving","strictification_gap")},
                     sort_keys=True))
