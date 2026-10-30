"""Authenticate and prepare the unchanged official PR5757 source export."""
from contextlib import contextmanager
from hashlib import sha1, sha256
import json
from pathlib import Path
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = 'a3a4478938171072f7df7547f7b1e1d0ff080aa42083103450e7d02f509bfc26'
MANIFEST_SHA256 = '7be632febc51fa5040cdd06a86c1c4f8b95c2632cc885b49af05bba838b672be'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def payload():
    raw = (HERE / 'inputs/PR5757.tar').read_bytes()
    require(sha256(raw).hexdigest() == ARCHIVE_SHA256, 'Official export hash')
    manifest_raw = (HERE / 'INPUT-MANIFEST.json').read_bytes()
    require(sha256(manifest_raw).hexdigest() == MANIFEST_SHA256, 'Complete manifest hash')
    manifest = json.loads(manifest_raw)
    rows = {r['path']: r for r in manifest['files']}
    require(len(rows) == len(manifest['files']) == 54, 'Complete source inventory')
    contents = {}
    with tarfile.open(HERE / 'inputs/PR5757.tar', 'r:') as stream:
        members = stream.getmembers()
        require(len(members) == 55 and {m.name for m in members} == set(rows) | {'.research-export.json'},
                'Exact archive members')
        for member in members:
            require(member.isfile() and 0 <= member.size <= 4 * 1024**2, 'Regular bounded archive member')
            data = stream.extractfile(member).read()
            if member.name == '.research-export.json':
                require(json.loads(data)['commit'] == manifest['source_head'], 'Official export head')
                continue
            row = rows[member.name]
            require(len(data) == row['bytes'] and sha256(data).hexdigest() == row['sha256'], 'Exact member hash')
            require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
                    'Exact member blob')
            parts = Path(member.name).parts
            require(parts and not Path(member.name).is_absolute() and '..' not in parts, 'Canonical member path')
            contents[member.name] = data
    return contents


def inventory(root):
    require(not root.is_symlink(), 'Regular source root')
    return {p.relative_to(root).as_posix(): [sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777]
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


@contextmanager
def prepared():
    contents = payload()
    with tempfile.TemporaryDirectory(prefix='single-pass-source-') as temporary:
        root = Path(temporary) / 'source'
        root.mkdir()
        try:
            for name, raw in contents.items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
                p.chmod(0o444)
            for p in root.rglob('*'):
                if p.is_dir():
                    p.chmod(0o555)
            root.chmod(0o555)
            before = inventory(root)
            yield root
            require(inventory(root) == before, 'Source bytes and modes unchanged')
            require(not any(p.is_symlink() for p in root.rglob('*')), 'No source links')
        finally:
            # This only disposes of the private temporary export, never committed inputs.
            for p in [root, *root.rglob('*')]:
                if p.is_dir():
                    p.chmod(0o755)
