"""Guard the declared width, then multiply at the actual encoded width."""
from contextlib import ExitStack
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import read_fixed
from encoded import compare
from fft_arithmetic import Arithmetic
from ring_words import Signed
from router_metadata import owned
from session import borrowed_count, borrowed_tape, erase_marker
from words import BLANK, RIGHT, need
from tensor_word import DIGIT_BITS, accumulate_digit, digit_product, read_digit, write_digit

SCALAR_BITS = 256


def small_product(left, right):
    """Multiply admitted fixed-width tapes with bounded row and retreat controls."""
    first, second = borrowed_count(left), borrowed_count(right)
    alias_copy = result = None
    try:
        if borrowed_tape(left.tape) is borrowed_tape(right.tape):
            alias_copy = Count(right)
            second = alias_copy
        if first.zero() or second.zero():
            return Count.literal(0)
        digits = 0
        for _ in range(SCALAR_BITS // DIGIT_BITS):
            if second.read() == RIGHT:
                break
            read_digit(second)
            digits += 1
        need(0 < digits <= SCALAR_BITS // DIGIT_BITS and second.read() == RIGHT,
             "fixed scalar second-operand extent")
        second.rewind()
        result = Count.literal(0)
        borrowed_tape(result.tape).clear()
        result.tape.append(RIGHT)
        result.rewind()
        for _ in range(SCALAR_BITS // DIGIT_BITS):
            if first.read() == RIGHT:
                break
            a, carry = read_digit(first), 0
            second.rewind()
            for _ in range(digits):
                need(second.read() != RIGHT, "complete fixed scalar product row")
                b = read_digit(second)
                carry, _ = accumulate_digit(result.tape, digit_product(a, b)+carry)
            need(second.read() == result.read() == RIGHT, "fixed scalar next high digit")
            write_digit(result.tape, carry, True)
            for _ in range(DIGIT_BITS*digits):
                result.step(-1)
        need(first.read() == RIGHT, "fixed scalar first-operand extent")
        result.rewind()
        result.normalize()
        returned, result = result, None
        return returned
    finally:
        first.rewind()
        second.rewind()
        if alias_copy is not None:
            alias_copy.close()
        if result is not None:
            result.close()


def measured_width(value, nominal):
    positive(nominal)
    result = Count.literal(0)
    value.rewind()
    try:
        while value.read() != RIGHT:
            need(value.read() in (0, 1), "canonical data-word digit")
            result.increment()
            value.step(1)
        need(compare(result, nominal) <= 0, "data magnitude fits declared word width")
        positive(result)
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()


class NarrowArithmetic(Arithmetic):
    def __init__(self, word, scope):
        super().__init__(word, scope)
        self.leaves = self.words = 0

    def multiply(self, left, right, width):
        positive(width)
        with ExitStack() as owners:
            a, = owners.enter_context(owned(measured_width(left.magnitude, width)))
            b, = owners.enter_context(owned(measured_width(right.magnitude, width)))
            cutoff, = owners.enter_context(owned(Count.literal(SCALAR_BITS)))
            size = a if compare(a, b) >= 0 else b
            if compare(size, cutoff) <= 0:
                self.word.idle()
                need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK,
                     "consume prior word return before scalar leaf")
                result = Signed(small_product(left.magnitude, right.magnitude),
                                left.negative != right.negative)
                self.products += 1
                self.leaves += 1
                return result
            with self.scope.suspended():
                returned = self.word.run(borrowed_count(left.magnitude),
                                         borrowed_count(right.magnitude), borrowed_count(size))
            magnitude = None
            try:
                with owned(Count(size)) as (output_width,):
                    output_width.multiply_small(2)
                    magnitude = read_fixed(returned, output_width)
                need(returned.read() == BLANK, "complete effective-width scalar product return")
                result = Signed(magnitude, left.negative != right.negative)
                magnitude = None
                self.products += 1
                self.words += 1
                return result
            finally:
                if magnitude is not None:
                    magnitude.close()
                returned.clear()
                erase_marker(returned)


def adapt_arithmetic(owner):
    need(type(owner.arithmetic) is Arithmetic and owner.arithmetic.products == 0
         and owner.arithmetic.word is owner.word and owner.arithmetic.scope is owner.scope,
         "fresh exact scalar interface before width adaptation")
    owner.arithmetic = NarrowArithmetic(owner.word, owner.scope)
