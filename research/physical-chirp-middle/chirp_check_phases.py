"""Certified phase error and changed-shape reuse of the numerical producer."""
from fractions import Fraction
from hashlib import sha256
from chirp_sources import require


def narrowing():
    from types import SimpleNamespace
    from cardinal_counts import Count
    from check_composed import encode
    from check_support import no_decode
    from phase_streams import narrow
    from ring_check_words import body, tape
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    B = 1 << 16
    counts = tuple(Count.literal(v) for v in (2, 18, 19))
    plan = SimpleNamespace(gaussians=counts[0], small=counts[1])
    pool = ScratchPool(32)
    scope = OuterScope(pool)
    positive = [(-B, B-1), (B-2, -1)]
    controls = []
    try:
        for values, rejected in ((positive, False), ([(2*B, 0), (0, 0)], True),
                                  ([(-2*B-1, 0), (0, 0)], True)):
            raw = encode(values, 19)
            source = tape(raw)
            with sealed_constructors(), scope.installed():
                try:
                    with no_decode():
                        result = narrow(source, counts[2], plan, pool)
                except ValueError as error:
                    require(rejected and "headroom" in str(error), "intended exact-width rejection")
                    controls.append(values[0][0])
                else:
                    try:
                        require(not rejected and body(borrowed_tape(result)) == encode(values, 18),
                                "narrowing preserves signed numerators without a shift")
                    finally:
                        result.clear()
                pool.empty()
            require(body(source) == raw, "narrowing preserves its borrowed wide packet")
        require(all(t.head == 1 and all(b == BLANK for b in t.cells[1:]) for t in pool.tapes),
                "narrowing scratch restoration")
        return {"exact_payload_sha256": sha256(encode(positive, 18)).hexdigest(),
                "overflow_controls": controls}
    finally:
        for value in counts:
            value.close()
        for value in pool.tapes:
            erase_marker(value)


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from chirp_kernel import ChirpKernel
    from ring_check_twiddles import reference
    from ring_check_words import body, decode, tape, word_bits
    from ring_words import read_signed
    from session import erase_marker
    from words import BLANK
    oracle, owner = reference(), ChirpKernel()
    receipts = []
    for p, ell, source_values, rows in ((16, 2, (1, 3), 2), (17, 3, (3, 5), 1)):
        r, lengths = 1 << ell, (ell-1, ell)
        raw_sources = b"".join(word_bits(v, ell) for v in source_values)
        sources, flags = tape(raw_sources), tape((0,))
        counts = tuple(Count.literal(v) for v in (1, ell, p, rows))
        width = Count.literal(p+2)
        before = dict(owner.calls)
        try:
            with no_decode():
                output = owner.run(sources, flags, *counts)
            actual = body(output)
            checked = 0
            for _ in range(rows):
                for j in range(r//2):
                    for k in range(r):
                        phase = (-2*source_values[0]*j*j-source_values[1]*k*k) % (2*r)
                        intervals = oracle.root_of_unity(phase, 2*r, p+24)
                        pair, errors = [], []
                        for interval in intervals:
                            value = read_signed(output, width)
                            try:
                                numerator = (-1 if value.negative else 1)*decode(value.magnitude)
                            finally:
                                value.close()
                            pair.append(numerator)
                            x = Fraction(numerator, 1 << p)
                            lo, hi = Fraction(interval.lo, interval.scale), Fraction(interval.hi, interval.scale)
                            errors.append(max(abs(x-lo), abs(x-hi)))
                        require(sum(x*x for x in pair) <= 1 << (2*p), "exact numerical chirp disk bound")
                        require(sum(x*x for x in errors) < Fraction(4, 1 << (2*p)),
                                "certified chirp error below two p-grid ulps")
                        checked += 1
            require(output.read() == BLANK and owner.closed and not owner.pool.live,
                    "complete numerical phase packet and restored owner")
            require(body(sources) == raw_sources and body(flags) == bytes((0,)), "preserved phase descriptors")
            require(owner.calls["tables"]-before["tables"] == 1
                    and owner.calls["phases"]-before["phases"] == checked,
                    "one short basis per complete packet")
            owner.idle()
            output.clear()
            erase_marker(output)
            receipts.append({"p": p, "ell": ell, "rows": rows, "phases": checked,
                             "sha256": sha256(actual).hexdigest(), "pool_peak": owner.pool.peak})
        finally:
            width.close()
            for value in counts:
                value.close()
    return {"packets": receipts, "certified_phases": sum(r["phases"] for r in receipts),
            "exact_narrowing": narrowing()}
