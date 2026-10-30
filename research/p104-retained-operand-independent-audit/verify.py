#!/usr/bin/env python3
"""Independent replay, delta, invoice, dense native and funding audit of PR6144 and PR6167.  Apache-2.0.

PR6144 (DreamingOfClouds, research/p104-root-relay-descent-2) lets owned registers 770, 771 and 772 descend
through the frames of helpers 705, 706 and 731 in PR6030's P104 word.  PR6167 (Ali Romman,
research/p104-retained-operand-descent) then retains helper 228's operand in a new lifetime of 770 and removes
one stop of root 772.  Python 3.12, standard library only.

The replay, invoice and dense-comparison functions are imported unchanged from Matarener's PR5827/PR5907 audit
(research/p104-unread-rung-independent-audit/verify.py, PR5960), the same functions the PR6030 audits use.
Nothing is imported from the PR6144 or PR6167 packages except their data files and, in layer 0 only, PR6144's
construct.py.  PR6167's five replacements are re-applied here from its PROOF.md, without its construct.py.
Layers (canonical main contains all three packages):
  0. sources: pinned predecessor words, archives and pricing equal canonical main; both words regenerate;
  1. own exact replay of the PR6030, PR6144 and PR6167 words and the exact deltas of both steps: unchanged fields
     and boundaries, exactly the declared itineraries, owned-operation multisets, paid and helper rank deltas,
     signed per-LOCAL margin changes; tamper controls on both new words;
  2. own invoice recount from the physical caller events and the closed formula, against complete_cost;
  3. dense all-column absolute-phase comparison of every native operator in the PR6144 and PR6167 inventories
     that is not in PR5960's FULL-CHECK.json or the PR6030 audit's NEW-MAPS.json, plus a fixed subset of the old
     ones matched against those digests; --full [--jobs N] recomputes both inventories completely;
  4. own 80-digit decimal interval engine: raw crossings, tested savings, tail ratios, uniqueness, failure of
     each predecessor invoice at the successor claim, and the integer compiler-threshold checks.
"""
from collections import Counter
from copy import deepcopy
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from hashlib import sha256
from multiprocessing import Pool
from pathlib import Path
import gzip, importlib.util, json, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P30 = ROOT/'research/p104-helper470-twin-rung-removal'
P44 = ROOT/'research/p104-root-relay-descent-2'
P67 = ROOT/'research/p104-retained-operand-descent'
PRED = ROOT/'research/p104-unread-rung-independent-audit'
A30 = ROOT/'research/p104-6030-independent-audit'
PACK = {'6030': P30, '6144': P44, '6167': P67}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = _load('a6167_pr5960', PRED/'verify.py')
need, read, replay, diff, invoice = M.need, M.read, M.replay, M.diff, M.invoice


def log(kind, **data):
    print(kind, json.dumps(data, sort_keys=True, default=str)[:300], flush=True)


M.log = log


def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin '+row['path'])


# ---------------------------------------------------------------- layer 0
PR6167_REPLACEMENTS = {  # PR6167 PROOF.md, "The new word"; positions in the PR6144 word
    12913: (['MOVE', 451, 3, 737, False], [['MOVE', 451, 3, 595, False]]),
    12918: (['ADD', 451, 228, '1', 737], [['INIT', 770, 737], ['COPY', 770, 228, '1', 737]]),
    13486: (['MOVE', 772, 520, 737, True], []),
    13487: (['ADD', 451, 772, '-4', 737], []),
    13488: (['MOVE', 772, 737, 595, True], [['MOVE', 772, 520, 595, True], ['ADD', 451, 772, '-4', 595],
                                            ['MOVE', 451, 595, 737, False], ['ADD', 451, 770, '1', 737],
                                            ['CLEAR', 770, 737]]),
}


def payload(w):
    return (json.dumps(w, sort_keys=True, indent=2)+'\n').encode()


def apply6167(base):
    word, program = deepcopy(base), []
    for i, e in enumerate(base['program']):
        if i in PR6167_REPLACEMENTS:
            old, new = PR6167_REPLACEMENTS[i]
            need(e == old, 'PR6167 source event %d' % i)
            program.extend(deepcopy(new))
        else:
            program.append(deepcopy(e))
    word['program'] = program
    return word


def layer0(words):
    same = lambda a, b: gzip.decompress(a.read_bytes()) == gzip.decompress(b.read_bytes())
    need(same(P44/'inputs/pr6030-WORD.json.gz', P30/'WORD.json.gz'), 'PR6144 pinned PR6030 word equals canonical payload')
    need(same(P67/'inputs/pr6144-WORD.json.gz', P44/'WORD.json.gz'), 'PR6167 pinned PR6144 word equals canonical payload')
    need((P67/'inputs/pr6144-pricing.py').read_bytes() == (P44/'pricing.py').read_bytes(), 'PR6167 pinned PR6144 pricing')
    tars = {(P/'inputs/pr5827-source.tar').read_bytes() for P in (P30, P44, P67)}
    need(len(tars) == 1, 'one PR5827 archive across PR6030, PR6144 and PR6167')
    K = _load('a6167_construct6144', P44/'construct.py')
    rebuilt = K.construct(words['6030'], read(P44/'EDIT.json.gz'))
    need(payload(rebuilt) == gzip.decompress((P44/'WORD.json.gz').read_bytes()), 'regenerated PR6144 word equals the shipped payload')
    own = apply6167(words['6144'])
    need(payload(own) == gzip.decompress((P67/'WORD.json.gz').read_bytes()), 'PR6167 PROOF.md replacements give the shipped payload')
    out = {'pinned_pr6030_word_equal_canonical': True, 'pinned_pr6144_word_and_pricing_equal_canonical': True,
           'pr5827_archive_identical_in_three_packages': True, 'pr6144_regenerated_by_its_construct': True,
           'pr6167_regenerated_from_proof_replacements_without_its_construct': True,
           'pr5827_archive_sha256': sha256(tars.pop()).hexdigest()}
    log('L0', **out)
    return out


# ---------------------------------------------------------------- layer 1: own replay and deltas
def itineraries(w):
    n = w['public']
    it = {r: [w['initial'][r] if r < n else None] for r in range(n+w['owned_fields'])}
    for e in w['program']:
        if e[0] == 'MOVE':
            it[e[1]].append(e[3])
        elif e[0] == 'INIT':
            it[e[1]].append(['INIT', e[2]])
    return it


STEPS = {
    '6144': {  # PR6144 README, "The edit"
        'base': '6030',
        'itineraries': {
            '705': [[3, 593, 1047, 553, 549], [3, 549]],
            '706': [[3, 594, 117, 534, 541], [3, 541]],
            '731': [[3, 595, 737, 520, 529], [3, 529]],
            '732': [[3, 594, 117, 222, 127], [3, 117, 222, 127]],
            '770': [[None, ['INIT', 549], 593], [None, ['INIT', 549], 553, 1047, 593]],
            '771': [[None, ['INIT', 541], 594], [None, ['INIT', 541], 534, 117, 594]],
            '772': [[None, ['INIT', 529], 595], [None, ['INIT', 529], 520, 737, 595]]},
        'owned_ops_added': {},
        'paid_delta': {'1': -4, '4': -1, '5': 1, '6': -3, '7': 3},
        'margin': {1: 4, 4: 1, 5: -1, 6: 3, 7: -3},
        'ops_delta': {'ADD': 19, 'MOVE': -4},
        'events': 22818, 'inventory': [770, 29, 31, 13]},
    '6167': {  # PR6167 PROOF.md
        'base': '6144',
        'itineraries': {
            '451': [[3, 737, 738, 911, 127], [3, 595, 737, 738, 911, 127]],
            '770': [[None, ['INIT', 549], 553, 1047, 593], [None, ['INIT', 737], ['INIT', 549], 553, 1047, 593]],
            '772': [[None, ['INIT', 529], 520, 737, 595], [None, ['INIT', 529], 520, 595]]},
        'owned_ops_added': {'INIT': ['INIT', 770, 737], 'COPY': ['COPY', 770, 228, '1', 737], 'CLEAR': ['CLEAR', 770, 737]},
        'paid_delta': {'1': 1, '2': -1, '4': -1, '5': 1},
        'margin': {2: 1, 4: 1, 1: -1, 5: -1},
        'ops_delta': {'CLEAR': 1, 'COPY': 1, 'INIT': 1},
        'events': 22821, 'inventory': [770, 29, 32, 13]},
}


def margin_positive(m):
    """sum_r c_r r^t > 0 for every 0 < t < 1, by Karamata: pad the negative ranks with zeros (0^t = 0); if the
    positive ranks are majorized by the negative ones, are not a permutation of them and have the same sum, strict
    concavity of x^t gives sum H(pos) > sum H(neg)."""
    pos = sorted((r for r, c in m.items() if c > 0 for _ in range(c)), reverse=True)
    neg = sorted((r for r, c in m.items() if c < 0 for _ in range(-c)), reverse=True)
    size = max(len(pos), len(neg))
    pos, neg = pos+[0]*(size-len(pos)), neg+[0]*(size-len(neg))
    need(sum(pos) == sum(neg) and pos != neg, 'equal rank mass, different profiles')
    need(all(sum(pos[:i]) <= sum(neg[:i]) for i in range(1, size+1)), 'positive ranks majorized by negative ranks')
    for k in range(1, 1000):  # numerical corroboration on a grid
        t = k/1000
        need(sum(c*r**t for r, c in m.items()) > 0, 'margin positive at t=%s' % t)
    return {'positive': [r for r in pos if r], 'negative': [r for r in neg if r]}


def step_delta(words, rp, new):
    s = STEPS[new]
    w0, w1 = words[s['base']], words[new]
    need(w0.keys() == w1.keys(), 'same word fields')
    need(all(w0[k] == w1[k] for k in w0 if k != 'program'), 'frames, ports, live, sizes and boundary charts unchanged')
    i0, i1 = itineraries(w0), itineraries(w1)
    changed = {str(r): [i0[r], i1[r]] for r in i0 if i0[r] != i1[r]}
    need(changed == s['itineraries'], 'exactly the declared itineraries change: %s' % changed)
    ms = lambda w, keep: Counter(json.dumps(e) for e in w['program'] if keep(e))
    for op in ('INIT', 'CLEAR', 'COPY', 'SCALE'):
        c = ms(w1, lambda e: e[0] == op); c.subtract(ms(w0, lambda e: e[0] == op))
        want = Counter({json.dumps(s['owned_ops_added'][op]): 1}) if op in s['owned_ops_added'] else Counter()
        need(+c == want and not -c, op+' events change exactly as declared')
    other = lambda e: e[0] == 'MOVE' and str(e[1]) not in s['itineraries']
    need(ms(w0, other) == ms(w1, other), 'every MOVE outside the declared itineraries unchanged as a multiset')
    d, h = diff(rp[new][0], rp[s['base']][0]), diff(rp[new][1], rp[s['base']][1])
    need(d == s['paid_delta'] and h == {}, 'paid and helper deltas %s %s' % (d, h))
    margin = Counter({int(k): -v for k, v in d.items()})
    margin = {k: v for k, v in margin.items() if v}
    need(margin == s['margin'], 'per-LOCAL margin change %s' % margin)
    karamata = margin_positive(margin)
    ops = diff(Counter(e[0] for e in w1['program']), Counter(e[0] for e in w0['program']))
    need(ops == s['ops_delta'], 'operation counts change as declared: %s' % ops)
    o = rp[new][3]
    need(len(w1['program']) == s['events'] <= 26000, 'event count and cap')
    need([o['public'], o['owned_fields'], o['owned_lifetimes'], o['peak_owned']] == s['inventory'], 'storage inventory')
    adds = ms(w1, lambda e: e[0] == 'ADD'); adds.subtract(ms(w0, lambda e: e[0] == 'ADD'))
    seq = lambda w: {r: [json.dumps(e) for e in w['program'] if e[1] == r or (e[0] in ('ADD', 'COPY') and e[2] == r)]
                     for r in range(w['public']+w['owned_fields'])}
    s0, s1 = seq(w0), seq(w1)
    out = {'itineraries': changed, 'paid_delta': d, 'helper_delta': h,
           'margin_delta_per_local': {str(k): v for k, v in sorted(margin.items()) if v}, 'margin_positive_on_0_1_by_karamata': karamata,
           'ops_delta': ops, 'add_events_removed_added': [-sum((-adds).values()), sum((+adds).values())],
           'events': [len(w0['program']), len(w1['program'])],
           'registers_with_changed_event_sequence': sorted(r for r in s0 if s0[r] != s1[r])}
    log('L1_delta_'+new, **out)
    return out


def layer1(words):
    rp = {k: replay(w, k) for k, w in words.items()}
    res = {k: rp[k][3] for k in rp}
    for k, P in PACK.items():
        a, o = read(P/'RESULT.json')['local'], res[k]
        need([a['paid'], a['helpers'], a['paid_rank_mass'], a['public_inputs'], a['owned_fields'], a['owned_lifetimes'], a['peak_owned_fields']] ==
             [o['paid'], o['helpers'], o['paid_rank_mass'], o['public'], o['owned_fields'], o['owned_lifetimes'], o['peak_owned']],
             'own replay statistics equal author local block '+k)
    for new in STEPS:
        res['delta_'+STEPS[new]['base']+'_'+new] = step_delta(words, rp, new)
    return res, rp


def tamper_controls(words):
    """Mutated PR6144 / PR6167 words must be rejected by the own replay."""
    def at(w, ev):
        return w['program'].index(ev)

    def rm(ev):
        return lambda w: w['program'].pop(at(w, ev))

    def sign(ev):
        def f(w):
            e = w['program'][at(w, ev)]; e[-2] = str(-Q(e[-2]))
        return f

    def swap_later(ev, after):  # move an event to just after another one
        def f(w):
            e = w['program'].pop(at(w, ev)); w['program'].insert(at(w, after)+1, e)
        return f

    def relay_back_705(w):  # give helper 705 its PR6030 first hop back
        w['program'][next(i for i, e in enumerate(w['program']) if e[:2] == ['MOVE', 705])][3] = 593
    cases = {
        '6144': [('drop_root770_descent_move', rm(next(e for e in words['6144']['program'] if e[:4] == ['MOVE', 770, 549, 553]))),
                 ('flip_first_read_of_771', sign(next(e for e in words['6144']['program'] if e[0] == 'ADD' and e[2] == 771))),
                 ('relay_hop_705_restored', relay_back_705)],
        '6167': [('drop_cache_copy', rm(['COPY', 770, 228, '1', 737])),
                 ('flip_cache_copy_sign', sign(['COPY', 770, 228, '1', 737])),
                 ('drop_late_operand', rm(['ADD', 451, 770, '1', 737])),
                 ('drop_cache_clear', rm(['CLEAR', 770, 737])),
                 ('root_coefficient_-2', lambda w: w['program'][at(w, ['ADD', 451, 772, '-4', 595])].__setitem__(3, '-2')),
                 ('copy_after_helper228_leaves_737', swap_later(['COPY', 770, 228, '1', 737],
                                                                next(e for e in words['6167']['program'][12919:] if e[:2] == ['MOVE', 228])))],
    }
    out, quiet = {}, M.log
    M.log = lambda *a, **k: None
    try:
        for k, muts in cases.items():
            for name, mut in muts:
                w = deepcopy(words[k]); mut(w)
                try:
                    replay(w, 'tamper'); out[k+'_'+name] = 'ACCEPTED'
                except (ValueError, IndexError) as e:
                    out[k+'_'+name] = 'rejected: '+str(e).split(':')[0]
    finally:
        M.log = quiet
    need(all(v.startswith('rejected') for v in out.values()), 'tamper controls %s' % out)
    log('L1_controls', **out)
    return out


# ---------------------------------------------------------------- layer 2: invoice
def layer2(rp, results):
    out = {}
    for k in PACK:
        P, T = invoice(rp[k][0], rp[k][1])
        cost = results[k]['complete_cost']
        AP = Counter({int(r): v for r, v in cost['paid'].items()}); AT = Counter({int(r): v for r, v in cost['targets'].items()})
        need((+P, +T) == (+AP, +AT), 'own invoice equals author complete_cost for '+k)
        surplus = sum(r*v for r, v in T.items())-sum(r*v for r, v in P.items())
        out[k] = {'paid_calls': sum(P.values()), 'productive_fields': sum(T.values()), 'rank_mass_surplus': surplus,
                  'paid_rank_mass': sum(r*v for r, v in P.items()), 'max_paid_rank': max(P), 'max_target_rank': max(T)}
        need([out[k]['paid_calls'], out[k]['productive_fields'], surplus] == [cost['paid_calls'], cost['productive_fields'], cost['rank_mass_surplus']],
             'headline invoice '+k)
        log('L2_invoice', word=k, **out[k])
    need(out['6144']['paid_calls'] == out['6167']['paid_calls'] == 66762 and out['6030']['paid_calls'] == 66834, 'paid call counts')
    return out


# ---------------------------------------------------------------- layer 4: funding
def dec(x):
    x = Q(x)
    return Decimal(x.numerator)/Decimal(x.denominator)


def margin_fn(cost):
    pad = Decimal(10)**-70

    def margin(kap):
        t, lo, hi = 1-kap, Decimal(0), Decimal(0)
        for r, n in cost['targets'].items():
            v = (t*Decimal(int(r)).ln()).exp(); lo += n*v*(1-pad); hi += n*v*(1+pad)
        for r, n in cost['paid'].items():
            v = (t*Decimal(int(r)).ln()).exp(); lo -= n*v*(1+pad); hi -= n*v*(1-pad)
        return lo, hi
    return margin


def layer4(results):
    getcontext().prec = 80
    out = {}
    for k in PACK:
        cost = results[k]['complete_cost']
        margin = margin_fn(cost)
        lo, hi, grid = 0, 10**12, 10**14
        while hi-lo > 1:
            m = (lo+hi)//2
            if margin(Decimal(m)/grid)[0] > 0:
                lo = m
            else:
                hi = m
        need(margin(Decimal(lo)/grid)[0] > 0 and margin(Decimal(hi)/grid)[1] < 0, 'strict crossing '+k)
        need([Q(lo, grid), Q(hi, grid)] == [Q(x) for x in cost['raw_root_interval']], 'crossing equals author interval '+k)
        claim, tested = Q(cost['kappa']), Q(cost['strictification']['tested'])
        need(claim < tested < Q(lo, grid) and margin(dec(tested))[0] > 0, 'claim < tested < crossing, tested positive '+k)
        st = cost['strictification']
        need(Q(st['tail_offset']) == Q(1, 7) and int(st['cutoff']) == 16 and int(st['floor']) == 17, 'strictification constants '+k)
        pw = lambda r, x: (x*Decimal(int(r)).ln()).exp()
        t, u = 1-dec(tested), Decimal(1)/7
        MT = sum(n*pw(r, t) for r, n in cost['targets'].items())
        MP = sum(n*pw(r, t) for r, n in cost['paid'].items())
        MPu = sum(n*pw(r, t+u) for r, n in cost['paid'].items())
        alpha, gamma = MP/MT, MPu/(pw(16, u)*MT)
        delta = sum(cost['targets'].values())*17/(pw(16, dec(tested))*MT)
        lim = Decimal(125)/128
        need(alpha < 1-Decimal(10)**-12 and gamma < lim and delta < lim, 'tail ratios '+k)
        dmax = Decimal(0)
        for side, sgn in (('targets', -1), ('paid', 1)):
            for r, n in cost[side].items():
                dmax += sgn*n*Decimal(int(r)).ln()*(pw(r, 1-Decimal('0.0034')) if sgn < 0 else pw(r, Decimal(1)))
        need(dmax < 0, 'raw margin strictly decreasing on [0,.0034] '+k)
        # integer compiler-threshold checks (same statements as the PR6030 admission review)
        c = cost['compiler']
        gap = (tested-claim)/7
        H, j = int(c['H']), int(c['integer_test_exponent'])
        need(Q(c['gap']) == gap and gap.numerator == 1 and H == gap.denominator*j, 'threshold grid '+k)
        need((H+1)**1024 < 2**j and (gap.denominator*(j-1)+1)**1024 >= 2**(j-1), 'threshold and predecessor '+k)
        out[k] = {'raw_crossing': [str(Q(lo, grid)), str(Q(hi, grid))], 'raw_crossing_decimal': [str(Decimal(lo)/grid), str(Decimal(hi)/grid)],
                  'claim': str(claim), 'tested': str(tested), 'tested_positive': True, 'equals_author': True,
                  'alpha': str(alpha)[:22], 'gamma': str(gamma)[:22], 'delta': str(delta)[:22], 'derivative_upper': str(dmax)[:22],
                  'compiler_threshold_checked': True}
        log('L4_funding', word=k, **out[k])
    need(Q(125, 128)**128 < Q(1, 16) and 1/(1+1024*Q(1, 10**12))+Q(4, 2**32) < 1, 'decay block and completion')
    need(16**64 < 17**63 and 2*(16**1024)**64 <= (145**1024)**63, 'splitting and complement')
    for new in STEPS:
        old = STEPS[new]['base']
        claim = dec(results[new]['complete_cost']['kappa'])
        upper = margin_fn(results[old]['complete_cost'])(claim)[1]
        need(upper < 0, 'predecessor %s invoice fails at the %s claim' % (old, new))
        g = Q(results[new]['complete_cost']['kappa'])-Q(results[old]['complete_cost']['kappa'])
        out['step_'+new] = {'predecessor_margin_upper_at_claim': str(upper)[:24], 'claim_gain': str(g)}
        log('L4_step', step=new, **out['step_'+new])
    return out


# ---------------------------------------------------------------- layer 3: dense native
def layer3(words, full, jobs):
    need(words['6030']['frames'] == words['6144']['frames'] == words['6167']['frames'], 'shared frame table')
    inv = {k: M.inventory(words[k]) for k in PACK}
    tasks = sorted(inv['6144'][0] | inv['6167'][0])
    reference = {json.dumps(d[0]): d for d in read(PRED/'FULL-CHECK.json')['maps']+read(A30/'NEW-MAPS.json')['maps']}
    new = sorted(t for t in tasks if json.dumps(list(t)) not in reference)
    need(not set(new) & inv['6030'][0], 'every map outside the reference digests is new after PR6030')
    covered = [t for t in tasks if json.dumps(list(t)) in reference]
    moves = [t for t in covered if t[0] == 'move']
    adapters = [t for t in covered if t[0] in ('main_in', 'main_out')]
    chosen = tasks if full else sorted(set(new) | {t for t in covered if t[0] == 'helper'} | set(adapters[::8]) | set(moves[::64]))
    if jobs > 1:
        with Pool(jobs, initializer=M._init, initargs=(words['6167']['frames'],)) as pool:
            done = pool.map(M.dense_task, chosen, chunksize=4)
    else:
        M._init(words['6167']['frames'])
        done = [M.dense_task(t) for t in chosen]
    done = [json.loads(json.dumps(d)) for d in done]
    fresh = {json.dumps(d[0]): d for d in done if json.dumps(d[0]) not in reference}
    need(sorted(fresh) == sorted(json.dumps(list(t)) for t in new), 'every new map computed')
    for d in done:
        k = json.dumps(d[0])
        if k in reference:
            need(reference[k] == d, 'matrix digest equals reference digest for '+k)
    newmaps = HERE/'NEW-MAPS.json'
    if newmaps.exists() and '--write' not in sys.argv:
        need(read(newmaps)['maps'] == sorted(fresh.values()), 'new-map digests equal NEW-MAPS.json')
    M._init(words['6167']['frames'])
    C, V, D, F = M._M['C'], M._M['V'], M._M['D'], M._M['F']
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
    native = {}
    for k in ('6144', '6167'):
        w, an = words[k], read(PACK[k]/'RESULT.json')['native']
        signed = len({(t[1], t[2]) for t in inv[k][0] if t[0] in ('move', 'helper')})
        need([signed, 2*(w['public']-2*len(w['live'])), 2*len(w['live'])] == [an['distinct_maps'], an['helper_normalizers'], an['main_adapters']],
             'distinct signed maps, helper normalizers and main adapters equal the author native block '+k)
        native[k] = {'tasks': len(inv[k][0]), 'distinct_moves': inv[k][1], 'distinct_helper_pairs': inv[k][2], 'distinct_signed_maps': signed}
    out = {'per_word': native, 'union_tasks': len(tasks), 'covered_by_reference_digests': len(covered),
           'new_after_pr6030': [d[0]+[d[1]] for d in sorted(fresh.values())],
           'new_in': {k: sorted(json.dumps(list(t)) for t in new if t in inv[k][0]) for k in ('6144', '6167')},
           'control_map': [a, b], 'controls': {'phase_only_fault': 'rejected', 'wrong_child_sign': 'rejected'},
           'reference_sha256': {'pr5960_full_check': sha256((PRED/'FULL-CHECK.json').read_bytes()).hexdigest(),
                                'pr6030_audit_new_maps': sha256((A30/'NEW-MAPS.json').read_bytes()).hexdigest()}}
    log('L3_dense', checked=len(done), of=len(tasks), new=len(new), full=full)
    return out, sorted(fresh.values())


def main():
    full = '--full' in sys.argv
    jobs = int(sys.argv[sys.argv.index('--jobs')+1]) if '--jobs' in sys.argv else 1
    authenticate()
    words = {k: read(P/'WORD.json.gz') for k, P in PACK.items()}
    results = {k: read(P/'RESULT.json') for k, P in PACK.items()}
    out = {'layer0_sources': layer0(words)}
    out['layer1_replay'], rp = layer1(words)
    out['layer1_replay']['tamper_controls'] = tamper_controls(words)
    out['layer2_invoice'] = layer2(rp, results)
    out['layer4_funding'] = layer4(results)
    if '--no-dense' in sys.argv:
        print('PASS layers 0, 1, 2, 4 (dense layer skipped)')
        return
    out['layer3_dense'], fresh = layer3(words, full, jobs)
    if '--write' in sys.argv:
        (HERE/'NEW-MAPS.json').write_text(json.dumps({'schema': 'p104-6144-6167-new-dense-maps/1', 'maps': fresh}, separators=(',', ':'))+'\n')
    out['layer3_dense']['new_maps_sha256'] = sha256((HERE/'NEW-MAPS.json').read_bytes()).hexdigest()
    out = json.loads(json.dumps(out, sort_keys=True, default=str))
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(out, indent=1, sort_keys=True)+'\n')
    else:
        need(out == read(HERE/'RESULT.json'), 'complete result equals RESULT.json')
    print('PASS_P104_6144_6167_INDEPENDENT_AUDIT', 'full' if full else 'subset')


if __name__ == '__main__':
    main()
