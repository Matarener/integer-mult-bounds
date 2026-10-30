# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the literal T8 candidate and replay its complete finite admission."""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA = Fraction('0.001729097946885651030613') - Fraction(1, 10**46) - Fraction(1, 10**70)
BASELINE = Fraction('0.001728996308346386172130') - Fraction(1, 10**46) - Fraction(1, 10**70)


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def run(script, *arguments, timeout):
    subprocess.run([sys.executable, '-I', '-Werror', '-B', str(HERE / script),
                    *map(str, arguments)], check=True, timeout=timeout)


def verify(work, main_files):
    need(__debug__, 'full ancestral admission requires enabled assertions')
    need(not work.exists(), 'use a fresh external work directory')
    need(not work.is_relative_to(ROOT), 'work directory must be outside the checkout')
    work.mkdir(parents=True)
    run('reconstruct.py', '--output', work / 'allocation', timeout=120)
    run('replay.py', '--main-files', main_files, '--allocation', work / 'allocation',
        '--work', work / 'replay', '--jobs', 2, timeout=570)
    admission = work / 'replay/admission'
    result = read(admission / 'RESULT.json')
    release_path = admission / 'release/RELEASE-RECEIPT.json'
    release = read(release_path)
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',
         'complete admission required')
    need(release['status'] == 'PASS_RELEASE', 'complete release required')
    need(Fraction(result['kappa']) == Fraction(release['kappa_decimal']) == KAPPA > BASELINE,
         'exact scoped T8 gain')
    need(hashlib.sha256(release_path.read_bytes()).hexdigest()
         == result['release_receipt_sha256'], 'release receipt binding')
    invoice = read(admission / 'discovery/global/audit/PREFIX-AND-INVOICE.json')
    need(invoice['private_zero_buffers'] == 91 and invoice['physical'] == 7677,
         'fully charged private buffers and physical families')
    need(invoice['physical_stock_identity'] == {
        'data_and_owner_families': 7168, 'local_helpers': 408,
        'private_centres': 8, 'private_zero_buffers': 91, 'coefficient_work': 2},
         'physical stock decomposition')
    expected = read(HERE / 'EXPECTED.json')
    profile = read(work / 'allocation/MODERN-OWNER-AUDIT.json')['profile']
    need(profile == expected['profile'], 'literal paid profile')
    need(all(stage['exit_code'] == 0 for stage in result['stages']), 'all stages completed')
    receipt = {'status': 'PASS_T8_RANK7_PROVIDER_COMPOSITION', 'kappa': str(KAPPA),
               'kappa_decimal': result['kappa_decimal'], 'baseline_pr': 3485,
               'baseline_kappa': str(BASELINE), 'gain': str(KAPPA - BASELINE),
               'replicas': 8, 'calls': 72, 'helpers_per_call': 408,
               'roles': 29376, 'profile': profile,
               'release_receipt_sha256': result['release_receipt_sha256'],
               'source_manifest_sha256': result['source_manifest_sha256'],
               'native_receipt_sha256': result['native_receipt_sha256'],
               'scope': 'Complete conditional finite T8 admission and modern outer arithmetic. '
                        'Both native providers reused from authenticated prior fresh executions. '
                        'Below the T740 frontier; inherited all-size assumptions remain.'}
    (work / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['kappa_decimal'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--main-files', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.work is None:
        parent = Path(tempfile.mkdtemp(prefix='t8-rank7-', dir=os.environ.get('TMPDIR')))
        work = parent / 'run'
    else:
        work = args.work.resolve()
    verify(work, args.main_files.resolve())


if __name__ == '__main__':
    main()
