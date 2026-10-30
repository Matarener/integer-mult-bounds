"""The complete physical middle map against staged and dense exact models."""

from fractions import Fraction
from hashlib import sha256
from math import isqrt
from chirp_sources import require


def truncate(value, divisor):
    return (abs(value)//divisor)*(-1 if value < 0 else 1)


def multiply(left, right, p):
    a, b = left
    c, d = right
    return truncate(a*c-b*d, 1 << p), truncate(a*d+b*c, 1 << p)


def conjugate(pair):
    return pair[0], -pair[1]


def models(values, p):
    from check_fourier import dense
    from ring_check_product import oracle
    B, v = 1 << p, isqrt(1 << (2*p-1))
    roots = [(B, 0), (v, v), (0, B), (-v, v), (-B, 0), (-v, -v), (0, -B), (v, -v)]
    exponents = [(-2*j*j-3*k*k) % 8 for j in range(2) for k in range(4)]
    kernel = [roots[e] for e in exponents]
    x0 = [multiply(conjugate(a), x, p) for a, x in zip(kernel, values)]
    left = [multiply(roots[i % 4], a, p) for i, a in enumerate(kernel)]
    right = [multiply(roots[i % 4], a, p) for i, a in enumerate(x0)]
    ff, fg = dense(left, (0,), 2, 1, False), dense(right, (0,), 2, 1, False)
    product = oracle(ff, fg, 1, p, 2, 1)
    opposite = dense(product, (0,), 2, 1, True)
    scaled = [(2*a, 2*b) for a, b in opposite]
    cyclic = [multiply(conjugate(roots[i % 4]), a, p) for i, a in enumerate(scaled)]
    expected = [multiply(conjugate(a), y, p) for a, y in zip(kernel, cyclic)]
    ideal = []
    for j in range(2):
        for k in range(4):
            real = imaginary = 0
            for u in range(2):
                for v in range(4):
                    a, b = values[4*u+v]
                    phase = (2*j*u+3*k*v) % 4
                    c, d = ((a, b), (-b, a), (-a, -b), (b, -a))[phase]
                    real += c
                    imaginary += d
            ideal.append((Fraction(real, 8), Fraction(imaginary, 8)))
    return expected, ideal


def run():
    from cardinal_counts import Count
    from check_composed import encode, fixture
    from check_support import no_decode
    from chirp_engine import Chirp
    from chirp_fixture import compiled_setup
    from convolution_engine import Convolution
    from cyclic_engine import Cyclic
    from fourier_engine import Fourier
    from ring_check_words import body, tape, word_bits
    from session import erase_marker
    from words import BLANK
    p, ell = 16, 2
    values = [(39321, 0), (-16381, 8193), (12001, -3001), (9007, 15013),
              (-7001, -21003), (20011, 19), (-10009, 17), (1001, -30001)]
    require(all(Fraction(a*a+b*b, 1 << (2*p)) <= Fraction(9, 25) for a, b in values),
            "complete middle-map input norm at most .6")
    expected, ideal = models(values, p)
    errors = [(Fraction(a)-c)**2+(Fraction(b)-d)**2
              for (a, b), (c, d) in zip(expected, ideal)]
    require(0 < max(errors) < (5*2+22)**2, "nonzero error below the full chirp allowance")
    require(all(Fraction(a*a+b*b, 1 << (2*p)) < Fraction(601, 1000)**2 for a, b in expected),
            "complete middle-map output norm below .601")
    raw = encode(values, p+2), word_bits(1, ell)+word_bits(3, ell), bytes([0])
    payload, sources, flags = (tape(value) for value in raw)
    counts = tuple(Count.literal(v) for v in (1, ell, p, 1))
    saved = tuple((bytes(v.tape.cells), v.tape.head) for v in counts)
    machine = Chirp(Cyclic(Convolution(Fourier(fixture()[0]))))
    try:
        with compiled_setup() as setup_calls, no_decode():
            output = machine.run(payload, sources, flags, *counts)
        actual = body(output)
        require(actual == encode(expected, p+2), "physical whole chirp equals staged exact oracle")
        require(tuple(body(v) for v in (payload, sources, flags)) == raw
                and tuple((bytes(v.tape.cells), v.tape.head) for v in counts) == saved,
                "complete chirp preserves borrowed ports")
        machine.idle()
        require(machine.closed and not machine.pool.live and machine.retained is machine.current is None,
                "closed complete chirp owner")
        require(all(t.head == 1 and all(b == BLANK for b in t.cells)
                    for owner in (machine, machine.kernel, machine.cyclic) for t in owner.pool.tapes),
                "complete chirp caller scratch erasure and origin heads")
        require(machine.calls == dict(kernels=1, endpoints=2, cyclic=1)
                and machine.cyclic.calls == dict(tables=1, twists=2, convolutions=1, narrowings=1, untwists=1)
                and machine.cyclic.convolution.calls == dict(forward=2, product=1, opposite=1, scale=1),
                "actual complete nested consumer calls")
        require(setup_calls == {"17^(.997)": 3, "18^(.997)": 3, "1^(.002)": 6},
                "exact scoped constant setup substitutions")
        try:
            machine.run(payload, sources, flags, *counts)
        except ValueError as error:
            require("consume prior chirp-middle output" in str(error), "protected chirp return")
            require(body(output) == actual, "protected chirp return remains intact")
        else:
            raise ValueError("missing protected chirp return rejection")
        output.clear()
        erase_marker(output)
        return {"p": p, "ell": ell, "A": 1, "gaussians": 8, "bits": len(actual),
                "sha256": sha256(actual).hexdigest(), "max_squared_error_in_p_grid_units": str(max(errors)),
                "calls": machine.calls, "cyclic_calls": machine.cyclic.calls,
                "convolution_calls": machine.cyclic.convolution.calls,
                "kernel_word_products": machine.kernel.arithmetic.products,
                "endpoint_word_products": machine.arithmetic.products,
                "twist_word_products": machine.cyclic.arithmetic.products,
                "pool_peak": machine.pool.peak, "cyclic_pool_peak": machine.cyclic.pool.peak,
                "compiled_setup_calls": setup_calls,
                "protected_return_control": True}
    finally:
        for value in counts:
            value.close()
