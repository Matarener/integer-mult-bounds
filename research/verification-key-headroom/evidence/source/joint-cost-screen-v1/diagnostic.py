"""One same-run disjoint integer + native-key cost diagnostic, not optimization.

Source-only at handoff. Parent owns every compiler/scientific/timing execution.
Existing Fraction callbacks, F(0), score operations and cache statistics stay
unchanged. A separate C activity marker rejects overlap with integer windows.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent.parent if HERE.parent.name == 'stages' else HERE.parent
BASE = HERE / 'baseline-public'
ORIGINAL_BASE = ROUND / 'baseline-public'
FULL_SHA256 = 'ce6f15ca892db095d4b9f79b58cb3c199b18da341def761c577cc8651abc0cc0'
INTEGER_SHA256 = '82a73e4bcf1835bfdd510c7ad5538625c1b380c559b671e6a67be490615a743a'
BASE_NATIVE_SHA256 = '78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb'
DIAGNOSTIC_NATIVE_SHA256 = '039c2c5fce353cf8be526c14f5f824dbc2b072999accddc310cc575e65e903f3'
BASELINE = dict(wall=34.66178539200337, cpu=34.47)
NOISE = dict(wall=2.713637237990042, cpu=2.3500000000000014)
RESERVE = dict(wall=0.50, cpu=0.50)
EXPECTED_COUNTS = dict(ideal=4, error_trace=121, reverse_all=121)
FAMILIES = tuple(EXPECTED_COUNTS)
sys.path.insert(0, str(BASE))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def verify_copy():
    receipt = json.loads((HERE / 'SOURCE-EDITS.json').read_text())
    need(receipt['original_native_sha256'] == BASE_NATIVE_SHA256 and
         receipt['diagnostic_native_sha256'] == DIAGNOSTIC_NATIVE_SHA256,
         'exact declared diagnostic source identities')
    need(receipt['changed_baseline_files'] == ['native_cache.c', 'NATIVE-SOURCE.json'],
         'only declared baseline diagnostic files changed')
    need(not any(path.is_symlink() for path in BASE.rglob('*')), 'no copied baseline symlinks')
    original_files = {str(path.relative_to(ORIGINAL_BASE)) for path in ORIGINAL_BASE.rglob('*')
                      if path.is_file() and '__pycache__' not in path.parts}
    need(original_files == set(receipt['original_inventory']), 'current original baseline census')
    files = {str(path.relative_to(BASE)) for path in BASE.rglob('*')
             if path.is_file() and '__pycache__' not in path.parts}
    need(files == set(receipt['original_inventory']), 'complete copied baseline file census')
    for relative, expected in receipt['original_inventory'].items():
        path = BASE / relative
        original = ORIGINAL_BASE / relative
        need(original.is_file() and not original.is_symlink(), 'regular original baseline source')
        need(sha256(original.read_bytes()).hexdigest() == expected['sha256'] and
             original.stat().st_mode & 0o777 == expected['mode'], 'current original baseline matches frozen copy inventory')
        need(not path.is_symlink() and path.is_file(), 'regular copied baseline source')
        need(path.stat().st_mode & 0o777 == expected['mode'], 'copied baseline mode')
        if relative not in ('native_cache.c', 'NATIVE-SOURCE.json'):
            need(sha256(path.read_bytes()).hexdigest() == expected['sha256'],
                 'unchanged copied baseline file: ' + relative)
    raw = (BASE / 'native_cache.c').read_bytes()
    need(sha256(raw).hexdigest() == DIAGNOSTIC_NATIVE_SHA256, 'exact diagnostic C source')
    need(json.loads((BASE / 'NATIVE-SOURCE.json').read_text()) ==
         dict(sha256=DIAGNOSTIC_NATIVE_SHA256), 'diagnostic cold-build source pin')
    restored = raw.decode()
    for edit in reversed(receipt['edits']):
        need(restored.count(edit['after']) == 1, 'unique reverse diagnostic seam')
        restored = restored.replace(edit['after'], edit['before'])
    need(sha256(restored.encode()).hexdigest() == BASE_NATIVE_SHA256,
         'diagnostic C reverses to exact original C')
    return dict(original_native_sha256=BASE_NATIVE_SHA256,
                diagnostic_native_sha256=DIAGNOSTIC_NATIVE_SHA256,
                copied_baseline_files=len(files), all_other_baseline_bytes_and_modes_equal=True,
                current_original_baseline_compared_per_file=True,
                diagnostic_edits_reverse_to_exact_original=True)


def plain_json(value):
    kind = type(value)
    if kind in (str, int, float, bool, type(None)):
        return True
    if kind in (list, tuple):
        return all(plain_json(item) for item in value)
    if kind is dict:
        return all(type(key) in (str, int) and plain_json(item)
                   for key, item in value.items())
    return False


class Ledger:
    def __init__(self, digest, actual_word, native):
        self.digest, self.native = digest, native
        self.actual_key = digest(actual_word)
        self.actual_length = len(actual_word['program'])
        self.depth = 0
        self.records, self.diagnostic_errors = [], []
        self.union_wall = self.union_cpu = 0.0

    def metadata(self, word):
        length, classification = None, 'unclassified'
        try:
            if type(word) is dict and type(word.get('program')) in (list, tuple):
                length = len(word['program'])
            if plain_json(word):
                if self.digest(word) == self.actual_key:
                    classification = 'actual_word'
                elif length is not None and length < self.actual_length:
                    classification = 'finite_fixture'
                else:
                    classification = 'modified_word_control'
        except Exception as error:
            self.diagnostic_errors.append(type(error).__name__)
        return length, classification

    def call(self, backend, family, word, args):
        function = getattr(backend, family)
        outermost = self.depth == 0
        self.depth += 1
        marked = False
        elapsed_wall = elapsed_cpu = None
        error_type = None
        try:
            if outermost:
                self.native._joint_integer_enter()
                marked = True
            started_wall = time.perf_counter()
            started_cpu = time.process_time()
            try:
                return function(word, *args)
            except BaseException as error:
                error_type = type(error).__name__
                raise
            finally:
                # Activity marker stays set until BOTH end clocks are sampled.
                elapsed_cpu = time.process_time() - started_cpu
                elapsed_wall = time.perf_counter() - started_wall
        finally:
            # Also clear a marker if a clock/diagnostic call failed. Original
            # callee exceptions are re-raised; diagnostic failures cannot PASS.
            try:
                if marked:
                    marked = False
                    self.native._joint_integer_leave()
            finally:
                self.depth -= 1
            if elapsed_wall is None or elapsed_cpu is None:
                self.diagnostic_errors.append('incomplete-timer')
            else:
                if outermost:
                    self.union_wall += elapsed_wall
                    self.union_cpu += elapsed_cpu
                length, classification = self.metadata(word)
                self.records.append(dict(family=family, program_length=length,
                    classification=classification, outermost=outermost,
                    exception=error_type, wall_seconds=elapsed_wall, cpu_seconds=elapsed_cpu))

    def report(self):
        counts = {name: sum(row['family'] == name for row in self.records)
                  for name in FAMILIES}
        need(self.depth == 0 and not self.diagnostic_errors, 'balanced complete integer timers')
        need(counts == EXPECTED_COUNTS, 'all original integer family calls retained')
        need(all(row['outermost'] for row in self.records), 'no nested integer timing overlap')
        return dict(counts=counts, expected_actual_program_length=self.actual_length,
                    disjoint_union_seconds=dict(wall=self.union_wall, cpu=self.union_cpu),
                    records=self.records)


_LEDGERS, _ORIGINAL_MODULES, _NATIVES = [], [], []


def timed_integer(module, reference, actual_word):
    path = Path(module.__file__)
    need(not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == INTEGER_SHA256,
         'exact original integer source')
    import native_backend
    native = native_backend.load()
    need(native_backend.receipt()['source_sha256'] == DIAGNOSTIC_NATIVE_SHA256,
         'activity marker belongs to the exact instrumented native module')
    original_engine = module.Engine
    ledger = Ledger(reference.digest, actual_word, native)
    _LEDGERS.append(ledger); _ORIGINAL_MODULES.append((module, original_engine)); _NATIVES.append(native)

    class TimedEngine:
        def __init__(self, ref): self._backend = original_engine(ref)
        def __getattr__(self, name): return getattr(self._backend, name)
        def ideal(self, word): return ledger.call(self._backend, 'ideal', word, ())
        def error_trace(self, word, weights, rounded):
            return ledger.call(self._backend, 'error_trace', word, (weights, rounded))
        def reverse_all(self, word, weights, rounded):
            return ledger.call(self._backend, 'reverse_all', word, (weights, rounded))

    facade = ModuleType(module.__name__ + '_joint_diagnostic')
    facade.__dict__.update(module.__dict__)
    facade.Engine = TimedEngine
    return facade


def checked_key_report(native, integer):
    data = native._joint_diagnostics()
    for name in ('key_depth', 'integer_depth', 'callback_depth', 'clock_failures',
                 'protocol_errors', 'nested_key_intervals', 'integer_overlap_intervals'):
        need(data[name] == 0, 'zero diagnostic imbalance/overlap/error: ' + name)
    total_integer = sum(integer['counts'].values())
    need(data['integer_enters'] == data['integer_leaves'] == total_integer,
         'every integer window has one balanced C activity marker')
    lookup, after = data['lookup'], data['after_callback']
    for phase in (lookup, after):
        need(phase['entries'] == phase['closed'] == phase['timed'],
             'all key intervals timed and closed')
        need(phase['excluded_callback'] == 0, 'frozen callbacks contain no nested key interval')
        need(phase['wall_seconds'] >= 0 and phase['cpu_seconds'] >= 0, 'nonnegative key clock intervals')
    need(lookup['entries'] == lookup['hits'] + lookup['misses'] + lookup['errors'],
         'lookup outcomes partition all hit/miss/error entries')
    need(lookup['inserted'] == 0 and after['hits'] == after['misses'] == 0,
         'phase outcomes are source-specific')
    need(after['entries'] == after['inserted'] + after['errors'] == lookup['misses'],
         'every miss callback has exactly one closed after-callback region')
    return data


def main():
    need(len(sys.argv) == 1, 'no alternate diagnostic workload or arguments')
    copy_receipt = verify_copy()
    path = BASE / 'full.py'
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == FULL_SHA256, 'exact original full qualifier source')
    source = raw.decode()
    before = "        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace\n"
    after = '''        integer_seam="            integer = v.load('integer_backend', package/'integer.py')\\n"
        require(changed.count(integer_seam)==1,'one unchanged integer diagnostic seam')
        changed=changed.replace(integer_seam,"            integer = _timed_integer(v.load('integer_backend', package/'integer.py'), reference, word)\\n")
        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace
        namespace['_timed_integer']=_timed_integer
'''
    need(source.count(before) == 1, 'one authenticated full namespace seam')
    source = source.replace(before, after)
    namespace = dict(__name__='_joint_cost_diagnostic', __file__=str(path), _timed_integer=timed_integer)
    exec(compile(source, str(path), 'exec'), namespace)
    namespace['main'](True)
    need(len(_LEDGERS) == len(_NATIVES) == 1, 'one selected original integer family and native module')
    need(all(module.Engine is engine for module, engine in _ORIGINAL_MODULES),
         'original loaded Engine classes and methods unchanged')
    integer = _LEDGERS[0].report()
    keys = checked_key_report(_NATIVES[0], integer)
    calibration = _NATIVES[0]._joint_clock_calibration()
    need(_NATIVES[0]._joint_diagnostics() == keys, 'clock calibration does not alter diagnostic totals')
    need(verify_copy() == copy_receipt, 'copied baseline and diagnostic source remain unchanged')
    key_union = {kind: keys['lookup'][kind + '_seconds'] + keys['after_callback'][kind + '_seconds']
                 for kind in ('wall', 'cpu')}
    union = {kind: integer['disjoint_union_seconds'][kind] + key_union[kind]
             for kind in ('wall', 'cpu')}
    threshold = {kind: max(0.15 * BASELINE[kind], 0.50, NOISE[kind]) for kind in ('wall', 'cpu')}
    free = {kind: union[kind] > threshold[kind] for kind in ('wall', 'cpu')}
    reserved = {kind: union[kind] - RESERVE[kind] > threshold[kind] for kind in ('wall', 'cpu')}
    status = ('REJECT_FREE_CEILING' if not all(free.values()) else
              'REJECT_PROVISIONAL_RESERVE' if not all(reserved.values()) else
              'HEADROOM_FOR_COST_DESIGN_ONLY')
    result = dict(status='PASS_JOINT_COST_DIAGNOSTIC', screen_status=status,
        performance_sample=False, optimization_constructed=False, construction_admitted=False,
        arithmetic_changed=False, original_fraction_callback_and_score_order_unchanged=True,
        original_cache_statistics_unchanged=True, source_copy=copy_receipt,
        full_source_sha256=FULL_SHA256, integer_source_sha256=INTEGER_SHA256,
        instrumented_driver_sha256=sha256(source.encode()).hexdigest(),
        expected_actual_native_counters_checked_by_original_full=namespace['ACTUAL_STATS'],
        expected_actual_fraction_output_checked_by_original_full=namespace['OUTPUT'],
        integer=integer, native_key_regions=keys, key_disjoint_union_seconds=key_union,
        same_run_disjoint_union_seconds=union, overlap_rejected=True,
        fixed_baseline_medians=BASELINE, fixed_noise_spreads=NOISE,
        necessary_zero_cost_threshold_seconds=threshold, zero_cost_gate=free,
        provisional_new_control_reserve_seconds=RESERVE,
        provisional_reserve_is_measured_bill=False, reserve_gate=reserved,
        retained_integer_runtime='UNPRICED_NONZERO', retained_key_runtime='UNPRICED_NONZERO',
        complete_new_validation_and_build_bill='UNPRICED_NONZERO',
        clock_overhead_calibration=calibration, calibration_subtracted=False,
        gc_added_separately=False, prior_run_numbers_added=False,
        callbacks_and_score_arithmetic_excluded_from_key_regions=True,
        outer_cpu_must_include_compiler_children=True,
        scope='same frozen PR5864 full_C qualifier scope; original separately registered custody scope unchanged')
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__': main()
