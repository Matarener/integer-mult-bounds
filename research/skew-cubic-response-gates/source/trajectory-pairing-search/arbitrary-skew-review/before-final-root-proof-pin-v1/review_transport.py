#!/usr/bin/env python3
"""Independent suffix transport and full occurrence inventory for the skew gate.
Apache-2.0. Substantial OpenAI Codex assistance. No supplier admission.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R = HERE.parents[1]
PINS = {
    'caller-joint/joint_prefix.py': 'a4dcaa1ad05ef8dbba60ddd47b3ad44a3095ebb5fd31f6adfb935a7b1c46a2c7',
    'caller-joint/joint_algebra.py': '5782033e347c9b10ad47c01ed12a0a52ea07e901fa9e8f7aa9d3a2a928327232',
    'root-joint/arbitrary_skew_gate.py': '252acc46613f3d843ae26fc515b40f664523d23403236597de1a52fc306f5706',
    'root-joint/ARBITRARY-SKEW-GATE.json': '35cc85e2908e260226fd34a0d8dafafa5f34988db6cd70a87b9e74520ecb85a4',
    'root-joint/ARBITRARY-SKEW-GATE-PROOF.md': '93c4a3eae94df219ef3b8c3fb1b9434c2d8ccdef4d335a64de07169929dda43a',
    'folded-fusion/SIMPLIFIED-FUSIONS.json': '4491cfe2a1f3e48510b33403b9b50c704865c3b1dc6d659ef5157840654e8fc3',
}
for relative, h in PINS.items():
    if hashlib.sha256((R / relative).read_bytes()).hexdigest() != h:
        raise ValueError('source pin: ' + relative)
sys.path.insert(0, str(R / 'caller-joint'))
sys.path.insert(0, str(R / 'two-site-continuation'))
import joint_prefix as source
from joint_algebra import *
from two_site import pair_columns


class Recorder:
    """Record the pinned generator's syntax, without its full bank matrix."""
    def __init__(self, n, m):
        self.n, self.m, self.events = n, m, []
    def add(self, d, s, c=1, label=''):
        if c:
            self.events.append(dict(kind='ADD', dst=d, src=s, coefficient=str(c), label=label))
    def swap(self, i, j, label=''):
        self.events.append(dict(kind='BANK_SWAP', banks=[i, j], label=label))
    def unary(self, b, g, label='', native=False, family=None):
        self.events.append(dict(kind='NATIVE' if native else 'ADDRESS_OR_UNIT', bank=b,
                                x_monomial=g.data(), native_family=family, label=label))


def generate(q):
    old = source.Word
    source.Word = Recorder
    try:
        return source.build(q).events
    finally:
        source.Word = old


def embed(data, m):
    g = qc.Mono(tuple(data['rows']), data['offset'], tuple(data['alpha']), tuple(data['quad']),
                data['constant'], data['global_phase'])
    d = len(g.rows)
    return qc.Mono(g.rows + tuple(1 << i for i in range(d, m)), g.offset,
                   g.alpha + (0,)*(m-d), g.quad + (0,)*(m-d), g.constant, g.global_phase)


def converted(events, m, J):
    out = []
    for e in events:
        e = dict(e)
        fam = e.get('native_family')
        if fam and fam['kind'] == 'J':
            fs = prefix(m, fam['completed'])
            g = fs @ J @ fs.inv()
            if fam.get('inverse'):
                g = g.inv()
            e['x_monomial'] = g.data()
        out.append(e)
    return out


def event_equal(a, b, m):
    fields = ['kind', 'bank', 'dst', 'src', 'coefficient', 'banks', 'label', 'native_family']
    if any(a.get(k) != b.get(k) for k in fields):
        return False
    if a['kind'] not in ('ADD', 'SCALE', 'BANK_SWAP'):
        return mono(qc.decode(a, m)) == mono(qc.decode(b, m))
    return True


def produce():
    pinned = json.loads((R / 'root-joint/ARBITRARY-SKEW-GATE.json').read_text())
    # Two different actual wider-support families, including a nontrivial
    # address-conjugated skew response. The proof is the separate induction.
    choices = [pinned['fixtures'][0]['J'], pinned['fixtures'][2]['J']]
    current = json.loads((R / 'folded-fusion/SIMPLIFIED-FUSIONS.json').read_text())['fixtures']
    results = []
    for q in range(2, 9):
        events = generate(q)
        n, k, m = 2*q+2, 2*q+1, 4*q+4
        first = next(i for i, e in enumerate(events) if e['label'] == 'query3 source swap')
        if q in (2, 3):
            actual = next(f for f in current if f['q'] == q)['prefix_events']
            at = next(i for i, e in enumerate(actual) if e['label'] == 'query3 source swap')
            need(len(actual[at:]) == len(events[first:]), 'same literal suffix length after first changed site')
            need(all(event_equal(a, b, m) for a, b in zip(actual[at:], events[first:])),
                 'generated repeating suffix equals current repaired physical source')
        # The folded base removes precisely these two J occurrences before
        # the first changed site; adding final tail-J makes the complete list.
        counts = Counter()
        removed = {'shared initial J exposure', 'query2 source J'}
        n_prefix = 0
        for e in events:
            fam = e.get('native_family')
            if fam and fam['kind'] == 'N':
                n_prefix += 1
            if fam and fam['kind'] == 'J' and e['label'] not in removed:
                counts[fam['completed']] += 1
        counts[k] += 1
        expected = Counter({0: 2})
        expected.update({2*t: 1 for t in range(1, q+1)})
        expected.update({2*t+1: 2 for t in range(1, q+1)})
        need(counts == expected and sum(counts.values()) == 3*q+2, 'complete chronological J occurrence table')
        remaining = Counter(counts)
        for r in range(2, q+1):
            need(remaining[2*r-1] >= 1, 'every transport J has a distinct paid occurrence')
            remaining[2*r-1] -= 1
        need(sum(remaining.values()) == n+1, 'n+1 chronological J ranks remain after cancellation')
        need(n_prefix == k*(n-1), 'all original fresh calls retained')
        complete_N_calls = n_prefix + 1 + (q-1)
        need(2*complete_N_calls == n*(2*k-1), 'folded uniform source plus reverse-current readers complete N mass')
        for case, data in enumerate(choices):
            J = embed(data, m)
            minus = qc.Mono(qc.identity(m).rows, 0, (0,)*m, (0,)*m, 0, 2)
            need(mono(J @ J) == mono(minus), 'actual whole-field skew square')
            E = converted(events, m, J)
            T = plane_swap(m, 0, 4) @ prefix(m, 3) @ J @ prefix(m, 3).inv()
            checked = []
            for r in range(2, q+1):
                later = next(i for i, e in enumerate(E) if e['label'] == f'query{2*r} source swap')
                A, B = pair_columns(E, first, later, n, m)
                bank = E[later]['bank']
                need(bank == 1, 'actual later physical source bank is one')
                need(all(not A[i] and not B[i] for i in range(n) if i != bank), 'complete forward column and inverse row isolation')
                need(A[bank] == mono(T) and B[bank] == mono(T.inv()), 'generalized transport and exact inverse dual')
                # Closed L, including its minus sign, from the deleted tail.
                Du = qc.identity(m)
                N0i = n_pair(m, 0).inv()
                for t in range(2, r+1):
                    Du = plane_swap(m, 0, 2*t) @ N0i @ J @ Du
                Du = Du @ plane_swap(m, 0, 3) @ N0i @ J @ J
                Fe = prefix(m, 2*r)
                L = Fe @ Du.inv() @ Fe.inv() @ T @ plane_swap(m, 0, 3)
                closed = minus
                for s in range(3, 2*r+1):
                    closed = n_pair(m, s) @ closed
                need(mono(L) == mono(closed), 'all-sign closed L telescope without commuting J')
                checked.append(dict(r=r, bank=bank, T=serial(mono(T)), L=serial(mono(L)),
                                    isolated_column_and_inverse_row=True))
                if r < q:
                    odd = 2*r+1
                    Jo = prefix(m, odd) @ J @ prefix(m, odd).inv()
                    T = plane_swap(m, 0, 2*r+2) @ Jo @ n_pair(m, odd) @ T
            results.append(dict(q=q, case=case, suffix_source_bound=(q in (2, 3)),
                                complete_J_counts=dict(sorted(counts.items())), remaining_J_counts=dict(sorted(remaining.items())),
                                complete_N_calls=complete_N_calls, complete_N_mass=2*complete_N_calls,
                                all_even_cut_transport_checks=checked))
    return dict(status='PASS_INDEPENDENT_ALL_Q_TRANSPORT_INDUCTION_CORROBORATION_AND_INVENTORY', no_new_kappa=True,
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(R/p), sha256=h) for p, h in PINS.items()],
                fixtures=results,
                all_parameter_evidence='Written arbitrary-operator column/dual-row induction and exact L telescope in PROOF.md; finite generated source checks are separate.',
                scope='The pinned repeated suffix, fixed folded base count and Du removal/two-post replacement interface. No all-general-Clifford finite census or selected supplier/controller admission.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(produce()))
    output = HERE / 'TRANSPORT-REVIEW.json'
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(output.read_text()) == result, 'saved independent transport review')
    print(result['status'], 'finite q2..8, two wider-support actual skew kernels')


if __name__ == '__main__':
    main()
