"""One original-integer call-boundary rejection diagnostic; not a benchmark.

SOURCE ONLY at handoff. Root owns all execution and resource accounting.
No arithmetic implementation is replaced. Frozen PR5864 full_C qualifier scope
and all its scientific/native/Observation checks run, with timers around the
selected ORIGINAL integer Engine methods. Separate custody scope is unchanged.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from types import ModuleType

ROUND = Path(__file__).resolve().parent.parent
BASE = ROUND / 'baseline-public'
FULL_SHA256 = 'ce6f15ca892db095d4b9f79b58cb3c199b18da341def761c577cc8651abc0cc0'
INTEGER_SHA256 = '82a73e4bcf1835bfdd510c7ad5538625c1b380c559b671e6a67be490615a743a'
BASELINE = dict(wall=34.66178539200337, cpu=34.47)
NOISE = dict(wall=2.713637237990042, cpu=2.3500000000000014)
EXPECTED_COUNTS = dict(ideal=4, error_trace=121, reverse_all=121)
FAMILIES = tuple(EXPECTED_COUNTS)
sys.path.insert(0, str(BASE))


def need(ok, message):
    if not ok:
        raise ValueError(message)


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
    def __init__(self, digest, actual_word):
        self.digest = digest
        self.actual_key = digest(actual_word)
        self.actual_length = len(actual_word['program'])
        self.depth = 0
        self.records = []
        self.diagnostic_errors = []
        self.union_wall = 0.0
        self.union_cpu = 0.0

    def metadata(self, word):
        # Classification is outside every eligible interval and never changes
        # the callee's return or exception. No foreign input method is invoked.
        length = None
        classification = 'unclassified'
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
        started_wall = time.perf_counter()
        started_cpu = time.process_time()
        error_type = None
        try:
            return function(word, *args)
        except BaseException as error:
            error_type = type(error).__name__
            raise
        finally:
            elapsed_cpu = time.process_time() - started_cpu
            elapsed_wall = time.perf_counter() - started_wall
            self.depth -= 1
            if outermost:
                self.union_wall += elapsed_wall
                self.union_cpu += elapsed_cpu
            # Original Engine implementations do not call these three methods
            # recursively. Outermost accounting still prevents double counting.
            length, classification = self.metadata(word)
            self.records.append(dict(family=family, program_length=length,
                                     classification=classification,
                                     outermost=outermost, exception=error_type,
                                     wall_seconds=elapsed_wall,
                                     cpu_seconds=elapsed_cpu))

    def report(self):
        counts = {name: sum(row['family'] == name for row in self.records)
                  for name in FAMILIES}
        need(self.depth == 0, 'all timed calls exited')
        need(not self.diagnostic_errors, 'diagnostic classification completed')
        need(counts == EXPECTED_COUNTS, 'all expected original Engine boundaries observed')
        need(all(row['outermost'] for row in self.records), 'frozen Engine boundaries are disjoint')
        union = dict(wall=self.union_wall, cpu=self.union_cpu)
        threshold = {kind: max(0.15 * BASELINE[kind], 0.50, NOISE[kind])
                     for kind in ('wall', 'cpu')}
        passes = {kind: union[kind] > threshold[kind] for kind in ('wall', 'cpu')}
        return dict(status='PASS_ORIGINAL_INTEGER_BOUNDARY_DIAGNOSTIC',
                    arithmetic_changed=False, fraction_path_changed=False,
                    performance_sample=False, complete_speed_claim=False,
                    scope='frozen PR5864 full_C qualifier; separate custody checks excluded as before',
                    counts=counts, expected_actual_program_length=self.actual_length,
                    eligible_disjoint_union_seconds=union,
                    fixed_baseline_medians=BASELINE, fixed_noise_spreads=NOISE,
                    necessary_zero_cost_threshold_seconds=threshold,
                    strictly_exceeds_zero_cost_threshold=passes,
                    nomination_rejected=not all(passes.values()),
                    construction_admitted=False,
                    interpretation=('Even deleting every timed original integer call cannot fund the fixed gate.'
                                    if not all(passes.values()) else
                                    'Zero-cost envelope did not reject; retained runtime and all new costs remain unpriced.'),
                    own_process_cpu_only_inside_engine=True,
                    outer_cpu_must_include_existing_compiler_children=True,
                    metadata_and_output_costs_outside_eligible_union=True,
                    records=self.records)


_LEDGERS = []
_ORIGINAL_MODULES = []


def timed_integer(module, reference, actual_word):
    path = Path(module.__file__)
    need(not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == INTEGER_SHA256,
         'exact original integer source for boundary diagnostic')
    original_engine = module.Engine
    ledger = Ledger(reference.digest, actual_word)
    _LEDGERS.append(ledger)
    _ORIGINAL_MODULES.append((module, original_engine))

    class TimedEngine:
        def __init__(self, ref):
            self._backend = original_engine(ref)

        def __getattr__(self, name):
            return getattr(self._backend, name)

        def ideal(self, word):
            return ledger.call(self._backend, 'ideal', word, ())

        def error_trace(self, word, weights, rounded):
            return ledger.call(self._backend, 'error_trace', word, (weights, rounded))

        def reverse_all(self, word, weights, rounded):
            return ledger.call(self._backend, 'reverse_all', word, (weights, rounded))

    # Only this local facade changes the selected constructor. The loaded
    # original module, its functions/globals, and every archive byte stay intact.
    facade = ModuleType(module.__name__ + '_boundary_diagnostic')
    facade.__dict__.update(module.__dict__)
    facade.Engine = TimedEngine
    return facade


def main():
    need(len(sys.argv) == 1, 'no diagnostic arguments or alternate workload')
    path = BASE / 'full.py'
    raw = path.read_bytes()
    need(not path.is_symlink() and sha256(raw).hexdigest() == FULL_SHA256,
         'exact frozen PR5864 full qualifier source')
    source = raw.decode()
    before = "        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace\n"
    after = '''        integer_seam="            integer = v.load('integer_backend', package/'integer.py')\\n"
        require(changed.count(integer_seam)==1,'one original integer diagnostic seam')
        changed=changed.replace(integer_seam,"            integer = _timed_integer(v.load('integer_backend', package/'integer.py'), reference, word)\\n")
        namespace=dict(entry.__dict__);namespace['_native_trace']=native_trace
        namespace['_timed_integer']=_timed_integer
'''
    need(source.count(before) == 1, 'one frozen full namespace seam')
    source = source.replace(before, after)
    namespace = dict(__name__='_original_integer_boundary_diagnostic',
                     __file__=str(path), _timed_integer=timed_integer)
    exec(compile(source, str(path), 'exec'), namespace)
    namespace['main'](True)
    need(len(_LEDGERS) == 1, 'one selected original integer Engine family')
    need(all(module.Engine is engine for module, engine in _ORIGINAL_MODULES),
         'loaded original Engine class was not changed')
    need(sha256(path.read_bytes()).hexdigest() == FULL_SHA256,
         'full qualifier source unchanged after diagnostic')
    result = _LEDGERS[0].report()
    result['full_source_sha256'] = FULL_SHA256
    result['integer_source_sha256'] = INTEGER_SHA256
    result['instrumented_driver_sha256'] = sha256(source.encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
