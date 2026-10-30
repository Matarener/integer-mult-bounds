"""Source-bound full qualifier and unsampled key capture; no alternate workload."""
from hashlib import sha256
import contextlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROUND=HERE.parent.parent if HERE.parent.name=='stages' else HERE.parent
BASE=HERE/'baseline-public'
ORIGINAL=ROUND/'baseline-public'
FULL_SHA='ce6f15ca892db095d4b9f79b58cb3c199b18da341def761c577cc8651abc0cc0'
BASE_SHA='78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb'
CAPTURE_SHA='83acea581d685a1e6b1e68f12935f35d874e209633be76411eb7ee9482a9920e'
CALLS=2579750
STATS=dict(calls=CALLS,hits=2252966,misses=326784,evictions=310400,bypasses=0,resident=16384,capacity=16384)
OUTPUT='954c7448ff74d78753828e9623ad44c46da9e5ce459420b6e50a5d47294250b9'
EXPECTED=dict(all_actual_witness_rows_equal=True,coefficient_scale_bits=55,coordinates=799,events=25984,
 finite_fixtures=dict(cases=120,controls=['nondyadic scalar','inexact scale division','nondyadic weight'],events=4240),
 guards=dict(owned=22,prefix=26,public=23),source_controls=6,
 source_result_sha256='cc7739703ed23532d187949c8507d09c13ac4c152e07a930f0087cde0d7a3d98')


def need(ok,why):
    if not ok:raise ValueError(why)


def verify_copy():
    receipt=json.loads((HERE/'SOURCE-EDITS.json').read_text())
    need(receipt['original_native_sha256']==BASE_SHA and receipt['diagnostic_native_sha256']==CAPTURE_SHA,'capture source identities')
    need(receipt['changed_baseline_files']==['native_cache.c','NATIVE-SOURCE.json'],'only declared baseline changes')
    inventories=[]
    for directory in (ORIGINAL,BASE):
        need(not any(p.is_symlink() for p in directory.rglob('*')),'no baseline symlinks')
        inventories.append({str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    need(inventories[0]==inventories[1]==set(receipt['original_inventory']) and len(inventories[0])==164,'exact original and copied 164-file census')
    for relative,pin in receipt['original_inventory'].items():
        original=ORIGINAL/relative;copied=BASE/relative
        need(sha256(original.read_bytes()).hexdigest()==pin['sha256'] and original.stat().st_mode&0o777==pin['mode'],'original source bytes/mode: '+relative)
        need(copied.stat().st_mode&0o777==pin['mode'],'copied mode: '+relative)
        if relative not in ('native_cache.c','NATIVE-SOURCE.json'):
            need(sha256(copied.read_bytes()).hexdigest()==pin['sha256'],'unchanged copied bytes: '+relative)
    raw=(BASE/'native_cache.c').read_bytes()
    need(sha256(raw).hexdigest()==CAPTURE_SHA,'capture C exact hash')
    need(json.loads((BASE/'NATIVE-SOURCE.json').read_text())==dict(sha256=CAPTURE_SHA),'capture loader pin')
    restored=raw.decode()
    for edit in reversed(receipt['edits']):
        need(restored.count(edit['after'])==1,'unique inverse capture seam')
        restored=restored.replace(edit['after'],edit['before'])
    need(sha256(restored.encode()).hexdigest()==BASE_SHA,'inverse restores complete original native C')
    return dict(copied_files=164,original_native_sha256=BASE_SHA,capture_native_sha256=CAPTURE_SHA,
                inverse_exact=True,other_bytes_and_all_modes_equal=True)


class Capture:
    def __init__(self):
        self.factories=0;self.calls=0;self.rows=None;self.native=None;self.word_digest=None
    def factory(self,original_factory,native_backend,full_captures):
        def create(reference,expected_word):
            self.factories+=1;need(self.factories==1,'one source-bound actual factory')
            original=original_factory(reference,expected_word)
            self.word_digest=reference.digest(expected_word)
            def call(word,weights,rounded):
                if reference.digest(word)!=self.word_digest:return original(word,weights,rounded)
                self.calls+=1;need(self.calls==1,'one complete actual invocation, no repeated capture')
                native=native_backend.load();self.native=native
                need(native_backend.receipt()['source_sha256']==CAPTURE_SHA,'capturing the source-pinned native build')
                try:
                    native._capture_begin()
                    result=original(word,weights,rounded)
                    need(len(full_captures)==1 and full_captures[0]==dict(statistics=STATS,output_sha256=OUTPUT,tokens=3587),'original actual counters/digest and exact weight-token count')
                    self.rows=native._capture_take()
                    need(type(self.rows) is tuple and len(self.rows)==CALLS,'all actual keys taken exactly once')
                    return result
                finally:
                    native._capture_abort()
            return call
        return create


def capture_qualified(destination):
    before=verify_copy();capture=Capture();path=BASE/'full.py';raw=path.read_bytes()
    need(sha256(raw).hexdigest()==FULL_SHA,'unchanged original full qualifier')
    source=raw.decode();seam="        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace\n"
    replacement="        namespace=dict(entry.__dict__);namespace['_native_trace']=_capture_factory(native_trace,native_backend,captures)\n"
    need(source.count(seam)==1,'one authenticated full namespace seam')
    changed=source.replace(seam,replacement)
    namespace=dict(__name__='_actual_key_capture',__file__=str(path),_capture_factory=capture.factory)
    sys.path.insert(0,str(BASE))
    try:
        exec(compile(changed,str(path),'exec'),namespace)
        log=destination/'FULL-QUALIFIER.stdout.txt'
        with log.open('w') as stream,contextlib.redirect_stdout(stream):namespace['main'](True)
        records=[json.loads(line) for line in log.read_text().splitlines() if line.startswith('{')]
        qualified=[row for row in records if row.get('mode')=='qualify']
        native=[row for row in records if row.get('status')=='PASS_COMPLETE_NATIVE_COVERAGE']
        need(len(qualified)==1 and qualified[0]['receipt']==EXPECTED,'complete frozen qualification receipt and all actual witness rows')
        need(len(native)==1 and native[0]['actual']==dict(statistics=STATS,output_sha256=OUTPUT,tokens=3587),'complete original native receipt')
        need(native[0]['native_finite_included'] and native[0]['integer_oracle_unchanged'] and native[0]['compiler_children_charged'],'original qualifier coverage markers')
        need(capture.factories==capture.calls==1 and capture.rows is not None,'one complete unsampled key capture')
        need(verify_copy()==before,'baseline bytes/modes and inverse unchanged after qualifier')
        rows=capture.rows;capture.rows=None
        need(all(type(key) is tuple and len(key)==7 and all(type(x) is int for x in key) for key in rows),'every original key has exactly seven exact PyLong fields')
        return rows,dict(status='PASS_COMPLETE_ACTUAL_KEY_CAPTURE',calls=len(rows),expected_word_digest=capture.word_digest,
            original_actual=native[0]['actual'],qualification_receipt=qualified[0]['receipt'],native_build=native[0]['build'],source_copy=before,
            full_original_sha256=FULL_SHA,full_in_memory_wrapper_sha256=sha256(changed.encode()).hexdigest(),
            original_fraction_operations_and_all_full_witness_checks_retained=True,capture_phase_is_performance_sample=False)
    except BaseException:
        capture.rows=None
        raise
    finally:
        if capture.native is not None:capture.native._capture_abort()
        # Explicitly release this owned wrapper namespace; no GC-policy change.
        namespace.clear()
