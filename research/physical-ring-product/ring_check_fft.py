"""Physical butterfly witnesses for exact numerators and final-only rounding."""

from fractions import Fraction
from types import SimpleNamespace
from ring_sources import require


def call(mode, numbers):
    from cardinal_counts import Count
    from check_support import no_decode
    from ring_check_words import body, decode
    from ring_engine import RingProduct
    from ring_words import Signed, add, difference, read_signed, truncate, write_signed
    from router_metadata import owned
    from session import erase_marker, sealed_constructors
    owner = RingProduct()
    Q = 16
    counts = [Count.literal(v) for v in (Q, Q+3, Q+1, Q+2)]
    plan = SimpleNamespace(Q=counts[0], word_width=counts[1], half_shift=counts[2])
    inputs = tuple(Signed(Count.literal(abs(value)), value < 0) for value in numbers)
    saved = tuple((bytes(v.magnitude.tape.cells), v.magnitude.tape.head) for v in inputs)
    owner.rearm()
    try:
        with no_decode(), sealed_constructors(), owner.scope.installed():
            if mode == "dif":
                result = owner.arithmetic.dif(*inputs, plan)
            elif mode == "dit":
                result = owner.arithmetic.dit(*inputs, plan)
            else:
                require(mode == "premature_dif", "declared physical butterfly mutant")
                a, b, c, d, u, v = inputs
                with owned(add(a, c), add(b, d), difference(a, c), difference(b, d),
                           Count.literal(1)) as (sr, si, dr, di, one):
                    with owned(truncate(dr, one), truncate(di, one)) as (pr, pi):
                        with owned(*owner.arithmetic.complex_product(pr, pi, u, v, plan.word_width)) as (rr, ri):
                            result = (truncate(sr, one), truncate(si, one),
                                      truncate(rr, plan.Q), truncate(ri, plan.Q))
            try:
                for value in result:
                    write_signed(value, owner.output, counts[3])
            finally:
                for value in result:
                    value.close()
            owner.pool.empty()
        for item in owner.pool.tapes:
            erase_marker(item)
        owner.output.rewind()
        owner.closed = True
        result = []
        for _ in range(4):
            value = read_signed(owner.output, counts[3])
            try:
                result.append((-1 if value.negative else 1)*decode(value.magnitude))
            finally:
                value.close()
        require(saved == tuple((bytes(v.magnitude.tape.cells), v.magnitude.tape.head) for v in inputs),
                "physical butterfly preserves borrowed operands")
        owner.output.clear()
        erase_marker(owner.output)
        owner.idle()
        return result
    finally:
        for value in (*inputs, *counts):
            value.close()


def run():
    B = 1 << 16
    cases = [
        ("dif", (3, 3, 0, 0, 46340, -46340)),
        ("dit", (8, 0, -3, -3, 46340, -46340)),
        ("dif", (B//3, -B//4, B//5, B//7, 46340, -46340)),
        ("dit", (-B//3, B//4, B//5, -B//7, 0, B)),
    ]
    receipts = []
    for mode, values in cases:
        a, b, c, d, u, v = values
        if mode == "dif":
            expected = [int(Fraction(a+c, 2)), int(Fraction(b+d, 2)),
                        int(Fraction(u*(a-c)-v*(b-d), 2*B)),
                        int(Fraction(u*(b-d)+v*(a-c), 2*B))]
        else:
            real, imaginary = u*c-v*d, u*d+v*c
            expected = [int(Fraction(B*a+real, 2*B)), int(Fraction(B*b+imaginary, 2*B)),
                        int(Fraction(B*a-real, 2*B)), int(Fraction(B*b-imaginary, 2*B))]
        actual = call(mode, values)
        require(actual == expected, "exact physical butterfly numerator and rounding")
        receipts.append({"mode": mode, "output": actual})
    mutant = call("premature_dif", cases[0][1])
    require(receipts[0]["output"] == [1, 1, 2, 0] and mutant == [1, 1, 1, 0],
            "physical premature butterfly truncation witness")
    return {"correct": receipts, "premature_dif": mutant}
