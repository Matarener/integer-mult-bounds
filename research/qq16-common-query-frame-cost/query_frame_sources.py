"""Authenticate canonical runtime bytes before executing the retained checker."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def authenticate():
    pins={}
    raw=(HERE/'SOURCES.json').read_bytes()
    need(sha256(raw).hexdigest()=='e07c9ced6625c59a74cf18ffb39d1836f09b99cad7dea431ac3f631535c5a6dd','source manifest integrity')
    for row in json.loads(raw)['files']:
        if row['usage']!='input':
            continue
        data=(ROOT/row['path']).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'source SHA256: '+row['path'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'source Git blob: '+row['path'])
        pins[row['path']]=row['sha256']
    return pins


def loaded():
    pins=authenticate()
    path=ROOT/'research/qq16-line-normalized-decoder/verify.py'
    module=types.ModuleType('pinned_line_decoder_for_frame_bound')
    module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module,module.load_source(),pins
