#!/usr/bin/env python3
"""Check feedback through the original forward native helper-query bank.

PR5388 supplies the basis, wrappers and return completions. All eight original
centers remain. Ali Romman, substantial OpenAI Codex assistance; Apache-2.0.
This is a local interface, not a closed caller or a kappa certificate.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PIN = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
PROFILE = {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}
QSYM = 1000000
KBASE = 10000


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    sys.modules[name] = out
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), out.__dict__)
    return out


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for record in manifest['files']:
        if record['usage'] == 'input':
            path = ROOT / record['path']
            need(sha256(path.read_bytes()).hexdigest() == record['sha256'],
                 'Changed live source: ' + record['path'])


authenticate()
ce = module('feedback_clifford', ROOT / 'research/coded-native-caller/clifford_exact.py')
core = module('feedback_native', ROOT / 'research/native-center-free-code/native_core.py')


def literal(word):
    out = ce.ident(9)
    for e in word:
        if e[0] == 'P':
            part = ce.perm(9, tuple(e[1]))
        elif e[0] == 'D':
            part = ce.diag(9, tuple(e[1]), tuple(e[2]))
        elif e[0] == 'X':
            part = ce.xgate(9, e[1])
        elif e[0] == 'phase':
            part = ce.Op(9, ce.identity(9), [tuple(e)])
        elif e[0] == 'C':
            part = ce.cgate(9, e[1], e[2])
        else:
            raise ValueError('Unknown physical word')
        out = out.then(part)
    return out


def equal(a, b):
    return a.tab == b.tab and a.zero_state() == b.zero_state()


def prepend(row, symbol):
    out = {}
    for (owner, word), coefficient in row.items():
        if word and word[0] == -symbol:
            word = word[1:]
        else:
            word = (symbol,) + word
        if word[:4] == (QSYM,) * 4:
            word = word[4:]
        key = (owner, word)
        out[key] = out.get(key, F()) + coefficient
    return {key:value for key,value in out.items() if value}


def act(row, *symbols):
    for symbol in reversed(symbols):
        row = prepend(row, symbol)
    return row


def scalar_program(program, rows, owners):
    for op in program:
        dst = owners[op[1]]
        if op[0] == 'add':
            core.add(rows[dst], rows[owners[op[2]]], F(op[3]))
        else:
            need(op[0] == 'scale' and F(op[2]), 'Nonzero scalar basis SCALE')
            rows[dst] = {key:F(op[2])*v for key,v in rows[dst].items()}


def original_departures(source, bank):
    c = source['canonical']
    rows = [core.identity(i) for i in range(633)]
    first = {}
    cold = bank['cold_helper_owners']
    ci = {owner:i for i,owner in enumerate(cold)}
    for event, e in enumerate(source['programs']['forward']):
        if e[0] == 'climb' and e[2] in ci and e[2] not in first:
            owner = e[2]
            expected = {(cold[j], ()):F(a) for j,a in bank['T_rows'][ci[owner]]}
            need(e[3] == 0 and rows[owner] == expected, 'Original uncoded first-departure row')
            first[owner] = event
        if e[0] == 'scalar':
            gate = e[1]
            dst = gate[1][1] + (632 if gate[1][0] == 'C' else 0)
            if gate[0] == 'clear':
                need(dst == 632, 'No persistent CLEAR')
                rows[dst] = {}
            elif gate[0] == 'copy':
                src = gate[2][1] + (632 if gate[2][0] == 'C' else 0)
                need(dst == 632, 'No persistent COPY')
                rows[dst] = rows[src].copy()
            elif gate[0] == 'add':
                src = gate[2][1] + (632 if gate[2][0] == 'C' else 0)
                core.add(rows[dst], rows[src], F(gate[3], gate[4]))
            else:
                need(gate[0] == 'scale', 'Known scalar operation')
                rows[dst] = {key:F(gate[2],gate[3])*v for key,v in rows[dst].items()}
        elif e[0] == 'warp':
            owner = e[1][1] + (632 if e[1][0] == 'C' else 0)
            rows[owner] = core.warp(rows[owner], e[2], False)
    need(len(first) == 358, 'Every cold first departure')
    for owner in range(632):
        need(rows[owner] == core.expected(owner, False), 'Original FULL endpoint')
    need(not rows[632], 'Original owned center cleanup')
    for q in bank['queries']:
        need(first[q['native_role']] == q['source_event'], 'Selected original event index')
    return len(first)


def check_physics(source, bank):
    c = source['canonical']
    Q = ce.cgate(9, 1)
    Q2 = Q.then(Q)
    R = ce.fourier(9)
    need(equal(Q2, ce.xgate(9, 1)), 'Q squared is the exact Pauli X')
    for q in bank['queries']:
        K, O = literal(q['input_K']['word']), literal(q['response']['word'])
        E = ce.canonical_frame(9, c['frames'][q['first_chart']])
        need(equal(K.then(E).then(O), Q), 'Absolute phase of relocated query')
        need(equal(K.then(R).then(K.adjoint()), R), 'Full return K commutator')
        need(equal(Q2.then(O.adjoint()), Q.then(K).then(E)), 'Physical raw feedback identity')
        for op in (K, O, K.adjoint().then(Q2), O.adjoint()):
            need(ce.rank([x for x,z,p in op.tab[9:]]) == 0, 'Feedback map has no Gaussian call')
            compiled, _ = ce.monomial(op)
            need(equal(compiled, op), 'Feedback monomial absolute phase')
            need(all(e[0] in ('P','D','X','phase') for e in compiled.circuit), 'Literal monomial operations only')
    for completion in bank['cold_completions']:
        role = completion['native_role']
        need(c['final'][role] == completion['final_chart'], 'Completion source chart')
        frame = ce.canonical_frame(9, c['frames'][completion['final_chart']])
        compiled = literal(completion['operator']['word'])
        need(equal(frame.then(compiled), R), 'Completed return absolute phase')
        rank = 9 - len(c['frames'][completion['final_chart']])
        need(rank == completion['charged_child_rank'], 'Completion paid rank')
        gates = [e for e in compiled.circuit if e[0] == 'C']
        need(gates == [('C', 1 << i, 1) for i in range(rank)], 'One positive completion child')
        positions = [i for i, e in enumerate(compiled.circuit) if e[0] == 'C']
        need(positions == list(range(positions[0], positions[0] + rank)), 'Contiguous completion child')
    return {'query_identities': len(bank['queries']), 'completion_identities': len(bank['cold_completions'])}


def run(source, bank, feedbacks, mutation=None):
    c, queries = source['canonical'], bank['queries']
    owners = bank['cold_helper_owners']
    raw_start, obs_start, scratch = 633, 745, 857
    owned = 225 + bool(feedbacks)
    rows = [core.identity(i) for i in range(632 + owned)]
    charts = c['start'][:] + [None] * owned
    paid, ordinary = Counter(), Counter()
    expected_helpers = [core.identity(i) for i in range(632)]
    for h, k in feedbacks:
        need(0 <= h < 112 and 0 <= k < 112 and h != k, 'Distinct valid feedback coordinates')
        core.add(expected_helpers[queries[k]['native_role']],
                 act(expected_helpers[queries[h]['native_role']], QSYM), F(1))

    def clear(slot, chart):
        need(slot >= 632, 'No persistent erasure')
        rows[slot], charts[slot] = {}, chart
        ordinary['owned_clear'] += 1

    def copy(dst, src):
        need(dst >= 633 and not rows[dst], 'Owned COPY needs a cleared target')
        rows[dst], charts[dst] = rows[src].copy(), charts[src]
        ordinary['owned_copy'] += 1

    for q in queries:
        j, owner = q['query_index'], q['native_role']
        rows[owner] = act(rows[owner], KBASE+j)
        rawslot, obs = raw_start+j, obs_start+j
        clear(rawslot, 0)
        copy(rawslot, owner)
        event = source['programs']['forward'][q['source_event']]
        need(event[0] == 'climb' and event[2:] == [owner,0,q['first_chart'],1], 'Exact relocated native H1')
        charts[rawslot] = q['first_chart']
        paid[1] += 1
        clear(obs, q['first_chart'])
        copy(obs, rawslot)
        rows[obs] = act(core.identity(owner), QSYM)
        charts[obs] = 0

    def invariant(j):
        q = queries[j]
        w, r, o = rows[q['native_role']], rows[raw_start+j], rows[obs_start+j]
        need(w == r, 'Held raw argument matches current helper coordinate')
        need(o == act(w, QSYM, -(KBASE+j)), 'Observation matches current helper coordinate')
        need(charts[raw_start+j] == q['first_chart'], 'Held raw physical chart')

    for index, (h, k) in enumerate(feedbacks):
        for j in (h,k):
            invariant(j)
        wh, wk = queries[h]['native_role'], queries[k]['native_role']
        if not (mutation == "dirty_scratch" and index == 0):
            clear(scratch, 0)
        copy(scratch, obs_start+h)
        rows[scratch] = act(rows[scratch], KBASE+k)
        ordinary['monomial_map'] += 1
        core.add(rows[wk], rows[scratch], F(1))
        ordinary['scalar_add'] += 1
        clear(scratch, 0)
        copy(scratch, wh)
        symbols = (QSYM, -(KBASE+h)) if mutation == "one_Q" and index == 0 else (QSYM, QSYM, -(KBASE+h))
        rows[scratch] = act(rows[scratch], *symbols)
        ordinary['monomial_map'] += 1
        if not (mutation == "stale_observation" and index == 0):
            core.add(rows[obs_start+k], rows[scratch], F(1))
        ordinary['scalar_add'] += 1
        # The exact physical identity above changes the declared chart here.
        rows[scratch] = act(rows[wh], KBASE+k, QSYM, -(KBASE+h))
        charts[scratch] = queries[k]['first_chart']
        ordinary['monomial_map'] += 1
        if not (mutation == "stale_raw" and index == 0):
            core.add(rows[raw_start+k], rows[scratch], F(1))
        ordinary['scalar_add'] += 1
        if not (mutation == "live_scratch" and index == len(feedbacks) - 1):
            clear(scratch, 0)
        for j in (h,k):
            invariant(j)

    for q in queries:
        actual = act(rows[q['native_role']], -(KBASE+q['query_index']))
        need(actual == expected_helpers[q['native_role']], 'Independent elementary feedback endpoint')
    desired = [row.copy() for row in rows[:632]]
    scalar_program(bank['entrance_scalar_program'], rows, owners)
    entered = [row.copy() for row in rows[:632]]
    by_event = {q['source_event']:q for q in queries}
    cuts = 0
    for event_index, e in enumerate(source['programs']['forward']):
        if event_index in by_event:
            q = by_event[event_index]
            owner, rawslot = q['native_role'], raw_start+q['query_index']
            need(charts[owner] == 0 and charts[rawslot] == q['first_chart'], 'Replacement charts')
            need(rows[owner] == rows[rawslot], 'Replacement row on all original and owned inputs')
            rows[owner], rows[rawslot] = rows[rawslot], rows[owner]
            if not (mutation == 'chart_swap' and cuts == 0):
                charts[owner], charts[rawslot] = charts[rawslot], charts[owner]
            need(charts[owner] == q['first_chart'] and charts[rawslot] == 0, 'Replacement chart transport')
            ordinary['physical_field_swap'] += 1
            clear(rawslot, 0)
            cuts += 1
            continue
        kind = e[0]
        if kind == 'scalar':
            gate, chart = e[1:]
            dst = gate[1][1]+(632 if gate[1][0] == 'C' else 0)
            if gate[0] == 'clear':
                need(dst == 632, 'Native persistent erasure')
                rows[dst], charts[dst] = {}, chart
                continue
            need(charts[dst] == chart, 'Native scalar destination chart')
            if gate[0] in ('copy','add'):
                src = gate[2][1]+(632 if gate[2][0] == 'C' else 0)
                need(charts[src] == chart, 'Native scalar source chart')
                if gate[0] == 'copy':
                    need(dst == 632, 'Native persistent overwrite')
                    rows[dst] = rows[src].copy()
                else:
                    core.add(rows[dst], rows[src], F(gate[3],gate[4]))
            else:
                need(gate[0] == 'scale', 'Known native scalar')
                rows[dst] = {key:F(gate[2],gate[3])*v for key,v in rows[dst].items()}
        elif kind == 'warp':
            _, ref, op, before, after = e
            owner = ref[1]+(632 if ref[0] == 'C' else 0)
            need(charts[owner] == before, 'Native warp chart')
            rows[owner], charts[owner] = core.warp(rows[owner], op, False), after
        elif kind in ('climb','center'):
            if kind == 'climb':
                _,_,owner,before,after,rank = e
                need(rank == len(c['frames'][after])-len(c['frames'][before]), 'Native climb rank')
            else:
                _,index,before,after,rank = e
                owner = 632+index
                need(rank == abs(len(c['frames'][after])-len(c['frames'][before])), 'Native center rank')
            need(charts[owner] == before, 'Native paid chart')
            charts[owner] = after
            paid[rank] += 1
        else:
            need(kind in ('phase','adapter','residual_adapter'), 'Known native marker')
    for owner in range(632):
        expected = entered[owner].copy()
        if 112 <= owner < 224:
            core.add(expected, entered[owner-112], F(1))
        need(rows[owner] == expected, 'Complete original FULL endpoint on transformed helper inputs')
    need(charts[:632] == c['final'], 'Original final charts')
    need(paid == Counter(PROFILE), 'All original Gaussian children, including eight centers')
    for index, completion in enumerate(bank['cold_completions']):
        if mutation == 'missing_completion' and index == 0:
            continue
        charts[completion['native_role']] = 1
        paid[completion['charged_child_rank']] += 1
    need(all(charts[owner] == 1 for owner in owners), 'Common return chart before scalar decoding')
    scalar_program(bank['exit_scalar_program'], rows, owners)
    for q in queries:
        owner, j = q['native_role'], q['query_index']
        rows[owner] = act(rows[owner], -(KBASE+j))
        desired[owner] = act(desired[owner], -(KBASE+j))
    for owner in owners:
        need(rows[owner] == desired[owner] == expected_helpers[owner], 'Returned transformed helper after completion and decode')
    for q in queries:
        j = q['query_index']
        need(rows[obs_start+j] == act(desired[q['native_role']], QSYM), 'Retained normalized feedback observation')
        clear(obs_start+j, 0)
    need(all(not row for row in rows[632:]), 'Every arbitrary owned input removed and every owned output cleared')
    n = len(feedbacks)
    need(ordinary == Counter(owned_clear=448+3*n, owned_copy=224+2*n,
                            physical_field_swap=112, scalar_add=3*n, monomial_map=3*n), 'Complete added ordinary invoice')
    return dict(status='PASS_UNCODED_FORWARD_EARLY_QUERY_FEEDBACK',
                source_payload_sha256=PIN,
                original_inputs=632, arbitrary_owned_inputs=owned, replacement_cuts=cuts,
                feedbacks=feedbacks, completed_paid=dict(sorted(paid.items())),
                helper_output_ranks_on_transformed_coordinates={4:2,7:7,8:41,9:358},
                ordinary=ordinary, all_owned_outputs_zero=True,
                source_scope='Original forward FULL, all eight centers retained.',
                target_scope='Helpers return on the transformed independent coordinates. A closed caller must prove its target.',
                fixed_basis_adds=6420, fixed_basis_scales=408,
                fixed_monomial_maps_at_most=400, additional_owned_fields=224 + bool(feedbacks),
                limitation='Forward interface only. No caller closure, complete precision tariff, or kappa improvement is claimed.')


def produce():
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == PIN, 'Pinned native payload')
    source = json.loads(raw)
    bank = json.loads((ROOT / 'research/native-helper-query-bank/BANK.json').read_text())
    first = original_departures(source, bank)
    physics = check_physics(source, bank)
    feedbacks = [(0,1), (1,0), (1,2), (2,111), (111,0)]
    result = run(source, bank, feedbacks)
    result['first_departure_rows_checked'] = first
    result['physical_checks'] = physics
    result['empty_sequence_control'] = run(source, bank, [])['ordinary']
    controls = []
    for mutation, expected in [
        ('stale_raw', 'Held raw argument matches current helper coordinate'),
        ('stale_observation', 'Observation matches current helper coordinate'),
        ('one_Q', 'Observation matches current helper coordinate'),
        ('chart_swap', 'Replacement chart transport'),
        ('dirty_scratch', 'Owned COPY needs a cleared target'),
        ('live_scratch', 'Every arbitrary owned input removed and every owned output cleared'),
        ('missing_completion', 'Common return chart before scalar decoding'),
    ]:
        try:
            run(source, bank, feedbacks, mutation)
        except ValueError as exc:
            need(str(exc) == expected, 'Wrong mutation rejection: ' + mutation + ': ' + str(exc))
            controls.append({'mutation': mutation, 'result': 'REJECT', 'reason': str(exc)})
        else:
            raise ValueError('Mutation passed: ' + mutation)
    result['rejected_controls'] = controls
    comparator = module('feedback_invoice', ROOT / 'scripts/compare_recursive_invoices.py')
    old = json.loads((HERE / 'SOURCE-INVOICE.json').read_text())
    new = json.loads((HERE / 'COMPLETION-INVOICE.json').read_text())
    old_helpers = Counter(len(source['canonical']['frames'][source['canonical']['final'][j]]) -
                          len(source['canonical']['frames'][source['canonical']['start'][j]])
                          for j in range(224, 632))
    need({int(r): n for r, n in old['paid'].items()} == PROFILE, 'Source invoice paid profile')
    need({int(r): n for r, n in old['targets'].items()} == old_helpers, 'Source invoice helper profile')
    need({int(r): n for r, n in new['paid'].items()} == result['completed_paid'], 'Completion invoice paid profile')
    need({int(r): n for r, n in new['targets'].items()} == result['helper_output_ranks_on_transformed_coordinates'],
         'Completion invoice helper profile before feedback')
    comparison = comparator.compare_invoices(old, new)
    need(comparison['classification'] == 'uniformly_worse', 'Completion is a strict concave-moment loss')
    need(comparison['rank_mass']['delta']['paid'] == comparison['rank_mass']['delta']['targets'] == 136,
         'Completion paid and target rank-mass change')
    result['completion_invoice_preflight'] = comparison
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='Write the result for package authors.')
    args = parser.parse_args()
    result = produce()
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    path = HERE / 'RESULT.json'
    if args.emit:
        path.write_text(payload)
    else:
        expected = json.dumps(json.loads(path.read_text()), sort_keys=True, indent=2) + '\n'
        need(payload == expected, 'Saved typed mathematical receipt differs')
    print(result['status'], json.dumps({'original_inputs': result['original_inputs'],
          'owned_inputs': result['arbitrary_owned_inputs'], 'replacement_cuts': result['replacement_cuts'],
          'feedback_shears': len(result['feedbacks']), 'rejected_controls': len(result['rejected_controls'])}, sort_keys=True))


if __name__ == '__main__':
    main()
