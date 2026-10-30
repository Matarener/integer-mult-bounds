#!/usr/bin/env python3
"""Bounded failure-mode checks for the exact runtime isolation boundary."""
from __future__ import annotations
import argparse,contextlib,gzip,hashlib,importlib.util,io,json,os,signal,tempfile
from pathlib import Path

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runtime_adapter',P/'audit_fast.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--audit-script',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=P/'FIXTURES.json')
    args=parser.parse_args();raw=args.audit_script.read_bytes();results=[]
    for mode in ('fork','pickle'):
        source,receipt=a.transform(raw,mode)
        assert source.split('\nreport=dict(',1)[1]==raw.decode().split('\nreport=dict(',1)[1]
        compile(source,str(args.audit_script),'exec')
        results.append(dict(check='pinned transformation, unchanged reports and mutators',mode=mode,receipt=receipt))

    template={'aliased':[]};template['other']=template['aliased']
    untouched={'independent':[3]}
    def mut(q):q['aliased'].append(7)
    def require_mutated(q):
        if not(q['other']==[7] and q['aliased'] is q['other']):
            raise RuntimeError('fixture aliasing mismatch must not count as expected audit rejection')
        if untouched!={'independent':[3]}:
            raise RuntimeError('fixture global mismatch must not count as expected audit rejection')
    with contextlib.redirect_stderr(io.StringIO()):
        for exception in a.EXPECTED:
            def audit(q,exception=exception):
                require_mutated(q)
                raise exception('intended audit rejection')
            a.fork_control('expected '+exception.__name__,mut,template,audit)
            assert template=={'aliased':[],'other':[]}
            results.append(dict(check='expected audit exception',exception=exception.__name__,status='rejected'))

        def require_failure(name,mutation,audit):
            try:a.fork_control(name,mutation,template,audit)
            except (AssertionError,RuntimeError) as error:
                results.append(dict(check=name,status='fails closed',parent_exception=type(error).__name__))
            else:raise AssertionError('unsafe fixture accepted '+name)

        require_failure('accepted mutant fails',mut,require_mutated)
        def unexpected(q):raise RuntimeError('not one of the five original expected classes')
        require_failure('unexpected audit exception fails',mut,unexpected)
        for exception in a.EXPECTED:
            def bad_mut(q,exception=exception):raise exception('mutator error is outside rejection handler')
            require_failure('mutator '+exception.__name__+' fails',bad_mut,require_mutated)
        if hasattr(os,'fork'):
            require_failure('signalled child fails',lambda q:os.kill(os.getpid(),signal.SIGTERM),require_mutated)
            require_failure('nonzero child exit fails',lambda q:os._exit(23),require_mutated)
            require_failure('missing rejection receipt fails',lambda q:os._exit(0),require_mutated)
    assert template['aliased'] is template['other'] and template['other']==[]
    assert untouched=={'independent':[3]}
    results.append(dict(check='parent aliasing and separate globals preserved',status='PASS'))

    args.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gzip-fixture-',dir=args.out.parent) as td:
        path=Path(td)/'input.json.gz';payload=b'{"same_decompressed_bytes":true}\n'*400000
        path.write_bytes(gzip.compress(payload,mtime=0))
        assert a.gzip_sha(path)==hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()
    results.append(dict(check='streamed gzip digest equals exact decompressed digest across chunk boundary',status='PASS'))
    result=dict(status='PASS_RUNTIME_ADAPTER_FAILURE_MODES',adapter_sha256=hashlib.sha256((P/'audit_fast.py').read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(raw).hexdigest(),checks=results)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],len(results),'checks',args.out)

if __name__=='__main__':main()
