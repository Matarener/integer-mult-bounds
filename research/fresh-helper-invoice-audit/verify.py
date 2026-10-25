#!/usr/bin/env python3
"""Source-bound finite invoice audit; no source-verifier imports.

Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor construction and attribution are recorded in README.md.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path

from audit import Frames, controller_invoice, local_invoice, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-rebuild/complex/full-identity-certificates/'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate_bytes(raw, row):
    require(sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
    blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == row['git_blob'], 'source Git blob mismatch')


def authenticate():
    live = [row for row in read(HERE / 'SOURCES.json')['files'] if row['usage'] == 'input']
    require({row['path'] for row in live} == {
        SOURCE + 'THREE-base-FULL-IDENTITY-CANONICAL.json.gz',
        SOURCE + 'THREE-base-FULL-IDENTITY-NATIVE.json.gz'}, 'exact live input inventory')
    for row in live:
        path = ROOT
        for part in Path(row['path']).parts:
            path = path / part
            require(not path.is_symlink(), 'source symlink')
        authenticate_bytes(path.read_bytes(), row)
    snapshot = read(HERE / 'snapshot/MANIFEST.json')
    require({row['file'] for row in snapshot} == {
        'changes.json', 'native-receipt.json.gz', 'controller.json',
        'combined-receipt.json', 'source-README.md'}, 'snapshot input inventory')
    require(len(snapshot) == 5, 'duplicate snapshot row')
    for row in snapshot:
        require(row['commit'] == '5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39',
                'snapshot source head')
        path = HERE / 'snapshot' / row['file']
        require(not path.is_symlink(), 'snapshot symlink')
        authenticate_bytes(path.read_bytes(), row)
    return live, snapshot


def histogram(value):
    return Counter({int(rank): count for rank, count in value.items()})


def compare_local(result, expected):
    require(result['helpers'] == histogram(expected['helpers']), 'helper invoice differs from source receipt')
    require(result['paid'] == histogram(expected['paid']), 'paid invoice differs from source receipt')


def compare_controller(result, expected):
    for key in ('targets', 'paid'):
        require(result[key] == histogram(expected[key]), 'complete invoice differs: ' + key)


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def signed_delta(new, old):
    return {rank: new[rank] - old[rank] for rank in sorted(new.keys() | old.keys())
            if new[rank] != old[rank]}


def rejected(name, function):
    try:
        function()
    except ValueError as exc:
        return {'control': name, 'rejected_by': str(exc)}
    raise ValueError('negative control accepted: ' + name)


def run():
    live, snapshots = authenticate()
    canonical = read(ROOT / (SOURCE + 'THREE-base-FULL-IDENTITY-CANONICAL.json.gz'))
    native = read(ROOT / (SOURCE + 'THREE-base-FULL-IDENTITY-NATIVE.json.gz'))
    changes = read(HERE / 'snapshot/changes.json')
    controller = read(HERE / 'snapshot/controller.json')
    expected_local = read(HERE / 'snapshot/native-receipt.json.gz')
    expected_combined = read(HERE / 'snapshot/combined-receipt.json')
    require(canonical['v'] == 112 and canonical['h'] == 9 and
            len(canonical['ports']) == len(set(canonical['ports'])) == 112 and
            len(canonical['centers']) == 8, 'source port/axis/center contract')

    # Without a patch, recover the explicit source climbs and eight unsplit centers.
    empty = {key: [] for key in ('entrances', 'exits', 'gates')}
    old, _ = local_invoice(canonical, native, empty)
    require(old['paid'] == old['original_paid'], 'unpatched reconstruction differs from explicit source climbs')
    baseline = controller_invoice(controller, old['helpers'], old['paid'])
    compare_controller(baseline, controller['invoice'])

    unit, both = local_invoice(canonical, native, changes)
    compare_local(unit, expected_local)
    combined = controller_invoice(controller, unit['helpers'], unit['paid'])
    compare_controller(combined, expected_combined)
    require(combined['event_counts'] == {'LOCAL': 19, 'QUERY_SHEAR': 16,
            'IDLE': 16, 'ADD': 96, 'SIGNED_SWAP': 17}, 'complete event census')
    require(sum(combined['targets'].values()) == 11560 and sum(combined['paid'].values()) == 69273,
            'combined field/call totals')
    require(mass(combined['targets']) == 260798 and mass(combined['paid']) == 259998,
            'combined rank masses')
    require(mass(unit['helpers']) - mass(old['helpers']) ==
            mass(unit['paid']) - mass(old['paid']) == 133, 'local conserved mass increment')

    # Fixed warp jumps and main endpoints cancel in old-versus-new subtraction.
    # Only helper boundary widths change the telescoped persistent rank mass.
    require(mass(combined['targets']) - mass(combined['paid']) ==
            mass(baseline['targets']) - mass(baseline['paid']) == 800,
            'rank surplus conservation')
    require(sum(baseline['paid'].values()) - sum(combined['paid'].values()) ==
            19 * (sum(old['paid'].values()) - sum(unit['paid'].values())) == 3629,
            'complete call savings')

    controls = []
    bad = deepcopy(changes)
    bad['entrances'].append(bad['entrances'][0])
    controls.append(rejected('duplicate-helper-boundary', lambda: local_invoice(canonical, native, bad)))
    bad = deepcopy(changes)
    bad['gates'][0][2] = -1
    controls.append(rejected('wrong-old-scalar-frame', lambda: local_invoice(canonical, native, bad)))
    bad = deepcopy(changes)
    bad['gates'].pop(0)
    controls.append(rejected('missing-scalar-retiming', lambda: compare_local(
        local_invoice(canonical, native, bad)[0], expected_local)))
    bad = deepcopy(changes)
    bad['exits'].pop(0)
    controls.append(rejected('missing-helper-exit', lambda: compare_local(
        local_invoice(canonical, native, bad)[0], expected_local)))
    bad = deepcopy(changes)
    bad['gates'][0][3] = next(i for i, frame in enumerate(canonical['frames']) if len(frame) == 1)
    controls.append(rejected('incompatible-contact-frame', lambda: local_invoice(canonical, native, bad)))
    controls.append(rejected('equal-dimension-distinct-spaces', lambda: Frames([[1], [2]]).width(0, 1)))
    controls.append(rejected('dependent-frame-basis', lambda: Frames([[1, 2, 3]])))

    for kind in ('QUERY_SHEAR', 'IDLE'):
        bad_word = deepcopy(controller)
        index = next(i for i, event in enumerate(bad_word['physical_events']) if event[0] == kind)
        bad_word['physical_events'].pop(index)
        controls.append(rejected('omitted-' + kind.lower(), lambda: controller_invoice(
            bad_word, unit['helpers'], unit['paid'])))
    bad_word = deepcopy(controller)
    index = next(i for i, event in enumerate(bad_word['physical_events']) if event[0] == 'SIGNED_SWAP')
    bad_word['physical_events'][index][0] = 'SWAP'
    controls.append(rejected('unsigned-controller-swap', lambda: controller_invoice(
        bad_word, unit['helpers'], unit['paid'])))
    bad_word = deepcopy(controller)
    gate = next(g for g in bad_word['boundaries']['left_program'] if g[0] == 'ADD')
    gate[-1] = str(-Fraction(gate[-1]))
    controls.append(rejected('changed-boundary-coefficient', lambda: controller_invoice(
        bad_word, unit['helpers'], unit['paid'])))
    bad_word = deepcopy(controller)
    bad_word['diagonal'][0][1] ^= 1
    controls.append(rejected('unearned-productive-stage', lambda: controller_invoice(
        bad_word, unit['helpers'], unit['paid'])))
    raw = (HERE / 'snapshot/changes.json').read_bytes()
    row = next(row for row in snapshots if row['file'] == 'changes.json')
    controls.append(rejected('changed-source-bytes', lambda: authenticate_bytes(raw + b'\n', row)))

    report = {
        'status': 'PASS_INDEPENDENT_FRESH_HELPER_INVOICE',
        'source_head': '5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39',
        'source_files_authenticated': len(live) + len(snapshots),
        'native_orientations': sorted(both),
        'persistent_roles_per_orientation': 632,
        'changed_role_bills': sum(a != b for a, b in zip(old['role_paid'], unit['role_paid'])),
        'scalar_frame_patches': len(changes['gates']),
        'helper_entrance_patches': len(changes['entrances']),
        'helper_exit_patches': len(changes['exits']),
        'persistent_scalar_contacts': len(unit['contacts']),
        'local_helpers': unit['helpers'], 'local_paid': unit['paid'],
        'local_paid_delta': signed_delta(unit['paid'], old['paid']),
        'local_helper_delta': signed_delta(unit['helpers'], old['helpers']),
        'local_paid_calls_saved': sum(old['paid'].values()) - sum(unit['paid'].values()),
        'local_target_and_paid_mass_increment': 133,
        'controller_events': combined['event_counts'],
        'main_targets': combined['main'], 'whole_idle_paid': combined['whole_idle'],
        'targets': combined['targets'], 'paid': combined['paid'],
        'productive_fields': sum(combined['targets'].values()),
        'paid_calls': sum(combined['paid'].values()),
        'paid_calls_saved': 3629,
        'target_rank_mass': mass(combined['targets']),
        'paid_rank_mass': mass(combined['paid']),
        'rank_surplus': 800,
        'rejection_controls': controls,
        'scope': 'Finite contact-path and full symbolic controller invoice only; no new kappa or supplier admission.',
    }
    return json.loads(json.dumps(report))


if __name__ == '__main__':
    report = run()
    require(report == read(HERE / 'RESULT.json'), 'audit receipt differs')
    print(json.dumps({'status': report['status'], 'paid_calls': report['paid_calls'],
                      'calls_saved': report['paid_calls_saved'], 'surplus': report['rank_surplus'],
                      'controls_rejected': len(report['rejection_controls'])}, sort_keys=True))
