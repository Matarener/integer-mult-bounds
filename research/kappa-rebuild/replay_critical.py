#!/usr/bin/env python3
"""Fresh native/proof-interface replay in a separately materialized checkout.

Run this against a checkout built from the exact base and cumulative overlay.
It regenerates receipts in that checkout. --reference enables comparison
against the delivered artifacts; only timing metadata and their resulting
source-hash references are normalized. No mathematical predicate is waived.
Apache-2.0; substantial OpenAI assistance.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import subprocess
import sys
import time

SCOPE = Path('research/kappa-rebuild')
IGNORED_TIMING_KEYS = {'runtime','runtime_seconds','elapsed_seconds','seconds'}


def need(value,message):
    if not value:
        raise AssertionError(message)


def stage(name,script,outputs,arguments=()):
    return {'name':name,'script':str(SCOPE/script),'outputs':outputs,'arguments':list(arguments)}


COMPLEX = [
    stage('complex_helper_reconstruction','complex/rebuild_native.py',['complex/fresh-certificates/RESULT-helpers.json','complex/fresh-certificates/*HELPER*'],('--stage','helpers')),
    stage('complex_h_reconstruction','complex/rebuild_native.py',['complex/fresh-certificates/RESULT-H.json','complex/fresh-certificates/*H112*'],('--stage','H')),
    stage('complex_logger_reconstruction','complex/rebuild_native.py',['complex/fresh-certificates/RESULT-logger.json','complex/fresh-certificates/*LOGGER*'],('--stage','logger')),
    stage('complex_dyadic_balance','complex/power_two_balance.py',['complex/balanced-certificates/*']),
    stage('complex_native_extensions','complex/native_extensions.py',['complex/extension-certificates/*']),
    stage('complex_composition_contracts','complex/composition_contracts.py',['complex/COMPOSITION-CONTRACTS.json']),
    stage('complex_phase_contacts','complex/audit_frame_contacts.py',['complex/FRAME-CONTACT-INDEPENDENT-AUDIT.json']),
    stage('complex_full_identity','complex/full_identity_rebuild.py',['complex/full-identity-certificates/*']),
    stage('p2_native_cover','controller/global_identity_cover.py',['controller/GLOBAL-IDENTITY-COVER.json.gz']),
    stage('p3_native_cover','controller/p3_native_cover.py',['controller/P3-NATIVE-COVER.json.gz']),
    stage('p3_independent_phases','transfer-audit/p3_native_audit.py',['transfer-audit/P3-NATIVE-AUDIT.json.gz']),
    stage('p3_independent_owners','transfer-audit/p3_cover_audit.py',['transfer-audit/P3-COVER-AUDIT.json']),
    stage('finite_integer_compiler','transfer-audit/finite_dag_audit.py',['transfer-audit/FINITE-DAG-AUDIT.json']),
]
BIT = [
    stage('bit_native_and_mixed_controller','bit/mixed_productive_bit.py',['bit/MIXED-PRODUCTIVE-BIT.json']),
    stage('bit_independent_controller','bit/check_mixed_controller.py',['bit/MIXED-CONTROLLER-INDEPENDENT.json']),
    stage('bit_native_common_cover_binding','bit/bit_native_binding.py',['bit/BIT-P3-NATIVE-BINDING.json']),
    stage('bit_delayed_cover','bit/delayed_cover_bridge.py',['bit/DELAYED-COVER-BRIDGE.json']),
    stage('bit_allsize_parameters','bit/bit_allsize_parameters.py',['bit/BIT-ALLSIZE-PARAMETERS.json']),
    stage('bit_independent_bridge','transfer-audit/bit_bridge_audit.py',['transfer-audit/BIT-BRIDGE-AUDIT.json']),
]
ASSEMBLY = [
    stage('complete_outer_parameters','controller/outer_parameters.py',['controller/OUTER-PARAMETERS.json']),
    stage('new_precision_and_stock','transfer-audit/precision_closure.py',['transfer-audit/PRECISION-CLOSURE.json']),
    stage('explicit_finite_ranks','controller/explicit_template_bounds.py',['controller/EXPLICIT-TEMPLATE-BOUNDS.json']),
    stage('independent_outer_transfer','transfer-audit/outer_transfer_audit.py',['transfer-audit/OUTER-TRANSFER-AUDIT.json']),
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def payload(path):
    raw=path.read_bytes()
    if path.suffix=='.gz':
        raw=gzip.decompress(raw)
    return json.loads(raw)


def normalize(value,hash_map):
    if isinstance(value,dict):
        return {k:normalize(v,hash_map) for k,v in value.items() if k not in IGNORED_TIMING_KEYS}
    if isinstance(value,list):
        return [normalize(v,hash_map) for v in value]
    if isinstance(value,str):
        return hash_map.get(value,value)
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--reference',type=Path)
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--skip-reconstruction',action='store_true',help='Run the final composition and all independent gates; preserve reconstructed primitive receipts. Disclosed in the report.')
    args=p.parse_args()
    repo=args.repo.resolve(); reference=args.reference.resolve() if args.reference else None
    need(repo.is_dir(),'Materialized replay checkout')
    need(reference is None or repo!=reference,'Reference artifacts must be separate from the replay checkout')
    report=args.report.resolve(); logs=report.parent/'critical-replay-logs'; logs.mkdir(parents=True,exist_ok=True)
    began=time.monotonic()
    configuration=COMPLEX[7:] if args.skip_reconstruction else COMPLEX
    runs=[]; outputs=set()
    def sequence(stages):
        local=[]
        for item in stages:
            script=repo/item['script'];need(script.is_file(),'Replay script exists: '+item['script'])
            command=[sys.executable,'-B',item['script'],*item['arguments']]
            t=time.monotonic(); logfile=logs/(item['name']+'.log')
            with logfile.open('wb') as output:
                process=subprocess.run(command,cwd=repo,stdout=output,stderr=subprocess.STDOUT,check=False)
            entry={'stage':item['name'],'command':command,'source_sha256':digest(script),
                   'returncode':process.returncode,'seconds':time.monotonic()-t,
                   'log':logfile.name,'log_sha256':digest(logfile)}
            local.append(entry)
            print(json.dumps({'stage':item['name'],'returncode':process.returncode,'seconds':round(entry['seconds'],3)}),flush=True)
            need(process.returncode==0,'Scientific replay failed; inspect '+str(logfile))
        return local
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            complex_job=pool.submit(sequence,configuration)
            bit_job=pool.submit(sequence,BIT)
            # Inspect both branches even if one fails.
            errors=[]
            for job in (complex_job,bit_job):
                try:runs.extend(job.result())
                except Exception as exc:errors.append(repr(exc))
            need(not errors,'; '.join(errors))
        runs.extend(sequence(ASSEMBLY))
        for item in [*configuration,*BIT,*ASSEMBLY]:
            for pattern in item['outputs']:
                paths=[x for x in (repo/SCOPE).glob(pattern) if x.is_file()]
                need(paths,'Every declared output pattern is nonempty: '+pattern)
                outputs.update(path.relative_to(repo).as_posix() for path in paths)
        comparisons=[]; hash_map={}
        if reference:
            for name in sorted(outputs):
                need((reference/name).is_file(),'Reference output exists: '+name)
                old,new=digest(reference/name),digest(repo/name)
                need(old not in hash_map or hash_map[old]==new,'Equal reference artifacts replay identically')
                hash_map[old]=new
            for name in sorted(outputs):
                old,new=reference/name,repo/name
                exact=old.read_bytes()==new.read_bytes()
                if not exact:
                    need(normalize(payload(old),hash_map)==normalize(payload(new),{}),
                         'Non-timing scientific artifact changed: '+name)
                comparisons.append({'path':name,'reference_sha256':digest(old),'replay_sha256':digest(new),
                                    'exact_bytes':exact,'equal_after_declared_timing_and_source_hash_normalization':True})
        result={'schema':'fresh-cumulative-kappa-critical-replay/1',
                'status':'PASS_FRESH_NATIVE_AND_CONDITIONAL_INTERFACE_REPLAY',
                'stages':runs,'artifact_comparisons':comparisons,
                'timing_keys_ignored_in_artifact_comparison':sorted(IGNORED_TIMING_KEYS),
                'hash_normalization':'Only exact old-to-fresh hashes of regenerated artifacts are substituted in source references. All remaining mathematical content is compared.',
                'reconstructed_primitive_stages_replayed':not args.skip_reconstruction,
                'complete_base_materialization_is_separately_receipted':True,
                'winning_uniform_words_materialized':False,
                'proof_limits':'Executable finite checks and quantitative interface gates do not constitute a formal proof of the written universal construction or discharge inherited outer hypotheses.',
                'runtime_seconds':time.monotonic()-began}
    except Exception as exc:
        result={'schema':'fresh-cumulative-kappa-critical-replay/1','status':'FAIL',
                'error':repr(exc),'finished_stages':runs,'runtime_seconds':time.monotonic()-began}
        report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        raise
    report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'stages':len(runs),'artifacts':len(comparisons),'seconds':result['runtime_seconds']}),flush=True)


if __name__=='__main__':
    main()
