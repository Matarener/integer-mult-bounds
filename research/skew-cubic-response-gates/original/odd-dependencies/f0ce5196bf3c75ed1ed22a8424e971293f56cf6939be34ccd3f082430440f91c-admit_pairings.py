#!/usr/bin/env python3
"""Admit four full-stock ADD-pairing certificates from literal source events.
Apache-2.0. Substantial OpenAI Codex assistance. No supplier/kappa admission.
"""
from pathlib import Path
import argparse, copy, hashlib, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pairing_search as search
t = search.t


def direct_crossed(events, n, m, crossings, omit_swap=None):
    """Independent event replay without graph nodes or edge IDs."""
    order = list(range(n))
    op = [t.ce.ident(m) for _ in range(n)]
    extra = [(0,)*4 for _ in range(n)]
    source_ordinals = [[] for _ in range(n)]
    for ordinal, e in enumerate(events):
        kind = e['kind']
        do_swap = kind == 'BANK_SWAP' and ordinal != omit_swap
        if kind == 'ADD' and ordinal in crossings:
            i, j = e['dst'], e['src']
            do_swap = True
        elif kind == 'BANK_SWAP':
            i, j = e['banks']
        if do_swap:
            order[i], order[j] = order[j], order[i]
            op[i], op[j] = op[j], op[i]
            extra[i], extra[j] = extra[j], extra[i]
            source_ordinals[i], source_ordinals[j] = source_ordinals[j], source_ordinals[i]
        elif kind not in ('ADD', 'BANK_SWAP', 'SCALE'):
            g, p = t.unary(e, m)
            b = e['bank']
            op[b] = op[b].then(g)
            extra[b] = t.add_phase(extra[b], p)
            source_ordinals[b] = source_ordinals[b] + [ordinal]
    result = [None] * n
    for bank, label in enumerate(order):
        result[label] = dict(final_bank=bank, op=op[bank], extra=extra[bank], source_ordinals=source_ordinals[bank])
    return result


def fixture(family, q):
    source = 'inputs/REPAIRED-SIMPLIFIED.json' if family == 'REPAIRED' else 'inputs/ADMITTED-TWO-SITE.json'
    f = next(f for f in json.loads((search.OLD / source).read_text())['fixtures'] if f['q'] == q)
    events = f.get('full_events', f['events'])
    n, m = f['banks'], f['ambient_arity']
    proposal_file = HERE / (family + '-Q' + str(q) + '-PROPOSAL.json')
    proposal = json.loads(proposal_file.read_text())
    t.need(proposal['producer_sha256'] == t.digest(HERE / 'pairing_search.py'), 'proposal source pin')
    add_ordinals = [i for i, e in enumerate(events) if e['kind'] == 'ADD']
    t.need(add_ordinals == proposal['ADD_event_ordinals'], 'all ADD ordinals pinned in chronological order')
    mask = int(proposal['mask'])
    crossings = [ordinal for bit, ordinal in enumerate(add_ordinals) if mask >> bit & 1]
    t.need(crossings == proposal['crossing_ADD_event_ordinals'], 'bitmask means exactly the saved ADD crossings')
    t.need(mask < (1 << len(add_ordinals)), 'pairing mask has no unbound bits')
    E, P, owner, nodes = t.graph_paths(events, n, m, crossing_adds=crossings)
    H = t.check_partition(E, P, n, m)
    direct = direct_crossed(events, n, m, set(crossings))
    phase_vectors = []
    paths = []
    for i, ((op, extra, rank), expected) in enumerate(zip(H, direct)):
        g = expected['op']
        t.need(op.tab == g.tab, 'independent direct signed crossed-strand product')
        t.need(t.stable(op.circuit) == t.stable(g.circuit), 'independent direct literal circuit and global phase order')
        t.need(extra == expected['extra'], 'all-f global tensor phase polynomial agrees')
        t.need(rank == m, 'every path holonomy is full native ambient arity')
        t.need(owner[expected['final_bank']] == i, 'crossed trajectory endpoint identity')
        source_list = [ordinal for eid in P[i] for ordinal in E[eid]['source_event_ordinals']]
        t.need(source_list == expected['source_ordinals'], 'every actual source unary appears in the right ordered strand')
        for product in (op.then(op.adjoint()), op.adjoint().then(op)):
            t.need(product.tab == t.ce.identity(m), 'holonomy literal inverse every signed Pauli column, both orders')
        phase_vectors.append(extra)
        paths.append(dict(initial_bank=i, final_bank=expected['final_bank'], edges=P[i],
                          source_unary_event_ordinals=source_list,
                          native_holonomy_arity_per_f=rank, one_coordinate_tableau=op.tab,
                          one_coordinate_literal_circuit=op.circuit,
                          extra_global_phase_exponent_by_f_mod4=extra,
                          literal_inverse_circuit=op.adjoint().circuit,
                          inverse_extra_global_phase_exponent_by_f_mod4=[(-x) % 4 for x in extra]))

    # The proposal evaluator is not trusted as the admission engine.
    mm, nn, prepared, expected_ordinals = search.prepare(f)
    fast, fast_ranks = search.evaluate(mask, mm, nn, prepared)
    t.need(fast == m*n and fast_ranks == [m]*n, 'independent fast score agrees after literal admission')
    zeroE, zeroP, _, _ = t.graph_paths(events, n, m)
    straight = sum(item[2] for item in t.check_partition(zeroE, zeroP, n, m))
    t.need(straight < m*n, 'all-straight mutant fails the full-stock witness target')

    bad = copy.deepcopy(P)
    bad[0] = bad[0][1:]
    try:
        t.check_partition(E, bad, n, m)
    except ValueError as error:
        omitted = str(error)
    else:
        raise ValueError('omitted edge passed new certificate')
    wrong_swap = None
    for ordinal, e in enumerate(events):
        if e['kind'] != 'BANK_SWAP':
            continue
        mutant = direct_crossed(events, n, m, set(crossings), omit_swap=ordinal)
        if any(x['op'].tab != y['op'].tab or t.stable(x['op'].circuit) != t.stable(y['op'].circuit)
               or x['extra'] != y['extra'] or x['final_bank'] != y['final_bank']
               for x, y in zip(direct, mutant)):
            wrong_swap = ordinal
            break
    t.need(wrong_swap is not None, 'an actual omitted BANK_SWAP transport changes the direct witness')

    mass = sum(e['rank_per_f'] for e in events if e['kind'] == 'NATIVE')
    stock = f.get('stock', n*m)
    t.need(stock == n*m and proposal['best_floor'] == stock, 'unchanged full-native old endpoint stock')
    return dict(family=family, q=q, banks=n, ambient_arity=m, stock=stock, original_native_mass=mass,
                source_path=str(search.OLD / source), source_sha256=t.digest(search.OLD / source),
                source_events_sha256=hashlib.sha256(t.stable(events).encode()).hexdigest(),
                proposal=dict(path=proposal_file.name, sha256=t.digest(proposal_file), trials=proposal['trials']),
                pairing_bitstring_chronological=''.join('1' if mask >> bit & 1 else '0' for bit in range(len(add_ordinals))),
                pairing_mask_decimal=str(mask), ADD_event_ordinals=add_ordinals,
                crossing_ADD_event_ordinals=crossings, graph_nodes=nodes, graph_edges=len(E),
                complete_edge_partition=True, independently_replayed_literal_circuits_and_tensor_phases=True,
                straight_floor_per_f=straight, admitted_floor_per_f=stock,
                trajectory_ranks_per_f=[m]*n, edges=E, trajectories=paths,
                negative_controls=dict(all_straight_target_rejected=dict(floor=straight, required=stock),
                                       omitted_edge_rejected=omitted,
                                       omitted_actual_BANK_SWAP_direct_transport_rejected_at_event=wrong_swap))


def produce():
    t.pin_inputs()
    fixtures = [fixture(family, q) for family in ['REPAIRED', 'TWO-SITE'] for q in [2, 3]]
    return dict(status='PASS_FOUR_EXACT_FULL_STOCK_PATH_PAIRING_CERTIFICATES', no_new_kappa=True,
                producer_sha256=t.digest(__file__), search_producer_sha256=t.digest(HERE / 'pairing_search.py'),
                frozen_trajectory_proof_sha256=t.digest(search.OLD / 'TRAJECTORY-PROOF.md'),
                frozen_trajectory_producer_sha256=t.digest(search.OLD / 'trajectory_certificate.py'),
                frozen_trajectory_manifest_sha256=t.digest(search.OLD / 'MANIFEST.json'),
                theorem='For each fixed listed unary/common-frame ADD graph, every Clifford-frame retiming has native rank mass at least stock (72f or128f).',
                domain='The four finite q2/q3 words, all positive f; arbitrary general Clifford frames can mix tensor coordinates.',
                fixtures=fixtures,
                limits=['Exact witness, not an exhaustive pairing search or a global caller lower bound.',
                        'The path certificate reaches the maximum possible sum n*m, but source native bills80/136 and76/132 are not certified minimal.',
                        'Native query recipes and original all-input caller/inverse semantics remain those of the unchanged source artifacts; no new supplier or endpoint is introduced.',
                        'Changed unary holonomies, nonlocal ADD/native chronology, new helper coupling or changed physical input/output contracts need a new certificate.',
                        'No all-q, positive-exponent moment, BIT, owner, storage, precision or kappa admission.'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    result = json.loads(json.dumps(produce()))
    output = HERE / 'FULL-STOCK-CERTIFICATES.json'
    if a.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        t.need(json.loads(output.read_text()) == result, 'saved stronger pairing certificate')
    print(result['status'])
    for f in result['fixtures']:
        print(f['family'], 'q'+str(f['q']), 'floor', f['admitted_floor_per_f'], 'mass', f['original_native_mass'],
              'paths', f['trajectory_ranks_per_f'])


if __name__ == '__main__':
    main()
