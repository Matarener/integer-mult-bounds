"""Check source bytes, native reconstruction, caller and ordinary admission."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import tempfile

import affine_local as local
import affine_caller as caller
import affine_ordinary as ordinary

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
need = local.need


def matrix_product(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)]
            for row in a]


def projector(basis):
    b = [[F(x) for x in row] for row in basis]
    n = len(b)
    gram = matrix_product(b, list(zip(*b)))
    a = [row + [F(i == j) for j in range(n)]
         for i, row in enumerate(gram)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i][j])
        a[j], a[k] = a[k], a[j]
        divisor = a[j][j]
        a[j] = [x/divisor for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x-factor*y for x, y in zip(a[i], a[j])]
    return matrix_product(matrix_product(list(zip(*b)),
                          [row[n:] for row in a]), b)


def native_identity():
    _, frames, _ = local.L.source()
    u = projector(frames['509']['B'])
    ell = projector(frames['79']['B'])
    eye = [[F(i == j) for j in range(8)] for i in range(8)]
    for p, rank in ((u, 4), (ell, 1)):
        need(p == list(map(list, zip(*p))) and matrix_product(p, p) == p,
             'Exact symmetric native projector')
        need(sum(p[i][i] for i in range(8)) == rank, 'Exact projector rank')
    need(matrix_product(u, ell) == ell and matrix_product(ell, u) == ell,
         'Exact nested address spaces')
    residual = [[x-y for x, y in zip(a, b)] for a, b in zip(u, ell)]
    def address(p):
        # The second bank is written in reversed coordinate order.
        return [[eye[i % 8][j % 8]-p[i % 8][j % 8]
                 if (i < 8) == (j < 8) else p[i % 8][j % 8]
                 for j in range(16)] for i in range(16)]
    need(matrix_product(address(ell), address(residual)) == address(u),
         'H1 after H3 is the exact H4 address operator')
    return {'ranks': [3, 1, 4], 'rational_address_identity': True}


def independent_caller(folder):
    invoice = local.L.read(folder/'INVOICE.json')
    n, owned = invoice['originals'], invoice['owned_allocated']
    values = [1 << i for i in range(n+owned)]
    paid, operations = Counter(), Counter()
    digest = sha256()
    with gzip.open(folder/'GLOBAL.jsonl.gz', 'rb') as stream:
        for raw in stream:
            digest.update(raw)
            e = json.loads(raw)
            operations[e[0]] += 1
            if e[0] == 'ADD':
                values[e[1]] ^= values[e[2]]
            elif e[0] == 'OWNED_CLEAR':
                need(n <= e[1] < n+owned, 'Independent owned-only clear')
                values[e[1]] = 0
            elif e[0] == 'QUERY':
                paid[e[2]] += 1
            elif e[0] in ('WHOLE_ZERO_FRAME', 'OWNED_ZERO_HEADER'):
                need(values[e[1]] == 0, 'Independent whole-zero control')
            else:
                need(e[0] == 'PAID_PORT_ROUTE', 'Independent opcode')
    need(values == [1 << i for i in range(n)] + [0]*owned,
         'Independent 11249 RAW/DIRTY column replay')
    need(paid == Counter({int(k): v for k, v in invoice['paid'].items()}),
         'Independent paid inventory')
    targets = local.L.read(folder/'TARGET-OWNERS.json')
    old_targets = local.L.read(local.SOURCE/'TARGET-OWNERS.json')
    need(targets == old_targets, 'Every retained native target is unchanged')
    return {'columns': n+owned, 'paid': dict(sorted(paid.items())),
            'operation_counts': dict(operations),
            'canonical_stream_sha256': digest.hexdigest(),
            'unchanged_target_descriptors': len(targets)}


def run():
    pins = local.L.read(HERE/'SOURCES.json')
    for pin in pins['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'],
                 'Exact live source: '+pin['path'])
    with tempfile.TemporaryDirectory(prefix='g20-affine-history-') as tmp:
        folder = Path(tmp)
        loc = local.run(folder)
        geometry = native_identity()
        glob = caller.run(folder)
        independent = independent_caller(folder)
        need(independent['canonical_stream_sha256'] == glob['canonical_stream_sha256'],
             'Independent literal stream hash')
        admitted = ordinary.run(folder)
        expected = local.L.read(HERE/'RESULT.json')
        actual = {'local': loc, 'geometry': geometry,
                  'global': {k: v for k, v in glob.items() if k != 'CPU_seconds'},
                  'independent': independent, 'ordinary': admitted}
        # JSON stores each integer rank key as a string.
        actual = json.loads(json.dumps(actual))
        need(actual == expected, 'Exact committed result')
        need(admitted['admitted'] == '108894687/31250000000', 'Certified component value')
        print('PASS_G20_AFFINE_HISTORY_ORDINARY_003484629984')
        print(json.dumps({'paid_jobs': glob['invoice']['QUERYs'],
                          'targets': glob['invoice']['originals'],
                          'owned': glob['invoice']['owned_allocated'],
                          'whole_kappa_changed': False}, sort_keys=True))


if __name__ == '__main__':
    run()
