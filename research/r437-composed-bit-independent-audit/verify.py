"""Independent exact word-level audit of PR #3647's composed R437 bit word.

Usage (repository root):  python3 -I -B research/r437-composed-bit-independent-audit/verify.py [--write]

Inputs: from main, the selected #589 word, its selection9-p111.json hosting patterns and #1043's
FRAME-PATHS.json and CERTIFICATE.json; from PR #3647, the R438 (helper464 GL) word, the R437 word,
the R437 record stream and the hosted template, vendored under inputs/ (all sha256-pinned in
SOURCES.json).
Semantics: wordsem.py, records.py, hosting.py and price.py, written for this audit from the
selected #589 chain's sources on main (see README); nothing from PR #3647, #1043 or main is imported.
Without --write the computed result must equal the committed RESULT.json.
Standard library only.  Sagar Thakrar (thakrarsagar), with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
import collections
import copy
import gzip
import hashlib
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from wordsem import (Geometry, Reject, bits, canonical, check_final_frames, check_identity,  # noqa: E402
                     check_pullback, forward, load, need, paths, profile, pullback, rebuild_DC,
                     reverse_orientation)
import compose  # noqa: E402
import hosting  # noqa: E402
import native  # noqa: E402
import price  # noqa: E402
import records  # noqa: E402
from compose import apply  # noqa: E402

W589 = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PATHS1043 = 'research/bit-boundary-persistence/FRAME-PATHS.json'
R438 = 'research/r437-composed-bit-independent-audit/inputs/FINAL-R438-WORD.json.gz'
R437 = 'research/r437-composed-bit-independent-audit/inputs/R437-COMPOSED-WORD.json.gz'
RECORDS = 'research/r437-composed-bit-independent-audit/inputs/R437-RECORDS.bin.gz'
TEMPLATE = 'research/r437-composed-bit-independent-audit/inputs/R437-GLOBAL-TEMPLATE.json.gz'
SEL589 = 'research/e8-bit-p111-tuned/data/selection9-p111.json'
CERT1043 = 'research/bit-boundary-persistence/CERTIFICATE.json'
C_R437 = (868314126713557740143, 500000000000000000000000)
C_589 = (1733427039589844234749, 10**24)
C_1043 = (433544072119966441673, 250000000000000000000000)


def sha(path):
    with open(os.path.join(ROOT, path), 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def pins():
    src = json.load(open(os.path.join(HERE, 'SOURCES.json')))
    out = {}
    for f in src['files'] + src['snapshot']:
        path = f.get('path') or 'research/r437-composed-bit-independent-audit/' + f['local']
        if f.get('usage', 'input') == 'input' or 'local' in f:
            need(sha(path) == f['sha256'], 'pin mismatch for %s' % path)
            out[path] = f['sha256']
    return out


def adds(w):
    c = {s: sum(len(g[2]) for g in w[s]) for s in 'DABC'}
    c['scatter'] = sum(len(r) for r in w['scatter'])
    c['total'] = sum(c.values())
    return c


def interface(w, geo):
    """Hypotheses of the selected interleaved scalar-interface lemma (H1-H5) and its conclusion."""
    v, n = w['v'], 2 * w['v'] + w['R']
    y = lambda r: v <= r < 2 * v
    out = {}
    out['H1'] = not any(not y(g[1]) and any(y(s) for s in g[2]) for sec in 'DABC' for g in w[sec])
    out['H2'] = all(len(w['frames'][g[0]]) == 0 and y(g[1]) and all(s >= 2 * v for s in g[2]) for g in w['D'])
    out['H3'] = (all(not y(g[1]) for g in w['A']) and all(2 * v <= q < n for q in w['ret'])
                 and all(y(g[1]) or all(not y(s) for s in g[2]) for g in w['B']))
    D, C = rebuild_DC(w)
    out['H4_C_literal_reverse'] = C == w['C']
    out['D0_rebuilt'] = D == w['D']
    raw, _, _, _ = forward(w, geo, sections=('A', 'scatter', 'B'), frames_on=False)
    ym, xm = ((1 << v) - 1) << v, (1 << v) - 1
    out['H5_V_identity'] = all(raw[v + t] & ym == 1 << (v + t) for t in range(v))
    out['U_block'] = all(raw[r] & ym == 0 for r in range(n) if not y(r))
    out['J_identity'] = all(raw[v + t] & xm == 1 << t for t in range(v))
    return out


def word_checks(name, w, geo):
    """Primary forward method, reverse pull-back, entrywise agreement, reverse orientation."""
    v, n = w['v'], 2 * w['v'] + w['R']
    val, cur, climbs, copies = forward(w, geo)
    check_final_frames(w, geo)
    bad = check_identity(w, val)
    col = pullback(w)
    badp = check_pullback(w, col)
    agree = all(((val[r] >> j) & 1) == ((col[j] >> r) & 1) for r in range(n) for j in range(n))
    rev = check_identity(w, reverse_orientation(w, geo))
    sw = {s: sum(1 for g in w[s] if g[1] < v) for s in 'DABC'}
    return dict(columns=n, sources=v, helpers=w['R'], forward_bad_columns=len(bad), pullback_bad_columns=len(badp),
                methods_agree_entrywise=agree, reverse_orientation_bad_columns=len(rev),
                copy_ranks=[c[2] for c in copies], profile=profile(geo, climbs, copies),
                mass=sum(k * x for k, x in profile(geo, climbs, copies).items()),
                scalar_adds=adds(w), gates={s: len(w[s]) for s in 'DABC'}, source_writes=sw,
                interface=interface(w, geo)), (val, climbs, copies)


def trace(w, akeys):
    """Per gate (origin key): destination, frame, value after, operand values; C gates are keyed
    by the A/B gate they literally reverse."""
    geo = Geometry(w)
    v = w['v']
    zkeys = [k for sec, ks in (('A', akeys), ('B', [('B', i) for i in range(len(w['B']))]))
             for k, g in zip(ks, w[sec]) if not (v <= g[1] < 2 * v)]
    ckeys = [('C',) + k for k in reversed(zkeys)]
    need(len(ckeys) == len(w['C']), 'C length')
    out, climbs = {}, []
    keymap = {'A': akeys, 'B': [('B', i) for i in range(len(w['B']))], 'C': ckeys}

    def tr(ev, val, cur):
        sec = ev[0]
        if sec in keymap:
            k = keymap[sec][ev[1]]
            out[k] = (ev[3], ev[2], val[ev[3]], tuple(val[s] for s in ev[4]), ev[4])
    _, _, cl, _ = forward(w, geo, trace=tr)
    # A move inside an edited window is dated by the last unchanged gate before it, so that a
    # re-synthesized node is compared window by window and any move across an unchanged gate shows.
    anchor = {}
    for sec in ('A', 'B', 'C'):
        last = None
        for k in keymap[sec]:
            if unchanged(k):
                last = k
                anchor[k] = k
            else:
                anchor[k] = ('window after', last)
    for r, a, b, where in cl:
        if where[0] in keymap:
            climbs.append((r, a, b, anchor[keymap[where[0]][where[1]]]))
        else:
            climbs.append((r, a, b, where))
    return out, climbs


EDITED_589_A = {compose.E464_DEL, compose.E470_DEL, compose.E470_READ} | set(range(*compose.E464_NODE_AT))


def unchanged(k):
    if k[0] == 'C':
        return unchanged(k[1:])
    return k[0] == 'B' or (k[0] == 'A' and k[1] not in EDITED_589_A)


def project(x, dead, ren):
    y = 0
    for b in bits(x):
        if b not in dead:
            y |= 1 << ren(b)
    return y


def compare(T0, T1, dead, ren, v):
    """Aligned trace comparison of a control/edited word (T1) against a reference (T0)."""
    clean = (1 << (2 * v)) - 1
    full_diff, clean_diff, dirt_cols, sw = [], [], set(), 0
    common = [k for k in T1 if k in T0]
    for k in common:
        d0, f0, x0, s0, r0 = T0[k]
        d1, f1, x1, s1, r1 = T1[k]
        need(ren(d0) == d1 and f0 == f1 and [ren(r) for r in r0] == list(r1), 'aligned gate %s differs in shape' % (k,))
        a = [project(x0, dead, ren)] + [project(s, dead, ren) for s in s0]
        b = [x1] + list(s1)
        if a != b:
            full_diff.append(k)
            for p, q in zip(a, b):
                dirt_cols |= set(bits(p ^ q))
        if [p & clean for p in a] != [q & clean for q in b]:
            clean_diff.append(k)
        if d1 < v:
            sw += 1
    return dict(aligned_gates=len(common), full_value_differences=sorted(full_diff, key=str),
                clean_value_differences=len(clean_diff), differing_columns=sorted(dirt_cols),
                source_write_gates_compared=sw)


def source_history(T, climbs, v):
    acc = {s: [] for s in range(v)}
    for k, (d, f, _, _, regs) in T.items():
        if k[0] == 'C':
            continue
        if d < v:
            acc[d].append((str(k), f, 'write'))
        for s in regs:
            if s < v:
                acc[s].append((str(k), f, 'read'))
    cl = {s: [(str(k), a, b) for r, a, b, k in climbs if r == s] for s in range(v)}
    return acc, cl


def history_diff(h0, h1, v):
    out = {}
    for s in range(v):
        a, b = set(h0[s]), set(h1[s])
        if a != b:
            out[s] = dict(removed=sorted(a - b), added=sorted(b - a))
    return out


def run():
    t0 = time.process_time()
    res = {'status': None, 'pins': pins()}
    w589 = load(os.path.join(ROOT, W589))
    r438 = load(os.path.join(ROOT, R438))
    r437 = load(os.path.join(ROOT, R437))
    fp = json.load(open(os.path.join(ROOT, PATHS1043)))
    v = w589['v']
    geo = Geometry(w589)
    for w in (r438, r437):
        need(all(w[k] == w589[k] for k in ('lines', 'frames', 'scatter', 'v', 'h', 'form', 'format', 'coords',
                                           'ports_geom', 'punctured')), 'geometry or scatter changed')
    res['frame_closure_memberships'] = geo.closure_checks()
    res['frames'] = len(geo.frames)

    # Controls and composition, built literally from selected #589
    node = r438['A'][1985:1995]
    c464, d464, ren464, k464 = apply(w589, node, do464=True)
    c470, d470, ren470, k470 = apply(w589, node, do470=True)
    comp, dcomp, rencomp, kcomp = apply(w589, node, do464=True, do470=True)
    strip = lambda w: {k: x for k, x in w.items() if k != 'stats'}
    res['composition'] = dict(
        e464_node=node,
        c464_equals_pr_R438_except_stats=strip(c464) == strip(r438),
        composed_equals_pr_R437_except_stats=strip(comp) == strip(r437),
        stats_589=w589['stats'], stats_pr_R438=r438['stats'], stats_pr_R437=r437['stats'],
        canonical_sha256=dict(
            w589=hashlib.sha256(canonical(w589)).hexdigest(),
            pr_R438=hashlib.sha256(canonical(r438)).hexdigest(),
            pr_R437=hashlib.sha256(canonical(r437)).hexdigest(),
            c470_rebuilt=hashlib.sha256(canonical(c470)).hexdigest()),
        edit_windows_589_A=dict(e464=[compose.E464_DEL, list(compose.E464_NODE_AT)],
                                e470=[compose.E470_DEL, compose.E470_READ]))

    words = [('selected589', w589), ('C464_pr_R438', r438), ('C470_rebuilt_1043', c470), ('R437_pr', r437)]
    res['words'] = {}
    side = {}
    for name, w in words:
        res['words'][name], side[name] = word_checks(name, w, geo)
    _, cl589, _ = side['selected589']
    # second frame method: exact rational projectors for every climb of the R437 word; the changed
    # paths (receiver 444, SOURCE77, GL node roles 340/241/349) also get the address-exchange identity
    _, cl437, _ = side['R437_pr']
    focus = sorted({(a, b) for r, a, b, _ in cl437 if r in (444, 77, 340, 241, 349)})
    res['native'] = native.check(r437, cl437, geo, focus)
    _, cl470, _ = side['C470_rebuilt_1043']
    res['frame_paths_1043'] = dict(
        selected589_equals_baseline=[p for _, p in sorted(paths(w589, cl589).items())] == fp['baseline'],
        c470_equals_candidate=[p for _, p in sorted(paths(c470, cl470).items())] == fp['candidate'])
    prof = {k: res['words'][k]['profile'] for k, _ in words}
    delta = lambda a, b: {r: prof[a].get(r, 0) - prof[b].get(r, 0) for r in sorted(set(prof[a]) | set(prof[b]))
                          if prof[a].get(r, 0) != prof[b].get(r, 0)}
    d1, d2, d3 = (delta('C464_pr_R438', 'selected589'), delta('C470_rebuilt_1043', 'selected589'),
                  delta('R437_pr', 'selected589'))
    res['profile_delta'] = dict(e464=d1, e470=d2, composed=d3,
                                additive={r: d1.get(r, 0) + d2.get(r, 0) for r in set(d1) | set(d2)
                                          if d1.get(r, 0) + d2.get(r, 0)} == d3,
                                composed_vs_C464=delta('R437_pr', 'C464_pr_R438'))

    # Aligned traces: what each edit changes, and whether the edits interact
    T589, C589 = trace(w589, [('A', i) for i in range(len(w589['A']))])
    T464, C464 = trace(c464, k464)
    T470, C470 = trace(c470, k470)
    T437, C437 = trace(r437, kcomp)
    res['traces'] = dict(
        e464_vs_589=compare(T589, T464, d464, ren464, v),
        e470_vs_589=compare(T589, T470, d470, ren470, v),
        composed_vs_589=compare(T589, T437, dcomp, rencomp, v),
        composed_vs_C464=compare(T464, T437, [469], lambda r: r - (r > 469), v),
        composed_vs_C470=compare(T470, T437, [464], lambda r: r - (r > 464), v))
    # Helper-dirt census of the retained totals at the scatter (the COPY sources), for scale: how
    # much arbitrary dirt each capture already carries in #589, and which columns the edits swap.
    def capture_dirt(w):
        val = forward(w, geo, sections=('D', 'A'), frames_on=False)[0]
        return [(q, [b for b in bits(val[q]) if b >= 2 * v]) for q in w['ret']]
    cd589, cd437 = capture_dirt(w589), capture_dirt(r437)
    need([rencomp(q) for q, _ in cd589] == [q for q, _ in cd437], 'retained totals do not correspond')
    res['capture_dirt'] = dict(
        selected589_columns={q: len(c) for q, c in cd589},
        R437_pr_columns={q: len(c) for q, c in cd437},
        selected589_totals_carrying_deleted_helpers={q: [b for b in c if b in dcomp] for q, c in cd589
                                                     if any(b in dcomp for b in c)},
        changes_vs_589=[dict(total_589=q0, total_R437=q1, deleted_helper_columns_dropped=[b for b in c0 if b in dcomp],
                             removed=sorted(set(rencomp(b) for b in c0 if b not in dcomp) - set(c1)),
                             added=sorted(set(c1) - set(rencomp(b) for b in c0 if b not in dcomp)))
                        for (q0, c0), (q1, c1) in zip(cd589, cd437)
                        if [rencomp(b) for b in c0 if b not in dcomp] != c1])
    # SOURCE77 late read and source chronology
    h589, sc589 = source_history(T589, C589, v)
    h437, sc437 = source_history(T437, C437, v)
    k_new = ('A470', 0)
    d, f, after, (x77,), regs = T437[k_new]
    res['source77'] = dict(
        new_read=dict(frame=f, frame_lines=geo.frames[f], frame_dim=geo.dim[f], receiver=d,
                      source_value_is_clean_input=x77 == 1 << 77),
        source77_climbs_589=[(str(k), a, b) for r, a, b, k in C589 if r == 77],
        source77_climbs_R437=[(str(k), a, b) for r, a, b, k in C437 if r == 77],
        receiver444_climbs_589=[(str(k), a, b) for r, a, b, k in C589 if r == 444],
        receiver444_climbs_R437=[(str(k), a, b) for r, a, b, k in C437 if r == 444])
    res['source_chronology'] = dict(
        all_source_climbs_identical=sc589 == {s: sc437[s] for s in range(v)},
        access_history_differences=history_diff(h589, h437, v))
    # Records consumed by PR #3647's hosting/invoice stage: byte equality with an independent
    # lowering of the audited word, then record replay in both orientations.
    with open(os.path.join(ROOT, RECORDS), 'rb') as fh:
        raw = gzip.decompress(fh.read())
    mine = records.lower(r437, geo)
    theirs = list(struct.iter_unpack('<6i', raw))
    fwd = records.replay(r437, geo, theirs, False)
    rev = records.replay(r437, geo, theirs, True)
    res['records'] = dict(
        pr_stream_sha256=hashlib.sha256(raw).hexdigest(), pr_stream_bytes=len(raw), records=len(theirs),
        independent_lowering_byte_equal=records.pack(mine) == raw,
        kinds={k: x for k, x in sorted(collections.Counter(r[0] for r in theirs).items())},
        forward=dict(bad_columns=len(fwd[0]), profile=fwd[1], adds=fwd[2], copies=fwd[3],
                     cancellation_free_row_l1=fwd[4], bits=fwd[4].bit_length()),
        reverse=dict(bad_columns=len(rev[0]), profile=rev[1], adds=rev[2], copies=rev[3],
                     cancellation_free_row_l1=rev[4], bits=rev[4].bit_length()))
    res['mutants'] = mutants(w589, node, geo)

    # Stretch: hosted template -> whole paid profile -> price bracket (bounded; see README)
    with open(os.path.join(ROOT, TEMPLATE), 'rb') as fh:
        tpl = json.loads(gzip.decompress(fh.read()))
    hres = hosting.check(tpl, r437, geo, theirs, res['words']['R437_pr']['profile'])
    hres['template_canonical_sha256'] = hashlib.sha256(canonical(tpl)).hexdigest()
    hres['template_source_record_sha256'] = tpl['source_record_sha256']
    res['hosting'] = hres
    # hosting controls (each must break at least one hosting check)
    hk = ('windows_rederived_equal', 'every_occurrence_once', 'stage_inside_window', 'offsets_disjoint_within_rank',
          'remainders_equal_published', 'owners_match_slots_and_blocks')
    hmut = []
    slots0 = tpl['hosting']['slots']
    def overlap(sl):
        first = {}
        for i, x in enumerate(sl):
            if (x[0], x[1]) in first:
                sl[i] = x[:2] + [sl[first[x[0], x[1]]][2]] + x[3:]
                return
            first[x[0], x[1]] = i
    for label, edit in (
            ('slot_moved_outside_window', lambda sl: sl.__setitem__(0, [6] + sl[0][1:])),
            ('slot_offsets_overlap', overlap),
            ('slot_dropped', lambda sl: sl.pop()),
            ('idle_rank_changed', None)):
        t2 = dict(tpl)
        t2['hosting'] = dict(tpl['hosting'], slots=[list(x) for x in slots0])
        if edit:
            edit(t2['hosting']['slots'])
        else:
            t2['schedule'] = [dict(e, rank=e['rank'] + 1) if e.get('idx') == 6 else e for e in tpl['schedule']]
        try:
            r2 = hosting.check(t2, r437, geo, theirs, res['words']['R437_pr']['profile'])
            broken = [k for k in hk if not r2[k]] + (['whole_profile'] if r2['whole_profile'] != hres['whole_profile'] else [])
        except Reject as e:
            broken = ['rejected: %s' % e]
        hmut.append(dict(mutant=label, rejected=bool(broken), broken=broken))
    res['hosting_mutants'] = hmut
    need(tpl['m'] == 64 and tpl['live'] == 28416, 'template m/W differ from the inherited 64/28416')
    F = price.Q
    res['price'] = dict(R437=price.bracket(hres['whole_profile'], tpl['m'], tpl['live'], F(*C_R437)))
    wp = hres['whole_profile']
    # price controls: relabel a single child of the whole profile; a worse child must break the
    # bound at c, a better one the bound at the next grid point
    res['price_mutants'] = []
    for label, src, dst, side in (('one_rank2_child_as_rank3', 2, 3, 'moment_upper_at_c_below_one'),
                                  ('one_rank42_child_as_rank34', 42, 34, 'moment_lower_at_next_grid_above_one')):
        bad = dict(wp)
        bad[src] -= 1
        bad[dst] = bad.get(dst, 0) + 1
        b2 = price.bracket(bad, tpl['m'], tpl['live'], F(*C_R437))
        res['price_mutants'].append(dict(mutant=label, rejected=not (b2['moment_upper_at_c_below_one'] and
                                                                     b2['moment_lower_at_next_grid_above_one']),
                                         failing_bound=[k for k in ('moment_upper_at_c_below_one',
                                                                    'moment_lower_at_next_grid_above_one')
                                                        if not b2[k]], expected_failing_bound=side))
    local_adds = res['words']['R437_pr']['scalar_adds']['total']
    need(local_adds == res['records']['forward']['adds'] == 24208, 'local ADD count')
    res['precision_R437'] = price.precision(res['records']['forward']['cancellation_free_row_l1'],
                                            res['records']['reverse']['cancellation_free_row_l1'],
                                            sum(wp.values()), max(wp), r437['R'], local_adds=local_adds)
    res['precision_R437']['children'] = sum(wp.values())
    # positive control 1: selected #589 from main only (word -> local profile; selection9-p111.json
    # patterns -> idle remainders on the same nine windows) must give the selected bit value
    sel = json.load(open(os.path.join(ROOT, SEL589)))['bit']
    win = hosting.windows(hosting.nine_stage_schedule())
    idle589 = collections.Counter()
    per_stage = collections.Counter()
    legal = True
    for idx, pat, copies in sel['patterns']:
        idle589[win[idx][1] - sum(pat)] += copies
    cover = collections.Counter()
    capacity = collections.Counter()
    for idx, pat, copies in sel['patterns']:
        cover[idx] += copies
        capacity[idx] += copies * len(pat)
    for idx, w, st, cnt in sel['stages']:
        legal &= st in win[idx][2] and w == 8
        per_stage[st] += cnt
        capacity[idx] -= cnt
    legal &= all(cover[idx] == 2 * v for idx, (p, r, st) in win.items() if r) and not +capacity and not -capacity
    idle589 = {k: x for k, x in idle589.items() if k}
    whole589 = collections.Counter()
    for k, x in res['words']['selected589']['profile'].items():
        whole589[int(k)] += 288 * x
    for k, x in idle589.items():
        whole589[k] += 32 * x
    res['price']['selected589_control'] = dict(
        idle_children_per_replica=dict(sorted(idle589.items())), stages_legal=legal,
        every_stage_hosts_all_helpers=all(per_stage[st] == w589['R'] for st in range(9)),
        whole_profile=dict(sorted(whole589.items())),
        bracket=price.bracket(dict(whole589), 64, 28416, F(*C_589)))
    # positive control 2: #1043's published hosted profile splits over the rebuilt E470 local profile
    certj = json.load(open(os.path.join(ROOT, CERT1043)))
    cert = certj['hosted']['candidate']['invoice']['bit_profile']
    lc = certj['hosted']['candidate']['parent']['local_checks']['forward']
    c470w = res['words']['C470_rebuilt_1043']
    res['c1043_certificate_vs_rebuilt'] = dict(
        local_profile_equal={int(k): x for k, x in lc['profile'].items()} == {int(k): x for k, x in c470w['profile'].items()},
        adds_equal=lc['adds'] == c470w['scalar_adds']['total'],
        gates_equal=certj['native']['candidate']['interface']['gates'] == c470w['gates'])
    cert = {int(k): x for k, x in cert.items()}
    loc470 = {int(k): x for k, x in res['words']['C470_rebuilt_1043']['profile'].items()}
    idle470 = {k: cert.get(k, 0) - 288 * loc470.get(k, 0) for k in set(cert) | set(loc470)}
    res['price']['c1043_control'] = dict(
        idle_children_per_replica={k: x // 32 for k, x in sorted(idle470.items()) if x},
        split_exact=all(x >= 0 and x % 32 == 0 for x in idle470.values()),
        bracket=price.bracket(cert, 64, 28416, F(*C_1043)))
    # Arithmetic split of the profile published in PR #3647's README/COMPOSED-PROOF into 288 local
    # calls plus a per-replica idle remainder; hosting.check above rederives the remainder itself.
    claimed = {1: 380160, 2: 400864, 3: 22176, 4: 26592, 5: 29376, 6: 17376, 7: 26496, 34: 64, 42: 352}
    loc = {int(k): x for k, x in res['words']['R437_pr']['profile'].items()}
    calls, replicas = 9 * 32, 32
    idle = {r: claimed.get(r, 0) - calls * loc.get(r, 0) for r in sorted(set(claimed) | set(loc))}
    need(all(x >= 0 and x % replicas == 0 for x in idle.values()), 'claimed profile does not split')
    res['whole_profile_split'] = dict(
        claimed=claimed, local_calls=calls, replicas=replicas,
        idle_children_per_replica={r: x // replicas for r, x in idle.items() if x},
        rank_mass=sum(r * x for r, x in claimed.items()), live_data=28416,
        deficit=64 * 28416 - sum(r * x for r, x in claimed.items()),
        helper_occurrences=calls * r437['R'])
    drop = lambda gates, q: [[f, d - (d > q), [x - (x > q) for x in srcs if x != q]] for f, d, srcs in gates]
    res['compensation_facts'] = dict(
        e470_D0_is_C464_D0_with_column_deleted=drop(c464['D'], 469) == r437['D'],
        e464_D0_is_589_D0_with_column_deleted=drop(w589['D'], 464) == c464['D'],
        e470_D0_is_589_D0_with_column_deleted=drop(w589['D'], 470) == c470['D'])
    res['cpu_seconds_note'] = 'not recorded (platform dependent)'
    ok = (all(x['forward_bad_columns'] == 0 and x['pullback_bad_columns'] == 0 and x['methods_agree_entrywise']
              and x['reverse_orientation_bad_columns'] == 0 and all(x['interface'].values())
              for x in res['words'].values())
          and res['composition']['c464_equals_pr_R438_except_stats']
          and res['composition']['composed_equals_pr_R437_except_stats']
          and all(res['frame_paths_1043'].values()) and res['profile_delta']['additive']
          and all(t['clean_value_differences'] == 0 for t in res['traces'].values())
          and res['traces']['composed_vs_C464']['full_value_differences'] == []
          and res['traces']['e470_vs_589']['full_value_differences'] == []
          and res['traces']['composed_vs_C470']['full_value_differences'] == res['traces']['e464_vs_589']['full_value_differences']
          and res['source_chronology']['all_source_climbs_identical']
          and res['source77']['new_read']['frame'] == 186 and res['source77']['new_read']['source_value_is_clean_input']
          and res['source77']['source77_climbs_589'] == res['source77']['source77_climbs_R437']
          and all(m['rejected'] == m['expect_rejected'] for m in res['mutants'])
          and res['whole_profile_split']['rank_mass'] == 1808352 and res['whole_profile_split']['deficit'] == 10272
          and res['whole_profile_split']['helper_occurrences'] == 125856
          and res['records']['independent_lowering_byte_equal']
          and res['records']['pr_stream_sha256'] == 'caeb2eb0e417992788c32c1f5812ada60b46d1dfdba9f4ac376299b2dede13cb'
          and all(res['records'][o]['bad_columns'] == 0 and res['records'][o]['profile'] == res['words']['R437_pr']['profile']
                  for o in ('forward', 'reverse'))
          and all(res['hosting'][k] for k in ('windows_rederived_equal', 'every_occurrence_once', 'stage_inside_window',
                                              'width_matches_word', 'copy_in_range', 'offsets_disjoint_within_rank',
                                              'remainders_equal_published', 'owners_match_slots_and_blocks',
                                              'local_programs_equal_records', 'calls_bound_to_local_programs'))
          and res['hosting']['banks'] == 0 and res['hosting']['hosted_occurrences'] == 125856
          and res['hosting']['whole_profile'] == res['whole_profile_split']['claimed']
          and res['hosting']['template_source_record_sha256'] == res['records']['pr_stream_sha256']
          # canonical template content digest published in PR #3647's EXPECTED.json
          and res['hosting']['template_canonical_sha256'] == '2e868ff427654e47df34779299545c53aa05b8c96697ee126e80e7bc6a50990a'
          and all(b['moment_upper_at_c_below_one'] and b['moment_lower_at_next_grid_above_one']
                  for b in (res['price']['R437'], res['price']['selected589_control']['bracket'],
                            res['price']['c1043_control']['bracket']))
          and res['price']['selected589_control']['stages_legal']
          and res['price']['selected589_control']['every_stage_hosts_all_helpers']
          and res['price']['c1043_control']['split_exact']
          and res['hosting']['schedule_equals_main_recipe']
          and all(res['native'][k] for k in ('projector_rank_equals_dim', 'nested_projector_identity',
                                             'address_exchange_identity_on_focus'))
          and all(m['rejected'] and m['failing_bound'] == [m['expected_failing_bound']] for m in res['price_mutants'])
          and all(res['c1043_certificate_vs_rebuilt'].values())
          and all(m['rejected'] for m in res['hosting_mutants'])
          and res['precision_R437']['prefix_bits'] == 177 and res['precision_R437']['coefficient_bits'] == [177, 177]
          and res['precision_R437']['two_level_bits'] == [393, 393] and res['precision_R437']['charged_two_level_bits'] == 512
          and res['precision_R437']['row_coefficient'] == 18355 and res['precision_R437']['halving_depth'] == 2
          and res['precision_R437']['row_below_inherited_cap_20161'] and res['precision_R437']['payload_below_2_104'])
    res['status'] = 'PASS_INDEPENDENT_R437_WORD_AUDIT' if ok else 'FAIL'
    return res, time.process_time() - t0


def mutants(w589, node, geo):
    out = []
    v = w589['v']
    T589, C589 = trace(w589, [('A', i) for i in range(len(w589['A']))])
    sc589 = source_history(T589, C589, v)[1]

    def judge(label, w, keys, expect, note):
        reason, ident = None, None
        try:
            r, _ = word_checks(label, w, geo)
            ident = r['forward_bad_columns'] == 0
            if r['forward_bad_columns'] or r['pullback_bad_columns']:
                reason = 'identity fails on %d columns' % r['forward_bad_columns']
            elif not all(r['interface'].values()):
                reason = 'interface fails: ' + ','.join(k for k, x in r['interface'].items() if not x)
            else:
                T, C = trace(w, keys)
                sc = source_history(T, C, v)[1]
                if sc != {s: sc589[s] for s in range(v)}:
                    moved = [s for s in range(v) if sc[s] != sc589[s]]
                    reason = 'source chronology changed for sources %s' % moved
        except Reject as e:
            reason = 'legality: ' + str(e)
        out.append(dict(mutant=label, rejected=reason is not None, reason=reason, expect_rejected=expect, note=note,
                        legal_and_f2_identity=ident))

    comp, dead, ren, keys = apply(w589, node, do464=True, do470=True)
    m = copy.deepcopy(comp)
    m['D'] = []
    judge('drop_D0', m, keys, True, 'no frame-zero dirt compensation')
    m = copy.deepcopy(comp)
    m['C'] = []
    judge('drop_cleanup_C', m, keys, True, 'no literal reverse cleanup')
    # stale compensation/cleanup: selected #589's D0 and C with the two deleted helpers' operands
    # and gates removed and the survivors renamed (what reuse of the old D0/C would give)
    def project_gates(gates):
        g2 = []
        for f, d, srcs in gates:
            if d in dead:
                continue
            ss = [ren(x) for x in srcs if x not in dead]
            if ss:
                g2.append([f, ren(d), ss])
        return g2
    m = copy.deepcopy(comp)
    m['D'] = project_gates(w589['D'])
    judge('stale_D0_from_589', m, keys, True, 'selected D0 reused with the deleted helpers dropped')
    m = copy.deepcopy(comp)
    m['C'] = project_gates(w589['C'])
    judge('stale_C_from_589', m, keys, True, 'selected C reused with the deleted helpers dropped')
    m, _, _, k = apply(w589, node, do464=True, do470=True, read=[79, 444, [77]])
    judge('late_read_at_frame79', m, k, True, 'replacement read at the removed carrier frame 79 (descends SOURCE77)')
    m, _, _, k = apply(w589, node, do464=True, do470=True, read_at=compose.E470_DEL - 1)
    judge('early_read_at_birth', m, k, True, 'replacement read moved to the removed birth position (before A[426])')
    m, _, _, k = apply(w589, node, do464=True, do470=True, read=[186, 444, [77]], read_at=None)
    judge('positive_control_composed', m, k, False, 'the composed word itself')
    # revert one deletion: E470 read removed outright (receiver never gets SOURCE77)
    m, _, _, k = apply(w589, node, do464=True, do470=True, read='drop')
    judge('drop_replacement_read', m, k, True, 'helper470 deleted without the replacement read')
    # naive helper464 deletion: old node with the 464 operand dropped instead of the GL node
    naive = [[f, d, [s for s in srcs if s != 464]] for f, d, srcs in compose.E464_OLD_NODE]
    m, _, _, k = apply(w589, naive, do464=True, do470=True)
    judge('naive_464_deletion', m, k, True, 'old node kept, helper464 operand dropped (no GL re-synthesis)')
    for j in range(len(node)):
        m, _, _, k = apply(w589, node[:j] + node[j + 1:], do464=True, do470=True)
        judge('gl_node_drop_gate_%d' % j, m, k, True, 'one of the ten GL node gates removed')
    return out


def main():
    res, cpu = run()
    path = os.path.join(HERE, 'RESULT.json')
    text = json.dumps(res, indent=1, sort_keys=True, default=list) + '\n'
    if '--write' in sys.argv:
        open(path, 'w').write(text)
    else:
        need(os.path.exists(path) and open(path).read() == text, 'computed result differs from RESULT.json')
    print(res['status'], 'cpu %.1fs' % cpu)
    return 0 if res['status'].startswith('PASS') else 1


if __name__ == '__main__':
    sys.exit(main())
