"""Execute a complete encoded coordinate router with one shared B1 cohort."""

from router_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits, power_two, read_fixed, shifted
from compact_layout import Layout
from compact_streams import digit_permutation
from encoded import compare, subtract
from records import Tape
from router_metadata import owned
from router_plan import BATCH, CNOT, END, GROUP, Plan, SWAP, UNGROUP, read_opcode
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from sparse_engine import SparseEngine
from stream import Counter
from words import BLANK, LEFT, need


class Router:
    def __init__(self, native, policy="standard"):
        need(policy in ("standard", "fixture-g1-k5"), "compiled router policy")
        self.policy = policy
        self.sparse = SparseEngine(native)
        self.binary = self.sparse.binary
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.current = None
        self.closed = True
        # These observations never select runtime operations.
        self.calls = dict(swaps=0, batches=0, cnots=0, groups=0, ungroups=0)
        self.last_mode = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle_child(self):
        need(self.sparse.closed and not self.sparse.pool.live
             and self.sparse.output.read() == BLANK and self.binary.closed
             and not self.binary.pool.live and self.binary.output.read() == BLANK
             and self.binary.native.closed, "closed shared router child")

    def rearm(self):
        need(self.closed and self.current is None and self.output.read() == BLANK,
             "consume previous router output")
        self.idle_child()
        self.output.step(-1)
        need(self.output.read() in (LEFT, BLANK), "router output origin")
        if self.output.read() == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def accept(self, returned):
        following = self.pool.acquire()
        try:
            append_bits(returned, following)
            following.rewind()
        except BaseException:
            following.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)
        self.current.clear()
        self.current = following

    def swap(self, a, b, width, n, R, C):
        positive(width)
        with owned(Count(a), Count(b)) as (a_end, b_end):
            a_end.add(width)
            b_end.add(width)
            need(compare(a_end, b) <= 0 and compare(b_end, n) <= 0,
                 "disjoint complete block exchange")
            with owned(subtract(n, b_end), subtract(b, a_end)) as (before_bits, gap_bits):
                with owned(power_two(before_bits), power_two(gap_bits), shifted(R, a)) as (before, gap, suffix):
                    before_with_rows = Count.product(C, before)
                    try:
                        self.idle_child()
                        with self.scope.suspended():
                            returned = self.binary.run(
                                borrowed_tape(self.current),
                                *(borrowed_count(v) for v in (width, before_with_rows, gap, suffix)))
                        self.accept(returned)
                    finally:
                        before_with_rows.close()
        self.calls["swaps"] += 1

    def cnot(self, source, target, n, R, C):
        need(compare(source, target) != 0 and compare(source, n) < 0 and compare(target, n) < 0,
             "distinct complete CNOT coordinates")
        plan = Layout(("address",), (n,), R)
        result, current = self.pool.acquire(), None
        try:
            with owned(Count.literal(1)) as (one,):
                with owned(subtract(n, one)) as (last,):
                    with owned(subtract(last, source), subtract(last, target), Counter(C)) as (left_s, left_t, rows):
                        early = compare(left_s, left_t) < 0
                        first, second = (left_s, left_t) if early else (left_t, left_s)
                        mapping = (0, 1, 3, 2) if early else (0, 3, 2, 1)
                        self.current.rewind()
                        while not rows.finished:
                            current = self.pool.acquire()
                            copy_bits(self.current, current, plan.row_bits)
                            current.rewind()
                            current = digit_permutation(current, plan, first, second, mapping, self.pool.acquire)
                            append_bits(current, result)
                            current.clear()
                            current = None
                            rows.decrement()
                        need(self.current.read() == BLANK, "complete CNOT outer packet")
            self.current.clear()
            result.rewind()
            self.current, result = result, None
            self.calls["cnots"] += 1
        finally:
            plan.close()
            if current is not None:
                current.clear()
            if result is not None:
                result.clear()

    def batch(self, pairs, count, plan, R, C):
        self.idle_child()
        with self.scope.suspended():
            returned = self.sparse.run(
                borrowed_tape(self.current),
                tuple(borrowed_count(v) for v in (plan.H, plan.H, plan.Y, plan.H)),
                borrowed_tape(pairs),
                *(borrowed_count(v) for v in (count, plan.y_width, plan.K, plan.G, R, C)))
        self.accept(returned)
        self.calls["batches"] += 1

    def execute(self, plan, original_R, C):
        n, R, grouped = Count(plan.n), Count(original_R), False
        pairs = self.pool.acquire()
        try:
            while True:
                op = read_opcode(plan.program)
                if op == END:
                    need(not grouped and plan.program.read() == BLANK, "complete restored router program")
                    break
                if op == SWAP:
                    with owned(read_fixed(plan.program, plan.width), read_fixed(plan.program, plan.width),
                               read_fixed(plan.program, plan.width)) as (a, b, width):
                        self.swap(a, b, width, n, R, C)
                elif op == CNOT:
                    with owned(read_fixed(plan.program, plan.width), read_fixed(plan.program, plan.width)) as (s, t):
                        self.cnot(s, t, n, R, C)
                elif op == GROUP:
                    need(not grouped and plan.mode == "fast", "group actual prepared suffix once")
                    n.close()
                    n = Count(plan.N)
                    following = shifted(R, plan.ell)
                    R.close()
                    R = following
                    grouped = True
                    self.calls["groups"] += 1
                elif op == UNGROUP:
                    need(grouped, "ungroup the prepared suffix")
                    n.close()
                    R.close()
                    n, R = Count(plan.n), Count(original_R)
                    grouped = False
                    self.calls["ungroups"] += 1
                else:
                    need(op == BATCH and grouped, "batch only in prepared prefix")
                    with owned(read_fixed(plan.program, plan.width)) as (count,):
                        positive(count)
                        with owned(Count.product(count, plan.y_width)) as (extent,):
                            extent.multiply_small(2)
                            copy_bits(plan.program, pairs, extent)
                        pairs.rewind()
                        self.batch(pairs, count, plan, R, C)
                        borrowed_tape(pairs).clear()
        finally:
            n.close()
            R.close()
            pairs.clear()
            plan.program.rewind()

    def run(self, payload, pairs, n, p, k, width, record_bits, outer_rows):
        source, descriptor = borrowed_tape(payload), borrowed_tape(pairs)
        need(source is not self.output and descriptor is not source and descriptor is not self.output,
             "distinct borrowed router payload and descriptor")
        positive(record_bits)
        positive(outer_rows)
        self.rearm()
        plan = layout = rows = None
        source.rewind()
        with sealed_constructors(), self.scope.installed():
            try:
                plan = Plan(n, p, k, width, self.pool.acquire, self.policy)
                plan.compile(descriptor)
                self.last_mode = plan.mode
                layout = Layout(("address",), (n,), record_bits)
                rows = Counter(outer_rows)
                self.current = self.pool.acquire()
                while not rows.finished:
                    copy_bits(source, self.current, layout.row_bits)
                    rows.decrement()
                need(source.read() == BLANK, "complete router outer-row payload")
                self.current.rewind()
                self.execute(plan, record_bits, outer_rows)
                self.idle_child()
                append_bits(self.current, self.output)
            finally:
                source.rewind()
                descriptor.rewind()
                if self.current is not None:
                    self.current.clear()
                    self.current = None
                if rows is not None:
                    rows.close()
                if layout is not None:
                    layout.close()
                if plan is not None:
                    plan.close()
            self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        return self.output
