#!/usr/bin/env python3
"""Exact five-stage six-bank prefix with two mid-query source handoffs.

The first three stages are the pinned nested-response construction.  The
last two stages change the physical source before its plane ADDRESS swap.
All six input columns are arbitrary.  No ordinary or private helper occurs.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CALLER = HERE.parent / 'caller'
sys.path.insert(0, str(CALLER))
import free_ops as F
from plane_group import Algebra
from nested_prefix import skeleton, probe


def need(x, message):
    if not x:
        raise ValueError(message)


class Physical:
    def __init__(self, skip_progress=False):
        self.A = Algebra(6)
        self.M = self.A.eye(6)
        self.Mi = self.A.eye(6)
        self.events = []
        self.skip_progress = skip_progress

    def app(self, B, Bi, event):
        A = self.A
        need(A.mm(B, Bi) == A.mm(Bi, B) == A.eye(6), 'each actual event is invertible')
        self.M = A.mm(B, self.M)
        self.Mi = A.mm(self.Mi, Bi)
        self.events.append(event)

    def add(self, dst, src, c, label):
        if not c:
            return
        A = self.A
        self.app(A.es(6, dst, src, A.mono(coefficient=c)),
                 A.es(6, dst, src, A.mono(coefficient=-c)),
                 dict(kind='ADD', dst=dst, src=src, coefficient=str(c), label=label))

    def unary(self, bank, op, kind, label):
        A = self.A
        B, Bi = A.eye(6), A.eye(6)
        B[bank][bank], Bi[bank][bank] = op, A.inv(op)
        self.app(B, Bi, dict(kind=kind, bank=bank, operator=A.serial(op),
                            native_arity=A.native_arity(op), label=label))

    def swap(self, i, j, label):
        B = self.A.eye(6)
        B[i], B[j] = B[j], B[i]
        self.app(B, B, dict(kind='BANK_SWAP', banks=[i, j], label=label))

    def fresh(self, stage, source):
        for bank in range(6):
            if bank == source:
                continue
            if self.skip_progress and stage == 4 and bank == 3:
                continue
            self.unary(bank, self.A.n(stage), 'NATIVE',
                       f'query{stage} paid fresh progress bank{bank}')


class Formal:
    def __init__(self):
        self.M, self.Mi = F.eye(6), F.eye(6)

    def app(self, B, Bi):
        need(F.mm(B, Bi) == F.mm(Bi, B) == F.eye(6), 'each formal event is invertible')
        self.M = F.mm(B, self.M)
        self.Mi = F.mm(self.Mi, Bi)

    def add(self, dst, src, c):
        if c:
            self.app(F.es(6, dst, src, c), F.es(6, dst, src, F.neg(c)))

    def scalar(self, dst, src, c):
        self.add(dst, src, F.mono((), c))

    def unary(self, bank, op):
        self.app(F.unary(6, bank, op), F.unary(6, bank, F.inv(op)))

    def swap(self, i, j):
        B = F.eye(6)
        B[i], B[j] = B[j], B[i]
        self.app(B, B)


def evaluate(x, A):
    out = A.Z
    for word, c in x.items():
        term = A.mono(coefficient=c)
        for letter in word:
            op = A.n(0) if letter == 0 else A.swap(0, abs(letter))
            term = A.mul(term, A.inv(op) if letter < 0 else op)
        out = A.add(out, term)
    return out


def bind(M, A, fresh):
    return [[A.mul(fresh, evaluate(x, A)) for x in row] for row in M]


def ec(z):
    return F.add(F.mono((), z[0]), F.mono((0,), z[1]))


def build(wrong_fanout=False, skip_progress=False):
    p, f = Physical(skip_progress), Formal()
    A = p.A
    _, ops = skeleton(2, (1, 0))
    choices = probe(2, (1, 1), (1, 0))
    need(all(c is not None for _, _, c in choices), 'pinned source retractions exist')
    f.scalar(5, 3, 1)
    p.add(5, 3, 1, 'input c-basis inverse')
    p.unary(1, A.n(0), 'NATIVE', 'shared entrance N exposure')
    p.add(2, 1, 1, 'shared entrance b1 += N t')
    p.unary(1, A.inv(A.n(0)), 'NATIVE', 'shared entrance N inverse')
    stage = 0
    source_rows = []
    for typ, dst, src, z in ops:
        if typ == 'a':
            f.add(dst, src, ec(z))
            if z[1]:
                need(stage == 0 and dst == 2 and src == 1 and z[0] == 0,
                     'the only encountered external N-ADD is the compiled shared entrance')
            else:
                p.add(dst, src, z[0], 'scalar nested response bridge')
        elif typ == 's':
            f.swap(dst, src)
            p.swap(dst, src, 'nested response bank permutation')
        else:
            stage += 1
            u = choices[stage - 1][2][1]
            if stage == 4:
                # This is exactly the current cut BEFORE its source N:
                # all scalar source-retraction entrances are retained.
                for bank, (a, b) in enumerate(u):
                    if bank != src:
                        f.scalar(bank, src, -a)
                        p.add(bank, src, -a, 'query4 scalar entrance before changed source identity')
                break
            continued = any(v[1] for v in u)
            source_rows.append(dict(stage=stage, source=src, target=dst,
                                    continued=continued,
                                    source_retraction=[[str(x), str(y)] for x, y in u]))
            for bank, value in enumerate(u):
                if bank != src:
                    f.add(bank, src, F.neg(ec(value)))
            f.add(dst, src, F.N)
            f.unary(src, F.prod(F.N if continued else F.I, F.mono((stage,))))
            for bank, value in enumerate(u):
                if bank != src:
                    f.add(bank, src, ec(value))
            for bank, (a, b) in enumerate(u):
                if bank != src:
                    p.add(bank, src, -a, f'query{stage} scalar entrance')
            p.unary(src, A.n(0), 'NATIVE', f'query{stage} existing source N')
            for bank, (a, b) in enumerate(u):
                if bank != src:
                    p.add(bank, src, -b, f'query{stage} entrance from source N exposure')
            p.add(dst, src, 1, f'query{stage} raw delivery')
            p.unary(src, A.swap(0, stage), 'ADDRESS', f'query{stage} source plane swap')
            p.fresh(stage, src)
            if continued:
                for bank, (a, b) in enumerate(u):
                    if bank != src:
                        p.add(bank, src, -b, f'query{stage} pre-continuation fanout')
                p.unary(src, A.n(0), 'NATIVE', f'query{stage} paid source continuation')
            for bank, (a, b) in enumerate(u):
                if bank != src:
                    p.add(bank, src, a, f'query{stage} scalar exit')
    need(stage == 4, 'stop at the complete current query4 scalar entrance')
    F3 = A.prod(*(A.n(j) for j in range(1, 4)))
    need(p.M == bind(f.M, A, F3), 'all six current cut columns bind to actual plane phases')
    cut = f.M
    cut_physical = p.M
    def scalar(dst, src, c, label):
        f.scalar(dst, src, c)
        p.add(dst, src, c, label)
    def common(bank, label):
        f.unary(bank, F.N)
        p.unary(bank, A.n(0), 'NATIVE', label)
    def swap(i, j, label):
        f.swap(i, j)
        p.swap(i, j, label)
    def changed_source(bank, stage):
        # Pulling the common fresh N_stage to the left gives
        # N_stage^-1 P_stage = P_stage N^-1.
        f.unary(bank, F.prod(F.mono((stage,)), F.inv(F.N)))
        p.unary(bank, A.swap(0, stage), 'ADDRESS', f'query{stage} ADDRESS on changed source')
        p.fresh(stage, bank)
    scalar(3, 0, -1, 'query4 current encoder c1 -= a')
    scalar(3, 4, -1, 'query4 current encoder c1 -= b2')
    common(1, 'query4 existing source N on u+c2')
    scalar(1, 3, -1, 'query4 isolate N c2 from held N u')
    swap(1, 3, 'query4 source handoff BEFORE source ADDRESS')
    changed_source(1, 4)
    swap(3, 5, 'query4 put completed public c2 into slot5')
    common(4, 'query5 existing source N on raw b2')
    scalar(3, 4, 1, 'query5 cancel b2 from the dirty first-pivot field')
    swap(4, 3, 'query5 source handoff BEFORE source ADDRESS')
    scalar(2, 4, 1 if wrong_fanout else -1,
           'query5 current-source fanout b1 -= (-v-N a) BEFORE source ADDRESS')
    changed_source(4, 5)
    swap(4, 3, 'query5 restore pivot3 and completed public b2 slot4')
    common(0, 'final paid N exposure on raw a')
    scalar(2, 0, -1, 'finish b1 using the current completed public a')
    return p, f, cut, cut_physical, source_rows


def replay(events, A, reverse=False):
    M = A.eye(6)
    for event in reversed(events) if reverse else events:
        kind = event['kind']
        if kind == 'ADD':
            c = Fraction(event['coefficient']) * (-1 if reverse else 1)
            B = A.es(6, event['dst'], event['src'], A.mono(coefficient=c))
        elif kind == 'BANK_SWAP':
            B = A.eye(6)
            i, j = event['banks']
            B[i], B[j] = B[j], B[i]
        else:
            op = A.Z
            for term in event['operator']:
                bits = sum(1 << j for j in term['N_planes'])
                op = A.add(op, A.mono(bits, term['ADDRESS_plane_permutation'],
                                     Fraction(term['coefficient'])))
            if reverse:
                op = A.inv(op)
            B = A.eye(6)
            B[event['bank']][event['bank']] = op
        M = A.mm(B, M)
    return M


def prove():
    p, f, cut, cut_physical, source_rows = build()
    A = p.A
    F5 = A.prod(*(A.n(j) for j in range(1, 6)))
    E = A.mul(F5, A.n(0))
    need(p.M == bind(f.M, A, F5), 'complete actual five-stage phase binding')
    need(F.mm(f.M, f.Mi) == F.mm(f.Mi, f.M) == F.eye(6),
         'free noncommuting operator word has both literal inverse orders')
    need(A.mm(p.M, p.Mi) == A.mm(p.Mi, p.M) == A.eye(6),
         'actual all-six-column word has both literal inverse orders')
    need(replay(p.events, A) == p.M and replay(p.events, A, True) == p.Mi,
         'serialized actual events and their exact reversed inverses bind')
    public, pivots = [0, 2, 4, 5], [1, 3]
    for bank in public:
        need(f.M[bank] == [F.N if j == bank else F.Z for j in range(6)],
             'every arbitrary public row is N times its own original input')
        need(p.M[bank] == [E if j == bank else A.Z for j in range(6)],
             'every public field receives all six actual native planes')
    H = [[f.M[i][j] for j in pivots] for i in pivots]
    L = [[f.M[i][j] for j in public] for i in pivots]
    histogram = Counter(event['native_arity'] for event in p.events if event['kind'] == 'NATIVE')
    need(histogram == {2: 34}, 'complete prefix is exactly 34 rank-2f native queries')
    need(build(True)[0].M != p.M, 'wrong current-source fanout sign changes all-column target')
    need(build(skip_progress=True)[0].M != p.M,
         'omitted fresh progress on handoff public c2 is detected')
    need(A.mm(replay(p.events[:-1], A, True), p.M) != A.eye(6),
         'omitted last inverse ADD is detected with arbitrary input columns')
    scans = Counter(event['kind'] for event in p.events)
    return dict(
        status='PASS_EXACT_FIVE_STAGE_MID_QUERY_HANDOFF_PREFIX', no_new_kappa=True,
        scientific_pin='20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        domain='Every f>=1; six arbitrary independent fields; actual common/fresh native planes N_i with N_i^2=-I and exact plane-permutation covariance. Formal retarded proof allows arbitrary invertible noncommuting P1,...,P5.',
        banks=['a', 't', 'b1', 'c1', 'b2', 'c2'],
        public_rows=public, pivot_rows=pivots,
        query_stages=5, actual_native_planes=6, ambient_arity_in_units_f=12,
        native_histogram_in_units_f=dict(histogram), native_rank_mass_in_units_f=68,
        stock_if_two_pivots_finish_in_units_f=72, D_before_pivot_tail_in_units_f=4,
        prefix_only=True, source_continuation_stages=[3], shared_entrance_N_calls=2,
        final_standalone_N_calls=1, nonrecursive_event_counts=dict(scans),
        source_retractions_first_three=source_rows,
        events=p.events, complete_formal_matrix=F.sm(f.M), complete_formal_inverse=F.sm(f.Mi),
        pivot_H=F.sm(H), public_L=F.sm(L),
        complete_physical_matrix=[[A.serial(x) for x in row] for row in p.M],
        complete_physical_inverse=[[A.serial(x) for x in row] for row in p.Mi],
        current_cut_formal_matrix=F.sm(cut),
        current_cut_physical_matrix=[[A.serial(x) for x in row] for row in cut_physical],
        cut_contract='In the retarded F3 frame (a,t,b1,c1,b2,c2)=(a,u+C,N*x-v,N*u+a+B,B,-v-N*(a+B)); all six coordinates (a,x,B,C,u,v) are independent. They are derived from the full current word, not initialized helpers.',
        handoff_endpoint_before_final_N='In F5 coordinates (a,P4*u,N*(x+a),P5*(N*v-a),N*B,N*C). Then N(a); b1-=a completes all four public rows.',
        exact_inverse='Reverse every serialized event; negate ADD coefficients, invert every Gaussian native/ADDRESS word, keep each bank SWAP. Both orders are checked on all six independent columns.',
        all_f_phase='N_f=i^(1-f) N1^tensor(f)=i Hp_f Hq_f, so N_f^2=-I. Disjoint planes commute and the literal ADDRESS swap satisfies P_i N_0=N_i P_i. These exact relations prove the serialized identity for every f>=1, including Gaussian global phases.',
        negative_controls=['Wrong pre-P5 current-source fanout sign', 'Omit fresh N4 progress on the new public c2', 'Omit the last inverse ADD'],
        attribution=['First-three-query nested-response entrance and its cut: mixed_carrier_caller_1019/caller/nested_prefix.py and nested_six.py.',
                     'Mid-query source handoff: root/root-chronology/source_handoff.py.',
                     'Second handoff and pre-P5 current-source fanout: independently derived by q4_pauli_fusion and stabilizer_escape_1019; final standalone N(a) closure proposed by root.',
                     'This file composes these mechanisms into the complete changed five-stage arbitrary-column prefix.'],
        limits=['The two pivot rows have not been compensated here. The 34-query invoice is a prefix invoice; an H/L tail must be added.',
                'This six-bank construction is exact; a recursive all-size response-sharing stage and bounded terminal cocycle are separate obligations.',
                'All scalar ADDs, bank SWAPs, ADDRESS permutations and native source/fresh scans are explicit. Native adapter and physical tape/precision/owner costs must be imported only under the actual caller interface.',
                'No whole multiplication theorem, formal-kernel result, or improved kappa is claimed.'],
        source_pins=[dict(path=str(CALLER / name), sha256=hashlib.sha256((CALLER / name).read_bytes()).hexdigest())
                     for name in ['free_ops.py', 'plane_group.py', 'nested_prefix.py', 'nested_six.py']])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = prove()
    out['producer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out = json.loads(json.dumps(out))
    path = HERE / 'SOURCE-HANDOFF-PREFIX.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved prefix receipt differs')
    print(out['status'], out['native_histogram_in_units_f'], 'prefix mass68f stock72f D4f; tail pending')


if __name__ == '__main__':
    main()
