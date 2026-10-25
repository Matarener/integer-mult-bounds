#!/usr/bin/env python3
"""Fresh bounded native RUP replay of pinned formulas and proofs; stdlib only.

Original inputs/checker credits and licenses are retained in source. Harness by
Toik Y with substantial OpenAI Codex assistance. No mathematical minimum claim.
All persistent writes require an explicit new output directory outside package.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import datetime
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import tempfile
import time

CHECKER_SHA = '78026871882de3f2fee66034e549e9c1a0a9a5291abd817d06f611f9ba0f355d'
RESERVE = 8 * 1024 ** 3
HEADROOM = 256 * 1024 ** 2
MAX_LINE = 1024 * 1024
MAX_LITERAL = 2 ** 30 - 1
DECIMAL = re.compile(rb'(?:0|-?[1-9][0-9]*)\Z')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest_file(path):
    size = path.stat().st_size
    h = hashlib.sha256()
    git = hashlib.sha1(b'blob ' + str(size).encode() + b'\0')
    lines = 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block); git.update(block); lines += block.count(b'\n')
    return {'bytes': size, 'sha256': h.hexdigest(), 'git_blob_sha': git.hexdigest(), 'newline_count': lines}


def space(path, stage, events, additional=0):
    free = shutil.disk_usage(path).free
    row = {'stage': stage, 'free_bytes': free, 'reserve_bytes': RESERVE,
           'headroom_bytes': HEADROOM, 'additional_expected_bytes': additional,
           'required_free_bytes': RESERVE + HEADROOM + additional, 'at_utc': utc()}
    events.append(row)
    need(free >= row['required_free_bytes'], '8 GiB reserve plus headroom fails at ' + stage)


def authenticate(source, pins_path):
    raw = pins_path.read_bytes()
    pins = json.loads(raw)
    need(type(pins) is dict and type(pins.get('files')) is list, 'typed SOURCE-PINS files required')
    checked = []
    seen = set()
    for row in pins['files']:
        relative = Path(row['path'])
        need(not relative.is_absolute() and '..' not in relative.parts, 'safe relative source pin')
        path = (source.parent / relative).resolve()
        need(path.parent == source and path.name not in seen, 'unique flat source file pin')
        seen.add(path.name)
        observed = digest_file(path)
        need(type(row['bytes']) is int and observed['bytes'] == row['bytes'], 'source byte pin ' + path.name)
        need(observed['sha256'] == row['sha256'] and observed['git_blob_sha'] == row['git_blob_sha'],
             'source SHA256/Git blob pin ' + path.name)
        if 'expected_git_blob' in row:
            need(observed['git_blob_sha'] == row['expected_git_blob'], 'ancestor Git blob pin ' + path.name)
        checked.append({'file': path.name, **observed})
    required = {'drat-trim.c', 'CHECKER.json', 'CERTIFICATES.json', 'length7.cnf', 'length8.cnf',
                'length7.rup.gz', 'length8.rup.gz'}
    need(required <= seen, 'all native replay inputs pinned')
    need(digest_file(source / 'drat-trim.c')['sha256'] == CHECKER_SHA, 'exact unchanged checker source')
    checker = json.loads((source / 'CHECKER.json').read_bytes())
    need(checker['source_sha256'] == CHECKER_SHA, 'authenticated checker declaration source SHA')
    certificates = json.loads((source / 'CERTIFICATES.json').read_bytes())['certificates']
    need({row['length'] for row in certificates} == {7, 8} and len(certificates) == 2, 'exact two certificates')
    return certificates, {'pins_file_sha256': hashlib.sha256(raw).hexdigest(),
                          'source_repository': pins.get('source_repository'),
                          'original_commit': pins.get('original_commit'),
                          'retained_ancestor': pins.get('retained_ancestor'),
                          'checker_commit': pins.get('checker_commit'), 'files': checked}


def cpu_limit(seconds):
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds))
    return apply


def run_child(command, directory, output, name, wall, cpu):
    stdout = output / (name + '.stdout.log')
    stderr = output / (name + '.stderr.log')
    started = utc(); begin = time.monotonic(); timed_out = False
    with stdout.open('wb') as out, stderr.open('wb') as err:
        child = subprocess.Popen(command, cwd=directory, stdout=out, stderr=err,
                                 start_new_session=True, preexec_fn=cpu_limit(cpu))
        try:
            code = child.wait(timeout=wall)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                code = child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                code = child.wait(timeout=5)
    return {'command': [str(x) for x in command], 'started_utc': started, 'finished_utc': utc(),
            'external_wall_seconds': time.monotonic() - begin, 'external_wall_limit_seconds': wall,
            'termination_grace_seconds': 2, 'kill_reap_wait_seconds': 5,
            'child_cpu_limit_seconds': cpu, 'exit_code': code, 'external_timeout': timed_out,
            'signal': -code if code < 0 else None, 'rss_bytes': None,
            'rss_status': 'UNKNOWN: no reliable per-process peak RSS sampler',
            'hard_ram_cap_enforced': False,
            'stdout': {'path': str(stdout), **digest_file(stdout)},
            'stderr': {'path': str(stderr), **digest_file(stderr)}}


def parse_native(run):
    text = '\n'.join(Path(run[key]['path']).read_bytes().decode('ascii', 'replace') for key in ('stdout', 'stderr'))
    lines = text.splitlines()
    statuses = [line for line in lines if line.startswith('s ')]
    exact_verified = statuses == ['s VERIFIED']
    forbidden = [word for word in ('TIMEOUT', 'NOT VERIFIED', 'DERIVATION', 'ERROR', 'SIGNAL')
                 if word in text.upper()]
    accepted = (run['exit_code'] == 0 and not run['external_timeout'] and run['signal'] is None
                and exact_verified and not forbidden)
    counters = {}
    patterns = {
        'clauses_core': r'c (\d+) of (\d+) clauses in core',
        'lemmas_core': r'c (\d+) of (\d+) lemmas in core using (\d+) resolution steps',
        'rat_core': r'c (\d+) RAT lemmas in core; (\d+) redundant literals in core lemmas',
        'native_verification_seconds_metadata': r'c verification time: ([0-9.]+) seconds',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        counters[key] = ([float(match.group(1))] if key.endswith('_metadata') else [int(x) for x in match.groups()]) if match else None
    return {'accepted': accepted, 'exact_status_lines': statuses, 'forbidden_markers': forbidden,
            'counters': counters, 'has_rup_failure_diagnostic': 'RUP check failed' in text,
            'has_native_nonverification': 's NOT VERIFIED' in lines,
            'timing_fields_are_nondeterministic_metadata': True}


def native(binary, formula, proof, work, output, name, rup=True, seconds=10):
    command = [str(binary), str(formula), str(proof)]
    if rup:
        command.append('-U')
    command.extend(('-t', str(seconds)))
    run = run_child(command, work, output, name, 420 if seconds == 300 else 10, seconds)
    run['native_result'] = parse_native(run)
    return run


def controls(binary, work, output, results):
    square = b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
    wrong = b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n'
    cube = b'p cnf 3 8\n' + b''.join((' '.join(str(sign * var) for sign, var in zip(signs, (1, 2, 3))) + ' 0\n').encode()
                                           for signs in itertools.product((1, -1), repeat=3))
    fixtures = [
        ('ascii_rup_positive', square, b'1 0\n0\n', True, True),
        ('binary_parser_positive', square, b'a\x02\x00a\x00', True, True),
        ('empty_only_rejected', square, b'0\n', True, False),
        ('wrong_satisfiable_formula_rejected', wrong, b'1 0\n0\n', True, False),
        ('rat_core_default_positive', cube, b'1 0\n2 0\n0\n', False, True),
        ('rat_core_rup_only_rejected', cube, b'1 0\n2 0\n0\n', True, False),
    ]
    for name, formula_bytes, proof_bytes, rup, expected in fixtures:
        formula, proof = work / (name + '.cnf'), work / (name + '.proof')
        formula.write_bytes(formula_bytes); proof.write_bytes(proof_bytes)
        run = native(binary, formula, proof, work, output, name, rup)
        result = run['native_result']
        run.update({'name': name, 'expected_verified': expected, 'rup_only': rup,
                    'formula': digest_file(formula), 'proof': digest_file(proof), 'control_passed': False})
        results.append(run)
        need(result['accepted'] == expected, 'native calibration acceptance mismatch ' + name)
        need(not run['external_timeout'] and run['signal'] is None, 'native calibration timeout/signal ' + name)
        if not expected:
            need(result['has_native_nonverification'] or result['has_rup_failure_diagnostic'],
                 'negative control must reject semantically, not by unknown error ' + name)
        if name == 'rat_core_default_positive':
            need(result['counters']['rat_core'] is not None and result['counters']['rat_core'][0] >= 1,
                 'default DRAT calibration actually uses RAT')
        if name == 'rat_core_rup_only_rejected':
            need(result['has_rup_failure_diagnostic'], 'RUP-only switch diagnostic')
        run['control_passed'] = True
    return results


def copy_bounded(source, destination, expected_bytes, expected_sha, expected_lines, compressed):
    need(type(expected_bytes) is int and 0 < expected_bytes, 'positive typed declared bytes')
    h = hashlib.sha256(); total = lines = 0; last = b''
    opener = gzip.open if compressed else open
    with opener(source, 'rb') as src, destination.open('xb') as dst:
        while chunk := src.read(min(1024 * 1024, expected_bytes - total + 1)):
            total += len(chunk)
            need(total <= expected_bytes, 'decompressed/copied stream exceeds declared bytes')
            h.update(chunk); lines += chunk.count(b'\n'); last = chunk[-1:]; dst.write(chunk)
    need(total == expected_bytes and h.hexdigest() == expected_sha, 'exact decompressed/copied bytes and SHA')
    need(type(expected_lines) is int and lines == expected_lines and last == b'\n', 'exact line count and terminated EOF')
    return {'bytes': total, 'sha256': h.hexdigest(), 'lines': lines, 'terminated_eof': True,
            'stream_read_limit_bytes': expected_bytes, 'compressed': compressed}


def strict_ascii(path, variables, expected_clauses=None):
    records = deletions = empty_additions = 0; last_empty = False; header = False
    with path.open('rb') as stream:
        while line := stream.readline(MAX_LINE + 1):
            need(len(line) <= MAX_LINE and line.endswith(b'\n'), 'bounded complete ASCII record')
            need(all(byte in (9, 10, 13, 32) or 33 <= byte <= 126 for byte in line), 'ASCII byte grammar')
            tokens = line.split()
            need(tokens, 'empty physical record rejected')
            if expected_clauses is not None and not header:
                need(tokens == [b'p', b'cnf', str(variables).encode(), str(expected_clauses).encode()], 'exact DIMACS header')
                header = True; continue
            deletion = tokens[0] == b'd'
            if deletion:
                need(expected_clauses is None, 'no formula deletion record'); tokens = tokens[1:]; deletions += 1
            need(tokens and tokens[-1] == b'0' and all(DECIMAL.fullmatch(token) for token in tokens), 'canonical decimal zero-terminated record')
            literals = [int(token) for token in tokens[:-1]]
            need(all(0 < abs(lit) <= min(variables, MAX_LITERAL) for lit in literals), 'nonzero in-range literal')
            records += 1; last_empty = not literals and not deletion
            if last_empty:
                empty_additions += 1
    if expected_clauses is not None:
        need(header and records == expected_clauses and deletions == 0, 'exact formula clause count')
    else:
        need(records > 0 and empty_additions > 0 and last_empty, 'proof has explicit final empty addition')
    return {'records': records, 'deletion_records': deletions, 'empty_additions': empty_additions,
            'last_record_empty_addition': last_empty, 'strict_canonical_decimal_ascii': True,
            'comments_accepted': False, 'maximum_line_bytes': MAX_LINE}


def replay(certificate, source, binary, work, output, events):
    n = certificate['length']; variables = certificate['variables']; clauses = certificate['clauses']
    need(type(variables) is int and type(clauses) is int and 0 < variables <= MAX_LITERAL and clauses > 0,
         'typed certificate dimensions')
    cnf_source = source / Path(certificate['cnf']).name
    proof_source = source / Path(certificate['proof_gzip']).name
    additional = certificate['cnf_bytes'] + certificate['proof_bytes']
    space(output, 'before_length' + str(n) + '_materialization', events, additional)
    formula, proof = work / ('length' + str(n) + '.cnf'), work / ('length' + str(n) + '.rup')
    run = {'length': n, 'status': 'INCOMPLETE', 'rup_only': True, 'internal_time_limit_seconds': 300}
    try:
        cnf_info = copy_bounded(cnf_source, formula, certificate['cnf_bytes'], certificate['cnf_sha256'], clauses + 1, False)
        proof_info = copy_bounded(proof_source, proof, certificate['proof_bytes'], certificate['proof_sha256'], certificate['proof_lines'], True)
        cnf_syntax = strict_ascii(formula, variables, clauses)
        proof_syntax = strict_ascii(proof, variables)
        need(proof_syntax['records'] == certificate['proof_lines'], 'every declared proof line is one strict record')
        space(output, 'after_length' + str(n) + '_materialization_before_native', events)
        before = {'cnf': digest_file(formula), 'proof': digest_file(proof)}
        run.update(native(binary, formula, proof, work, output, 'length' + str(n) + '_rup', True, 300))
        after = {'cnf': digest_file(formula), 'proof': digest_file(proof)}
        need(before == after, 'native inputs unchanged after checker')
        space(output, 'after_length' + str(n) + '_native', events)
        run.update({'length': n, 'rup_only': True, 'internal_time_limit_seconds': 300,
                    'formula': cnf_info, 'proof': proof_info, 'formula_ascii': cnf_syntax,
                    'proof_ascii': proof_syntax, 'inputs_before_after_identical': True})
        need(run['native_result']['accepted'], 'fresh native RUP verification did not succeed for length ' + str(n))
        rat = run['native_result']['counters']['rat_core']
        need(rat is not None and rat[0] == 0, 'RUP replay has zero reported RAT core lemmas')
        run['status'] = 'PASS_FRESH_NATIVE_RUP_REPLAY'
    except Exception as error:
        run['status'] = 'FAILED_CLOSED'
        run['error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        formula.unlink(missing_ok=True); proof.unlink(missing_ok=True)
        space(output, 'after_length' + str(n) + '_cleanup', events)
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument('--source', type=Path, default=here / 'source')
    parser.add_argument('--pins', type=Path, help='defaults to SOURCE-PINS.json beside source/')
    parser.add_argument('--output', type=Path, required=True, help='new directory outside the package')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--controls-only', action='store_true')
    modes.add_argument('--length', type=int, choices=(7, 8), action='append')
    parser.add_argument('--cc', default='cc')
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    pins = (args.pins or source.parent / 'SOURCE-PINS.json').resolve()
    package = source.parent
    need(output != package and package not in output.parents, 'output must be outside package')
    need(source.is_dir() and pins.is_file(), 'source and pins available')
    need(not output.exists(), 'output directory must be new; no overwrite')
    output.mkdir(parents=True)
    result = {'schema': 'b4-fresh-native-rup-replay-v1', 'status': 'INCOMPLETE', 'started_utc': utc(),
              'proof_scope': 'Fresh native RUP-only verification of exact pinned CNF/proof bytes; model equivalence, shorter lengths and minimum admission remain separate.',
              'harness_sha256': digest_file(Path(__file__).resolve())['sha256'],
              'platform': {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
                           'python': sys.version, 'native_timing_is_metadata': True},
              'hard_ram_cap_enforced': False, 'rss_bytes': None, 'rss_status': 'UNKNOWN',
              'disk_reserve_bytes': RESERVE, 'headroom_bytes': HEADROOM,
              'disk_checks': [], 'controls': [], 'proof_replays': [], 'minimum_claim': None,
              'original_mathematical_argument_credit': 'Brian Ross',
              'harness_credit': 'Toik Y with substantial OpenAI Codex assistance'}
    exit_code = 1
    try:
        space(output, 'startup', result['disk_checks'])
        certificates, source_receipt = authenticate(source, pins)
        result['authenticated_source'] = source_receipt
        compiler = shutil.which(args.cc)
        need(compiler is not None, 'native C compiler available')
        compiler = str(Path(compiler).resolve())
        with tempfile.TemporaryDirectory(prefix='native-work-', dir=output) as directory:
            work = Path(directory); binary = work / 'drat-trim'
            version = run_child([compiler, '--version'], work, output, 'compiler-version', 10, 10)
            result['compiler'] = {'executable': compiler, 'version': version, 'source_sha256': CHECKER_SHA,
                                  'compile_flags': ['-std=c99', '-O2', '-Dgetc_unlocked=getc']}
            need(version['exit_code'] == 0 and not version['external_timeout'], 'compiler version succeeded')
            compile_run = run_child([compiler, '-std=c99', '-O2', '-Dgetc_unlocked=getc', str(source / 'drat-trim.c'), '-o', str(binary)],
                                    work, output, 'compile', 60, 60)
            result['compiler']['compile'] = compile_run
            need(compile_run['exit_code'] == 0 and not compile_run['external_timeout'] and binary.is_file(), 'unchanged checker compilation succeeded')
            need(digest_file(source / 'drat-trim.c')['sha256'] == CHECKER_SHA, 'checker source unchanged after compile')
            result['compiler'].update({'binary': digest_file(binary), 'source_changed': False})
            controls(binary, work, output, result['controls'])
            for n in args.length or ([] if args.controls_only else [7, 8]):
                need(n not in [row['length'] for row in result['proof_replays']], 'no duplicate native proof run')
                certificate = next(row for row in certificates if row['length'] == n)
                replay_result = replay(certificate, source, binary, work, output, result['disk_checks'])
                result['proof_replays'].append(replay_result)
                need(replay_result['status'] == 'PASS_FRESH_NATIVE_RUP_REPLAY', 'fresh proof replay failed closed')
        space(output, 'finished', result['disk_checks'])
        result['status'] = 'PASS_CONTROLS_ONLY' if args.controls_only else 'PASS_FRESH_NATIVE_RUP_REPLAY'
        exit_code = 0
    except Exception as error:
        result['status'] = 'FAILED_CLOSED'
        result['error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        result['finished_utc'] = utc()
        receipt = output / 'RESULT.json'
        receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        print(json.dumps({'status': result['status'], 'receipt': str(receipt), 'receipt_sha256': digest_file(receipt)['sha256'],
                          'controls': len(result['controls']), 'proof_replays': len(result['proof_replays'])}, sort_keys=True))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
