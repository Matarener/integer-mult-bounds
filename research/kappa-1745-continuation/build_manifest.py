#!/usr/bin/env python3
"""Byte-exact closure for the corrected 0.001745 continuation package.

Prior manifests are authenticated as source inventories, not as assertions
that their mathematical claims remain valid. All prior bytes stay frozen.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = 'kappa-1745-corrected-continuation-manifest-v1'
EXCLUDED = {'MANIFEST.json', 'VALIDATION.json'}
PRIOR = ('kappa-adaptive-continuation', 'kappa-next-regime')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def relative_name(name):
    p = Path(name)
    need(isinstance(name, str) and name and not p.is_absolute() and '..' not in p.parts and p.as_posix() == name,
         'normalized relative source name: '+repr(name))
    return p


def digest(path):
    need(path.is_file() and not path.is_symlink(), 'regular source: '+str(path))
    h = sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024*1024), b''):
            h.update(data)
    return {'bytes': path.stat().st_size, 'sha256': h.hexdigest()}


def read(path):
    return json.loads(path.read_text())


def tree_files(path):
    out = []
    for p in path.rglob('*'):
        need(not p.is_symlink(), 'source symlink is outside the replay contract')
        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
            out.append(p)
    return sorted(out)


def dependency_inventory():
    out = {}
    for name in PRIOR:
        base = ROOT/'research'/name
        manifest = read(base/'MANIFEST.json')
        for directory, rows in ((base, manifest['files']), (ROOT, manifest['repository_dependencies'])):
            for filename, expected in rows.items():
                p = directory/relative_name(filename)
                current = digest(p)
                need(current == expected, 'frozen predecessor source changed: '+str(p.relative_to(ROOT)))
                out[p.relative_to(ROOT).as_posix()] = current
        for filename in ('MANIFEST.json', 'VALIDATION.json'):
            if (base/filename).exists():
                p = base/filename
                out[p.relative_to(ROOT).as_posix()] = digest(p)
    # The complete predecessor closures already include the native caller,
    # exact moment engines, word checkers, controller and receiver inputs.
    # Retain repository guidance as context for a portable continuation.
    for filename in ('AGENTS.md', 'CONTRIBUTING.md', 'autoresearch.md', 'LICENSE',
                     'certificates/selected-result.json',
                     'docs/research/bottleneck-brief.md',
                     'docs/research/research-glossary.md',
                     'docs/research/research-family-status.md',
                     'docs/research/research-package-guide.md'):
        p = ROOT/filename
        if p.is_file():
            out[filename] = digest(p)
    # The new entrance proof has one additional archived extractor dependency
    # beyond the complete predecessor closures. Check the whole review list,
    # rather than relying on a manually maintained one-file exception.
    for row in read(HERE/'bit-geometry/REPLAY-INPUTS.json')['input_files']:
        p = ROOT/relative_name(row['path'])
        current = digest(p)
        need(current == {'bytes': row['bytes'], 'sha256': row['sha256']},
             'independent review replay source pin: '+row['path'])
        if not p.is_relative_to(HERE):
            out[row['path']] = current
    need(all(not (ROOT/name).is_relative_to(HERE) for name in out), 'disjoint scope and dependencies')
    return dict(sorted(out.items()))


def inventory():
    return {
        'schema': SCHEMA,
        'scope': HERE.relative_to(ROOT).as_posix(),
        'files': {p.relative_to(HERE).as_posix(): digest(p) for p in tree_files(HERE)
                  if p.relative_to(HERE).as_posix() not in EXCLUDED},
        'repository_dependencies': dependency_inventory(),
        'excluded_scope_paths': sorted(EXCLUDED),
        'python_requirement': 'Python 3.11 or later, assertions enabled, -B recommended. Core certificate checks use the standard library. Optional discovery searches use NumPy/SciPy.',
        'scope_note': 'A complete local evidence and replay inventory. Includes an explicit correction of the previous high complex claim; source authentication does not endorse a historical claim.',
    }


def check(path=HERE/'MANIFEST.json'):
    expected = read(path)
    need(expected.get('schema') == SCHEMA, 'known manifest schema')
    observed = inventory()
    if expected != observed:
        for key in ('files', 'repository_dependencies'):
            a, b = expected.get(key, {}), observed[key]
            missing = sorted(set(a)-set(b))
            extra = sorted(set(b)-set(a))
            changed = sorted(k for k in set(a)&set(b) if a[k] != b[k])
            if missing or extra or changed:
                raise ValueError(key+': '+json.dumps({'missing': missing[:10], 'extra': extra[:10], 'changed': changed[:10]}))
        raise ValueError('manifest metadata differs')
    return {'manifest_sha256': digest(path)['sha256'], 'scope_files': len(observed['files']),
            'repository_dependencies': len(observed['repository_dependencies'])}


if __name__ == '__main__':
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--replace', action='store_true', help='producer-only update after release files change')
    args = ap.parse_args()
    path = HERE/'MANIFEST.json'
    if not args.check:
        need(args.replace or not path.exists(), 'fresh manifest unless producer explicitly requests replacement')
        path.write_text(json.dumps(inventory(), indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': 'PASS_CORRECTED_CONTINUATION_MANIFEST', **check()}, sort_keys=True))
