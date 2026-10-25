#!/usr/bin/env python3
"""Execute the complete final native and guarded physical checks sequentially.

The source scripts and owners remain frozen. Output files and logs belong to
this continuation. This command is suitable in a fresh isolated replay copy.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from hashlib import sha256
from pathlib import Path
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent/'kappa-next-regime'
SHA = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'


def main():
    out = HERE/'bit-integration'
    logs = out/'final-native-logs'
    logs.mkdir(exist_ok=False)
    word = HERE/'bit-word/early-birth-prefixes/WORD.json.gz'
    pool = out/'early-birth-prefixes'
    commands = [
        ('native-catalogue', OLD/'native-catalogue/review.py', '--pool', pool, '--word', word, '--word-content-sha256', SHA, '--output', out/'FINAL-NATIVE-REVIEW.json'),
        ('complete-symbolic-word', OLD/'native-catalogue/whole_word.py', '--template', pool/'GLOBAL-TEMPLATE.json.gz', '--word', word, '--word-content-sha256', SHA, '--output', out/'FINAL-WHOLE-WORD.json'),
        ('bind-physical-fixture', HERE/'build_final_physical.py'),
        ('physical-fixture', out/'final_physical_probe.py', '--output', out/'FINAL-PHYSICAL-PROBE.json'),
    ]
    steps = []
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for label, script, *arguments in commands:
        argv = [sys.executable, '-B', str(script), *map(str, arguments)]
        log = logs/(label+'.log')
        print(label+': running', flush=True)
        begin = time.monotonic()
        with log.open('xb') as stream:
            done = subprocess.run(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        step = {'label': label, 'argv': argv, 'exit_code': done.returncode, 'elapsed_seconds': time.monotonic()-begin,
                'script_sha256': sha256(script.read_bytes()).hexdigest(),
                'log': str(log.relative_to(ROOT)), 'log_sha256': sha256(log.read_bytes()).hexdigest()}
        steps.append(step)
        (out/'FINAL-NATIVE-EXECUTION.json').write_text(json.dumps({'status': 'RUNNING' if done.returncode == 0 else 'FAILED', 'steps': steps}, indent=2, sort_keys=True)+'\n')
        if done.returncode:
            raise RuntimeError(label+' failed\n'+log.read_text()[-5000:])
        print(label+': PASS', flush=True)
    native, whole, physical = (json.loads((out/name).read_text()) for name in ('FINAL-NATIVE-REVIEW.json', 'FINAL-WHOLE-WORD.json', 'FINAL-PHYSICAL-PROBE.json'))
    assert native['actual_word_content_sha256'] == whole['native_binding']['actual_word_content_sha256'] == physical['word_content_sha256'] == SHA
    assert native['binding_sha256'] == whole['native_binding']['binding_sha256'] == physical['catalogue']['binding_sha256']
    assert native['canonical_requests'] == whole['complete']['residuals'] == 987525
    assert physical['complete_GL64_payload_executed'] is False
    paths = [word, pool/'GLOBAL-TEMPLATE.json.gz', Path(__file__), HERE/'build_final_physical.py']
    result = {'status': 'PASS_FINAL_NATIVE_SYMBOLIC_AND_CONTROLLED_PHYSICAL_EXECUTION', 'steps': steps,
              'word_content_sha256': SHA, 'binding_sha256': native['binding_sha256'],
              'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths},
              'scope': 'Complete finite native catalogue and complete symbolic word; source-bound 46-bit controlled nested physical fixture. Complete GL64 physical residual execution and all-size source/primitive assumptions remain unproved here.'}
    (out/'FINAL-NATIVE-EXECUTION.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
