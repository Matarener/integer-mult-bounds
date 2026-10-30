"""Checks for the PR6030 binding of fast_state.zero_state: random-circuit equivalence, mutants, invalidation.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
Deterministic (fixed seed), stdlib only, about ten seconds.
"""
from collections import Counter
from pathlib import Path
import copy
import importlib.machinery
import importlib.util
import json
import random
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import fast  # noqa: E402
import run  # noqa: E402

VENDOR = ROOT / 'research/p104-native-channel/vendor/clifford_exact.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejects(action, message=None):
    try:
        action()
    except (ValueError, AssertionError, IndexError) as error:
        return message is None or str(error) == message
    return False


def random_invertible(n, rng):
    while True:
        rows = tuple(rng.randrange(1, 1 << n) for _ in range(n))
        if C.rank(rows) == n:
            return rows


def random_symmetric(n, rng):
    Q = [0] * n
    for i in range(n):
        for j in range(i, n):
            if rng.random() < 0.4:
                Q[i] |= 1 << j
                Q[j] |= 1 << i
    return tuple(Q)


def random_circuit(n, rng, length):
    ops = []
    for _ in range(length):
        kind = rng.choice('PXDCFH')
        if kind == 'P':
            ops.append(C.perm(n, random_invertible(n, rng)))
        elif kind == 'X':
            ops.append(C.xgate(n, rng.randrange(1 << n)))
        elif kind == 'D':
            Q = random_symmetric(n, rng)
            alpha = tuple(((Q[i] >> i) & 1) + 2 * rng.randrange(2) for i in range(n))
            ops.append(C.diag(n, Q, alpha))
        elif kind == 'C':
            ops.append(C.cgate(n, rng.randrange(1, 1 << n), rng.choice((1, -1))))
        elif kind == 'F':
            ops.append(C.fourier(n, rng.sample(range(n), rng.randrange(n + 1))))
        else:
            ops.append(C.Op(n, C.identity(n), [('phase', rng.randrange(-5, 6))]))
    out = C.ident(n)
    for op in ops:
        out = out.then(op)
    return out


C = load(VENDOR, 'clifford_exact_test_copy')


def main():
    need(fast.source_digest(VENDOR.read_bytes()) == fast.PIN, 'Repository clifford_exact.py has the pinned bytes')
    original = C.Op.zero_state
    replacement = fast.evaluator().zero_state
    rng = random.Random(6030)
    calls = Counter()
    for n in range(1, 10):
        for trial in range(120 if n < 8 else 40):
            op = random_circuit(n, rng, rng.randrange(0, 9))
            for basis in {0, rng.randrange(1 << n)}:
                need(replacement(op, basis) == original(op, basis), 'Random circuit n=%d trial=%d' % (n, trial))
                calls['random'] += 1
            if trial % 4 == 0:
                for side in (op, op.adjoint()):
                    rank = C.rank([x for x, z, p in side.tab[n:]])
                    if rank:
                        _, compiled = C.lower_child(side)   # exercises the compiler's own zero_state asserts
                        need(replacement(compiled) == original(compiled), 'Lowered child n=%d' % n)
                        calls['lowered'] += 1
        for r in range(n + 1):
            U = tuple(sorted(rng.sample(range(1, 1 << n), min(r, (1 << n) - 1))))
            if C.rank(U) == len(U):
                frame = C.canonical_frame(n, U)
                need(replacement(frame) == original(frame), 'Canonical frame n=%d r=%d' % (n, r))
                calls['frames'] += 1
    need(type(replacement(C.fourier(3))[0]) is list, 'Output container type')

    # mutants must be rejected by the differential wrapper on this workload
    mutants = {}
    def mutant_c_sign(self, basis=0):
        vec, den = original(self, basis)
        return ([(a, -b) for a, b in vec], den) if any(e[0] == 'C' for e in self.circuit) else (vec, den)
    def mutant_no_halving(self, basis=0):
        vec, den = original(self, basis)
        return [(2 * a, 2 * b) for a, b in vec], den + 1      # same value, unreduced representation
    def mutant_phase(self, basis=0):
        vec, den = original(self, basis)
        return [(-b, a) for a, b in vec], den
    probe = [C.canonical_frame(9, (3, 5, 17)), C.fourier(4), random_circuit(6, rng, 6)]
    for label, mutant in (('c_sign', mutant_c_sign), ('no_halving', mutant_no_halving), ('global_phase', mutant_phase)):
        wrapped = fast.differential(original, mutant, Counter())
        mutants[label] = any(rejects(lambda op=op: wrapped(op), 'zero_state differential mismatch') for op in probe)
    need(all(mutants.values()), 'Every mutant rejected: ' + json.dumps(mutants))

    # invalidation: the loader hook refuses changed clifford_exact.py bytes and accepts the pinned ones
    counter = Counter()
    restore = run.install('fast', counter)
    try:
        with tempfile.TemporaryDirectory() as directory:
            good = Path(directory) / 'good' / 'clifford_exact.py'
            bad = Path(directory) / 'bad' / 'clifford_exact.py'
            good.parent.mkdir(); bad.parent.mkdir()
            raw = VENDOR.read_bytes()
            good.write_bytes(raw)
            bad.write_bytes(raw + b'\n# one changed byte\n')
            loaded = load(good, 'clifford_exact_good')
            need(counter['patched_loads'] == 1 and loaded.Op.zero_state in run.install.replacements,
                 'Pinned bytes patched')
            need(loaded.Op(3, loaded.identity(3), []).zero_state() == ([(1, 0)] + [(0, 0)] * 7, 0)
                 and counter['fast_calls'] == 1, 'Patched copy calls the replacement')
            changed_refused = rejects(lambda: load(bad, 'clifford_exact_bad'))
    finally:
        restore()
    need(changed_refused, 'Changed clifford_exact.py bytes refused')
    need(importlib.machinery.SourceFileLoader.exec_module.__qualname__.startswith('_LoaderBasics'), 'Loader hook removed')

    # invalidation: a changed pin for any declared target input is refused before the run
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    run.check_pins(pins)
    tampered = 0
    for index, row in enumerate(pins['files']):
        if row['usage'] != 'input':
            continue
        bad = copy.deepcopy(pins)
        bad['files'][index]['sha256'] = '0' * 64
        tampered += rejects(lambda bad=bad: run.check_pins(bad))
    need(tampered == sum(row['usage'] == 'input' for row in pins['files']), 'Every changed input pin refused')

    # invalidation: one changed byte in any declared input file is refused (copied tree, real pins)
    changed_files = 0
    with tempfile.TemporaryDirectory() as directory:
        copy_root = Path(directory)
        inputs = [row['path'] for row in pins['files'] if row['usage'] == 'input']
        for path in inputs:
            (copy_root / path).parent.mkdir(parents=True, exist_ok=True)
            (copy_root / path).write_bytes((ROOT / path).read_bytes())
        run.check_pins(pins, copy_root)
        for path in inputs:
            raw = (ROOT / path).read_bytes()
            (copy_root / path).write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
            changed_files += rejects(lambda: run.check_pins(pins, copy_root), 'Changed pinned input ' + path)
            (copy_root / path).write_bytes(raw)
    need(changed_files == len(inputs), 'Every changed input file refused')

    print(json.dumps({'status': 'PASS_ZERO_STATE_TABLES_EQUIVALENCE_AND_CONTROLS', 'calls': dict(calls),
                      'mutants_rejected': mutants, 'changed_source_refused': True,
                      'changed_pins_refused': tampered, 'changed_files_refused': changed_files}, sort_keys=True))


if __name__ == '__main__':
    main()
