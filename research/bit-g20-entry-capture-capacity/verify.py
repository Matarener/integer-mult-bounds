"""Check the complete G20 entry-kernel bound.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from pathlib import Path
import gzip
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent

def need(value, message):
    if not value:
        raise ValueError(message)

def read(name):
    data = (ROOT / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

def rank(rows, low=False):
    basis = {}
    for row in rows:
        while row:
            pivot = (row & -row).bit_length() - 1 if low else row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)

def census(local):
    base, frames, program = local.source()
    kernel = local.relations(program)
    rows = [1 << i for i in range(658)] + [0, 0]
    queries = {}
    for site, event in enumerate(program):
        op, dest = event[:2]
        if op == 'ADD':
            rows[dest] ^= rows[event[2]]
        elif op == 'COPY':
            rows[dest] = rows[event[2]]
        elif op in ('CLEAR', 'TICKET_CLEAR'):
            rows[dest] = 0
        elif op == 'Q':
            row = rows[dest]
            for pivot, vector in kernel.items():
                if row >> pivot & 1:
                    row ^= vector
            ids = local.bitids(row)
            if row and all(base['final'][i] == 1 for i in ids) and any(i >= 222 and i not in kernel for i in ids):
                queries[site] = (row, event[-1])
    need(len(queries) == 2327, 'Complete eligible query census')
    need(len({row for row, _ in queries.values()}) == 1733, 'Distinct forms')
    need(sum(r for _, r in queries.values()) == 3640, 'Eligible rank mass')
    return queries

def partition_check(queries, certificate):
    need(certificate['colors'] == 30 and len(certificate['groups']) == 30, 'Thirty colors')
    expected = {(site, copy) for site, (_, r) in queries.items() for copy in range(4 * r)}
    seen = set()
    for group in certificate['groups']:
        tokens = [tuple(pair) for pair in group]
        need(all(token in expected and token not in seen for token in tokens), 'Token range and disjointness')
        need(len(set(tokens)) == len(tokens), 'No repeated token')
        rows = [queries[site][0] for site, _ in tokens]
        need(rank(rows) == rank(rows, True) == len(rows), 'Independent color, both pivot orders')
        seen.update(tokens)
    need(seen == expected, 'Every query token appears')

def retire(local, late):
    base, frames, _ = local.source()
    word = local.read(local.R / 'WORD.json.gz')
    pivots = {462, 463, 466, 468}
    owned = set(word['owned']) | pivots
    rows = [1 << i for i in range(660)]
    state = word['start'][:]
    program = []
    first = set()
    removed = Counter()
    for h in sorted(pivots):
        program.append(['ERASE', h, state[h]])
        rows[h] = 0
    for event in word['records']:
        op, d = event[:2]
        if late and op == 'ADD' and event[2] in pivots and event[2] not in first:
            h = event[2]
            program.append(['ERASE', h, state[h]])
            rows[h] = 0
            first.add(h)
        if op == 'ERASE':
            rows[d] = 0
            state[d] = event[2]
        elif op == 'INIT':
            state[d] = event[2]
        elif op == 'ADD':
            rows[d] ^= rows[event[2]]
        elif op in ('Q', 'ZERO_Q'):
            if op == 'Q' and not rows[d]:
                event = ['ZERO_Q', *event[1:]]
                removed[event[-1]] += 1
            state[d] = event[3]
        program.append(event)
    for h in sorted(pivots):
        program.append(['ERASE', h, word['final'][h]])
    for modulus in (None, 101, 10201):
        local.replay(base, frames, program, owned, modulus)
    need(removed == ({3: 4} if late else {1: 4}), 'Actual retirement saving')
    return dict(removed)

def main():
    for row in read('INPUTS.json'):
        need(hashlib.sha256((ROOT / row['local']).read_bytes()).hexdigest() == row['sha256'], 'Pinned input bytes')
    sys.path.insert(0, str(ROOT / 'source'))
    import local_relations as local
    queries = census(local)
    certificate = read('PARTITION.json.gz')
    partition_check(queries, certificate)
    low = read('DENSITY-LOWER.json.gz')
    tokens = [tuple(x) for x in low['tokens']]
    need(len(tokens) == len(set(tokens)) == 12094, 'Lower witness tokens')
    need(all(site in queries and 0 <= copy < 4 * queries[site][1] for site, copy in tokens), 'Lower witness domain')
    rows = [queries[site][0] for site, _ in tokens]
    need(rank(rows) == rank(rows, True) == low['rank'] == 417, 'Lower witness rank')
    need(len(tokens) > 29 * low['rank'], 'Twenty-nine colors are impossible')
    need(8 ** 99 * 2 ** 100 > 15 ** 100, 'Strict debit bound for 0<C<=1/100')
    bad = json.loads(json.dumps(certificate))
    bad['groups'][0].append(bad['groups'][0][0])
    try:
        partition_check(queries, bad)
    except ValueError:
        pass
    else:
        raise ValueError('Duplicate token accepted')
    base, frames, _ = local.source()
    word = local.read(local.R / 'WORD.json.gz')
    local.replay(base, frames, word['records'], set(word['owned']))
    result = {'status': 'PASS_G20_JOINT_ENTRY_CAPACITY', 'queries': len(queries), 'forms': 1733,
              'rank_mass': 3640, 'capacity_upper': '15/2', 'capacity_lower': '6047/834',
              'best_quarter_grid_upper': '15/2', 'early_partial_saved': retire(local, False),
              'late_partial_saved': retire(local, True), 'partial_target_debit': {'4': 4}}
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
