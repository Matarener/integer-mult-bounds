"""Check uninterrupted source-bound CRT rows and the paid update boundary.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All host serialization is confined to the initial test fixture.
"""
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path, text=None):
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes() if text is None else text, str(path), 'exec'), module.__dict__)
    return module


def modules():
    for pin in json.loads((P / 'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Source bytes')
    helper = load('reentry_fixture', ROOT / 'research/crt-mixed-row-entry/verify.py')
    base = helper.modules()
    rom = load('reentry_rom', ROOT / 'research/crt-encoded-benes-rom-producer/microcode.py')
    join = load('reentry_join', ROOT / 'research/crt-current-row-query/join.py')
    adapter = load('reentry_adapter', P / 'reentry.py')
    return helper, base, rom, join, adapter, rom.producer_program()


def decode(source, widths, w, records):
    raw, at, values = source.cells, 1, []
    for h in widths:
        need(raw[at] == records.ROOT, 'Observed source tag')
        at += 1 + h + 1 + h + 1
        values.append(sum(raw[at + j] << j for j in range(h)))
        at += h
        need(raw[at] == records.RECORD_END, 'Observed record end')
        at += 1
    need(raw[at] == w.RIGHT and at + 1 == len(raw), 'Exact source backing extent')
    return tuple(values)


def footprint(query):
    if query.output is None:
        return {}, []
    owned = [*query.entry.inputs, *query.entry.context.owned]
    backings = {id(t.cells): t.cells for t in [*owned, *query.ports]}
    backings.update({id(cells): cells for cells in query.service.values()})
    return backings, owned


def bounds(widths, ell, level, start, row):
    size = 1 << level
    middle, stop = start + size // 2, start + size
    active = [i for i in range(middle, stop) if widths[i] == ell or row not in (ell - 1, ell)]
    if not active:
        return 0, 0
    precision = 1 + sum(widths[start:stop])
    length = 2 + sum(3 * h + 4 for h in widths)
    stream = 2 + sum(widths[middle:stop]) + size // 2
    work = length + (size + 1) * (precision + 2)
    work += sum((2**widths[i] + 1) * (widths[i] + 1) + 2**widths[i] * (2 * widths[i] - 1)
                + 2 * widths[i] + 4 for i in active)
    time = 2**20 * (precision + 2)**4 + 2**16 * (precision + 2)**2
    time += 128 * (length + precision + size + 1) + 4096 * work
    time += sum(2 * 10**6 * precision**2 * (2**widths[i] + 1)**3 * (widths[i] + 1)**4 for i in active)
    time += 4096 * (length + stream)
    storage = 57 * (precision + 2) + 3 * (precision - 2) * (2 * precision + 4) + 6 + 3 * precision + 4 * size + 4
    height = max(widths[i] for i in active)
    storage += 5 * precision * 2**height * (height**2 + 3 * height + 1)
    storage += 2**height * (4 * height - 1) + 48 * precision + 2 * height + 104
    storage += 2 * (height + 2) + stream
    return time, storage


def run_case(mod, name, moduli, widths, ell, state, level, start):
    helper, base, rom, join, adapter, program = mod
    w, records, entry, numeric, caller_module, crt, row_module = base
    precision = 1 + sum(widths[start:start + (1 << level)])
    source = helper.axis_stream(w, records, entry, moduli, widths, state)
    source_id, cells_id = id(source), id(source.cells)
    dirty = [helper.port(w, entry, helper.bits(3 * i + 1, precision) + [w.RIGHT]) for i in range(8)]
    for i, tape in enumerate(dirty):
        for _ in range(i % 3):
            tape.step(1)
    initial_dirty = helper.snapshot(dirty)
    caller = caller_module.Caller(moduli, widths, ell, crt)
    staging = join.Tape()
    queries, all_backings, trace = [], {}, []
    expected = tuple(state)
    middle, stop = start + (1 << (level - 1)), start + (1 << level)
    initial_source = bytes(source.cells)
    schedule = list(range(2 * ell - 1)) + list(reversed(range(2 * ell - 1)))
    for step, row in enumerate(schedule):
        before = bytes(source.cells), source.head
        traffic_before = helper.traffic([source, *dirty])
        stage_before = staging.actions
        specs = [s for s in caller.row(expected, level, row) if middle <= s[0] < stop]
        expected = caller.apply(expected, specs)
        query = join.RowQuery(w, records, entry, numeric, row_module, rom, program,
                              source, dirty, widths, ell, level, start, row)
        need((bytes(source.cells), source.head) == before, 'Borrowed source unchanged during query')
        backings, owned = footprint(query)
        before_update = helper.traffic([source])
        output_before = 0 if query.output is None else query.output.actions
        adapter.consume_into_source(query, staging, widths, level, start)
        need(query.closed, 'Old query retires before reentry')
        need(id(source) == source_id and id(source.cells) == cells_id, 'Same physical source throughout')
        need(decode(source, widths, w, records) == expected and source.head == 1, 'Actual updated row and entry head')
        need(helper.snapshot(dirty) == initial_dirty, 'Protected dirty bytes and heads')
        need(all(x == '_' for x in staging.cells) and staging.head == 0, 'Staging is blank after consumption')
        need(all(t.head == 1 and all(x == w.BLANK for x in t.cells) for t in owned), 'All numerical roles retired')
        need(all(t.head == 0 and all(x == '_' for x in t.cells) for t in query.ports), 'All joined roles retired')
        if query.service is not None:
            need(all(all(x == '_' for x in cells) for cells in query.service.values()), 'All producer backing retired')
        if query.output is not None:
            height = max(widths[i] for i in query.entry.active)
            bank = 5 * precision * 2**height * (height**2 + 3 * height + 1)
            bank += 2**height * (4 * height - 1) + 48 * precision + 2 * height + 104
            service_backings = {id(cells): cells for cells in query.service.values()}
            need(len(service_backings) == 52 and sum(map(len, service_backings.values())) == bank,
                 'Exact inherited ROM bank count')
            extra_ids = set(backings) - set(service_backings) - {id(t.cells) for t in owned}
            stream = 2 + sum(widths[middle:stop]) + (1 << (level - 1))
            need(len(extra_ids) == 3 and sum(len(backings[i]) for i in extra_ids) == 2 * (height + 2) + stream,
                 'Exact disjoint coordinate, countdown and result backings')
        need(not set(all_backings) & set(backings), 'Distinct row workspaces are retained and charged')
        all_backings.update(backings)
        queries.append(query)  # Keep every retired backing live for the full storage measurement.
        time_bound, storage_bound = bounds(widths, ell, level, start, row)
        extra = helper.traffic([source]) - before_update + staging.actions - stage_before
        if query.output is not None:
            extra += query.output.actions - output_before
            length = 2 + sum(3 * h + 4 for h in widths)
            stream = 2 + sum(widths[middle:stop]) + (1 << (level - 1))
            need(extra <= 128 * (length + stream), 'Paid update scan allowance')
            arena = query.entry.context.arena.meter
            measured = helper.traffic([source, *dirty, *owned]) - traffic_before
            measured += arena.reads + arena.writes + arena.moves
            measured += sum(t.actions for t in query.ports) + query.producer_steps + staging.actions - stage_before
        else:
            measured = helper.traffic([source, *dirty]) - traffic_before + staging.actions - stage_before
            need(measured == 0 and not backings, 'Idle row has no work or allocation')
        need(measured <= time_bound and sum(map(len, backings.values())) <= storage_bound, 'Complete row cost and storage')
        trace.append(dict(row=row, state=list(expected), producer_calls=query.invocations,
                          measured_source_actions=measured, update_tape_actions=extra,
                          time_bound=time_bound, retained_cells=sum(map(len, backings.values())), storage_bound=storage_bound))
        if step == 2 * ell - 2:
            forward = list(expected)
    need(bytes(source.cells) == initial_source and source.head == 1, 'Reverse rows restore the whole owned source')
    need(expected == tuple(state), 'Round trip endpoint')
    stream_bound = 2 + sum(widths[middle:stop]) + (1 << (level - 1))
    retained = len(staging.cells) + sum(map(len, all_backings.values()))
    retained_bound = stream_bound + sum(x['storage_bound'] for x in trace)
    need(retained <= retained_bound, 'All retired row backings remain billed')
    return dict(name=name, moduli=list(moduli), widths=list(widths), ell=ell, level=level, start=start,
                initial=list(state), forward=forward, trace=trace, initial_serializations=1,
                retained_cells=retained, retained_bound=retained_bound,
                source_cells=len(source.cells), borrowed_dirty_cells=sum(len(t.cells) for t in dirty))


def adapter_controls(mod):
    helper, base, rom, join, adapter, program = mod
    w, records, entry, *_ = base
    source_text = (P / 'reentry.py').read_text()
    mutations = [
        ('retirement', '    query.close()\n    #', '    # query close omitted\n    #'),
        ('coordinate', 'source.write(w.ONE if bit == \'1\' else w.ZERO)', 'source.write(w.ZERO)'),
        ('target_boundary', 'chosen = middle <= axis < stop', 'chosen = start <= axis < stop'),
        ('staging_retirement', '    staging.erase()', '    # staging retained'),
        ('source_head', '    source.rewind()', '    # source head not returned'),
    ]
    rejected = []
    for label, old, new in [('positive', None, None), *mutations]:
        implementation = adapter
        if old is not None:
            need(source_text.count(old) == 1, 'One exact semantic mutation')
            implementation = load('reentry_mutant_' + label, P / 'reentry.py', source_text.replace(old, new))
        source = helper.axis_stream(w, records, entry, (7, 3), (3, 2), (1, 1))
        original = bytes(source.cells)
        output = join.Tape(list('L11|R'))  # The actual source row-one return is coordinate three.
        query = SimpleNamespace(w=w, records=records, source=source, output=output, closed=False)
        def close():
            need(not query.closed and bytes(source.cells) == original, 'Source borrow ends before update')
            output.erase()
            query.closed = True
        query.close = close
        staging = join.Tape()
        try:
            implementation.consume_into_source(query, staging, (3, 2), 1, 0)
            need(query.closed and decode(source, (3, 2), w, records) == (1, 3), 'Correct adapter endpoint and retirement')
            need(source.head == 1 and staging.head == 0 and all(x == '_' for x in staging.cells), 'Complete adapter cleanup')
        except ValueError:
            need(label != 'positive', 'Positive adapter fixture')
            rejected.append(label)
        else:
            need(label == 'positive', 'Defective adapter accepted')
    return rejected


def main():
    mod = modules()
    controls = adapter_controls(mod)
    cases = [run_case(mod, 'mixed_padded_roundtrip', (7, 3), (3, 2), 3, (1, 1), 1, 0),
             run_case(mod, 'two_target_roundtrip', (5, 7, 3, 2), (3, 3, 2, 2), 3, (3, 2, 1, 1), 2, 0),
             run_case(mod, 'nonroot_roundtrip', (5, 7, 3, 2), (3, 3, 2, 2), 3, (3, 2, 1, 1), 1, 2),
             run_case(mod, 'invalid_left_roundtrip', (7, 3), (3, 2), 3, (7, 1), 1, 0)]
    result = dict(status='PASS_CRT_PAID_ROW_REENTRY', cases=cases, adapter_controls=controls,
                  row_invocations=sum(len(x['trace']) for x in cases),
                  producer_calls=sum(row['producer_calls'] for x in cases for row in x['trace']),
                  kappa_change=None)
    if '--write' in sys.argv:
        (P / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((P / 'RESULT.json').read_text()), 'Committed receipt')
    print(result['status'], 'rows=' + str(result['row_invocations']), 'producer_calls=' + str(result['producer_calls']),
          'controls=' + str(len(controls)))


if __name__ == '__main__':
    main()
