#!/usr/bin/env python3
"""Fresh, source-authenticated P112 scatter replay; standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(repo):
    manifest = json.loads((HERE / 'ARTIFACTS.json').read_text())
    for name, expected in manifest.items():
        need(digest(HERE / name) == expected, 'package source changed: ' + name)
    pins = json.loads((HERE / 'SCATTER-SOURCES.json').read_text())
    for pin in pins['files']:
        path = (repo if pin['root'] == 'repo' else HERE) / pin['path']
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'],
             'source SHA256: ' + pin['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'original Git blob: ' + pin['path'])
    return manifest


def run(repo, out):
    started = time.monotonic()
    before = authenticate(repo)
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    # Each child gets an empty bytecode namespace. The candidate also compiles
    # the exact authenticated geometry/basis source instead of loading .pyc.
    for script, result in [('check_direction.py', 'CUT-REVIEW.json'),
                           ('verify_scatter.py', 'SCATTER-RESULT.json')]:
        cache = out / (script.removesuffix('.py') + '-pycache')
        cache.mkdir()
        argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(cache),
                str(HERE / script), '--repo', str(repo), '--output', str(out / result)]
        with (out / (script + '.log')).open('w') as log:
            subprocess.run(argv, check=True, cwd=repo, env=env,
                           stdout=log, stderr=subprocess.STDOUT, timeout=260)
    direction = json.loads((out / 'CUT-REVIEW.json').read_text())
    need(direction['status'] == 'PASS_INDEPENDENT_NATIVE_CUT_DIRECTION_AUDIT',
         'independent direction audit')
    need(direction['canonical_cut_events'] == direction['native_matching_events'] == 176,
         'complete cut coverage')
    result = json.loads((out / 'SCATTER-RESULT.json').read_text())
    need(result['status'] ==
         'PASS_SELECTED_CUT_SCATTER_ORIENTATION_AND_DIRTY_SANDWICH_NO_NEW_KAPPA',
         'fresh scatter replay')
    need(len(result['blocks']) == 14, 'all fourteen tetrads')
    need(result['witness']['correct_US_p_first_output'] == '-1/2' and
         result['witness']['inverse_transpose_reader_as_scatter_first_output'] == '-1/4' and
         result['witness']['hybrid_reader_as_scatter_first_output'] == '0',
         'exact orientation witness')
    cases = result['sandwich_cases']
    need([(c['transformed_tetrads'], c['cut_adds'], c['extra_scalar_adds'],
           c['extra_scalar_scales'], c['extra_scalar_total']) for c in cases] ==
         [(3, 181, 167, 18, 185), (14, 214, 794, 84, 878)], 'complete scalar invoice')
    for c in cases:
        need(c['ordinary_columns_checked'] == 704 and c['all_private_roles_restored']
             and c['recursive_profile_delta'] == {}, 'complete endpoint and bill')
        need(c['missing_dirty_basis_entrance_rejected'] and
             c['wrong_hybrid_scatter_full_endpoint_control']['changed_normalized_scalar_entries'] > 0,
             'full-word defect controls')
    need(authenticate(repo) == before, 'source stability after replay')
    summary = {'status': 'PASS_P112_SCATTER_ORIENTATION_NO_NEW_KAPPA',
               'seconds': time.monotonic() - started,
               'parent_optimization': sys.flags.optimize,
               'child_optimization': 0, 'native_compiler_reexecuted': False,
               'direction_events': 176, 'tetrads': 14,
               'sandwich_cases': [3, 14], 'ordinary_columns_each': 704,
               'controls': {'reversed_opcode_event': 1, 'scatter_coefficient': 1,
                            'missing_dirty_entrance_full_word': 2,
                            'hybrid_scatter_full_word': 2},
               'results': {name: digest(out / name)
                           for name in ('CUT-REVIEW.json', 'SCATTER-RESULT.json')}}
    (out / 'RESULT.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(summary['status'])
    print('176 cut bindings; 14 tetrads; 704 columns per sandwich; scalar overhead 185/878; delta H = 0')
    return summary


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=HERE.parents[1])
    ap.add_argument('--out', type=Path, help='Fresh output directory; omit for temporary output.')
    args = ap.parse_args()
    if args.out is None:
        with tempfile.TemporaryDirectory(prefix='p112-scatter-') as tmp:
            run(args.repo.resolve(), Path(tmp))
    else:
        args.out.mkdir(parents=True, exist_ok=False)
        run(args.repo.resolve(), args.out.resolve())
