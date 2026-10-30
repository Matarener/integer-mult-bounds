"""Authenticate and independently audit the three fixed destination sums."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import audit as A
import controls


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [row for row in rows if row['usage'] == 'input']
    for row in inputs:
        A.need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
               'source hash ' + row['path'])
    return len(inputs)


def read(name):
    data = (HERE / 'inputs' / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    inputs = authenticate()
    before, after = [read(tag + '-WORD.json.gz') for tag in ('before', 'after')]
    records = [read(tag + '-RESULT.json') for tag in ('before', 'after')]
    for word, receipt in zip((before, after), records):
        A.need(sha256(canonical(word)).hexdigest() == receipt['canonical_word_sha256'], 'Published whole word')
    A.need(all(before[k] == after[k] for k in ('public', 'live', 'ports', 'frames')), 'Unchanged field and frame alphabet')
    main_roles = set(before['live']) | {i + 112 for i in before['live']}
    A.need(all(before[side][i] == after[side][i] for side in ('initial', 'final') for i in main_roles),
           'Every inherited main interface stays fixed')
    A.need(records[0]['physical_caller'] == records[1]['physical_caller'], 'Same inherited physical caller receipt')
    counted = [A.inventory(word) for word in (before, after)]
    for count, receipt in zip(counted, records):
        A.need(json.loads(json.dumps(count)) == receipt['local'], 'Every published local inventory field')
    traced = A.trace(before, after)
    plan = read('after-PLAN.json')
    A.need(plan['source_canonical_sha256'] == records[0]['canonical_word_sha256']
           and plan['steps'][-1]['output_sha256'] == records[1]['canonical_word_sha256'],
           'Plan endpoint source identities')
    A.need(traced['old_copy_values'] == 23, 'Every retained COPY value')
    witness = read('after-WITNESS.json')
    A.need(len(traced['groups']) == len(witness) == 3, 'All three source accumulations')
    for item in witness:
        group = item['accumulation']
        found = traced['groups'][group['owned_role']]
        A.need((found['destination'], found['frame_before'], found['frame_after']) ==
               (group['role'], group['before'], group['after']), 'Source group identity')
    invoices = [A.billing(word, count, receipt) for word, count, receipt in zip((before, after), counted, records)]
    deltas = {}
    for name in ('paid', 'helpers'):
        keys = set(counted[0][name]) | set(counted[1][name])
        deltas[name] = {k: counted[1][name].get(k, 0) - counted[0][name].get(k, 0)
                        for k in sorted(keys) if counted[1][name].get(k, 0) != counted[0][name].get(k, 0)}
    A.need(deltas == {'paid': {1: -6, 2: 4, 6: 2, 7: -2},
                      'helpers': {1: -2, 2: 2, 7: 2, 8: -2}}, 'Exact signed rank change')
    prefix = []
    value = 0
    for x, y in zip([1, 1, 1, 1, 7, 7, 7, 7], [0, 0, 2, 2, 6, 6, 8, 8]):
        value += x - y
        prefix.append(value)
    A.need(min(prefix) >= 0 and prefix[-1] == 0 and max(prefix) > 0, 'Strict concave improvement')
    result = {'scope': 'Exact trace and inventory under the native frame-conversion premise; no supplier admission.',
              'source_inputs': inputs, 'trace': traced, 'local': counted, 'full_invoices': invoices,
              'local_changes': deltas, 'majorization_prefixes': prefix,
              'controls': controls.run(before, after, records[1], counted[1])}
    A.need(authenticate() == inputs, 'Retained source inventory')
    raw = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.record:
        (HERE / 'RESULT.json').write_text(raw)
    else:
        A.need((HERE / 'RESULT.json').read_text() == raw, 'Exact typed canonical audit receipt')
    print('PASS_P104_ALL_THREE_ACCUMULATION_TRACES_AND_INVOICES')


if __name__ == '__main__':
    main()
