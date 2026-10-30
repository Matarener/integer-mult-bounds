"""Semantic rejection controls for the recorded-evidence checker, not source faults."""
from copy import deepcopy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import verify as V
import reproduce

def source_rejection_controls():
    """Exercise original source authentication on fresh deliberately damaged copies.

    Rejection must occur before any mathematical replay. A timeout, generic
    exception or different rejection site is a failed control.
    """
    cases={
        'engine':'research/exact-clifford-quadratic-replay/quadratic.py',
        'word':'research/p104-helper-subspace-splits/WORD.json.gz',
        'compiler':'research/p104-native-channel/vendor/clifford_exact.py'}
    outcomes={}
    for label,name in cases.items():
        with tempfile.TemporaryDirectory(prefix='linux5757-source-control-') as directory:
            work=Path(directory)/'copy'
            with contextlib.redirect_stdout(io.StringIO()):
                reproduce.prepare(work)
            source=work/'payload/source'
            path=source/name
            path.chmod(0o644)
            raw=bytearray(path.read_bytes())
            if label=='word':raw[0]^=1
            else:raw.extend(b'\n# SYNTHETIC_SOURCE_CUSTODY_CONTROL_ONLY\n')
            path.write_bytes(raw)
            env=os.environ.copy()
            for key in ('PYTHONPATH','PYTHONOPTIMIZE','PYTHONINSPECT','PYTHONSTARTUP'):
                env.pop(key,None)
            command=[sys.executable,'-I','-O','-B',str(source/'research/selected-quadratic-replay/run.py')]
            completed=subprocess.run(command,cwd=source,env=env,capture_output=True,timeout=10)
            message='ValueError: Selected adapter source hash: '+name
            V.require(completed.returncode==1 and completed.stdout==b'' and completed.stderr.decode().rstrip().endswith(message),'Exact pre-science source rejection: '+label)
            outcomes[label]={'exit':1,'predicate':'Selected adapter source hash','path':name,'scientific_replay_started':False}
    return outcomes

def main():
    labels=V.BENCHMARK+V.QUALIFICATION
    rows=[V.decode((HERE/'evidence'/x/'receipt.json').read_bytes()) for x in labels]
    out={x:(HERE/'evidence'/x/'stdout.txt').read_bytes() for x in labels}
    err={x:(HERE/'evidence'/x/'stderr.txt').read_bytes() for x in labels}
    runner=V.sha((HERE/'measurement-runner.py').read_bytes())
    with tarfile.open(HERE/'inputs/PR5757.tar','r:') as archive:
        cross=V.decode(archive.extractfile('research/selected-quadratic-replay/CROSS.json').read())
    def check(r=rows,o=out,e=err):
        return V.check_runs(r,lambda l:o[l],lambda l:e[l],runner,cross)
    positive=check()
    results={}
    def reject(label,action,predicate):
        try:
            action()
        except ValueError as failure:
            V.require(str(failure)==predicate,'Unexpected rejection site: '+label+': '+str(failure))
            results[label]=predicate
            return
        raise ValueError('Synthetic invalid record accepted: '+label)
    def edit(index,key,value):
        changed=deepcopy(rows);changed[index][key]=value;return changed
    reject('boolean_exit_alias',lambda:check(edit(0,'exit',False)),'Successful exact exit')
    reject('resource_stop',lambda:check(edit(0,'termination','wall_or_aggregate_cap')),'No stop or source mutation')
    reject('source_mutation',lambda:check(edit(0,'source_bytes_and_modes_unchanged',False)),'No stop or source mutation')
    reject('memory_overrun',lambda:check(edit(0,'sampled_process_group_rss_bytes',1024**3+1)),'Sampled group memory cap')
    reject('missing_qualification',lambda:check(rows[:-1]),'All ordered benchmark and qualification runs')
    changed=deepcopy(rows);changed[0],changed[1]=changed[1],changed[0]
    reject('reordered_samples',lambda:check(changed),'All ordered benchmark and qualification runs')
    reject('runner_drift',lambda:check(edit(0,'runner_sha256','0'*64)),'Actual runner and source manifest')
    reject('wrong_entry_point',lambda:check(edit(0,'script','only-a-success-marker.py')),'Complete expected entry point')
    reject('wrong_source_inventory',lambda:check(edit(0,'source_inventory_sha256','0'*64)),'One exact immutable read-only source inventory')
    reject('nonfinite_time',lambda:check(edit(0,'wall_seconds',float('nan'))),'Bounded finite runtime')
    reject('optimization_alias',lambda:check(edit(6,'optimized',1)),'Explicit optimization mode')
    changed_out=dict(out);changed_out[labels[0]]=out[labels[0]]+b'changed\n'
    reject('changed_scientific_stdout',lambda:check(o=changed_out),'Bound complete scientific output')
    changed=deepcopy(rows);changed_out=dict(out)
    index=7;label=labels[index]
    changed_out[label]=b'PASS_ALL_SELECTED_LITERAL_STATES\n'
    changed[index]['stdout_bytes']=len(changed_out[label]);changed[index]['stdout_sha256']=V.sha(changed_out[label])
    reject('truncated_oracle_with_rehashed_receipt',lambda:check(changed,changed_out),'Complete actual-state oracle evidence')
    changed_err=dict(err);changed_err[labels[0]]=b'hidden failure\n'
    reject('unexpected_diagnostic',lambda:check(e=changed_err),'No hidden diagnostics')
    reject('changed_manifest',lambda:V.check_source(manifest_raw=(HERE/'INPUT-MANIFEST.json').read_bytes()+b' '),'Source manifest binding')
    with tempfile.TemporaryDirectory(prefix='linux5757-synthetic-') as directory:
        damaged=Path(directory)/'damaged.tar'
        raw=bytearray((HERE/'inputs/PR5757.tar').read_bytes());raw[-1]^=1;damaged.write_bytes(raw)
        reject('changed_source_container',lambda:V.check_source(archive=damaged),'Official source export binding')
    V.require(not V.same(True,1) and not V.same(False,0),'Typed canonical report comparison')
    reject('duplicate_json_key',lambda:V.decode('{"x":1,"x":2}'),'Duplicate JSON key')
    source_controls=source_rejection_controls()
    print('PASS_SYNTHETIC_RECORDED_EVIDENCE_CONTROLS',json.dumps({'controls':results,'count':len(results),'actual_source_entry_controls':source_controls,'positive_median_speedup':positive['median_speedup']},sort_keys=True))

if __name__=='__main__':
    main()
