"""Opt-in publication preflight with bounded joint source ancestry.

The byte/mode preflight retains ywz65's implementation. Source-history policy
follows Nick Petalas's existing preflight and the retained immutable-reader
contributors. New batching and adapter by Nick Petalas. Apache-2.0.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_research_commit import check as byte_check
from check_research_commit import MAX_SOURCE_COMMITS, MAX_SOURCE_METADATA_BYTES, MAX_SOURCE_ROWS
from research_package import canonical_relative_path, git_source_env, require, source_pin


def history_git(root, *args, input=None):
    env = git_source_env()
    env['GIT_GRAFT_FILE'] = os.devnull
    env.pop('GIT_SHALLOW_FILE', None)
    return subprocess.run(['git', '--no-replace-objects', *args], cwd=root, env=env, input=input,
                          capture_output=True, check=False, timeout=30)


def joint_ancestors(root, pins, commit):
    """Check exact commit types and share one walk across bounded source pins.

    A nonempty difference takes the original per-pin diagnostic path. Errors
    and malformed batch responses fail closed, rather than becoming a hit.
    """
    payload = ''.join(pin + '\n' for pin in pins).encode('ascii')
    types = history_git(root, 'cat-file', '--batch-check=%(objectname) %(objecttype)',
                        input=payload)
    require(types.returncode == 0, 'Git source commit check failed: '
            + types.stderr.decode('utf-8', errors='replace').strip())
    rows = types.stdout.splitlines()
    require(len(rows) == len(pins), 'incomplete Git source commit response')
    for pin, row in zip(pins, rows):
        if row != (pin + ' commit').encode('ascii'):
            require(row in [(pin + ' ' + kind).encode('ascii')
                            for kind in ('missing', 'blob', 'tree', 'tag')],
                    'invalid Git source commit response')
            return False
    difference = history_git(root, 'rev-list', '--max-count=1', *pins, '--not', commit)
    require(difference.returncode == 0, 'Git ancestry check failed: '
            + difference.stderr.decode('utf-8', errors='replace').strip())
    require(not difference.stdout or re.fullmatch(rb'[0-9a-f]{40,64}\n', difference.stdout),
            'invalid Git ancestry response')
    return not difference.stdout


def publication_sources(root, package, commit):
    """Read bounded, immutable metadata without local replacements or grafts."""
    spec = commit + ':' + package + '/SOURCES.json'
    size = history_git(root, 'cat-file', '-s', spec)
    require(size.returncode == 0 and size.stdout.strip().isdigit(), 'missing publication SOURCES.json')
    require(int(size.stdout) <= MAX_SOURCE_METADATA_BYTES, 'source metadata byte limit exceeded')
    payload = history_git(root, 'cat-file', 'blob', spec)
    require(payload.returncode == 0 and len(payload.stdout) == int(size.stdout),
            'incomplete publication SOURCES.json')
    return json.loads(payload.stdout)


def source_history(root, package, commit):
    """Check committed pins against raw publication ancestry, not local refs.

    This is declared history availability, not full SOURCES.json validation
    or discovery of imports, archive references or runtime dependencies.
    """
    sources = publication_sources(root, package, commit)
    require(isinstance(sources, dict), 'SOURCES.json must be an object')
    base = sources.get('base_commit')
    require(isinstance(base, str) and re.fullmatch(r'[0-9a-f]{40,64}', base),
            'SOURCES.json base_commit must be an exact commit ID')
    rows = sources.get('files')
    require(isinstance(rows, list), 'SOURCES.json files must be a list')
    require(len(rows) <= MAX_SOURCE_ROWS, 'source row limit exceeded')
    commits = {base}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('path'), str),
                'SOURCES.json files rows need a string path')
        canonical_relative_path(row['path'])
        commits.add(source_pin(row, base).split(':', 1)[0])
    require(len(commits) <= MAX_SOURCE_COMMITS, 'source commit limit exceeded')
    shallow = history_git(root, 'rev-parse', '--is-shallow-repository')
    require(shallow.returncode == 0, 'cannot inspect Git history')
    require(shallow.stdout.strip() == b'false', 'source-history check requires full Git history')
    pins = sorted(commits)
    if len(pins) > 1 and joint_ancestors(root, pins, commit):
        return pins
    for pin in pins:
        resolved = history_git(root, 'rev-parse', '--verify', '--end-of-options', pin + '^{commit}')
        require(resolved.returncode == 0 and resolved.stdout.strip() == pin.encode('ascii'),
                'unavailable source commit: ' + pin)
        ancestor = history_git(root, 'merge-base', '--is-ancestor', pin, commit)
        require(ancestor.returncode in (0, 1),
                'Git ancestry check failed: ' + ancestor.stderr.decode('utf-8', errors='replace').strip())
        require(ancestor.returncode == 0,
                'source pin is not an ancestor of publication ' + commit + ': ' + pin
                + '; a separate cached branch/object is not publication history')
    return pins



def check(root, package, ref='HEAD', check_source_history=False, check_modes=False):
    result = byte_check(root, package, ref, check_source_history=False, check_modes=check_modes)
    if check_source_history:
        result['source_history_commits'] = source_history(root, package, result['commit'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True)
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--check-source-history', action='store_true')
    parser.add_argument('--check-modes', action='store_true')
    args = parser.parse_args()
    try:
        result = check(ROOT, args.package, args.ref, args.check_source_history, args.check_modes)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc) + '\n')
    print('PASS_RESEARCH_COMMIT_BYTES ' + json.dumps(result))


if __name__ == '__main__':
    main()
