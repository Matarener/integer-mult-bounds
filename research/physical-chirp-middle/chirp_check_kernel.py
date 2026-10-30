"""Complete numerical chirp against exact eighth-root integer formulas."""
from hashlib import sha256
from math import isqrt
from chirp_sources import require


def run(owner=None):
    from cardinal_counts import Count
    from chirp_kernel import ChirpKernel
    from check_composed import encode
    from check_support import no_decode
    from ring_check_words import body, tape, word_bits
    from session import erase_marker
    from words import BLANK
    p, ell = 16, 2
    B, diagonal = 1 << p, isqrt(1 << (2*p-1))
    roots = [(B, 0), (diagonal, diagonal), (0, B), (-diagonal, diagonal),
             (-B, 0), (-diagonal, -diagonal), (0, -B), (diagonal, -diagonal)]
    exponents = [(-2*j*j-3*k*k) % 8 for j in range(2) for k in range(4)]
    expected = encode([roots[e] for e in exponents], p+2)
    raw_sources, raw_flags = word_bits(1, ell)+word_bits(3, ell), bytes([0])
    sources, flags = tape(raw_sources), tape(raw_flags)
    counts = tuple(Count.literal(x) for x in (1, ell, p, 1))
    machine = ChirpKernel() if owner is None else owner
    output = None
    try:
        with no_decode():
            output = machine.run(sources, flags, *counts)
        actual = body(output)
        require(actual == expected, "full numerical chirp equals exact eighth-root oracle")
        require(body(sources) == raw_sources and body(flags) == raw_flags, "borrowed chirp descriptors")
        require(machine.closed and not machine.pool.live, "closed numerical chirp owner")
        machine.idle()
        require(all(t.head == 1 and all(b == BLANK for b in t.cells)
                    for t in (*machine.pool.tapes, *machine.odometer.canonical)),
                "chirp scratch and odometer restoration")
        output.clear()
        erase_marker(output)
        return {"p": p, "ell": ell, "gaussians": len(exponents), "exponents": exponents,
                "sha256": sha256(actual).hexdigest(), "axis_visits": machine.odometer.visits,
                "wraps": machine.odometer.wraps, "word_products": machine.arithmetic.products,
                "pool_peak": machine.pool.peak}
    finally:
        if output is not None and output.read() != BLANK:
            output.clear()
            erase_marker(output)
        for value in counts:
            value.close()
