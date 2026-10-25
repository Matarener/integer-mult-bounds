#!/usr/bin/env python3
"""Bounded source checks. Lean is explicit and opt-in; no GL64 enumeration."""
import argparse
from hashlib import sha1, sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = 'research/selected-compiler-visitation-audit'
SCIENTIFIC_SHA256 = 'c1bc50f54937cd3b2efae61bb5b655b55859b3ed7ddcf1a2e9bbd8682fc88f3d'
BRIDGE_SHA256 = 'cb7ce5a50357fe01d4e9bf0a6c65d8767e431d3124d3e14d06e90f0bd46c38fa'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def regular(root, name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name,
         'canonical relative POSIX path required')
    pure = PurePosixPath(name)
    need(not pure.is_absolute() and str(pure) == name
         and all(part not in ('', '.', '..') for part in name.split('/')),
         'canonical relative POSIX path required')
    path = root / name
    need(path.is_file(), 'missing input: ' + name)
    need(not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(root)),
         'symlink input: ' + name)
    need(path.resolve().is_relative_to(root.resolve()), 'input outside root: ' + name)
    return path


def authenticate(root, sources, replay):
    need(sources.get('schema_version') == replay.get('schema_version') == 1, 'manifest schema')
    need(re.fullmatch('[0-9a-f]{40}', sources.get('base_commit', '')) is not None, 'base commit syntax')
    seen, live = set(), set()
    for row in sources['files']:
        name = row['path']
        need(name not in seen, 'duplicate source pin')
        seen.add(name)
        need(row['usage'] in ('input', 'provenance'), 'source usage')
        if row['usage'] == 'provenance':
            continue  # Git-backed provenance is checked by research_package.py and publication preflight.
        raw = regular(root, name).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch: ' + name)
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'source Git-blob mismatch: ' + name)
        live.add(name)
    need(replay['inputs'] == sorted(live), 'exact live-pin / replay-input inventory')
    return live


def inputs(root=ROOT):
    sources, replay = read_json(HERE/'SOURCES.json'), read_json(HERE/'VERIFY.json')
    live = authenticate(root, sources, replay)
    independent = read_json(HERE/'AUTHENTICATION.json')
    required = (set(independent['package_sha256']) | {r['path'] for r in independent['live_inputs']}
                | set(independent['lifetime_source_sha256']))
    need(live == required and len(live) == 152, 'complete predecessor and source inventory')
    bridge = HERE/'lean/CompilerAudit/SourceBridge.lean'
    need(sha256(bridge.read_bytes()).hexdigest() == BRIDGE_SHA256, 'verified bridge bytes changed')
    return live


def export_integrity(root=ROOT):
    # The shared exporter validates tar member modes too; an extracted Windows
    # filesystem need not preserve POSIX mode bits. Here we check payload bytes.
    manifest_path = root/'.research-export.json'
    if not manifest_path.exists():
        need((root/'.git').exists(), 'Git-free replay requires .research-export.json')
        return None
    manifest = read_json(manifest_path)
    need(manifest.get('format') == 'research-package-export-v1', 'export schema')
    need(manifest.get('package') == 'research/selected-compiler-source-bridge', 'export package')
    need(re.fullmatch('[0-9a-f]{40,64}', manifest.get('commit', '')) is not None, 'export commit label')
    expected = {}
    for row in manifest['files']:
        name = row['path']
        need(name not in expected and name != '.research-export.json', 'duplicate/reserved export path')
        need(row['mode'] in (0o644, 0o755), 'declared export mode')
        raw = regular(root, name).read_bytes()
        need(len(raw) == row['size'] and sha256(raw).hexdigest() == row['sha256'], 'export changed: ' + name)
        expected[name] = row
    observed = {p.relative_to(root).as_posix() for p in root.rglob('*')
                if p.is_file() and p != manifest_path}
    need(set(expected) == observed, 'complete Git-free export inventory')
    return len(expected)


def package_hashes():
    return {p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file()}


def fresh_output(value):
    out = value.resolve()
    need(value.is_absolute() and not out.exists() and not out.is_relative_to(ROOT),
         'fresh absolute output outside source tree required')
    need(not any((p/name).exists() for p in out.parents
                 for name in ('LOCAL-MANIFEST.json', 'EXPORT-MANIFEST.json', '.research-export.json', '.git')),
         'protected output ancestor')
    out.mkdir(parents=True, exist_ok=False)
    return out


def run(output=None):
    sys.dont_write_bytecode = True
    export_count = export_integrity()
    live = inputs()
    owned = package_hashes()
    records, results = [], {}
    # Each child gets a new, never-populated bytecode namespace. -B alone is not enough.
    cache = Path(tempfile.mkdtemp(prefix='source-bridge-bytecode-')).resolve()
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'PYTHONPYCACHEPREFIX'):
        env.pop(key, None)
    flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])

    def check(label, script, args=(), as_json=True, timeout=90):
        cmd = [sys.executable, *flags, '-X', 'pycache_prefix='+str(cache), str(script), *map(str,args)]
        start = time.monotonic()
        try:
            result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, timeout=timeout)
            code, stdout, stderr, timed = result.returncode, result.stdout, result.stderr, False
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr, timed = None, exc.stdout or b'', exc.stderr or b'', True
        record = dict(label=label, returncode=code, timed_out=timed,
                      elapsed_seconds=round(time.monotonic()-start, 6),
                      script_sha256=sha256(script.read_bytes()).hexdigest())
        records.append(record)
        if output is not None:
            (output/(label+'.stdout')).write_bytes(stdout)
            (output/(label+'.stderr')).write_bytes(stderr)
            (output/'RUNS.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
        need(not timed and code == 0,
             label+' failed: '+(stdout+stderr).decode('utf-8',errors='replace')[-6000:])
        value = json.loads(stdout) if as_json else stdout.decode('utf-8').strip()
        results[label] = value
        return value

    try:
        check('replay-controls', HERE/'test_replay.py', as_json=False)
        check('census-controls', HERE/'test_independent_census.py', as_json=False)
        check('capacity-controls', HERE/'test_capacity.py', as_json=False)
        baseline = check('predecessor', ROOT/AUDIT/'verify.py')
        need(sha256(canonical(baseline).encode()).hexdigest() == SCIENTIFIC_SHA256,
             'predecessor scientific receipt changed')
        check('source-certificate', ROOT/AUDIT/'lean/extract_census.py', ['--check'], as_json=False)
        census = check('independent-census', HERE/'independent_census.py', ['--source','--root',ROOT])
        need(census['status'] == 'PASS', 'independent census status')
        lifetime = check('original-lifetime', HERE/'independent_lifetime.py', ['--original','--root',ROOT])
        need(lifetime['status'] == 'passed', 'original lifetime status')
        check('synthetic-lifetime', HERE/'independent_lifetime.py', ['--synthetic','--root',ROOT])
        check('capacity', HERE/'capacity.py')
        need(inputs() == live and package_hashes() == owned, 'source/package changed during replay')
        need(export_integrity() == export_count, 'export changed during replay')
    finally:
        # Only an empty, freshly created cache directory is removed, never a source tree.
        cache.rmdir()
    # Detailed child stdout/stderr are retained in explicit --output runs.
    # Timings/interpreter details are not a cross-platform scientific digest.
    results['predecessor'] = {'scientific_sha256': SCIENTIFIC_SHA256,
                              'live_pins': baseline['live_pins']}
    return dict(schema='compiler-source-bridge-checks-v1', status='PASS_BOUNDED_SOURCE_CHECKS',
                live_inputs=len(live), bridge_source_sha256=BRIDGE_SHA256,
                optimization=sys.flags.optimize, python=sys.version, records=records, results=results,
                lean_executed=False,
                scope='Bounded source/fixture/arithmetic checks only; no GL64 enumeration, Python semantics proof, native/stock or full multiplication theorem.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh external directory for diagnostics/receipt')
    parser.add_argument('--integrity-only', action='store_true')
    args = parser.parse_args()
    if args.integrity_only:
        result = dict(status='PASS_INPUT_AND_EXPORT_INTEGRITY_ONLY',live_inputs=len(inputs()),
                      export_files=export_integrity())
    else:
        output = fresh_output(args.output) if args.output is not None else None
        result = run(output)
        if output is not None:
            (output/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
