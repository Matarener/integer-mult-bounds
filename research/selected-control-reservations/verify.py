#!/usr/bin/env python3
"""Source-bound raw5413 address placement, not final compiler admission.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PLAN = 'research/coupled-helper-neutral-completion/capsule/workspace/swarm-coupled-caller-sol-high-20261024/agents/challenge/WHOLECALLER-PLAN-v1.json'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row.get('usage') == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash: ' + row['path'])
    return json.loads((ROOT / PLAN).read_text())


def word_image(word, axes):
    image = list(range(axes))
    for event in word:
        need(len(event) == 3 and event[0] == 'SWAP_BITS', 'unsupported route')
        a, b = event[1:]
        need(type(a) is int and type(b) is int and 0 <= a < axes and 0 <= b < axes and a != b,
             'route axis outside active template')
        image[a], image[b] = image[b], image[a]
    return image


def census(plan):
    need(plan['ambient_axes'] == 145, 'wrong ambient')
    base = list(range(145))
    swaps = 0
    routes = []
    for family in ('main_targets', 'helper_targets', 'idle_jobs'):
        for index, row in enumerate(plan[family]):
            p, inv = row['permutation'], row['inverse_permutation']
            need(sorted(p) == base and sorted(inv) == base, 'not a permutation')
            need([p[inv[a]] for a in base] == base, 'wrong inverse')
            need(p[:row['rank']] == row['active_axes'], 'active-prefix mismatch')
            need(row['absolute_phase'] == 0 and row['affine_translation'] == [], 'non-pure route')
            pre, post = word_image(row['pre_word'], 145), word_image(row['post_word'], 145)
            expected_pre, expected_post = (p, inv) if family == 'idle_jobs' else (inv, p)
            need(pre == expected_pre and post == expected_post, 'source route direction')
            need([pre[post[a]] for a in base] == base, 'route round trip')
            swaps += len(row['pre_word']) + len(row['post_word'])
            routes.append((family, index, row))
    need([len(plan[k]) for k in ('main_targets', 'helper_targets', 'idle_jobs')] == [32, 72, 15], 'route count')
    need(swaps == 16748, 'literal swap count')
    stages = {r['stage']: r['local_axes'] for r in plan['stage_embeddings']}
    need(len(stages) == 18 and len(plan['locals']) == 18, 'local stage count')
    private = []
    for row in plan['stage_embeddings']:
        axes = row['local_axes']
        need(len(axes) == 9 and axes[0] == 0 and len(set(axes)) == 9, 'local plane')
        need(row['same_for_all649_local_fields'] is True and row['spectators'] == 'identity', 'local full-field contract')
        private.extend(axes[1:])
    need(sorted(private) == list(range(1, 145)), 'private plane collision')
    for row in plan['locals']:
        need(row['local_axes'] == stages[row['stage']], 'local stage binding')
    central = 0
    for row in plan['main_targets']:
        need(row['q_exponent'] in (-1, 1), 'Q exponent')
        need(row['central_X_after_LEFT'] == (row['q_exponent'] == -1), 'central correction')
        central += row['central_X_after_LEFT']
    need(central == 16, 'central correction count')
    return routes, {'routes': len(routes), 'swaps': swaps, 'local_planes': 18, 'central_translations': central}


def reservation(d, D, K, G, q0, f, lead=0):
    need(all(type(x) is int for x in (d, D, K, G, q0, f, lead)), 'noninteger dimensions')
    need(d >= D > 0 and min(K, G, q0, f) > 0 and lead >= 0, 'invalid dimensions')
    H = d * G
    qF, qB = (2 * H + K - 1) // K, (H + K - 1) // K
    start, end = (q0 + qF) * K, (D - qB) * K
    origin = start + lead * K
    need(origin + 145 * f * K <= end, 'no raw145 active block: use source fallback')
    fields = ((0, q0 * K), (q0 * K, q0 * K + H),
              (q0 * K + H, q0 * K + 2 * H), (end, end + H))
    need(fields[2][1] <= start and fields[3][1] <= D * K, 'reservation capacity')
    need((f - 1) * G <= H, 'insufficient compact field')
    return {'origin': origin, 'end': end, 'K': K, 'f': f, 'fields': fields,
            'D': D, 'q0': q0, 'qF': qF, 'qB': qB, 'H': H}


def selected_bit(layout, axis, column, rho):
    need(0 <= axis < 145 and 0 <= column < layout['f'] and 0 <= rho < layout['K'], 'bad selected coordinate')
    return layout['origin'] + (axis * layout['f'] + column) * layout['K'] + rho


def check_placement(routes, plan, layout):
    # Endpoint inequalities certify complete integer intervals, not sampled columns.
    origin, f, K = layout['origin'], layout['f'], layout['K']
    need(origin >= layout['fields'][2][1] and origin + 145*f*K <= layout['end'], 'control overlap')
    for _, _, row in routes:
        for word in (row['pre_word'], row['post_word']):
            for _, a, b in word:
                for axis in (a, b):
                    lo, hi = selected_bit(layout, axis, 0, 0), selected_bit(layout, axis, f-1, K-1)
                    need(origin <= lo <= hi < layout['end'], 'route escapes active region')
                    need(all(hi < left or right <= lo for left, right in layout['fields']), 'route uses row or control bit')
    for row in plan['stage_embeddings']:
        spans = [(origin + a*f*K, origin + (a+1)*f*K) for a in row['local_axes']]
        need(len(set(spans)) == 9 and all(origin <= lo < hi <= layout['end'] for lo, hi in spans), 'local physical plane')


def literal_lift(routes):
    # Independent interleaved-column oracle; includes every axis, not tensor payloads.
    checks = 0
    for _, _, row in routes:
        for f in (1, 2, 3):
            for name, scalar_image in (('pre_word', word_image(row['pre_word'], 145)),
                                       ('post_word', word_image(row['post_word'], 145))):
                labels = [(a, j) for a in range(145) for j in range(f)]
                for _, a, b in row[name]:
                    for j in range(f):
                        labels[a*f+j], labels[b*f+j] = labels[b*f+j], labels[a*f+j]
                need(labels == [(scalar_image[a], j) for a in range(145) for j in range(f)], 'column-lift disagreement')
                checks += 145*f
    return checks


def child_packet(row, f, drop_spectator=False):
    # Only IDLE pre_inverseJ puts its actual child on a canonical prefix.
    pre = word_image(row['pre_word'], 145)
    prefix = [(a, j) for a in pre[:row['rank']] for j in range(f)]
    after = [(a, j) for a in pre[row['rank']:] for j in range(f)]
    if drop_spectator:
        after = after[:-1]
    need(prefix == [(a, j) for a in row['active_axes'] for j in range(f)], 'child active prefix')
    need(sorted(prefix + after) == [(a, j) for a in range(145) for j in range(f)], 'child loses spectator')
    need(len(prefix) == row['rank']*f and len(after) == (145-row['rank'])*f, 'child extent')
    return len(prefix), len(after)


def split_row(row, divisors, initial_rows):
    need(initial_rows > 0 and 0 <= row < initial_rows, 'row range')
    total, current, digits = initial_rows, row, []
    for width in divisors:
        need(type(width) is int and width > 0 and total % width == 0, 'nonintegral row split')
        current, w = divmod(current, width)
        digits.append(w)
        total //= width
    restored = current
    for width, w in reversed(list(zip(divisors, digits))):
        restored = restored*width + w
    need(restored == row, 'row return')
    return current, tuple(digits)


def expect_failure(name, action):
    try:
        action()
    except ValueError:
        return name
    raise ValueError('mutation survived: ' + name)


def verify():
    plan = authenticate()
    routes, result = census(plan)
    families = []
    for f in (1, 2, 3, 7, 31, 10**30):
        layout = reservation(1000*f, 1000*f, 64, 3, 11, f, 2)
        check_placement(routes, plan, layout)
        families.append({'f': f, 'origin': layout['origin'], 'active_end': layout['end'],
                         'q0': layout['q0'], 'qF': layout['qF'], 'qB': layout['qB']})
    result['placement_families'] = families
    result['literal_lift_coordinates'] = literal_lift(routes)
    result['idle_child_cases'] = 0
    for row in plan['idle_jobs']:
        for f in (1, 2, 7):
            child_packet(row, f)
            result['idle_child_cases'] += 1
    # Actual final compiler arities are deliberately not replaced by raw10928.
    # These are universal-law boundary controls with arbitrary legal divisors.
    row_cases = 0
    for divisors in ((3, 5), (10928, 418+1), (10**40+7, 10**30+9)):
        stock = 1
        for width in divisors:
            stock *= width
        original = stock+1
        padded = ((original+stock-1)//stock)*stock
        need(original <= padded < 2*original, 'whole-row padding')
        for row in sorted({0, 1, divisors[0]-1, divisors[0], original-1, original, padded-1}):
            split_row(row, divisors, padded)
            row_cases += 1
    result['row_boundary_cases'] = row_cases
    mutations = []
    bad = deepcopy(plan); bad['idle_jobs'][0]['pre_word'] = list(reversed(bad['idle_jobs'][0]['pre_word']))
    mutations.append(expect_failure('IDLE_wrong_pre_direction', lambda: census(bad)))
    bad_axis = deepcopy(plan); bad_axis['main_targets'][0]['pre_word'][0][1] = 145
    mutations.append(expect_failure('route_out_of_template', lambda: census(bad_axis)))
    bad_plane = deepcopy(plan); bad_plane['stage_embeddings'][1]['local_axes'][1] = 1
    mutations.append(expect_failure('stage_private_axis_collision', lambda: census(bad_plane)))
    bad_central = deepcopy(plan); bad_central['main_targets'][0]['central_X_after_LEFT'] = False
    mutations.append(expect_failure('omitted_central_translation', lambda: census(bad_central)))
    layout = reservation(2000, 2000, 64, 3, 11, 2)
    bad_layout = dict(layout, origin=layout['fields'][1][0])
    mutations.append(expect_failure('active_slot_in_front_control', lambda: check_placement(routes, plan, bad_layout)))
    mutations.append(expect_failure('missing_child_spectator', lambda: child_packet(plan['idle_jobs'][0], 2, True)))
    mutations.append(expect_failure('nondivisible_row_stock', lambda: split_row(0, (3, 5), 16)))
    mutations.append(expect_failure('undersized_active_region', lambda: reservation(145, 145, 64, 3, 11, 1)))
    result['semantic_controls'] = mutations
    result['scope'] = 'raw5413 route/reservation binding; expanded compiler injection and stock unverified'
    expected = PACKAGE / 'RESULT.json'
    need(expected.is_file(), 'missing result receipt')
    frozen = json.loads(expected.read_text())
    need(json.dumps(result, sort_keys=True, separators=(',', ':')) ==
         json.dumps(frozen, sort_keys=True, separators=(',', ':')), 'receipt changed')
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_SELECTED_CONTROL_RESERVATIONS')
    return result


if __name__ == '__main__':
    verify()
