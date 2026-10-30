"""Reach the retuned ordinary selector through actual monomial packets."""

from types import SimpleNamespace
import sys
from unittest.mock import patch

from active_sources import active, load_check, load_t74_binding, require


def run():
    reference = load_check(active().controller / "check_monomial.py", "active_check_monomial")
    import ordinary
    from cardinal_counts import Count
    from macro_code import Code
    from monomial_packets import MonomialPackets
    from records import Tape
    from retuned_native import profile, retune
    from session import erase_marker
    from words import BLANK
    from active_root import ActiveWidthRoot, production_layer
    from active_plan import ActiveWidthPlan
    from retuned_machine import RetunedMachine

    def fixture_native():
        return ordinary.Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                                 SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)

    built = []

    def fixed_factory(q):
        require(q == active().production.PRIME, "production factory receives its fixed prime")
        native = fixture_native()
        built.append(native)
        return native

    # Adapt Hiroki Kumazaki's PR3576 whole-factory and stale-alias checks.
    fixture = load_check(active().t74 / "check_runtime.py", "active_check_factory_fixture")
    bound = fixture.ZFixture()
    calls = []

    def fixed_binding(prepared):
        require(prepared == active().prepared, "production binding receives authenticated prepared source")
        calls.append("binding")
        return bound

    def observed_factory(q):
        calls.append("native")
        return fixed_factory(q)

    with patch.object(active().production, "build_native", observed_factory), \
            patch.object(active().t74_binding, "T74Binding", fixed_binding):
        layer = production_layer()
    native = built[0]
    require(calls == ["binding", "native"] and isinstance(layer, ActiveWidthRoot)
            and isinstance(layer.plan, ActiveWidthPlan) and isinstance(layer.machine, RetunedMachine)
            and layer.machine.binding is bound and layer.closed,
            "complete binding/native/actual-root production constructor flow")
    require(built == [native] and native.closed and native.profile == profile(),
            "root owns the retuned native in its closed entry state")
    saved_path, saved_binding = sys.path[:], sys.modules.get("binding")
    try:
        load_t74_binding(active().t74)
    except ValueError as exc:
        require(str(exc) == "fresh T74 binding namespace", "stale binding alias rejection")
    else:
        raise ValueError("accepted a stale T74 binding alias")
    require(sys.path == saved_path and sys.modules.get("binding") is saved_binding
            and sys.modules["active_t74_binding"] is active().t74_binding,
            "rejected alias preserves both module namespaces and import paths")
    native = retune(fixture_native())
    engine = MonomialPackets(("u", "t", "v0", "v1", "b"), ("v0", "v1"), native)
    literal = dict(matrix_rows=[3, 1], offset=1, phase=1, linear_Z4=[1, 2], quadratic_rows=[2, 0])
    engine.select(literal)
    dims = (1, 1, 2, 2, 1)
    widths = tuple(Count.literal(v) for v in dims)
    args = tuple(Count.literal(v) for v in (2, 1, 1, 0, 4, 1, 1))
    raw = reference.encode([(i*5) % 7-3 for i in range(2*(1 << sum(dims)))], 4)
    source = Tape()
    for bit in raw:
        source.append(bit)
    source.rewind()
    selected = []
    original_select = ordinary.select

    def observe_select(width, q, compiled):
        selected.append((compiled.numerator, compiled.denominator))
        return original_select(width, q, compiled)

    try:
        with patch.object(ordinary, "select", observe_select):
            for inverse in (False, True):
                result = engine.run(source, widths, *args, inverse=inverse)
                actual = bytes(result.cells[1:]).rstrip(bytes([BLANK]))
                require(actual == reference.oracle(raw, dims, literal, 2, 4, 1, inverse),
                        "complete monomial address and phase endpoint")
                require(bytes(source.cells[1:]).rstrip(bytes([BLANK])) == raw, "native-flow input preservation")
                result.clear()
                erase_marker(result)
        require(len(selected) == 40 and set(selected) == {(1, 577)}, "actual native selector flow")
        require(native.closed and engine.closed and engine.compact.closed
                and not engine.pool.live, "completed native and compact calls")
        try:
            retune(native)
        except ValueError as exc:
            require(str(exc) == "fresh native from the active cohort", "late retuning rejection")
        else:
            raise ValueError("retuned an already consumed native lifecycle")
    finally:
        source.clear()
        for count in (*widths, *args):
            count.close()
    return {"status": "PASS_RETUNED_T74_NATIVE_FLOW", "packets": 2, "bits_each": len(raw),
            "selector_calls": len(selected), "profiles": sorted(set(selected)),
            "compact_calls": dict(engine.compact.calls), "late_retuning_rejected": True,
            "production_constructor_flow": [*calls, "actual_root"], "stale_binding_rejected": True,
            "scope": "Actual reduced tape calls; fixed production construction is observed, not GL64-executed."}
