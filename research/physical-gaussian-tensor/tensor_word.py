"""Exact fixed-digit leaves inside the retained physical Karatsuba owner."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare
from ring_words import fits
from router_metadata import owned
from word_product import WordProduct
from words import BLANK, RIGHT, need

LEAF_BITS = 1024
DIGIT_BITS = 32
DIGIT_RADIX = 1 << DIGIT_BITS
DIGIT_MASK = DIGIT_RADIX-1
CONTROL_MAX = DIGIT_RADIX*DIGIT_RADIX-1


def digit_product(first, second):
    """Thirty-two fixed shift/add phases; controls never exceed sixty-four bits."""
    need(type(first) is int and type(second) is int and 0 <= first <= DIGIT_MASK and 0 <= second <= DIGIT_MASK,
         "fixed thirty-two-bit control operands")
    if first == 0 or second == 0:
        return 0
    result, shifted, remaining = 0, first, second
    for _ in range(DIGIT_BITS):
        if remaining & 1:
            result += shifted
        remaining >>= 1
        shifted <<= 1
    need(0 <= result <= DIGIT_MASK*DIGIT_MASK and remaining == 0 and shifted <= DIGIT_MASK*DIGIT_RADIX,
         "sixty-four-bit finite-control product")
    return result


def read_digit(source):
    value = 0
    for position in range(DIGIT_BITS):
        symbol = source.read()
        if symbol == RIGHT:
            break
        need(symbol in (0, 1), "complete canonical magnitude digit")
        value |= symbol << position
        source.step(1)
    return value


def write_digit(target, value, extend):
    need(type(value) is int and 0 <= value <= DIGIT_MASK, "thirty-two-bit output control")
    for position in range(DIGIT_BITS):
        target.write((value >> position) & 1)
        target.step(1)
    if extend:
        need(target.read() == BLANK, "vacant accumulated-digit extension")
        target.write(RIGHT)


def accumulate_digit(target, addend):
    """Add a bounded product and carry while scanning the old digit once."""
    need(type(addend) is int and 0 <= addend <= CONTROL_MAX-DIGIT_MASK,
         "bounded product and incoming digit carry")
    extend = target.read() == RIGHT
    remaining, previous = addend, 0
    for position in range(DIGIT_BITS):
        bit = 0 if extend else target.read()
        need(bit in (0, 1), "complete accumulated digit")
        previous |= bit << position
        value = (remaining & 1)+bit
        target.write(value & 1)
        remaining = (remaining >> 1)+(value >> 1)
        target.step(1)
    if extend:
        need(target.read() == BLANK, "vacant accumulated-digit extension")
        target.write(RIGHT)
    total = previous+addend
    need(0 <= remaining <= DIGIT_MASK and total <= CONTROL_MAX,
         "sixty-four-bit accumulated digit and outgoing carry")
    return remaining, total


def leaf_width(width):
    size = 0
    width.rewind()
    try:
        for position in range(11):
            bit = width.read()
            if bit == RIGHT:
                return size if 1 <= size <= LEAF_BITS else None
            if bit not in (0, 1):
                return None
            size |= bit << position
            width.step(1)
        return size if width.read() == RIGHT and 1 <= size <= LEAF_BITS else None
    finally:
        width.rewind()


def leaf_fits(value, size):
    need(type(size) is int and 1 <= size <= LEAF_BITS, "bounded word-leaf admission width")
    length, overflow = 0, False
    value.rewind()
    try:
        while value.read() != RIGHT:
            need(value.read() in (0, 1), "canonical data-word digit")
            if length < size:
                length += 1
            else:
                overflow = True
            value.step(1)
        need(not overflow, "data magnitude fits declared word width")
    finally:
        value.rewind()


class DigitWordProduct(WordProduct):
    """Preserve the original recursive continuation and exact word boundary."""
    def __init__(self):
        super().__init__(leaf_bits=LEAF_BITS)
        self.digit_counts = dict(products=0, rows=0, updates=0, max_control=0)

    def leaf(self, first, second):
        self.digit_counts["products"] += 1
        if first.zero() or second.zero():
            return Count.literal(0)
        result = None
        first.rewind()
        second.rewind()
        try:
            digits = 0
            for _ in range(LEAF_BITS // DIGIT_BITS):
                if second.read() == RIGHT:
                    break
                read_digit(second)
                digits += 1
            need(0 < digits <= LEAF_BITS // DIGIT_BITS and second.read() == RIGHT,
                 "fixed word-leaf digit extent")
            second.rewind()
            tape = self.pool.acquire()
            result = object.__new__(Count)
            result.tape = tape
            result.tape.append(RIGHT)
            result.rewind()
            for _ in range(LEAF_BITS // DIGIT_BITS):
                if first.read() == RIGHT:
                    break
                a, carry = read_digit(first), 0
                second.rewind()
                for _ in range(digits):
                    need(second.read() != RIGHT, "complete fixed word-leaf row")
                    b = read_digit(second)
                    carry, total = accumulate_digit(result.tape, digit_product(a, b)+carry)
                    self.digit_counts["updates"] += 1
                    self.digit_counts["max_control"] = max(self.digit_counts["max_control"], total)
                need(second.read() == result.read() == RIGHT, "new high digit after each product row")
                write_digit(result.tape, carry, True)
                for _ in range(DIGIT_BITS*digits):
                    result.step(-1)
                self.digit_counts["rows"] += 1
            need(first.read() == RIGHT, "complete fixed word-leaf first operand")
            result.rewind()
            result.normalize()
            output, result = result, None
            return output
        finally:
            first.rewind()
            second.rewind()
            if result is not None:
                result.close()

    def enter(self):
        need(self.leaf_bits == LEAF_BITS, "fixed digit-leaf compile parameter")
        n, a, b = self.c("n"), self.c("a"), self.c("b")
        with owned(Count.literal(LEAF_BITS)) as (cutoff,):
            small = compare(n, cutoff) <= 0
        if not small:
            return super().enter()
        self.calls["nodes"] += 1
        positive(n)
        size = leaf_width(n)
        if size is None:
            fits(a, n)
            fits(b, n)
        else:
            leaf_fits(a, size)
            leaf_fits(b, size)
        self.finish(self.leaf(a, b))
        self.clear_active()
        self.calls["leaves"] += 1
        return False


def pristine(word):
    need(type(word) is WordProduct and word.closed and not word.pool.live
         and all(value == 0 for value in word.calls.values())
         and word.output.read() == BLANK
         and all(tape.read() == BLANK for tape in word.canonical),
         "pristine retained word owner before source adaptation")


def adapt_scalar(owner):
    pristine(owner.word)
    need(owner.arithmetic.word is owner.word, "retained scalar arithmetic owner link")
    word = DigitWordProduct()
    owner.word = word
    owner.arithmetic.word = word
    return word


def adapt_fft_word(owner):
    from tensor_twiddles import adapt_twiddles
    need(owner.closed and not owner.pool.live and owner.output.read() == BLANK
         and all(value == 0 for value in owner.calls.values()), "fresh FFT-word source adaptation")
    pristine(owner.base)
    owner.base = DigitWordProduct()
    adapt_scalar(owner.product)
    adapt_twiddles(owner.product)
    owner.canonical = (*owner.base.canonical, owner.base.output, owner.product.output,
                       *owner.product.word.canonical, owner.product.word.output,
                       owner.product.twiddles.output)
    return owner


def adapt_chirp(owner):
    need(owner.closed and owner.current is owner.retained is None
         and all(value == 0 for value in owner.calls.values()), "fresh complete chirp source adaptation")
    for scalar in (owner, owner.kernel, owner.cyclic, owner.cyclic.convolution.product):
        adapt_scalar(scalar)
    return owner
