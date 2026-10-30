#!/usr/bin/env python3
"""Exact nine-call dirty-core factors with the literal T360 owner assignments.

This verifies the scalar specialization of the changed global contract. Native
payload and cover operators are deliberately NOT assigned a zero-cost terminal
implementation. Rank here is a matrix rank, not a lower bound on recursive cost.

Apache-2.0; substantial OpenAI Codex assistance. The retained PR3734 and
kappa-consumer-followup authors retain credit for the source word and local pair.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def module(path):
    env = {'__name__': 'retained_source', '__file__': str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec'), env)
    return type('Source', (), env)


def add(dst, src, scale=F(1)):
    for key, value in src.items():
        dst[key] = dst.get(key, F(0)) + scale * value
        if not dst[key]:
            del dst[key]


def dot(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum((value * b.get(key, F(0)) for key, value in a.items()), F(0))


def eye():
    return [[F(i == j) for j in range(8)] for i in range(8)]


def shear(p, invp, dst, src, coefficient):
    p[dst] = [x + coefficient * y for x, y in zip(p[dst], p[src])]
    # P' = E P, hence P'^-1 = P^-1 E^-1.
    for row in invp:
        row[src] -= coefficient * row[dst]


def recipe_tail(stage, pair):
    changes = []
    if stage in (1, 3, 5):
        changes += [(2*pair, 2*(pair+1), 1), (2*(pair+1)+1, 2*pair+1, -1)]
    if stage in (2, 4, 6):
        changes += [(2*pair, 2*(pair+1), -1), (2*(pair+1)+1, 2*pair+1, 1)]
    if stage == 8:
        for pair in (2, 1, 0):
            changes += [(2*(pair+1), 2*pair, 1), (2*pair+1, 2*(pair+1)+1, -1)]
    return changes


def map_vector(local, mapping, prefixes, inverse_prefixes, image):
    out = {}
    for role, value in local.items():
        family = mapping[role]
        owner, within = divmod(family, 896)
        bank, port = divmod(within, 112)
        if image:
            weights = [row[bank] for row in inverse_prefixes[owner]]
        else:
            weights = prefixes[owner][bank]
        add(out, {896*owner+112*b+port: w for b, w in enumerate(weights) if w}, value)
    return out


def modular_rank(rows, prime=1000003):
    """A nonzero modular minor certifies the same lower bound over Q."""
    pivots = {}
    witness = []
    det = 1
    for row_number, row in enumerate(rows):
        r = {key: (v.numerator * pow(v.denominator, -1, prime)) % prime for key, v in row.items()}
        r = {key: value for key, value in r.items() if value}
        while r:
            key = min(r)
            if key not in pivots:
                pivot = r[key]
                det = det * pivot % prime
                inv = pow(pivot, -1, prime)
                pivots[key] = {k: v*inv % prime for k, v in r.items()}
                witness.append({'row': row_number, 'column': key, 'pivot_mod_prime': pivot})
                break
            factor = r[key]
            for k, v in pivots[key].items():
                r[k] = (r.get(k, 0) - factor*v) % prime
                if not r[k]:
                    del r[k]
    return {'rank': len(pivots), 'prime': prime, 'pivots': witness, 'pivot_product_mod_prime': det}


def apply_factor(state, factor):
    values = [dot(row, state) for row in factor['V']]
    out = state.copy()
    for row, value in zip(factor['U'], values):
        add(out, row, value)
    return out


def serializable(rows):
    return [{str(k): str(v) for k, v in sorted(row.items())} for row in rows]


def run(followup, out, replicas):
    recovered = followup/'artifact/recovered-involutory'
    source = followup/'artifact/live-source/research/staged544-producer-return'
    local = followup/'artifact/integer-mult-bounds/research/kappa-consumer-followup/controller'
    m = module(recovered/'modern_native_component.py')
    c = module(local/'check_controller.py')
    inp = recovered/'modern-source/inputs'
    receipt = read(inp/'NATIVE-RECEIPT.json')
    need(m.digest(inp/'NATIVE-RECEIPT.json') == m.NATIVE_RECEIPT_SHA, 'native receipt source pin')
    item = receipt['providers']['base']
    loc = inp/'native-cache'/item['word_sha256']/'local'
    paths = [loc/'CANONICAL-WORD.json.gz', loc/'LOCAL-PROGRAMS.json.gz']
    for path in paths:
        need(m.digest(path) == item['complete_native_files']['local/'+path.name], 'local source payload pin')
    word, programs = map(read, paths)
    R, K, _, _, _, _ = m.clean_reconstruction(word, programs)
    cut = programs['forward'].index(['phase', 'centers'])
    before = m.replay(programs['forward'][:cut])
    H = [{role: a for (role, warp), a in before['L', center].items() if role >= 224 and not warp}
         for center in word['centers']]
    pivots = (224, 225, 227, 229, 240, 241, 256, 257)
    pinv = c.inverse([[row.get(h, F(0)) for h in pivots] for row in H])
    query = []
    for r, h in zip(R, H):
        row = r.copy()
        add(row, h)
        query.append(row)
    images = [{p: -row[k] for p, row in enumerate(K) if k in row} for k in range(8)]
    for i, h in enumerate(pivots):
        for k, value in enumerate(pinv[i]):
            if value:
                images[k][h] = 12*value
    need([[dot(v, u) for u in images] for v in query] ==
         [[F(-2*(i == j)) for j in range(8)] for i in range(8)], 'Q A = -2 I')

    owner_inputs = source/'inputs'
    order = read(owner_inputs/'ORDER.json')
    fill = read(owner_inputs/'FILL.json.gz')['rows']
    plan = read(owner_inputs/'PLAN.json.gz')
    family_bank = {int(child): 2*pair+plan['sides'][child] for child, pair in plan['pairs'].items()}
    mappings = {}
    later_uses = Counter()
    for time, h, owner, child, port, offset in fill:
        family = 896*owner + 112*family_bank[child] + port
        later_uses[family] += 1
        if order[time][1] in replicas:
            mappings.setdefault(time, {})[224+h] = family
    prefixes, inverse_prefixes = [eye() for _ in range(360)], [eye() for _ in range(360)]
    factors = {replica: [] for replica in replicas}
    pair_sequence = (0, 0, 0, 1, 1, 2, 2, 3, 3)
    stages_seen = [-1]*360
    for time, (stage, replica) in enumerate(order):
        need(stages_seen[replica] == stage-1, 'per-replica chronological order')
        stages_seen[replica] = stage
        pair = pair_sequence[stage]
        if replica in replicas:
            mapping = mappings[time]
            for p in range(224):
                mapping[p] = 896*replica + 224*pair + p
            need(len(mapping) == 632 and len(set(mapping.values())) == 632, 'literal local family uniqueness')
            image, q = (query, images) if stage % 2 else (images, query)
            U = [map_vector(row, mapping, prefixes, inverse_prefixes, True) for row in image]
            V = [map_vector(row, mapping, prefixes, inverse_prefixes, False) for row in q]
            need([[dot(v, u) for u in U] for v in V] ==
                 [[F(-2*(i == j)) for j in range(8)] for i in range(8)], 'owner-conjugated involution')
            factors[replica].append({'stage': stage, 'time': time, 'orientation': 'backward' if stage % 2 else 'forward',
                                     'mapping': mapping.copy(), 'U': U, 'V': V})
        changes = [(2*pair, 2*pair+1, -1)] if stage % 2 else [(2*pair+1, 2*pair, 1)]
        changes += recipe_tail(stage, pair)
        for dst, src, coefficient in changes:
            shear(prefixes[replica], inverse_prefixes[replica], dst, src, coefficient)
    need(stages_seen == [8]*360, 'complete T360 clock')
    S = eye()
    for pair in range(4):
        S[2*pair][2*pair] = S[2*pair+1][2*pair+1] = F(0)
        S[2*pair][2*pair+1], S[2*pair+1][2*pair] = F(-1), F(1)
    need(all(p == S for p in prefixes), 'all ordinary replicas reach exact signed exchange')

    out.mkdir(parents=True, exist_ok=True)
    result = {'status': 'PASS_OWNER_COUPLED_NINE_FACTORS_SCALAR_SPECIALIZATION', 'replicas': {},
              'scope': 'Actual owners and chronological ordinary bank prefixes; native payload operators remain unevaluated. Matrix ranks are not recursive-child lower bounds.',
              'source_sha256': {str(p.relative_to(followup)): sha256(p.read_bytes()).hexdigest() for p in paths +
                               [owner_inputs/f for f in ('ORDER.json', 'FILL.json.gz', 'PLAN.json.gz')]},
              'model': 'Exactly one replica uses nine changed local words; all other calls use the original supplier, so their later uses of changed helpers are propagated by their ordinary prefixes.',
              'defect_factor': 'E_j = I + (P_j^-1 A_j)(Q_j P_j); backward swaps A_j and Q_j^T.',
              'product_rank_argument': 'M-I=U T V, with U=[U_0,...,U_8], V=[V_0;...;V_8], T block-lower-unitriangular. Full rank72 of U and V therefore certifies rank(M-I)=72.'}
    for replica, fs in factors.items():
        all_u, all_v = [row for f in fs for row in f['U']], [row for f in fs for row in f['V']]
        ur, vr = modular_rank(all_u), modular_rank(all_v)
        support = sorted({key for row in all_u+all_v for key in row})
        test_input = {key: F((key*104729+7919) % 127 - 63) for key in support
                      if (key*104729+7919) % 127 != 63}
        changed = test_input.copy()
        for f in fs:
            changed = apply_factor(changed, f)
        restored = changed.copy()
        for f in reversed(fs):
            restored = apply_factor(restored, f)
        need(restored == test_input, 'complete nine-factor reversal with dirty input')
        wrong = changed.copy()
        for f in fs:
            wrong = apply_factor(wrong, f)
        need(wrong != test_input, 'wrong inverse order rejection')
        need(changed != test_input, 'uncompleted helper propagation is detected')
        payload = [{'stage': f['stage'], 'time': f['time'], 'orientation': f['orientation'],
                    'physical_mapping': f['mapping'], 'U_columns': serializable(f['U']), 'V_rows': serializable(f['V'])}
                   for f in fs]
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
        (out/f'FACTORS-replica-{replica}.json.gz').write_bytes(gzip.compress(raw, mtime=0))
        counts = Counter()
        for f in fs:
            roles = set(H_role for row in H for H_role in row) if f['stage'] % 2 else set(pivots)
            for h in roles:
                counts[later_uses[f['mapping'][h]]] += 1
        result['replicas'][str(replica)] = {'calls': 9, 'low_rank_factors': 72, 'image_rank_witness': ur,
              'query_rank_witness': vr, 'exact_defect_rank': 72 if ur['rank'] == vr['rank'] == 72 else None,
              'active_physical_family_support': len(support), 'active_owners': len({p//896 for p in support}),
              'dirty_nonzero_input_families': sum(bool(v) for v in test_input.values()),
              'nine_factor_reverse_restores_every_touched_family': True, 'wrong_inverse_order_rejected': True,
              'uncompleted_word_changes_state': True, 'changed_family_total_helper_contact_histogram': dict(counts),
              'factor_payload_sha256': sha256(raw).hexdigest()}
    (out/'OWNER-COUPLED-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--followup', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    parser.add_argument('--replicas', type=int, nargs='+', default=[0, 179, 359])
    args = parser.parse_args()
    result = run(args.followup, args.out, set(args.replicas))
    print(result['status'])
    for replica, record in result['replicas'].items():
        print(f"replica {replica}: exact scalar defect rank {record['exact_defect_rank']}, "
              f"{record['active_physical_family_support']} families across {record['active_owners']} owners")
