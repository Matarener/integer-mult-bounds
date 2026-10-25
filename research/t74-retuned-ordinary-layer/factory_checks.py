# SPDX-License-Identifier: Apache-2.0
"""Source-bound constructor audit and separately labelled reduced root replay."""

import ast
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
import importlib
import inspect
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

import factory


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def rejects(function, reason):
    try:
        function()
    except ValueError:
        return
    raise ValueError("accepted control: " + reason)


def constructor_body_check(modules):
    """Compare the entire constructor body, including imports and admission."""
    original = ast.parse(inspect.getsource(modules["production_native"].build_native)).body[0]
    candidate = ast.parse(inspect.getsource(factory._native)).body[0]
    expected = deepcopy(original.body[1:])  # Retained first statement is its docstring.
    changed = 0
    for node in ast.walk(ast.Module(body=expected, type_ignores=[])):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Profile":
            need(not node.args and not node.keywords, "unchanged predecessor profile call")
            node.keywords = [ast.keyword(arg="numerator", value=ast.Constant(1)),
                             ast.keyword(arg="denominator", value=ast.Constant(577))]
            changed += 1
    need(changed == 1, "one changed ordinary coupling")
    left = ast.dump(ast.Module(body=expected, type_ignores=[]), include_attributes=False)
    right = ast.dump(ast.Module(body=candidate.body, type_ignores=[]), include_attributes=False)
    need(left == right, "exact production constructor body except fixed profile")
    return sha256(left.encode()).hexdigest()


def recorder_check(modules):
    """Exercise the public constructor control flow without production allocation."""
    records = []

    class Catalogue:
        def __init__(self, q):
            self.q = q
            records.append(("catalogue", q))

    class Specifications:
        def __init__(self, catalogue):
            self.catalogue = catalogue
            records.append(("specifications", catalogue.q))

    class Binding:
        def __init__(self, specifications):
            self.specifications = specifications
            records.append(("binding", specifications.catalogue.q))

    def topology(catalogue):
        records.append(("topology", catalogue.q))
        return SimpleNamespace(catalogue=catalogue)

    def compile_node(topology, binding, mode):
        need(topology.catalogue is binding.specifications.catalogue, "one source catalogue")
        records.append(("compile", mode))
        return ("compiled", mode)

    class Ordinary:
        def __init__(self, q, binding, topology, programs, capacity, profile, fixture_index_floor):
            need(programs == (("compiled", 0),), "complete single mode-zero program")
            self.q, self.binding, self.profile = q, binding, profile
            self.fixture_index_floor = fixture_index_floor
            self.banks = tuple(SimpleNamespace(capacity=capacity) for _ in range(4))
            self.runtime = SimpleNamespace(arena=SimpleNamespace(capacity=capacity),
                                           indices=SimpleNamespace(capacity=capacity))
            records.append(("ordinary", q, capacity, profile.numerator, profile.denominator,
                            profile.dimension, profile.child_rank, profile.row_factor,
                            fixture_index_floor))

    constructors = [("catalogue", "Catalogue", Catalogue),
                    ("catalogue", "Specifications", Specifications),
                    ("node", "selected_topology", topology),
                    ("macro_binding", "SelectedBinding", Binding),
                    ("macro_code", "compile_node", compile_node),
                    ("ordinary", "Ordinary", Ordinary)]
    with ExitStack() as stack:
        for module, name, value in constructors:
            stack.enter_context(patch.object(importlib.import_module(module), name, value))
        old = modules["production_native"].build_native(factory.PRIME)
        old_events, records[:] = tuple(records), []
        native = factory.build_native()
        new_events = tuple(records)
        need(old_events[:-1] == new_events[:-1], "unchanged constructor source pipeline")
        need(old_events[-1][3:5] == (17, 10000) and new_events[-1][3:5] == (1, 577),
             "actual constructor coupling substitution")
        need(old_events[-1][:3] == new_events[-1][:3] and old_events[-1][5:] == new_events[-1][5:],
             "unchanged production capacity and remaining profile")
        rejects(lambda: factory.require_native(old), "old ordinary profile")
        rejects(lambda: factory.build_native(2), "reduced prime in production")
        rejects(lambda: factory.build_native(True), "boolean production prime")
        native.banks[0].capacity -= 1
        rejects(lambda: factory.require_native(native), "wrong numerical capacity")
        native.banks[0].capacity += 1
        native.fixture_index_floor = 1
        rejects(lambda: factory.require_native(native), "fixture-only index floor")
        native.fixture_index_floor = 0
        wrong_layer = SimpleNamespace(machine=SimpleNamespace(monomial=SimpleNamespace(
            compact=SimpleNamespace(binary=SimpleNamespace(native=old)))))
        rejects(lambda: factory.require_layer(wrong_layer, native), "wrong downstream native")
        good_layer = SimpleNamespace(machine=SimpleNamespace(monomial=SimpleNamespace(
            compact=SimpleNamespace(binary=SimpleNamespace(native=native)))))
        factory.require_layer(good_layer, native)
        rejects(lambda: factory.require_native(SimpleNamespace(profile=native.profile)),
                "non-ordinary native object")
        records[:] = []
        prepared = object()
        constructed = []

        class T74Binding:
            def __init__(self, value):
                need(value is prepared, "exact prepared source passed to production binding")
                self.catalogue = object()
                records.append(("t74_binding",))

        class T74RootLayer:
            def __init__(self, binding, result, catalogue):
                need(isinstance(binding, T74Binding) and catalogue is binding.catalogue,
                     "production root receives binding's exact catalogue")
                self.machine = SimpleNamespace(monomial=SimpleNamespace(
                    compact=SimpleNamespace(binary=SimpleNamespace(native=result))))
                constructed.append(result)
                records.append(("t74_root",))

        t74_binding = modules["t74_binding"]
        t74_root = modules["t74_root"]
        with patch.object(t74_binding, "T74Binding", T74Binding), \
                patch.object(t74_root, "T74RootLayer", T74RootLayer):
            production = factory.production_layer(prepared)
            production_events = tuple(records)
            need(production_events == (("t74_binding",),) + new_events + (("t74_root",),),
                 "complete production binding/native/root constructor trace")
            need(len(constructed) == 1 and constructed[0] is
                 production.machine.monomial.compact.binary.native,
                 "production factory threads its exact constructed native")
            with patch.object(t74_root, "T74RootLayer", lambda *args: wrong_layer):
                rejects(lambda: factory.production_layer(prepared), "production root swaps native")
        with patch.dict(sys.modules, {"_t74_retuned_binding": SimpleNamespace(__file__="/tmp/wrong-binding.py")}):
            rejects(factory.runtime, "stale foreign binding import")
    return dict(events=new_events, production_events=production_events, rejected_controls=9,
                scope="Injected constructor recorders; no GL64 catalogue or production allocation executed")


def root_fixture():
    """Load the two authenticated live fixtures without changing native search order."""
    pins = {
        "check_root_runtime.py": "2a20427322c0200ef2d1968db3ac853fc6bf346d3ea9b149c5684ef01e9878f4",
        "check_runtime.py": "c669b8e00074bf4f7e27f34f1c834b536b327577d8097ca20c2a1414d0c12926",
    }
    for name, digest in pins.items():
        need(sha256((factory.T74 / name).read_bytes()).hexdigest() == digest,
             "unchanged root fixture: " + name)
    previous_path = sys.path[:]
    try:
        sys.path[:] = [str(factory.T74)] + [entry for entry in sys.path if entry != str(factory.T74)]
        for name in ("check_runtime", "check_root_runtime"):
            existing = sys.modules.get(name)
            if existing is not None:
                need(Path(getattr(existing, "__file__", "")).resolve() == factory.T74 / (name + ".py"),
                     "one authenticated root fixture: " + name)
            module = importlib.import_module(name)
            need(Path(module.__file__).resolve() == factory.T74 / (name + ".py"),
                 "actual authenticated root fixture: " + name)
        return module
    finally:
        sys.path[:] = previous_path


def reduced_root_check(modules):
    root_check = root_fixture()
    actual_ordinary = modules["ordinary"].Ordinary
    actual_layer = root_check.T74RootLayer
    constructed = []
    native_run_calls = []

    def ordinary(*args, **options):
        need("profile" not in options, "one reduced fixture coupling")
        native = actual_ordinary(*args, profile=factory.profile(), **options)
        factory.require_native(native, production=False)
        constructed.append(native)
        index = len(native_run_calls)
        native_run_calls.append(0)
        run = native.run

        def observed_run(*args, **options):
            native_run_calls[index] += 1
            return run(*args, **options)

        native.run = observed_run
        return native

    def layer(binding, native, catalogue, *args, **options):
        result = actual_layer(binding, native, catalogue, *args, **options)
        factory.require_layer(result, native, production=False)
        return result

    with patch.object(root_check, "Ordinary", ordinary), patch.object(root_check, "T74RootLayer", layer):
        direct = root_check.run(False)
        fast = root_check.run(True)
    need(len(constructed) == 2 and all(n.profile == factory.profile() for n in constructed),
         "both actual reduced root paths carry retuned native")
    return dict(direct=direct, fast=fast, native_objects=2, native_run_calls=native_run_calls,
                scope="Actual retained reduced-root execution; reduced q/capacity/guard, not production T74/O73/GL64")


def run():
    factory.authenticate()
    bundles = factory._live_module("bundles")
    old = os.environ.get("T74_CONTROLLER_EXPORT")
    with tempfile.TemporaryDirectory(prefix="t74-retuned-factory-") as temporary:
        destination = Path(temporary) / "controller"
        bundles.extract("pr3385-controller.tar", destination)
        os.environ["T74_CONTROLLER_EXPORT"] = str(destination)
        try:
            modules = factory.runtime()
            body_hash = constructor_body_check(modules)
            construction = recorder_check(modules)
            roots = reduced_root_check(modules)
            return dict(status="PASS_RETUNED_T74_FACTORY_BINDING", constructor_ast_sha256=body_hash,
                        constructor=construction, reduced_roots=roots,
                        runtime_source_sha256={name: sha256(Path(modules[name].__file__).read_bytes()).hexdigest()
                                               for name in factory.COHORT_PINS},
                        live_binding_import_name=modules["t74_binding"].__name__)
        finally:
            if "predecessor" in sys.modules:
                sys.modules["predecessor"].close_test_imports()
            if old is None:
                os.environ.pop("T74_CONTROLLER_EXPORT", None)
            else:
                os.environ["T74_CONTROLLER_EXPORT"] = old


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
