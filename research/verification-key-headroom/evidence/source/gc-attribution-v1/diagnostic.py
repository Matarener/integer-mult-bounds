"""One passive complete PR5864 cyclic-GC attribution; not a performance sample."""
import gc
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

ROUND=Path(__file__).resolve().parents[2]
BASE=ROUND/'baseline-public'
OUTPUT=ROUND/'runtime/gc-attribution-v1'
FULL_SHA='ce6f15ca892db095d4b9f79b58cb3c199b18da341def761c577cc8651abc0cc0'
BASELINE={'wall':34.66178539200337,'cpu':34.47}
NOISE={'wall':2.713637237990042,'cpu':2.3500000000000014}

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    need(sha256((BASE/'full.py').read_bytes()).hexdigest()==FULL_SHA,'exact frozen PR5864 full source')
    OUTPUT.mkdir(exist_ok=False)
    original_callbacks=gc.callbacks
    callbacks_before=tuple(original_callbacks)
    enabled_before=gc.isenabled()
    threshold_before=gc.get_threshold()
    debug_before=gc.get_debug()
    garbage_before=tuple(id(x) for x in gc.garbage)
    stats_before=gc.get_stats()
    records=[];errors=[];active=[]
    def callback(phase,info):
        # Collector callbacks cannot raise: retain diagnostic errors and reject
        # outside the callback rather than emit an ignored/unraisable error.
        if phase=='start':
            if active:errors.append('nested-start')
            active.append((info.get('generation'),time.perf_counter(),time.process_time()))
        elif phase=='stop':
            ended_cpu=time.process_time();ended_wall=time.perf_counter()
            if not active:
                errors.append('unmatched-stop');return
            generation,started_wall,started_cpu=active.pop()
            if info.get('generation')!=generation:errors.append('generation-mismatch')
            if not active:
                records.append({'generation':generation,'wall_seconds':ended_wall-started_wall,
                    'cpu_seconds':ended_cpu-started_cpu,'collected':info.get('collected'),
                    'uncollectable':info.get('uncollectable')})
        else:errors.append('unknown-phase')
    original_callbacks.append(callback)
    callback_state_at_end=None
    error=None
    try:
        sys.path.insert(0,str(BASE))
        import full
        full.main(True)
    except BaseException as caught:
        error=type(caught).__name__
        raise
    finally:
        callback_state_at_end=(gc.callbacks is original_callbacks and
            tuple(gc.callbacks)==callbacks_before+(callback,))
        # Slice assignment retains the same public callback-list identity.
        original_callbacks[:]=callbacks_before
        need(gc.callbacks is original_callbacks,'GC callback list identity unchanged')
        need(tuple(gc.callbacks)==callbacks_before,'exact callback state restored')
        need(gc.isenabled()==enabled_before,'GC enabled state unchanged')
        need(gc.get_threshold()==threshold_before,'GC thresholds unchanged')
        need(gc.get_debug()==debug_before,'GC debug state unchanged')
        need(tuple(id(x) for x in gc.garbage)==garbage_before,'GC garbage list unchanged')
        need(callback_state_at_end,'only the appended passive timer callback present')
        need(not active and not errors,'paired disjoint GC observations')
    stats_after=gc.get_stats()
    by_generation=[]
    for generation in range(3):
        rows=[r for r in records if r['generation']==generation]
        delta=stats_after[generation]['collections']-stats_before[generation]['collections']
        # Statistics snapshots can cause allocation/collection before registration
        # or after removal; do not pretend any unobserved interval was measured.
        by_generation.append({'generation':generation,'observed_collections':len(rows),
            'stats_delta_collections':delta,'wall_seconds':sum(r['wall_seconds'] for r in rows),
            'cpu_seconds':sum(r['cpu_seconds'] for r in rows),
            'collected':sum(r['collected'] for r in rows),
            'uncollectable':sum(r['uncollectable'] for r in rows)})
    union={m:sum(r[m+'_seconds'] for r in records) for m in ('wall','cpu')}
    zero={m:max(0.15*BASELINE[m],0.5,NOISE[m]) for m in ('wall','cpu')}
    reserve={'wall':0.5,'cpu':0.5}
    report={'status':'PASS_PASSIVE_COMPLETE_GC_ATTRIBUTION','performance_sample':False,
        'arithmetic_changed':False,'gc_policy_changed':False,'construction_admitted':False,
        'scope':'same frozen PR5864 full_C qualifier; unchanged separate custody scope',
        'observation':'all observed cyclic collections, including the original explicit finite collect controls; automatic-only removable bill cannot be larger',
        'callback_overhead':'start/stop and existing callbacks can inflate or perturb observations; not a universal machine/runtime bound',
        'callbacks_restored':True,'runtime_gc_policy_unchanged':True,'source_full_sha256':FULL_SHA,
        'fixed_baseline_medians':BASELINE,'fixed_noise_spreads':NOISE,
        'observed_disjoint_gc_seconds':union,'zero_cost_threshold_seconds':zero,
        'provisional_new_control_reserve_seconds':reserve,
        'reserve_is_actual_measured_bill':False,
        'future_policy_requires_separate_cycle_finalizer_restore_and_complete_paid_validation':True,
        'standalone_zero_cost_screen_pass':all(union[m]>zero[m] for m in union),
        'preliminary_reserve_screen_pass':all(union[m]>zero[m]+reserve[m] for m in union),
        'do_not_add_to_prior_integer_union':'GC intervals may overlap the earlier original-integer intervals; no disjoint combination attribution exists',
        'by_generation':by_generation,'stats_before':stats_before,'stats_after':stats_after,
        'records':records}
    (OUTPUT/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},sort_keys=True))

if __name__=='__main__':main()
