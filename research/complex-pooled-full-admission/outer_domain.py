#!/usr/bin/env python3
"""Bounded exact cost, constructor-source and CRT-token checks.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
No production ordinary constructor or numerical payload is executed.
"""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import outer_factory as factory


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reject(name, action):
    try:
        action()
    except (ValueError, KeyError):
        return name
    raise ValueError("control accepted: "+name)


def source_receipts(contracts):
    pins = json.loads((HERE/"OUTER-DOMAIN-PINS.json").read_bytes())
    need(pins["schema"] == 1, "outer-domain receipt schema")
    receipts = {name: json.loads(factory.checked(HERE/"evidence"/name, expected))
                for name, expected in pins["receipts"].items()}
    crt = receipts["CRT-3935-COMPATIBILITY.json"]
    need(crt["old"] == "240597ed313fc2854c0462b23c89dc3bae72aaf5"
         and crt["new"] == factory.GAUSSIAN_HEAD and crt["all_same"], "exact CRT source comparison identity")
    network = json.loads(contracts[factory.CRT+"/NETWORK-SOURCES.json"])
    expected = {row["path"]: row for row in network["files"]}
    observed = {row["path"]: row for row in crt["files"]}
    need(len(expected) == len(observed) == 8 and set(expected) == set(observed), "all eight CRT source inputs")
    replayed = []
    for name, row in expected.items():
        seen = observed[name]
        need(seen["same"] and seen["sha256"] == row["sha256"] and seen["bytes"] == row["size"],
             "complete retained archive comparison: "+name)
        if name in contracts:
            need(factory.digest(contracts[name]) == row["sha256"], "replayed CRT constructor comparison")
            replayed.append(name)
    need(len(replayed) == 5, "five included CRT constructor/proof inputs")
    cohort = receipts["GAUSSIAN-PHYSICAL-COHORT.json"]
    need(cohort["source_head"] == factory.GAUSSIAN_HEAD and len(cohort["found"]) == 10,
         "complete retained constructor cohort observation")
    for row in cohort["found"]:
        need(row["archive_chain"] and row["archive_chain"][0].startswith("PR3935:inputs/"),
             "explicit retained nested archive path")
        if row["path"] in contracts:
            need(factory.digest(contracts[row["path"]]) == row["sha256"] and row["matches_contract"],
                 "replayed nested constructor member comparison")
        else:
            need(row["path"] == "research/physical-complex-controller/scalar_program.py"
                 and row["sha256"] == "4c005167b4c2fe0d98d2dd93b7f931b251259417ff4392b67ee0fbe290f6d48a",
                 "separately pinned ScalarProgram cohort")
    return {"retained_full_CRT_inputs": 8, "replayed_CRT_contract_bodies": replayed,
            "retained_nested_constructor_members": 10,
            "whole_runtime_archive_comparison_replayed": False,
            "receipt_sha256": pins["receipts"]}


CONSTRUCTORS = {
    "ComposedRoot": ("research/t74-support-composition/composed_engine.py", ["self", "router", "root", "policy"], 1),
    "Fourier": ("research/physical-synthetic-fourier/fourier_engine.py", ["self", "layer"], 0),
    "Convolution": ("research/physical-ring-product/convolution_engine.py", ["self", "fourier"], 1),
    "Cyclic": ("research/physical-chirp-middle/cyclic_engine.py", ["self", "convolution"], 1),
    "Chirp": ("research/physical-chirp-middle/chirp_engine.py", ["self", "cyclic"], 1),
    "Tensor": ("research/physical-gaussian-tensor/tensor_engine.py", ["self", "chirp", "router"], 0),
    "FullRouter": ("research/physical-gaussian-tensor/tensor_router.py", ["self", "native"], 1),
    "Converter": ("research/crt-address-streams/crt_converter.py", ["self", "router"], 0),
}


def constructors(contracts):
    result = {}
    for name, (path, arguments, defaults) in CONSTRUCTORS.items():
        classes = [node for node in ast.parse(contracts[path]).body
                   if isinstance(node, ast.ClassDef) and node.name == name]
        need(len(classes) == 1, "one exact constructor class")
        init = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "__init__"]
        need(len(init) == 1 and [arg.arg for arg in init[0].args.args] == arguments
             and len(init[0].args.defaults) == defaults, "actual constructor parameters: "+name)
        result[name] = arguments[1:]
    return result


def factory_graph(body):
    tree = ast.parse(body)
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "production_consumers")
    calls = [node for node in ast.walk(fn) if isinstance(node, ast.Call)]
    full = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == "FullRouter"]
    need(len(full) == 2 and all(len(node.args) == 1 and isinstance(node.args[0], ast.Name) for node in full)
         and {node.args[0].id for node in full} == {"gaussian_native", "crt_native"},
         "FullRouter receives ordinary natives, not Router objects")
    natives = [node for node in calls if isinstance(node.func, ast.Name) and node.func.id == "native"]
    need(len(natives) == 3 and all(not node.args and not node.keywords for node in natives),
         "three additional fresh ordinary factories")
    pooled = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == "production_layer"]
    need(len(pooled) == 1 and not pooled[0].args and not pooled[0].keywords,
         "one pooled complex root owns the fourth ordinary factory")
    need(not any(isinstance(node.func, ast.Attribute) and node.func.attr == "opened" for node in calls),
         "constructor adapter opens no cold source cohort")


def token_checks(contracts):
    """Execute the unchanged loader's authentication and token, not numerical classes."""
    with tempfile.TemporaryDirectory(prefix="outer-crt-token-") as directory:
        root = Path(directory)
        for path in (factory.CRT+"/crt_sources.py", factory.CRT+"/SOURCES.json", factory.ASSEMBLY):
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contracts[path])
        module_path = root/factory.CRT/"crt_sources.py"
        spec = importlib.util.spec_from_file_location("outer_domain_crt_fixture", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        factory.authenticate_module(module, contracts[factory.CRT+"/crt_sources.py"])
        state = object()  # Token-only fixture, never a production cohort.
        controls = [reject("unbound_CRT_token", module.activate)]
        with factory.crt_token(module, state):
            need(module.activate() is state, "real CRT activate returns the scoped token")
            controls.append(reject("nested_CRT_token", lambda: enter_token(module, object())))
            need(module._active is state, "nested rejection preserves outer token")
        need(module._active is None, "successful token scope restoration")
        try:
            with factory.crt_token(module, state):
                raise RuntimeError("injected post-authentication scope failure")
        except RuntimeError:
            pass
        need(module._active is None, "exception token scope restoration")
        assembly = root/factory.ASSEMBLY
        assembly.write_bytes(contracts[factory.ASSEMBLY]+b"\nchanged\n")
        controls.append(reject("changed_CRT_authenticated_input", lambda: enter_token(module, state)))
        need(module._active is None, "activation failure restores the source token")
        controls.append(reject("changed_loaded_constructor_body", lambda: factory.authenticate_module(
            module, contracts[factory.CRT+"/crt_sources.py"]+b"\n")))
        return controls


def enter_token(module, state):
    with factory.crt_token(module, state):
        pass


def bridge_checks():
    aliases = (factory.GLOBAL_ALIAS, factory.LOCAL_ALIAS)
    need(all(name not in sys.modules for name in aliases), "fresh bounded bridge-check aliases")
    controls = []
    for alias in aliases:
        sentinel = object()
        sys.modules[alias] = sentinel
        try:
            controls.append(reject("foreign_private_bridge_alias:"+alias, enter_bridge))
            need(sys.modules[alias] is sentinel, "rejection preserves the foreign module")
        finally:
            del sys.modules[alias]
    previous = None
    for _ in range(2):
        with factory.global_bridge() as module:
            need(callable(module.production_layer) and sys.modules[factory.GLOBAL_ALIAS] is module,
                 "exact authenticated global-bridge definitions compiled")
            local = module.local_module()
            need(local is not previous and sys.modules[factory.LOCAL_ALIAS] is local
                 and callable(local.frozen_inputs), "fresh exact-byte local bridge definitions")
            previous = local
        need(all(name not in sys.modules for name in aliases), "both private bridge aliases restored")
    return controls


def enter_bridge():
    with factory.global_bridge():
        pass


def exponent_bounds(sigma=Q(".99826995"), alpha=Q(".99827")):
    C = Q(".001730980255989036959962")
    tau, eta, cap = Q(332353, 332929), Q(1, 10**6), Q(997, 1000)
    beta = 1-cap*(1-tau)
    Phi = 1-cap*(1-alpha)
    target = 1-Q(1, 580)
    need(1-C < sigma and tau < sigma < alpha, "stopped-tree moment and inequality ordering")
    internal = sigma-eta*(sigma-tau)
    leaf = sigma+eta*(1-sigma)
    need(internal < alpha and leaf < alpha and Q(499, 500) < alpha,
         "all internal, stopped-leaf and reservation costs")
    need(500*(1-alpha) < 1, "complete failed-guard root tariff")
    need(beta == Q(41544341, 41616125) and beta < Phi < target,
         "complete support-cap, router and final logarithm allowance")
    need(Q(".9981") < Phi and Q(".603") < Phi and Q(3, 5) < Phi,
         "complete Gaussian, chirp-extra and scalar bills")
    return {name: str(value) for name, value in dict(C=C, tau=tau, sigma=sigma, alpha=alpha,
        internal=internal, leaf=leaf, beta=beta, Phi=Phi, target=target,
        internal_gap=alpha-internal, leaf_gap=alpha-leaf, router_gap=Phi-beta,
        final_log_gap=target-Phi, kappa=Q(1, 580)).items()}


def certificate():
    contracts, manifest = factory.contract_sources()
    source = source_receipts(contracts)
    specifications = factory.runtime_pins()
    for package, rows in specifications.items():
        for name, row in rows["files"].items():
            path = package+"/"+name
            if path in contracts:
                need(factory.digest(contracts[path]) == row["sha256"], "runtime pins match included contracts")
    graph = (HERE/"outer_factory.py").read_bytes()
    factory_graph(graph)
    mutated = graph.replace(b"FullRouter(gaussian_native)", b"FullRouter(Router(gaussian_native))")
    need(mutated != graph, "constructor mutation reaches the actual invocation")
    controls = token_checks(contracts)
    controls.extend(bridge_checks())
    controls.extend([
        reject("original_sigma_below_tau", lambda: exponent_bounds(1-Q(".001730980255989036959962"))),
        reject("old_complex_layer_target", lambda: exponent_bounds(alpha=Q(".99827101"))),
        reject("Router_passed_as_native", lambda: factory_graph(mutated)),
    ])
    return {"status": "PASS_OUTER_COST_DOMAIN_SOURCE_AND_TOKEN_CHECKS",
            "exact_exponents": exponent_bounds(), "source_comparison": source,
            "constructor_parameters": constructors(contracts),
            "source_contract_files": len(manifest["files"]),
            "runtime_package_pins": {name: len(row["files"]) for name, row in specifications.items()},
            "controls_rejected": controls,
            "real_CRT_loader_authentication_executed": True,
            "global_bridge_definitions_compiled_from_authenticated_bytes": True,
            "local_bridge_definitions_compiled_in_two_fresh_scopes": True,
            "token_scope_success_and_exception_restoration": True,
            "production_native_constructors_executed": False,
            "numerical_payload_executed": False,
            "runtime_source_closure_supplied": False,
            "scope": "Exact exponents, actual constructor source interfaces, retained archive comparison receipts and actual CRT loader token lifecycle on a small token-only fixture. The production adapter and conditional all-size proof are distinct from these bounded checks."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = certificate()
    encoded = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")
    print(result["status"]+" controls="+str(len(result["controls_rejected"]))+
          " production_native_constructors_executed=false numerical_payload_executed=false")


if __name__ == "__main__":
    main()
