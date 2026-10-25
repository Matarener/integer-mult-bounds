#!/usr/bin/env python3
"""Rebuild and strictly audit five cross-call whole-role cycles on the selected T16 map."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = 'research/complex-t16-evacuation-increment/data'
SEARCH = ROOT / 'research/complex-t16-two-stage-cycles/search'
EXPECTED_KAPPA = Q('0.001673623729715781')
PR3338_KAPPA = Q('0.001673619538656538')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_gzip_json(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def clean_env():
    env = {key: os.environ[key] for key in
           ('PATH', 'SYSTEMROOT', 'WINDIR', 'TMPDIR', 'TEMP', 'TMP') if key in os.environ}
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    return env


def verify_input_pins():
    sources = read_json(P / 'SOURCES.json')
    assert sources['base_commit'] == '6f100d4bb5083f8c35d96fd95a539811c62f245c'
    for row in sources['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            assert path.is_file(), row['path']
            assert digest(path) == row['sha256'], 'source pin mismatch: ' + row['path']
    baseline_sources = read_json(ROOT / 'research/complex-t16-evacuation-increment/SOURCES.json')
    for row in baseline_sources['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            assert path.is_file() and digest(path) == row['sha256'], \
                'predecessor source pin mismatch: ' + row['path']
    return sources


def group(row):
    return int(row['owner_replica']), int(row['child']), int(row['port'])


def validate_and_apply_cycles(lib, rows, plan, cycles):
    progression = []
    previous_kappa = Q('0.001673618490895016')
    for cycle in cycles:
        assert cycle['old_slacks'] == [2, 1, 3]
        assert cycle['widths'] == [5, 4, 4]
        assert cycle['new_slacks'] == [3, 0, 3]
        moves = cycle['moves']
        assert len(moves) == 3
        source_groups = [tuple(move['source_group']) for move in moves]
        target_groups = [tuple(move['destination_group']) for move in moves]
        times = [int(move['time']) for move in moves]
        assert len(set(source_groups)) == len(set(target_groups)) == 3
        assert len(set(times)) == 3, 'cross-call cycles require three distinct calls'
        assert target_groups == source_groups[1:] + source_groups[:1]

        model = lib.Model(rows)
        occupied_groups = {(model.bin(i), int(row['time']))
                           for i, row in enumerate(model.roles)}
        indices = []
        widths = []
        old_slacks = []
        for move, source, target, t in zip(moves, source_groups, target_groups, times):
            matches = [i for i, row in enumerate(rows)
                       if int(row['time']) == t and int(row['helper']) == int(move['helper'])
                       and group(row) == source]
            assert len(matches) == 1, ('cycle role is not unique', cycle['number'], move)
            index = matches[0]
            role = rows[index]
            width = int(role['width'])
            assert width == int(move['width'])
            assert source in model.cap and target in model.cap
            assert t in model.allowed[target], ('target outside exact source window', move)
            assert (target, t) not in occupied_groups, ('target group occupied at call', move)
            source_family = model.fam[source]
            target_family = model.fam[target]
            assert target_family not in model.occ[t] or target_family == source_family, \
                ('target physical family is not freed by this cycle', move)
            old_slack = model.free(source)
            indices.append(index)
            widths.append(width)
            old_slacks.append(old_slack)
        assert old_slacks == cycle['old_slacks'], (cycle['number'], old_slacks)
        assert widths == cycle['widths'], (cycle['number'], widths)

        predicted = [old_slacks[0] + widths[0] - widths[2],
                     old_slacks[1] + widths[1] - widths[0],
                     old_slacks[2] + widths[2] - widths[1]]
        assert predicted == cycle['new_slacks'], (cycle['number'], predicted)
        assert min(predicted) >= 0

        for index, target in zip(indices, target_groups):
            rows[index] = lib.relocate(rows[index], *target)
        rows = lib.compact(rows)
        audit = lib.audit(rows, plan, controls=True)
        assert audit['controls'] == 11
        price = lib.price(audit['profile'])
        kappa = Q(price['kappa'])
        assert price['kappa_decimal'] == cycle['kappa_after']
        assert kappa > previous_kappa, (cycle['number'], previous_kappa, kappa)
        progression.append({'cycle': cycle['number'], 'kappa': price['kappa'],
                            'kappa_decimal': price['kappa_decimal'],
                            'idle': {str(k): v for k, v in sorted(audit['idle'].items())}})
        previous_kappa = kappa
    assert previous_kappa == EXPECTED_KAPPA
    return rows, progression


def compare_built_candidate(rows, work):
    packed_rows = load_gzip_json(P / 'data/OWNERS.json.gz')
    assert rows == packed_rows, 'five cycles do not reconstruct packaged owner map'
    owner_path = work / 'OWNERS.json.gz'
    owner_path.write_bytes(gzip.compress(json.dumps(rows).encode('utf-8'), mtime=0))
    rebuilt = work / 'rebuilt'
    subprocess.run([sys.executable, '-B', str(SEARCH / 'buildcand.py'),
                    str(SEARCH), str(owner_path), str(rebuilt), '10008'],
                   cwd=ROOT, env=clean_env(), check=True)
    rebuilt_rows = load_gzip_json(rebuilt / 'OWNERS.json.gz')
    assert rebuilt_rows == rows
    return rebuilt

def strict_replay(data_dir, work):
    source = work / 'source'
    source.mkdir()
    archive = ROOT / 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            assert member.isfile() and (source / member.name).resolve().is_relative_to(source.resolve())
        tar.extractall(source, filter='data')
    manifest = read_json(source / 'MANIFEST.json')
    actual = {f.relative_to(source).as_posix(): digest(f) for f in source.rglob('*')
              if f.is_file() and f != source / 'MANIFEST.json'}
    assert actual == manifest, 'frozen PR1087 source manifest mismatch'
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
        shutil.copyfile(data_dir / name, source / 'data' / name)

    local = work / 'local'
    local.mkdir()
    pins = read_json(ROOT / 'research/complex-t16-two-stage-cycles/LOCAL-PINS.json')
    provider_archive = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    prefix = 'candidate/strict/global/base/providers/gauge44/'
    with tarfile.open(provider_archive) as tar:
        for name, expected in pins.items():
            member = tar.getmember(prefix + name)
            assert member.isfile()
            content = tar.extractfile(member).read()
            assert hashlib.sha256(content).hexdigest() == expected, 'provider pin mismatch: ' + name
            (local / name).write_bytes(content)

    replay_dir = work / 'strict'
    subprocess.run([sys.executable, '-E', '-S', '-B', str(source / 'verify_t16.py'),
                    '--main', str(ROOT), '--local', str(local), '--work', str(replay_dir)],
                   env=clean_env(), check=True)
    receipt = read_json(replay_dir / 'REPLAY.json')
    expected = read_json(data_dir / 'SPEC.json')['expected']
    assert receipt['status'] == 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
    assert receipt['kappa'] == expected['kappa']
    assert receipt['kappa_decimal'] == expected['kappa_decimal']
    assert receipt['conservative_kappa_decimal'] == expected['conservative_kappa_decimal']
    assert receipt['complex_profile'] == expected['global_profile']
    assert receipt['actual_73_axis_charts'] == expected['actual_73column_sigmas'] == 10008
    assert receipt['controls'] == {'admission': 69, 'bit_supplier': 12,
                                   'independent_t16': 6, 'controller_mutations': 15}
    pinned = read_json(P / 'evidence/REPLAY.json')
    for key in ('status', 'kappa', 'kappa_decimal', 'conservative_kappa_decimal',
                'actual_73_axis_charts', 'controls'):
        assert receipt[key] == pinned[key], 'strict replay differs from packaged evidence: ' + key
    return replay_dir, receipt


def verify_word_cap(kappa):
    result = read_json(ROOT / 'research/complex-local-word-ceiling/RESULT.json')
    alpha = Q(result['ceiling']['a_ceiling'])
    cap = alpha / (1 + alpha)
    selected = Q(read_json(ROOT / 'certificates/selected-result.json')['kappa'])
    assert cap == Q(1690054109089, 1001690054109089)
    fraction = kappa / cap
    gap_fraction = (kappa - selected) / (cap - selected)
    expected = read_json(P / 'RESULT.json')['word_packing_ceiling']
    assert expected['kappa_ceiling'] == str(cap)
    assert Q(expected['fraction_of_word_kappa_ceiling']) == fraction
    assert Q(expected['fraction_of_selected_to_ceiling_gap']) == gap_fraction
    return cap, fraction, gap_fraction


def run():
    verify_input_pins()
    lib = load_module('t16_cross_call_owner_lib', SEARCH / 'lib.py')
    base_rows = load_gzip_json(ROOT / (BASE + '/OWNERS.json.gz'))
    base_plan = read_json(ROOT / (BASE + '/PLAN.json'))
    base_audit = lib.audit(base_rows, base_plan, controls=True)
    assert lib.price(base_audit['profile'])['kappa_decimal'] == '0.001673618490895016'
    cycles = read_json(P / 'CYCLES.json')['cycles']
    rows, progression = validate_and_apply_cycles(lib, base_rows, base_plan, cycles)
    with tempfile.TemporaryDirectory(prefix='t16-cross-call-strict-') as tmp:
        work = Path(tmp)
        rebuilt = compare_built_candidate(rows, work)
        candidate_package = work / 'candidate-package'
        data_dir = candidate_package / 'data'
        data_dir.mkdir(parents=True)
        for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
            shutil.copyfile(rebuilt / name, data_dir / name)
        replay_dir, receipt = strict_replay(data_dir, work)
        checker = load_module('t16_cross_call_independent_check',
                              ROOT / 'research/complex-t16-two-stage-cycles/check.py')
        checker.P = candidate_package
        check_path = work / 'CHECK.json'
        checker.run(ROOT, replay_dir, check_path)
        check = read_json(check_path)
        assert check == read_json(P / 'evidence/CHECK.json'), \
            'independent check differs from pinned receipt'

    kappa = Q(receipt['kappa'])
    assert kappa == EXPECTED_KAPPA
    assert kappa > PR3338_KAPPA
    assert check['sweep']['binding'] == 'complex'
    assert check['majorization']['candidate_majorizes_selected'] is True
    cap, fraction, gap_fraction = verify_word_cap(kappa)
    assert fraction < 1 and Q('0.01') > cap
    print('PASS_T16_FIVE_CROSS_CALL_THREE_ROLE_CYCLES', receipt['kappa_decimal'])
    print('strict replay', receipt['status'], 'charts', receipt['actual_73_axis_charts'],
          'controls', receipt['controls'])
    print('independent owner/pricing audit', check['candidate']['controls'],
          'binding', check['sweep']['binding'], 'conservative κ',
          check['price_new_conservative']['kappa_decimal'])
    print('gain over open PR3338', str(kappa - PR3338_KAPPA),
          'fixed-word cap', str(cap), 'fraction realized', float(fraction),
          'selected-to-cap gap realized', float(gap_fraction))
    print('cycle progression', json.dumps(progression, sort_keys=True))


if __name__ == '__main__':
    run()
