#!/usr/bin/env python3
"""Exact favorable-budget obstruction for one frozen unpooled R437 invoice.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Chris R/Clear1nsight supplied the carrier/host; retained credit is in NOTICE.
No predecessor code is executed and no source word, root or native replay runs.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import ast
import json


HERE = Path(__file__).resolve().parent
PINS = {
    "HOST-RESULT.json": ("000837b2b7a1e9d7e4b6b657a055c6f5f3886c7ea343239f8620f79d5d7b2ae8",
                         "ee0952e10f744cf1c6d9c237006ccae4ce3c36c8"),
    "host.py": ("df01e61dc31a1cb6b2bf3549be1e2241f7a30829c2c98567f462271e3fc216ee",
                "2cb9b22890fdfacea4ee51a75b7746dd35b78489"),
    "ORDINARY-TRANSFER-PROOF.md": ("29ed43abaf5451a8514dff2233ba02f44c1d3839e72035ec5711d4edf060b8f9",
                                   "092408728aa81e5a1e6d63307a3c0b85174e2ff2"),
    "SELECTED-RECORD.json": ("2a0220e866417774606e0f991e41b9c1d26b1f43b97857238cf478dbc7d330b5",
                             "581f8d87008354eb5b869f7ed9de1317ad837ce8"),
    "SELECTED-CLAIM.json": ("66fbb5b21f32f1c4ba544c20d5a44ebcdfd11bce2bfa2d609c656ae520d3b21e",
                            "3a8673160d129f0bec6aacf3ff2c2cf693839221"),
}
PROFILE = {1: 380448, 2: 400288, 3: 22464, 4: 26592, 5: 29376,
           6: 17376, 7: 26496, 26: 32, 42: 384}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def compare_receipt(actual, expected):
    need(canonical(actual) == canonical(expected), "canonical typed receipt mismatch")


def authenticate(name, raw):
    expected_sha, expected_blob = PINS[name]
    need(sha256(raw).hexdigest() == expected_sha, "raw source authentication: " + name)
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == expected_blob, "Git blob authentication: " + name)
    return {"path": "source/" + name, "bytes": len(raw),
            "sha256": expected_sha, "git_blob": blob}


def syntax(expression):
    return ast.dump(ast.parse(expression, mode="eval").body, include_attributes=False)


def model_from_price(source):
    """Inspect the authenticated price AST without evaluating any source code."""
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "price"]
    need(len(functions) == 1, "one retained price definition")
    price = functions[0]
    need([argument.arg for argument in price.args.args] == ["profile", "c"], "price arguments")
    factors = [node.value for node in ast.walk(price) if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == "factor" for target in node.targets)]
    need(len(factors) == 1, "one price normalization factor")
    factor = factors[0]
    need(isinstance(factor, ast.Call) and isinstance(factor.func, ast.Name)
         and factor.func.id == "Q" and len(factor.args) == 2
         and ast.dump(factor.args[0], include_attributes=False) == syntax("n*r"),
         "price rank-weight numerator")
    denominator = factor.args[1]
    need(isinstance(denominator, ast.BinOp) and isinstance(denominator.op, ast.Mult)
         and isinstance(denominator.left, ast.Constant) and isinstance(denominator.right, ast.Constant)
         and type(denominator.left.value) is type(denominator.right.value) is int,
         "price productive normalization")
    dimension, width = denominator.left.value, denominator.right.value
    calls = [node for node in ast.walk(price) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)]
    logs = [node for node in calls if node.func.id == "log_bounds"]
    exponentials = [node for node in calls if node.func.id == "exp_bounds"]
    need(len(logs) == len(exponentials) == 1 and len(logs[0].args) == 2
         and ast.dump(logs[0].args[0], include_attributes=False) == syntax(str(dimension))
         and ast.dump(logs[0].args[1], include_attributes=False) == syntax("r")
         and [ast.dump(arg, include_attributes=False) for arg in exponentials[0].args]
         == [syntax("c*l"), syntax("c*h")], "price exponential saving convention")
    required_surcharge = ast.dump(ast.parse(
        "pp[1]=pp.get(1,0)+Q(32*64*64*E,10**16)").body[0], include_attributes=False)
    need(any(ast.dump(node, include_attributes=False) == required_surcharge for node in ast.walk(price)),
         "nonnegative retained rank-one surcharge")
    return dimension, width, {
        "dimension": dimension, "productive_width": width,
        "price_ast_sha256": sha256(ast.dump(price, include_attributes=False).encode()).hexdigest(),
        "checked_sites": ["factor=Q(n*r,64*28416)", "log_bounds(64,r)",
                          "exp_bounds(c*l,c*h)", "nonnegative rank-one surcharge"],
        "scope": "Static model-site binding; no predecessor implementation execution",
    }


def check_contract(profile, dimension, width):
    need(dimension == 64 and width == 28416, "fixed productive normalization")
    need(profile == PROFILE, "fixed unpooled paid profile")
    need(all(type(rank) is int and 0 < rank < dimension and type(count) is int and count > 0
             for rank, count in profile.items()), "positive proper-rank invoice")


def bound(profile, dimension, width, saving):
    """L(c)=A+cB <= the optimistic moment; this is not a root enclosure."""
    need(0 <= saving < 1, "saving in relaxed moment range")
    base = slope = Q(0)
    terms = []
    for rank, count in sorted(profile.items()):
        need(type(rank) is int and 0 < rank <= dimension and type(count) is int and count > 0,
             "bound positive rank/count")
        weight = Q(count * rank, dimension * width)
        log_lower = Q(2 * (dimension - rank), dimension + rank)
        term = weight * (1 + saving * log_lower)
        base += weight
        slope += weight * log_lower
        terms.append({"rank": rank, "count": count, "rank_weight": str(weight),
                      "log_lower": str(log_lower), "linear_term": str(term)})
    return base, slope, base + saving * slope, terms


def target(claim, role="admitted_BIT_saving"):
    need(role == "admitted_BIT_saving", "target role must be admitted BIT saving")
    admitted, ordinary = Q(claim[role]), Q(claim["ordinary_BIT_saving"])
    need(admitted == Q(17, 5000) and ordinary == Q(8590884599, 2500000000000)
         and 0 < admitted <= ordinary < 1, "current ordinary/admitted target binding")
    return admitted, ordinary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit candidate only; never writes files")
    args = parser.parse_args()
    raw = {name: (HERE / "source" / name).read_bytes() for name in PINS}
    authenticated = [authenticate(name, value) for name, value in raw.items()]
    host = json.loads(raw["HOST-RESULT.json"])
    selected, claim = (json.loads(raw[name]) for name in ("SELECTED-RECORD.json", "SELECTED-CLAIM.json"))
    need(selected["certificate_sha256"] == PINS["SELECTED-CLAIM.json"][0]
         and selected["kappa"] == claim["kappa"], "current selected claim provenance")
    profile = {int(rank): count for rank, count in host["profiles"]["new"].items()}
    dimension, width, model = model_from_price(raw["host.py"])
    check_contract(profile, dimension, width)
    need(sum(rank * count for rank, count in profile.items()) == host["mass_new"] == 1808352
         and "fixed unpooled OQ4" in host["scope"], "retained host profile scope")
    transfer = raw["ORDINARY-TRANSFER-PROOF.md"].decode()
    need("a=c(1-c)=575/331776" in transfer and "17/10000<c<1/512" in transfer
         and "dimension 64, W=28416" in transfer, "declared historical transfer bridge")
    admitted, ordinary = target(claim)
    base, slope, lower, terms = bound(profile, dimension, width, admitted)
    need(base < 1 and slope > 0 and lower > 1, "first discriminating linear lower bound")
    controls = []

    def reject(name, reason, action, **evidence):
        try:
            action()
        except ValueError as error:
            need(str(error) == reason, "control rejected for unintended reason: " + name)
            controls.append({"name": name, "reason": str(error), "rejected": True, **evidence})
        else:
            raise ValueError("control accepted: " + name)

    dropped = dict(profile)
    del dropped[2]
    moved = dict(profile)
    moved[1] += moved.pop(42)
    for name, changed in (("dropped_rank_two_bin", dropped), ("moved_rank_42_bin_to_rank_one", moved)):
        changed_lower = bound(changed, dimension, width, admitted)[2]
        need(changed_lower < 1, "changed-model control is not discriminating")
        reject(name, "fixed unpooled paid profile", lambda changed=changed: check_contract(changed, dimension, width),
               recomputed_changed_model_lower=str(changed_lower),
               interpretation="Changed invoice; original exclusion must not be transferred. This is not a candidate admission.")
    reject("physical_width_as_productive_width", "fixed productive normalization",
           lambda: check_contract(profile, dimension, 28425))
    wrong_slot_lower = bound(profile, dimension, width, Q(claim["kappa"]))[2]
    need(wrong_slot_lower <= 1, "wrong-slot control must lose this lower-bound exclusion")
    reject("whole_kappa_as_target", "target role must be admitted BIT saving", lambda: target(claim, "kappa"),
           recomputed_wrong_slot_lower=str(wrong_slot_lower),
           interpretation="This lower bound is inconclusive at the wrong slot; it is not an actual-moment pass.")
    reject("changed_source_bytes", "raw source authentication: HOST-RESULT.json",
           lambda: authenticate("HOST-RESULT.json", raw["HOST-RESULT.json"] + b" "))
    result = {
        "schema": "r437-unpooled-budget-obstruction/1", "sources": authenticated,
        "model": model, "profile": {str(rank): count for rank, count in sorted(profile.items())},
        "paid_children": sum(profile.values()), "rank_mass": host["mass_new"],
        "ordinary_saving": str(ordinary), "admitted_saving": str(admitted),
        "target_role": "weaker admitted BIT saving; ordinary saving is larger",
        "selected_whole_kappa_provenance_only": claim["kappa"],
        "optimistic_moment": "M0(c)=sum_r n_r*r/(64*28416)*exp(c*log(64/r))",
        "linear_lower_bound": {"formula": "L(c)=A+c*B <= M0(c)", "A": str(base), "B": str(slope),
                               "target": str(admitted), "L": str(lower), "L_minus_one": str(lower - 1),
                               "terms": terms},
        "proof": ["For 1<=r<=64, log(64/r)>=2*(64-r)/(64+r).",
                  "For nonnegative u, exp(u)>=1+u; summing positive rank weights gives L(c)<=M0(c).",
                  "B>0, so every relaxed c>=admitted target has L(c)>=L(target)>1.",
                  "The declared bridge a=c*(1-c)<=c makes c>=a>=admitted a necessary condition.",
                  "All omitted bad-event or added costs are nonnegative under this fixed model."],
        "excluded_retained_moment_contraction_budget": True,
        "positive_control_zero_saving": {"L_at_zero": str(base), "strictly_below_one": base < 1},
        "relaxation": "All nonnegative extra charges omitted optimistically; not asserted zero in the real caller",
        "scope": "Only the frozen unpooled invoice and declared moment-certification budget requiring M<=1; not a runtime lower bound or exclusion of other analyses",
        "bridge_limit": "Historical transfer is stated at c=1/576 with c<1/512; dropping that range is only an optimistic moment relaxation, not an extension of its physical theorem",
        "remaining": "Different pooled invoice, changed receiver/model, physical compiler/native/stock/precision admission and all-R437 exclusion are outside scope; selected frontier unchanged",
        "failure_controls": controls,
    }
    alias = deepcopy(result)
    alias["excluded_retained_moment_contraction_budget"] = 1
    reject("boolean_integer_receipt_alias", "canonical typed receipt mismatch",
           lambda: compare_receipt(result, alias))
    if not args.emit:
        compare_receipt(result, json.loads((HERE / "RESULT.json").read_text(encoding="utf-8")))
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    print("PASS_R437_UNPOOLED_BUDGET_OBSTRUCTION")


if __name__ == "__main__":
    main()
