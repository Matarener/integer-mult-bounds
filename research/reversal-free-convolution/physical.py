"""Execute the changed fixed-tape caller on a genuinely nonidentity B."""

from hashlib import sha256
from reference import original, require


def encode(values, width):
    return bytes((value >> bit) & 1 for pair in values for value in pair for bit in range(width))


def body(tape):
    from words import BLANK
    tape.rewind()
    result = bytearray()
    for _ in range(len(tape.cells)+1):
        value = tape.read()
        if value == BLANK:
            tape.rewind()
            return bytes(result)
        require(value in (0, 1), "binary returned payload")
        result.append(value)
        tape.step(1)
    raise ValueError("terminated payload")


def make_tape(bits):
    from records import Tape
    result = Tape()
    for bit in bits:
        result.append(bit)
    result.rewind()
    return result


def check_closed(owner):
    from words import BLANK
    owner.idle()
    require(owner.closed and not owner.pool.live and owner.a is owner.b is owner.current is None,
            "closed changed caller with no live payload")
    for item in owner.pool.tapes:
        require(item.head == 1 and all(value == BLANK for value in item.cells),
                "erased changed-caller scratch at origin")
    require(owner.fourier.closed and not owner.fourier.pool.live
            and owner.fourier.current is None, "closed changed Fourier owner")


def read_width(port):
    from words import RIGHT
    port.rewind()
    value = 0
    try:
        for bit in range(32):
            if port.read() == RIGHT:
                return value
            require(port.read() in (0, 1), "binary returned width")
            value |= port.read() << bit
            port.step(1)
        raise ValueError("bounded returned width")
    finally:
        port.rewind()


def run():
    from adapter import convolution
    from cardinal_counts import Count
    from check_composed import fixture
    from check_support import no_decode
    from session import erase_marker
    from words import BLANK
    # Four addresses on one length-four axis. B exchanges records 1 and 2.
    ell, p, rows, lengths = 2, 3, 1, (2,)
    from checks import character_packet
    first = character_packet()
    second = [(0, a) for a, _ in first]
    require(all(a*a+b*b <= 1 << (2*p) for a, b in first+second), "disk-grid fixture")
    expected_values = [(a << 2, b << 2) for a, b in original(first, second, lengths, ell, p, rows)]
    expected = encode(expected_values, p+4)
    require(any(a or b for a, b in expected_values), "nonzero complete convolution fixture")
    originals = encode(first, p+2), encode(second, p+2), bytes((1,))
    inputs = tuple(make_tape(bits) for bits in originals)
    counts = tuple(Count.literal(value) for value in (1, ell, p, rows))
    saved = tuple((bytes(value.tape.cells), value.tape.head) for value in counts)
    owner = convolution(fixture()[0])
    try:
        with no_decode():
            output, width_port = owner.run(*inputs, *counts)
        actual = body(output)
        require(actual == expected, "changed physical caller equals original rounded convolution")
        require(tuple(body(value) for value in inputs) == originals, "unchanged borrowed data and flags")
        require(saved == tuple((bytes(value.tape.cells), value.tape.head) for value in counts),
                "unchanged borrowed encoded metadata")
        width = read_width(width_port)
        require(width == p+4, "original widened width")
        check_closed(owner)
        require(owner.calls == dict(forward=2, product=1, opposite=1, scale=1), "full original composition")
        require(owner.fourier.calls == dict(roots=6, diagonals=3, reversals=0, lifts=3, truncations=3),
                "actual three reversals omitted with all arithmetic stages retained")
        output.clear()
        erase_marker(output)
        try:
            with no_decode():
                owner.run(*inputs, *counts)
        except ValueError as error:
            require("consume both" in str(error), "protected width port still enforced")
        else:
            raise ValueError("unconsumed width port accepted")
        width_port.clear()
        erase_marker(width_port)
        require(output.read() == width_port.read() == BLANK, "consumed output ports")
        return {"gaussians": 16, "address_bits": 2, "ell": ell, "p": p, "rows": rows,
                "output_width": width, "output_bits": len(actual), "sha256": sha256(actual).hexdigest(),
                "fourier_calls": dict(owner.fourier.calls), "consumer_calls": dict(owner.calls),
                "removed_sparse_router_calls": 3, "protected_width_control": True}
    finally:
        for count in counts:
            count.close()
