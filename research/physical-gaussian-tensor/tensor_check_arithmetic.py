"""Effective-width exact products preserve nominal guards and ownership."""
from hashlib import sha256
from unittest.mock import patch
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from fft_word_engine import FftWord
    from expansion_check_block import packet_bytes
    from records import Tape
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_count, borrowed_tape, erase_marker, initialize_marker, sealed_constructors
    import tensor_arithmetic
    from tensor_arithmetic import NarrowArithmetic
    from tensor_word import adapt_fft_word
    from words import BLANK
    word = adapt_fft_word(FftWord(base_bits=4096))
    pool, digest = ScratchPool(64), sha256()
    scope = OuterScope(pool)
    arithmetic = NarrowArithmetic(word, scope)
    for tape in pool.tapes:
        erase_marker(tape)
    cases = [(a, b, width) for a, b in ((0, 0), (0, -3), (-3, 0), (-7, 9), (19, -21), (-31, -63), (255, 255))
             for width in (8, 50, 546)]
    cases.extend(((1 << 79, -(1 << 80)+1, 546), ((1 << 160)-1, (1 << 79)+3, 1092),
                  ((1 << 512)-1, -(1 << 511)+3, 600)))
    for bits in (31, 32, 33, 255, 256, 257):
        maximum = (1 << bits)-1
        cases.extend(((maximum, maximum, 1096), (maximum, -(maximum//3), 1096)))
    def evaluate(a, b, width, reject=False):
        with owned(Signed(Count.literal(abs(a)), a < 0), Signed(Count.literal(abs(b)), b < 0),
                   Count.literal(width)) as (left, right, nominal):
            saved = [bytes(value.tape.cells) for value in (left.magnitude, right.magnitude, nominal)]
            operand = (Signed(borrowed_count(left.magnitude), left.negative) if a == b and a != 0
                       else left if a == b else right)
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        if reject:
                            try:
                                with no_decode():
                                    result = arithmetic.multiply(left, operand, nominal)
                            except ValueError:
                                pass
                            else:
                                result.close()
                                raise ValueError("missing nominal-width guard")
                        else:
                            with no_decode():
                                result = arithmetic.multiply(left, operand, nominal)
                            with owned(result):
                                actual = decode(result.magnitude)*(-1 if result.negative else 1)
                                require(actual == a*b, "effective-width physical word matches the complete signed product")
                                digest.update(packet_bytes(result.magnitude.tape))
                    finally:
                        pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [bytes(value.tape.cells) for value in (left.magnitude, right.magnitude, nominal)]
                    and all(value.tape.head == 1 for value in (left.magnitude, right.magnitude, nominal)),
                    "effective-width scalar preserves its borrowed ports")
            require(not pool.live and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in pool.tapes),
                    "effective-width arithmetic restores fixed parent scratch")
            word.idle()
            require(word.closed and word.output.read() == BLANK, "effective-width arithmetic consumes its actual word return")
    for case in cases:
        evaluate(*case)
    for case in ((0, 0, 0), (1 << 16, 0, 16), (0, 1 << 16, 16), (1 << 16, 1, 16)):
        evaluate(*case, reject=True)
    for alias in (False, True):
        with owned(Signed(Count.literal((1 << 65)-1)), Signed(Count.literal((1 << 64)+3)),
                   Count.literal(1096)) as (left, right, width):
            values = (left.magnitude, right.magnitude, width)
            saved = [(bytes(value.tape.cells), value.tape.head) for value in values]
            operand = Signed(borrowed_count(left.magnitude)) if alias else right
            product, updates = tensor_arithmetic.digit_product, 0
            def interrupted_product(a, b):
                nonlocal updates
                value = product(a, b)
                updates += 1
                if updates == 3:
                    Tape()
                return value
            for tape in pool.tapes:
                initialize_marker(tape)
            try:
                with sealed_constructors(), scope.installed():
                    try:
                        with no_decode(), patch.object(tensor_arithmetic, "digit_product", interrupted_product):
                            result = arithmetic.multiply(left, operand, width)
                    except ValueError as error:
                        require("physical Tape allocation inside" in str(error), "late scalar allocation rejection")
                    else:
                        result.close()
                        raise ValueError("missing late scalar allocation rejection")
                    require(updates == 3 and not pool.live, "failed scalar leaf releases owned result and alias copy")
                    pool.empty()
            finally:
                for tape in pool.tapes:
                    erase_marker(tape)
            require(saved == [(bytes(value.tape.cells), value.tape.head) for value in values],
                    "failed scalar leaf restores both borrowed operands")
    with owned(Signed(Count.literal(3)), Signed(Count.literal(5)), Count.literal(546)) as (left, right, width):
        literal = Count.literal
        def interrupted_cutoff(cls, value):
            if value == tensor_arithmetic.SCALAR_BITS:
                raise ValueError("planned scalar cutoff allocation failure")
            return literal(value)
        values = (left.magnitude, right.magnitude, width)
        saved = [(bytes(value.tape.cells), value.tape.head) for value in values]
        for tape in pool.tapes:
            initialize_marker(tape)
        try:
            with sealed_constructors(), scope.installed():
                try:
                    with no_decode(), patch.object(Count, "literal", classmethod(interrupted_cutoff)):
                        result = arithmetic.multiply(left, right, width)
                except ValueError as error:
                    require(str(error) == "planned scalar cutoff allocation failure", "specific cutoff rejection")
                else:
                    result.close()
                    raise ValueError("missing scalar cutoff rejection")
                require(not pool.live, "failed cutoff construction releases both measured widths")
                pool.empty()
        finally:
            for tape in pool.tapes:
                erase_marker(tape)
        require(saved == [(bytes(value.tape.cells), value.tape.head) for value in values],
                "failed cutoff construction preserves borrowed ports")
    with owned(Count.literal(3), Count.literal(5), Count.literal(8)) as parameters:
        protected = word.run(*parameters)
        saved_return = packet_bytes(protected)
        try:
            with owned(Signed(Count.literal(3)), Signed(Count.literal(5)), Count.literal(546)) as (left, right, width):
                for tape in pool.tapes:
                    initialize_marker(tape)
                try:
                    with sealed_constructors(), scope.installed():
                        try:
                            try:
                                with no_decode():
                                    result = arithmetic.multiply(left, right, width)
                            except ValueError as error:
                                require("consume prior word return" in str(error), "scalar leaf preserves the word-owner boundary")
                            else:
                                result.close()
                                raise ValueError("scalar leaf bypassed the protected word return")
                        finally:
                            pool.empty()
                finally:
                    for tape in pool.tapes:
                        erase_marker(tape)
            require(packet_bytes(protected) == saved_return, "scalar rejection preserves the complete protected child output")
        finally:
            protected.clear()
            erase_marker(protected)
    evaluate(-31, 17, 546)
    require(arithmetic.leaves > 0 and arithmetic.words > 0
            and arithmetic.leaves+arithmetic.words == arithmetic.products == len(cases)+1,
            "actual fixed scalar leaves and retained larger word calls")
    return {"products": len(cases)+1, "rejections": 8, "pool_peak": pool.peak,
            "leaves": arithmetic.leaves, "words": arithmetic.words,
            "sha256": digest.hexdigest(), "scope": "fixed physical scalar leaves and shorter word calls after both nominal-width guards"}
