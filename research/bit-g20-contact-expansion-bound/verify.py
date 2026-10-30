"""Check all G20 contact expansion certificates with integer arithmetic.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from math import lcm
import gzip
import hashlib
import heapq
import json
import struct

ROOT = Path(__file__).resolve().parent
SCALE = 10**6

def need(value, message):
    if not value:
        raise ValueError(message)

def read(name):
    data = (ROOT/name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

def powers(invoice):
    ranks = set(range(1, 8)) | {int(x) for side in ('paid', 'targets') for x in invoice[side]}
    # Decimal only proposes the integers. Integer powers prove every bound.
    with localcontext() as ctx:
        ctx.prec = 45
        out = {r: int(Decimal(SCALE)*Decimal(r)**(Decimal(9963)/10000)) for r in ranks}
    scale_power = SCALE**10000
    for r, value in out.items():
        exact = scale_power*r**9963
        need(value**10000 <= exact < (value+1)**10000, 'Exact rational tariff interval')
    return out

def integer_rows(rows):
    out = []
    for row in rows:
        row = list(map(Fraction, row))
        denominator = lcm(*(x.denominator for x in row))
        out.append([int(x*denominator) for x in row])
    return out

def row_space(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for pivot, old in sorted(basis.items()):
            c = row[pivot]
            row = [a-c*b for a, b in zip(row, old)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        c = row[pivot]
        row = [x/c for x in row]
        for i, old in list(basis.items()):
            c = old[pivot]
            basis[i] = [a-c*b for a, b in zip(old, row)]
        basis[pivot] = row
    return tuple(tuple(row) for _, row in sorted(basis.items()))

def model():
    for pin in read('INPUTS.json'):
        data = (ROOT/pin['local']).read_bytes()
        if pin['decode_gzip']:
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'Exact pinned source bytes')
    invoice = read('INVOICE.json')
    weights = powers(invoice)
    frames = read('FRAMES.json.gz')['frames']
    codes = sorted(map(int, frames))
    need(len(codes) == 645, 'Complete projector catalogue')
    dims = {i: frames[str(i)]['dim'] for i in codes}
    a = {i: integer_rows(frames[str(i)]['A']) for i in codes}
    b = {i: integer_rows(frames[str(i)]['B']) for i in codes}
    spaces = {i: row_space(b[i]) for i in codes}
    need(len(set(spaces.values())) == len(codes), 'No unpriced alias frame is omitted')
    need(all(len(spaces[i]) == dims[i] and len(row_space(a[i])) == 8-dims[i] and all(sum(x*y for x, y in zip(u, v)) == 0 for u in a[i] for v in b[i]) for i in codes), 'Exact complementary rational frame spaces')
    adjacency = {i: [] for i in codes}
    for i in codes:
        for j in codes:
            rank = dims[j]-dims[i]
            if 0 < rank < 8 and all(sum(x*y for x, y in zip(u, v)) == 0 for u in b[i] for v in a[j]):
                adjacency[i].append((j, rank))
                adjacency[j].append((i, rank))
    need(sum(map(len, adjacency.values())) == 52624, 'All proper nested projector edges')
    distances = {}
    for source in codes:
        ds = [10**18]*(max(codes)+1)
        ds[source] = 0
        queue = [(0, source)]
        while queue:
            cost, u = heapq.heappop(queue)
            if cost != ds[u]:
                continue
            for v, rank in adjacency[u]:
                value = cost+weights[rank]
                if value < ds[v]:
                    ds[v] = value
                    heapq.heappush(queue, (value, v))
        # These potentials alone prove the lower bound for every finite path.
        need(all(0 <= ds[v] < 10**18 for v in codes), 'Finite nonnegative distances')
        need(all(ds[v] <= ds[u]+weights[r] for u in codes for v, r in adjacency[u]), 'Path lower-bound potentials')
        distances[source] = ds
    word = read('WORD.json.gz')
    program, owned = word['records'], set(word['owned'])
    values = [1 << i for i in range(660)]
    state = word['start'][:]
    vertices, chains, mutable = {}, defaultdict(list), set()
    for i in range(658):
        if i not in owned:
            vertices[-1, i] = state[i]
            chains[i].append((-1, i))
    public_paid, all_paid = Counter(), Counter()
    for k, event in enumerate(program):
        op, d = event[:2]
        if op == 'ADD':
            s, frame = event[2:]
            need(state[d] == state[s] == frame, 'Actual common frame')
            values[d] ^= values[s]
            vertices[k, -1] = frame
            for i in (d, s):
                if i not in owned:
                    chains[i].append((k, -1))
            if d not in owned and s not in owned:
                mutable.add((k, -1))
        elif op == 'ERASE':
            need(d in owned, 'Only owned erasure')
            values[d] = 0
            state[d] = event[2]
        elif op == 'INIT':
            need(d in owned and values[d] == 0, 'Whole-zero initialization')
            state[d] = event[2]
        else:
            need(op in ('Q', 'ZERO_Q'), 'Source opcode')
            before, after, rank = event[2:]
            need(state[d] == before and (after, rank) in adjacency[before], 'Actual proper nested query')
            if op == 'ZERO_Q':
                need(values[d] == 0, 'Whole-zero free query')
            else:
                all_paid[rank] += 1
                if d not in owned:
                    public_paid[rank] += 1
            state[d] = after
        need(d in owned or values[d] != 0, 'No free public zero path is omitted')
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(660)]
    need(values == expected and state == word['final'], 'Every RAW/DIRTY scalar endpoint')
    for i in chains:
        vertices[len(program), i] = word['final'][i]
        chains[i].append((len(program), i))
    edges = Counter(tuple(sorted((u, v))) for chain in chains.values() for u, v in zip(chain, chain[1:]))
    need(len(mutable) == 17060 and sum(edges.values()) == 37299 and sum(public_paid.values()) == 2862, 'Complete contact graph census')
    calls = read('CALLS.json')
    need(len(calls) == 18 and all(c['new_direction_inverse'] and Counter({int(r): n for r, n in c['paid'].items()}) == all_paid for c in calls), 'All eighteen exact source call profiles')
    old_upper = sum(n*(weights[r]+1) for r, n in public_paid.items())
    baseline = sum(n*distances[vertices[u]][vertices[v]] for (u, v), n in edges.items())
    need(old_upper-baseline == 2862, 'Uniform path-rounding gap')
    return codes, weights, vertices, mutable, edges, distances, invoice, old_upper-baseline

def network(alpha, vertices, mutable, edges, dist):
    active = sorted(k for k in mutable if vertices[k] != alpha)
    positions = {k: i for i, k in enumerate(active)}
    count = len(active)
    delta, arcs = [0]*count, []
    for (u, v), mult in edges.items():
        i, j = positions.get(u), positions.get(v)
        a, b = vertices[u], vertices[v]
        old = dist[a][b]
        if i is None and j is None:
            continue
        if i is None:
            delta[j] += mult*(dist[a][alpha]-old)
        elif j is None:
            delta[i] += mult*(dist[alpha][b]-old)
        else:
            d10, d01 = dist[alpha][b], dist[a][alpha]
            capacity = mult*(d10+d01-old)
            need(capacity >= 0, 'Metric submodularity')
            delta[i] += mult*(d10-old)
            delta[j] -= mult*d10
            if capacity:
                arcs.append((i, j, capacity))
    source, sink = count, count+1
    for i, d in enumerate(delta):
        if d > 0:
            arcs.append((source, i, d))
        elif d < 0:
            arcs.append((i, sink, -d))
    return arcs, source, sink, sum(min(0, d) for d in delta)

def flow_check(arcs, source, sink, constant, pairs):
    balance, seen = [0]*(sink+1), set()
    for index, flow in pairs:
        need(index not in seen and 0 <= index < len(arcs), 'Unique valid flow arc')
        seen.add(index)
        u, v, capacity = arcs[index]
        need(0 < flow <= capacity, 'Integer flow capacity')
        balance[u] += flow
        balance[v] -= flow
    need(all(balance[i] == 0 for i in range(source)), 'Internal flow conservation')
    need(balance[source] == -balance[sink] and balance[source]+constant == 0, 'Feasible flow proves every expansion has nonnegative lower cost')
    return balance[source]

def main():
    codes, weights, vertices, mutable, edges, dist, invoice, gap = model()
    data = gzip.decompress((ROOT/'FLOWS.bin.gz').read_bytes())
    need(data[:8] == b'G20FLOW1', 'Flow certificate format')
    offset = 8
    flow_count = 0
    for alpha in codes:
        label, count = struct.unpack_from('<II', data, offset)
        offset += 8
        need(label == alpha, 'Every catalogue frame appears once and in order')
        pairs = list(struct.iter_unpack('<II', data[offset:offset+8*count]))
        offset += 8*count
        arcs, source, sink, constant = network(alpha, vertices, mutable, edges, dist)
        flow_check(arcs, source, sink, constant, pairs)
        if alpha == codes[0]:
            broken = pairs[:]
            broken[0] = (broken[0][0], broken[0][1]+1)
            try:
                flow_check(arcs, source, sink, constant, broken)
            except ValueError:
                pass
            else:
                raise ValueError('Corrupted flow accepted')
        flow_count += count
    need(offset == len(data), 'No missing or extra certificate bytes')
    moment_upper = sum(n*(weights[int(r)]+1) for r, n in invoice['targets'].items())-sum(n*weights[int(r)] for r, n in invoice['paid'].items())
    changed_upper = moment_upper+18*gap
    need(changed_upper == -46255824, 'Strict complete caller loss at C=37/10000')
    # This invoice structure proves strict monotonicity after division by 8^t.
    targets = {int(r): n for r, n in invoice['targets'].items()}
    paid = {int(r): n for r, n in invoice['paid'].items()}
    high = {r: n for r, n in paid.items() if r > 7}
    need(all(r > 8 and targets[r+1] == n for r, n in high.items()), 'All high paid jobs have their retained next-rank targets')
    need(set(targets) == {4, 8, 127} | {r+1 for r in high} and targets[127] > targets[4] and 127 > 16, 'Uniform monotonicity witness')
    print(json.dumps({'status': 'PASS_G20_ALL_CATALOGUE_EXPANSIONS', 'frames': len(codes), 'mutable_contacts': len(mutable),
                      'flow_entries': flow_count, 'local_gain_upper': '2862/1000000',
                      'complete_moment_upper': '-46255824/1000000', 'saving_test': '37/10000',
                      'certificate_sha256': hashlib.sha256(data).hexdigest()}, sort_keys=True))

if __name__ == '__main__':
    main()
