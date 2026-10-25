"""Literal Count-tape profile checks against separate integer specifications."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interface
from predecessor import close, require, runtime


def run():
    _, encoded, _ = runtime()
    from cardinal_counts import Count
    from check_support import no_decode
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from words import RIGHT

    def decode(count):
        # Observer only: this value never supplies an operand to the runtime.
        tape = count.tape if hasattr(count.tape, "cells") else count.tape.physical
        digits = []
        for bit in tape.cells[1:]:
            if bit == RIGHT:
                break
            digits.append(bit)
        return sum(bit << index for index, bit in enumerate(digits))
    actual = interface.profile()
    require((actual.numerator, actual.denominator, actual.dimension, actual.child_rank, actual.row_factor)
            == (1, 577, 64, 42, 269241600), "actual selected profile")
    pool = ScratchPool(64)
    roots = []
    for value in (1, 2, 64, 311311, 2**20):
        original = Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            width = encoded.atom_width(original, actual.numerator, actual.denominator)
            observed = decode(width)
            require((observed-1)**577 < value <= observed**577, "literal reciprocal root")
            width.close()
            pool.empty()
        original.close()
        roots.append([value, observed])
    boundaries = []
    for delta in (-1, 0, 1):
        value = 2**577 + delta
        two, cap = Count.literal(2), Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            power = encoded.fixed_power(two, actual.denominator, cap)
            observed = decode(power)
            require(observed == min(2**577, value), "large exact compiled-power boundary")
            require((encoded.compare(power, cap) >= 0) == (delta <= 0), "ceiling-root predicate seam")
            power.close()
            pool.empty()
        two.close()
        cap.close()
        boundaries.append(delta)
    plans = []
    reduced = encoded.Profile(numerator=1, denominator=577, dimension=2, child_rank=1, row_factor=6)
    for q, value in ((2, 1), (2, 2), (2, 64), (2, 512), (3, 512)):
        original = Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            plan = encoded.select(original, q, reduced)
            observed = {key: item if key == "fits" else decode(item) for key, item in plan.items()}
            width = observed["width"]
            cursor, depth = value, 0
            while cursor >= 2:
                cursor //= 2
                depth += 1
            order = (q*q-1)*(q*q-q)
            stock = (6*order*q**(4*(width-1)))**depth
            rows, borrowed = 1, 0
            while rows < stock:
                rows *= q
                borrowed += 1
            require((observed["stock"], observed["depth"], observed["rows"], observed["borrowed"])
                    == (stock, depth, rows, borrowed), "exact original-width stock and borrowing")
            if 2*borrowed < value:
                body, remainder = divmod(value-borrowed, width)
                require((observed["body"], observed["remainder"], observed["fits"])
                        == (body, remainder, body >= 2), "actual fit and body split")
            else:
                require(not observed["fits"], "strict fit rejection")
            for key, item in plan.items():
                if key != "fits":
                    item.close()
            pool.empty()
        original.close()
        plans.append({"q": q, "original": value, **observed})
    return {"status": "PASS_RETUNED_ENCODED_PROFILE", "roots": roots,
            "large_power_boundary_offsets": boundaries, "reduced_plans": plans,
            "peak_setup_leases": pool.peak,
            "scope": "Actual selected root predicate; reduced stock geometries. No selected large-prime payload execution."}


if __name__ == "__main__":
    try:
        print(json.dumps(run(), sort_keys=True))
    finally:
        close()
