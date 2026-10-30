#!/usr/bin/env python3
"""Freeze the portable research closure without generated runtime clones.

The complete previous portable closure is retained and authenticated. New
sources, exact receipts and collected current release evidence are added.
No prior file is rewritten. Apache-2.0. Substantial OpenAI assistance.
"""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PRIOR = REPO / 'research/kappa-1745-continuation'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def record(p):
    need(p.is_file() and not p.is_symlink(), 'Regular authentic input ' + str(p))
    return dict(bytes=p.stat().st_size, sha256=sha(p))


def main():
    prior = json.loads((PRIOR / 'MANIFEST.json').read_text())
    dependencies = {}
    for root, key in [(PRIOR, 'files'), (REPO, 'repository_dependencies')]:
        for rel, expected in prior[key].items():
            p = root / rel
            actual = record(p)
            need(actual == expected, 'Every previous portable source unchanged: ' + str(p))
            dependencies[p.relative_to(REPO).as_posix()] = actual
    for p in [PRIOR / 'MANIFEST.json', PRIOR / 'VALIDATION.json',
              REPO / 'research/shared-phase-repair-rank/vendor/PR3220-PROOF.md']:
        dependencies[p.relative_to(REPO).as_posix()] = record(p)

    files = {}
    excluded_directories = {'release-work', '__pycache__', 'python-deps',
                            'replay-output', 'full-replay-output', 'native-replay-output'}
    for base, dirs, names in os.walk(HERE):
        dirs[:] = sorted(d for d in dirs if d not in excluded_directories)
        for name in sorted(names):
            p = Path(base) / name
            rel = p.relative_to(HERE).as_posix()
            if p.suffix == '.pyc' or rel in ('MANIFEST.json', 'VALIDATION.json'):
                continue
            files[rel] = record(p)
    for required in ['README.md', 'TASK.json', 'CLAIM.json', 'replay.py',
                     'evidence/full-release/RESULT.json',
                     'evidence/full-release/FILE-INVENTORY.json']:
        need(required in files, 'Completed artifact required before freezing: ' + required)
    readme = (HERE / 'README.md').read_text()
    need('RELEASE_PENDING' not in readme and 'REPORT_TODO' not in readme,
         'Report must describe the completed outcome')
    claim = json.loads((HERE / 'CLAIM.json').read_text())
    need(claim['status'] == 'PASS_NEW_OPERATOR_GUARDED_CONDITIONAL_KAPPA_INCREASE',
         'Fresh conjunctive claim required')
    manifest = dict(
        schema_version=1,
        status='FROZEN_OPERATOR_REPAIR_PORTABLE_INPUTS',
        files=dict(sorted(files.items())),
        repository_dependencies=dict(sorted(dependencies.items())),
        prior_manifest_sha256=sha(PRIOR / 'MANIFEST.json'),
        current_claim_sha256=sha(HERE / 'CLAIM.json'),
        exclusions=sorted(excluded_directories),
        scope='Authenticates bytes, not every historical claim. The current claim is emitted only by build_claim.py after operator, native, complete invoice and outer admission agree. Large temporary runtime clones are inventoried in evidence/full-release/FILE-INVENTORY.json and reproduced by replay.py --full.',
    )
    (HERE / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(manifest['status'], len(files), 'current files,', len(dependencies), 'retained dependencies')


if __name__ == '__main__':
    main()
