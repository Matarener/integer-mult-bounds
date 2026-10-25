"""Canonical full coarse-field and inner-field order across complete tensors."""
from hashlib import sha256
from itertools import product
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from records import Tape
    from router_metadata import owned
    from session import erase_marker
    from tensor_fixture import literal_native
    from tensor_gather import Gather
    from tensor_router import FullRouter
    from words import BLANK
    gather = Gather(FullRouter(literal_native()))
    records = []
    def clear(tape):
        tape.clear()
        erase_marker(tape)
    def packet(data):
        result = Tape()
        for bit in data:
            result.append(bit)
        result.rewind()
        return result
    def restored():
        gather.idle()
        require(gather.closed and not gather.pool.live
                and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in gather.pool.tapes),
                "complete canonical gather restoration")
    for flags_raw, ell, inner, C, R in (((1,), 3, 1, 2, 7), ((0,), 3, 1, 1, 6),
                                        ((1, 0), 3, 1, 1, 9)):
        widths = [ell if flag else ell-1 for flag in flags_raw]+[ell]
        lengths = [1 << width for width in widths]
        volume = 1 << sum(widths)
        values = [bytes((i >> bit) & 1 for bit in range(R)) for i in range(C*volume)]
        expected = [None]*(C*volume)
        for c in range(C):
            for rank, address in enumerate(product(*(range(length) for length in lengths))):
                coarse_rank = inner_rank = 0
                for value, width in zip(address, widths):
                    coarse_rank = (coarse_rank << (width-inner))+(value >> inner)
                    inner_rank = (inner_rank << inner)+(value & ((1 << inner)-1))
                destination = (coarse_rank << (len(widths)*inner))+inner_rank
                expected[c*volume+destination] = values[c*volume+rank]
        raw, desired = b"".join(values), b"".join(expected)
        source, flags = packet(raw), packet(bytes(flags_raw))
        with owned(*(Count.literal(v) for v in (len(flags_raw), ell, inner, 2, R, C))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            with no_decode():
                output = gather.run(source, flags, *parameters)
            actual = packet_bytes(output)
            require(actual == desired and actual != raw, "full canonical gather preserves coarse-axis order and inner-axis order")
            counts = dict(gather.last_counts)
            restored()
            intermediate = packet(actual)
            clear(output)
            with no_decode():
                output = gather.run(intermediate, flags, *parameters, inverse=True)
            require(packet_bytes(output) == raw and packet_bytes(source) == raw
                    and packet_bytes(flags) == bytes(flags_raw), "inverse gather restores complete natural tensor and borrowed ports")
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters], "gather preserves encoded global parameters")
            restored()
            clear(output)
            clear(intermediate)
            records.append({"flags": list(flags_raw), "ell": ell, "inner_bits": inner,
                            "rows": C, "record_bits": R, "counts": counts,
                            "output_sha256": sha256(actual).hexdigest()})
        clear(source)
        clear(flags)
    controls = []
    with owned(*(Count.literal(v) for v in (1, 3, 1, 2, 1, 1))) as parameters:
        source = packet(bytes(64))
        for data, message in ((b"", "target-axis flags"), (bytes([1, 0]), "flags extent")):
            flags = packet(data)
            try:
                with no_decode():
                    gather.run(source, flags, *parameters)
            except ValueError as error:
                require(message in str(error), "specific canonical gather flag rejection")
            else:
                raise ValueError("missing canonical gather flag rejection")
            require(packet_bytes(source) == bytes(64) and packet_bytes(flags) == data
                    and gather.output.read() == BLANK, "failed gather restores borrowed ports and clears output")
            restored()
            controls.append(message)
            clear(flags)
        flags = packet(bytes([1]))
        with no_decode():
            output = gather.run(source, flags, *parameters)
        require(packet_bytes(output) == bytes(64), "positive complete gather reuse after rejection")
        clear(output)
        clear(flags)
        clear(source)
        restored()
    return {"cases": records, "controls": controls, "pool_peak": gather.pool.peak,
            "scope": "actual complete canonical gathers using q2 literal batches; no numerical line-map substitution"}
