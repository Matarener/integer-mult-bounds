"""Exact source-bound affine tag check. JoyboyBrian / OpenAI Codex; Apache-2.0."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 9
SIZE = 1 << N


def need(ok, why):
    if not ok:
        raise ValueError(why)


def parity(x):
    return x.bit_count() % 2


def linear(rows, x):
    return sum(parity(r & x) << j for j, r in enumerate(rows))


def pullback(rows, t):
    return sum(parity(t & linear(rows, 1 << j)) << j for j in range(N))


def decoded(r, x):
    bits = [j for j in range(N) if x >> j & 1]
    phase = r['phase'] + sum(r['linear_Z4'][j] for j in bits)
    phase += 2 * sum((r['quadratic_rows'][j] >> k) & 1
                     for j in bits for k in bits if j < k)
    return linear(r['matrix_rows'], x) ^ r['offset'], phase % 4


def tagged(rows, b, c, t, x):
    y = linear(rows, x) ^ b
    return y, (c + y.bit_count() - x.bit_count() + 2 * parity(t & x)) % 4


def extract(r):
    rows, b = r['matrix_rows'], r['offset']
    c = (r['phase'] - b.bit_count()) % 4
    residual = [(decoded(r, 1 << j)[1] - c
                 - (linear(rows, 1 << j) ^ b).bit_count() + 1) % 4
                for j in range(N)]
    need(all(v in (0, 2) for v in residual), 'not an even coordinate tag')
    t = sum((v // 2) << j for j, v in enumerate(residual))
    need(all(decoded(r, x) == tagged(rows, b, c, t, x) for x in range(SIZE)),
         'quadratic residual is not a character')
    return rows, b, c, t


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                 == row['sha256'], 'source bytes changed: ' + row['path'])
    items = json.loads((ROOT / 'research/native-lift-phase-tags/source/RECIPES.json').read_text())['items']
    forward, inverse = items[:2]
    need(forward['kind'] == inverse['kind'] == 'warp', 'source kind')
    need(forward['entrance'] == inverse['terminal'] and
         forward['terminal'] == inverse['entrance'] and
         forward['G_columns'] == inverse['G_columns'] and
         (forward['sign'], inverse['sign']) == (1, -1), 'inverse source interface')
    need(all(i['recipe']['rank'] == 0 and i['recipe']['right'] is None
             for i in (forward, inverse)), 'source monomial scope')
    f, g = forward['recipe']['left'], inverse['recipe']['left']
    need((f['offset'], f['phase'], g['offset'], g['phase']) == (426, 1, 330, 0),
         'actual source offsets and phases')
    A, b, c, t = extract(f)
    B, d, e, u = extract(g)
    need((c, t) == (0, 16), 'forward normalized tag')
    need(all(linear(B, linear(A, x)) == x for x in range(SIZE)), 'linear inverse')
    need(d == linear(B, b), 'inverse translation')
    need(u == pullback(B, t), 'inverse input tag')
    need(e == (-c + 2 * parity(u & b)) % 4, 'inverse constant')
    dropped_constant = wrong_offset = dropped_source_phase = 0
    # Z_2 is a calibration tag, not a claimed neighboring source operation.
    z = 2
    need(parity(z & b) == 1, 'nontrivial translation control')
    for x in range(SIZE):
        y, p = decoded(f, x)
        back, q = decoded(g, y)
        need((back, (p + q) % 4) == (x, 0), 'inverse roundtrip')
        yi, pi = decoded(g, x)
        backi, qi = decoded(f, yi)
        need((backi, (pi + qi) % 4) == (x, 0), 'other inverse roundtrip')
        # Z_z M = i^(c+2 z.b) J_(A,b) Z_(t+A^T z).
        lhs = (y, (p + 2 * parity(z & y)) % 4)
        rhs = tagged(A, b, c + 2 * parity(z & b), t ^ pullback(A, z), x)
        need(lhs == rhs, 'affine tag propagation')
        dropped_constant += lhs != tagged(A, b, c, t ^ pullback(A, z), x)
        wrong_offset += tagged(B, b, e, u, y)[0] != x
        dropped_source_phase += (y, (p - f['phase']) % 4) != (y, p)
    need((dropped_constant, wrong_offset, dropped_source_phase) == (512, 512, 512),
         'phase/offset controls must discriminate every column')
    receipt = dict(columns=SIZE, forward_tag=[c,t], inverse_tag=[e,u],
                   offsets=[b,d], roundtrip_columns=2*SIZE,
                   omitted_translation_constant_mismatches=dropped_constant,
                   wrong_inverse_offset_mismatches=wrong_offset,
                   omitted_source_phase_mismatches=dropped_source_phase)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
