"""Check every common-frame G20 helper cut.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent
N = 660

def need(value, message):
    if not value:
        raise ValueError(message)

def read(name):
    data = (ROOT / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

def rational_basis(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for pivot, old in sorted(basis.items()):
            a = row[pivot]
            row = [v-a*w for v, w in zip(row, old)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        a = row[pivot]
        row = [x/a for x in row]
        for j, old in list(basis.items()):
            a = old[pivot]
            basis[j] = [v-a*w for v, w in zip(old, row)]
        basis[pivot] = row
    return tuple(tuple(str(x) for x in row) for _, row in sorted(basis.items()))

def kernel(rows):
    basis, zero = {}, []
    for i, row in enumerate(rows):
        coefficient = 1 << i
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                basis[pivot] = (row, coefficient)
                break
            old, old_coefficient = basis[pivot]
            row ^= old
            coefficient ^= old_coefficient
        if not row:
            zero.append(coefficient)
    return zero

def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = (row & -row).bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)

def combine(rows, mask):
    value = 0
    while mask:
        bit = mask & -mask
        value ^= rows[bit.bit_length()-1]
        mask ^= bit
    return value

def paired_zero(rows, columns):
    left, right = kernel(rows), kernel(columns)
    paired = all(not ((u & v).bit_count() % 2) for u in left for v in right)
    # Form the columns of R from its rows. Then compute C R directly.
    r_columns = defaultdict(int)
    for i, row in enumerate(rows):
        while row:
            bit = row & -row
            r_columns[bit.bit_length()-1] ^= 1 << i
            row ^= bit
    product = [combine(columns, c) for c in r_columns.values()]
    rank_test = rank(product) == rank(rows)+rank(columns)-len(rows)
    need(paired == rank_test, 'Annihilator pairing and independent rank product agree')
    return paired, len(left), len(right)

def main():
    for row in read('INPUTS.json'):
        data = (ROOT / row['local']).read_bytes()
        if row['decode_gzip']:
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'Exact source bytes')
    frames = read('FRAMES.json.gz')['frames']
    canonical = {int(k): rational_basis(v['B']) for k, v in frames.items()}
    need(all(len(canonical[int(k)]) == v['dim'] for k, v in frames.items()), 'Exact frame dimensions')
    shapes = sorted(set(canonical.values()))
    labels = {k: shapes.index(v) for k, v in canonical.items()}
    dim = {i: len(v) for i, v in enumerate(shapes)}
    labels[None] = None
    word = read('WORD.json.gz')
    program, owned = word['records'], set(word['owned'])
    helpers = {h for h in range(222, 658) if h not in owned and dim[labels[word['start'][h]]] == 8}
    need(len(helpers) == 423, 'Retained full8 helpers')
    groups = defaultdict(set)
    for h in range(222, 658):
        if h not in owned:
            groups[labels[word['start'][h]]].add(h)
    need(sorted(map(len, groups.values())) == [1, 1, 2, 423], 'All four endpoint groups')
    compatible = defaultdict(list)
    masks = {}
    for entrance, members in groups.items():
        masks[entrance] = ((1 << N)-1) ^ sum(1 << h for h in members)
        for frame, shape in enumerate(shapes):
            if 0 < len(shape) < dim[entrance] and rational_basis(shapes[entrance]+shape) == shapes[entrance]:
                compatible[frame].append(entrance)
    a = [1 << i for i in range(N)]
    b = a[:]
    after_erase = {}
    for k in range(len(program)-1, -1, -1):
        op, dest = program[k][:2]
        if op == 'ADD':
            b[program[k][2]] ^= b[dest]
        elif op == 'ERASE':
            after_erase[k] = b[dest]
            b[dest] = 0
    first_b = b[:]
    state = [labels[x] for x in word['start']]
    banks = defaultdict(set)
    for i, frame in enumerate(state):
        banks[frame].add(i)
    visited, counts = set(), Counter()
    def check(frame):
        if frame is None or not 0 < dim[frame] < 8 or not banks[frame]:
            return
        fields = tuple(sorted(banks[frame]))
        rows, columns = tuple(a[i] for i in fields), tuple(b[i] for i in fields)
        for entrance in compatible[frame]:
            key = (entrance, frame, fields, rows, columns)
            if key in visited:
                continue
            forbidden = masks[entrance]
            zero, left, right = paired_zero([x & forbidden for x in rows], [x & forbidden for x in columns])
            need(zero, 'No independent helper channel at this physical cut')
            visited.add(key)
            counts['contexts'] += 1
            counts['input_kernel'] += left > 0
            counts['output_kernel'] += right > 0
            counts['both_kernels'] += left > 0 and right > 0
            counts['bank_fields_max'] = max(counts['bank_fields_max'], len(fields))
            counts['rank'+str(dim[entrance])+'_contexts'] += 1
    def header(dest, frame):
        old = state[dest]
        banks[old].remove(dest)
        banks[frame].add(dest)
        state[dest] = frame
        return {old, frame}
    for frame in list(banks):
        check(frame)
    before_erase, old_headers = {}, []
    for k, e in enumerate(program):
        op, dest = e[:2]
        old_headers.append(state[dest])
        affected = {state[dest]}
        if op == 'ADD':
            need(state[dest] == state[e[2]] == labels[e[-1]], 'Actual common frame')
            a[dest] ^= a[e[2]]
            b[e[2]] ^= b[dest]
        elif op == 'ERASE':
            before_erase[k] = a[dest]
            a[dest] = 0
            b[dest] = after_erase[k]
        if op in ('Q', 'ZERO_Q', 'ERASE', 'INIT'):
            affected |= header(dest, labels[e[3] if op in ('Q', 'ZERO_Q') else e[2]])
        for frame in affected:
            check(frame)
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(N)]
    need(a == expected and b == [1 << i for i in range(N)], 'Complete RAW/DIRTY endpoint and suffix map')
    forward, forward_counts = visited, dict(counts)
    visited, counts = set(), Counter()
    for frame in list(banks):
        check(frame)
    for k in range(len(program)-1, -1, -1):
        e = program[k]
        op, dest = e[:2]
        affected = {state[dest]}
        if op == 'ADD':
            a[dest] ^= a[e[2]]
            b[e[2]] ^= b[dest]
        elif op == 'ERASE':
            a[dest] = before_erase[k]
            b[dest] = 0
        if op in ('Q', 'ZERO_Q', 'ERASE', 'INIT'):
            affected |= header(dest, old_headers[k])
        for frame in affected:
            check(frame)
    need(a == [1 << i for i in range(N)] and b == first_b, 'Reverse traversal reaches the exact entry')
    need(visited == forward and dict(counts) == forward_counts, 'Both traversals cover identical physical cut states')
    need(paired_zero([0, 0], [0, 0])[0] is False, 'A true isolated helper channel must be detected')
    need(paired_zero([1, 0], [0, 1])[0] is True, 'Orthogonal nonzero kernels are not a split')
    need(paired_zero([1, 0], [1, 0])[0] is False, 'A nonzero pairing must be detected')
    digests = sorted(hashlib.sha256(repr(k).encode()).hexdigest() for k in forward)
    result = {'status': 'PASS_G20_ALL_HELPER_SPLIT_CUTS', 'events': len(program), 'cuts': len(program)+1,
              'original_frame_ids': len(frames), 'physical_frame_classes': len(shapes),
              'full_helpers': len(helpers), 'partial_helpers': 4, 'endpoint_groups': 4, **forward_counts,
              'cut_state_sha256': hashlib.sha256('\n'.join(digests).encode()).hexdigest()}
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
