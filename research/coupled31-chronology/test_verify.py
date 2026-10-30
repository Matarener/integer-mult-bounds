#!/usr/bin/env python3
"""Reject damaged source, word, proof and receipt copies.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def main():
    controls = []
    for kind in ('source', 'query', 'order', 'proof', 'receipt'):
        with tempfile.TemporaryDirectory(prefix='coupled31-control-') as directory:
            target = Path(directory)/'package'
            shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns('__pycache__'))
            if kind == 'source':
                path = target/'sources/p104-result.json'
                path.write_text(path.read_text()+' ')
            elif kind in ('query', 'order'):
                path = target/'WORD31.json'
                word = json.loads(path.read_text())
                thin = next(i for i, c in enumerate(word['calls']) if c['stage'] == word['g'])
                if kind == 'query':
                    word['calls'][thin]['r'] = [0]*len(word['calls'][thin]['r'])
                else:
                    word['order'].remove(thin)
                    word['order'].append(thin)
                path.write_text(json.dumps(word))
            elif kind == 'proof':
                path = target/'PROOF.md'
                path.write_text(path.read_text().replace('g <= L b+2', 'g <= L b+3'))
            else:
                path = target/'RESULT.json'
                value = json.loads(path.read_text())
                value['pricing']['requested_31_leaf']['minimum_thin_rank'] = 10
                path.write_text(json.dumps(value))
            process = subprocess.run([sys.executable, '-I', '-O', '-B', str(target/'verify.py')],
                                     cwd='/', capture_output=True, text=True, timeout=30)
            if process.returncode == 0:
                raise ValueError('damaged package accepted: '+kind)
            expected = {'source': 'source hash', 'query': 'complete Laurent endpoint',
                        'order': 'complete Laurent endpoint', 'proof': 'saved result differs',
                        'receipt': 'saved result differs'}[kind]
            if expected not in process.stderr:
                raise ValueError('wrong failure for '+kind+': '+process.stderr)
            controls.append(kind)
    print('PASS_COUPLED31_CORRUPTION_CONTROLS '+json.dumps(controls))


if __name__ == '__main__':
    main()
