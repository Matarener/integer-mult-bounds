#!/usr/bin/env python3
"""Bind an all-fresh p3 native unit and its exact full idle operators.

Finite source, ownership, contraction and exact-moment checks. The written
all-column tensor construction and inherited transfer remain proof premises.
Apache-2.0; substantial OpenAI/Codex assistance.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.dont_write_bytecode = True
PINS = {
    'controller/P3-NATIVE-COVER.json.gz': 'facfc6d6ecde151afb7e6a167776f3fdaac1c816e785a21a39f7f0bfd9140f3f',
    'controller/p3_native_cover.py': 'fae71fcbbd20b9ee73b049cf6f43ea1d048217fb15feb6055a007e47da3363fe',
    'complex/full-identity-certificates/RESULT.json': '943d5fad2fc529f470df05a35446e07ecaef7344abfce450d2c2eb2c9b3798f6',
    'complex/full_identity_rebuild.py': '9af2ffbb0038c92e2a7d281081b0daaeadce75b11b566e5427845dc1af91e33d',
    'transfer-audit/p3_cover_audit.py': 'a0fe9a26f77556e83b31b0c91fea909d6f3d8209d0f9f7ad4e5bc1375d33615e',
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def counter(row):
    return Counter({int(k): int(v) for k, v in row.items()})


def paid_histogram(program):
    return Counter(event[-1] for event in program if event[0] in ('climb', 'center'))


def independent_axes(axes):
    basis = {}
    for axis in axes:
        value = axis
        while value:
            pivot = value.bit_length()-1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
        if not value:
            return False
    return True


def polynomial(terms, dimension):
    linear = [0]*dimension
    quadratic = [0]*dimension
    for axis, coefficient in terms:
        support = [i for i in range(dimension) if axis >> i & 1]
        for i in support:
            linear[i] = (linear[i]+coefficient) % 4
            if coefficient % 2:
                for j in support:
                    if j > i:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def fuse_centers(program):
    out, count, index = [], 0, 0
    while index < len(program):
        event = program[index]
        if event[0] != 'center':
            out.append(event)
            index += 1
            continue
        following = program[index+1]
        need(following[0] == 'center' and event[1] == following[1] == 0,
             'Both adjacent children use the same owned center')
        need(event[3] == following[2] and sorted((event[4], following[4])) == [3, 5],
             'The exact intermediate frame cancels in the 3+5 center path')
        out.append(['center', 0, event[2], following[3], 8])
        index += 2
        count += 1
    need(count == 8, 'Exactly eight center paths in each native invocation')
    return out


def run(root):
    base = root/'research/kappa-rebuild'
    sources = {}
    for name, wanted in PINS.items():
        path = base/name
        actual = sha256(path.read_bytes()).hexdigest()
        need(actual == wanted, 'Exact original source pin: '+name)
        sources[str(path.relative_to(root))] = actual
    receipt = read(base/'controller/P3-NATIVE-COVER.json.gz')
    cover = receipt['cover']
    native_base = base/'complex/full-identity-certificates'
    provider = read(native_base/'RESULT.json')['providers']['THREE-base']
    for name, wanted in provider['artifacts'].items():
        path = native_base/name
        need(sha256(path.read_bytes()).hexdigest() == wanted, 'Exact native artifact '+name)
        sources[str(path.relative_to(root))] = wanted
    native = read(native_base/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    collapsed = {}
    for direction, program in native.items():
        collapsed[direction] = fuse_centers(program)
        need(paid_histogram(collapsed[direction]) == counter(provider['unsplit_replays'][direction]['paid_profile']),
             'Restored program has the pinned unsplit native paid profile')
        need(all(row['product_exact_including_phase'] for row in provider['split_center_phase_recipes'][direction]),
             'The original split replay checked absolute phase of every center path')

    # Every helper now has its own independent physical input. The native
    # all-column autonomous contract supplies the same main operator.
    helper_path = root/provider['helper_boundary']['certificate']
    helper_hash = provider['helper_boundary']['certificate_sha256']
    need(sha256(helper_path.read_bytes()).hexdigest() == helper_hash, 'Actual complete helper boundaries')
    sources[str(helper_path.relative_to(root))] = helper_hash
    helper = read(helper_path)
    widths = {row['role']: row['width'] for row in helper['recipes']}
    need(set(widths) == set(range(224, 632)), 'All408 actual arbitrary-input helper roles')
    need(provider['all_408_helpers_autonomous'] and provider['all_632_persistent_inputs_arbitrary'],
         'Fresh helper inputs are independent arbitrary fields')
    targets = Counter(row['target_rank'] for row in receipt['main_endpoint_normalizers'])
    need(targets == Counter({25:448, 57:224}), 'Exact unchanged main endpoint census')
    by_stage = defaultdict(list)
    for row in cover['helper_bindings']:
        by_stage[row['stage']].append(row)
    for stage in range(7):
        need(len(by_stage[stage]) == 408 and {row['role'] for row in by_stage[stage]} == set(widths),
             'Every actual helper receives its own new productive owner')
        for row in by_stage[stage]:
            need(row['width'] == widths[row['role']], 'Native boundary backs the helper target width')
            targets[row['width']] += 1
    # Check the full idle operator, including its affine phase, directly.
    phase_path = root/'research/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    if not phase_path.exists():
        phase_path = root/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    phase_hash = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
    need(sha256(phase_path.read_bytes()).hexdigest() == phase_hash, 'Exact native port phase source')
    sources[str(phase_path.relative_to(root))] = phase_hash
    phases = read(phase_path)
    need(len(phases['recipes']) == 112, 'All actual port recipes')
    axes = [1 << i for i in range(57)]
    idle = Counter()
    missing_phase_rejected = 0
    window_keys = set()
    for window in cover['windows']:
        key = window['index'], window['owner']
        need(key not in window_keys, 'One whole idle job per actual window/owner')
        window_keys.add(key)
        q = phases['recipes'][window['port']]['q']
        desired = []
        for stage in window['stages']:
            desired += ([(a,1) for a in axes[:9]]+[(q,-1)] if stage == 0
                        else [(a,1) for a in axes[9+8*(stage-1):9+8*stage]])
        actual = [(a,1) for a in window['axes']]+[(window['translation_after'],2)]
        need(independent_axes(window['axes']), 'Whole idle axis list is independent')
        need(polynomial(actual,57) == polynomial(desired,57), 'Exact whole idle operator including translation')
        if window['translation_after']:
            need(polynomial([(a,1) for a in window['axes']],57) != polynomial(desired,57),
                 'Dropping the nonzero whole-idle phase correction fails')
            missing_phase_rejected += 1
        idle[len(window['axes'])] += 1
    need(idle == Counter({8:448,16:448}), 'Allfour retained windows paid on all224 owners')
    paid = idle.copy()
    for direction in ('forward', 'backward', 'forward', 'backward', 'forward', 'backward', 'forward'):
        paid.update(paid_histogram(collapsed[direction]))
    need(targets == Counter({5:196,6:126,7:392,8:651,9:1491,25:448,57:224}), 'All-fresh native target census')
    need(paid == Counter({1:17409,2:4991,3:1568,4:714,5:140,8:504,16:448}), 'Complete paid native and whole-idle tariff')
    need(sum(k*v for k,v in targets.items())-sum(k*v for k,v in paid.items()) == 224,
         'Rank surplus of the complete actual all-fresh word')
    bad = [list(row) for row in native['forward']]
    index = next(i for i, row in enumerate(bad) if row[0] == 'center')
    bad[index+1][2] = -1
    rejected = False
    try:
        fuse_centers(bad)
    except AssertionError:
        rejected = True
    need(rejected, 'Wrong intermediate center frame is rejected')
    return {
        'schema': 'native-all-fresh-full-idle-inventory/1',
        'source_head': 'da637c87c89482bc4c86be36bd0071b3d400dbed',
        'status': 'PASS_ACTUAL_ARBITRARY_HELPERS_AND_COMPLETE_PHASE_CORRECT_IDLE_JOBS',
        'source_sha256': sources,
        'targets': dict(sorted(targets.items())), 'paid': dict(sorted(paid.items())),
        'fresh_helper_fields': 2856, 'main_fields': 672,
        'restored_native_centers': 56, 'whole_idle_profile': dict(sorted(idle.items())),
        'ambient_rank': 57, 'productive_fields': 3528,
        'paid_calls': sum(paid.values()), 'rank_surplus': 224,
        'native_scalar_allowance': 1147304,
        'controls': {'wrong_intermediate_center_rejected': rejected,
                     'whole_idle_missing_phase_rejected_count': missing_phase_rejected,
                     'raw_rule_not_strictly_separated': max(paid) >= min(targets)},
        'scope': 'Exact finite all-fresh controller inventory. Native all-column closure is inherited; the raw rule requires the separate tensor strictification before the old strict compiler applies.',
    }



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'targets', 'paid', 'productive_fields', 'paid_calls')}))
