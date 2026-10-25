#!/usr/bin/env python3
"""Independent frame/billing audit; no physical operator or supplier admission.

mihir-s-05, with substantial OpenAI Codex assistance. Apache-2.0.
The source constructor is used only to emit the object being checked.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source'
BASE = 'research/kappa-rebuild/complex/full-identity-certificates/'
OLD = 'research/fresh-helper-boundary/'
JOIN = 'research/missing-join-frame/'
NEW = 'research/joint-helper-lattice/'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    data = (SOURCE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


@lru_cache(None)
def reduced(basis):
    """Unique reduced binary row basis, independently implemented by elimination."""
    pivots = {}
    for value in basis:
        need(type(value) is int and 0 < value < 512, 'invalid nine-axis vector')
        for bit in sorted(pivots, reverse=True):
            if value & (1 << bit):
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            for other in pivots:
                if pivots[other] & (1 << bit):
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def basis(row):
    result = reduced(tuple(row))
    need(len(result) == len(row), 'dependent frame basis')
    return result


def contained(left, right):
    return len(reduced(tuple(left) + tuple(right))) == len(right)


def rank_step(left, right):
    need(left != right and contained(left, right), 'non-nested positive transport')
    return len(right) - len(left)


def operands(operation):
    need(operation[0] in ('add', 'copy', 'scale', 'clear'), 'unknown scalar operation')
    return operation[1:3] if operation[0] in ('add', 'copy') else operation[1:2]


def contacts(program):
    result, counts, phase = {}, Counter(), None
    for position, event in enumerate(program):
        if event[0] == 'phase':
            phase = event[1]
        if event[0] == 'scalar' and all(r[0] == 'L' for r in operands(event[1])):
            key = (phase, counts[phase])
            result[key] = position
            counts[phase] += 1
    return result


def reconstruct():
    """Apply pinned edits to the source declarations, without its constructor."""
    c = read(BASE + 'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    programs = read(BASE + 'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    need(set(programs) == {'forward', 'backward'}, 'both native orientations required')
    need(len(c['start']) == len(c['final']) == 632, '632 persistent fields')
    for row in c['frames']:
        basis(row)
    maps = {d: contacts(p) for d, p in programs.items()}
    need(maps['forward'].keys() == maps['backward'].keys(), 'dual contact inventory')
    for key in maps['forward']:
        f = programs['forward'][maps['forward'][key]]
        b = programs['backward'][maps['backward'][key]]
        expected = deepcopy(f[1])
        if expected[0] == 'add':
            expected[1], expected[2] = expected[2], expected[1]
            expected[3] = -expected[3]
        else:
            need(expected[0] == 'scale', 'reversible persistent scalar')
            expected[2], expected[3] = expected[3], expected[2]
        need(b[1] == expected and b[2] == f[2], 'exact scalar inverse-transpose pair')
    parent = read(OLD + 'CHANGES.json')
    for label, field in [('entrances', 'start'), ('exits', 'final')]:
        seen = set()
        for role, old, new in parent[label]:
            need(224 <= role < 632 and role not in seen, 'parent helper edit domain')
            seen.add(role)
            need(c[field][role] == old, 'parent boundary source pin')
            c[field][role] = new
    seen = set()
    for phase, ordinal, old, new in parent['gates']:
        key = phase, ordinal
        need(key not in seen, 'duplicate parent contact')
        seen.add(key)
        for d in programs:
            event = programs[d][maps[d][key]]
            need(event[2] == old, 'parent contact source pin')
            event[2] = new
    join = read(JOIN + 'PATCH.json')
    need((join['phase'], join['ordinal']) == ('B', 480), 'predecessor contact')
    basis(join['new_basis'])
    c['frames'].append(join['new_basis'])
    for d in programs:
        event = programs[d][maps[d]['B', 480]]
        need(event[2] == join['old_frame'], 'predecessor contact source pin')
        event[2] = len(c['frames']) - 1
    old_c, old_programs = deepcopy(c), deepcopy(programs)
    counts = apply_patch(c, programs, read(NEW + 'PATCH.json'))
    need(c['start'][:224] == old_c['start'][:224] and
         c['final'][:224] == old_c['final'][:224], 'unchanged main boundaries')
    return old_c, old_programs, c, programs, counts


def apply_patch(c, programs, patch):
    need(patch['source_head'] == '322e0ec764aa7ef7801383feb1f656e460dd8bed', 'patch predecessor')
    maps = {d: contacts(p) for d, p in programs.items()}
    seen, counts = set(), Counter()
    for change in patch['changes']:
        phase, ordinal = change['phase'], change['ordinal']
        key = phase, ordinal
        need(key not in seen, 'duplicate patch location')
        seen.add(key)
        old, new = basis(change['old']), basis(change['new'])
        need(old != new, 'unchanged patch entry')
        # Independent labels: append every new basis; compare subspaces, not IDs.
        frame = len(c['frames'])
        c['frames'].append(change['new'])
        if phase in ('entrance', 'exit'):
            need(224 <= ordinal < 632, 'patch changes a non-helper boundary')
            field = 'start' if phase == 'entrance' else 'final'
            need(basis(c['frames'][c[field][ordinal]]) == old, 'patch boundary source pin')
            c[field][ordinal] = frame
        else:
            for d in programs:
                need(key in maps[d], 'unknown scalar contact')
                event = programs[d][maps[d][key]]
                need(basis(c['frames'][event[2]]) == old, 'patch scalar source pin')
                event[2] = frame
        counts[phase] += 1
    return dict(sorted(counts.items()))


def skeleton(program, c):
    """Retained nontransport events; only source-prescribed center fusion/wrappers."""
    out, position = [], 0
    while position < len(program):
        e = deepcopy(program[position])
        position += 1
        if e[0] == 'climb' or (e[0] in ('adapter', 'residual_adapter') and e[2] >= 224):
            continue
        if e[0] == 'center':
            second = program[position]
            need(second[0] == 'center' and second[1] == e[1] == 0 and
                 second[2] == e[3] and sorted([e[4], second[4]]) == [3, 5],
                 'retained center split')
            e = ['center', 0, e[2], second[3], 8]
            position += 1
        out.append(normalize(e, c))
    return out


def normalize(e, c):
    e = deepcopy(e)
    indices = {'scalar': [2], 'warp': [3, 4], 'center': [2, 3],
               'climb': [3, 4], 'adapter': [], 'residual_adapter': [], 'phase': []}
    need(e[0] in indices, 'unknown native event')
    for i in indices[e[0]]:
        need(type(e[i]) is int and 0 <= e[i] < len(c['frames']), 'invalid frame reference')
        e[i] = basis(c['frames'][e[i]])
    return e


def demands(word, c):
    """Build each field's ordered demand path first; no source synthesis helpers."""
    requests = defaultdict(list)
    for position, e in enumerate(word):
        if e[0] == 'scalar':
            for role in operands(e[1]):
                if role[0] == 'L':
                    requests[role[1]].append((position, e[2], e[2]))
        elif e[0] == 'warp':
            need(e[1][0] == 'L', 'persistent warp domain')
            requests[e[1][1]].append((position, e[3], e[4]))
    plan, paid = {}, Counter()
    for role in range(632):
        current = basis(c['frames'][c['start'][role]])
        requests[role].append((len(word), basis(c['frames'][c['final'][role]]), None))
        transitions = []
        for position, target, after in requests[role]:
            if current != target:
                rank = rank_step(current, target)
                transitions.append((position, current, target, rank))
                paid[rank] += 1
            current = target if after is None else after
        plan[role] = transitions
    return plan, paid


def audit_program(program, c, wanted_word, expected_c):
    frames = [basis(row) for row in c['frames']]
    need(c.keys() == expected_c.keys(), 'canonical field inventory')
    for field in c.keys() - {'frames', 'start', 'final'}:
        need(c[field] == expected_c[field], 'retained canonical declaration: ' + field)
    for field in ('start', 'final'):
        need(len(c[field]) == 632 and [frames[i] for i in c[field]] ==
             [basis(expected_c['frames'][i]) for i in expected_c[field]], 'emitted boundary mismatch')
    expected_plan, paid = demands(wanted_word, expected_c)
    current = {('L', i): frames[f] for i, f in enumerate(c['start'])}
    actual_plan, actual_word, invoice, event_counts = defaultdict(list), [], Counter(), Counter()
    owned_zero = {}
    for raw in program:
        e = normalize(raw, c)
        kind = e[0]
        event_counts[kind] += 1
        if kind == 'climb':
            _, _, role, old, new, rank = e
            need(type(role) is int and 0 <= role < 632, 'transport role domain')
            need(current['L', role] == old, 'transport source state')
            need(rank == rank_step(old, new), 'emitted transport rank')
            current['L', role] = new
            actual_plan[role].append((len(actual_word), old, new, rank))
            invoice[rank] += 1
            continue
        if kind == 'scalar':
            op, frame = e[1:]
            role = tuple(op[1])
            need(role[0] in ('L', 'C'), 'scalar role kind')
            if op[0] == 'clear':
                need(role == ('C', 0), 'borrowed field clear')
                current[role] = frame
                owned_zero[role] = True
            else:
                for operand in operands(op):
                    need(current.get(tuple(operand)) == frame, 'scalar common frame')
                if op[0] == 'copy':
                    need(role == ('C', 0), 'borrowed field copy')
                else:
                    coefficient = Fraction(*op[-2:])
                    n, d = abs(coefficient.numerator), coefficient.denominator
                    need(n > 0 and d & (d - 1) == 0, 'non-dyadic scalar')
                    if op[0] == 'scale':
                        need(n & (n - 1) == 0, 'nonunit dyadic scale')
                    else:
                        need(op[0] == 'add' and op[1] != op[2], 'invalid shear')
                if role[0] == 'C':
                    owned_zero[role] = False
        elif kind == 'warp':
            role = tuple(e[1])
            need(current.get(role) == e[3], 'warp source state')
            current[role] = e[4]
        elif kind == 'center':
            role = 'C', e[1]
            old, new, rank = e[2:]
            need(role == ('C', 0) and current.get(role) == old, 'owned center source state')
            need((contained(old, new) or contained(new, old)) and old != new,
                 'owned center nesting')
            need(rank == abs(len(new) - len(old)) == 8, 'owned center charge')
            current[role] = new
            invoice[rank] += 1
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'unknown event')
        actual_word.append(e)
    need(actual_word == wanted_word, 'retained logical/owned event word mismatch')
    need(all(actual_plan[r] == expected_plan[r] for r in range(632)), 'chronological demand path mismatch')
    need([current['L', r] for r in range(632)] == [frames[f] for f in c['final']], 'final persistent frames')
    need(owned_zero == {('C', 0): True}, 'owned center not finally cleared')
    centers = sum(e[0] == 'center' for e in wanted_word)
    need(centers == 8, 'all eight center jobs retained')
    paid[8] += centers
    need(invoice == paid, 'complete paid invoice mismatch')
    return {'paid': dict(sorted(invoice.items())), 'events': dict(sorted(event_counts.items())),
            'persistent_transports': sum(len(v) for v in expected_plan.values()),
            'scalar_contacts': event_counts['scalar'], 'owned_center_jobs': centers}


def helper_profile(c):
    result = Counter()
    for r in range(224, 632):
        a, b = (basis(c['frames'][c[field][r]]) for field in ('start', 'final'))
        result[rank_step(a, b)] += 1
    need(sum(result.values()) == 408, '408 independent helper fields')
    return dict(sorted(result.items()))


def source_inputs():
    rows = json.loads((HERE / 'UPSTREAM.json').read_bytes())['files']
    for row in rows:
        path = HERE / row['path']
        need(path.resolve().is_relative_to(SOURCE.resolve()) and path.is_file() and not path.is_symlink(),
             'invalid source snapshot path')
        raw = path.read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch')
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source Git blob mismatch')
    return rows


def emit_source(rows):
    # Only the pinned constructor is executed. Its verification engines are never imported.
    with tempfile.TemporaryDirectory(prefix='pr4470-frame-audit-') as directory:
        root = Path(directory)
        for row in rows:
            target = root / row['upstream_path']
            need(target.resolve().is_relative_to(root), 'invalid upstream snapshot path')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / row['path'], target)
        process = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'emit_source.py'), str(root)],
                                 cwd=root, capture_output=True, text=True, encoding='utf-8', timeout=60)
        need(process.returncode == 0, 'source constructor failed: ' + process.stderr)
        return json.loads(process.stdout)


def rejected(label, thunk, message):
    try:
        thunk()
    except ValueError as exc:
        need(message in str(exc), 'wrong rejection for ' + label + ': ' + str(exc))
        return label
    raise ValueError('negative control accepted: ' + label)


def main():
    rows = source_inputs()
    old_c, old_programs, new_c, new_programs, changes = reconstruct()
    emitted = emit_source(rows)
    need(set(emitted['programs']) == set(emitted['before']) == {'forward', 'backward'}, 'both emitted orientations')
    results = {}
    for name, c, originals, actual_c, actual in [
        ('old', old_c, old_programs, emitted['baseline'], emitted['before']),
        ('new', new_c, new_programs, emitted['canonical'], emitted['programs'])]:
        results[name] = {d: audit_program(actual[d], actual_c, skeleton(originals[d], c), c) for d in actual}
        need(results[name]['forward']['paid'] == results[name]['backward']['paid'], 'orientation invoice agreement')
        results[name]['helpers'] = helper_profile(c)
    declared = read(NEW + 'RESULT.json')
    need(results['new']['helpers'] == {int(k): v for k, v in declared['local_helpers'].items()}, 'declared helper profile')
    need(results['new']['forward']['paid'] == {int(k): v for k, v in declared['local_paid'].items()}, 'declared paid profile')
    need(changes == emitted['changes'], 'constructor patch coverage')
    need(changes.get('entrance') == 38 and changes.get('exit') == 47 and
         sum(v for k, v in changes.items() if k not in ('entrance', 'exit')) == 414, '499 changed locations')
    controls = [rejected('rank-only non-nested transition', lambda: rank_step((1,), (4, 2)), 'non-nested'),
                rejected('dependent frame basis', lambda: basis([1, 2, 3]), 'dependent')]
    need(basis([1, 2]) == basis([3, 2]) and rank_step((), basis([3, 2])) == 2, 'equivalent-basis positive control')
    good = emitted['programs']['forward']
    c = emitted['canonical']
    word = skeleton(new_programs['forward'], new_c)
    mutations = [('wrong emitted rank', 'climb', lambda e: e.__setitem__(5, e[5] + 1), 'emitted transport rank'),
                 ('changed scalar coefficient', 'scalar', lambda e: e[1].__setitem__(3, e[1][3] + 1), 'word mismatch'),
                 ('changed warp operator', 'warp', lambda e: e.__setitem__(2, e[2] + 1), 'word mismatch'),
                 ('borrowed clear', 'scalar', lambda e: e.__setitem__(1, ['clear', ['L', 0]]), 'borrowed field clear')]
    for label, kind, mutate, message in mutations:
        bad = deepcopy(good)
        event = next(e for e in bad if e[0] == kind and (kind != 'scalar' or e[1][0] == 'add'))
        mutate(event)
        controls.append(rejected(label, lambda: audit_program(bad, c, word, new_c), message))
    for kind, message in [('climb', 'scalar common frame'), ('center', 'scalar common frame')]:
        bad = deepcopy(good)
        del bad[next(i for i, e in enumerate(bad) if e[0] == kind)]
        controls.append(rejected('unpaid ' + kind, lambda: audit_program(bad, c, word, new_c), message))
    patch = read(NEW + 'PATCH.json')
    for label, mutate, message in [
        ('duplicate edit', lambda p: p['changes'].append(deepcopy(p['changes'][0])), 'duplicate patch'),
        ('main-field credit', lambda p: p['changes'][0].__setitem__('ordinal', 0), 'non-helper'),
        ('wrong old basis', lambda p: p['changes'][0].__setitem__('old', [1]), 'source pin')]:
        bad = deepcopy(patch)
        mutate(bad)
        controls.append(rejected(label, lambda: apply_patch(deepcopy(old_c), deepcopy(old_programs), bad), message))
    def mass(profile):
        return sum(k * v for k, v in profile.items())
    report = {'status': 'PASS_PR4470_CHRONOLOGICAL_FRAME_AUDIT', 'scope': 'Chronological frames, retained event word, local paid and helper profiles; no physical phases, full column identity, controller or kappa admission.',
              'source_files': len(rows), 'changes': changes, 'profiles': results,
              'paid_job_reduction': sum(results['old']['forward']['paid'].values()) - sum(results['new']['forward']['paid'].values()),
              'paid_mass_change': mass(results['new']['forward']['paid']) - mass(results['old']['forward']['paid']),
              'helper_mass_change': mass(results['new']['helpers']) - mass(results['old']['helpers']),
              'negative_controls': controls, 'positive_controls': ['actual predecessor and changed source constructors, both orientations', 'equivalent binary bases']}
    text = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(text, encoding='utf-8', newline='\n')
    else:
        need(json.loads((HERE / 'RESULT.json').read_bytes()) == json.loads(text), 'committed audit receipt differs')
    print(text)


if __name__ == '__main__':
    main()
