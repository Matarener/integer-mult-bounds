"""Check the source blob and an exactly decodable spectral control."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

import history_module as h

HERE = Path(__file__).resolve().parent


def main():
    h.MOD = None
    data = (HERE/'N3-PROGRAM.json').read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob != '757fe38c7de18c137be95e0d8e4f7c53e0b5d443':
        raise ValueError('The source program does not match its pinned Git blob')
    program = json.loads(data)
    # At lambda=2, the fixture has C=2P_minus and E=I. These four
    # coefficient families are lambda/2, 1-lambda/2, and the two
    # inverse-code coefficients lambda/(2(lambda-1)) and
    # (lambda-2)/(2(lambda-1)). Include their exterior signs.
    replace = {Q(49): Q(1), Q(-49): Q(-1), Q(-48): Q(0), Q(48): Q(0),
               Q(49, 97): Q(1), Q(-49, 97): Q(-1),
               Q(48, 97): Q(0), Q(-48, 97): Q(0)}
    changes = 0
    for e in program:
        if e[0] in ('ADD', 'SCALE'):
            i = 3 if e[0] == 'ADD' else 2
            c = Q(e[i], e[i+1])
            if c in replace:
                new = replace[c]
                e[i:i+2] = [new.numerator, new.denominator]
                changes += 1
    history, targets, _ = h.source(program)
    records = []
    for weight in range(5):
        chi = (1 << weight)-1
        basis = {}
        for name, row in history:
            for p in range(24):
                h.insert(h.project(row, chi, p), basis)
        hits = [not h.residue(h.project(t, chi, h.ID), basis) for t in targets]
        if not all(hits):
            raise ValueError('The spectral control must recover all four targets')
        records.append({'weight': weight, 'rank': len(basis), 'targets': hits})
    result = {'status': 'PASS_EXACT_CONTROL_AT_LAMBDA_2',
              'coefficient_changes': changes,
              'reason': 'In this small fixture C=2P_minus and E=K(I-C)^-1=I.',
              'cases': records,
              'scope': 'Control only. The actual global C modes do not cover the full K-minus eigenspace, so this is not a global repair.'}
    if result != json.loads((HERE/'control-lambda2.json').read_bytes()):
        raise ValueError('The saved control receipt differs')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
