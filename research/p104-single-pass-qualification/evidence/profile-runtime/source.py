"""Authenticate the unchanged complete PR5831 export before importing it."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
BUNDLE_SHA256 = '6ad8d8e0463e8e6ea8d503610c3f9ec38108f16092bc479bc1cb6f48683f6ab6'
SOURCE_HEAD = '7c5eb98e7439d778141d63e801e53d4cd7e1d587'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def payload(archive=None):
    archive = HERE / 'inputs/PR5831.tar' if archive is None else archive
    require(sha256(archive.read_bytes()).hexdigest() == BUNDLE_SHA256, 'Exact PR5831 bundle')
    with tarfile.open(archive, 'r:') as stream:
        members = stream.getmembers()
        require(len(members) == 14 and len({m.name for m in members}) == 14, 'Complete unique baseline bundle')
        require(all(m.isfile() and 0 <= m.size <= 8 * 1024**2 for m in members), 'Regular bounded baseline members')
        receipt = json.loads(stream.extractfile('.research-export.json').read())
        require(receipt['commit'] == SOURCE_HEAD, 'Exact baseline export head')
        rows = {r['path']: r for r in receipt['files']}
        require(len(rows) == len(receipt['files']) == 13, 'Complete baseline file census')
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
    with tempfile.TemporaryDirectory(prefix='precision-linux-source-') as temporary:
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
            yield root / 'research/p104-integer-error-replay'
            after = {str(p.relative_to(root)): [sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777]
                     for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
            require(after == before and not any(p.is_symlink() for p in root.rglob('*')), 'Baseline export unchanged')
        finally:
            for path in [root, *root.rglob('*')]:
                if path.is_dir():
                    path.chmod(0o755)
