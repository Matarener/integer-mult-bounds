"""Optimistic owned-zero scratch experiments; not supplier admission."""
from __future__ import annotations
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = 'research/e8-bit-p111-tuned/'
WORD = BASE + 'data/bitE8mut-p111.json.gz'
CHECKER = BASE + 'code/xcheck_p.py'
GLOBAL = BASE + 'vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def authenticate():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], row['path'])
    spec = importlib.util.spec_from_file_location('owned_zero_checker', ROOT / CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with gzip.open(ROOT / WORD, 'rt') as stream:
        word = json.load(stream)
    return word, module.Word(word)


def combine(mask, rows):
    out = 0
    while mask:
        bit = mask & -mask
        out ^= rows[bit.bit_length() - 1]
        mask ^= bit
    return out


def inverse(rows):
    n = len(rows)
    work = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i] >> col & 1), None)
        need(pivot is not None, 'source block is singular')
        work[col], work[pivot] = work[pivot], work[col]
        for i in range(n):
            if i != col and work[i] >> col & 1:
                work[i] ^= work[col]
    mask = (1 << n) - 1
    need(all(r & mask == 1 << i for i, r in enumerate(work)), 'inverse reduction')
    return [r >> n for r in work]


def binary_rank(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def replay(w, checker, mode, omit_target_gate=False):
    v, n = w['v'], checker.n
    values = [1 << r if r < 2 * v else 0 for r in range(n)]
    current = w['start'][:2 * v] + [None] * w['R']
    profile, births, forks = Counter(), Counter(), {}
    omitted = False

    def climb(register, frame):
        old = current[register]
        if old is None:
            current[register] = frame
            births[checker.fdim[frame]] += 1
        elif old != frame:
            need(checker.nested(old, frame), 'changed frame nesting')
            rank = checker.fdim[frame] - checker.fdim[old]
            need(rank > 0, 'nonpositive frame climb')
            profile[rank] += 1
            current[register] = frame

    for phase in ('A', 'scatter', 'B'):
        if phase == 'scatter':
            copies = [values[r] for r in w['ret']]
            for r in w['ret']:
                need(values[r] != 0, 'unexpected zero retained total')
                profile[checker.fdim[current[r]]] += 1
            for target, row in enumerate(w['scatter']):
                for k in row:
                    values[v + target] ^= copies[k]
            continue
        for frame, destination, sources in w[phase]:
            if omit_target_gate and v <= destination < 2 * v and not omitted:
                omitted = True
                continue
            need(len(sources) == len(set(sources)), 'duplicate source operand')
            addition = combine(sum(1 << s for s in sources), values)
            if not addition:
                continue
            for r in [destination] + [s for s in sources if values[s]]:
                climb(r, frame)
            if destination < v and destination not in forks:
                forks[destination] = frame
            values[destination] ^= addition
    for target in range(v):
        need(values[v + target] == (1 << target) ^ (1 << (v + target)),
             'changed target endpoint')
        climb(v + target, w['final'][v + target])
    if mode == 'source_decoder':
        for source in range(v):
            climb(source, checker.FULL)
        decoder = inverse(values[:v])
        need(all(combine(row, values[:v]) == 1 << i for i, row in enumerate(decoder)),
             'full-frame source decoding')
        expected, _, _ = checker.replay(
            sections=('A', 'scatter', 'B'),
            values=[1 << r if r < 2 * v else 0 for r in range(n)],
            frames_on=False)
        need(expected == values, 'independent raw scalar replay differs')
    else:
        for source in range(v):
            frame = w['start'][source] if mode == 'eager_fork' else forks.get(source, current[source])
            rank = 8 - checker.fdim[frame]
            if rank:
                profile[rank] += 1
    profile.pop(0, None)
    answer = {'profile': {str(r): c for r, c in sorted(profile.items())},
            'rank_mass': sum(r * c for r, c in profile.items()),
            'helper_birth_dimensions': dict(sorted(births.items())),
            'source_mutations': len(forks), 'target_columns_checked': 2 * v,
            'source_decoder_dimension': v if mode == 'source_decoder' else 0}
    if mode == 'source_decoder':
        answer['rank_source_code_minus_identity'] = binary_rank(
            [r ^ (1 << i) for i, r in enumerate(values[:v])])
    return answer


def idle_invoice(v, replicas=32, pairs=4):
    tree = ast.parse((ROOT / GLOBAL).read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'recipe']
    need(len(nodes) == 1, 'one pinned schedule recipe')
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), GLOBAL, 'exec'), namespace)
    levels, idle = [-1] * pairs, Counter()
    forward = reverse = 0
    for event in namespace['recipe'](pairs):
        if event['kind'] == 'local':
            stage, pair = event['stage'], event['pair']
            need(levels[pair] == stage - 1, 'local entrance level')
            levels[pair] = stage
            reverse += bool(event['reverse'])
            forward += not event['reverse']
            if stage % 2 and stage <= 2 * pairs - 3:
                j = (stage + 1) // 2
                need(levels[j] == -1, 'first idle level')
                levels[j] = stage
                idle[7 * (stage + 1)] += 2 * v * replicas
            elif not stage % 2 and 2 <= stage <= 2 * pairs - 2:
                j = stage // 2
                need(levels[j] == stage - 1, 'second idle level')
                levels[j] = stage
                idle[7] += 2 * v * replicas
            elif stage == 2 * pairs:
                for j in range(pairs):
                    rank = 7 * (2 * pairs - levels[j])
                    if rank:
                        idle[rank] += 2 * v * replicas
                    levels[j] = 2 * pairs
        elif event['kind'] == 'bridge':
            need(levels[event['dst']] == levels[event['src']], 'bridge level')
        else:
            need(levels == [2 * pairs] * pairs, 'terminal exchange levels')
    need((forward, reverse) == (5, 4), 'five forward and four reverse calls')
    return idle


def calculate():
    w, checker = authenticate()
    v, replicas = w['v'], 32
    idle = idle_invoice(v, replicas)
    idle_mass = sum(r * c for r, c in idle.items())
    capacity = 64 * 8 * v * replicas
    trials = {}
    for mode in ('eager_fork', 'lazy_fork', 'source_decoder'):
        result = replay(w, checker, mode)
        # Reverse has ONLY the retained monotone data endpoint mass 7+7.
        # All helper, copy, setup, erasure and scalar costs there are free.
        bill = Q(5 * replicas * result['rank_mass'] + 4 * replicas * 14 * v + idle_mass, capacity)
        need(bill > 1, 'named implementation survived the rejection screen')
        result['optimistic_bill_at_zero'] = str(bill)
        trials[mode] = result
    try:
        replay(w, checker, 'source_decoder', omit_target_gate=True)
    except RuntimeError as error:
        need(str(error) == 'changed target endpoint', 'wrong mutation failure')
    else:
        raise RuntimeError('omitted target addition was accepted')
    dirty_values = [1 << r for r in range(checker.n)]
    dirty, _, _ = checker.replay(sections=('A', 'scatter', 'B'),
                                 values=dirty_values, frames_on=False)
    need(any(dirty[v + t] != (1 << t) ^ (1 << (v + t)) for t in range(v)),
         'omitting D must fail on arbitrary helper dirt')
    without_idle = Q(5 * replicas * trials['source_decoder']['rank_mass'] + 4 * replicas * 14 * v, capacity)
    need(without_idle < 1, 'omitted idle false-positive control')
    return {'status': 'REJECT_THREE_OWNED_ZERO_IMPLEMENTATIONS_IN_RETAINED_SCHEDULE',
            'selected_kappa_unchanged': '0.001672660197076918',
            'capacity': capacity, 'idle_profile': dict(sorted(idle.items())),
            'idle_mass': idle_mass, 'trials': trials,
            'omitted_idle_false_positive_bill': str(without_idle),
            'controls': ['omitted target gate rejected', 'omitted idle would falsely pass',
                         'borrowed dirty helpers fail without D'],
            'not_proved': ['physical/all-size supplier admission',
                           'universal owned-scratch or source-consuming impossibility',
                           'a new complex supplier or improved kappa']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    encoded = json.dumps(calculate(), indent=2, sort_keys=True) + '\n'
    destination = PACKAGE / 'RESULT.json'
    if args.write:
        destination.write_text(encoded)
    else:
        need(destination.read_text() == encoded, 'receipt differs')
    print('PASS_OWNED_ZERO_NATIVE_DAG modes=3 exact_target_columns=222 no_new_kappa')


if __name__ == '__main__':
    main()
