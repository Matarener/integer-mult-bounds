#!/usr/bin/env python3
"""Bounded semantic controls against private copies, never source edits.

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

ROOT = Path(__file__).resolve().parent

MUTANTS = (
    ('half-ties-toward-zero', 'frontier.py',
     '(abs(value)+26)//52', '(abs(value)+25)//52'),
    ('ignore-binary-coset', 'frontier.py',
     'patterns = self.signatures.get(signature, [])', 'patterns = list(range(256))'),
    ('forget-relative-input-scale', 'frontier.py',
     'q = [round52(scale*t) for t in self.transpose(x)]',
     'q = [round52(t) for t in self.transpose(x)]'),
    ('omit-weight-four-words', 'frontier.py',
     'for z in self.dual)', 'for z in self.dual if z.bit_count() != 4)'),
    ('reuse-history-after-every-round', 'history.py',
     'exponent = 8*rounds*components', 'exponent = 8*components'),
)


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix='precision-state-mutations-') as temporary:
        for name, filename, before, after in MUTANTS:
            target = Path(temporary)/name
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
            path = target/filename
            original = path.read_text()
            if original.count(before) != 1:
                raise ValueError('mutation anchor is not unique: '+name)
            path.write_text(original.replace(before, after))
            modes = []
            for optimized in (False, True):
                command = [sys.executable, '-B']+(['-O'] if optimized else [])+[str(target/'verify.py')]
                result = subprocess.run(command, cwd=temporary, capture_output=True, text=True,
                                        timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
                if result.returncode == 0 or 'PASS_PRECISION_STATE_FRONTIER' in result.stdout:
                    raise ValueError('semantic mutant survived: '+name)
                lines = result.stderr.strip().splitlines()
                if not lines or not lines[-1].startswith('ValueError:'):
                    raise ValueError('mutant failed outside a semantic check: '+name)
                modes.append({'optimized':optimized, 'exit_code':result.returncode,
                              'rejection':lines[-1]})
            results.append({'name':name, 'file':filename,
                            'original_sha256':hashlib.sha256(original.encode()).hexdigest(),
                            'replacement':{'before':before, 'after':after}, 'modes':modes})
    print(json.dumps({'status':'PASS_SEMANTIC_MUTATION_CONTROLS', 'mutants':results},
                     sort_keys=True, indent=2))


if __name__ == '__main__':main()
