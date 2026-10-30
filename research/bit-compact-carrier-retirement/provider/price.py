#!/usr/bin/env python3
"""Complete finite price from an emitted owner receipt, with independent powers.

Counts and source identity are input obligations. This program proves only the
arithmetic implications displayed in RECURSION.md. No external imports.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import math

M = 64
W = 28416
REPLICAS = 32
CALLS = 288
EPS = Q(1, 10**16)
LAMBDA = EPS*32*M*M
SCALE = 1 << 224
HERE = Path(__file__).resolve().parent
INPUT_PINS = {
    "local": "ccd419ac1cb123edd8a27aa9d0a6ab3713087a8bcd5be39114a7bd0f254ceebc",
    "r438": "6da8c593257c8440f0fe35488d941715d953d715e2e464ffdfffff7ed31eee9c",
    "selected_assembly": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return Q((x*SCALE).__floor__(), SCALE)


def up(x):
    return -down(-x)


def dec(x):
    with localcontext() as ctx:
        ctx.prec = 65
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def interval(x):
    return dict(lower=str(x[0]), upper=str(x[1]),
                decimal_lower=dec(x[0]), decimal_upper=dec(x[1]))


def read(path, pin=None):
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    need(pin is None or sha == pin, "source pin: "+Path(path).name)
    return json.loads(raw), sha


def profile(value):
    need(isinstance(value, dict), "histogram object")
    out = {int(r): n for r, n in value.items()}
    need(all(type(n) is int and n > 0 and 0 < r < M
             for r, n in out.items()), "proper positive integer child histogram")
    return out


@lru_cache(None)
def log_bounds(x):
    """Positive atanh log series, range reduced to 1 <= x <= 2."""
    need(x >= 1, "log domain")
    k = 0
    while x > 2:
        x /= 2
        k += 1

    def unit(y):
        z = (y-1)/(y+1)
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(80)), Q(0))
        tail = 2*z**161/(161*(1-z*z))
        return lo, lo+tail

    a, b = unit(x)
    c, d = unit(Q(2))
    return down(a+k*c), up(b+k*d)


def exp_bounds(lo, hi):
    need(0 <= lo <= hi < Q(1, 10), "small exponential domain")

    def partial(x):
        total = term = Q(1)
        for j in range(1, 25):
            term *= x/j
            total += term
        return total, term

    low, _ = partial(lo)
    high, term = partial(hi)
    return down(low), up(high+term*hi/25/(1-hi/26))


def moment(P, b):
    """Conservative BIT moment, including one fallback allowance per request."""
    lo = hi = Q(0)
    for r, count in P.items():
        x, y = log_bounds(Q(M, r))
        a, z = exp_bounds(b*x, b*y)
        factor = Q(r*count, M*W)
        lo += factor*a
        hi += factor*z
    x, y = log_bounds(Q(M))
    a, z = exp_bounds(b*x, b*y)
    factor = Q(LAMBDA*sum(P.values()), M*W)
    return down(lo+factor*a), up(hi+factor*z)


@lru_cache(None)
def binomial_power(r, b):
    """Independent integer-grid generalized-binomial bounds on (64/r)^b."""
    need(0 < r <= M and 0 <= b <= 1, "binomial domain")
    scale = 1 << 192
    if not b or r == M:
        return Q(1), Q(1), 0
    low_term = high_term = low_sum = high_sum = scale
    for n in range(1, 16385):
        q = Q(M-r, M)*(b+n-1)/n
        low_term = low_term*q.numerator//q.denominator
        high_term = -((-high_term*q.numerator)//q.denominator)
        low_sum += low_term
        high_sum += high_term
        tail = -((-high_term*(M-r))//r)
        if tail <= 1 << 32:  # tail <= 2^-160; rounding remains included
            return Q(low_sum, scale), Q(high_sum+tail, scale), n
    raise ValueError("binomial tail budget")


def independent_moment(P, b):
    lo = hi = Q(0)
    max_terms = 0
    for r, count in P.items():
        x, y, terms = binomial_power(r, b)
        factor = Q(r*count, M*W)
        lo += factor*x
        hi += factor*y
        max_terms = max(max_terms, terms)
    x, y, terms = binomial_power(1, b)
    factor = Q(LAMBDA*sum(P.values()), M*W)
    return (lo+factor*x, hi+factor*y), max(max_terms, terms)


def bracket(P):
    # Decimal proposes only; both exact algorithms decide the endpoint signs.
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [(Decimal(r*n)/Decimal(M*W),
                  (Decimal(M)/Decimal(r)).ln()) for r, n in P.items()]
        fb = Decimal(LAMBDA.numerator*sum(P.values()))/Decimal(LAMBDA.denominator*M*W)
        logm = Decimal(M).ln()
        lo, hi = Decimal(0), Decimal(".003")
        for _ in range(240):
            mid = (lo+hi)/2
            cost = sum(p*(mid*x).exp() for p, x in terms)+fb*(mid*logm).exp()
            if cost < 1:
                lo = mid
            else:
                hi = mid
        ticks = int((((lo+hi)/2)*10**24).to_integral_value(rounding=ROUND_FLOOR))
    lower = Q(ticks, 10**24)
    upper = lower+Q(1, 10**24)
    a, b = moment(P, lower), moment(P, upper)
    ia, terms1 = independent_moment(P, lower)
    ib, terms2 = independent_moment(P, upper)
    need(a[1] < 1 < b[0], "primary strict adjacent root signs")
    need(ia[1] < 1 < ib[0], "independent strict adjacent root signs")
    return {
        "lower": str(lower), "upper": str(upper),
        "decimal_lower": dec(lower), "decimal_upper": dec(upper),
        "primary_lower_residual": interval((a[0]-1, a[1]-1)),
        "primary_upper_residual": interval((b[0]-1, b[1]-1)),
        "binomial_lower_residual": interval((ia[0]-1, ia[1]-1)),
        "binomial_upper_residual": interval((ib[0]-1, ib[1]-1)),
        "max_binomial_terms": max(terms1, terms2),
    }


def finite_invoice(word, P, route_factor_bound):
    F = word["positive_majorant"]["forward"]
    R = word["positive_majorant"]["inverse"]
    p5 = 64*F**3*R**2
    p9 = 2**18*F**5*R**4
    need((p5.bit_length(), p9.bit_length()) == (114, 211), "precision boundaries")
    E = sum(P.values())
    unit = CALLS*word["adds"]+63936
    J = 8*32*9*(222+438)+8*W+2*9*32*438+2*2592
    high, good, compiler = 16*(M*M+1)**2, 8*M*M+8, 128*(2*M)**3
    out = {
        "p5": str(p5), "p9": str(p9), "p5_bits": p5.bit_length(),
        "p9_bits": p9.bit_length(), "charged_p5": 128, "charged_p9": 256,
        "old_104_192_caps_rejected": p5 >= 2**104 and p9 >= 2**192,
        "unit_additions": unit, "bridge_additions": 63936,
        "copy_erase_episodes": 2592, "J": J, "physical": W+9,
        "child_count": E, "fallback_children_allowance": 32*M*M*E,
        "row_coefficient_if_inherited_row_contract": 2*(M*M+1)+9909+252,
        "halving_inequality": [2*max(P)**2, M**2],
    }
    G = route_factor_bound
    need(type(G) is int and G > 0, "route-factor bound")
    selectors = 2*9*32*((W-1)+438*M*G)
    nonprefix = unit+J*high+J*(W+9)+E*(good+compiler)+16*M**3+2592+selectors+1
    C = p9+nonprefix
    two = (C+1)**2*(E+1)**2
    need(nonprefix < 2**210 and E < 2**20 and two < 2**512,
         "complete finite envelope fits charged depth-two precision")
    out.update({
        "route_factor_bound": G, "selectors": str(selectors),
        "nonprefix": str(nonprefix), "coefficient": str(C),
        "coefficient_bits": C.bit_length(), "two_level_coefficient": str(two),
        "two_level_bits": two.bit_length(), "charged_two_level": 512,
        "scope": "Source invoice arithmetic conditional on the stated route-factor tariff.",
    })
    return out


def route_invoice(owner):
    routing = owner["routing_invoice"]
    coordinate = owner["coordinate_route_bound"]
    expected = dict(rho15=240, legacy_chart=144, new_complete_chart=604,
                    legacy_basis=2, permutation=63, tail=64)
    need(routing["selector_G_terms"] == expected, "explicit route tariff components")
    need(routing["max_sigma_primitives"] == 151
         and routing["max_both_halves_primitives"] == 302
         and routing["max_complete_route_primitives"] == 604,
         "measured chart arithmetic tariff")
    need(coordinate["max_64_coordinate_forward_primitives"]
         == coordinate["max_64_coordinate_inverse_primitives"]
         == routing["max_sigma_primitives"]
         and coordinate["max_128_coordinate_chart_primitives"]
         == routing["max_both_halves_primitives"]
         and coordinate["max_128_coordinate_chart_and_inverse_primitives"]
         == routing["max_complete_route_primitives"],
         "route invoice agrees with replayed coordinate programs")
    need(routing["selector_G"] == sum(expected.values()) == 1117, "complete route G")
    return routing["selector_G"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner-result", type=Path, default=HERE/"OWNERS.json")
    ap.add_argument("--source-result", type=Path, default=HERE/"inputs/PR4183-RESULT.json")
    ap.add_argument("--r438-certificate", type=Path, default=HERE/"inputs/R438-CERTIFICATE.json")
    ap.add_argument("--selected-assembly", type=Path, default=HERE/"inputs/SELECTED-ASSEMBLY.json")
    args = ap.parse_args()
    owner, owner_sha = read(args.owner_result)
    source, source_sha = read(args.source_result, INPUT_PINS["local"])
    old, old_sha = read(args.r438_certificate, INPUT_PINS["r438"])
    selected, selected_sha = read(args.selected_assembly, INPUT_PINS["selected_assembly"])
    G = route_invoice(owner)
    need(owner["live_families"] == W and owner["calls"] == CALLS
         and owner["private_family_reserve"] == 9 and owner["banks"] == 0, "fixed stock")
    need(Counter(owner["ordered_widths"]) == Counter({8: 433, 4: 5}), "complete widths")
    idle = {int(r): n for r, n in owner["idle_per_replica_including_zero"].items() if int(r)}
    need(sum(idle.values()) == 1998 and sum(r*n for r, n in idle.items()) == 10602,
         "complete idle child and rank counts")
    words = source["words"]
    profiles = {}
    for name, key in [("frozen", "baseline"), ("candidate", "boolean")]:
        H = profile(words[key]["histogram"])
        P = Counter({r: CALLS*n for r, n in H.items()})
        P.update({r: REPLICAS*n for r, n in idle.items()})
        need(sum(r*n for r, n in P.items()) == 1808352, "closed rank mass")
        need(M*W-sum(r*n for r, n in P.items()) == 10272, "complete deficit")
        profiles[name] = dict(sorted(P.items()))
    delta = {r: profiles["candidate"].get(r, 0)-profiles["frozen"].get(r, 0)
             for r in profiles["candidate"]}
    need({r: n for r, n in delta.items() if n} == {1: -288, 6: -288, 7: 288},
         "matched full profile difference")
    profiles["r438"] = profile(old["pipeline"]["candidate"]["hosted"]["invoice"]["bit_profile"])
    need(sum(profiles["candidate"].values()) == 902592
         and sum(profiles["frozen"].values()) == 902880, "complete query counts")
    results = {}
    for name, P in profiles.items():
        results[name] = dict(profile=P, children=sum(P.values()),
                             rank_mass=sum(r*n for r, n in P.items()), root=bracket(P))
    roots = {name: (Q(x["root"]["lower"]), Q(x["root"]["upper"])) for name, x in results.items()}
    need(roots["r438"][1] < roots["frozen"][0] < roots["frozen"][1] < roots["candidate"][0],
         "strict complete root ordering")
    complex_b = Q(selected["complex_lower"])
    need(complex_b < roots["r438"][0], "selected complex remains binding")
    gain = (roots["candidate"][0]-roots["frozen"][1],
            roots["candidate"][1]-roots["frozen"][0])
    rates = {}
    for b in [Q(0), Q(17, 10000), Q(139, 80000), Q(1, 500), complex_b]:
        values = {name: moment(P, b) for name, P in profiles.items()}
        raw_saving = (M*W*(values["frozen"][0]-values["candidate"][1]),
                      M*W*(values["frozen"][1]-values["candidate"][0]))
        rates[str(b)] = {"moment": {name: interval(v) for name, v in values.items()},
                         "matched_raw_saving": interval(raw_saving)}
    split = rates[str(Q(139, 80000))]["moment"]
    need(Q(split["candidate"]["upper"]) < 1 < Q(split["frozen"]["lower"]),
         "actual separating rational rate")
    need(Q(rates["0"]["moment"]["candidate"]["upper"]) < Q(199, 200),
         "linear stopped-recurrence margin")
    need(Q(split["candidate"]["upper"]) < 1-Q(1, 2400000),
         "fractional stopped-recurrence margin")
    invoices = {name: finite_invoice(words[key], profiles[name], G)
                for name, key in [("frozen", "baseline"), ("candidate", "boolean")]}
    need(int(invoices["candidate"]["coefficient"]) < int(invoices["frozen"]["coefficient"]),
         "matched finite coefficient decreases")
    b = Q(139, 80000)
    result = {
        "status": "PASS_COMPLETE_CONDITIONAL_RECURSIVE_PRICE",
        "no_new_kappa": True, "m": M, "W": W,
        "physical": W+9, "deficit": 10272,
        "idle_per_replica": idle, "idle_rank_global": 339264,
        "profiles": results, "matched_root_gain": interval(gain),
        "matched_profile_delta": {r: n for r, n in delta.items() if n},
        "rates": rates, "finite_invoice": invoices,
        "compatible_packet_factor": math.lcm(W, W+9),
        "source_prime_contract": "Fixed source-admissible prime q>2^80, avoiding all inherited selector-program denominator primes; the new dyadic owner algebra separately holds over every odd residue ring.",
        "stopped_recurrence": {
            "b": str(b), "linear_majorant_coefficient": 200,
            "fractional_majorant_coefficient": 2400000,
            "bound": "T(n,w)<=200*C*n+2400000*C*n^(1-b)*w",
            "conditional_ordinary_wrapper_saving": str(b*(1-b)),
            "scope": "Written induction under the stated uniform local charge, completed-child, fresh-stock and primitive contracts; current selected executable is not rebound here.",
        },
        "complex_endpoint": str(complex_b), "selected_kappa": selected["kappa"],
        "source_sha256": {"owner": owner_sha, "local": source_sha,
                          "r438": old_sha, "selected_assembly": selected_sha},
        "method": "Primary rational atanh80/exp24 with 224-bit outward rounding; independent integer-grid binomial powers and explicit geometric tail.",
        "scope": "Complete emitted finite profiles priced with conservative BIT fallback. Runtime, common-grid, row, routing and all-size transfer contracts remain explicit hypotheses.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
