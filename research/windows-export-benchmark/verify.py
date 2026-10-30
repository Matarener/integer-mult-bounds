"""Check portable receipt controls and one retained native measurement.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Unit observations are synthetic; the separate native receipt is read-only.
This verifier never invokes a real timing subprocess or scientific replay.
"""
from contextlib import redirect_stdout
from copy import deepcopy
from hashlib import sha1, sha256
import io
import json
from pathlib import Path
import statistics
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

import benchmark

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEAD = '9889f94b6ed045c1069b2e6f7e4471d0322f2f16'
PREFIX = 'research/windows-export-benchmark/vendor/root/'
SOURCE = 'research/export-single-scan/benchmark.py'
ORACLE = 'research/export-single-scan/BENCHMARK-toolkit.json'
BASELINE = 'research/export-single-scan/baseline/export_research_package.py'
CANDIDATE = 'scripts/export_research_package.py'
PATHS = {SOURCE, ORACLE, BASELINE, CANDIDATE,
         'research/export-single-scan/baseline/research_package.py', 'scripts/research_package.py'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    rows = [r for r in json.loads((HERE / 'SOURCES.json').read_bytes())['files'] if 'retained_path' in r]
    need(len(rows) == 6 and {r['path'] for r in rows} == PATHS, 'six exact retained inputs')
    raw = {}
    for row in rows:
        need(row['retained_path'] == PREFIX + row['path'], 'retained path binding')
        need(row['pin'] == 'head:' + HEAD + ':' + row['path'], 'exact source head binding')
        content = (ROOT / row['retained_path']).read_bytes()
        need(sha256(content).hexdigest() == row['sha256'], 'retained source SHA256')
        need(sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == row['git_blob'],
             'retained source Git blob')
        raw[row['path']] = content
    return raw


def error_is(action, kind, message=None, attribute=None):
    try:
        action()
    except (ValueError, AttributeError, RuntimeError) as error:
        need(type(error) is kind, 'unexpected exception class: ' + repr(error))
        if message is not None:
            need(str(error) == message, 'unexpected exception reason: ' + repr(error))
        if attribute is not None:
            need(getattr(error, 'name', None) == attribute, 'unexpected missing attribute')
        return
    raise ValueError('expected exception was not raised')


def environment_controls():
    absent = SimpleNamespace(cpu_count=lambda: 3)
    row = benchmark.environment_info(absent)
    need(row['load'] is None and row['load_status'] == 'unavailable'
         and row['load_reason'] == 'api_absent' and row['logical_cpus'] == 3, 'absent API metadata')
    value = (0.25, 0.5, 0.75)
    available = benchmark.environment_info(SimpleNamespace(cpu_count=lambda: 7, getloadavg=lambda: value))
    need(available['load'] is value and available['load_status'] == 'available'
         and available['load_reason'] is None and available['logical_cpus'] == 7, 'available telemetry preserved')
    for kind in (NotImplementedError, OSError):
        def unsupported():
            raise kind('load telemetry unavailable')
        result = benchmark.environment_info(SimpleNamespace(cpu_count=lambda: None, getloadavg=unsupported))
        need(result['load'] is None and result['load_status'] == 'unavailable'
             and result['load_reason'] == kind.__name__, 'explicit unsupported API metadata')
    def broken():
        raise RuntimeError('unexpected telemetry bug')
    error_is(lambda: benchmark.environment_info(SimpleNamespace(cpu_count=lambda: 3, getloadavg=broken)),
             RuntimeError, 'unexpected telemetry bug')
    return ['api_absent', 'available_value', 'NotImplementedError', 'OSError', 'unexpected_RuntimeError']


def main_controls(frozen, original, directory):
    archive, old_output = directory / 'unit.tar', directory / 'lost.json'
    archive.write_bytes(b'synthetic unit archive; no timed subprocess')
    raw = deepcopy(original)
    raw.pop('environment')
    absent = SimpleNamespace(cpu_count=lambda: 3)
    args = ['--archive', str(archive), '--output', str(old_output)]
    old_measure = Mock(return_value=deepcopy(raw))
    with patch.object(frozen, 'benchmark', old_measure), patch.object(frozen, 'os', absent), \
            patch.object(sys, 'argv', [frozen.__file__, *args]), redirect_stdout(io.StringIO()):
        error_is(frozen.main, AttributeError, attribute='getloadavg')
    old_measure.assert_called_once_with(archive.resolve(), 9, 5, directory.resolve())
    need(not old_output.exists(), 'frozen failure precedes receipt creation')
    output = directory / 'preserved.json'
    portable_measure = Mock(return_value=deepcopy(raw))
    real_environment = benchmark.environment_info
    with patch.object(benchmark, 'load_source', return_value=frozen), \
            patch.object(frozen, 'benchmark', portable_measure), \
            patch.object(benchmark, 'environment_info', side_effect=lambda: real_environment(absent)), \
            redirect_stdout(io.StringIO()):
        benchmark.main(['--archive', str(archive), '--output', str(output)])
    portable_measure.assert_called_once_with(archive.resolve(), 9, 5, directory.resolve())
    saved = json.loads(output.read_bytes())
    need({k:v for k,v in saved.items() if k != 'environment'} == raw,
         'all completed synthetic measurement fields retained unchanged')
    need(saved['environment']['load'] is None and saved['environment']['load_reason'] == 'api_absent',
         'portable receipt states missing telemetry')
    before = output.read_bytes()
    with patch.object(benchmark, 'load_source') as forbidden:
        error_is(lambda: benchmark.main(['--archive', str(archive), '--output', str(output)]),
                 ValueError, 'output must be a new external file')
        forbidden.assert_not_called()
    need(output.read_bytes() == before, 'existing output bytes preserved')
    inside = HERE / ('never-created-' + directory.name + '.json')
    need(not inside.exists(), 'unused in-repository rejection fixture')
    with patch.object(benchmark, 'load_source') as forbidden:
        error_is(lambda: benchmark.main(['--archive', str(archive), '--output', str(inside)]),
                 ValueError, 'output must be a new external file')
        forbidden.assert_not_called()
    need(not inside.exists(), 'in-repository path rejected without publication')
    return ['frozen_completed_then_missing_API', 'portable_complete_receipt',
            'existing_output_preserved', 'repository_output_rejected_before_measurement']


def ordering_control(frozen, original, raw, directory):
    source_path = ROOT / PREFIX / SOURCE
    need(Path(frozen.__file__) == source_path and frozen.benchmark.__code__.co_filename == str(source_path),
         'benchmark function is compiled from the authenticated frozen source')
    archive = directory / 'order.tar'
    archive.write_bytes(b'synthetic ordering fixture')
    calls = []
    def fake_measure(script, supplied_archive, repetitions, cwd):
        calls.append((Path(script), supplied_archive, repetitions, cwd))
        return ([1000000 + 100 * len(calls) + j for j in range(repetitions)],
                [original['complete_stdout'].encode()] * repetitions)
    with patch.object(frozen, 'measure', side_effect=fake_measure):
        result = frozen.benchmark(archive, 9, 5, directory)
    scripts = [ROOT / PREFIX / BASELINE, ROOT / PREFIX / CANDIDATE]
    expected = [(scripts[side], archive, 5, directory)
                for pair in range(9) for side in (pair % 2, 1 - pair % 2)]
    need(calls == expected, 'all eighteen alternating batches retain frozen order')
    need(result['successful_commands'] == 90 and result['errors'] == 0
         and result['pairs'] == 9 and result['commands_per_side_per_pair'] == 5,
         'fixed ninety-command protocol')
    need(result['source_sha256'] == [sha256(raw[p]).hexdigest() for p in (BASELINE, CANDIDATE)],
         'frozen baseline and candidate bytes are actually selected')
    return 'frozen_nine_by_five_alternating_order'


def validate_receipt(value, original, raw):
    need(type(value) is dict and set(value) == set(original), 'complete receipt schema')
    need(value['pairs'] == 9 and type(value['pairs']) is int
         and value['commands_per_side_per_pair'] == 5 and type(value['commands_per_side_per_pair']) is int,
         'fixed nine by five measurement protocol')
    need(value['successful_commands'] == 90 and type(value['successful_commands']) is int
         and value['errors'] == 0 and type(value['errors']) is int, 'ninety successful complete commands')
    for key in ('archive_sha256', 'archive_bytes'):
        need(value[key] == original[key], 'official immutable fixture and complete output: ' + key)
    original_stdout = original['complete_stdout']
    need(original_stdout.endswith('\n') and original_stdout.count('\n') == 1 and '\r' not in original_stdout,
         'pinned complete output has one terminal LF')
    need(value['complete_stdout'] in (original_stdout, original_stdout[:-1] + '\r\n'),
         'official immutable fixture and complete output: complete_stdout')
    need(value['source_sha256'] == [sha256(raw[p]).hexdigest() for p in (BASELINE, CANDIDATE)],
         'exact measured script hashes')
    samples = value['elapsed_ns']
    need(type(samples) is list and len(samples) == 2
         and all(type(side) is list and len(side) == 9 for side in samples)
         and all(type(batch) is list and len(batch) == 5 for side in samples for batch in side),
         'two sides of nine five-sample batches')
    need(all(type(n) is int and n > 0 for side in samples for batch in side for n in batch),
         'positive integral nanosecond observations')
    medians = [statistics.median([n for batch in side for n in batch]) for side in samples]
    need(value['median_ns'] == medians, 'medians recomputed from all raw observations')
    need(value['wall_time_reduction'] == 1 - medians[1] / medians[0], 'reduction recomputed from medians')
    env = value['environment']
    need(type(env) is dict and set(env) == {'python', 'platform', 'logical_cpus', 'load', 'load_status', 'load_reason'},
         'portable environment schema')
    need(type(env['python']) is str and env['python'].startswith('3.12.')
         and type(env['platform']) is str and env['platform'].startswith('Windows'), 'native Windows Python3.12 record')
    need(type(env['logical_cpus']) is int and env['logical_cpus'] > 0, 'positive native CPU count')
    need(env['load'] is None and env['load_status'] == 'unavailable'
         and env['load_reason'] == 'api_absent', 'native unavailable load telemetry is explicit')
    pairs = [(statistics.median(samples[0][i]), statistics.median(samples[1][i])) for i in range(9)]
    return dict(median_ns=medians, wall_time_reduction=value['wall_time_reduction'],
                paired_candidate_wins=sum(after < before for before, after in pairs),
                paired_candidate_ties=sum(after == before for before, after in pairs),
                sample_ranges_ns=[[min(n for b in side for n in b), max(n for b in side for n in b)] for side in samples],
                successful_commands=90, errors=0)


def receipt_controls(original, raw):
    # Synthetic data are deliberately labelled; this does not claim a native run.
    value = deepcopy(original)
    value['environment'] = dict(python='3.12.synthetic', platform='Windows-synthetic',
                                logical_cpus=1, load=None, load_status='unavailable', load_reason='api_absent')
    validate_receipt(value, original, raw)
    crlf = deepcopy(value)
    crlf['complete_stdout'] = original['complete_stdout'][:-1] + '\r\n'
    validate_receipt(crlf, original, raw)
    cases = [
        ('sample_count', lambda x:x['elapsed_ns'][0][0].pop(), 'two sides of nine five-sample batches'),
        ('nonpositive_sample', lambda x:x['elapsed_ns'][0][0].__setitem__(0, 0), 'positive integral nanosecond observations'),
        ('wrong_median', lambda x:x['median_ns'].__setitem__(0, x['median_ns'][0] + 1), 'medians recomputed from all raw observations'),
        ('wrong_reduction', lambda x:x.__setitem__('wall_time_reduction', 0.123), 'reduction recomputed from medians'),
        ('wrong_source', lambda x:x['source_sha256'].__setitem__(0, '0' * 64), 'exact measured script hashes'),
        ('wrong_archive', lambda x:x.__setitem__('archive_sha256', '0' * 64), 'official immutable fixture and complete output: archive_sha256'),
        ('wrong_stdout', lambda x:x.__setitem__('complete_stdout', x['complete_stdout'].replace('529', '528')), 'official immutable fixture and complete output: complete_stdout'),
        ('foreign_terminal_separator', lambda x:x.__setitem__('complete_stdout', original['complete_stdout'][:-1] + '\v'), 'official immutable fixture and complete output: complete_stdout'),
        ('fabricated_zero_load', lambda x:x['environment'].__setitem__('load', 0), 'native unavailable load telemetry is explicit'),
        ('failed_command', lambda x:x.__setitem__('errors', 1), 'ninety successful complete commands'),
    ]
    for label, change, message in cases:
        wrong = deepcopy(value)
        change(wrong)
        error_is(lambda: validate_receipt(wrong, original, raw), ValueError, message)
    return [label for label, _, _ in cases]


def run(controls_only=False):
    raw = sources()
    original = json.loads(raw[ORACLE])
    frozen = benchmark.load_source()
    groups = environment_controls()
    with tempfile.TemporaryDirectory(prefix='windows-export-controls-') as temporary:
        directory = Path(temporary).resolve()
        groups += main_controls(frozen, original, directory)
        groups.append(ordering_control(frozen, original, raw, directory))
    rejected = receipt_controls(original, raw)
    result = dict(control_groups=groups, synthetic_receipt_controls=rejected,
                  source_head=HEAD, retained_files=len(raw), real_timing_commands_run_by_verifier=0)
    if not controls_only:
        path = HERE / 'BENCHMARK-WINDOWS.json'
        encoded = path.read_bytes()
        value = json.loads(encoded)
        result['native_receipt_sha256'] = sha256(encoded).hexdigest()
        result['native_observation'] = validate_receipt(value, original, raw)
        result['native_environment'] = value['environment']
    return result


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--controls-only']), 'registered receipt check or explicit unit-only mode')
    controls_only = sys.argv[1:] == ['--controls-only']
    result = run(controls_only)
    print('PASS_WINDOWS_EXPORT_BENCHMARK_CONTROLS' if controls_only else 'PASS_WINDOWS_EXPORT_BENCHMARK')
    print(json.dumps(result, sort_keys=True))
