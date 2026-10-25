"""Run one variable-pair sparse XOR batch through the retained physical B1."""

from sparse_sources import active, require
active()
from compact_counts import append_bits, copy_bits
from compact_engine import CompactEngine
from compact_layout import Layout
from compact_streams import repair, rotate
from cardinal_counts import positive
from session import borrowed_tape, erase_marker, sealed_constructors
from sparse_control import SparseControl
from stream import Counter
from words import BLANK, need


class SparseEngine(CompactEngine):
    def __init__(self, native):
        state = active()
        require(isinstance(native, state.ordinary.Ordinary)
                and native.profile == state.encoded.Profile(numerator=1, denominator=577),
                "retuned native from the authenticated cohort")
        super().__init__(("u", "t", "y", "b"), "y", "y", True, native)

    def complete_row(self, source, plan, control):
        current = source
        try:
            for operation in control.operations:
                if operation[0] == "swap":
                    following = self.swap(current, plan, *operation[1:])
                else:
                    following = rotate(current, plan, control, operation, self.pool.acquire)
                    self.calls["rotations"] += 1
                current = following
            current = repair(current, plan, control, self.pool.acquire)
            result, current = current, None
            return result
        finally:
            if current is not None:
                current.clear()

    def run(self, payload, widths, pairs, pair_count, position_bits, K, G, record_bits, outer_rows):
        source, pairs = borrowed_tape(payload), borrowed_tape(pairs)
        need(source is not self.output and pairs is not source and pairs is not self.output,
             "distinct borrowed sparse payload and descriptor")
        positive(outer_rows)
        self.rearm()
        plan = rows = current = None
        source.rewind()
        with sealed_constructors(), self.scope.installed():
            try:
                plan = Layout(self.names, widths, record_bits)
                control = SparseControl(pairs, pair_count, position_bits, K, G)
                control.validate(plan)
                rows = Counter(outer_rows)
                while not rows.finished:
                    current = self.pool.acquire()
                    copy_bits(source, current, plan.row_bits)
                    current.rewind()
                    current = self.complete_row(current, plan, control)
                    append_bits(current, self.output)
                    current.clear()
                    current = None
                    rows.decrement()
                    self.calls["rows"] += 1
                need(source.read() == BLANK, "complete sparse outer-row packet")
            finally:
                source.rewind()
                pairs.rewind()
                if current is not None:
                    current.clear()
                if rows is not None:
                    rows.close()
                if plan is not None:
                    plan.close()
            self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        return self.output
