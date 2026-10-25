"""Complete encoded shape, scalar normalization and common production policy."""
from math import isqrt
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from records import Tape
    from ring_check_words import decode, word_bits
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from tensor_plan import Policy, TensorHeader, TensorPlan
    from words import BLANK
    pool, evidence, policies = ScratchPool(256), [], []
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    def packet(data):
        tape = Tape()
        for bit in data:
            tape.append(bit)
        tape.rewind()
        return tape
    def restored():
        require(not pool.live and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in pool.tapes),
                "tensor metadata restores all owned tapes")
    for flags_raw, ell, p, P, source_values in (((1,), 3, 48, 80, (7, 7)),
                                               ((0,), 4, 48, 80, (7, 15)),
                                               ((1, 0), 4, 80, 112, (15, 7, 15))):
        raw_sources = b"".join(word_bits(v, ell) for v in source_values)
        sources, flags = packet(raw_sources), packet(bytes(flags_raw))
        with owned(*(Count.literal(v) for v in (len(flags_raw), ell, p, 2, 1, P, 4, 1, 8, 1, 1))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            plan = header = page = None
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode():
                            plan = TensorPlan(sources, flags, *parameters, pool.acquire)
                        D = len(source_values)
                        widths = [ell if bit else ell-1 for bit in flags_raw]+[ell]
                        S = 1
                        for value in source_values:
                            S *= value
                        j = (32*p-1).bit_length()
                        expected = {"dimensions": D, "d": D+1, "u": 4, "L": 2,
                                    "target_halo": 4, "j": j, "gamma": D*(8+j+1),
                                    "component_bits": p+2, "record_bits": 2*(p+2),
                                    "source_product": S, "target_product": 1 << sum(widths),
                                    "address_bits": sum(widths), "outer_bits": sum(widths)-ell,
                                    "inner_address_bits": D, "coarse_address_bits": sum(widths)-D,
                                    "coarse_product": 1 << (sum(widths)-D)}
                        actual = {name: decode(getattr(plan, name)) for name in expected}
                        require(actual == expected, "complete encoded tensor shape and actual-axis normalization")
                        for i, (s, width) in enumerate(zip(source_values, widths)):
                            with owned(Count.literal(i)) as (index,):
                                with no_decode():
                                    row = plan.axis(index)
                                with owned(row):
                                    require([decode(getattr(row, name)) for name in row.names]
                                            == [s, 1 << width, width, 1 << (width-1)],
                                            "complete original global axis row")
                        page = pool.acquire()
                        with no_decode():
                            TensorHeader.dump(plan, page)
                            page.rewind()
                            header = TensorHeader(page)
                        require(page.read() == BLANK and decode(header.mode) == 0,
                                "explicit tensor catalogue policy framing")
                        require(packet_bytes(plan.sources) == raw_sources
                                and packet_bytes(plan.flags) == bytes(flags_raw), "chirp ports keep original global order")
                        evidence.append({"flags": list(flags_raw), "ell": ell, "p": p, "P": P,
                                         "sources": list(source_values), **actual})
                    finally:
                        for value in (header, plan):
                            if value is not None:
                                value.close()
                        if page is not None:
                            page.clear()
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters]
                    and packet_bytes(sources) == raw_sources and packet_bytes(flags) == bytes(flags_raw),
                    "complete tensor plan preserves borrowed metadata ports")
            restored()
        for tape in (sources, flags):
            tape.clear()
            erase_marker(tape)
    for p, alpha in ((101, 2), (4800, 4), (16384, 6)):
        with owned(Count.literal(p), Count.literal(alpha)) as parameters:
            for tape in pool.tapes:
                initialize_marker(tape)
            plan = None
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode():
                            plan = Policy(*parameters)
                        root = isqrt(p)+(isqrt(p)**2 < p)
                        inner = (p**8-1).bit_length()
                        target = (16*p+alpha*alpha-1)//(alpha*alpha)
                        w = isqrt(target)+(isqrt(target)**2 < target)+2
                        expected = {"P": 32768*p, "sigma": 4096*p, "radius": alpha*root,
                                    "halo": 4096*p**3, "inner_bits": inner,
                                    "expansion_capacity": 1 << inner, "w": w}
                        require({name: decode(getattr(plan, name)) for name in expected} == expected,
                                "encoded common production policy without coefficient allocation")
                        policies.append({"p": p, "alpha": alpha, **expected})
                    finally:
                        if plan is not None:
                            plan.close()
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            restored()
    return {"shapes": evidence, "production_policies": policies, "pool_peak": pool.peak,
            "scope": "complete explicit shape and common production policy metadata; no complete production tensor or coefficients executed"}
