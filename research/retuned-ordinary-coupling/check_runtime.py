"""Use the retuned factory for real ordinary and binary tape returns."""

import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interface
from predecessor import close, require, runtime


def run():
    ordinary, encoded, _ = runtime()
    import check_engine
    from cardinal_counts import Count
    from check_join import body
    from check_support import no_decode
    from physical_words import PhysicalWord
    from provenance import Provenance
    from records import Tape
    from words import BLANK, Word

    class SmallBinding(check_engine.Binding):
        """Declare one unused row for this reduced GL2 fixture."""
        def check_stock(self, machine):
            one = Count.literal(1)
            try:
                require(one.equals(machine.count("unused")), "reduced exact unused row")
            finally:
                one.close()

    with patch.object(check_engine, "Ordinary", interface.ordinary), \
            patch.object(check_engine, "Binding", SmallBinding):
        native = check_engine.fixture_engine()
    require(native.profile == interface.profile(), "factory binds the actual retuned backend")
    selected_profiles = []
    select = ordinary.select

    def observe_select(original, q, profile):
        selected_profiles.append(profile)
        return select(original, q, profile)

    with patch.object(ordinary, "select", observe_select):
        fallback = check_engine.check_case(native, 2, 2, 3, 2, False)
    require(selected_profiles == [interface.profile()], "Ordinary.run passes the certified profile")

    # A declared reduced wrapper plan checks two genuine padded C0 returns.
    # It does not claim that the selected c profile admits this tiny width.
    payload = Tape()
    for index in range(256):
        payload.append(((index*13) ^ (index >> 2) ^ 0x53) & 1)
    payload.rewind()
    initial = body(payload)
    provenance = Provenance(384)
    provenance.mark(payload)
    returns, pending = [], []

    def observe(stage, padded, returned):
        if stage == "before":
            require(not pending, "one padded root")
            pending.append((body(padded), provenance.masks(padded, 384)))
            return
        saved, masks = pending.pop()
        expected, expected_masks = bytearray(384), [0]*384
        for address, bit in enumerate(saved):
            row, rest = divmod(address, 64)
            first, rest = divmod(rest, 16)
            gap, second = divmod(rest, 4)
            reverse_first = ((first & 1) << 1) | (first >> 1)
            reverse_second = ((second & 1) << 1) | (second >> 1)
            target = row*64 + reverse_second*16 + gap*4 + reverse_first
            expected[target], expected_masks[target] = bit, masks[address]
        require(body(returned) == expected and provenance.masks(returned, 384) == tuple(expected_masks),
                "each padded C0 endpoint before cancellation")
        require(body(padded) == saved and padded.head == returned.head == 1, "padded input preservation")
        returns.append(len(saved))

    native.observe = observe
    original, one = Count.literal(4), Count.literal(1)

    def reduced_plan():
        values = {"width": 1, "depth": 1, "stock": 3, "rows": 4,
                  "borrowed": 2, "body": 2, "remainder": 0}
        return {"fits": True, **{name: Count.literal(value) for name, value in values.items()}}

    def forbidden(*args, **kwargs):
        raise ValueError("runtime numerical decoding or Word allocation")

    with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden):
        output = native.execute_plan(payload, original, one, one, one, reduced_plan)
        expected, masks = bytearray(256), [0]*256
        for address, bit in enumerate(initial):
            first, second = divmod(address, 16)
            target = second*16+first
            expected[target], masks[target] = bit, 1 << address
        require(body(output) == expected and provenance.masks(output, 256) == tuple(masks),
                "complete reduced ordinary endpoint")
        require(body(payload) == initial and returns == [384, 384] and not pending,
                "both completed restrictions and borrowed input")
        work = [*native.pool.tapes, *native.runtime.pool.tapes, *native.runtime.roles.values(),
                *native.runtime.handoff.values(), native.runtime.output]
        for bank in (*native.banks, native.runtime.arena, native.runtime.indices):
            require(not bank.live and not bank.initialized, "closed numerical banks")
            work.extend(word.tape for word in (*bank.words, bank.template))
        require(all(all(bit == BLANK for bit in tape.cells) for tape in work), "owned work erasure")
        output.clear()
    payload.clear()
    original.close()
    one.close()

    native.observe = None
    binary = interface.binary(native)
    payload = Tape()
    for index in range(16):
        payload.append((index ^ (index >> 2)) & 1)
    payload.rewind()
    initial = body(payload)
    provenance = Provenance(16)
    provenance.mark(payload)
    width, one = Count.literal(2), Count.literal(1)
    with no_decode(), provenance.installed(), patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden), patch.object(ordinary, "select", observe_select):
        output = binary.run(payload, width, one, one, one)
        expected, masks = bytearray(16), [0]*16
        for address, bit in enumerate(initial):
            first, second = divmod(address, 4)
            expected[second*4+first], masks[second*4+first] = bit, 1 << address
        require(body(output) == expected and provenance.masks(output, 16) == tuple(masks),
                "retuned binary-to-ordinary endpoint")
        require(body(payload) == initial and all(all(bit == BLANK for bit in tape.cells)
                for tape in binary.pool.tapes), "binary ownership and cleanup")
        output.clear()
    payload.clear()
    width.close()
    one.close()
    require(selected_profiles == [interface.profile()]*2, "ordinary and binary use the retuned selector")
    try:
        interface.ordinary(None, None, None, None, profile=encoded.Profile())
    except ValueError as exc:
        require(str(exc) == "one certified coupling profile", "profile override rejection")
    else:
        raise ValueError("uncertified profile override accepted")
    return {"status": "PASS_RETUNED_ORDINARY_RUNTIME", "actual_profile_fallback": fallback,
            "declared_reduced_original_columns": 256, "padded_return_columns": returns,
            "binary_columns": 16, "selector_calls": len(selected_profiles),
            "scope": "q2 reduced physical fixtures, including a declared plan; no selected GL64 payload execution."}


if __name__ == "__main__":
    try:
        print(json.dumps(run(), sort_keys=True))
    finally:
        close()
