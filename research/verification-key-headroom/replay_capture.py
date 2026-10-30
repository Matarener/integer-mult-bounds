"""Optional fresh capture reproduction, only when explicitly requested.

Not registered for publication/CI. New timings never replace archived samples.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

ROOT=Path(__file__).resolve().parent
PINS=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('replay_capture.py','archive_support.py'):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]['sha256']:raise ValueError('protected replay wrapper source: '+name)
S=types.ModuleType('_headroom_capture_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def main():
    import argparse
    import subprocess
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    args=parser.parse_args();destination=args.evidence.resolve()
    S.need(sys.platform=='linux' and sys.version_info[:2]==(3,12),'original Linux CPython 3.12 replay environment required')
    S.need(not destination.exists() and not destination.is_relative_to(S.REPO),'fresh external evidence directory required')
    S.authenticate();destination.mkdir(parents=True)
    reconstructed=S.reconstruct(destination/'context')
    source_check=S.validate_context(reconstructed);S.official_baseline(reconstructed)
    command=[sys.executable,'-B',str(reconstructed/'run_guarded.py'),'actual-key-pilot-v1','stages/actual-key-pilot-v1/stage_entry.py']
    report=dict(status='STARTED_OPTIONAL_REPRODUCTION',command=command,source_check=source_check,
                automatic_retries=0,historical_nomination='REJECT_THIS_ACTUAL_KEY_CONDITIONAL_NOMINATION',
                new_timings_supersede_historical=False,construction_admitted=False)
    result_path=destination/'REPLAY-RESULT.json'
    def write():result_path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    write()
    try:
        with (destination/'guard.stdout.txt').open('wb') as out,(destination/'guard.stderr.txt').open('wb') as err:
            completed=subprocess.run(command,cwd=reconstructed,stdout=out,stderr=err,check=False)
        report['returncode']=completed.returncode
        S.need(completed.returncode==0,'single guarded capture failed; all evidence retained, no retry')
        guard=json.loads((reconstructed/'runtime/runs/actual-key-pilot-v1/receipt.json').read_text())
        fresh_root=reconstructed/'runtime/actual-key-pilot-v1-artifacts'
        fresh=json.loads((fresh_root/'RESULT.json').read_text())
        S.need(guard['status']=='PASS' and fresh['status']=='PASS_ACTUAL_KEY_COMPARISON_ONLY','complete fresh guarded capture/replay')
        committed=json.loads((ROOT/'data/DATA.json').read_text())['actual_corpus']
        left=S.corpus_blocks(ROOT/'data'/committed['file'],committed['sha256'])
        right=S.corpus_blocks(fresh_root/fresh['corpus']['file'],fresh['corpus']['sha256'])
        count=0
        for a,b in zip(left,right,strict=True):
            S.need(a==b,'every regenerated key value/order equals committed corpus')
            count+=len(a)
        S.need(count==S.CALLS,'complete regenerated corpus equality')
        S.validate_context(reconstructed);S.authenticate()
        report.update(status='PASS_FRESH_CAPTURE_VALUES_ONLY',all_regenerated_key_values_equal=True,calls=count,
                      new_corpus_container_sha256=fresh['corpus']['sha256'],guard_receipt=guard,
                      compression_hash_equality_required=False)
    except BaseException as error:
        report.update(status='FAIL_OPTIONAL_REPRODUCTION_RETAINED',error_type=type(error).__name__,error=str(error))
        raise
    finally:write()
    print(json.dumps(dict(status=report['status'],result=str(result_path),new_timings_supersede_historical=False)))


if __name__=='__main__':main()
