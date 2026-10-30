"""Measure gzip time and size on the three fixed G20 output payloads.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This diagnostic does not measure the complete replay.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
import time
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    verify.authenticate()
    rows = []
    for name in ['WORD.json.gz', 'GLOBAL.jsonl.gz', 'SOURCE-DESCRIPTORS.json.gz']:
        raw = gzip.decompress((verify.SOURCE / name).read_bytes())
        samples = {}
        for level in [9, 1, 2, 3, 6, 0, 0, 6, 3, 2, 1, 9, 9, 1, 2, 3, 6, 0]:
            start = time.perf_counter()
            packed = gzip.compress(raw, compresslevel=level, mtime=0)
            compress = time.perf_counter() - start
            start = time.perf_counter()
            got = gzip.decompress(packed)
            decompress = time.perf_counter() - start
            verify.need(got == raw, 'Exact decompressed bytes')
            samples.setdefault(level, []).append({'compress_seconds': compress,
                                                  'decompress_seconds': decompress,
                                                  'bytes': len(packed)})
        rows.append({'file': name, 'raw_bytes': len(raw),
                     'raw_sha256': sha256(raw).hexdigest(), 'samples': samples})
        args.output.write_text(json.dumps({'python': platform.python_version(),
                                         'zlib': zlib.ZLIB_VERSION, 'rows': rows}, indent=2) + '\n')
    verify.authenticate()


if __name__ == '__main__':
    main()
