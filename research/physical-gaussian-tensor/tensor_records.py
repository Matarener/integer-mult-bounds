"""Exact signed-record codecs with bounded width control and a retained fallback."""
from contextlib import ExitStack, contextmanager
from importlib import import_module
import sys
from unittest.mock import patch
from tensor_sources import active
active()
from cardinal_counts import Count
from compact_counts import read_fixed as original_read_fixed, write_fixed as original_write_fixed
import ring_words
import gaussian_convolution
import word_product
from session import borrowed_tape
from words import RIGHT, need

WIDTH_LIMIT = 4096
WIDTH_BITS = 13
original_power_two = ring_words.power_two
original_bit_at = ring_words.bit_at


def bounded_width(width):
    width.rewind()
    value = 0
    try:
        for position in range(WIDTH_BITS):
            bit = width.read()
            if bit == RIGHT:
                return value if value <= WIDTH_LIMIT else None
            if bit not in (0, 1):
                return None
            value |= bit << position
            width.step(1)
        return value if width.read() == RIGHT and value <= WIDTH_LIMIT else None
    finally:
        width.rewind()


def read_fixed(source, width):
    size = bounded_width(width)
    if size is None:
        return original_read_fixed(source, width)
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    try:
        for _ in range(size):
            bit = source.read()
            need(bit in (0, 1), "complete fixed-width binary key")
            result.tape.append(bit)
            source.step(1)
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise


def write_fixed(value, target, width):
    size = bounded_width(width)
    if size is None:
        return original_write_fixed(value, target, width)
    value.rewind()
    try:
        for _ in range(size):
            ended = value.read() == RIGHT
            bit = 0 if ended else value.read()
            need(bit in (0, 1), "fixed-width key digit")
            target.append(bit)
            if not ended:
                value.step(1)
        need(value.read() == RIGHT or value.zero(), "key fits declared width")
    finally:
        value.rewind()


def power_two(amount):
    size = bounded_width(amount)
    if size is None:
        return original_power_two(amount)
    result = Count.literal(0)
    try:
        borrowed_tape(result.tape).clear()
        for _ in range(size):
            result.tape.append(0)
        result.tape.append(1)
        result.tape.append(RIGHT)
        result.rewind()
        return result
    except BaseException:
        result.close()
        raise


def bit_at(value, position):
    index = bounded_width(position)
    if index is None:
        return original_bit_at(value, position)
    value.rewind()
    try:
        for _ in range(index):
            bit = value.read()
            if bit == RIGHT:
                return 0
            need(bit in (0, 1), "bit-window source digit")
            value.step(1)
        bit = value.read()
        if bit == RIGHT:
            return 0
        need(bit in (0, 1), "bit-window digit")
        return bit
    finally:
        value.rewind()


CODEC_BINDINGS = ((ring_words, "read_fixed", original_read_fixed, read_fixed),
                  (ring_words, "write_fixed", original_write_fixed, write_fixed),
                  (gaussian_convolution, "read_fixed", original_read_fixed, read_fixed),
                  (gaussian_convolution, "write_fixed", original_write_fixed, write_fixed),
                  (word_product, "write_fixed", original_write_fixed, write_fixed),
                  (ring_words, "power_two", original_power_two, power_two),
                  (ring_words, "bit_at", original_bit_at, bit_at))


def preload_record_cohort():
    for name in ("expansion_tile", "gaussian_core", "chirp_engine", "tensor_twiddles"):
        import_module(name)


def record_aliases():
    names = ("expansion_records", "expansion_tile_geometry", "gaussian_axis",
             "gaussian_exponentials", "gaussian_interior", "gaussian_page",
             "chirp_kernel", "chirp_odometer", "chirp_plan", "phase_basis", "tensor_twiddles")
    need(all(name in sys.modules for name in names), "preloaded numerical-record alias cohort")
    namespaces = [vars(sys.modules[name]) for name in names]
    module = sys.modules["tensor_twiddles"]
    namespaces.extend((module.SmallTwiddles.run.__globals__, module.SmallPhaseBasis.run.__globals__))
    return tuple((namespace, namespace["power_two"]) for namespace in namespaces)


@contextmanager
def bounded_record_io():
    """Adapt signed records, Gaussian packed slots and complete word returns."""
    from tensor_signed import signed_bindings
    signed = signed_bindings()
    preload_record_cohort()
    aliases = record_aliases()
    need(all(getattr(module, name) is original for module, name, original, _ in CODEC_BINDINGS),
         "one retained numerical-record codec cohort")
    need(all(namespace[key] is original for namespace, key, original, _ in signed),
         "one retained signed-record cohort")
    try:
        with ExitStack() as stack:
            for module, name, _, replacement in CODEC_BINDINGS:
                stack.enter_context(patch.object(module, name, replacement))
            for namespace, key, original, replacement in signed:
                stack.callback(namespace.__setitem__, key, original)
                namespace[key] = replacement
            yield
    finally:
        need(all(getattr(module, name) is original for module, name, original, _ in CODEC_BINDINGS),
             "restore retained numerical-record codecs")
        need(all(namespace["power_two"] is original for namespace, original in aliases),
             "preserve preloaded numerical-record aliases")
        need(all(namespace[key] is original for namespace, key, original, _ in signed),
             "restore retained signed-record cohort")
