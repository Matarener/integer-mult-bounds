#!/usr/bin/env python3
"""Independent BIT cap-copy and retimed common-code controller witnesses.

Local scalar construction belongs to helper-boundary/bit_transvection.py.
This file consumes its matrix snapshot and the frozen R438 geometry. It proves
native chart admission of the added code sweeps at unchanged idle-window
boundaries, not a restored endpoint or a complete physical supplier.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""

import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
RECIPE_SOURCE = REPO / ('research/e8-bit-p111-tuned/vendor/pr510/'
    'e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def xor_all(values):
    result = 0
    for value in values:
        result ^= value
    return result


def binary_product(a, b):
    return [xor_all(b[j] for j in bits(row)) for row in a]


def binary_rank(a):
    pivots = {}
    for row in a:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mm(a, b):
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def plus(a, b, scale=1):
    return [[x + scale * y for x, y in zip(r, s)] for r, s in zip(a, b)]


def serial(a):
    return [[[x.numerator, x.denominator] for x in row] for row in a]


def rational_rank(rows):
    pivots = {}
    for row in rows:
        row = list(map(Q, row))
        for j, old in sorted(pivots.items()):
            c = row[j]
            row = [x - c * y for x,y in zip(row,old)]
        j = next((j for j,x in enumerate(row) if x), None)
        if j is not None:
            c = row[j]
            pivots[j] = [x / c for x in row]
    return len(pivots)


def source_matrices(word, frozen):
    v, n = word['v'], 2 * word['v'] + word['R']
    rows = [1 << i for i in range(n)]
    for name in ('D', 'A'):
        for _, dst, sources in word[name]:
            for source in sources:
                rows[dst] ^= rows[source]
    r = [rows[p] & ((1 << v) - 1) for p in word['ret']]
    k = [sum(1 << j for j in row) for row in word['scatter']]
    need(r == frozen['R'] and k == frozen['K'], 'producer R/K not actual R438')
    w, h = frozen['W'], frozen['H']
    need(binary_product(r, w) == [0] * 9, 'R W not zero')
    need(binary_product(r, h) == r, 'R H not R')
    need(binary_product(h, h) == [1 << j for j in range(v)], 'H not involutive')
    delta = [row ^ (1 << j) for j, row in enumerate(h)]
    need(binary_rank(r) == binary_rank(w) == binary_rank(delta) == 9,
         'actual transvection ranks')
    need(all(k), 'a physical scatter row is zero')
    return {'source_rank': 9, 'scatter_rank': binary_rank(k),
            'source_code_defect_rank': 9, 'all_scatter_rows_nonzero': True,
            'same_code_odd_nine_stage_augmentation': 'E_aug=H; rank(E_aug-I)=9',
            'selected_row_repair_identity_obstruction': {
                'stage_count': 9, 'max_repair_rows_per_stage': 9,
                'union_support_at_most': 81, 'nonzero_K_rows': v,
                'uncovered_K_rows_at_least': v - 81,
                'scope': 'fixed R,K at augmentation; W_s=K+U_s, RW_s=0; each U_s has at most9 nonzero rows'}}


def inplace_code(h):
    """Explicit no-helper CNOT synthesis; no assumed clean private values."""
    a = h[:]
    elimination = []
    n = len(a)
    def add(dst, src):
        need(dst != src, 'self code gate')
        a[dst] ^= a[src]
        elimination.append([dst, src])
    for j in range(n):
        p = next((p for p in range(j, n) if a[p] >> j & 1), None)
        need(p is not None, 'singular source code')
        if p != j:
            add(p, j)
            add(j, p)
            add(p, j)
        for p in range(n):
            if p != j and a[p] >> j & 1:
                add(p, j)
    need(a == [1 << j for j in range(n)], 'code elimination')
    gates = list(reversed(elimination))
    for reverse in (False, True):
        rows = [1 << j for j in range(n)]
        positive = [1] * n
        for dst, src in reversed(gates) if reverse else gates:
            rows[dst] ^= rows[src]
            positive[dst] += positive[src]
        # This particular matrix is involutive over F2, not necessarily over Z.
        need(rows == h, 'explicit code synthesis/inverse')
    bounds = []
    for order in (gates, list(reversed(gates))):
        positive = [1] * n
        for dst, src in order:
            positive[dst] += positive[src]
        bounds.append(max(positive))
    return gates, {'binary_scalar_CNOTs': len(gates), 'new_private_fields': 0,
                   'arbitrary_dirty_helpers_needed': 0,
                   'signed_integer_forward_positive_bound': str(bounds[0]),
                   'signed_integer_reverse_positive_bound': str(bounds[1]),
                   'integer_lift_inverse': 'reverse the exact word and negate ADD coefficients; H squared identity is asserted only over F2',
                   'source_access': 'each CNOT reads and writes the listed actual bank families with rho_s owner-address reindexing; scans, coordinate arithmetic and head return remain paid'}


def geometry(word):
    """Reconstruct the same exact E8 reflection BFS as the pinned geometry."""
    path = REPO / 'research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
    all_word = json.loads(gzip.decompress(path.read_bytes()))
    lines = all_word['lines']
    ident = eye(8)
    gs, todo = {0: ident}, [0]
    while todo:
        more = []
        for i in todo:
            for j in range(120):
                ip = sum(x * y for x, y in zip(lines[i], lines[j])) // 2
                if j in gs or abs(ip) != 1:
                    continue
                d = [Q(x - y if ip == 1 else x + y)
                     for x, y in zip(lines[i], lines[j])]
                norm = sum(x * x for x in d)
                reflection = [[Q(a == b) - 2 * d[a] * d[b] / norm
                               for b in range(8)] for a in range(8)]
                gs[j] = mm(reflection, gs[i])
                more.append(j)
        todo = more
    need(len(gs) == 120, 'actual E8 route BFS incomplete')
    digests = []
    caps = []
    denominators = set()
    for p, old_label in enumerate(word['ports_geom']):
        q, g = word['lines'][p], gs[old_label]
        need(q == lines[old_label], 'actual punctured port ordering')
        need(mm(transpose(g), g) == ident, 'nonorthogonal E8 chart')
        first = [row[0] * 2 for row in g]
        need(first == q or first == [-x for x in q], 'route root image')
        entrance = [word['lines'][j] for j in word['frames'][word['start'][p]]]
        cap = [word['lines'][j] for j in word['frames'][word['final'][111+p]]]
        need(rational_rank(entrance) == 1 and all(
             all(4*x == sum(a*b for a,b in zip(row,q))*y for x,y in zip(row,q))
             for row in entrance), 'actual source initial frame not P_p')
        need(rational_rank(cap) == 7 and all(sum(x*y for x,y in zip(row,q)) == 0 for row in cap),
             'actual target final frame not K_p')
        projector = [[Q(x * y, 4) for y in q] for x in q]
        complement = plus(ident, projector, -1)
        a = [row[1:] for row in g]
        need(mm(a, transpose(a)) == complement, 'A A* not K')
        need(mm(transpose(a), a) == eye(7), 'A* A not I7')
        need(mm(projector, a) == [[Q(0)] * 7 for _ in range(8)], 'P A not zero')
        rho = [projector[i] + a[i] for i in range(8)]
        rho += [row + [Q(0)] * 7 for row in transpose(a)]
        need(mm(rho, rho) == eye(15), 'actual rho15 not involutive')
        p15 = [row + [Q(0)] * 7 for row in projector] + [[Q(0)] * 15 for _ in range(7)]
        k15 = [row + [Q(0)] * 7 for row in complement] + [[Q(0)] * 15 for _ in range(7)]
        e15 = [[Q(i == j and i >= 8) for j in range(15)] for i in range(15)]
        need(mm(mm(rho, p15), rho) == p15, 'rho does not fix P')
        need(mm(mm(rho, k15), rho) == e15, 'rho K rho not exterior E')
        need(mm(mm(rho, e15), rho) == k15, 'rho E rho not K')
        # Exact native address exchange law on both address halves.
        def exchange(u):
            c = plus(ident, u, -1)
            return [c[i] + u[i] for i in range(8)] + [u[i] + c[i] for i in range(8)]
        need(mm(exchange(ident), exchange(projector)) == exchange(complement),
             'D_I D_P not D_K')
        need(mm(exchange(projector), exchange(projector)) == eye(16), 'D_P not involutive')
        if p in (0, 1, 2, 4, 8, 9, 14, 30, 59):
            caps.append({'port': p, 'rank': 1,
                         'literal_copy': 'D_P takes a fresh copy from FULL to K_p, source unchanged; ERASE sees its original snapshot',
                         'complementary_inverse': 'same rank-one projector, literal reverse snapshot lifecycle'})
        denominators.update(x.denominator for row in rho for x in row)
        digests.append(sha256(canonical(serial(rho))).hexdigest())
    return {'ports': len(digests), 'actual_stage_routes': 9 * len(digests),
            'rho15_digests': digests, 'route_denominators': sorted(denominators),
            'native_D_identity_columns': 2 * 16 * len(digests),
            'actual_R438_entrance_and_cap_frames_bound': 2 * len(digests),
            'rank_one_FULL_to_cap_copy_witnesses': caps,
            'all_stage_admission_law': {
                'Y_hole_at_level_t_less_than_s': 'rho_s (K_p+E_<=t) rho_s = E_s+E_<=t, independent of port',
                'X_after_progress_to_level_t_at_least_s': 'rho_s (I+E_<=t) rho_s = I+E_<=t, independent of port',
                'initial_Y': 'zero remains zero under every actual rho_s',
                's0': 'rho_0=I; initial Y zero and completed X I are common',
                'invalid_late_X_before_progress': 'rho_s (I+E_<=t) rho_s = P_p+E_s+E_<=t for t<s; this is port-dependent'},
            'scope': 'written all-t,s implication from audited local projector identities and disjoint exterior blocks; arbitrary odd address fields avoiding recorded dyadic denominators'}


def recipe():
    raw = RECIPE_SOURCE.read_bytes()
    tree = ast.parse(raw)
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'recipe')
    selected = ast.Module(body=[fn], type_ignores=[])
    env = {}
    exec(compile(selected, str(RECIPE_SOURCE), 'exec'), env)
    events = env['recipe'](4)
    need(len(events) == 19, 'actual recipe length')
    return events, sha256(raw).hexdigest()


def xor_dict(a, b):
    return a ^ b


def code_apply(row, stages):
    # Free noncommuting invertible generators, each used only positively in
    # this controller. An input column is independent of every other column.
    for s in stages:
        row = {((s,) + word, column) for word, column in row}
    return row


def controller(events, omit=None):
    banks = [[{((), 2 * p)}, {((), 2 * p + 1)}] for p in range(4)]
    levels = [-1] * 4
    word = []
    rank_profile = Counter()
    bridge_checks = []
    extra = []
    def sweep(pair, side, stages, cut):
        if not stages:
            return
        level = levels[pair]
        for s in stages:
            need(side == 1 and (level == -1 or s > level) or
                 side == 0 and level >= s,
                 'code chart not admitted at actual native cut')
        key = len(extra)
        event = dict(op='code sweep', pair=pair, side='Y' if side else 'X',
                     stages=stages, native_level=level, cut=cut,
                     source_cut='before all borrowing in this idle window' if side else
                                'after all borrowed helpers have restored and the idle child completed')
        extra.append(event)
        word.append(event)
        if key != omit:
            banks[pair][side] = code_apply(banks[pair][side], stages)
    # These banks are untouched by the data controller until their first
    # retained idle child. Their arbitrary preloaded dirt may be borrowed and
    # restored while waiting; it need not be independently clean.
    for p in range(1, 4):
        sweep(p, 1, list(range(2 * p)), 'original first idle-window entrance')
    for event in events:
        if event['kind'] == 'local':
            s, p, rev = event['stage'], event['pair'], event['reverse']
            need(levels[p] == s - 1, 'active local level')
            if not rev:
                sweep(p, 1, [s], 'immediately before active forward call')
            x, y = banks[p]
            banks[p] = [xor_dict(x, y), code_apply(y, [s])] if rev else [
                code_apply(x, [s]), xor_dict(y, code_apply(x, [s]))]
            levels[p] = s
            word.append({'op': 'complete local coded call', **event})
            if rev:
                sweep(p, 0, [s], 'immediately after active reverse call')
            idles = []
            if s % 2 and s <= 5:
                j = (s + 1) // 2
                idles.append((j, -1, s))
            elif s % 2 == 0 and 2 <= s <= 6:
                j = s // 2
                idles.append((j, s - 1, s))
            elif s == 8:
                for j in range(4):
                    old = levels[j]
                    idles.append((j, old, 8))
            for j, old, new in idles:
                need(levels[j] == old, 'original idle entry level')
                rank = 7 * (new - old)
                rank_profile[rank] += 2 * 111 if rank else 0
                word.append(dict(op='unchanged idle child', pair=j,
                                 source_level=old, target_level=new, rank=rank))
                levels[j] = new
                stages = list(range(new + 1)) if old == -1 else list(range(old + 1, new + 1))
                sweep(j, 0, stages, 'original idle-window exit')
        elif event['kind'] == 'bridge':
            d, s = event['dst'], event['src']
            need(levels[d] == levels[s], 'original bridge frame level')
            def factors(row):
                return {key[0] for key in row}
            codes = [factors(banks[p][side]) for p in (d, s) for side in (0, 1)]
            need(all(value == codes[0] for value in codes), 'actual bridge code mismatch')
            banks[d][0] ^= banks[s][0]
            banks[s][1] ^= banks[d][1]
            word.append(event)
            bridge_checks.append(dict(dst=d, src=s, level=levels[d],
                                      common_code=list(next(iter(codes[0])))))
            # Apply a Y preload at the actual entrance of its idle window,
            # before any intervening call borrows cells from that window.
            last_stage = next(
                entry['stage'] for entry in reversed(word)
                if entry.get('op') == 'complete local coded call')
            if last_stage in (1, 3, 5):
                j = (last_stage + 1) // 2
                sweep(j, 1, [last_stage + 1], 'immediately after preceding bridge; short idle-window entrance')
            elif last_stage in (2, 4, 6):
                retired = (last_stage - 2) // 2
                sweep(retired, 1, list(range(last_stage + 1, 9)),
                      'immediately after last bridge; terminal idle-window entrance')
        else:
            need(levels == [8] * 4, 'terminal level')
            banks = [[y, x] for x, y in banks]
            word.append(event)
    expected = [[{(tuple(range(8, -1, -1)), 2 * p)},
                 {(tuple(range(8, -1, -1)), 2 * p + 1)}] for p in range(4)]
    need(banks == expected, 'all arbitrary bank columns coded endpoint')
    rank_profile.pop(0, None)
    need(rank_profile == Counter({14: 444, 7: 666, 28: 444, 42: 444}),
         'original unhosted idle profile changed')
    return word, {'extra_code_factors': sum(len(e['stages']) for e in extra),
                  'code_sweeps': len(extra), 'original_idle_profile_per_replica': dict(sorted(rank_profile.items())),
                  'original_idle_rank_mass_per_replica': sum(r * n for r, n in rank_profile.items()),
                  'original_bridge_checks': bridge_checks,
                  'original_long_idle_windows_preserved': True,
                  'all_arbitrary_bank_columns': 8,
                  'extra_rank_zero_code_work_needs_full_access_invoice': True,
                  'endpoint': 'diag(E8,...,E8), E8=G8...G0; arbitrary invertible noncommuting G_s',
                  'local_orientation': 'G_s=A_s for forward, G_s=A_s^-1 for reverse',
                  'owner_condition': 'all new Y preloads before borrowing begins; X code after all owners restore. Restored arbitrary correlated dirt remains admissible under a globally invertible preload.'}


def owner_windows(word):
    """Compare chronological eligible stages with the actual retained rule."""
    source = REPO / ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
                     'vendor/idle-axis-hosting/hosting_core.py')
    tree = ast.parse(source.read_bytes())
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'windows')
    env = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), env)
    schedule = []
    original_positions = []
    idle = 0
    for pos, event in enumerate(word):
        if event.get('op') == 'complete local coded call':
            schedule.append({'kind': 'local', 'stage': event['stage'], 'pair': event['pair']})
        elif event.get('op') == 'unchanged idle child':
            schedule.append({'kind': 'idle', 'pair': event['pair'], 'rank': event['rank'], 'idx': idle})
            idle += 1
        elif event.get('kind') in ('bridge', 'exchange'):
            schedule.append(event)
        else:
            continue
        original_positions.append(pos)
    old = env['windows'](schedule)
    old_with_positions = {}
    last, locals_ = {}, []
    for i, event in enumerate(schedule):
        pos = original_positions[i]
        if event['kind'] == 'local':
            locals_.append((pos, event['stage'], event['pair']))
            last[event['pair']] = pos
        elif event['kind'] == 'bridge':
            last[event['dst']] = last[event['src']] = pos
        elif event['kind'] == 'idle':
            p = event['pair']
            old_with_positions[event['idx']] = (last.get(p, -1), pos)
    # The enlarged physical touch alphabet counts each code sweep as a touch
    # of its actual pair, conservatively even when only one member changes.
    last, locals_, receipts = {}, [], []
    for pos, event in enumerate(word):
        op = event.get('op')
        if op == 'complete local coded call':
            locals_.append((pos, event['stage'], event['pair']))
            last[event['pair']] = pos
        elif op == 'code sweep':
            last[event['pair']] = pos
        elif event.get('kind') == 'bridge':
            last[event['dst']] = last[event['src']] = pos
        elif op == 'unchanged idle child':
            idx = len(receipts)
            p, r, expected = old[idx]
            lo = last.get(p, -1)
            actual = frozenset(s for q, s, pp in locals_ if lo < q < pos and pp != p)
            need(actual == expected, 'a new code touch destroys an old helper owner window')
            old_lo, old_hi = old_with_positions[idx]
            receipts.append({'idle_index': idx, 'pair': p, 'original_rank': r,
                             'old_last_pair_touch_index': old_lo, 'new_last_pair_touch_index': lo,
                             'idle_child_index': pos, 'original_idle_child_index': old_hi,
                             'eligible_helper_stages_old': sorted(expected),
                             'eligible_helper_stages_with_all_code_touches': sorted(actual),
                             'no_added_code_between_first_eligible_stage_and_child':
                                 not any(e.get('op') == 'code sweep' and e['pair'] == p and
                                         (min((q for q,s,pp in locals_ if s in expected), default=pos) < q2 < pos)
                                         for q2,e in enumerate(word))})
            need(receipts[-1]['no_added_code_between_first_eligible_stage_and_child'],
                 'code sweep interrupts a pending owner interval')
    # Cheap diagnosis of the superseded late-terminal-Y placement. Moving
    # that touch behind an eligible call would strictly shrink the window.
    terminal = next(r for r in receipts if r['pair'] == 0 and r['original_rank'] == 42)
    need(terminal['eligible_helper_stages_old'] == [3,4,5,6,7,8], 'terminal window control')
    return {'retained_windows_source_sha256': sha256(source.read_bytes()).hexdigest(),
            'windows': receipts,
            'late_terminal_Y_mutation': {'pair': 0, 'late_touch_after_stage': 8,
                'retained_eligible_stages': [3,4,5,6,7,8], 'eligible_stages_if_touch_at_child': [],
                'rejection': 'later preload invalidates existing strict owner-window stages'}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    frozen_path = HERE / 'BIT-CODE-INPUT.json'
    frozen = json.loads(frozen_path.read_bytes())
    path = Path(frozen['source_word'])
    need(sha256(path.read_bytes()).hexdigest() == frozen['source_gzip_sha256'], 'raw R438 word pin')
    word = json.loads(gzip.decompress(path.read_bytes()))
    algebra = source_matrices(word, frozen['matrices'])
    gates, invoice = inplace_code(frozen['matrices']['H'])
    geo = geometry(word)
    events, recipe_pin = recipe()
    controller_word, result = controller(events)
    ownership = owner_windows(controller_word)
    need(result['extra_code_factors'] == 63, 'whole common-code extra count')
    controls = []
    for skip in (0, 3, 9, 15):
        try:
            controller(events, omit=skip)
        except ValueError as error:
            controls.append({'omitted_code_sweep': skip, 'rejection': str(error)})
        else:
            raise ValueError('omitted code sweep escaped')
    complete = {'status': 'PASS_BIT_NATIVE_CAP_COPY_AND_IDLE_BOUNDARY_CODE_CONTROLLER_ENDPOINT_OPEN',
                'source_pin': frozen['source_pin'], 'raw_word_sha256': frozen['source_gzip_sha256'],
                'matrix_input_sha256': sha256(frozen_path.read_bytes()).hexdigest(),
                'canonical_recipe_source_sha256': recipe_pin,
                'ordered_controller_sha256': sha256(canonical(controller_word)).hexdigest(),
                'algebra': algebra, 'native_geometry': geo, 'code_scalar_invoice': invoice,
                'controller': result, 'chronological_owner_windows': ownership,
                'negative_controls': controls,
                'terminal_debt': {'completed_fields': 'past-chart inverse code at common FULL',
                    'hole_fields': 'N E8^-1 N on original physical input, N=diag(D_Pp); both gauges remain',
                    'conservative_rank_one_upper': 2 * 4 * 111,
                    'rank_one_upper_is_not_a_lower_bound': True},
                'limits': ['shared-label mutable-source native realization remains inherited',
                    'nine-stage integer-lift precision not re-admitted',
                    'no complete rank-zero source-access/tape invoice',
                    'owner windows preserved structurally, changed whole program not emitted or owner-replayed',
                    'no restored endpoint or supplier or new conditional kappa']}
    output = canonical(complete)
    if args.write:
        (HERE / 'BIT-NATIVE-CONTROLLER.json').write_text(json.dumps(complete, sort_keys=True, indent=2) + '\n')
        (HERE / 'BIT-NATIVE-CONTROLLER-WORD.json').write_text(json.dumps(
            {'inplace_code_CNOTs': gates, 'ordered_controller': controller_word}, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads((HERE / 'BIT-NATIVE-CONTROLLER.json').read_bytes()) == json.loads(output),
             'full BIT native/controller receipt differs')
        need(json.loads((HERE / 'BIT-NATIVE-CONTROLLER-WORD.json').read_bytes()) ==
             {'inplace_code_CNOTs': gates, 'ordered_controller': controller_word},
             'full ordered BIT native/controller word differs')
    print(complete['status'])
    print('63 extra code factors; original long idle windows retained; terminal N E^-1 N unresolved')


if __name__ == '__main__':
    main()
