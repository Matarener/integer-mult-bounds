"""Authenticate and open the retained source closure.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(raw, pin):
    need(len(raw) == pin['size'], 'Exact source size: '+pin['path'])
    need(sha256(raw).hexdigest() == pin['sha256'], 'Exact source SHA256: '+pin['path'])
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
         'Exact source Git blob: '+pin['path'])


@contextmanager
def sources():
    pins = json.loads((HERE/'SOURCES.json').read_bytes())
    for pin in pins['direct_sources']:
        authenticate((HERE/pin['local_path']).read_bytes(), pin)
    archive = pins['source_archive']
    path = HERE/archive['local_path']
    need(sha256(path.read_bytes()).hexdigest() == archive['sha256'], 'Exact source archive')
    members = {p['path']: p for p in pins['archived_files']}
    need(len(members) == len(pins['archived_files']) == 20, 'Exact source inventory')
    with tempfile.TemporaryDirectory(prefix='p104-second-block-source-') as directory:
        root = Path(directory)
        with tarfile.open(path, 'r:') as bundle:
            seen = set()
            for member in bundle.getmembers():
                name = PurePosixPath(member.name)
                need(member.isfile() and not name.is_absolute() and '..' not in name.parts
                     and '\\' not in member.name and ':' not in member.name,
                     'Regular relative source file')
                need(member.name in members and member.name not in seen, 'Unique declared source file')
                seen.add(member.name)
                raw = bundle.extractfile(member).read()
                authenticate(raw, members[member.name])
                target = root.joinpath(*name.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        need(seen == set(members), 'Complete source archive')
        yield root/archive['package']
