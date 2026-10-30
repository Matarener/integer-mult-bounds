"""Authenticate the official PR5608 export before importing its source closure.

Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
Source-export format and payload checks follow the retained repository exporter.
"""
from contextlib import contextmanager
from hashlib import sha256,sha1
from pathlib import Path,PurePosixPath
import gzip,importlib.util,io,json,sys,tarfile,tempfile
HERE=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
@contextmanager
def sources():
    pins=read(HERE/'SOURCES.json')
    for p in pins['external_inputs']:
        raw=(HERE/p['local_path']).read_bytes()
        need(sha256(raw).hexdigest()==p['sha256'],'Pinned source SHA256 '+p['local_path'])
        need(sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==p['git_blob'],'Pinned source blob '+p['local_path'])
    pin=pins['source_export'];raw=(HERE/pin['local_path']).read_bytes()
    need(sha256(raw).hexdigest()==pin['sha256'],'Exact published export archive')
    with tempfile.TemporaryDirectory(prefix='p104-composed-source-') as directory:
        root=Path(directory)
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as bundle:
            names=[]
            for m in bundle.getmembers():
                p=PurePosixPath(m.name)
                need(m.isfile() and not p.is_absolute() and '..' not in p.parts and '\\' not in m.name and ':' not in m.name,'Regular relative source file')
                need(m.name not in names,'Unique export path');names.append(m.name)
                target=root.joinpath(*p.parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(bundle.extractfile(m).read())
        manifest=read(root/'.research-export.json')
        need(manifest['commit']==pin['commit'] and len(manifest['files'])==pin['files'],'Exact published source inventory')
        need(set(names)=={'.research-export.json'}|{r['path'] for r in manifest['files']},'No omitted or extra source payload')
        for r in manifest['files']:
            b=(root/r['path']).read_bytes();need(len(b)==r['size'] and sha256(b).hexdigest()==r['sha256'],'Authenticated source payload '+r['path'])
        package=root/pin['package']
        common=load(package/'common.py','retained_source_common')
        with common.closure() as framework:yield package,framework
