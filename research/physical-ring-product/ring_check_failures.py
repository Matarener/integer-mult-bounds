"""Boundary rejections and physically executed normalized-product mutants."""

from unittest.mock import patch
from ring_sources import require


def chain(error):
    result = []
    while error is not None:
        result.append(str(error))
        error = error.__context__
    return " | ".join(result)


def run():
    from cardinal_counts import Count
    from ring_check_product import packet
    from ring_check_words import body, tape
    from product_plan import ProductPlan
    from records import Tape
    from ring_engine import RingProduct
    from session import erase_marker
    from twiddle_setup import Twiddles
    from word_product import WordProduct
    from words import BLANK
    owner = RingProduct()
    controls = []
    # Header and extent errors precede any FFT/data multiplication.
    for name, parameters, left_bits, right_bits, message in (
        ("zero_dimension", (0, 2, 1, 1), 32, 32, "positive cardinality"),
        ("zero_degree_log", (1, 2, 0, 1), 32, 32, "positive cardinality"),
        ("degree_reaches_precision", (1, 2, 2, 1), 32, 32, "polynomial degree"),
        ("short_left", (1, 2, 1, 1), 31, 32, "complete opaque binary payload"),
        ("extra_right", (1, 2, 1, 1), 32, 33, "complete normalized-product input packet"),
    ):
        inputs = tape([0]*left_bits), tape([0]*right_bits)
        counts = tuple(Count.literal(v) for v in parameters)
        try:
            try:
                owner.run(*inputs, *counts)
            except ValueError as error:
                require(message in chain(error), "intended product boundary rejection: " + name)
                controls.append(name)
            else:
                raise ValueError("missing normalized-product rejection: " + name)
            require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                    "pre-callee product failure restores owner")
        finally:
            for value in counts:
                value.close()
    counts = tuple(Count.literal(v) for v in (1, 2, 1, 1))
    shared = tape([0]*32)
    try:
        try:
            owner.run(shared, shared, *counts)
        except ValueError as error:
            require("distinct borrowed" in str(error), "packet-alias rejection")
            controls.append("aliased_packets")
        else:
            raise ValueError("missing product packet-alias rejection")
    finally:
        for value in counts:
            value.close()

    owner, receipt, _ = packet(1, 2, 1, owner=owner, consume=False,
        first=[(1, 1), (-2, 2), (3, 0), (0, -3)],
        second=[(2, -1), (1, 3), (-1, 1), (2, 0)])
    held = body(owner.output)
    counts = tuple(Count.literal(v) for v in (1, 2, 1, 1))
    try:
        try:
            owner.run(tape([0]*32), tape([0]*32), *counts)
        except ValueError as error:
            require("consume prior normalized-product output" in str(error)
                    and body(owner.output) == held, "protected product return stays intact")
            controls.append("protected_output")
        else:
            raise ValueError("missing protected product return rejection")
    finally:
        for value in counts:
            value.close()
        owner.output.clear()
        erase_marker(owner.output)

    values = [(8, 0)]*8
    original_twiddles = Twiddles.run

    def wrong_direction(self, precision, length, opposite=False):
        return original_twiddles(self, precision, length, False)

    with patch.object(Twiddles, "run", wrong_direction):
        try:
            packet(1, 3, 2, first=values, second=values)
        except ValueError as error:
            require("zero final ordinary-convolution coefficient" in chain(error),
                    "wrong inverse direction reaches exact-recovery guard")
            controls.append("wrong_inverse_twiddle")
        else:
            raise ValueError("missing inverse-twiddle mutation")

    class WrongRecovery(ProductPlan):
        def compile(self):
            super().compile()
            self.recovery_shift.increment()

    with patch("ring_engine.ProductPlan", WrongRecovery):
        try:
            packet(1, 3, 2, first=values, second=values)
        except ValueError as error:
            require("exact negacyclic oracle" in str(error), "wrong recovery scale reaches oracle")
            controls.append("wrong_recovery_shift")
        else:
            raise ValueError("missing recovery-scale mutation")
    with patch("ring_engine.difference", lambda lower, _upper: lower.copy()):
        try:
            packet(1, 3, 2, first=values, second=values)
        except ValueError as error:
            require("exact negacyclic oracle" in str(error), "omitted wrapping reaches oracle")
            controls.append("omitted_negacyclic_subtraction")
        else:
            raise ValueError("missing negacyclic-wrap mutation")
    original_enter = WordProduct.enter

    def allocate_during_data(self):
        Tape()
        return original_enter(self)

    with patch.object(WordProduct, "enter", allocate_during_data):
        try:
            packet(1, 2, 1)
        except ValueError as error:
            require("compile" in chain(error).lower() or "allocation" in chain(error).lower(),
                    "new physical tape mutation reaches allocation guard")
            controls.append("dynamic_physical_tape")
        else:
            raise ValueError("missing physical-allocation guard")
    return {"controls": controls, "positive_after_rejections": receipt}
