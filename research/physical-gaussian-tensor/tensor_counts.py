"""Exact fixed-digit schoolbook multiplication for encoded setup counters."""
from contextlib import ExitStack, contextmanager
from unittest.mock import patch
from tensor_sources import active
active()
from cardinal_counts import Count
from compact_counts import Counter
from router_metadata import owned
from session import borrowed_tape
from tensor_word import DIGIT_BITS, accumulate_digit, digit_product, read_digit, write_digit
from words import RIGHT, need


def digit_count_product(cls, left, right):
    """Keep both arbitrary-width operands and the result on their own tapes."""
    first = second = count = backward = result = None
    try:
        first = cls(left)
        second = cls(right)
        if first.zero() or second.zero():
            return cls.literal(0)
        count = cls.literal(0)
        finite_digits = 0
        while second.read() != RIGHT:
            read_digit(second)
            count.increment()
            if finite_digits is not None:
                finite_digits = None if finite_digits == 32 else finite_digits+1
        second.rewind()
        backward = cls(count)
        backward.multiply_small(DIGIT_BITS)
        result = cls.literal(0)
        borrowed_tape(result.tape).clear()
        result.tape.append(RIGHT)
        result.rewind()
        while first.read() != RIGHT:
            a, carry = read_digit(first), 0
            second.rewind()
            while second.read() != RIGHT:
                b = read_digit(second)
                carry, _ = accumulate_digit(result.tape, digit_product(a, b)+carry)
            need(result.read() == RIGHT, "setup product next high digit")
            write_digit(result.tape, carry, True)
            if finite_digits is not None:
                for _ in range(DIGIT_BITS*finite_digits):
                    result.step(-1)
            else:
                with owned(Counter(backward)) as (steps,):
                    while not steps.finished:
                        result.step(-1)
                        steps.decrement()
        result.rewind()
        result.normalize()
        returned, result = result, None
        return returned
    finally:
        for value in (result, backward, count, second, first):
            if value is not None:
                value.close()


@contextmanager
def exact_setup_arithmetic():
    """Specialize exact setup primitives within one outer invocation only."""
    import encoded
    import gaussian_rationals
    import gaussian_window
    import twiddle_setup
    from tensor_division import stream_divide
    original = Count.__dict__["product"]
    original_divide = encoded.divide
    division_modules = (encoded, gaussian_rationals, gaussian_window, twiddle_setup)
    need(original.__func__ is not digit_count_product, "one setup arithmetic adaptation")
    need(original_divide is not stream_divide and all(module.divide is original_divide for module in division_modules),
         "one retained setup division cohort")
    with ExitStack() as stack:
        stack.enter_context(patch.object(Count, "product", classmethod(digit_count_product)))
        for module in division_modules:
            stack.enter_context(patch.object(module, "divide", stream_divide))
        yield
    need(Count.__dict__["product"] is original, "restore the retained setup arithmetic class")
    need(all(module.divide is original_divide for module in division_modules), "restore every retained setup division alias")
