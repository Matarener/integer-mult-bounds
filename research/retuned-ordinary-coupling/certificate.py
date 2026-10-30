"""Two exact moment engines and rational consequences of the changed coupling."""

from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predecessor import ROOT, authenticate, require

C = F(1, 577)
A = C*(1 - C)
INPUTS = {
    "research/rank7-selected-transfer-budget/intervals.py":
        "a247fb83211d2ae83305d73126fc13f2a699e3657a580522cf81d90884e36447",
    "research/e8-bit-p111-tuned/tune/EXPECTED.json":
        "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
    "research/rank7-joint-endframes/CLAIM.json":
        "436e0d297cbdf195445d3697d496ac675e95210b79e70ce602a6a6667a4c6ce9",
}


def inputs():
    for name, digest in INPUTS.items():
        path = ROOT / name
        require(path.is_file() and not path.is_symlink(), "regular certificate input")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "source bytes: " + name)
    bit = json.loads((ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json").read_bytes())["nine"]
    claim = json.loads((ROOT / "research/rank7-joint-endframes/CLAIM.json").read_bytes())
    spec = importlib.util.spec_from_file_location(
        "retained_moment_intervals", ROOT / "research/rank7-selected-transfer-budget/intervals.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return bit, claim, engine


def root_power(rank, dimension, saving=C, bits=160):
    """Enclose (rank/dimension)^(1-saving) using integer powers only."""
    require(0 < rank < dimension and 0 < saving < 1, "root-power domain")
    numerator, denominator = (1-saving).as_integer_ratio()
    scale = 1 << bits
    target = rank**numerator * scale**denominator
    divisor = dimension**numerator
    low, high = 0, scale
    while high - low > 1:
        middle = (low + high)//2
        if middle**denominator * divisor <= target:
            low = middle
        else:
            high = middle
    require(low**denominator * divisor <= target < high**denominator * divisor,
            "outward integer-power enclosure")
    return F(low, scale), F(high, scale)


def integer_moment(histogram, live, saving=C):
    low = high = F(0)
    for rank, count in histogram.items():
        a, b = root_power(rank, 64, saving)
        low += F(count, live)*a
        high += F(count, live)*b
    fallback = F(32*64**2*sum(histogram.values()), 10**16*live)
    a, b = root_power(1, 64, saving)
    return low + fallback*a, high + fallback*b


def decimal_enclosure(bounds, digits=30):
    low, high = bounds
    scale = 10**digits
    return [low.numerator*scale//low.denominator,
            -(-high.numerator*scale//high.denominator), scale]


def run():
    authenticate()
    bit, claim, intervals = inputs()
    histogram = intervals.profile(bit["profile"], 64)
    live = bit["bit"]["live"]
    require(live == 28416 and sum(histogram.values()) == 904896
            and sum(r*n for r, n in histogram.items()) == 1808352, "complete paid BIT profile")
    direct = integer_moment(histogram, live)
    series = intervals.moment(histogram, 64, live, C, True)
    require(max(direct[0], series[0]) <= min(direct[1], series[1]), "independent moment overlap")
    expected = [999998938581682162866772413602, 999998938581682162866772413603, 10**30]
    require(decimal_enclosure(direct) == decimal_enclosure(series) == expected,
            "retuned moment enclosure")
    require(max(direct[1], series[1]) < 1-F(1, 10**6), "new strict moment margin")
    require(min(direct[0], series[0]) > F(9999, 10000), "old rounded margin is unavailable")
    mu1 = intervals.moment(histogram, 64, live, F(0), True)
    require(mu1[0] == mu1[1] < F(199, 200), "retained linear moment")
    bit_cap, complex_cap = F(bit["bit_lower"]), F(claim["complex_lower"])
    require(F(17, 10000) < C < bit_cap < F(1, 576), "admitted reciprocal coupling")
    require(A == F(576, 332929) and A > complex_cap > F(577, 578**2),
            "reciprocal rate boundary")
    old_rate = F(17, 10000)*(1-F(17, 10000))
    require(old_rate < complex_cap, "old ordinary rate does not cover the new complex target")
    bad = integer_moment(histogram, live, F(1, 576))
    require(bad[0] > 1, "denominator 576 fails the complete moment")
    upper = intervals.moment(histogram, 64, live, bit_cap+F(1, 10**24), True)
    omitted = intervals.moment(histogram, 64, live, bit_cap+F(1, 10**24), False)
    require(upper[0] > 1 > omitted[1], "fallback surcharge changes the endpoint decision")
    require(17**128 > 2**5*16**128, "stock-fit power comparison")
    require(32780*F(17, 16)*20 == 696575 < 2**20, "uniform sufficient fit threshold")
    wrapper = 33584 + F(17, 4)*10**6
    require(wrapper == 4283584 < 4300000, "complete ordinary coefficient")
    return {"status": "PASS_RETUNED_ORDINARY_CERTIFICATE", "coupling": str(C),
            "ordinary_saving": str(A), "complex_comparison_gap": str(A-complex_cap),
            "moment": expected, "c0_power_coefficient": 10**6,
            "ordinary_coefficient": int(wrapper), "fit_from": 2**20,
            "controls": ["old_margin", "old_rate", "denominator_576", "denominator_578", "omitted_surcharge"],
            "scope": "Exact rate and proof constants under retained physical/source premises; no outer or kappa claim."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
