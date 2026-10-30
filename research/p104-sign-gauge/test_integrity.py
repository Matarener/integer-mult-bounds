#!/usr/bin/env python3
"""Actual source/receipt/word corruption and read-only Git-free export controls.

Charan / theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)
INPUTS = json.loads((HERE / 'VERIFY.json').read_text())['inputs']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def copy_payload(destination):
    for path in [*HERE.iterdir(), *(ROOT / name for name in INPUTS)]:
        if path.is_file() and path.suffix != '.pyc':
            out = destination / path.relative_to(ROOT)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, out)


def replay(root):
    env = dict(os.environ, PATH='')
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(root / PACKAGE / 'verify.py')],
                          cwd=root, env=env, capture_output=True, text=True, timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix='p104-sign-controls-') as temporary:
        root = Path(temporary)
        clean = root / 'clean'
        copy_payload(clean)
        files = sorted(p for p in clean.rglob('*') if p.is_file())
        hashes = {str(p.relative_to(clean)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        dirs = sorted([clean, *(p for p in clean.rglob('*') if p.is_dir())], reverse=True)
        try:
            for p in files:
                p.chmod(0o444)
            for p in dirs:
                p.chmod(0o555)
            completed = replay(clean)
            require(completed.returncode == 0 and 'PASS_P104_SIGN_GAUGE' in completed.stdout,
                    'Read-only Git-free optimized replay: ' + completed.stderr)
            require(hashes == {str(p.relative_to(clean)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in clean.rglob('*') if p.is_file()}, 'Replay wrote files')
        finally:
            for p in dirs:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)
        for label, expected in [('source', 'Input SHA256 mismatch'),
                                ('receipt', 'Exact receipt mismatch'),
                                ('word', 'Committed complete word differs')]:
            changed = root / label
            copy_payload(changed)
            pkg = changed / PACKAGE
            if label == 'source':
                p = changed / INPUTS[0]
                p.write_bytes(p.read_bytes() + b'corrupt')
            elif label == 'receipt':
                p = pkg / 'RESULT.json'
                value = json.loads(p.read_text())
                value['saved_real_primitives_per_local_call'] += 2
                p.write_text(json.dumps(value))
            else:
                p = pkg / 'WORD.json.gz'
                value = json.loads(gzip.decompress(p.read_bytes()))
                value['program'].pop()
                p.write_bytes(gzip.compress(json.dumps(value).encode(), mtime=0))
            completed = replay(changed)
            require(completed.returncode != 0 and expected in completed.stderr,
                    label + ' corruption not rejected by the intended gate: ' + completed.stderr)
        # Container bytes may change while the complete mathematical payload stays fixed.
        repacked = root / 'repacked'
        copy_payload(repacked)
        p = repacked / PACKAGE / 'WORD.json.gz'
        p.write_bytes(gzip.compress(gzip.decompress(p.read_bytes()), compresslevel=1, mtime=123))
        completed = replay(repacked)
        require(completed.returncode == 0, 'Lossless gzip repacking rejected: ' + completed.stderr)
    print('PASS_P104_SIGN_INTEGRITY readonly_git_free=1 corruptions_rejected=3 gzip_repack=1')


if __name__ == '__main__':
    main()
