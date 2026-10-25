"""Complete physical Fourier/product composition against two exact models."""

from fractions import Fraction
from hashlib import sha256
from ring_sources import require


def direct(first, second, flags, ell, p, rows):
    from check_fourier import coordinates, natural_lengths
    lengths = natural_lengths(flags, ell)
    r, M = 1 << ell, 1 << sum(lengths)
    result = []
    for row in range(rows):
        for j in range(M):
            js = coordinates(j, lengths)
            real, imaginary = [0]*r, [0]*r
            for k in range(M):
                ks = coordinates(k, lengths)
                partner = 0
                for a, b, width in zip(js, ks, lengths):
                    partner = (partner << width) | ((a-b) % (1 << width))
                for a in range(r):
                    x, y = first[(row*M+k)*r+a]
                    for b in range(r):
                        u, v = second[(row*M+partner)*r+b]
                        wrap, target = divmod(a+b, r)
                        sign = -1 if wrap else 1
                        real[target] += sign*(x*u-y*v)
                        imaginary[target] += sign*(x*v+y*u)
            result.extend((Fraction(a, (1 << p)*r*M), Fraction(b, (1 << p)*r*M))
                          for a, b in zip(real, imaginary))
    return result


def run():
    from cardinal_counts import Count
    from check_composed import encode, fixture
    from check_fourier import dense
    from ring_check_product import oracle
    from check_support import no_decode
    from ring_check_words import body, decode, tape
    from convolution_engine import Convolution
    from fourier_engine import Fourier
    from session import erase_marker
    from words import BLANK
    p, ell, A, rows, flags = 3, 2, 1, 2, (0,)
    first = ([(3, 0), (4, 0), (4, 0), (4, 0)] + [(4, 0)]*4
             + [(0, -3), (0, -4), (0, -4), (0, -4)] + [(0, -4)]*4)
    second = ([(7, 0), (8, 0), (8, 0), (8, 0)] + [(8, 0)]*4
              + [(0, 7), (0, 8), (0, 8), (0, 8)] + [(0, 8)]*4)
    forward_first, forward_second = dense(first, flags, ell, rows, False), dense(second, flags, ell, rows, False)
    product = oracle(forward_first, forward_second, A, p, ell, rows)
    opposite = dense(product, flags, ell, rows, True)
    expected_values = [(a << A, b << A) for a, b in opposite]
    ideal = direct(first, second, flags, ell, p, rows)
    errors = [(Fraction(a)-c)**2+(Fraction(b)-d)**2
              for (a, b), (c, d) in zip(expected_values, ideal)]
    require(max(errors) > 0 and max(errors) < 32*(1 << (2*A)),
            "nonzero rounding inside the complete normalized-convolution error bound")
    expected_width = p+2+A
    expected = encode(expected_values, expected_width)
    original = encode(first, p+2), encode(second, p+2), bytes(flags)
    inputs = tuple(tape(value) for value in original)
    counts = tuple(Count.literal(value) for value in (len(flags), ell, p, rows))
    saved = tuple((bytes(value.tape.cells), value.tape.head) for value in counts)
    owner = Convolution(Fourier(fixture()[0]))
    try:
        with no_decode():
            output, width_port = owner.run(*inputs, *counts)
        actual = body(output)
        width = Count(width_port)
        try:
            require(decode(width) == expected_width, "explicit widened convolution output descriptor")
        finally:
            width.close()
        require(actual == expected, "complete physical convolution equals staged exact oracle")
        require(tuple(body(value) for value in inputs) == original
                and saved == tuple((bytes(value.tape.cells), value.tape.head) for value in counts),
                "complete convolution preserves all borrowed ports")
        require(owner.closed and not owner.pool.live and owner.a is owner.b is owner.current is None,
                "closed convolution caller")
        owner.idle()
        require(all(item.head == 1 and all(bit == BLANK for bit in item.cells) for item in owner.pool.tapes),
                "convolution scratch erasure and origin heads")
        require(owner.calls == dict(forward=2, product=1, opposite=1, scale=1),
                "actual complete outer consumer calls")
        output.clear()
        erase_marker(output)
        try:
            owner.run(*inputs, *counts)
        except ValueError as error:
            require("consume both" in str(error), "width port participates in protected return")
        else:
            raise ValueError("missing protected width-port rejection")
        width_port.clear()
        erase_marker(width_port)
        return {"A": A, "p": p, "ell": ell, "rows": rows, "flags": list(flags),
                "gaussians": len(first), "output_width": expected_width, "bits": len(actual),
                "sha256": sha256(actual).hexdigest(), "max_squared_error_in_p_grid_units": str(max(errors)),
                "calls": owner.calls, "product_word_calls": owner.product.arithmetic.products,
                "pool_peak": owner.pool.peak, "protected_width_control": True}
    finally:
        for value in counts:
            value.close()
