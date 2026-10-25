"""Reject malformed sparse descriptors and expose omitted repair/inverse work."""

from unittest.mock import patch

from sparse_sources import require
from sparse_oracle import Case


def invalid_descriptors():
    from cardinal_counts import Count
    from check_support import no_decode
    from compact_layout import Layout
    from records import Tape
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from sparse_control import SparseControl
    cases = (
        (Case(((0, 0),), 1, 2, 1, 5), None, None, "source outside target set"),
        (Case(((1, 0), (1, 3)), 1, 2, 2, 5), None, None, "distinct sparse sources"),
        (Case(((2, 0), (4, 1)), 1, 2, 2, 5), None, None, "bounded source and ordered disjoint target guards"),
        (Case(((5, 0),), 1, 2, 1, 5), None, None, "bounded source and ordered disjoint target guards"),
        (Case(((1, 4),), 1, 2, 1, 5), None, None, "complete final target guard"),
        (Case(((2, 0),), 1, 2, 1, 5), 4, None, "canonical position field width"),
        (Case(((2, 0),), 1, 2, 1, 5), None, "short", "complete fixed-width binary key"),
        (Case(((2, 0),), 1, 2, 1, 5), None, "extra", "exact pair descriptor extent"),
        (Case(((4, 0), (1, 3)), 2, 2, 3, 5), None, None, "complete equal controls with active digits"),
        (Case(((2, 0),), 1, 2, 1, 5), None, "early", "sparse rotation reads only preceding fields"),
    )
    results = []
    for case, width_override, mutation, message in cases:
        w = case.position_bits if width_override is None else width_override
        bits = [(position >> bit) & 1 for pair in case.pairs for position in pair for bit in range(w)]
        if mutation == "short":
            bits = bits[:-1]
        elif mutation == "extra":
            bits.append(0)
        pairs = Tape()
        for bit in bits:
            pairs.append(bit)
        pairs.rewind()
        widths = tuple(Count.literal(value) for value in case.widths)
        args = tuple(Count.literal(value) for value in (len(case.pairs), w, case.K, case.G, 4))
        before = (bytes(pairs.cells), pairs.head,
                  tuple((bytes(x.tape.cells), x.tape.head) for x in (*widths, *args)))
        pool = ScratchPool(288)
        with no_decode(), sealed_constructors(), pool.install():
            plan = Layout(("u", "t", "y", "b"), widths, args[-1])
            control = SparseControl(pairs, *args[:4])
            if mutation == "early":
                control.operations = (("rotate", "y", ("y", "t"), "first_compact", 1),)
            try:
                control.validate(plan)
            except ValueError as exc:
                require(str(exc) == message, "specific descriptor rejection: " + str(exc))
            else:
                raise ValueError("invalid sparse descriptor accepted")
            plan.close()
            pool.empty()
        require(before == (bytes(pairs.cells), pairs.head,
                           tuple((bytes(x.tape.cells), x.tape.head) for x in (*widths, *args))),
                "failed descriptor validation preserves borrowed state")
        results.append(message)
        pairs.clear()
        for value in (*widths, *args):
            value.close()
    return results


def semantic_controls():
    import sparse_engine
    from check_sparse_payload import run_case
    from sparse_control import SparseControl
    mixed = Case(((2, 0),), 1, 5, 1, 5)
    controls = []
    with patch.object(sparse_engine, "repair", lambda source, *_args: source):
        try:
            run_case(mixed)
        except ValueError as exc:
            require(str(exc) == "complete sparse endpoint for every independent input bit", "omitted repair reaches endpoint check")
            controls.append("omitted_repair")
        else:
            raise ValueError("omitted repair passed the complete endpoint")
    original = SparseControl.execute_state

    def omit_inverse(self, state, layout, inverse=False):
        if not inverse:
            return original(self, state, layout, False)

    with patch.object(SparseControl, "execute_state", omit_inverse):
        try:
            run_case(mixed)
        except ValueError as exc:
            require(str(exc) in ("sorted exceptional destination fills this hole",
                                 "complete sparse endpoint for every independent input bit"),
                    "omitted inverse reaches repair/endpoint check: " + str(exc))
            controls.append("omitted_inverse")
        else:
            raise ValueError("omitted inverse passed complete repair")
    return controls


def empty_parameters():
    """An empty list must not exponentiate unused large guard parameters."""
    from cardinal_counts import Count
    from check_support import no_decode
    from compact_layout import Layout
    from records import Tape
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    import sparse_control
    from sparse_control import SparseControl
    pairs = Tape()
    widths = tuple(Count.literal(value) for value in (1, 1, 2, 1))
    args = tuple(Count.literal(value) for value in (0, 1, 10**6, 10**6, 4))
    pool = ScratchPool(288)
    with no_decode(), sealed_constructors(), pool.install():
        plan = Layout(("u", "t", "y", "b"), widths, args[-1])
        control = SparseControl(pairs, *args[:4])
        control.validate(plan)
        state = {name: Count.literal(value) for name, value in dict(u=1, t=0, y=3, b=1).items()}
        with patch.object(sparse_control, "power_two", side_effect=ValueError("unused guard exponentiation")):
            require(not control.bad(state), "empty descriptor is never exceptional")
            control.execute_state(state, plan)
        from check_sparse_controls import inspect_count
        require({name: inspect_count(value) for name, value in state.items()} == dict(u=1, t=0, y=3, b=1),
                "empty sparse word preserves arbitrary dirty fields")
        plan.close_state(state)
        plan.close()
        pool.empty()
    pairs.clear()
    for value in (*widths, *args):
        value.close()
    return True


def ownership_controls():
    from cardinal_counts import Count
    from check_sparse_payload import run_case
    from records import Tape
    from session import erase_marker, sealed_constructors
    engine, _result = run_case(Case((), 1, 1, 1, 1), consume=False)
    preserved = bytes(engine.output.cells)
    source, pairs, one, zero = Tape(), Tape(), Count.literal(1), Count.literal(0)
    try:
        try:
            engine.run(source, (), pairs, zero, one, one, one, one, one)
        except ValueError as exc:
            require(str(exc) == "consume previous compact output", "protected output reuse rejection")
        else:
            raise ValueError("unconsumed sparse output overwritten")
        require(bytes(engine.output.cells) == preserved, "rejected reuse preserves protected output")
        engine.output.clear()
        erase_marker(engine.output)
        try:
            engine.run(source, (), source, zero, one, one, one, one, one)
        except ValueError as exc:
            require(str(exc) == "distinct borrowed sparse payload and descriptor", "borrowed alias rejection")
        else:
            raise ValueError("aliased payload/pair tape accepted")
        with sealed_constructors():
            try:
                Tape()
            except ValueError as exc:
                require("physical allocation" in str(exc), "sealed physical constructor rejection")
            else:
                raise ValueError("runtime physical allocation accepted")
    finally:
        source.clear()
        pairs.clear()
        one.close()
        zero.close()
    return ["protected_output", "borrowed_alias", "physical_allocation"]


def run():
    return dict(status="PASS_SPARSE_BOUNDARY_CONTROLS", descriptors=invalid_descriptors(),
                empty_unused_guards=empty_parameters(), semantic=semantic_controls(), ownership=ownership_controls(),
                scope="Descriptor admission and deliberate semantic mutants; no interrupted-macro rollback claim.")
