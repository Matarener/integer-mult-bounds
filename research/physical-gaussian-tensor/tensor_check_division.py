"""Exact streamed quotient/remainder, bounded controls and alias restoration."""
from hashlib import sha256
from unittest.mock import patch
from tensor_sources import require


def run():
    import encoded
    import gaussian_rationals
    import gaussian_window
    import twiddle_setup
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from records import Tape
    from ring_check_words import decode
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    from tensor_counts import exact_setup_arithmetic
    from tensor_division import stream_divide
    from words import BLANK
    pool, digest = ScratchPool(64), sha256()
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    cases = [(a, b) for a in range(64) for b in range(1, 33)]
    for width in (31, 32, 33, 65, 129, 257):
        divisor = (1 << width)-3
        cases.extend(((0, divisor), (divisor-1, divisor), (divisor, divisor),
                      (divisor+1, divisor), (divisor*divisor+divisor-1, divisor)))
    cases.extend((((1 << 4097)-1, (1 << 32)-1), ((1 << 4096)+17, 1 << 31),
                  ((1 << 1025)+7, (1 << 513)+3)))
    for width in (33, 65, 129, 513, 4097):
        divisor = (1 << (width-1))+3
        cases.extend(((1, divisor), ((1 << (width-2))-1, divisor),
                      ((1 << (width-1))-1, divisor), (divisor-1, divisor),
                      (divisor, divisor), (17*divisor+2, divisor)))
    original = encoded.divide
    modules = (encoded, gaussian_rationals, gaussian_window, twiddle_setup)
    def check(a, b):
        with owned(Count.literal(a), Count.literal(b)) as (first, second):
            saved = [(bytes(v.tape.cells), v.tape.head) for v in (first, second)]
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode():
                            result = stream_divide(first, first if a == b else second)
                        with owned(*result) as (quotient, remainder):
                            require((decode(quotient), decode(remainder)) == divmod(a, b),
                                    "complete exact quotient and remainder against host divmod")
                            digest.update(packet_bytes(quotient.tape))
                            digest.update(packet_bytes(remainder.tape))
                    finally:
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in (first, second)],
                    "setup division preserves both borrowed operands and origin heads")
    for case in cases:
        check(*case)
    with owned(Count.literal(7), Count.literal(0)) as parameters:
        try:
            with no_decode():
                stream_divide(*parameters)
        except ValueError:
            pass
        else:
            raise ValueError("missing zero-divisor rejection")
    try:
        with exact_setup_arithmetic():
            require(all(module.divide is stream_divide for module in modules), "actual fixed setup aliases")
            raise RuntimeError("planned setup interruption")
    except RuntimeError:
        pass
    require(all(module.divide is original for module in modules), "restore setup aliases after interruption")
    for fail_at, divisor in ((2, 7), (3, (1 << 65)+3)):
        with owned(Count.literal((1 << 130)+7), Count.literal(divisor)) as (first, second):
            saved = [(bytes(v.tape.cells), v.tape.head) for v in (first, second)]
            literal, calls = Count.literal, 0
            def interrupted_literal(cls, value):
                nonlocal calls
                calls += 1
                if calls == fail_at:
                    raise RuntimeError("planned setup allocation interruption")
                return literal(value)
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode(), patch.object(Count, "literal", classmethod(interrupted_literal)):
                            stream_divide(first, second)
                    except RuntimeError as error:
                        require(str(error) == "planned setup allocation interruption", "expected setup interruption")
                    else:
                        raise ValueError("missing setup allocation interruption")
                    require(calls == fail_at and not pool.live, "close earlier allocations before returning failure")
                    pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in (first, second)],
                    "interrupted division restores borrowed operands and origin heads")
    for width in (33, 130):
        with owned(Count.literal((1 << width)-1), Count.literal((1 << 65)+3)) as (first, second):
            saved = [(bytes(v.tape.cells), v.tape.head) for v in (first, second)]
            original_msb, original_append = Count.msb, Tape.append
            scans = appends = 0
            armed = False
            def prefix_msb(value):
                nonlocal scans, armed
                result = original_msb(value)
                scans += 1
                if scans == 3:
                    armed = True
                return result
            def prefix_append(tape, value):
                nonlocal appends
                if armed:
                    appends += 1
                    if appends == 3:
                        raise RuntimeError("planned remainder prefix interruption")
                return original_append(tape, value)
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode(), patch.object(Count, "msb", prefix_msb), patch.object(Tape, "append", prefix_append):
                            stream_divide(first, second)
                    except RuntimeError as error:
                        require(str(error) == "planned remainder prefix interruption", "specific partial-prefix failure")
                    else:
                        raise ValueError("missing partial-prefix failure")
                    require(scans == appends == 3 and not pool.live,
                            "prefix interruption returns all owned tapes")
                    pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(v.tape.cells), v.tape.head) for v in (first, second)],
                    "prefix interruption restores both exhausted and unexhausted numerator heads")
    check(12345, 67)
    require(not pool.live and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in pool.tapes),
            "setup division restores its fixed tape inventory")
    return {"cases": len(cases)+1, "maximum_numerator_bits": max(a.bit_length() for a, _ in cases),
            "maximum_divisor_bits": max(b.bit_length() for _, b in cases), "pool_peak": pool.peak,
            "sha256": digest.hexdigest(), "controls": ["zero_divisor", "alias", "interrupted_alias_scope",
                                                       "interrupted_reverse_allocation", "interrupted_remainder_allocation",
                                                       "interrupted_short_prefix", "interrupted_long_prefix",
                                                       "positive_reuse"],
            "scope": "exact streamed division; only proven thirty-two-bit divisors enter finite control"}
