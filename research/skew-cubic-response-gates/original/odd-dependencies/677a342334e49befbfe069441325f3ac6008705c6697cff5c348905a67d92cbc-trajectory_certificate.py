#!/usr/bin/env python3
"""Exact edge-partition lower bounds for a fixed common-frame ADD word.

Apache-2.0. Substantial OpenAI Codex assistance. No search or kappa claim.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import argparse, copy, hashlib, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'caller-joint'))
from joint_algebra import ce


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def pin_inputs():
    data = json.loads((HERE / 'INPUT-PINS.json').read_text())
    for pin in data['files']:
        p = Path(pin['source']) if pin.get('read_only_source') else HERE / pin['copy_relative']
        need(digest(p) == pin['sha256'], 'frozen input pin: ' + str(p))
    return data


@lru_cache(None)
def compile_literal(m, encoded):
    op = ce.ident(m)
    for gate in json.loads(encoded):
        kind = gate[0]
        if kind == 'P':
            g = ce.perm(m, tuple(gate[1]))
        elif kind == 'D':
            g = ce.diag(m, tuple(gate[1]), tuple(gate[2]))
        elif kind == 'C':
            need(gate[2] in (-1, 1), 'literal chirp direction')
            g = ce.cgate(m, gate[1], gate[2])
        elif kind == 'X':
            g = ce.xgate(m, gate[1])
        elif kind == 'phase':
            g = ce.Op(m, ce.identity(m), [tuple(gate)])
        else:
            raise ValueError('unsupported actual unary gate: ' + kind)
        op = op.then(g)
    return op


def unary(event, m):
    op = compile_literal(m, stable(event['one_coordinate_literal_circuit']))
    need(op.tab == tuple(tuple(t) for t in event['one_coordinate_tableau']), 'actual signed unary tableau')
    rank = ce.rank(x for x, z, phase in op.tab[m:])
    need(rank == event['rank_per_f'], 'actual unary B-rank')
    need((event['kind'] == 'NATIVE') == bool(rank), 'native versus rank-zero event kind')
    extra = event.get('extra_global_phase_exponent_by_f_mod4')
    if extra is None:
        e = event['phase_exponent']
        extra = [e * (1 - r) % 4 for r in range(4)]
    need(len(extra) == 4, 'explicit all-f scalar phase')
    return op, tuple(x % 4 for x in extra)


def columns(op):
    return tuple(x | (z << op.n) for x, z, phase in op.tab)


def rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            p = value.bit_length() - 1
            if p in basis:
                value ^= basis[p]
            else:
                basis[p] = value
                break
    return len(basis)


def linear(A, value):
    out = 0
    while value:
        bit = value & -value
        out ^= A[bit.bit_length() - 1]
        value -= bit
    return out


def distance(U, V, m):
    return rank(tuple(U) + tuple(V)) - m


def add_phase(a, b):
    return tuple((x + y) % 4 for x, y in zip(a, b))


def direct_paths(events, n, m):
    """Independent physical-label traversal: ADDs do not move a strand."""
    labels = list(range(n))
    ops = [ce.ident(m) for _ in range(n)]
    phases = [(0,) * 4 for _ in range(n)]
    for event in events:
        kind = event['kind']
        if kind == 'BANK_SWAP':
            i, j = event['banks']
            labels[i], labels[j] = labels[j], labels[i]
            ops[i], ops[j] = ops[j], ops[i]
            phases[i], phases[j] = phases[j], phases[i]
        elif kind not in ('ADD', 'SCALE'):
            op, extra = unary(event, m)
            b = event['bank']
            ops[b] = ops[b].then(op)
            phases[b] = add_phase(phases[b], extra)
    out = [None] * n
    for bank, label in enumerate(labels):
        out[label] = (bank, ops[bank], phases[bank])
    return out


def graph_paths(events, n, m, omit_swap=None, crossing_adds=()):
    """Every ADD is a common-frame node; optionally cross its two strands."""
    at = [0] * n
    owner = list(range(n))
    pending = [ce.ident(m) for _ in range(n)]
    phases = [(0,) * 4 for _ in range(n)]
    unaries = [[] for _ in range(n)]
    paths = [[] for _ in range(n)]
    edges = []
    nodes = 1
    crosses = set(crossing_adds)

    def emit(bank, node):
        eid = len(edges)
        op = pending[bank]
        edges.append(dict(id=eid, u=at[bank], v=node, bank=bank,
                          one_coordinate_tableau=op.tab,
                          one_coordinate_literal_circuit=op.circuit,
                          extra_global_phase_exponent_by_f_mod4=phases[bank],
                          source_event_ordinals=unaries[bank],
                          rank_per_f=ce.rank(x for x, z, p in op.tab[m:])))
        paths[owner[bank]].append(eid)
        at[bank] = node
        pending[bank] = ce.ident(m)
        phases[bank] = (0,) * 4
        unaries[bank] = []

    for ordinal, event in enumerate(events):
        kind = event['kind']
        if kind == 'ADD':
            i, j = event['dst'], event['src']
            need(i != j, 'ADD operands distinct')
            emit(i, nodes)
            emit(j, nodes)
            nodes += 1
            if ordinal in crosses:
                owner[i], owner[j] = owner[j], owner[i]
        elif kind == 'BANK_SWAP':
            i, j = event['banks']
            at[i], at[j] = at[j], at[i]
            pending[i], pending[j] = pending[j], pending[i]
            phases[i], phases[j] = phases[j], phases[i]
            unaries[i], unaries[j] = unaries[j], unaries[i]
            if ordinal != omit_swap:
                owner[i], owner[j] = owner[j], owner[i]
        elif kind == 'SCALE':
            # Scalar field multiplication commutes with every address operator.
            # It is still counted as a paid whole-field scan, not a native child.
            pass
        else:
            op, extra = unary(event, m)
            b = event['bank']
            pending[b] = pending[b].then(op)
            phases[b] = add_phase(phases[b], extra)
            unaries[b] = unaries[b] + [ordinal]
    for bank in range(n):
        emit(bank, 0)
    return edges, paths, owner, nodes


def check_partition(edges, paths, n, m):
    need(len(paths) == n, 'one path per initial bank')
    need(sorted(e for path in paths for e in path) == list(range(len(edges))), 'partition covers every graph edge once')
    result = []
    for path in paths:
        op = ce.ident(m)
        extra = (0,) * 4
        previous = 0
        for eid in path:
            e = edges[eid]
            need(e['id'] == eid and e['u'] == previous, 'consecutive path endpoints')
            previous = e['v']
            segment = compile_literal(m, stable(e['one_coordinate_literal_circuit']))
            need(segment.tab == tuple(tuple(t) for t in e['one_coordinate_tableau']), 'edge actual signed tableau')
            op = op.then(segment)
            extra = add_phase(extra, e['extra_global_phase_exponent_by_f_mod4'])
        need(previous == 0, 'literal endpoint path returns to fixed boundary')
        r = ce.rank(x for x, z, p in op.tab[m:])
        Z = tuple(1 << (m + i) for i in range(m))
        need(distance(Z, tuple(linear(columns(op), z) for z in Z), m) == r, 'Grassmann distance equals native rank')
        result.append((op, extra, r))
    return result


def source_pin(relative):
    return dict(path=relative, sha256=digest(HERE / relative))


def fixture_certificate(name, relative, fixture):
    events = fixture.get('full_events', fixture['events'])
    n, m = fixture['banks'], fixture['ambient_arity']
    edges, paths, owner, nodes = graph_paths(events, n, m)
    holonomies = check_partition(edges, paths, n, m)
    direct = direct_paths(events, n, m)
    need(sorted(owner) == list(range(n)), 'SWAP transports a permutation of physical strands')
    for i, ((op, extra, r), (bank, expected, expected_extra)) in enumerate(zip(holonomies, direct)):
        need(op.tab == expected.tab, 'independent physical unary holonomy tableau')
        need(stable(op.circuit) == stable(expected.circuit), 'independent physical holonomy exact circuit order and phase')
        need(extra == expected_extra and owner[bank] == i, 'physical strand endpoint and tensor phase')
    hist = Counter(e['rank_per_f'] for e in events if e['kind'] == 'NATIVE')
    mass = sum(r * count for r, count in hist.items())
    Z_score = sum(e['rank_per_f'] for e in edges)
    lower = sum(item[2] for item in holonomies)
    need(lower <= Z_score <= mass, 'rank lower bound versus original edge and gate invoices')
    reported = fixture.get('mass', fixture.get('native_mass'))
    need(mass == reported, 'source complete native mass')
    parent = fixture.get('parent_arity', m)
    stock = fixture.get('optimistic_stock', fixture.get('stock', n * parent))
    need(stock == n * parent, 'fixed endpoint stock')

    # Defect-sensitive controls use the actual finite source graph.
    wrong = copy.deepcopy(paths)
    wrong[0] = wrong[0][1:]
    try:
        check_partition(edges, wrong, n, m)
    except ValueError as error:
        omission = str(error)
    else:
        raise ValueError('edge-omission negative control accepted')
    wrong_swap = None
    for ordinal, event in enumerate(events):
        if event['kind'] != 'BANK_SWAP':
            continue
        E, P, labels, _ = graph_paths(events, n, m, omit_swap=ordinal)
        try:
            H = check_partition(E, P, n, m)
            for (op, extra, r), (_, expected, ep) in zip(H, direct):
                need(op.tab == expected.tab and stable(op.circuit) == stable(expected.circuit) and extra == ep,
                     'independent physical trajectory disagrees with omitted SWAP transport')
        except ValueError as error:
            wrong_swap = dict(source_event_ordinal=ordinal, rejected=str(error))
            break
    need(wrong_swap is not None, 'a nontrivial literal-SWAP omission is detected')

    outpaths = []
    for i, ((op, extra, r), (bank, _, _)) in enumerate(zip(holonomies, direct)):
        outpaths.append(dict(initial_bank=i, final_bank=bank, edges=paths[i],
                             native_holonomy_arity_per_f=r, one_coordinate_tableau=op.tab,
                             one_coordinate_literal_circuit=op.circuit,
                             extra_global_phase_exponent_by_f_mod4=extra))
    return dict(family=name, q=fixture['q'], banks=n, ambient_arity=m,
                endpoint_arity_per_f=parent, stock=stock, source=source_pin(relative),
                source_events_sha256=hashlib.sha256(stable(events).encode()).hexdigest(),
                native_histogram=dict(sorted(hist.items())), original_native_mass=mass,
                graph_nodes=nodes, graph_edges=len(edges), boundary_all_Z_invoice=Z_score,
                trajectory_floor_per_f=lower, trajectory_ranks_per_f=[h[2] for h in holonomies],
                bound_equals_source_invoice=(lower == mass), bound_equals_endpoint_stock=(lower == stock),
                complete_edge_partition=True, exact_independent_holonomy_replay=True,
                phases='Each holonomy is i^extra[f mod 4] times its literal coordinate circuit tensor power; field SCALE factors commute and are separately counted.',
                scalar_scan_counts=dict(Counter(e['kind'] for e in events if e['kind'] in ('ADD', 'SCALE', 'BANK_SWAP'))),
                edges=edges, trajectories=outpaths,
                negative_controls=dict(omitted_edge_rejected=omission, wrong_SWAP_transport=wrong_swap))


def produce():
    pins = pin_inputs()
    sources = [('PAULI-DEFAULT', 'inputs/pauli/DEFAULT.json'),
               ('PAULI-ISOLATED', 'inputs/pauli/ISOLATED.json'),
               ('REPAIRED-SIMPLIFIED', 'inputs/REPAIRED-SIMPLIFIED.json'),
               ('ADMITTED-TWO-SITE', 'inputs/ADMITTED-TWO-SITE.json')]
    results = []
    for family, relative in sources:
        for fixture in json.loads((HERE / relative).read_text())['fixtures']:
            results.append(fixture_certificate(family, relative, fixture))
    pauli = [r for r in results if r['family'].startswith('PAULI-')]
    need(all(r['bound_equals_source_invoice'] and r['bound_equals_endpoint_stock'] for r in pauli),
         'sharp Pauli fixed-trajectory floor')
    return dict(status='PASS_EXACT_FIXED_WORD_TRAJECTORY_CERTIFICATES', no_new_kappa=True,
                model='Fixed unary holonomies, fixed ADD common-frame graph, arbitrary Clifford Lagrangian frame gauges, literal physical input/output boundaries.',
                proof_domain='The listed q2/q3 words; every positive f, including general frames mixing tensor coordinates. No all-q fixture extrapolation.',
                fixtures=results, input_pin_manifest_sha256=digest(HERE / 'INPUT-PINS.json'),
                producer_sha256=digest(__file__),
                external_exact_clifford_source=dict(path=str(Path(ce.__file__).resolve()), sha256=digest(ce.__file__)),
                limits=['This is an exact mathematical rank-mass lower bound, not a numerical-search lower bound.',
                        'It does not fix a positive-exponent moment or admit a new supplier, owners, storage, rounding or BIT.',
                        'Words with changed unary holonomies, nonlocal scalar rewrites across native sites, new helpers or changed endpoint contracts are outside this fixed-graph certificate.',
                        'Pauli ISOLATED is used as a literal Clifford word; no selected-native lowering of its changed site is newly asserted here.'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = produce()
    result = json.loads(json.dumps(result))
    output = HERE / 'TRAJECTORY-CERTIFICATES.json'
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(output.read_text()) == result, 'saved exact trajectory certificate')
    print(result['status'])
    for r in result['fixtures']:
        print(r['family'], 'q' + str(r['q']), r['trajectory_ranks_per_f'], 'floor', r['trajectory_floor_per_f'],
              'invoice', r['original_native_mass'], 'stock', r['stock'])


if __name__ == '__main__':
    main()
