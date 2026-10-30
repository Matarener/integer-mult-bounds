#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check exact supplied bytes in the checkout and optionally a Git commit/index.

This verifies declared byte identity, not the mathematics or dependency closure.
Substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--git-ref', help='commit/ref, or INDEX for staged bytes')
    args = parser.parse_args()
    inputs = json.loads((HERE/'IMPORT.json').read_text())['source_files']
    for name, expected in inputs.items():
        path = ROOT/name
        if not path.resolve().is_relative_to(ROOT) or path.is_symlink():
            raise ValueError('invalid source path: '+name)
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('working byte mismatch: '+name)
    if args.git_ref:
        prefix = '' if args.git_ref == 'INDEX' else args.git_ref
        queries = ''.join(prefix+':'+name+'\n' for name in inputs).encode()
        raw = subprocess.run(['git','cat-file','--batch'], input=queries,
                             stdout=subprocess.PIPE, check=True, cwd=ROOT).stdout
        offset = 0
        for name, expected in inputs.items():
            end = raw.index(b'\n', offset)
            header = raw[offset:end].split()
            if len(header) != 3 or header[1] != b'blob':
                raise ValueError('missing Git blob: '+name)
            size = int(header[2]); offset = end+1
            content = raw[offset:offset+size]; offset += size+1
            if sha256(content).hexdigest() != expected:
                raise ValueError('Git byte mismatch: '+name)
        if offset != len(raw):
            raise ValueError('unexpected trailing batch output')
    print(json.dumps(dict(status='PASS_EXACT_IMPORTED_BYTES', files=len(inputs), git_ref=args.git_ref)))


if __name__ == '__main__':
    main()
