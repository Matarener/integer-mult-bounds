"""Authenticate every retained input before the selected replay imports it."""
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate():
    count = 0
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        if sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Selected adapter source hash: ' + row['path'])
        if sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != row['git_blob']:
            raise ValueError('Selected adapter source blob: ' + row['path'])
        count += 1
    return count
