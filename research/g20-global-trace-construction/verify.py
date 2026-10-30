"""Check the full G20 stream, source records and arbitrary input maps.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
Keep the source construction and proof credits in inputs/ and NOTICE.
"""
import argparse
from collections import Counter
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
OUTPUTS = ['GLOBAL.jsonl.gz', 'GLOBAL-RESULT.json', 'INVOICE.json', 'CALLS.json',
           'PRIVATE-EPISODES.json', 'TARGET-OWNERS.json', 'SOURCE-DESCRIPTORS.json.gz']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def extract(path, target):
    with tarfile.open(path) as archive:
        for member in archive:
            need(member.isfile() or member.isdir(), 'Regular source archive')
            rel = Path(member.name)
            need(not rel.is_absolute() and '..' not in rel.parts, 'Relative source path')
            out = target / rel
            if member.isdir():
                out.mkdir(parents=True, exist_ok=True)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(archive.extractfile(member).read())


def events(path):
    return [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]


def scan(program, descriptors, invoice):
    n, owned = invoice['originals'], invoice['owned_allocated']
    width = n + owned
    rows = [1 << i for i in range(width)]
    norms = [1] * width
    versions, epochs = [0] * width, [0] * width
    peak, used = 1, 0
    prefix, semantics = sha256(), sha256()
    counts, paid = Counter(), Counter()
    for ix, e in enumerate(program):
        op, d = e[:2]
        counts[op] += 1
        if op == 'ADD':
            need(0 <= d < width and 0 <= e[2] < width and d != e[2], 'ADD owners')
            rows[d] ^= rows[e[2]]
            norms[d] += norms[e[2]]
            peak = max(peak, norms[d])
            versions[d] += 1
        elif op == 'OWNED_CLEAR':
            need(n <= d < width, 'Private reset owner')
            rows[d] = norms[d] = 0
            versions[d] += 1
            epochs[d] += 1
        elif op == 'QUERY':
            need(used < len(descriptors), 'Query has source record')
            item = descriptors[used]
            expected = dict(event=ix, prefix_sha256=prefix.hexdigest(), owner=d,
                            rank=e[2], version=versions[d], epoch=epochs[d],
                            RAW_hex=hex(rows[d]), detail=e[3])
            need(all(item[k] == v for k, v in expected.items()), 'Exact chronological source record')
            detail = e[3][:-1] if e[3][0] == 'LOCAL_INVERSE' else e[3]
            semantics.update(canonical([d, e[2], detail, hex(rows[d])]))
            used += 1
            paid[e[2]] += 1
            versions[d] += 1
        elif op in ('OWNED_ZERO_HEADER', 'WHOLE_ZERO_FRAME'):
            need(rows[d] == 0, 'Exact zero before free frame change')
            need(op == 'WHOLE_ZERO_FRAME' or n <= d < width, 'Private zero header')
        else:
            need(op == 'PAID_PORT_ROUTE', 'Known global opcode')
        prefix.update((json.dumps(e, separators=(',', ':')) + '\n').encode())
    need(used == len(descriptors), 'Complete source record coverage')
    need(rows == [1 << i for i in range(n)] + [0] * owned, 'All global input columns')
    need(paid == {int(k): v for k, v in invoice['paid'].items()}, 'Full paid invoice')
    dual = [1 << i for i in range(width)]
    for e in reversed(program):
        if e[0] == 'ADD':
            dual[e[2]] ^= dual[e[1]]
        elif e[0] == 'OWNED_CLEAR':
            dual[e[1]] = 0
    need(dual == [1 << i for i in range(n)] + [0] * owned, 'Separate full transpose')
    return dict(events=len(program), counts=dict(counts), queries=used,
                stream_sha256=prefix.hexdigest(), query_semantics_sha256=semantics.hexdigest(),
                majorant=str(peak), majorant_bits=peak.bit_length(),
                input_axes=width, matrix_coefficients=width * width)


def fee(invoice, glob, matcher):
    n, m, owned = invoice['originals'], invoice['QUERYs'], invoice['owned_allocated']
    ops = glob['operation_counts']
    scans = sum(ops[k] for k in ('ADD', 'OWNED_CLEAR', 'OWNED_ZERO_HEADER', 'WHOLE_ZERO_FRAME')) + 2 * owned
    parking = 4 * (n + owned) * m
    routes = 7548 + 7248 + 72
    matrix = m * (32 * 127**2 + 8 * 127**3)
    terms = matcher['global_occurrences'] * matcher['paired_address_coefficient_terms_per_call'] + matcher['new_target_coefficient_terms']
    return dict(scans=scans, parking=parking, routes=routes, raw=glob['expanded_event_count'],
                matrix=matrix, matcher=terms, total=scans + parking + routes + glob['expanded_event_count'] + matrix + terms)


def run(emit=None):
    pins = read(HERE / 'SOURCES.json')
    for item in pins['vendored_inputs']:
        need(sha256((HERE/item['path']).read_bytes()).hexdigest() == item['sha256'], 'Frozen source ' + item['path'])
    with tempfile.TemporaryDirectory(prefix='g20-global-trace-') as temp:
        root = Path(temp)
        extract(HERE/'inputs/PR5708.tar.gz', root/'source')
        extract(HERE/'inputs/PR5828.tar', root/'local')
        source = root/'source/research/g20-conjugation-admission'
        local = root/'local/research/g20-trace-resynthesis'
        args = [sys.executable, '-I', '-B'] + (['-O'] if sys.flags.optimize else [])
        result = subprocess.run(args + [str(local/'verify.py')], capture_output=True, text=True, timeout=180)
        need(result.returncode == 0, 'Complete local replay: ' + result.stderr[-2000:])
        spec = read(HERE/'ADAPTATION.json')
        text = (source/'global_retirement.py').read_text()
        need(sha256(text.encode()).hexdigest() == spec['source_sha256'], 'Exact compiler source')
        body = text.split('def run():\n', 1)[1].split("if __name__=='__main__':", 1)[0]
        for old, new in spec['body_changes']:
            need(body.count(old) == 1, 'One declared compiler change')
            body = body.replace(old, new)
        need((HERE/'compile.py').read_text() == spec['header'] + body, 'Only declared compiler changes')
        L = load('global_trace_source', source/'integration.py')
        compiler = load('global_trace_compiler', HERE/'compile.py')
        word = read(local/'WORD.json.gz')
        oldword = read(source/'WORD.json.gz')
        trace = load('checked_local_trace', local/'verify.py')
        need(trace.observations(word) == trace.observations(oldword), 'Every native and reset input matches PR5708')
        need(all(word[k] == oldword[k] for k in ('start', 'final', 'owned')), 'Exact local boundary')
        output = root/'output'
        output.mkdir()
        compiler.compile_global(L, word, output)
        old, new = (events(p/'GLOBAL.jsonl.gz') for p in (source, output))
        oldinvoice, invoice = (read(p/'INVOICE.json') for p in (source, output))
        need(invoice == oldinvoice, 'Unchanged complete invoice and owned reserve')
        need(read(output/'TARGET-OWNERS.json') == read(source/'TARGET-OWNERS.json'), 'Every productive owner')
        before = scan(old, read(source/'SOURCE-DESCRIPTORS.json.gz'), invoice)
        desc = read(output/'SOURCE-DESCRIPTORS.json.gz')
        after = scan(new, desc, invoice)
        need(before['query_semantics_sha256'] == after['query_semantics_sha256'], 'All actual global native query values')
        glob = read(output/'GLOBAL-RESULT.json')
        need([glob['canonical_stream_sha256'], glob['majorant'], glob['operation_counts']] ==
             [after['stream_sha256'], after['majorant'], after['counts']], 'Independent full stream receipt')
        need(int(after['majorant']) <= int(before['majorant']) and after['majorant_bits'] < 1024, 'Retained precision envelope')
        oldcalls, calls = (read(p/'CALLS.json') for p in (source, output))
        need(len(calls) == len(oldcalls) == 18, 'Every physical call')
        outside = []
        for program, cs in ((old, oldcalls), (new, calls)):
            last = 0
            stripped = []
            for c in cs:
                stripped.extend(program[last:c['core_begin']])
                last = c['core_end']
            stripped.extend(program[last:])
            outside.append(stripped)
        need(outside[0] == outside[1], 'All controller, idle, thin and port work is fixed')
        need(all({k: v for k, v in a.items() if k not in ('core_begin', 'core_end')} ==
                 {k: v for k, v in b.items() if k not in ('core_begin', 'core_end')}
                 for a, b in zip(oldcalls, calls)), 'Actual call ownership and direction')
        for c in calls:
            need(c['core_end'] - c['core_begin'] == len(word['records']), 'Complete local core interval')
        episodes = read(output/'PRIVATE-EPISODES.json')
        active, peak = set(), 0
        begin = {e['begin']: e for e in episodes}
        end = {e['end']: e for e in episodes}
        need(len(begin) == len(end) == len(episodes), 'Unique lifetime endpoints')
        for ix, e in enumerate(new):
            if ix in begin:
                owner = begin[ix]['owner']
                need(owner not in active and e[0] == 'ADD' and e[1] == owner, 'Private lifetime start')
                active.add(owner)
                peak = max(peak, len(active))
            if ix in end:
                owner = end[ix]['owner']
                need(owner in active and e[:2] == ['OWNED_CLEAR', owner], 'Private lifetime return')
                active.remove(owner)
        need(not active and peak <= 48, 'All private lifetimes return')
        oldfee, newfee = (fee(invoice, read(p/'GLOBAL-RESULT.json'), read(source/'MATCHER.json')) for p in (source, output))
        retained = read(source/'ORDINARY-RESULT.json')['fee_bounds']['base_counts']['coarse_primitive_count_with_dimension_work']
        need(oldfee['total'] == retained and newfee['total'] < retained < 2**64, 'Full positive finite fee')
        controls = []
        first = desc[0]
        for key in ('event', 'version', 'epoch'):
            bad = [dict(first, **{key: first[key] + 1})] + desc[1:]
            try:
                scan(new, bad, invoice)
            except ValueError as error:
                need(str(error) == 'Exact chronological source record', 'Expected source rejection')
                controls.append('stale_' + key)
            else:
                raise ValueError('Stale source record accepted')
        result = dict(status='PASS_G20_COMPLETE_TRACE_CALLER', source=before, constructed=after,
                      calls=len(calls), owned_episodes=len(episodes), peak_owned=peak,
                      invoice=invoice, old_fee=oldfee, new_fee=newfee,
                      saved_global_adds=before['counts']['ADD'] - after['counts']['ADD'],
                      saved_finite_primitives=oldfee['total'] - newfee['total'],
                      negative_controls=controls)
        if emit:
            emit.mkdir(parents=True, exist_ok=True)
            for name in OUTPUTS:
                (emit/name).write_bytes((output/name).read_bytes())
            (emit/'WORD.json.gz').write_bytes((local/'WORD.json.gz').read_bytes())
            (emit/'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
        else:
            need(result == read(HERE/'RESULT.json'), 'Complete retained result')
            need((HERE/'WORD.json.gz').read_bytes() == (local/'WORD.json.gz').read_bytes(), 'Exact installed word')
            for name in OUTPUTS:
                retained, generated = (p.read_bytes() for p in (HERE/name, output/name))
                if name.endswith('.gz'):
                    retained, generated = map(gzip.decompress, (retained, generated))
                need(retained == generated, 'Exact generated artifact ' + name)
    print('PASS_G20_COMPLETE_TRACE_CALLER', result['saved_global_adds'], result['new_fee']['total'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    run(parser.parse_args().emit)
