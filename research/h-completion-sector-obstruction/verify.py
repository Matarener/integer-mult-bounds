#!/usr/bin/env python3
"""Exact native witness for the completion-independent H sector obstruction.

The universal implications are proved in README.md. No predecessor executable
is imported; this is a scoped obstruction, not a complete decoder lower bound.
zxv, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AXES = tuple(1 << i for i in range(73))
SELECTED = (0, 7, 20, 27, 36, 46, 57, 111)
OLD_BLOCK = sum(AXES[9:17])
sys.dont_write_bytecode = True


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def act(columns, value):
    out = 0
    while value:
        low = value & -value
        out ^= columns[low.bit_length()-1]
        value ^= low
    return out


def geometry(packet):
    R = [{int(k): Q(v) for k, v in row.items()} for row in packet['R_rows']]
    need(len(R) == 8, 'eight source query rows')
    dot = lambda a, b: sum((v*b.get(k, 0) for k, v in a.items()), Q(0))
    need(all(dot(a, b) == 56*int(i == j)
             for i, a in enumerate(R) for j, b in enumerate(R)), 'R R^t = 56 I')
    need(all(sum((r.get(a, 0)*r.get(b, 0) for r in R), Q(0)) == 4*int(a == b)
             for a in SELECTED for b in SELECTED), 'selected Gram = 4 I')
    J = [{p: value for p in range(112)
          if (value := Q(i == p)-sum((r.get(i, 0)*r.get(p, 0)
                                      for r in R), Q(0))/4)} for i in range(112)]
    ordinary = sorted(set(range(112))-set(SELECTED))
    L = [{p: value for p in ordinary
          if (value := sum((r.get(a, 0)*r.get(p, 0) for r in R), Q(0))/4)}
         for a in SELECTED]
    need(all(dot(a, b) == 13*int(i == j)
             for i, a in enumerate(L) for j, b in enumerate(L)), 'L L^t = 13 I')
    C = [{**row, SELECTED[k]: Q(1)} for k, row in enumerate(L)]
    B = [{k: -L[k][p] for k in range(8) if p in L[k]} if p in ordinary
         else {SELECTED.index(p): Q(11)} for p in range(112)]
    need(all(sum((coefficient*B[p].get(j, 0) for p, coefficient in C[i].items()), Q(0))
             == -2*int(i == j) for i in range(8) for j in range(8)), 'C B = -2 I')
    H = [{j: value for j in range(112)
          if (value := Q(i == j)+sum((x*C[k].get(j, 0)
                                      for k, x in B[i].items()), Q(0)))} for i in range(112)]
    need(all(H[i] == J[i] for i in ordinary), 'completion changes selected rows only')
    need(1 not in SELECTED and 2 not in SELECTED, 'witness edge is ordinary')
    need(J[1][2] == -Q(1, 2), 'fixed ordinary edge J[1,2] = -1/2')
    return J, H


def chart(phases, stage, port):
    need(1 <= stage <= 8, 'stored native stages')
    recipe = phases['recipes'][port]
    basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
    fresh = AXES[9+8*(stage-1):9+8*stage]
    swaps = [b ^ f for b, f in zip(basis, fresh)]
    g = tuple(e ^ act(swaps, sum(((e & v).bit_count() % 2) << i
                                for i, v in enumerate(swaps))) for e in AXES)
    need(all(act(g, g[i]) == AXES[i] for i in range(73)), 'owner map involution')
    active = tuple(range(9))+tuple(range(9+8*(stage-1), 9+8*stage))
    moved = [sum((g[i] >> j) & 1 for i in active) % 4 for j in range(73)]
    delta = [(int(j in active)-moved[j]) % 4 for j in range(73)]
    need(all(v in (0, 2) for v in delta), 'even linear phase defect')
    d = sum((v//2) << j for j, v in enumerate(delta))
    need(all((d & g[i]).bit_count() % 2 == (d & AXES[i]).bit_count() % 2
             for i in range(73)), 'signed owner involution')
    return g, d


def phase_checks(phases, port, g, d):
    active = AXES[:17]
    old, fresh = sum(AXES[:9]), sum(AXES[9:17])
    q = phases['recipes'][port]['q']
    tests = [0]+list(active)+[a ^ b for i, a in enumerate(active) for b in active[i+1:]]
    failures = 0
    for y in tests:
        z = act(g, y) ^ d
        need((z & (old | fresh)).bit_count() % 4 == (y & (old | fresh)).bit_count() % 4,
             'complete signed full Gaussian phase')
        need((z & q).bit_count() % 2 == (y & q).bit_count() % 2,
             'signed owner fixes port phase')
        need(((z & old).bit_count()+(z & q).bit_count() % 2) % 4
             == (1+(y & fresh).bit_count()) % 4, 'old hole to i times fresh Gaussian')
        bare = act(g, y)
        failures += int((bare & (old | fresh)).bit_count() % 4
                        != (y & (old | fresh)).bit_count() % 4)
    need(failures > 0, 'omitting the character must fail the phase contract')
    return {'port': port, 'phase_basis_tests': len(tests), 'bare_owner_failures': failures,
            'g_columns': list(g), 'character_mask': d}


def coefficient(gout, dout, gin, din, address, scalar):
    middle = act(gin, address)
    final = act(gout, middle)
    sign = (-1)**(((din & address).bit_count()+(dout & middle).bit_count()) % 2)
    return final, sign*scalar


def apply_stage(matrix, charts, vector):
    out = [{} for _ in range(112)]
    for i, row in enumerate(matrix):
        gi, di = charts[i]
        for p, scalar in row.items():
            gp, dp = charts[p]
            for address, value in vector[p].items():
                at, c = coefficient(gi, di, gp, dp, address, scalar)
                out[i][at] = out[i].get(at, Q(0))+c*value
                if not out[i][at]:
                    del out[i][at]
    return out


def authenticate():
    result = {}
    for row in read(HERE/'VENDOR.json')['files']:
        digest = sha256((ROOT/row['path']).read_bytes()).hexdigest()
        need(digest == row['sha256'], 'changed predecessor input: '+row['path'])
        result[row['path']] = digest
    return result


def verify():
    sources = authenticate()
    packet = read(HERE/'vendor/certificate.json.gz')
    phases = read(HERE/'vendor/DATA-PHASES.json')
    need(phases['m'] == 73 and len(phases['recipes']) == 112, 'native dimensions')
    need(all(row['port'] == p for p, row in enumerate(phases['recipes'])),
         'native port ordering')
    J, H = geometry(packet)
    charts = [chart(phases, 1, p) for p in range(112)]
    phase_receipts = [phase_checks(phases, p, *charts[p]) for p in (1, 2)]
    g1, d1 = charts[1]
    g2, d2 = charts[2]
    y = 512
    z, value = coefficient(g1, d1, g2, d2, y, J[1][2])
    need(z == 9235 and value == -Q(1, 2), 'actual completion-independent edge witness')
    need(y & OLD_BLOCK == 512 and z & OLD_BLOCK == 9216, 'distinct old-block sectors')
    # A single input role contributes exactly G[1,2], with no sum over other
    # entries of G. Replacing any selected rows therefore cannot change it.
    for scale in (Q(-7, 4), Q(0), Q(5, 8)):
        altered = [dict(row) for row in H]
        for p in SELECTED:
            altered[p] = {j: scale*(p+1)*(j+1) for j in range(112) if scale}
        at, c = coefficient(g1, d1, g2, d2, y, altered[1][2])
        need((at, c) == (z, value), 'arbitrary selected-row perturbation changes witness')
    future = []
    for stage in range(2, 9):
        for p in range(112):
            g, d = chart(phases, stage, p)
            need(all(g[i] & OLD_BLOCK == AXES[i] & OLD_BLOCK for i in range(73)),
                 'future owner must preserve every old-block sector')
            future.append((stage, p))
    # H^2=I follows from C B=-2I, already checked. Full signed conjugation
    # has the same involution. It can invert the witness, by revisiting the
    # OLD block; it is deliberately outside the fresh-sector hypothesis.
    basis = [{} for _ in range(112)]
    basis[2] = {y: Q(1)}
    moved = apply_stage(H, charts, basis)
    need(moved[1].get(z) == value, 'complete default H agrees with single-edge witness')
    restored = apply_stage(H, charts, moved)
    need(restored == basis, 'old-chart inverse restores arbitrary basis witness')
    identity = [{i: Q(1)} for i in range(112)]
    need(apply_stage(identity, charts, basis) == basis,
         'changing the ordinary body to identity must escape this witness')
    projected = [{a: c for a, c in row.items() if a & OLD_BLOCK == 512}
                 for row in moved]
    need(projected[1].get(z, 0) == 0, 'noninvertible projection can erase leakage')
    other_sector = [{} for _ in range(112)]
    other_sector[1] = {z: Q(1)}
    need(all(not {a: c for a, c in row.items() if a & OLD_BLOCK == 512}
             for row in other_sector), 'same projection destroys independent input data')
    return {
        'schema': 'H-arbitrary-completion-sector-obstruction/1',
        'status': 'PASS_COMPLETION_INDEPENDENT_SECTOR_WITNESS',
        'source_sha256': sources,
        'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'selected_rows': list(SELECTED), 'fixed_ordinary_edge': {'row': 1, 'column': 2, 'value': '-1/2'},
        'witness': {'input_role': 2, 'input_address': y, 'output_role': 1,
                    'output_address': z, 'coefficient': str(value),
                    'input_block_label': 512, 'output_block_label': 9216,
                    'commutator_Pi_A_coefficient': '1/2'},
        'owner_phase_receipts': phase_receipts,
        'stage_one_involutive_charts': 112,
        'later_sector_preserving_charts': len(future),
        'later_checked_stages': list(range(2, 9)),
        'universal_claim': 'For every invertible G over Q with G[1,2]=-1/2, A=Gamma(G tensor I)Gamma^-1 and A^-1 fail to commute with Pi. Multiplication on either side by invertible Pi-commuting operators cannot remove this obstruction.',
        'full_column_lift': 'At f columns use (512,0,...,0) and (9235,0,...,0). All extra columns stay zero and have character phase +1; the same coefficient is -1/2 for every integer f>=1.',
        'controls': {'bare_owner_phase_rejected': True,
                     'arbitrary_selected_row_perturbations_preserve_witness': 3,
                     'old_block_revisit_restores_default_H': True,
                     'changing_fixed_ordinary_body_to_identity_escapes': True,
                     'noninvertible_projection_erases_leak_and_loses_arbitrary_data': True},
        'scope': 'Actual complex H owner geometry and a fixed ordinary edge. No general decoder impossibility, paid-query floor, BIT obstruction or kappa claim. Universal implications are the written proof in README.md.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write a new receipt instead of comparing RESULT.json')
    args = parser.parse_args()
    result = verify()
    if args.out:
        need(not args.out.exists(), 'output must be new')
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(read(HERE/'RESULT.json') == result, 'committed receipt differs')
    print(json.dumps({'status': result['status'], 'witness': result['witness'],
                      'later_sector_preserving_charts': result['later_sector_preserving_charts']}))


if __name__ == '__main__':
    main()
