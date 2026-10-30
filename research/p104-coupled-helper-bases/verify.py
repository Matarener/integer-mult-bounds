"""Check the coupled helper word and its complete conditional price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The fixed-invoice derivative check follows the credited PR5580 checker.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import difflib
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import closure, load, need, read
import local as L
from construct import construct


def inventory(base, word, old, new):
    need(base['frames'] == word['frames'] and base['ports'] == word['ports'] and
         base['live'] == word['live'], 'Same native charts and 104 literal ports')
    main = set(base['live']) | {h+112 for h in base['live']}
    for h in main:
        need((base['initial'][h], base['final'][h]) ==
             (word['initial'][h], word['final'][h]), 'Same main boundary contract')
    need((base['public'], word['public']) == (735, 744), 'Nine additional independent inputs')
    need(new['paid'] == {1: 2209, 2: 459, 3: 494, 4: 93, 5: 160, 6: 18, 7: 14},
         'Exact new paid profile')
    need(new['helpers'] == {1: 2, 2: 5, 4: 90, 5: 7, 7: 5, 8: 18, 9: 409},
         'Exact new target profile')
    def owned(w):
        return [[e[0], e[1]-w['public'], *e[2:]] for e in w['program']
                if e[1] >= w['public'] and e[0] in ('INIT', 'CLEAR', 'MOVE')]
    need(owned(base) == owned(word), 'Same eight owned lifetimes and paid paths')
    need(sum(e[0] == 'COPY' for e in word['program']) == 8, 'Eight owned copies')
    def delta(key):
        return {r: new[key].get(r, 0)-old[key].get(r, 0)
                for r in sorted(new[key].keys() | old[key].keys())
                if new[key].get(r, 0) != old[key].get(r, 0)}
    need(sum(new['paid'].values()) == sum(old['paid'].values())-7, 'Seven fewer local transports')
    need(sum(r*n for r, n in delta('paid').items()) == -26 and
         sum(r*n for r, n in delta('helpers').items()) == -26, 'Both rank masses fall by 26')
    return {'source_events': len(base['program']), 'events': len(word['program']),
            'local_paid_delta': delta('paid'), 'local_target_delta': delta('helpers'),
            'all_main_boundaries_fixed': True, 'owned_paid_paths_fixed': True,
            'owned_paid_rank_mass': sum(abs(len(word['frames'][e[2]])-len(word['frames'][e[3]]))
                                       for e in word['program'] if e[0] == 'MOVE' and e[4])}


def controls(base, witness, word):
    variants = {}
    bad = deepcopy(word)
    bad['program'].pop(next(i for i, e in enumerate(bad['program']) if e[0] == 'ADD'))
    variants['missing_input_basis_operation'] = bad
    bad = deepcopy(word)
    event = next(e for e in bad['program'] if e[0] == 'ADD' and 735 in e[1:3])
    event[-2] = str(2*Q(event[-2]))
    variants['wrong_new_helper_coefficient'] = bad
    bad = deepcopy(word)
    bad['final'][61] = base['final'][61]
    variants['old_retired_helper_exit'] = bad
    bad = deepcopy(word)
    bad['program'].insert(0, ['INIT', 735, bad['initial'][735]])
    variants['fresh_input_treated_as_owned_zero'] = bad
    rejected = {}
    for name, bad in variants.items():
        try:
            L.replay(bad)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('Invalid word accepted: '+name)
    bad = deepcopy(witness)
    bad['steps'][6]['source_functional'][0][1] = '3'
    try:
        construct(base, bad)
    except ValueError as error:
        rejected['false_cut_witness'] = str(error)
    else:
        raise ValueError('False cut witness accepted')
    return rejected


def complete_profiles(local):
    targets = Counter({r: 18*n for r, n in local['helpers'].items()})
    paid = Counter({r: 18*n for r, n in local['paid'].items()})
    targets[145] += 208
    paid[1] += 1560
    for length in (7, 8):
        for j in range(1, length+1):
            targets[8*(j+1)+1] += 208
            paid[8*(j+1)] += 208
    return targets, paid


def ceiling(E, targets, paid):
    cap, lower, upper = Q('.0034'), Q(0), Q(0)
    for rank in targets.keys() | paid.keys():
        coefficient = paid.get(rank, 0)-targets.get(rank, 0)
        power = (E.power(rank, 1-cap)[0], Q(rank))
        term = E.scale(E.mul(power, E.log_bounds(rank)), coefficient)
        lower += term[0]
        upper += term[1]
    need(upper < 0, 'Strictly decreasing complete moment on the retained BIT band')
    return {'kappa_interval': [Q(0), cap], 'moment_derivative': [lower, upper],
            'scope': 'This fixed paid and target invoice under the retained BIT cap.'}


def main():
    for pin in read(HERE/'SOURCES.json')['external_inputs']:
        raw = (HERE/pin['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'Source bytes: '+pin['local_path'])
        need(sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest() == pin['git_blob'],
             'Source Git object: '+pin['local_path'])
    base, witness, word = (read(HERE/p) for p in
                           ('inputs/pr5580-WORD.json.gz', 'WITNESS.json', 'WORD.json.gz'))
    regenerated, steps = construct(base, witness)
    need(regenerated == word, 'Deterministic complete word reconstruction')
    print('PASS source pins and all fifteen exact construction steps', flush=True)
    with closure() as root:
        L.ROOT = root
        old_path = root/'research/p104-productive-controller/local.py'
        old_checker = load(old_path, 'p104_legacy_local')
        old = old_checker.replay(base)
        need(L.replay(base) == old, 'Generalized checker agrees with source checker')
        for source, target, label in ((old_path, HERE/'local.py', 'VERIFIER'),
                                      (HERE/'inputs/pr5580-pricing.py', HERE/'pricing.py', 'PRICING')):
            names = ('PR5545/local.py', 'local.py') if label == 'VERIFIER' else ('PR5580/pricing.py', 'pricing.py')
            diff = ''.join(difflib.unified_diff(source.read_text().splitlines(True),
                                               target.read_text().splitlines(True),
                                               fromfile=names[0], tofile=names[1]))
            need(diff == (HERE/(label+'-CHANGES.diff')).read_text(), 'Exact '+label+' review diff')
        need((HERE/'caller.py').read_bytes() == (root/'research/p104-productive-controller/caller.py').read_bytes(),
             'Unchanged source caller')
        local = L.replay(word)
        inv, rejected = inventory(base, word, old, local), controls(base, witness, word)
        reverse = L.reverse_columns(word)
        print('PASS arbitrary-input endpoints, ownership, controls and dense transpose', flush=True)
        native = L.native(word)
        print('PASS exact signed native maps', native['distinct_maps'], flush=True)
        C = load(HERE/'caller.py', 'coupled_helper_caller')
        caller = C.construct()
        need(caller == read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')
        physical = C.physical(caller, word)
        rejected.update(C.controls(caller))
        print('PASS complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'coupled_helper_pricing')
        result = P.run(local, native, caller, physical)
        print('PASS complete price, compiler and outer transfer', result['raw_root_interval'], flush=True)
        E = load(root/'research/higher-moment-strictification/verify.py', 'coupled_helper_margin')
        targets, paid = complete_profiles(local)
        need(P.encode(targets) == result['targets'] and P.encode(paid) == result['paid'], 'Third complete invoice')
        old_t, old_p = complete_profiles(old)
        parent_interval = [Q('.00308189496866'), Q('.00308189496867')]
        def margin(t, p, k):
            a, b = E.moment(t, 1-k), E.moment(p, 1-k)
            return a[0]-b[1], a[1]-b[0]
        need(margin(old_t, old_p, parent_interval[0])[0] > 0 >
             margin(old_t, old_p, parent_interval[1])[1], 'Exact PR5580 crossing')
        need(margin(old_t, old_p, P.KAPPA)[1] < 0, 'Old complete invoice rejects the new claim')
        old_power = E.scale(E.power(145, -1024*P.TESTED), 1-P.TESTED)
        need(old_power[1] < Q(63, 64)**1000, 'Old logarithm power is insufficient')
        rejected['old_invoice_at_new_kappa'] = 'Strict negative complete moment'
        rejected['old_logarithm_power_1000'] = 'Insufficient complement capacity'
        lo, hi = map(Q, result['raw_root_interval'])
        gain = [lo-parent_interval[1], hi-parent_interval[0]]
        need(gain[0] > 0, 'Strict gain over the parent raw ceiling')
        fixed_ceiling = ceiling(E, targets, paid)
        split_word = read(HERE/'inputs/pr5599-WORD.json.gz')
        split_local = L.replay(split_word)
        split_t, split_p = complete_profiles(split_local)
        split_interval = [Q('.00309839352211'), Q('.00309839352212')]
        need(margin(split_t, split_p, split_interval[0])[0] > 0 >
             margin(split_t, split_p, split_interval[1])[1], 'Exact PR5599 crossing')
        difference = {r: targets.get(r, 0)-paid.get(r, 0)-split_t.get(r, 0)+split_p.get(r, 0)
                      for r in targets.keys() | paid.keys() | split_t.keys() | split_p.keys()}
        need({r: c for r, c in difference.items() if c} == {4: 18, 5: 18, 9: -18},
             'Strict gain of eighteen g(4,5) over the released split component')
        need(sum(split_p.values())-sum(paid.values()) == 126 and
             sum(split_t.values())-sum(targets.values()) == 108,
             'Fewer paid calls and productive fields than PR5599')
        parallel = {'pr': 5599, 'source_commit': '0644592d421b375c221045954fdf13932575ffa8',
                    'claim': Q('.00309839'), 'claim_gain': P.KAPPA-Q('.00309839'),
                    'raw_interval': split_interval,
                    'raw_gain_interval': [lo-split_interval[1], hi-split_interval[0]],
                    'paid_calls': sum(split_p.values()), 'productive_fields': sum(split_t.values()),
                    'signed_moment_delta': {4: 18, 5: 18, 9: -18},
                    'scope': 'Pinned parallel word; exact scalar endpoint and full invoice comparison. Its native and compiler checks are not repeated.'}
    receipt = P.encode({'status': 'PASS_P104_COUPLED_HELPER_KAPPA_00309980',
                        'construction': steps, 'inventory': inv, 'local': local,
                        'transpose': reverse, 'native': native, 'physical': physical,
                        'controls': rejected, 'parent_raw_interval': parent_interval,
                        'raw_gain_interval': gain, 'fixed_invoice_ceiling': fixed_ceiling,
                        'parallel_comparison': parallel,
                        'result': result})
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        need(receipt == read(HERE/'RESULT.json'), 'Exact complete committed receipt')
    print('PASS_P104_COUPLED_HELPER_KAPPA_00309980', flush=True)


if __name__ == '__main__':
    main()
