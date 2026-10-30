"""Complete physical Gaussian chirp middle map in natural tensor order."""

from chirp_sources import active
active()
from chirp_kernel import ChirpKernel
from chirp_packets import validate
from chirp_plan import ChirpPlan
from compact_counts import append_bits
from cyclic_engine import Cyclic
from fft_arithmetic import Arithmetic
from phase_streams import paired
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from word_product import WordProduct
from words import BLANK, need


class Chirp:
    def __init__(self, cyclic=None):
        self.cyclic = Cyclic() if cyclic is None else cyclic
        need(isinstance(self.cyclic, Cyclic), "authenticated complete cyclic owner")
        self.kernel, self.word = ChirpKernel(), WordProduct()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.retained = self.current = None
        self.closed = True
        self.calls = dict(kernels=0, endpoints=0, cyclic=0)
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.cyclic.idle()
        self.kernel.idle()
        need(self.cyclic.closed and not self.cyclic.pool.live and self.cyclic.output.read() == BLANK
             and self.kernel.closed and not self.kernel.pool.live and self.kernel.output.read() == BLANK
             and self.kernel.odometer.phase is None
             and self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK,
             "consumed complete chirp children")

    def accept(self, returned):
        result = self.pool.acquire()
        try:
            append_bits(returned, result)
            result.rewind()
            return result
        except BaseException:
            result.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)

    def run(self, payload, sources, flags, axes, ell, precision, rows):
        payload, sources, flags = (borrowed_tape(v) for v in (payload, sources, flags))
        need(len({id(payload), id(sources), id(flags)}) == 3
             and all(v is not self.output for v in (payload, sources, flags)),
             "distinct borrowed chirp-middle ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK
             and self.retained is self.current is None, "consume prior chirp-middle output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = ChirpPlan(flags, axes, ell, precision, rows)
                    plan.compile()
                    validate(payload, plan.packet_bits, "chirp payload")
                    with self.scope.suspended():
                        returned = self.kernel.run(borrowed_tape(sources), borrowed_tape(flags),
                            *(borrowed_count(v) for v in (axes, ell, precision, rows)))
                    self.retained = self.accept(returned)
                    self.calls["kernels"] += 1
                    self.current = paired(self.retained, payload, plan, self.pool,
                                          self.arithmetic, conjugate=True)
                    self.calls["endpoints"] += 1
                    self.idle()
                    with self.scope.suspended():
                        returned = self.cyclic.run(borrowed_tape(self.retained), borrowed_tape(self.current),
                            borrowed_tape(flags), *(borrowed_count(v) for v in (axes, ell, precision, rows)))
                    following = self.accept(returned)
                    self.current.clear()
                    self.current = following
                    self.calls["cyclic"] += 1
                    following = paired(self.retained, self.current, plan, self.pool,
                                       self.arithmetic, conjugate=True)
                    self.current.clear()
                    self.current = following
                    self.calls["endpoints"] += 1
                    self.idle()
                    append_bits(self.current, self.output)
                    succeeded = True
                finally:
                    for value in (payload, sources, flags, axes, ell, precision, rows):
                        value.rewind()
                    for value in (self.retained, self.current):
                        if value is not None:
                            value.clear()
                    self.retained = self.current = None
                    if plan is not None:
                        plan.close()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
