#!/usr/bin/env python3
"""Source-bound selected-census exporter/checker for the Lean data module.

Stdlib only.  Runs the ORIGINAL v2 activation and selected_census() (never the
full selected LOW loop, tiny trace or factory) in a fresh source namespace,
then emits or checks a compact interval certificate plus generated Lean DATA.
This is a Python extraction check, not a verified parser or a Lean proof.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
CERT = HERE / 'SelectedCensus.json'
LEAN = HERE / 'CompilerAudit' / 'SelectedData.lean'
BOUND = ('SOURCES.json', 'VERIFY.json', 'EXPECTED.json', 'source_audit.py', 'verify.py')
SCHEMA = 'compiler-audit-selected-census-v1'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def seq_sha(ids):
    return sha256(json.dumps(list(ids), separators=(',', ':')).encode()).hexdigest()


def census():
    """Authenticate live pins, run original selected_census, derive intervals."""
    sys.path.insert(0, str(PACKAGE))
    import verify
    need(verify.ROOT == ROOT and verify.HERE == PACKAGE, 'package/root layout')
    verify.export_integrity(ROOT)
    sources, replay = verify.read_json(PACKAGE/'SOURCES.json'), verify.read_json(PACKAGE/'VERIFY.json')
    expected = verify.read_json(PACKAGE/'EXPECTED.json')
    bound = {name: sha256((PACKAGE/name).read_bytes()).hexdigest() for name in BOUND}
    live = verify.authenticate(ROOT, sources, replay)
    import source_audit
    modules = source_audit.activate(ROOT)
    groups, summary, old = source_audit.selected_census(modules)
    # Every repository module actually loaded must be a live pin or this package.
    prefix = PACKAGE.relative_to(ROOT).as_posix() + '/'
    for name, module in list(sys.modules.items()) + [('catalogue.old', old)]:
        path = getattr(module, '__file__', None)
        if path and Path(path).resolve().is_relative_to(ROOT.resolve()):
            rel = Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
            need(rel in live or rel.startswith(prefix), 'undeclared repository module: ' + rel)
    need(summary == expected['source']['census'], 'fresh census differs from EXPECTED.json')
    coeff = expected['selected_coefficients_at_N_one']
    need(summary['group_sizes'] == coeff['group_sizes'] and coeff['requests'] == summary['requests'], 'coefficient sizes')
    R, rho = summary['requests'], summary['replicas']
    need(rho == 32 and R == 28278 and len(groups) == 19, 'rho=32, R=28278, 19 groups')
    rows, empties = [], 0
    for index, g in enumerate(groups):
        ids = g['request_ids']
        need(type(g['common']) is bool and g['order'] in ('low-major', 'id-major'), 'group fields')
        need(g['common'] == (g['order'] == 'low-major') == (g['kind'] == 'local_cover_sweep'), 'common/order/kind')
        start = ids[0] if ids else R  # canonical empty interval
        empties += not ids
        need(all(type(i) is int for i in ids) and ids == list(range(start, start + len(ids))),
             'group %d is not an increasing integer interval' % index)
        digest = seq_sha(ids)
        need(digest == summary['group_sequence_sha256'][index] == seq_sha(range(start, start + len(ids))),
             'sequence SHA')
        rows.append(dict(index=index, schedule_index=g['schedule_index'], kind=g['kind'], order=g['order'],
                         common=g['common'], low_major=g['order'] == 'low-major', start=start,
                         count=len(ids), sequence_sha256=digest))
    nonempty = sorted((r['start'], r['count']) for r in rows if r['count'])
    cursor = 0
    for start, count in nonempty:
        need(start == cursor, 'interval partition gap/overlap at %d' % cursor)
        cursor += count
    need(cursor == R and sum(r['count'] for r in rows) == R, 'full request-ID partition of range(R)')
    need([r['schedule_index'] for r in rows] == sorted({r['schedule_index'] for r in rows}), 'schedule order')
    need(verify.authenticate(ROOT, sources, replay) == live, 'input stability after extraction')
    need(bound == {n: sha256((PACKAGE/n).read_bytes()).hexdigest() for n in BOUND}, 'package stability')
    order_contiguous = [(r['start'], r['count']) for r in rows if r['count']] == nonempty
    return dict(schema=SCHEMA, base_commit=sources['base_commit'], live_pins=len(live),
                package_sha256=bound, replica_count=rho, request_count=R, kinds=summary['kinds'],
                empty_groups=empties, empty_canonical_start=R, schedule_order_contiguous=order_contiguous,
                interval_tuple='(start, count, common, lowMajor)', groups=rows,
                scope='Python source extraction/check only; Lean receives DATA, proofs are separate')


def render_json(cert):
    return (json.dumps(cert, indent=2, sort_keys=True) + '\n').encode()


def render_lean(cert):
    b = lambda x: 'true' if x else 'false'
    tup = ',\n'.join('  (%d, %d, %s, %s)' % (r['start'], r['count'], b(r['common']), b(r['low_major']))
                     for r in cert['groups'])
    strs = lambda xs: ',\n'.join('  "%s"' % x for x in xs)
    lines = [
        '/-!',
        'GENERATED by research/selected-compiler-visitation-audit/lean/extract_census.py.',
        'DATA ONLY: no theorems, no axioms. Do not edit by hand; rerun --check.',
        'Base commit %s; SOURCES.json sha256 %s.' % (cert['base_commit'], cert['package_sha256']['SOURCES.json']),
        'Tuple meaning: (start, count, common, lowMajor), selected groups in schedule order.',
        'An empty group is canonically encoded with start = requestCount.',
        '-/',
        '',
        'namespace CompilerAudit.SelectedData',
        '',
        'def replicaCount : Nat := %d' % cert['replica_count'],
        '',
        'def requestCount : Nat := %d' % cert['request_count'],
        '',
        'def intervals : List (Nat × Nat × Bool × Bool) := [',
        tup,
        ']',
        '',
        'def scheduleIndices : List Nat := [%s]' % ', '.join(str(r['schedule_index']) for r in cert['groups']),
        '',
        'def kinds : List String := [',
        strs(r['kind'] for r in cert['groups']),
        ']',
        '',
        'def sequenceSha256 : List String := [',
        strs(r['sequence_sha256'] for r in cert['groups']),
        ']',
        '',
        'end CompilerAudit.SelectedData',
        '',
    ]
    return '\n'.join(lines).encode()


FROZEN_MARKERS = ('LOCAL-MANIFEST.json', 'EXPORT-MANIFEST.json', '.git')


def fresh_external(path):
    need(Path(path).is_absolute(), 'emit destination must be an explicit absolute path: %s' % path)
    path = Path(path).resolve()
    need(not path.is_relative_to(ROOT.resolve()), 'emit destination must be outside ROOT: %s' % path)
    for ancestor in path.parents:
        for marker in FROZEN_MARKERS:
            need(not (ancestor / marker).exists() and not (ancestor / marker).is_symlink(),
                 'emit destination beneath frozen package/checkout (%s): %s' % (ancestor / marker, path))
    need(not path.exists() and not path.is_symlink(), 'emit destination must be fresh: %s' % path)
    need(path.parent.is_dir(), 'emit parent directory must exist: %s' % path.parent)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='default: compare fresh census to committed bytes')
    mode.add_argument('--emit', action='store_true', help='write to FRESH paths outside ROOT')
    ap.add_argument('--json', help='certificate path (emit: required; check: default lean/SelectedCensus.json)')
    ap.add_argument('--lean', help='Lean path (emit: required; check: default lean/CompilerAudit/SelectedData.lean)')
    args = ap.parse_args()
    if args.emit:
        need(args.json and args.lean, '--emit requires --json and --lean')
        out_json, out_lean = fresh_external(args.json), fresh_external(args.lean)
        need(out_json != out_lean, 'distinct emit destinations')
    sys.dont_write_bytecode = True
    cache = Path(tempfile.mkdtemp(prefix='compiler-audit-census-bytecode-'))
    old_prefix, sys.pycache_prefix = sys.pycache_prefix, str(cache)
    try:
        cert = census()
    finally:
        sys.pycache_prefix = old_prefix
        cache.rmdir()  # fresh and empty: no recursive deletion
    data, lean = render_json(cert), render_lean(cert)
    need(render_lean(json.loads(data)) == lean, 'JSON certificate does not regenerate Lean bytes')
    if args.emit:
        for path, payload in ((out_json, data), (out_lean, lean)):
            fresh_external(path)
            with open(path, 'xb') as handle:
                handle.write(payload)
        print('EMITTED', out_json, out_lean)
        return
    cpath, lpath = Path(args.json or CERT), Path(args.lean or LEAN)
    need(cpath.read_bytes() == data, 'certificate differs from fresh source census: %s' % cpath)
    need(lpath.read_bytes() == lean, 'generated Lean bytes differ: %s' % lpath)
    print('PASS_SELECTED_CENSUS_CERTIFICATE groups=%d requests=%d replicas=%d'
          % (len(cert['groups']), cert['request_count'], cert['replica_count']))


if __name__ == '__main__':
    main()