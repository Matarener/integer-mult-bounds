#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently corroborate PR4088's mixed-provider owner invoice.

Prepared for the yssite campaign with substantial OpenAI Codex assistance,
2026-10-20. This checker credits Cinna Davis's PR4088 construction and unpaidmoon's
PR4165 idle/rebind finding. It imports no repository code, invokes no subprocesses,
and writes no files. Optional controls change only private in-memory inputs.

Independence: frame ranks enumerate complete F2 spans; exact observation windows
are reconstructed from the flat execution schedule. The owner walker and lead
admission binding are not imported. Local cost profiles and observer definitions
remain declared source interfaces. This is a finite ledger check, not a native,
scalar-semantics, Z4-operator, all-size, or ordinary/outer release proof.

Use --repo PATH when this script is outside research/mixed-provider-admission.
Only that installed location permits repository-root inference. All consumed
source paths and byte hashes are emitted in consumed_sources.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path('research/staged544-mixed-fourth-entry')
PREDECESSOR = Path('research/staged544-mixed-idle-rebind')


class LedgerError(ValueError):
    def __init__(self, code, detail=''):
        self.code = code
        self.detail = detail
        super().__init__(code + (': ' + detail if detail else ''))


def require(condition, code, detail=''):
    if not condition:
        raise LedgerError(code, detail)


def rank(vectors):
    """Enumerate at most 512 span elements, without a shared basis routine."""
    span = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'frame-vector')
        span |= {value ^ vector for value in tuple(span)}
    return len(span).bit_length() - 1


def repo_path(argument):
    if argument is not None:
        return Path(argument).resolve()
    here = Path(__file__).resolve().parent
    require(here.name == 'mixed-provider-admission' and here.parent.name == 'research',
            'explicit-repo-required', 'use --repo PATH outside research/mixed-provider-admission')
    return here.parent.parent


class Sources:
    def __init__(self, repo):
        self.repo = repo
        self.consumed = {}
        self.declared = {}
        for name in ('MANIFEST.json', 'EXPORTED-SOURCES.json'):
            manifest = self.read(PACKAGE / name, authenticate=False)
            for relative, entry in manifest.items():
                digest = entry['sha256'] if isinstance(entry, dict) else entry
                path = (PACKAGE / relative).as_posix()
                require(path not in self.declared or self.declared[path] == digest,
                        'conflicting-source-pin', path)
                self.declared[path] = digest

    def raw(self, path, authenticate=True):
        name = path.as_posix()
        raw = (self.repo / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if authenticate:
            require(name in self.declared, 'undeclared-source', name)
            require(digest == self.declared[name], 'source-pin', name)
        self.consumed[name] = digest
        return raw

    def read(self, path, authenticate=True):
        raw = self.raw(path, authenticate)
        return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def exact_windows(order, template, plan, phases):
    clock = {tuple(call): time for time, call in enumerate(order)}
    require(len(order) == len(clock) == 3240, 'order-uniqueness')
    require(set(clock) == {(s, r) for s in range(9) for r in range(360)}, 'order-domain')
    require(all(clock[s, r] < clock[s + 1, r] for r in range(360) for s in range(8)),
            'stage-chronology')
    positive = {entry['child'] for entry in template['idle_children']}
    require(len(positive) == 18 and len(phases['recipes']) == 112, 'bin-dimensions')
    stage_pairs = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    observations = defaultdict(list)
    windows = {}
    stage = None
    index = -1
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            stage, index = event['stage'], 0
        else:
            index += 1
        require(stage is not None, 'event-before-local-stage')
        if kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                stream = 2 * event['pair'] + side
                if child in positive:
                    require(stream == 2 * plan['pairs'][str(child)] + plan['sides'][str(child)],
                            'stream-route')
                for owner in range(360):
                    endpoint = (clock[stage, owner], index)
                    prior = observations[owner, stream][-1] if observations[owner, stream] else (-1, -1)
                    require((owner, child) not in windows, 'duplicate-window')
                    windows[owner, child] = prior, endpoint, stream
        if kind == 'local_cover_sweep':
            touched = (2 * stage_pairs[stage], 2 * stage_pairs[stage] + 1)
        elif kind == 'bridge':
            touched = [2 * pair + side for pair in (event['src'], event['dst']) for side in (0, 1)]
        elif kind == 'terminal':
            touched = range(8)
        else:
            require(kind in ('idle_cover_sweep', 'terminal_Y_translations'), 'unrecognized-event')
            touched = ()
        for owner in range(360):
            for stream in touched:
                observations[owner, stream].append((clock[stage, owner], index))
    shared = defaultdict(list)
    for (owner, child), (low, high, stream) in windows.items():
        if child in positive:
            shared[owner, stream].append((low, high))
    for intervals in shared.values():
        intervals.sort()
        require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])),
                'overlapping-stream-windows')
    return clock, windows, stage_pairs


def scan(rows, order, dispatch, windows, stage_pairs, phases, widths, first_row_override=None):
    require(len(rows) == 1321920, 'role-count')
    used = defaultdict(int)
    same_call = set()
    hosted_mass = 0
    first = {}
    for index, original in enumerate(rows):
        row = first_row_override if index == 0 and first_row_override is not None else original
        require(len(row) == 6 and all(type(value) is int for value in row), 'row-types')
        time, helper, owner, child, port, offset = row
        require((time, helper) == divmod(index, 408), 'row-identity')
        if helper == 0:
            same_call = set()
        require((owner, child) in windows and 0 <= port < 112, 'owner-identity')
        low, high, stream = windows[owner, child]
        require(low < (time, -1) < high, 'strict-observation-window')
        key = owner, child, port
        physical = owner, stream, port
        require(physical not in same_call, 'same-call-alias')
        same_call.add(physical)
        stage, replica = order[time]
        require(4 * owner + stream // 2 != 4 * replica + stage_pairs[stage], 'productive-alias')
        record = phases['recipes'][port]['idle_children'][child]
        axes = record['orthogonal_axes']
        require(len(axes) == len(set(axes)) == record['rank'], 'axis-identity')
        provider = dispatch[stage, replica]
        width = widths[provider][helper]
        require(offset == used[key], 'compact-prefix',
                f'row {index}: expected {used[key]}, got {offset}')
        require(offset + width <= len(axes), 'axis-capacity', f'row {index}')
        used[key] += width
        hosted_mass += width
        if helper == 367 and provider not in first:
            first[provider] = dict(row_index=index, row=row, call=order[time], width=width,
                                   window=[low, high], stream=stream, axis_capacity=len(axes))
    idle = Counter()
    axis_mass = positive_bins = 0
    for owner in range(360):
        for port, recipe in enumerate(phases['recipes']):
            for child, record in enumerate(recipe['idle_children']):
                capacity = len(record['orthogonal_axes'])
                axis_mass += capacity
                positive_bins += bool(capacity)
                left = capacity - used[owner, child, port]
                require(left >= 0, 'negative-complement')
                if left:
                    idle[left] += 1
    require(hosted_mass + sum(r * n for r, n in idle.items()) == axis_mass, 'axis-mass')
    return dict(idle=idle, first=first, hosted_axis_mass=hosted_mass, total_axis_mass=axis_mass,
                positive_bins=positive_bins, occupied_positive_bins=sum(bool(v) for v in used.values()))


def invoice(counts, profiles, idle, expected):
    profile = Counter(idle)
    for provider, count in counts.items():
        for r, n in profiles[provider].items():
            profile[r] += count * n
    require(dict(profile) == {int(r): n for r, n in expected['profile'].items()}, 'complete-profile')
    require(dict(idle) == {int(r): n for r, n in expected['idle'].items()}, 'idle-profile')
    require(sum(r * n for r, n in profile.items()) == 65088 * 360, 'paid-rank-mass')
    return dict(sorted(profile.items()))


def reject(label, expected_code, expected_detail, action):
    try:
        action()
    except LedgerError as error:
        require(error.code == expected_code and expected_detail in error.detail,
                'wrong-control-rejection', f'{label}: {error}')
        return dict(control=label, rejection=error.code, detail=error.detail)
    raise LedgerError('accepted-control', label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, help='repository root')
    parser.add_argument('--controls', action='store_true', help='run three bounded in-memory rejection controls')
    args = parser.parse_args()
    sources = Sources(repo_path(args.repo))
    read = sources.read
    pairs = [('owner/' + n, 'inputs/' + n) for n in
             ('ORDER.json', 'DISPATCH.json', 'MIXED-DISPATCH.json', 'FILL.json.gz',
              'PLAN.json.gz', 'TEMPLATE.json.gz', 'PR4085-PROFILE.json')]
    pairs += [('owner/old-NATIVE-' + s + '.json.gz', 'inputs/NATIVE-' + s + '.json.gz')
              for s in ('base', 'extra')]
    pairs += [('inputs/' + k + '-' + s + '.json.gz', 'inputs/' + k + '-' + s + '.json.gz')
              for k in ('THREE', 'FOUR') for s in ('base', 'extra')]
    for left, right in pairs:
        raw = sources.raw(PACKAGE / left)
        # PR4165's duplicate input is authenticated by exact equality to the pinned PR4088 bytes.
        other = sources.raw(PREDECESSOR / right, authenticate=False)
        require(raw == other, 'cross-package-source', left)
    order = read(PACKAGE / 'owner/ORDER.json')
    template = read(PACKAGE / 'owner/TEMPLATE.json.gz')
    plan = read(PACKAGE / 'owner/PLAN.json.gz')
    phases = read(PACKAGE / 'inputs/DATA-PHASES.json')
    require(template['exact_data_phase_recipe_sha256'] == sources.consumed[(PACKAGE / 'inputs/DATA-PHASES.json').as_posix()],
            'phase-pin')
    clock, windows, stage_pairs = exact_windows(order, template, plan, phases)
    old = read(PACKAGE / 'owner/DISPATCH.json')
    new = read(PACKAGE / 'owner/MIXED-DISPATCH.json')
    require(len(old) == len(new) == 3240, 'dispatch-row-count')
    predecessor = {(s, r): provider for s, r, provider in old}
    dispatch = {(s, r): provider for s, r, provider in new}
    require(len(predecessor) == len(dispatch) == 3240 and set(dispatch) == set(clock) == set(predecessor),
            'dispatch-identity')
    require(new == [[s, r, provider + ('-four' if 109 * clock[s, r] % 324 < 109 else '')]
                    for s, r, provider in old], 'literal-selector')
    counts = Counter(dispatch.values())
    require(counts == Counter({'gauge44': 1040, 'gauge44-four': 528, 'extra': 1110, 'extra-four': 562}),
            'provider-counts')
    origin = read(PACKAGE / 'owner/old-NATIVE-base.json.gz')['helper_origin']
    require(origin == read(PACKAGE / 'owner/old-NATIVE-extra.json.gz')['helper_origin'], 'orientation-origin')
    widths, profiles, inventories = {}, {}, {}
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        for kind, suffix in (('THREE', ''), ('FOUR', '-four')):
            word = read(PACKAGE / f'inputs/{kind}-{tag}.json.gz')
            name = provider + suffix
            require(origin == sorted(set(range(224, 704)) - set(word['removed'])), 'helper-origin')
            widths[name] = [rank(word['helper_final'].get(str(h), [1 << i for i in range(9)]))
                            - rank(word['start_extra'].get(str(h), [])) for h in origin]
            profiles[name] = {int(r): n for r, n in word['report']['local_profile'].items()}
            inventories[name] = dict(sorted(Counter(widths[name]).items()))
            native_kind = 'THREE-CANONICAL' if kind == 'THREE' else 'NATIVE-CANONICAL'
            canonical = read(PACKAGE / f'evidence/{native_kind}-{tag}.json.gz')
            require(canonical['helper_origin'] == origin, 'native-helper-map')
            native_widths = [rank(canonical['frames'][canonical['final'][r]])
                             - rank(canonical['frames'][canonical['start'][r]]) for r in range(224, 632)]
            require(native_widths == widths[name], 'native-candidate-widths')
    for provider in ('gauge44', 'extra'):
        changes = [(h, origin[h], a, b) for h, (a, b) in
                   enumerate(zip(widths[provider], widths[provider + '-four'])) if a != b]
        require(changes == [(367, 601, 8, 7)], 'width-changes')
    fill = read(PACKAGE / 'owner/FILL.json.gz')
    require(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
            and fill['dispatch_overrides'] == [], 'fill-schema')
    rows = fill['rows']
    result = read(PACKAGE / 'RESULT.json')
    def walk(chosen_dispatch=dispatch, first_row_override=None):
        return scan(rows, order, chosen_dispatch, windows, stage_pairs, phases, widths, first_row_override)
    scanned = walk()
    profile = invoice(counts, profiles, scanned['idle'], result)
    controls = []
    if args.controls:
        changed_dispatch = dict(dispatch)
        require(dispatch[tuple(order[0])] == 'extra-four', 'control-t0-provider')
        changed_dispatch[tuple(order[0])] = 'extra'
        controls.append(reject('stamp-three-t0', 'compact-prefix', 'row 29389: expected 8, got 7',
                               lambda: walk(changed_dispatch)))
        bad_row = list(rows[0])
        bad_row[-1] += 1
        controls.append(reject('offset-hole', 'compact-prefix', 'row 0: expected 0, got 1',
                               lambda: walk(first_row_override=bad_row)))
        bad_profiles = {provider: dict(values) for provider, values in profiles.items()}
        bad_profiles['extra-four'][1] += 1
        controls.append(reject('extra-rank-one', 'complete-profile', '',
                               lambda: invoice(counts, bad_profiles, scanned['idle'], result)))
    output = dict(status='PASS_INDEPENDENT_MIXED_LEDGER', provider_counts=dict(counts),
                  width_histograms=inventories, first_helper601_per_provider=scanned.pop('first'),
                  profile=profile, rows=len(rows), exact_windows_including_zero_slots=len(windows),
                  paid_rank_mass=sum(r * n for r, n in profile.items()), controls=controls,
                  consumed_sources=dict(sorted(sources.consumed.items())), **scanned)
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
