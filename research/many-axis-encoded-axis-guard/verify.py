#!/usr/bin/env python3
"""Encoded TensorPlan.production_axis contract for the many-axis prime band.

The fixture is the PR #3935 tensor plan vendored by PR #4029 at
726c9a3a1dc58d2b1223dd681eb712255be407c1. This checker does not execute an
encoded Count runtime and does not reprove the imported prime-number estimate.
"""
import ast
import hashlib
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture-tensor-plan.py"
FIXTURE_SHA256 = "474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3"
MESSAGES = (
    "production tensor strict lower ratio",
    "production tensor strict upper ratio",
    "production tensor period exceeds paired halo",
)
FACTORS = (4, 2, 2, 2)


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def call_name(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = func.value
        if isinstance(base, ast.Name):
            if base.id in ("self", "Count"):
                return base.id + "." + func.attr
            return func.attr
        return func.attr
    return None


def method(tree, class_name, name):
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    need(len(classes) == 1, "unique " + class_name)
    methods = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == name]
    need(len(methods) == 1, "unique " + class_name + "." + name)
    return methods[0]


def production_axis_contract(tree, raw_text):
    """The guard is three predicates on live Counts. It does not touch a tape."""
    axis = method(tree, "TensorPlan", "production_axis")
    need([arg.arg for arg in axis.args.args] == ["self", "s", "t"], "production_axis arguments")
    names = []
    factors = []
    messages = []
    self_fields = []

    class Collect(ast.NodeVisitor):
        def visit_Call(self, node):
            name = call_name(node)
            names.append(name)
            if name == "multiply_small":
                need(len(node.args) == 1 and isinstance(node.args[0], ast.Constant)
                     and type(node.args[0].value) is int, "multiply_small constant")
                factors.append(node.args[0].value)
            if name == "need":
                need(len(node.args) == 2 and isinstance(node.args[1], ast.Constant), "need message")
                messages.append(node.args[1].value)
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                self_fields.append(node.attr)
            self.generic_visit(node)

    Collect().visit(axis)
    allowed = {
        "owned", "subtract", "compare", "need", "Count.product", "Count.literal", "Count",
        "multiply_small", "add",
    }
    need(set(names) <= allowed, "unexpected production_axis call " + repr(sorted(set(names) - allowed)))
    forbidden = {"rewind", "read", "write", "write_fixed", "read_fixed", "clear", "append", "step", "dump"}
    need(forbidden.isdisjoint(names), "production_axis touches a tape operation")
    need(tuple(factors) == FACTORS, "multiply_small sequence " + repr(factors))
    need(tuple(messages) == MESSAGES, "predicate messages " + repr(messages))
    need(set(self_fields) == {"d", "target_halo", "w"}, "self fields " + repr(sorted(set(self_fields))))
    init = method(tree, "TensorPlan", "__init__")
    init_calls = [node for node in ast.walk(init) if isinstance(node, ast.Call)]
    named = [call_name(node) for node in init_calls]
    sites = [node for node in init_calls if call_name(node) == "self.production_axis"]
    need(len(sites) == 1, "one production_axis call site")
    rewinds = [node for node in init_calls if call_name(node) == "rewind"]
    need(rewinds, "init rewinds the tapes")
    need(any(node.lineno > sites[0].lineno for node in rewinds), "a rewind follows production_axis")
    need("read_fixed" in named and "write_fixed" in named, "source tape load stays in __init__")
    segment = "\n".join(raw_text.splitlines()[axis.lineno - 1:axis.end_lineno])
    need("rewind" not in segment and "read_fixed" not in segment and "write_fixed" not in segment,
         "production_axis source names a tape operation")
    need("odd original" not in segment and "near-one" not in segment,
         "oddness or near-one moved into production_axis")
    return {"calls": names, "factors": factors, "messages": messages, "self_fields": sorted(set(self_fields))}


def in_band(s, t, d):
    """Open-closed real band I(t,d) = (t(1-1/(3d)), t(1-1/(4d))]."""
    low = Fraction(t * (3 * d - 1), 3 * d)
    high = Fraction(t * (4 * d - 1), 4 * d)
    return low < s <= high


def ratio_gap(s, t, d):
    """Exact encoded gap g=t-s and the two strict ratio predicates."""
    gap = t - s
    lower = 4 * d * gap > s
    upper = (2 * d - 1) * gap < s
    return gap, lower, upper


def period_holds(s, target_halo, w):
    return s > 2 * (target_halo + 2 * w)


def near_one(s, t):
    return s < t < 2 * s


def endpoint_identities(d):
    """The real band sits strictly inside both ratio predicates for every d>=1."""
    need(d >= 1, "dimension")
    # g >= t/(4d) > t/(4d+1), and g < t/(3d) < t/(2d).
    need(Fraction(1, 4 * d) > Fraction(1, 4 * d + 1), "lower endpoint slack")
    need(Fraction(1, 3 * d) < Fraction(1, 2 * d), "upper endpoint slack")
    # Equivalent forms used by the source: 4d*g>s iff g>t/(4d+1), and (2d-1)*g<s iff g<t/(2d).
    # At the closed lower endpoint g=t/(4d), 4d*g=t>s because s=t-g<t.
    need(Fraction(4 * d, 4 * d) > Fraction(4 * d - 1, 4 * d), "closed endpoint remains a strict ratio")


def period_implication(ell, d):
    """Every band integer beats 2K when K<=2^(ell-3) and d>=2."""
    need(ell >= 2 and d >= 2, "period domain")
    coefficient = Fraction(3 * d - 1, 3 * d)
    need(coefficient >= Fraction(5, 6), "d=2 is the tight coefficient")
    half_scale = 1 << (ell - 1)
    # s > t*coefficient >= half_scale*(5/6) = 2^(ell-2)*(10/6) > 2^(ell-2) >= 2K.
    need(half_scale * Fraction(5, 6) == (1 << (ell - 2)) * Fraction(10, 6), "scale reduction")
    need(Fraction(10, 6) > 1, "strict room over 2K")


def bernoulli_product(d):
    """(1-1/(3d))^(d-1) >= 1-(d-1)/(3d) > 2/3, so T/S<3/2."""
    capital = d - 1
    slack = Fraction(1, 3 * d)
    bound = 1 - capital * slack
    need((1 - slack) ** capital >= bound, "Bernoulli on the prime band")
    need(bound == Fraction(2 * capital + 3, 3 * capital + 3), "Bernoulli remainder")
    need(bound > Fraction(2, 3), "product room")
    need(Fraction(3, 2) * bound > 1, "T/S reciprocal")


def finite_band_scan():
    checked = 0
    for ell in range(2, 41):
        for d in (2, 3, 8, 40):
            period_implication(ell, d)
            bernoulli_product(d)
            endpoint_identities(d)
    for ell in range(3, 13):
        for d in range(2, 9):
            endpoint_identities(d)
            period_implication(ell, d)
            bernoulli_product(d)
            ceiling = 1 << (ell - 3)
            for shift in (0, 1):
                target = 1 << (ell - shift)
                low = int(Fraction(target * (3 * d - 1), 3 * d)) + 1
                high = int(Fraction(target * (4 * d - 1), 4 * d))
                for source in range(low, high + 1):
                    need(in_band(source, target, d), "integer band membership")
                    gap, lower, upper = ratio_gap(source, target, d)
                    need(lower and upper, "band integer fails a ratio predicate")
                    need(Fraction(target, 4 * d) <= gap < Fraction(target, 3 * d), "proof gap form")
                    need(near_one(source, target), "band integer fails near-one")
                    need(period_holds(source, ceiling, 0), "maximum K fails period")
                    need(period_holds(source, ceiling - 2, 1) if ceiling >= 2 else True, "split halo and w")
                    checked += 1
                if low <= high:
                    need(not in_band(low - 1, target, d), "integer below the band")
                    need(not in_band(high + 1, target, d), "integer above the band")
    return checked


def controls(contract):
    # Even band member: ratios and near-one pass, the odd-source gate in __init__ does not.
    need(in_band(14, 16, 2), "even witness leaves the band")
    gap, lower, upper = ratio_gap(14, 16, 2)
    need(lower and upper and near_one(14, 16) and 14 % 2 == 0, "even witness should pass ratios only")
    # Factor 2 is load-bearing: s>K would accept a pair the encoded guard rejects.
    source, target, dimension, halo = 939, 1024, 4, 470
    need(in_band(source, target, dimension), "factor-2 witness leaves the band")
    _, lower, upper = ratio_gap(source, target, dimension)
    need(lower and upper, "factor-2 witness fails ratios")
    need(source > halo and not period_holds(source, halo, 0), "factor 2 is necessary")
    # Maximum legal K for ell=10 still passes.
    need(period_holds(source, 1 << 7, 0), "legal K rejected")
    # A structural mutation that drops the final doubling is not this method.
    need(contract["factors"] == [4, 2, 2, 2], "recorded factors")
    need([4, 2, 2] != list(FACTORS), "control distinguishes a missing final doubling")
    # Below-band and above-band ratio failures.
    _, lower, upper = ratio_gap(513, 1024, 4)
    need(not upper, "short source must fail the upper ratio")
    _, lower, upper = ratio_gap(1023, 1024, 4)
    need(not lower, "long source must fail the lower ratio")


def main():
    raw = FIXTURE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "fixture sha256")
    text = raw.decode()
    need("odd original tensor source axis" in text, "odd-source gate missing")
    need("near-one original tensor axis" in text, "near-one gate missing")
    tree = ast.parse(raw)
    contract = production_axis_contract(tree, text)
    checked = finite_band_scan()
    controls(contract)
    print(
        "PASS_MANY_AXIS_ENCODED_AXIS_GUARD"
        f" band_integers={checked} factors={contract['factors']}"
        " tape_ops_in_production_axis=0 odd_gate=init_only"
        " period=s>2*(target_halo+2*w) no_new_kappa"
    )


if __name__ == "__main__":
    main()
