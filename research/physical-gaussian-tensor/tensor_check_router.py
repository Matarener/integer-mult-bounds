"""Whole dense-support permutations, matching order, capped batches and reuse."""
from hashlib import sha256
from unittest.mock import patch
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from records import Tape
    from router_metadata import owned
    from session import erase_marker
    from tensor_router import FullRouter
    from tensor_fixture import literal_native
    from words import BLANK
    router = FullRouter(literal_native())
    records = []
    def clear(tape):
        tape.clear()
        erase_marker(tape)
    def packet(data):
        tape = Tape()
        for bit in data:
            tape.append(bit)
        tape.rewind()
        return tape
    def encode_pairs(mapping, width):
        return bytes((value >> bit) & 1 for old, new in mapping for value in (old, new) for bit in range(width))
    def restored():
        router.idle()
        require(router.closed and router.current is None and not router.pool.live
                and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in router.pool.tapes),
                "complete batched-router scratch restoration")
    for mapping, C, R in (((1, 2, 3, 4, 0), 1, 6),
                           ((0, 2, 3, 1, 4, 5), 2, 7),
                           ((3, 2, 1, 0), 3, 6), ((0, 1, 2), 1, 4)):
        n, p, width = len(mapping), 2, max(1, (len(mapping)-1).bit_length())
        identity = tuple(mapping) == tuple(range(n))
        entries = [] if identity else list(enumerate(mapping))
        values = [bytes((i >> bit) & 1 for bit in range(R)) for i in range(C*(1 << n))]
        expected = [None]*len(values)
        for c in range(C):
            for i in range(1 << n):
                target = sum(((i >> old) & 1) << new for old, new in enumerate(mapping))
                expected[c*(1 << n)+target] = values[c*(1 << n)+i]
        raw, destination = b"".join(values), b"".join(expected)
        descriptor_bytes = encode_pairs(entries, width)
        source, descriptor = packet(raw), packet(descriptor_bytes)
        with owned(*(Count.literal(v) for v in (n, p, len(entries), width, R, C))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            with no_decode():
                output = router.run(source, descriptor, *parameters)
            actual = packet_bytes(output)
            counts = dict(router.last_counts)
            require(actual == destination and packet_bytes(source) == raw
                    and packet_bytes(descriptor) == descriptor_bytes, "actual full-support batches implement the complete permutation")
            require(counts["involutions"] == 2 and counts["batches"] == counts["edges"]
                    and (identity or counts["batches"] >= 2), "p2 cap forces separately executed transposition batches")
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters], "router preserves borrowed parameter ports")
            restored()
            intermediate = packet(actual)
            clear(output)
            inverse = [0]*n
            for old, new in enumerate(mapping):
                inverse[new] = old
            inverse_descriptor = packet(encode_pairs([] if identity else list(enumerate(inverse)), width))
            with no_decode():
                output = router.run(intermediate, inverse_descriptor, *parameters)
            require(packet_bytes(output) == raw, "inverse full-support batches restore every original address")
            clear(output)
            clear(intermediate)
            clear(inverse_descriptor)
            restored()
            records.append({"permutation": list(mapping), "rows": C, "record_bits": R,
                            "counts": counts, "output_sha256": sha256(actual).hexdigest()})
        clear(source)
        clear(descriptor)
    controls = []
    with owned(*(Count.literal(v) for v in (3, 2, 3, 2, 4, 1))) as parameters:
        raw = bytes((i//3+i) % 2 for i in range(32))
        descriptor_bytes = encode_pairs(list(enumerate((1, 2, 0))), 2)
        def reject(call, fragment):
            try:
                with no_decode():
                    call()
            except ValueError as error:
                require(fragment in str(error), "specific full-support router rejection: " + str(error))
            else:
                raise ValueError("missing full-support router rejection")
        for label, data, pairs, fragment in (
                ("short_input", raw[:-1], descriptor_bytes, "complete"),
                ("extra_input", raw+b"\x00", descriptor_bytes, "rectangle"),
                ("short_descriptor", raw, descriptor_bytes[:-1], "descriptor"),
                ("duplicate_image", raw, encode_pairs(list(enumerate((1, 1, 0))), 2), "unique permutation")):
            source, descriptor = packet(data), packet(pairs)
            reject(lambda: router.run(source, descriptor, *parameters), fragment)
            require(packet_bytes(source) == data and packet_bytes(descriptor) == pairs
                    and router.output.read() == BLANK, "rejected full-support call restores borrowed inputs and return")
            restored()
            controls.append(label)
            clear(source)
            clear(descriptor)
        source, descriptor = packet(raw), packet(descriptor_bytes)
        original_idle = router.idle
        idle_calls = 0
        def allocate():
            nonlocal idle_calls
            original_idle()
            idle_calls += 1
            if idle_calls == 2:
                Tape()
        with patch.object(router, "idle", allocate):
            reject(lambda: router.run(source, descriptor, *parameters), "physical Tape allocation inside")
        restored()
        controls.append("sealed_allocation")
        with no_decode():
            output = router.run(source, descriptor, *parameters)
        result_bytes = packet_bytes(output)
        reject(lambda: router.run(source, descriptor, *parameters), "consume prior full-support router output")
        require(packet_bytes(output) == result_bytes and packet_bytes(source) == raw
                and packet_bytes(descriptor) == descriptor_bytes, "protected router return survives rejected reuse")
        controls.append("protected_return")
        clear(output)
        clear(source)
        clear(descriptor)
        restored()
    return {"cases": records, "controls": controls, "pool_peak": router.pool.peak,
            "scope": "complete physical dense-support routing via actual q2 literal child calls; production-prime execution and fast-branch rate retain their source limits"}
