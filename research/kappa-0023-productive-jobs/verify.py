#!/usr/bin/env python3
"""Replay the frozen 0.0023 checkpoint sequentially in a new private directory.

Only the dependency order changes: the independent phase audit must precede
the cover that records its hash. No scientific predicate or frozen source is
patched. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zlib
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCOPE = Path('research/kappa-rebuild')
TIMING = {'runtime', 'runtime_seconds', 'elapsed_seconds', 'seconds'}
ENVIRONMENT_RECEIPTS = {str(SCOPE / 'complex/fresh-certificates' / ('RESULT-' + tag + '.json'))
                        for tag in ('H', 'helpers', 'logger')}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(root, name):
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and str(p) == name,
         'Canonical relative input path: ' + name)
    target = root
    for part in p.parts:
        target = target / part
        need(not target.is_symlink(), 'No source symlink: ' + name)
    need(target.is_file(), 'Source exists: ' + name)
    return target


def read_payload(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def normalize(value, hashes):
    if isinstance(value, dict):
        return {k: normalize(v, hashes) for k, v in value.items() if k not in TIMING}
    if isinstance(value, list):
        return [normalize(v, hashes) for v in value]
    return hashes.get(value, value) if isinstance(value, str) else value


def compare_outputs(repo, outputs):
    hashes = {}
    for name in sorted(outputs):
        old, new = digest(checked(ROOT, name)), digest(checked(repo, name))
        need(old not in hashes or hashes[old] == new, 'Equal source artifacts replay equally')
        hashes[old] = new
    comparisons = []
    for name in sorted(outputs):
        old, new = checked(ROOT, name), checked(repo, name)
        exact = old.read_bytes() == new.read_bytes()
        left, right = normalize(read_payload(old), hashes), normalize(read_payload(new), {})
        environment_changes = {}
        if name in ENVIRONMENT_RECEIPTS:
            # These exact metadata leaves identify the executing host. Preserve
            # both values in the receipt; no other environment field is waived.
            for key, actual in (('python', sys.version), ('platform', platform.platform())):
                need(right['environment'][key] == actual, 'Fresh environment metadata is accurate')
                a, b = left['environment'].pop(key), right['environment'].pop(key)
                if a != b:
                    environment_changes[key] = {'reference': a, 'fresh': b}
        need(left == right, 'Scientific artifact differs beyond declared metadata/hash substitution: ' + name)
        comparisons.append({'path': name, 'reference_sha256': digest(old),
                            'fresh_sha256': digest(new), 'exact_bytes': exact,
                            'environment_changes': environment_changes,
                            'equal_after_declared_normalization': True})
    return comparisons


def authenticate():
    manifest = json.loads((HERE / 'IMPORT.json').read_text())
    names, destinations = set(), set()
    for row in manifest['imported_files'] + manifest['canonical_main_inputs']:
        name = row['path']
        need(name not in names, 'Unique imported input: ' + name)
        names.add(name)
        destination = row.get('replay_path', name)
        relative = PurePosixPath(destination)
        need(not relative.is_absolute() and '..' not in relative.parts and str(relative) == destination,
             'Canonical replay destination: ' + destination)
        need(destination not in destinations, 'Unique replay destination: ' + destination)
        destinations.add(destination)
        path = checked(ROOT, name)
        need(path.stat().st_size == row['bytes'] and digest(path) == row['sha256'],
             'Exact input bytes: ' + name)
        if 'mode' in row:
            need(path.stat().st_mode & 0o777 == row['mode'], 'Exact source mode: ' + name)
    claim = json.loads((ROOT / SCOPE / 'CLAIM.json').read_text())
    need(claim['kappa'] == '23/10000', 'Exact claimed kappa')
    need(claim['official_selected_frontier_modified'] is False, 'Conditional claim scope')
    target = Fraction(claim['kappa'])
    savings = {k: Fraction(v) for k, v in claim['nine_outer_savings'].items()}
    need(len(savings) == 9 and min(savings.values()) - target == Fraction(98849, 50000000000),
         'All nine outer costs and exact limiting slack')
    previous = Fraction('0.001730980255989036959962') - Fraction(1, 10**46) - Fraction(1, 10**70)
    return manifest, {
        'kappa': str(target), 'previous_pr': 4181, 'previous_conditional_kappa': str(previous),
        'relative_exponent_saving_increase': str(target / previous - 1),
        'limiting_outer_slack': str(min(savings.values()) - target),
        'source_scope_files': len(manifest['imported_files']),
        'canonical_main_inputs': len(manifest['canonical_main_inputs']),
    }


def load_stages():
    path = ROOT / SCOPE / 'replay_critical.py'
    spec = importlib.util.spec_from_file_location('frozen_kappa_replay', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stages = [*module.COMPLEX, *module.BIT, *module.ASSEMBLY]
    phase = next(s for s in stages if s['name'] == 'p3_independent_phases')
    stages.remove(phase)
    index = next(i for i, s in enumerate(stages) if s['name'] == 'p3_native_cover')
    stages.insert(index, phase)
    need(len(stages) == 23 and len({s['name'] for s in stages}) == 23,
         'Exactly the original 23 distinct scientific stages')
    return stages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--out', type=Path, help='New, nonexistent directory for replay, logs and receipt')
    args = parser.parse_args()
    need(args.check_only != (args.out is not None), 'Choose --check-only or --out NEW_DIRECTORY')
    manifest, arithmetic = authenticate()
    if args.check_only:
        subprocess.run([sys.executable, '-B', str(ROOT / SCOPE / 'verify_scope.py')],
                       cwd=ROOT, check=True)
        print(json.dumps({'status': 'PASS_FROZEN_IMPORT_AND_CLAIM_ARITHMETIC', **arithmetic}, sort_keys=True))
        return
    out = args.out.resolve()
    need(not out.exists(), 'Replay output must not already exist')
    need(not out.is_relative_to(ROOT), 'Keep generated replay outside the contribution checkout')
    out.mkdir(parents=True)
    repo = out / 'repo'
    logs = out / 'logs'
    logs.mkdir()
    rows = manifest['imported_files'] + manifest['canonical_main_inputs']
    for row in rows:
        source = checked(ROOT, row['path'])
        destination = repo / row.get('replay_path', row['path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    stages = load_stages()
    started = time.monotonic()
    result = {
        'schema': 'conditional-kappa-0023-local-replay/1', 'status': 'RUNNING',
        'base_commit': manifest['base_commit'], 'import_manifest_sha256': digest(HERE / 'IMPORT.json'),
        'review_runner_sha256': digest(Path(__file__)),
        'environment': {'python': sys.version, 'executable': sys.executable,
                        'platform': platform.platform(), 'zlib': zlib.ZLIB_RUNTIME_VERSION},
        'execution': 'Sequential, in a fresh directory; original scientific scripts are unchanged.',
        'order_repair': 'p3_independent_phases precedes p3_native_cover, which pins its regenerated hash.',
        'arithmetic': arithmetic, 'stages': [], 'comparisons': [],
        'limits': 'Finite executable checks and quantitative interfaces; written universal proofs and inherited analytic/native assumptions require external review. Winning uniform templates are not materialized.',
    }
    receipt = out / 'VALIDATION.json'
    environment = os.environ.copy()
    environment.pop('PYTHONOPTIMIZE', None)
    environment.pop('PYTHONPATH', None)
    try:
        with tempfile.TemporaryDirectory(prefix='kappa-0023-bytecode-') as cache:
            environment['PYTHONPYCACHEPREFIX'] = cache
            for stage in stages:
                script = checked(repo, stage['script'])
                command = [sys.executable, '-B', '-X', 'pycache_prefix=' + cache,
                           stage['script'], *stage['arguments']]
                logfile = logs / (stage['name'] + '.log')
                began = time.monotonic()
                with logfile.open('wb') as output:
                    completed = subprocess.run(command, cwd=repo, env=environment,
                                               stdout=output, stderr=subprocess.STDOUT,
                                               timeout=600, check=False)
                entry = {'stage': stage['name'], 'command': command,
                         'source_sha256': digest(script), 'returncode': completed.returncode,
                         'seconds': time.monotonic() - began,
                         'log': str(logfile.relative_to(out)), 'log_sha256': digest(logfile)}
                result['stages'].append(entry)
                print(json.dumps({k: entry[k] for k in ('stage', 'returncode', 'seconds')}), flush=True)
                need(completed.returncode == 0, 'Stage failed; inspect ' + str(logfile))
        outputs = set()
        for stage in stages:
            for pattern in stage['outputs']:
                found = [p for p in (repo / SCOPE).glob(pattern) if p.is_file()]
                need(found, 'Nonempty declared output: ' + pattern)
                outputs.update(p.relative_to(repo).as_posix() for p in found)
        result['comparisons'] = compare_outputs(repo, outputs)
        need(len(outputs) == 59, 'Exactly the checkpoint\'s 59 declared artifacts')
        # Recheck every frozen input after execution; regenerated files live elsewhere.
        authenticate()
        result.update(status='PASS_FRESH_23_STAGE_CONDITIONAL_REPLAY',
                      ignored_timing_keys=sorted(TIMING),
                      environment_metadata_exceptions={name: ['environment/python', 'environment/platform']
                                                       for name in sorted(ENVIRONMENT_RECEIPTS)},
                      source_hash_substitution='Exact old-to-fresh hashes of the 59 regenerated artifacts only; no other fields are waived.',
                      exact_artifacts=sum(r['exact_bytes'] for r in result['comparisons']))
    except Exception as error:
        result.update(status='FAIL', error=repr(error))
        raise
    finally:
        result['runtime_seconds'] = time.monotonic() - started
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'stages': len(result['stages']),
                      'artifacts': len(result['comparisons']), 'exact_artifacts': result['exact_artifacts'],
                      'receipt': str(receipt)}, sort_keys=True))


if __name__ == '__main__':
    main()
