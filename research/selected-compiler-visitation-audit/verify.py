#!/usr/bin/env python3
"""Read-only, stdlib replay of one bounded public compiler-population audit."""
import argparse
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def regular(root, name):
    need(type(name) is str and name and '\\' not in name, 'canonical relative POSIX path')
    p = PurePosixPath(name)
    need(not p.is_absolute() and str(p) == name and not any(x in ('', '.', '..') for x in name.split('/'))
         and ':' not in name, 'canonical relative POSIX path')
    path = root / name
    need(path.is_file(), 'missing input: ' + name)
    need(not any(q.is_symlink() for q in (path, *path.parents) if q.is_relative_to(root)), 'symlink input: ' + name)
    need(path.resolve().is_relative_to(root.resolve()), 'input outside root')
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
            continue  # Git-backed historical provenance belongs to research_package.py.
        live.add(name)
        data = regular(root, name).read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'source SHA256 mismatch: ' + name)
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
             'source Git-blob mismatch: ' + name)
    need(replay['inputs'] == sorted(live), 'exact live-pin / replay-input inventory')
    return live


def export_integrity(root):
    path = root / 'EXPORT-MANIFEST.json'
    if not path.exists():
        return
    manifest = read_json(path)
    need(manifest.get('schema') == 'compiler-visitation-export-v1', 'export schema')
    files = manifest['files']
    observed = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p != path}
    need(set(files) == observed, 'complete Git-free export inventory')
    for name, digest in files.items():
        need(sha256(regular(root, name).read_bytes()).hexdigest() == digest, 'export changed: ' + name)


def input_controls(root, sources, replay):
    cases = []
    index = next(i for i, row in enumerate(sources['files']) if row['usage'] == 'input')
    for field, value in [('sha256', '0'*64), ('git_blob', '0'*40), ('path', '../outside'),
                         ('path', '/outside'), ('usage', 'unknown')]:
        changed = deepcopy(sources)
        changed['files'][index][field] = value
        cases.append((changed, replay))
    changed = deepcopy(sources)
    changed['files'].append(deepcopy(changed['files'][index]))
    cases.append((changed, replay))
    changed = deepcopy(sources)
    changed['files'].pop(index)
    cases.append((changed, replay))
    changed = deepcopy(replay)
    changed['inputs'] = changed['inputs'][1:]
    cases.append((sources, changed))
    for changed_sources, changed_replay in cases:
        try:
            authenticate(root, changed_sources, changed_replay)
        except ValueError:
            continue
        raise ValueError('input corruption control was accepted')
    return len(cases)


def run(sources, replay):
    live = authenticate(ROOT, sources, replay)
    sys.path.insert(0, str(HERE))
    import accounting
    import test_accounting
    import source_audit
    controls = input_controls(ROOT, sources, replay)
    arithmetic = test_accounting.run()
    groups, source = source_audit.run(ROOT)
    concrete = [accounting.Group(g['kind'], g['order'], tuple(g['request_ids']), g['common']) for g in groups]
    selected = accounting.visit_invoice(concrete, source['census']['replicas'], 1)
    # Coefficients at N=1; the proof is linear in the symbolic LOW size N.
    need(selected['source_visits'] == 904896 and selected['distinct_keys'] == 28278, 'selected symbolic coefficients')
    package_prefix = HERE.relative_to(ROOT).as_posix() + '/'
    need(all(name in live or name.startswith(package_prefix) for name in source['loaded_sources'].values()),
         'undeclared repository module imported: ' + repr(sorted(name for name in source['loaded_sources'].values() if name not in live and not name.startswith(package_prefix))))
    need(authenticate(ROOT, sources, replay) == live, 'input stability after replay')
    return dict(schema='public-compiler-visitation-v1', source=source, arithmetic=arithmetic,
                input_corruption_controls_rejected=controls, live_pins=len(live),
                selected_coefficients_at_N_one=selected,
                scope='successful mode-0 public compiler only; no complete GL64/native/stock/precision theorem')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--emit', action='store_true', help='print newly computed receipt instead of comparing EXPECTED.json')
    ap.add_argument('--integrity-only', action='store_true', help='verify live inputs/export only; no scientific replay')
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    # -B alone still reads stale .pyc. A fresh empty prefix also blocks those reads.
    cache = Path(tempfile.mkdtemp(prefix='compiler-visitation-bytecode-'))
    old_prefix = sys.pycache_prefix
    sys.pycache_prefix = str(cache)
    try:
        export_integrity(ROOT)
        sources, replay = read_json(HERE/'SOURCES.json'), read_json(HERE/'VERIFY.json')
        authenticate(ROOT, sources, replay)
        if args.integrity_only:
            print('PASS_INPUT_AND_EXPORT_INTEGRITY_ONLY')
            return
        result = run(sources, replay)
        if not args.emit:
            need(canonical(result) == canonical(read_json(HERE/'EXPECTED.json')), 'scientific receipt differs')
        export_integrity(ROOT)
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        sys.pycache_prefix = old_prefix
        cache.rmdir()  # fresh and empty: no recursive deletion


if __name__ == '__main__':
    main()
