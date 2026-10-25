#!/usr/bin/env python3
"""Literal retained-owner replay for an independently proved changed native word.

Accepts two NATIVE632-format words whose helper widths only decrease. Reuses
every original source owner and emits compacted offsets, an independently
recounted full invoice and an exact root. Native local correctness must be
proved separately; this command never treats a supplied word as its own proof.
The chronology predicates follow the retained credited PR3638 owner audit.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
import gzip
import json
from pathlib import Path
from local_repack import read, rank, module, REPO


def span(axes):
    values = {0}
    for axis in axes:
        values |= {v ^ axis for v in values}
    return frozenset(values)


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, required=True)
    ap.add_argument('--base-word', type=Path, required=True)
    ap.add_argument('--extra-word', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    data = args.followup/'artifact/live-source/research/staged544-producer-return/inputs'
    inv_path = REPO/'research/kappa-global-continuation/invoice-analysis/invoice.py'
    I = module(inv_path, 'compacted_invoice')
    frozen_path = inv_path.parent/'evidence/RESULT.json'
    frozen = I.read(frozen_path)
    I.need(frozen['script_sha256'] == I.digest(inv_path), 'frozen invoice engine binding')
    I.need(frozen['arithmetic_engine_sha256'] == I.digest(I.ENGINE_PATH), 'outward-rational engine binding')
    for rel, expected in frozen['m73_literal_allocation']['input_sha256'].items():
        I.need(I.digest(args.followup/rel) == expected, 'retained input binding: '+rel)
    order = read(data/'ORDER.json')
    dispatch = {(s, r): p for s, r, p in read(data/'DISPATCH.json')}
    clock = {tuple(call): i for i, call in enumerate(order)}
    I.need(len(order) == 3240 and set(clock) == {(s, r) for s in range(9) for r in range(360)}, 'complete clock')
    I.need(all([clock[s, r] for s in range(9)] == sorted(clock[s, r] for s in range(9)) for r in range(360)), 'source stage order')
    I.need(set(dispatch) == set(clock), 'dispatch coverage')
    old_widths, new_widths, local, changes, supplied = {}, {}, {}, {}, {}
    for tag, provider, new_path in (('base', 'gauge44', args.base_word), ('extra', 'extra', args.extra_word)):
        old = read(data/f'NATIVE-{tag}.json.gz')
        new = read(new_path)
        supplied[provider] = {'path': str(new_path), 'sha256': I.digest(new_path)}
        I.need(new['R'] == old['R'] == 408 and len(new['start']) == len(new['final']) == 632,
               'same native live and helper namespace')
        I.need(new['ports'] == old['ports'] and new['helper_origin'] == old['helper_origin'],
               'same port labels and actual helper identities')
        I.need(new['zero_buffers'] == old['zero_buffers'] and len(new['zero_buffers']) == 91,
               'same private zero stock')
        os = [span(v) for v in old['frames']]
        ns = [span(v) for v in new['frames']]
        for end in ('start', 'final'):
            I.need(all(ns[new[end][r]] == os[old[end][r]] for r in range(224)),
                   'unchanged ordinary data boundary spans')
        ow = [rank(old['frames'][old['final'][r]])-rank(old['frames'][old['start'][r]]) for r in range(224, 632)]
        nw = [rank(new['frames'][new['final'][r]])-rank(new['frames'][new['start'][r]]) for r in range(224, 632)]
        I.need(all(0 < b <= a for a, b in zip(ow, nw)), 'only positive-width decreases in this fast path')
        old_widths[provider], new_widths[provider] = ow, nw
        local[provider] = {int(r): n for r, n in new['local_profile'].items()}
        I.need(all(0 < r < 73 and type(n) is int and n >= 0 for r, n in local[provider].items()), 'supplied local profile schema')
        I.need(local[provider].get(8) == 8 and sum(r*n for r, n in local[provider].items()) == 1792+64+sum(nw),
               'unchanged eight centres and complete local width accounting')
        changes[provider] = [{'native_register': 224+h, 'borrowed_origin': new['helper_origin'][h],
                              'old_width': a, 'new_width': b} for h, (a, b) in enumerate(zip(ow, nw)) if a != b]
    template = read(data/'TEMPLATE.json.gz')
    plan = read(data/'PLAN.json.gz')
    caps = {c['child']: c['rank'] for c in template['idle_children']}
    I.need(len(caps) == 18 and sum(caps.values()) == 432, 'actual retained idle geometry')
    families = {c: 2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in caps}
    windows = {}
    for owner in range(360):
        touched, current = {}, None
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                current = clock[event['stage'], owner]
                pair = next(e['pair'] for e in template['recipe'] if e['kind'] == 'local' and e['stage'] == event['stage'])
                touched[pair] = current
            elif kind == 'bridge':
                I.need(current is not None, 'bridge has a source time')
                touched[event['src']] = touched[event['dst']] = current
            elif kind == 'idle_cover_sweep':
                I.need(current is not None, 'idle has a source time')
                for child in event['child_indices']:
                    if child in caps:
                        I.need((owner, child) not in windows, 'unique source idle child')
                        windows[owner, child] = caps[child], touched.get(event['pair'], -1), current
            else:
                I.need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family', 'terminal_Y_translations', 'terminal'),
                       'retained source schedule grammar')
    I.need(len(windows) == 360*18, 'all physical windows')
    fw = defaultdict(list)
    for (owner, child), (_, low, high) in windows.items():
        fw[owner, families[child]].append((low, high))
    for intervals in fw.values():
        I.need(all(max(a, c) >= min(b, d) for i, (a, b) in enumerate(intervals) for c, d in intervals[i+1:]),
               'a physical family has no overlapping source windows')
    fill = read(data/'FILL.json.gz')
    I.need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'] and not fill['dispatch_overrides'],
           'literal retained allocation schema')
    I.need(len(fill['rows']) == 3240*408, 'every helper call represented')
    used_old, used_new = Counter(), Counter()
    rows = []
    seen = set()
    profile = Counter()
    for t, pair in enumerate(order):
        profile.update({r: n for r, n in local[dispatch[tuple(pair)]].items()})
    changed_offsets = 0
    for i, row in enumerate(fill['rows']):
        I.need(len(row) == 6 and all(type(v) is int for v in row), 'integer literal owner row')
        t, h, owner, child, port, offset = row
        I.need(t == i//408 and h == i % 408, 'ordered complete helper identities')
        if h == 0:
            seen = set()
        I.need((owner, child) in windows and 0 <= port < 112, 'actual owner child and port')
        capacity, low, high = windows[owner, child]
        I.need(low < t <= high, 'strict lower and closed upper physical source interval')
        physical = owner*896+families[child]*112+port
        I.need(physical not in seen, 'same-call physical-family injection')
        seen.add(physical)
        provider = dispatch[tuple(order[t])]
        key = owner, child, port
        I.need(offset == used_old[key], 'source fill has compact chronological prefix')
        used_old[key] += old_widths[provider][h]
        new_offset = used_new[key]
        I.need(new_offset <= offset, 'width decreases never advance a prefix')
        used_new[key] += new_widths[provider][h]
        I.need(used_old[key] <= capacity and used_new[key] <= capacity, 'old and new bin capacities')
        changed_offsets += new_offset != offset
        rows.append([t, h, owner, child, port, new_offset])
    idle = Counter()
    for (owner, child), (capacity, _, _) in windows.items():
        for port in range(112):
            rem = capacity-used_new[owner, child, port]
            if rem:
                idle[rem] += 1
    profile.update(idle)
    I.need(sum(r*n for r, n in profile.items()) == 65088*360, 'complete raw deficit320 per replica')
    I.need(max(profile) <= I.C.max_idle_rank(73), 'retained outer rank guard')
    new_price = I.moment(profile, 73, 896*360, I.TARGET)
    old_price = I.moment(I.BASE, 73, 896*360, I.TARGET)
    result = {'status': 'PASS_LITERAL_COMPACTED_OWNER_ALLOCATION_AND_EXACT_INVOICE',
              'script_sha256': I.digest(Path(__file__)), 'frozen_invoice_receipt_sha256': I.digest(frozen_path),
              'shared_utility_sha256': I.digest(Path(__file__).with_name('local_repack.py')),
              'supplied_native_words': supplied, 'width_changes': changes,
              'native_local_profile_source': 'Supplied native word receipts; local operator correctness is an external proof obligation, not inferred by this allocation checker.',
              'replicas': 360, 'calls': 3240, 'helper_roles': len(rows), 'productive_families': 322560,
              'physical_family_upper': 323069, 'same_call_family_injection_checked': True,
              'complete_source_windows_checked': len(windows), 'compacted_offset_changes': changed_offsets,
              'provider_local_profiles': local, 'idle_profile': dict(sorted(idle.items())),
              'full_profile': dict(sorted(profile.items())), 'raw_rank_mass': 65088*360,
              'raw_normalizer': 73*896*360, 'root': I.root(profile, 73, 896*360),
              'target_residual': I.interval(new_price[0]-1, new_price[1]-1),
              'strictly_improves_actual_baseline': new_price[1] < old_price[0],
              'strictly_passes_target': new_price[1] < 1,
              'limitations': ['Does not prove the supplied changed local words or their native phases.',
                              'Retains the inherited all-size hosting, precision/tape, analytic and bit obligations.']}
    args.out.mkdir(parents=True, exist_ok=True)
    payload = {'columns': fill['columns'], 'dispatch_overrides': [], 'rows': rows}
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    (args.out/'FILL.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (args.out/'PROFILE.json').write_text(json.dumps(dict(sorted(profile.items())), indent=2)+'\n')
    result['fill_sha256'] = I.digest(args.out/'FILL.json.gz')
    (args.out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    print('root', result['root']['decimal'], 'actual_gain', result['strictly_improves_actual_baseline'],
          'target_pass', result['strictly_passes_target'])


if __name__ == '__main__':
    main()
