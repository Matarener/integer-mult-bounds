"""Run PR6030's unchanged primary verifier with the merged gate-table clifford_exact zero_state.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.

    python3.12 -I -B [-O] run.py [--mode fast|differential|original]

fast          replace Op.zero_state on every loaded copy of the pinned clifford_exact.py with
              research/clifford-state-performance/fast_state.zero_state (Charles Bethin) (default)
differential  run the original and the replacement on every call and require equal results
original      the same harness with no replacement (timing baseline)

The PR6030 package (research/p104-helper470-twin-rung-removal, DreamingOfClouds) is executed in place
and unmodified: its verify.py authenticates its own source chain and requires the committed RESULT.json
byte-for-byte equal to the regenerated one.  This wrapper first checks that every file of that package
which the run reads matches the pins in this package's SOURCES.json, and refuses to patch any module
named clifford_exact.py whose bytes differ from fast.PIN; it executes exactly the hashed bytes, and after the run every module in
sys.modules loaded from a file named clifford_exact.py must carry the replacement.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.machinery
import json
import runpy
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import fast  # noqa: E402

TARGET = ROOT / 'research/p104-helper470-twin-rung-removal'
MARKER = 'PASS_P104_BASE5907_EDIT_KAPPA_312580400'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_pins(pins=None, root=ROOT):
    pins = json.loads((HERE / 'SOURCES.json').read_bytes()) if pins is None else pins
    rows = [row for row in pins['files'] if row['usage'] == 'input']
    need(len(rows) >= 7, 'Pinned target inventory')
    for row in rows:
        need(sha256((root / row['path']).read_bytes()).hexdigest() == row['sha256'], 'Changed pinned input ' + row['path'])
    vendored = next(row for row in rows if row['path'].endswith('vendor/clifford_exact.py'))
    need(vendored['sha256'] == fast.PIN, 'fast.PIN equals the pinned clifford_exact.py')
    return len(rows)


def install(mode, counter):
    evaluator = None if mode == 'original' else fast.evaluator()
    loader = importlib.machinery.SourceFileLoader
    original_exec = loader.exec_module

    def exec_module(self, module):
        path = Path(self.path)
        if path.name != 'clifford_exact.py':
            return original_exec(self, module)
        raw = self.get_data(self.path)
        need(fast.source_digest(raw) == fast.PIN, 'Refusing to patch unpinned clifford_exact.py bytes: ' + str(path))
        # execute exactly the hashed bytes (no bytecode cache can substitute for them)
        exec(compile(raw, self.path, 'exec', dont_inherit=True), module.__dict__)
        counter['clifford_loads'] += 1
        if mode == 'original':
            return None
        replacement = fast.counted(evaluator.zero_state, counter)
        if mode == 'differential':
            replacement = fast.differential(module.Op.zero_state, evaluator.zero_state, counter)
        module.Op.zero_state = replacement
        install.replacements.add(replacement)
        counter['patched_loads'] += 1
        return None

    loader.exec_module = exec_module
    install.evaluator = evaluator
    install.replacements = set()
    return lambda: setattr(loader, 'exec_module', original_exec)


def main(argv):
    mode = argv[argv.index('--mode') + 1] if '--mode' in argv else 'fast'
    need(mode in ('fast', 'differential', 'original'), '--mode must be fast, differential or original')
    pinned = check_pins()
    counter = Counter()
    restore = install(mode, counter)
    saved = sys.argv
    sys.argv = [str(TARGET / 'verify.py')]
    start = time.perf_counter()
    try:
        runpy.run_path(str(TARGET / 'verify.py'), run_name='__main__')
    finally:
        sys.argv = saved
        restore()
    seconds = time.perf_counter() - start
    need(counter['clifford_loads'] >= 1, 'The target run loaded clifford_exact.py')
    # tripwire for copies loaded by any other route: every registered module from a file named clifford_exact.py
    copies = [m for m in list(sys.modules.values()) if Path(str(getattr(m, '__file__', '') or '')).name == 'clifford_exact.py']
    need(len(copies) >= 1, 'A registered clifford_exact module')
    if mode != 'original':
        need(all(m.Op.zero_state in install.replacements for m in copies), 'Every registered clifford_exact copy patched')
    counter['registered_copies'] = len(copies)
    if mode != 'original':
        need(counter['patched_loads'] == counter['clifford_loads'], 'Every loaded copy patched')
    if mode == 'fast':
        need(counter['fast_calls'] > 0, 'Replacement calls observed')
    if mode == 'differential':
        need(counter['differential_calls'] > 0, 'Differential calls observed')
    if install.evaluator is not None:
        for name in ('permutation_table', 'phase_table'):
            info = getattr(install.evaluator, name).cache_info()
            counter[name + '_hits'], counter[name + '_misses'] = info.hits, info.misses
    print(json.dumps({'status': 'PASS_6030_PRIMARY_' + mode.upper(), 'target_marker': MARKER,
                      'pinned_inputs': pinned, 'counters': dict(sorted(counter.items())),
                      'seconds': round(seconds, 2), 'python': sys.version.split()[0],
                      'optimize_flag': sys.flags.optimize}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main(sys.argv)
