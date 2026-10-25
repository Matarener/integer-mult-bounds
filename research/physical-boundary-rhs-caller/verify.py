"""Source-bound actual caller composition and independent Fraction oracle."""
import argparse
from contextlib import contextmanager
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'source bytes: '+row['path'])


def case(length, block_size):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_core import Core
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed
    from router_metadata import owned
    from session import initialize_marker, erase_marker, sealed_constructors, borrowed_tape
    from words import BLANK
    import boundary_pages
    from fixture import fixture
    from caller import first_pass_pair
    from rhs_layout import pack, unpack

    tapes = []
    original_init = Tape.__init__
    def track(tape):
        original_init(tape)
        tapes.append(tape)
    Tape.__init__ = track
    try:
        core, consumer = Core(), boundary_pages.BoundaryPages()
        page, source, lower, upper, reference_rhs, width_int, precision_int = fixture(length)
        dirty = Tape()
        for value in (1, 0, 1, 1, 0, 1, 0):
            dirty.append(value)
        dirty.rewind()
        protected = (page, source, dirty)
        saved = [(bytes(t.cells), t.head) for t in protected]
        def meter():
            return [sum(getattr(t.meter, key) for t in tapes) for key in ('reads','writes','moves')]
        def delta(start):
            return [a-b for a,b in zip(meter(),start)]
        def values(tape, count, width):
            out = []
            tape.rewind()
            for _ in range(count):
                with owned(read_signed(tape, width)) as (value,):
                    out.append(Q((-1 if value.negative else 1)*decode(value.magnitude), 1 << precision_int))
            need(tape.read() == BLANK, 'exact decoded extent')
            tape.rewind()
            return out
        for tape in core.pool.tapes:
            initialize_marker(tape)
        outputs, header, pages, matrices, packed, returned, scattered = (), None, (), [], None, None, ()
        phases = {}
        with owned(Count.literal(block_size), Count.literal(2)) as (block, two):
            try:
                with sealed_constructors(), core.scope.installed():
                    start = meter()
                    with no_decode():
                        outputs, header = first_pass_pair(core, page, source)
                    phases['actual_first_pass_pair'] = delta(start)
                    n = len(lower)
                    need([values(t,n,header.width) for t in outputs] == reference_rhs, 'actual Core RHS equals independent first-pass oracle')
                    def make(value):
                        return Rational(Signed(Count.literal(abs(value.numerator)), value < 0), Count.literal(value.denominator))
                    matrices = [Matrix(header.boundary_length, header.boundary_length, core.pool,
                                       lambda i,j,a=a: make(a[decode(i)][decode(j)])) for a in (lower,upper)]
                    start = meter()
                    with no_decode():
                        pages = boundary_pages.prepare_pages(*matrices, block, header.width, header.P, core.pool)
                    phases['exact_reference_page_setup'] = delta(start)
                    start = meter()
                    with no_decode():
                        packed = pack(*outputs, header.boundary_length, block, header.width, core.pool)
                    phases['pack'] = delta(start)
                    snapshot = [body(borrowed_tape(t)) for t in (*pages,packed,*outputs)]
                    start = meter()
                    with core.scope.suspended(), no_decode():
                        returned = consumer.run(*pages, packed, header.boundary_length, two, block, header.width, header.P)
                    phases['unchanged_boundary_consumer'] = delta(start)
                    start = meter()
                    with no_decode():
                        scattered = unpack(returned, header.boundary_length, block, header.width, core.pool)
                    phases['unpack'] = delta(start)
                    actual = [values(t,n,header.width) for t in scattered]
                    oracle = load('boundary_independent_oracle', ROOT/'research/physical-boundary-pages/verify.py')
                    data = [list(row) for row in zip(*reference_rhs)]
                    expected_padded = oracle.oracle(lower, upper, data, block_size, precision_int)
                    padded_rows = ((n+block_size-1)//block_size)*block_size
                    expected = [[],[]]
                    for batch in range((2+block_size-1)//block_size):
                        for row in range(padded_rows):
                            for col in range(block_size):
                                j=batch*block_size+col
                                if row<n and j<2:
                                    expected[j].append(expected_padded[(batch*padded_rows+row)*block_size+col])
                    need(actual == expected, 'caller-order output equals independent rounded block oracle')
                    need(actual[0] != actual[1], 'component swap is discriminating')
                    if length == 5:
                        need(actual != reference_rhs, 'bypassing the actual boundary consumer is falsified')
                    need(snapshot == [body(borrowed_tape(t)) for t in (*pages,packed,*outputs)], 'all consumer and layout borrows preserved')
                    need(saved == [(bytes(t.cells),t.head) for t in protected], 'source page and arbitrary dirty spectator preserved')
                    start = meter()
                    for t in scattered:
                        t.clear()
                    scattered=()
                    returned.clear(); erase_marker(returned); returned=None
                    packed.clear(); packed=None
                    for t in outputs:
                        t.clear()
                    outputs=()
                    for t in pages:
                        t.clear()
                    pages=()
                    for m in matrices:
                        m.close()
                    matrices=[]
                    header.close(); header=None
                    phases['consume_and_cleanup'] = delta(start)
                core.pool.empty(); core.idle(); consumer.idle()
                for tape in core.pool.tapes:
                    erase_marker(tape)
                need(all(t.head == 1 and all(v == BLANK for v in t.cells) for t in core.pool.tapes), 'all caller scratch restored including retained backing')
                need(not consumer.pool.live and consumer.closed, 'consumer ownership restored')
                return {'length':length,'rows':n,'block':block_size,'columns':2,'width':width_int,'precision':precision_int,
                        'rhs':[[str(v) for v in row] for row in reference_rhs], 'result':[[str(v) for v in row] for row in actual],
                        'physical_phases_reads_writes_moves':phases, 'retained_cells_all_constructed_tapes':sum(len(t.cells) for t in tapes),
                        'constructed_tape_count':len(tapes),'consumer_matrix_products':consumer.products,
                        'consumer_scalar_products':consumer.arithmetic.products}
            finally:
                # Valid executions are the theorem; this also bounds checker cleanup on rejection.
                for t in (*scattered,*outputs,*pages):
                    t.clear()
                for t in (packed,returned):
                    if t is not None: t.clear()
                for m in matrices: m.close()
                if header is not None: header.close()
        for t in protected:
            t.clear(); erase_marker(t)
    finally:
        Tape.__init__ = original_init


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true'); parser.add_argument('--quick',action='store_true')
    args=parser.parse_args(); authenticate()
    sys.path[:0]=[str(HERE),str(ROOT/'research/physical-gaussian-core'),str(ROOT/'research/physical-boundary-pages')]
    import gaussian_sources
    with gaussian_sources.opened():
        sys.path.insert(0,str(HERE))
        results=[case(5,2)] if args.quick else [case(5,2),case(1,4),case(5,1)]
        from controls import run
        controls=run()
    receipt={'status':'PASS_PHYSICAL_BOUNDARY_RHS_CALLER','cases':results,'controls':controls}
    if args.write: (HERE/'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    elif not args.quick: need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(receipt,sort_keys=True),'typed receipt')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__': main()
