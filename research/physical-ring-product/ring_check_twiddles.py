"""Independent rational interval checks for the physical twiddle producer."""

from fractions import Fraction
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
from ring_sources import require


def reference():
    path = Path(__file__).resolve().parents[1] / "certified-gaussian-recovery/intervals.py"
    require(sha256(path.read_bytes()).hexdigest()
            == "159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df",
            "pinned Mason Hale interval reference")
    name = "ring_mason_interval_reference"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from ring_check_words import body, decode
    from ring_words import read_signed
    from session import erase_marker
    from twiddle_setup import Twiddles
    from words import BLANK
    oracle = reference()
    owner = Twiddles()
    checked = 0
    receipts = []
    conjugates = {}
    for Q, length, opposite in ((16, 2, False), (16, 4, False), (16, 8, False),
                                 (16, 8, True), (21, 8, False), (17, 16, False)):
        precision, stage, width = (Count.literal(value) for value in (Q, length, Q+2))
        saved = tuple((bytes(v.tape.cells), v.tape.head) for v in (precision, stage))
        try:
            with no_decode():
                output = owner.run(precision, stage, opposite)
            packet = body(output)
            values = []
            for index in range(length//2):
                actual = []
                for _ in range(2):
                    value = read_signed(output, width)
                    try:
                        actual.append((-1 if value.negative else 1)*decode(value.magnitude))
                    finally:
                        value.close()
                reference_value = oracle.root_of_unity(index if opposite else -index, length, Q+24)
                phase = (index if opposite else -index) % length
                exact_quarter = (4*phase) % length == 0
                if exact_quarter:
                    scale = 1 << Q
                    exact = ((scale, 0), (0, scale), (-scale, 0), (0, -scale))[(4*phase)//length]
                    require(tuple(actual) == exact, "exact rational quarter-turn twiddle")
                errors = []
                for number, interval in zip(actual, reference_value):
                    x = Fraction(number, 1 << Q)
                    lo, hi = Fraction(interval.lo, interval.scale), Fraction(interval.hi, interval.scale)
                    require(exact_quarter or (number == 0) or (0 < x <= lo) or (hi <= x < 0),
                            "physical twiddle component moves inward")
                    errors.append(max(abs(x-lo), abs(x-hi)))
                require(actual[0]**2+actual[1]**2 <= 1 << (2*Q), "exact twiddle disk inequality")
                require(sum(error*error for error in errors) < Fraction(4, 1 << (2*Q)),
                        "certified physical complex twiddle error")
                values.append(tuple(actual))
                checked += 1
            require(output.read() == BLANK and owner.closed and not owner.pool.live,
                    "complete closed twiddle producer")
            require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in (precision, stage)),
                    "twiddle producer preserves numerical ports")
            require(all(t.head == 1 and all(bit == BLANK for bit in t.cells) for t in owner.pool.tapes),
                    "twiddle scratch erasure and origins")
            if Q == 16 and length == 8:
                conjugates[opposite] = values
            receipts.append({"Q": Q, "length": length, "opposite": opposite,
                             "sha256": sha256(packet).hexdigest(), "pool_peak": owner.pool.peak})
            output.clear()
            erase_marker(output)
        finally:
            precision.close()
            stage.close()
            width.close()
    require(conjugates[True] == [(real, -imaginary) for real, imaginary in conjugates[False]],
            "exact inverse twiddle conjugation")
    controls = []
    for Q, length, message in ((15, 8, "precision"), (16, 6, "dyadic"),
                               (16, 1, "nontrivial"), (16, 1 << 17, "address width")):
        precision, stage = Count.literal(Q), Count.literal(length)
        try:
            try:
                owner.run(precision, stage)
            except ValueError as error:
                require(message in str(error), "intended twiddle admission failure")
                controls.append([Q, length])
            else:
                raise ValueError("missing twiddle admission failure")
            require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                    "twiddle rejection restores owned work")
        finally:
            precision.close()
            stage.close()
    return {"twiddles": checked, "packets": receipts, "rejections": controls}
