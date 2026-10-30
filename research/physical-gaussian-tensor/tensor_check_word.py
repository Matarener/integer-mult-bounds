"""Fixed-digit controls, exact leaves and complete recursive/FFT joins."""
from hashlib import sha256
from unittest.mock import patch
from tensor_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from expansion_check_block import packet_bytes
    from expansion_tile import Tile
    from fft_arithmetic import Arithmetic
    from fft_word_engine import FftWord
    from gaussian_core import Core
    from records import Tape
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
    import tensor_word
    from tensor_fixture import finite_chirp
    from tensor_word import (CONTROL_MAX, DIGIT_BITS, DIGIT_MASK, DigitWordProduct,
                             adapt_chirp, adapt_fft_word, digit_product)
    from words import BLANK
    for a in range(256):
        for b in range(256):
            require(digit_product(a, b) == a*b, "all eight-bit pairs through the fixed thirty-two-phase control")
    edges = (0, 1, 2, 255, 256, 65535, 65536, (1 << 31)-1, 1 << 31, DIGIT_MASK)
    for a in edges:
        for b in edges:
            require(digit_product(a, b) == a*b, "full-width digit and carry-boundary control")
    for a, b in ((-1, 0), (0, -1), (DIGIT_MASK+1, 0), (0, DIGIT_MASK+1)):
        try:
            digit_product(a, b)
        except ValueError:
            pass
        else:
            raise ValueError("missing fixed digit-width control")
    for size in (0, 1, 31, 32, 1024, 1025, 2048, 1 << 129):
        with owned(Count.literal(size)) as (width,):
            with no_decode():
                observed = tensor_word.leaf_width(width)
            require(observed == (size if 1 <= size <= 1024 else None) and width.tape.head == 1,
                    "bounded leaf-width probe preserves its origin and fallback boundary")
    for size, bits, malformed in ((1, 1, False), (32, 32, False), (1024, 1024, False),
                                  (1, 4097, False), (1024, 4097, False), (1, 3, True)):
        with owned(Count.literal((1 << bits)-1)) as (value,):
            if malformed:
                value.step(1)
                value.step(1)
                value.tape.write(BLANK)
                value.rewind()
            saved = bytes(value.tape.cells)
            try:
                with no_decode():
                    tensor_word.leaf_fits(value, size)
            except ValueError as error:
                require(str(error) == ("canonical data-word digit" if malformed else
                                      "data magnitude fits declared word width") and (malformed or bits > size),
                        "full leaf digit validation precedes oversized-width rejection")
            else:
                require(not malformed and bits <= size, "bounded leaf admission")
            require(bytes(value.tape.cells) == saved and value.tape.head == 1,
                    "bounded leaf admission preserves borrowed data and origin")
    machine = DigitWordProduct()
    hashes, case_count, recursive = sha256(), 0, 0
    def clear(tape):
        tape.clear()
        erase_marker(tape)
    def restored(word):
        require(word.closed and not word.pool.live and word.output.read() == BLANK
                and all(t.head == 1 and all(v == BLANK for v in t.cells)
                        for t in (*word.pool.tapes, *word.canonical)), "complete adapted word restoration")
    widths = (1, 2, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128, 129, 255, 256, 257, 513, 1024, 1025, 2049)
    for width in widths:
        limit = (1 << width)-1
        cases = [(limit, limit), ((1 << (width-1)) | 1, ((1 << (width//2))+3) & limit)]
        if width in (1, 8, 1024, 2049):
            cases.append((0, limit))
        for a, b in cases:
            with owned(Count.literal(a), Count.literal(b), Count.literal(width)) as parameters:
                saved = [(bytes(v.tape.cells), v.tape.head) for v in parameters]
                before = machine.calls["parks"]
                with no_decode():
                    output = machine.run(*parameters)
                raw = packet_bytes(output)
                actual = sum(bit << index for index, bit in enumerate(raw))
                require(actual == a*b and len(raw) == 2*width, "complete exact word including partial digits and all carries")
                require(saved == [(bytes(v.tape.cells), v.tape.head) for v in parameters], "adapted word preserves borrowed values and heads")
                recursive += machine.calls["parks"] > before
                hashes.update(raw)
                case_count += 1
                clear(output)
                restored(machine)
    require(recursive > 0 and machine.digit_counts["max_control"] == CONTROL_MAX,
            "actual inherited recursive continuation and worst sixty-four-bit carry")
    require(hashes.hexdigest() == "7e5e413f9988cb1fc178b6fa181b8d7a7ec4f776588f8fc1e55861b27fc616ce",
            "unchanged complete word fixtures after the fixed-digit refinement")
    controls = ["bounded_leaf_width", "saturating_leaf_fits", "late_leaf_digit_after_overflow"]
    def reject(call, fragment):
        try:
            with no_decode():
                call()
        except ValueError as error:
            require(fragment in str(error), "specific digit-word rejection: " + str(error))
        else:
            raise ValueError("missing digit-word rejection")
    for a, b, width, label, fragment in ((0, 1, 0, "zero_width", "positive"),
                                       (256, 0, 8, "wide_first_with_zero_second", "width"),
                                       (0, 256, 8, "wide_second_with_zero_first", "width")):
        with owned(Count.literal(a), Count.literal(b), Count.literal(width)) as parameters:
            reject(lambda: machine.run(*parameters), fragment)
        restored(machine)
        controls.append(label)
    with owned(Count.literal((1 << 128)-1), Count.literal((1 << 128)-1), Count.literal(128)) as parameters:
        original, updates = tensor_word.digit_product, 0
        def allocate(a, b):
            nonlocal updates
            value = original(a, b)
            updates += 1
            if updates == 7:
                Tape()
            return value
        with patch.object(tensor_word, "digit_product", allocate):
            reject(lambda: machine.run(*parameters), "physical Tape allocation inside")
        restored(machine)
        controls.append("late_leaf_allocation")
        with no_decode():
            output = machine.run(*parameters)
        raw = packet_bytes(output)
        reject(lambda: machine.run(*parameters), "consume prior word-product output")
        require(packet_bytes(output) == raw, "protected digit-word return survives rejected reuse")
        controls.append("protected_return")
        clear(output)
        restored(machine)
    pool = ScratchPool(32)
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
    arithmetic = Arithmetic(machine, scope)
    with owned(Count.literal((1 << 71)+3), Count.literal((1 << 63)+7), Count.literal(80)) as parameters:
        a, b, width = parameters
        for tape in pool.tapes:
            initialize_marker(tape)
        with sealed_constructors(), scope.installed():
            with no_decode():
                result = arithmetic.multiply(Signed(a, True), Signed(b), width)
            with owned(result):
                require(result.negative and decode(result.magnitude) == ((1 << 71)+3)*((1 << 63)+7),
                        "retained signed Arithmetic consumes the actual digit-word owner")
            pool.empty()
        for tape in pool.tapes:
            erase_marker(tape)
    restored(machine)
    tile, core, chirp = Tile(), Core(), finite_chirp()
    adapt_fft_word(tile.word)
    adapt_fft_word(core.word)
    adapt_chirp(chirp)
    require(tile.word is tile.block.word is tile.block.convolution.word
            and core.word is core.interior.word is core.boundary.word is core.interior.convolution.word,
            "adaptation preserves scalar/convolution FFT-word root aliases")
    for fft_word in (tile.word, core.word):
        require(type(fft_word.base) is DigitWordProduct and type(fft_word.product.word) is DigitWordProduct
                and fft_word.product.arithmetic.word is fft_word.product.word,
                "actual digit-word children and retained arithmetic links")
        expected = (*fft_word.base.canonical, fft_word.base.output, fft_word.product.output,
                    *fft_word.product.word.canonical, fft_word.product.word.output, fft_word.product.twiddles.output)
        require(fft_word.canonical == expected, "FFT-word canonical inventory names the new actual children")
    for owner in (chirp, chirp.kernel, chirp.cyclic, chirp.cyclic.convolution.product):
        require(type(owner.word) is DigitWordProduct and owner.arithmetic.word is owner.word,
                "complete chirp arithmetic points to its actual adapted owner")
    # Exercise the real FFT branch with the adapted exact scalar leaves.
    fft_word = adapt_fft_word(FftWord(base_bits=16))
    with owned(Count.literal((1 << 17)-13), Count.literal((1 << 16)+19), Count.literal(17)) as parameters:
        with no_decode():
            output = fft_word.run(*parameters)
        raw = packet_bytes(output)
        require(sum(bit << i for i, bit in enumerate(raw)) == ((1 << 17)-13)*((1 << 16)+19)
                and len(raw) == 34 and fft_word.calls == dict(base=0, fft=1),
                "complete actual FFT-word return with fixed-digit scalar leaves")
        fft_hash = sha256(raw).hexdigest()
        clear(output)
        fft_word.idle()
    return {"byte_control_pairs": 65536, "wide_control_pairs": len(edges)**2,
            "digit_bits": DIGIT_BITS, "digit_rejections": 4, "physical_products": case_count,
            "widths": list(widths), "recursive_products": recursive, "product_sequence_sha256": hashes.hexdigest(),
            "digit_counts": machine.digit_counts, "controls": controls, "fft_output_sha256": fft_hash,
            "scope": "fixed thirty-two-bit digits, retained recursive continuation and one actual FFT-word join; full tensor remains separate"}
