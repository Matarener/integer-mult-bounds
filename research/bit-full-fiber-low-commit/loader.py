# SPDX-License-Identifier: Apache-2.0
"""Load only authenticated predecessor bytes; no ambient module lookup."""
from pathlib import Path
import hashlib
import json
import sys
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent


def load():
    raw={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            content=(ROOT/row['path']).read_bytes()
            if hashlib.sha256(content).hexdigest()!=row['sha256']:
                raise ValueError('source SHA256 '+row['path'])
            raw[row['path']]=content
    modules={}
    names={'machine':'research/fixed-tape-ordered-shear/machine.py',
           'counters':'research/fixed-tape-ordered-shear/counters.py'}
    if any(name in sys.modules for name in names):
        raise ValueError('preloaded predecessor module')
    try:
        for name,path in names.items():
            module=types.ModuleType(name);module.__file__=str(ROOT/path)
            sys.modules[name]=module
            exec(compile(raw[path],module.__file__,'exec'),module.__dict__)
            modules[name]=module
    finally:
        for name in names:
            sys.modules.pop(name,None)
    return raw,modules
