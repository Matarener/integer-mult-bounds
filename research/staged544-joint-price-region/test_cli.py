#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual optimized CLI controls in disposable copies; original inputs stay intact."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def main():
    before = hashes(HERE)
    controls = []
    with tempfile.TemporaryDirectory(prefix='staged544-joint-cli-') as temporary:
        work = Path(temporary) / 'package'

        def reset():
            if work.exists():
                shutil.rmtree(work)
            shutil.copytree(HERE, work, ignore=shutil.ignore_patterns('__pycache__'))
            work.chmod(0o755)
            for path in work.rglob('*'):
                path.chmod(0o755 if path.is_dir() else 0o644)

        def run(script='verify.py', *args):
            return subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B',
                                   str(work / script), *args], capture_output=True,
                                  text=True, timeout=90)

        def reject(label, script='verify.py'):
            result = run(script)
            need(result.returncode != 0, label + ' was accepted')
            controls.append(label)

        reset()
        result = run()
        need(result.returncode == 0 and 'PASS_STAGED544_JOINT_PRICE_REGION' in result.stdout,
             'positive primary CLI')
        need(run('independent.py').returncode == 0, 'positive independent CLI')
        for key, value, label, script in [
            ('a', '1/2', 'changed exponent', 'verify.py'),
            ('demands', [234,18,162,478,864,1917], 'changed inventory', 'verify.py'),
            ('extras', [[16,[0,0,0,0,2,0]]], 'removed extra column', 'verify.py'),
            ('expected_axis_ranges', ['18','49','88/3','30','48'], 'inflated range', 'independent.py'),
        ]:
            reset()
            path = work / 'MODEL.json'
            data = json.loads(path.read_text())
            data[key] = value
            path.write_text(json.dumps(data))
            reject(label, script)
        reset()
        path = work / 'retained/3815-ceiling_certificate.py'
        path.write_bytes(path.read_bytes() + b'\n# corrupted source\n')
        reject('source bytes')
        reset()
        path = work / 'RESULT.json'
        data = json.loads(path.read_text())
        data['axis_witnesses'][0]['counts'][0] = '673'
        path.write_text(json.dumps(data))
        reject('corrupted result witness')
        reset()
        yes = run('verify.py', '--flows', '0','48','0','0','0')
        no = run('verify.py', '--flows', '0','28','28','0','0')
        need(yes.returncode == no.returncode == 0, 'classification CLI exit')
        need(json.loads(yes.stdout)['sharp_common_price'] is True, 'boundary CLI classification')
        need(json.loads(no.stdout)['sharp_common_price'] is False, 'coupled CLI classification')
    need(before == hashes(HERE), 'original bytes changed')
    print('PASS_STAGED544_JOINT_REAL_CLI controls=' + str(len(controls)) +
          ' positives=4 original_bytes_unchanged no_new_kappa')


if __name__ == '__main__':
    main()
