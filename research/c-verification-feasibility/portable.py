"""Reconstruct exact measured source layout from the official frozen export.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
Only immutable source bytes are reused. No scientific answers or PASS receipts
are reused. Every fresh invocation pays extraction, binding, compile and checks.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = '7b142567acacac5182045bf8daa8780e916661c2cf343dbf81b13c88ead85d64'
HEAD = '3f15c943e4ad6479f03e674c80fff1269a16ccfe'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unpack(destination):
    archive = HERE / 'inputs' / 'PR5864.tar'
    require(not archive.is_symlink() and sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            'exact official PR5864 export')
    with tarfile.open(archive, 'r:') as stream:
        members = stream.getmembers()
        require(len(members) == 164 and len({m.name for m in members}) == 164,
                'unique complete official export')
        receipt = json.loads(stream.extractfile('.research-export.json').read())
        require(receipt['commit'] == HEAD and len(receipt['files']) == 163,
                'exact published source head and file census')
        rows = {row['path']: row for row in receipt['files']}
        require(set(rows) | {'.research-export.json'} == {m.name for m in members},
                'exact declared export members')
        for member in members:
            path = Path(member.name)
            require(member.isfile() and 0 <= member.size <= 8 * 1024**2 and
                    not path.is_absolute() and '..' not in path.parts,
                    'bounded regular safe member')
            raw = stream.extractfile(member).read()
            if member.name == '.research-export.json':
                relative = path
            else:
                row = rows[member.name]
                require(len(raw) == row['size'] and sha256(raw).hexdigest() == row['sha256']
                        and row['mode'] in (0o644, 0o755), 'exact source bytes and mode declaration')
                relative = path.relative_to('research/fraction-native-qualification')
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o444)


def inventory(root):
    return {str(p.relative_to(root)): [sha256(p.read_bytes()).hexdigest(), p.stat().st_mode & 0o777]
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


@contextmanager
def prepared(mode):
    require(mode in ('baseline', 'integer', 'rational', 'complete-B', 'complete-C'), 'known replay scope')
    with tempfile.TemporaryDirectory(prefix='c-verification-screen-') as temporary:
        root = Path(temporary)
        baseline = root / 'baseline-public'
        baseline.mkdir()
        unpack(baseline)
        before = inventory(baseline)
        stage = root / 'stages' / 'integer-complete-v1'
        stage.parent.mkdir()
        stage.mkdir()
        for p in (HERE / 'integer').iterdir():
            if p.is_file():
                shutil.copy2(p, stage / p.name)
        for name in ('baseline_full.py', 'candidate_full.py'):
            shutil.copy2(HERE / 'drivers' / name, stage / name)
        if mode == 'rational':
            stage = root / 'stages' / 'rational-v2'
            stage.mkdir()
            for p in (HERE / 'rational').iterdir():
                if p.is_file():
                    shutil.copy2(p, stage / p.name)
            package = stage / 'package'
            shutil.copytree(baseline, package)
            source = package / 'native_cache.c'
            source.chmod(0o644)
            source.write_bytes((stage / 'native_bulk.c').read_bytes())
            source_manifest = package / 'NATIVE-SOURCE.json'
            manifest = json.loads(source_manifest.read_text())
            manifest['sha256'] = sha256(source.read_bytes()).hexdigest()
            source_manifest.chmod(0o644)
            source_manifest.write_text(json.dumps(manifest, indent=2) + '\n')
        try:
            yield root, baseline, stage
        finally:
            require(inventory(baseline) == before and
                    not any(p.is_symlink() for p in baseline.rglob('*')),
                    'all original PR5864 baseline bytes and modes remain unchanged')

