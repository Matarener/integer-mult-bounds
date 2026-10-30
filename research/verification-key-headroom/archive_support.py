"""Archive integrity and bounded value transport; no scientific module imports.

Chris R / Clear1nsight with substantial OpenAI Codex/Astra assistance.
Apache-2.0. Hash tables and source-bound replay are standard techniques.
"""
from hashlib import sha256
import gzip
import io
import pickletools
import json
from pathlib import Path, PurePosixPath
import pickle
import shutil
import sys
import tarfile
import types

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
CONTEXT=ROOT/'context'
STAGE='stages/actual-key-pilot-v1'
OFFICIAL_PATH='research/c-verification-feasibility/inputs/PR5864.tar'
OFFICIAL_SHA='7b142567acacac5182045bf8daa8780e916661c2cf343dbf81b13c88ead85d64'
OFFICIAL_HEAD='3f15c943e4ad6479f03e674c80fff1269a16ccfe'
CALLS=2579750
BLOCK=4096


def need(ok,reason):
    if not ok:raise ValueError(reason)


def digest_file(path):
    h=sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def regular(root,relative):
    part=PurePosixPath(relative)
    need(not part.is_absolute() and part.parts and all(x not in ('.','..') for x in part.parts),'canonical archive path')
    path=root
    for component in part.parts:
        path=path/component
        need(not path.is_symlink(),'no symlink: '+relative)
    need(path.is_file(),'regular file: '+relative)
    return path


def authenticate():
    manifest=json.loads((ROOT/'CODE-SOURCES.json').read_text())
    need(manifest['schema_version']==1,'code manifest version')
    for relative,pin in manifest['files'].items():
        path=regular(ROOT,relative)
        need(path.stat().st_size==pin['bytes'] and digest_file(path)==pin['sha256'],'exact protected bytes: '+relative)
        need(bool(path.stat().st_mode&0o111)==bool(pin['git_mode']&0o111),'Git executable mode: '+relative)
    expected_code={p for p in manifest['files'] if Path(p).suffix in ('.py','.c','.inc')}
    live_code={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.py','.c','.inc')}
    need(live_code==expected_code,'complete protected source-code census')
    official=regular(REPO,OFFICIAL_PATH)
    need(digest_file(official)==OFFICIAL_SHA,'official PR5864 immutable input')
    return manifest


def inventory(root):
    need(not any(p.is_symlink() for p in root.rglob('*')),'no context symlinks')
    return {str(p.relative_to(root)):dict(sha256=digest_file(p),mode=p.stat().st_mode&0o777,bytes=p.stat().st_size)
            for p in sorted(root.rglob('*')) if p.is_file()}


def reconstruct(destination):
    destination=destination.resolve()
    need(not destination.is_relative_to(REPO),'external reconstruction directory')
    need(not destination.exists(),'fresh reconstruction directory')
    shutil.copytree(CONTEXT,destination)
    # Read-only Git-free exports may have 0555 directories and 0444 files.
    # Change only this fresh external copy, never the published source tree.
    for directory in (destination,*destination.rglob('*')):
        if directory.is_dir():directory.chmod(0o755)
    measured=json.loads((ROOT/'MEASURED-CONTEXT.json').read_text())
    for relative,pin in measured['original_baseline_files'].items():
        (destination/'baseline-public'/relative).chmod(pin['mode'])
    target=destination/STAGE
    for relative,pin in measured['original_baseline_files'].items():
        out=target/'baseline-public'/relative
        if relative not in measured['baseline_overlay']:
            out.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(destination/'baseline-public'/relative,out)
    # Git only preserves executable mode. Restore the measured 0664 stage modes
    # from the retained census, in this fresh external tree only.
    for relative,pin in measured['measured_stage_files'].items():
        (target/relative).chmod(pin['mode'])
    return destination


def validate_context(context):
    measured=json.loads((ROOT/'MEASURED-CONTEXT.json').read_text())
    need(inventory(context/'baseline-public')==measured['original_baseline_files'],'all 164 original baseline bytes/modes')
    need(inventory(context/STAGE)==measured['measured_stage_files'],'all 177 measured stage bytes/modes')
    stage=context/STAGE
    receipt=json.loads((stage/'SOURCE-EDITS.json').read_text())
    need(receipt['changed_baseline_files']==['native_cache.c','NATIVE-SOURCE.json'],'two declared capture overlays')
    for relative,pin in receipt['original_inventory'].items():
        original=regular(context/'baseline-public',relative);copied=regular(stage/'baseline-public',relative)
        need(digest_file(original)==pin['sha256'] and original.stat().st_mode&0o777==pin['mode'],'original baseline source receipt')
        need(copied.stat().st_mode&0o777==pin['mode'],'copied baseline mode')
        if relative not in receipt['changed_baseline_files']:need(digest_file(copied)==pin['sha256'],'unchanged copied baseline bytes')
    raw=(stage/'baseline-public/native_cache.c').read_bytes()
    need(sha256(raw).hexdigest()==receipt['diagnostic_native_sha256'],'capture C exact pin')
    need(json.loads((stage/'baseline-public/NATIVE-SOURCE.json').read_text())==dict(sha256=receipt['diagnostic_native_sha256']),'capture cold-loader pin')
    restored=raw.decode()
    for edit in reversed(receipt['edits']):
        need(restored.count(edit['after'])==1,'unique inverse diagnostic seam')
        restored=restored.replace(edit['after'],edit['before'])
    need(sha256(restored.encode()).hexdigest()==receipt['original_native_sha256'],'capture C reverses to entire original C')
    # Resolve every old path convention and pin without importing old code.
    frozen=json.loads((stage/'FROZEN-SOURCE.json').read_text())
    for directory,key in ((stage,'files_sha256'),(context,'reference_files_sha256')):
        for relative,pin in frozen[key].items():need(digest_file(regular(directory,relative))==pin,'frozen source/reference: '+relative)
    return dict(original_baseline_files=164,measured_stage_files=177,all_bytes_and_modes_equal=True,exact_C_inverse=True)


def official_baseline(context):
    prefix='research/fraction-native-qualification/'
    archive=regular(REPO,OFFICIAL_PATH)
    need(digest_file(archive)==OFFICIAL_SHA,'official input before tar read')
    with tarfile.open(archive,'r:') as stream:
        members=stream.getmembers();names={m.name for m in members}
        need(len(members)==len(names)==164 and all(m.isfile() for m in members),'complete regular official export')
        exported=stream.extractfile('.research-export.json').read()
        receipt=json.loads(exported)
        need(receipt['commit']==OFFICIAL_HEAD and receipt['package']=='research/fraction-native-qualification','official export lineage')
        rows=receipt['files'];need(len(rows)==163,'official source file count')
        need(names=={r['path'] for r in rows}|{'.research-export.json'},'official export exact census')
        need((context/'baseline-public/.research-export.json').read_bytes()==exported,'original complete export receipt')
        for row in rows:
            name=row['path'];need(name.startswith(prefix),'official package prefix')
            member=stream.getmember(name)
            need(member.size==row['size'] and member.mode&0o777==row['mode'],'official member size/mode')
            raw=stream.extractfile(member).read()
            need(len(raw)==row['size'] and sha256(raw).hexdigest()==row['sha256'],'official payload pin')
            path=regular(context/'baseline-public',name[len(prefix):])
            need(path.read_bytes()==raw and path.stat().st_mode&0o777==row['mode'],'retained baseline equals official export')
    return dict(official_export_files=163,retained_export_receipt=True,head=OFFICIAL_HEAD,sha256=OFFICIAL_SHA)


class PlainUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        raise ValueError('class/global objects are outside the pinned plain corpus format')


# Only plain protocol-5 structure is needed. Scan each bounded object before
# deserializing; no GLOBAL/STACK_GLOBAL/REDUCE/BUILD/OBJ/INST/NEWOBJ/EXT forms.
PLAIN_OPS={'PROTO','FRAME','EMPTY_DICT','MEMOIZE','MARK','SHORT_BINUNICODE',
 'BINUNICODE','BINUNICODE8','BININT','BININT1','BININT2','LONG1','LONG4',
 'NEWFALSE','NEWTRUE','SETITEMS','SETITEM','EMPTY_TUPLE','TUPLE','TUPLE1',
 'TUPLE2','TUPLE3','BINGET','LONG_BINGET','STOP'}


class BoundedObjectReader:
    def __init__(self,stream):self.stream=stream;self.raw=io.BytesIO();self.size=0
    def tell(self):return self.size
    def save(self,value):
        self.size+=len(value);need(self.size<=64*1024*1024,'bounded single pickle object')
        self.raw.write(value);return value
    def read(self,count):
        need(type(count) is int and 0<=count<=64*1024*1024-self.size,'bounded pickle operand')
        return self.save(self.stream.read(count))
    def readline(self):return self.save(self.stream.readline(64*1024*1024-self.size+1))


def plain_object(stream):
    reader=BoundedObjectReader(stream);first=True
    for opcode,argument,position in pickletools.genops(reader):
        need(opcode.name in PLAIN_OPS,'plain-only pickle opcode: '+opcode.name)
        if first:
            need(opcode.name=='PROTO' and argument==5,'explicit protocol 5')
            first=False
    need(not first,'one complete pickle object')
    # genops consumes exactly through STOP without unpickler read-ahead.
    # A fresh unpickler gives each bounded object a fresh memo.
    return PlainUnpickler(io.BytesIO(reader.raw.getvalue())).load()


def corpus_blocks(path,transport_pin):
    # Only committed pinned data or a fresh source-pinned replay's own output.
    need(digest_file(path)==transport_pin,'authenticate corpus container before unpickling')
    expected=json.loads((ROOT/'data/DATA.json').read_text())['actual_corpus']['format']
    with gzip.open(path,'rb') as stream:
        need(plain_object(stream)==expected,'complete corpus format/header')
        for start in range(0,CALLS,BLOCK):
            block=plain_object(stream)
            need(type(block) is tuple and len(block)==min(BLOCK,CALLS-start),'complete bounded corpus block')
            for key in block:
                need(type(key) is tuple and len(key)==7 and all(type(x) is int for x in key),'seven exact signed integer fields')
            yield block
        need(stream.read(1)==b'','strict decompressed EOF after final object')


def read_plain_gzip(path,pin):
    need(digest_file(path)==pin['transport_sha256'],'committed transport SHA')
    with gzip.open(path,'rb') as stream:raw=stream.read(pin['uncompressed_bytes']+1)
    need(len(raw)==pin['uncompressed_bytes'] and sha256(raw).hexdigest()==pin['uncompressed_sha256'],'authoritative complete decompressed payload')
    return raw


def source_module(name,path):
    need(name not in sys.modules,'fresh owned module namespace: '+name)
    relative=str(path.relative_to(ROOT));pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
    raw=path.read_bytes();need(sha256(raw).hexdigest()==pins[relative]['sha256'],'authenticate module bytes before execution')
    module=types.ModuleType(name);module.__file__=str(path);module.__package__=''
    sys.modules[name]=module
    try:exec(compile(raw,str(path),'exec'),module.__dict__)
    except BaseException:sys.modules.pop(name,None);raise
    return module
