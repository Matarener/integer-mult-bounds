"""Malformed boundaries and executed phase-direction/carry fault controls."""
from unittest.mock import patch
from chirp_sources import require


def run():
    from cardinal_counts import Count
    from check_composed import encode, fixture
    from chirp_check_kernel import run as positive_kernel
    from chirp_engine import Chirp
    from chirp_fixture import compiled_setup
    from convolution_engine import Convolution
    from cyclic_engine import Cyclic
    from fourier_engine import Fourier
    from ring_check_words import tape, word_bits
    from twiddle_setup import TwiddlePlan
    from words import BLANK
    owner = Chirp(Cyclic(Convolution(Fourier(fixture()[0]))))
    source = word_bits(1, 2)+word_bits(3, 2)
    payload = encode([(0, 0)]*8, 18)
    rejected = []
    for name, source_bits, flags, parameters, data, message in (
        ("short_precision", source, (0,), (1, 2, 15, 1), payload, "precision and degree"),
        ("degree_reaches_precision", source, (0,), (1, 16, 16, 1), payload, "precision and degree"),
        ("missing_norm_margin", source, (1, 1), (2, 2, 16, 1), payload, "at least thirteen"),
        ("zero_rows", source, (0,), (1, 2, 16, 0), payload, "positive cardinality"),
        ("even_source", word_bits(1, 2)+word_bits(2, 2), (0,), (1, 2, 16, 1), payload, "odd positive"),
        ("oversized_source", word_bits(3, 2)+word_bits(3, 2), (0,), (1, 2, 16, 1), payload, "odd positive"),
        ("short_source", source[:-1], (0,), (1, 2, 16, 1), payload, "complete chirp source packet"),
        ("extra_source", source+b"\x00", (0,), (1, 2, 16, 1), payload, "exact chirp source packet extent"),
        ("short_payload", source, (0,), (1, 2, 16, 1), payload[:-1], "complete chirp payload"),
        ("extra_payload", source, (0,), (1, 2, 16, 1), payload+b"\x00", "exact chirp payload extent"),
    ):
        counts = tuple(Count.literal(v) for v in parameters)
        try:
            try:
                owner.run(tape(data), tape(source_bits), tape(flags), *counts)
            except ValueError as error:
                require(message in str(error), "intended chirp boundary failure: " + name + ": " + str(error))
                rejected.append(name)
            else:
                raise ValueError("missing chirp boundary rejection: " + name)
            require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                    "ordinary rejection restores complete chirp owner")
            owner.idle()
        finally:
            for value in counts:
                value.close()
    original = TwiddlePlan.value

    def conjugated(plan, index):
        real, imaginary = original(plan, index)
        try:
            return real, imaginary.negated()
        finally:
            imaginary.close()

    for name, target, replacement in (
        ("wrong_phase_orientation", "twiddle_setup.TwiddlePlan.value", conjugated),
        ("omitted_carry_subtraction", "chirp_odometer.modular_subtract", lambda left, _right, _mod: Count(left)),
    ):
        with patch(target, replacement):
            try:
                positive_kernel()
            except ValueError as error:
                require("eighth-root oracle" in str(error), "physical phase mutant reaches exact comparison")
                rejected.append(name)
            else:
                raise ValueError("missing physical phase mutant rejection")
    with compiled_setup():
        import composed_plan
        value = Count.literal(19)
        try:
            try:
                composed_plan.floor_power(value, 997, 1000)
            except ValueError as error:
                require("outside the certified" in str(error), "compiled setup scope rejection")
                rejected.append("uncertified_setup_argument")
            else:
                raise ValueError("missing compiled setup scope rejection")
        finally:
            value.close()
    positive = positive_kernel(owner.kernel)
    owner.idle()
    return {"controls": rejected, "positive_after_rejections": positive}
