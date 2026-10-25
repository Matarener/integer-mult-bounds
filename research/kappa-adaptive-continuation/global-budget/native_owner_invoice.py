#!/usr/bin/env python3
"""Replay the attained PR3815 allocation with two width-preserving native words.

Every literal owner row is rechecked. Paid local children are independently
recounted from both emitted native programs, rather than trusting the supplied
histogram. Full native operator correctness and complete outer admission are
separate gates; this certificate binds their concrete compiled inputs.
Chronology predicates follow the credited PR3638 / PR3734 owner audit.
Apache-2.0; substantial OpenAI Codex assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ADOPTED = HERE.parent/'sources/PR3815/research/staged544-clock-ceiling'
OLD = ADOPTED.parent/'staged544-producer-return'


def basis(rows):
    pivots = {}
    for row in rows:
        for bit in sorted(pivots, reverse=True):
            if row & (1 << bit):
                row ^= pivots[bit]
        if row:
            bit = row.bit_length()-1
            for other in pivots:
                if pivots[other] & (1 << bit):
                    pivots[other] ^= row
            pivots[bit] = row
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def recount(I, word, events):
    """Literal positive child ranks and common frames, in either orientation."""
    frames = word['frames']
    current = word['start'].copy()
    paid, private, zlive = Counter(), {}, set()
    for event in events:
        tag = event[0]
        if tag == 'climb':
            _, phase, reg, old, new, rank = event
            I.need(current[reg] == old, 'literal climb source frame')
            I.need(basis(frames[old]+frames[new]) == basis(frames[new]), 'nested positive climb')
            I.need(rank == len(basis(frames[new]))-len(basis(frames[old])) > 0, 'recounted climb rank')
            paid[rank] += 1
            current[reg] = new
        elif tag == 'center':
            _, reg, old, new, rank = event
            I.need(private.get(('C', reg)) == old, 'center scratch source frame')
            a, b = basis(frames[old]), basis(frames[new])
            I.need(rank == abs(len(a)-len(b)) > 0, 'recounted center rank')
            I.need(basis(frames[old]+frames[new]) in (a, b), 'nested center child')
            private['C', reg] = new
            paid[rank] += 1
        elif tag == 'warp':
            _, reg, op, old, new = event
            I.need(op != 0 and len(basis(frames[old])) == len(basis(frames[new])), 'zero-rank warp')
            if reg[0] == 'L':
                I.need(current[reg[1]] == old, 'warp current native frame')
                current[reg[1]] = new
            else:
                I.need(reg[0] == 'Z' and reg[1] in zlive and old == new == 1, 'owned warp frame')
        elif tag == 'zero_buffer':
            _, action, reg = event
            I.need(reg in word['zero_buffers'], 'owned zero identifier')
            if action == 'alloc':
                I.need(reg not in zlive, 'unique zero allocation')
                zlive.add(reg)
            else:
                I.need(action == 'free' and reg in zlive, 'live zero release')
                zlive.remove(reg)
        elif tag == 'scalar':
            op, frame = event[1:]
            target = tuple(op[1])
            if op[0] == 'clear':
                I.need(target[0] == 'C', 'only center scratch cleared')
                private[target] = frame
                continue
            regs = [target]+([tuple(op[2])] if op[0] in ('add', 'copy') else [])
            I.need(op[0] in ('add', 'copy', 'scale'), 'scalar grammar')
            for reg in regs:
                if reg[0] == 'L':
                    I.need(current[reg[1]] == frame, 'literal scalar common native frame')
                elif reg[0] == 'Z':
                    I.need(reg[1] in zlive and frame == 1, 'owned zero common frame')
                else:
                    I.need(reg[0] == 'C' and private.get(reg) == frame, 'center scalar common frame')
        else:
            I.need(tag in ('phase', 'adapter', 'residual_adapter'), 'emitted native grammar')
    I.need(current == word['final'] and not zlive, 'complete emitted native endpoint')
    return dict(sorted(paid.items()))


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--base-local', type=Path, required=True)
    ap.add_argument('--extra-local', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    inv = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    spec = importlib.util.spec_from_file_location('native_owner_exact_invoice', inv)
    I = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(I)
    receipt_path = HERE/'PR3815-INDEPENDENT-REVIEW.json'
    receipt = I.read(receipt_path)
    I.need(receipt['status'] == 'PASS_FRESH_PR3815_OWNERS_AND_INDEPENDENT_EXACT_PRICE_DUAL', 'attained source review')
    for rel, expected in receipt['input_sha256'].items():
        I.need(I.digest(REPO/rel) == expected, 'attained source binding: '+rel)
    widths, profiles, inputs = {}, {}, {}
    for tag, provider, folder in (('base', 'gauge44', args.base_local), ('extra', 'extra', args.extra_local)):
        old_path = OLD/f'inputs/NATIVE-{tag}.json.gz'
        word_path, programs_path = folder/'CANONICAL-WORD.json.gz', folder/'LOCAL-PROGRAMS.json.gz'
        checks_path = folder/'LOCAL-CHECKS.json'
        replay_path, phases_path = folder/'INDEPENDENT-LOCAL-REPLAY.json', folder/'CLIFFORD-REVIEW.json'
        complete_path, input_path = folder.parents[1]/'RESULT.json', folder.parents[1]/'INPUT.json.gz'
        complete = I.read(complete_path)
        I.need(complete['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY'
               and all(step['exit_code'] == 0 for step in complete['steps']), 'complete five-stage native replay')
        I.need(complete['word_sha256'] == I.digest(input_path), 'native complete input binding')
        for rel, expected in complete['source_sha256'].items():
            I.need(I.digest(folder.parents[1]/'source'/rel) == expected, 'native compiler source binding')
        replay, phases = I.read(replay_path), I.read(phases_path)
        I.need(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'independent native operator replay')
        I.need(phases['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'native phase replay')
        I.need(replay['canonical_word_sha256'] == phases['canonical_word_sha256'] == I.digest(word_path),
               'native independent/phase proofs bind the supplied canonical word')
        I.need(replay['local_programs_sha256'] == I.digest(programs_path), 'native replay binds emitted programs')
        old, word = I.read(old_path), I.read(word_path)
        I.need(word['R'] == old['R'] == 408 and len(word['start']) == len(word['final']) == 632, 'native dimensions')
        for name in ('ports', 'helper_origin', 'zero_buffers'):
            I.need(word[name] == old[name], 'unchanged native '+name)
        I.need(len(word['zero_buffers']) == 91, 'private stock count')
        for end in ('start', 'final'):
            I.need(all(basis(word['frames'][word[end][r]]) == basis(old['frames'][old[end][r]])
                       for r in range(632)), 'all data/helper endpoint subspaces unchanged')
        width = [len(basis(word['frames'][word['final'][r]]))-len(basis(word['frames'][word['start'][r]]))
                 for r in range(224, 632)]
        original = [len(basis(old['frames'][old['final'][r]]))-len(basis(old['frames'][old['start'][r]]))
                    for r in range(224, 632)]
        I.need(width == original and min(width) > 0, 'identical ordered positive helper widths')
        widths[provider] = width
        checks, programs = I.read(checks_path), I.read(programs_path)
        local = {int(r): n for r, n in word['local_profile'].items()}
        for orientation in ('forward', 'backward'):
            events = programs[orientation]
            raw = json.dumps(events, sort_keys=True, separators=(',', ':')).encode()
            I.need(hashlib.sha256(raw).hexdigest() == checks[orientation]['sha256'], 'emitted program payload pin')
            I.need(recount(I, word, events) == local, 'independently recounted native child histogram')
            I.need(checks[orientation]['all_columns'] == 632 and checks[orientation]['zero_buffers_returned_to_zero'] == 91,
                   'source complete scalar/owned checks')
        I.need(sum(r*n for r, n in local.items()) == 1792+64+sum(width), 'complete native width/rank conservation')
        profiles[provider] = local
        inputs[provider] = {str(p.resolve().relative_to(REPO)): I.digest(p)
                            for p in (word_path, programs_path, checks_path, old_path, replay_path,
                                      phases_path, complete_path, input_path)}
    order = I.read(ADOPTED/'inputs/ORDER.json')
    dispatch = {(s, r): pid for s, r, pid in I.read(OLD/'inputs/DISPATCH.json')}
    clock = {tuple(call): t for t, call in enumerate(order)}
    I.need(len(order) == 3240 and set(clock) == {(s, r) for s in range(9) for r in range(360)}, 'complete source clock')
    I.need(set(dispatch) == set(clock), 'complete original dispatch')
    I.need(all([clock[s, r] for s in range(9)] == sorted(clock[s, r] for s in range(9)) for r in range(360)), 'replica stage order')
    template, plan = I.read(OLD/'inputs/TEMPLATE.json.gz'), I.read(OLD/'inputs/PLAN.json.gz')
    caps = {child['child']: child['rank'] for child in template['idle_children']}
    families = {c: 2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in caps}
    pairs = {event['stage']: event['pair'] for event in template['recipe'] if event['kind'] == 'local'}
    windows = {}
    for owner in range(360):
        touched, time = {}, None
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                time = clock[event['stage'], owner]
                touched[pairs[event['stage']]] = time
            elif kind == 'bridge':
                I.need(time is not None, 'bridge source time')
                touched[event['src']] = touched[event['dst']] = time
            elif kind == 'idle_cover_sweep':
                I.need(time is not None, 'idle source time')
                for c in event['child_indices']:
                    if c in caps:
                        I.need((owner, c) not in windows, 'unique physical window')
                        windows[owner, c] = caps[c], touched.get(event['pair'], -1), time
            else:
                I.need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family', 'terminal_Y_translations', 'terminal'),
                       'original schedule grammar')
    I.need(len(windows) == 6480, 'all actual idle windows')
    intervals = defaultdict(list)
    for (owner, child), (_, lo, hi) in windows.items():
        intervals[owner, families[child]].append((lo, hi))
    for times in intervals.values():
        I.need(all(max(a, c) >= min(b, d) for j, (a, b) in enumerate(times) for c, d in times[j+1:]),
               'disjoint windows on each physical family')
    fill = I.read(ADOPTED/'inputs/FILL.json.gz')
    I.need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'] and not fill['dispatch_overrides'], 'literal source fill schema')
    I.need(len(fill['rows']) == 1321920, 'all helper roles')
    used, seen = Counter(), set()
    for j, row in enumerate(fill['rows']):
        I.need(len(row) == 6 and all(type(value) is int for value in row), 'integer physical owner row')
        time, helper, owner, child, port, offset = row
        I.need(time == j//408 and helper == j%408, 'ordered complete helper identities')
        if helper == 0:
            seen = set()
        I.need((owner, child) in windows and 0 <= port < 112, 'physical owner slot')
        cap, lo, hi = windows[owner, child]
        I.need(lo < time <= hi, 'literal strict lower/closed upper time window')
        physical = 896*owner+112*families[child]+port
        I.need(physical not in seen, 'same-call physical family injection')
        seen.add(physical)
        stage, replica = order[time]
        I.need(physical//224 != 4*replica+pairs[stage], 'productive data/helper nonaliasing')
        key = owner, child, port
        width = widths[dispatch[stage, replica]][helper]
        I.need(offset == used[key] and offset+width <= cap, 'compact chronological offset and rank capacity')
        used[key] += width
    idle = Counter()
    for (owner, child), (cap, _, _) in windows.items():
        for port in range(112):
            rem = cap-used[owner, child, port]
            I.need(rem >= 0, 'physical bin capacity')
            if rem:
                idle[rem] += 1
    I.need(idle == {1: 84240, 3: 23328, 5: 4320, 48: 137952}, 'attained unchanged idle profile')
    paid = Counter(idle)
    for stage, replica in order:
        paid.update(profiles[dispatch[stage, replica]])
    I.need(sum(r*n for r, n in paid.items()) == 65088*360, 'complete raw deficit remains320 per replica')
    I.need(max(paid) <= I.C.max_idle_rank(73), 'complete recursive rank guard')
    root = I.root(paid, 73, 322560)
    R = I.module(OLD/'rational_price.py', 'native_owner_second_price_engine')
    signed = dict(paid)
    signed[73] = -322560
    low, high = map(F, root['rational'])
    I.need(R.interval(signed, low)[1] < 0 < R.interval(signed, high)[0], 'independent source price engine agrees')
    price = dict(status='PASS_EXACT_ACTUAL_CHRONOLOGICAL_PROFILE_PRICE', replicas=360,
                 profile=dict(sorted(paid.items())), root_lower=str(low), root_upper=str(high),
                 lower_decimal=root['decimal'][0], upper_decimal=root['decimal'][1],
                 predecessor_pr=3815, predecessor_root_lower=str(I.TARGET),
                 gain_lower_over_predecessor=str(low-I.TARGET),
                 scope='Exact two-engine root for the replayed physical owner allocation; full native and outer admission are separate bound gates.')
    result = dict(status='PASS_LITERAL_CHANGED_NATIVE_OWNERS_AND_TWO_ENGINE_INVOICE',
                  script_sha256=I.digest(Path(__file__)), source_review_sha256=I.digest(receipt_path),
                  supplied_native_inputs=inputs, native_profile_recount_orientations=4,
                  provider_local_profiles=profiles, source_windows=6480, helper_rows=1321920,
                  productive_families=322560, physical_families=323069, replicas=360, calls=3240,
                  helper_widths_unchanged_in_order=True, all_native_endpoint_subspaces_unchanged=True,
                  physical_injection_and_data_nonaliasing_checked=True,
                  idle_profile=dict(sorted(idle.items())), profile=dict(sorted(paid.items())),
                  raw_rank_mass=65088*360, root=root, price=price,
                  improves_adopted_ceiling=low>I.TARGET,
                  conditional_kappa=str(low-F(1, 10**46)-F(1, 10**70)),
                  scope='Complete finite allocation and two-engine price check. Native phase/operator replay and changed-word outer ledgers must also pass; their costs are not inferred from these arithmetic checks.')
    args.out.mkdir(parents=True, exist_ok=True)
    for name, payload in (('PROFILE.json', dict(sorted(paid.items()))), ('PRICE.json', price), ('RESULT.json', result)):
        (args.out/name).write_text(json.dumps(payload, indent=2)+'\n')
    print(result['status'], 'root', root['decimal'], 'productive', 322560, 'physical', 323069)


if __name__ == '__main__':
    main()
