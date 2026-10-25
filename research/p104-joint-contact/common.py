"""Authenticate and open the retained Git-free PR5545 source closure.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
from pathlib import Path,PurePosixPath
import gzip,importlib.util,json,sys,tarfile,tempfile

HERE=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:
        raise ValueError(why)

@contextmanager
def supplier():
    pins=json.loads((HERE/'SOURCES.json').read_bytes())['retained_source']
    path=HERE/'inputs'/Path(pins['path']).name
    raw=path.read_bytes()
    need(sha256(raw).hexdigest()==pins['sha256'],'Retained PR5545 capsule byte pin')
    with tempfile.TemporaryDirectory(prefix='p104-joint-contact-')as tmp:
        root=Path(tmp)
        with tarfile.open(fileobj=BytesIO(gzip.decompress(raw)),mode='r:')as archive:
            members=archive.getmembers()
            names=[m.name for m in members]
            need(len(names)==len(set(names)),'Unique retained source paths')
            for member in members:
                name=PurePosixPath(member.name)
                need(member.isfile()and not name.is_absolute()and '..'not in name.parts,'Regular retained source path')
                target=root/member.name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        manifest_raw=(root/'.research-export.json').read_bytes()
        need(sha256(manifest_raw).hexdigest()==pins['export_manifest_sha256'],'Exact official export inventory')
        manifest=json.loads(manifest_raw)
        need(manifest['commit']==pins['commit']and manifest['package']=='research/p104-full-frame-contact','Exact predecessor head and package')
        need(len(manifest['files'])==pins['files']==33,'Full predecessor closure')
        need(set(names)=={'.research-export.json'}|{r['path']for r in manifest['files']},'No omitted or extra dependency')
        for row in manifest['files']:
            raw=(root/row['path']).read_bytes()
            need(len(raw)==row['size']and sha256(raw).hexdigest()==row['sha256'],'Source file '+row['path'])
        source=root/'research/p104-productive-controller'
        spec=importlib.util.spec_from_file_location('local',source/'local.py')
        L=importlib.util.module_from_spec(spec);sys.modules['local']=L;spec.loader.exec_module(L)
        C=L.load(source/'caller.py','p104_joint_caller')
        R=L.load(root/'research/p104-full-frame-contact/construct.py','p104_joint_predecessor')
        yield root,L,C,R
