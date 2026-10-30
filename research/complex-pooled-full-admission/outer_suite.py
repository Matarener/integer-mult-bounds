#!/usr/bin/env python3
"""Bounded outer checks; no production construction or numerical payload.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Each child finishes and its status propagates before returning.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    options = ['-O'] if not __debug__ else []
    with tempfile.TemporaryDirectory(prefix='pooled-outer-checks-') as directory:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                   PYTHONPYCACHEPREFIX=str(Path(directory)/'bytecode'))
        env.pop('PYTHONOPTIMIZE', None)
        for name, flag, recorded in (
                ('outer_check.py', '--out', 'OUTER-CHECK-PORTABLE.json'),
                ('outer_domain.py', '--output', 'OUTER-DOMAIN.json')):
            receipt = Path(directory)/recorded
            subprocess.run([sys.executable, *options, '-B', str(HERE/name),
                            flag, str(receipt)], env=env, check=True, timeout=90)
            if json.loads(receipt.read_bytes()) != json.loads((HERE/'evidence'/recorded).read_bytes()):
                raise ValueError('fresh bounded receipt differs from preserved evidence: '+recorded)
    print('PASS_BOUNDED_OUTER_SUITE_NOT_PRODUCTION_EXECUTION')


if __name__ == '__main__':
    main()
