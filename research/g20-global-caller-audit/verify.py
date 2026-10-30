"""Check the frozen G20 global caller without source implementation imports.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The construction and local native proof retain their source attribution.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    raw = (SOURCE / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in pins['original_sources']:
        raw = (HERE / row['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Source SHA256: ' + row['local_path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'Source Git blob: ' + row['local_path'])
    native = read('NATIVE-SOURCES.json')
    for name in ['WORD.json.gz', 'LOCAL-RESULT.json', 'MATCHER.json', 'FRAMES.json']:
        row = next(r for r in native['files'] if r['path'].endswith('/' + name))
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == row['sha256'],
             'The native proof covers the same input: ' + name)
    return len(pins['original_sources'])


def layout(word, controller):
    thick = controller['invoice']['thick_stages']
    need(len(thick) == len(set(thick)) == 18, 'Eighteen distinct full stages')
    pivots = sorted(r for r in word['owned'] if r < 658)
    snapshots = sorted(r for r in word['owned'] if r >= 660)
    need(len(pivots) == 22 and len(snapshots) == 24, 'Exact retired and snapshot inventories')
    retired = {3552 + 436*j + r - 222 for j in range(18) for r in pivots}
    retained = [r for r in range(11400) if r not in retired]
    compact = {r: i for i, r in enumerate(retained)}
    n = len(retained) + 18
    owned = list(range(n, n + len(word['owned'])))
    need((n, len(owned)) == (11022, 48), 'Public and owned global counts')
    private = dict(zip([658, 659] + pivots + snapshots, owned))

    def owners(stage, x, y):
        j = thick.index(stage)
        mapping = dict(private)
        for r in range(222):
            mapping[r] = compact[(x if r < 111 else y)*111 + r % 111]
        for r in range(222, 658):
            if r not in private:
                mapping[r] = compact[3552 + 436*j + r - 222]
        mapping[684] = len(retained) + j
        need(set(mapping) == set(range(685)) and len(set(mapping.values())) == 685,
             'Injective complete local owner map')
        return mapping

    old = read('BASE-CALLS.json')
    need([(c['stage'], c['helper_owner_begin']) for c in old]
         == [(s, 3552 + 436*j) for j, s in enumerate(thick)], 'Original helper cohorts')
    return n, owned, retired, retained, owners


def bind(events, word, controller, calls):
    n, owned, retired, retained, owners = layout(word, controller)
    at = 0
    actual_calls, helper_maps = [], []

    def consume(expected):
        nonlocal at
        need(at < len(events) and events[at] == expected, 'Exact macro binding at event ' + str(at))
        at += 1

    def add(d, s, label):
        consume(['ADD', d, s, label])

    def scalar(op, d, s, label):
        need(op in ['ADD', 'SWAP'], 'Scalar controller opcode')
        for port in range(111):
            a, b = d*111 + port, s*111 + port
            add(a, b, label)
            if op == 'SWAP':
                add(b, a, label)
                add(a, b, label)

    for r in owned:
        consume(['OWNED_CLEAR', r, None, 'GLOBAL_ENTRY_ARBITRARY_DIRTY'])
    for op, d, s in controller['boundaries']['right_program']:
        scalar(op, d, s, 'RIGHT_BOUNDARY')
    for event in controller['physical_events']:
        op = event[0]
        if op in ['LOCAL', 'QUERY_SHEAR']:
            _, stage, pair, reverse = event
            x, y = (2*pair+1, 2*pair) if reverse else (2*pair, 2*pair+1)
        if op == 'LOCAL':
            mapping = owners(stage, x, y)
            helper_maps.append(mapping)
            if stage:
                for bank in [x, y]:
                    for port in range(111):
                        consume(['PAID_PORT_ROUTE', stage, bank*111+port, port, 'ENTRY'])
            begin = at
            paid = Counter()
            for i, e in enumerate(word['records']):
                kind, r = e[:2]
                d = mapping[r]
                if kind == 'ADD':
                    consume(['ADD', d, mapping[e[2]], ['LOCAL', stage, e[3], i]])
                elif kind == 'ERASE':
                    consume(['OWNED_CLEAR', d, e[2], ['LOCAL', stage, i]])
                elif kind == 'INIT':
                    consume(['OWNED_ZERO_HEADER', d, e[2], stage])
                elif kind == 'Q':
                    a, b, rank = e[2:]
                    consume(['QUERY', d, rank, ['LOCAL_INVERSE', stage, a, b, i]])
                    paid[rank] += 1
                else:
                    need(kind == 'ZERO_Q', 'Local event opcode')
                    consume(['WHOLE_ZERO_FRAME', d, *e[2:], stage])
            j = controller['invoice']['thick_stages'].index(stage)
            actual_calls.append(dict(stage=stage, pair=pair, source_bank=x, target_bank=y,
                old_direction_inverse=reverse, new_direction_inverse=True,
                helper_old_owner_begin=3552+436*j, core_begin=begin, core_end=at,
                owned_global_indices=owned, retained_helper_count=415,
                paid={str(k): v for k, v in paid.items()}))
            if stage:
                for bank in [x, y]:
                    for port in range(111):
                        consume(['PAID_PORT_ROUTE', stage, bank*111+port, port, 'RETURN'])
        elif op == 'QUERY_SHEAR':
            for port in range(111):
                add(n, x*111+port, ['THIN_COPY', stage, port])
                consume(['QUERY', n, 1, ['THIN', stage, port]])
                add(y*111+port, n, ['THIN_DELIVER', stage, port])
                consume(['OWNED_CLEAR', n, None, ['THIN', stage, port]])
        elif op == 'IDLE':
            _, pair, stages = event
            need(len(stages) == len(set(stages)), 'Disjoint idle stage blocks')
            need(set(stages) <= set(controller['invoice']['thick_stages']), 'Actual full-stage idle blocks')
            for bank in [2*pair, 2*pair+1]:
                for port in range(111):
                    consume(['QUERY', bank*111+port, 7*len(stages), ['WHOLE_IDLE', stages, port]])
        else:
            scalar(op, event[1], event[2], 'BRIDGE' if op == 'ADD' else 'FINAL_SWAP')
    for op, d, s in controller['boundaries']['left_program']:
        scalar(op, d, s, 'LEFT_BOUNDARY')
    for r in owned:
        consume(['OWNED_CLEAR', r, None, 'GLOBAL_EXIT_TEARDOWN'])
    need(at == len(events) and actual_calls == calls, 'Complete stream and exact call boundaries')
    return n, owned, retired, retained, helper_maps


def forward(events, descriptors, n, owned):
    rows = [1 << i for i in range(n + len(owned))]
    norms = [1] * len(rows)
    versions, epochs = [0]*len(rows), [0]*len(rows)
    prefix = sha256()
    paid, counts = Counter(), Counter()
    live, episodes = {}, []
    peak, peak_live, query = 1, 0, 0
    for at, event in enumerate(events):
        op, d = event[:2]
        counts[op] += 1
        need(0 <= d < len(rows) or op == 'PAID_PORT_ROUTE', 'Global owner range')
        if op == 'ADD':
            s = event[2]
            need(0 <= s < len(rows) and s != d, 'Distinct valid ADD operands')
            rows[d] ^= rows[s]
            norms[d] += norms[s]
            peak = max(peak, norms[d])
            versions[d] += 1
            if d >= n and d not in live:
                label = event[3]
                need(label[0] in ['LOCAL', 'THIN_COPY'], 'Owned lifetime starts in a known macro')
                live[d] = (at, label[1], label[0] == 'THIN_COPY')
                peak_live = max(peak_live, len(live))
        elif op == 'OWNED_CLEAR':
            need(d >= n, 'No public erasure')
            rows[d] = norms[d] = 0
            versions[d] += 1
            epochs[d] += 1
            if d in live:
                begin, stage, thin = live.pop(d)
                item = dict(owner=d, stage=stage, begin=begin, end=at)
                if thin:
                    item['kind'] = 'THIN'
                episodes.append(item)
        elif op == 'QUERY':
            need(query < len(descriptors) and 0 < event[2] <= 127, 'Valid paid query')
            item = descriptors[query]
            expected = dict(event=at, prefix_sha256=prefix.hexdigest(), owner=d,
                version=versions[d], epoch=epochs[d], rank=event[2], detail=event[3], RAW_hex=hex(rows[d]))
            need(all(item.get(k) == v for k, v in expected.items()), 'Complete chronological query descriptor')
            paid[event[2]] += 1
            versions[d] += 1
            query += 1
        elif op in ['OWNED_ZERO_HEADER', 'WHOLE_ZERO_FRAME']:
            need(rows[d] == 0 and (op == 'WHOLE_ZERO_FRAME' or d >= n), 'Whole-zero precondition')
        else:
            need(op == 'PAID_PORT_ROUTE', 'Global opcode')
        prefix.update((json.dumps(event, separators=(',', ':')) + '\n').encode())
    need(query == len(descriptors) and not live, 'All queries and lifetimes consumed')
    need(rows == [1 << i for i in range(n)] + [0]*len(owned), 'Complete RAW and dirty endpoint')
    return dict(paid=dict(paid), counts=dict(counts), episodes=episodes, peak_live=peak_live,
                majorant=str(peak), majorant_bits=peak.bit_length(), stream_sha256=prefix.hexdigest())


def reverse_raw(events, n, own):
    rows = [1 << i for i in range(n + own)]
    for e in reversed(events):
        if e[0] == 'ADD':
            rows[e[2]] ^= rows[e[1]]
        elif e[0] == 'OWNED_CLEAR':
            rows[e[1]] = 0
    need(rows == [1 << i for i in range(n)] + [0]*own, 'Independent transpose RAW and dirty endpoint')
    return (n + own)**2


def interfaces(word):
    frames = read('FRAMES.json')['frames']
    witnesses = []
    denominator = 2
    for port in range(111):
        a, line = word['start'][port], word['final'][port]
        complement, b = word['start'][111+port], word['final'][111+port]
        need(a == 1 and b == 0, 'Actual full-to-line and complement-to-zero interfaces')
        u, space = frames[str(line)]['B'], frames[str(complement)]['B']
        need(len(u) == 1 and len(space) == 7, 'One central and seven stage directions')
        need(all(sum(x*y for x, y in zip(u[0], row)) == 0 for row in space),
             'The two main interface spaces are orthogonal')
        columns = u + space
        matrix = [[Fraction(columns[j][i]) for j in range(8)] for i in range(8)]
        augmented = [row[:] + [Fraction(i == j) for j in range(8)] for i, row in enumerate(matrix)]
        for j in range(8):
            pivot = next((i for i in range(j, 8) if augmented[i][j]), None)
            need(pivot is not None, 'Complete invertible port normalizer')
            augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
            value = augmented[j][j]
            augmented[j] = [x/value for x in augmented[j]]
            for i in range(8):
                if i != j:
                    value = augmented[i][j]
                    augmented[i] = [x-value*y for x, y in zip(augmented[i], augmented[j])]
        inverse = [row[8:] for row in augmented]
        for left, right in [(matrix, inverse), (inverse, matrix)]:
            need(all(sum(left[i][k]*right[k][j] for k in range(8)) == (i == j)
                     for i in range(8) for j in range(8)), 'Both port inverse identities')
        norm = sum(x*x for x in u[0])
        projection = [[Fraction(u[0][i]*u[0][j], norm) for j in range(8)] for i in range(8)]
        need(all(sum(projection[i][k]*matrix[k][j] for k in range(8))
                 == (matrix[i][j] if j == 0 else 0) for i in range(8) for j in range(8)),
             'Exact central-line conjugation')
        for table in [matrix, inverse, projection]:
            for row in table:
                for value in row:
                    denominator = lcm(denominator, value.denominator)
        witnesses.append(dict(port=port, line=line, complement=complement,
            normalizer=[[str(x) for x in row] for row in matrix],
            inverse=[[str(x) for x in row] for row in inverse]))
    return dict(paired_address_halves=2, port_count=len(witnesses),
                normalizer_denominator_lcm=denominator, ports=witnesses)


def physical(controller):
    # Encode (monomial mask, output bank) in one integer. Reverse propagation
    # gives the transpose over the group algebra of commuting involutions.
    rows = [{i} for i in range(32)]

    def shift(row, mask):
        return {x ^ (mask << 5) for x in row}

    def scalar(program):
        for op, d, s in reversed(program):
            if op == 'ADD':
                rows[s] ^= rows[d]
            else:
                need(op == 'SWAP', 'Physical boundary opcode')
                rows[d], rows[s] = rows[s], rows[d]

    scalar(controller['boundaries']['left_program'])
    for event in reversed(controller['physical_events']):
        op = event[0]
        if op in ['LOCAL', 'QUERY_SHEAR']:
            _, stage, pair, rev = event
            x, y = (2*pair+1, 2*pair) if rev else (2*pair, 2*pair+1)
            if op == 'LOCAL':
                rows[x] = shift(rows[x], 1 << (stage+1))
                rows[y] = shift(rows[y], 1 << (stage+1))
            rows[x] ^= shift(rows[y], 1)
        elif op == 'IDLE':
            mask = sum(1 << (s+1) for s in event[2])
            for bank in [2*event[1], 2*event[1]+1]:
                rows[bank] = shift(rows[bank], mask)
        else:
            scalar([event])
    scalar(controller['boundaries']['right_program'])
    want = [{(mask << 5) | i} for i, mask in enumerate(controller['diagonal'])]
    need(rows == want, 'Every physical controller coefficient')
    need(all(mask & 1 for mask in controller['diagonal']), 'Every main target includes its central line')
    return [1 + 7*(mask >> 1).bit_count() for mask in controller['diagonal']]


def targets(word, main_ranks, maps, records, n):
    expected = {111*bank+p: rank for bank, rank in enumerate(main_ranks) for p in range(111)}
    labels = {111*bank+p: dict(original_owner=111*bank+p, rank=rank,
        matcher='MAIN_BANK_'+str(bank), port=p,
        operator='D_(P_line+selectedorthogonalstageblocks)',
        route_pair_required_in_generic_job_matching=True)
        for bank, rank in enumerate(main_ranks) for p in range(111)}
    dims = {int(k): v['dim'] for k, v in read('FRAMES.json')['frames'].items()}
    stages = read('CONTROLLER.json')['invoice']['thick_stages']
    required_routes = set(expected)
    for stage, mapping in zip(stages, maps):
        for r in list(range(222, 658)) + [684]:
            if r in word['owned']:
                continue
            a, b = word['start'][r], word['final'][r]
            need((a, b) in [(1, 0), (1, 508), (508, 0)], 'Native-audited helper endpoint class')
            owner = mapping[r]
            need(owner not in expected, 'One independent target for each public input')
            expected[owner] = abs(dims[a] - dims[b])
            if (a, b) == (1, 0):
                labels[owner] = dict(original_owner=owner, rank=8,
                    matcher='IDENTITY_FULL8', native_frame=1,
                    route_pair_required_in_generic_job_matching=False)
            else:
                labels[owner] = dict(original_owner=owner, rank=4,
                    matcher='FRAME508_COMPLEMENT' if a == 1 else 'FRAME508',
                    split='full8_to_frame508' if a == 1 else 'frame508_to_zero',
                    native_source_frame=a, native_target_frame=b,
                    route_pair_required_in_generic_job_matching=True)
                if a == 508:
                    labels[owner]['stage'] = stage
            if (a, b) != (1, 0):
                required_routes.add(owner)
    need(set(expected) == set(range(n)), 'Complete target owner coverage')
    actual = {r['original_owner']: r['rank'] for r in records}
    need(len(actual) == len(records) == n and actual == expected, 'Exact bijective target ledger')
    need({r['original_owner']: r for r in records} == labels, 'Every target native interface and matcher')
    need({r['original_owner'] for r in records if r['route_pair_required_in_generic_job_matching']}
         == required_routes, 'Every required target route pair')
    return Counter(expected.values()), 2*len(required_routes)


def fees(result, invoice, required_routes, matcher, ordinary):
    n, own, queries = invoice['originals'], invoice['owned_allocated'], invoice['QUERYs']
    counts = result['counts']
    scans = sum(counts[k] for k in ['ADD', 'OWNED_CLEAR', 'OWNED_ZERO_HEADER', 'WHOLE_ZERO_FRAME']) + 2*own
    parking = 4*(n+own)*queries
    coefficient_terms = 0
    for names, count in [(('forward', 'inverse'), 72), (('new_target_forward', 'new_target_inverse'), 36)]:
        coefficient_terms += 2*count*sum(Fraction(x) != 0 for name in names for row in matcher[name] for x in row)
    declared = ordinary['fee_bounds']['base_counts']
    route_charge = declared['internal_and_wholejob_routes']
    need(route_charge >= counts['PAID_PORT_ROUTE'] + required_routes, 'Complete internal and target route charge')
    dimension = queries*(32*127**2 + 8*127**3)
    total = scans + parking + route_charge + sum(counts.values()) + dimension + coefficient_terms
    expected = dict(raw_records=sum(counts.values()), new_matcher_coefficient_terms=coefficient_terms,
        all_XOR_CLEAR_INIT_zeroheader_passes=scans, parent_parking_FIELD_passes=parking,
        internal_and_wholejob_routes=route_charge, coarse_primitive_count_with_dimension_work=total,
        strict_upper=2**64, all_owned_allocated=own, owned_productive_credit=0)
    need(declared == expected and total < 2**64, 'Complete positive finite bill')
    need(result['majorant_bits'] < 1024, 'Global precision envelope')
    return dict(primitive_upper_bound=total, required_target_routes=required_routes,
        retained_route_allowance=route_charge-counts['PAID_PORT_ROUTE'],
        extra_retired_route_allowance=route_charge-counts['PAID_PORT_ROUTE']-required_routes,
        coefficient_terms=coefficient_terms, dimension_work=dimension, parking=parking, scans=scans)


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid boundary accepted')


def run():
    source_count = authenticate()
    word, controller, calls = read('WORD.json.gz'), read('CONTROLLER.json'), read('CALLS.json')
    events = [json.loads(line) for line in gzip.decompress((SOURCE/'GLOBAL.jsonl.gz').read_bytes()).splitlines()]
    descriptors = read('SOURCE-DESCRIPTORS.json.gz')
    n, owned, retired, retained, maps = bind(events, word, controller, calls)
    result = forward(events, descriptors, n, owned)
    transpose = reverse_raw(events, n, len(owned))
    port_interfaces = interfaces(word)
    main = physical(controller)
    target_records = read('TARGET-OWNERS.json')
    target_counts, routes = targets(word, main, maps, target_records, n)
    invoice = read('INVOICE.json')
    need(result['paid'] == {int(k): v for k, v in invoice['paid'].items()}, 'Paid invoice')
    need(target_counts == {int(k): v for k, v in invoice['targets'].items()}, 'Target invoice')
    need(sum(result['paid'].values()) == invoice['QUERYs'] == 56223, 'All paid calls counted')
    need(sum(k*v for k, v in target_counts.items()) - sum(k*v for k, v in result['paid'].items())
         == invoice['rank_surplus'] == 753, 'Complete rank surplus')
    need(invoice['originals'] == n and invoice['owned_allocated'] == len(owned)
         and invoice['owned_output_credit'] == 0, 'No owned productive credit')
    need(result['episodes'] == read('PRIVATE-EPISODES.json'), 'Every exact owned episode')
    glob = read('GLOBAL-RESULT.json')
    for a, b in [('counts', 'operation_counts'), ('majorant', 'majorant'),
                 ('majorant_bits', 'majorant_bits'), ('stream_sha256', 'canonical_stream_sha256')]:
        need(result[a] == glob[b], 'Exact global receipt: ' + b)
    need(glob['retained_old_ids'] == retained and glob['retired_original_old_ids'] == sorted(retired),
         'Every retired original is debited')
    fee = fees(result, invoice, routes, read('MATCHER.json'), read('ORDINARY-RESULT.json'))
    controls = {}
    bad = descriptors.copy(); bad[0] = dict(bad[0], detail=['FALSE_GEOMETRY'])
    controls['false_query_geometry'] = reject(lambda: forward(events, bad, n, owned))
    bad_epoch = descriptors.copy(); bad_epoch[0] = dict(bad_epoch[0], epoch=bad_epoch[0]['epoch']+1)
    controls['stale_epoch'] = reject(lambda: forward(events, bad_epoch, n, owned))
    bad_events = events.copy(); ix = next(i for i, e in enumerate(events) if e[0] == 'PAID_PORT_ROUTE')
    bad_events[ix] = list(bad_events[ix]); bad_events[ix][-1] = 'FALSE_RETURN'
    controls['wrong_port_route'] = reject(lambda: bind(bad_events, word, controller, calls))
    controls['dirty_input_leak'] = reject(lambda: reverse_raw([['ADD', 0, n, 'CONTROL']] + events, n, len(owned)))
    bad_targets = target_records.copy(); bad_targets[1] = dict(bad_targets[1], original_owner=0)
    controls['duplicate_target_owner'] = reject(lambda: targets(word, main, maps, bad_targets, n))
    bad_matcher = target_records.copy()
    target_index = next(i for i, r in enumerate(target_records) if r.get('split'))
    bad_matcher[target_index] = dict(bad_matcher[target_index], native_target_frame=0)
    controls['wrong_target_normalizer'] = reject(lambda: targets(word, main, maps, bad_matcher, n))
    bad_controller = dict(controller, diagonal=controller['diagonal'].copy())
    bad_controller['diagonal'][0] ^= 2
    controls['wrong_stage_operator'] = reject(lambda: physical(bad_controller))
    bad_word = dict(word, start=word['start'].copy())
    bad_word['start'][112] = word['start'][111]
    controls['wrong_port_complement'] = reject(lambda: interfaces(bad_word))
    bad_fee = read('ORDINARY-RESULT.json')
    bad_fee['fee_bounds']['base_counts']['new_matcher_coefficient_terms'] -= 1
    controls['omitted_matcher_term'] = reject(lambda: fees(result, invoice, routes, read('MATCHER.json'), bad_fee))
    controls['public_erasure'] = reject(lambda: forward([['OWNED_CLEAR', 0, None, 'CONTROL']], [], n, owned))
    return dict(status='PASS_G20_GLOBAL_CALLER_BOUNDARY', source_files=source_count,
        source_head='829d01fc031f7323ffcfa423fdfd1f24dcbe3190', events=len(events),
        input_columns=n+len(owned), independent_inputs=n, owned=len(owned),
        scalar_endpoint_coefficients=transpose, full_calls=len(calls), paid_queries=len(descriptors),
        owned_episodes=len(result['episodes']), peak_live_owned=result['peak_live'],
        majorant=result['majorant'], majorant_bits=result['majorant_bits'],
        stream_sha256=result['stream_sha256'], main_target_ranks=main, targets=dict(target_counts),
        paid=result['paid'], rank_surplus=753, finite_fee=fee, negative_controls=controls,
        port_interfaces=port_interfaces,
        limits=['The native proof is an authenticated dependency, not replayed here.',
                'Finite physical primitive charges do not prove their tape-time tariffs.',
                'Compiler, stock, precision, analytic and compatible outer obligations remain.',
                'No new kappa, selected-frontier update or independent human acceptance.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_bytes()), 'Exact retained result')
    print(result['status'])


if __name__ == '__main__':
    main()
