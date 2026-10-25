"""Exact cost margins for the actual-width T74 statement."""

from fractions import Fraction as F
import importlib.util
import json

from active_sources import require

SIGMA = F(998271, 10**6)
TAU = F(332353, 332929)
ETA = F(1, 10**6)
ALPHA = F(99827101, 10**8)


def run(roots):
    t74 = roots["t74-export.tar"]
    rate = roots["ordinary-rate-export.tar"]
    profile = {int(r): n for r, n in json.loads(
        (t74 / "research/rank7-joint-endframes/allocation/PROFILE.json").read_bytes()).items()}
    order = json.loads((t74 / "research/rank7-joint-endframes/allocation/ORDER.json").read_bytes())
    require(len(order) == 666 and set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(74)},
            "complete T74 order")
    require(sum(profile.values()) == 2394506 and sum(r*n for r, n in profile.items()) == 4816512,
            "complete unchanged T74 histogram")
    path = rate / "research/rank7-selected-transfer-budget/intervals.py"
    spec = importlib.util.spec_from_file_location("active_width_interval_engine", path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    low, high = engine.moment(profile, 73, 66304, 1-SIGMA)
    scale = 10**30
    enclosure = [low.numerator*scale//low.denominator, -(-high.numerator*scale//high.denominator)]
    require(enclosure == [999999903535664027556833879161, 999999903535664027556833879162]
            and high < 1-F(9, 10**8), "new strict full-profile moment")
    internal = SIGMA-ETA*(SIGMA-TAU)
    leaf = SIGMA+ETA*(1-SIGMA)
    reservation = F(499, 500)
    require(TAU < SIGMA < ALPHA and leaf < ALPHA and reservation < ALPHA,
            "new exponent order and positive margins")
    require(ALPHA-internal == F(3329655759, 332929000000000000)
            and ALPHA-leaf == F(8271, 10**12)
            and ALPHA-reservation == F(27101, 10**8), "exact power margins")
    require(500*(1-ALPHA) == F(172899, 200000) < 1, "fallback fits one logarithm")
    require(F(997, 1000)*F(501, 500) == F(499497, 500000) < 1,
            "complete target span fits the precision domain")
    require((10**6).bit_length()-1+(10**6).bit_count() == 26, "new capped product count")
    require((1000).bit_length()-1+(1000).bit_count() == 15, "old capped product count")
    extra = dict(profile)
    extra[1] += 1
    require(engine.moment(extra, 73, 66304, 1-SIGMA)[0] > 1,
            "one unpaid positive-rank child breaks the moment")
    old_tau = F(99830289, 10**8)
    require(old_tau > ALPHA and SIGMA+F(1, 1000)*(1-SIGMA) > ALPHA,
            "old ordinary rate and stopping power cannot certify the target")
    # Arithmetic-only witness that the production fast guard is nonvacuous.
    # No corresponding double-exponential payload is allocated.
    g, p, K = 1 << 10000, 1 << 10050, 1 << 20
    G = 4*10050+6
    depth, cursor = 0, g
    while cursor >= 73:
        cursor = 48*(cursor//73)
        depth += 1
    lam = 6000
    require(66304 < 2**17 and 73**2+17 < lam, "conservative row-divisor logarithm")
    q0 = lam*depth
    qF, qB = -(-(2*g*G)//K), -(-(g*G)//K)
    require(10000*1000 <= 10050*997 and 10000 == 500*20, "exact power witness")
    require(q0+qF+qB < g and K > 3*G and 3*g*G < g*K < p,
            "nonvacuous fast reservation geometry")
    return {"status": "PASS_ACTIVE_WIDTH_T74_BUDGET", "profile": profile,
            "moment_numerators": enclosure, "moment_denominator": scale,
            "ordinary_exponent": str(TAU), "internal_exponent": str(internal),
            "leaf_exponent": str(leaf), "reservation_exponent": str(reservation),
            "target_exponent": str(ALPHA), "fallback_logarithm_power": str(500*(1-ALPHA)),
            "controls": ["one_unpaid_child", "old_ordinary_rate", "old_stop_power"],
            "arithmetic_fast_witness": {"log2_g": 10000, "log2_p": 10050,
                                        "log2_K": 20, "row_log_divisor": lam, "depth": depth},
            "scope": "Exact budget and nonvacuous arithmetic witness under the stated physical/root premises."}
