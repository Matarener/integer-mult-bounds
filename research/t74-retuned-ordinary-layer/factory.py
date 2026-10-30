# SPDX-License-Identifier: Apache-2.0
"""Opt-in PR3477 T74 factory with PR3562's ordinary coupling.

Hiroki Kumazaki, with substantial OpenAI Codex assistance. Construction bodies
derive from Jose Manuel's retained PR3385/3477 production native/root factories;
the stronger ordinary theorem and compiled profile are his PR3562 result.
"""

from hashlib import sha256
import importlib
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
T74 = ROOT / "research/t74-physical-layer"
PRIME = 213 * (1 << 80) + 1
CAPACITY = 1 << 24
LIVE_PINS = {
    "predecessor.py": "52318d8926e5268559680b466408fcfbd2ae91bbfcd11bba6c617cd5411b2bb7",
    "t74_root.py": "7bf9001c8fcaa3d9ac9883f3378aa747f39b373d9f88bfc47933797c25e562fd",
    "t74_machine.py": "3bc4c40f275852cea82dbdcf41b8e586bae2e599112ee073a367acc66f37ce83",
    "binding.py": "bd05a117aad3f696a108f0ce95287f1ea3a36603e3df8a2811e74138e73e1057",
    "compile_word.py": "1ae8eeedd1a3e8fea68762550d6f7c9495112785ed82bf824d8f82eba21f64a2",
    "bundles.py": "4078e1db81df8e9921c22beb5c56535f670617ac660e603bea78d6f15e13f424",
    "inputs/pr3385-controller.tar": "85c1442175741317a6f17f39586ddef54a4be8e8942a0bc517fcafa103ff7498",
    "inputs/t74-native-controller.tar": "21dd575587ee31e39f568c3cd3e0eb58b65aea0e78602d9eccefe482548029aa",
}
COHORT_PINS = {
    "production_native": "4c1f8f69212162bd297010c6e21a32e31755cbfe2e40f9935b8d87a9e4260d46",
    "ordinary": "7f8338e748bcd42fbef1e7cc47b6c5040dfb3aad216e34759bcb12b8e14f7705",
    "encoded": "10ad2fa5902a48d49cf2b89a30b3f2711d63a6a43b9512a6427affcdf07335a7",
    "binary": "578fb5bc793fc544dca8111605bf9f6067b8ba7dc7489a3ac243e1df3cd37953",
    "monomial_packets": "6856e80c13ebf3b6e9e0e142ed65420579b5a1b4892f23859d3c6e5f17a334b4",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def authenticate():
    for name, digest in LIVE_PINS.items():
        path = T74 / name
        require(path.is_file() and not path.is_symlink(), "regular T74 source: " + name)
        require(sha256(path.read_bytes()).hexdigest() == digest, "T74 source pin: " + name)


def _live_module(name, alias=None):
    """Do not accept an archived module with a colliding short import name."""
    require(name + ".py" in LIVE_PINS, "declared live T74 module")
    key = name if alias is None else alias
    existing = sys.modules.get(key)
    if existing is not None:
        require(Path(getattr(existing, "__file__", "")).resolve() == T74 / (name + ".py"),
                "one retained T74 module: " + name)
    # Scope live-path precedence: subsequent cold native imports must still find
    # their archived vendor `binding`, not the unrelated live T74 source.
    previous_path = sys.path[:]
    try:
        sys.path[:] = [str(T74)] + [entry for entry in sys.path if entry != str(T74)]
        if alias is None:
            module = importlib.import_module(name)
        elif existing is not None:
            module = existing
        else:
            specification = importlib.util.spec_from_file_location(key, T74 / (name + ".py"))
            module = importlib.util.module_from_spec(specification)
            sys.modules[key] = module
            try:
                specification.loader.exec_module(module)
            except BaseException:
                sys.modules.pop(key, None)
                raise
    finally:
        sys.path[:] = previous_path
    require(Path(module.__file__).resolve() == T74 / (name + ".py"),
            "actual retained T74 module: " + name)
    return module


def runtime():
    """Join the already specified PR3477 export, never a second tape cohort.

    As in the retained factory, T74_CONTROLLER_EXPORT names an authenticated
    PR3385 export. Its loader verifies all 74 exported inputs before import.
    """
    authenticate()
    predecessor = _live_module("predecessor")
    predecessor.activate()
    modules = {name: importlib.import_module(name) for name in COHORT_PINS}
    for name, module in modules.items():
        require(sha256(Path(module.__file__).read_bytes()).hexdigest() == COHORT_PINS[name],
                "actual T74 cohort source: " + name)
    importlib.import_module("cohort").ready()
    # Resolve the original constructor's native dependencies while the cohort's
    # vendor search order is still intact, before loading the live T74 modules.
    for name in ("catalogue", "node", "macro_binding", "macro_code"):
        importlib.import_module(name)
    for name in ("bundles", "compile_word", "t74_machine", "t74_root"):
        _live_module(name)
    # Native Catalogue imports the unrelated archived `binding.split_basis`.
    # Give the unchanged live T74 binding its own name instead of replacing it.
    modules["t74_binding"] = _live_module("binding", "_t74_retuned_binding")
    modules["t74_root"] = _live_module("t74_root")
    return modules


def profile():
    return runtime()["encoded"].Profile(numerator=1, denominator=577)


def _native(q):
    # Source-derived body: the sole AST change to production_native.build_native
    # is Profile(numerator=1, denominator=577). The checker verifies that fact.
    from catalogue import Catalogue, Specifications
    from node import selected_topology
    from macro_binding import SelectedBinding
    from macro_code import compile_node
    from encoded import Profile
    from ordinary import Ordinary
    from words import need
    need(type(q) is int and q > 1 << 80, "fixed selected native prime range")
    catalogue = Catalogue(q)
    specifications = Specifications(catalogue)
    topology = selected_topology(catalogue)
    binding = SelectedBinding(specifications)
    programs = (compile_node(topology, binding, mode=0),)
    return Ordinary(q, binding, topology, programs, capacity=1 << 24,
                    profile=Profile(numerator=1, denominator=577), fixture_index_floor=0)


def require_native(native, production=True):
    modules = runtime()
    require(isinstance(native, modules["ordinary"].Ordinary), "retained ordinary native object")
    require(native.profile == modules["encoded"].Profile(numerator=1, denominator=577),
            "retuned ordinary native profile")
    if production:
        require(type(native.q) is int and native.q > 1 << 80, "production native prime range")
        require(native.fixture_index_floor == 0, "production native index floor")
        arenas = (*native.banks, native.runtime.arena, native.runtime.indices)
        require(len(native.banks) == 4 and all(arena.capacity == CAPACITY for arena in arenas),
                "unchanged six production numerical capacities")


def build_native(q=PRIME):
    """Construct the actual selected native; its production size is enormous."""
    runtime()
    native = _native(q)
    require_native(native)
    return native


def require_layer(layer, native, production=True):
    require_native(native, production)
    require(layer.machine.monomial.compact.binary.native is native,
            "same native object through T74 monomial and binary consumers")


def production_layer(prepared):
    """Keep the full T74 binding/root path and change only the ordinary profile."""
    modules = runtime()
    binding = modules["t74_binding"].T74Binding(prepared)
    native = build_native(PRIME)
    layer = modules["t74_root"].T74RootLayer(binding, native, binding.catalogue)
    require_layer(layer, native)
    return layer
