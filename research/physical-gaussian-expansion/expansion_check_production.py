"""Encoded whole-tile production metadata without production-sized coefficients."""
from fractions import Fraction as Q
from math import isqrt
from expansion_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_tile_geometry import ProductionTile, stencil_bounds
    from ring_check_words import decode
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from words import BLANK
    pool = ScratchPool(256)
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    signed = lambda v: (-1 if v.negative else 1)*decode(v.magnitude)
    p, alpha, d = 4800, 4, 300
    L = 1 << ((p**8-1).bit_length())
    t = 16*L
    s = t-(1 << 92)-1
    halo = 4096*p**3
    records, controls = [], []
    cases = [("first", s, t, d, alpha, p, 0, None),
             ("middle", s, t, d, alpha, p, 1, None),
             ("rounding_transition", s, t, d, alpha, p, 8, None),
             ("last", s, t, d, alpha, p, 15, None),
             ("target_precision", s, t, d, alpha, 100, "production expansion precision"),
             ("alpha_one", s, t, d, 1, p, "integer alpha"),
             ("alpha_square", s, t, d, 70, p, "alpha squared"),
             ("concentration", s, t, d, 2, p, "logarithmic Gaussian concentration"),
             ("similarity", s, t, 301, alpha, p, "similarity guard"),
             ("cell_separation", s, t, 290, alpha, p, "cell/band separation"),
             ("nondyadic_target", s, t-1, d, alpha, p, "dyadic target"),
             ("incomplete_tile", (1 << 64)-(1 << 54)-1, 1 << 64, d, alpha, p, "complete target tile"),
             ("tile_out_of_range", s, t, d, alpha, p, "complete target tile"),
             ("global_period", 2*L-(1 << 89)-1, 2*L, d, alpha, p, "global period")]
    for case in cases:
        if len(case) == 8:
            name, S, T, D, a, target_p, index, rejection = case
        else:
            name, S, T, D, a, target_p, rejection = case
            index = 16 if name == "tile_out_of_range" else 0
        with owned(*(Count.literal(v) for v in (S, T, D, a, target_p, index))) as parameters:
            saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
            for tape in pool.tapes:
                initialize_marker(tape)
            plan = None
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode():
                            plan = ProductionTile(*parameters)
                        require(rejection is None, "missing production domain rejection: " + name)
                        root = isqrt(p)+(isqrt(p)**2 < p)
                        expected = {"p": p, "alpha": alpha, "u": alpha*alpha, "d": d,
                                    "radius": alpha*root, "P": 32768*p, "sigma": 4096*p,
                                    "L": L, "halo": halo, "target_length": L, "input_capacity": L,
                                    "blocks": (L+alpha*root-1)//(alpha*root)}
                        actual = {key: decode(getattr(plan, key)) for key in expected}
                        require(actual == expected and signed(plan.target_start) == index*L,
                                "encoded production expansion tile parameters")
                        # q_j=floor(t*j/s+1/2) lies in [a,b) precisely on
                        # [ceil(s*(2a-1)/(2t)), ceil(s*(2b-1)/(2t))).
                        left = -((-s*(2*(index*L-halo)-1))//(2*t))
                        right = -((-s*(2*((index+1)*L+halo)-1))//(2*t))
                        require(signed(plan.source_start) == left and decode(plan.source_count) == right-left,
                                "same original global compression window at both period seams")
                        with no_decode():
                            low, high = stencil_bounds(plan.s, plan.t, plan.radius,
                                                       plan.target_start, plan.target_length)
                        with owned(low, high):
                            require(left <= signed(low) <= signed(high) <= right,
                                    "production halo contains complete expansion stencils")
                        require(decode(plan.inverse_plan.w) == 72 and right-left <= L
                                and L % (alpha*root) == 144,
                                "paired band, source padding and clipped last production block")
                        records.append({"tile_index": index, **actual, "source_start": left,
                                        "source_count": right-left, "source_padding": L-(right-left),
                                        "w": decode(plan.inverse_plan.w), "u_theta": str(Q(alpha*alpha*(t-s), s))})
                    except ValueError as error:
                        if rejection is None:
                            raise
                        require(rejection in str(error), "specific production rejection: " + name + ": " + str(error))
                        controls.append(name)
                    finally:
                        if plan is not None:
                            plan.close()
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters],
                    "production metadata preserves borrowed parameters")
            require(all(tape.head == 1 and all(v == BLANK for v in tape.cells) for tape in pool.tapes),
                    "production metadata restores owned tapes after success and rejection")
    return {"tiles": records, "controls": controls, "pool_peak": pool.peak,
            "scope": "encoded production metadata only; no production-sized coefficient page or payload execution"}
