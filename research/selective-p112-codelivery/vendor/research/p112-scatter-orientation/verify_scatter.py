#!/usr/bin/env python3
"""Exact orientation witness and restored pre-B target-basis sandwich.

This is a finite, source-bound operator audit, not a supplier improvement.
P112 geometry and integer basis are reused with their predecessor attribution.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import types
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[1]
PROVIDER = 'candidate/strict/global/base/providers/gauge44/'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def tr(a):
    return [list(row) for row in zip(*a)]


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def inv(a):
    n = len(a)
    m = [[Q(x) for x in row]+e for row, e in zip(a, eye(n))]
    for j in range(n):
        k = next((i for i in range(j, n) if m[i][j]), None)
        need(k is not None, 'singular matrix')
        m[k], m[j] = m[j], m[k]
        d = m[j][j]
        m[j] = [x/d for x in m[j]]
        for i in range(n):
            if i != j and m[i][j]:
                d = m[i][j]
                m[i] = [x-d*y for x, y in zip(m[i], m[j])]
    return [row[n:] for row in m]


def literal_constant(path, name):
    tree = ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


def load_module(name, path):
    # Compile the authenticated source itself; never load a neighboring .pyc.
    m = types.ModuleType(name)
    m.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m


def add(row, source, c):
    for k, x in list(source.items()):
        z = row.get(k, Q(0)) + c*x
        if z:
            row[k] = z
        else:
            row.pop(k, None)


def replay(word, events, check_endpoint=True):
    """All 704 ordinary scalar columns and literal common-frame labels.

    Native Fourier/adapter operators are unchanged. Same-frame identities at
    the modified cut hold for arbitrary 512-address vectors, so no operator
    sampling or re-certification of unchanged Clifford children is needed.
    """
    n, v = 2*word['v']+word['R'], word['v']
    rows = {('L', i): {i: Q(1)} for i in range(n)}
    labels = {('L', i): word['start'][i] for i in range(n)}
    profile = Counter()
    for event in events:
        tag = event[0]
        if tag == 'phase':
            continue
        if tag == 'climb':
            _, _, i, old, new, rank = event
            need(labels['L', i] == old, 'ordinary frame source')
            labels['L', i] = new
            profile[rank] += 1
        elif tag == 'center':
            _, i, old, new, rank = event
            need(labels['C', i] == old, 'private frame source')
            labels['C', i] = new
            profile[rank] += 1
        elif tag == 'scalar':
            _, op, frame = event
            kind, dest = op[0], tuple(op[1])
            if kind == 'clear':
                need(dest[0] == 'C', 'ordinary clearing forbidden')
                rows[dest], labels[dest] = {}, frame
            elif kind == 'copy':
                src = tuple(op[2])
                need(dest[0] == 'C' and labels[src] == frame, 'private copy')
                rows[dest], labels[dest] = dict(rows[src]), frame
            elif kind == 'scale':
                need(labels[dest] == frame, 'scale frame')
                c = Q(op[2], op[3]); need(c != 0, 'invertible scale')
                rows[dest] = {k: c*x for k, x in rows[dest].items()}
            elif kind == 'add':
                src = tuple(op[2])
                need(src != dest and labels[src] == labels[dest] == frame,
                     'same-frame scalar ADD')
                add(rows[dest], rows[src], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar gate')
        elif tag in ('adapter', 'residual_adapter'):
            # These fixed recipes do not change the normalized scalar rows.
            continue
        else:
            raise ValueError('unknown event')
    need(all(not row for role, row in rows.items() if role[0] == 'C'),
         'private workspace restoration')
    if check_endpoint:
        need(all(rows['L', i] == ({i: Q(1), i-v: Q(1)} if v <= i < 2*v
                                 else {i: Q(1)}) for i in range(n)),
             'complete arbitrary-input scalar endpoint')
    return rows, labels, profile


def basis_events(ports, ops):
    """Expand swaps into three signed ADDs and one sign scale."""
    out = []
    def plus(i, j, sign):
        out.append(['scalar', ['add', ['L', 112+ports[i]],
                              ['L', 112+ports[j]], sign, 1], 0])
    def neg(i):
        out.append(['scalar', ['scale', ['L', 112+ports[i]], -1, 1], 0])
    for op in ops:
        if op[0] == 'add':
            plus(op[1], op[2], op[3])
        elif op[0] == 'neg':
            neg(op[1])
        elif op[0] == 'swap':
            i, j = op[1:]
            plus(i, j, 1); plus(j, i, -1); plus(i, j, 1); neg(j)
        else:
            raise ValueError('unknown basis operation')
    return out


def install(word, events, scatter, blocks):
    pre, post = [], []
    for b in blocks:
        # R U=I, hence U is reverse(R) with each gate inverted.
        pre.extend(basis_events(b['ports'], [
            (op[0], op[1], op[2], -op[3]) if op[0] == 'add' else op
            for op in reversed(b['reduce_ops'])]))
        post.extend(basis_events(b['ports'], b['reduce_ops']))
    out, emitted = [], set()
    for event in events:
        if event == ['phase', 'B']:
            out.extend(post)
        out.append(event)
        if event == ['phase', 'centers']:
            out.extend(pre)
        if (event[0] == 'scalar' and event[1][0] == 'add'
                and event[1][1][0] == 'L' and 112 <= event[1][1][1] < 224
                and event[1][2][0] == 'C'):
            out.pop()
            k = event[1][2][1]
            if k not in emitted:
                emitted.add(k)
                for i, row in enumerate(scatter):
                    c = row[k]
                    if c:
                        out.append(['scalar', ['add', ['L', 112+i],
                                               ['C', k], c.numerator, c.denominator], 0])
    need(emitted == set(range(8)), 'all eight native centre channels')
    return out


def run(repo):
    sources = json.loads((HERE/'SCATTER-SOURCES.json').read_text())
    for p in sources['files']:
        path = (repo if p['root'] == 'repo' else HERE)/p['path']
        need(sha(path.read_bytes()) == p['sha256'], 'source pin: '+str(path))
    with tarfile.open(repo/sources['archive'], 'r:gz') as archive:
        contents = {}
        for key, pin in sources['archive_members'].items():
            raw = archive.extractfile(pin['path']).read()
            need(sha(raw) == pin['sha256'], 'archive member: '+key)
            contents[key] = json.loads(gzip.decompress(raw))
    word, events = contents['word'], contents['programs']['forward']
    need((word['v'], word['R'], word['h']) == (112, 480, 9), 'selected dimensions')
    prefix = events[:events.index(['phase', 'centers'])]
    prefix_counts = Counter()
    for event in prefix:
        tag = event[0]
        need(tag in ('phase', 'scalar', 'climb', 'adapter', 'residual_adapter'),
             'prefix consists of invertible ordinary operations')
        prefix_counts[tag] += 1
        if tag == 'scalar':
            need(event[1][0] in ('add', 'scale'), 'no private zeroing in prefix')
            if event[1][0] == 'scale':
                need(Q(event[1][2], event[1][3]) != 0, 'nonzero prefix scale')
    suffix = events[events.index(['phase', 'B']):]
    suffix_counts = Counter()
    for event in suffix:
        tag = event[0]
        need(tag in ('phase', 'scalar', 'climb', 'adapter', 'residual_adapter'),
             'suffix consists of invertible ordinary operations')
        suffix_counts[tag] += 1
        if tag == 'scalar':
            need(event[1][0] in ('add', 'scale') and event[1][1][0] == 'L',
                 'no ordinary suffix erasure or private use')
            if event[1][0] == 'scale':
                need(Q(event[1][2], event[1][3]) != 0, 'nonzero suffix scale')
    centers = {role: k for k, role in enumerate(word['centers'])}
    need(set(centers).isdisjoint(range(112, 224)), 'independent centre carriers and targets')
    s = [[Q(0)]*8 for _ in range(112)]
    for kind, dest, src, num, den, *_ in word['cut']:
        need(kind == 'add' and 112 <= dest < 224 and src in centers,
             'canonical cut has destination-first scatter syntax')
        s[dest-112][centers[src]] += Q(num, den)
    native = Counter((e[1][1][1]-112, e[1][2][1], Q(e[1][3], e[1][4]))
                     for e in events if e[0] == 'scalar' and e[1][0] == 'add'
                     and e[1][1][0] == 'L' and 112 <= e[1][1][1] < 224
                     and e[1][2][0] == 'C')
    need(native == Counter((i, k, x) for i, row in enumerate(s)
                            for k, x in enumerate(row) if x), 'native scatter binding')
    need(sum(native.values()) == 176, 'selected cut count')
    geometry = load_module('scatter_p112_geometry',
                           repo/'research/p112-tetrad-local-decoder/verify.py')
    bp = HERE/'vendor/p112-tetrad-dual-anchor-screen/verify.py'
    basis = load_module('scatter_p112_basis', bp)
    perm = literal_constant(HERE/'vendor/selected-p112-tetrad-rank32-route/verify.py',
                            'ROOT_TO_PORT')
    roots, frame = geometry.roots_and_frame()
    groups = defaultdict(list)
    for i, root in enumerate(sorted(set(roots)-set(frame))):
        co = [geometry.dot(root, f)//4 for f in frame]
        t = tuple(j for j, x in enumerate(co) if x)
        groups[t, sum(x < 0 for x in co) % 2].append((i, co))
    blocks, receipt = [], []
    for t in sorted({t for t, _ in groups}):
        even, odd = groups[t, 0], groups[t, 1]
        e0 = [[co[j] for j in t] for _, co in even]
        e1 = [[co[j] for j in t] for _, co in odd]
        cross = mm(mm(e0, tr(e1)), basis.D_EVEN_SUM)
        need(all(x.denominator == 1 and x % 4 == 0 for row in cross for x in row),
             'integral kernel transition')
        u = tr([[-x/4 for x in row] for row in cross]+basis.D_EVEN_SUM)
        u += [eye(8)[i] for i in (0, 5, 6, 7)]
        need(all(Q(x).denominator == 1 for row in u for x in row), 'integer basis')
        u = [[int(x) for x in row] for row in u]
        need(mm(u, inv(u)) == eye(8), 'unimodular basis inverse')
        k = mm(e0+e1, tr(e0+e1))
        need(mm(u, k)[:4] == [[Q(0)]*8 for _ in range(4)], 'P112 update kernel')
        ports = [perm[i] for i, _ in even+odd]
        sb = [s[i] for i in ports]
        us = mm(u, sb)
        reader = mm(tr(inv(u)), sb)
        hybrid = sb[:4]+reader[4:]
        need(mm(tr(reader), u) == tr(sb), 'abstract transpose identity remains valid')
        need(us[:4] != [[Q(0)]*8 for _ in range(4)], 'actual scatter is not killed')
        reduce_ops = basis.reduce_to_identity(u)
        b = {'ports': ports, 'u': u, 'us': us, 'hybrid': hybrid, 'reduce_ops': reduce_ops}
        blocks.append(b)
        support = lambda a: sum(x != 0 for row in a for x in row)
        receipt.append({'tetrad': list(t), 'ports_in_U_order': ports,
                        'old_scatter': support(sb), 'correct_scatter_US': support(us),
                        'US_top_four_support': support(us[:4]),
                        'U_abstract_operations': dict(Counter(z[0] for z in reduce_ops)),
                        'U_literal_operations': len(basis_events(ports, reduce_ops))})
        if len(blocks) == 1:
            need(ports == [110, 21, 37, 47, 46, 36, 20, 111], 'witness port order')
            need(us[0][7] == -Q(1, 2) and hybrid[0][7] == 0
                 and reader[0][7] == -Q(1, 4),
                 'wrong-direction coefficient control')
            witness = {'p': [0]*7+[1], 'dirty_output': [0]*8,
                       'correct_US_p_first_output': '-1/2',
                       'inverse_transpose_reader_as_scatter_first_output': '-1/4',
                       'hybrid_reader_as_scatter_first_output': '0',
                       'ordinary_target_role': 112+ports[0]}
    need(len(blocks) == 14 and sum(r['correct_scatter_US'] for r in receipt) == 214,
         'all fourteen actual scatter supports')
    original_rows, original_labels, original_profile = replay(word, events)
    cases = []
    for count in (3, 14):
        changed = [row[:] for row in s]
        for b in blocks[:count]:
            for i, port in enumerate(b['ports']):
                changed[port] = b['us'][i]
        candidate = install(word, events, changed, blocks[:count])
        rows, labels, profile = replay(word, candidate)
        need((rows, labels, profile) == (original_rows, original_labels, original_profile),
             'complete endpoint, frames, recursive profile')
        scalars = lambda ev: Counter(e[1][0] for e in ev if e[0] == 'scalar')
        delta = scalars(candidate)-scalars(events)
        cut = sum(x != 0 for row in changed for x in row)
        need(delta == Counter(add=54*count+cut-176, scale=6*count),
             'full literal basis and scatter cost')
        # Omit the dirty-basis entrance: exact arbitrary-dirty failure control.
        bad = install(word, events, changed, blocks[:count])
        start = bad.index(['phase', 'centers'])+1
        del bad[start:start+30*count]
        bad_rows, bad_labels, bad_profile = replay(word, bad, check_endpoint=False)
        need((bad_labels, bad_profile) == (original_labels, original_profile),
             'missing entrance control keeps the labels and recursive bill')
        differences = [(role[1], j, row.get(j, Q(0)), original_rows[role].get(j, Q(0)))
                       for role, row in sorted(bad_rows.items()) if role[0] == 'L'
                       for j in range(112, 224)
                       if row.get(j, Q(0)) != original_rows[role].get(j, Q(0))]
        need(differences, 'missing entrance U must fail on arbitrary initial dirty outputs')
        target_role, dirty_column, actual, expected = differences[0]
        wrong_scatter = [row[:] for row in s]
        for b in blocks[:count]:
            for i, port in enumerate(b['ports']):
                wrong_scatter[port] = b['hybrid'][i]
        wrong_events = install(word, events, wrong_scatter, blocks[:count])
        wrong_rows, wrong_labels, wrong_profile = replay(word, wrong_events, check_endpoint=False)
        need((wrong_labels, wrong_profile) == (original_labels, original_profile),
             'wrong scatter preserves valid common-frame recipes')
        wrong_entries = [(role[1], j, row.get(j, Q(0)), original_rows[role].get(j, Q(0)))
                         for role, row in sorted(wrong_rows.items()) if role[0] == 'L'
                         for j in range(704)
                         if row.get(j, Q(0)) != original_rows[role].get(j, Q(0))]
        need(wrong_entries, 'hybrid reader wrongly installed as native scatter')
        wr, wc, wa, we = wrong_entries[0]
        cases.append({'transformed_tetrads': count, 'cut_adds': cut,
                      'extra_scalar_adds': delta['add'], 'extra_scalar_scales': delta['scale'],
                      'extra_scalar_total': sum(delta.values()), 'recursive_profile_delta': {},
                      'ordinary_columns_checked': 704, 'all_private_roles_restored': True,
                      'native_512_address_vector_identity': 'all vectors by same-frame matrix identity',
                      'missing_dirty_basis_entrance_rejected': True,
                      'missing_entrance_normalized_scalar_witness': {
                          'initial_dirty_output_role': dirty_column,
                          'final_ordinary_role': target_role,
                          'actual_coefficient': str(actual), 'required_coefficient': str(expected)},
                      'wrong_hybrid_scatter_full_endpoint_control': {
                          'changed_normalized_scalar_entries': len(wrong_entries),
                          'initial_ordinary_column': wc, 'final_ordinary_role': wr,
                          'actual_coefficient': str(wa), 'required_coefficient': str(we)}})
    return {'status': 'PASS_SELECTED_CUT_SCATTER_ORIENTATION_AND_DIRTY_SANDWICH_NO_NEW_KAPPA',
            'domain': 'Pinned selected forward native cut; exact dyadic complex vectors and arbitrary dirty ordinary roles',
            'canonical_example': word['cut'][0],
            'native_example': next(e for e in events if e[0] == 'scalar'
                                   and e[1][:3] == ['add', ['L', 118], ['C', 1]]),
            'witness': witness, 'blocks': receipt, 'sandwich_cases': cases,
            'local_witness_reachability': {
                'prefix_event_inventory': dict(prefix_counts),
                'suffix_event_inventory': dict(suffix_counts),
                'no_prefix_clear_or_copy': True,
                'no_suffix_ordinary_erasure_or_private_use': True,
                'argument': 'Every ordinary prefix gate and each centre descent is invertible. Set pre-cut outputs to zero, seven centre carriers to zero, and the eighth carrier to the inverse-descent image of any nonzero 512-vector. Inverting the ordinary prefix gives an allowed arbitrary input.'},
            'existing_recursive_profile': {str(r): n for r, n in sorted(original_profile.items())},
            'unresolved': ['Changed decoder producer before this cut', 'Rounded execution and magnitude/storage admission',
                           'New paid recursive gain and complete joint supplier', 'Hosting and all-size outer transfer']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run(args.repo)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    for case in result['sandwich_cases']:
        print(json.dumps(case, sort_keys=True))
