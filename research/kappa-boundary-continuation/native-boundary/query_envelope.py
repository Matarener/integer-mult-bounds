#!/usr/bin/env python3
"""Exact failure of scalar precompression before the varying native lines.

This is a restricted interface obstruction, not a lower bound on arbitrary
routed native circuits or on the terminal consumer. Apache-2.0; substantial
OpenAI Codex assistance; authenticated PR3734 query/source credit retained.
"""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rank(matrix):
    a = [[F(v) for v in row] for row in matrix]
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        q = a[row][col]
        a[row] = [v/q for v in a[row]]
        for i in range(row+1, len(a)):
            q = a[i][col]
            if q:
                a[i] = [x-q*y for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def run(scope, out):
    ir_path = scope/'helper-consumer/evidence/ALTERNATING-CONSUMER-IR.json.gz'
    ir_raw = gzip.decompress(ir_path.read_bytes())
    need(sha256(ir_raw).hexdigest() == '6d6818a0694987878a4e54c4a5dc7125b38e1d3fe8d94578593044c8172c4cf8',
         'retained query IR payload pin')
    ir = json.loads(ir_raw)
    phase_path = scope/'inputs/kappa-consumer-followup/artifact/integer-mult-bounds/research/pr3190-independent-operator-audit/vendor/DATA-PHASES.json'
    phase_raw = phase_path.read_bytes()
    need(sha256(phase_raw).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'native phase pin')
    labels = [e['q'] for e in json.loads(phase_raw)['recipes']]
    R = [[F(row.get(str(p), 0)) for p in range(112)] for row in ir['R']]
    need(rank(R) == 8 and len(set(labels)) == 112, 'actual source rank and distinct labels')
    annihilators = []
    for row in R:
        support = [labels[p] for p, value in enumerate(row) if value]
        ann = [v for v in range(1, 512) if all(not ((v&q).bit_count() % 2) for q in support)]
        need(len(support) == 56 and len(ann) == 1 and ann[0].bit_count() % 2 == 1,
             'every actual query support has one norm-one annihilator')
        annihilators.append(ann[0])
    annihilator_gram = [[(a&b).bit_count() % 2 for b in annihilators]
                       for a in annihilators]
    # These eight normals are individually norm one, but are not an
    # orthogonal frame. Their support-hyperplane property does not imply a
    # simultaneous orthogonal query chart.
    need(any(annihilator_gram[i][j] for i in range(8) for j in range(8) if i != j),
         'do not mistake individual support hyperplanes for an orthogonal frame')

    # The Fourier-character projection isolates every individual source column.
    # This certifies full scalar row-envelope dimension over Q, without relying
    # on a numerical matrix rank or treating that dimension as a native tariff.
    for p in range(112):
        k = next(k for k in range(8) if R[k][p])
        for t in range(112):
            total = sum((-1)**(((labels[p]^labels[t])&xi).bit_count() % 2) for xi in range(512))
            need(total*R[k][t] == (512*R[k][p] if t == p else 0), 'exact character isolation of e_p')

    # Five actual ports give a sparse kernel witness. Native positive C_q has
    # one-layer multiplier i^(q.xi), so it changes the cancelled input into a
    # nonzero query. Any operation applied only to the original eight zero
    # queries must still give zero, regardless of its recursive rank.
    ports = [0, 7, 27, 57, 76]
    values = [F(-1,2), F(1,2), F(-1,2), F(-1,2), F(1)]
    xi = 1
    need(all(sum(R[k][p]*v for p, v in zip(ports, values)) == 0 for k in range(8)), 'literal R kernel')
    a, b = (F(1,2), F(1,2)), (F(1,2), F(-1,2))
    outputs = [[(F(), F()) for z in range(512)] for k in range(8)]
    for p, value in zip(ports, values):
        source = [value*((-1)**((xi&z).bit_count() % 2)) for z in range(512)]
        transformed = [add(mul(a, (source[z], F())), mul(b, (source[z^labels[p]], F()))) for z in range(512)]
        for k in range(8):
            if R[k][p]:
                outputs[k] = [add(x, mul((R[k][p], F()), y)) for x, y in zip(outputs[k], transformed)]
    wanted = [(F(),F()),(F(1),F(-1)),(F(1),F(-1))]+[(F(),F())]*5
    need([row[0] for row in outputs] == wanted, 'literal 512-coordinate native line witness')
    for k in range(8):
        need(all(value == mul(wanted[k], (F((-1)**((xi&z).bit_count() % 2)),F()))
                 for z, value in enumerate(outputs[k])), 'full Fourier-vector output')

    # Tensoring a one-layer scalar identity is not the diagonal-translation
    # identity used by the cover's rank-zero affine grammar.
    true_tensor = [mul(a,a),mul(a,b),mul(b,a),mul(b,b)]
    false_diagonal = [a,(F(),F()),(F(),F()),b]
    need(true_tensor != false_diagonal and true_tensor[1] == (F(1,2),F()), 'two-layer rank-zero shortcut rejected')
    # A genuine common normal does commute through the scalar gather. Check
    # every frequency and every matrix entry, rather than relying on the
    # failing varying-normal case to define our expected result.
    for xi_control in range(512):
        multiplier = (F(), F(1)) if (labels[0]&xi_control).bit_count() % 2 else (F(1), F())
        need(all(mul((entry,F()), multiplier) == mul(multiplier, (entry,F()))
                 for row in R for entry in row), 'common-label positive control')
    out.mkdir(parents=True, exist_ok=True)
    result = dict(status='PASS_SCALAR_QUERY_ENVELOPE_AND_LITERAL_NATIVE_COUNTEREXAMPLE',
        source_ir_payload_sha256=sha256(ir_raw).hexdigest(), source_phase_sha256=sha256(phase_raw).hexdigest(),
        query_support_sizes=[56]*8, query_support_binary_ranks=[8]*8,
        query_support_annihilator_normals=annihilators,
        query_support_annihilator_gram_mod2=annihilator_gram,
        query_support_annihilators_are_orthogonal=False, scalar_query_rank=8,
        minimum_scalar_pregather_envelope=112,
        envelope_identity='For each source p choose k with R[k,p] != 0. The signed sum (512 R[k,p])^-1 sum_xi (-1)^(q_p.xi) R[k,:] diag((-1)^(q_t.xi)) equals e_p exactly.',
        kernel_witness=dict(ports=ports, coefficients=[str(v) for v in values], Fourier_index=xi,
            native_R_Cq_output_at_address_zero=[[str(x),str(y)] for x,y in wanted],
            all512_payload_coordinates_checked=True),
        tensor_control=dict(layers=2, native_off_diagonal_amplitude='1/2', proposed_rank_zero_amplitude='0', rejected=True),
        scoped_conclusion='A source-independent scalar gather into the 8 R-queries (or any fixed scalar envelope smaller than 112) cannot precede all source-dependent C_q lines and retain this native V boundary, even if the later operation on those queries is arbitrary. This rejects gather-first/transform-later pricing for this interface.',
        positive_control='If all source labels are equal, the 8-dimensional R row space is invariant and the common C_q can be applied after gathering.',
        outside_scope=['routed or native operations inside the pregather', 'source-dependent query charts',
            'shared interstage circuits and producer retiming', 'general native-child lower bounds', 'new kappa'])
    (out/'QUERY-ENVELOPE-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--scope', type=Path, default=Path(__file__).resolve().parents[2]/'kappa-global-continuation')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    run(args.scope.resolve(), args.out.resolve())
