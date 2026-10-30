"""Independent bounded identity/lifetime audit. No official verifier imports.

--synthetic: stdlib only; no source imports. --original: parent-run only.
Data fixtures are explicitly not the selected numerical construction.
Adapted from the verified Astra lifetime worker, with substantial OpenAI Codex
assistance. Apache-2.0. Jose Manuel (jmbarrancoml), David Arias, ywz65,
Nick Petalas and retained README/NOTICE contributors retain source credit;
Ross Richardson's retained-backing methodology remains a predecessor.
Never enumerate GL64.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, replace
import gc
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys
import time
from types import SimpleNamespace as NS
import weakref

MAX_DIMENSION = 2
MAX_RETURNS = 32
MAX_OPERATIONS = 512
MAX_TRACE_EVENTS = 12000
HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[1]
CALLER = "research/selected-bit-physical-caller"
I2 = ((1, 0), (0, 1))
S2 = ((0, 1), (1, 0))

class Rejected(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise Rejected(message)

def reject(label, function, contains):
    try:
        function()
    except ValueError as error:
        need(contains in str(error), f"{label}: unexpected rejection {error}")
        return {"control": label, "rejected": True, "reason": str(error)}
    raise Rejected(label + ": control was accepted")

@dataclass(frozen=True)
class SyntheticWrapper:
    code: int
    plan: object
    identifier: int = 0
    common: bool = False
    low: tuple = I2
    axis: object = None

@dataclass(frozen=True)
class Returned:
    ref: object
    blocks: tuple


def direct_refs(operation):
    # Exactly direct tuple elements, not recursively traversed plans or lows.
    return operation[1:]


def inspect_operations(operations, returned):
    need(len(operations) <= MAX_OPERATIONS, "operation bound")
    need(len(returned) <= MAX_RETURNS, "wrapper bound")
    wrappers = [entry.ref() for entry in returned]
    need(all(w is not None for w in wrappers), "factory return died before inspection")
    need(len({id(w) for w in wrappers}) == len(wrappers), "non-fresh factory identity")
    interval = -1
    active = None
    seen_blocks = []
    counts = [0] * len(wrappers)
    for operation in operations:
        for item in direct_refs(operation):
            for i, w in enumerate(wrappers):
                if item is w:
                    counts[i] += 1
        kind = operation[0]
        if kind == "residual_begin":
            need(active is None, "overlapping residual intervals")
            interval += 1
            need(interval < len(wrappers), "extra begin")
            active = wrappers[interval]
            need(operation[2] is active, "begin identity mismatch")
            seen_blocks = []
        elif kind == "block":
            need(active is not None, "block outside interval")
            need(operation[1] is active, "block identity mismatch")
            seen_blocks.append(operation[2])
        elif kind == "residual_end":
            need(active is not None, "finish outside interval")
            need(operation[2] is active, "finish identity mismatch")
            need(tuple(seen_blocks) == returned[interval].blocks, "missing/changed block")
            active = None
    need(active is None, "missing finish")
    need(interval + 1 == len(wrappers), "missing begin/finish interval")
    expected = [2 + len(entry.blocks) for entry in returned]
    need(counts == expected, "direct per-wrapper reference count")
    B = sum(len(entry.blocks) for entry in returned)
    need(sum(counts) == 2 * len(returned) + B, "2*T+B reference count")
    return {"T": len(returned), "B": B, "direct_references": sum(counts),
            "distinct_identities": len(wrappers), "zero_block_returns": expected.count(2)}


def fixture_operations(wrappers, blocks):
    operations = [("node",)]
    for w, bs in zip(wrappers, blocks):
        operations.append(("residual_begin", "idle", w))
        operations.extend(("block", w, b) for b in bs)
        operations.append(("residual_end", "idle", w))
    operations.append(("return",))
    return tuple(operations)


def synthetic():
    empty = ()
    three = (("forward", 0, 0), ("good", 1, 0), ("backward", 2, 0))
    plan = object()
    wrappers = [SyntheticWrapper(7, plan) for _ in range(3)]
    need(wrappers[0] == wrappers[1] and wrappers[0] is not wrappers[1], "equal-valued distinct control")
    blocks = [empty, three, empty]
    returned = [Returned(weakref.ref(w), b) for w, b in zip(wrappers, blocks)]
    operations = fixture_operations(wrappers, blocks)
    positive = inspect_operations(operations, returned)
    controls = []
    controls.append(reject("interned-wrapper fixture", lambda: inspect_operations(
        fixture_operations([wrappers[0]] * 3, blocks),
        [Returned(weakref.ref(wrappers[0]), b) for b in blocks]), "non-fresh"))
    missing_end = tuple(op for i, op in enumerate(operations) if i != len(operations)-2)
    controls.append(reject("missing-finish output fixture", lambda: inspect_operations(missing_end, returned), "missing finish"))
    removed = False
    missing_block = []
    for op in operations:
        if op[0] == "block" and not removed:
            removed = True
        else:
            missing_block.append(op)
    controls.append(reject("missing-block output fixture", lambda: inspect_operations(missing_block, returned), "missing/changed block"))
    substitute = replace(wrappers[1])
    changed = list(operations)
    position = next(i for i, op in enumerate(changed) if op[0] == "block")
    changed[position] = ("block", substitute, changed[position][2])
    controls.append(reject("same-value different-block-identity output fixture", lambda: inspect_operations(changed, returned), "block identity"))
    changed_end = list(operations)
    position = next(i for i, op in enumerate(changed_end) if op[0] == "residual_end")
    changed_end[position] = ("residual_end", "idle", replace(wrappers[0]))
    controls.append(reject("same-value different-finish-identity output fixture", lambda: inspect_operations(changed_end, returned), "finish identity"))
    # Independent weak-reference test: Code-like operations alone keep wrappers alive.
    def owned():
        ws = [SyntheticWrapper(i, None) for i in range(3)]
        return fixture_operations(ws, [empty]*3), [weakref.ref(w) for w in ws]
    owned_ops, refs = owned()
    gc.collect()
    need(all(r() is not None for r in refs), "operations must retain wrappers")
    del owned_ops
    gc.collect()
    need(all(r() is None for r in refs), "no hidden synthetic wrapper root")
    # An observer is an additional root: Code release alone need not end lifetime.
    observed_ops, observed_refs = owned()
    observer_holds = [observed_refs[0]()]
    del observed_ops
    gc.collect()
    need(observed_refs[0]() is not None and all(r() is None for r in observed_refs[1:]),
         "observer-held wrapper survives release of operations")
    observer_holds.clear()
    gc.collect()
    need(all(r() is None for r in observed_refs), "wrapper dies after observer releases its root")
    # An identity observer distinguishes sharing despite identical dataclass values.
    identity_observation = len({id(w) for w in wrappers})
    interned_observation = len({id(w) for w in [wrappers[0]] * 3})
    need(identity_observation == 3 and interned_observation == 1, "identity observer discriminates interning")
    return {"status": "passed", "positive": positive, "controls": controls,
            "observer_control": {"fresh_identities": identity_observation,
                                 "interned_identities": interned_observation,
                                 "lifetime": "observer reference extends lifetime beyond operations"},
            "weak_lifetime": "alive with operations, dead after operations released",
            "scope": "synthetic checker controls only; not evidence of original compiler execution"}


def source_pins():
    """Independent allowlist from the prior lifetime run, not a census import."""
    manifest = json.loads((HERE / "AUTHENTICATION.json").read_bytes())
    pins = manifest["lifetime_source_sha256"]
    need(len(pins) == 61, "61 lifetime source pins")
    live = {row["path"]: row["sha256"] for row in manifest["live_inputs"]}
    for rel, digest in pins.items():
        safe_source_path(rel)
        need(rel.startswith(CALLER + "/") and rel.endswith(".py"), "lifetime source scope")
        need(rel not in live or live[rel] == digest, "lifetime/live pin disagreement: " + rel)
    return pins


def safe_source_path(rel):
    need(isinstance(rel, str) and rel and "\\" not in rel, "POSIX source path")
    path = PurePosixPath(rel)
    need(not path.is_absolute() and not PureWindowsPath(rel).drive
         and ".." not in path.parts and path.as_posix() == rel and rel != ".",
         "safe repository-relative source path")
    return rel


class SourceLoader(importlib.abc.Loader):
    def __init__(self, path, root, records, pins, loaded_names):
        self.path, self.root = Path(path).absolute(), Path(root).resolve()
        self.records, self.pins, self.loaded_names = records, pins, loaded_names

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        self.loaded_names.add(module.__name__)
        need(self.path.is_relative_to(self.root), "source path outside root")
        key = safe_source_path(self.path.relative_to(self.root).as_posix())
        need(key in self.pins, "unlisted source import: " + key)
        need(self.path.resolve().is_relative_to(self.root) and self.path.is_file()
             and not self.path.is_symlink(), "regular contained source: " + key)
        need(self.path.name not in ("verify.py", "source_audit.py", "accounting.py", "extract_census.py"),
             "forbidden verifier/audit source: " + key)
        data = self.path.read_bytes()
        # Hash and compile the SAME bytes. No second read and no .pyc loader.
        digest = hashlib.sha256(data).hexdigest()
        need(digest == self.pins[key], "source hash mismatch: " + key)
        self.records[key] = digest
        module.__file__ = str(self.path)
        exec(compile(data, str(self.path), "exec", dont_inherit=True), module.__dict__)


class SourceFinder(importlib.abc.MetaPathFinder):
    def __init__(self, root, records, pins):
        self.root, self.records, self.pins = Path(root).resolve(), records, pins
        base = self.root / CALLER
        caller = base / "inputs/pr2753"
        self.directories = (base, caller, caller / "predecessor", caller / "predecessor/vendor",
                            base / "inputs/pr2769", base / "inputs/pr2769/vendor")
        self.loaded_names = set()
        self.names = {p.stem for directory in self.directories for p in directory.glob("*.py")}
        self.names.update(Path(rel).stem for rel in pins
                          if (self.root / rel).parent in self.directories and rel.endswith(".py"))
        self.names.add("bank_codec")

    def spec(self, name, path):
        return importlib.util.spec_from_loader(name, SourceLoader(
            path, self.root, self.records, self.pins, self.loaded_names), origin=str(path))

    def find_spec(self, fullname, path=None, target=None):
        if any(word in fullname for word in ("verif", "source_audit", "accounting", "extract_census")):
            raise Rejected("forbidden verifier/audit import: " + fullname)
        if "." in fullname:
            return None
        for directory in self.directories:
            candidate = directory / (fullname + ".py")
            rel = candidate.relative_to(self.root).as_posix()
            if rel in self.pins or candidate.is_file():
                # Missing pinned files must not fall back to an ambient module.
                return self.spec(fullname, candidate)
            need(not (directory / fullname / "__init__.py").is_file(),
                 "unlisted source package: " + fullname)
        return None

    def file_spec(self, name, location=None, *args, **kwargs):
        if location is not None and Path(location).absolute().is_relative_to(self.root):
            need(not args and not kwargs, "plain original source-file import")
            return self.spec(name, location)
        return self.previous_file_spec(name, location, *args, **kwargs)

    def __enter__(self):
        need(not self.names.intersection(sys.modules), "preloaded source module namespace")
        self.previous_meta, self.previous_path = list(sys.meta_path), list(sys.path)
        self.previous_file_spec = importlib.util.spec_from_file_location
        self.previous_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        sys.meta_path.insert(0, self)
        importlib.util.spec_from_file_location = self.file_spec
        return self

    def __exit__(self, *exc):
        importlib.util.spec_from_file_location = self.previous_file_spec
        sys.meta_path[:] = self.previous_meta
        sys.path[:] = self.previous_path
        sys.dont_write_bytecode = self.previous_bytecode
        for name in self.loaded_names:
            sys.modules.pop(name, None)


@contextmanager
def original_modules(root):
    root = Path(root).resolve()
    base = root / CALLER
    records = {}
    finder = SourceFinder(root, records, source_pins())
    with finder:
        # Deliberately bypass loader.authenticate (it runs an official verifier).
        # Load ORIGINAL definitions unchanged; seed the original loader's already-active
        # import state with the ORIGINAL codec. No public factory/compiler method patched.
        loader = importlib.import_module("loader")
        importlib.import_module("sources").ROOT = root
        spec = finder.spec("bank_codec", base / "inputs/pr2769/codec.py")
        codec = importlib.util.module_from_spec(spec)
        sys.modules["bank_codec"] = codec
        try:
            spec.loader.exec_module(codec)
        except BaseException:
            sys.modules.pop("bank_codec", None)
            raise
        loader._active = True
        modules = {name: importlib.import_module(name) for name in
                   ("macro_code", "macro_binding", "macro_machine", "catalogue", "sources", "plan", "low_codes")}
        yield modules, records


class TinyCatalogue:
    """Declared dimension-2 idle fixture; never constructs Catalogue/SelectedTopology."""
    dimension = 2
    q = 3
    lows = (I2, S2)
    def __init__(self, modules):
        self.modules = modules
        self.codes = modules["low_codes"].LowCodes(3, 2, 4)
        self.requests = tuple(NS(kind="IDLE") for _ in range(4))
    def low_classes(self):
        yield from self.lows
    def template_for(self, identifier, common):
        need(0 <= identifier < 4 and isinstance(common, bool), "tiny template guard")
        from fractions import Fraction as F
        eye = tuple(tuple(F(x) for x in row) for row in I2)
        base = ((F(1), F(0)), (F(0), F(0)))
        return self.modules["sources"].Template(3, 1, ("declared tiny", identifier), base, eye, eye)

class TinyTopology:
    dimension = 2
    replicas = 2
    schedule = ({"kind": "idle", "idx": 0},)
    idles = {0: (0, 1, 2, 3)}
    def __init__(self, catalogue):
        self.catalogue = catalogue
    def idle_family(self, identifier, replica):
        need(0 <= identifier < 4 and 0 <= replica < 2, "tiny idle guard")
        return replica * 4 + identifier


def selected_receiver(modules, specs):
    # __init__ hard-codes a 64x64 ambient bind; do NOT execute it on tiny data.
    receiver = object.__new__(modules["macro_binding"].SelectedBinding)
    receiver.specifications = specs
    receiver.catalogue = specs.catalogue
    receiver.codes = specs.catalogue.codes
    receiver.ambient = None  # residual never reads ambient
    return receiver


def seed_records(modules, specs):
    for identifier in range(4):
        for low in specs.catalogue.lows:
            code = specs.catalogue.codes.encode(identifier, False, low)
            template = specs.catalogue.template_for(identifier, False)
            # Actual source dataclass, deliberately supplied rather than claiming
            # selected compile_specification can generate dimension-2 records.
            specs[code] = modules["sources"].Specification(code, template, low, True)


def populate_plan_fixture(modules, specs):
    P, C, R = (getattr(modules["plan"], name) for name in ("Plan", "Command", "Reference"))
    plans = (P(2, 1, False, ()), P(2, 1, True, ()),
             P(2, 1, False, (C("add", 1, 0, R("head")), C("sign", 1, -1, R("fixed")))),
             P(2, 1, False, (C("child", 0, 1, R("unit")),)))
    blocks = ((), (("forward", 0, 0), ("good", 1, 0), ("backward", 2, 0)),
              (("sweep", 0, 0), ("sweep", 1, 0)),
              (("pair", 0, 0), ("pair", 0, 1), ("pair", 0, 2)))
    for identifier, plan in enumerate(plans):
        for low in specs.catalogue.lows:
            specs.plans[specs.catalogue.codes.encode(identifier, False, low)] = plan
    return blocks

class RecordingBinding:
    def __init__(self, receiver, blocks, intern=False):
        self.receiver, self.blocks, self.intern = receiver, blocks, intern
        self.returned, self.cache = [], {}
    def residual(self, identifier, common, low, mode):
        need(len(self.returned) < MAX_RETURNS, "factory-call size guard")
        need(len(low) <= MAX_DIMENSION and all(len(row) <= MAX_DIMENSION for row in low), "LOW dimension guard")
        key = (identifier, common, low, mode)
        if self.intern and key in self.cache:
            definition = self.cache[key]
        else:
            definition = self.receiver.residual(identifier, common, low, mode)
            if self.intern:
                self.cache[key] = definition
        need(definition.plan.dimension <= MAX_DIMENSION, "plan dimension guard")
        self.returned.append(Returned(weakref.ref(definition), self.blocks[identifier]))
        return definition


def compile_traced(modules, topology, binding):
    need(topology.dimension <= 2 and topology.catalogue.codes.dimension <= 2, "topology dimension guard")
    need(topology.replicas <= 2 and len(topology.schedule) <= 1 and len(topology.catalogue.lows) <= 2,
         "topology event guard")
    need(topology.replicas * len(topology.idles[0]) * len(topology.catalogue.lows) <= MAX_RETURNS, "preflight return bound")
    visited = {}
    events = 0
    start = time.monotonic()
    filename = modules["macro_code"].compile_node.__code__.co_filename
    def trace(frame, event, arg):
        nonlocal events
        if frame.f_code.co_filename != filename:
            return None
        events += 1
        need(events <= MAX_TRACE_EVENTS and time.monotonic()-start < 60, "trace work/time guard")
        operations = frame.f_locals.get("operations", ())
        need(len(operations) <= MAX_OPERATIONS, "emission operation guard")
        if frame.f_code.co_name == "residual" and event in ("line", "return"):
            for i, record in enumerate(binding.returned):
                wrapper = record.ref()
                need(wrapper is not None, "returned wrapper died during emission")
                n = sum(item is wrapper for op in operations for item in direct_refs(op))
                visited.setdefault(i, set()).add(n)
                if i < len(binding.returned)-1:
                    need(n == 2+len(record.blocks), "prior return not retained during later interval")
        return trace
    need(sys.gettrace() is None, "do not overwrite an existing tracer")
    try:
        sys.settrace(trace)
        code = modules["macro_code"].compile_node(topology, binding, mode=0)
    finally:
        sys.settrace(None)
    summary = inspect_operations(code.operations, binding.returned)
    for i, record in enumerate(binding.returned):
        required = set(range(3 + len(record.blocks)))
        need(required <= visited.get(i, set()), "missing factory/begin/block/finish lifetime trace")
    summary["emission_trace_events"] = events
    summary["per_return_observed_direct_counts"] = [sorted(visited[i]) for i in range(len(binding.returned))]
    return code, summary


def original(root=DEFAULT_ROOT):
    with original_modules(root) as (modules, imports):
        return original_fixture(modules, imports)


def original_fixture(modules, imports):
    cat = TinyCatalogue(modules)
    S = modules["catalogue"].Specifications
    # This rejection is an original-source limitation, not a positive fresh test.
    cold = S(cat)
    cold_result = reject("original cold Specifications dimension-2 rejection",
                         lambda: cold.bind(0, False, I2), "fixed raw low class")
    need(len(cold) == 0 and not cold.plans, "failed cold bind did not populate caches")
    specs = S(cat)
    seed_records(modules, specs)
    receiver = selected_receiver(modules, specs)
    first = receiver.residual(0, False, I2, 0)
    second = receiver.residual(0, False, I2, 0)
    need(first == second and first is not second, "original factory must allocate fresh equal wrappers")
    need(first.plan is second.plan is specs.plan(first.code), "source plan cache sharing")
    need(specs.bind(0, False, I2) is specs[first.code], "source record cache sharing")
    need(len(specs.plans) == 1, "original plan cache initially empty then populated once")
    # Factory refs are not roots in the source-record/plan caches.
    refs = (weakref.ref(first), weakref.ref(second))
    del first, second
    gc.collect()
    need(all(r() is None for r in refs), "specification caches unexpectedly retain wrappers")
    blocks = populate_plan_fixture(modules, specs)
    topology = TinyTopology(cat)
    binding = RecordingBinding(receiver, blocks)
    code, summary = compile_traced(modules, topology, binding)
    need((summary["T"], summary["B"], summary["direct_references"]) == (16, 32, 64), "declared fixture cardinalities")
    returned = list(binding.returned)  # weak references only
    # A second compile using already populated identical Specifications must
    # create a disjoint set of wrappers and leave the first code intact.
    binding2 = RecordingBinding(receiver, blocks)
    code2, summary2 = compile_traced(modules, topology, binding2)
    need(not ({id(r.ref()) for r in returned} & {id(r.ref()) for r in binding2.returned}), "cross-compilation wrapper reuse")
    # Test only ORIGINAL cached-owner geometry branch; no numeric Machine run.
    w = returned[0].ref()
    twin = replace(w)
    machine = object.__new__(modules["macro_machine"].Machine)
    page, layout, fields = object(), object(), object()
    machine.geometry_state = (w, page, layout, fields, None)
    with machine.geometry(w) as result:
        need(result == (page, layout, fields), "same-owner geometry reuse")
    def wrong_owner():
        with machine.geometry(twin):
            pass
    geometry_control = reject("original geometry rejects distinct equal wrapper while active", wrong_owner, "one active residual geometry")
    need(w == twin and w is not twin, "geometry control equal-value premise")
    del w, twin, machine, wrong_owner
    # Original compiler with intentionally DIFFERENT binding fixture. Not a
    # mutation of SelectedBinding.residual or compile_node.
    interned = RecordingBinding(receiver, blocks, intern=True)
    interned_code = modules["macro_code"].compile_node(topology, interned, 0)
    interned_control = reject("original compiler + interned binding fixture", lambda: inspect_operations(interned_code.operations, interned.returned), "non-fresh")
    del interned_code, interned
    gc.collect()
    need(all(r.ref() is not None for r in returned), "first Code owns all first-run wrappers")
    need(all(r.ref() is not None for r in binding2.returned), "second Code owns all second-run wrappers")
    del code
    gc.collect()
    need(all(r.ref() is None for r in returned), "first wrappers should die despite live specs and second Code")
    need(all(r.ref() is not None for r in binding2.returned), "second Code independently owns wrappers")
    del code2
    gc.collect()
    need(all(r.ref() is None for r in binding2.returned), "no hidden recorder/cache roots after Code release")
    return {"status": "passed", "first_compile": summary, "populated_recompile": summary2,
            "cold_original_rejection": cold_result, "geometry_control": geometry_control,
            "interned_binding_control": interned_control, "weak_lifetime": "two Code lifetimes independent; no wrapper roots in specs",
            "imports_sha256": imports,
            "bytecode_policy": "independent hash-checked source-only imports; no pyc reads/writes or cache directory",
            "loader_authenticate_executed": False, "loader_active_seeded": True,
            "limitations": ["original loader.authenticate bypassed; loader._active=True is seeded after codec import, not cold initialization",
                            "imported source bytes only: no original loader authentication or scientific receipt replay",
                            "SelectedBinding constructor and real cold selected specification not executed (64-only)",
                            "tiny seeded records and plan fixtures are not selected numerical endpoint proofs",
                            "geometry cached-owner branch only; no full numerical Machine execution",
                            "no source-request census/order validation and no native byte accounting"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--synthetic", action="store_true")
    modes.add_argument("--original", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                        help="repository/source-export root; unused in synthetic mode")
    args = parser.parse_args(argv)
    start = time.monotonic()
    result = synthetic() if args.synthetic else original(args.root)
    result.update(mode="synthetic" if args.synthetic else "original", python=sys.version,
                  elapsed_seconds=round(time.monotonic()-start, 6))
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
