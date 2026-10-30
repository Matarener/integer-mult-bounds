"""Bounded signed records with direct two's-complement tape conversion."""
from importlib import import_module
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from ring_words import Signed, read_signed as original_read_signed, write_signed as original_write_signed
from session import borrowed_tape
from tensor_records import bounded_width
from words import RIGHT, need


def read_signed(source, width):
    positive(width)
    if borrowed_tape(source) is borrowed_tape(width.tape):
        return original_read_signed(source, width)
    size = bounded_width(width)
    if size is None:
        return original_read_signed(source, width)
    raw = None
    try:
        raw = Count.literal(0)
        borrowed_tape(raw.tape).clear()
        sign = 0
        for _ in range(size):
            sign = source.read()
            need(sign in (0, 1), "complete fixed-width binary key")
            raw.tape.append(sign)
            source.step(1)
        raw.tape.append(RIGHT)
        raw.rewind()
        if sign:
            carry = 1
            for _ in range(size):
                value = 1-raw.read()+carry
                raw.tape.write(value & 1)
                carry = value >> 1
                raw.step(1)
            need(carry == 0 and raw.read() == RIGHT, "complete negative signed record")
        raw.normalize()
        result = Signed(raw, bool(sign))
        raw = None
        return result
    finally:
        if raw is not None:
            raw.close()


def write_signed(value, destination, width):
    positive(width)
    magnitude = value.magnitude
    if any(borrowed_tape(destination) is tape for tape in
           (borrowed_tape(magnitude.tape), borrowed_tape(width.tape))):
        return original_write_signed(value, destination, width)
    size = bounded_width(width)
    if size is None:
        return original_write_signed(value, destination, width)
    magnitude.rewind()
    try:
        lower_nonzero, high = False, 0
        for position in range(size):
            bit = magnitude.read()
            if bit == RIGHT:
                break
            need(bit in (0, 1), "binary comparison digits")
            if position == size-1:
                high = bit
            else:
                lower_nonzero = lower_nonzero or bit == 1
            magnitude.step(1)
        need(magnitude.read() == RIGHT and (high == 0 or value.negative and not lower_nonzero),
             "signed data-word headroom")
        magnitude.rewind()
        carry = 1
        for _ in range(size):
            ended = magnitude.read() == RIGHT
            bit = 0 if ended else magnitude.read()
            need(bit in (0, 1), "fixed-width key digit")
            if value.negative:
                current = 1-bit+carry
                destination.append(current & 1)
                carry = current >> 1
            else:
                destination.append(bit)
            if not ended:
                magnitude.step(1)
        need(magnitude.read() == RIGHT, "complete signed magnitude")
    finally:
        magnitude.rewind()


READ_MODULES = ("ring_words", "chirp_kernel", "expansion_block", "expansion_prepare",
                "expansion_tile", "fft_word_codec", "gaussian_boundary", "gaussian_convolution",
                "gaussian_core", "gaussian_interior", "phase_streams", "ring_engine", "tensor_engine")
WRITE_MODULES = ("ring_words", "chirp_kernel", "expansion_block", "expansion_prepare",
                 "gaussian_boundary", "gaussian_convolution", "gaussian_core", "gaussian_interior",
                 "gaussian_window", "phase_basis", "phase_streams", "ring_engine", "tensor_engine",
                 "twiddle_setup")


def signed_bindings():
    import_module("tensor_engine")
    result = []
    for names, key, original, replacement in (
        (READ_MODULES, "read_signed", original_read_signed, read_signed),
        (WRITE_MODULES, "write_signed", original_write_signed, write_signed),
    ):
        for name in names:
            result.append((vars(import_module(name)), key, original, replacement))
    module = import_module("tensor_twiddles")
    for function in (module.SmallTwiddles.run, module.SmallPhaseBasis.run):
        result.append((function.__globals__, "write_signed", original_write_signed, write_signed))
    return tuple(result)
