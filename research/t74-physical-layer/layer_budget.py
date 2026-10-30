# SPDX-License-Identifier: Apache-2.0
"""Exact T74 layer budget, conditional on a complete physical realization."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/rank7-joint-endframes/allocation/PROFILE.json": "94a819747f3ced41f1544ada0036c983fc0c92847b9644380f877a06cd7931cf",
    "research/rank7-joint-endframes/allocation/ORDER.json": "519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1",
    "research/complex-local-word-ceiling/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def run():
    raw = {}
    for path, digest in PINS.items():
        raw[path] = (ROOT / path).read_bytes()
        need(sha256(raw[path]).hexdigest() == digest, "source hash: " + path)
    profile = {int(r): n for r, n in json.loads(raw[next(iter(PINS))]).items()}
    order = json.loads(raw["research/rank7-joint-endframes/allocation/ORDER.json"])
    need(len(order) == 666 and set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(74)},
         "complete 74-replica source order")
    families = 896 * 74
    need(sum(r * n for r, n in profile.items()) == 4816512 and sum(profile.values()) == 2394506,
         "complete profile, not a per-call histogram")
    engine = types.ModuleType("t74_retained_ceiling")
    source = "research/complex-local-word-ceiling/ceiling.py"
    exec(compile(raw[source], str(ROOT / source), "exec", optimize=0), engine.__dict__)
    sigma, tau, beta, alpha = Q(9983, 10000), Q(99830289, 10**8), Q(1, 1000), Q(199661, 200000)
    lower = upper = Q(0)
    for rank, count in profile.items():
        a, b = engine.child_cost(rank, 73, 1 - sigma)
        lower += count * a / families
        upper += count * b / families
    need(upper < 1 and 1 - upper > Q(20603111, 250000000000), "strict T74 moment gap")
    leaf = sigma + beta * (1 - sigma)
    reservation = Q(499, 500)
    need(sigma < tau < alpha and leaf < tau and reservation < tau, "internal term dominates with logarithm")
    gaps = {"internal": alpha - tau, "leaf": alpha - leaf, "reservation": alpha - reservation}
    need(gaps == {"internal": Q(211, 10**8), "leaf": Q(33, 10**7), "reservation": Q(61, 200000)},
         "exact final power margins")
    scale = 10**30
    outward = [lower.numerator * scale // lower.denominator,
               -((-upper.numerator * scale) // upper.denominator)]
    return dict(status="PASS_CONDITIONAL_T74_PHYSICAL_LAYER_BUDGET", families=families,
                calls=len(order), profile=profile, moment_outward_numerators=outward, denominator=scale,
                sigma=str(sigma), ordinary_exponent=str(tau), leaf_exponent=str(leaf),
                reservation_exponent=str(reservation), final_exponent=str(alpha),
                margins={k: str(v) for k, v in gaps.items()}, saving=str(1-alpha),
                scope="Requires complete physical lowering with no extra positive-rank children, retained B1 and long records; no completed layer or new integer kappa is certified here.")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
