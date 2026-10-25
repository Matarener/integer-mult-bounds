#!/usr/bin/env python3
"""Actual PR589 defect-nine involution, with native rank-one completion.

The old nine copied rank-seven centers are removed. The dirty-input
compensation is recomputed, preserving every source and helper. Nine row
corrections are gathered at the completed frame and transported into selected
target holes through one explicitly owned, reused field. All arithmetic here
is native XOR over F2; no complex rational coefficient is imported.

Apache-2.0; substantial OpenAI assistance. The unmodified local body retains
the eumemic/Claude attribution and predecessor lineage in its NOTICE.md.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

import mixed_productive_bit as B
import pr589_state_sharing_probe as P

HERE = Path(__file__).resolve().parent


def geometry(w):
    v, n = w['v'], 2*w['v']+w['R']
    rows = [1 << i for i in range(n)]
    for _, d, ss in w['A']:
        for s in ss:
            rows[d] ^= rows[s]
    mask = (1 << v)-1
    V = [rows[r] & mask for r in w['ret']]
    U = [sum(1 << k for k in row) for row in w['scatter']]
    B.need(B.bit_rank(V, v) == len(V) == 9, 'Nine independent actual producer signals')
    selected, columns = [], []
    for j in range(v):
        c = sum(((r >> j) & 1) << i for i, r in enumerate(V))
        if B.bit_rank(columns+[c], 9) > len(columns):
            selected.append(j)
            columns.append(c)
        if len(selected) == 9:
            break
    minor = [sum(((row >> a) & 1) << j for j, a in enumerate(selected)) for row in V]
    VU = B.bit_mul(V, U)
    M = B.bit_mul(B.bit_inverse(minor), VU)
    correction = B.bit_mul(M, V)
    Up = list(U)
    for a, r in zip(selected, M):
        Up[a] ^= r
    B.need(not any(B.bit_mul(V, Up)), 'Completed defect is square-zero')
    J = [r ^ (1 << i) for i, r in enumerate(B.bit_mul(U, V))]
    H = [r ^ (1 << i) for i, r in enumerate(B.bit_mul(Up, V))]
    B.need(B.bit_mul(H, H) == [1 << i for i in range(v)], 'Actual 111-port H squared is identity')
    changed = list(J)
    for a, r in zip(selected, correction):
        changed[a] ^= r
    B.need(changed == H, 'Only nine declared target rows change')
    gaussian_program, gaussian_add_count = B.bit_factor(H)
    # In the (ordinary, selected) split write V=V_A [L,I]. Because VU'=0,
    # U'V_A=[K;LK], so H=S_L S_K S_L over F2. This literal three-shear
    # program is much smaller than generic elimination and uses no scratch.
    ordinary = [i for i in range(v) if i not in selected]
    normalized = B.bit_mul(B.bit_inverse(minor), V)
    L = [row & ~sum(1 << a for a in selected) for row in normalized]
    K = B.bit_mul([Up[i] for i in ordinary], minor)
    L_program = [['ADD', a, s] for a, row in zip(selected, L)
                 for s in ordinary if row >> s & 1]
    K_program = [['ADD', u, a] for u, row in zip(ordinary, K)
                 for j, a in enumerate(selected) if row >> j & 1]
    program = L_program+K_program+L_program
    exact = [1 << i for i in range(v)]
    for _, d, s in program:
        exact[d] ^= exact[s]
    B.need(exact == H, 'All columns of the three-shear common-frame H')
    add_count = len(program)
    return dict(V_rows=V, U_rows=U, VU_rows=VU, selected=selected,
                selected_minor_rows=minor, M_rows=M, correction_rows=correction,
                Uprime_rows=Up, J_rows=J, H_rows=H, L_full_port_rows=L,
                ordinary_ports=ordinary, K_selected_coordinate_rows=K,
                H_constant_program=program, H_unit_ADDs_including_three_ADD_SWAP=add_count,
                H_gaussian_fallback_ADDs=gaussian_add_count,
                H_three_shear_ADDs=[len(L_program), len(K_program), len(L_program)],
                correction_source_row_weights=[r.bit_count() for r in correction])


def clean_body(w, geo, masks, dims):
    v, n = w['v'], 2*w['v']+w['R']
    rows = [1 << i for i in range(n)]
    for name in ('A', 'B'):
        for _, d, ss in w[name]:
            for s in ss:
                rows[d] ^= rows[s]
    low = (1 << (2*v))-1
    D = []
    for t in range(v):
        B.need(rows[v+t] & low == (1 << (v+t)) | geo['J_rows'][t],
               'Actual no-scatter raw body has the claimed J endpoint')
        dirt = rows[v+t] >> (2*v)
        srcs = [2*v+i for i in range(w['R']) if dirt >> i & 1]
        if srcs:
            D.append([0, v+t, srcs])
    current = list(w['start'])
    events = []
    def climb(r, new):
        old = current[r]
        if old == new:
            return
        B.need(masks[old] & ~masks[new] == 0 and dims[old] < dims[new], 'Body nested frame')
        events.append(['MOVE', r, old, new, dims[new]-dims[old]])
        current[r] = new
    for section in (D, w['A'], w['B'], w['C']):
        for f, d, ss in section:
            for r in [d]+ss:
                climb(r, f)
            for s in ss:
                events.append(['ADD', d, s, f])
    for r, f in enumerate(w['final']):
        climb(r, f)
    return events, D


def completion(w, geo, masks, dims):
    v, n = w['v'], 2*w['v']+w['R']
    full = next(i for i, d in enumerate(dims) if d == 8)
    events = []
    for a, row in zip(geo['selected'], geo['correction_rows']):
        target = w['final'][v+a]
        B.need(dims[target] == 7 and masks[target] & ~masks[full] == 0, 'Rank-one target hole')
        events.append(['OWNED_CLEAR', n, full])
        for s in range(v):
            if row >> s & 1:
                events.append(['ADD', n, s, full])
        events += [['MOVE', n, full, target, 1], ['ADD', v+a, n, target], ['OWNED_ERASE', n, target]]
    return events


def reverse_body(events):
    return [[op, r, new, old, rank] if op == 'MOVE' else list(event)
            for event in reversed(events)
            for op, r, *tail in [event]
            for old, new, rank in ([tail] if op == 'MOVE' else [[0, 0, 0]])]


def audit(w, geo, events, forward, completion_enabled=True):
    v, n = w['v'], 2*w['v']+w['R']
    current = list(w['start'] if forward else w['final'])+[None]
    rows = [1 << i for i in range(n)]+[0]
    norms = [1]*n+[0]
    maximum = 1
    invoice, counts = Counter(), Counter()
    for event in events:
        op = event[0]
        counts[op] += 1
        if op == 'MOVE':
            _, r, old, new, rank = event
            B.need(current[r] == old, 'Exact physical transition entrance')
            current[r] = new
            invoice[rank] += 1
        elif op == 'ADD':
            _, d, s, frame = event
            B.need(current[d] == current[s] == frame and d != s, 'Literal common-frame XOR')
            rows[d] ^= rows[s]
            norms[d] += norms[s]
            maximum = max(maximum, norms[d])
        elif op == 'OWNED_CLEAR':
            _, r, frame = event
            B.need(r == n and current[r] is None and rows[r] == 0, 'Owned slot is not independent input credit')
            rows[r], norms[r], current[r] = 0, 0, frame
        else:
            B.need(op == 'OWNED_ERASE', 'Known primitive')
            _, r, frame = event
            B.need(r == n and current[r] == frame, 'Erase only the owned completed stream')
            rows[r], norms[r], current[r] = 0, 0, None
    target = geo['H_rows'] if completion_enabled else geo['J_rows']
    expected = [(1 << i) ^ (target[i-v] if v <= i < 2*v else 0) for i in range(n)]+[0]
    B.need(rows == expected, 'All arbitrary sources, targets and helper input columns')
    B.need(current == list(w['final'] if forward else w['start'])+[None], 'Every actual endpoint frame')
    expected_bill = Counter(B.LOCAL)
    expected_bill[7] -= 9
    if completion_enabled:
        expected_bill[1] += 9
    B.need(invoice == expected_bill, 'Complete literal invoice including owned completion')
    return dict(direction='forward' if forward else 'reverse',
                arbitrary_columns=n, arbitrary_dirty_helpers=w['R'],
                owned_fields=1 if completion_enabled else 0,
                owned_field_cleared_after_every_use=current[n] is None,
                paid=dict(sorted(invoice.items())), paid_rank_mass=sum(r*c for r, c in invoice.items()),
                primitive_counts=dict(counts), prefix_positive_majorant=str(maximum),
                prefix_positive_majorant_bits=maximum.bit_length(),
                no_permanent_helper_query_defect=True)


def run():
    start = time.monotonic()
    w, masks, dims = P.load()
    geo = geometry(w)
    body, dirt = clean_body(w, geo, masks, dims)
    complete = completion(w, geo, masks, dims)
    backward_body = reverse_body(body)
    forward, backward = body+complete, complete+backward_body
    checks = [audit(w, geo, forward, True), audit(w, geo, backward, False)]
    no_completion = audit(w, geo, body, True, False)
    B.need(geo['H_rows'] != geo['J_rows'], 'Omitting completion changes the advertised endpoint')
    # New descents are literal complement projectors from the full frame.
    metadata = json.loads((HERE/'sources/pr589-regenerated/records/frames.json').read_text())['frames']
    projectors = B.frame_projectors(metadata)
    physical = []
    for a in geo['selected']:
        line = projectors[w['start'][a]]
        hyp = projectors[w['final'][w['v']+a]]
        B.need(all(line[i][j]+hyp[i][j] == int(i == j) for i in range(8) for j in range(8)),
               'Actual q-line complements the actual target hyperplane')
        physical.append(dict(selected_port=a, source_frame=1, target_frame=w['final'][w['v']+a],
                             rank=1, physical_operator='D_(I−P_qperp)=D_Pq',
                             exact_rational_complement_checked=True))
    artifact = dict(schema='actual-PR589-H-involution-native-word/1',
                    source_sha256=B.WORD_HASH, start=w['start'], final=w['final'],
                    geometry=geo, new_D=dirt, forward=forward, reverse=backward,
                    additional_owned_field=2*w['v']+w['R'],
                    owned_erase_contract='Owned workstream may be cleared in linear stream cost; it is never credited as an independent arbitrary productive input.')
    raw = B.canonical(artifact)
    data = gzip.compress(raw, compresslevel=9, mtime=0)
    out = HERE/'PR589-H-NATIVE.json.gz'
    out.write_bytes(data)
    return dict(schema='actual-PR589-H-involution-native-receipt/1',
                status='PASS_EXACT_NATIVE_H_COMPLETION', source_word_sha256=B.WORD_HASH,
                generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                artifact_sha256=sha256(data).hexdigest(), canonical_artifact_sha256=sha256(raw).hexdigest(),
                scalar_field='F2, literal XOR ADDs and three-ADD SWAP lowering',
                geometry=dict(selected=geo['selected'], defect_rank=9,
                              old_VU_rank=B.bit_rank(geo['VU_rows'], 9), completed_VU_zero=True,
                              H_squared_identity=True, H_equals_J=False,
                              correction_source_row_weights=geo['correction_source_row_weights'],
                              common_frame_H_ADDs=geo['H_unit_ADDs_including_three_ADD_SWAP'],
                              common_frame_H_three_shear_counts=geo['H_three_shear_ADDs'],
                              common_frame_H_gaussian_fallback_ADDs=geo['H_gaussian_fallback_ADDs']),
                full_arbitrary_input_checks=checks,
                omitted_completion_negative_control=dict(expected_endpoint='H', actual_endpoint='J',
                                                          unequal_rows=sum(a != b for a, b in zip(geo['H_rows'], geo['J_rows'])),
                                                          paid=no_completion['paid']),
                physical_completion_contacts=physical,
                changed_local_invoice=dict(rank1_increment=9, rank7_decrement=9,
                                           net_rank_mass_saved=54, owned_field_count=1),
                global_monodromy_closed=False, new_kappa=False,
                runtime_seconds=time.monotonic()-start)


if __name__ == '__main__':
    result = run()
    (HERE/'PR589-H-COMPLETION.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2))
