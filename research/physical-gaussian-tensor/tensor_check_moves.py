"""Complete mixed-radix ordering, inverse, one-field padding and ownership."""
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
    from tensor_moves import FieldMove
    from words import BLANK
    mover = FieldMove()
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
    def restored():
        mover.idle()
        require(mover.closed and not mover.pool.live
                and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in mover.pool.tapes),
                "complete mixed-radix scratch restoration")
    for C, A, q, R in ((2, 3, 5, 7), (3, 5, 3, 11), (2, 1, 8, 3),
                        (1, 7, 1, 5), (1, 2, 6, 1)):
        values = [bytes(((17*i+3) >> (bit % 7)) & 1 for bit in range(R)) for i in range(C*A*q)]
        raw = b"".join(values)
        expected = b"".join(values[(c*A+a)*q+j] for c in range(C) for j in range(q) for a in range(A))
        source = packet(raw)
        with owned(*(Count.literal(v) for v in (C, A, q, R))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            with no_decode():
                forward = mover.run(source, *parameters)
            actual = packet_bytes(forward)
            forward_counts = dict(mover.last_counts)
            require(actual == expected and packet_bytes(source) == raw,
                    "complete arbitrary-spectator field move preserves significance and input")
            restored()
            intermediate = packet(actual)
            clear(forward)
            with no_decode():
                backward = mover.run(intermediate, *parameters, right=True)
            require(packet_bytes(backward) == raw and packet_bytes(intermediate) == expected,
                    "complete mixed-radix inverse restores original tensor order")
            bits = (q-1).bit_length()
            require(forward_counts == dict(splits=bits, interleaves=0, prefixes=C*((1 << bits)-1),
                                           complete_blocks=2*A*C*((1 << bits)-1))
                    and mover.last_counts == dict(splits=0, interleaves=bits, prefixes=C*((1 << bits)-1),
                                                  complete_blocks=2*A*C*((1 << bits)-1)),
                    "whole scan invoice includes complete prefixes and both buffers")
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters],
                    "mixed-radix calls preserve borrowed parameter values and heads")
            restored()
            records.append({"C": C, "A": A, "q": q, "R": R, "forward_counts": forward_counts,
                            "output_sha256": sha256(actual).hexdigest()})
            clear(backward)
            clear(intermediate)
        clear(source)
    controls = []
    with owned(*(Count.literal(v) for v in (1, 3, 5, 2))) as parameters:
        raw = bytes((i//3+i) % 2 for i in range(30))
        def reject(call, fragment):
            try:
                with no_decode():
                    call()
            except ValueError as error:
                require(fragment in str(error), "specific mixed-radix failure: " + str(error))
            else:
                raise ValueError("missing mixed-radix failure")
        for label, data in (("short", raw[:-1]), ("extra", raw+b"\x00")):
            source = packet(data)
            reject(lambda: mover.run(source, *parameters), "complete")
            require(packet_bytes(source) == data and mover.output.read() == BLANK,
                    "failed mixed-radix call preserves malformed input and clears return")
            restored()
            controls.append(label)
            clear(source)
        source = packet(raw)
        def allocate(*args, **kwargs):
            Tape()
        with patch.object(mover, "stage", allocate):
            reject(lambda: mover.run(source, *parameters), "physical Tape allocation inside")
        restored()
        controls.append("sealed_allocation")
        with no_decode():
            result = mover.run(source, *parameters)
        result_bytes = packet_bytes(result)
        reject(lambda: mover.run(source, *parameters), "consume prior mixed-radix output")
        require(packet_bytes(result) == result_bytes and packet_bytes(source) == raw,
                "protected mixed-radix return and borrowed input survive rejected reuse")
        controls.append("protected_return")
        clear(result)
        clear(source)
        restored()
    return {"cases": records, "controls": controls, "pool_peak": mover.pool.peak,
            "scope": "actual complete short-field moves; full Gaussian tensor composition remains separate"}
