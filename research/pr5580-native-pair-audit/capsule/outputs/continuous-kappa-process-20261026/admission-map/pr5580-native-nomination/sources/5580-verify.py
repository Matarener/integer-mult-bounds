"""Check the changed contact, complete caller and conditional kappa.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retained sources and their contributors are listed in SOURCES.json.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import closure, load, need, read
from construct import construct


def inventory(base, word):
    for key in base:
        if key != 'program':
            need(word[key] == base[key], 'Unchanged word field: ' + key)
    def scalar(program):
        return [e[:-1] for e in program if e[0] != 'MOVE']
    need(scalar(word['program']) == scalar(base['program']),
         'Same ordered scalar and owned operations')
    old = [e for e in base['program'] if e[0] != 'MOVE']
    new = [e for e in word['program'] if e[0] != 'MOVE']
    changes = [(a, b) for a, b in zip(old, new) if a != b]
    need(changes == [(['ADD', 451, 228, '1', 262],
                     ['ADD', 451, 228, '1', 737])], 'One changed scalar chart')
    def bill(w):
        return Counter(abs(len(w['frames'][e[2]]) - len(w['frames'][e[3]]))
                       for e in w['program'] if e[0] == 'MOVE')
    before, after = bill(base), bill(word)
    delta = {r: after[r] - before[r] for r in before.keys() | after.keys()
             if after[r] != before[r]}
    need(delta == {2: 1, 3: -2, 4: 1}, 'Exact changed paid profile')
    return {'source_events': len(base['program']), 'events': len(word['program']),
            'ordered_scalar_events': len(old), 'changed_contacts': changes,
            'local_paid_delta': delta, 'global_paid_delta': {r: 18*n for r, n in delta.items()},
            'all_public_endpoints_fixed': True, 'all_productive_targets_fixed': True,
            'owned_lifetimes_fixed': True}


def controls(L, base, word):
    variants = {}
    bad = deepcopy(word)
    bad['program'].remove(['MOVE', 228, 262, 737, False])
    variants['missing_source_transport'] = bad
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD', 451, 228, '1', 737])
    event[-1] = 262
    variants['old_contact_frame'] = bad
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD', 451, 228, '1', 737])
    event[-2] = '2'
    variants['wrong_scalar_coefficient'] = bad
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['MOVE', 228, 737, 520, False])
    event[3] = 262
    variants['non_nested_return'] = bad
    rejected = {}
    for name, bad in variants.items():
        try:
            L.replay(bad)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('Accepted invalid word: ' + name)
    try:
        inventory(base, base)
    except ValueError as error:
        rejected['unchanged_word'] = str(error)
    else:
        raise ValueError('Accepted unchanged word as a profile improvement')
    print('PASS contact controls', rejected, flush=True)
    return rejected


def ceiling(E, targets, paid):
    """Bound the moment derivative on the retained BIT band."""
    cap = Q('0.0034')
    lower = upper = Q(0)
    for rank in targets.keys() | paid.keys():
        coefficient = paid.get(rank, 0) - targets.get(rank, 0)
        power = (E.power(rank, 1-cap)[0], Q(rank))
        term = E.scale(E.mul(power, E.log_bounds(rank)), coefficient)
        lower += term[0]
        upper += term[1]
    need(upper < 0, 'Strictly decreasing complete moment on the retained BIT band')
    return {'kappa_interval': [Q(0), cap], 'moment_derivative': [lower, upper],
            'scope': 'This fixed paid and target invoice; the inherited BIT cap is retained.'}


def main():
    sources = read(HERE/'SOURCES.json')
    for pin in sources['external_inputs']:
        raw = (HERE/pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source bytes: ' + pin['local_path'])
        header = ('blob ' + str(len(raw)) + '\0').encode()
        from hashlib import sha1
        need(sha1(header + raw).hexdigest() == pin['git_blob'], 'Source Git object: ' + pin['local_path'])
    base = read(HERE/'inputs/pr5569-WORD.json.gz')
    word = read(HERE/'WORD.json.gz')
    need(construct(base) == word, 'Regenerated complete word payload')
    inv = inventory(base, word)
    source_price = (HERE/'inputs/pr5569-pricing.py').read_text()
    for before, after in (
            ("KAPPA, TESTED = Q('.00308181'), Q('.0030818105')",
             "KAPPA, TESTED = Q('.00308189'), Q('.0030818905')"),
            ("PREVIOUS = Q('.00304117')", "PREVIOUS = Q('.00308181')"),
            ("'kappa_decimal':'.00308181'", "'kappa_decimal':'.00308189'"),
            ("'previous_open_pr5545':PREVIOUS", "'previous_open_pr5569':PREVIOUS"),
            ("'tensor_native_growth_bound':'Each rank-r Gaussian has row l1 norm at most 2^(rf); sum of local ranks is 5894.'",
             "'tensor_native_growth_bound':f'Each rank-r Gaussian has row l1 norm at most 2^(rf); sum of local ranks is {sum(r*n for r,n in local[\"paid\"].items())}.'")):
        need(source_price.count(before) == 1, 'Unique pricing declaration: ' + before)
        source_price = source_price.replace(before, after)
    need(source_price == (HERE/'pricing.py').read_text(), 'Only declared pricing constants change')
    print('PASS source pins, exact reconstruction and changed invoice', flush=True)
    with closure() as root:
        L = load(root/'research/p104-productive-controller/local.py', 'local')
        L.ROOT = root
        parent_local = L.replay(base)
        local = L.replay(word)
        need(parent_local['helpers'] == local['helpers'], 'Same helper census')
        need(parent_local['real_scalar_allowance'] == local['real_scalar_allowance'], 'Same scalar allowance')
        rejected = controls(L, base, word)
        print('PASS both exact arbitrary-input endpoints', flush=True)
        reverse = L.reverse_columns(word)
        print('PASS exact transpose', flush=True)
        native = L.native(word)
        print('PASS exact signed native maps', native['distinct_maps'], flush=True)
        C = load(root/'research/p104-productive-controller/caller.py', 'event_contact_caller')
        caller = C.construct()
        need(caller == read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')
        physical = C.physical(caller, word)
        print('PASS full physical caller', flush=True)
        P = load(HERE/'pricing.py', 'event_contact_pricing')
        result = P.run(local, native, caller, physical)
        print('PASS complete pricing', result['raw_root_interval'], flush=True)
        E = L.load(root/'research/higher-moment-strictification/verify.py', 'contact_margin')
        targets = {int(r): n for r, n in result['targets'].items()}
        paid = {int(r): n for r, n in result['paid'].items()}
        parent_paid = dict(paid)
        for r, n in inv['global_paid_delta'].items():
            parent_paid[r] -= n
        parent_interval = [Q('0.00308181851522'), Q('0.00308181851523')]
        parent_signs = []
        for k in parent_interval:
            t, p = E.moment(targets, 1-k), E.moment(parent_paid, 1-k)
            parent_signs.append((t[0]-p[1], t[1]-p[0]))
        need(parent_signs[0][0] > 0 > parent_signs[1][1], 'Exact predecessor crossing')
        lo, hi = map(Q, result['raw_root_interval'])
        gain = [lo-parent_interval[1], hi-parent_interval[0]]
        need(gain[0] > 0, 'Strict gain over predecessor raw ceiling')
        fixed_ceiling = ceiling(E, targets, paid)
    receipt = P.encode({'status': 'PASS_P104_EVENT_CONTACT_KAPPA_00308189',
                        'inventory': inv, 'local': local, 'transpose': reverse,
                        'native': native, 'physical': physical, 'controls': rejected,
                        'parent_raw_interval': parent_interval, 'raw_gain_interval': gain,
                        'fixed_invoice_ceiling': fixed_ceiling,
                        'result': result})
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        need(receipt == read(HERE/'RESULT.json'), 'Exact complete committed receipt')
    print('PASS_P104_EVENT_CONTACT_KAPPA_00308189', flush=True)


if __name__ == '__main__':
    main()
