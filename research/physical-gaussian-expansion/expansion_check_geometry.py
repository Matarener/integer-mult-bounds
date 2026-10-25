"""Exact global origins, signed stencils, crop indices and production metadata."""
from fractions import Fraction as Q
from math import isqrt
from expansion_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_geometry import BlockGeometry, ProductionBlock
    from expansion_records import BlockHeader
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from words import BLANK
    pool = ScratchPool(256)
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    records = []
    identities = 0
    cases = ((7, 8, 2, 1, 0, 1, 4, 32, 4),
             (7, 8, 2, 1, 1, 1, 4, 32, 4),
             (7, 8, 2, 2, 7, 2, 4, 40, 5),
             (13, 14, 2, 2, -2, 2, 8, 48, 8),
             (13, 14, 2, 2, 11, 1, 8, 48, 8),
             (3, 4, 2, 2, 2, 2, 4, 32, 3),
             (3, 4, 2, 2, 4, 1, 4, 32, 3))
    for s, t, alpha, radius, start, length, p, bits, sigma in cases:
        with owned(*(Count.literal(v) for v in (s, t, alpha, radius, abs(start), length, p, bits, sigma))) as args:
            source_length, target_length, a, b, origin, m, target_p, P, scale = args
            saved = [(bytes(value.tape.cells), value.tape.head) for value in args]
            plan = header = page = None
            for tape in pool.tapes:
                initialize_marker(tape)
            with sealed_constructors(), scope.installed():
                try:
                    with no_decode():
                        plan = BlockGeometry(source_length, target_length, a, b,
                                             Signed(origin, start < 0), m, target_p, P, scale)
                    def signed(value):
                        return (-1 if value.negative else 1)*decode(value.magnitude)
                    def rational(value):
                        return Q(signed(value.numerator), decode(value.denominator))
                    kappa = Q(s, t)
                    j0 = (kappa*start).__floor__()
                    gamma = j0-kappa*start
                    low = -radius-1
                    high = (kappa*(length-1)-gamma).__ceil__()+radius+1
                    n, nc = high-low+1, high-low+length
                    require(signed(plan.j0) == j0 and rational(plan.gamma) == gamma
                            and signed(plan.source_start) == j0+low
                            and (decode(plan.n), decode(plan.nc)) == (n, nc),
                            "exact lifted expansion source window and convolution length")
                    arrays = {}
                    for kind, count in (("A", n), ("K", nc), ("B", length)):
                        values = []
                        for index in range(count):
                            with owned(Count.literal(index)) as (position,):
                                with no_decode():
                                    value = plan.exponent(kind, position)
                                with owned(value):
                                    values.append(rational(value))
                        arrays[kind] = values
                    for index, h in enumerate(range(low, high+1)):
                        for z in range(length):
                            kernel_index = n-1+z-index
                            require(0 <= kernel_index < nc, "complete prefix crop contains every term")
                            direct = Q((j0+h-kappa*(start+z))**2, alpha*alpha)
                            require(arrays["A"][index]+arrays["K"][kernel_index]+arrays["B"][z] == direct,
                                    "exact original real Gaussian exponent after crop")
                            identities += 1
                    page = pool.acquire()
                    with no_decode():
                        BlockHeader.dump(plan, page)
                        page.rewind()
                        header = BlockHeader(page)
                        require(page.read() == BLANK, "complete expansion metadata frame")
                        header.repeat(page)
                    require(page.read() == BLANK and decode(header.extract) == bits-p-2*sigma,
                            "normalization remains before final-grid extraction")
                    records.append({"s": s, "t": t, "alpha": alpha, "radius": radius,
                                    "target": [start, length], "source": [j0+low, n],
                                    "nc": nc, "p": p, "P": bits, "sigma": sigma,
                                    "u_theta": str(Q(alpha*alpha*(t-s), s))})
                    require(saved == [(bytes(value.tape.cells), value.tape.head) for value in args],
                            "geometry preserves borrowed parameters")
                finally:
                    for value in (header, plan):
                        if value is not None:
                            value.close()
                    if page is not None:
                        page.clear()
                    pool.empty()
            for tape in pool.tapes:
                erase_marker(tape)
    require(records[-2]["source"] == [-2, 9] and records[-1]["source"] == [0, 7],
            "positive left advance with an equal source right endpoint")
    production = []
    for p, alpha in ((101, 2), (127, 3), (16384, 6)):
        with owned(Count.literal(p), Count.literal(alpha)) as args:
            for tape in pool.tapes:
                initialize_marker(tape)
            with sealed_constructors(), scope.installed():
                plan = None
                try:
                    with no_decode():
                        plan = ProductionBlock(*args)
                    root = isqrt(p)
                    root += root*root < p
                    actual = {name: decode(getattr(plan, name)) for name in ("u", "radius", "P", "sigma")}
                    require(actual == {"u": alpha*alpha, "radius": alpha*root,
                                       "P": 32768*p, "sigma": 4096*p},
                            "encoded production expansion metadata")
                    production.append({"p": p, "alpha": alpha, **actual})
                finally:
                    if plan is not None:
                        plan.close()
                    pool.empty()
            for tape in pool.tapes:
                erase_marker(tape)
    for tape in pool.tapes:
        require(tape.head == 1 and all(value == BLANK for value in tape.cells), "geometry scratch restoration")
    return {"blocks": records, "factor_identities": identities, "production": production,
            "pool_peak": pool.peak,
            "scope": "exact encoded geometry and metadata only; coefficient pages and data consumers remain separate"}
