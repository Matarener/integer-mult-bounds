#!/usr/bin/env python3
"""Memory-bounded runtime adapter for the pinned whole-owner auditor.

Scientific source fa3488b62... is compiled in memory, without changing any
audited input, assertion, mutation function, or report/export construction.
Only dead data lifetime and the mechanism for isolating mutations change.

The original audit_fast.py's pickle deepcopy remains the portable fallback.
POSIX uses one copy-on-write child per mutation, in the original order. Only
the original expected exceptions thrown by audit(q) count as rejection;
accepted mutants, mutator errors, unexpected exceptions and signals fail.

Usage: audit_fast.py AUDIT_SCRIPT BASE HOSTED REPORT [--mutation-controls]
Diagnostics go to stderr and REPORT.parent/RUNTIME-PROGRESS.jsonl. They are
separate from the byte-identical scientific reports. Apache-2.0.
"""
from __future__ import annotations
import ast,copy,gzip,hashlib,json,os,pickle,sys,time,traceback
from collections import Counter
from pathlib import Path
try:import resource
except ImportError:resource=None

AUDIT_SHA256='fa3488b62efdf8a0c37de0ca0caba587b4b036c5f068e002eb04c71c12b9e9b4'
EMIT_SHA256='549603ca6d28b163a43b2dfaaaa788161c73d7952ab9190289407caca5418c71'
EXPECTED=(AssertionError,KeyError,IndexError,ValueError,TypeError)
_original_deepcopy=copy.deepcopy
_started=time.monotonic()
_record=None
_context='initialization'

def max_rss_kib():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource is not None else None

def progress(stage,**fields):
    row=dict(stage=stage,context=_context,pid=os.getpid(),seconds=round(time.monotonic()-_started,6),
             max_rss_kib=max_rss_kib(),**fields)
    line=json.dumps(row,sort_keys=True)
    print('AUDIT_RUNTIME '+line,file=sys.stderr,flush=True)
    if _record is not None:
        with _record.open('a',encoding='utf-8') as stream:stream.write(line+'\n')

def fast_copy(value,memo=None):
    if memo is not None:return _original_deepcopy(value,memo)
    return pickle.loads(pickle.dumps(value,pickle.HIGHEST_PROTOCOL))

def gzip_sha(path):
    digest=hashlib.sha256()
    with gzip.open(path,'rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()

def fork_control(name,mut,template,audit):
    """Run exactly one original mutator and auditor in an isolated child."""
    global _context
    if not hasattr(os,'fork'):
        q=fast_copy(template);mut(q)  # mutator exceptions are never rejections
        try:audit(q)
        except EXPECTED:return
        raise AssertionError('ACCEPTED '+name)
    readfd,writefd=os.pipe();pid=os.fork()
    if pid==0:
        os.close(readfd);_context='control: '+name
        try:
            try:mut(template)
            except BaseException as error:
                result=dict(status='mutator_error',name=name,exception=type(error).__name__,detail=repr(error),traceback=traceback.format_exc())
            else:
                try:audit(template)
                except EXPECTED as error:
                    result=dict(status='rejected',name=name,expected_class=next(t.__name__ for t in EXPECTED if isinstance(error,t)),exception=type(error).__name__,detail=repr(error))
                except BaseException as error:
                    result=dict(status='unexpected_exception',name=name,exception=type(error).__name__,detail=repr(error),traceback=traceback.format_exc())
                else:result=dict(status='accepted',name=name)
            result['max_rss_kib']=max_rss_kib()
            payload=json.dumps(result,sort_keys=True).encode()
            while payload:
                count=os.write(writefd,payload);payload=payload[count:]
            os.close(writefd);os._exit(0)
        except BaseException:
            os._exit(120)
    os.close(writefd);chunks=[];length=0
    try:
        while True:
            chunk=os.read(readfd,65536)
            if not chunk:break
            chunks.append(chunk);length+=len(chunk)
            if length>1024*1024:raise RuntimeError('oversized control diagnostic')
    finally:os.close(readfd)
    waited,status=os.waitpid(pid,0)
    if waited!=pid or not os.WIFEXITED(status) or os.WEXITSTATUS(status)!=0:
        raise RuntimeError('control did not exit normally: '+name+' status='+str(status))
    try:result=json.loads(b''.join(chunks))
    except (ValueError,UnicodeError) as error:raise RuntimeError('missing control rejection receipt: '+name) from error
    if result.get('name')!=name or result.get('status')!='rejected' or result.get('expected_class') not in {t.__name__ for t in EXPECTED}:
        raise AssertionError('control did not produce the original expected rejection: '+json.dumps(result,sort_keys=True))
    progress('mutation-rejected',name=name,exception=result['exception'],child_max_rss_kib=result['max_rss_kib'])

ORIGINAL_REJECT="""def reject(name,mut):
 if '--mutation-controls' not in sys.argv[4:]:return
 q=copy.deepcopy(ct);mut(q)
 try:audit(q)
 except(AssertionError,KeyError,IndexError,ValueError,TypeError):controls.append(name)
 else:raise AssertionError('ACCEPTED '+name)
"""
FORK_REJECT="""def reject(name,mut):
 if '--mutation-controls' not in sys.argv[4:]:return
 _runtime_control(name,mut,ct,audit)
 controls.append(name)
"""

def transform(raw,control_mode='fork'):
    assert hashlib.sha256(raw).hexdigest()==AUDIT_SHA256,'exact scientific auditor source pin'
    source=raw.decode().replace('\r\n','\n')
    tree=ast.parse(source)
    audit=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='audit')
    assert not any(isinstance(n,ast.Name) and n.id=='ct' for n in ast.walk(audit))
    assert [n.id for n in ast.walk(tree) if isinstance(n,ast.Name) and n.id=='touches']==['touches','touches']
    replacements=[
      ("parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz')",
       "_runtime_progress('parent-load-start')\nparent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz')\nfor _runtime_call in parent['calls']:del _runtime_call['owners'][224:]\ndel _runtime_call\n_runtime_progress('parent-loaded-and-unused-helper-owners-released')"),
      ("ct=read(OUT/'GLOBAL-TEMPLATE.json.gz');summary=read(OUT/'HOSTED.json')",
       "_runtime_progress('hosted-load-start')\nct=read(OUT/'GLOBAL-TEMPLATE.json.gz');summary=read(OUT/'HOSTED.json')\n_runtime_progress('hosted-loaded')"),
      (';touches=defaultdict(list)',''),
      ('touches[family].append((s,rep,h));',''),
      ("r=audit(ct);raw=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==summary['template_sha256'];",
       "_runtime_progress('positive-audit-start');r=audit(ct);_runtime_progress('positive-audit-pass');assert _runtime_gzip_sha(OUT/'GLOBAL-TEMPLATE.json.gz')==summary['template_sha256'];"),
      (" for call in t['calls']:"," _runtime_call_count=0\n for call in t['calls']:\n  _runtime_call_count+=1\n  if _runtime_call_count%360==0:_runtime_progress('audited-invocations',invocations=_runtime_call_count)"),
    ]
    if control_mode=='fork':replacements.append((ORIGINAL_REJECT,FORK_REJECT))
    else:assert control_mode=='pickle'
    for old,new in replacements:
        assert source.count(old)==1,'unique runtime substitution: '+old[:80]
        source=source.replace(old,new)
    # Every scientific assertion is retained in its original order, except
    # the digest expression whose argument is now streamed exactly.
    old_asserts=[ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Assert)]
    new_asserts=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Assert)]
    removed=Counter(old_asserts)-Counter(new_asserts);added=Counter(new_asserts)-Counter(old_asserts)
    assert sum(removed.values())==sum(added.values())==1
    assert 'raw' in next(iter(removed)) and '_runtime_gzip_sha' in next(iter(added))
    # Mutator calls and their literal bodies are byte-for-byte the source.
    old_calls=[ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='reject']
    new_calls=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='reject']
    assert old_calls==new_calls
    return source,dict(source_sha256=AUDIT_SHA256,transformed_sha256=hashlib.sha256(source.encode()).hexdigest(),
        preserved_scientific_assertions=len(old_asserts)-1,equivalent_streamed_digest_assertions=1,
        preserved_mutator_call_sites=len(old_calls),control_mode=control_mode,substitutions=len(replacements))

def main():
    global _record,_context
    assert __debug__,'assertions must remain enabled'
    script=Path(sys.argv[1]).resolve();raw=script.read_bytes()
    if script.name=='emit_allcold.py':
        assert hashlib.sha256(raw).hexdigest()==EMIT_SHA256,'exact unchanged emitter source pin'
        copy.deepcopy=fast_copy
        sys.argv=sys.argv[1:];sys.path.insert(0,str(script.parent))
        exec(compile(raw.decode(),str(script),'exec'),dict(__file__=str(script),__name__='__main__'))
        return
    report=Path(sys.argv[4]).resolve()
    report.parent.mkdir(parents=True,exist_ok=True)
    _record=report.parent/'RUNTIME-PROGRESS.jsonl'
    mode=os.environ.get('AUDIT_RUNTIME_CONTROLS','fork' if hasattr(os,'fork') else 'pickle')
    source,receipt=transform(raw,mode)
    receipt['adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (report.parent/'RUNTIME-ADAPTER.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    copy.deepcopy=fast_copy
    sys.argv=sys.argv[1:];sys.path.insert(0,str(script.parent))
    context=dict(__file__=str(script),__name__='__main__',_runtime_progress=progress,_runtime_gzip_sha=gzip_sha,_runtime_control=fork_control)
    progress('adapter-start',**receipt)
    exec(compile(source,str(script),'exec'),context)
    _context='complete';progress('adapter-complete')

if __name__=='__main__':main()
