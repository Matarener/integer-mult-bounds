"""Source-bound finite checks; host decoding/snapshots occur only in this verifier.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import json
import sys
from types import ModuleType

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    mod = ModuleType(name)
    mod.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), mod.__dict__)
    return mod


def retired(pool, w):
    need(not pool.live, 'source borrow retired')
    for role, cells in pool.backing.items():
        blank = w.BLANK if role.startswith('numeric.') else '_'
        need(all(x == blank for x in cells), 'historical tail blank: ' + role)
        if role in pool.ports:
            need(pool.ports[role].head == 1, 'numerical entry head')


def controls(pool, w, source, dirty, geometry):
    checks = []
    def reject(label, action):
        try:
            action()
        except ValueError:
            checks.append(label)
        else:
            raise ValueError('negative control survived: ' + label)
    pool.begin(geometry, source, dirty)
    reject('source_borrow_not_retired', lambda: pool.begin(geometry, source, dirty))
    pool.live = False
    role = 'numeric.canonical_right'
    tape = pool.ports[role]
    tape.cells[-1] = w.ONE
    reject('historical_tail_not_blank', lambda: retired(pool, w))
    tape.cells[-1] = w.BLANK
    old = pool.backing['query.countdown']
    pool.backing['query.countdown'] = pool.backing['query.coordinate']
    pool.live = True
    pool.used = set(pool.backing)
    reject('accidental_role_alias', lambda: pool.end(True))
    pool.backing['query.countdown'] = old
    pool.end(True)
    # Different roles peak in different epochs; total-invoice max loses retained cells.
    epochs = ({'a': 9, 'b': 1}, {'a': 1, 'b': 9})
    need(sum(max(e[r] for e in epochs) for r in ('a', 'b')) == 18, 'rolewise high water')
    reject('max_total_invoice', lambda: need(max(sum(e.values()) for e in epochs) == 18, 'undercount'))
    return checks


def main():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'source bytes')
    source_text = (ROOT/'research/crt-current-row-query/join.py').read_text()
    for old, new in json.loads((P/'SEAMS.json').read_text()).items():
        need(source_text.count(old) == 1, 'one exact constructor seam')
        source_text = source_text.replace(old, new)
    need(source_text == (P/'query.py').read_text(), 'unchanged source query body')
    pred = load('predecessor', ROOT/'research/crt-paid-row-reentry/verify.py')
    helper, base, rom, original, adapter, program = pred.modules()
    w, records, entry, numeric, caller_module, crt, row_module = base
    query_module = load('pooled_query', P/'query.py')
    workspace = load('workspace', P/'workspace.py')
    widths, moduli, state, ell, level, start = (3, 2), (7, 3), (1, 1), 3, 1, 0
    precision = 1 + sum(widths)
    source = helper.axis_stream(w, records, entry, moduli, widths, state)
    dirty = [helper.port(w, entry, helper.bits(3*i+1, precision)+[w.RIGHT]) for i in range(8)]
    for i, tape in enumerate(dirty):
        for _ in range(i % 3): tape.step(1)
    initial = bytes(source.cells), source.head
    protected = helper.snapshot(dirty)
    pool = workspace.Workspace()
    staging = original.Tape()
    caller = caller_module.Caller(moduli, widths, ell, crt)
    expected = state
    trace, ids, extents, high = [], {}, {}, {}
    write = source.write
    def guarded_write(value):
        need(not pool.live, 'source write before query close')
        write(value)
    source.write = guarded_write
    schedule = list(range(5)) + list(reversed(range(5)))
    for step, row in enumerate(schedule):
        before_source = bytes(source.cells), source.head
        before_traffic = helper.traffic([source, *dirty, *pool.ports.values()])
        before_setup = pool.setup_actions
        before_stage = staging.actions
        expected = caller.apply(expected, caller.row(expected, level, row))
        query = query_module.RowQuery(w, records, entry, numeric, row_module, rom, program,
                                     source, dirty, widths, ell, level, start, row, pool)
        need((bytes(source.cells), source.head) == before_source, 'query borrows current source')
        if step == 0:
            try: source.write(source.read())
            except ValueError: pass
            else: raise ValueError('source write before close allowed')
        live_right_extent = (query.entry.right.cells.index(w.RIGHT) + 1) if query.output is not None else None
        backings, owned = pred.footprint(query)
        need(set(backings) <= {id(c) for c in pool.backing.values()}, 'every source allocation mapped')
        adapter.consume_into_source(query, staging, widths, level, start)
        retired(pool, w)
        need(pred.decode(source, widths, w, records) == expected, 'current-state logical row oracle')
        need(helper.snapshot(dirty) == protected, 'protected bytes and heads')
        need(source.head == 1 and staging.head == 0 and all(x == '_' for x in staging.cells), 'entry heads')
        for role, cells in pool.backing.items():
            need(role not in ids or ids[role] == id(cells), 'stable physical backing identity')
            ids[role] = id(cells)
            high[role] = max(high.get(role, 0), len(cells))
            need(len(cells) == high[role], 'historical capacity not truncated')
        extents[str(step)] = {r: len(c) for r, c in pool.backing.items()}
        actions = helper.traffic([source, *dirty, *pool.ports.values()]) - before_traffic
        actions += staging.actions - before_stage + pool.setup_actions - before_setup
        actions += sum(t.actions for t in query.ports) + query.producer_steps
        if query.entry.context:
            meter = query.entry.context.arena.meter
            actions += meter.reads + meter.writes + meter.moves
        allowance, _ = pred.bounds(widths, ell, level, start, row)
        allowance += 4*63 + 118 if query.output is not None else 0
        need(actions <= allowance, 'full paid primitive actions and explicit setup')
        trace.append(dict(row=row, state=list(expected), roles_used=len(pool.used), actions=actions,
                          allowance=allowance, producer_calls=query.invocations, live_right_extent=live_right_extent))
        if step == 4: forward = list(expected)
    need((bytes(source.cells), source.head) == initial, 'entire source roundtrip')
    need(forward == [1, 2] and len(pool.backing) == 118, 'claimed first fixture')
    # Retained capacity includes every role separately, not the largest row bill.
    retained = len(staging.cells) + sum(high.values())
    need(retained == len(staging.cells) + sum(len(c) for c in pool.backing.values()), 'exact retained role sum')
    right_extents = [t['live_right_extent'] for t in trace if t['live_right_extent'] is not None]
    need(any(b < a for a, b in zip(right_extents, right_extents[1:])), 'actual shorter reentry after longer extent')
    height, n, stream = max(widths[1:]), 2, len(staging.cells)
    bank = 5*precision*2**height*(height**2+3*height+1)
    bank += 2**height*(4*height-1)+48*precision+2*height+104
    for role, capacity in high.items():
        if role.startswith('rom.'): bound = bank
        elif role in ('query.coordinate', 'query.countdown'): bound = height+2
        elif role == 'query.output': bound = stream
        elif role.startswith('numeric.word.') or role in ('numeric.template', 'numeric.guide'): bound = precision+2
        else: bound = n*(2*precision+4)+2
        need(capacity <= bound, 'source-derived role envelope: '+role)
    faults = controls(pool, w, source, dirty, (widths, ell, level, start))
    faults += pred.adapter_controls((helper, base, rom, original, adapter, program))
    faults.append('source_write_before_close')
    # Execute the real ROM/numerical pipeline with its deliberate stale-offset fault.
    wrong = query_module.RowQuery(w, records, entry, numeric, row_module, rom, program,
                                 source, dirty, widths, ell, level, start, 1, pool, fault='zero_offset')
    adapter.consume_into_source(wrong, staging, widths, level, start)
    correct = caller.apply(state, caller.row(state, level, 1))
    need(pred.decode(source, widths, w, records) != correct, 'stale-offset mutation must differ')
    retired(pool, w)
    faults.append('actual_zero_offset_producer')
    result = dict(status='PASS_CRT_STABLE_ROW_WORKSPACE', roles=118, forward=forward, trace=trace,
                  high_water=high, epoch_extents=extents, retained_cells=retained,
                  controls=faults, source_initializations=1, kappa_change=None)
    if '--write' in sys.argv:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == json.loads((P/'RESULT.json').read_text()), 'committed receipt')
    print(result['status'], 'roles=118', 'retained='+str(retained), 'controls='+str(len(faults)))


if __name__ == '__main__': main()
