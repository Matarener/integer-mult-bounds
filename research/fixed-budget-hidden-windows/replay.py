#!/usr/bin/env python3
"""Bounded, serial offline replay. Writes no package files. Python 3.10+."""
from pathlib import Path
from hashlib import sha256
import json
import os
import platform
import re
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    environment.pop('PYTHONOPTIMIZE', None)
    expected = {'main': (root/'RESULT.json').read_bytes(),
                'independent': (root/'independent-check.json').read_bytes()}
    test_code = ('import sys,unittest;sys.path.insert(0,sys.argv[1]);'
                 'suite=unittest.defaultTestLoader.loadTestsFromName("test_verify");'
                 'result=unittest.TextTestRunner(verbosity=1).run(suite);'
                 'sys.exit(not result.wasSuccessful())')
    records = []
    for optimized in (False, True):
        prefix = [sys.executable, '-I', '-B'] + (['-O'] if optimized else [])
        for name, script in (('main','verify.py'), ('independent','independent_check.py'), ('tests',None)):
            arguments = ([str(root/script)] if script else ['-c', test_code, str(root)])
            child = subprocess.run(prefix+arguments, cwd=root, env=environment,
                                   capture_output=True, timeout=30, check=False)
            if child.returncode:
                raise RuntimeError(name+' replay failed: '+child.stderr.decode(errors='replace'))
            record = {'check': name, 'optimized': optimized, 'status': 'pass'}
            if name in expected:
                if child.stdout != expected[name]:
                    raise RuntimeError(name+' output differs from saved exact receipt')
                record['receipt_sha256'] = sha256(child.stdout).hexdigest()
            else:
                count = re.search(rb'Ran (\d+) tests',child.stderr)
                if count is None or int(count.group(1)) != 26:
                    raise RuntimeError('test suite count changed or was empty')
                record['tests'] = 26
            records.append(record)
    print(json.dumps({'status':'pass','python':platform.python_version(),
                      'writes_package_files':False,'timeout_seconds_per_command':30,
                      'serial':True,'runs':records},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
