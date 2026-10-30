"""Count literal tape operations and keep parking-table traffic separate."""

from contextlib import contextmanager
from unittest.mock import patch

from records import Tape


@contextmanager
def measured(engine):
    counts = {"reads": 0, "writes": 0, "moves": 0}
    read, write, step = Tape.read, Tape.write, Tape.step
    parking = engine.runtime.numerical
    before_codec, before_machine = (
        dict(parking.codec_counts),
        dict(parking.machine.counts),
    )

    def counted_read(tape):
        counts["reads"] += 1
        return read(tape)

    def counted_write(tape, value):
        counts["writes"] += 1
        return write(tape, value)

    def counted_step(tape, direction):
        counts["moves"] += abs(direction)
        return step(tape, direction)

    result = {"source_tapes": counts}
    with (
        patch.object(Tape, "read", counted_read),
        patch.object(Tape, "write", counted_write),
        patch.object(Tape, "step", counted_step),
    ):
        yield result
    result["parking_codec"] = {
        key: parking.codec_counts[key] - value for key, value in before_codec.items()
    }
    result["parking_table"] = {
        key: parking.machine.counts[key] - value
        for key, value in before_machine.items()
    }
    result["total_tape_operations"] = {
        key: counts[key] + result["parking_codec"][key] + result["parking_table"][key]
        for key in ("reads", "writes", "moves")
    }
