#!/usr/bin/env python3
"""Inspect saved native RUP evidence; never compile or execute a checker.

Only these non-proof observations may differ between two native runs: top-level
UTC/platform/disk/RSS observations; compiler location/version/compile/binary
observations; run absolute directory prefixes, UTC/wall/RSS observations; raw-log
file digests (each independently authenticated); and native verification time.
Every other receipt field is compared recursively with exact JSON types.
Original proof/checker credit: Brian Ross and retained source notices. Receipt
inspection by Toik Y with substantial OpenAI Codex assistance.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import shutil
import tempfile

SCHEMA = 'b4-fresh-native-rup-replay-v1'
PINS_SHA = 'c1ffa96fda47deeb1e7f2ed0b6023cd4d864be31ab3b853a72912d5bf3e06308'
CHECKER_SHA = '78026871882de3f2fee66034e549e9c1a0a9a5291abd817d06f611f9ba0f355d'
CHECKER_COMMIT = '2e3b2dc0ecf938addbd779d42877b6ed69d9a985'
FLAGS = ['-std=c99', '-O2', '-Dgetc_unlocked=getc']
NAMES = ('ascii_rup_positive', 'binary_parser_positive', 'empty_only_rejected',
         'wrong_satisfiable_formula_rejected', 'rat_core_default_positive',
         'rat_core_rup_only_rejected')
RUN_META = ('started_utc', 'finished_utc', 'external_wall_seconds', 'rss_bytes', 'rss_status')
TOP_META = ('started_utc', 'finished_utc', 'platform', 'disk_checks', 'rss_bytes', 'rss_status')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def pairs(rows):
    value = {}
    for key, item in rows:
        need(key not in value, 'duplicate JSON key: ' + key)
        value[key] = item
    return value


def load(path):
    def bad_constant(value):
        raise ValueError('non-finite JSON constant: ' + value)
    return json.loads(path.read_bytes(), object_pairs_hook=pairs, parse_constant=bad_constant)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    need(path.is_file() and not path.is_symlink(), 'regular file required: ' + str(path))
    size = path.stat().st_size
    h = hashlib.sha256()
    g = hashlib.sha1(b'blob ' + str(size).encode() + b'\0')
    lines = 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block); g.update(block); lines += block.count(b'\n')
    return {'bytes': size, 'sha256': h.hexdigest(), 'git_blob_sha': g.hexdigest(), 'newline_count': lines}


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def authenticate(package):
    raw = (package / 'SOURCE-PINS.json').read_bytes()
    need(sha(raw) == PINS_SHA, 'original SOURCE-PINS bytes changed')
    pins = load(package / 'SOURCE-PINS.json')
    need(type(pins.get('files')) is list and len(pins['files']) == 14, 'exact fourteen source pins')
    need(pins['original_commit'] == 'ca0002008b497428f0b651501c4a220a9d2785e7', 'original source commit')
    need(pins['retained_ancestor'] == '37fdc4122f84d80cccd85aa51f631acf79904003', 'retained source ancestor')
    need(pins['checker_commit'] == CHECKER_COMMIT, 'checker commit')
    files = []; seen = set()
    for row in pins['files']:
        relative = Path(row['path'])
        need(len(relative.parts) == 2 and relative.parts[0] == 'source' and relative.name not in seen,
             'unique flat source pin')
        seen.add(relative.name)
        actual = digest(package / relative)
        need(type(row['bytes']) is int and typed_equal(actual['bytes'], row['bytes']), 'typed source byte count')
        need(actual['sha256'] == row['sha256'] and actual['git_blob_sha'] == row['git_blob_sha'] == row['expected_git_blob'],
             'source byte/Git-blob seal: ' + relative.name)
        files.append({'file': relative.name, **actual})
    sources = load(package / 'SOURCES.json')
    declared = [row for row in sources['files'] if row['usage'] == 'input']
    need(declared, 'declared execution inputs required')
    declared_paths = set(); repo = package.parents[1]
    for row in declared:
        rel = Path(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) not in declared_paths,
             'unique safe declared input')
        declared_paths.add(str(rel))
        path = repo / rel
        actual = digest(path)
        expected_blob = row.get('git_blob', row.get('git_blob_sha'))
        need(actual['sha256'] == row['sha256'] and actual['git_blob_sha'] == expected_blob,
             'declared input SHA256/Git blob: ' + str(rel))
        if 'bytes' in row:
            need(type(row['bytes']) is int and row['bytes'] == actual['bytes'], 'declared input typed byte count')
    prefix = str(package.relative_to(repo))
    need({prefix + '/' + row['path'] for row in pins['files']} <= declared_paths,
         'all fourteen source files declared as inputs')
    need('.github/workflows/gl3-rup-native-replay.yml' in declared_paths, 'dedicated workflow declared as input')
    need(digest(package / 'source/drat-trim.c')['sha256'] == CHECKER_SHA, 'unchanged checker source')
    endings = load(package / 'UPSTREAM-LINE-ENDINGS.json')
    need(endings['status'] == 'PASS_EXACT_OFFICIAL_CODE_MODULO_RETAINED_CRLF' and
         endings['official_commit'] == CHECKER_COMMIT and
         endings['official_repository'] == 'marijnheule/drat-trim', 'official line-ending provenance')
    need(type(endings['rows']) is list and len(endings['rows']) == 2 and
         [r['local'] for r in endings['rows']] == ['source/drat-trim.c', 'source/DRAT-LICENSE'],
         'exact checker/license line-ending comparisons')
    for row in endings['rows']:
        raw_source = (package / row['local']).read_bytes()
        retained = byte_digest(raw_source); normalized = byte_digest(raw_source.replace(b'\r\n', b'\n'))
        need(row['retained_source_modified'] is False and
             typed_equal(row['retained_bytes'], retained['bytes']) and
             row['retained_sha256'] == retained['sha256'] and
             row['retained_git_blob'] == retained['git_blob_sha'] and
             typed_equal(row['official_bytes'], normalized['bytes']) and
             row['official_sha256'] == normalized['sha256'] and
             row['official_git_blob'] == normalized['git_blob_sha'], 'exact CRLF-to-LF container comparison')
    harness_sha = digest(package / 'native_replay.py')['sha256']
    certificates = load(package / 'source/CERTIFICATES.json')['certificates']
    need(type(certificates) is list and len(certificates) == 2 and
         [row['length'] for row in certificates] == [7, 8] and
         all(type(row['length']) is int for row in certificates), 'exact certificate lengths')
    material = {}
    for cert in certificates:
        n = cert['length']
        for key in ('variables', 'clauses', 'cnf_bytes', 'proof_bytes', 'proof_lines'):
            need(type(cert[key]) is int and cert[key] > 0, 'typed original certificate dimensions')
        cnf = package / ('source/length%d.cnf' % n)
        cnf_digest = digest(cnf)
        with cnf.open('rb') as stream:
            need(stream.readline() == ('p cnf %d %d\n' % (cert['variables'], cert['clauses'])).encode(), 'original CNF header')
        need(cnf_digest['bytes'] == cert['cnf_bytes'] and cnf_digest['sha256'] == cert['cnf_sha256'] and
             cnf_digest['newline_count'] == cert['clauses'] + 1, 'original CNF bytes/count/SHA')
        h = hashlib.sha256(); total = lines = deletions = empty = 0; last = b''
        with gzip.open(package / ('source/length%d.rup.gz' % n), 'rb') as stream:
            for line in stream:
                total += len(line)
                need(total <= cert['proof_bytes'], 'decompressed proof exceeds original bound')
                h.update(line); lines += 1; last = line
                need(line.endswith(b'\n'), 'proof record must end at newline')
                tokens = line.split()
                deletions += bool(tokens and tokens[0] == b'd')
                empty += tokens == [b'0']
        need(total == cert['proof_bytes'] and h.hexdigest() == cert['proof_sha256'] and
             lines == cert['proof_lines'] and last.split() == [b'0'], 'original decompressed proof bytes/count/SHA/final empty')
        material[n] = {'certificate': cert, 'deletions': deletions, 'empty': empty}
    auth = {'pins_file_sha256': PINS_SHA, 'source_repository': pins['source_repository'],
            'original_commit': pins['original_commit'], 'retained_ancestor': pins['retained_ancestor'],
            'checker_commit': pins['checker_commit'], 'files': files}
    return auth, material, harness_sha, len(declared)


def read_log(row, directory, expected_name):
    need(type(row) is dict and type(row.get('path')) is str, 'typed log reference')
    need(set(row) == {'path', 'bytes', 'sha256', 'git_blob_sha', 'newline_count'}, 'exact raw-log reference fields')
    need(Path(row['path']).name == expected_name, 'exact raw log basename')
    path = directory / expected_name
    actual = digest(path)
    need(typed_equal({k: row.get(k) for k in actual}, actual), 'raw log digest/count mismatch: ' + expected_name)
    return path.read_bytes()


def parse_native(stdout, stderr, run):
    text = '\n'.join(x.decode('ascii', 'replace') for x in (stdout, stderr))
    lines = text.splitlines()
    statuses = [line for line in lines if line.startswith('s ')]
    forbidden = [word for word in ('TIMEOUT', 'NOT VERIFIED', 'DERIVATION', 'ERROR', 'SIGNAL') if word in text.upper()]
    accepted = (type(run['exit_code']) is int and run['exit_code'] == 0 and
                run['external_timeout'] is False and run['signal'] is None and
                statuses == ['s VERIFIED'] and not forbidden)
    patterns = {'clauses_core': r'c (\d+) of (\d+) clauses in core',
                'lemmas_core': r'c (\d+) of (\d+) lemmas in core using (\d+) resolution steps',
                'rat_core': r'c (\d+) RAT lemmas in core; (\d+) redundant literals in core lemmas',
                'native_verification_seconds_metadata': r'c verification time: ([0-9.]+) seconds'}
    counters = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        need(len(matches) <= 1, 'duplicate native counter: ' + key)
        if not matches:
            counters[key] = None
        elif key.endswith('_metadata'):
            counters[key] = [float(matches[0])]
        else:
            counters[key] = [int(x) for x in matches[0]]
    return {'accepted': accepted, 'exact_status_lines': statuses, 'forbidden_markers': forbidden,
            'counters': counters, 'has_rup_failure_diagnostic': 'RUP check failed' in text,
            'has_native_nonverification': 's NOT VERIFIED' in lines,
            'timing_fields_are_nondeterministic_metadata': True}


def check_run(run, logs, name, native=False):
    need(type(run['exit_code']) is int and type(run['external_timeout']) is bool,
         'exact native exit/timeout types')
    need(run['external_timeout'] is False and run['signal'] is None, 'timeout or signal cannot verify')
    need(type(run['command']) is list and all(type(x) is str for x in run['command']), 'typed command')
    stdout = read_log(run['stdout'], logs, name + '.stdout.log')
    stderr = read_log(run['stderr'], logs, name + '.stderr.log')
    if native:
        parsed = parse_native(stdout, stderr, run)
        need(typed_equal(parsed, run['native_result']), 'raw native status/counters differ from receipt: ' + name)
        need(parsed['counters']['native_verification_seconds_metadata'] is not None, 'native final timing record missing')
        return parsed
    need(run['exit_code'] == 0, 'compiler/version nonzero exit')
    return None


def fixture_bytes():
    square = b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
    wrong = b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n'
    cube = b'p cnf 3 8\n' + b''.join((' '.join(str(sign * var) for sign, var in zip(signs, (1, 2, 3))) + ' 0\n').encode()
                                   for signs in itertools.product((1, -1), repeat=3))
    return [(square, b'1 0\n0\n', True, True), (square, b'a\x02\x00a\x00', True, True),
            (square, b'0\n', True, False), (wrong, b'1 0\n0\n', True, False),
            (cube, b'1 0\n2 0\n0\n', False, True), (cube, b'1 0\n2 0\n0\n', True, False)]


def byte_digest(data):
    return {'bytes': len(data), 'sha256': sha(data),
            'git_blob_sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
            'newline_count': data.count(b'\n')}


def command(run, formula_name, proof_name, rup, seconds):
    need([Path(x).name for x in run['command'][:3]] == ['drat-trim', formula_name, proof_name], 'native exact command inputs')
    need(run['command'][3:] == (['-U'] if rup else []) + ['-t', str(seconds)], 'native RUP switch/time command')
    need(type(run['child_cpu_limit_seconds']) is int and run['child_cpu_limit_seconds'] == seconds,
         'native exact CPU limit')
    need(type(run['external_wall_limit_seconds']) is int and run['external_wall_limit_seconds'] == (420 if seconds == 300 else 10), 'native exact wall limit')
    need(run['hard_ram_cap_enforced'] is False and run['rss_bytes'] is None, 'memory accounting scope retained')
    need(type(run.get('termination_grace_seconds')) is int and run['termination_grace_seconds'] == 2 and
         type(run.get('kill_reap_wait_seconds')) is int and run['kill_reap_wait_seconds'] == 5, 'bounded termination grace')


def inspect(receipt, logs, package, auth, material, harness_sha):
    need(receipt['schema'] == SCHEMA and receipt['status'] == 'PASS_FRESH_NATIVE_RUP_REPLAY', 'complete native pair receipt required')
    need(receipt['minimum_claim'] is None, 'native proof replay is not a minimum claim')
    need(receipt['harness_sha256'] == harness_sha, 'exact executing harness hash')
    need(typed_equal(receipt['authenticated_source'], auth), 'all fourteen typed authenticated-source records')
    need(receipt['hard_ram_cap_enforced'] is False and receipt['rss_bytes'] is None, 'native memory scope')
    need(type(receipt['disk_reserve_bytes']) is int and receipt['disk_reserve_bytes'] == 8 * 1024 ** 3 and
         type(receipt['headroom_bytes']) is int and receipt['headroom_bytes'] == 256 * 1024 ** 2, 'disk reserve contract')
    need('error' not in receipt, 'native receipt contains error')
    stages = ['startup']
    for n in (7, 8):
        stages.extend(['before_length%d_materialization' % n,
                       'after_length%d_materialization_before_native' % n,
                       'after_length%d_native' % n, 'after_length%d_cleanup' % n])
    stages.append('finished')
    need(type(receipt['disk_checks']) is list and [r['stage'] for r in receipt['disk_checks']] == stages,
         'complete disk-reserve checkpoint sequence')
    materialization_bytes = {'before_length%d_materialization' % n:
                             material[n]['certificate']['cnf_bytes'] + material[n]['certificate']['proof_bytes']
                             for n in (7, 8)}
    for row in receipt['disk_checks']:
        need(row['additional_expected_bytes'] == materialization_bytes.get(row['stage'], 0),
             'disk checkpoint reserves exact declared CNF/proof materialization')
        for key in ('free_bytes', 'reserve_bytes', 'headroom_bytes', 'additional_expected_bytes', 'required_free_bytes'):
            need(type(row[key]) is int and row[key] >= 0, 'typed disk-reserve observation')
        need(row['reserve_bytes'] == receipt['disk_reserve_bytes'] and
             row['headroom_bytes'] == receipt['headroom_bytes'] and
             row['required_free_bytes'] == row['reserve_bytes'] + row['headroom_bytes'] + row['additional_expected_bytes'] and
             row['free_bytes'] >= row['required_free_bytes'], 'disk-reserve checkpoint passed')
    compiler = receipt['compiler']
    need(compiler['source_sha256'] == CHECKER_SHA and compiler['source_changed'] is False and
         typed_equal(compiler['compile_flags'], FLAGS), 'unchanged C checker and compile flags')
    check_run(compiler['version'], logs, 'compiler-version')
    check_run(compiler['compile'], logs, 'compile')
    for run, seconds in [(compiler['version'], 10), (compiler['compile'], 60)]:
        need(type(run['child_cpu_limit_seconds']) is int and run['child_cpu_limit_seconds'] == seconds and
             type(run['external_wall_limit_seconds']) is int and run['external_wall_limit_seconds'] == seconds and
             run['hard_ram_cap_enforced'] is False and run['rss_bytes'] is None,
             'bounded compiler/version process contract')
    need(compiler['version']['command'] == [compiler['executable'], '--version'], 'compiler version command')
    cc = compiler['compile']['command']
    need(len(cc) == 7 and cc[0] == compiler['executable'] and cc[1:4] == FLAGS and
         Path(cc[4]).name == 'drat-trim.c' and cc[5] == '-o' and Path(cc[6]).name == 'drat-trim', 'compile command flags/source')
    controls = receipt['controls']
    need(type(controls) is list and len(controls) == 6 and [x['name'] for x in controls] == list(NAMES), 'exact six ordered native controls')
    for run, name, (formula, proof, rup, expected) in zip(controls, NAMES, fixture_bytes()):
        need(run['expected_verified'] is expected and run['rup_only'] is rup and run['control_passed'] is True, 'typed control contract: ' + name)
        need(typed_equal(run['formula'], byte_digest(formula)) and typed_equal(run['proof'], byte_digest(proof)), 'exact control fixture hashes: ' + name)
        command(run, name + '.cnf', name + '.proof', rup, 10)
        parsed = check_run(run, logs, name, True)
        need(parsed['accepted'] is expected, 'native control semantic outcome: ' + name)
        if expected:
            need(run['exit_code'] == 0 and parsed['counters']['clauses_core'] is not None and parsed['counters']['lemmas_core'] is not None and parsed['counters']['rat_core'] is not None, 'verified positive paired native evidence')
        else:
            need(run['exit_code'] != 0 and parsed['has_native_nonverification'] is True, 'semantic rejection, not silent/error-only exit')
        if name == 'rat_core_default_positive':
            need(parsed['counters']['rat_core'][0] >= 1, 'default DRAT must genuinely use RAT')
        if name == 'rat_core_rup_only_rejected':
            need(parsed['has_rup_failure_diagnostic'] is True, 'RUP-only control must reject RAT-only step')
    runs = receipt['proof_replays']
    need(type(runs) is list and len(runs) == 2 and [x['length'] for x in runs] == [7, 8] and
         all(type(x['length']) is int for x in runs), 'exact paired native lengths seven/eight')
    for run in runs:
        n = run['length']; cert = material[n]['certificate']
        need(run['status'] == 'PASS_FRESH_NATIVE_RUP_REPLAY' and 'error' not in run and
             run['rup_only'] is True and run['inputs_before_after_identical'] is True and
             type(run['internal_time_limit_seconds']) is int and run['internal_time_limit_seconds'] == 300, 'full successful RUP replay fields')
        command(run, 'length%d.cnf' % n, 'length%d.rup' % n, True, 300)
        parsed = check_run(run, logs, 'length%d_rup' % n, True)
        need(parsed['accepted'] is True and parsed['counters']['rat_core'] is not None and
             parsed['counters']['rat_core'][0] == 0, 'native zero-exit VERIFIED, zero RAT, no error markers')
        for field, bytekey, shakey, linecount, compressed in [('formula', 'cnf_bytes', 'cnf_sha256', cert['clauses'] + 1, False), ('proof', 'proof_bytes', 'proof_sha256', cert['proof_lines'], True)]:
            expected = {'bytes': cert[bytekey], 'sha256': cert[shakey], 'lines': linecount,
                        'terminated_eof': True, 'stream_read_limit_bytes': cert[bytekey], 'compressed': compressed}
            need(typed_equal(run[field], expected), 'original certificate exact materialization: ' + field)
        common = {'strict_canonical_decimal_ascii': True, 'comments_accepted': False, 'maximum_line_bytes': 1024 * 1024}
        need(typed_equal(run['formula_ascii'], {**common, 'records': cert['clauses'], 'deletion_records': 0, 'empty_additions': 0, 'last_record_empty_addition': False}), 'formula grammar/count receipt')
        need(typed_equal(run['proof_ascii'], {**common, 'records': cert['proof_lines'], 'deletion_records': material[n]['deletions'], 'empty_additions': material[n]['empty'], 'last_record_empty_addition': True}), 'decompressed proof grammar/count receipt')
        original = parse_native((package / ('source/length%d-checker.log' % n)).read_bytes(), b'', {'exit_code': 0, 'external_timeout': False, 'signal': None})
        need(all(typed_equal(parsed['counters'][k], original['counters'][k]) for k in ('clauses_core', 'lemmas_core', 'rat_core')), 'proof-relevant native counters match pinned predecessor log')
    return projection(receipt)


def projection(receipt):
    value = copy.deepcopy(receipt)
    for key in TOP_META:
        value.pop(key, None)
    compiler = value['compiler']
    for key in ('executable', 'version', 'compile', 'binary'):
        compiler.pop(key)
    for run in value['controls'] + value['proof_replays']:
        for key in RUN_META:
            run.pop(key, None)
        run['command'][:3] = [Path(x).name for x in run['command'][:3]]
        run.pop('stdout'); run.pop('stderr')
        run['native_result']['counters'].pop('native_verification_seconds_metadata')
    return value



def selftest(retained, logs, package, auth, material, harness_sha, reference):
    """Exercise actual saved evidence mutations; no native calls or source copies."""
    names = ['actual_retained_pair_and20_rawlogs']
    mutants = {
        'native_exit0_without_VERIFIED': lambda x: x['proof_replays'][0]['native_result'].update(exact_status_lines=[]),
        'timeout_even_with_zero_exit': lambda x: x['proof_replays'][0].update(external_timeout=True),
        'absent_required_control': lambda x: x['controls'].pop(),
        'wrong_raw_evidence_hash': lambda x: x['proof_replays'][0]['stdout'].update(sha256='0' * 64),
        'typed_exit_zero_replaced_false': lambda x: x['proof_replays'][0].update(exit_code=False),
        'RAT_only_accidentally_expected_accepted': lambda x: x['controls'][-1].update(expected_verified=True),
        'typed_rat_zero_replaced_false': lambda x: x['proof_replays'][0]['native_result']['counters']['rat_core'].__setitem__(0, False),
        'source_bytecount_integer_replaced_false': lambda x: x['authenticated_source']['files'][0].update(bytes=False),
        'original_decompressed_proof_hash_wrong': lambda x: x['proof_replays'][1]['proof'].update(sha256='0' * 64),
        'disk_checkpoint_below_reserve': lambda x: x['disk_checks'][0].update(free_bytes=0),
        'disk_materialization_budget_removed': lambda x: x['disk_checks'][1].update(additional_expected_bytes=0, required_free_bytes=x['disk_reserve_bytes'] + x['headroom_bytes']),
    }
    def rejects(value, directory, name):
        try:
            inspect(value, directory, package, auth, material, harness_sha)
        except (ValueError, KeyError, TypeError, IndexError, AttributeError):
            names.append(name)
            return
        raise ValueError('receipt mutation was accepted: ' + name)
    for name, mutate in mutants.items():
        value = copy.deepcopy(retained)
        mutate(value)
        rejects(value, logs, name)
    for name in ('hashlinked_stdout_missing_VERIFIED', 'RAT_only_accidentally_native_accepted'):
        with tempfile.TemporaryDirectory(prefix='rup-receipt-control-') as directory:
            temporary = Path(directory)
            need(package != temporary and package not in temporary.parents, 'selftest logs outside package')
            for path in logs.glob('*.log'):
                shutil.copyfile(path, temporary / path.name)
            value = copy.deepcopy(retained)
            if name == 'hashlinked_stdout_missing_VERIFIED':
                run = value['proof_replays'][0]
                path = temporary / 'length7_rup.stdout.log'
                path.write_bytes(path.read_bytes().replace(b's VERIFIED', b'c status missing'))
                run['stdout'] = {'path': str(path), **digest(path)}
            else:
                run = value['controls'][-1]
                path = temporary / 'rat_core_rup_only_rejected.stdout.log'
                path.write_bytes((temporary / 'rat_core_default_positive.stdout.log').read_bytes())
                run['stdout'] = {'path': str(path), **digest(path)}
                run['exit_code'] = 0
                run['native_result'] = parse_native(path.read_bytes(), b'', run)
            rejects(value, temporary, name)
    value = copy.deepcopy(retained)
    value['platform']['system'] = 'other-platform-metadata'
    value['compiler']['binary']['sha256'] = 'other-binary-metadata'
    value['proof_replays'][0]['external_wall_seconds'] = 9.5
    need(typed_equal(reference, inspect(value, logs, package, auth, material, harness_sha)),
         'documented runtime metadata did not normalize')
    names.append('runtime_metadata_normalizes')
    value = copy.deepcopy(retained)
    value['proof_replays'][0]['unknown_proof_field'] = 'must remain'
    need(not typed_equal(reference, inspect(value, logs, package, auth, material, harness_sha)),
         'unknown proof field was normalized away')
    names.append('unknown_proof_field_preserved')
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent,
                        help='package root (default: directory of this verifier)')
    parser.add_argument('--native-receipt', type=Path,
                        help='inspect new native RESULT.json and sibling raw logs against retained evidence')
    parser.add_argument('--selftest', action='store_true',
                        help='run sixteen saved-evidence controls without native execution')
    args = parser.parse_args()
    package = args.package.resolve()
    auth, material, harness_sha, declared_count = authenticate(package)
    retained = load(package / 'NATIVE-RESULT.json')
    reference = inspect(retained, package / 'native-logs', package, auth, material, harness_sha)
    if args.native_receipt:
        path = args.native_receipt.resolve()
        observed = inspect(load(path), path.parent, package, auth, material, harness_sha)
        need(typed_equal(observed, reference), 'new native proof-relevant receipt fields differ from retained run')
    control_names = selftest(retained, package / 'native-logs', package, auth, material, harness_sha, reference) if args.selftest else []
    print(json.dumps({'schema': 'b4-native-rup-evidence-inspection-v1',
                      'status': 'PASS_SAVED_NATIVE_RUP_EVIDENCE_INSPECTION',
                      'execution_performed': False, 'source_files': 14, 'declared_input_files': declared_count,
                      'proof_lengths': [7, 8], 'native_controls': 6, 'raw_logs_authenticated': 20,
                      'source_pins_sha256': PINS_SHA, 'checker_commit': CHECKER_COMMIT,
                      'harness_sha256': harness_sha, 'proof_relevant_receipt_sha256': canonical(reference),
                      'minimum_claim': None, 'receipt_control_cases': len(control_names),
                      'receipt_control_names': control_names}, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, TypeError, IndexError, AttributeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({'status': 'FAIL_CLOSED', 'error': str(error)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
