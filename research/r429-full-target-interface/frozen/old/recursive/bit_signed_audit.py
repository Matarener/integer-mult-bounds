#!/usr/bin/env python3
"""Independent exact signed local replay and whole added-code growth bound.

The original-window controller is proved over binary VALUES. The integer
program is its literal signed lift, with no assertion that its global integer
endpoint is the binary identity. Prefix row-norms give a separate bound valid
under isometric owner/address permutations. No endpoint decoder is assumed.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
N, V = 660, 111


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def identity(n):
    return [{i: 1} for i in range(n)] + [{}]


def add(a, b, c):
    output = a.copy()
    for j, value in b.items():
        output[j] = output.get(j, 0) + c * value
        if not output[j]:
            del output[j]
    return output


def row_weights(row):
    return tuple(sum(abs(c) for j,c in row.items() if low <= j < high)
                 for low,high in ((0,V),(V,2*V),(2*V,N)))


def replay(records, backward=False, initial=None):
    rows = [row.copy() for row in (identity(N) if initial is None else initial)]
    open_source = None
    prefix = 1
    envelope = {(1,0,0),(0,1,0),(0,0,1)}
    copies = 0
    for op, dst, src, c, frame, phase in reversed(records) if backward else records:
        if op == 1:
            need(open_source is None or dst != open_source, 'integer snapshot source mutated')
            rows[dst] = add(rows[dst], rows[src], -c if backward else c)
            weights = row_weights(rows[dst])
            envelope.add(weights)
            prefix = max(prefix, sum(weights))
        elif op == (3 if backward else 2):
            need(open_source is None and src == N and not rows[N], 'integer COPY overwrites private')
            rows[N] = rows[dst].copy()
            open_source = dst
            copies += 1
        elif op == (2 if backward else 3):
            need(open_source == dst and rows[N] == rows[dst], 'integer ERASE original snapshot')
            rows[N], open_source = {}, None
        else:
            need(op == 0, 'integer record opcode')
    need(open_source is None and not rows[N] and copies == 6, 'integer private endpoint')
    return rows, prefix, envelope


def parity(rows):
    return [sum(1 << j for j,c in row.items() if c & 1) for row in rows]


def dense_digest(rows, n):
    # Producer's documented signed-matrix digest is one comma-delimited row
    # per line, distinct from its canonical JSON word digest.
    h = sha256()
    for row in rows:
        h.update((','.join(str(row.get(j,0)) for j in range(n)) + '\n').encode())
    return h.hexdigest()


def block_norms(rows):
    src = max(sum(abs(c) for c in row.values()) for row in rows[:V])
    target_x = max(row_weights(row)[0] for row in rows[V:2*V])
    target_h = max(row_weights(row)[2] for row in rows[V:2*V])
    return {'source_endpoint_row_norm': src,
            'target_source_block_row_norm': target_x,
            'target_helper_block_row_norm': target_h}


def code(records):
    records = [r for r in records if r[0] == 1 and 21 <= r[5] <= 24]
    output, prefixes = [], []
    for backward in (False, True):
        rows = [{i: 1} for i in range(V)]
        prefix = 1
        for _, d, s, c, f, phase in reversed(records) if backward else records:
            need(d < V and s < V and d != s, 'source code not inplace')
            rows[d] = add(rows[d], rows[s], -c if backward else c)
            prefix = max(prefix, sum(abs(c) for c in rows[d].values()))
        output.append(rows)
        prefixes.append(prefix)
    rows = [row.copy() for row in output[0]]
    for _, d, s, c, f, phase in reversed(records):
        rows[d] = add(rows[d], rows[s], -c)
    need(rows == [{i: 1} for i in range(V)], 'signed source-code literal inverse')
    norms = [max(sum(abs(c) for c in row.values()) for row in a) for a in output]
    return records, output, prefixes, norms


def global_bound(ordered, local, local_prefix, envelopes, code_prefix, code_norm):
    norms = [[1,1] for _ in range(4)]
    maximum = 1
    checkpoints = []
    counts = Counter()
    for event in ordered:
        op = event.get('op')
        if op == 'code sweep':
            p, side = event['pair'], int(event['side'] == 'Y')
            for s in event['stages']:
                reverse = s % 2
                counts['inverse_code' if reverse else 'forward_code'] += 1
                maximum = max(maximum, code_prefix[reverse] * norms[p][side])
                norms[p][side] *= code_norm[reverse]
        elif op == 'complete local coded call':
            p, reverse = event['pair'], int(event['reverse'])
            src_side = 1 if reverse else 0
            dst_side = 1 - src_side
            x, y = norms[p][src_side], norms[p][dst_side]
            # Hosted helpers may live in an already preloaded idle DATA bank.
            # Their normalized coefficients are therefore bounded by the
            # largest current bank norm, rather than by fresh independent1.
            h = max(n for pair in norms for n in pair)
            maximum = max(maximum, max(a*x + b*y + c*h for a,b,c in envelopes[reverse]))
            endpoint = local[reverse]
            norms[p][src_side] = endpoint['source_endpoint_row_norm'] * x
            norms[p][dst_side] = y + endpoint['target_source_block_row_norm'] * x + endpoint['target_helper_block_row_norm'] * h
            counts['local_inverse' if reverse else 'local_forward'] += 1
            checkpoints.append({'stage': event['stage'], 'prefix_upper_bits': maximum.bit_length()})
        elif event.get('kind') == 'bridge':
            d, s = event['dst'], event['src']
            norms[d][0] += norms[s][0]
            norms[s][1] += norms[d][1]
            maximum = max(maximum, *(n for pair in norms for n in pair))
            counts['scalar_bridge_shears'] += 2
        elif event.get('kind') == 'exchange':
            norms = [[y,x] for x,y in norms]
    need(counts == Counter(forward_code=35, inverse_code=28, local_forward=5,
                          local_inverse=4, scalar_bridge_shears=18), 'whole added-code count')
    crude = (1 << 18) * local_prefix[0]**5 * local_prefix[1]**4 * code_prefix[0]**35 * code_prefix[1]**28
    need(maximum <= crude, 'weighted global bound exceeds product upper')
    # Completing the easy four FULL banks applies the nine inverse G factors
    # independently on each bank; the maximum norm multiplies by one such
    # sequence, not its fourth power.
    completed_decode = code_prefix[0]**4 * code_prefix[1]**5
    return {'ordered_extra_code_counts': dict(counts),
            'all63_code_factors_included': True,
            'encoded_hosted_helper_inputs_bounded': True,
            'weighted_global_prefix_upper': str(maximum),
            'weighted_global_prefix_upper_bits': maximum.bit_length(),
            'charge_rounded_up_to_64_bits': 64*((maximum.bit_length()+63)//64),
            'crude_product_prefix_upper_bits': crude.bit_length(),
            'after_easy_completed_bank_decode_upper_bits': (maximum*completed_decode).bit_length(),
            'local_stage_checkpoints': checkpoints,
            'norm_proof': 'owner/address permutations are isometries; each hosted helper is bounded by the largest current encoded DATA-bank norm. Use exact local block-prefix envelopes, exact source code prefix norm, endpoint block norms and triangle inequalities at actual bridges',
            'limits': 'terminal hole decoder omitted; tape, native child interior defect and all-size rounded-interface theorem remain separate'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    meta = json.loads((HERE/'BIT-SIGNED-INPUT.json').read_bytes())
    compressed = (HERE/'BIT-SIGNED-INPUT-WORD.json.gz').read_bytes()
    raw = gzip.decompress(compressed)
    need(sha256(compressed).hexdigest() == meta['word_gzip_sha256'] and
         sha256(raw).hexdigest() == meta['word_canonical_sha256'], 'actual signed producer word hashes')
    program = json.loads(raw)
    frozen = json.loads((HERE/'BIT-THREE-ROW-INPUT.json').read_bytes())
    records, matrices = program['records'], frozen['matrices']
    forward, f, ef = replay(records)
    inverse, r, er = replay(records, True)
    roundtrip, _, _ = replay(records, True, forward)
    need(roundtrip == identity(N), 'full signed inverse roundtrip')
    need(f == meta['prefix_F'] and r == meta['prefix_R'], 'independent exact prefix discrepancy')
    source_code, source_rows, source_prefix, source_norm = code(records)
    for direction, rows in enumerate((forward, inverse)):
        for p in range(V):
            need(rows[p] == source_rows[direction][p], 'integer source interface has dirt/target dependence')
            need(rows[V+p].get(V+p) == 1 and all(j < V or j == V+p or j >= 2*V for j in rows[V+p]),
                 'integer target self block')
            need(all(not c & 1 for j,c in rows[V+p].items() if j >= 2*V), 'odd helper leakage')
        for h in range(2*V,N):
            need(rows[h] == {h:1}, 'integer helper not literally restored')
        expected = [1 << i for i in range(N)] + [0]
        for p in range(V):
            expected[p] = matrices['Hinv' if direction else 'H'][p]
            expected[V+p] ^= (1 << p) if direction else matrices['H'][p]
        need(parity(rows) == expected, 'integer lift is not actual all-column BIT code')
    need(dense_digest(source_rows[0],V) == meta['source_integer_matrix_sha256'] and
         dense_digest(source_rows[1],V) == meta['source_integer_inverse_sha256'], 'source code digest')
    ordered = json.loads((HERE/'BIT-NATIVE-CONTROLLER-WORD.json').read_bytes())['ordered_controller']
    bound = global_bound(ordered, [block_norms(forward),block_norms(inverse)],
                         [f,r], [ef,er], source_prefix, source_norm)
    result = {'status':'PASS_INDEPENDENT_SIGNED_BIT_LIFT_AND_ALL63_CODE_GROWTH_ENDPOINT_OPEN',
              'signed_word_canonical_sha256':meta['word_canonical_sha256'],
              'all_integer_columns_each_orientation':N, 'literal_helpers_restored':438,
              'full_forward_inverse_roundtrip':True, 'local_exact_prefix':[f,r],
              'local_old_formula_bits':[(64*f**3*r**2).bit_length(),((1<<18)*f**5*r**4).bit_length()],
              'source_code_ADDs':len(source_code), 'source_code_exact_prefix':source_prefix,
              'source_code_endpoint_norm':source_norm,
              'local_endpoint_block_norms':[block_norms(forward),block_norms(inverse)],
              'global_controller_growth':bound,
              'integer_scope':'The source is A_Z x, helpers exactly restored, target self identity and even helper leakage. The desired coded target identity is over F2; no integer identity substitution is made.',
              'limits':['exact signed scalar normalization and copied snapshots, not internal native child errors',
                        'no global restored endpoint or terminal N E^-1 N implementation',
                        'new charged precision theorem, physical source/tape invoice and modern all-size release not supplied',
                        'no supplier or conditional kappa claim']}
    if args.write:
        (HERE/'BIT-SIGNED-AUDIT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads((HERE/'BIT-SIGNED-AUDIT.json').read_bytes()) == json.loads(canonical(result)),
             'complete signed/controller growth receipt differs')
    print(result['status'])
    print('local norms',f,r,'all63 bridge prefix bits',bound['weighted_global_prefix_upper_bits'])


if __name__ == '__main__':
    main()
