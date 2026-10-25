#!/usr/bin/env python3
"""Check the forward BIT helper-query interface on the retained source."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/kappa-rebuild/bit/sources/pr589-regenerated'
WORD_HASH = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
LOCAL = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mul(a, b):
    result = [[F(0)] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        result[i][j] += x * y
    return result


def rank(a):
    rows = [list(map(F, row)) for row in a]
    pivot = 0
    for column in range(len(rows[0])):
        index = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if index is None:
            continue
        rows[pivot], rows[index] = rows[index], rows[pivot]
        value = rows[pivot][column]
        rows[pivot] = [x/value for x in rows[pivot]]
        for i in range(pivot+1, len(rows)):
            value = rows[i][column]
            rows[i] = [x-value*y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def block(a):
    n = len(a)
    return [[a[i % n][j % n] if i // n == j // n else F(0)
             for j in range(2*n)] for i in range(2*n)]


def partial(p):
    n = len(p)
    return [[(F(i % n == j % n) - p[i % n][j % n]
              if i // n == j // n else p[i % n][j % n])
             for j in range(2*n)] for i in range(2*n)]


def census(word, records):
    writes = Counter()
    reads = Counter()
    first = {}
    for index, (op, a, b, c, d, tag) in enumerate(records):
        if op == 0 and 222 <= a < 661 and a not in first:
            first[a] = dict(owner=a, source_event=index, old_frame=b,
                            new_frame=c, rank=d, prior_writes=writes[a],
                            prior_reads=reads[a], roots=word['frames'][c])
        elif op == 1:
            writes[a] += 1
            reads[b] += 1
    need(len(first) == 439, 'Every helper has a first MOVE')
    need(all(row['prior_writes'] == 0 and row['old_frame'] == 0
             for row in first.values()), 'Every first helper argument is its original input')
    selected = sorted((row for row in first.values() if row['rank'] == 1),
                      key=lambda row: row['source_event'])
    need(len(selected) == 286, 'The source has 286 first rank-one queries')
    for row in selected:
        need(len(row['roots']) == 1, 'Each selected frame is one source line')
        row['port'] = row['roots'][0]
    groups = defaultdict(list)
    for row in selected:
        groups[row['port']].append(row['owner'])
    need(len(groups) == 111 and min(map(len, groups.values())) == 2,
         'Every port has at least two distinct raw helper queries')
    return first, selected, dict(sorted(groups.items()))


def normalizers(word, frames):
    identity = eye(8)
    central = [[F(i == j == 0) for j in range(8)] for i in range(8)]
    query, full = partial(central), partial(identity)
    rows = []
    for port, source_root in enumerate(word['lines']):
        u = [F(x, 2) for x in source_root]
        need(sum(x*x for x in u) == 1, 'The root has unit norm')
        v = [u[i] - F(i == 0) for i in range(8)]
        norm = sum(x*x for x in v)
        k = identity if not norm else [[F(i == j) - 2*v[i]*v[j]/norm
                                       for j in range(8)] for i in range(8)]
        p = [[x*y for y in u] for x in u]
        complement = [[F(i == j)-p[i][j] for j in range(8)] for i in range(8)]
        final_y = frames[str(word['final'][111+port])]
        need(word['start'][port] == port+2 and word['start'][111+port] == 0
             and word['final'][port] == 1, 'The actual main entrance and X exit frames match')
        need(final_y['dim'] == 7 and rank(final_y['B']) == 7
             and all(sum(F(x)*y for x, y in zip(row, u)) == 0 for row in final_y['B']),
             'The actual Y exit is the exact complementary frame')
        need(mul(full, partial(p)) == partial(complement), 'The actual main diagonal is D_(I-P)')
        need(mul(partial(complement), partial(p)) == full, 'The actual main shear is D_(I-P) Q')
        frame = frames[str(port + 2)]
        basis = frame['B']
        need(frame['dim'] == 1 and len(basis) == 1, 'The actual first frame has rank one')
        z = list(map(F, basis[0])); scale = sum(x*x for x in z)
        need([[x*y/scale for y in z] for x in z] == p, 'The native frame uses the same projector')
        need(mul(k, k) == identity and [row[0] for row in k] == u,
             'The rational Householder map is its own inverse')
        need(mul(mul(k, central), k) == p, 'The head normalizer gives the source projector')
        big_k, event = block(k), partial(p)
        need(mul(event, big_k) == mul(big_k, query), 'E K = K Q exactly')
        need(mul(full, big_k) == mul(big_k, full), 'K commutes with the full helper endpoint')
        need(mul(query, query) == eye(16), 'The BIT common query is an involution')
        rows.append(dict(port=port, K=[[str(x) for x in row] for row in k],
                         nonidentity=k != identity))
    return rows


def stage_routes(word):
    path = ROOT / 'research/kappa-rebuild/bit/BIT-P3-NATIVE-BINDING.json'
    raw = path.read_bytes()
    binding = json.loads(raw)
    local = [[F(i == j and i < 8) for j in range(15)] for i in range(15)]
    result = []
    for row in binding['ports']:
        port = row['port']
        rho = [[F(x) for x in line] for line in row['chart_15']]
        root = list(map(F, word['lines'][port]))
        p = [[root[i]*root[j]/4 if i < 8 and j < 8 else F(0)
              for j in range(15)] for i in range(15)]
        target = [[p[i][j]+F(i == j and i >= 8) for j in range(15)] for i in range(15)]
        need(mul(rho, rho) == eye(15), 'The actual port route is an involution')
        need(mul(mul(rho, p), rho) == p, 'The actual port route fixes the query projector')
        need(mul(mul(rho, local), rho) == target,
             'The actual port route sends the helper target to P plus the fresh seven-plane')
        need(mul(block(rho), partial(p)) == mul(partial(p), block(rho)),
             'The held helper query commutes with the actual address route')
        need(mul(mul(block(rho), partial(local)), block(rho)) == partial(target),
             'The helper output is the exact routed native rank-eight job')
        result.append(dict(port=port, local_head_axes=list(range(8)),
                           fresh_stage_axes=list(range(8, 15)),
                           rho_sha256=sha256(json.dumps(row['chart_15']).encode()).hexdigest()))
    need(sorted(row['port'] for row in result) == list(range(111)),
         'Every actual native port route is checked exactly once')
    return dict(binding_sha256=sha256(raw).hexdigest(), ports=result,
                selected_helpers=222, added_native_children={},
                added_cover_route_maps_per_fresh_stage=666,
                input='rho_(port,stage) xi', observation='Q_port xi',
                output='D_(P_port+B_stage) xi = Q_port D_Bstage xi',
                proof='rho is used at the helper input, held observation, and helper output. It fixes P_port and conjugates the source local rank-eight projector to P_port+B_stage. The source scalar identity accepts the separately routed inputs. The same15-coordinate identities embed at each fresh stage with all other coordinates fixed.')


def replay(word, frames, records, selected, hoist, fault=None, input_rows=None):
    slots = {row['source_event']: (index, row) for index, row in enumerate(selected)}
    count = len(selected)
    total = 662 + 2*count
    initial = input_rows or [1 << i for i in range(661)]
    first_owned_column = max(row.bit_length() for row in initial)
    values = list(initial) + [1 << (first_owned_column+i) for i in range(total-661)]
    current = list(word['start']) + [-1]*(total-661)
    values[661] = 0
    paid = Counter()
    if hoist:
        for index, row in enumerate(selected):
            raw, observation = 662+index, 662+count+index
            if fault != 'dirty_owned_input' or index:
                values[raw] = 0
            values[observation] = 0
            values[raw] ^= values[row['owner']]
            current[raw] = row['new_frame']
            paid[1] += 1
            values[observation] ^= values[raw]
            current[observation] = 'Q'
        if fault == 'wrong_held_input':
            values[662] ^= 1
    owned = None
    cuts = 0
    for event_index, (op, a, b, c, f, tag) in enumerate(records):
        if op == 0:
            need(current[a] == b, 'The MOVE entrance frame matches')
            if hoist and event_index in slots:
                index, row = slots[event_index]
                raw = 662+index
                need(values[a] == values[raw] == initial[a],
                     'The source cut equals the held original helper input')
                need(current[a] == 0 and current[raw] == c,
                     'The held raw field has the child exit frame')
                values[a], values[raw] = values[raw], values[a]
                if fault != 'wrong_swap_tags' or cuts:
                    current[a], current[raw] = current[raw], current[a]
                if fault != 'uncleared_raw' or cuts:
                    values[raw] = 0
                    current[raw] = -1
                cuts += 1
            else:
                current[a] = c
                paid[f] += 1
        elif op == 1:
            need(current[a] == current[b] == f, 'Every source ADD has its original common frame')
            need(a != b and a != owned, 'The scalar destination is legal')
            if c & 1:
                values[a] ^= values[b]
        elif op == 2:
            need(owned is None and b == 661 and values[b] == 0 and current[a] == c,
                 'The original owned COPY entrance is unchanged')
            owned = a
            values[b], current[b] = values[a], f
            paid[abs(frames[str(c)]['dim']-frames[str(f)]['dim'])] += 1
        elif op == 3:
            need(owned == a and b == 661 and values[b] == values[a],
                 'The original center value stays unchanged until its ERASE')
            values[b], current[b], owned = 0, -1, None
        else:
            raise ValueError('Unknown source opcode')
    expected = [initial[i] ^ (initial[i-111] if 111 <= i < 222 else 0)
                for i in range(661)]
    need(values[:661] == expected, 'All 661 independent source columns have the exact endpoint')
    need(current[:661] == word['final'] and owned is None, 'All source exit frames are unchanged')
    need(dict(paid) == LOCAL, 'The complete paid profile is unchanged')
    if hoist:
        for index, row in enumerate(selected):
            observation = 662+count+index
            need(values[observation] == initial[row['owner']], 'The normalized observation has its original input')
            if fault != 'uncleared_observation' or index:
                values[observation] = 0
                current[observation] = -1
        need(cuts == count and not any(values[661:]), 'Every owned field is cleared after use')
    return dict(all_persistent_inputs=661, owned_input_columns=total-661 if hoist else 1,
                replacement_cuts=cuts, paid=dict(sorted(paid.items())),
                original_ADDs=sum(event[0] == 1 for event in records),
                original_COPYs=sum(event[0] == 2 for event in records),
                endpoint_row_sha256=sha256(json.dumps(expected).encode()).hexdigest())


def feedback(groups):
    width = 439
    low = (1 << width)-1
    def q(row):
        return ((row & low) << width) | (row >> width)
    inputs = [1 << i for i in range(width)]
    observations = [q(row) for row in inputs]
    pairs = []
    for port, owners in groups.items():
        a, b = owners[0]-222, owners[1]-222
        old_a = inputs[a]
        inputs[b] ^= observations[a]
        observations[b] ^= old_a
        need(observations[b] == q(inputs[b]), 'The response update uses Q squared equal to identity')
        pairs.append([port, a+222, b+222])
    need(all(observations[i] == q(inputs[i]) for i in range(width)), 'All stored input/response pairs agree')
    for _, aa, bb in reversed(pairs):
        a, b = aa-222, bb-222
        inputs[b] ^= q(inputs[a])
    need(inputs == [1 << i for i in range(width)], 'The helper input change is invertible')
    return dict(disjoint_pairs=pairs, arbitrary_helper_columns=439,
                ring='F2[Q]/(Q^2-1)', response_update='xi_k += Q xi_h; observation_k += xi_h',
                endpoint='The source returns R times the changed helper input vector. A controller must retain or decode this full operator block; this check does not restore the original helper jobs for free.')


def reverse_census(records):
    values = [1 << i for i in range(661)]+[0]
    first = {}
    for index, (op, a, b, c, f, tag) in enumerate(reversed(records)):
        if op == 0 and 222 <= a < 661 and a not in first:
            first[a] = (f, (values[a] & ((1 << 222)-1)).bit_count())
        elif op == 1 and c & 1:
            values[a] ^= values[b]
        elif op == 3:
            values[b] = values[a]
        elif op == 2:
            values[b] = 0
    return dict(helpers=len(first), first_rank_one=sum(r == 1 for r, m in first.values()),
                helper_only_rows=sum(m == 0 for r, m in first.values()))


def run():
    raw = (SOURCE/'WORD.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == WORD_HASH, 'The source gzip hash matches')
    word = json.loads(gzip.decompress(raw))
    frame_bytes = (SOURCE/'records/frames.json').read_bytes()
    frames = json.loads(frame_bytes)['frames']
    record_bytes = (SOURCE/'records/249-records.bin').read_bytes()
    records = list(struct.iter_unpack('<6i', record_bytes))
    first, selected, groups = census(word, records)
    maps = normalizers(word, frames)
    routes = stage_routes(word)
    need(all(word['start'][i] == 0 and word['final'][i] == 1 for i in range(222, 661)),
         'All 439 helpers have the same full-rank endpoint')
    original = replay(word, frames, records, selected, False)
    hoisted = replay(word, frames, records, selected, True)
    paired_owners = {owner for owners in groups.values() for owner in owners[:2]}
    paired = [row for row in selected if row['owner'] in paired_owners]
    need(len(paired) == 222, 'The direct port interface has two helpers per port')
    paired_replay = replay(word, frames, records, paired, True)
    feedback_inputs = [1 << i for i in range(661)]
    for owners in groups.values():
        a, b = owners[:2]
        feedback_inputs[b] ^= 1 << (661+a)
    feedback_replay = replay(word, frames, records, paired, True, input_rows=feedback_inputs)
    controls = {}
    for fault in ('wrong_held_input', 'wrong_swap_tags', 'dirty_owned_input',
                  'uncleared_raw', 'uncleared_observation'):
        try:
            replay(word, frames, records, selected, True, fault)
        except ValueError as error:
            controls[fault] = str(error)
        else:
            raise ValueError('A bad hoist was accepted')
    count = len(selected)
    return dict(status='PASS_FORWARD_BIT_EARLY_HELPER_QUERY_INTERFACE',
                base='1ec1119972c9aefe42525172d07b332fcff81cb4',
                source_sha256={'WORD.json.gz': sha256(raw).hexdigest(),
                               'records/frames.json': sha256(frame_bytes).hexdigest(),
                               'records/249-records.bin': sha256(record_bytes).hexdigest()},
                independent_cold_helpers=439, scalar_first_departure_basis='I_439',
                selected_first_queries=selected, per_port_helpers=groups,
                common_query_normalizers=maps, routed_stage_interface=routes,
                original_replay=original, hoisted_replay=hoisted,
                added_paid_children={}, target_profile={8: 439},
                direct_port_interface=dict(selected_owners=sorted(paired_owners),
                    selected_queries=222, normalizer_maps=0, source_replay=paired_replay,
                    contract='At each port use its own Q=D_P. Both chosen helpers start with that exact Q. Their endpoint is D_I8=Q D_(I8-P).',
                    extra_ordinary_work=dict(owned_COPY=444, owned_CLEAR=888,
                                             whole_field_SWAP=222, owned_fields=444)),
                added_ordinary_work=dict(owned_COPY=2*count, owned_CLEAR=4*count,
                                         whole_field_SWAP=count, owned_fields=2*count,
                                         nonidentity_head_chart_maps=3*sum(maps[row['port']]['nonidentity'] for row in selected)),
                feedback=feedback(groups), feedback_source_replay=feedback_replay,
                reverse_first_departures=reverse_census(records),
                negative_controls=controls, new_kappa=False,
                limits='This is the forward native finite interface. Original scalar endpoint and chart replacement checks are exact on all source columns. The rational address identities bind the response and return maps. It does not prove a profitable controller, full cover hosting, ordinary-work precision, uniform compilation, or multiplication kappa.',
                credit='The BIT source is the retained PR589/PR555 construction. The held-query rescheduling follows PR5388 at commit568717635d8d11175a80024c9c596e16f54b1ea4. This BIT adaptation and its checker have substantial OpenAI Codex assistance.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
