#!/usr/bin/env python3
"""Bounded source-bound physical caller audit. Credit/scope: CONTRACT.md.

Apache-2.0; new independent spectral/ownership audit, Codex-assisted.
Retained compiler/literal descriptions are authenticated before import.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from functools import lru_cache
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
import os
import resource
import sys
import time

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
PRIOR = ROOT/'outputs/p104-contact-reassessment-20261025'
NATIVE = ROOT/'outputs/p104-native-contact-audit-20261025'
DIM = 265
AXES = tuple(1 << i for i in range(DIM))
ZERO = bytes([128])*34
TRACE_START = time.monotonic()


def checkpoint(stage, **counts):
    # Operational evidence is deliberately outside the scientific JSON output.
    trace = os.environ.get('P104_TRACE_FILE')
    if trace:
        entry = {'stage': stage, 'elapsed_seconds': time.monotonic()-TRACE_START,
                 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 'phase_cache_entries': polynomial.cache_info().currsize, **counts}
        with open(trace, 'a') as stream:
            stream.write(json.dumps(entry, sort_keys=True)+'\n')
            stream.flush()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def terms(items):
    out = Counter()
    for axis, value in items:
        need(type(axis) is int and 0 <= axis < (1 << DIM), 'spectral axis range')
        out[axis] += value
    return tuple(sorted((axis, n % 4) for axis, n in out.items() if axis and n % 4))


@lru_cache(maxsize=128)
def polynomial(items):
    # parity(S) = sum z_i - 2 sum z_i*z_j mod4; higher terms vanish.
    linear, quadratic = {}, set()
    for axis, n in items:
        support = [i for i in range(axis.bit_length()) if axis >> i & 1]
        for i in support:
            linear[i] = (linear.get(i, 0)+n) % 4
        if n % 2:
            for i, a in enumerate(support):
                for b in support[i+1:]:
                    pair = (a, b)
                    if pair in quadratic:
                        quadratic.remove(pair)
                    else:
                        quadratic.add(pair)
    return (0, tuple(sorted((i, n) for i, n in linear.items() if n)), tuple(sorted(quadratic)))


def image(columns, value):
    out = 0
    while value:
        bit = value & -value
        out ^= columns[bit.bit_length()-1]
        value ^= bit
    return out


def moved(items, columns):
    return terms((image(columns, a), n) for a, n in items)


def contact(old, new, route):
    old_phase, new_phase = polynomial(moved(old, route)), polynomial(new)
    need(old_phase[0] == new_phase[0] and old_phase[2] == new_phase[2], 'contact absolute/quadratic phase')
    a, b = dict(old_phase[1]), dict(new_phase[1])
    delta = {i: (b.get(i, 0)-a.get(i, 0)) % 4 for i in a.keys() | b.keys()}
    need(set(delta.values()) <= {0, 2}, 'contact translation has even linear phase')
    t = sum(1 << i for i, n in delta.items() if n == 2)
    need(polynomial(terms([*moved(old, route), (t, 2)])) == new_phase, 'complete contact phase')
    inv_t = image(route, t)
    need(polynomial(terms([*moved(new, route), (inv_t, 2)])) == polynomial(old), 'inverse contact phase')
    return {'translation': t, 'inverse_translation': inv_t}


def route_for(stage, basis, q):
    swaps = [] if stage == 0 else [b ^ AXES[9+8*(stage-1)+i] for i, b in enumerate(basis)]
    route = tuple(e ^ image(swaps, sum(((e & v).bit_count() % 2) << i for i, v in enumerate(swaps))) for e in AXES)
    need(all((v & w).bit_count() % 2 == 0 for v in swaps for w in swaps), 'route transvections commute')
    need(all(image(route, route[i]) == e for i, e in enumerate(AXES)), '265-axis route inverse')
    # Fixed complement and the <=17-axis support reduce orthogonality exactly.
    support = [i for i, e in enumerate(AXES) if route[i] != e]
    need(len(support) <= 17 and image(route, q) == q, 'route support and fixed Q')
    need(all((route[i] & route[j]).bit_count() % 2 == int(i == j) for i in support for j in range(DIM)), 'route orthogonality')
    return route, swaps


def layout(selected, q, basis, kind):
    # P_O = (base9 orthogonal change) after (coordinate permutation).
    base = list(AXES[:9]) if kind == 'main' and selected[0] else [q, *basis]
    need(len(base) == 9 and all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(base) for j, b in enumerate(base)), 'canonicalizer base9 orthogonal')
    active = (list(range(9)) if selected[0] else [0]) if kind == 'main' else (list(range(1, 9)) if selected[0] else [])
    active += [i for s in range(1, 33) if selected[s] for i in range(9+8*(s-1), 9+8*s)]
    active_set = set(active)
    order = active + [i for i in range(DIM) if i not in active_set]
    need(sorted(order) == list(range(DIM)), 'canonicalizer permutation')
    columns = tuple(base[i] if i < 9 else AXES[i] for i in order)
    position = {old: new for new, old in enumerate(order)}
    def inverse(value):
        old = sum(((a & value).bit_count() % 2) << i for i, a in enumerate(base)) | (value & ~511)
        out = 0
        while old:
            low = old & -old
            out ^= AXES[position[low.bit_length()-1]]
            old ^= low
        return out
    need(all(inverse(columns[i]) == e for i, e in enumerate(AXES)), 'explicit complete canonicalizer inverse')
    rank = len(active)
    positive = terms((a, 1) for a in columns[:rank])
    return {'base9_columns': base, 'axis_order': order, 'rank': rank, 'inverse': 'inverse permutation after base9 transpose'}, positive


def plus(dst, src, factor):
    for key, n in src.items():
        n = dst.get(key, 0)+factor*n
        if n:
            dst[key] = n
        else:
            dst.pop(key, None)


def packed(term):
    need(len(term) == 34 and all(type(x) is int and -128 <= x <= 127 for x in term), 'exact Laurent exponent range')
    return bytes(x+128 for x in term)


def shifted(row, term, factor=1):
    need(len(term) == 34, 'complete Laurent shift dimension')
    active = [(i, n) for i, n in enumerate(term) if n]
    out = []
    for cell in row:
        moved_cell = {}
        for key, n in cell.items():
            target = bytearray(key)
            for i, delta in active:
                value = target[i]+delta
                need(0 <= value <= 255, 'Laurent exponent overflow rejected, never wrapped')
                target[i] = value
            moved_cell[bytes(target)] = factor*n
        out.append(moved_cell)
    return out


def laurent(word):
    # The literal boundary has integer coefficients. Z embeds exactly in Q.
    def coefficient(value):
        n = F(value)
        need(n.denominator == 1, 'source Laurent boundary is integral')
        return n.numerator
    no_shift = (0,)*34
    rows = [[{ZERO: 1} if i == j else {} for j in range(32)] for i in range(32)]
    def scalar(e):
        op, dst = e[:2]
        if op == 'SWAP':
            rows[dst], rows[e[2]] = rows[e[2]], rows[dst]
        elif op == 'SCALE':
            rows[dst] = shifted(rows[dst], no_shift, coefficient(e[2]))
        else:
            need(op == 'ADD', 'boundary grammar')
            for a, b in zip(rows[dst], rows[e[2]]):
                plus(a, b, coefficient(e[3]))
    for e in word['boundaries']['right_program']:
        scalar(e)
    for step, e in enumerate(word['physical_events']):
        op = e[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            _, s, pair, back = e
            x, y = 2*pair, 2*pair+1
            if back:
                x, y = y, x
            for a, b in zip(rows[y], shifted(rows[x], (1 if back else -1,)+(0,)*33)):
                plus(a, b, -1 if back else 1)
            if op == 'LOCAL':
                t = (0,)+tuple(int(i == s) for i in range(33))
                rows[x], rows[y] = shifted(rows[x], t), shifted(rows[y], t)
        elif op == 'Q_POWER':
            need(e[2] in (-2, 2), 'only free even Q powers')
            rows[e[1]] = shifted(rows[e[1]], (e[2],)+(0,)*33)
        elif op == 'IDLE':
            t = (0,)+tuple(int(i in e[2]) for i in range(33))
            for r in (2*e[1], 2*e[1]+1):
                rows[r] = shifted(rows[r], t)
        elif op == 'SIGNED_SWAP':
            rows[e[1]], rows[e[2]] = rows[e[2]], shifted(rows[e[1]], no_shift, -1)
        else:
            scalar(e)
        if step % 40 == 0:
            checkpoint('laurent_progress', step=step, terms=sum(len(cell) for row in rows for cell in row))
    for e in word['boundaries']['left_program']:
        scalar(e)
    expected = [[{packed(word['diagonal'][i]): 1} if i == j else {} for j in range(32)] for i in range(32)]
    need(rows == expected, 'literal complete free-Laurent endpoint and exterior signs')
    return digest([[[[[x-128 for x in k], str(n)] for k, n in sorted(cell.items())] for cell in row] for row in rows])


def reject(work):
    try:
        work()
    except ValueError as e:
        return str(e)
    raise ValueError('deliberate fault accepted')


def query_check(program, src, dst, scratch, q, basis):
    need(len({src, dst, scratch}) == 3 and scratch >= FIELD_COUNT, 'owned query/source/destination separation')
    need(program == [['INIT_ZERO', scratch], ['COPY', scratch, src], ['P_INVERSE', scratch, [q, *basis]],
                     ['GAUSSIAN', scratch, 1], ['P', scratch, [q, *basis]], ['X', scratch, q],
                     ['ADD', dst, scratch, 1], ['CLEAR_OWNED', scratch]], 'literal clear/copy/positive-child/correct/add/clear chronology')
    need(polynomial(terms([(q, 1), (q, 2)])) == polynomial(terms([(q, -1)])), 'positive Q plus translation is Q inverse')


def main():
    checkpoint('authenticate_begin')
    manifest = read(B/'INPUTS.json')
    for name, sha in manifest['files'].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha, 'source pin '+name)
    word = read(Path(os.environ['P104_WORD'])) if 'P104_WORD' in os.environ else read(PRIOR/'sources/contact/WORD.json.gz')
    controller = read(PRIOR/'sources/predecessor/CONTROLLER.json')
    source = read(Path(os.environ['P104_RESULT'])) if 'P104_RESULT' in os.environ else read(PRIOR/'sources/contact/RESULT.json')
    public = word['public']
    owned_count = word.get('owned_fields', 8)
    owned_live, owned_peak, owned_lifetimes = set(), 0, 0
    for event in word['program']:
        if event[0] == 'INIT':
            need(public <= event[1] < public+owned_count and event[1] not in owned_live, 'owned allocation')
            owned_live.add(event[1]); owned_lifetimes += 1
            owned_peak = max(owned_peak, len(owned_live))
        elif event[0] == 'CLEAR':
            need(event[1] in owned_live, 'owned release')
            owned_live.remove(event[1])
    need(not owned_live, 'owned fields restored before return')
    helper_count = public - 208
    field_count = 3328 + 18*helper_count
    global FIELD_COUNT
    FIELD_COUNT = field_count
    phases = {r['q']: r['idle_children'][0]['orthogonal_axes'][:8] for r in read(B/'sources/DATA-PHASES.json')['recipes']}
    C = load(NATIVE/'sources/clifford_exact.py', 'route_clifford_compiler')
    V = load(NATIVE/'sources/native_verify.py', 'route_literal_definitions')
    D = load(NATIVE/'check.py', 'route_independent_dense')
    checkpoint('contacts_begin')
    controls, routes, contact_payload = {}, [], []
    first_translation = None
    full = [e for e in controller['physical_events'] if e[0] == 'LOCAL']
    need(len(full) == 18 and all(not e[3] for e in full), 'all18 forward local calls')
    for _, stage, pair, _ in full:
        for port, q in enumerate(word['ports']):
            basis = phases[q]
            need(q.bit_count() % 2 == 1 and all((q & b).bit_count() % 2 == 0 for b in basis), 'odd Q and orthogonal helper basis')
            route, swaps = route_for(stage, basis, q)
            spectator = [(a, 1) for a in AXES[9:9+8*stage]]
            raw_x = terms([(q, 1)]) if stage == 0 else terms((a, 1) for a in AXES[:9+8*(stage-1)])
            raw_y = () if stage == 0 else terms([*raw_x, (q, -1)])
            entry_x, entry_y = terms([*spectator, (q, 1)]), terms(spectator)
            exit_x = terms([*spectator, *((a, 1) for a in AXES[:9])])
            exit_y = terms([*exit_x, (q, -1)])
            out_x = terms((a, 1) for a in AXES[:9+8*stage])
            out_y = terms([*out_x, (q, -1)])
            pairs = [(raw_x, entry_x), (raw_y, entry_y), (exit_x, out_x), (exit_y, out_y)]
            maps = [contact(a, b, route) for a, b in pairs]
            for (a, b), record in zip(pairs, maps):
                if record['translation'] and first_translation is None:
                    first_translation = (a, b, route)
            d0 = [(a, 1) for a in AXES[:9]]+[(q, -1)]
            delta = terms(d0 if stage == 0 else ((a, 1) for a in AXES[9+8*(stage-1):9+8*stage]))
            for incoming, outgoing, extra in [(0, 2, []), (1, 3, []), (0, 3, [(q, -1)])]:
                actual = terms([*moved(terms([*d0, *extra]), route),
                                (maps[outgoing]['translation'] ^ image(route, maps[incoming]['translation']), 2)])
                need(polynomial(actual) == polynomial(terms([*delta, *extra])), 'physical entry/local/exit block including translations')
            need(all(m['translation'].bit_count() <= 17 and m['inverse_translation'].bit_count() <= 17 for m in maps), 'contact translation allowance')
            routes.append({'stage': stage, 'pair': pair, 'port': port, 'q': q, 'swap_vectors': swaps, 'maps': maps})
            contact_payload.append([stage, q, maps])
        checkpoint('contact_site_complete', stage_index=stage, contacts=4*len(routes))
    need(hashlib.sha256(json.dumps(contact_payload, separators=(',', ':')).encode()).hexdigest() == source['physical_caller']['route_payload_sha256'], 'author contact payload independently reconstructed')
    a, b, route = first_translation
    controls['omitted_contact_translation'] = reject(lambda: need(polynomial(moved(a, route)) == polynomial(b), 'missing nonzero physical contact translation'))
    controls['wrong_route'] = reject(lambda: contact(a, b, AXES))
    controls['global_phase'] = reject(lambda: need((1, *polynomial(a)[1:]) == polynomial(a), 'nonzero absolute spectral phase'))
    checkpoint('laurent_begin')
    endpoint_hash = laurent(controller)
    checkpoint('laurent_endpoint_complete')
    bad = deepcopy(controller)
    next(e for e in bad['physical_events'] if e[0] == 'SIGNED_SWAP')[0] = 'SWAP'
    controls['exterior_sign'] = reject(lambda: laurent(bad))
    bad = deepcopy(controller)
    bad['physical_events'].remove(next(e for e in bad['physical_events'] if e[0] == 'IDLE'))
    controls['lost_idle'] = reject(lambda: laurent(bad))
    checkpoint('laurent_controls_complete')
    # Native helper endpoint normalizers and intrinsic main adapters.
    @lru_cache(None)
    def chart(i):
        return C.canonical_frame(9, tuple(word['frames'][i]))
    checked, normalizers = {}, []
    def exact(actual, expected, label):
        key = digest([actual, expected])
        if key not in checked:
            need(V.tableau(actual) == V.tableau(expected), label+' signed Pauli images')
            need(D.dense_column(D.compile_circuit(actual), 0) == D.dense_column(D.compile_circuit(expected), 0), label+' exact independent phase anchor')
            checked[key] = True
        return key
    @lru_cache(None)
    def endpoint(a, b):
        rec, _ = C.lower_child(chart(a).adjoint().then(chart(b)))
        literal = V.adjoint(V.frame(word['frames'][a], 9))+V.frame(word['frames'][b], 9)
        check = exact(V.recipe(rec), literal, 'helper endpoint')
        right, left = V.monomial(rec['right']), V.monomial(rec['left'])
        exact(V.adjoint(right)+literal+V.adjoint(left), V.fourier(rec['rank']), 'normalized helper Gaussian')
        return rec, check
    local_main = set(word['live']) | {r+112 for r in word['live']}
    helpers = [r for r in range(public) if r not in local_main]
    helper_profile = Counter()
    for h in helpers:
        a, b = word['initial'][h], word['final'][h]
        rec, check = endpoint(a, b)
        rank = len(word['frames'][b])-len(word['frames'][a])
        need(rank > 0 and rec['rank'] == rank, 'helper target native rank')
        helper_profile[rank] += 1
        normalizers.append({'local_field': h, 'rank': rank, 'initial': a, 'final': b, 'recipe': rec, 'exact_check': check,
                            'placement': 'right inverse before LOCAL; left inverse after LOCAL'})
    checkpoint('helper_normalizers_complete', helpers=len(normalizers))
    adapters = []
    for r, q in zip(word['live'], word['ports']):
        a, b = word['initial'][r], word['final'][r+112]
        tests = [(C.cgate(9, q, 1).adjoint().then(chart(a)), V.adjoint((('C', q, 1),))+V.frame(word['frames'][a], 9)),
                 (chart(b).adjoint().then(C.cgate(9, q, -1).then(C.fourier(9))), V.adjoint(V.frame(word['frames'][b], 9))+(('C', q, -1),)+V.fourier(9))]
        for op, literal in tests:
            rec, _ = C.lower_child(op)
            need(rec['rank'] == 0, 'intrinsic main adapter is monomial')
            adapters.append({'local_field': r, 'recipe': rec, 'exact_check': exact(V.recipe(rec), literal, 'intrinsic main adapter')})
    checkpoint('main_intrinsic_adapters_complete', adapters=len(adapters))
    need(len(helpers) == helper_count and helper_profile == Counter({int(k):v for k,v in source['local']['helpers'].items()}), 'complete helper profile')
    fields = []
    for site, event in enumerate(full):
        mapping = {}
        for p, r in enumerate(word['live']):
            mapping[r], mapping[r+112] = 2*event[2]*104+p, (2*event[2]+1)*104+p
        mapping.update({h:3328+site*helper_count+i for i, h in enumerate(helpers)})
        need(len(mapping) == len(set(mapping.values())) == public, 'injective full-call public inventory')
        fields.append({'site': site, 'stage': event[1], 'local_to_global': [mapping[i] for i in range(public)], 'owned_lifetimes': ({f'{public}..{public+7}':field_count} if owned_count == 8 else {str(public+i):field_count+i for i in range(owned_count)})})
    helper_ids = [f['local_to_global'][h] for f in fields for h in helpers]
    need(set(helper_ids) == set(range(3328, field_count)) and len(helper_ids) == len(set(helper_ids)), 'all fresh helpers owned once')
    def bad_alias():
        bad_ids = helper_ids[:]
        bad_ids[helper_count] = bad_ids[0]
        need(len(bad_ids) == len(set(bad_ids)), 'helper output alias collision')
    controls['helper_alias_collision'] = reject(bad_alias)
    checkpoint('ownership_complete', helpers=len(helper_ids))
    layouts, mains, idles, queries = {}, [], [], []
    main_profile, idle_profile = Counter(), Counter()
    negative = None
    def intern(value):
        key = digest(value)
        layouts[key] = value
        return key
    for bank, term in enumerate(controller['diagonal']):
        qp, selected = term[0], term[1:]
        need(qp in (-1, 1) and set(selected) <= {0, 1}, 'endpoint exponent alphabet')
        for port, q in enumerate(word['ports']):
            record, positive = layout(selected, q, phases[q], 'main')
            physical = terms([(q, qp-selected[0])]+[(a, 1) for s, yes in enumerate(selected) if yes for a in (AXES[:9] if s == 0 else AXES[9+8*(s-1):9+8*s])])
            translation = q if qp == -1 else 0
            need(polynomial(terms([*physical, (translation, 2)])) == polynomial(positive), 'full main physical target with final translation')
            need(record['rank'] == 1+8*sum(selected), 'complete main rank')
            if translation and negative is None:
                negative = physical, positive
            main_profile[record['rank']] += 1
            mains.append({'field':bank*104+port, 'rank':record['rank'], 'layout':intern(record), 'final_translation':translation,
                          'placement':'P_O before RIGHT; X_translation then P_O inverse after LEFT'})
        checkpoint('main_bank_complete', bank=bank, mains=len(mains), layouts=len(layouts))
    controls['missing_final_main_translation'] = reject(lambda: need(polynomial(negative[0]) == polynomial(negative[1]), 'missing final main translation'))
    scratch = field_count if owned_count == 8 else field_count+owned_count
    for index, e in enumerate(controller['physical_events']):
        if e[0] == 'IDLE':
            selected = [int(i in e[2]) for i in range(33)]
            need(len(e[2]) == len(set(e[2])), 'idle distinct stages')
            for port, q in enumerate(word['ports']):
                record, positive = layout(selected, q, phases[q], 'idle')
                physical = terms([(a, 1) for s in e[2] for a in (AXES[:9] if s == 0 else AXES[9+8*(s-1):9+8*s])]+[(q, -1)]*selected[0])
                correction = contact(positive, physical, AXES)['translation']
                need(record['rank'] == 8*len(e[2]), 'whole idle rank')
                idles.append({'event':index, 'fields':[(2*e[1]+k)*104+port for k in (0, 1)], 'layout':intern(record), 'translation':correction,
                              'program':'P_O inverse; Gaussian(rank); P_O; X_translation'})
                idle_profile[record['rank']] += 2
        elif e[0] == 'QUERY_SHEAR':
            need(not e[3], 'source thin queries are all forward')
            for port, q in enumerate(word['ports']):
                src, dst = 2*e[2]*104+port, (2*e[2]+1)*104+port
                program = [['INIT_ZERO', scratch], ['COPY', scratch, src], ['P_INVERSE', scratch, [q, *phases[q]]],
                           ['GAUSSIAN', scratch, 1], ['P', scratch, [q, *phases[q]]], ['X', scratch, q], ['ADD', dst, scratch, 1], ['CLEAR_OWNED', scratch]]
                query_check(program, src, dst, scratch, q, phases[q])
                queries.append({'event':index, 'program':program})
    p = queries[0]['program']; src, dst = p[1][2], p[-2][1]
    q = p[-3][2]; basis = phases[q]
    controls['owned_lifetime'] = reject(lambda: query_check(p, src, dst, src, q, basis))
    bad_query = [row for row in p if row[0] != 'X']
    controls['missing_inverse_Q_correction'] = reject(lambda: query_check(bad_query, src, dst, scratch, q, basis))
    checkpoint('queries_idles_complete', queries=len(queries), idles=len(idles))
    need(polynomial(terms([(q, 1)])) != polynomial(terms([(q, -1)])), 'omitted inverse correction fails spectral operator')
    paid_local = Counter(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]])) for e in word['program'] if e[0] == 'MOVE')
    paid = Counter({r:18*n for r, n in paid_local.items()})+idle_profile+Counter({1:len(queries)})
    targets = Counter({r:18*n for r, n in helper_profile.items()})+main_profile
    costs = source['complete_cost']
    need(paid == Counter({int(r):n for r, n in costs['paid'].items()}) and targets == Counter({int(r):n for r, n in costs['targets'].items()}), 'complete unchanged paid/target invoice')
    need(len(mains) == 3328 and len(idles) == 1560 and len(queries) == 1560 and sum(targets.values()) == field_count, 'complete occurrence census')
    nr = costs['nonrecursive']
    scalar = 0
    for e in word['program']:
        if e[0] in ('INIT','CLEAR'): scalar += 2
        elif e[0] == 'MOVE': continue
        else:
            q=F(e[-2]); n,d=abs(q.numerator),q.denominator
            if e[0] == 'SCALE': scalar += 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
            else: scalar += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    need(nr['local_scalar'] == scalar and nr['local_routes'] == (sum(paid_local.values())+2*helper_count+208+4*104+4*owned_lifetimes)*1000, 'independently recounted ordinary allowances')
    events, boundary = len(controller['physical_events']), sum(len(controller['boundaries'][s+'_program']) for s in ('left', 'right'))
    ordinary = 18*(nr['local_scalar']+nr['local_routes'])+len(queries)*1000+2*len(idles)*1000+len(mains)*1000+16*32*104*(events+boundary)+sum(e[0] == 'Q_POWER' for e in controller['physical_events'])*104*9
    need(17*17+17 < 1000 and 2*(264+81)+9 < 1000, 'explicit fixed-map address-pass bounds')
    need(ordinary <= nr['raw_scalar_upper'] < nr['raw_budget'], 'conservative finite descriptor passes fit retained raw allowance')
    # Packed representation controls are exact, with no modular exponent alias.
    controls['laurent_exponent_overflow'] = reject(lambda: shifted([{packed((127,)+(0,)*33):1}], (1,)+(0,)*33))
    need(shifted([{packed((-2,)+(0,)*33):3}], (2,)+(0,)*33) == [{ZERO:3}], 'negative Laurent powers retained exactly')
    result = {'schema':'p104-physical-caller-target-binding/v1', 'status':'PASS_SCOPED_CALLER_AND_TARGET_BINDING',
              'reviewed_head':manifest['reviewed_head'], 'canonical_main':manifest['canonical_main'], 'sources':manifest['files'],
              'dimension':DIM, 'free_laurent_endpoint_sha256':endpoint_hash, 'route_recipes':routes,
              'helper_normalizers':normalizers, 'intrinsic_main_adapters':adapters, 'field_maps':fields,
              'canonical_layouts':layouts, 'main_targets':mains, 'whole_idles':idles, 'thin_queries':queries,
              'paid':dict(sorted(paid.items())), 'targets':dict(sorted(targets.items())), 'controls':controls,
              'native_checks':{'distinct_signed_Pauli_and_independent_phase_anchors':len(checked), 'fresh_helpers':len(helper_ids), 'owned_peak':owned_peak},
              'ordinary':{'abstract_address_phase_scalar_pass_upper':ordinary, 'retained_raw_scalar_upper':nr['raw_scalar_upper'],
                          'paid_native_maps_replayed':False, 'machine_and_precision_admitted':False,
                          'main_map_pair_pass_bound':2*(264+81)+9, 'local_contact_pass_bound':17*17+17,
                          'meaning':'fixed finite descriptor passes under retained per-pass/tape contract; not a new tape or precision theorem'},
              'limits':['Local all-input native ABI and untouched paid-map correctness remain inherited.',
                        'Spectators are not additional productive outputs; helper normalizers occur before/after their own fresh call.',
                        'No full compiler/outer replay or independent human/formal admission. No kappa claim.'], 'kappa_claim':None}
    checkpoint('invoice_complete', paid=sum(paid.values()), targets=sum(targets.values()))
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    checkpoint('scientific_output_complete')


if __name__ == '__main__':
    main()
