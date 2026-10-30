#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reused-code algebra/control probe of the pinned original normal-form plan.

This deliberately executes credited predecessor definitions. It is separate
from the new independent matrix compiler and is not physical payload execution.
"""
import ast
from dataclasses import dataclass
import gzip
import hashlib
import json
from math import prod
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from copy_child import eye, inverse, mul, need, projector, reduce_rational, split_basis


def source_definitions(name, wanted, namespace):
    path = HERE / "inputs" / ("predecessor-" + name + ".py")
    records = json.loads((HERE / "SOURCES.json").read_bytes())["retained"]
    pin = next(row for row in records if row["path"] == "inputs/" + path.name)
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "pinned reused source")
    tree = ast.parse(raw, filename=str(path))
    selected = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in wanted]
    need({node.name for node in selected} == set(wanted), "exact selected predecessor definitions")
    # Imports/fixture builders are excluded, not rewritten. This isolates the
    # unmodified pure plan definitions from the large authenticated runtime.
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


def main():
    namespace = dict(__name__="pinned_predecessor_plan", dataclass=dataclass, prod=prod, need=need)
    source_definitions("plan", ["Reference", "Command", "Request", "Plan", "compile_plan"], namespace)
    oracle = dict(need=need)
    source_definitions("oracle", ["good_pivots"], oracle)
    raw = (HERE / "inputs/r437-word.json.gz").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == "e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e", "R437 probe pin")
    word = json.loads(gzip.decompress(raw))
    # Evaluate the exact pinned guard expressions, not a rewritten predicate.
    # This is a schema-compatibility proof; it does not execute a full template.
    catalogue_path = HERE / "inputs/predecessor-catalogue.py"
    cat_bytes = catalogue_path.read_bytes()
    cat_pin = next(row for row in json.loads((HERE / "SOURCES.json").read_bytes())["retained"]
                   if row["path"] == "inputs/predecessor-catalogue.py")
    need(hashlib.sha256(cat_bytes).hexdigest() == cat_pin["sha256"], "pinned catalogue guard source")
    cat_ast = ast.parse(cat_bytes)
    guards = {}
    for node in ast.walk(cat_ast):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "need" and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value in ("replica owner symmetry", "fresh selected COPY")):
            guards[node.args[1].value] = compile(ast.Expression(body=node.args[0]), str(catalogue_path), "eval")
    need(set(guards) == {"replica owner symmetry", "fresh selected COPY"}, "exact selected schema guards")
    ordinary = 2 * word["v"] + word["R"]
    owner_accepts = {}
    copy_accepts = {}
    for count in (ordinary, 661):
        owners = [(0, ("identity",))] * count
        context = dict(other=dict(owners=owners), call=dict(owners=owners), replica=0)
        owner_accepts[str(count)] = eval(guards["replica owner symmetry"], context, context)
        copy_accepts[str(count)] = eval(guards["fresh selected COPY"], {},
                                       dict(temporary=count, opened=None, base=SimpleNamespace(rank=7), rank=7))
    need(ordinary == 659 and owner_accepts == {"659": False, "661": True}
         and copy_accepts == {"659": False, "661": True}, "R437 requires explicit source/schema integration")
    rational, rank = projector(word["lines"], word["frames"][515])
    need(rank == 7, "actual R437 frame")
    q, p = 3, [[0] * 64 for _ in range(64)]
    for i, row in enumerate(reduce_rational(rational, q)):
        p[i][:8] = row
    basis = split_basis(p, 7, q, q)
    good_g = inverse(basis, q)
    good = mul(mul(good_g, p, q), inverse(good_g, q), q)
    oracle["good_pivots"](good, 7, q)
    gp = namespace["compile_plan"](good, 7, q, True)
    need(len(gp.commands) == 4936 and all(c.kind == "add" and c.target > c.source for c in gp.commands), "every original good adapter is physically ordered")
    permutation = eye(64)
    for i in range(7):
        permutation[i], permutation[57 + i] = permutation[57 + i], permutation[i]
    bad_g = mul(permutation, inverse(basis, q), q)
    bad = mul(mul(bad_g, p, q), inverse(bad_g, q), q)
    try:
        oracle["good_pivots"](bad, 7, q)
    except ValueError:
        pass
    else:
        raise ValueError("bad probe entered the good source branch")
    bp = namespace["compile_plan"](bad, 7, q, False)
    need(all(c.target > c.source for c in bp.commands if c.kind == "add"), "all original fallback scalar adapters are ordered")
    expanded = {}
    for f in (1, 2, 3, 10, 64):
        children = 0
        for c in bp.commands:
            if c.kind == "child":
                same_bank = (c.target < 64) == (c.source < 64)
                children += 1 + (2 if same_bank and f // 2 else 0)
        need(children <= 49911, "all original main and half children fit the complete allowance")
        expanded[str(f)] = children
    count = {kind: sum(c.kind == kind for c in bp.commands) for kind in ("add", "child", "sign")}
    need(count["add"] <= 16256 and count["sign"] <= 1 and count["child"] <= 16637, "fallback finite-control bounds")
    result = dict(status="PASS_REUSED_ORIGINAL_PLAN_ALGEBRA_AND_COUNTS", frame=515,
                  dimension=64, rank=7, q=3, good_adapter_commands=4936,
                  good_forward_backward_ADDs_per_column=9872,
                  fallback_command_counts=count, expanded_fallback_children=expanded,
                  fallback_children_upper=49911,
                  actual_R437_ordinary_roles=ordinary,
                  selected_owner_schema_accepts=owner_accepts,
                  selected_private_schema_accepts=copy_accepts,
                  scope="Reused pure plan compiler and low pivot probe; no physical payload, generated callback or CALL/RETURN execution")
    expected = HERE / "SOURCE-PLAN.json"
    if "--write-result" in sys.argv:
        expected.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(expected.read_bytes()) == result, "source-plan receipt differs")
    print(result["status"] + " good_ADDs_per_column=9872 fallback_cap=49911")


if __name__ == "__main__":
    main()
