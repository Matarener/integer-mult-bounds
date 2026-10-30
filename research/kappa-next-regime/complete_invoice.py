#!/usr/bin/env python3
"""Whole T35 finite invoice, with retained and conservative coefficient bounds.

Uses the actual two local IR words and absolute-owner profile. Both rank-price
engines and the inherited bad-class surcharge are retained. A fully sequential
coefficient envelope also pays for every replica's local call and bridge, so
the result does not rely on carrying a replica-local norm bound across pooling.
Apache-2.0. Substantial OpenAI assistance; PR3647/463/510 invoice credit retained.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE / 'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
POOL = HERE / 'geometry-search/pool35'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load_engine(name):
    path = BASE / 'vendor/engines' / (name + '.py')
    spec = importlib.util.spec_from_file_location('pool35_'+name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_details(template, word):
    out = {}
    scalar_adds = sum(len(terms) for phase in ('A','B','C','D') for _,_,terms in word[phase]) + sum(map(len,word['scatter']))
    for orientation, events in template['local_programs'].items():
        values = [1 << i for i in range(659)] + [0]
        norms = [1]*659 + [0]
        opened, largest, adds, copies = None, 1, 0, 0
        profile = Counter()
        for event in events:
            op, d = event[:2]
            if op == 0:
                if event[4]:
                    profile[event[4]] += 1
            elif op == 1:
                source, coefficient = event[2:4]
                need(d != opened and (source != 659 or opened is not None), 'immutable open COPY source')
                if coefficient & 1:
                    values[d] ^= values[source]
                norms[d] += abs(coefficient)*norms[source]
                largest = max(largest, norms[d])
                adds += 1
            elif op == 2:
                need(opened is None and values[659] == 0 and event[2] == 659, 'fresh private COPY')
                opened = d
                values[659], norms[659] = values[d], norms[d]
                copies += 1
                profile[event[5]] += 1
            else:
                need(op == 3 and opened == d and values[659] == values[d], 'literal private erasure')
                values[659], norms[659], opened = 0, 0, None
        want = [(1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(659)]
        need(values == want+[0] and opened is None, 'all659 arbitrary dirty input columns and cleanup')
        need(copies == 9 and adds == scalar_adds, 'complete source-bound R437 scalar inventory')
        need(len(events) == adds+sum(profile.values())+copies,
             'all ADD, MOVE, COPY and ERASE records counted')
        out[orientation] = {'adds':adds, 'copies':copies, 'prefix_l1':largest,
                            'profile':dict(sorted(profile.items())), 'events':len(events)}
    need(out['forward']['profile'] == out['reverse']['profile'], 'equal paid profiles in both orientations')
    return out


def run(pool, word_path, block_review):
    template = read(pool/'GLOBAL-TEMPLATE.json.gz')
    result = read(pool/'RESULT.json')
    word = read(word_path)
    expected = read(BASE/'EXPECTED.json')
    baseline = read(BASE/'generated/GLOBAL-TEMPLATE.json.gz')
    need(template['schedule'] == baseline['schedule'], 'literal predecessor global controller')
    details = local_details(template,word)
    profile = {int(k):v for k,v in result['profile'].items()}
    recomputed_profile = Counter()
    for call in template['calls']:
        recomputed_profile.update(details[call['orientation']]['profile'])
    idles = read(pool/'IDLE-INVENTORY.json.gz')
    recomputed_profile.update(row[-1] for row in idles)
    need(recomputed_profile == profile, 'actual local programs plus every absolute idle child')
    T, W, R, V, L, m, depth = 35, 31080, 437, 111, 9, 64, 2
    physical, E, d, N = W+9, sum(profile.values()), m*m, 2*m
    need((template['replicas'],template['live'],template['private_centre_reserve']) == (T,W,9),
         'all productive and private physical fields')
    need(E == 988155 and m*W-sum(r*n for r,n in profile.items()) == 11235,
         'complete priced rank mass and raw deficit')
    need(2*max(profile)**depth < m**depth and physical < 2**15, 'halving and family index')
    geometry = read(BASE/'data/GEOMETRY.json')
    local_prefix = 2**18*details['forward']['prefix_l1']**5*details['reverse']['prefix_l1']**4
    # Product of operator-norm bounds of EVERY executed local word/bridge.
    # Coordinate gathering, scattering, and permutations have norm one under
    # the inherited packet contracts. No replica-independence shortcut is used.
    sequential_prefix = local_prefix**T
    block_prefix = local_prefix**5
    block_receipt = read(block_review)
    for name, pin in block_receipt['source_sha256'].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == pin,
             'independent block proof source pin: '+name)
    need(int(block_receipt['coefficient_prefix_bound']) == block_prefix and
         block_receipt['payload_blocks'] == 7 and
         block_receipt['replicas_per_block'] == 5 and
         block_receipt['private_regular_payload_carry'] is False,
         'independent seven-block separation and coefficient bound')
    unit = L*T*details['forward']['adds'] + 18*V*T
    episodes = 9*L*T
    J = 8*T*L*(2*V+R)+8*(8*V*T)+2*L*T*R+2*episodes
    high, good, compiler = 16*(d+1)**2, 8*m*m+8, 128*N**3
    selectors = 2*L*T*((W-1)+R*m*(geometry['max_route_factors']+144+2+(m-1)+m))
    common = {'unit':unit, 'J_times_high':J*high, 'J_times_physical':J*physical,
              'E_times_good':E*good, 'E_times_compiler':E*compiler,
              'matrix_test':16*m**3, 'copy_erase_episodes':episodes,
              'selectors':selectors, 'one':1}
    envelopes = {}
    for label, prefix in [('retained_replica_formula',local_prefix),
                          ('five_replica_block_upper_bound',block_prefix),
                          ('complete_sequential_upper_bound',sequential_prefix)]:
        coefficient = sum(common.values())+prefix
        two = (coefficient+1)**depth*(E+1)**depth
        charged_prefix = 64*((prefix.bit_length()+63)//64)
        charged_two = max(512,64*((two.bit_length()+63)//64))
        need(prefix < 2**charged_prefix and two < 2**charged_two,
             'fully charged coefficient envelopes')
        need(charged_two < 210000, 'conservative coefficient stays within retained semantic umbrella')
        envelopes[label] = {'prefix':str(prefix), 'prefix_bits':prefix.bit_length(),
            'charged_prefix_bits':charged_prefix, 'coefficient':str(coefficient),
            'coefficient_bits':coefficient.bit_length(), 'two_level_coefficient':str(two),
            'two_level_bits':two.bit_length(), 'charged_two_level_bits':charged_two}
    row = depth*(m*m+1)+9909+252
    need(row == 18355 < 20161, 'retained row coefficient cap')
    first, second = load_engine('moment'), load_engine('base_two_moment')
    bracket = first.certify(profile,m,W,True)
    lower, upper = F(bracket['lower']), F(bracket['upper'])
    need((lower,upper) == (F(result['bit_endpoint_lower']),F(result['bit_endpoint_upper'])),
         'recomputed complete moment bracket')
    fallback_per_child = 32*m*m
    exact_fallback = 6*N*(N-1)+3*N+6*(N-1)
    need(exact_fallback == 98682 < fallback_per_child, 'complete inherited fallback bound')
    signs = []
    for label, endpoint in [('lower',lower),('upper',upper)]:
        lo, hi = second.moment(m,W,list(profile.items()),endpoint)
        fl, fh = second.moment(m,W,[(1,fallback_per_child*E)],endpoint)
        lo, hi = lo+fl/10**16, hi+fh/10**16
        need(hi < 1 if label == 'lower' else lo > 1, 'second engine strict full-invoice sign')
        signs.append({'endpoint':str(endpoint),'lower':str(lo),'upper':str(hi)})
    source_paths = [pool/'GLOBAL-TEMPLATE.json.gz',pool/'RESULT.json',pool/'IDLE-INVENTORY.json.gz',
                    word_path,block_review,BASE/'EXPECTED.json',BASE/'vendor/assemble9.py',
                    BASE/'code/invoice_audit.py',BASE/'data/GEOMETRY.json']
    return {'status':'PASS_T35_COMPLETE_FINITE_INVOICE_WITH_CONSERVATIVE_COEFFICIENTS',
        'm':m,'W':W,'physical':physical,'replicas':T,'local':details,'profile':profile,
        'paid_requests':E,'J':J,'components_without_prefix':{k:str(v) for k,v in common.items()},
        'coefficient_envelopes':envelopes,
        'chosen_envelope':'five_replica_block_upper_bound',
        'ROW':row,'ROW_cap':20161,'halving':[2*max(profile)**2,m*m],
        'fallback_exact_bound':exact_fallback,'fallback_charged_per_child':fallback_per_child,
        'fallback_total':fallback_per_child*E,'bad_fraction':'1/10000000000000000',
        'bit_lower':str(lower),'bit_upper':str(upper),'second_engine_signs':signs,
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        'scope':'Complete finite inherited-formula invoice. The chosen coefficient envelope pays for every call and bridge in each independently separated five-replica payload block; the fully sequential envelope is also certified. General physical source/route/preparation and all-size contracts remain inherited hypotheses; this arithmetic does not prove them.'}


if __name__ == '__main__':
    import sys
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser()
    parser.add_argument('--pool',type=Path,default=POOL)
    parser.add_argument('--word',type=Path,default=BASE/'data/r0042/R437-COMPOSED-WORD.json.gz')
    parser.add_argument('--block-review',type=Path,default=HERE/'geometry-search/BLOCK-PREFIX-REVIEW.json')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    need(__debug__, 'assertions must remain enabled')
    result = run(args.pool.resolve(),args.word.resolve(),args.block_review.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result == read(HERE/'COMPLETE-INVOICE.json'),'exact full invoice receipt')
    print(json.dumps({'status':result['status'],'bit_lower':result['bit_lower'],
                      'ROW':result['ROW'], 'coefficient_bits':{
                          k:(v['prefix_bits'],v['two_level_bits']) for k,v in result['coefficient_envelopes'].items()}}))
