"""Authenticate the retained C1/B1 source closure before importing it."""
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def authenticate(root=ROOT):
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input' and sha256((root/row['path']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('source changed: '+row['path'])


def activate():
    authenticate()
    sys.path.insert(0,str(ROOT/'research/selected-bit-fast-primitives'))
    import stage_sources
    return stage_sources.activate()
