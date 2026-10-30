#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact hosting/cover/gauge instantiation for the pooled source.

The universal implication is proved in HOSTING-ADMISSION.md. This bounded
checker instantiates its hypotheses on every actual owner/event/port. It does
not enumerate the 73-dimensional cover or execute a production-size payload.
Prepared for Ross Richardson with substantial OpenAI Codex assistance.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PRIOR = REPO / 'research/complex-pooled-full-admission'
BASE = REPO / 'research/staged544-mixed-fourth-entry/owner'
N = 73


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    pins = read_json(HERE / 'HOSTING-PINS.json')
    for relative, entry in pins['files'].items():
        raw = (REPO / relative).read_bytes()
        need(len(raw) == entry['bytes'] and digest(raw) == entry['sha256'],
             'hosting source pin: ' + relative)
    manifest = read_json(PRIOR / 'PHYSICAL-GLOBAL-PINS.json')['bundle']
    members = {}
    with tarfile.open(PRIOR / manifest['path']) as archive:
        inventory = archive.getmembers()
        need(len(inventory) == len(manifest['files']), 'global archive member count')
        for member in inventory:
            name = member.name
            need(member.isfile() and name in manifest['files'] and name not in members,
                 'unique regular authenticated member')
            raw = archive.extractfile(member).read()
            expected = manifest['files'][name]
            need(len(raw) == expected['bytes'] and digest(raw) == expected['sha256'],
                 'global archive member digest: ' + name)
            members[name] = raw
    return pins, members


def transpose(rows):
    return tuple(sum(((rows[i] >> j) & 1) << i for i in range(len(rows)))
                 for j in range(len(rows)))


def act(rows, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(rows))


def orthogonal(rows):
    return len(set(rows)) == len(rows) and all(
        0 <= r < 1 << len(rows) for r in rows) and all(
        ((a & b).bit_count() & 1) == (i == j)
        for i, a in enumerate(rows) for j, b in enumerate(rows))


def port_basis(q):
    # Construct the explicit orthogonal transvection on a permuted standard basis.
    missing = next(i for i in range(9) if not (q >> i & 1))
    isotropic = q ^ (1 << missing)
    order = list(range(N))
    order[0], order[missing] = order[missing], order[0]
    return tuple((1 << i) ^ (isotropic if isotropic >> i & 1 else 0) for i in order)


def data_columns(basis, stage):
    if not stage:
        return tuple(1 << i for i in range(N))
    vectors = [basis[1 + i] ^ (1 << (9 + 8 * (stage - 1) + i)) for i in range(8)]
    return tuple(
        _xor([(1 << j)] + [v for v in vectors if v >> j & 1]) for j in range(N))


def _xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def observation_windows(projection, template):
    calls = projection['calls']
    local = {e['stage']: e for e in template['recipe'] if e['kind'] == 'local'}
    need(len(calls) == 3240 and [c['time'] for c in calls] == list(range(3240)),
         'complete indexed calls')
    need(len(projection['execution_schedule']) == 10802, 'complete actual event inventory')
    last = defaultdict(lambda: -1)
    windows, positions = {}, {}
    per_replica = defaultdict(list)
    event_counts = Counter()
    for index, event in enumerate(projection['execution_schedule']):
        kind = event['kind']
        event_counts[kind] += 1
        source = template['execution_schedule'][event['source_event']]
        need(kind == source['kind'], 'actual event kind matches original chronology')
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            need(index >= 10800, 'global suffix follows every replica')
            continue
        replica = event['replica']
        need(0 <= replica < 360 and event['replicas'] == [replica], 'single whole replica event')
        per_replica[replica].append(event['source_event'])
        for key in ('stage', 'pair', 'child_indices', 'from_level', 'to_level',
                    'src', 'dst', 'coefficient', 'pairs'):
            if key in source:
                need(event[key] == source[key], 'literal chronological field: ' + key)
        if kind == 'local_cover_sweep':
            time = event['time']
            need(time not in positions, 'unique complete call dispatch')
            call = calls[time]
            spec = local[call['stage']]
            need((call['replica'], call['stage'], call['pair'], call['orientation'],
                  call['provider_id']) == (replica, event['stage'], spec['pair'],
                  'backward' if spec['reverse'] else 'forward', event['provider_id']),
                 'complete call endpoint/source-event binding')
            positions[time] = index
            last[replica, call['pair']] = index
        elif kind == 'bridge':
            last[replica, event['src']] = last[replica, event['dst']] = index
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                key = replica, child
                need(key not in windows, 'unique original idle child boundary')
                windows[key] = last[replica, event['pair']], index, event['pair'], side
        elif kind in ('terminal_Y_translations', 'terminal'):
            for pair in range(4):
                last[replica, pair] = index
        else:
            raise ValueError('uncovered actual event')
    need(set(positions) == set(range(3240)), 'all complete native events placed')
    need(len(windows) == 360 * 20 and all(
        per_replica[r] == list(range(30)) for r in range(360)),
        'each replica follows every original event exactly once')
    need(event_counts == Counter(local_cover_sweep=3240, idle_cover_sweep=3600,
         bridge=3240, terminal_Y_translations=360, terminal=360,
         bank_padding_cover_sweep=1, translate_every_live_family=1), 'actual event counts')
    return positions, windows, event_counts


def validate_host(row, ordinal, projection, phases, positions, windows, used,
                  chart_cache, sigmas, pairs, sides):
    time, helper, replica, child, port, offset = row
    need((time, helper) == divmod(ordinal, 408), 'one assignment per actual helper in order')
    need(0 <= child < 18 and 0 <= replica < 360 and 0 <= port < 112, 'actual owner domain')
    call = projection['calls'][time]
    width = projection['local_providers'][call['provider_id']]['widths'][helper]
    lower, upper, pair, side = windows[replica, child]
    need(lower < positions[time] < upper, 'whole native call inside original observation-free window')
    need((pair, side) == (pairs[str(child)], sides[str(child)]), 'original child role')
    family = 896 * replica + (2 * pair + side) * 112 + port
    owner_family, route_id = call['owners'][224 + helper]
    need(owner_family == family, 'literal physical helper family')
    route = projection['physical_owner_routes'][route_id]
    typ, actual_child, actual_offset = route[:3]
    actual_width = 9 if typ == 3 else route[3]
    spectators = () if typ == 3 else tuple(route[4])
    need(typ in (3, 4) and (actual_child, actual_offset, actual_width) ==
         (child, offset, width), 'literal owner child/offset/width')
    key = replica, child, port
    need(used[key] == offset, 'consecutive original-axis partition')
    axes = phases['recipes'][port]['idle_children'][child]['orthogonal_axes']
    need(offset + width <= len(axes), 'original idle capacity')
    cache_key = port, child, offset, width, spectators
    if cache_key not in chart_cache:
        basis = port_basis(phases['recipes'][port]['q'])
        active = tuple(axes[offset:offset + width])
        indices = tuple(basis.index(v) for v in active)
        expected = tuple(i for i in range(N) if i not in indices)[:9 - width]
        need(spectators == expected, 'literal spectator completion')
        order = indices + spectators + tuple(i for i in range(N)
                                             if i not in indices and i not in spectators)
        chart = tuple(basis[i] for i in order)
        need(orthogonal(chart) and chart[:width] == active, 'orthogonal chart has original axes')
        chart_digest = digest(canonical(chart))
        need(sigmas.get(chart_digest) == list(chart), 'complete emitted helper chart binding')
        chart_cache[cache_key] = chart_digest
    used[key] += width
    return key


def hosting(projection, phases, sigmas, fill, plan, template):
    positions, windows, counts = observation_windows(projection, template)
    calls = projection['calls']
    need(projection['m'] == 73 and projection['live'] == 322560 and
         projection['physical'] == 323069, 'complete pooled physical namespace')
    need(not projection['bank_padding']['children'] and not projection['bank_padding']['families'],
         'no missing bank padding child')
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
         and not fill['dispatch_overrides'], 'unchanged literal fill schema')
    need(len(fill['rows']) == 1321920, 'all actual helpers assigned')
    provider_counts = Counter()
    data_chart_keys = set()
    ports = projection['local_providers']['gauge44']['ports']
    need(phases['ports'] == 112 and len(phases['recipes']) == len(ports) == 112,
         'complete literal data port order')
    for port, recipe in enumerate(phases['recipes']):
        q = recipe['q']
        need(recipe['port'] == port and q == ports[port] and 0 < q < 511
             and q.bit_count() % 2 == 1 and orthogonal(port_basis(q)),
             'complete original orthogonal port basis')
    for call in calls:
        owners = call['owners']
        need(len(owners) == len({o[0] for o in owners}) == 632 and
             all(0 <= o[0] < 322560 for o in owners), 'complete distinct whole owner families')
        provider_counts[call['provider_id']] += 1
        for role, (family, route_id) in enumerate(owners[:224]):
            side, port = divmod(role, 112)
            need(family == 896 * call['replica'] + 224 * call['pair'] + 112 * side + port and
                 projection['physical_owner_routes'][route_id] == [1, call['stage'], port],
                 'productive families and literal route')
            data_chart_keys.add((port, call['stage']))
    need(provider_counts == Counter(gauge44=1568, extra=592, **{'extra-four':1080}),
         'only three active providers in actual counts')
    for port, stage in data_chart_keys:
        need(orthogonal(data_columns(port_basis(phases['recipes'][port]['q']), stage)),
             'actual productive chart orthogonal')
    used, charts = defaultdict(int), {}
    for ordinal, row in enumerate(fill['rows']):
        validate_host(row, ordinal, projection, phases, positions, windows, used, charts,
                      sigmas, plan['pairs'], plan['sides'])
    need(set(charts.values()) == set(sigmas) and len(sigmas) == 6489,
         'all and only emitted helper charts reached')
    remainders = {(r['replica'], r['child'], r['port']): r for r in projection['idle_children']}
    need(len(remainders) == len(projection['idle_children']) == 162900, 'unique complete positive tails')
    residual_profile, original_mass, hosted_mass = Counter(), 0, sum(used.values())
    for replica in range(360):
        for child in range(20):
            _, _, pair, side = windows[replica, child]
            for port, recipe in enumerate(phases['recipes']):
                key = replica, child, port
                axes = recipe['idle_children'][child]['orthogonal_axes']
                original_mass += len(axes)
                offset = used.get(key, 0)
                rank = len(axes) - offset
                need(rank >= 0, 'no original axis overallocated')
                if rank:
                    need(key in remainders, 'every positive suffix paid')
                    row = remainders.pop(key)
                    need(row['pending_offset'] == row['hosted'] == offset and row['rank'] == rank
                         and row['family'] == 896 * replica + (2 * pair + side) * 112 + port
                         and row['replicas'] == 1, 'literal complete original-axis residual')
                    residual_profile[rank] += 1
                else:
                    need(key not in remainders, 'no extra zero tail')
    need(not remainders and residual_profile == Counter({3:22788, 5:1620, 48:138492}),
         'complete unchanged priced residual histogram')
    need(hosted_mass + sum(r * c for r, c in residual_profile.items()) == original_mass,
         'all original axes occur exactly once')
    # Targeted controls rerun the local hypothesis predicate on actual data.
    first = fill['rows'][0]
    failures = []
    for name, mutate in (
        ('wrong-whole-call-window', lambda row: [row[0], row[1], calls[row[0]]['replica'],
          12, row[4], row[5]]),
        ('wrong-original-axis-offset', lambda row: row[:5] + [row[5] + 1]),
        ('wrong-port-owner', lambda row: row[:4] + [(row[4] + 1) % 112] + row[5:])):
        try:
            validate_host(mutate(first), 0, projection, phases, positions, windows,
                          defaultdict(int), {}, sigmas, plan['pairs'], plan['sides'])
        except ValueError:
            failures.append(name)
        else:
            raise ValueError('mutation accepted: ' + name)
    return dict(calls=3240, persistent_owner_entries=3240 * 632, hosted_helper_rows=len(fill['rows']),
                observation_windows=len(windows), original_axis_mass=original_mass,
                hosted_axis_mass=hosted_mass, positive_residuals=162900,
                residual_profile=dict(sorted(residual_profile.items())), helper_charts=len(sigmas),
                data_charts=len(data_chart_keys), provider_counts=dict(provider_counts),
                event_counts=dict(counts), rejecting_controls=failures)


@lru_cache(None)
def phase(axis):
    support = tuple(i for i in range(N) if axis >> i & 1)
    quadratic = sum(1 << (N * i + j) for i in support for j in support if i < j)
    return tuple((axis >> i) & 1 for i in range(N)), quadratic


ZERO = ((0,) * N, 0)


def add(*values):
    linear, quadratic = [0] * N, 0
    for coefficients, cross in values:
        linear = [(x + y) % 4 for x, y in zip(linear, coefficients)]
        quadratic ^= cross
    return tuple(linear), quadratic


def scale(value, coefficient):
    return tuple(coefficient * x % 4 for x in value[0]), value[1] if coefficient % 2 else 0


def factor(axes, translation=0):
    return add(scale(phase(translation), 2), *(phase(axis) for axis in axes))


def phase_controller(phases, template):
    checks = 0
    local = {e['stage']: e for e in template['recipe'] if e['kind'] == 'local'}
    identity = [[int(i == j) for j in range(8)] for i in range(8)]
    for port, recipe in enumerate(phases['recipes']):
        q = recipe['q']
        basis = port_basis(q)
        initial = [phase(q) if side == 0 else ZERO for _ in range(4) for side in range(2)]
        gauges = initial[:]
        matrix = [row[:] for row in identity]

        def shear(dst, src, coefficient):
            matrix[dst] = [x + coefficient * y for x, y in zip(matrix[dst], matrix[src])]

        for event in template['execution_schedule']:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                stage = event['stage']
                spec = local[stage]
                x, y = 2 * spec['pair'], 2 * spec['pair'] + 1
                columns = data_columns(basis, stage)
                rows = transpose(columns)
                full = factor(columns[:9])
                cq = phase(act(rows, q))
                diagonal = add(full, scale(cq, -1))
                align = recipe['stage_alignment'][stage]
                ex, ey, ox, oy = (scale(phase(align[k]), 2) for k in
                                  ('entry_X', 'entry_Y', 'exit_X', 'exit_Y'))
                gx, gy = add(diagonal, ex, ox, gauges[x]), add(diagonal, ey, oy, gauges[y])
                if spec['reverse']:
                    off = add(full, ey, ox, gauges[y])
                    need(off == gx, 'exact physical backward scalar/gauge factor')
                    shear(x, y, -1)
                else:
                    off = add(full, scale(cq, -2), ex, oy, gauges[x])
                    need(off == gy, 'exact physical forward scalar/gauge factor')
                    shear(y, x, 1)
                gauges[x], gauges[y] = gx, gy
                checks += 1
            elif kind == 'idle_cover_sweep':
                for side, child in enumerate(event['child_indices']):
                    entry = recipe['idle_children'][child]
                    role = 2 * event['pair'] + side
                    gauges[role] = add(gauges[role], factor(entry['orthogonal_axes'], entry['translation_after']))
            elif kind == 'bridge':
                src, dst, coefficient = event['src'], event['dst'], event['coefficient']
                for target, source, c in ((2 * dst, 2 * src, coefficient),
                                          (2 * src + 1, 2 * dst + 1, -coefficient)):
                    need(gauges[target] == gauges[source], 'exact global signed-bridge gauge')
                    shear(target, source, c)
                    checks += 1
            elif kind == 'terminal_Y_translations':
                for pair in range(4):
                    gauges[2 * pair + 1] = add(gauges[2 * pair + 1], scale(phase(recipe['terminal_Y_translation']), 2))
            elif kind == 'terminal':
                for pair in range(4):
                    x, y = 2 * pair, 2 * pair + 1
                    gauges[x], gauges[y] = gauges[y], gauges[x]
                    matrix[x], matrix[y] = matrix[y], [-v for v in matrix[x]]
            else:
                need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family'), 'phase event alphabet')
        total = factor(1 << j for j in range(N))
        need(matrix == identity and gauges == [add(total, v) for v in initial],
             'all-port complete original chronology equals C_all')
        checks += 8
    return dict(ports=len(phases['recipes']), exact_operator_factor_identities=checks,
                scalar_role_dimension=8, domain='all 73-bit Fourier characters; multiplicative lift for every f>=1')


def cover_checks(members):
    # Independent brute force constructs each small group; compare every source
    # label and the correction on every character. This supplements the proof.
    module = types.ModuleType('authenticated_cover')
    source = members['source/research/physical-complex-controller/cover.py']
    exec(compile(source, '<authenticated-cover>', 'exec'), module.__dict__)
    results = []
    for dimension in range(1, 6):
        cover = module.OrthogonalCover(dimension)
        matrices = []

        def extend(prefix):
            if len(prefix) == dimension:
                matrices.append(tuple(prefix))
                return
            for vector in range(1 << dimension):
                if vector.bit_count() % 2 and all(not ((vector & row).bit_count() % 2) for row in prefix):
                    extend(prefix + [vector])

        extend([])
        need(len(matrices) == cover.size, 'independent complete small orthogonal group')
        for ordinal, matrix in enumerate(matrices):
            need(cover.unrank(ordinal) == matrix and cover.rank(matrix) == ordinal,
                 'complete small cover rank/unrank equality')
            delta = sum((((row.bit_count() - 1) // 2) & 1) << i for i, row in enumerate(matrix))
            for character in range(1 << dimension):
                lhs = act(transpose(matrix), character).bit_count() % 4
                rhs = (character.bit_count() + 2 * ((delta & character).bit_count() % 2)) % 4
                need(lhs == rhs, 'exact all-character common-cover correction')
        results.append(dict(dimension=dimension, matrices=len(matrices), characters_each=1 << dimension))
    full = module.OrthogonalCover(N)
    probes = (0, 1, full.size // 2, full.size - 1)
    for ordinal in probes:
        need(full.rank(full.unrank(ordinal)) == ordinal, '73-dimensional endpoint/interior label probe')
    return dict(complete_small_groups=results, full_dimension=N, full_cover_bits=full.size.bit_length(),
                full_cover_probes=len(probes), universal_domain='written proof, not exhaustive full-cover enumeration')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    pins, members = authenticate()
    projection = json.loads(members['data/PHYSICAL-PROJECTION.json'])
    phases = json.loads(members['data/DATA-PHASES.json'])
    sigmas = json.loads(members['data/ACTUAL-SIGMAS.json'])
    fill = read_json(PRIOR / 'frozen/pr4181/owner/FILL.json.gz')
    plan, template = read_json(BASE / 'PLAN.json.gz'), read_json(BASE / 'TEMPLATE.json.gz')
    result = dict(status='PASS', schema=1,
                  coverage='finite exact source hypotheses; universal proof in HOSTING-ADMISSION.md',
                  source_pins_sha256=digest((HERE / 'HOSTING-PINS.json').read_bytes()),
                  hosting=hosting(projection, phases, sigmas, fill, plan, template),
                  global_operator=phase_controller(phases, template), cover=cover_checks(members))
    result = json.loads(json.dumps(result))
    if args.check:
        need(result == read_json(args.check), 'fresh hosting result equals recorded receipt')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(json.dumps(result, sort_keys=True, indent=2).encode() + b'\n')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
