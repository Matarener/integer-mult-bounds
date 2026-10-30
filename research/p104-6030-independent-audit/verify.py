#!/usr/bin/env python3
"""Independent replay, delta, invoice, dense native and funding audit of PR6030.  Apache-2.0.

PR6030 (DreamingOfClouds) removes helper 470's frame-593 rung from PR5907's P104 word.  Python 3.12, standard
library only.  The replay, invoice, dense-comparison and funding code is Matarener's PR5827/PR5907 audit
(research/p104-unread-rung-independent-audit/verify.py, prepared with Claude), copied here function for function
and applied to the PR5907 -> PR6030 pair.  Nothing is imported from the PR6030 package except its data files
and, in layer 0 only, its construct.py.
Layers (canonical main contains both packages):
  0. sources: PR6030's pinned PR5907 word equals canonical main's PR5907 word, its PR5827 archive equals the one
     pinned in PR5907, and PR6030's construct.py regenerates the shipped word payload;
  1. own exact replay of the PR5907 and PR6030 words (strict MOVE nesting, common charts, dyadic coefficients,
     owned lifetimes, all 799 endpoint rows, helper nesting) and the exact delta: unchanged fields, the three
     boundary changes, the six changed itineraries, INIT/CLEAR/COPY and every other MOVE unchanged as multisets,
     paid and helper rank deltas;
  2. own invoice recount from the physical caller events and the closed formula, against complete_cost;
  3. dense all-column absolute-phase comparison of every native operator in the PR6030 inventory that is not in
     the predecessor's FULL-CHECK.json, plus a fixed subset of the old ones matched against those digests;
     --full [--jobs N] recomputes the whole PR6030 inventory;
  4. own 80-digit decimal interval engine: raw crossing, tested saving, tail ratios, uniqueness.
"""
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from hashlib import sha256
from multiprocessing import Pool
from pathlib import Path
import gzip, importlib.util, io, json, sys, tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P07 = ROOT/'research/p104-helper468-rung-removal'
P30 = ROOT/'research/p104-helper470-twin-rung-removal'
PRED = ROOT/'research/p104-unread-rung-independent-audit'
CONTROLLER = ROOT/'research/p104-productive-controller/CONTROLLER.json'
CLIFFORD = ROOT/'research/p104-native-channel/vendor/clifford_exact.py'
LITERAL = ROOT/'research/p104-native-channel/vendor/native_verify.py'
DENSE = ROOT/'research/p104-contact-independent-audit/capsule/outputs/p104-native-contact-audit-20261025/check.py'


def log(kind, **data):
    print(kind, json.dumps(data, sort_keys=True, default=str)[:300], flush=True)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin '+row['path'])


# ---------------------------------------------------------------- layer 0
def layer0():
    pinned = (P30/'inputs/pr5907-WORD.json.gz').read_bytes()
    canon = (P07/'WORD.json.gz').read_bytes()
    need(gzip.decompress(pinned) == gzip.decompress(canon), 'PR6030 pinned PR5907 word equals canonical main payload')
    need((P30/'inputs/pr5827-source.tar').read_bytes() == (P07/'inputs/pr5827-source.tar').read_bytes(),
         'PR6030 PR5827 archive equals the one pinned in PR5907')
    spec = importlib.util.spec_from_file_location('a6030_construct', P30/'construct.py')
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
    rebuilt = K.construct(read(P07/'WORD.json.gz'), read(P30/'EDIT.json.gz'))
    # own serialization of the regenerated word, compared byte for byte with the decompressed shipped payload
    own = (json.dumps(rebuilt, sort_keys=True, indent=2)+'\n').encode()
    need(own == gzip.decompress((P30/'WORD.json.gz').read_bytes()), 'regenerated PR6030 word equals the shipped payload bytes')
    out = {'pinned_pr5907_payload_equal_canonical': pinned == canon or 'payload_only',
           'pr5827_archive_equal_pr5907_pin': True, 'pr6030_regenerated_word_equal': True}
    log('L0', **out)
    return out


# ---------------------------------------------------------------- layer 1: own replay
def span(basis):
    s = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in s, 'independent binary basis')
        s |= {x ^ v for x in s}
    return frozenset(s)


def replay(w, name):
    S = [span(f) for f in w['frames']]
    n, m = w['public'], w['owned_fields']
    live = set(w['live'])
    cur = list(w['initial'])+[None]*m
    rows = [{r: Q(1)} for r in range(n+m)]
    owned, paid, peak, lifetimes = set(), Counter(), 0, 0
    ops = Counter()
    for i, e in enumerate(w['program']):
        op, r = e[0], e[1]
        ops[op] += 1
        need(0 <= r < n+m, 'role index at %d' % i)
        if op == 'MOVE':
            a, b, private = e[2], e[3], e[4]
            need(cur[r] == a and (r in owned) == private, 'transport source/ownership at %d' % i)
            need(S[b] < S[a] if private else S[a] < S[b], 'strict nesting at %d' % i)
            paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1
            cur[r] = b
        elif op == 'INIT':
            need(r >= n and r not in owned, 'owned init at %d' % i)
            owned.add(r); lifetimes += 1
            peak = max(peak, len(owned))
            rows[r], cur[r] = {}, e[2]
        elif op == 'CLEAR':
            need(r in owned and cur[r] == e[2], 'owned erasure at %d' % i)
            owned.discard(r)
            rows[r], cur[r] = {}, None
        else:
            q, f = Q(e[-2]), e[-1]
            need(q != 0 and cur[r] == f, 'destination chart at %d' % i)
            d = q.denominator
            need(d & (d-1) == 0, 'dyadic coefficient at %d' % i)
            if op == 'SCALE':
                rows[r] = {k: q*v for k, v in rows[r].items()}
            else:
                s = e[2]
                need(s != r and 0 <= s < n+m and cur[s] == f, 'common chart at %d' % i)
                if op == 'COPY':
                    need(r in owned and not rows[r], 'COPY into cleared owned field at %d' % i)
                    rows[r] = {k: q*v for k, v in rows[s].items()}
                else:
                    need(op == 'ADD', 'opcode at %d' % i)
                    t = dict(rows[r])
                    for k, v in rows[s].items():
                        t[k] = t.get(k, 0)+q*v
                    rows[r] = {k: v for k, v in t.items() if v}
    need(not owned and cur[:n] == w['final'], 'public and owned exits')
    for r in range(n+m):
        expected = {r: Q(1)} if r < n else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(rows[r] == expected, 'endpoint row %d' % r)
    main = live | {r+112 for r in live}
    helpers = Counter()
    for r in range(n):
        if r in main:
            continue
        a, b = w['initial'][r], w['final'][r]
        need(S[a] < S[b], 'helper %d initial span strictly inside final span' % r)
        helpers[len(w['frames'][b])-len(w['frames'][a])] += 1
    out = {'events': len(w['program']), 'ops': dict(ops), 'public': n, 'owned_fields': m, 'owned_lifetimes': lifetimes,
           'peak_owned': peak, 'paid': {str(k): v for k, v in sorted(paid.items())},
           'helpers': {str(k): v for k, v in sorted(helpers.items())}, 'helper_count': sum(helpers.values()),
           'endpoint_rows': n+m, 'paid_rank_mass': sum(k*v for k, v in paid.items())}
    log('L1_replay', word=name, **out)
    return paid, helpers, S, out


def diff(a, b):
    c = Counter(a); c.subtract(b)
    return {str(k): v for k, v in sorted(c.items()) if v}


def itineraries(w):
    n = w['public']
    it = {r: [w['initial'][r] if r < n else None] for r in range(n+w['owned_fields'])}
    for e in w['program']:
        if e[0] == 'MOVE':
            it[e[1]].append(e[3])
        elif e[0] == 'INIT':
            it[e[1]].append(['INIT', e[2]])
    return it


ITINERARIES = {  # PR6030 README, "The edit"
    '115': [[3, 105], [3, 189]],
    '127': [[3, 602, 637, 643, 646, 649, 141], [3, 595, 637, 643, 646, 649, 141]],
    '470': [[3, 593, 714, 875, 1001, 131, 127], [3, 714, 875, 1001, 131, 127]],
    '704': [[3, 593, 612, 127], [3, 593, 714, 127]],
    '713': [[3, 394], [76, 394]],
    '736': [[424, 127], [749, 127]],
}


def layer1(words):
    res = {}
    rp = {k: replay(w, k) for k, w in words.items()}
    for k in rp:
        res[k] = rp[k][3]
    w0, w1 = words['5907'], words['6030']
    need(w0.keys() == w1.keys(), 'same word fields')
    need(all(w0[k] == w1[k] for k in w0 if k not in ('program', 'initial', 'final')), 'frames, ports, live and sizes unchanged')
    bchg = {k: {str(r): [w0[k][r], w1[k][r]] for r in range(w0['public']) if w0[k][r] != w1[k][r]} for k in ('initial', 'final')}
    need(bchg == {'initial': {'713': [3, 76], '736': [424, 749]}, 'final': {'115': [105, 189]}},
         'PR6030 boundary changes exactly as declared: %s' % bchg)
    i0, i1 = itineraries(w0), itineraries(w1)
    changed = {str(r): [i0[r], i1[r]] for r in i0 if i0[r] != i1[r]}
    need(changed == ITINERARIES, 'exactly the six declared itineraries change: %s' % changed)
    ms = lambda w, keep: Counter(json.dumps(e) for e in w['program'] if keep(e))
    for op in ('INIT', 'CLEAR', 'COPY'):
        need(ms(w0, lambda e: e[0] == op) == ms(w1, lambda e: e[0] == op), op+' events unchanged as a multiset')
    other = lambda e: e[0] == 'MOVE' and str(e[1]) not in ITINERARIES
    need(ms(w0, other) == ms(w1, other), 'every MOVE outside the six itineraries unchanged as a multiset')
    d, h = diff(rp['6030'][0], rp['5907'][0]), diff(rp['6030'][1], rp['5907'][1])
    expect = read(P30/'EXPECT.json')
    need(d == expect['paid_delta'] and h == expect['helper_delta'], 'PR6030 deltas %s %s' % (d, h))
    margin = Counter({int(k): v for k, v in h.items()}); margin.subtract({int(k): v for k, v in d.items()})
    need(+margin == Counter({1: 1, 3: 1}) and -margin == Counter({4: 1}), 'per-LOCAL margin change is H1 + H3 - H4: %s' % margin)
    ranks = {r: [len(w0['frames'][w0['final'][r]])-len(w0['frames'][w0['initial'][r]]),
                 len(w1['frames'][w1['final'][r]])-len(w1['frames'][w1['initial'][r]])] for r in (115, 713, 736)}
    need(len(w1['program']) == expect['events'] <= 26000, 'event count and cap')
    o = res['6030']
    need([o['public'], o['owned_fields'], o['owned_lifetimes'], o['peak_owned']] == expect['inventory'], 'storage inventory')
    for k, P in (('5907', P07), ('6030', P30)):  # own replay statistics against each author's RESULT local block
        a, o = read(P/'RESULT.json')['local'], res[k]
        need([a['paid'], a['helpers'], a['paid_rank_mass'], a['public_inputs'], a['owned_fields'], a['owned_lifetimes'], a['peak_owned_fields']] ==
             [o['paid'], o['helpers'], o['paid_rank_mass'], o['public'], o['owned_fields'], o['owned_lifetimes'], o['peak_owned']],
             'own replay statistics equal author local block '+k)
    # registers whose event sequence (any opcode) differs, for the record
    seq = lambda w: {r: [json.dumps(e) for e in w['program'] if e[1] == r or (e[0] in ('ADD', 'COPY') and e[2] == r)] for r in range(w['public']+w['owned_fields'])}
    s0, s1 = seq(w0), seq(w1)
    res['delta_5907_6030'] = {'boundary_changes': bchg, 'itineraries': changed, 'paid_delta': d, 'helper_delta': h,
                              'margin_delta_per_local': {str(k): v for k, v in sorted(margin.items()) if v},
                              'changed_helper_ranks': {str(k): v for k, v in ranks.items()},
                              'ops_delta': diff(Counter(e[0] for e in w1['program']), Counter(e[0] for e in w0['program'])),
                              'events': [len(w0['program']), len(w1['program'])],
                              'registers_with_changed_event_sequence': sum(s0[r] != s1[r] for r in s0)}
    log('L1_delta_6030', **res['delta_5907_6030'])
    return res, rp


# ---------------------------------------------------------------- layer 2: invoice
def invoice(paid_local, helpers_local):
    c = read(CONTROLLER)
    ev = Counter(e[0] for e in c['physical_events'])
    need(ev['LOCAL'] == 18 and ev['QUERY_SHEAR'] == 15 and ev['IDLE'] == 15, 'caller census')
    need(all(e[3] is False for e in c['physical_events'] if e[0] == 'LOCAL'), 'forward local calls')
    P, T = Counter(), Counter()
    for e in c['physical_events']:
        if e[0] == 'LOCAL':
            P.update(paid_local); T.update(helpers_local)
        elif e[0] == 'QUERY_SHEAR':
            P[1] += 104
        elif e[0] == 'IDLE':
            P[8*len(e[2])] += 208
    for term in c['diagonal']:
        T[1+8*sum(term[1:])] += 104
    # closed formula of PR5827 PROOF.md, computed separately
    P2 = Counter({r: 18*v for r, v in paid_local.items()}); T2 = Counter({r: 18*v for r, v in helpers_local.items()})
    P2[1] += 1560; T2[145] += 208
    for L in (7, 8):
        for j in range(1, L+1):
            P2[8*(j+1)] += 208; T2[1+8*(j+1)] += 208
    need((+P, +T) == (+P2, +T2), 'event invoice equals closed formula')
    return P, T


def layer2(rp, results):
    out = {}
    for k in ('5907', '6030'):
        P, T = invoice(rp[k][0], rp[k][1])
        cost = results[k]['complete_cost']
        AP = Counter({int(r): v for r, v in cost['paid'].items()}); AT = Counter({int(r): v for r, v in cost['targets'].items()})
        need((+P, +T) == (+AP, +AT), 'own invoice equals author complete_cost for '+k)
        surplus = sum(r*v for r, v in T.items())-sum(r*v for r, v in P.items())
        out[k] = {'paid_calls': sum(P.values()), 'productive_fields': sum(T.values()), 'rank_mass_surplus': surplus,
                  'max_paid_rank': max(P), 'max_target_rank': max(T)}
        log('L2_invoice', word=k, **out[k])
    e = read(P30/'EXPECT.json')
    need([out['6030'][x] for x in ('paid_calls', 'productive_fields', 'rank_mass_surplus')] ==
         [e['paid_calls'], e['productive_fields'], e['rank_mass_surplus']], 'PR6030 headline invoice')
    return out


# ---------------------------------------------------------------- layer 4: funding
def layer4(results):
    getcontext().prec = 80
    pad = Decimal(10)**-70
    out = {}
    for k in ('5907', '6030'):
        cost = results[k]['complete_cost']

        def margin(kap):
            t, lo, hi = 1-kap, Decimal(0), Decimal(0)
            for r, n in cost['targets'].items():
                v = (t*Decimal(int(r)).ln()).exp(); lo += n*v*(1-pad); hi += n*v*(1+pad)
            for r, n in cost['paid'].items():
                v = (t*Decimal(int(r)).ln()).exp(); lo -= n*v*(1+pad); hi -= n*v*(1-pad)
            return lo, hi
        lo, hi, grid = 0, 10**12, 10**14
        while hi-lo > 1:
            m = (lo+hi)//2
            if margin(Decimal(m)/grid)[0] > 0:
                lo = m
            else:
                hi = m
        need(margin(Decimal(lo)/grid)[0] > 0 and margin(Decimal(hi)/grid)[1] < 0, 'strict crossing '+k)
        author = [Q(x) for x in cost['raw_root_interval']]
        need([Q(lo, grid), Q(hi, grid)] == author, 'crossing equals author interval '+k)
        claim, tested = Q(cost['kappa']), Q(cost['strictification']['tested'])
        sgn = lambda x: 'positive' if margin(Decimal(x.numerator)/Decimal(x.denominator))[0] > 0 else 'negative/undecided'
        need(claim < tested < Q(lo, grid) and sgn(tested) == 'positive', 'claim < tested < crossing, tested positive '+k)
        out[k] = {'raw_crossing': [str(Q(lo, grid)), str(Q(hi, grid))], 'raw_crossing_decimal': [str(Decimal(lo)/grid), str(Decimal(hi)/grid)],
                  'claim': str(claim), 'tested': str(tested), 'tested_sign': sgn(tested), 'equals_author': True}
        log('L4_funding', word=k, **out[k])
    # charged tail ratios of the strictification at the tested saving, recomputed in decimal
    for k in ('5907', '6030'):
        cost = results[k]['complete_cost']
        st = cost['strictification']
        tested, u, c, b = Decimal(str(Q(st['tested']).numerator))/Decimal(Q(st['tested']).denominator), Decimal(1)/7, 16, 17
        need(Q(st['tail_offset']) == Q(1, 7) and int(st['cutoff']) == c and int(st['floor']) == b, 'strictification constants '+k)
        pw = lambda r, x: (x*Decimal(int(r)).ln()).exp()
        t = 1-tested
        MT = sum(n*pw(r, t) for r, n in cost['targets'].items())
        MP = sum(n*pw(r, t) for r, n in cost['paid'].items())
        MPu = sum(n*pw(r, t+u) for r, n in cost['paid'].items())
        alpha, gamma = MP/MT, MPu/(pw(c, u)*MT)
        delta = sum(cost['targets'].values())*b/(pw(c, tested)*MT)
        lim = Decimal(125)/128
        need(alpha < 1-Decimal(10)**-12 and gamma < lim and delta < lim, 'tail ratios '+k)
        # uniqueness of the raw crossing on [0, .0034]: d/dk margin < 0 there (bound each term at its worst end)
        dmax = Decimal(0)
        for side, sgn in (('targets', -1), ('paid', 1)):
            for r, n in cost[side].items():
                lr = Decimal(int(r)).ln()
                worst = pw(r, 1-Decimal('0.0034')) if sgn < 0 else pw(r, Decimal(1))
                dmax += sgn*n*lr*worst
        need(dmax < 0, 'raw margin strictly decreasing on [0,.0034] '+k)
        out[k].update(alpha=str(alpha)[:22], gamma=str(gamma)[:22], delta=str(delta)[:22], derivative_upper=str(dmax)[:22])
        log('L4_tails', word=k, alpha=str(alpha)[:22], gamma=str(gamma)[:22], delta=str(delta)[:22], derivative_upper=str(dmax)[:22])
    g = Q(results['6030']['complete_cost']['kappa'])-Q(results['5907']['complete_cost']['kappa'])
    out['claim_gain_6030_over_5907'] = str(g)
    log('L4_gain', gain=str(g), gain_float=float(g))
    return out


# ---------------------------------------------------------------- layer 3: dense native
_M = {}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _init(frames):
    _M['C'] = _load('a6030_clifford', CLIFFORD)
    _M['V'] = _load('a6030_literal', LITERAL)
    _M['D'] = _load('a6030_dense', DENSE)
    _M['F'] = frames


def compare(actual, expected, rank):
    D = _M['D']
    a, b = D.compile_circuit(actual), D.compile_circuit(expected)
    h = sha256()
    for column in range(512):
        left, right = D.dense_column(a, column), D.dense_column(b, column)
        need(left == right, 'exact complex column %d' % column)
        re, im, d = left
        need(sum(v*v for v in re)+sum(v*v for v in im) == 1 << (2*d), 'exact column norm')
        need(sum(bool(x or y) for x, y in zip(re, im)) == 1 << rank, 'measured child rank')
        h.update(json.dumps([column, d, re, im], separators=(',', ':')).encode())
    return h.hexdigest()


def dense_task(task):
    C, V, F = _M['C'], _M['V'], _M['F']
    kind, a, b, q = task
    if kind in ('move', 'helper'):
        rec, _ = C.lower_child(C.canonical_frame(9, tuple(F[a])).adjoint().then(C.canonical_frame(9, tuple(F[b]))))
        rank = abs(len(F[a])-len(F[b]))
        need(rec['rank'] == rank, 'lowered rank')
        out = [list(task), rank, compare(V.recipe(rec), V.adjoint(V.frame(F[a], 9))+V.frame(F[b], 9), rank)]
    else:
        if kind == 'main_in':
            op, expected = C.cgate(9, q, 1).adjoint().then(C.canonical_frame(9, tuple(F[a]))), V.adjoint((('C', q, 1),))+V.frame(F[a], 9)
        else:
            op, expected = C.canonical_frame(9, tuple(F[a])).adjoint().then(C.cgate(9, q, -1).then(C.fourier(9))), V.adjoint(V.frame(F[a], 9))+(('C', q, -1),)+V.fourier(9)
        rec, _ = C.lower_child(op)
        need(rec['rank'] == 0, 'intrinsic adapter is monomial')
        out = [list(task), 0, compare(V.recipe(rec), expected, 0)]
    return out


def inventory(w):
    live = set(w['live'])
    main = live | {r+112 for r in live}
    moves = {(e[2], e[3]) for e in w['program'] if e[0] == 'MOVE'}
    helpers = {(w['initial'][r], w['final'][r]) for r in range(w['public']) if r not in main}
    tasks = {('move', a, b, 0) for a, b in moves} | {('helper', a, b, 0) for a, b in helpers}
    tasks |= {('main_in', w['initial'][r], 0, q) for r, q in zip(w['live'], w['ports'])}
    tasks |= {('main_out', w['final'][r+112], 0, q) for r, q in zip(w['live'], w['ports'])}
    return tasks, len(moves), len(helpers)


def layer3(words, full, jobs):
    need(words['6030']['frames'] == words['5907']['frames'], 'shared frame table')
    tasks, nmoves, nhelpers = inventory(words['6030'])
    old, _, _ = inventory(words['5907'])
    tasks = sorted(tasks)
    reference = {json.dumps(d[0]): d for d in read(PRED/'FULL-CHECK.json')['maps']}
    new = sorted(t for t in tasks if json.dumps(list(t)) not in reference)
    need(set(new) == set(tasks)-old and not set(new) & old, 'every map outside FULL-CHECK is new in PR6030')
    covered = [t for t in tasks if json.dumps(list(t)) in reference]
    moves = [t for t in covered if t[0] == 'move']
    adapters = [t for t in covered if t[0] in ('main_in', 'main_out')]
    chosen = tasks if full else sorted(set(new) | {t for t in covered if t[0] == 'helper'} | set(adapters[::8]) | set(moves[::64]))
    if jobs > 1:
        with Pool(jobs, initializer=_init, initargs=(words['6030']['frames'],)) as pool:
            done = pool.map(dense_task, chosen, chunksize=4)
    else:
        _init(words['6030']['frames'])
        done = [dense_task(t) for t in chosen]
    done = [json.loads(json.dumps(d)) for d in done]
    fresh = {json.dumps(d[0]): d for d in done if json.dumps(d[0]) not in reference}
    need(sorted(fresh) == sorted(json.dumps(list(t)) for t in new), 'every new map computed')
    for d in done:
        k = json.dumps(d[0])
        if k in reference:
            need(reference[k] == d, 'matrix digest equals predecessor FULL-CHECK for '+k)
    newmaps = HERE/'NEW-MAPS.json'
    if newmaps.exists() and '--write' not in sys.argv:
        need(read(newmaps)['maps'] == sorted(fresh.values()), 'new-map digests equal NEW-MAPS.json')
    # rejection controls on a new map
    _init(words['6030']['frames'])
    C, V, D, F = _M['C'], _M['V'], _M['D'], _M['F']
    nm = [t for t in new if t[0] in ('move', 'helper') and abs(len(F[t[1]])-len(F[t[2]])) > 0]
    _, a, b, _ = nm[0]
    rec, _ = C.lower_child(C.canonical_frame(9, tuple(F[a])).adjoint().then(C.canonical_frame(9, tuple(F[b]))))
    actual, expected = V.recipe(rec), V.adjoint(V.frame(F[a], 9))+V.frame(F[b], 9)
    fault = actual+(('phase', 1),)
    need(V.tableau(fault) == V.tableau(actual) and D.first_difference(fault, expected) is not None, 'phase-only fault rejected densely')
    flipped = list(actual)
    i = next(i for i, g in enumerate(flipped) if g[0] == 'C')
    flipped[i] = ('C', flipped[i][1], -flipped[i][2])
    need(D.first_difference(tuple(flipped), expected) is not None, 'wrong child sign rejected')
    signed = len({(t[1], t[2]) for t in tasks if t[0] in ('move', 'helper')})
    an = read(P30/'RESULT.json')['native']
    w = words['6030']
    need([signed, 2*(w['public']-2*len(w['live'])), 2*len(w['live'])] == [an['distinct_maps'], an['helper_normalizers'], an['main_adapters']],
         'distinct signed maps, helper normalizers and main adapters equal the author native block')
    out = {'tasks': len(tasks), 'distinct_moves': nmoves, 'distinct_helper_pairs': nhelpers, 'distinct_signed_maps': signed,
           'covered_by_predecessor_full_check': len(covered), 'new_in_pr6030': [d[0]+[d[1]] for d in sorted(fresh.values())],
           'control_map': [a, b], 'controls': {'phase_only_fault': 'rejected', 'wrong_child_sign': 'rejected'},
           'predecessor_full_check_sha256': sha256((PRED/'FULL-CHECK.json').read_bytes()).hexdigest()}
    log('L3_dense', checked=len(done), of=len(tasks), new=len(new), full=full)
    return out, sorted(fresh.values())


def tamper_controls(words):
    """Each mutated PR6030 word must be rejected by the own replay or the declared delta."""
    from copy import deepcopy
    w0, w1 = words['5907'], words['6030']

    def first(w, op, r):
        return next(i for i, e in enumerate(w['program']) if e[0] == op and e[1] == r)

    def flip(w):
        e = w['program'][first(w, 'ADD', 268)]; e[-2] = str(-Q(e[-2]))

    def drop(w):
        del w['program'][first(w, 'ADD', 470)]

    def third(w):
        e = next(x for x in w['program'] if x[0] == 'SCALE'); e[-2] = str(Q(e[-2])/3)

    def restore(w):
        w['final'][115] = 105

    def rung(w):  # put back helper 470's frame-593 rung by retargeting its first MOVE
        e = w['program'][first(w, 'MOVE', 470)]; e[3] = 593
    out, quiet = {}, globals()['log']
    globals()['log'] = lambda *a, **k: None
    try:
        for name, mut in (('flip_add_sign_helper268', flip), ('drop_add_into_helper470', drop), ('scale_by_one_third', third),
                          ('restore_final_115_chart', restore), ('retarget_helper470_move_to_593', rung)):
            w = deepcopy(w1); mut(w)
            try:
                layer1({'5907': w0, '6030': w}); out[name] = 'ACCEPTED'
            except ValueError as e:
                out[name] = 'rejected: '+str(e).split(':')[0]
    finally:
        globals()['log'] = quiet
    need(all(v.startswith('rejected') for v in out.values()), 'tamper controls %s' % out)
    log('L1_controls', **out)
    return out


def main():
    full = '--full' in sys.argv
    jobs = int(sys.argv[sys.argv.index('--jobs')+1]) if '--jobs' in sys.argv else 1
    authenticate()
    words = {'5907': read(P07/'WORD.json.gz'), '6030': read(P30/'WORD.json.gz')}
    results = {'5907': read(P07/'RESULT.json'), '6030': read(P30/'RESULT.json')}
    out = {'layer0_sources': layer0()}
    out['layer1_replay'], rp = layer1(words)
    out['layer1_replay']['tamper_controls'] = tamper_controls(words)
    out['layer2_invoice'] = layer2(rp, results)
    out['layer4_funding'] = layer4(results)
    out['layer3_dense'], fresh = layer3(words, full, jobs)
    if '--write' in sys.argv:
        (HERE/'NEW-MAPS.json').write_text(json.dumps({'schema': 'p104-6030-new-dense-maps/1', 'maps': fresh}, separators=(',', ':'))+'\n')
    out['layer3_dense']['new_maps_sha256'] = sha256((HERE/'NEW-MAPS.json').read_bytes()).hexdigest()
    out['mode'] = 'full' if full else 'subset'
    out = json.loads(json.dumps(out, sort_keys=True, default=str))
    out.pop('mode')
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(out, indent=1, sort_keys=True)+'\n')
    else:
        need(out == read(HERE/'RESULT.json'), 'complete result equals RESULT.json')
    print('PASS_P104_6030_INDEPENDENT_AUDIT', 'full' if full else 'subset')


if __name__ == '__main__':
    main()
