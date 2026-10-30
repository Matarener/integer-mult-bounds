#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Observe unchanged PR5707 source writes; the integer oracle is checker-only."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/encoded-minimum-root-prefix'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash: ' + row['path'])


def oracle(M, K, T, m, r, F):
    for q in range(M):
        w, d = M - q, 0
        while w >= T:
            w = r * (w // m)
            d += 1
        stock = F ** d
        # If rows > stock then padding < rows + stock < 2 rows.
        if K * q >= stock.bit_length():
            return q, d, stock
        rows = 1 << (K * q)
        if ((rows + stock - 1) // stock) * stock < 2 * rows:
            return q, d, stock
    raise ValueError('missing feasible prefix')


def extent_bound(M, K, m, F):
    A = (F - 1).bit_length() * (m - 1) * M.bit_length()
    return max(7, M.bit_length() + K.bit_length() + 1, A + 2) + 2


def run_history(warm):
    from cardinal_counts import Count
    from records import Tape
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors
    from words import BLANK, LEFT, RIGHT
    import planner

    def decode(count):
        raw = count.tape.physical.cells
        end = raw.index(RIGHT, 1)
        need(all(v in (0, 1) for v in raw[1:end]), 'binary result')
        return sum(v << i for i, v in enumerate(raw[1:end]))

    def snapshot(counts):
        return tuple((bytes(c.tape.cells), c.tape.head) for c in counts)

    pool = ScratchPool(32)
    scope = OuterScope(pool)
    if warm:
        for i, tape in enumerate(pool.tapes):
            for _ in range(400 + 7 * i):
                tape.append(0)
            tape.clear()
    initial = [len(t.cells) for t in pool.tapes]
    historical = initial[:]
    slots = {id(t): i for i, t in enumerate(pool.tapes)}
    original_write = Tape.write
    writes = 0
    local_max = []
    envelope = initial[:]
    active_bound = 0

    def observed_write(tape, symbol):
        nonlocal writes
        original_write(tape, symbol)
        if id(tape) in slots:
            i = slots[id(tape)]
            writes += 1
            local_max[i] = max(local_max[i], tape.head + 1)
            historical[i] = max(historical[i], tape.head + 1)
            need(tape.head + 1 <= active_bound, 'actual write exceeds primitive envelope')
            need(len(tape.cells) == historical[i], 'exact physical tape high-water recurrence')
            need(len(tape.cells) <= envelope[i], 'historical envelope')

    cases = [(4, 1, 2, 2, 1, 6), (512, 1, 2, 2, 1, 6),
             (1, 1, 2, 2, 1, 6), (7, 1 << 60, 2, 2, 1, 6),
             (31, 2, 3, 3, 2, 5), (4, 1, 2, 2, 1, 6),
             (9, 4, 1000, 2, 1, 6)]
    records = []
    output_control = last_call_control = warm_control = False
    try:
        Tape.write = observed_write
        for args in cases:
            M, K, T, m, r, F = args
            # Input construction is outside the measured pool and installed scope.
            counts = tuple(Count.literal(v) for v in (M, K, T))
            before = snapshot(counts)
            active_bound = extent_bound(M, K, m, F)
            envelope = [max(v, active_bound) for v in envelope]
            local_max = [1] * 32
            with sealed_constructors(), scope.installed():
                result = planner.minimum_prefix(*counts, m, r, F)
                got = tuple(decode(c) for c in result)
                need(got == oracle(*args), 'independent strict-padding oracle')
                need(len(pool.live) == 3, 'exactly three caller-owned returned Counts')
                try:
                    pool.empty()
                except ValueError as error:
                    need('closes all scratch leases' in str(error), 'output control reason')
                    output_control = True
                else:
                    raise ValueError('missing output ownership control accepted')
                need(snapshot(counts) == before, 'borrowed bytes and heads restored')
                for value in result:
                    value.close()
            pool.empty()
            lengths = [len(t.cells) for t in pool.tapes]
            need(lengths == historical, 'independent end-of-call lengths')
            need(all(t.head == 1 and t.cells[0] == LEFT and
                     all(v == BLANK for v in t.cells[1:]) for t in pool.tapes),
                 'all retained tails erased with origins retained')
            if not warm and max(lengths) > active_bound:
                last_call_control = True
            if warm and sum(lengths) > 32 * max(extent_bound(a[0], a[1], a[3], a[5]) for a in cases):
                warm_control = True
            records.append(dict(arguments=args, output=got, new_write_bound=active_bound,
                                per_tape_written_extent=local_max[:], per_tape_backing=lengths))
            for count in counts:
                count.close()
    finally:
        Tape.write = original_write
    need(pool.peak <= 14 and writes > 0, 'source lease cap and nonempty observation')
    need(output_control, 'missing output cleanup rejected')
    need(warm_control if warm else last_call_control, 'history-specific negative control')
    return dict(warm=warm, initial_backing=initial, final_backing=historical,
                peak_live=pool.peak, pool_writes=writes, records=records,
                output_control=output_control, last_call_control=last_call_control,
                omitted_warm_control=warm_control)


def main():
    authenticate()
    sys.path.insert(0, str(SOURCE))
    import retained
    retained.activate()
    result = [run_history(False), run_history(True)]
    print(json.dumps(dict(status='PASS_ENCODED_PREFIX_SCRATCH_HISTORY', histories=result),
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
