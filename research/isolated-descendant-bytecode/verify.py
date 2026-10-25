#!/usr/bin/env python3
"""Run one authenticated existing test across its ordinary Python child boundary.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
METHOD = 'test_real_cli_is_read_only_and_reports_no_pass_on_history_failure'

# Keep the original test body and child command unchanged. Plant the numeric
# disagreement only in that test's own temporary repository after publish().
FIXTURE = '''import importlib.util
import json
import os
from pathlib import Path
import py_compile
import sys
import unittest
import actual_history as history

class DescendantHistory(history.SourceHistoryTests):
 def publish(self, rows=(), base=None):
  head = super().publish(rows, base)
  source = self.root / 'scripts/research_package.py'
  if source.exists() and not hasattr(self, 'planted'):
   self.planted = True
   original = source.read_bytes()
   needle = b'len(fields) == 3 and'
   if original.count(needle) != 1: raise ValueError('numeric fixture source drift')
   stamp = source.stat().st_mtime_ns
   previous = sys.pycache_prefix
   try:
    sys.pycache_prefix = os.environ.get('STALE_PREFIX') or None
    cache = Path(importlib.util.cache_from_source(str(source.resolve())))
   finally:
    sys.pycache_prefix = previous
   mode = getattr(py_compile.PycInvalidationMode, os.environ['CACHE_MODE'])
   cache.parent.mkdir(parents=True, exist_ok=True)
   py_compile.compile(str(source), cfile=str(cache), doraise=True,
                      optimize=0, invalidation_mode=mode)
   if os.environ['FIXTURE_KIND'] != 'clean':
    source.write_bytes(original.replace(needle, b'len(fields) == 4 and'))
    os.utime(source, ns=(stamp, stamp))
   if os.environ['FIXTURE_KIND'] == 'source-only': cache.unlink()
   content, bytecode = source.read_bytes(), cache.read_bytes() if cache.exists() else None
   def observe():
    if source.read_bytes() != content or source.stat().st_mtime_ns != stamp:
     raise ValueError('source bytes or timestamp changed during test')
    if (cache.read_bytes() if cache.exists() else None) != bytecode:
     raise ValueError('preexisting cache changed during test')
    Path(os.environ['OBSERVATION']).write_text(json.dumps({
     'source_and_cache_unchanged': True,
     'current_parser_fields': 3 if os.environ['FIXTURE_KIND'] == 'clean' else 4,
     'cached_parser_fields': 3 if bytecode is not None else None}), encoding='utf-8')
   self.addCleanup(observe)
  return head

def load_tests(loader, tests, pattern):
 return unittest.TestSuite([DescendantHistory('METHOD')])
'''.replace("'METHOD'", repr(METHOD))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pinned_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))
    result = {}
    for row in manifest['files']:
        if row['path'].startswith(('scripts/', 'tests/')):
            spec = manifest['base_commit'] + ':' + row['path']
            content = subprocess.run(['git', 'show', spec], cwd=ROOT,
                                     capture_output=True, check=True, timeout=30).stdout
            require(sha256(content).hexdigest() == row['sha256'],
                    'pinned source SHA256 mismatch: ' + row['path'])
            blob = subprocess.run(['git', 'rev-parse', spec], cwd=ROOT,
                                  capture_output=True, check=True, timeout=30).stdout.strip().decode('ascii')
            require(blob == row['git_blob'], 'pinned Git blob mismatch: ' + row['path'])
            result[row['path']] = content
    return result


def exercise(sources, runner, mode, kind, expected, external=False):
    with tempfile.TemporaryDirectory(prefix='isolated-descendant-proof-') as temporary:
        root = Path(temporary)
        for name in ('scripts', 'tests', 'owned'):
            (root / name).mkdir()
        for name in ('check_research_commit.py', 'research_package.py'):
            (root / 'scripts' / name).write_bytes(sources['scripts/' + name])
        (root / 'scripts/run_isolated_tests.py').write_bytes(runner)
        (root / 'tests/actual_history.py').write_bytes(sources['tests/test_research_source_history.py'])
        (root / 'tests/test_descendant.py').write_text(FIXTURE, encoding='utf-8')
        observation = root / 'observation.json'
        env = os.environ.copy()
        for name in ('PYTHONPYCACHEPREFIX', 'PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME',
                     'STALE_PREFIX', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            env.pop(name, None)
        env.update(PYTHONDONTWRITEBYTECODE='1', CACHE_MODE=mode, FIXTURE_KIND=kind,
                   OBSERVATION=str(observation), TMPDIR=str(root / 'owned'),
                   TMP=str(root / 'owned'), TEMP=str(root / 'owned'))
        if external:
            env['PYTHONPYCACHEPREFIX'] = env['STALE_PREFIX'] = str(root / 'external')
        result = subprocess.run(
            [sys.executable, '-I', '-B', str(root / 'scripts/run_isolated_tests.py'),
             '--workers', '1', '--module-timeout', '20'], cwd=root, env=env,
            capture_output=True, timeout=30)
        require(result.returncode == expected, 'unexpected CLI verdict: ' + repr(result.stderr))
        require(METHOD.encode() in result.stderr and b'Ran 1 test' in result.stderr,
                'original test did not execute')
        if expected:
            require(b'AssertionError: 1 != 0' in result.stderr and
                    b'missing or non-blob Git source' in result.stderr,
                    'not the intended current-source numeric failure: ' + repr(result.stderr))
            require(b'PASS all' not in result.stdout, 'failed test reported success')
        else:
            require(b'PASS all 1 test modules' in result.stdout, 'missing completion summary')
        require(observation.is_file(), 'fixture cleanup/preservation observer did not run')
        observed = json.loads(observation.read_text(encoding='utf-8'))
        require(observed['source_and_cache_unchanged'], 'source/cache preservation failed')
        require(not any((root / 'owned').iterdir()), 'owned completion/cache directory survived')
        return {'verdict': 'fail' if expected else 'pass', **observed,
                'owned_directories_removed': True}


def verify():
    sources = pinned_sources()
    baseline = sources['scripts/run_isolated_tests.py']
    candidate = (ROOT / 'scripts/run_isolated_tests.py').read_bytes()
    cases = {}
    for mode in ('TIMESTAMP', 'UNCHECKED_HASH'):
        cases[mode] = {}
        for label, runner, fixed in (('baseline', baseline, False), ('candidate', candidate, True)):
            cases[mode][label] = {
                'clean': exercise(sources, runner, mode, 'clean', 0),
                'stale': exercise(sources, runner, mode, 'stale', int(fixed)),
                'source_only': exercise(sources, runner, mode, 'source-only', 1)}
    cases['inherited_external_prefix'] = {
        label: exercise(sources, runner, 'UNCHECKED_HASH', 'stale', int(fixed), external=True)
        for label, runner, fixed in (('baseline', baseline, False), ('candidate', candidate, True))}
    cases['checked_hash'] = {
        label: exercise(sources, runner, 'CHECKED_HASH', 'stale', 1)
        for label, runner in (('baseline', baseline), ('candidate', candidate))}
    return {'status': 'PASS_ISOLATED_DESCENDANT_BYTECODE', 'method': METHOD,
            'baseline_runner_sha256': sha256(baseline).hexdigest(),
            'cases': cases,
            'scope': 'Existing source-history test and ordinary environment-inheriting Python children; no -I/-E descendant guarantee or mathematical certificate bypass.'}


def main():
    result = verify()
    require(result == json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8')),
            'differential result differs from committed RESULT.json')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
