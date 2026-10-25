# SPDX-License-Identifier: Apache-2.0
"""Scope B: an independent literal-owner audit of PR #3633's T488 journal (hexapode).

Object.  The 1,791,936-row owner journal FILL (columns time, helper, owner_replica, child, port, offset) that PR3633's
deterministic expander emits for 488 replicas = 8 copies of 61 base replicas (the retained T37, T8 and T16
chronologies), 4,392 calls of 408 helpers each.  The journal is identified by PR3633's own pin of its uncompressed
payload (owners/EXPECTED.json payload_sha256); binding() recomputes that hash from the rows.

Model (stated by PR3633 owners/UPSTREAM-PROOF.md and its source lineage; each item is re-derived here, not imported):
  * Calls.  ORDER lists the 4,392 (stage, replica) calls; replica r = base + 61 * copy runs its nine stages in order.
    ORDER must be the copy embedding of the base order ORDER37 + T8 (+37) + T16 (+45), each base call followed by its
    8 copies (copy index innermost), and DISPATCH the same embedding of the base dispatch.
  * Bins.  Every replica owns 18 source children c (the frozen template's idle children) on each of 112 ports; bin
    (o, c, p) has capacity rank(c) in {8, 16, 32, 48} (672 + 448 + 448 + 448 bins per replica).
  * Windows.  Child c of replica r is available on the actual times lo < t <= hi (strict lower, closed upper; lo = -1
    means initially available).  Two derivations from the frozen template must agree: (a) from each idle sweep's
    from_level / to_level annotation, lo = time of stage from_level (or -1), hi = time of stage to_level; (b) by
    replaying the template's execution_schedule: a local sweep of stage s at time t touches pair(s), a bridge touches
    its src and dst at the current time, and an idle sweep of pair q opens its children at the last touch of q (or -1)
    and closes them at the current time.
  * Physical families.  Child c belongs to family class 2 * pair(c) + side(c) (PLAN pairs/sides); the physical family
    of bin (o, c, p) is (o, class(c), p), 8 * 112 = 896 per replica.  Children of one class have pairwise disjoint
    windows, and within one call no two roles may use the same physical family (which also gives at most one role
    per bin per call).
  * Roles.  Row i is (t, h) = (i // 408, i % 408); helper h of call t has the width of its provider's word (widths are
    passed in from this package's own frame recount of the two staged supplier words, audit_staged_words.py).  Each
    role must fit: 0 <= offset and offset + width <= capacity.
  * Chronological prefixes.  In every bin, the roles sorted by time have offsets 0, w1, w1 + w2, ... exactly, so every
    intermediate pending mask is a compact prefix.
  * Invoice.  Every one of the 488 * 2016 bins is charged idle rank capacity - used (nothing when full); the complete
    histogram is 4,392 local bills {1:2439, 2:726, 3:224, 4:102, 5:20, 8:8} plus the idle histogram, and must equal
    the claimed profile.  Rank mass is 65,088 T (an identity once every role is placed exactly once).

audit(rows, ctx) is the single semantic check used by the positive run and by every negative control; its passes are
ordered (row-local checks, then same-call families, then per-bin prefixes, then the invoice) so a control that breaks
one rule is caught by that rule.  binding() is separate: it fixes which journal is audited.

Lineage and credit (models only; no code of these is imported or executed): the copied-owner construction and
literal format of PR3605 (Ross Richardson) and PR3633/PR3624/PR3626 (hexapode); the source template, windows and
family convention of the retained rank7-joint-endframes / coupled-carrier-cap740 packages and the earlier owner-
checker lineage named in PR3633's UPSTREAM-SOURCE-CREDITS.md.  Standard library only.
"""
import gzip
import hashlib
import json
from collections import Counter

from audit_common import need

T = 488
BASE = 61
COPIES = 8
STAGES = 9
CALLS = STAGES * T
HELPERS = 408
PORTS = 112
CHILDREN = 18
CLASSES = 8
LOCAL = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
COLUMNS = ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
# Template events that open or close no idle-child window (terminal phase, bank padding, live-family translation).
IGNORED_EVENTS = ('terminal_Y_translations', 'terminal', 'bank_padding_cover_sweep', 'translate_every_live_family')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def read_json(path):
    b = open(path, 'rb').read()
    return json.loads(gzip.decompress(b) if str(path).endswith('.gz') else b)


# ---------------------------------------------------------------------------------------------------------------
# Binding: the payload hash that PR3633 pins, recomputed from the rows in PR3633's documented serialisation.

def payload_bytes_iter(rows):
    head = json.dumps({'columns': COLUMNS, 'dispatch_overrides': []}, sort_keys=True, separators=(',', ':'))
    yield (head[:-1] + ',"rows":[').encode()
    for j, row in enumerate(rows):
        yield ((',' if j else '') + json.dumps(row, separators=(',', ':'))).encode()
    yield b']}\n'


def decode_columns(blob_xz):
    """Rows from data/FILL-columns.xz (tools/encode_journal.py): owner uint16, child, port, offset uint8 columns,
    little-endian; time and helper are implicit.  binding() then fixes the decoded rows to PR3633's pin."""
    import lzma
    import sys
    from array import array
    blob = lzma.decompress(blob_xz)
    n = CALLS * HELPERS
    need(len(blob) == 5 * n, 'owners.binding: column blob has %d bytes, expected %d' % (len(blob), 5 * n))
    owners = array('H')
    owners.frombytes(blob[:2 * n])
    if sys.byteorder != 'little':
        owners.byteswap()
    child, port, off = blob[2 * n:3 * n], blob[3 * n:4 * n], blob[4 * n:]
    return [[i // HELPERS, i % HELPERS, owners[i], child[i], port[i], off[i]] for i in range(n)]


def binding(rows, expected_payload_sha, raw_payload=None):
    """owners.binding: the rows re-serialised in PR3633's documented FILL format (and, when given, the decompressed
    FILL bytes themselves) hash to PR3633's pinned payload sha256."""
    if raw_payload is not None:
        need(sha256(raw_payload) == expected_payload_sha, 'owners.binding: FILL payload sha256 %s != pinned %s'
             % (sha256(raw_payload), expected_payload_sha))
    h = hashlib.sha256()
    for part in payload_bytes_iter(rows):
        h.update(part)
    need(h.hexdigest() == expected_payload_sha, 'owners.binding: the rows do not re-serialise to the pinned payload')
    return dict(payload_sha256=expected_payload_sha, reserialised=True, raw_payload_checked=raw_payload is not None)


# ---------------------------------------------------------------------------------------------------------------
# Order, dispatch and windows.

def base_order(o37, o8, o16):
    return [list(x) for x in o37] + [[s, r + 37] for s, r in o8] + [[s, r + 45] for s, r in o16]


def check_order(order, order37, order8, order16):
    base = base_order(order37, order8, order16)
    need(len(base) == STAGES * BASE and sorted(map(tuple, base)) == sorted((s, r) for s in range(STAGES)
                                                                           for r in range(BASE)),
         'owners.order: the base order is not every (stage, base replica) exactly once')
    emb = [[s, r + BASE * cp] for s, r in base for cp in range(COPIES)]
    need(order == emb, 'owners.order: ORDER is not the 8-copy embedding of ORDER37 + T8 + T16')
    clock = {}
    for t, (s, r) in enumerate(order):
        clock[s, r] = t
    need(len(clock) == CALLS and set(clock) == set((s, r) for s in range(STAGES) for r in range(T)),
         'owners.order: ORDER does not list every (stage, replica) exactly once')
    need(all(all(clock[s, r] < clock[s + 1, r] for s in range(STAGES - 1)) for r in range(T)),
         'owners.order: a replica runs its stages out of order')
    return clock


def check_dispatch(dispatch, order, d37, d8, d16):
    base = {}
    for rows, off in ((d37, 0), (d8, 37), (d16, 45)):
        for s, r, pid in rows:
            need((s, r + off) not in base, 'owners.dispatch: duplicate base dispatch entry')
            base[s, r + off] = pid
    need(len(base) == STAGES * BASE, 'owners.dispatch: base dispatch does not cover the base calls')
    emb = [[s, r, base[s, r % BASE]] for s, r in order]
    need(dispatch == emb, 'owners.dispatch: DISPATCH is not the embedding of the base dispatch')
    counts = Counter(pid for _, _, pid in dispatch)
    return [pid for _, _, pid in dispatch], dict(sorted(counts.items()))


def derive_windows(template, plan, clock):
    """Returns cap[c], cls[c] and win[r][c] = (lo, hi); owners.windows_agree checks both derivations agree and
    owners.windows_disjoint the per-class disjointness; owners.windows covers the structural checks."""
    cap = {}
    for x in template['idle_children']:
        need(cap.setdefault(x['child'], x['rank']) == x['rank'], 'owners.windows: child with two ranks')
    need(sorted(cap) == list(range(CHILDREN)), 'owners.windows: idle children are not 0..17')
    per_cap = Counter(cap[x['child']] for x in template['idle_children'])
    need(dict(per_cap) == {8: 672, 16: 448, 32: 448, 48: 448}, 'owners.windows: bins per replica %r' % dict(per_cap))
    need(Counter((x['child'], x['port']) for x in template['idle_children']) ==
         Counter((c, p) for c in range(CHILDREN) for p in range(PORTS)),
         'owners.windows: idle children do not cover every (child, port) once')
    cls = [2 * plan['pairs'][str(c)] + plan['sides'][str(c)] for c in range(CHILDREN)]
    need(sorted(set(cls)) == list(range(CLASSES)), 'owners.windows: family classes are not 0..7')
    stage_pair = dict((x['stage'], x['pair']) for x in template['recipe'] if x['kind'] == 'local')
    need(sorted(stage_pair) == list(range(STAGES)), 'owners.windows: recipe local stages')
    sweeps = [e for e in template['execution_schedule'] if e['kind'] == 'idle_cover_sweep']
    seen = Counter(c for e in sweeps for c in e['child_indices'] if c in cap)
    need(dict(seen) == dict((c, 1) for c in range(CHILDREN)), 'owners.windows: idle children not swept exactly once')
    for e in sweeps:
        for c in e['child_indices']:
            if c in cap:
                need(plan['pairs'][str(c)] == e['pair'], 'owners.windows: PLAN pair of child %d != sweep pair' % c)
    win_a, win_b = [], []
    for r in range(T):
        a, b = {}, {}
        for e in sweeps:                                          # derivation (a): level annotations
            lo = -1 if e['from_level'] < 0 else clock[e['from_level'], r]
            hi = clock[e['to_level'], r]
            for c in e['child_indices']:
                if c in cap:
                    a[c] = (lo, hi)
        touched, now = {}, None                                   # derivation (b): event replay
        for e in template['execution_schedule']:
            k = e['kind']
            if k == 'local_cover_sweep':
                now = clock[e['stage'], r]
                touched[stage_pair[e['stage']]] = now
            elif k == 'bridge':
                need(now is not None, 'owners.windows: bridge before any local sweep')
                touched[e['src']] = now
                touched[e['dst']] = now
            elif k == 'idle_cover_sweep':
                need(now is not None, 'owners.windows: idle sweep before any local sweep')
                for c in e['child_indices']:
                    if c in cap:
                        b[c] = (touched.get(e['pair'], -1), now)
            else:
                need(k in IGNORED_EVENTS, 'owners.windows: unknown template event kind %r' % k)
        win_a.append([a[c] for c in range(CHILDREN)])
        win_b.append([b[c] for c in range(CHILDREN)])
    need(win_a == win_b, 'owners.windows_agree: level annotations and event replay give different windows')
    for r in range(T):
        for k in range(CLASSES):
            ivs = sorted(win_a[r][c] for c in range(CHILDREN) if cls[c] == k)
            need(all(ivs[j][1] <= ivs[j + 1][0] for j in range(len(ivs) - 1)),
                 'owners.windows_disjoint: replica %d class %d has overlapping child windows' % (r, k))
    return [cap[c] for c in range(CHILDREN)], cls, win_a


def check_active_pair_lemma(win, clock, stage_pair, pair_of):
    """owners.active_pair (template level): for every replica r and stage s, no child whose pair is the stage's local
    pair is open at the stage's time.  Then the per-role exclusion 'no owner role of call (s, r) sits in replica r on
    a child of the active local pair' (a gate of PR3630's independent_owners.py) follows from the windows for every
    journal; audit() also checks it directly."""
    n = 0
    for r in range(T):
        for s in range(STAGES):
            t = clock[s, r]
            for c in range(CHILDREN):
                if pair_of[c] == stage_pair[s]:
                    lo, hi = win[r][c]
                    need(not (lo < t <= hi), 'owners.active_pair: replica %d child %d (pair %d) is open at stage %d'
                         % (r, c, pair_of[c], s))
                    n += 1
    return n


def make_ctx(order, clock, providers_by_call, widths, template, plan, claimed):
    cap, cls, win = derive_windows(template, plan, clock)
    for pid, ws in widths.items():
        need(len(ws) == HELPERS and Counter(ws) == Counter({4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}),
             'owners.widths: provider %s helper widths do not match the staged inventory' % pid)
    stage_pair = dict((x['stage'], x['pair']) for x in template['recipe'] if x['kind'] == 'local')
    pair_of = [plan['pairs'][str(c)] for c in range(CHILDREN)]
    lemma = check_active_pair_lemma(win, clock, stage_pair, pair_of)
    return dict(order=order, cap=cap, cls=cls, win=win, wbc=[widths[pid] for pid in providers_by_call],
                claimed=dict((int(k), v) for k, v in claimed.items()), pair_of=pair_of,
                call_replica=[r for s, r in order], call_pair=[stage_pair[s] for s, r in order],
                stage_pair=stage_pair, clock=clock, active_pair_lemma_triples=lemma)


# ---------------------------------------------------------------------------------------------------------------
# The semantic audit (main path for the positive run and for every control).

def audit(rows, ctx):
    cap, cls, win, wbc = ctx['cap'], ctx['cls'], ctx['win'], ctx['wbc']
    crep, cpair, pair_of = ctx['call_replica'], ctx['call_pair'], ctx['pair_of']
    need(len(rows) == CALLS * HELPERS, 'owners.shape: %d rows, expected %d' % (len(rows), CALLS * HELPERS))
    # Pass 1: row-local rules.
    at_upper = after_lower = initial = 0
    for i, row in enumerate(rows):
        need(type(row) is list and len(row) == 6 and all(type(v) is int for v in row),
             'owners.schema: row %d is not six integers' % i)
        t, h, o, c, p, z = row
        need(t == i // HELPERS and h == i % HELPERS, 'owners.identity: row %d is (%d, %d)' % (i, t, h))
        need(0 <= o < T and 0 <= c < CHILDREN and 0 <= p < PORTS, 'owners.bounds: row %d %r' % (i, row))
        need(o != crep[t] or pair_of[c] != cpair[t], 'owners.active_pair: row %d sits on its own call\'s active local '
             'pair' % i)
        lo, hi = win[o][c]
        need(lo < t <= hi, 'owners.window: row %d time %d outside (%d, %d]' % (i, t, lo, hi))
        at_upper += t == hi
        after_lower += lo >= 0 and t == lo + 1
        initial += lo < 0
        w = wbc[t][h]
        need(0 <= z and z + w <= cap[c], 'owners.capacity: row %d offset %d width %d cap %d' % (i, z, w, cap[c]))
    # Pass 2: one role per physical family per call.
    seen, current = set(), -1
    for row in rows:
        t, h, o, c, p, z = row
        if t != current:
            seen, current = set(), t
        f = (o * CLASSES + cls[c]) * PORTS + p
        need(f not in seen, 'owners.family: call %d reuses physical family (%d, %d, %d)' % (t, o, cls[c], p))
        seen.add(f)
    # Pass 3: chronological compact prefixes (rows are in time order, so bins fill chronologically).
    used = {}
    patterns = {}
    for row in rows:
        t, h, o, c, p, z = row
        b = (o * CHILDREN + c) * PORTS + p
        w = wbc[t][h]
        u = used.get(b, 0)
        need(z == u, 'owners.prefix: bin (%d, %d, %d) role at time %d has offset %d, pending prefix %d'
             % (o, c, p, t, z, u))
        used[b] = u + w
        patterns.setdefault(b, []).append(w)
    # Pass 4: the complete invoice over every bin, including empty ones.
    idle = Counter()
    for o in range(T):
        for c in range(CHILDREN):
            for p in range(PORTS):
                left = cap[c] - used.get((o * CHILDREN + c) * PORTS + p, 0)   # >= 0 by passes 1 and 3
                if left:
                    idle[left] += 1
    H = Counter(dict((r, n * CALLS) for r, n in LOCAL.items()))
    H.update(idle)
    H = dict(sorted(H.items()))
    need(H == dict(sorted(ctx['claimed'].items())), 'owners.histogram: recount %r != claimed %r' % (H, ctx['claimed']))
    mass = sum(r * n for r, n in H.items())
    need(mass == 65088 * T, 'owners.histogram: rank mass %d != 65088 T' % mass)
    by_cap = Counter((cap[(b // PORTS) % CHILDREN], tuple(sorted(ws))) for b, ws in patterns.items())
    empty = Counter()
    for o in range(T):
        for c in range(CHILDREN):
            for p in range(PORTS):
                if (o * CHILDREN + c) * PORTS + p not in patterns:
                    empty[cap[c], ()] += 1
    by_cap.update(empty)
    return dict(rows=len(rows), calls=CALLS, replicas=T, bins=T * CHILDREN * PORTS, used_bins=len(patterns),
                idle=dict(sorted(idle.items())), profile=H, rank_mass=mass, pattern_multiset=by_cap,
                active_pair_lemma_triples=ctx['active_pair_lemma_triples'],
                window_boundaries=dict(roles_at_closed_upper_endpoint=at_upper,
                                       roles_one_after_strict_lower_endpoint=after_lower,
                                       roles_in_initially_open_windows=initial))


def aggregate_patterns(candidate):
    """The literal per-capacity pattern multiset implied by PR3633's aggregate (groups [cap, lo, hi, n], x rows
    [group, pattern-vector over widths 4..9, count])."""
    W = (4, 5, 6, 7, 8, 9)
    out = Counter()
    for gi, q, n in candidate['x']:
        capg = candidate['groups'][gi][0]
        out[capg, tuple(w for w, k in zip(W, q) for _ in range(k))] += n
    return out


def check_aggregate(record, candidate):
    """owners.aggregate: the literal journal realises exactly the aggregate's bin patterns, capacity by capacity."""
    agg = aggregate_patterns(candidate)
    lit = record['pattern_multiset']
    need(agg == lit, 'owners.aggregate: literal pattern multiset differs from the aggregate in %d entries'
         % len(set(agg.items()) ^ set(lit.items())))
    return dict(distinct_capacity_patterns=len(lit), bins=sum(lit.values()))


def check_stock(word, template, buffers):
    """owners.stock: physical = 896 T + 408 helpers + 8 centres + 91 buffers + 2 coefficient registers, each
    component read from the staged word (helpers, centres, private buffers) and the template (coefficient
    namespace).  PR3633 reports 437,757."""
    helpers = word['report']['R'] - len(word['removed'])
    centres = len(word['centers'])
    lo, hi = template['private_namespace']['coefficient']
    total = CLASSES * PORTS * T + helpers + centres + buffers + (hi - lo)
    need((helpers, centres, buffers, hi - lo) == (408, 8, 91, 2) and total == 437757,
         'owners.stock: physical %d from (%d, %d, %d, %d)' % (total, helpers, centres, buffers, hi - lo))
    return dict(live=CLASSES * PORTS * T, helpers=helpers, centres=centres, private_buffers=buffers,
                coefficient=hi - lo, physical=total)


# ---------------------------------------------------------------------------------------------------------------
# Negative controls.  Each mutates one object (journal row, claimed profile, input file, template), runs the SAME
# function the positive run uses (audit, make_ctx, check_order, check_dispatch, binding, check_aggregate,
# check_stock) and must be rejected with exactly the named rule id (audit_lib.expect).  Journal rows are mutated in
# place and restored in a finally block.

def _swap_row(rows, i, new):
    old = rows[i]
    rows[i] = new
    return old


def _with_row(rows, i, new, fn):
    old = _swap_row(rows, i, new)
    try:
        fn()
    finally:
        rows[i] = old


def _with_rows(rows, changes, fn):
    olds = [(i, rows[i]) for i, _ in changes]
    for i, new in changes:
        rows[i] = new
    try:
        fn()
    finally:
        for i, old in olds:
            rows[i] = old


def bin_index(rows, ctx):
    """Per bin: chronological list of row indices (positive data only)."""
    out = {}
    for i, (t, h, o, c, p, z) in enumerate(rows):
        out.setdefault((o, c, p), []).append(i)
    return out


def controls(rows, ctx, inp, AL):
    out = []
    cap, cls, win, wbc = ctx['cap'], ctx['cls'], ctx['win'], ctx['wbc']
    run = lambda: audit(rows, ctx)
    E = lambda name, rule, fn, **kw: AL.expect(out, name, rule, fn, **kw)
    t, h, o, c, p, z = rows[5]
    E('row_not_six_integers', 'owners.schema', lambda: _with_row(rows, 5, [t, h, o, c, p, float(z)], run))
    E('swapped_helper_identities', 'owners.identity',
      lambda: _with_rows(rows, [(5, [t, rows[6][1], o, c, p, z]), (6, [t, h] + rows[6][2:])], run))
    E('port_out_of_range', 'owners.bounds', lambda: _with_row(rows, 5, [t, h, o, c, PORTS, z], run))
    # Strict lower endpoint: re-host a role at time t on a child of the same replica that opens exactly at t.
    lower = next((i, c2) for i, (t, h, o, c, p, z) in enumerate(rows) for c2 in range(CHILDREN)
                 if win[o][c2][0] == t)
    i, c2 = lower
    E('role_at_strict_lower_endpoint', 'owners.window', lambda: _with_row(rows, i, rows[i][:3] + [c2] + rows[i][4:], run),
      row=i)
    upper = next((i, c2) for i, (t, h, o, c, p, z) in enumerate(rows) for c2 in range(CHILDREN)
                 if win[o][c2][1] == t - 1 and win[o][c2][0] < t)
    i2, c3 = upper
    E('role_after_closed_upper_endpoint', 'owners.window',
      lambda: _with_row(rows, i2, rows[i2][:3] + [c3] + rows[i2][4:], run), row=i2)
    # Active local pair: put a role of call t on its own call's replica, on a child of the call's active pair (the
    # per-role gate runs before the window check); and a window table whose child stays open across a same-pair stage
    # (the template-level lemma, through the function make_ctx uses).
    t, h, o, c, p, z = rows[11]
    c_act = next(c2 for c2 in range(CHILDREN) if ctx['pair_of'][c2] == ctx['call_pair'][t])
    E('role_on_own_active_local_pair', 'owners.active_pair',
      lambda: _with_row(rows, 11, [t, h, ctx['call_replica'][t], c_act, p, z], run))
    bad_win = [list(w) for w in win]
    r0 = 0
    c0 = next(c2 for c2 in range(CHILDREN) if ctx['pair_of'][c2] == ctx['stage_pair'][STAGES - 1])
    bad_win[r0][c0] = (-1, ctx['clock'][STAGES - 1, r0])
    E('window_open_across_same_pair_stage', 'owners.active_pair',
      lambda: check_active_pair_lemma(bad_win, ctx['clock'], ctx['stage_pair'], ctx['pair_of']))
    # Same-call family reuse: put role B of call 0 on role A's bin at A's offset, with B no wider than A.
    a = 0
    b = next(j for j in range(1, HELPERS) if wbc[0][rows[j][1]] <= wbc[0][rows[a][1]])
    E('same_call_family_reused', 'owners.family',
      lambda: _with_row(rows, b, rows[b][:2] + rows[a][2:5] + [rows[a][5]], run), rows=[a, b])
    t, h, o, c, p, z = rows[7]
    E('offset_overflows_capacity', 'owners.capacity',
      lambda: _with_row(rows, 7, [t, h, o, c, p, cap[c] - wbc[t][h] + 1], run))
    bins = bin_index(rows, ctx)
    # Unpaid hole: the last role of a bin with spare capacity moves up by one.
    hole = next(ix[-1] for key, ix in bins.items()
                if rows[ix[-1]][5] + wbc[rows[ix[-1]][0]][rows[ix[-1]][1]] < cap[key[1]])
    E('unpaid_chronological_hole', 'owners.prefix',
      lambda: _with_row(rows, hole, rows[hole][:5] + [rows[hole][5] + 1], run), row=hole)
    # Offsets not in time order: in a two-role bin with different widths, the later role takes offset 0.
    pair = next(ix for key, ix in bins.items() if len(ix) == 2
                and wbc[rows[ix[0]][0]][rows[ix[0]][1]] != wbc[rows[ix[1]][0]][rows[ix[1]][1]])
    w0, w1 = (wbc[rows[j][0]][rows[j][1]] for j in pair)
    E('offsets_not_in_time_order', 'owners.prefix',
      lambda: _with_rows(rows, [(pair[0], rows[pair[0]][:5] + [w1]), (pair[1], rows[pair[1]][:5] + [0])], run),
      rows=list(pair))
    E('dropped_role', 'owners.shape', lambda: audit(rows[:-1], ctx))
    bad = dict(ctx, claimed=dict(ctx['claimed']))
    bad['claimed'][1] += 1
    E('claimed_profile_plus_one_rank1', 'owners.histogram', lambda: audit(rows, bad))
    # The pre-change PR3133 provider widths (main's PR3133-PROVIDERS.json; they differ from the staged words exactly at
    # helpers 389 and 397, 7 -> 8) do not host this journal.
    old = dict((pid, list(ws)) for pid, ws in inp['pr3133_widths'].items())
    need(all([j for j in range(HELPERS) if old[pid][j] != inp['widths'][pid][j]] == [389, 397] for pid in old),
         'owners.widths: PR3133 and staged widths do not differ exactly at helpers 389 and 397')
    oldctx = dict(ctx, wbc=[old[pid] for pid in inp['providers_by_call']])
    E('pr3133_widths_for_helpers_389_397', inp['pr3133_width_rule'], lambda: audit(rows, oldctx))
    order = [list(x) for x in inp['order']]
    order[0], order[1] = order[1], order[0]
    E('order_entries_swapped', 'owners.order', lambda: check_order(order, *inp['base_orders']))
    disp = [list(x) for x in inp['dispatch']]
    disp[0][2] = 'extra' if disp[0][2] == 'gauge44' else 'gauge44'
    E('dispatch_provider_flipped', 'owners.dispatch', lambda: check_dispatch(disp, inp['order'], *inp['base_dispatch']))
    tm = json.loads(json.dumps(inp['template']))
    sw = next(e for e in tm['execution_schedule'] if e['kind'] == 'idle_cover_sweep' and e['from_level'] >= 0)
    sw['from_level'] -= 1
    E('template_level_annotation_shifted', 'owners.windows_agree',
      lambda: make_ctx(inp['order'], inp['clock'], inp['providers_by_call'], inp['widths'], tm, inp['plan'],
                       inp['claimed']))
    tk = json.loads(json.dumps(inp['template']))
    next(e for e in tk['execution_schedule'] if e['kind'] == 'terminal')['kind'] = 'terminal_mutated'
    E('template_unknown_event_kind', 'owners.windows',
      lambda: make_ctx(inp['order'], inp['clock'], inp['providers_by_call'], inp['widths'], tk, inp['plan'],
                       inp['claimed']))
    pl = json.loads(json.dumps(inp['plan']))
    pl['sides']['1'] = 1 - pl['sides']['1']
    E('plan_side_flipped_merges_family_classes', 'owners.windows_disjoint',
      lambda: make_ctx(inp['order'], inp['clock'], inp['providers_by_call'], inp['widths'], inp['template'], pl,
                       inp['claimed']))
    t, h, o, c, p, z = rows[9]
    E('journal_row_changed_after_pinning', 'owners.binding',
      lambda: _with_row(rows, 9, [t, h, o, c, p, z + 1], lambda: binding(rows, inp['payload_sha256'])))
    swapped = [list(x) for x in inp['order']]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    E('rebuilt_order_differs_from_pinned_literal_file', 'owners.literal_files',
      lambda: check_literal_files(inp['expected'], swapped, inp['dispatch'], inp['claimed']))
    bad_disp = [list(x) for x in inp['dispatch']]
    bad_disp[-1][2] = 'extra' if bad_disp[-1][2] == 'gauge44' else 'gauge44'
    E('rebuilt_dispatch_differs_from_pinned_literal_file', 'owners.literal_files',
      lambda: check_literal_files(inp['expected'], inp['order'], bad_disp, inp['claimed']))
    cand = json.loads(json.dumps(inp['candidate']))
    cand['x'][0][2] += 1
    E('aggregate_pattern_count_changed', 'owners.aggregate', lambda: check_aggregate(inp['record'], cand))
    wd = json.loads(json.dumps(inp['word']))
    wd['centers'] = wd['centers'][:-1]
    E('word_with_seven_centres', 'owners.stock', lambda: check_stock(wd, inp['template'], inp['buffers']))
    return out


# ---------------------------------------------------------------------------------------------------------------
# Entry point used by verify.py.  I is audit_common.PinnedInputs over verify.INPUTS (git blob id + sha256 pins);
# widths {provider: [408 widths]} come from audit_staged_words (own frame recount of the two supplier words).

def literal_file_bytes(name, obj):
    """PR3633's expander serialisation of its literal side files (owners/portable_expand.py documents the format)."""
    if name == 'PROFILE.json':
        return (json.dumps(dict((int(k), v) for k, v in sorted(obj.items(), key=lambda kv: int(kv[0]))), indent=2)
                + '\n').encode()
    return (json.dumps(obj, separators=(',', ':')) + '\n').encode()


def check_literal_files(expected, order, dispatch, profile):
    """owners.literal_files: the ORDER, DISPATCH and PROFILE rebuilt here serialise to PR3633's pinned literal files."""
    got = dict((n, sha256(literal_file_bytes(n, o))) for n, o in
               (('ORDER.json', order), ('DISPATCH.json', dispatch), ('PROFILE.json', profile)))
    for n, h in got.items():
        need(h == expected['literal_files'][n], 'owners.literal_files: rebuilt %s sha256 %s != pinned %s'
             % (n, h, expected['literal_files'][n]))
    return got


def run(I, widths, rows, AL, with_controls=True):
    """rows: decode_columns(data/FILL-columns.xz); binding() below fixes them to PR3633's pinned payload."""
    exp = I.json('t488_expected')
    o37, o8, o16 = I.json('t488_order37'), I.json('t488_order_t8'), I.json('t488_order_t16')
    d37, d8, d16 = I.json('t488_dispatch37'), I.json('t488_dispatch_t8'), I.json('t488_dispatch_t16')
    base = base_order(o37, o8, o16)
    order = [[s, r + BASE * cp] for s, r in base for cp in range(COPIES)]
    clock = check_order(order, o37, o8, o16)
    bd = {}
    for rows_, off in ((d37, 0), (d8, 37), (d16, 45)):
        for s, r, pid in rows_:
            bd[s, r + off] = pid
    dispatch = [[s, r, bd[s, r % BASE]] for s, r in order]
    pbc, counts = check_dispatch(dispatch, order, d37, d8, d16)
    need(counts == {'extra': 1680, 'gauge44': 2712}, 'owners.dispatch: provider counts %r' % counts)
    files = check_literal_files(exp, order, dispatch, exp['profile'])
    need(exp['rows'] == CALLS * HELPERS and exp['replicas'] == T and exp['calls'] == CALLS and exp['physical'] == 437757,
         'owners.binding: EXPECTED.json header')
    bind = binding(rows, exp['payload_sha256'])
    template, plan = I.json('template'), I.json('plan')
    ctx = make_ctx(order, clock, pbc, widths, template, plan, exp['profile'])
    rec = audit(rows, ctx)
    agg = check_aggregate(rec, I.json('t488_candidate'))
    word = I.json('word_base')
    stock = check_stock(word, template, len(word['helper_final']))
    out = dict(order_dispatch=dict(calls=CALLS, base_replicas=BASE, copies=COPIES, providers=counts,
                                   literal_files_sha256=files),
               binding=bind, audit=dict((k, v) for k, v in rec.items() if k != 'pattern_multiset'),
               aggregate=agg, stock=stock)
    if with_controls:
        pr3133 = I.json('pr3133_providers')
        inp = dict(widths=widths, pr3133_widths=dict((pid, pr3133[pid]['widths']) for pid in widths), providers_by_call=pbc, pr3133_width_rule='owners.capacity', order=order,
                   base_orders=(o37, o8, o16), dispatch=dispatch, base_dispatch=(d37, d8, d16), template=template,
                   plan=plan, clock=clock, claimed=exp['profile'], payload_sha256=exp['payload_sha256'],
                   candidate=I.json('t488_candidate'), record=rec, word=word, buffers=len(word['helper_final']),
                   expected=exp)
        out['controls'] = controls(rows, ctx, inp, AL)
    return out
