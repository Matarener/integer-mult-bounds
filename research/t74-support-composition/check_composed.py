"""Checker-only Gaussian oracles and complete composed invocation fixtures."""

from collections import Counter as Observations
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import sys
import tempfile

from composed_sources import active, require


def selected_tape(n, selected):
    from records import Tape
    width = max(1, (n-1).bit_length())
    result = Tape()
    for value in selected:
        for bit in range(width):
            result.append((value >> bit) & 1)
    result.rewind()
    return result


def fixture(policy="standard", fast_root=False):
    from active_plan import ActiveWidthPlan
    from active_root import ActiveWidthRoot
    from composed_engine import ComposedRoot
    from macro_code import Code
    from retuned_native import retune
    from router_engine import Router
    state = active()
    if not hasattr(state, "fixture_module"):
        state.fixture_module = state.root_sources.load_check(
            state.root.t74 / "check_runtime.py", "active_check_composed_fixture")
        with patch.dict(sys.modules, {"check_runtime": state.fixture_module}):
            state.root_helper = state.root_sources.load_check(
                state.root.t74 / "check_root_runtime.py", "active_check_composed_root_helpers")
    binding = state.fixture_module.ZFixture()
    if fast_root:
        binding.cover = state.root_helper.OneCover()
        from cardinal_counts import Count
        from encoded import compare
        from machine import copy_symbols
        from session import sealed_constructors

        class PersistentFixturePlan(ActiveWidthPlan):
            """One compiled reduced root with a real spectator and two coefficients."""
            def compute(self, *arguments):
                require(self.closed and not self.pool.live, "closed fixed root fixture")
                self.clear()
                values = dict(precision=8, selected=7, left=1, right=0, coefficients=2, outer_rows=1,
                              residue=0, zero=0, d=7, K=1, G=1, H=1, depth=2, q0=2, qF=2, qB=1,
                              Q0=5, delta=28, input_bits=10, work_bits=67, gaussians=512, prefixes=2,
                              original_rows=4, padded_rows=4, stock=4, row_bits=8576,
                              core_width=2, core_front=0, core_back=0)
                with sealed_constructors(), self.scope.installed():
                    for actual, expected in zip(arguments, (8, 7, 1, 0, 2, 1, 0)):
                        constant = Count.literal(expected)
                        try:
                            require(compare(actual, constant) == 0, "fixed persistent-record root fixture")
                        finally:
                            constant.close()
                    for name, value in values.items():
                        constant = Count.literal(value)
                        try:
                            copy_symbols(constant.tape, self.roles[name])
                        finally:
                            constant.close()
                    self.pool.empty()
                self.fast = True
                self.closed = True
                return self

        plan = PersistentFixturePlan(2, 1, 2, guard_exponent=2)
    else:
        plan = ActiveWidthPlan(2, 1, 4, guard_exponent=2)

    def native():
        return retune(state.root.ordinary.Ordinary(
            2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
            (Code((("unreachable",),), 0),), capacity=64))

    visits = Observations()
    router = Router(native())
    root = ActiveWidthRoot(binding, native(), binding.catalogue, plan,
                           lambda _machine, event: visits.update([event]))
    return ComposedRoot(router, root, policy), visits


def encode(values, width):
    result = bytearray()
    for pair in values:
        for value in pair:
            require(-(1 << (width-1)) <= value < 1 << (width-1), "checker signed input width")
            result.extend((value >> bit) & 1 for bit in range(width))
    return bytes(result)


def truncate(value):
    return int(value)  # Checker-only truncation of Fraction toward zero.


def oracle(values, n, selected, r, C, truncate_each=False):
    current = [tuple(Fraction(v) for v in pair) for pair in values]
    for bit in selected:
        stride = 1 << bit
        for row in range(C):
            for address in range(1 << n):
                if address & stride:
                    continue
                for coefficient in range(r):
                    a = (row*(1 << n)+address)*r+coefficient
                    b = (row*(1 << n)+address+stride)*r+coefficient
                    old_a, old_b = current[a], current[b]
                    current[a] = tuple((x+y)/2 for x, y in zip(old_a, old_b))
                    current[b] = tuple((x-y)/2 for x, y in zip(old_a, old_b))
        if truncate_each:
            current = [tuple(Fraction(truncate(v)) for v in pair) for pair in current]
    return [tuple(truncate(v) for v in pair) for pair in current]


def body(tape):
    from check_support import bits
    return bits(tape)


def run_packet(n, p, selected, r=1, C=1, policy="standard", fast_root=False,
               values=None, owner=None, consume=True):
    from cardinal_counts import Count
    from check_support import no_decode
    from records import Tape
    from session import erase_marker
    from words import BLANK
    machine, visits = fixture(policy, fast_root) if owner is None else owner
    count = C*(1 << n)*r
    if values is None:
        values = [((i*3) % 7-3, (i*11) % 5-2) for i in range(count)]
    require(len(values) == count and all(a*a+b*b <= 1 << (2*p) for a, b in values),
            "complete checker input inside unit disk")
    original = encode(values, p+2)
    expected = encode(oracle(values, n, selected, r, C), p+2)
    payload, positions = Tape(), selected_tape(n, selected)
    for bit in original:
        payload.append(bit)
    payload.rewind()
    counts = tuple(Count.literal(v) for v in (n, p, len(selected), max(1, (n-1).bit_length()), r, C))
    saved = tuple((bytes(value.tape.cells), value.tape.head) for value in counts)
    saved_positions = (bytes(positions.cells), positions.head)
    before, root_before = dict(machine.calls), dict(visits)
    root_calls, route_calls = [], []
    profiles = []
    original_transform, original_route = machine.root.run, machine.router.run
    original_select = active().root.ordinary.select
    from check_support import inspect_count

    def observe_root(source, *args):
        root_calls.append(tuple(inspect_count(value) for value in args))
        return original_transform(source, *args)

    def observe_route(source, descriptor, *args):
        route_calls.append(tuple(inspect_count(value) for value in args))
        return original_route(source, descriptor, *args)

    def observe_select(width, q, profile):
        profiles.append((profile.numerator, profile.denominator))
        return original_select(width, q, profile)

    try:
        with no_decode(), patch.object(machine.root, "run", observe_root), patch.object(machine.router, "run", observe_route), \
                patch.object(active().root.ordinary, "select", observe_select):
            returned = machine.run(payload, positions, *counts)
        require(body(returned) == expected, "complete composed endpoint on original selected coordinates")
        require(body(payload) == original and payload.head == returned.head == 1,
                "preserved composed input and canonical return")
        require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in counts)
                and saved_positions == (bytes(positions.cells), positions.head), "preserved selected descriptor and parameters")
        machine.idle()
        require(machine.closed and machine.current is None and not machine.pool.live, "closed composed owner")
        require(machine.root.machine.closed and machine.root.plan.closed and not machine.root.plan.pool.live
                and all(tape.head == 1 and tape.read() == BLANK for tape in machine.root.plan.roles.values()),
                "restored inherited root machine and planning baselines")
        for tape in machine.pool.tapes:
            require(tape.head == 1 and all(bit == BLANK for bit in tape.cells), "blank composed-owned bodies and markers")
        calls = {key: machine.calls[key]-before[key] for key in before}
        events = {key: visits[key]-root_before.get(key, 0) for key in visits}
        require(events.get("enter", 0) == events.get("return", 0), "balanced root child visits")
        require(not profiles or set(profiles) == {(1, 577)}, "actual shared retuned ordinary selector")
        result = dict(n=n, p=p, selected=selected, coefficients=r, rows=C, gaussians=count,
                      payload_bits=len(original), mode=machine.last_mode, calls=calls,
                      root_calls=root_calls, route_calls=route_calls, visits=events,
                      peak=machine.pool.peak, selector_calls=len(profiles),
                      output_sha256=sha256(expected).hexdigest())
        if machine.last_mode == "composed":
            ell = 1 if policy == "fixture-ell1" else (p-1).bit_length()**2
            require(calls == dict(swaps=2, routes=2, roots=1, lifts=0, truncations=0),
                    "complete exposure-root-inverse invoice")
            require(root_calls[0][4] == r*(1 << ell)
                    and all(call[4] == 2*(p+2)*r*(1 << ell) for call in route_calls),
                    "actual persistent coefficient records at both routers and root")
        elif machine.last_mode == "literal":
            require(calls == dict(swaps=0, routes=0, roots=len(selected), lifts=1, truncations=1)
                    and all(call[0] == p+len(selected) and call[1] == 1 for call in root_calls),
                    "lifted exact-grid literal branch with one final truncation")
        if consume:
            returned.clear()
            erase_marker(returned)
        return (machine, visits), result
    finally:
        payload.clear()
        positions.clear()
        for value in counts:
            value.close()


def direct():
    owner, standard = run_packet(4, 2, (0,))
    _, identity = run_packet(3, 5, (), r=2, C=2, owner=owner)
    _, moved = run_packet(5, 5, (0, 1), policy="fixture-ell1")
    require(standard["mode"] == moved["mode"] == "composed" and identity["mode"] == "identity",
            "standard and reduced-suffix complete composed endpoints")
    return dict(status="PASS_COMPOSED_DIRECT_RETURNS", cases=[standard, identity, moved])


def literal():
    values = [(-3, 0), (-2, 0), (-3, 0), (0, 0)]
    expected = oracle(values, 2, (0, 1), 1, 1)
    naive = oracle(values, 2, (0, 1), 1, 1, truncate_each=True)
    require(expected != naive, "discriminating repeated-truncation witness")
    owner, first = run_packet(2, 3, (0, 1), values=values)
    _, second = run_packet(3, 5, (0, 2), r=2, C=3, owner=owner)
    require(first["mode"] == second["mode"] == "literal", "small-geometry literal coverage")
    return dict(status="PASS_COMPOSED_LITERAL_GRID", cases=[first, second],
                exact_then_truncate=expected, premature_truncation=naive)


def fast():
    selected = (0, 1, 2, 3, 4, 5, 7)
    mask = sum(1 << bit for bit in selected)
    alternate = sum(1 << bit for bit in selected[::2])
    values = []
    for address in range(512):
        magnitude = 8*(1+((address >> 6) & 1)+2*((address >> 8) & 1))
        values.append(((-1 if (address & mask).bit_count() % 2 else 1)*magnitude,
                       (-1 if (address & alternate).bit_count() % 2 else 1)*(magnitude+8)))
    require(any(a or b for a, b in oracle(values, 9, selected, 1, 1)), "nonzero complete fast-root witness")
    _, result = run_packet(9, 8, selected, policy="fixture-ell1", fast_root=True, values=values)
    require(result["mode"] == "composed" and result["visits"].get("enter", 0) > 0,
            "complete physical composition through recursive T74 root")
    return dict(status="PASS_COMPOSED_RECURSIVE_RETURN", result=result,
                scope="Reduced external suffix and root reservations, q2 native; actual complete physical router/root/inverse.")


def sources():
    import composed_sources
    import composed_engine
    import native_sources
    from active_plan import ActiveWidthPlan
    from macro_code import Code
    from retuned_native import retune
    from check_composed_failures import rejects
    state = active()
    require(state.compact_counts == (21, 15) and len(state.bridge.compared_backend) == 23,
            "complete shared source comparisons")
    require(state.bridge.source is native_sources.activate()[0] and isinstance(state.root.source, Path),
            "distinct source-module and source-path context contracts")
    fixture_module = state.root_sources.load_check(
        state.root.t74 / "check_runtime.py", "active_check_composed_factory_binding")
    binding, natives = fixture_module.ZFixture(), []

    def finite_native():
        value = retune(state.root.ordinary.Ordinary(
            2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
            (Code((("unreachable",),), 0),), capacity=64))
        natives.append(value)
        return value

    with patch.object(composed_engine, "build_native", finite_native), \
            patch.object(state.root.t74_binding, "T74Binding", lambda _prepared: binding):
        joined = composed_engine.production_layer()
    joined.idle()
    require(len(natives) == 2 and natives[0] is not natives[1]
            and joined.router.binary.native is natives[0] and all(value.closed for value in natives)
            and type(joined.root.plan) is ActiveWidthPlan and joined.policy == "standard",
            "actual production constructor flow owns two fresh natives and the actual-width plan")
    rejected = []

    def nested_runtime():
        with composed_sources.opened():
            raise ValueError("unexpected nested runtime")

    rejected.append(rejects(nested_runtime, "second cold composition runtime", "cold composition namespace"))
    with tempfile.TemporaryDirectory(prefix="composed-source-controls-") as directory:
        base = Path(directory)
        for name in composed_sources.PINS:
            original = composed_sources.authenticate(name)
            altered = base / name
            data = bytearray(original.read_bytes())
            data[-1] ^= 1
            altered.write_bytes(data)
            rejected.append(rejects(lambda: composed_sources.authenticate(name, altered),
                                    "altered " + name, "pinned composition source"))
        alias = base / "source-alias.tar"
        alias.symlink_to(original)
        rejected.append(rejects(lambda: composed_sources.authenticate(name, alias), "source symlink", "regular composition export"))
        compact_root = state.bridge.roots["compact-export.tar"]
        manifest = json.loads((compact_root / ".research-export.json").read_text())
        changed = base / "compact-control"
        changed.mkdir()
        (changed / ".research-export.json").write_text(json.dumps(manifest))
        first = manifest["files"][0]["path"]
        member = changed / first
        member.parent.mkdir(parents=True)
        member.write_bytes((compact_root / first).read_bytes()+b"\n")
        rejected.append(rejects(lambda: composed_sources.compare_compact(changed, state.bridge.compact, native_sources.ROOT),
                                "changed Compact cohort member", "shared Compact cohort bytes"))
    return dict(status="PASS_COMPOSED_SOURCE_COHORT", compact_package_files=21,
                compact_external_files=15, ordinary_backend_files=23, production_factory_calls=2,
                factory_scope="Actual constructor with explicit finite provider substitutes; no GL64 compilation.",
                rejected=rejected)


def metadata():
    from check_composed_metadata import run
    return run()


def failures():
    from check_composed_failures import run
    return run()


def budget():
    from check_composed_budget import run
    return run()
