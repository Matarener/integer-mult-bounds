"""Authenticate every consumed source before import. Apache-2.0."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def authenticate():
    items = json.loads((ROOT / 'INPUTS.json').read_text())
    for item in items:
        if sha256((ROOT / item['local']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Frozen source: ' + item['local'])
    return len(items)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
