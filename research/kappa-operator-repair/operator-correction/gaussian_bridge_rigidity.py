#!/usr/bin/env python3
"""Certify the matrix premise for the Gaussian-coefficient rigidity extension.

The argument for the unbounded coefficient class is written in PROOF.md.
This checks its exact twenty projector columns and retained left inverse;
it does not rerun a fixed-slot or controller search. Apache-2.0; AI assisted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import full_operator as F
from correction import projector

HERE = Path(__file__).resolve().parent
OLD_CERTIFICATE = F.OLD / 'complex/SLOT-PROJECTOR-RIGIDITY.json'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=HERE / 'GAUSSIAN-BRIDGE-RIGIDITY.json')
    args = ap.parse_args()
    F.authenticate()
    old = F.read(OLD_CERTIFICATE)
    for path, digest in old['source_pins'].items():
        F.require(F.sha(F.REPO / path) == digest, 'retained projector certificate source')
    normal = F.normalize(F.read(F.TEMPLATE), F.read(F.PHASES)['recipes'][0])
    columns = []
    for child in range(20):
        K = projector(normal['prefixes'][child])
        columns.append(sum(((K[i][j][0] + K[i][j][1]) % 2) << (8 * i + j)
                           for i in range(8) for j in range(8)))
    F.require(columns == list(map(int, old['columns'])), 'independent signed prefix projectors match retained mod-pi columns')
    inverse = list(map(int, old['left_inverse_rows']))
    F.require(all((inverse[i] & columns[j]).bit_count() % 2 == int(i == j)
                  for i in range(20) for j in range(20)), 'exact400-entry left inverse')
    moves = [(d, r, int(a)) for owner, port, d, r, a in F.read(F.MOVES)['moves'] if owner == port == 0]
    edits = F.phase_edits(moves)
    slot_xor = {}
    for child, pairs in edits.items():
        value = 0
        for axis, _ in pairs:
            value ^= axis
        slot_xor[child] = value
    F.require(any(slot_xor.values()), 'actual overlay has a forbidden first-order phase')
    result = {
        'status': 'PASS_UNBOUNDED_GAUSSIAN_COEFFICIENT_RIGIDITY_PREMISE',
        'independently_reconstructed_projectors': 20,
        'left_inverse_identity_entries': 400,
        'prime': 'pi=1-i in the local Gaussian-integer ring; i reduces to1 modulo pi',
        'fixed_hypotheses': ['The same twenty phase-slot positions and local endpoint/gauge interface',
            'Every scalar prefix reduces to the retained prefix modulo pi',
            'Scalar gates and their inverses have coefficients integral at pi',
            'The complete zero-character scalar operator is exactly I'],
        'new_coefficient_scope': 'Arbitrary constant Gaussian-integer coefficients with the same graph modulo pi, including replacing nonzero signed coefficients by +/-i or any other coefficient congruent to1. Extra scalar factors congruent toI modulo pi are also covered. No bound on coefficient magnitude is used.',
        'conclusion': 'Every slot phase difference delta_c(character) must vanish modulo4 for every character. With arbitrary added linear translations, any replacement orthonormal frame has the same orthogonal projector and hence the same rank at each slot. Constant Gaussian bridge dressing cannot repair a nonzero rank transfer.',
        'actual_owner0_port0_first_order_slot_xors': {str(k): str(v) for k, v in sorted(slot_xor.items())},
        'proof_steps': [
            'Write the normalized discrepancy as a product of I+(i^delta_c-1)K_c, with K_c=M_c^-1 E_c M_c.',
            'Modulo pi^2, identity and the twenty-column left inverse force delta_c even separately for each slot and character.',
            'All phase perturbations now lie in (pi^2). Modulo pi^3 their cross terms vanish, and K_c may be replaced by its mod-pi value.',
            'The same left inverse forces delta_c/2 even. Thus delta_c=0 modulo4 at every slot.',
            'The exact Z4 phase polynomial fixes off-diagonal entries of sum aa^T, and the linear coefficients modulo2 fix its diagonal. Orthogonal-frame rank equals projector rank.'
        ],
        'outside_scope': ['coefficients with a denominator divisible by pi, including1/2',
            'changed scalar topology modulo pi', 'new phase slots or changed local endpoints',
            'coordinate-dependent scalar/operator coefficients', 'changed stock/width/local supplier interfaces'],
        'old_fixed_slot_census_rerun': False,
        'new_supplier': False, 'new_kappa': False,
        'input_files': {str(p.relative_to(F.REPO)): F.sha(p) for p in [*F.PINS, OLD_CERTIFICATE,
                        Path(F.__file__), HERE / 'correction.py', Path(__file__)]},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], 'projectors', 20, 'left_inverse_entries', 400)


if __name__ == '__main__':
    main()
