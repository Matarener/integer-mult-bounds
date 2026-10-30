"""Authenticate verbatim predecessor inputs before loading any predecessor code.

Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
Source authors and their complete notices are retained under vendor/.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys

HERE = Path(__file__).resolve().parent
RETAINED_COMMIT = 'b83ff89de649be3bd2dc2d885da254bae00c8836'
PACKAGE = 'research/p104-accumulated-block-composition/'
ORIGINS = {'accumulated': '9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62',
           'blocks': '206cb717c0c07737d61637b93f7502ca48850348'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(directory=HERE):
    pins = json.loads((directory/'SOURCES.json').read_bytes())
    need(pins['retained_commit'] == RETAINED_COMMIT, 'Exact retained source ancestor')
    names = set()
    for row in pins['vendored']:
        name = row['local_path']
        parts = PurePosixPath(name).parts
        need(parts and parts[0] == 'vendor' and '..' not in parts
             and not name.startswith('/') and '\\' not in name and ':' not in name,
             'Relative vendored source path')
        need(len(parts) >= 3 and parts[1] in ORIGINS
             and row['pin'] == 'head:'+ORIGINS[parts[1]]+':'+row['path'],
             'Exact original source head')
        need(name not in names, 'Unique vendored source')
        names.add(name)
        path = directory
        for part in parts:
            path = path/part
            need(not path.is_symlink(), 'No source symlink')
        need(path.is_file(), 'Regular vendored source')
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Exact source SHA256: '+name)
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'Exact source Git blob: '+name)
        retained = [r for r in pins['files'] if r.get('local_path') == name]
        need(len(retained) == 1, 'One retained repository pin for each runtime origin')
        target = retained[0]
        need(target['origin'] == row and target['path'] == PACKAGE+name
             and target['pin'] == 'head:'+RETAINED_COMMIT+':'+target['path']
             and target['sha256'] == row['sha256'] and target['git_blob'] == row['git_blob'],
             'Exact retained source bytes and original provenance')
    actual = {p.relative_to(directory).as_posix()
              for p in (directory/'vendor').rglob('*') if p.is_file() or p.is_symlink()}
    need(actual == names, 'Complete vendored payload inventory')
    return {'files': len(names), 'source_manifest_sha256': sha256((directory/'SOURCES.json').read_bytes()).hexdigest()}


@contextmanager
def sources():
    authenticate()
    yield HERE/'vendor/accumulated', HERE/'vendor/blocks'
