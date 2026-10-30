"""Check variable encoded positions, raw inverse, guards and sparse endpoints."""

from hashlib import sha256
import json
from random import Random

from sparse_sources import active, require
from sparse_oracle import Case


def inspect_count(count):
    from words import RIGHT
    result = 0
    tape = getattr(count.tape, "physical", count.tape)
    for index, bit in enumerate(tape.cells[1:]):
        if bit == RIGHT:
            return result
        require(bit in (0, 1), "observed canonical Count")
        result |= bit << index
    raise ValueError("unterminated observed Count")


def descriptor(case):
    from records import Tape
    tape = Tape()
    for pair in case.pairs:
        for position in pair:
            for bit in range(case.position_bits):
                tape.append((position >> bit) & 1)
    tape.rewind()
    return tape


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from compact_layout import Layout
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from sparse_control import SparseControl, WORD
    require(WORD == active().reference.Compact(1, 1, 1, 0, "y", "y", True).operations(),
            "retained late-source chronology with explicit same-y packing")
    rng, digest = Random(16733599), sha256()
    totals = dict(states=0, offsets=0, good=0, bad=0, peak=0, repair_witnesses=0)
    cases = (
        (Case(((5, 1), (15, 10), (25, 21)), 2, 7, 8, 29), []),
        (Case(((1, 0),), 2, 6, 2, 6), [dict(u=1, t=1, y=18, b=3)]),
        (Case(((4, 0),), 1, 5, 2, 5), [dict(u=3, t=3, y=31, b=2)]),
        (Case(((1, 0), (6, 5)), 1, 5, 3, 10), [dict(u=7, t=0, y=594, b=5)]),
        (Case(((1, 0), (8, 7), (17, 16)), 2, 6, 8, 22), [dict(u=169, t=73, y=1313170, b=217)]),
        (Case(((4, 0), (1, 3)), 1, 2, 2, 5), []),
        (Case((), 1, 1, 2, 5), []),
    )
    for case, specific in cases:
        pairs = descriptor(case)
        widths = tuple(Count.literal(value) for value in case.widths)
        args = tuple(Count.literal(value) for value in (len(case.pairs), case.position_bits, case.K, case.G, 4))
        before = (bytes(pairs.cells), pairs.head, tuple((bytes(x.tape.cells), x.tape.head) for x in (*widths, *args)))
        states = list(specific)
        states.extend({name: rng.randrange(1 << width) for name, width in zip(("u", "t", "y", "b"), case.widths)}
                      for _ in range(8))
        for _ in range(6):
            good = case.good_state(rng)
            if good is not None:
                states.append(good)
        pool = ScratchPool(288)
        with no_decode(), sealed_constructors(), pool.install():
            plan = Layout(("u", "t", "y", "b"), widths, args[-1])
            control = SparseControl(pairs, *args[:4])
            control.validate(plan)
            for raw in states:
                state = {name: Count.literal(value) for name, value in raw.items()}
                try:
                    bad = control.bad(state)
                    require(bad == case.bad(raw), "encoded sparse guard")
                    totals["bad" if bad else "good"] += 1
                    for operation in WORD:
                        if operation[0] != "rotate":
                            continue
                        value = control.offset(state, operation, plan)
                        expected = operation[-1]*case.offset(raw, operation[3]) % (1 << dict(zip(plan.names, case.widths))[operation[1]])
                        require(inspect_count(value) == expected, "encoded variable-position signed offset")
                        value.close()
                        prefix = {name: Count.literal(raw[name] if plan.names.index(name) < plan.names.index(operation[1]) else 0)
                                  for name in plan.names}
                        try:
                            value = control.offset(prefix, operation, plan)
                            require(inspect_count(value) == expected, "offset reads only the supplied prefix")
                            value.close()
                        finally:
                            plan.close_state(prefix)
                        totals["offsets"] += 1
                    control.execute_state(state, plan)
                    observed = {name: inspect_count(value) for name, value in state.items()}
                    expected = case.raw(raw)
                    require(observed == expected and control.bad(state) == bad, "raw sparse word and invariant bad set")
                    if not bad:
                        require(expected == case.ideal(raw), "guarded sparse XOR with sources inside guards")
                    if expected != case.ideal(raw):
                        totals["repair_witnesses"] += 1
                    require(case.raw(expected, True) == raw, "independent current-state inverse")
                    control.execute_state(state, plan, True)
                    require({name: inspect_count(value) for name, value in state.items()} == raw,
                            "encoded current-control inverse")
                    control.ideal_state(state)
                    require({name: inspect_count(value) for name, value in state.items()} == case.ideal(raw),
                            "encoded simultaneous sparse XOR endpoint")
                    digest.update(json.dumps((raw, expected, case.ideal(raw), bad), sort_keys=True).encode())
                    totals["states"] += 1
                finally:
                    plan.close_state(state)
            plan.close()
            pool.empty()
        require(before == (bytes(pairs.cells), pairs.head,
                           tuple((bytes(x.tape.cells), x.tape.head) for x in (*widths, *args))),
                "borrowed pair tape and encoded descriptors preserved")
        totals["peak"] = max(totals["peak"], pool.peak)
        pairs.clear()
        for value in (*widths, *args):
            value.close()
    require(totals["good"] and totals["bad"] and totals["repair_witnesses"], "both guard regimes and necessary repair")
    # A same-y early-source rotation would read its own target and lose injectivity.
    early = lambda y: (y + 2*((y >> 1) & 1)) % 64
    require(early(18) == early(20) == 20 and all(8 <= y//2 < 24 for y in (18, 20)),
            "good-address collision rejects the naive early-source adaptation")
    return dict(status="PASS_ENCODED_SPARSE_CONTROLS", **totals, state_sha256=digest.hexdigest(),
                early_source_collision=[18, 20, 20],
                scope="Encoded finite states and written all-size obligations; no materialization of the large state spaces.")
