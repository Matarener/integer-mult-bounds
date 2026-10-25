#!/usr/bin/env python3
"""Check the exact two-band census and its uniform width-policy consequence."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE_PATH = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
FRAME_CHECK_PATH = 'research/two-full-border-paid-precision/independent-review/invariance/check_invariance.py'
PAYLOAD_SHA = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
SPLIT = {1: (1,), 2: (2,), 3: (3,), 4: (3, 1), 5: (3, 2), 8: (3, 3, 2)}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # Convert histogram keys to JSON strings before their canonical sort.
    normalized = json.loads(json.dumps(value))
    return json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()


def load_source():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    pins = {row['path']: row for row in sources['files'] if row['usage'] == 'input'}
    for name in (SOURCE_PATH, FRAME_CHECK_PATH):
        need(sha256((ROOT / name).read_bytes()).hexdigest() == pins[name]['sha256'],
             'A pinned live source changed: ' + name)
    spec = importlib.util.spec_from_file_location('retained_frame_audit', ROOT / FRAME_CHECK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frame_result = module.run(ROOT / SOURCE_PATH)
    raw = gzip.decompress((ROOT / SOURCE_PATH).read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD_SHA, 'The native payload changed')
    return json.loads(raw), frame_result


def owner(ref):
    need(ref[0] in ('L', 'C'), 'Unknown source owner')
    if ref[0] == 'L':
        need(type(ref[1]) is int and 0 <= ref[1] < 632, 'Invalid persistent owner')
        return ref[1]
    need(ref[1] == 0, 'Only the retained center C0 is present')
    return 632


def valuation(value):
    value = F(value)
    need(value != 0, 'The valuation needs a nonzero number')
    a, b = abs(value.numerator), value.denominator
    return (a & -a).bit_length() - (b & -b).bit_length()


def loss(fine, coarse):
    return max(0, valuation(fine) - valuation(coarse))


def execute(program, direction, include_helpers=True):
    rows = [{} for _ in range(633)]
    for i in range(112):
        rows[i] = {i: F(1)}
        if direction == 'backward':
            rows[112 + i] = {i: F(1)}
    if include_helpers:
        for i in range(224, 632):
            rows[i] = {i: F(1)}
    profile, wide, split = Counter(), Counter(), Counter()
    sites = []
    for index, event in enumerate(program):
        if event[0] in ('climb', 'center'):
            r = event[2] if event[0] == 'climb' else 632
            rank = event[-1]
            need(type(rank) is int and rank in SPLIT, 'Invalid paid rank')
            profile[rank] += 1
            high = sorted((i, x) for i, x in rows[r].items() if i < 112)
            low = sorted((i, x) for i, x in rows[r].items() if i >= 224)
            if high and low:
                main, coarse = high[0]
                helper, fine = low[0]
                wide[rank] += 1
                split.update(SPLIT[rank])
                sites.append({'event': index, 'source_event': event, 'owner': r,
                              'rank': rank, 'main_input': main,
                              'main_coefficient': str(coarse), 'helper_input': helper,
                              'helper_coefficient': str(fine),
                              'entropy_constant_loss': loss(fine, coarse)})
        if event[0] != 'scalar':
            need(event[0] in ('climb', 'center', 'warp', 'phase', 'adapter'),
                 'An unhandled source event is present')
            continue
        gate = event[1]
        r = owner(gate[1])
        if gate[0] == 'clear':
            rows[r] = {}
        elif gate[0] == 'copy':
            rows[r] = dict(rows[owner(gate[2])])
        elif gate[0] == 'scale':
            rows[r] = {i: x * F(gate[2], gate[3]) for i, x in rows[r].items()}
        elif gate[0] == 'add':
            s = owner(gate[2])
            need(s != r, 'A scalar ADD has the same source and target')
            for i, x in rows[s].items():
                value = rows[r].get(i, F()) + x * F(gate[3], gate[4])
                if value:
                    rows[r][i] = value
                else:
                    rows[r].pop(i, None)
        else:
            raise ValueError('Unknown scalar operation')
    need(dict(profile) == PROFILE, 'The complete source profile differs')
    for i in range(112):
        need(rows[i] == ({i: F(1)} if direction == 'forward' else {}),
             'The restricted main X endpoint differs')
        need(rows[112 + i] == {i: F(1)}, 'The restricted main Y endpoint differs')
    for i in range(224, 632):
        need(rows[i] == ({i: F(1)} if include_helpers else {}),
             'An independent helper return differs')
    need(not rows[632], 'The owned center does not return to zero')
    return {'direction': direction, 'paid_sites': sum(profile.values()),
            'wide_profile': dict(sorted(wide.items())),
            'wide_split_profile': dict(sorted(split.items())), 'sites': sites}


def direct_cut(program, site, direction, a, b, k):
    values = [F() for _ in range(633)]
    main, helper = site['main_input'], site['helper_input']
    values[main] = F(b)
    if direction == 'backward':
        values[112 + main] = F(b)
    values[helper] = F(a, 1 << k)
    for index, event in enumerate(program):
        if index == site['event']:
            return values[event[2] if event[0] == 'climb' else 632]
        if event[0] != 'scalar':
            continue
        gate = event[1]
        r = owner(gate[1])
        if gate[0] == 'clear':
            values[r] = F()
        elif gate[0] == 'copy':
            values[r] = values[owner(gate[2])]
        elif gate[0] == 'scale':
            values[r] *= F(gate[2], gate[3])
        else:
            need(gate[0] == 'add', 'Unknown direct scalar operation')
            values[r] += values[owner(gate[2])] * F(gate[3], gate[4])
    raise ValueError('The requested paid cut is absent')


def finite_injectivity(fine, coarse, k, constant):
    need(k > constant >= 0, 'Invalid finite band sizes')
    low_count = 1 << (k - constant)
    values = {fine * F(a, 1 << k) + coarse * b
              for a in range(low_count) for b in range(1 << k)}
    need(len(values) == low_count * (1 << k), 'The declared two-band map is not injective')
    return len(values)


def rejected(name, operation):
    try:
        operation()
    except ValueError as error:
        return {'name': name, 'result': 'REJECT', 'reason': str(error)}
    raise ValueError('A negative control passed: ' + name)


def same_receipt(actual, retained):
    need(canonical(actual) == canonical(retained), 'The retained exact receipt differs')


def run():
    word, frames = load_source()
    calls, direct_checks = [], []
    no_helpers = []
    for direction in ('forward', 'backward'):
        program = word['programs'][direction]
        call = execute(program, direction)
        empty = execute(program, direction, include_helpers=False)
        need(not empty['sites'], 'A two-band witness survived removal of all helper inputs')
        no_helpers.append({'direction': direction, 'wide_sites': 0})
        for site in [call['sites'][0], call['sites'][len(call['sites']) // 2], call['sites'][-1]]:
            fine, coarse = F(site['helper_coefficient']), F(site['main_coefficient'])
            k = 5
            for a, b in ((0, 1), (1, 0), (3, 5), (7, 31)):
                need(direct_cut(program, site, direction, a, b, k)
                     == fine * F(a, 1 << k) + coarse * b,
                     'The separate scalar cut evaluation differs')
            direct_checks.append({'direction': direction, 'event': site['event'], 'samples': 4})
        calls.append(call)
    pairs = sorted({(s['helper_coefficient'], s['main_coefficient']) for c in calls for s in c['sites']})
    finite = []
    for fine_text, coarse_text in pairs:
        fine, coarse = F(fine_text), F(coarse_text)
        c = loss(fine, coarse)
        need(all(x.denominator & (x.denominator - 1) == 0 for x in (fine, coarse)),
             'A band coefficient is not dyadic')
        numerator_bits = {}
        for k in (32, 64):
            a, b = valuation(fine), valuation(coarse)
            u, v = fine / (F(2) ** a), coarse / (F(2) ** b)
            shift = 2 * k - 1 + b - a
            need(u.denominator == v.denominator == 1 and shift >= 1 and k > a,
                 'The canonical numerator fixture is outside its stated range')
            value = fine / (1 << k) + coarse * (1 << (k - 1))
            numerator = int(u) + int(v) * (1 << shift)
            need(value.numerator == numerator and numerator & 1,
                 'The exact reduced numerator identity differs')
            numerator_bits[str(k)] = abs(numerator).bit_length()
        finite.append({'fine': fine_text, 'coarse': coarse_text, 'constant_loss': c,
                       'k': 5, 'distinct_values': finite_injectivity(fine, coarse, 5, c),
                       'reduced_numerator_bits': numerator_bits})
    original, split, baseline, targets = Counter(), Counter(), Counter(), Counter()
    for call in calls:
        original.update(call['wide_profile'])
        split.update(call['wide_split_profile'])
    for rank, count in PROFILE.items():
        for child in SPLIT[rank]:
            baseline[child] += 2 * count
    c = word['canonical']
    for i in range(224, 632):
        rank = len(c['frames'][c['final'][i]]) - len(c['frames'][c['start'][i]])
        targets[rank] += 2
    targets[17] += 224
    need(dict(baseline) == {1: 4656, 2: 920, 3: 1386}, 'The baseline split invoice differs')
    need(dict(targets) == {4: 56, 7: 14, 8: 94, 9: 652, 17: 224}, 'The complete target invoice differs')
    need(dict(original) == {1: 3163, 2: 406, 3: 742, 4: 165, 5: 40, 8: 8}, 'The wide-cut census differs')
    charged = baseline.copy()
    charged[1] += original[1]
    mass = lambda profile: sum(r * n for r, n in profile.items())
    need(mass(targets) == 10750 and mass(baseline) == 10654 and mass(charged) == 13817,
         'The rank masses differ')
    need(max(charged) == 3 and min(targets) == 4, 'The rank-separation proof does not apply')
    need(mass(targets) < mass(charged), 'The uniform linear-width tariff is not rejected')
    damaged = deepcopy(word['programs']['forward'])
    last_clear = max(i for i, e in enumerate(damaged) if e[0] == 'scalar' and e[1][0] == 'clear')
    damaged.pop(last_clear)
    controls = [
        rejected('understated_valuation_loss', lambda: finite_injectivity(F(4), F(1), 5, 0)),
        rejected('zero_band_coefficient', lambda: loss(F(0), F(1))),
        rejected('removed_final_owned_clear', lambda: execute(damaged, 'forward')),
        rejected('integer_to_float_receipt', lambda: same_receipt({'wide_H1': 3163}, {'wide_H1': 3163.0})),
    ]
    witnesses = {'schema': 'two-full-exact-width-witnesses/v1', 'calls': calls}
    result = {
        'schema': 'two-full-exact-width-gate/v1',
        'status': 'PASS_TWO_FULL_EXACT_WIDTH_GATE', 'new_kappa': False,
        'source_payload_sha256': PAYLOAD_SHA,
        'witness_payload_sha256': sha256(canonical(witnesses)).hexdigest(),
        'frame_audit': {'status': frames['status'], 'events': sum(x['events'] for x in frames['orientations'].values()),
                        'warp_matrices': len(frames['warp_checks']),
                        'all_contacts_and_transports_checked': True},
        'restricted_independent_columns_per_call': 520,
        'original_paid_sites': 6596, 'wide_sites': sum(original.values()),
        'original_wide_profile': dict(sorted(original.items())),
        'split_wide_profile_information_only': dict(sorted(split.items())),
        'entropy_constant_max': max(x['constant_loss'] for x in finite),
        'complete_targets': dict(sorted(targets.items())),
        'baseline_paid': dict(sorted(baseline.items())), 'charged_paid': dict(sorted(charged.items())),
        'rank_masses': {'target': mass(targets), 'baseline': mass(baseline), 'charged': mass(charged)},
        'all_power_moments_ratio_upper': str(F(mass(targets), mass(charged))),
        'policy': {'site_width': 'Uniform over all permitted inputs at each paid occurrence',
                   'representation': 'Literal exact per-register numerator; one shared exponent is allowed',
                   'baseline_width': 'k+o(k)', 'width_tariff': 'Linear in the leading width',
                   'limit': 'k tends to infinity at fixed native rank and fixed fiber/column multiplicity'},
        'finite_injectivity': finite, 'direct_cut_checks': direct_checks,
        'no_helper_controls': no_helpers, 'negative_controls': controls,
        'omitted': ['Adaptive-width sum bound', 'Joint symbolic-state lower bound',
                    'A limit with growing fiber/column multiplicity',
                    'Full physical Gaussian execution', 'Recursive child compatibility',
                    'Compiler and outer multiplication replay'],
    }
    return witnesses, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write the rebuilt package certificate and receipt')
    parser.add_argument('--output', type=Path, help='Write the checked exact receipt to this path')
    args = parser.parse_args()
    witnesses, result = run()
    certificate = PACKAGE / 'WITNESSES.json.gz'
    receipt = PACKAGE / 'RESULT.json'
    if args.write:
        certificate.write_bytes(gzip.compress(canonical(witnesses), mtime=0))
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        same_receipt(witnesses, json.loads(gzip.decompress(certificate.read_bytes())))
        same_receipt(result, json.loads(receipt.read_text()))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_TWO_FULL_EXACT_WIDTH_GATE wide_sites=4524 extra_H1=3163 ratio_upper=10750/13817 new_kappa=false')


if __name__ == '__main__':
    main()
