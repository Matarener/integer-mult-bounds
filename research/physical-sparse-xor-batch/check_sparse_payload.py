"""Move complete Gaussian records and track each independent input bit."""

from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch

from sparse_sources import active, load_check, require
from sparse_oracle import Case
from check_sparse_controls import descriptor


def run_case(case, outer=1, engine=None, consume=True):
    from cardinal_counts import Count
    from check_support import no_decode
    from macro_code import Code
    from provenance import Provenance
    from records import Tape
    from session import erase_marker
    from sparse_control import SparseControl
    from sparse_engine import SparseEngine
    state = active()
    helpers = getattr(run_case, "helpers", None)
    if helpers is None:
        helpers = load_check("check_payload.py", "sparse_check_payload_helpers")
        run_case.helpers = helpers
    if engine is None:
        native = state.ordinary.Ordinary(
            2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
            (Code((("unreachable",),), 0),), capacity=64,
            profile=state.encoded.Profile(numerator=1, denominator=577))
        engine = SparseEngine(native)
    record_bits = 4  # Two complete two-bit signed Gaussian components.
    widths = tuple(Count.literal(value) for value in case.widths)
    args = tuple(Count.literal(value) for value in
                 (len(case.pairs), case.position_bits, case.K, case.G, record_bits, outer))
    pairs = descriptor(case)
    source = Tape()
    records = 1 << sum(case.widths)
    length = outer*records*record_bits
    for index in range(length):
        source.append((index*11 ^ index//7 ^ 5) & 1)
    source.rewind()
    original = helpers.body(source)
    saved = (bytes(pairs.cells), pairs.head,
             tuple((bytes(value.tape.cells), value.tape.head) for value in (*widths, *args)))
    expected, masks = bytearray(length), [0]*length
    guard_expected = {False: 0, True: 0}
    for row in range(outer):
        for ordinal in range(records):
            initial = case.decode(ordinal)
            target = case.encode(case.ideal(initial))
            guard_expected[case.bad(initial)] += 1
            for bit in range(record_bits):
                origin = (row*records+ordinal)*record_bits+bit
                destination = (row*records+target)*record_bits+bit
                expected[destination], masks[destination] = original[origin], 1 << origin
    observer = Provenance(length)
    observer.mark(source)
    original_bad, guard_actual = SparseControl.bad, {False: 0, True: 0}
    original_select, profiles = state.ordinary.select, []
    before = dict(engine.calls)

    def observe_bad(control, values):
        value = original_bad(control, values)
        guard_actual[value] += 1
        return value

    def observe_select(width, q, profile):
        profiles.append((profile.numerator, profile.denominator))
        return original_select(width, q, profile)

    def forbidden(*_args, **_kwargs):
        raise ValueError("indexed sparse oracle reached during physical execution")

    try:
        with no_decode(), observer.installed(), patch.object(SparseControl, "bad", observe_bad), \
                patch.object(state.ordinary, "select", observe_select), \
                patch.multiple(Case, raw=forbidden, ideal=forbidden, offset=forbidden,
                               bad=forbidden, mask=forbidden, pack=forbidden, encode=forbidden, decode=forbidden):
            returned = engine.run(source, widths, pairs, *args)
        require(helpers.body(returned) == expected and observer.masks(returned, length) == tuple(masks),
                "complete sparse endpoint for every independent input bit")
        require(helpers.body(source) == original and source.head == returned.head == 1,
                "borrowed payload and protected output heads")
        require(saved == (bytes(pairs.cells), pairs.head,
                          tuple((bytes(value.tape.cells), value.tape.head) for value in (*widths, *args))),
                "borrowed sparse descriptor and counts preserved")
        helpers.closed_work(engine)
        require(guard_actual == guard_expected, "complete good/bad census")
        calls = {key: engine.calls[key]-before[key] for key in before}
        require(calls == dict(ordinary=12*outer, rotations=10*outer, rows=outer),
                "fixed operation count per complete row")
        require(profiles and set(profiles) == {(1, 577)}, "actual retuned selector flow")
        result = dict(pairs=len(case.pairs), widths=case.widths, outer_rows=outer, records=outer*records,
                      payload_bits=length, good=guard_actual[False], bad=guard_actual[True], calls=calls,
                      selector_calls=len(profiles), profile=[1, 577], peak=engine.pool.peak,
                      output_sha256=sha256(expected).hexdigest())
        if consume:
            returned.clear()
            erase_marker(returned)
        return engine, result
    finally:
        source.clear()
        pairs.clear()
        for value in (*widths, *args):
            value.close()


def mixed():
    engine, first = run_case(Case(((2, 0),), 1, 5, 1, 5))
    require((first["good"], first["bad"]) == (32, 224), "mixed source-in-guard fixture")
    _engine, reused = run_case(Case((), 1, 1, 1, 2), outer=2, engine=engine)
    require(reused["bad"] == 0, "empty descriptor gives identity on both rows")
    return dict(status="PASS_SPARSE_MIXED_GAUSSIAN_PACKET", cases=[first, reused],
                scope="Complete reduced Gaussian records, mixed guard and output reuse; no production rate execution.")


def multiple():
    _engine, result = run_case(Case(((4, 0), (1, 3)), 1, 2, 2, 5))
    require((result["good"], result["bad"]) == (0, 2048), "complete all-bad multi-pair fixture")
    return dict(status="PASS_SPARSE_MULTIPAIR_GAUSSIAN_PACKET", result=result,
                scope="Complete reduced-guard two-pair packet; full repair semantics, not a sparse bad fraction.")
