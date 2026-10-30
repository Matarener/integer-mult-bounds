"""Byte-transport check of the complete canonical witness, separate from timing."""
import gzip
from hashlib import sha256
import json
from pathlib import Path

root = Path(__file__).resolve().parent / 'evidence' / 'canonical'
manifest = json.loads((root / 'MANIFEST.json').read_text())
for name, row in manifest.items():
    path = root / (name + '.gz')
    digest = sha256()
    size = 0
    with gzip.open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            digest.update(block)
    if size != row['canonical_bytes'] or digest.hexdigest() != row['canonical_sha256']:
        raise ValueError('complete canonical artifact changed: ' + name)
print('PASS_COMPLETE_CANONICAL_WITNESS_AND_RANK_TRANSPORT')
