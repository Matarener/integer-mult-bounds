"""One prospective actual-key capture and fixed BCCB replay; parent guard only."""
import time
COLD_START=time.perf_counter()
import gzip
import gc
import hashlib
import json
from pathlib import Path
import pickle
import resource
import sys
import traceback
import run_pilot as approved
from load_pilot import compile_and_load,verify_sources
from capture_actual import CALLS,STATS,capture_qualified,verify_copy

ORDER=(('B1',0),('C1',1),('C2',1),('B2',0))
BLOCK=4096
ANCHOR=dict(wall=4.684712576272432,cpu=4.683428714999984)
THRESHOLD=dict(wall=5.199267808800505,cpu=5.1705)


def cpu():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime
COLD_CPU=cpu()


def archive_corpus(rows,destination):
    path=destination/'actual-keys-v1.pickle.gz'
    header=dict(format='actual-keys-v1',pickle_protocol=5,block_keys=BLOCK,calls=CALLS,key_fields=7,
                values='exact signed Python integers',order='original contribution order',cross_block_identity_preserved=False)
    with path.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=1,mtime=0) as stream:
        writer=pickle.Pickler(stream,protocol=5);writer.dump(header);writer.clear_memo()
        for start in range(0,CALLS,BLOCK):
            writer.dump(rows[start:start+BLOCK]);writer.clear_memo()
    # Bounded streaming readback checks every archived key value/order, while
    # timed replay retains the original in-memory object identities.
    with gzip.open(path,'rb') as stream:
        reader=pickle.Unpickler(stream)
        if reader.load()!=header:raise ValueError('corpus serialization header')
        reader.memo.clear()
        for start in range(0,CALLS,BLOCK):
            block=reader.load();reader.memo.clear()
            if type(block) is not tuple or block!=rows[start:start+BLOCK]:raise ValueError('entire archived corpus equals captured keys')
        try:reader.load()
        except EOFError:pass
        else:raise ValueError('no trailing corpus object')
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return dict(file=path.name,sha256=digest.hexdigest(),compressed_bytes=path.stat().st_size,format=header,
                complete_streaming_value_readback=True,replay_uses_original_captured_objects=True)


def screen(samples):
    by={r['name']:r for r in samples};out={}
    for kind in ('wall','cpu'):
        pairs=[by['B1'][kind]-by['C1'][kind],by['B2'][kind]-by['C2'][kind]]
        saving=min(pairs);budget=ANCHOR[kind]+saving-0.5
        out[kind]=dict(paired_key_only_seconds=pairs,smaller_key_only_seconds=saving,
            different_run_integer_gross_anchor=ANCHOR[kind],provisional_reserve_seconds=0.5,
            optimistic_budget_seconds=budget,zero_reserve_budget_seconds=budget+0.5,
            necessary_15pct_threshold_seconds=THRESHOLD[kind],necessary_threshold_met=budget>=THRESHOLD[kind])
    out.update(status='HEADROOM_FOR_SOURCE_SPECIFIC_COST_DESIGN_ONLY' if all(out[k]['necessary_threshold_met'] for k in ('wall','cpu')) else 'REJECT_THIS_ACTUAL_KEY_CONDITIONAL_NOMINATION',
        measured_actual_key_only=True,measured_complete_saving=False,construction_admitted=False,
        integer_anchor_from_different_run=True,integer_anchor_includes_clock_overhead=True,
        integer_residual_assumed_seconds=0,real_integer_residual='UNPRICED_NONZERO',reserve_measured=False,
        complete_new_validation_build_bill='UNPRICED_NONZERO',synthetic_failed_screen_remains_closed=True)
    return out


def main(destination):
    if len(sys.argv)!=1:raise ValueError('no alternate workload or arguments')
    destination.mkdir(parents=True,exist_ok=False)
    report=dict(status='STARTED',scope='source-specific full actual-key capture and key-only replay',samples=[],
        calls_per_sample=CALLS,frozen_order=[n for n,_ in ORDER],automatic_retries=0,construction_admitted=False)
    approved.write_json(destination/'RESULT.json',report)
    try:
        report['source_manifest']=verify_sources()
        rows,report['capture']=capture_qualified(destination)
        approved.write_json(destination/'CAPTURE-RECEIPT.json',report['capture'])
        report['post_qualifier_cleanup']=dict(unreachable_objects_collected=gc.collect(),charged_to_outer=True,
            after_all_original_qualifier_checks=True,captured_keys_retained=True,gc_policy_unchanged=True)
        report['corpus']=archive_corpus(rows,destination)
        module,report['key_build']=compile_and_load(destination)
        controls=approved.finite_controls(module)
        approved.write_json(destination/'FINITE-CONTROLS.json',controls)
        report['finite_controls']=dict(status=controls['status'],receipts=len(controls['receipts']),natural_rehashes=controls['natural_rehashes'])
        del controls
        expected=approved.literal_oracle(rows,16384)
        if expected[3]!={k:v for k,v in STATS.items() if k!='bypasses'}:raise ValueError('actual source counters match literal key oracle')
        report['oracle_output']=approved.retain_full(destination,'oracle',expected)
        approved.write_json(destination/'RESULT.json',report)
        for name,mode in ORDER:
            wall=time.perf_counter_ns();process=time.process_time_ns()
            actual=module.run(mode,rows,16384)
            process=time.process_time_ns()-process;wall=time.perf_counter_ns()-wall
            sample=dict(name=name,mode=mode,calls=CALLS,wall=wall/1e9,cpu=process/1e9)
            report['samples'].append(sample)
            sample['output']=approved.retain_full(destination,name,actual)
            approved.write_json(destination/'RESULT.json',report)
            approved.assert_equal(actual,expected,mode)
            if mode==1 and actual[3]['rehashes']<1:raise ValueError('actual custom replay exercises natural rehash')
            sample['full_output_equality']=True
            del actual
            approved.write_json(destination/'RESULT.json',report)
        verify_sources();verify_copy()
        report['conditional_screen']=screen(report['samples'])
        report['status']='PASS_ACTUAL_KEY_COMPARISON_ONLY'
    except BaseException as error:
        report['status']='FAIL_RETAINED_NO_RETRY'
        report['failure']=dict(type=type(error).__name__,message=str(error))
        (destination/'traceback.txt').write_text(traceback.format_exc())
        raise
    finally:
        report['child_cold_through_final_receipt_boundary']=dict(wall=time.perf_counter()-COLD_START,cpu_including_compiler_children=cpu()-COLD_CPU,
             excludes_process_startup_exit_and_this_final_write=True)
        report['parent_outer_guard_receipt_required']=True
        approved.write_json(destination/'RESULT.json',report)
    print(json.dumps(dict(status=report['status'],screen=report['conditional_screen']['status'],result=str(destination/'RESULT.json'))))
