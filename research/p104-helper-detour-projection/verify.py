"""Check the helper-detour projection, path bound and exact source inventory.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The retained native and interval engines keep their original notices.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import product
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def span(vectors):
    out = frozenset({0})
    for v in vectors:
        out |= frozenset(x ^ v for x in out)
    return out


def basis(space):
    out, have = [], frozenset({0})
    for v in sorted(space):
        if v not in have:
            out.append(v)
            have = span(out)
    need(have == space, 'Exact subspace basis')
    return out


def dim(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'Binary subspace cardinality')
    return n.bit_length() - 1


def distance(a, b):
    return dim(a) + dim(b) - 2 * dim(a & b)


def subspaces(n):
    seen, todo = {frozenset({0})}, [frozenset({0})]
    universe = frozenset(range(1 << n))
    while todo:
        a = todo.pop()
        for v in universe - a:
            b = a | frozenset(x ^ v for x in a)
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return sorted(seen, key=lambda s: (len(s), sorted(s)))


def compositions(total, count):
    if count == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in compositions(total - first, count - 1):
                yield (first,) + tail


def signed(paid, targets):
    out = Counter(r for r in targets if r)
    out.subtract(r for r in paid if r)
    return {r: v for r, v in out.items() if v}


def evaluate(coefficients, powers):
    lo = hi = Q(0)
    for r, count in coefficients.items():
        a, b = powers[r]
        lo += count * (a if count > 0 else b)
        hi += count * (b if count > 0 else a)
    return lo, hi


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def source_modules():
    pins = read(HERE / 'SOURCES.json')
    for row in pins['direct_sources']:
        raw = (HERE / row['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'] and
             sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'Exact source bytes: ' + row['local_path'])
    return (load(HERE / 'source/clifford_exact.py', 'detour_native'),
            load(HERE / 'source/moments.py', 'detour_moments'))


def finite_geometry(C):
    spaces = subspaces(4)
    need(len(spaces) == 67, 'All binary subspaces in dimension four')
    ops = [C.canonical_frame(4, tuple(basis(s))) for s in spaces]
    inverses = [op.adjoint() for op in ops]
    for i, a in enumerate(spaces):
        for j, b in enumerate(spaces):
            actual = C.rank([x for x, z, p in inverses[i].then(ops[j]).tab[4:]])
            need(actual == distance(a, b), 'Actual native distance on every small pair')
    small = subspaces(3)
    flags = checks = 0
    for a0 in small:
        for a in small:
            if not a0 <= a:
                continue
            for b in small:
                if not a < b:
                    continue
                for b0 in small:
                    if not b <= b0:
                        continue
                    flags += 1
                    for f in small:
                        projected = span(tuple(a) + tuple(f & b))
                        need(a <= projected <= b, 'Projected chart lies in the query interval')
                        for h in range(1, 4):
                            cost = lambda x, y: min(distance(x, y), h)
                            old = cost(a0, f) + cost(f, b0) - cost(a, f) - cost(f, b)
                            new = cost(a0, projected) + cost(projected, b0) - cost(a, projected) - cost(projected, b)
                            need(old <= new, 'Every discrete concave hinge respects projection')
                            checks += 1
    # All two-qubit Lagrangians test the metric premise beyond canonical charts.
    lagrangians = []
    def symp(x, y):
        return (((x & 3) & (y >> 2)).bit_count() + ((y & 3) & (x >> 2)).bit_count()) % 2
    for s in subspaces(4):
        if dim(s) == 2 and all(symp(x, y) == 0 for x in s for y in s):
            lagrangians.append(s)
    need(len(lagrangians) == 15, 'All two-qubit Lagrangians')
    triangle_checks = 0
    for a, b, f in product(lagrangians, repeat=3):
        af, bf, ab = (2 - dim(x & y) for x, y in ((a, f), (b, f), (a, b)))
        need(af <= ab + bf, 'Lagrangian distance triangle inequality')
        for h in (1, 2):
            need(min(af, h) - min(bf, h) <= min(ab, h), 'Concave endpoint path bound')
            triangle_checks += 1
    # Literal full sums check the cancellation for every path of up to three cuts.
    a0, a, b, b0 = (span(v) for v in ([], [1], [1, 2], [1, 2, 4]))
    paths = 0
    for length in (1, 2, 3):
        for path in product(small, repeat=length):
            for h in (1, 2, 3):
                phi = lambda r: min(r, h)
                targets = [a0] + list(path) + [b0]
                paid = [a] + list(path) + [b]
                gain = sum(phi(distance(x, y)) for x, y in zip(targets, targets[1:]))
                gain -= sum(phi(distance(x, y)) for x, y in zip(paid, paid[1:]))
                gain += phi(distance(a, b)) - phi(distance(a0, b0))
                bound = phi(distance(a0, a)) + phi(distance(b, b0)) + phi(distance(a, b)) - phi(distance(a0, b0))
                need(gain <= bound, 'Literal arbitrary-path upper bound')
            paths += 1
    return dict(native_pairs=len(spaces)**2, binary_flags=flags, flag_hinge_checks=checks,
                lagrangians=15, metric_hinge_checks=triangle_checks, literal_paths=paths)


def dimension_patterns():
    patterns = checks = 0
    for row in compositions(9, 10):
        y, z = row[::2], row[1::2]
        blocks = [x + w for x, w in zip(y, z)]
        if blocks[2] == 0:
            continue
        a0, u, q, v, outside = blocks
        a, b, b0 = a0 + u, a0 + u + q, a0 + u + q + v
        x0, x1, x2, x3 = (sum(y[:i]) for i in range(1, 5))
        f = sum(y)
        s, e1, e3, k = z[0] + y[4], z[1], y[3], y[2]
        delta = e1 + e3
        target = [a0 + f - 2*x0, b0 + f - 2*x3]
        paid = [a + f - 2*x1, b + f - 2*x2]
        need(target == [u + k + s + e3 - e1, q - k + v + s + e1 - e3]
             and paid == [k + s + delta, q - k + s + delta], 'Exact flag defect decomposition')
        for h in range(1, 10):
            phi = lambda r: min(r, h)
            raw = sum(map(phi, target)) - sum(map(phi, paid))
            projected = phi(u+k) + phi(q-k+v) - phi(k) - phi(q-k)
            need(raw <= projected, 'All rank-nine patterns and concave hinges')
            checks += 1
        patterns += 1
    need(patterns == 37180, 'All feasible nine-dimensional flag intersection patterns')
    return dict(patterns=patterns, hinge_checks=checks)


def power_endpoints(E):
    count = 0
    for c in (Q('.00311313795'), Q('.0034'), Q('.01'), Q(1, 2), Q(9, 10)):
        powers = {r: E.power(r, 1-c) for r in range(1, 10)}
        for total in range(1, 10):
            for u in range(total):
                for q in range(1, total-u+1):
                    v = total-u-q
                    endpoint = 0 if u >= v else q
                    best = signed([endpoint, q-endpoint], [u+endpoint, q-endpoint+v])
                    for k in range(q+1):
                        actual = signed([k, q-k], [u+k, q-k+v])
                        gap = Counter(best)
                        gap.subtract(actual)
                        gap = {r: n for r, n in gap.items() if n}
                        need(not gap or evaluate(gap, powers)[0] > 0, 'Exact power endpoint optimum')
                        count += 1
    # This is a necessary restriction: an arbitrary concave tariff need not have an endpoint maximum.
    phi = lambda r: min(r, 2)
    endpoint = phi(1)+phi(3)-phi(0)-phi(2)
    interior = 2*phi(2)-2*phi(1)
    need(interior == 2 and endpoint == 1, 'Reject extension of endpoint theorem to every concave tariff')
    return dict(power_comparisons=count, hinge_endpoint_counterexample=dict(u=1, q=2, v=1, endpoint=endpoint, interior=interior))


def all_clifford_one_cut(E):
    n = 3
    def symp(x, y):
        return (((x & 7) & (y >> 3)).bit_count() + ((y & 7) & (x >> 3)).bit_count()) % 2
    lagrangians = [s for s in subspaces(6) if dim(s) == 3
                  and all(symp(x, y) == 0 for x in basis(s) for y in basis(s))]
    need(len(lagrangians) == 135, 'All three-qubit Lagrangian images')
    def image(w):
        return frozenset(x | (z << n) for x in w for z in range(1 << n)
                         if all(((x ^ z) & v).bit_count() % 2 == 0 for v in w))
    a0, a, b, b0 = [image(span(v)) for v in ([], [1], [1, 2], [1, 2, 4])]
    metric = lambda x, y: n-dim(x & y)
    need([metric(x, y) for x, y in ((a0, a), (a, b), (b, b0), (a0, b0))] == [1, 1, 1, 3],
         'Exact geodesic source boundary in the full Clifford domain')
    checks = 0
    for c in (Q('.00311313795'), Q(1, 2), Q(9, 10)):
        powers = {r: E.power(r, 1-c) for r in range(1, 4)}
        upper = signed([], [1, 2])
        for f in lagrangians:
            delta = Counter(upper)
            delta.subtract(signed([metric(a, f), metric(f, b)], [metric(a0, f), metric(f, b0)]))
            delta[1] -= 1
            delta = {r: m for r, m in delta.items() if m}
            need(not delta or evaluate(delta, powers)[0] > 0, 'Power endpoint optimum for every Clifford image')
            checks += 1
    return dict(lagrangians=135, exact_power_checks=checks)


def source_inventory(word, receipt):
    frames = [span(v) for v in word['frames']]
    need(all(dim(s) == len(v) for s, v in zip(frames, word['frames'])), 'Independent source frame bases')
    public = word['public']
    main = set(word['live']) | {112+r for r in word['live']}
    helper_ids = set(range(public)) - main
    need(len(main) == 208 and public == 767 and len(helper_ids) == 559,
         'Exact source main and public interface')
    need('main = live | {r+112 for r in live}' in (HERE/'source/source-local.py').read_text(),
         'Literal source main-field contract')
    current = word['initial'][:] + [None]*word['owned_fields']
    paid, helpers, queries = Counter(), Counter(), []
    for h in sorted(helper_ids):
        a0, b0 = frames[word['initial'][h]], frames[word['final'][h]]
        need(a0 < b0, 'Positive nested source helper boundary')
        helpers[distance(a0, b0)] += 1
    for pc, event in enumerate(word['program']):
        op = event[0]
        if op == 'MOVE':
            _, h, a, b, private = event
            need(current[h] == a and private == (h >= public), 'Actual source MOVE frame and ownership')
            current[h] = b
            r = distance(frames[a], frames[b])
            need(r > 0, 'Positive paid source rank')
            paid[r] += 1
            if h in helper_ids:
                a0, b0 = word['initial'][h], word['final'][h]
                need(frames[a0] <= frames[a] < frames[b] <= frames[b0], 'Actual helper-query flag')
                u, q, v = dim(frames[a])-dim(frames[a0]), r, dim(frames[b0])-dim(frames[b])
                queries.append(dict(pc=pc, helper=h, frames=[a0, a, b, b0], ranks=[u, q, v]))
        elif op == 'INIT':
            _, h, frame = event
            need(h >= public and current[h] is None, 'Fresh owned frame lifetime')
            current[h] = frame
        elif op == 'CLEAR':
            _, h, frame = event
            need(h >= public and current[h] == frame, 'Owned frame cleanup')
            current[h] = None
        elif op in ('ADD', 'COPY'):
            _, dst, src, value, frame = event
            need(current[dst] == current[src] == frame, 'Actual scalar operand frames')
        else:
            need(op == 'SCALE' and current[event[1]] == event[3], 'Actual scalar scale frame')
    need(current == word['final'] + [None]*word['owned_fields'], 'All source frame endpoints')
    need(dict(paid) == {int(k): v for k, v in receipt['local']['paid'].items()}, 'All source paid ranks')
    need(dict(helpers) == {int(k): v for k, v in receipt['local']['helpers'].items()}, 'All source target ranks')
    wrong = Counter(distance(frames[word['initial'][h]], frames[word['final'][h]])
                    for h in range(208, public))
    need(wrong != helpers, 'Reject a contiguous-main partition despite equal field counts')
    need(len(queries) == 2534 and len({r['helper'] for r in queries}) == 559, 'Complete helper-query inventory')
    return queries, paid, helpers


def source_controls(word, receipt):
    controls = []
    bad = deepcopy(word)
    bad['live'] = list(range(104))
    controls.append(('contiguous-main-role-assumption', bad, receipt))
    bad = deepcopy(word)
    first = next(i for i, e in enumerate(bad['program']) if e[0] == 'MOVE')
    bad['program'][first][2] = (bad['program'][first][2] + 1) % len(bad['frames'])
    controls.append(('wrong-query-source-frame', bad, receipt))
    bad = deepcopy(receipt)
    bad['local']['helpers']['9'] -= 1
    controls.append(('missing-original-helper-target', word, bad))
    rejected = []
    for name, candidate, expected in controls:
        try:
            source_inventory(candidate, expected)
        except ValueError as error:
            rejected.append(dict(control=name, rejection=str(error)))
        else:
            raise ValueError('Accepted invalid source control: ' + name)
    return rejected


def bounds(queries, E, receipt):
    groups = defaultdict(list)
    for row in queries:
        groups[row['helper']].append(row)
    outputs = {}
    for c in (Q('.00311313795'), Q('.0034'), Q('.01')):
        powers = {r: E.power(r, 1-c) for r in range(1, 10)}
        selected = {}
        for mode in ('one_cut', 'arbitrary_path'):
            choices = []
            for helper, rows in sorted(groups.items()):
                candidates = {}
                for row in rows:
                    u, q, v = row['ranks']
                    if mode == 'one_cut':
                        parts = [u, q+v] if u >= v else [u+q, v]
                    else:
                        parts = [u, q, v]
                    parts = tuple(sorted(r for r in parts if r))
                    candidates.setdefault(parts, row['pc'])
                values = [(evaluate(signed([sum(parts)], parts), powers), parts, pc)
                          for parts, pc in candidates.items()]
                values.sort(key=lambda x: (x[0][0], x[1]), reverse=True)
                win, parts, pc = values[0]
                for loss, other, other_pc in values[1:]:
                    need(win[0] > loss[1], 'Exact source profile ordering')
                choices.append(dict(helper=helper, pc=pc, target_parts=parts, gain=win))
            total = (Q(0), Q(0))
            for x in choices:
                total = add(total, x['gain'])
            ordered = sorted(choices, key=lambda x: x['gain'][0], reverse=True)
            for left, right in zip(ordered, ordered[1:]):
                lc = signed([sum(left['target_parts'])], left['target_parts'])
                rc = signed([sum(right['target_parts'])], right['target_parts'])
                need(lc == rc or left['gain'][0] >= right['gain'][1],
                     'Exact ordering for the minimum helper count')
            prefix = (Q(0), Q(0))
            required = None
            for i, x in enumerate(ordered, 1):
                previous = prefix
                prefix = add(prefix, x['gain'])
                if prefix[0] >= 1:
                    need(previous[1] < 1, 'Exact minimum number of relaxed helpers for one H1 fee')
                    required = i
                    break
            need(required is not None, 'Source envelope can fund a unit fee with enough helpers')
            selected[mode] = dict(total_gain=E.display(total), minimum_helpers_for_one_H1=required,
                maximum_gain=E.display(ordered[0]['gain']), zero_gain_helpers=sum(x['gain'] == (0, 0) for x in choices),
                choices=[dict(helper=x['helper'], pc=x['pc'], target_parts=x['target_parts'], gain=E.display(x['gain'])) for x in choices])
        outputs[str(c)] = selected
    # Exact universal cap at the largest declared exponent. Jensen bounds three parts by 3,3,3.
    c = Q('.01')
    p = {r: E.power(r, 1-c) for r in range(1, 10)}
    cap = evaluate({3: 3, 9: -1}, p)
    need(0 < cap[0] <= cap[1] < Q(1, 10), 'Every one-target detour gain is below one tenth of H1 through C=.01')
    return outputs, dict(three_part_cap_at_one_percent=E.display(cap), ordinary_work_charged=False)


def run():
    C, E = source_modules()
    geometry = finite_geometry(C)
    patterns = dimension_patterns()
    endpoints = power_endpoints(E)
    clifford = all_clifford_one_cut(E)
    word, receipt = read(HERE/'source/WORD.json.gz'), read(HERE/'source/RESULT.json')
    queries, paid, helpers = source_inventory(word, receipt)
    controls = source_controls(word, receipt)
    budgets, cap = bounds(queries, E, receipt)
    result = dict(status='PASS_HELPER_DETOUR_PROJECTION_AND_SHARP_PATH_BUDGETS', geometry=geometry,
        dimension_patterns=patterns, endpoint_checks=endpoints, full_clifford_check=clifford, source_head='a1b338e5d9271b541f2a198f4fc19cefc565feed',
        source_queries=len(queries), source_helpers=sum(helpers.values()),
        source_paid=dict(sorted(paid.items())), source_targets=dict(sorted(helpers.items())),
        full_query_zero_gain=sum(row['ranks'][0] == row['ranks'][2] == 0 for row in queries),
        budgets=budgets, universal_cap=cap, source_controls=controls,
        limits=['Optimistic recursive tariff bounds, not physical independent-target cuts.',
                'Choose at most one original query per helper; alternative cuts are not additive.',
                'Shared-query graphs, changed endpoints and extra ordinary/native fees require a new contract.',
                'Source frame and rank checks do not repeat its scalar endpoint, native-phase or compiler admission.'])
    return result, dict(schema='p104-helper-query-flags/1', source_head=result['source_head'], queries=queries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='detour-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, queries = run()
    for name, value in (('RESULT.json', result), ('QUERY-BOUNDS.json', queries)):
        # JSON normalizes integer dictionary keys and tuples in the reproducible receipt.
        normalized = json.loads(json.dumps(value))
        if args.write:
            (HERE/name).write_text(json.dumps(normalized, sort_keys=True, indent=2)+'\n')
        else:
            need(read(HERE/name) == normalized, 'Exact retained receipt: '+name)
    print(result['status'])
    print('Geometry:', result['geometry'])
    for c, rows in result['budgets'].items():
        print(c, {m: dict(gain=v['total_gain'], fee_helpers=v['minimum_helpers_for_one_H1']) for m, v in rows.items()})


if __name__ == '__main__':
    main()
