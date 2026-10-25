#!/usr/bin/env python3
"""Independent right-normal replay and paid fresh-progress intervals.

This reconstructs the source-handoff family as one explicit word.  Its
operator normal form is P_perm * N_mask, opposite to caller/plane_group.py.
All integer coefficients and Gaussian signs are exact.  No assert is used.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CALLER = HERE.parent / 'caller'


def need(x, why):
    if not x:
        raise ValueError(why)


class RightAlgebra:
    """P_p N_x, where N_i^2=-I and permutations act on plane labels."""
    def __init__(self, planes):
        self.planes = planes
        self.id = tuple(range(planes))
        self.one = (self.id, 0)

    def product(self, a, b):
        p, x = a
        q, y = b
        # N_x P_q = P_q N_(q^-1 x), in right normal form.
        z = sum(1 << i for i in range(self.planes) if x >> q[i] & 1)
        sign = -1 if (z & y).bit_count() & 1 else 1
        return (tuple(p[q[i]] for i in range(self.planes)), z ^ y), sign

    def inverse(self, a):
        p, x = a
        pi = [None] * self.planes
        for i, j in enumerate(p):
            pi[j] = i
        y = sum(1 << p[i] for i in range(self.planes) if x >> i & 1)
        op = tuple(pi), y
        sign = -1 if x.bit_count() & 1 else 1
        need(self.product(a, op) == self.product(op, a) == (self.one, sign),
             'right-normal Gaussian inverse')
        return op, sign

    def plus(self, a, b, scale=1):
        c = dict(a)
        for op, z in b.items():
            c[op] = c.get(op, 0) + scale * z
            if not c[op]:
                del c[op]
        return c

    def times(self, a, b):
        c = {}
        for op, z in a.items():
            for oq, w in b.items():
                r, sign = self.product(op, oq)
                c[r] = c.get(r, 0) + sign * z * w
                if not c[r]:
                    del c[r]
        return c

    def eye(self, n):
        return [[{self.one: 1} if i == j else {} for j in range(n)] for i in range(n)]

    def mm(self, a, b):
        n = len(a)
        out = [[{} for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for h in range(n):
                if a[i][h]:
                    for j in range(n):
                        if b[h][j]:
                            out[i][j] = self.plus(out[i][j], self.times(a[i][h], b[h][j]))
        return out

    def op(self, event):
        data = event['operator']
        p = tuple(data['block_permutation'])
        leftmask = sum(1 << i for i in data['native_blocks'])
        rightmask = sum(1 << i for i in range(self.planes) if leftmask >> p[i] & 1)
        return (p, rightmask), data['sign']

    def commute(self, event, mask):
        op, sign = self.op(event)
        return self.product(op, (self.id, mask)) == self.product((self.id, mask), op)

    def replay(self, events, n, return_inverse=True):
        M, Mi = self.eye(n), self.eye(n)
        for event in events:
            typ = event['kind']
            if typ == 'ADD':
                d, s, z = event['dst'], event['src'], int(event['coefficient'])
                M[d] = [self.plus(a, b, z) for a, b in zip(M[d], M[s])]
                if return_inverse:
                    # Right multiplication by the inverse shear changes col s.
                    for row in Mi:
                        row[s] = self.plus(row[s], row[d], -z)
            elif typ == 'BANK_SWAP':
                a, b = event['banks']
                M[a], M[b] = M[b], M[a]
                if return_inverse:
                    for row in Mi:
                        row[a], row[b] = row[b], row[a]
            else:
                op, sign = self.op(event)
                bank = event['bank']
                M[bank] = [self.times({op: sign}, a) for a in M[bank]]
                if return_inverse:
                    oi, si = self.inverse(op)
                    for row in Mi:
                        row[bank] = self.times(row[bank], {oi: sign * si})
        return M, Mi

    def serial(self, M):
        return [[[[list(p), x, c] for (p, x), c in sorted(a.items())] for a in row] for row in M]


def event_word(q, omit_raw_a_repair=False):
    """One explicit word; no transported-source search is called."""
    need(q >= 2, 'the handoff family starts at q=2')
    n, planes = 2 * q + 2, 2 * q + 2
    events = []
    def add(d, s, c, label):
        if c:
            events.append(dict(kind='ADD', dst=d, src=s, coefficient=str(c), label=label))
    def unary(bank, blocks, permutation=None, sign=1, label='', native=True):
        p = list(range(planes)) if permutation is None else permutation
        events.append(dict(kind='NATIVE' if native else 'ADDRESS_OR_UNIT', bank=bank,
                           operator=dict(sign=sign, native_blocks=list(blocks),
                                         block_permutation=p, native_arity=2 * len(blocks)), label=label))
    def common(bank, label, inverse=False):
        unary(bank, [0], sign=-1 if inverse else 1, label=label)
    def swap(a, b, label):
        events.append(dict(kind='BANK_SWAP', banks=[a, b], label=label))
    def source_swap(bank, stage):
        p = list(range(planes))
        p[0], p[stage] = p[stage], p[0]
        unary(bank, [], p, label=f'query{stage} source swap', native=False)
    def fresh(source, stage, target):
        for bank in range(n):
            if bank != source:
                unary(bank, [stage], label=f'query{stage} target fresh' if bank == target
                      else f'query{stage} inactive fresh progress')
    for r in range(2, q + 1):
        add(2 * r + 1, 3, 1, 'raw c-basis')
    common(1, 'shared input N exposure')
    add(2, 1, 1, 'shared input fanout')
    common(1, 'shared input N inverse', True)
    for r in range(q, 0, -1):
        add(2 * r + 1, 1, -1, 'initial nested scalar bridge')
        add(0, 2 * r, 1, 'initial nested scalar bridge')
    add(2, 0, -1, 'query1 scalar entrance')
    common(0, 'query1 source common')
    add(1, 0, 1, 'query1 delivery')
    source_swap(0, 1)
    fresh(0, 1, 1)
    add(2, 0, 1, 'query1 scalar exit')
    add(0, 2, -1, 'initial nested scalar bridge')
    add(1, 3, 1, 'initial nested scalar bridge')
    for r in range(1, q + 1):
        add(2 * r + 1, 1, -1, 'query2 scalar entrance')
    common(1, 'query2 source common')
    add(2, 1, 1, 'query2 delivery')
    source_swap(1, 2)
    fresh(1, 2, 2)
    for r in range(1, q + 1):
        add(2 * r + 1, 1, 1, 'query2 scalar exit')
    add(1, 3, -1, 'initial nested scalar bridge')
    common(2, 'query3 source common')
    for r in range(2, q + 1):
        add(2 * r + 1, 2, 1, 'query3 source fanout')
    add(3, 2, 1, 'query3 delivery')
    source_swap(2, 3)
    fresh(2, 3, 3)
    for r in range(2, q + 1):
        add(2 * r + 1, 2, 1, 'query3 pre-continuation fanout')
    common(2, 'query3 retained source continuation')
    add(2, 0, 1, 'initial nested scalar bridge')
    add(3, 1, 1, 'initial nested scalar bridge')
    add(1, 3, -1, 'initial nested scalar bridge')
    swap(2, 3, 'initial nested permutation')
    add(0, 4, -1, 'initial nested scalar bridge')
    add(1, 5, 1, 'initial nested scalar bridge')
    for r in range(2, q + 1):
        add(2 * r + 1, 1, -1, 'query4 scalar source entrance')
    if not omit_raw_a_repair:
        for r in range(3, q + 1):
            add(0, 2 * r, -1, 'restore raw a from deeper response entrance')
    add(3, 0, -1, 'held source subtract raw a')
    for r in range(2, q + 1):
        add(3, 2 * r, -1, 'held source subtract future raw b')
    for r in range(2, q + 1):
        even, odd, b, c = 2 * r, 2 * r + 1, 2 * r, 2 * r + 1
        common(1, f'query{even} source common')
        add(1, 3, -1, f'query{even} isolate raw c difference')
        swap(1, 3, f'query{even} source handoff')
        source_swap(1, even)
        fresh(1, even, 3)
        swap(3, c, f'query{even} move finished c difference')
        common(b, f'query{odd} source common')
        for ell in range(r + 1, q + 1):
            add(2 * ell + 1, b, 1, f'query{odd} future c first fanout')
        add(3, b, 1, f'query{odd} delivery')
        swap(b, 3, f'query{odd} source handoff')
        add(2, b, -1, f'query{odd} finish current b accumulator')
        for ell in range(r + 1, q + 1):
            add(2 * ell + 1, b, -1, f'query{odd} restore future raw c differences')
        source_swap(b, odd)
        fresh(b, odd, 3)
        if r < q:
            add(2, 1, 1, f'query{odd} retain other carrier in b accumulator')
            nextc = 2 * r + 3
            for ell in range(r + 2, q + 1):
                add(2 * ell + 1, nextc, -1, f'query{odd} next c difference')
                add(2 * ell + 1, 1, 1, f'query{odd} retain other carrier in future c')
            swap(1, nextc, f'query{odd} move next raw c into t')
            add(1, b, 1, f'query{odd} next source preload')
            common(b, f'query{odd} retained source continuation')
        swap(b, 3, f'query{odd} move finished b to its public slot')
    common(0, 'final raw a common query')
    add(2, 0, -1, 'final b accumulator isolation')
    for r in range(3, q + 1):
        add(2 * r + 1, 2 * r - 1, 1, 'triangular c difference decode')
    return events


def canonical_event(event):
    typ = event['kind']
    if typ == 'ADD':
        return typ, event['dst'], event['src'], int(event['coefficient'])
    if typ == 'BANK_SWAP':
        return typ, tuple(event['banks'])
    x = event['operator']
    return typ, event['bank'], x['sign'], tuple(x['native_blocks']), tuple(x['block_permutation'])


def histogram(events):
    return Counter(event['operator']['native_arity'] for event in events if event['kind'] == 'NATIVE')


def defer_fresh(events, n, planes, flush_swaps=False):
    """Pay each postponed fresh factor at its actual first incompatible cut."""
    A = RightAlgebra(planes)
    pending = [[] for _ in range(n)]
    out, batches, transports = [], [], []
    def flush(bank, deadline, reason):
        if not pending[bank]:
            return
        requests = pending[bank]
        blocks = [e['operator']['native_blocks'][0] for _, e in requests]
        need(len(set(blocks)) == len(blocks), 'no repeated native plane is silently cancelled')
        event = dict(kind='NATIVE', bank=bank,
                     operator=dict(sign=1, native_blocks=sorted(blocks),
                                   block_permutation=list(range(planes)), native_arity=2 * len(blocks)),
                     label='paid deferred fresh-progress batch')
        batches.append(dict(bank=bank, original_request_indices=[i for i, _ in requests],
                            original_request_banks=[e['bank'] for _, e in requests],
                            native_planes=sorted(blocks), deadline_before_original_event=deadline,
                            reason=reason, output_event_index=len(out), arity_in_units_f=2 * len(blocks)))
        out.append(event)
        pending[bank] = []
    for index, event in enumerate(events):
        fresh = event['kind'] == 'NATIVE' and ('target fresh' in event['label'] or 'inactive fresh progress' in event['label'])
        if fresh:
            need(len(event['operator']['native_blocks']) == 1 and event['operator']['sign'] == 1,
                 'a fresh request is an actual single signed native plane')
            pending[event['bank']].append((index, event))
            continue
        typ = event['kind']
        if typ == 'ADD':
            for bank in sorted({event['dst'], event['src']}):
                flush(bank, index, 'next scalar ADD touches this field')
        elif typ == 'BANK_SWAP':
            a, b = event['banks']
            if flush_swaps:
                flush(a, index, 'bank SWAP conservative deadline')
                flush(b, index, 'bank SWAP conservative deadline')
            else:
                transports.append(dict(original_event_index=index, banks=[a, b],
                                       pending_request_indices=[[i for i, _ in pending[a]], [i for i, _ in pending[b]]]))
                pending[a], pending[b] = pending[b], pending[a]
        else:
            bank = event['bank']
            mask = sum(1 << e['operator']['native_blocks'][0] for _, e in pending[bank])
            if mask and not A.commute(event, mask):
                flush(bank, index, 'next unary fails exact native-plane commutation')
        out.append(event)
    for bank in range(n):
        flush(bank, len(events), 'declared prefix endpoint')
    need(sum(k * v for k, v in histogram(out).items()) == sum(k * v for k, v in histogram(events).items()),
         'all postponed native rank mass remains paid')
    return out, batches, transports


def reverse_events(events):
    out = []
    for event in reversed(events):
        e = json.loads(json.dumps(event))
        if e['kind'] == 'ADD':
            e['coefficient'] = str(-int(e['coefficient']))
        elif e['kind'] != 'BANK_SWAP':
            p = e['operator']['block_permutation']
            pi = [None] * len(p)
            for i, j in enumerate(p):
                pi[j] = i
            # Invert left-normal N_x P_p independently from right replay.
            mask = sum(1 << j for j in e['operator']['native_blocks'])
            invmask = sum(1 << pi[i] for i in range(len(p)) if mask >> i & 1)
            e['operator']['block_permutation'] = pi
            e['operator']['native_blocks'] = [i for i in range(len(p)) if invmask >> i & 1]
            if mask.bit_count() & 1:
                e['operator']['sign'] *= -1
        out.append(e)
    return out


def matrix_digest(A, M):
    raw = json.dumps(A.serial(M), separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def factory_certificate(q, A, M):
    """Separate the exact alternating carrier factories from the fixed J."""
    def P(stage):
        p = list(A.id)
        p[0], p[stage] = p[stage], p[0]
        return {(tuple(p), 0): 1}
    N, I = {(A.id, 1): 1}, {A.one: 1}
    Ni = {(A.id, 1): -1}
    Q1 = A.times(A.times(Ni, P(1)), N)
    J = [[A.plus(A.plus(P(2), Q1), I, -1), A.plus(I, P(2), -1)],
         [A.plus(Q1, I, -1), I]]
    u, v = (1, A.times(P(3), N)), (0, I)
    for r in range(2, q + 1):
        U = u[0], A.times(P(2 * r), u[1])
        V = v[0], A.times(A.times(P(2 * r + 1), N), v[1])
        if r < q:
            u, v = V, (U[0], {op: -c for op, c in U[1].items()})
    factories = [U, V]
    Ffresh = {(A.id, ((1 << A.planes) - 1) ^ 1): 1}
    rows = []
    support_union = set()
    for physical_row, (coordinate, factory) in zip((1, 3), factories):
        need(len(factory) == 1, 'each terminal factory is a single actual native/ADDRESS word')
        (perm, rightmask), sign = next(iter(factory.items()))
        leftsupport = [perm[i] for i in range(A.planes) if rightmask >> i & 1]
        need(0 not in leftsupport and not support_union.intersection(leftsupport),
             'terminal factories have disjoint fresh native supports')
        support_union.update(leftsupport)
        expected = [A.times(A.times(Ffresh, factory), J[coordinate][j]) for j in range(2)]
        need([M[physical_row][j] for j in (1, 3)] == expected,
             'all actual pivot-input columns factor through the exact fixed J')
        rows.append(dict(physical_row=physical_row, fixed_J_coordinate=coordinate,
                         ADDRESS_permutation=list(perm), native_support_left_normal=sorted(leftsupport),
                         native_block_count=len(leftsupport), exact_Gaussian_unit=sign,
                         one_direct_inverse_factory_child_arity_in_units_f=2 * len(leftsupport)))
    need(support_union == set(range(3, 2 * q + 2, 2)),
         'factory native supports are exactly the q odd fresh planes 3,5,...,2q+1')
    return dict(rows=rows, total_native_blocks=q,
                exact_support_union=sorted(support_union),
                direct_inverse_factory_rank_mass_in_units_f=2 * q,
                scope='Exact factorization and invoice for direct diagonal inverse-factory cleanup. This is not a lower bound on arbitrary joint H/L compensation words.')


def check_q(q, source_compare=False, full_intervals=False):
    n, planes = 2 * q + 2, 2 * q + 2
    events = event_word(q)
    if source_compare:
        sys.path.insert(0, str(CALLER))
        import handoff_family
        _, _, _, supplied = handoff_family.build(q, True)
        need(list(map(canonical_event, events)) == list(map(canonical_event, supplied)),
             f'q{q} independently reconstructed trace differs from the supplied literal word')
    A = RightAlgebra(planes)
    M, Mi = A.replay(events, n)
    need(A.mm(M, Mi) == A.mm(Mi, M) == A.eye(n), 'both complete inverse matrix orders')
    rev, _ = A.replay(reverse_events(events), n, False)
    need(rev == Mi, 'serialized reverse/inverse word binds independently')
    E = {(A.id, (1 << planes) - 1): 1}
    public = [i for i in range(n) if i not in (1, 3)]
    need(all(M[i] == [E if j == i else {} for j in range(n)] for i in public),
         f'q{q} all independent actual public columns')
    expected = n * (2 * q + 1) + q + 2
    need(histogram(events) == {2: expected}, 'separate-progress prefix histogram')
    batched, batches, transports = defer_fresh(events, n, planes)
    Mb, Mbi = A.replay(batched, n)
    need(Mb == M and Mbi == Mi, 'paid batched word equals the complete original word and inverse')
    need(A.replay(reverse_events(batched), n, False)[0] == Mi,
         'actual reversed batched event list restores every raw input')
    if q >= 3:
        mutant, _ = A.replay(event_word(q, True), n, False)
        need(any(mutant[i] != M[i] for i in public), 'omitted raw-a repair must change a public raw-input column')
    # A defect control changes a real pending progress batch, not a promise.
    bad = json.loads(json.dumps(batched))
    chosen = next(e for e in bad if e['label'] == 'paid deferred fresh-progress batch')
    chosen['operator']['sign'] *= -1
    need(A.replay(bad, n, False)[0] != M, 'wrong deferred Gaussian batch phase is detected')
    phase_adapters = sum((len(b['native_planes']) - 1) % 4 != 0 for b in batches)
    result = dict(q=q, banks=n, stages=2 * q + 1, ambient_arity_in_units_f=2 * planes,
                  independent_source_trace_match=source_compare,
                  separate_histogram=dict(histogram(events)), batched_histogram=dict(histogram(batched)),
                  rank_mass_in_units_f=2 * expected, stock_in_units_f=2 * n * planes,
                  D_prefix_in_units_f=2 * q, public_rows=public,
                  original_event_count=len(events), batched_event_count=len(batched),
                  batch_count=len(batches), transported_pending_intervals=len(transports),
                  largest_batch_arity_in_units_f=max(b['arity_in_units_f'] for b in batches),
                  batch_Gaussian_UNIT_scan_count=phase_adapters,
                  batch_selected_plane_packing_ADDRESS_scan_upper_bound=2 * len(batches),
                  batch_native_lowering='Product of r disjoint N_f planes equals i^(r-1) times the actual native N_(r*f) after the displayed plane packing. Pay the Gaussian UNIT scan when r-1 is nonzero modulo4 and the two packing/unpacking ADDRESS scans unless a separate literal layout removes them.',
                  terminal_factory_diagnostic=factory_certificate(q, A, M),
                  complete_matrix_sha256=matrix_digest(A, M),
                  complete_inverse_sha256=matrix_digest(A, Mi),
                  all_actual_columns_and_both_inverse_orders='PASS',
                  all_batched_columns_and_literal_reverse='PASS')
    if full_intervals:
        result.update(original_events=events, batched_events=batched,
                      fresh_progress_intervals=batches, pending_bank_transports=transports)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--quick', action='store_true', help='check q2..5 rather than the saved full receipt')
    args = ap.parse_args()
    qs = [2, 3, 4, 5] if args.quick else [2, 3, 4, 5, 6, 8, 12, 16]
    fixtures = []
    for q in qs:
        fixtures.append(check_q(q, q <= 5, q in (2, 3, 4, 8, 16)))
        print('PASS_RIGHT_NORMAL_HANDOFF_AND_PAID_PROGRESS', 'q', q,
              'hist', fixtures[-1]['batched_histogram'], flush=True)
    out = dict(status='PASS_INDEPENDENT_ACTUAL_HANDOFF_FAMILY_AND_PAID_PROGRESS',
               no_new_kappa=True, prefix_only=True,
               scientific_pin='20ecf2891d80b5acf18d980b2164fb44ea7faa90',
               fixtures=fixtures,
               exact_arithmetic='Integer linear combinations of P_perm N_mask; the product rule is derived in right normal form, independently of caller/plane_group.py left normal form. N_i^2=-I Gaussian signs are retained.',
               all_q_retiming_proof='At each processed cut original_prefix=D_pending*retimed_prefix. Each pending fresh N_i commutes through a unary only after exact group multiplication verifies commutation. Pending factors are transported through an actual bank SWAP by conjugation. Before each ADD all pending factors on both participating banks are paid. Pending factors on other banks commute with the ADD. Endpoint pays every remaining factor. Hence the complete changed word equals the original for every finite q, with all native rank mass retained.',
               covered_domain='Finite independent full-column replay q2,3,4,5,6,8,12,16, plus the written all-q local commutation invariant for the displayed event generator. The source all-pair affine induction remains a separate written construction; neither is a formal-kernel result.',
               negative_controls=['Omitting the q>=3 raw-a repair changes an actual public input column.',
                                  'Wrong sign on a paid deferred fresh batch changes the complete operator.'],
               limits=['The terminal two-pivot H/L compensation is not part of this prefix receipt.',
                       'The batching schedule is valid and fully paid; no global optimality of its moment is claimed.',
                       'Each wide native batch is an actual product of distinct disjoint native planes, arity 2f times its displayed plane count. Native ADDRESS/adapters, scalar ADD/SWAP scans, ownership, precision and outer assembly retain their independent costs.'],
               attribution=['Source handoff and final raw-a closure: root.',
                            'Scalable pair encoder and raw-a repair: mixed_carrier_caller_1019/caller/handoff_family.py.',
                            'Second source handoff/current-source fanout: q4_pauli_fusion and stabilizer_escape_1019.',
                            'Independent explicit trace reconstruction, right-normal all-column replay and legal paid progress intervals: q4_pauli_fusion.'],
               source_pins=[dict(path=str(CALLER / name), sha256=hashlib.sha256((CALLER / name).read_bytes()).hexdigest())
                            for name in ['handoff_family.py', 'nested_family.py', 'nested_prefix.py', 'plane_group.py']],
               producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out = json.loads(json.dumps(out))
    if args.quick:
        return
    path = HERE / 'INDEPENDENT-HANDOFF-FAMILY.json'
    if args.write:
        path.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved independent family receipt differs')
    print(out['status'], 'prefix only; no new kappa')


if __name__ == '__main__':
    main()
