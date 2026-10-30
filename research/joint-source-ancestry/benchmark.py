"""Time complete publication preflights; write temporary files only outside Git."""
import argparse
import hashlib
import json
import os
import platform
import pstats
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
FIXTURE = 'research/e8-d0-root-swaps'
sys.path.insert(0, str(ROOT / 'scripts'))
from research_package import git_source_env, require


def run(argv):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=60,
                            env=git_source_env(), check=True)
    return result.stdout


def baseline(directory, base):
    raw = run(['git', 'show', base + ':scripts/check_research_commit.py'])
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())['files']
    expected = next(row['sha256'] for row in pins
                    if row['path'] == 'scripts/check_research_commit.py')
    require(hashlib.sha256(raw).hexdigest() == expected, 'baseline source differs')
    source = directory / 'baseline-source.py'
    source.write_bytes(raw)
    wrapper = directory / 'baseline-cli.py'
    # Preserve the original CLI's ROOT and sibling imports while freezing only
    # the changed module. Both sides use the same current source-reader module.
    wrapper.write_text('import sys\nfrom pathlib import Path\n'
                       f'sys.path.insert(0, {str(ROOT / "scripts")!r})\n'
                       f'exec(compile(Path({str(source)!r}).read_bytes(), '
                       f'{str(ROOT / "scripts/check_research_commit.py")!r}, "exec"), '
                       f'{{"__name__": "__main__", "__file__": '
                       f'{str(ROOT / "scripts/check_research_commit.py")!r}}})\n')
    return wrapper, hashlib.sha256(raw).hexdigest()


def profile(directory, scripts, base):
    summaries = {}
    for side, script in scripts.items():
        destination = directory / (side + '.profile')
        run([sys.executable, '-B', '-m', 'cProfile', '-o', str(destination),
             str(script), '--package', FIXTURE, '--ref', base, '--check-source-history'])
        summaries[side] = {}
        for (filename, _, name), (calls, _, _, cumulative, _) in pstats.Stats(str(destination)).stats.items():
            selected = (((filename.endswith('check_research_commit.py')
                          or filename.endswith('preflight.py'))
                         and name in ('main', 'check', 'source_history', 'history_git'))
                        or (filename.endswith('subprocess.py') and name == 'run'))
            if selected:
                key = Path(filename).name + ':' + name
                summaries[side][key] = {'calls': calls, 'cumulative_seconds': cumulative}
    return summaries


def measure(directory, pairs, base):
    old, old_hash = baseline(directory, base)
    changed = PACKAGE / 'preflight.py'
    scripts = {'baseline': old, 'changed': changed}
    profiles = profile(directory, scripts, base)
    rows, expected = [], None
    for pair in range(pairs):
        order = ('baseline', 'changed') if pair % 2 == 0 else ('changed', 'baseline')
        for side in order:
            start = time.perf_counter()
            output = run([sys.executable, '-B', str(scripts[side]), '--package',
                          FIXTURE, '--ref', base, '--check-source-history'])
            elapsed = time.perf_counter() - start
            expected = output if expected is None else expected
            require(output == expected, 'complete preflight receipts differ')
            rows.append({'pair': pair, 'side': side, 'seconds': elapsed, 'returncode': 0})
    summary = {}
    for side in scripts:
        times = [row['seconds'] for row in rows if row['side'] == side]
        summary[side] = {'median_seconds': statistics.median(times),
                         'minimum_seconds': min(times), 'maximum_seconds': max(times)}
    return {'schema_version': 1, 'base_commit': base, 'fixture': FIXTURE,
            'pairs': pairs, 'samples': rows, 'summary': summary, 'failures': 0,
            'untimed_diagnostic_profiles': profiles,
            'receipt': json.loads(expected.decode().split(' ', 1)[1]),
            'receipt_sha256': hashlib.sha256(expected).hexdigest(),
            'baseline_source_sha256': old_hash,
            'changed_source_sha256': hashlib.sha256(changed.read_bytes()).hexdigest(),
            'shared_preflight_sha256': hashlib.sha256(
                (ROOT / 'scripts/check_research_commit.py').read_bytes()).hexdigest(),
            'shared_source_reader_sha256': hashlib.sha256(
                (ROOT / 'scripts/research_package.py').read_bytes()).hexdigest(),
            'python': sys.version, 'platform': platform.platform(),
            'logical_cpus': os.cpu_count(), 'load_average': os.getloadavg()
            if hasattr(os, 'getloadavg') else None,
            'git': run(['git', '--version']).decode().strip()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--pairs', type=int, default=7)
    args = parser.parse_args()
    require(5 <= args.pairs <= 20, 'use between five and twenty timing pairs')
    scratch = args.scratch.resolve()
    require(scratch.is_dir() and not scratch.is_relative_to(ROOT),
            'scratch must be an existing directory outside the checkout')
    base = json.loads((PACKAGE / 'SOURCES.json').read_text())['base_commit']
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        result = measure(Path(directory), args.pairs, base)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
