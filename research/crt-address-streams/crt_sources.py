"""Authenticate and open the actual PR3935 physical tensor/router cohort."""
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import base64
from hashlib import sha1, sha256
import importlib.util
import http.client
import json
import shutil
from pathlib import Path
import sys
import tempfile
import urllib.request
import urllib.error
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_active = None


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input' and sha256((ROOT/row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('source changed: '+row['path'])


def activate():
    authenticate()
    if _active is None:
        raise ValueError('authenticated CRT tensor cohort required')
    return _active


def source_manifest():
    manifest = json.loads((HERE/'NETWORK-SOURCES.json').read_text())
    if manifest['repository'] != 'CrocSwap/integer-mult-bounds' or manifest['head'] != '240597ed313fc2854c0462b23c89dc3bae72aaf5':
        raise ValueError('fixed CRT tensor source identity')
    expected = {'tensor_sources.py', 'tensor_router.py', 'tensor_fixture.py', 'tensor_plan.py',
                'inputs/chirp-export.tar.gz', 'inputs/expansion-export.tar.gz', 'inputs/headroom-source.tar', 'PROOF.md'}
    paths = {row['path'] for row in manifest['files']}
    if paths != {'research/physical-gaussian-tensor/'+name for name in expected} or len(paths) != len(manifest['files']):
        raise ValueError('exact CRT tensor dependency inventory')
    return manifest


def check_tree(root, manifest):
    root = Path(root)
    for row in manifest['files']:
        path = root/row['path']
        if not path.is_file() or path.is_symlink() or path.stat().st_size != row['size']:
            raise ValueError('complete frozen tensor source: '+row['path'])
        body = path.read_bytes()
        blob = sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()
        if sha256(body).hexdigest() != row['sha256'] or blob != row['git_blob']:
            raise ValueError('frozen tensor source changed: '+row['path'])


def fetch_tree(root, manifest):
    for row in manifest['files']:
        path = Path(root)/row['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        print('FETCH_PINNED_TENSOR '+row['path'],flush=True)
        headers={'User-Agent':'integer-mult-crt-source-replay'}
        if row['size'] > 1048576:
            # Bounded public byte ranges avoid partially delivered large raw
            # or base64 responses. Every range and the complete blob are checked.
            def part_at(start):
                end=min(row['size'],start+1048576)-1
                url=('https://raw.githubusercontent.com/'+manifest['repository']+'/'+manifest['head']+'/'+row['path']
                     +'?crt-bytes='+str(start)+'-'+str(end))
                request=urllib.request.Request(url,headers={**headers,'Range':'bytes='+str(start)+'-'+str(end)})
                for attempt in range(2):
                    try:
                        with urllib.request.urlopen(request,timeout=20) as response:
                            if response.status!=206 or response.headers.get('Content-Range')!='bytes '+str(start)+'-'+str(end)+'/'+str(row['size']):
                                raise ValueError('exact frozen tensor byte range')
                            part=response.read(end-start+1)
                        if len(part)!=end-start+1:
                            raise ValueError('complete frozen tensor byte range')
                        return part
                    except (urllib.error.URLError,TimeoutError,http.client.IncompleteRead):
                        if attempt:raise
            # Four bounded, independent ranges preserve order and exact pins.
            # Await every worker before publishing any source file.
            with ThreadPoolExecutor(max_workers=4) as executor:
                body=b''.join(executor.map(part_at,range(0,row['size'],1048576)))
        else:
            blob_url='https://api.github.com/repos/'+manifest['repository']+'/git/blobs/'+row['git_blob']
            with urllib.request.urlopen(urllib.request.Request(blob_url,headers=headers),timeout=30) as response:
                encoded=response.read(2*row['size']+16384)
            item=json.loads(encoded)
            if item.get('sha')!=row['git_blob'] or item.get('size')!=row['size'] or item.get('encoding')!='base64':
                raise ValueError('exact public tensor blob metadata')
            body=base64.b64decode(''.join(item['content'].split()),validate=True)
        if len(body) != row['size'] or sha256(body).hexdigest() != row['sha256']:
            raise ValueError('downloaded tensor source differs: '+row['path'])
        path.write_bytes(body)
    check_tree(root, manifest)


@contextmanager
def opened(source_root=None, fetch=False):
    global _active
    authenticate()
    if _active is not None or 'tensor_sources' in sys.modules or 'cardinal_counts' in sys.modules:
        raise ValueError('cold CRT tensor namespace')
    if source_root is not None and fetch:
        raise ValueError('choose an offline source root or a fresh fetched tree')
    manifest = source_manifest()
    if source_root is None and not fetch:
        raise ValueError('supply --source-root or explicitly permit --fetch')
    temporary = tempfile.TemporaryDirectory(prefix='crt-tensor-dependency-')
    private_root = Path(temporary.name)/'sources'
    old_path = sys.path[:]
    old_cache, old_write = sys.pycache_prefix, sys.dont_write_bytecode
    module = None
    try:
        if fetch:
            fetch_tree(private_root, manifest)
        else:
            check_tree(source_root, manifest)
            # Only declared source bytes enter sys.path. Ignore unpinned sibling
            # modules/caches in an offline cache; never modify that cache.
            for row in manifest['files']:
                target=private_root/row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(source_root)/row['path'], target)
        check_tree(private_root, manifest)
        sys.pycache_prefix = str(Path(temporary.name)/'empty-bytecode')
        sys.dont_write_bytecode = True
        package = private_root/'research/physical-gaussian-tensor'
        spec = importlib.util.spec_from_file_location('tensor_sources', package/'tensor_sources.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules['tensor_sources'] = module
        spec.loader.exec_module(module)
        with module.opened() as state:
            _active = state
            sys.path[:0] = [str(HERE), str(package)]
            try:
                yield state
            finally:
                _active = None
    finally:
        sys.path[:] = old_path
        sys.pycache_prefix, sys.dont_write_bytecode = old_cache, old_write
        if module is not None and sys.modules.get('tensor_sources') is module:
            del sys.modules['tensor_sources']
        if temporary is not None:
            temporary.cleanup()
