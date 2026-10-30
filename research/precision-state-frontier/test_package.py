#!/usr/bin/env python3
"""Read-only portable replay and CLI controls; Python 3.10+, standard library.

Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

from frontier import Geometry, ROOT, need


def main():
    geo = Geometry()
    expected = (ROOT/'RESULT.json').read_bytes()
    with tempfile.TemporaryDirectory(prefix='precision-state-portable-') as temporary:
        outer = Path(temporary)
        package = outer/'package'
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('__pycache__'))
        for path in package.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        package.chmod(0o555)
        environment = {key:value for key,value in os.environ.items() if not key.startswith('PYTHON')}
        environment.update(PATH='', PYTHONDONTWRITEBYTECODE='1',
                           PYTHONPYCACHEPREFIX=str(outer/'fresh-pycache'))
        def run(script, arguments=(), optimized=False, success=True):
            command = [sys.executable, '-B']+(['-O'] if optimized else [])+[str(package/script), *arguments]
            result = subprocess.run(command, cwd=outer, env=environment, capture_output=True, timeout=30)
            need((result.returncode == 0) == success, 'portable CLI exit: '+script)
            if success:need(not result.stderr, 'portable warnings or stderr: '+script)
            return result.stdout
        for optimized in (False, True):
            need(run('verify.py', optimized=optimized) == expected, 'portable exact receipt')
        # Exercise the published JSON interfaces with a nontrivial 16-state
        # fiber and with a tag-free relative-five-bit input.
        cli_roundtrips = []
        for g in (4, 5):
            y = [-v for v in geo.mul([4]*8)]
            x = geo.recover(y, g, 15) if g == 4 else [i-56 for i in range(112)]
            source = outer/('input-'+str(g)+'.json')
            source.write_text(json.dumps({'g':g, 'x':x}))
            encoded = run('frontier.py', ('encode', str(source)))
            packet = json.loads(encoded)
            need(packet['worst_case_states'] == (16 if g == 4 else 1), 'CLI frontier state bound')
            encoded_file = outer/('encoded-'+str(g)+'.json');encoded_file.write_bytes(encoded)
            recovered = json.loads(run('frontier.py', ('decode', str(encoded_file)), optimized=True))
            need(recovered['x'] == x, 'CLI exact recovery')
            cli_roundtrips.append({'relative_bits':g, 'states':packet['worst_case_states']})
        budget_file = outer/'budget.json'
        budget_file.write_text(json.dumps({'rounds':18}))
        result = json.loads(run('history.py', (str(budget_file),)))
        need(result['minimum_packed_bits'] == 533, 'CLI history budget')
        duplicate = outer/'duplicate.json';duplicate.write_text('{"g":0,"g":1,"x":[]}')
        run('frontier.py', ('encode', str(duplicate)), success=False)
        forged = json.loads(encoded);forged['tag']=1
        forged_file=outer/'forged.json';forged_file.write_text(json.dumps(forged))
        run('frontier.py', ('decode', str(forged_file)), optimized=True, success=False)
        invalid_budget=outer/'invalid-budget.json';invalid_budget.write_text('{"rounds":true}')
        run('history.py', (str(invalid_budget),), success=False)
        need(not (outer/'fresh-pycache').exists(), 'no package-side or external bytecode writes')
        # Restore write permission only to clean this temporary export.
        for path in package.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        package.chmod(0o755)
    print(json.dumps({'status':'PASS_PORTABLE_PRECISION_STATE_PACKAGE',
                     'normal_and_optimized_receipt_sha256':hashlib.sha256(expected).hexdigest(),
                     'empty_path':True, 'read_only_package':True, 'cli_roundtrips':cli_roundtrips,
                     'history_cli_bits':533, 'cli_rejections':3}, sort_keys=True, indent=2))


if __name__ == '__main__':main()
