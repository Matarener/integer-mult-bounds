#!/usr/bin/env python3
"""Literal uniform nine-block native geometry and productive endpoint cost.

The candidate uses common stage owner routes, so its scalar local code has
no stage-dependent conjugation. This script closes every native endpoint;
it deliberately grants a zero-price scalar residual inverse when pricing.
Apache-2.0; substantial OpenAI Codex assistance. Retained source credit is
preserved in the accompanying README.
"""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def action(columns, value):
    answer = 0
    while value:
        low = value & -value
        answer ^= columns[low.bit_length()-1]
        value ^= low
    return answer


def sig(axes=(), translation=0):
    """Exact Z/4 Fourier phase polynomial: linear and quadratic terms.

    parity(a.x) = sum a_i x_i - 2 sum_(i<j) a_i a_j x_i x_j mod4.
    Translation contributes 2 parity(delta.x), whose quadratic terms vanish.
    Equality of these polynomials and the uniform-vector value fixes phase.
    """
    out = {}
    def add(key, value):
        value = (out.get(key, 0) + value) % 4
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    for axis, sign in axes:
        bits = [j for j in range(81) if axis >> j & 1]
        for i in bits:
            add((i,), sign)
        for k, i in enumerate(bits):
            for j in bits[k+1:]:
                add((i, j), -2*sign)
    for j in range(81):
        if translation >> j & 1:
            add((j,), 2)
    return out


def plus(a, b):
    out = a.copy()
    for key, value in b.items():
        value = (out.get(key, 0)+value) % 4
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def minus(a, b):
    return plus(a, {k: -v for k, v in b.items()})


def block(stage):
    return [1 << (9*stage+j) for j in range(9)]


def full(level):
    return sig([(1 << j, 1) for j in range(9*(level+1))])


def phase_eval(s, value):
    return sum(coefficient for monomial, coefficient in s.items()
               if all(value >> j & 1 for j in monomial)) % 4


def run(scope, out):
    followup = scope/'inputs/kappa-consumer-followup'
    phase_path = followup/'artifact/integer-mult-bounds/research/pr3190-independent-operator-audit/vendor/DATA-PHASES.json'
    phase_raw = phase_path.read_bytes()
    need(sha256(phase_raw).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'native phase source pin')
    phases = json.loads(phase_raw)
    template_path = followup/'artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz'
    need(sha256(template_path.read_bytes()).hexdigest() == '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e', 'controller source pin')
    template = read(template_path)
    program, old_hists, zero_hists, counts = [], [], [], Counter()
    routes = {}
    for stage in range(9):
        rho = [1 << j for j in range(81)]
        if stage:
            for j in range(9):
                rho[j], rho[9*stage+j] = rho[9*stage+j], rho[j]
        need(all(action(rho, action(rho, 1 << j)) == 1 << j for j in range(81)), 'uniform route inverse')
        routes[stage] = rho
    for p in range(128):
        old = p < 112
        q = phases['recipes'][p]['q'] if old else 0
        qperp = phases['recipes'][p]['idle_children'][0]['orthogonal_axes'][:8] if old else []
        if old:
            basis = [q]+qperp
            need(all((u & v).bit_count() % 2 == (i == j) for i, u in enumerate(basis) for j, v in enumerate(basis)), 'actual orthonormal q-perp basis')
            delta = sum((((sum((v >> j) & 1 for v in basis)-1)//2) & 1) << j for j in range(9))
            need(sig([(v, 1) for v in qperp], delta) == minus(full(0), sig([(q, 1)])), 'exact native complement phase')
        else:
            delta = 0
        current = [[sig([(q, 1)]) if old else {}, {}] for _ in range(4)]
        levels, hist = [-1]*4, Counter()
        def child(pair, side, axes, shift, purpose):
            need(len(axes) == len(set(axes)) and all((u & v).bit_count() % 2 == (i == j)
                 for i, u in enumerate(axes) for j, v in enumerate(axes)), 'every emitted child has orthonormal axes')
            current[pair][side] = plus(current[pair][side], sig([(v, 1) for v in axes], shift))
            if axes:
                hist[len(axes)] += 1
                program.append(dict(kind='native_child', port=p, pair=pair, side=side,
                    axes=axes, rank=len(axes), translation_after=shift, purpose=purpose))
            else:
                need(not shift, 'zero rank child cannot hide an adapter')
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                stage = event['stage']
                pair = next(e['pair'] for e in template['recipe'] if e['kind'] == 'local' and e['stage'] == stage)
                need(levels[pair] == stage-1, 'local predecessor level')
                if stage and old:
                    child(pair, 0, [q << (9*stage)], 0, 'next normal on X')
                    child(pair, 1, [q << (9*(stage-1))], 0, 'previous Y hole fill')
                    counts['gap_H1'] += 2
                exterior = full(stage-1)
                required = [plus(exterior, sig([(q << (9*stage), 1)])) if old else exterior, exterior]
                need(current[pair] == required, 'literal local entrance gauges')
                rho = routes[stage]
                need(action(rho, q) == q << (9*stage), 'uniform native normal route')
                # Both sides are pulled back by this same coordinate permutation.
                # Its exterior excludes the local first9 block for every port.
                exterior_axes = [action(rho, 1 << j) for j in range(9*stage)]
                need(all(not (v & 511) for v in exterior_axes), 'common exterior avoids local block')
                for side in range(2):
                    current[pair][side] = full(stage)
                if old:
                    current[pair][1] = minus(current[pair][1], sig([(q << (9*stage), 1)]))
                levels[pair] = stage
                counts['literal_local_entrance_exit_pairs'] += 1
                program.append(dict(kind='native_local', port=p, pair=pair, stage=stage,
                    common_owner_route=stage, common_exterior_axes=exterior_axes))
            elif kind == 'idle_cover_sweep':
                pair, level = event['pair'], event['to_level']
                previous = levels[pair]
                need(previous == event['from_level'], 'actual idle source level')
                terminal = level == 8
                target = [full(level), full(level)]
                if old:
                    target[1] = minus(target[1], sig([(q if terminal else q << (9*level), 1)]))
                before_hist = hist.copy()
                if not old:
                    axes = [1 << j for j in range(9*(previous+1), 9*(level+1))]
                    for side in range(2):
                        child(pair, side, axes, 0, 'zero-port idle')
                elif terminal:
                    axes = [1 << j for j in range(9*(previous+1), 81)]
                    child(pair, 0, axes, 0, 'terminal X full completion')
                    child(pair, 1, axes + [q, q << (9*previous)], q,
                          'terminal Y initial-normal closure')
                elif previous == -1:
                    child(pair, 0, qperp + [1 << j for j in range(9, 9*(level+1))], delta, 'initial X idle')
                    child(pair, 1, [1 << j for j in range(9*level)] + [v << (9*level) for v in qperp],
                          delta << (9*level), 'initial Y idle')
                else:
                    axes = [1 << j for j in range(9*(previous+1), 9*(level+1))]
                    child(pair, 0, axes, 0, 'intermediate X idle')
                    child(pair, 1, [q << (9*previous)] + [1 << j for j in range(9*(previous+1), 9*level)]
                          + [v << (9*level) for v in qperp], delta << (9*level), 'intermediate Y idle')
                need(current[pair] == target, 'exact idle output phase')
                if terminal and old:
                    counts['terminal_shift_rank'] += 2
                counts['idle_rank_mass'] += sum(r*c for r, c in (hist-before_hist).items())
                levels[pair] = level
            elif kind == 'bridge':
                dst, src = event['dst'], event['src']
                need(current[dst] == current[src], 'actual scalar bridge gauges')
                counts['bridge_contacts'] += 1
            elif kind == 'terminal_Y_translations':
                for pair in range(4):
                    if old:
                        current[pair][1] = plus(current[pair][1], sig(translation=q))
                program.append(dict(kind='terminal_translation', port=p, vector=q))
            elif kind == 'terminal':
                for pair in range(4):
                    # Signed exchange and the ordinary scalar prefix S cancel.
                    # Initial X has logical coordinate C_q^-1 x, initial Y=y.
                    x = minus(current[pair][1], sig([(q, 1)])) if old else current[pair][1]
                    y = current[pair][0]
                    need(x == y == full(8), 'both productive physical endpoints FULL81')
                counts['full_productive_endpoints'] += 8
            else:
                need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family'), 'schedule grammar')
        # Separate the explicit per-boundary rank1 tariff from idle histograms.
        if old:
            idle_hist = hist - Counter({1: 16})
            old_hists.append(idle_hist)
        else:
            zero_hists.append(hist)
    need(all(h == old_hists[0] for h in old_hists) and all(h == zero_hists[0] for h in zero_hists), 'port-independent rank census')
    old_mass = sum(r*c for r, c in old_hists[0].items())
    zero_mass = sum(r*c for r, c in zero_hists[0].items())
    need((old_mass, zero_mass, counts['gap_H1']) == (488, 486, 1792), 'uniform native invoice')
    capacity = 81*1024
    total = 9*5070 + 1792 + 112*old_mass + 16*zero_mass - 9*2990
    need(total == capacity == 82944, 'complete raw zero deficit')
    # Dropping terminal closure gives a concrete wrong Fourier phase: q8 and
    # q0 are independent. At xi on one selectedq0 coordinate the mismatch is1.
    q = phases['recipes'][0]['q']
    wrong = minus(sig([(q << 72, 1)]), sig([(q, 1)]))
    witness = q & -q
    need(phase_eval(wrong, witness) != 0, 'terminal mismatch rejection control')
    payload = dict(version=1, stage_owner_routes=routes, emitted_events=program)
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    out.mkdir(parents=True, exist_ok=True)
    (out/'UNIFORM81-NATIVE.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    result = dict(status='PASS_LITERAL_UNIFORM81_GEOMETRY_RAW_DEFICIT_ZERO', dimension=81,
        productive_fields=1024, source_phase_sha256=sha256(phase_raw).hexdigest(),
        source_template_sha256=sha256(template_path.read_bytes()).hexdigest(),
        native_payload_sha256=sha256(raw).hexdigest(), counters=dict(counts),
        old_port_idle_histogram=dict(sorted(old_hists[0].items())), old_port_idle_rank_mass=old_mass,
        zero_port_idle_histogram=dict(sorted(zero_hists[0].items())), zero_port_idle_rank_mass=zero_mass,
        local_rank_mass=45630, explicit_gap_H1=1792, remaining_helper_credit=26910,
        complete_preconsumer_rank_mass=total, productive_rank_normalizer=capacity, raw_deficit=0,
        terminal_closure_extra_rank_mass=896,
        terminal_closure='Final Y padding targets FULL81 C_q0^-1, rather than FULL81 C_q8^-1. Its extra2 axes are fused into the idle child, with inverseq0 implemented by a positive line and translation.',
        phase_controls=dict(omitted_initial_normal_closure_rejected=True, witness_fourier_index=witness,
                            wrong_multiplier_exponent=phase_eval(wrong, witness)),
        route_scope='Every stage uses one standard9-block coordinate swap for all128 ports. Scalar local D commutes with this common owner-only route; this does not assert that the whole nine-call scalar controller is identity.',
        price_consequence='For any positive saving exponent a, every positive child rank r<81 has (r/81)^(1-a)>r/81. Even granting a free residual inverse and ideal exact-width helper hosting, raw mass already equals81*1024, so this emitted full uniform-chart family cannot give positive kappa.',
        excluded_claims=['universal endpoint lower bound for other chart families', 'complete changed helper allocation',
                         'profitable residual consumer', 'new kappa'])
    (out/'UNIFORM81-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--scope', type=Path, default=Path(__file__).resolve().parents[2]/'kappa-global-continuation')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    run(args.scope.resolve(), args.out.resolve())
