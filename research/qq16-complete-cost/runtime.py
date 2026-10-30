# SPDX-License-Identifier: Apache-2.0
"""Authenticate retained #4172 and canonical nested closure before execution.

Chris R / Clear1nsight with substantial OpenAI Codex assistance.
The original physical/numerical sources and all prior notices are unchanged.
"""
from pathlib import Path
import hashlib, io, json, sys, tarfile, tempfile, types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST_SHA='0efdb3b0a648bedf80b4f1e4f36b6bcfc76fd03f9626c700db4ce09476ee0025'
_temporary=None
_history=None
def need(ok,why):
    if not ok: raise ValueError(why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,'duplicate JSON key');result[key]=value
    return result
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def module(name,path):
    result=types.ModuleType(name);result.__file__=str(path)
    sys.modules[name]=result
    exec(compile(path.read_bytes(),str(path),'exec'),result.__dict__)
    return result
def authenticated_inputs():
    raw=(HERE/'inputs/PR4172-MANIFEST.json').read_bytes()
    need(sha(raw)==MANIFEST_SHA,'retained manifest integrity')
    manifest=parse(raw);archive=(HERE/'inputs/PR4172.tar').read_bytes()
    need(sha(archive)==manifest['archive_sha256'],'retained archive integrity')
    expected={row['path']:row['sha256'] for row in manifest['files']}
    need(len(expected)==len(manifest['files']),'duplicate retained path')
    files={}
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as source:
        for member in source:
            if member.isdir():continue
            need(member.isfile() and member.name in expected and member.name not in files,'retained member/path')
            need(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts,'safe retained path')
            raw=source.extractfile(member).read()
            need(sha(raw)==expected[member.name],'retained content integrity')
            files[member.name]=raw
    need(set(files)==set(expected),'complete retained archive')
    sources=parse(files['research/qq16-native-history/SOURCES.json'])
    for row in sources['files']:
        if row['usage']!='input':continue
        rel=row['path'];need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'canonical path')
        raw=(ROOT/rel).read_bytes()
        need(sha(raw)==row['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'canonical input integrity:'+rel)
        need(rel not in files,'canonical collision');files[rel]=raw
    return files
def cold():
    global _temporary,_history
    need(_temporary is None,'one cold source cohort per process')
    files=authenticated_inputs()
    _temporary=tempfile.TemporaryDirectory(prefix='qq16-cost-')
    root=Path(_temporary.name)
    for rel,raw in files.items():
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    _history=module('qq16_history_runtime',root/'research/qq16-native-history/runtime.py')
    return _history.cold()
def predecessor():
    need(_temporary is not None,'cold cohort required')
    return Path(_temporary.name)/'research/qq16-native-history'
def cleanup():
    global _temporary
    if _history is not None:_history.cleanup()
    if _temporary is not None:_temporary.cleanup();_temporary=None
