#!/usr/bin/env python3
"""Minimum three-row invertible completion of the actual no-COPY PR589 J.

This strengthens the local H experiment: invertibility, with opposite scalar
wrappers in the two orientations, suffices for the noncommuting controller.
Three new rank-one completed-frame gathers are optimal for row-supported
completion because the actual J has corank three. The full direct endpoint
bill still fails, and is recorded without an exponent claim.

Apache-2.0; substantial OpenAI assistance. Immutable local-body attribution
is the retained PR589 eumemic/Claude notice and its cited predecessors.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

import mixed_productive_bit as B
import pr589_h_completion as H
import pr589_state_sharing_probe as P

HERE = Path(__file__).resolve().parent


def completion_geometry(J):
    v = len(J)
    basis, dependent = [], []
    for i, row in enumerate(J):
        if B.bit_rank(basis+[row], v) > len(basis):
            basis.append(row)
        else:
            dependent.append(i)
    original_rank = len(basis)
    B.need(original_rank == 108 and len(dependent) == 3, 'Actual J corank is three')
    G, correction, choices = list(J), [], []
    for a in dependent:
        j = next(j for j in range(v) if B.bit_rank(basis+[1 << j], v) > len(basis))
        basis.append(1 << j)
        correction.append(J[a] ^ (1 << j))
        choices.append(j)
        G[a] = 1 << j
    inverse = B.bit_inverse(G)
    B.need(B.bit_rank(G, v) == v, 'Three literal rows complete invertibility')
    B.need(B.bit_rank(correction, v) == 3, 'Correction has exact rank three')
    forward_program, forward_adds = B.bit_factor(G)
    inverse_program, inverse_adds = B.bit_factor(inverse)
    return dict(J_rows=J, H_rows=G, G_rows=G, G_inverse_rows=inverse,
                J_rank=original_rank, selected=dependent, replacement_source_columns=choices,
                correction_rows=correction, correction_source_row_weights=[r.bit_count() for r in correction],
                forward_constant_program=forward_program, inverse_constant_program=inverse_program,
                forward_constant_ADDs=forward_adds, inverse_constant_ADDs=inverse_adds)


def scalar_program(program, offset, frame):
    out = []
    for op, d, s in program:
        d, s = offset+d, offset+s
        if op == 'ADD':
            out.append(['ADD', d, s, frame])
        else:
            B.need(op == 'SWAP', 'Constant program has binary ADD/SWAP only')
            out += [['ADD', d, s, frame], ['ADD', s, d, frame], ['ADD', d, s, frame]]
    return out


def audit(w, geo, events, forward, wrapped=False):
    v, n = w['v'], 2*w['v']+w['R']
    cur = list(w['start'] if forward else w['final'])+[None]
    values = [1 << i for i in range(n)]+[0]
    norms, maximum = [1]*n+[0], 1
    paid, counts = Counter(), Counter()
    for event in events:
        op = event[0]
        counts[op] += 1
        if op == 'MOVE':
            _, r, old, new, rank = event
            B.need(cur[r] == old, 'Literal frame entrance')
            cur[r] = new
            paid[rank] += 1
        elif op == 'ADD':
            _, d, s, f = event
            B.need(cur[d] == cur[s] == f and d != s, 'Literal common-frame XOR')
            values[d] ^= values[s]
            norms[d] += norms[s]
            maximum = max(maximum, norms[d])
        elif op == 'OWNED_CLEAR':
            _, r, f = event
            B.need(r == n and values[r] == 0 and cur[r] is None, 'One separately owned field')
            values[r], norms[r], cur[r] = 0, 0, f
        else:
            B.need(op == 'OWNED_ERASE', 'Known native primitive')
            _, r, f = event
            B.need(r == n and cur[r] == f, 'Owned transformed stream may be erased')
            values[r], norms[r], cur[r] = 0, 0, None
    expected = [1 << i for i in range(n)]+[0]
    if wrapped:
        matrix = geo['G_rows'] if forward else geo['G_inverse_rows']
        for i, row in enumerate(matrix):
            expected[i] = row
            expected[v+i] = row ^ (row << v)
    else:
        for i, row in enumerate(geo['G_rows']):
            expected[v+i] ^= row
    B.need(values == expected, 'All 661 arbitrary original data/helper columns')
    B.need(cur == list(w['final'] if forward else w['start'])+[None], 'All native endpoint frames')
    want = Counter(B.LOCAL)
    want[7] -= 9
    want[1] += 3
    B.need(paid == want, 'Three new rank-one requests and no hidden center return')
    return dict(direction='forward' if forward else 'reverse', wrapped=wrapped,
                arbitrary_columns=n, restored_dirty_helpers=w['R'], paid=dict(sorted(paid.items())),
                paid_rank_mass=sum(r*c for r, c in paid.items()), primitive_counts=dict(counts),
                prefix_positive_majorant=str(maximum), prefix_positive_majorant_bits=maximum.bit_length(),
                owned_fields=1, owned_clear_erase_episodes=3)


def run():
    start = time.monotonic()
    w, masks, dims = P.load()
    h_path = HERE/'PR589-H-NATIVE.json.gz'
    h = json.loads(gzip.decompress(h_path.read_bytes()))
    geo = completion_geometry(h['geometry']['J_rows'])
    body, D = H.clean_body(w, geo, masks, dims)
    correction = H.completion(w, geo, masks, dims)
    forward = body+correction
    reverse = correction+H.reverse_body(body)
    wrapped_forward = (scalar_program(geo['forward_constant_program'], 111, 0)+
                       forward+scalar_program(geo['forward_constant_program'], 0, 1))
    wrapped_reverse = (scalar_program(geo['inverse_constant_program'], 0, 1)+
                       reverse+scalar_program(geo['inverse_constant_program'], 111, 0))
    checks = [audit(w, geo, forward, True), audit(w, geo, reverse, False),
              audit(w, geo, wrapped_forward, True, True), audit(w, geo, wrapped_reverse, False, True)]
    # Removing even one completion row leaves rank at most110. This is a
    # concrete negative control as well as the corank lower bound.
    controls = []
    for a in geo['selected']:
        wrong = list(geo['G_rows'])
        wrong[a] = geo['J_rows'][a]
        rank = B.bit_rank(wrong, 111)
        B.need(rank == 110, 'Every one of the three completions is necessary here')
        controls.append(dict(omitted_selected_port=a, resulting_rank=rank))
    paid = Counter({int(r): 7*n for r, n in checks[0]['paid'].items()})
    paid[7] += 1332
    targets = Counter({8: 3073, 22: 444, 50: 222})
    repaired = paid.copy()
    repaired[1] += 666
    margin = lambda profile: sum(r*n for r, n in targets.items())-sum(r*n for r, n in profile.items())
    B.need(margin(paid) == 645 and margin(repaired) == -21, 'Full source/helper/output invoice')
    artifact = dict(schema='actual-PR589-minimum-invertible-completion-native-word/1',
                    geometry=geo, start=w['start'], final=w['final'], new_D=D,
                    forward=forward, reverse=reverse,
                    wrapped_forward=wrapped_forward, wrapped_reverse=wrapped_reverse,
                    owned_field=2*w['v']+w['R'],
                    source_word_sha256=B.WORD_HASH)
    raw = B.canonical(artifact)
    data = gzip.compress(raw, compresslevel=9, mtime=0)
    (HERE/'PR589-MINIMUM-COMPLETION-NATIVE.json.gz').write_bytes(data)
    return dict(schema='actual-PR589-minimum-invertible-completion-receipt/1',
                status='PASS_MINIMUM_THREE_ROW_NATIVE_COMPLETION_GLOBAL_DEBT_UNFUNDED',
                source_word_sha256=B.WORD_HASH, generator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                H_source_artifact_sha256=sha256(h_path.read_bytes()).hexdigest(),
                artifact_sha256=sha256(data).hexdigest(), canonical_artifact_sha256=sha256(raw).hexdigest(),
                J_rank=108, completed_rank=111, minimum_row_supported_correction_rank=3,
                minimum_proof='rank(J+E)-rank(J)<=rank(E)<=number of modified rows; the three displayed row replacements attain the bound.',
                selected=geo['selected'], replacement_source_columns=geo['replacement_source_columns'],
                correction_source_row_weights=geo['correction_source_row_weights'],
                common_frame_G_ADDs=geo['forward_constant_ADDs'], common_frame_G_inverse_ADDs=geo['inverse_constant_ADDs'],
                full_arbitrary_input_checks=checks, omitted_row_negative_controls=controls,
                physical_completion='Each selected target is its native q-perp; the completed source bank is fullI8. Their exact complement is native rank-one Pq, as in the independently audited H completion.',
                global_contract='In the pair gauge S=diag(I,Q), forward wrapped multiplier is G_s b_s and reverse wrapped multiplier is G_s^-1 b_s. Both multiply the two fields equally, so the same noncommuting interval factorization applies.',
                global_raw_paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())), raw_rank_margin=645,
                direct_head_repair_rank1_calls=666, direct_repaired_paid=dict(sorted(repaired.items())),
                direct_repaired_rank_margin=-21,
                exact_raw_margin_at_004=B.interval_row(B.margin_interval(paid, targets, Q(1, 250))),
                exact_repaired_margin_at_004=B.interval_row(B.margin_interval(repaired, targets, Q(1, 250))),
                no_new_global_closure=True, new_kappa=False,
                runtime_seconds=time.monotonic()-start)


if __name__ == '__main__':
    result = run()
    (HERE/'PR589-MINIMUM-COMPLETION.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'selected', 'replacement_source_columns', 'correction_source_row_weights',
                                           'common_frame_G_ADDs', 'common_frame_G_inverse_ADDs', 'full_arbitrary_input_checks',
                                           'raw_rank_margin', 'direct_repaired_rank_margin', 'runtime_seconds')}, indent=2))
