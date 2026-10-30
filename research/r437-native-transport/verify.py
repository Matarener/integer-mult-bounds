"""Read-only, source-authenticated replay; no foreign Git objects required."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(HERE))
from check_transport import need, main

def regular(path):
    need(path.is_file(), 'regular source file: '+str(path))
    need(all(not part.is_symlink() for part in (path,*path.parents)), 'no source symlink')

def authenticate():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    need(sources['base_commit']=='20ecf2891d80b5acf18d980b2164fb44ea7faa90','canonical base')
    for row in sources['files']:
        if row['usage']!='input':
            continue
        path=ROOT/row['path']; regular(path); data=path.read_bytes()
        need(sha256(data).hexdigest()==row['sha256'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'canonical source identity: '+row['path'])
    expected=set()
    for row in sources['retained']:
        path=HERE/row['path']; regular(path);data=path.read_bytes();expected.add(row['path'])
        need(len(data)==row['bytes'] and sha256(data).hexdigest()==row['sha256'] and
             sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
             'retained source identity: '+row['path'])
    observed={f.relative_to(HERE).as_posix() for f in (HERE/'inputs').rglob('*') if f.is_file()}
    need(expected==observed|{'adapter.py'},'complete retained source inventory')
    need('--write' not in sys.argv,'registered verification is read-only')

if __name__ == '__main__':
    authenticate()
    main()
