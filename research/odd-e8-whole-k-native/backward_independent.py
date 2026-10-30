"""Independent read-only exact inverse-transpose stream correspondence."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import gzip, json

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def calculate(package):
    forward_raw = gzip.decompress((package / 'K-PROGRAM.json.gz').read_bytes())
    backward_raw = gzip.decompress((package / 'B-PROGRAM.json.gz').read_bytes())
    forward_raw = (json.dumps(json.loads(forward_raw), sort_keys=True, separators=(',', ':')) + '\n').encode()
    backward_raw = (json.dumps(json.loads(backward_raw), sort_keys=True, separators=(',', ':')) + '\n').encode()
    need(sha256(forward_raw).hexdigest() == '98941b295d428462b82dae52a369de97dcbf5be1dd7a369f6c495cda5fc6ac8a', 'fixed independently reviewed forward payload')
    need(sha256(backward_raw).hexdigest() == 'f6b26f28f2a8f2dcfbf81f98c7ca18f967384b7b61518766494f8e821d5bf56f', 'fixed backward payload')
    F, B = json.loads(forward_raw), json.loads(backward_raw)
    ports = F['port_order']
    need(B['port_order'] == ports and B['axis_dimension'] == 25, 'identical original fields')
    fields = {(r, p) for r in ('X', 'Y') for p in ports}
    defsF, defsB = F['definitions'], B['definitions']
    for key, word in defsB.items():
        need(sha256(json.dumps(word, separators=(',', ':')).encode()).hexdigest() == key, 'backward word address')
    def conjugate(word):
        out = []
        for gate in word:
            if gate[0] == 'D':
                out.append(['D', gate[1], [(-a) % 4 for a in gate[2]]])
            elif gate[0] == 'phase':
                out.append(['phase', (-gate[1]) % 4])
            else:
                need(gate[0] in ('P', 'X'), 'original executable monomial contains no child')
                out.append(gate)
        return out
    programF, programB = F['program'], B['program']
    need(len(programB) == len(programF) + 3 * len(ports), 'only three literal boundary gates per port added')
    for p, gate in zip(ports, programB[:len(ports)]):
        need(gate[:3] == ['BOUNDARY_MONOMIAL', 'X', p] and defsB[gate[3]] == [['X', 1]], 'actual input Q^-2 boundary')
    for p, gateX, gateY in zip(ports, programB[-2*len(ports)::2], programB[-2*len(ports)+1::2]):
        need(gateX[:3] == ['BOUNDARY_MONOMIAL', 'X', p] and defsB[gateX[3]] == [['X', (1 << 25) - 1]], 'actual fused output-X D²Q² boundary')
        need(gateY[:3] == ['BOUNDARY_MONOMIAL', 'Y', p] and defsB[gateY[3]] == [['X', ((1 << 25) - 1) ^ 1]], 'actual output-Y D² boundary')
    counts, paid = Counter(), Counter()
    for old, new in zip(programF, programB[len(ports):-2*len(ports)]):
        kind = old[0]
        need(new[0] == kind, 'same literal chronology and opcode')
        if kind == 'MONOMIAL':
            need(new[1:3] == old[1:3] and defsB[new[3]] == conjugate(defsF[old[3]]), 'every ordinary monomial is actual complex conjugate')
        elif kind == 'PAID_PATH':
            need(new[1:3] == old[1:3] and new[3:5] == ['conjugate:' + old[3], 'conjugate:' + old[4]], 'actual inverse-transpose path charts')
            a, b = old[5], new[5]
            need(b['rank'] == a['rank'] and b['child_axes'] == a['child_axes'], 'same paid child rank and axes')
            need(defsB[b['before_monomial']] == conjugate(defsF[a['before_monomial']]), 'before monomial exact conjugate')
            mask = sum(1 << j for j in a['child_axes'])
            need(defsB[b['after_monomial']] == [['X', mask]] + conjugate(defsF[a['after_monomial']]), 'literal positive-child inverse X mask included at correct cut')
        else:
            need(kind == 'ADD', 'no extra/noninvertible/owned opcode')
            need(new == ['ADD', old[3], old[4], old[1], old[2], -old[5], old[6], 'conjugate:' + old[7]], 'every actual ADD inverse transpose swaps roles and negates coefficient once')
    for gate in programB:
        need((gate[1], gate[2]) in fields, 'only original fields used')
        if gate[0] in ('MONOMIAL', 'BOUNDARY_MONOMIAL'):
            word = defsB[gate[3]]
            need(all(x[0] in ('P', 'D', 'X', 'phase') for x in word), 'backward wrappers ordinary')
            counts.update(x[0] for x in word)
        elif gate[0] == 'PAID_PATH':
            paid[gate[5]['rank']] += 1
            for key in ('before_monomial', 'after_monomial'):
                counts.update(x[0] for x in defsB[gate[5][key]])
        else:
            need(gate[0] == 'ADD' and (gate[3], gate[4]) in fields, 'all ADD sources original')
            counts['ADD'] += 1
    need(paid == {8: 512, 9: 512, 15: 512, 16: 512}, 'actual backward paid bill')
    need(counts == {'ADD': 38912, 'P': 7680, 'D': 7680, 'X': 6656, 'phase': 3072}, 'actual backward ordinary bill including fused masks')
    result = {'status': 'PASS', 'schema': 'independent-whole-K-backward-relative-word/v1',
              'forward_science': sha256(forward_raw).hexdigest(), 'backward_science': sha256(backward_raw).hexdigest(),
              'original_fields': len(fields), 'original_instructions_matched': len(programF),
              'boundary_instructions': 3 * len(ports), 'paid_profile': dict(sorted(paid.items())),
              'ordinary_profile': dict(sorted(counts.items())), 'helpers': 0, 'owned_fields': 0,
              'scientific_basis': 'Every actual F gate was checked against its exact same-chronology E^-T replacement. C_axes^-1=C_axes X_mask, monomial E^-T=conj(E), real ADD inverse transpose reverses and negates. Boundary J A² F^-T J^-1=A U(-Q C_K) uses no [C_K,Q].',
              'scope': 'No dense whole operator comparison; this is an exact gatewise mathematical correspondence, depending on the independently reviewed F word. It does not construct H, close E/caller, price precision/storage or claim kappa.'}
    return result
