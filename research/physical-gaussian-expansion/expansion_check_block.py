"""Whole producer/block checks against staged arithmetic and Gaussian intervals."""
from fractions import Fraction as Q
from hashlib import sha256
from expansion_sources import require


def packet_bytes(tape):
    from words import BLANK
    tape.rewind()
    result = bytearray()
    try:
        while tape.read() != BLANK:
            result.append(tape.read())
            tape.step(1)
        return bytes(result)
    finally:
        tape.rewind()


def inputs(start, length, period):
    pairs = ((Q(3, 4), Q(-1, 4)), (Q(1, 2), Q(1, 4)), (Q(-1, 8), Q(1, 2)),
             (Q(5, 8), Q(-3, 8)), (Q(-1, 4), Q(1, 4)), (Q(3, 8), Q(-1, 8)),
             (Q(1, 2), Q(3, 8)))
    return [pairs[(j % period) % len(pairs)] for j in range(start, start+length)]


def expected_page(page, s, t, alpha, radius, start, length, p, bits, sigma):
    from expansion_records import BlockHeader
    from gaussian_check_exponentials import oracle
    from ring_check_words import decode
    from ring_words import read_signed
    from router_metadata import owned
    from words import BLANK
    page.rewind()
    with owned(BlockHeader(page)) as (header,):
        signed = lambda value: (-1 if value.negative else 1)*decode(value.magnitude)
        kappa = Q(s, t)
        j0 = (kappa*start).__floor__()
        gamma = j0-kappa*start
        low = -radius-1
        high = (kappa*(length-1)-gamma).__ceil__()+radius+1
        n, nc = high-low+1, high-low+length
        require((decode(header.n), decode(header.m), decode(header.nc), signed(header.source_start),
                 signed(header.target_start)) == (n, length, nc, j0+low, start),
                "producer binds the full global source and target windows")
        factors = {}
        for kind, count in (("A", n), ("K", nc), ("B", length)):
            factors[kind] = []
            for index in range(count):
                with owned(read_signed(page, header.width)) as (value,):
                    actual = Q(signed(value), 1 << bits)
                if kind == "A":
                    h = low+index
                    exponent = ((1-kappa)*h*h+2*gamma*h+gamma*gamma)/(alpha*alpha)
                elif kind == "K":
                    d = -high+index
                    exponent = kappa*d*d/(alpha*alpha)
                else:
                    z = index
                    exponent = ((kappa*kappa-kappa)*z*z-2*gamma*kappa*z)/(alpha*alpha)
                lower, upper = oracle(abs(exponent), exponent < 0, 0 if kind == "K" else sigma)
                require(0 <= actual <= lower <= upper <= 1 and upper-actual < Q(4, 1 << bits),
                        "complete normalized factor encloses its original real Gaussian coefficient")
                factors[kind].append(actual)
        with owned(read_signed(page, header.width)) as (value,):
            c = Q(signed(value), 1 << bits)
        require(c == Q((1 << bits)//(2*alpha), 1 << bits) and page.read() == BLANK,
                "exact encoded reciprocal alpha and complete factor page")
    page.rewind()
    return j0+low, factors, c


def models(data, factors, c, s, t, alpha, source_start, target_start, m, p, bits, sigma, check_premature=True):
    from gaussian_check_exponentials import oracle
    n = len(data)
    rounding = lambda value: Q(int(value*(1 << bits)), 1 << bits)
    actual, premature = [], []
    errors = Q(0)
    for z in range(m):
        pair, wrong = [], []
        for component in (0, 1):
            weighted = [rounding(factors["A"][i]*data[i][component]) for i in range(n)]
            convolution = rounding(sum((weighted[i]*factors["K"][n-1+z-i] for i in range(n)), Q(0)))
            post_chirp = rounding(factors["B"][z]*convolution)
            fine = rounding(c*post_chirp)
            value = int(fine*(1 << (2*sigma+p)))
            pair.append(value)
            early = Q(int(post_chirp*(1 << p)), 1 << p)
            wrong.append(int(c*early*(1 << (2*sigma+p))))
            lower = upper = Q(0)
            for i in range(n):
                exponent = (source_start+i-Q(s, t)*(target_start+z))**2/(alpha*alpha)
                lo, hi = oracle(exponent)
                ends = sorted((data[i][component]*lo, data[i][component]*hi))
                lower += ends[0]/(2*alpha)
                upper += ends[1]/(2*alpha)
            errors = max(errors, abs(Q(value, 1 << p)-lower), abs(Q(value, 1 << p)-upper))
        actual.append(pair)
        premature.append(wrong)
    require(errors < Q(2, 1 << p), "whole normalized finite block agrees with direct Gaussian intervals")
    if check_premature:
        require(actual != premature, "premature p-grid extraction changes the complete normalized result")
    return actual, premature, Q((errors*(1 << 96)).__ceil__(), 1 << 96)


def periodic_error(actual, s, t, alpha, target_start, p):
    """Independent periodic S/2 enclosure, with a rigorous omitted tail."""
    from gaussian_check_exponentials import oracle
    require(alpha >= 2, "periodic Gaussian oracle alpha domain")
    result = Q(0)
    scale = 1 << 96
    tail = Q(1, 1 << 256)
    for z, pair in enumerate(actual):
        center = Q(s, t)*(target_start+z)
        origin = center.__floor__()
        lower = [Q(0), Q(0)]
        upper = [Q(0), Q(0)]
        for j in range(origin-8*alpha, origin+8*alpha+1):
            lo, hi = oracle((j-center)**2/(alpha*alpha))
            values = inputs(j, 1, s)[0]
            for component, value in enumerate(values):
                ends = sorted((value*lo/(2*alpha), value*hi/(2*alpha)))
                lower[component] += Q((ends[0]*scale).__floor__(), scale)
                upper[component] += Q((ends[1]*scale).__ceil__(), scale)
        # Beyond distance8alpha the two normalized tails are bounded by
        # (1/alpha+1/(16pi))*exp(-64pi)<2^-256 for alpha>=2.
        for component, value in enumerate(pair):
            result = max(result, abs(Q(value, 1 << p)-(lower[component]-tail)),
                         abs(Q(value, 1 << p)-(upper[component]+tail)))
    require(result < Q(2, 1 << p), "finite complete output agrees with the periodic Gaussian map")
    return Q((result*scale).__ceil__(), scale)


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_block import Block
    from expansion_prepare import Preparation
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK
    preparation, block = Preparation(), Block()
    records = []
    for s, t, alpha, radius, start, length, p, bits, sigma in (
            (7, 8, 2, 1, 0, 1, 4, 32, 4),
            (7, 8, 2, 1, -1, 1, 8, 48, 4)):
        page = returned = None
        source = Tape()
        with owned(*(Count.literal(v) for v in (s, t, alpha, radius, abs(start), length, p, bits, sigma))) as args:
            source_length, target_length, a, b, origin, m, target_p, P, scale = args
            saved = [(bytes(value.tape.cells), value.tape.head) for value in args]
            try:
                with no_decode():
                    page = preparation.run_explicit(source_length, target_length, a, b,
                                                     Signed(origin, start < 0), m, target_p, P, scale)
                page_bytes = packet_bytes(page)
                source_start, factors, c = expected_page(page, s, t, alpha, radius, start, length, p, bits, sigma)
                data = inputs(source_start, len(factors["A"]), s)
                expected, premature, error = models(data, factors, c, s, t, alpha, source_start,
                                                    start, length, p, bits, sigma)
                global_error = periodic_error(expected, s, t, alpha, start, p)
                with owned(Count.literal(p+2)) as (width,):
                    for pair in data:
                        for value in pair:
                            numerator = int(value*(1 << p))
                            with owned(Signed(Count.literal(abs(numerator)), numerator < 0)) as (encoded,):
                                write_signed(encoded, source, width)
                    source.rewind()
                    source_bytes = body(source)
                    before = dict(block.word.calls)
                    with no_decode():
                        returned = block.run(page, source)
                    raw = body(returned)
                    actual = []
                    for _ in range(length):
                        with owned(read_signed(returned, width), read_signed(returned, width)) as (real, imaginary):
                            actual.append([(-1 if v.negative else 1)*decode(v.magnitude) for v in (real, imaginary)])
                    require(actual == expected and returned.read() == BLANK,
                            "complete produced expansion block equals the exact staged model")
                    require(any(v for pair in actual for v in pair), "nonzero complete expansion return")
                    word_calls = {key: block.word.calls[key]-before[key] for key in before}
                    require(sum(word_calls.values()) == 4*len(data)+6*length+8,
                            "complete expansion word invoice includes norms and normalization")
                    require(packet_bytes(page) == page_bytes and body(source) == source_bytes,
                            "complete expansion preserves borrowed page and source")
                    require(saved == [(bytes(value.tape.cells), value.tape.head) for value in args],
                            "complete factor producer preserves borrowed parameters")
                    require(preparation.closed and not preparation.pool.live and block.closed and not block.pool.live,
                            "complete expansion owners close their scratch leases")
                    records.append({"s": s, "t": t, "alpha": alpha, "radius": radius,
                                    "target": [start, length], "source": [source_start, len(data)],
                                    "p": p, "P": bits, "sigma": sigma, "values": actual,
                                    "premature_values": premature, "direct_error": str(error),
                                    "periodic_error": str(global_error),
                                    "page_sha256": sha256(page_bytes).hexdigest(), "core_sha256": sha256(raw).hexdigest(),
                                    "word_calls": word_calls, "preparation_counts": preparation.last_counts})
            finally:
                for tape in (returned, page, source):
                    if tape is not None:
                        tape.clear()
                        erase_marker(tape)
                block.idle()
    return {"blocks": records, "preparation_pool_peak": preparation.pool.peak,
            "block_pool_peak": block.pool.peak,
            "scope": "complete encoded coefficient producer and normalized finite block; reduced radii do not assert production Gaussian tail bounds"}
