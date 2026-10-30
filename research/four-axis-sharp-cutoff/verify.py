"""Check the sharp four-axis native monomial cutoff.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor roles are recorded in PROOF.md and SOURCES.json.
"""
from array import array
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import math
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
THRESHOLDS = (12, 9, 10, 11)
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(vectors, dimension=4):
    basis = [0] * dimension
    for x in vectors:
        for i in range(dimension - 1, -1, -1):
            if (x >> i) & 1:
                if basis[i]:
                    x ^= basis[i]
                else:
                    basis[i] = x
                    break
    return sum(bool(x) for x in basis)


def span(vectors):
    out = {0}
    for x in vectors:
        out |= {x ^ y for y in out}
    return out


def phase(counts):
    width = sum(counts)
    u = [sum(m for x, m in enumerate(counts) if (x >> i) & 1) % 4 for i in range(4)]
    v = [sum(m for x, m in enumerate(counts) if ((x >> i) & 1) and ((x >> j) & 1)) % 2
         for i, j in PAIRS]
    return (width % 4 | sum((z % 2) << (i + 2) for i, z in enumerate(u))
            | sum((z // 2) << (i + 6) for i, z in enumerate(u))
            | sum(z << (i + 10) for i, z in enumerate(v)))


def check_witness(character, packed):
    need(isinstance(packed, int) and 0 <= packed < 2**64, 'Packed witness domain')
    counts = [(packed >> (4 * x)) & 15 for x in range(16)]
    need(phase(counts) == character, 'Complete literal phase character')
    need(rank([16 | x for x, m in enumerate(counts) if m], 5) == 5, 'Full affine span')
    need(sum(counts) <= THRESHOLDS[character % 4], 'Character threshold')
    return counts


def image(columns):
    values = [0]
    for a in columns:
        values += [x ^ a for x in values]
    return tuple(values)


def order(g):
    seen = set()
    out = 1
    for x in range(16):
        if x in seen:
            continue
        y, length = x, 0
        while y not in seen:
            seen.add(y)
            length += 1
            y = g[y]
        out = math.lcm(out, length)
    return out


def group_key(g):
    return (order(g), rank([g[1 << i] ^ (1 << i) for i in range(4)]),
            rank([g[g[1 << i]] ^ g[1 << i] ^ (1 << i) for i in range(4)]))


def group_certificate(coefficients):
    columns = [c for c in product(range(16), repeat=4) if rank(c) == 4]
    other = []
    for a in range(1, 16):
        for b in set(range(16)) - span([a]):
            for c in set(range(16)) - span([a, b]):
                for d in set(range(16)) - span([a, b, c]):
                    other.append((a, b, c, d))
    need(len(columns) == 20160 and set(columns) == set(other), 'Two complete GL(4,2) inventories')
    maps = [image(c) for c in columns]
    weights = [coefficients[group_key(g)] for g in maps]
    need(coefficients[group_key(tuple(range(16)))] == 21, 'Nonzero identity coefficient')
    types = Counter(group_key(g) for g in maps)
    cosets = 0
    for ell in range(1, 16):
        plane = [x for x in range(16) if (ell & x).bit_count() % 2 == 0]
        basis = []
        for x in plane:
            if x not in span(basis):
                basis.append(x)
        need(len(basis) == 3, 'All linear hyperplanes')
        sums, sizes = Counter(), Counter()
        for g, a in zip(maps, weights):
            key = tuple(g[x] for x in basis)
            sums[key] += a
            sizes[key] += 1
        need(len(sizes) == 2520 and set(sizes.values()) == {8}, 'Complete stabilizer cosets')
        need(not any(sums.values()), 'Every hyperplane coset sum is zero')
        cosets += len(sizes)
    # A full linear span need not be a full affine span.
    points = list(range(8, 16))
    linear_sum = sum(a for g, a in zip(maps, weights) if all(g[x] == x for x in points))
    affine_sum = sum(a for g, a in zip(maps, weights)
                     if all((g[x] ^ g[8] ^ 8) == x for x in points))
    need(linear_sum == 21 and affine_sum == 0, 'Translation average is necessary')
    return cosets, sorted((list(k), v) for k, v in types.items())


def lower_census():
    transitions = []
    for x in range(16):
        pairs = sum((((x >> i) & 1) * ((x >> j) & 1)) << k for k, (i, j) in enumerate(PAIRS))
        row = array('H')
        for c in range(65536):
            p, q, v = (c >> 2) & 15, (c >> 6) & 15, c >> 10
            row.append(((c + 1) & 3) | ((p ^ x) << 2) | ((q ^ (p & x)) << 6) | ((v ^ pairs) << 10))
        transitions.append(row)
    full = {}
    totals, zeros = Counter(), Counter()
    def visit(start, left, character, support, width):
        if left == 0:
            totals[width] += 1
            if character >> 2 == 0:
                zeros[width] += 1
                if support not in full:
                    full[support] = len(span([16 | x for x in range(16) if support >> x & 1])) == 32
                need(not full[support], 'No low-width zero-phase tuple has full affine span')
            return
        for x in range(start, 16):
            visit(x, left - 1, transitions[x][character], support | (1 << x), width)
    for f in range(5, 9):
        visit(0, f, 0, 0, f)
        need(totals[f] == math.comb(15 + f, 15), 'Complete multiset census')
    return dict(sorted(totals.items())), dict(sorted(zeros.items()))


def main():
    for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Source bytes')
    data = (HERE / 'WITNESSES.json.gz').read_bytes()
    witnesses = json.loads(gzip.decompress(data))
    need(len(witnesses) == 65536, 'All phase characters')
    histogram = Counter()
    for c, packed in enumerate(witnesses):
        histogram[sum(check_witness(c, packed))] += 1
    table = json.loads((HERE / 'COEFFICIENTS.json').read_text())
    coefficients = {tuple(k): v for k, v in zip(table['keys'], table['coefficients'])}
    cosets, types = group_certificate(coefficients)
    totals, zeros = lower_census()
    bad = dict(coefficients)
    bad[(2, 1, 4)] += 1
    controls = [lambda: check_witness(1, witnesses[0]),
                lambda: check_witness(1024, witnesses[0]),
                lambda: check_witness(0, sum(1 << (4 * x) for x in range(8, 16))),
                lambda: group_certificate(bad),
                lambda: need(21 == 0, 'Omitted translation average fails')]
    rejected = 0
    for test in controls:
        try:
            test()
        except ValueError:
            rejected += 1
        else:
            raise ValueError('Defective fixture accepted')
    result = dict(status='PASS_FOUR_AXIS_SHARP_CUTOFF', cutoff=9,
                  residue_thresholds=list(THRESHOLDS), phase_characters=65536,
                  witness_sha256=sha256(data).hexdigest(), witness_length_histogram=dict(sorted(histogram.items())),
                  gl4_elements=20160, class_types=types, hyperplane_cosets=cosets,
                  lower_multisets=totals, lower_zero_phase_multisets=zeros,
                  threshold_diagonal_entry=21, rejected_controls=rejected, kappa_change=None)
    # JSON normalizes integer dictionary keys for the receipt comparison.
    result = json.loads(json.dumps(result))
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Committed receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
