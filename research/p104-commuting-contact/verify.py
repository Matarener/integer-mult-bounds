"""Verify the P104 commuting-write contact cascade on the PR5580 word.

Pierre-Loic Doulcet (hexapode). Apache-2.0.
Retained source notices and predecessor contributors are listed in SOURCES.json.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import closure, load, need, read
from construct import construct, construct_fixed_endpoints


def inventory(base, word_fixed, word):
    for key in base:
        if key != 'program':
            need(word_fixed[key] == base[key], 'Unchanged fixed-endpoint word field: ' + key)
        if key not in ('program', 'initial'):
            need(word[key] == base[key], 'Unchanged headline word field: ' + key)
    need(
        [i for i, (a, b) in enumerate(zip(base['initial'], word['initial'])) if a != b] == [531],
        'Only helper 531 initial frame changes in headline word (597 -> 3)'
    )
    need(base['initial'][531] == 597 and word['initial'][531] == 3, 'Exact helper 531 initial frame change')

    def bill(w):
        return Counter(
            abs(len(w['frames'][e[2]]) - len(w['frames'][e[3]]))
            for e in w['program'] if e[0] == 'MOVE'
        )

    before = bill(base)
    after_fixed = bill(word_fixed)
    after = bill(word)
    delta_fixed = {
        r: after_fixed[r] - before[r]
        for r in before.keys() | after_fixed.keys()
        if after_fixed[r] != before[r]
    }
    delta = {
        r: after[r] - before[r]
        for r in before.keys() | after.keys()
        if after[r] != before[r]
    }
    need(delta_fixed == {1: -4, 4: -4, 5: 4}, 'Exact Stage A fixed-endpoint local paid delta')
    need(delta == {1: -8, 3: -1, 4: -2, 5: 4}, 'Exact Stage A+B headline local paid delta')
    return {
        'source_events': len(base['program']),
        'fixed_endpoint_events': len(word_fixed['program']),
        'events': len(word['program']),
        'fixed_endpoint_local_paid_delta': delta_fixed,
        'fixed_endpoint_global_paid_delta': {r: 18 * n for r, n in delta_fixed.items()},
        'local_paid_delta': delta,
        'global_paid_delta': {r: 18 * n for r, n in delta.items()},
        'local_target_delta': {8: -1, 9: 1},
        'global_target_delta': {8: -18, 9: 18},
        'all_main_endpoints_fixed': True,
        'owned_lifetimes_fixed': True,
    }


def controls(L, base, word):
    variants = {}
    bad = deepcopy(word)
    bad['program'].remove(['MOVE', 197, 3, 355, False])
    variants['missing_source_transport'] = bad

    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD', 198, 648, '1/2', 3])
    event[-1] = 597
    variants['mismatched_commuted_frame'] = bad

    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['ADD', 198, 648, '1/2', 3])
    event[-2] = '1'
    variants['wrong_scalar_coefficient'] = bad

    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e == ['MOVE', 648, 3, 120, False])
    event[3] = 597
    variants['non_nested_return'] = bad

    rejected = {}
    for name, bad_word in variants.items():
        try:
            L.replay(bad_word)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('Accepted invalid word: ' + name)
    try:
        inventory(base, base, base)
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
        power = (E.power(rank, 1 - cap)[0], Q(rank))
        term = E.scale(E.mul(power, E.log_bounds(rank)), coefficient)
        lower += term[0]
        upper += term[1]
    need(upper < 0, 'Strictly decreasing complete moment on the retained BIT band')
    return {
        'kappa_interval': [Q(0), cap],
        'moment_derivative': [lower, upper],
        'scope': 'This fixed paid and target invoice; the inherited BIT cap is retained.',
    }


def main():
    sources = read(HERE / 'SOURCES.json')
    for pin in sources['external_inputs']:
        raw = (HERE / pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source bytes: ' + pin['local_path'])
        header = ('blob ' + str(len(raw)) + '\0').encode()
        need(sha1(header + raw).hexdigest() == pin['git_blob'], 'Source Git object: ' + pin['local_path'])
    base = read(HERE / 'inputs/pr5580-WORD.json.gz')
    word_fixed = read(HERE / 'WORD-FIXED-ENDPOINTS.json.gz')
    word = read(HERE / 'WORD.json.gz')
    need(construct_fixed_endpoints(base) == word_fixed, 'Regenerated Stage A fixed-endpoint word payload')
    need(construct(base) == word, 'Regenerated full Stage A+B cascade word payload')
    inv = inventory(base, word_fixed, word)

    source_price = (HERE / 'inputs/pr5580-pricing.py').read_text()
    for before, after in (
        ("KAPPA, TESTED = Q('.00308189'), Q('.0030818905')",
         "KAPPA, TESTED = Q('.00308520'), Q('.0030852005')"),
        ("PREVIOUS = Q('.00308181')", "PREVIOUS = Q('.00308189')"),
        ("'kappa_decimal':'.00308189'", "'kappa_decimal':'.00308520'"),
        ("'previous_open_pr5569':PREVIOUS", "'previous_open_pr5580':PREVIOUS"),
        ("sum(paid.values()) == 66852", "sum(paid.values()) == 66726"),
    ):
        need(source_price.count(before) == 1, 'Unique pricing declaration: ' + before)
        source_price = source_price.replace(before, after)
    need(source_price == (HERE / 'pricing.py').read_text(), 'Only declared pricing constants change')
    print('PASS source pins, exact reconstruction and changed invoice', flush=True)

    with closure() as root:
        L = load(root / 'research/p104-productive-controller/local.py', 'local')
        L.ROOT = root
        parent_local = L.replay(base)
        fixed_local = L.replay(word_fixed)
        local = L.replay(word)
        need(parent_local['helpers'] == fixed_local['helpers'], 'Same helper census on Stage A fixed-endpoint word')
        need(local['helpers'] == {9: 425, 4: 83, 5: 5, 8: 14}, 'Exact Stage A+B helper census')
        need(parent_local['real_scalar_allowance'] == fixed_local['real_scalar_allowance'] == local['real_scalar_allowance'], 'Same scalar allowance')
        rejected = controls(L, base, word)
        print('PASS exact arbitrary-input endpoints (base, Stage A fixed-endpoint, Stage A+B headline)', flush=True)
        reverse = L.reverse_columns(word)
        print('PASS exact transpose', flush=True)
        native = L.native(word)
        print('PASS exact signed native maps', native['distinct_maps'], flush=True)
        C = load(root / 'research/p104-productive-controller/caller.py', 'commuting_contact_caller')
        caller = C.construct()
        need(caller == read(root / 'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')
        physical = C.physical(caller, word)
        print('PASS full physical caller', flush=True)
        P = load(HERE / 'pricing.py', 'commuting_contact_pricing')
        result = P.run(local, native, caller, physical)
        print('PASS complete pricing', result['raw_root_interval'], flush=True)

        E = L.load(root / 'research/higher-moment-strictification/verify.py', 'commuting_contact_margin')
        targets = {int(r): n for r, n in result['targets'].items()}
        paid = {int(r): n for r, n in result['paid'].items()}
        parent_targets = dict(targets)
        for r, n in inv['global_target_delta'].items():
            parent_targets[r] -= n
        parent_paid = dict(paid)
        for r, n in inv['global_paid_delta'].items():
            parent_paid[r] -= n
        fixed_paid = dict(parent_paid)
        for r, n in inv['fixed_endpoint_global_paid_delta'].items():
            fixed_paid[r] += n

        parent_interval = [Q('0.00308189496866'), Q('0.00308189496867')]
        parent_signs = []
        for k in parent_interval:
            t, p = E.moment(parent_targets, 1 - k), E.moment(parent_paid, 1 - k)
            parent_signs.append((t[0] - p[1], t[1] - p[0]))
        need(parent_signs[0][0] > 0 > parent_signs[1][1], 'Exact PR5580 predecessor crossing')

        fixed_interval = [Q('0.00308415555080'), Q('0.00308415555081')]
        fixed_signs = []
        for k in fixed_interval:
            t, p = E.moment(parent_targets, 1 - k), E.moment(fixed_paid, 1 - k)
            fixed_signs.append((t[0] - p[1], t[1] - p[0]))
        need(fixed_signs[0][0] > 0 > fixed_signs[1][1], 'Exact Stage A fixed-endpoint crossing')

        lo, hi = map(Q, result['raw_root_interval'])
        gain = [lo - parent_interval[1], hi - parent_interval[0]]
        need(gain[0] > 0, 'Strict gain over PR5580 raw ceiling')
        fixed_ceiling = ceiling(E, targets, paid)

    receipt = P.encode({
        'status': 'PASS_P104_COMMUTING_CONTACT_KAPPA_00308520',
        'inventory': inv,
        'local': local,
        'fixed_endpoint_local': fixed_local,
        'transpose': reverse,
        'native': native,
        'physical': physical,
        'controls': rejected,
        'parent_raw_interval': parent_interval,
        'fixed_endpoint_raw_interval': fixed_interval,
        'raw_gain_interval': gain,
        'fixed_invoice_ceiling': fixed_ceiling,
        'result': result,
    })
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    else:
        need(receipt == read(HERE / 'RESULT.json'), 'Exact complete committed receipt')
    print('PASS_P104_COMMUTING_CONTACT_KAPPA_00308520', flush=True)


if __name__ == '__main__':
    main()
