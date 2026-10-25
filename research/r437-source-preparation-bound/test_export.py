"""Git-free positive replay and exact-source/receipt rejection under -O."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok: raise ValueError(message)


def main():
    pins = [r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input']
    with tempfile.TemporaryDirectory(prefix='r437-producer-export-') as directory:
        root = Path(directory)
        package = root/PACKAGE
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for row in pins:
            target = root/row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/row['path'], target)
        env = dict(os.environ)
        env.pop('PYTHONPATH', None)
        env.pop('PYTHONOPTIMIZE', None)
        def run():
            return subprocess.run([sys.executable,'-O','-B','-X',f'pycache_prefix={root}/private-cache',str(package/'verify.py')],
                                  cwd=root, env=env, capture_output=True, text=True, timeout=180)
        positive = run()
        need(positive.returncode == 0, 'Git-free optimized positive: '+positive.stderr)
        rejected = 0
        for row in pins:
            target = root/row['path']
            before = target.read_bytes()
            target.write_bytes(before+b'\n# intentional corruption control\n')
            result = run()
            need(result.returncode != 0 and 'changed source: '+row['path'] in result.stderr,
                 'exact source mutation rejected before import: '+row['path'])
            target.write_bytes(before)
            rejected += 1
        receipt = package/'RESULT.json'
        value = json.loads(receipt.read_text())
        value['status'] = 'intentional receipt corruption'
        receipt.write_text(json.dumps(value))
        result = run()
        need(result.returncode != 0 and 'committed exact receipt' in result.stderr,
             'changed mathematical receipt rejects under optimization')
    print('PASS Git-free optimized positive;', rejected, 'source mutations and changed receipt reject')


if __name__ == '__main__': main()
