"""Package-specific exact integers for complete signed-word and recursion checks."""

from hashlib import sha256
from unittest.mock import patch
from ring_sources import require


def decode(value):
    from words import RIGHT
    result, position = 0, 0
    value.rewind()
    try:
        while value.read() != RIGHT:
            result |= value.read() << position
            position += 1
            value.step(1)
        return result
    finally:
        value.rewind()


def word_bits(value, width):
    return bytes((value >> bit) & 1 for bit in range(width))


def tape(bits):
    from records import Tape
    result = Tape()
    for bit in bits:
        result.append(bit)
    result.rewind()
    return result


def body(value):
    from check_support import bits
    return bits(value)


def blank_owner(machine):
    from words import BLANK
    require(machine.closed and not machine.pool.live, "closed scalar product owner")
    for item in (*machine.canonical, *machine.pool.tapes):
        require(item.head == 1 and all(bit == BLANK for bit in item.cells),
                "word product restores bodies and origin heads")


def product_packet(machine, a, b, width, consume=True):
    from cardinal_counts import Count
    from check_support import no_decode
    from session import erase_marker
    inputs = tuple(Count.literal(v) for v in (a, b, width))
    before = tuple((bytes(value.tape.cells), value.tape.head) for value in inputs)
    calls = dict(machine.calls)
    try:
        with no_decode():
            returned = machine.run(*inputs)
        actual = body(returned)
        require(actual == word_bits(a*b, 2*width), "physical unsigned word product")
        require(before == tuple((bytes(value.tape.cells), value.tape.head) for value in inputs),
                "word product preserves borrowed numerical ports")
        blank_owner(machine)
        depth, n = 0, width
        while n > machine.leaf_bits:
            n = (n+1)//2
            depth += 1
        nodes = (3**(depth+1)-1)//2
        delta = {key: machine.calls[key]-calls[key] for key in calls}
        require(delta == dict(nodes=nodes, leaves=3**depth, parks=nodes-1, restores=nodes-1),
                "complete three-child recursion and physical restoration")
        if consume:
            returned.clear()
            erase_marker(returned)
        return {"width": width, "nodes": nodes, "leaves": 3**depth,
                "sha256": sha256(actual).hexdigest(), "pool_peak": machine.pool.peak}
    finally:
        for value in inputs:
            value.close()


def signed_codec():
    from cardinal_counts import Count
    from ring_words import Signed, add, difference, nearest, read_signed, scaled, truncate, write_signed
    checked = 0
    for width in (2, 3, 5, 8, 17):
        limit = 1 << (width-1)
        for value in (-limit, -limit+1, -1, 0, 1, limit-1):
            source = tape(word_bits(value, width))
            w = Count.literal(width)
            actual = read_signed(source, w)
            destination = tape(())
            try:
                require((-1 if actual.negative else 1)*decode(actual.magnitude) == value,
                        "signed magnitude parser including minimum")
                write_signed(actual, destination, w)
                require(body(destination) == word_bits(value, width), "signed word round trip")
                checked += 1
                for shift in (0, 1, width, width+2):
                    amount = Count.literal(shift)
                    moved = scaled(actual, amount)
                    quotient = truncate(actual, amount)
                    try:
                        require((-1 if moved.negative else 1)*decode(moved.magnitude) == value*(1 << shift),
                                "linear signed left shift")
                        expected = (abs(value) >> shift)*(-1 if value < 0 else 1)
                        require((-1 if quotient.negative else 1)*decode(quotient.magnitude) == expected,
                                "signed truncation toward zero")
                        if shift:
                            rounded = nearest(actual, amount)
                            try:
                                expected = ((abs(value)+(1 << (shift-1))) >> shift)*(-1 if value < 0 else 1)
                                require((-1 if rounded.negative else 1)*decode(rounded.magnitude) == expected,
                                        "signed nearest integer including tie convention")
                            finally:
                                rounded.close()
                    finally:
                        moved.close()
                        quotient.close()
                        amount.close()
            finally:
                actual.close()
                w.close()
    for a in (-17, -1, 0, 1, 19):
        for b in (-11, 0, 13):
            left = Signed(Count.literal(abs(a)), a < 0)
            right = Signed(Count.literal(abs(b)), b < 0)
            plus, minus = add(left, right), difference(left, right)
            try:
                require((-1 if plus.negative else 1)*decode(plus.magnitude) == a+b
                        and (-1 if minus.negative else 1)*decode(minus.magnitude) == a-b,
                        "exact signed word addition and subtraction")
                checked += 1
            finally:
                for value in (left, right, plus, minus):
                    value.close()
    return checked


def run():
    from cardinal_counts import Count
    from session import erase_marker
    from word_product import WordProduct
    from words import BLANK
    codec = signed_codec()
    machine = WordProduct()
    records = []
    for width in (1, 2, 3, 8, 16, 17, 31, 32, 33, 64, 65):
        maximum = (1 << width)-1
        pairs = ((0, maximum), (maximum, maximum), (maximum//3, maximum-maximum//5))
        for a, b in pairs:
            records.append(product_packet(machine, a, b, width))
    records.append(product_packet(machine, (1 << 257)-19, (1 << 256)+123, 257))
    product_packet(machine, 9, 7, 4, consume=False)
    protected = body(machine.output)
    counts = tuple(Count.literal(v) for v in (1, 1, 2))
    controls = []
    try:
        try:
            machine.run(*counts)
        except ValueError as error:
            require("consume prior word-product output" in str(error), "protected word output boundary")
            require(body(machine.output) == protected, "protected word output stays intact")
            controls.append("protected_output")
        else:
            raise ValueError("missing protected word output rejection")
    finally:
        for value in counts:
            value.close()
        machine.output.clear()
        erase_marker(machine.output)
    for a, b, width in ((1, 1, 0), (256, 1, 8)):
        counts = tuple(Count.literal(v) for v in (a, b, width))
        try:
            try:
                machine.run(*counts)
            except ValueError:
                controls.append("invalid_width" if width == 0 else "oversized_magnitude")
            else:
                raise ValueError("missing word input-width rejection")
            blank_owner(machine)
            require(machine.output.read() == BLANK, "invalid word call has empty return")
        finally:
            for value in counts:
                value.close()
    original_phase = WordProduct.phase

    def wrong_middle(self, phase, negative=False):
        original_phase(self, phase, not negative if phase == 3 else negative)

    mutant = WordProduct(2)
    with patch.object(WordProduct, "phase", wrong_middle):
        try:
            product_packet(mutant, 9, 7, 4)
        except ValueError as error:
            require("physical unsigned word product" in str(error), "signed-difference mutant reaches oracle")
            controls.append("wrong_middle_sign")
        else:
            raise ValueError("missing signed-difference mutation")
        finally:
            mutant.output.clear()
            erase_marker(mutant.output)
    return {"signed_cases": codec, "unsigned_packets": len(records)+1, "max_width": 257,
            "largest": records[-1], "controls": controls}
