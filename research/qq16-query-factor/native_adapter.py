"""Independent native-phase and normalized-route screen, without logical replay.

The package driver authenticates source bytes before importing this module.
This is not a native compiler: it proves a concrete omitted-adapter witness
and rejects a stated separately normalized route under an explicit tariff.
New work by Chris R / Clear1nsight with OpenAI Codex assistance, Apache-2.0.
"""
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
PHASE_MEMBER = 't16/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def parity(value):
    return value.bit_count() % 2


def phase(terms, character):
    return sum(coefficient * parity(axis & character)
               for axis, coefficient in terms) % 4


def mono(recipe, address):
    exponent = recipe['phase']
    for j in range(9):
        if address >> j & 1:
            exponent += recipe['linear_Z4'][j]
            exponent += 2 * (recipe['quadratic_rows'][j] & address).bit_count()
    mapped = recipe['offset']
    for j, row in enumerate(recipe['matrix_rows']):
        mapped ^= parity(row & address) << j
    return mapped, exponent % 4


def kernel(recipe, address):
    middle, exponent = mono(recipe['right'], address)
    result = {}
    for position, value in ((middle, (1, 1)), (middle ^ 1, (1, -1))):
        output, extra = mono(recipe['left'], position)
        real, imag = value
        for _ in range((exponent + extra) % 4):
            real, imag = -imag, real
        old = result.get(output, (0, 0))
        result[output] = (old[0] + real, old[1] + imag)
    return {key: value for key, value in result.items() if value != (0, 0)}


def act(columns, vector):
    result = 0
    for i in range(73):
        if vector >> i & 1:
            result ^= columns[i]
    return result


def source_route(record, stage):
    axes = record['idle_children'][0]['orthogonal_axes'][:8]
    swaps = [axis ^ (1 << (9 + 8 * (stage - 1) + i)) for i, axis in enumerate(axes)]
    return tuple((1 << j) ^ act(swaps + [0] * (73-len(swaps)),
                 sum(parity((1 << j) & vector) << i for i, vector in enumerate(swaps)))
                 for j in range(73))


def polar_rank(terms):
    rows = [0] * 73
    for axis, coefficient in terms:
        if coefficient % 2:
            for j in range(73):
                if axis >> j & 1:
                    rows[j] ^= axis
    pivots = {}
    for initial in rows:
        row = initial
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def candidate_phase_audit(records, full):
    raw = (PKG / 'CANDIDATE-WORD.json').read_bytes()
    word = json.loads(raw)
    identity = tuple(1 << j for j in range(73))
    # Independently derive every named route from source chart swaps.
    for name, values in word['routes'].items():
        g = tuple(values)
        if name == 'I':
            expected = identity
        elif name.startswith('r1_'):
            expected = source_route(records[int(name[3:])], 1)
        elif name.startswith('r2_'):
            expected = source_route(records[int(name[3:])], 2)
        else:
            need(name.startswith('r21_'), 'known literal owner route name')
            p = int(name[4:])
            left, right = source_route(records[p], 2), source_route(records[p], 1)
            expected = tuple(act(left, v) for v in right)
        need(g == expected, 'literal route derives from pinned source chart')
    owned = set(word['owned_fields'])

    def frame(field):
        if field in owned or field.startswith('X'):
            return tuple(tuple(term) for term in full)
        need(field.startswith('Y'), 'known current or owned field')
        return tuple(tuple(term) for term in full) + ((records[int(field[1:])]['q'], -1),)

    @lru_cache(None)
    def adapter(target, source, route):
        g = tuple(word['routes'][route])
        moved = tuple((act(g, axis), -coefficient) for axis, coefficient in frame(source))
        terms = frame(target) + moved
        return polar_rank(terms), terms

    histogram = Counter()
    first = None
    stage_two = None
    for index, event in enumerate(word['events']):
        if event[0] == 'clear':
            need(event[1] in owned, 'owned-only initialization and retirement')
            continue
        need(event[0] == 'add_view', 'known literal query-factor gate')
        _, target, source, coefficient, route = event
        rank, terms = adapter(target, source, route)
        histogram[rank] += 1
        if first is None:
            g = tuple(word['routes'][route])
            character = 1
            moved_terms = [(act(g, a), c) for a,c in frame(source)]
            target_phase = phase(frame(target), character)
            moved_phase = phase(moved_terms, character)
            need(target_phase != moved_phase and (target_phase-moved_phase)%2 == 1,
                 'first literal gate needs more than a payload translation')
            first = {'event_index': index, 'event': event, 'owner': 'identity',
                     'payload_character': 'e0', 'raw_routed_source_phase_mod4': moved_phase,
                     'required_target_phase_mod4': target_phase, 'required_adapter_polar_rank': rank,
                     'translation_only_rejected': True}
        if stage_two is None and route.startswith('r2_') and rank >= 16:
            stage_two = {'event_index':index, 'event':event, 'required_adapter_polar_rank':rank}
    need(first is not None and stage_two is not None, 'actual ingress and future-route phase witnesses')
    return {'candidate_word_sha256':hashlib.sha256(raw).hexdigest(),
            'scope':'gatewise phase obligations under declared F17 owned carrier; not an additive fused-word lower bound',
            'phase_adapter_polar_rank_histogram':{str(rank): count for rank, count in sorted(histogram.items())},
            'first_literal_gate':first, 'first_rank_at_least_16_future_route':stage_two,
            'all_named_routes_source_derived':True,
            'physical_route_translation_and_native_compiler':'not emitted'}


def compute():
    packet = json.loads(gzip.decompress(
        (ROOT / 'research/joint-query/certificate.json.gz').read_bytes()))
    with tarfile.open(ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz') as archive:
        member = archive.extractfile(PHASE_MEMBER).read()
    phases = json.loads(member)
    records = phases['recipes']
    need(phases['m'] == 73 and len(records) == 112, 'source phase dimension')
    labels = [record['q'] for record in records]
    need(all(record['port'] == p for p, record in enumerate(records)), 'literal port order')
    need(all(0 < q < 512 and parity(q) == 1 for q in labels), '112 nonzero odd source lines')
    full = [[1 << i, 1] for i in range(17)]
    frame_ids = [name for name, item in packet['native_frame_registry'].items()
                 if item['line_terms_Z4'] == full]
    need(len(frame_ids) == 1, 'source registered F17 phase')
    positive, negative = set(), set()
    columns = 0
    for key, item in packet['native_line_recipes'].items():
        p, sign = item['port'], item['sign']
        need(item['rank'] == item['recipe']['rank'] == 1, 'signed line child rank')
        need(item['label'] == labels[p] and sign in (-1, 1), 'source line label and sign')
        (positive if sign == 1 else negative).add(p)
        for address in range(512):
            want = {address: (1, sign), address ^ labels[p]: (1, -sign)}
            need(kernel(item['recipe'], address) == want, 'literal signed line kernel column')
            columns += 1
    selected = set(packet['A_ports'] + packet['T_ports'])
    need(positive == negative == selected and len(selected) == 16,
         'packet recipes cover exactly sixteen selected ports')

    # This witness rejects the proposed raw scalar gate between different
    # native gauges. It does not assert that a larger compensated word fails.
    port, character = 0, 1
    q = labels[port]
    x_terms = full
    y_terms = full + [[q, -1]]
    x_phase = phase(x_terms, character)
    y_phase = phase(y_terms, character)
    need(q == 11 and x_phase == 1 and y_phase == 0,
         'actual q11/e0 native frame witness')
    corrected_phase = (x_phase - parity(q & character)) % 4
    wrong_sign_phase = (x_phase + parity(q & character)) % 4
    need(corrected_phase == y_phase and wrong_sign_phase != y_phase,
         'signed compensation and opposite-sign rejection')
    need(phase(x_terms, 0) == phase(y_terms, 0) == 0,
         'constant payload cannot detect this gate defect')

    # Count an explicitly specified route, not a lower bound on every repair.
    entry = [('line', 'Y' + str(p), p, 1) for p in range(len(labels))]
    exit_word = [('line', 'Y' + str(p), p, -1) for p in range(len(labels))]
    normalization_word = entry + exit_word
    need(len(normalization_word) == 224 and
         all(entry[p][2] == exit_word[p][2] and entry[p][3] == -exit_word[p][3]
             for p in range(112)), 'full entry/exit route restores all Y gauges')
    # Under C_r = c*(r*lambda)^(1-a), 0<=a<=1 and c,lambda>0,
    # C8/C1 = 8^(1-a)<=8. Grant every other new cost zero.
    removed_h8, added_h1 = 16, 32
    optimistic_removed_h1_units = removed_h8 * 8
    optimistic_new_h1_units = added_h1 + len(normalization_word)
    need(optimistic_new_h1_units > optimistic_removed_h1_units,
         'strict separately-normalized route rejection')
    return {
        'schema': 'qq16-native-adapter-screen-v1',
        'status': 'phase-obstruction-and-conditional-route-rejection',
        'candidate_phase_obligations': candidate_phase_audit(records, full),
        'phase_member': PHASE_MEMBER,
        'phase_member_sha256': hashlib.sha256(member).hexdigest(),
        'registered_common_frame': frame_ids[0],
        'literal_signed_recipe_columns_checked': columns,
        'literal_signed_recipe_ports': sorted(selected),
        'ordinary_ports_without_signed_recipe_in_this_packet': sorted(set(range(112)) - selected),
        'raw_scalar_gate_witness': {
            'gate': 'Y0 += X0', 'owner': 'identity', 'payload_character': 'e0',
            'source_q': q, 'logical_X0': 1, 'logical_Y0': 0,
            'actual_unlifted_added_phase_mod4': x_phase,
            'required_Y_added_phase_mod4': y_phase,
            'inverse_Cq_corrected_phase_mod4': corrected_phase,
            'wrong_positive_Cq_phase_mod4': wrong_sign_phase,
            'constant_payload_control_agrees': True,
            'scope': 'gatewise native lifting; compensating multi-gate words remain open',
        },
        'normalized_route_screen': {
            'route': 'normalize every current Y to F17; execute logical repair; restore every Y gauge',
            'entry_H1': len(entry), 'exit_H1': len(exit_word),
            'normalization_H1_total': len(normalization_word),
            'two_wrappers_per_line_total': 2 * len(normalization_word),
            'recipe_availability': '32 selected-port signed recipes checked; 192 ordinary-port signed recipes not emitted',
            'tariff_assumption': 'C_r=c*(r*lambda)^(1-a), c>0, lambda>0, 0<=a<=1; comparable child interfaces',
            'applicability_to_actual_supplier': 'not established',
            'optimistic_old_H1_units_upper_bound': optimistic_removed_h1_units,
            'optimistic_new_H1_units_lower_bound': optimistic_new_h1_units,
            'optimistic_saving_H1_units_upper_bound': optimistic_removed_h1_units - optimistic_new_h1_units,
            'granted_zero_only_for_rejection': ['query work', '28,616 scalar increase',
                'wrappers', 'owner-frame transport', 'allocation', 'restoration beyond gauges',
                'movement', 'precision', 'control'],
            'conclusion': 'stated separately-normalized route cannot save under stated tariff; no general repair lower bound',
        },
        'unproved': ['a native lift of the query-specific correction',
            'physical adapter and head movement bill', 'exclusive query stock and native scratch lease',
            'finite precision certificate', 'actual recursive incidence and supplier tariff'],
    }
