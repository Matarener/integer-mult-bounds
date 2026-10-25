"""Encoded digit-pair roots and complete inward small-order phase tables."""
from hashlib import sha256
from math import isqrt
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from ring_check_words import decode
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from tensor_twiddles import SmallPhaseBasis, SmallTwiddles, integer_sqrt
    from words import BLANK
    pool = ScratchPool(64)
    scope = OuterScope(pool)
    for item in pool.tapes:
        erase_marker(item)
    values = set(range(512))
    for width in (8, 17, 48, 54, 113, 257, 512):
        root = (1 << width)-3
        values.update((root*root-1, root*root, root*root+1, (root+1)**2-1))
    for number in sorted(values):
        with owned(Count.literal(number)) as (incoming,):
            saved = bytes(incoming.tape.cells)
            for item in pool.tapes:
                initialize_marker(item)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode():
                            result = integer_sqrt(incoming)
                        with owned(result):
                            require(decode(result) == isqrt(number), "independent host square-root oracle across square boundaries")
                    finally:
                        pool.empty()
            finally:
                for item in pool.tapes:
                    erase_marker(item)
            require(saved == bytes(incoming.tape.cells) and incoming.tape.head == 1,
                    "digit-pair square root preserves its borrowed operand")
    require(not pool.live and all(item.head == 1 and all(v == BLANK for v in item.cells) for item in pool.tapes),
            "digit-pair square root restores fixed owned tapes")
    tables, phase, evidence = SmallTwiddles(), SmallPhaseBasis(), []
    def read_packet(raw, width):
        result = []
        for start in range(0, len(raw), width):
            bits = raw[start:start+width]
            value = sum(bit << i for i, bit in enumerate(bits))
            result.append(value-(1 << width) if bits[-1] else value)
        return list(zip(result[::2], result[1::2]))
    for p in (16, 48, 54, 113):
        B = 1 << p
        # Bound each radical through a finer rational enclosure, then prove
        # that its interval lies within one target-grid integer bin.
        F = 1 << (4*p)
        sqrt_two = isqrt(2*F*F)
        lower = (2*F+sqrt_two)*B*B
        upper = (2*F+sqrt_two+1)*B*B
        c = isqrt(lower//(4*F))
        require(c*c*4*F <= lower and upper < (c+1)**2*4*F, "cos(pi/8) floor interval")
        lower = (2*F-sqrt_two-1)*B*B
        upper = (2*F-sqrt_two)*B*B
        s = isqrt(lower//(4*F))
        require(s*s*4*F <= lower and upper < (s+1)**2*4*F, "sin(pi/8) floor interval")
        h = isqrt(B*B//2)
        roots = ((B, 0), (c, s), (h, h), (s, c), (0, B), (-s, c), (-h, h), (-c, s))
        for order in (2, 4, 8, 16):
            for opposite in (False, True):
                with owned(Count.literal(p), Count.literal(order)) as parameters:
                    with no_decode():
                        output = tables.run(*parameters, opposite=opposite)
                    try:
                        raw = packet_bytes(output)
                        expected = [(roots[j*(16//order)][0], roots[j*(16//order)][1]*(1 if opposite else -1))
                                    for j in range(order//2)]
                        require(read_packet(raw, p+2) == expected, "complete small-order signed table against radical enclosures")
                        require(all(a*a+b*b <= B*B for a, b in expected), "inward complex disk at every small-order phase")
                        evidence.append({"p": p, "order": order, "opposite": opposite, "sha256": sha256(raw).hexdigest()})
                    finally:
                        output.clear()
                        erase_marker(output)
        with owned(Count.literal(p), Count.literal(3)) as parameters:
            with no_decode():
                output = phase.run(*parameters)
            try:
                require(read_packet(packet_bytes(output), p+2) == [roots[1], roots[2], roots[4], (-B, 0)],
                        "actual positive phase basis including its exact final minus one")
            finally:
                output.clear()
                erase_marker(output)
    for owner in (tables, phase):
        require(owner.closed and not owner.pool.live
                and all(item.head == 1 and all(v == BLANK for v in item.cells) for item in owner.pool.tapes),
                "small-order source producer restores fixed owned tapes")
    return {"roots": len(values), "root_pool_peak": pool.peak, "tables": evidence,
            "phase_bases": 4, "scope": "exact inward physical small-order radicals; no larger-order producer change"}
