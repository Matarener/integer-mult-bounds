"""Check the complete receipt, source-bound measurements and rejection controls."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
import preflight as checker
from research_package import require


def main():
    evidence = json.loads((PACKAGE / 'BENCHMARK.json').read_text())
    source = PACKAGE / 'preflight.py'
    require(hashlib.sha256(source.read_bytes()).hexdigest()
            == evidence['changed_source_sha256'], 'measured implementation changed')
    samples = evidence['samples']
    require(evidence['failures'] == 0 and evidence['pairs'] >= 5,
            'measurement must include at least five successful pairs')
    require(len(samples) == 2 * evidence['pairs']
            and all(row['returncode'] == 0 for row in samples), 'incomplete measurements')
    actual = checker.check(ROOT, evidence['fixture'], evidence['base_commit'], True)
    require(actual == evidence['receipt'], 'complete publication receipt changed')
    require(actual['files'] == 14 and len(actual['source_history_commits']) == 5,
            'real fixture coverage changed')
    command = [sys.executable, '-W', 'error', '-B']
    if sys.flags.optimize:
        command.append('-O')
    subprocess.run([*command, str(PACKAGE / 'test_history.py'), '-v'],
                   cwd=ROOT, timeout=120, check=True)
    print('PASS_JOINT_SOURCE_ANCESTRY ' + json.dumps(
        {'fixture_files': actual['files'], 'source_commits': 5, 'tests': 18,
         'claim_type': 'scoped algorithmic equivalence and empirical timing'}, sort_keys=True))


if __name__ == '__main__':
    main()
