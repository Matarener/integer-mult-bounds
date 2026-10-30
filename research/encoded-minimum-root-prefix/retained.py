"""Load the exact historical caller in its own source tree. Apache-2.0."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
_temporary=None
_ready=None


def activate():
    global _temporary,_ready
    if _ready is not None:
        return _ready
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for name in ('source-snapshot.tar','SOURCE-INDEX.json'):
        row=next(r for r in manifest['files'] if r['path'].endswith('/'+name))
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('source hash: '+name)
    entries=json.loads((HERE/'SOURCE-INDEX.json').read_text())
    expected={r['path']:r for r in entries}
    if len(expected)!=len(entries):
        raise ValueError('distinct retained source paths')
    if 'cohort' in sys.modules:
        raise ValueError('cold retained root namespace required')
    _temporary=tempfile.TemporaryDirectory(prefix='encoded-root-source-')
    root=Path(_temporary.name)
    seen=set()
    with tarfile.open(HERE/'source-snapshot.tar','r:') as archive:
        for entry in archive:
            path=PurePosixPath(entry.name)
            if path.is_absolute() or '..' in path.parts or not entry.isfile() or entry.name in seen or entry.name not in expected:
                raise ValueError('exact regular retained source member')
            seen.add(entry.name)
            raw=archive.extractfile(entry).read();row=expected[entry.name]
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if len(raw)!=row['size'] or hashlib.sha256(raw).hexdigest()!=row['sha256'] or blob!=row['git_blob']:
                raise ValueError('retained source member hash')
            dest=root/entry.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);dest.chmod(0o444)
    if seen!=set(expected):
        raise ValueError('complete retained source tree')
    sys.path.insert(0,str(root/'research/physical-complex-controller'))
    import cohort
    cohort.activate()
    _ready=(root,cohort)
    return _ready
