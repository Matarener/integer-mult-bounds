"""Actual coefficient producer and complete source-box tensor reference."""
from hashlib import sha256
from tensor_sources import require


def run(opposite=False, prepared=None):
    from cardinal_counts import Count
    from check_composed import encode
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from ring_check_words import tape, word_bits
    from router_metadata import owned
    from session import erase_marker
    from tensor_catalogue import TensorPreparation
    from tensor_engine import Tensor
    from tensor_fixture import finite_chirp, literal_native, p48_setup
    from tensor_model import Cursor, full
    from tensor_router import FullRouter
    from words import BLANK
    B = 1 << 48
    values = [((48+(7*i+3) % 15-7)*(B//256), ((5*i+2) % 17-8)*(B//256)) for i in range(49)]
    require(all(4*(a*a+b*b) <= B*B for a, b in values), "complete source-box half-disk fixture")
    raw = encode(values, 50), word_bits(7, 3)*2, bytes((1,))
    payload, sources, flags = (tape(value) for value in raw)
    preparation = TensorPreparation() if prepared is None else None
    machine = Tensor(finite_chirp(), FullRouter(literal_native()))
    with owned(*(Count.literal(v) for v in (1, 3, 48, 2, 1, 80, 4, 1, 8, 1, 1))) as parameters:
        saved = [(bytes(value.tape.cells), value.tape.head) for value in parameters]
        if prepared is None:
            with no_decode():
                catalogue = preparation.run(sources, flags, *parameters)
        else:
            catalogue = tape(prepared)
        original = packet_bytes(catalogue)
        expected, expanded, middle = full(values, original, opposite)
        require(len(expected) == 49 and any(a or b for a, b in expected), "complete nonzero restored source-box reference")
        require(all(a*a+b*b <= B*B for a, b in expected), "reference restored output fits its disk boundary")
        with owned(Count.literal(1)) as (rows,):
            cursor = Cursor(original)
            for _ in range(13):
                cursor.count()
            cursor.take(7)
            cursor.count()
            changed = bytearray(original)
            require(changed[cursor.position:cursor.position+3] == bytes((1, 1, 1)), "first original-axis count locator")
            changed[cursor.position+1] = 0
            wrong_axis = tape(changed)
            try:
                with owned(Count.literal(0)) as (index,):
                    try:
                        with no_decode():
                            machine.lines.run(payload, wrong_axis, index, rows, rows)
                    except ValueError as error:
                        require("tensor profile binds its original global axis" in str(error), "changed global-axis binding rejection")
                    else:
                        raise ValueError("missing original-axis page binding")
                require(packet_bytes(wrong_axis) == bytes(changed) and machine.lines.output.read() == BLANK
                        and machine.lines.closed and not machine.lines.pool.live,
                        "failed axis binding restores the complete line owner")
            finally:
                wrong_axis.clear()
                erase_marker(wrong_axis)
            bad_values = list(values)
            bad_values[0] = (B//2+1, 0)
            bad_bytes = encode(bad_values, 50)
            bad = tape(bad_bytes)
            try:
                try:
                    with no_decode():
                        machine.run(bad, catalogue, rows, opposite=opposite)
                except ValueError as error:
                    require("complete tensor disk-grid boundary" in str(error), "whole tensor half-disk entrance rejection")
                else:
                    raise ValueError("missing complete tensor entrance rejection")
                require(packet_bytes(bad) == bad_bytes and packet_bytes(catalogue) == original
                        and machine.output.read() == BLANK and not machine.pool.live
                        and machine.current is machine.following is None,
                        "failed entrance preserves borrowed ports and releases caller scratch")
            finally:
                bad.clear()
                erase_marker(bad)
            with p48_setup() as setup, no_decode():
                output = machine.run(payload, catalogue, rows, opposite=opposite)
            try:
                actual = packet_bytes(output)
                require(actual == encode(expected, 50), "complete physical tensor equals the independent natural-coordinate staged reference")
                require(machine.last_counts == dict(natural_padding=4, gathers=4, halos=4,
                            expansion_axes=2, compression_axes=2, assembled_axes=2, chirps=1),
                        "complete physical tensor schedule with four full-support gathers")
                require(setup == {"51^(.997)": 9, "52^(.997)": 9, "1^(.002)": 18},
                        "one complete natural-order chirp with exact p48 metadata")
                require([packet_bytes(port) for port in (payload, sources, flags)] == list(raw)
                        and packet_bytes(catalogue) == original
                        and saved == [(bytes(value.tape.cells), value.tape.head) for value in parameters],
                        "complete tensor preserves source data, coefficients and encoded metadata")
                machine.idle()
                require(machine.closed and not machine.pool.live and machine.current is machine.following is None
                        and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in machine.pool.tapes),
                        "complete tensor restores fixed owned scratch and origin heads")
                try:
                    machine.run(payload, catalogue, rows, opposite=opposite)
                except ValueError as error:
                    require("consume previous complete tensor return" in str(error), "protected complete tensor return")
                else:
                    raise ValueError("missing complete tensor protected-return guard")
                require(packet_bytes(output) == actual, "protected return remains byte-identical")
                evidence = {"opposite": opposite, "inputs": 49, "middle_coordinates": 64,
                            "output_bits": len(actual), "sha256": sha256(actual).hexdigest(),
                            "catalogue_sha256": sha256(original).hexdigest(),
                            "expanded_sha256": sha256(encode(expanded, 50)).hexdigest(),
                            "middle_sha256": sha256(encode(middle, 50)).hexdigest(),
                            "nonzero_outputs": sum(bool(a or b) for a, b in expected),
                            "calls": machine.last_counts, "pool_peak": machine.pool.peak,
                            "coefficient_producer": preparation.last_counts if preparation is not None else None,
                            "coefficient_source": "fresh producer" if prepared is None else "serialized producer return",
                            "controls": ["global-axis page binding", "half-disk entrance", "positive reuse after failure", "protected return"],
                            "scope": "complete explicit p48/P80 two-axis staged composition; no production-size or Fourier-identity claim"}
            finally:
                output.clear()
                erase_marker(output)
        catalogue.clear()
        erase_marker(catalogue)
    for port in (payload, sources, flags):
        port.clear()
        erase_marker(port)
    return evidence
