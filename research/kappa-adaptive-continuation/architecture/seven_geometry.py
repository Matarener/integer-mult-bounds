#!/usr/bin/env python3
"""Seven complete PR3734 local calls on three pairs in 57 dimensions.

Emits and checks the scalar paired chain, actual port-dependent native routes,
all affine phases and the twelve idle children per port. Helper allocation is
a separate admission: this file makes no claim that its exact widths fit.
Apache-2.0. Substantial OpenAI assistance; source credit in README.md.
"""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json


PHASE_REL = 'artifact/integer-mult-bounds/research/pr3190-independent-operator-audit/vendor/DATA-PHASES.json'
NATIVE_REL = 'artifact/live-source/research/staged544-producer-return/inputs/'
PINS = {
    PHASE_REL: 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    NATIVE_REL+'NATIVE-base.json.gz': 'bfe0cc0badac6c6d18461ceea0b299162c0f280c05f81b63f11fcc06cf9180e6',
    NATIVE_REL+'NATIVE-extra.json.gz': 'c5eec94a64cecfd6b83de05619628ad4868e889d62a55b49973f09705cc60448',
}
M, PAIRS, STAGES, PORTS = 57, 3, 7, 112
AXES = tuple(1 << j for j in range(M))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def act(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length()-1]
        value ^= bit
    return result


def sig(lines=(), shift=0):
    """Exact Z/4 character phase polynomial, including all cross terms."""
    result = {}
    def add(key, value):
        result[key] = (result.get(key, 0)+value) % 4
        if not result[key]:
            del result[key]
    for axis, sign in lines:
        support = [j for j in range(M) if axis >> j & 1]
        for j in support:
            add((j,), sign)
        for i, j in enumerate(support):
            for k in support[i+1:]:
                add((j, k), -2*sign)
    for j in range(M):
        if shift >> j & 1:
            add((j,), 2)
    return result


def plus(a, b):
    result = a.copy()
    for key, value in b.items():
        result[key] = (result.get(key, 0)+value) % 4
        if not result[key]:
            del result[key]
    return result


def minus(a, b):
    return plus(a, {key: -value for key, value in b.items()})


def full(level):
    return sig([(x, 1) for x in AXES[:9+8*level]]) if level >= 0 else {}


def orthogonal(axes):
    return all((a & b).bit_count() % 2 == (i == j)
               for i, a in enumerate(axes) for j, b in enumerate(axes))


def schedule():
    """Literal B3 controller with the required idle sweeps inserted."""
    out = [dict(kind='local', pair=0, stage=0, reverse=False),
           dict(kind='local', pair=0, stage=1, reverse=True)]
    for pair in range(1, PAIRS):
        previous = pair-1
        stage = 2*pair
        out.extend([
            dict(kind='idle', pair=pair, from_level=-1, to_level=stage-1,
                 eligible_stages=list(range(stage))),
            dict(kind='bridge', dst=previous, src=pair, coefficient=1),
            dict(kind='local', pair=previous, stage=stage, reverse=False),
            dict(kind='idle', pair=pair, from_level=stage-1, to_level=stage,
                 eligible_stages=[stage]),
            dict(kind='bridge', dst=previous, src=pair, coefficient=-1),
            dict(kind='local', pair=pair, stage=stage+1, reverse=True),
        ])
    out.append(dict(kind='local', pair=PAIRS-1, stage=STAGES-1, reverse=False))
    for pair in range(PAIRS-1):
        out.append(dict(kind='idle', pair=pair, from_level=2*pair+2,
                        to_level=STAGES-1, eligible_stages=list(range(2*pair+3, STAGES))))
    out.extend(dict(kind='bridge', dst=pair, src=pair-1, coefficient=1)
               for pair in range(PAIRS-1, 0, -1))
    out.extend([dict(kind='terminal_Y_translation'), dict(kind='terminal')])
    return out


def controller(events, omit_bridge=None):
    rows = [[int(i == j) for j in range(2*PAIRS)] for i in range(2*PAIRS)]
    bridges = 0
    for event in events:
        kind = event['kind']
        if kind == 'local':
            x, y = event['pair'], PAIRS+event['pair']
            dst, src, coefficient = (x, y, -1) if event['reverse'] else (y, x, 1)
            rows[dst] = [a+coefficient*b for a, b in zip(rows[dst], rows[src])]
        elif kind == 'bridge':
            bridges += 1
            if bridges == omit_bridge:
                continue
            dst, src, c = event['dst'], event['src'], event['coefficient']
            rows[dst] = [a+c*b for a, b in zip(rows[dst], rows[src])]
            rows[PAIRS+src] = [a-c*b for a, b in zip(rows[PAIRS+src], rows[PAIRS+dst])]
        elif kind == 'terminal':
            rows = rows[PAIRS:]+[[-x for x in row] for row in rows[:PAIRS]]
    return rows


def run(source, out):
    loaded = {}
    for relative, pin in PINS.items():
        path = source/relative
        need(sha256(path.read_bytes()).hexdigest() == pin, 'source pin '+relative)
        loaded[relative] = read(path)
    phases = loaded[PHASE_REL]
    native = loaded[NATIVE_REL+'NATIVE-base.json.gz']
    local = {int(r): n for r, n in native['local_profile'].items()}
    widths = [len(native['frames'][native['final'][i]])-
              len(native['frames'][native['start'][i]]) for i in range(224, 632)]
    need(local == {1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}, 'retain all eight centre children')
    need(Counter(widths) == {4:26, 5:2, 6:18, 7:53, 8:96, 9:213}, 'current helper widths')
    extra = loaded[NATIVE_REL+'NATIVE-extra.json.gz']
    extra_widths = [len(extra['frames'][extra['final'][i]])-
                    len(extra['frames'][extra['start'][i]]) for i in range(224, 632)]
    need(extra['local_profile'] == native['local_profile'] and extra_widths == widths,
         'both provider variants have the same billed interface')
    events = schedule()
    identity = [[int(i == j) for j in range(6)] for i in range(6)]
    need(controller(events) == identity, 'complete seven-call scalar endpoint identity')
    need(controller(events, omit_bridge=1) != identity, 'bridge deletion rejection control')
    routes, children, histograms = [], [], []
    count = Counter()
    for p, q in enumerate(native['ports']):
        recipe = phases['recipes'][p]
        need(recipe['q'] == q, 'actual local label binding')
        chart = tuple(recipe['idle_children'][0]['orthogonal_axes'][:8])
        need(orthogonal((q,)+chart), 'actual nine-axis orthonormal chart')
        beta = sum(1 << j for j, v in enumerate(chart) if (v.bit_count()-1)//2 % 2)
        delta = recipe['idle_children'][0]['translation_after']
        need(sig([(x, 1) for x in chart], delta) == minus(full(0), sig([(q, 1)])),
             'exact q-perpendicular native phase')
        for stage in range(STAGES):
            if stage == 0:
                rho, entry, exit_ = AXES, 0, 0
            else:
                fresh = AXES[9+8*(stage-1):9+8*stage]
                swaps = [a ^ b for a, b in zip(chart, fresh)]
                rho = tuple(x ^ act(swaps, sum(((x & u).bit_count() % 2) << j
                                              for j, u in enumerate(swaps))) for x in AXES)
                entry = q ^ act(chart, beta)
                exit_ = act(chart, beta) ^ (beta << (9+8*(stage-1)))
            need(orthogonal(rho) and all(act(rho, act(rho, x)) == x for x in AXES),
                 'literal 57-axis orthogonal involution')
            need(act(rho, q) == q and max(rho) < 1 << M, 'fixed normal and closed57-axis route')
            need(recipe['stage_alignment'][stage] ==
                 dict(entry_X=entry, entry_Y=entry, exit_X=exit_, exit_Y=exit_),
                 'inherited affine phase recipe')
            old_x = [(q, 1)] if stage == 0 else [(x, 1) for x in AXES[:1+8*stage]]
            old_y = [] if stage == 0 else old_x+[(q, -1)]
            exterior = [(x, 1) for x in AXES[9:9+8*stage]]
            new_x = [(x, 1) for x in AXES[:9+8*stage]]
            new_y = new_x+[(q, -1)]
            for old, local_in, new, local_out in (
                (old_x, [(q, 1)]+exterior, new_x, [(x, 1) for x in AXES[:9]]+exterior),
                (old_y, exterior, new_y, [(x, 1) for x in AXES[:9]]+exterior+[(q, -1)])):
                need(sig([(act(rho, x), s) for x, s in old], act(rho, entry)) == sig(local_in),
                     'native local entrance phase')
                need(sig(local_out, act(rho, exit_)) == sig([(act(rho, x), s) for x, s in new]),
                     'native local exit phase')
                count['local_side_phase_identities'] += 2
            routes.append(dict(port=p, stage=stage, columns=list(rho),
                               entry_translation=entry, exit_translation=exit_))
        current = [[sig([(q, 1)]), {}] for _ in range(PAIRS)]
        levels, hist = [-1]*PAIRS, Counter()
        for event in events:
            kind = event['kind']
            if kind == 'local':
                pair, stage = event['pair'], event['stage']
                need(levels[pair] == stage-1, 'local stage predecessor')
                old = [sig([(q, 1)]), {}] if stage == 0 else [full(stage-1), minus(full(stage-1), sig([(q, 1)]))]
                need(current[pair] == old, 'current physical local entrance gauges')
                current[pair] = [full(stage), minus(full(stage), sig([(q, 1)]))]
                levels[pair] = stage
                count['literal_complete_local_calls_per_port'] += 1
            elif kind == 'idle':
                pair, previous, level = event['pair'], event['from_level'], event['to_level']
                need(levels[pair] == previous, 'literal idle predecessor')
                axes = (list(chart)+list(AXES[9:9+8*level])) if previous == -1 else list(AXES[9+8*previous:9+8*level])
                shift = delta if previous == -1 else 0
                need(orthogonal(axes), 'every positive idle child has orthonormal axes')
                for side in range(2):
                    current[pair][side] = plus(current[pair][side], sig([(a, 1) for a in axes], shift))
                    children.append(dict(port=p, pair=pair, side=side, from_level=previous,
                                         to_level=level, rank=len(axes), axes=axes, translation_after=shift,
                                         eligible_stages=event['eligible_stages']))
                    hist[len(axes)] += 1
                need(current[pair] == [full(level), minus(full(level), sig([(q, 1)]))],
                     'exact idle completion phase')
                levels[pair] = level
            elif kind == 'bridge':
                need(current[event['dst']] == current[event['src']], 'both bridge sides share exact gauges')
                count['admitted_scalar_bridges_per_port'] += 1
            elif kind == 'terminal_Y_translation':
                for pair in range(PAIRS):
                    current[pair][1] = plus(current[pair][1], sig(shift=q))
            elif kind == 'terminal':
                for pair in range(PAIRS):
                    # The controller sends normalized initial coordinates to
                    # (-y, C_q^-1 x) before the terminal signed exchange.
                    actual_x = minus(current[pair][1], sig([(q, 1)]))
                    actual_y = current[pair][0]
                    need(actual_x == actual_y == full(STAGES-1), 'every physical data output FULL57')
                    count['productive_full57_fields'] += 2
        histograms.append(hist)
    need(all(h == {8:4, 16:4, 32:4} for h in histograms), 'actual idle child rank histogram')
    # Removing the mandatory terminal translation changes a nonzero multiplier
    # by sign on any character xi with q.xi=1.
    q0 = native['ports'][0]
    witness = q0 & -q0
    need((q0 & witness).bit_count() % 2 == 1, 'terminal phase omission rejection witness')
    idle_mass = PORTS*sum(r*c for r, c in histograms[0].items())
    local_mass = STAGES*sum(r*c for r, c in local.items())
    helper_credit = STAGES*sum(widths)
    payload = dict(version=1, dimension=M, pairs=PAIRS, ports=PORTS,
                   schedule=events, stage_routes=routes, idle_children=children,
                   local_profile=local, helper_widths=widths)
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    result = dict(status='PASS_LITERAL_SEVEN_CALL_DATA_GEOMETRY', source_pins=PINS,
                  payload_sha256=sha256(raw).hexdigest(), dimension=M, pairs=PAIRS, stages=STAGES,
                  productive_fields=2*PAIRS*PORTS, local_profile=local,
                  helper_width_inventory=dict(sorted(Counter(widths).items())), helper_width_sum=sum(widths),
                  idle_children_per_port={8:4, 16:4, 32:4}, idle_rank_mass=idle_mass,
                  local_rank_mass=local_mass, helper_width_credit=helper_credit,
                  paid_idle_rank_if_all_helpers_hosted=idle_mass-helper_credit,
                  total_rank_if_all_helpers_hosted=local_mass+idle_mass-helper_credit,
                  productive_rank_normalizer=M*2*PAIRS*PORTS,
                  raw_deficit_if_all_helpers_hosted=M*2*PAIRS*PORTS-(local_mass+idle_mass-helper_credit),
                  counters=dict(count), controls=dict(omitted_bridge_rejected=True,
                  omitted_terminal_translation_rejected=True, terminal_witness_character=witness),
                  scope='Exact scalar and data phase/route/idle geometry only. Retains all eight centre H8 calls per local supplier. No helper allocation, lane clock, whole-execution owner matching, or precision invoice is certified here.',
                  excluded_claims=['new kappa', 'bank-free helper hosting', 'complete multiplication theorem'])
    out.mkdir(parents=True, exist_ok=True)
    (out/'SEVEN57-GEOMETRY.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (out/'SEVEN57-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ['idle_rank_mass','helper_width_credit','paid_idle_rank_if_all_helpers_hosted','raw_deficit_if_all_helpers_hosted']},sort_keys=True))


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2]/'kappa-global-continuation/inputs/kappa-consumer-followup')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    run(args.source.resolve(), args.out.resolve())
