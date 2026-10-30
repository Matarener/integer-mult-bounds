#!/usr/bin/env python3
"""Bind exact native evidence to PR5569. Scratch-net, with OpenAI Codex.

Apache-2.0. Clifford lowering and literal gates retain their source authors.
Dense execution is Chris R / Clear1nsight's PR5548 interpreter.
The reused full-run evidence is Matarener's PR5572 receipt for PR5551.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from multiprocessing import Pool
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'research/p104-joint-contact/WORD.json.gz'
NEW = HERE / 'inputs/successor-word.json.gz'
COMPILER = ROOT / 'research/p104-native-channel/vendor/clifford_exact.py'
LITERAL = ROOT / 'research/p104-native-channel/vendor/native_verify.py'
DENSE = ROOT / 'research/p104-contact-independent-audit/capsule/outputs/p104-native-contact-audit-20261025/check.py'
MODULES = {}
DESCRIPTORS = {}
FRAMES = {}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    pins = read(HERE / 'SOURCES.json')
    for row in pins['files']:
        if row['usage'] == 'input':
            need(digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'live source: ' + row['path'])
    retained = read(HERE / 'INPUTS.json')['files']
    for row in retained:
        raw = (HERE / row['path']).read_bytes()
        need(digest(raw) == row['sha256'], 'retained source: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'retained Git blob: ' + row['path'])
    prior = read(HERE / 'inputs/predecessor-sources.json')
    for path in (OLD, COMPILER, LITERAL, DENSE):
        rel = path.relative_to(ROOT).as_posix()
        rows = [row for row in prior['files'] if row['path'] == rel]
        need(len(rows) == 1 and rows[0]['sha256'] == digest(path.read_bytes()), 'prior engine/word pin: ' + rel)
    return {'live': len([r for r in pins['files'] if r['usage'] == 'input']), 'retained': len(retained)}


def load(name, path):
    # Compile authenticated source directly, without consulting .pyc files.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def initialize():
    authenticate()
    MODULES['C'] = load('binding_clifford', COMPILER)
    MODULES['V'] = load('binding_literal', LITERAL)
    MODULES['D'] = load('binding_dense', DENSE)
    DESCRIPTORS.clear()
    FRAMES.clear()


def native_frame(basis):
    key = tuple(basis)
    if key not in FRAMES:
        FRAMES[key] = MODULES['C'].canonical_frame(9, key)
    return FRAMES[key]


def span(basis):
    values = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in values, 'independent nine-bit frame')
        values |= {x ^ value for x in values}
    return values


def occurrences(word):
    """Bind every literal event and endpoint, including owned returns."""
    frames = word['frames']
    spans = [span(f) for f in frames]
    public = word['public']
    need(public == 735 and len(word['initial']) == len(word['final']) == public, 'P104 public domain')
    live, ports = word['live'], word['ports']
    need(len(live) == len(ports) == 104 and len(set(live)) == 104, 'P104 live ports')
    need(all(type(r) is int and 0 <= r < 112 for r in live), 'live input domain')
    need(all(type(q) is int and 0 < q < 512 for q in ports), 'native port domain')
    main = set(live) | {r + 112 for r in live}
    current = dict(enumerate(word['initial']))
    owned, result = set(), []
    for i, event in enumerate(word['program']):
        op, reg = event[:2]
        if op == 'MOVE':
            _, _, left, right, private = event
            need(type(private) is bool and private == (reg in owned), 'MOVE ownership')
            need(current.get(reg) == left, 'MOVE source frame')
            need(spans[right] < spans[left] if private else spans[left] < spans[right], 'strict MOVE nesting')
            result.append({'site': ['event', i, reg, private], 'task': ['move', left, right, 0]})
            current[reg] = right
        elif op == 'INIT':
            need(public <= reg < public + 8 and reg not in current, 'owned INIT')
            owned.add(reg)
            current[reg] = event[2]
        elif op == 'CLEAR':
            need(reg in owned and current[reg] == event[2], 'owned CLEAR frame')
            owned.remove(reg)
            del current[reg]
        elif op in ('ADD', 'COPY', 'SCALE'):
            need(current.get(reg) == event[-1], 'scalar destination chart')
            if op != 'SCALE':
                need(current.get(event[2]) == event[-1], 'scalar source chart')
                if op == 'COPY':
                    need(reg in owned, 'COPY ownership')
        else:
            raise ValueError('unknown opcode')
    need(not owned and current == dict(enumerate(word['final'])), 'complete final frame inventory')
    for reg in range(public):
        if reg not in main:
            a, b = word['initial'][reg], word['final'][reg]
            need(spans[a] <= spans[b], 'nested helper endpoints')
            result.append({'site': ['helper', reg], 'task': ['helper', a, b, 0]})
    for reg, port in zip(live, ports):
        result.append({'site': ['main_in', reg], 'task': ['main_in', word['initial'][reg], 0, port]})
    for reg, port in zip(live, ports):
        result.append({'site': ['main_out', reg + 112], 'task': ['main_out', word['final'][reg + 112], 0, port]})
    need(len({tuple(r['site']) for r in result}) == len(result), 'unique occurrence sites')
    return result


def descriptor(word, task):
    C, V = MODULES['C'], MODULES['V']
    kind, a, b, port = task
    left = word['frames'][a]
    cache_key = (kind if kind not in ('move', 'helper') else 'frame_pair', tuple(left),
                 tuple(word['frames'][b]) if kind in ('move', 'helper') else port)
    if cache_key in DESCRIPTORS:
        return DESCRIPTORS[cache_key]
    if kind in ('move', 'helper'):
        right = word['frames'][b]
        op = native_frame(left).adjoint().then(native_frame(right))
        expected = V.adjoint(V.frame(left, 9)) + V.frame(right, 9)
        boundary = ['frame_pair', left, right]
        rank = abs(len(left) - len(right))
    elif kind == 'main_in':
        op = C.cgate(9, port, 1).adjoint().then(native_frame(left))
        expected = V.adjoint((('C', port, 1),)) + V.frame(left, 9)
        boundary, rank = ['main_in', left, port], 0
    else:
        need(kind == 'main_out', 'known task kind')
        op = native_frame(left).adjoint().then(C.cgate(9, port, -1).then(C.fourier(9)))
        expected = V.adjoint(V.frame(left, 9)) + (('C', port, -1),) + V.fourier(9)
        boundary, rank = ['main_out', left, port], 0
    recipe, _ = C.lower_child(op)
    need(recipe['rank'] == rank, 'native rank equals boundary dimension gap')
    spec = {'dimension': 9, 'boundary': boundary, 'rank': rank, 'recipe': recipe,
            'actual': V.recipe(recipe), 'expected': expected}
    DESCRIPTORS[cache_key] = spec
    return spec


def inventory(word):
    sites = occurrences(word)
    by_task, operators = {}, {}
    for task in sorted({tuple(row['task']) for row in sites}):
        spec = descriptor(word, task)
        key = digest(canonical(spec))
        if key in operators:
            need(canonical(operators[key]) == canonical(spec), 'operator key collision')
        operators[key] = spec
        by_task[task] = key
    for row in sites:
        row['operator'] = by_task[tuple(row['task'])]
    return sites, by_task, operators


def bind_reference(receipt, by_task, operators):
    need(receipt['schema'] == 'p104-5551-dense-inventory/1', 'prior receipt schema')
    records = {}
    for task, rank, matrix in receipt['maps']:
        task = tuple(task)
        need(task not in records, 'duplicate prior task')
        need(task in by_task, 'unexpected prior task')
        need(type(rank) is int and rank == operators[by_task[task]]['rank'], 'prior task rank')
        need(isinstance(matrix, str) and len(matrix) == 64 and all(c in '0123456789abcdef' for c in matrix), 'prior matrix digest format')
        records[task] = matrix
    need(set(records) == set(by_task), 'complete prior task coverage')
    result = {}
    for task, matrix in records.items():
        key = by_task[task]
        if key in result:
            need(result[key]['matrix_sha256'] == matrix, 'same operator has consistent prior evidence')
        else:
            result[key] = {'matrix_sha256': matrix, 'prior_tasks': []}
        result[key]['prior_tasks'].append(list(task))
    for row in result.values():
        row['prior_tasks'].sort()
    return result


def compare(job):
    key, spec = job
    D = MODULES['D']
    actual, expected = D.compile_circuit(spec['actual']), D.compile_circuit(spec['expected'])
    matrix = hashlib.sha256()
    for column in range(512):
        left, right = D.dense_column(actual, column), D.dense_column(expected, column)
        need(left == right, 'exact matrix column ' + str(column))
        re, im, den = left
        need(sum(v*v for v in re) + sum(v*v for v in im) == 1 << (2*den), 'exact column norm')
        need(sum(bool(a or b) for a, b in zip(re, im)) == 1 << spec['rank'], 'exact column support rank')
        matrix.update(json.dumps([column, den, re, im], separators=(',', ':')).encode())
    return key, matrix.hexdigest()


def reject(function, message):
    try:
        function()
    except ValueError as error:
        need(message in str(error), 'unexpected control failure: ' + str(error))
        return 'rejected'
    raise ValueError('control accepted: ' + message)


def controls(receipt, old_tasks, old_ops, new_ops, reused, fresh, word, tasks):
    out = {}
    for label, edit, reason in [
        ('missing_task', lambda r: r['maps'].pop(), 'complete prior task coverage'),
        ('duplicate_task', lambda r: r['maps'].append(r['maps'][0]), 'duplicate prior task'),
        ('wrong_rank', lambda r: r['maps'][0].__setitem__(1, 99), 'prior task rank'),
        ('extra_task', lambda r: r['maps'].append([['move', -1, -1, 0], 0, '0'*64]), 'unexpected prior task'),
    ]:
        bad = deepcopy(receipt)
        edit(bad)
        out[label] = reject(lambda: bind_reference(bad, old_tasks, old_ops), reason)
    key = sorted(fresh)[0]
    spec = deepcopy(new_ops[key])
    need(key not in reused, 'fresh map cannot inherit evidence')
    out['uncovered_operator'] = 'not reused'
    task = next(t for t in tasks if tasks[t] in reused and t[0] == 'move' and 2 <= len(word['frames'][t[1]]) < 9)
    changed = dict(word, frames=list(word['frames']))
    changed['frames'][task[1]] = list(reversed(word['frames'][task[1]]))
    need(canonical(descriptor(changed, task)) != canonical(descriptor(word, task)), 'same-label changed-frame invalidation')
    out['same_label_changed_frame'] = 'invalidates reuse'
    renamed = dict(word, frames=word['frames'] + [word['frames'][task[1]]])
    renamed_task = (task[0], len(word['frames']), task[2], task[3])
    need(canonical(descriptor(renamed, renamed_task)) == canonical(descriptor(word, task)), 'frame renumbering preserves exact descriptor')
    out['renumbered_identical_frame'] = 'same descriptor'
    bad_word = deepcopy(word)
    event = next(e for e in bad_word['program'] if e[0] == 'MOVE' and e[4])
    event[4] = False
    out['owned_return_flag'] = reject(lambda: occurrences(bad_word), 'MOVE ownership')
    for field, edit in [
        ('frame_bytes', lambda s: s['boundary'].__setitem__(1, list(reversed(s['boundary'][1])))),
        ('recipe_phase', lambda s: s['recipe']['left'].__setitem__('phase', (s['recipe']['left']['phase'] + 1) % 4)),
        ('literal_phase', lambda s: s.__setitem__('expected', tuple(s['expected']) + (('phase', 1),))),
    ]:
        candidate = next(v for v in new_ops.values() if v['boundary'][0] == 'frame_pair' and len(v['boundary'][1]) >= 2)
        bad = deepcopy(candidate)
        edit(bad)
        need(digest(canonical(bad)) != digest(canonical(candidate)), 'descriptor mutation invalidates ' + field)
        out[field] = 'invalidates reuse'
    V, D = MODULES['V'], MODULES['D']
    actual, expected = tuple(spec['actual']), tuple(spec['expected'])
    phase = actual + (('phase', 1),)
    need(V.tableau(phase) == V.tableau(actual), 'phase-only control preserves tableau')
    out['global_phase'] = {'first_rejected_column': D.first_difference(phase, expected), 'tableau_unchanged': True}
    flipped = list(actual)
    i = next(i for i, gate in enumerate(flipped) if gate[0] == 'C')
    flipped[i] = ('C', flipped[i][1], -flipped[i][2])
    out['child_sign'] = {'first_rejected_column': D.first_difference(tuple(flipped), expected)}
    bad = deepcopy(spec)
    bad['rank'] += 1
    out['support_rank'] = reject(lambda: compare(('bad', bad)), 'exact column support rank')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--inventory-only', action='store_true')
    parser.add_argument('--jobs', type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    pins = authenticate()
    initialize()
    old, new = read(OLD), read(NEW)
    _, old_tasks, old_ops = inventory(old)
    sites, tasks, operators = inventory(new)
    receipt = read(HERE / 'inputs/predecessor-full-check.json')
    reference = bind_reference(receipt, old_tasks, old_ops)
    reused = set(operators) & set(reference)
    fresh = set(operators) - set(reference)
    need(fresh and reused, 'both changed and retained operators exist')
    # A hash is an index, not the equality test for evidence reuse.
    for key in reused:
        need(canonical(operators[key]) == canonical(old_ops[key]), 'exact reused descriptor bytes')
    summary = {
        'status': 'INVENTORY_ONLY',
        'scope': 'Finite nine-axis native operators only; inherited full-run evidence is explicit. No all-width or complete supplier admission.',
        'source_authentication': pins,
        'prior_tasks': len(old_tasks), 'prior_operators': len(old_ops),
        'successor_tasks': len(tasks), 'successor_operators': len(operators),
        'successor_occurrences': len(sites),
        'occurrence_kinds': dict(sorted(Counter(r['task'][0] for r in sites).items())),
        'reused_operators': len(reused), 'fresh_operators': len(fresh),
        'reused_occurrences': sum(r['operator'] in reused for r in sites),
        'fresh_occurrences': sum(r['operator'] in fresh for r in sites),
        'fresh_ranks': dict(sorted(Counter(str(operators[k]['rank']) for k in fresh).items())),
    }
    print(json.dumps(summary, sort_keys=True), flush=True)
    if args.inventory_only:
        return
    summary['controls'] = controls(receipt, old_tasks, old_ops, operators, reused, fresh, new, tasks)
    samples = set()
    for kind in sorted({t[0] for t in tasks}):
        samples.add(next(tasks[t] for t in sorted(tasks) if t[0] == kind and tasks[t] in reused))
    jobs = [(key, operators[key]) for key in sorted(fresh | samples)]
    results = {}
    if args.jobs == 1:
        results.update(map(compare, jobs))
    else:
        with Pool(args.jobs, initializer=initialize) as pool:
            for count, (key, matrix) in enumerate(pool.imap_unordered(compare, jobs, chunksize=2), 1):
                results[key] = matrix
                if count % 50 == 0:
                    print('Exact operators completed:', count, '/', len(jobs), flush=True)
    for key in samples:
        need(results[key] == reference[key]['matrix_sha256'], 'retained positive control matrix digest')
    summary['positive_control_operators'] = sorted(samples)
    summary['fresh_complex_entries_compared'] = len(fresh) * 512 * 512
    summary['status'] = 'PASS_P104_SUCCESSOR_NATIVE_BINDING'
    records = []
    for key in sorted(operators):
        records.append({'operator': key, 'rank': operators[key]['rank'],
                        'evidence': 'reused_PR5572' if key in reused else 'fresh_all_512_columns',
                        'matrix_sha256': reference[key]['matrix_sha256'] if key in reused else results[key],
                        'prior_tasks': reference[key]['prior_tasks'] if key in reused else []})
    bindings = {'schema': 'p104-successor-native-binding/1', 'operators': records, 'occurrences': sites}
    summary['bindings_sha256'] = digest(canonical(bindings))
    for name, value in {'RESULT.json': summary, 'BINDINGS.json': bindings}.items():
        path = HERE / name
        if args.write:
            if name == 'BINDINGS.json':
                # One record per line keeps the large occurrence inventory reviewable.
                text = '{"schema": "p104-successor-native-binding/1",\n"operators": [\n'
                text += ',\n'.join(canonical(row).decode() for row in value['operators'])
                text += '\n],\n"occurrences": [\n'
                text += ',\n'.join(canonical(row).decode() for row in value['occurrences'])
                path.write_text(text + '\n]}\n')
            else:
                path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
        else:
            need(canonical(read(path)) == canonical(value), 'reproduced ' + name)
    print('PASS_P104_SUCCESSOR_NATIVE_BINDING', flush=True)


if __name__ == '__main__':
    main()
