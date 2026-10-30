#!/usr/bin/env python3
"""Replay one emitted receiver admission audit into a fresh output directory.

The existing scientific source and discovery inputs are read only. The three
hosted input files are copied so the original auditor's idle-frame export also
lands in fresh work. The discovery record is separate from the prior attempt.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path

P=Path(__file__).resolve().parent
def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--admission',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--control-mode',choices=['fork','pickle'],default='fork')
    a=ap.parse_args();admission=a.admission.resolve();out=a.out.resolve()
    assert not out.exists(),'fresh output directory required'
    out.mkdir(parents=True);hosted=out/'hosted';hosted.mkdir()
    base=admission/'discovery/global/base'
    original_hosted=admission/'discovery/global/hosted'
    source=admission/'layout/packing74/code/audit_allcold.py'
    root=admission/'layout/joint1148-round45/source'
    upstream=root/'research/complex-k492-owner-repair/vendor/multicold'
    portable=upstream/'code/run_portable.py'
    witness=admission/'discovery/runtime/data/SPEC.json'
    bindings={}
    for name in ['GLOBAL-TEMPLATE.json.gz','HOSTED.json','ACTUAL-SIGMAS.json.gz']:
        src=original_hosted/name;shutil.copy2(src,hosted/name)
        bindings[str(src.relative_to(admission))]=sha(src)
        assert sha(hosted/name)==bindings[str(src.relative_to(admission))]
    summary=json.loads((hosted/'HOSTED.json').read_text())
    for name,expected in summary['source_artifacts'].items():
        path=base/name;actual=sha(path);assert actual==expected
        bindings[str(path.relative_to(admission))]=actual
    for path in [source,witness,portable,base/'split-centres/GLOBAL-TEMPLATE.json.gz']:
        bindings[str(path.relative_to(admission))]=sha(path)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
             MULTICOLD_SOURCE=str(upstream),GAIN_PR564_SOURCE=str(upstream),WITNESS_SPEC=str(witness),
             WITNESS_DISCOVER='1',WITNESS_RECORD=str(out/'WITNESS-RECORD.jsonl'),
             AUDIT_RUNTIME_CONTROLS=a.control_mode,AUDIT_FAST_SHARDS='1')
    env.pop('PYTHONOPTIMIZE',None);env.pop('AUDIT_FAST_SHARD',None)
    command=[sys.executable,'-B',str(portable),str(P/'audit_fast.py'),str(source),str(base),str(hosted),str(out/'audit/ASYNC-AUDIT.json'),'--mutation-controls']
    inputs=dict(admission=str(admission),source_artifacts=bindings,adapter_sha256=sha(P/'audit_fast.py'),
                command=command,cwd=str(root),environment={k:env[k] for k in ['PYTHONDONTWRITEBYTECODE','PYTHONUTF8','PYTHONINTMAXSTRDIGITS','MULTICOLD_SOURCE','GAIN_PR564_SOURCE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD','AUDIT_RUNTIME_CONTROLS','AUDIT_FAST_SHARDS']})
    (out/'INPUTS.json').write_text(json.dumps(inputs,indent=2,sort_keys=True)+'\n')
    start=time.monotonic()
    with (out/'AUDIT.log').open('w') as log:
        result=subprocess.run(command,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
    receipt=dict(status='PASS_FULL_RUNTIME_AUDIT_REPLAY' if result.returncode==0 else 'FAILED_RUNTIME_AUDIT_REPLAY',
                 exit_code=result.returncode,seconds=time.monotonic()-start,inputs_sha256=sha(out/'INPUTS.json'),log_sha256=sha(out/'AUDIT.log'))
    if result.returncode==0:
        scientific=['audit/ASYNC-AUDIT.json','audit/OWNERS-AND-PROFILE.json','audit/IDLE-REMAINDER-FRAMES.json','hosted/IDLE-REMAINDER-FRAMES.json.gz']
        receipt['scientific_outputs']={name:sha(out/name) for name in scientific}
        report=json.loads((out/'audit/ASYNC-AUDIT.json').read_text())
        receipt['audit_status']=report['status'];receipt['hosted_helper_roles']=report['helper_busy_family_window_checks']
        receipt['complete_invocations']=report['complete_invocations'];receipt['controls_rejected']=report['mutations_rejected']
        progress=[json.loads(line) for line in (out/'audit/RUNTIME-PROGRESS.jsonl').read_text().splitlines()]
        receipt['parent_peak_rss_kib']=max(row['max_rss_kib'] for row in progress if row['context'] in ['initialization','complete'])
        receipt['max_control_child_rss_kib']=max(row.get('child_max_rss_kib',0) for row in progress)
    (out/'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)
    assert result.returncode==0,'original audit conditions did not all pass'

if __name__=='__main__':main()
