"""Complete CRT coefficient order <-> compact actual tensor order.

All numerical metadata stays encoded. The full-support field permutation is
executed by the authenticated, unchanged PR3935 FullRouter, never a free oracle.
"""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from records import Tape
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from tensor_router import FullRouter
from words import BLANK, RIGHT, need
from crt_descriptor import compile_descriptor
from crt_offsets import compile_offsets
from crt_padding import padded
from crt_shape import Shape, power_two
from crt_shear import shifted
from crt_streams import copy_rows
from encoded_crt import write_count


def shape_from_plan(plan, factory):
    from tensor_plan import TensorPlan
    need(isinstance(plan, TensorPlan), 'actual PR3935 tensor plan')
    output = index = remaining = None
    try:
        output = factory()
        index = Count.literal(0)
        remaining = Counter(plan.dimensions)
        while not remaining.finished:
            row = plan.axis(index)
            try:
                write_count(row.s, output)
                write_count(row.t, output)
            finally:
                row.close()
            index.increment()
            remaining.decrement()
        output.rewind()
        result, output = output, None
        return result
    finally:
        if output is not None:
            output.clear()
        if remaining is not None:
            remaining.close()
        if index is not None:
            index.close()


def repeated_offsets(source, rows, factory):
    output = counter = None
    source.rewind()
    try:
        output = factory()
        counter = Counter(rows)
        while not counter.finished:
            while source.read() != BLANK:
                symbol = source.read()
                need(symbol in (0, 1, RIGHT), 'complete serialized CRT offset metadata')
                output.append(symbol)
                source.step(1)
            source.rewind()
            counter.decrement()
        output.rewind()
        result, output = output, None
        return result
    finally:
        source.rewind()
        if counter is not None:
            counter.close()
        if output is not None:
            output.clear()


class Converter:
    def __init__(self, router):
        need(isinstance(router, FullRouter), 'actual complete full-support CRT router')
        self.router = router
        self.pool = ScratchPool(192)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.current = None
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.router.idle()
        need(self.router.closed and not self.router.pool.live and self.router.output.read() == BLANK,
             'consumed CRT full-router output')

    def replace(self, output):
        need(output is not self.current, 'distinct owned CRT stage output')
        self.current.clear()
        self.current = output
        self.current.rewind()

    def route(self, shape, p, R, rows, inverse):
        descriptor = width = returned = following = records = None
        try:
            descriptor, width = compile_descriptor(shape, self.pool.acquire, inverse)
            with self.scope.suspended():
                returned = self.router.run(borrowed_tape(self.current), borrowed_tape(descriptor),
                    *(borrowed_count(v) for v in (shape.bits, p, shape.bits, width, R, rows)))
            following = self.pool.acquire()
            records = Count.product(rows, shape.padded_total)
            copy_rows(returned, following, records, R)
            need(returned.read() == BLANK, 'complete CRT full-router return')
            following.rewind()
            self.replace(following)
            following = None
            self.last_counts['global_routes'] += 1
            self.last_counts['router'] = dict(self.router.last_counts)
        finally:
            for count in (width, records):
                if count is not None:
                    count.close()
            for tape in (descriptor, following):
                if tape is not None:
                    tape.clear()
            if returned is not None:
                returned.clear()
                erase_marker(returned)
        self.idle()

    def triangular(self, shape, rows, R, inverse):
        index = remaining = one = None
        try:
            one = Count.literal(1)
            index = Count.literal(0) if inverse else subtract(shape.dimensions, one)
            remaining = Counter(shape.dimensions)
            while not remaining.finished:
                row = shape.axis(index)
                s, t, width, _P, _mu, prior = row
                prefix = offsets = all_offsets = before = suffix_bits = tail_bits = following = None
                try:
                    prefix, offsets = compile_offsets(shape, index, self.pool.acquire)
                    all_offsets = repeated_offsets(offsets, rows, self.pool.acquire)
                    before = Count.product(rows, prefix)
                    after_prefix = subtract(shape.bits, prior)
                    try:
                        tail_bits = subtract(after_prefix, width)
                    finally:
                        after_prefix.close()
                    tail = power_two(tail_bits)
                    try:
                        suffix_bits = Count.product(tail, R)
                    finally:
                        tail.close()
                    following = shifted(self.current, all_offsets, before, s, t, suffix_bits,
                                        self.pool.acquire, inverse)
                    self.replace(following)
                    following = None
                    self.last_counts['triangular_shifts'] += 1
                    remaining.decrement()
                    if not remaining.finished:
                        if inverse:
                            index.increment()
                        else:
                            next_index = subtract(index, one)
                            index.close()
                            index = next_index
                finally:
                    for count in (*row, prefix, before, suffix_bits, tail_bits):
                        if count is not None:
                            count.close()
                    for tape in (offsets, all_offsets, following):
                        if tape is not None:
                            tape.clear()
        finally:
            if remaining is not None:
                remaining.close()
            for count in (index, one):
                if count is not None:
                    count.close()

    def run(self, payload, source_shape, dimensions, precision, record_bits, rows,
            inverse=False, tensor_plan=None):
        need(type(inverse) is bool, 'literal complete CRT direction')
        source = borrowed_tape(payload)
        shape_source = None if source_shape is None else borrowed_tape(source_shape)
        parameters = tuple(borrowed_count(v) for v in (dimensions, precision, record_bits, rows))
        dimensions, p, R, C = parameters
        forbidden = (*self.pool.tapes, self.output, *self.router.pool.tapes, self.router.output,
                     *self.router.router.pool.tapes, self.router.router.output)
        need(source not in forbidden and (shape_source is None or shape_source not in forbidden)
             and source is not shape_source and all(v.tape not in forbidden
                 and v.tape is not source and v.tape is not shape_source for v in parameters),
             'external complete CRT ports')
        need((shape_source is None) == (tensor_plan is not None), 'one CRT shape source contract')
        for count in parameters:
            positive(count)
        need(self.closed and not self.pool.live and self.output.read() == BLANK, 'consume prior CRT output')
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(global_routes=0, triangular_shifts=0, padding_passes=0)
        shape = owned_shape_source = records = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    if tensor_plan is not None:
                        owned_shape_source = shape_from_plan(tensor_plan, self.pool.acquire)
                        shape_source = owned_shape_source
                    shape = Shape(shape_source, dimensions, self.pool.acquire)
                    if tensor_plan is not None:
                        need(compare(shape.bits, tensor_plan.address_bits) == 0
                             and compare(shape.source_total, tensor_plan.source_product) == 0
                             and compare(shape.padded_total, tensor_plan.target_product) == 0,
                             'complete actual tensor shape binding')
                        owned_shape_source.clear()
                        owned_shape_source = None
                    self.current = padded(source, shape, C, R, self.pool.acquire, natural=inverse)
                    self.last_counts['padding_passes'] += 1
                    if inverse:
                        self.triangular(shape, C, R, True)
                        self.route(shape, p, R, C, True)
                    else:
                        self.route(shape, p, R, C, False)
                        self.triangular(shape, C, R, False)
                    following = padded(self.current, shape, C, R, self.pool.acquire, remove=True, natural=not inverse)
                    self.replace(following)
                    self.last_counts['padding_passes'] += 1
                    records = Count.product(C, shape.source_total)
                    copy_rows(self.current, self.output, records, R)
                    need(self.current.read() == BLANK, 'complete compact CRT output')
                    self.idle()
                    succeeded = True
                finally:
                    if records is not None:
                        records.close()
                    if self.current is not None:
                        self.current.clear()
                        self.current = None
                    if owned_shape_source is not None:
                        owned_shape_source.clear()
                    if shape is not None:
                        shape.close()
                    source.rewind()
                    if shape_source is not None and owned_shape_source is None and tensor_plan is None:
                        shape_source.rewind()
                    for count in parameters:
                        count.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output

    def run_plan(self, payload, plan, rows, inverse=False, record_bits=None):
        return self.run(payload, None, plan.dimensions, plan.p,
                        plan.record_bits if record_bits is None else record_bits, rows,
                        inverse=inverse, tensor_plan=plan)
