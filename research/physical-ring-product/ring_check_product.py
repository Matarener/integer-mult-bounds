"""Exact Gaussian convolution oracle and complete physical product packets."""

from fractions import Fraction
from hashlib import sha256
from ring_sources import require


def oracle(first, second, A, p, ell, rows):
    r, records = 1 << ell, rows*(1 << A)
    result = []
    for record in range(records):
        real, imaginary = [0]*r, [0]*r
        for a in range(r):
            x, y = first[record*r+a]
            for b in range(r):
                u, v = second[record*r+b]
                wrap, index = divmod(a+b, r)
                sign = -1 if wrap else 1
                real[index] += sign*(x*u-y*v)
                imaginary[index] += sign*(x*v+y*u)
        result.extend((int(Fraction(a, 1 << (p+ell))), int(Fraction(b, 1 << (p+ell))))
                      for a, b in zip(real, imaginary))
    return result


def packet(A, p, ell, rows=1, owner=None, first=None, second=None, consume=True):
    from cardinal_counts import Count
    from check_composed import encode
    from check_support import no_decode
    from ring_check_words import body, tape
    from ring_engine import RingProduct
    from session import erase_marker
    from words import BLANK
    machine = RingProduct() if owner is None else owner
    count = rows*(1 << (A+ell))
    limit = 1 << (p-1)
    if first is None:
        first = [((3*i+1) % (2*limit+1)-limit, (5*i+2) % (2*limit+1)-limit) for i in range(count)]
    if second is None:
        second = [((7*i+3) % (2*limit+1)-limit, (11*i+1) % (2*limit+1)-limit) for i in range(count)]
    require(len(first) == len(second) == count
            and all(a*a+b*b <= 1 << (2*p) for a, b in (*first, *second)),
            "complete product fixture in disk-grid domain")
    original = encode(first, p+2), encode(second, p+2)
    expected_values = oracle(first, second, A, p, ell, rows)
    expected = encode(expected_values, p+2)
    inputs = tape(original[0]), tape(original[1])
    counts = tuple(Count.literal(value) for value in (A, p, ell, rows))
    saved = tuple((bytes(value.tape.cells), value.tape.head) for value in counts)
    before = dict(machine.calls)
    products = machine.arithmetic.products
    nodes = dict(machine.word.calls)
    try:
        with no_decode():
            returned = machine.run(*inputs, *counts)
        actual = body(returned)
        require(actual == expected, "complete physical normalized product equals exact negacyclic oracle")
        require(tuple(body(value) for value in inputs) == original
                and saved == tuple((bytes(value.tape.cells), value.tape.head) for value in counts),
                "normalized product preserves complete borrowed ports")
        require(machine.closed and machine.a is machine.b is machine.current is None and not machine.pool.live,
                "closed normalized-product owner")
        machine.idle()
        for item in machine.pool.tapes:
            require(item.head == 1 and all(bit == BLANK for bit in item.cells),
                    "product scratch erasure and origin heads")
        m = ell+1
        Q = 2*p+2*m+(12*m+1).bit_length()+3
        expected_products = rows*(1 << A)*(1 << m)*(6*m+4)
        require(machine.arithmetic.products-products == expected_products,
                "complete paid word multiplication invoice")
        delta = {key: machine.calls[key]-before[key] for key in before}
        require(delta == dict(stages=3*m, tables=3*m, pointwise=1, recoveries=1),
                "complete three-transform normalized product schedule")
        depth, n = 0, Q+3
        while n > machine.word.leaf_bits:
            n = (n+1)//2
            depth += 1
        expected_nodes = (3**(depth+1)-1)//2
        require(machine.word.calls["nodes"]-nodes["nodes"] == expected_products*expected_nodes
                and machine.word.calls["leaves"]-nodes["leaves"] == expected_products*3**depth,
                "actual recursive data-word children at every multiplier call")
        receipt = {"A": A, "p": p, "ell": ell, "rows": rows, "Q": Q,
                   "gaussians": count, "word_products": expected_products, "word_depth": depth,
                   "word_nodes": expected_products*expected_nodes, "calls": delta,
                   "pool_peak": machine.pool.peak, "word_pool_peak": machine.word.pool.peak,
                   "twiddle_pool_peak": machine.twiddles.pool.peak, "sha256": sha256(actual).hexdigest()}
        if consume:
            returned.clear()
            erase_marker(returned)
        return machine, receipt, expected_values
    finally:
        for value in counts:
            value.close()


def run():
    owner, first, _ = packet(1, 2, 1,
        first=[(1, 1), (-2, 2), (3, 0), (0, -3)],
        second=[(2, -1), (1, 3), (-1, 1), (2, 0)])
    _, second, _ = packet(1, 3, 2, rows=2, owner=owner)
    _, third, _ = packet(1, 8, 2, owner=owner)
    values = [(8, 0)]*8
    _, boundary, exact = packet(1, 3, 2, owner=owner, first=values, second=values)
    require(max(a*a+b*b for a, b in exact) == 64, "exact unit-disk output boundary")
    return {"packets": [first, second, third, boundary]}
