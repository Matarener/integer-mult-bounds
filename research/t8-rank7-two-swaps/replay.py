# SPDX-License-Identifier: Apache-2.0
"""Git-free full T8 admission with explicitly reused authenticated native cache."""
import argparse
import importlib.util
from fractions import Fraction
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('scientific_materialize', HERE / 'materialize.py')
_materialize = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_materialize)
build, need = _materialize.build, _materialize.need
EXPECTED_PROFILE = {1:177116, 2:52128, 3:16952, 4:7344, 5:1612, 8:576, 32:1, 48:3050}
EXPECTED_KAPPA = Fraction('0.001729097946885651030613') - Fraction(1,10**46) - Fraction(1,10**70)
RECIPE_SHA = '54b4e3d38bf16b81d87827275325dfe0bf0b5cb6f7e4ce7543a1061c6ad89122'
OVERLAY_SHA = '053de667b534bef38f71f0c86f39647c3af501a3f940bb3e3e797d4373ee2144'


def replay(main_files, allocation, work, jobs=1, materialize_only=False):
    need(__debug__ and os.name == 'posix', 'enabled assertions and POSIX required')
    need(type(jobs) is int and 1 <= jobs <= 2, 'bounded worker count')  # noqa: E721
    need(not work.exists(), 'fresh work directory')
    order = json.loads((allocation / 'ORDER.json').read_text())
    dispatch = json.loads((allocation / 'DISPATCH.json').read_text())
    need(len(order) == 72 and len(dispatch) == 72, 'T8 call inventory')
    expected = [[s, r, 'extra' if i == 0 else 'gauge44']
                for i, (s, r) in enumerate(order)]
    need(dispatch == expected, 'explicit first-call extra dispatcher')
    scientific = work / 'scientific'
    receipt = build(main_files, HERE / 'MATERIALIZE.json',
                    HERE / 'derived-overlay.tar.gz', scientific, RECIPE_SHA, OVERLAY_SHA)
    (work / 'MATERIALIZATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    if materialize_only:
        return {**receipt, 'status': 'MATERIALIZED_ONLY_NOT_ADMITTED'}
    command = [sys.executable, '-B', str(scientific / 'adapters/admit_extension.py')]
    values = {'source': scientific / 'source', 'fill': allocation / 'FILL.json.gz',
              'order': allocation / 'ORDER.json', 'dispatch': allocation / 'DISPATCH.json',
              'native-cache': scientific / 'native-cache',
              'native-receipt': scientific / 'NATIVE-RECEIPT.json',
              'work': work / 'admission', 'replica-helper-dir': scientific / 'helpers',
              'reconstructor': scientific / 'helpers/reconstruct_replica.py',
              'comparison-claim': scientific / 'PR2969-CLAIM.json',
              'blocknorm-checker': scientific / 'adapters/extension_blocknorm.py'}
    for flag, path in values.items():
        command += ['--' + flag, str(path.resolve())]
    command += ['--source-profile', 'rank7-joint-endframes', '--comparison-profile',
                'pr2969', '--jobs', str(jobs)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', PYTHONINTMAXSTRDIGITS='0')
    for key in ['PYTHONPATH', 'PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER']:
        env.pop(key, None)
    with (work / 'admission.log').open('w') as log:
        process = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=540)
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        need(code == 0, 'unchanged admission failed; inspect admission.log')
    result = json.loads((work / 'admission/RESULT.json').read_text())
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',
         'terminal admission required')
    need(result['replicas'] == 8 and result['actual_expected_helpers'] == 408,
         'frozen replicas/helper inventory')
    need({int(r):n for r,n in result['profile'].items()} == EXPECTED_PROFILE,
         'frozen complete paid profile')
    need(Fraction(result['kappa']) == EXPECTED_KAPPA, 'frozen exact endpoint')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['main-files', 'allocation', 'work']:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--jobs', type=int, choices=(1, 2), default=1)
    parser.add_argument('--materialize-only', action='store_true')
    args = parser.parse_args()
    result = replay(args.main_files.resolve(), args.allocation.resolve(),
                    args.work.resolve(), args.jobs, args.materialize_only)
    print(result['status'])


if __name__ == '__main__':
    main()
