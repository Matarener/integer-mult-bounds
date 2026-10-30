"""Run the unchanged complete release after the controller timeout.

Local research orchestration by SovereignSteak with OpenAI Codex assistance.
This does not rewrite the failed controller receipt or claim its success.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from fractions import Fraction

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'replay-t740-cold/run'
WORK = ROOT / 'replay-t740-release-continuation'
PACKAGE = RUN / 'candidate/package'
spec = importlib.util.spec_from_file_location('admission', RUN / 'adapters/admit_extension.py')
admission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admission)


def read(path):
    return json.loads(path.read_text())


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def authenticate():
    source = RUN / 'source-edits'
    cache = RUN / 'native/native-cache'
    prepared = read(RUN / 'candidate/RESULT.json')
    native = read(RUN / 'native/NATIVE-RECEIPT.json')
    need(admission.sha(source / 'MANIFEST.json') == prepared['source_manifest_sha256'], 'source manifest')
    need(admission.tree(source, ('MANIFEST.json',)) == read(source / 'MANIFEST.json'), 'source inventory')
    need(native['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE', 'native status')
    need(admission.sha(RUN / 'native/NATIVE-RECEIPT.json') == prepared['native_receipt_sha256'], 'native binding')
    need(admission.tree(cache) == native['cache_files'], 'native cache inventory')
    need(all(admission.sha(Path(p)) == h for p, h in prepared['external_input_sha256'].items()), 'external inputs')
    need(admission.tree(PACKAGE, ('MANIFEST.json',)) == read(PACKAGE / 'MANIFEST.json'), 'package inventory')
    discovery = read(RUN / 'candidate/discovery/STAGES.json')
    need(len(discovery) == 7 and all(s['exit_code'] == 0 for s in discovery), 'discovery completion')
    return admission.sha(PACKAGE / 'MANIFEST.json')


def main():
    need(not WORK.exists(), 'fresh external work required')
    manifest = authenticate()
    command = [sys.executable, '-B', str(PACKAGE / 'verify_release.py'), '--main', str(RUN),
               '--work', str(WORK), '--native-cache', str(RUN / 'native/native-cache'), '--jobs', '2']
    start = time.time()
    receipt = dict(status='RUNNING', command=command, package_manifest_sha256=manifest,
                   original_controller_exit=1, original_controller_timeout_seconds=3600)
    target = ROOT / 'evidence/t740-release-continuation.json'
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    with (ROOT / 'logs/t740-release-continuation.log').open('w') as log:
        code = subprocess.call(command, stdout=log, stderr=subprocess.STDOUT,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                                        OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
    receipt.update(exit_code=code, seconds=time.time()-start, status='FAIL' if code else 'RELEASE_RETURNED_ZERO')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    need(code == 0, 'release failed; inspect log')
    need(authenticate() == manifest, 'post-run input binding')
    release = read(WORK / 'RELEASE-RECEIPT.json')
    outer = read(PACKAGE / 'outer/OUTER-CLAIM.json')
    need(release['status'] == 'PASS_RELEASE' and release['manifest_sha256'] == manifest, 'release receipt binding')
    need(Fraction(release['kappa_decimal']) == Fraction(outer['kappa_rational']), 'exact kappa binding')
    receipt.update(status='PASS_INDEPENDENT_COMPLETE_RELEASE_CONTINUATION',
                   release_receipt_sha256=admission.sha(WORK / 'RELEASE-RECEIPT.json'),
                   scope='Unchanged full release plus pre/post source/cache/external bindings; original timed-out controller remains failed.')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
