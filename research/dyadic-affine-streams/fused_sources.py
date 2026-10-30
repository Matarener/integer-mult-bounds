"""Authenticate the live source closure before loading the retained runtime."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def authenticate(root=ROOT):
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            if sha256((root / row['path']).read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('source changed: ' + row['path'])


def activate():
    authenticate()
    sys.path.insert(0, str(ROOT / 'research/high-carry-streams'))
    import bindings
    return bindings.activate()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
