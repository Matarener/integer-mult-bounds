"""Authenticate the unchanged complete PR5818 export before importing it."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
BUNDLE_SHA256 = 'f166f27e7c247315e852f78e30b2d348e9b66518645b783b5344a6767d87e7cc'
SOURCE_HEAD = 'a0171b8d2f942cdfc5295307548fe484c570b1ba'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def payload():
    archive = HERE / 'inputs/PR5818.tar'
    require(sha256(archive.read_bytes()).hexdigest() == BUNDLE_SHA256, 'Exact PR5818 bundle')
    with tarfile.open(archive, 'r:') as stream:
        members = stream.getmembers()
        require(len(members) == 46 and len({m.name for m in members}) == 46, 'Complete unique baseline bundle')
        require(all(m.isfile() and 0 <= m.size <= 8 * 1024**2 for m in members), 'Regular bounded baseline members')
        receipt = json.loads(stream.extractfile('.research-export.json').read())
        require(receipt['commit'] == SOURCE_HEAD, 'Exact baseline export head')
        rows = {r['path']: r for r in receipt['files']}
        require(len(rows) == len(receipt['files']) == 45, 'Complete baseline file census')
        require({m.name for m in members} == set(rows) | {'.research-export.json'}, 'Exact baseline member set')
        contents = {}
        for member in members:
            path = Path(member.name)
            require(not path.is_absolute() and '..' not in path.parts and path.parts, 'Safe baseline path')
            raw = stream.extractfile(member).read()
            if member.name in rows:
                row = rows[member.name]
                require(len(raw) == row['size'] and sha256(raw).hexdigest() == row['sha256'], 'Exact baseline file bytes')
                require(row['mode'] in (0o644, 0o755), 'Regular baseline file mode')
            contents[member.name] = raw
    return contents


@contextmanager
def baseline():
    contents = payload()
    with tempfile.TemporaryDirectory(prefix='literal-setup-baseline-') as temporary:
        root = Path(temporary)
        try:
            for name, raw in contents.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                path.chmod(0o444)
            for path in root.rglob('*'):
                if path.is_dir():
                    path.chmod(0o555)
            before = {str(p.relative_to(root)): [sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777]
                      for p in root.rglob('*') if p.is_file()}
            yield root / 'research/selected-single-pass-qualification'
            after = {str(p.relative_to(root)): [sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777]
                     for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
            require(after == before and not any(p.is_symlink() for p in root.rglob('*')), 'Baseline export unchanged')
        finally:
            for path in [root, *root.rglob('*')]:
                if path.is_dir():
                    path.chmod(0o755)
