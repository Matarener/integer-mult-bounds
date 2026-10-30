"""Build shorter complete G20 scalar windows. Ali Romman / OpenAI Codex.

Apache-2.0. Source and synthesis credits are in NOTICE and ORIGINS.json.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
import synthesize_binary_linear as synthesis


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def tables():
    out = {}
    for n in range(2, 5):
        problem = dict(schema='binary-linear-synthesis/v1', width=n,
                       target=[1 << i for i in range(n)],
                       gates=[dict(op='xor', src=s, dst=d, cost=1)
                              for d in range(n) for s in range(n) if s != d])
        cert = synthesis.synthesize(problem)
        out[n] = (problem['gates'], {int(k, 16): v for k, v in cert['potential'].items()})
    return out


def shortest(events, table):
    roles = sorted({x for e in events for x in e[1:3]})
    n = len(roles); ids = {r: i for i, r in enumerate(roles)}
    target = [1 << i for i in range(n)]
    for e in events:
        target[ids[e[1]]] ^= target[ids[e[2]]]
    state = sum(row << (n * i) for i, row in enumerate(target))
    gates, distance = table[n]; cost = distance[state]; word = []
    while distance[state]:
        for gate in gates:
            prior = synthesis.step(state, gate, n)
            if distance[prior] + 1 == distance[state]:
                word.append(['ADD', roles[gate['dst']], roles[gate['src']], events[0][3]])
                state = prior
                break
        else:
            raise ValueError('No attaining path')
    return word[::-1], cost


def same_endpoint(old, new):
    need(old and all(e[0] == 'ADD' and e[3] == old[0][3] for e in old), 'Old common frame')
    roles = sorted({x for e in old for x in e[1:3]})
    need(all(e[0] == 'ADD' and e[3] == old[0][3] and e[1] in roles and e[2] in roles
             and e[1] != e[2] for e in new), 'New common frame and roles')
    # The literal truth table is separate from the matrix-state search.
    for bits in range(1 << len(roles)):
        outputs = []
        for events in (old, new):
            values = {r: (bits >> i) & 1 for i, r in enumerate(roles)}
            for e in events:
                values[e[1]] ^= values[e[2]]
            outputs.append(values)
        need(outputs[0] == outputs[1], 'Complete local endpoint')


def improve_run(events, table):
    length = len(events); costs = [0] * (length + 1); choices = {}
    for a in range(length - 1, -1, -1):
        costs[a] = 1 + costs[a + 1]; roles = set()
        for b in range(a, length):
            roles.update(events[b][1:3])
            if len(roles) > 4:
                break
            if b == a:
                continue
            new, cost = shortest(events[a:b + 1], table)
            if cost + costs[b + 1] < costs[a]:
                costs[a] = cost + costs[b + 1]; choices[a] = (b + 1, new)
    out, edits, a = [], [], 0
    while a < length:
        if a not in choices:
            out.append(events[a]); a += 1
        else:
            b, new = choices[a]; old = events[a:b]
            same_endpoint(old, new)
            need(len(new) == shortest(old, table)[1], 'Attain certified minimum')
            edits.append(dict(first=a, stop=b, before=old, after=new))
            out.extend(new); a = b
    need(len(out) == costs[0], 'Minimum disjoint-window cover')
    return out, edits


def pass_once(records, table):
    out, edits, i = [], [], 0
    while i < len(records):
        if records[i][0] != 'ADD':
            out.append(records[i]); i += 1
            continue
        stop = i + 1
        while stop < len(records) and records[stop][0] == 'ADD' and records[stop][3] == records[i][3]:
            stop += 1
        new, local = improve_run(records[i:stop], table)
        edits.extend(dict(run_start=i, **e) for e in local)
        out.extend(new); i = stop
    return out, edits


def replay(word):
    width = len(word['start']); rows = [1 << i for i in range(width)]
    frames, norms = word['start'][:], [1] * width
    owned, active = set(word['owned']), set(); boundary, peak, norm_peak = [], 0, 1
    counts, paid = Counter(), Counter()
    for e in word['records']:
        op, d = e[:2]; counts[op] += 1
        if op == 'ADD':
            _, _, s, frame = e
            need(d != s and frames[d] == frames[s] == frame, 'Actual common native frame')
            rows[d] ^= rows[s]; norms[d] += norms[s]
            if d in owned:
                active.add(d)
            norm_peak = max(norm_peak, norms[d]); peak = max(peak, len(active))
            continue
        boundary.append(sha256(canonical([e, rows])).hexdigest())
        if op in ('ERASE', 'INIT'):
            need(d in owned and (op == 'ERASE' or rows[d] == 0), 'Owned zero precondition')
            rows[d] = norms[d] = 0; frames[d] = e[2]; active.discard(d)
        else:
            need(op in ('Q', 'ZERO_Q') and frames[d] == e[2], 'Native route source')
            need(op == 'Q' or rows[d] == 0, 'Whole zero free move')
            frames[d] = e[3]
            if op == 'Q':
                paid[e[4]] += 1
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    need(rows == expected and frames == word['final'], 'All input columns and final frames')
    dual = [1 << i for i in range(width)]
    for e in reversed(word['records']):
        if e[0] == 'ADD':
            dual[e[2]] ^= dual[e[1]]
        elif e[0] in ('ERASE', 'INIT'):
            dual[e[1]] = 0
    transposed = [sum(((row >> i) & 1) << j for j, row in enumerate(expected)) for i in range(width)]
    need(dual == transposed, 'Separate reverse endpoint')
    return dict(counts=dict(counts), paid=dict(sorted(paid.items())), peak_owned=peak,
                positive_majorant=str(norm_peak), majorant_bits=norm_peak.bit_length(),
                boundary_sha256=sha256(canonical(boundary)).hexdigest(), endpoint_columns=width)


def build():
    for row in json.loads((ROOT / 'ORIGINS.json').read_text()):
        need(sha256((ROOT / row['local']).read_bytes()).hexdigest() == row['sha256'],
             'Source bytes: ' + row['local'])
    source = json.loads(gzip.decompress((ROOT / 'source/WORD.json.gz').read_bytes()))
    table = tables(); word, rounds = deepcopy(source), []
    while True:
        new, edits = pass_once(word['records'], table)
        if not edits:
            break
        need(len(new) < len(word['records']), 'Strict finite descent')
        rounds.append(edits); word['records'] = new
    before, after = replay(source), replay(word)
    need(before['paid'] == after['paid'] and before['boundary_sha256'] == after['boundary_sha256'],
         'Every native or owned boundary keeps its complete value')
    need(after['peak_owned'] <= before['peak_owned'], 'No new owned reserve')
    result = dict(status='PASS_G20_FOUR_ROLE_RESYNTHESIS', source=before, constructed=after,
                  rounds=len(rounds), replacements=sum(map(len, rounds)),
                  saved_local_adds=before['counts']['ADD'] - after['counts']['ADD'],
                  saved_18_call_adds=18 * (before['counts']['ADD'] - after['counts']['ADD']),
                  group_sizes={n: len(t[1]) for n, t in table.items()},
                  word_sha256=sha256(canonical(word)).hexdigest(),
                  remaining_improving_windows=0, new_kappa=False)
    calls = json.loads((ROOT / 'source/CALLS.json').read_text())
    ordinary = json.loads((ROOT / 'source/ORDINARY-RESULT.json').read_text())
    need(len(calls) == 18 and all(c['core_end'] - c['core_begin'] == len(source['records'])
                                 and c['new_direction_inverse'] is True for c in calls),
         'Eighteen complete calls use this source orientation')
    base_count = ordinary['fee_bounds']['base_counts']['coarse_primitive_count_with_dimension_work']
    need(base_count == 952838314401, 'Exact source finite allowance')
    result['source_primitive_count'] = base_count
    result['substitution_primitive_count'] = base_count - 2 * result['saved_18_call_adds']
    first = next(e for r in rounds for e in r if e['after'])
    bad = deepcopy(first['after']); bad[0][1], bad[0][2] = bad[0][2], bad[0][1]
    rejected = []
    for label, new in [('wrong_direction', bad), ('missing_gate', first['after'][1:]),
                       ('changed_frame', [e[:3] + [-1] for e in first['after']])]:
        try:
            same_endpoint(first['before'], new)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('Control was accepted: ' + label)
    bad_word = deepcopy(word)
    bad_word['records'] = [e for e in bad_word['records'] if e[0] != 'ERASE']
    try:
        replay(bad_word)
    except ValueError:
        rejected.append('missing_owned_erasure')
    else:
        raise ValueError('Erasure control was accepted')
    result['rejected_controls'] = rejected
    return word, rounds, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); word, edits, result = build()
    outputs = {'WORD.json.gz': gzip.compress(canonical(word), mtime=0),
               'EDITS.json': json.dumps(edits, indent=2).encode() + b'\n',
               'RESULT.json': json.dumps(result, indent=2).encode() + b'\n'}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, data in outputs.items():
            (args.output / name).write_bytes(data)
    else:
        for name, data in outputs.items():
            retained = (ROOT / name).read_bytes()
            need((gzip.decompress(retained) == gzip.decompress(data)) if name.endswith('.gz')
                 else retained == data, 'Rebuilt output: ' + name)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
