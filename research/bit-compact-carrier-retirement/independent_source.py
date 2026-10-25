#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Standalone independent mixed-width SOURCE/owner audit; Python stdlib only.

Usage: python portable_source.py --provider PACKAGE --output RESULT.json
The provider supplies SOURCE-AUDIT-PINS.json or MANIFEST.json with a relative
files -> SHA256 map. No producer module, network, Git, or external cache is read.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
import gzip
from math import gcd, lcm
from pathlib import Path, PurePosixPath
import sys
from time import process_time


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def tr(a):
    return list(map(list, zip(*a)))


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def independent(rows):
    reduced, pivots, original = [], [], []
    for row in rows:
        z = list(map(Q, row))
        for u, j in zip(reduced, pivots):
            c = z[j]
            z = [x-c*y for x, y in zip(z, u)]
        j = next((k for k, x in enumerate(z) if x), None)
        if j is not None:
            c = z[j]
            reduced.append([x/c for x in z])
            pivots.append(j)
            original.append(list(map(Q, row)))
    return original


def determinant(a):
    a = [list(map(Q, row)) for row in a]
    d = Q(1)
    for j in range(len(a)):
        k = next((i for i in range(j, len(a)) if a[i][j]), None)
        need(k is not None, 'singular Gram basis')
        if j != k:
            a[j], a[k] = a[k], a[j]
            d = -d
        c = a[j][j]
        d *= c
        for i in range(j+1, len(a)):
            c = a[i][j]/a[j][j]
            a[i] = [x-c*y for x, y in zip(a[i], a[j])]
    return d


def inverse(a):
    n = len(a)
    z = [list(map(Q, row))+e for row, e in zip(a, eye(n))]
    for j in range(n):
        k = next((i for i in range(j, n) if z[i][j]), None)
        need(k is not None, 'singular source matrix')
        z[j], z[k] = z[k], z[j]
        c = z[j][j]
        z[j] = [x/c for x in z[j]]
        for i in range(n):
            if i != j:
                c = z[i][j]
                z[i] = [x-c*y for x, y in zip(z[i], z[j])]
    return [row[n:] for row in z]


def replay(program, n):
    a = eye(n)
    for record in program:
        op = record[0]
        if op == 'swap':
            need(len(record) == 3, 'swap schema')
            _, i, j = record
            need(0 <= i < n and 0 <= j < n, 'swap index')
            a[i], a[j] = a[j], a[i]
        elif op == 'scale':
            need(len(record) == 3, 'scale schema')
            _, i, c = record
            c = Q(c)
            need(0 <= i < n and c in (Q(-1), Q(2), Q(1, 2)), 'odd-unit scale alphabet')
            a[i] = [c*x for x in a[i]]
        else:
            need(op == 'add' and len(record) == 4, 'coordinate opcode')
            _, i, j, c = record
            c = Q(c)
            need(0 <= i < n and 0 <= j < n and i != j and c in (Q(-1), Q(1)), 'unit ADD schema')
            a[i] = [x+c*y for x, y in zip(a[i], a[j])]
    return a


def dyadic_scaled(a):
    d = lcm(*(Q(t).denominator for row in a for t in row))
    need(d > 0 and d & (d-1) == 0, 'non-dyadic source coefficient')
    return [[int(Q(t)*d) for t in row] for row in a], d


def sparse_orthogonal(a):
    gram = defaultdict(Q)
    for row in a:
        z = [(j, Q(x)) for j, x in enumerate(row) if x]
        for j, x in z:
            for k, y in z:
                gram[j, k] += x*y
    n = len(a)
    need(all(v == Q(i == j) for (i, j), v in gram.items()), 'chart orthogonality off-diagonal')
    need(all(gram[i, i] == 1 for i in range(n)), 'chart orthogonality diagonal')


def authenticate(provider, relative, expected):
    p = PurePosixPath(relative)
    need(not p.is_absolute() and '..' not in p.parts and p.as_posix() == relative,
         'noncanonical provider pin path')
    path = provider.joinpath(*p.parts)
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(provider),
         'pin leaves provider: '+relative)
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, 'source byte pin: '+relative)
    return raw


def loads(raw, name):
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def rejection(fn, label):
    try:
        fn()
    except ValueError as error:
        return {'name': label, 'rejected': True, 'reason': str(error)}
    raise ValueError('defect accepted: '+label)


def relative_check(c, bases, projectors):
    f = int(c['terminal_frame'])
    need(f in bases, 'unknown terminal SOURCE frame')
    k = 8 if f == 1 else 4
    axes = c['axes']
    need(len(axes) == k and len(set(axes)) == k and all(0 <= t < 64 for t in axes),
         'terminal axes/rank')
    expected_perm = axes+[i for i in range(64) if i not in axes]
    need(c['permutation'] == expected_perm, 'terminal permutation axes/order')
    perm = replay(c['permutation_program'], 64)
    need(all(sum(t != 0 for t in row) == 1 and sum(row) == 1 for row in perm),
         'nonpermutation chart program')
    block = eye(64)
    for i in range(8):
        block[i][:8] = tr(bases[f])[i]
    wanted = [block[next(j for j, t in enumerate(row) if t)] for row in perm]
    actual = [[Q(x) for x in row] for row in c['relative_matrix']]
    need(len(actual) == 64 and all(len(row) == 64 for row in actual), 'relative64 shape')
    need(actual == wanted, 'actual SOURCE terminal/coframe matrix')
    sparse_orthogonal(actual)
    # Independently check image of every terminal image column.  Since
    # E=B[:,0:k] B[:,0:k]^T, this proves the full64-dimensional conjugation.
    for j in range(k):
        image = [sum(row[t]*bases[f][t][j] for t in range(8)) for row in actual]
        need(image == [Q(i == axes[j]) for i in range(64)], 'wrong actual SOURCE projector axis')
    need(projectors[f] == mm([row[:k] for row in bases[f]], tr([row[:k] for row in bases[f]])),
         'terminal SOURCE root-span binding')
    return actual, dyadic_scaled(actual)


def canonical_controller():
    recipe = [{'kind': 'local', 'stage': 0, 'pair': 0, 'reverse': False}]
    for p in range(4):
        recipe.append({'kind': 'local', 'stage': 2*p+1, 'pair': p, 'reverse': True})
        if p < 3:
            recipe.append({'kind': 'bridge', 'dst': p, 'src': p+1, 'coefficient': 1})
        recipe.append({'kind': 'local', 'stage': 2*p+2, 'pair': p, 'reverse': False})
        if p < 3:
            recipe.append({'kind': 'bridge', 'dst': p, 'src': p+1, 'coefficient': -1})
    recipe += [{'kind': 'bridge', 'dst': p+1, 'src': p, 'coefficient': 1} for p in (2, 1, 0)]
    recipe.append({'kind': 'exchange'})
    levels = [-1]*4
    events, children = [], []
    def advance(pair, hi):
        lo = levels[pair]
        axes = list(range(1 if lo == -1 else 8+7*lo, 8+7*hi))
        c = {'kind': 'idle', 'idx': len(children), 'pair': pair, 'source_level': lo,
             'target_level': hi, 'axes': axes, 'rank': len(axes)}
        events.append(c)
        children.append(c)
        levels[pair] = hi
    for event in recipe:
        events.append(event)
        if event['kind'] == 'local':
            s, p = event['stage'], event['pair']
            need(levels[p] == s-1, 'canonical local source level')
            levels[p] = s
            if 1 <= s <= 6:
                advance((s+1)//2, s)
            if s == 8:
                for p in range(4):
                    advance(p, 8)
        elif event['kind'] == 'bridge':
            need(levels[event['src']] == levels[event['dst']], 'canonical bridge source levels')
        else:
            need(levels == [8]*4, 'canonical final source level')
    return events, children


def audit(objects, route_invoice):
    word, geom, term, data_geom, charts, order, slots, remainders, dispatch, receipt = objects
    need((geom['h'], geom['v'], geom['R']) == (8, 111, 438) and
         len(geom['lines']) == 111 and all(len(row) == 8 for row in geom['lines']),
         'actual SOURCE geometry dimensions')
    need(len(word['start']) == len(word['final']) == 658 and word['namespace'] == 658 and
         word['active_ordinary_roles'] == 658 and word['physical_helpers'] == 436,
         'all658 actual ordinary RAW roles; private658 is separate')
    need(word['start'][222:] == [0]*436, 'helper initial frames are zero gauges, not zero payload')
    partial = {222+i: f for i, f in enumerate(word['final'][222:]) if f != 1}
    need(partial == {462: 506, 463: 506, 466: 508, 468: 509}, 'actual compact partial terminal list')
    bases = {int(f): [[Q(x) for x in row] for row in b] for f, b in charts['terminal_bases'].items()}
    need(set(bases) == {1, 506, 508, 509} and bases[1] == eye(8), 'terminal SOURCE basis registry')
    need(all(len(b) == 8 and all(len(row) == 8 for row in b) for b in bases.values()),
         'terminal8 SOURCE matrix shapes')
    need({int(f) for f in charts['terminal_programs']} == set(bases), 'terminal SOURCE program inventory')
    projectors, partials = {1: eye(8)}, []
    for f in (506, 508, 509):
        basis = independent([geom['lines'][j] for j in geom['frames'][f]])
        need(len(basis) == 4, 'actual partial root rank')
        gram = mm(basis, tr(basis))
        det = determinant(gram)
        need(det.denominator == 1 and det > 0 and int(det) & (int(det)-1) == 0,
             'original root Gram has odd-prime exception')
        e = mm(mm(tr(basis), inverse(gram)), basis)
        projectors[f] = e
        sparse_orthogonal(bases[f])
        old = next(c for c in term['charts'] if c['terminal_frame'] == f)
        need([[Q(x) for x in row] for row in old['projector']] == e, 'SOURCE partial projector bytes')
        need(tr([[Q(x) for x in col] for col in old['Q_columns']]) == bases[f], 'SOURCE terminal basis bytes')
        partials.append({'frame': f, 'rank': 4, 'original_root_Gram_determinant': str(det),
                         'projector': [[str(x) for x in row] for row in e]})
    for f, program in charts['terminal_programs'].items():
        need(replay(program['program'], 8) == bases[int(f)], 'terminal primitive forward')
        need(replay(program['inverse'], 8) == tr(bases[int(f)]), 'terminal primitive inverse')
        need(len(program['program']) == len(program['inverse']) == program['primitive_count'], 'terminal paid count')
    need(len(charts['family_charts']) == len(charts['family_programs']) == len(geom['lines']) == 111,
         'family SOURCE inventory')
    for port, (matrix, program) in enumerate(zip(charts['family_charts'], charts['family_programs'])):
        a = [[Q(x) for x in row] for row in matrix]
        need(len(a) == 8 and all(len(row) == 8 for row in a), 'family8 SOURCE chart shape')
        sparse_orthogonal(a)
        need([row[0] for row in a] == [Q(x, 2) for x in geom['lines'][port]], 'family SOURCE first axis')
        need(replay(program['program'], 8) == a and replay(program['inverse'], 8) == tr(a), 'family primitive all-input replay')
        need(len(program['program']) == program['primitive_count'], 'family primitive paid count')
    need(len(data_geom['ports']) == 111, 'retained DATA SOURCE inventory')
    rho_checks = 0
    for port, item in enumerate(data_geom['ports']):
        need(item['port'] == port and item['q'] == geom['lines'][port], 'retained rho SOURCE port order')
        rho, d = dyadic_scaled(item['rho15'])
        need(len(rho) == 15 and all(len(row) == 15 for row in rho), 'rho15 shape')
        for i in range(15):
            for j in range(15):
                dot = sum(a*b for a, b in zip(rho[i], rho[j]))
                need(dot == d*d*int(i == j), 'rho15 orthogonality')
                q = item['q']+[0]*7
                rv_i, rv_j = sum(a*b for a, b in zip(rho[i], q)), sum(a*b for a, b in zip(rho[j], q))
                line = q[i]*q[j]
                head = 4*int(i == j and i < 8)
                ext = 4*int(i == j and i >= 8)
                hc = 4*sum(rho[i][k]*rho[j][k] for k in range(8))
                xc = 4*sum(rho[i][k]*rho[j][k] for k in range(8, 15))
                need(rv_i*rv_j == d*d*line, 'rho SOURCE line identity')
                need(hc == d*d*(line+ext), 'rho full DATA head identity')
                need(hc-rv_i*rv_j == d*d*ext, 'rho SOURCE complement identity')
                need(xc == d*d*(head-line), 'rho SOURCE exterior identity')
        rho_checks += 4
    relatives = charts['relative_charts']
    need(len(relatives) == 24 and [c['id'] for c in relatives] == list(range(24)), 'new24 relative SOURCE charts')
    relative_matrices, scaled_matrices = [], []
    for c in relatives:
        a, scaled = relative_check(c, bases, projectors)
        relative_matrices.append(a)
        scaled_matrices.append(scaled)
    max_route = max(len(charts['terminal_programs'][str(c['terminal_frame'])]['inverse'])+
                    len(c['permutation_program'])+len(p['program'])
                    for c in relatives for p in charts['family_programs'])
    need(max_route == 159, 'new actual64 routing count')
    need(route_invoice['max64chart_coordinate_primitives'] == max_route and
         route_invoice['selector_G'] == 240+144+4*max_route+2+63+64 == 1149, 'new routing fee not old1117')
    events, children = canonical_controller()
    need(order['controller'] == events, 'actual canonical controller source order')
    calls = {e['stage']: (i, e) for i, e in enumerate(events) if e['kind'] == 'local'}
    windows = {}
    for c in children:
        end = events.index(c)
        touches = [i for i, e in enumerate(events[:end]) if
                   (e['kind'] == 'local' and e['pair'] == c['pair']) or
                   (e['kind'] == 'bridge' and c['pair'] in (e['src'], e['dst']))]
        lo = max(touches, default=-1)
        ss = [s for s, (i, e) in calls.items() if lo < i < end and e['pair'] != c['pair']]
        windows[c['idx']] = ss
        need(order['windows'][str(c['idx'])] == {'lower_open_event': lo, 'upper_open_event': end, 'stages': ss},
             'actual strict SOURCE window')
    expected_calls = [{'stage': s, 'replica': r, 'event': calls[s][0]} for s in range(9) for r in range(32)]
    need(order['calls'] == expected_calls, 'whole sweep/replica chronology')
    widths = [8 if f == 1 else 4 for f in word['final'][222:]]
    need(receipt['ordered_widths'] == widths, 'actual ordered helper SOURCE widths')
    need((receipt['ordinaryRAW'], receipt['helpers'], receipt['W'], receipt['private']) == (658, 436, 28416, 9),
         'unchanged original stock/private reserve')
    keys = {(tuple(c['axes']), c['terminal_frame']): c['id'] for c in relatives}
    need(len(keys) == 24, 'duplicate SOURCE chart keys')
    used, routes, same = defaultdict(set), {}, defaultdict(list)
    for child, cp, offset, width, stage, helper in slots:
        need(child in range(10) and stage in windows[child], 'slot SOURCE window')
        need(0 <= cp < 222 and 0 <= helper < 436 and offset >= 0 and width == widths[helper], 'slot typed extent')
        need(children[child]['pair'] != calls[stage][1]['pair'], 'host is active DATA pair')
        axes = children[child]['axes'][offset:offset+width]
        need(len(axes) == width and not used[child, cp].intersection(axes), 'slot overlap')
        used[child, cp].update(axes)
        need((stage, helper) not in routes, 'duplicate helper occurrence')
        f = word['final'][222+helper]
        need((tuple(axes), f) in keys, 'slot actual SOURCE chart missing')
        cid = keys[tuple(axes), f]
        routes[stage, helper] = child, cp, offset, width, cid
        same[stage, 2*children[child]['pair']*111+cp].append(cid)
    need(set(routes) == {(s, h) for s in range(9) for h in range(436)}, 'all helper SOURCE occurrences')
    expected_rem = []
    for c in children:
        for cp in range(222):
            rest = [a for a in c['axes'] if a not in used[c['idx'], cp]]
            need(rest == c['axes'][len(used[c['idx'], cp]):], 'noncompact pending SOURCE suffix')
            expected_rem.append([c['idx'], cp, rest])
    need(remainders == expected_rem, 'unpaid/wrong pending SOURCE remainder')
    pair_cache, hist = {}, Counter()
    for ids in same.values():
        for ca, cb in combinations(ids, 2):
            key = tuple(sorted((ca, cb)))
            if key not in pair_cache:
                ai, ad = scaled_matrices[ca]
                bi, bd = scaled_matrices[cb]
                d = lcm(ad, bd)
                gg = 0
                for ar, br in zip(ai, bi):
                    for a, b in zip(ar, br):
                        delta = a*(d//ad)-b*(d//bd)
                        if delta:
                            gg = gcd(gg, abs(delta)//gcd(abs(delta), d))
                need(gg > 0 and gg & (gg-1) == 0, 'odd-prime SOURCE owner collision')
                pair_cache[key] = gg
            hist[pair_cache[key]] += 1
    need(hist == {1: 5579}, 'all5579 exact owner differences')
    need(len(dispatch) == 288, 'all local dispatch SOURCE descriptors')
    global_used, seen = defaultdict(set), set()
    critical = []
    for descriptor in dispatch:
        stage, rep = descriptor['stage'], descriptor['replica']
        need(0 <= stage < 9 and 0 <= rep < 32 and (stage, rep) not in seen, 'dispatch domain/duplicate')
        seen.add((stage, rep))
        active, rev = calls[stage][1]['pair'], calls[stage][1]['reverse']
        need(descriptor['pair'] == active and descriptor['orientation'] == ('reverse' if rev else 'forward'), 'dispatch orientation SOURCE law')
        need(len(descriptor['owners']) == 658, 'all658 owner descriptors')
        for role in range(222):
            side, port = divmod(role, 111)
            if rev:
                side = 1-side
            need(descriptor['owners'][role] == [rep*888+(2*active+side)*111+port, ['data', stage, port]],
                 'actual DATA SOURCE owner')
        for h in range(436):
            child, cp, offset, width, cid = routes[stage, h]
            family = rep*888+2*children[child]['pair']*111+cp
            need(descriptor['owners'][222+h] == [family, ['hosted', child, offset, width, cid]], 'actual hosted SOURCE owner')
            axes = relatives[cid]['axes']
            need(not global_used[family].intersection(axes), 'cross-stage physical SOURCE overlap')
            global_used[family].update(axes)
            if stage == 4 and rep == 0 and h in (240, 241, 244, 246):
                critical.append({'absolute_helper': 222+h, 'family': family, 'child': child,
                                 'offset': offset, 'width': width, 'axes': axes,
                                 'terminal': word['final'][222+h], 'chart': cid})
        need(descriptor['private_owner'] == [28416+stage, ['private', 'd']], 'private/live SOURCE alias or wrong owner')
    need([c['offset'] for c in critical] == [16, 20, 24, 28] and
         all(c['family'] == 200 and c['child'] == 6 and c['width'] == 4 for c in critical), 'critical stage4 SOURCE cohost')
    need(next(r[2] for r in expected_rem if r[:2] == [6, 200]) == list(range(54, 64)), 'critical pending remainder')
    mutants = []
    c = next(c for c in relatives if c['terminal_frame'] == 506)
    wrong = dict(c)
    wrong['terminal_frame'] = 508
    mutants.append(rejection(lambda: relative_check(wrong, bases, projectors), 'equal-rank-wrong-terminal'))
    wrong_axes = dict(c)
    wrong_axes['axes'] = c['axes'][:-1]+[63]
    mutants.append(rejection(lambda: relative_check(wrong_axes, bases, projectors), 'equal-rank-wrong-axis'))
    return {'partial_SOURCE_projectors': partials, 'relative_SOURCE_charts': 24,
            'family_SOURCE_charts': 111, 'rho15_SOURCE_identities': rho_checks,
            'all_coordinate_programs_replayed': True, 'max64_route': max_route, 'selector_G': 1149,
            'slots': len(slots), 'dispatches': len(dispatch), 'ordinary_owners_checked': 288*658,
            'helper_owner_occurrences': 288*436, 'samefamily_pairs_per_replica': sum(hist.values()),
            'owner_difference_numerator_gcds': dict(hist), 'all_odd_local_ring_owner_separation': True,
            'critical_stage4_family200': critical, 'defect_controls': mutants}


def native_source_audit(word, geom, native):
    """Independent exact signed rows, physical FRAME state and COPY versions."""
    frames = []
    gram_hist = Counter()
    for indices in geom['frames']:
        basis = independent([geom['lines'][i] for i in indices])
        gram = mm(basis, tr(basis))
        det = determinant(gram) if basis else Q(1)
        need(det.denominator == 1 and det > 0 and int(det) & (int(det)-1) == 0,
             'actual original-root frame has non-odd-unit Gram')
        gram_hist[str(det)] += 1
        project = mm(mm(tr(basis), inverse(gram)), basis) if basis else [[Q(0)]*8 for _ in range(8)]
        need(sum(project[i][i] for i in range(8)) == len(basis), 'SOURCE projector rank')
        frames.append((basis, project))
    need(len(frames) == 636, 'all636 SOURCE frames')
    nested_cache = {}
    def nested(old, new, rank):
        key = old, new, rank
        if key not in nested_cache:
            a, b = frames[old], frames[new]
            need(0 < rank < 8 and len(b[0])-len(a[0]) == rank, 'proper paid recursive rank')
            for v in a[0]:
                need([sum(v[j]*b[1][i][j] for j in range(8)) for i in range(8)] == v,
                     'actual nested SOURCE projector')
            nested_cache[key] = True
    def replay_rows(reverse=False, initial=None):
        rows = [{i: 1} for i in range(658)]+[{}] if initial is None else [dict(r) for r in initial]
        need(len(rows) == 659 and rows[658] == {}, 'private initialized and allocated, no DATA credit')
        state = list(word['final'] if reverse else word['start'])+[None]
        versions = [0]*658
        norm = [1]*658+[0]
        opened = None
        captures = []
        hist = Counter()
        peak = 1
        records = reversed(word['records']) if reverse else word['records']
        for position, raw in enumerate(records):
            need(len(raw) == 6, 'literal record schema')
            op, d, s, c, f, section = raw
            need(0 <= d < 658, 'no phantom ordinary destination')
            if op == 0:
                before, after = (c, s) if reverse else (s, c)
                need(opened is None and state[d] == before, 'immutable COPY/no recursive MOVE during lease')
                nested(s, c, f)
                state[d] = after; versions[d] += 1; hist[f] += 1
            elif op == 1:
                need(0 <= s <= 658 and d != s and c in (-1, 1), 'literal signed VALUE schema')
                need(state[d] == state[s] == f, 'actual same-FRAME ADD')
                need(opened is None or d != opened['source'], 'COPY source immutable')
                need(s != 658 or opened is not None, 'private used outside actual lease')
                coefficient = -c if reverse else c
                for j, value in list(rows[s].items()):
                    value = rows[d].get(j, 0)+coefficient*value
                    if value: rows[d][j] = value
                    else: rows[d].pop(j, None)
                versions[d] += 1
                norm[d] += norm[s]; peak = max(peak, norm[d])
            else:
                need(op in (2, 3) and s == 658, 'proper private opcode/index')
                copy = op == (3 if reverse else 2)
                if copy:
                    need(opened is None and not rows[658] and state[658] is None, 'COPY owned complete zero')
                    need(state[d] == c and f == 0 and len(frames[c][0]) == 7, 'COPY actual rank7 SOURCE/current coframe')
                    rows[658] = dict(rows[d]); state[658] = 0; norm[658] = norm[d]; hist[7] += 1
                    # The actual SOURCE coefficient row must be supported inside
                    # the actual7D SOURCE frame, not merely have the same rank.
                    support = [j for j, value in rows[d].items() if j < 111 and value % 2]
                    for j in support:
                        v = list(map(Q, geom['lines'][j])); E = frames[c][1]
                        need([sum(E[i][k]*v[k] for k in range(8)) for i in range(8)] == v,
                             'SOURCE capture coefficient/frame support')
                    opened = {'source': d, 'version': versions[d], 'frame': c,
                              'position': position, 'SOURCE_support': support,
                              'signed_full_RAW_row': dict(rows[d])}
                else:
                    need(opened is not None and opened['source'] == d and state[d] == c and state[658] == f == 0,
                         'ERASE physical source/coframe guard')
                    need(versions[d] == opened['version'] and rows[d] == rows[658] == opened['signed_full_RAW_row'],
                         'literal all-RAW signed SOURCE immutable/ERASE equality')
                    captures.append({'source': d, 'frame': c, 'version': versions[d],
                                     'COPY_position': opened['position'], 'ERASE_position': position,
                                     'SOURCE_support': opened['SOURCE_support'],
                                     'signed_RAW_terms': len(rows[d])})
                    rows[658] = {}; state[658] = None; norm[658] = 0; opened = None
        need(opened is None and not rows[658] and state[658] is None, 'private zero/closed at return')
        need(state[:658] == list(word['start'] if reverse else word['final']), 'actual all658 SOURCE endpoints')
        need(len(captures) == 9, 'all nine actual complete captures')
        return rows, {'positive_prefix': peak, 'histogram': dict(sorted(hist.items())), 'captures': captures}
    reports, outputs = {}, {}
    identity = [{i: 1} for i in range(658)]+[{}]
    for reverse, name in ((False, 'forward'), (True, 'reverse')):
        rows, report = replay_rows(reverse)
        for i in list(range(111))+list(range(222, 658)):
            need(rows[i] == {i: 1}, 'all original SOURCE and arbitrary-DIRTY helpers restored as signed functions')
        for i in range(111, 222):
            need({j for j, c in rows[i].items() if c % 2} == {i, i-111}, 'all TARGET required Boolean shear')
        expected = native['words']['candidate']['local_checks'][name]
        need(report['positive_prefix'] == expected['positive_prefix_bound'], 'new positive F/R bound')
        need({str(k): v for k, v in report['histogram'].items()} == expected['histogram'], 'new paid native QUERY profile')
        reports[name], outputs[name] = report, rows
    need(replay_rows(True, outputs['forward'])[0] == identity, 'signed inverse forward/reverse allRAW')
    need(replay_rows(False, outputs['reverse'])[0] == identity, 'signed inverse reverse/forward allRAW')
    return {'all_actual_frames': 636, 'original_root_Gram_det_histogram': dict(gram_hist),
            'all658_independent_signed_RAW': True, 'all_original_DIRTY_unrestricted': True,
            'both_signed_inverse_orders': True, 'private_source_index': 658,
            'private_original_DATA_credit': 0, 'orientations': reports}


def finite_row_invoice(invoice, native_review):
    F = native_review['orientations']['forward']['positive_prefix']
    R = native_review['orientations']['reverse']['positive_prefix']
    need((F, R) == (70697651, 546751590), 'new independent positive envelope')
    E, J = 900416, 8*32*9*(222+436)+8*28416+2*9*32*436+2*2592
    unit = 288*19071+63936
    selectors = 2*9*32*((28416-1)+436*64*1149)
    P5, P9 = 64*F**3*R**2, 2**18*F**5*R**4
    nonprefix = unit+J*(16*(64**2+1)**2)+J*28425+E*(8*64**2+8+128*(2*64)**3)+16*64**3+2592+selectors+1
    C = P9+nonprefix
    C2 = (C+1)**2*(E+1)**2
    values = {'positive_F': F, 'positive_R': R, 'p5': P5, 'p9': P9,
              'p5_bits': P5.bit_length(), 'p9_bits': P9.bit_length(),
              'charged_p5': 64*((P5.bit_length()+63)//64),
              'charged_p9': 64*((P9.bit_length()+63)//64),
              'unit_ADDs': unit, 'J': J, 'selectors': selectors, 'nonprefix': nonprefix,
              'coefficient': C, 'coefficient_bits': C.bit_length(),
              'two_level_coefficient': C2, 'two_level_bits': C2.bit_length(),
              'charged_two_level': 640}
    for key, value in values.items():
        need(int(invoice[key]) == value, 'new full finite invoice arithmetic: '+key)
    need((values['charged_p5'], values['charged_p9'], values['charged_two_level']) == (192, 320, 640),
         'old precision ceilings cannot be retained')
    need(values['charged_two_level'] >= 64*((C2.bit_length()+63)//64), 'two-level overcharge covers exact bits')
    row = 2*(64**2+1)+9909+252
    need(row == invoice['ROW_coefficient'] == 18355 < invoice['old_ROW_ceiling'] == 20161,
         'ROW theorem coefficient is separate from events/prefix')
    need(2*42**2 == 3528 < 4096 and 658+1 <= 680 and invoice['physical'] == 28425,
         'proper child/minimal-width/physical private stock')
    return dict(values, ROW_coefficient=row,
                scope='Inherited source-bound logicalp1 root coupling and compatible R=tK^D(n); finite constants enter C. No arbitrary fresh stock, binary physical-tape compiler or outer closure theorem.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--provider', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True, help='JSON result file or output directory')
    args = ap.parse_args()
    started = process_time()
    provider = args.provider.resolve()
    need(provider.is_dir(), 'provider directory missing')
    manifest_name = next((n for n in ('SOURCE-AUDIT-PINS.json', 'REHOST-MANIFEST.json', 'MANIFEST.json')
                          if (provider/n).is_file()), None)
    need(manifest_name is not None, 'configured source manifest missing')
    manifest = json.loads((provider/manifest_name).read_bytes())
    mapping = manifest.get('files')
    if isinstance(mapping, list):
        need(all(isinstance(v, dict) and set(v) >= {'path', 'sha256'} for v in mapping), 'source list schema')
        need(len({v['path'] for v in mapping}) == len(mapping), 'duplicate source manifest paths')
        mapping = {v['path']: v['sha256'] for v in mapping}
    need(isinstance(mapping, dict), 'configured manifest files map missing')
    names = ['inputs/WORD.json.gz', 'inputs/GEOMETRY.json.gz', 'inputs/TERMINAL-CHARTS.json',
             'inputs/CALLER-GEOMETRY.json.gz', 'new-owners/CHARTS.json.gz', 'new-owners/ORDER.json.gz',
             'new-owners/SLOTS.json.gz', 'new-owners/REMAINDERS.json.gz', 'new-owners/DISPATCH.json.gz', 'OWNERS.json']
    # Authenticate the complete configured immutable package, not only the ten
    # finite geometry datasets. Historical provenance is distinct from runtime.
    for name, expected in mapping.items():
        need(isinstance(expected, str), 'source SHA schema')
        authenticate(provider, name, expected)
    values, local_pins = [], []
    for name in names:
        need(name in mapping and isinstance(mapping[name], str), 'configured source pin absent: '+name)
        raw = authenticate(provider, name, mapping[name])
        values.append(loads(raw, name))
        local_pins.append({'path': name, 'sha256': mapping[name], 'bytes': len(raw)})
    need('NEW-INVOICE.json' in mapping, 'new actual route invoice pin')
    route_invoice = json.loads(authenticate(provider, 'NEW-INVOICE.json', mapping['NEW-INVOICE.json']))
    result = audit(values, route_invoice)
    extra_names = ['native.py', 'upstream-native.py', 'owner.py', 'upstream-owner.py',
                   'caller.py', 'upstream-caller.py', 'CALLER-SOURCES.json', 'NATIVE.json',
                   'NEW-INVOICE.json', 'ALLSIZE-BINDING.md']
    extra = {}
    for name in extra_names:
        need(name in mapping, 'actual runtime source pin absent: '+name)
        raw = authenticate(provider, name, mapping[name])
        extra[name] = raw
        local_pins.append({'path': name, 'sha256': mapping[name], 'bytes': len(raw)})
    # Each wrapper authenticates the actual bytes it compiles, independent of
    # import cache. These checks inspect the source rather than executing it.
    for wrapper, upstream in (('native.py', 'upstream-native.py'), ('owner.py', 'upstream-owner.py')):
        need(sha256(extra[upstream]).hexdigest().encode() in extra[wrapper], 'wrapper immutable upstream pin')
    active_word_sha = mapping['inputs/WORD.json.gz']
    need(active_word_sha.encode() in extra['native.py'] and active_word_sha.encode() in extra['owner.py'],
         'actual active658 WORD pin in both runtime interfaces')
    source_map = json.loads(extra['CALLER-SOURCES.json'])
    need(source_map['base'] == '12fa8c5c844be21bfefb38a19503fbd867a11244' and len(source_map['files']) == 84,
         'retained complete caller source-map scope')
    source_digest = sha256(json.dumps(source_map['files'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(source_digest.encode() in extra['caller.py'], 'actual runtime caller source-map authentication')
    prefix = 'research/selected-bit-recursive-caller/'
    for name, expected in source_map['files'].items():
        need(name.startswith(prefix), 'caller source scope')
        relative = 'inputs/caller/'+name[len(prefix):]
        authenticate(provider, relative, expected)
    result['native_SOURCE'] = native_source_audit(values[0], values[1], json.loads(extra['NATIVE.json']))
    result['new_finite_ROW_invoice'] = finite_row_invoice(json.loads(extra['NEW-INVOICE.json']), result['native_SOURCE'])
    result['source_manifest_sha256'] = sha256((provider/manifest_name).read_bytes()).hexdigest()
    result['complete_configured_files_authenticated'] = len(mapping)
    result['runtime_84_caller_bytes_authenticated'] = True
    # Negative input authentication control is in memory; candidate files
    # are never modified, even while exercising the rejection path.
    sample = names[0]
    raw = (provider/sample).read_bytes()
    altered = bytes([raw[0] ^ 1])+raw[1:]
    result['defect_controls'].append(rejection(
        lambda: need(sha256(altered).hexdigest() == mapping[sample], 'source byte pin: '+sample),
        'source-byte-pin'))
    result.update({'status': 'PASS_INDEPENDENT_PORTABLE_SOURCE_OWNER_AUDIT',
                   'source_manifest': manifest_name, 'source_pins': local_pins,
                   'producer_auditor_imported': False, 'stdlib_only': True,
                   'new_exponent_admitted': None,
                   'scope': 'Exact SOURCE/owner/typed whole-packet ROW compatibility; inherited logical p1 root-coupled input/stock/callee premises. Physical compiler and outer arbitrary stock transfer remain separate.',
                   'CPU_seconds': process_time()-started})
    output = args.output
    if output.suffix.lower() != '.json':
        output = output/'RESULT.json'
    need(output.resolve() not in {provider/name for name in names}, 'output would overwrite source input')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'relative_SOURCE_charts', 'family_SOURCE_charts',
          'rho15_SOURCE_identities', 'helper_owner_occurrences', 'samefamily_pairs_per_replica',
          'max64_route', 'selector_G', 'defect_controls', 'CPU_seconds')}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
