#!/usr/bin/env python3
"""Exact finite calibration of the proof and constructive source codec.

Apache-2.0; substantial OpenAI Codex assistance. No full physical caller.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random

from frontier import Geometry, ROOT, load, need
from history import budget


def source_facts(geo):
    m = geo.m
    gram = [[sum(row[i]*row[j] for row in m) for j in range(8)] for i in range(8)]
    need(gram == [[56*int(i == j) for j in range(8)] for i in range(8)], 'full source Gram')
    need(all(sum(v != 0 for v in row) == 4 for row in m), 'source row support')
    code = {0}
    for row in geo.binary:
        code |= {x ^ row for x in list(code)}
    need(code == set(geo.dual) and len(code) == 16, 'source self-dual binary code')
    need(Counter(v.bit_count() for v in code) == {0: 1, 4: 14, 8: 1}, 'weight enumerator')
    need(all((a & b).bit_count() % 2 == 0 for a in code for b in code), 'complete self-orthogonality')
    for j, (i, ca, k, cb) in enumerate(geo.pairs):
        need([ca*a+cb*b for a, b in zip(m[i], m[k])] == [2*int(j == h) for h in range(8)],
             'integer two-unit row combination')
    congruences = 0
    rng = random.Random(20261024)
    for g in range(1, 8):
        step = 1 << (g-1)
        vectors = [[step*((mask >> j) & 1) for j in range(8)] for mask in range(256)]
        vectors += [[rng.randrange(-65, 66) for _ in range(8)] for _ in range(32)]
        for q in vectors:
            direct = all(v % (1 << g) == 0 for v in geo.mul(q))
            predicted = all(v % step == 0 for v in q) and sum(((q[j]//step) & 1) << j for j in range(8)) in code
            need(direct == predicted, 'dyadic source lattice classification')
            congruences += 1
    cosets = 0
    for a, b in ((7, 6), (4, 3), (2, 2), (1, 1), (1, 0)):
        counts = [sum(a**(8-(v ^ z).bit_count())*b**(v ^ z).bit_count() for v in code) for z in range(256)]
        need(max(counts) == counts[0], 'coset enumerator upper bound')
        cosets += len(counts)
    return {'gram_entries': 64, 'binary_codewords': sorted(code),
            'weight_enumerator': {'0': 1, '4': 14, '8': 1},
            'two_unit_witnesses': [list(x) for x in geo.pairs],
            'dyadic_congruence_cases': congruences, 'coset_enumerator_cases': cosets}


def scalar_candidates(geo):
    cases = 0
    # Independent Fraction nearest rounding, including both exact tie signs.
    def independent(t):
        value = Fraction(t, 52)
        whole = abs(value.numerator)//value.denominator
        fraction = abs(value)-whole
        answer = whole+int(fraction >= Fraction(1, 2))
        return answer if value >= 0 else -answer
    for s in range(-160, 161):
        candidates = [q for q in range(-100, 101) if independent(s+56*q) == q]
        low = -((26+s)//4)
        high = (26-s)//4
        # Recover the mode list through a separately evaluated interval rule.
        interval = [q for q in range(low, high+1) if independent(s+56*q) == q]
        need(candidates == interval and len(interval) <= 13, 'complete scalar fiber interval')
        if interval:
            need(interval == list(range(min(interval), max(interval)+1)), 'contiguous scalar fiber')
        cases += 1
    return cases


def frontier_suite(geo):
    rng = random.Random(53)
    expected = [815730721, 51008161, 362401, 4096, 16, 1]
    h_bound = [24, 12, 6, 16, 14, 0]
    rows, inverse_cases = [], 0
    for g, maximum in enumerate(expected):
        a = 2 if g == 3 else 4 if g == 4 else 0
        y = [-v for v in geo.mul([a]*8)]
        count = sum(n for _, n in geo.blocks(y, g))
        need(count == maximum == geo.maximum(g), 'attaining worst-case fiber')
        tags = set(range(count)) if count <= 16 else {0, count-1, count//2} | {rng.randrange(count) for _ in range(17)}
        seen = set()
        for tag in sorted(tags):
            x = geo.recover(y, g, tag)
            packet = geo.encode(x, g)
            need(packet['tag'] == tag and packet['y'] == y and geo.decode(packet) == x,
                 'rank/unrank attaining fiber')
            need(max(map(abs, x)) <= h_bound[g], 'explicit finite input range')
            seen.add(tuple(x)); inverse_cases += 1
        need(len(seen) == len(tags), 'distinct preimages')
        rows.append({'relative_guard': g, 'maximum_fiber': maximum,
                     'packed_bits': (maximum-1).bit_length(), 'attaining_input_bound': h_bound[g],
                     'sampled_tags': len(tags), 'fractional_slots_plus_tag':112*g+(maximum-1).bit_length()})
    random_cases = 0
    for g in range(9):
        for magnitude in (0, 1, 26, 10**6):
            x = [rng.randrange(-magnitude, magnitude+1) for _ in range(112)]
            packet = geo.encode(x, g)
            need(geo.decode(packet) == x, 'arbitrary-input exact codec')
            need(packet['fiber_states'] <= geo.maximum(g), 'per-output fiber cap')
            if g >= 5:
                need(packet['tag'] == 0 and packet['fiber_states'] == 1, 'relative-five-bit injectivity')
            random_cases += 1
    return {'frontier': rows, 'attaining_fiber_roundtrips': inverse_cases,
            'other_input_roundtrips': random_cases}


def source_kernel(geo):
    sources = load(ROOT/'SOURCES.json')
    kernel_path = ROOT/'source/kernel.py'
    need(hashlib.sha256(kernel_path.read_bytes()).hexdigest() == sources['vendored_kernel_sha256'],
         'unchanged finite-kernel bytes')
    spec = importlib.util.spec_from_file_location('pinned_inverse_kernel', kernel_path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    rng = random.Random(13)
    cases = 0
    for g in range(6):
        fixtures = [[0]*112, [26 if i == 0 else 0 for i in range(112)],
                    [-26 if i == 0 else 0 for i in range(112)],
                    [rng.randrange(-40, 41) for _ in range(112)]]
        for x in fixtures:
            scaled = [(1 << g)*a for a in x]
            bound = max(map(abs, scaled))
            width = module.word_width(bound)
            words = [module.encode(a, width) for a in scaled]
            scratch = [module.encode(1 if i % 2 else -1, width) for i in range(9)]
            module.recode(words, list(map(list, zip(*geo.m))), bound, scratch)
            output = [module.decode(w) for w in words]
            want, _ = geo.forward(x, g)
            need(output == want and all(not any(w) for w in scratch), 'literal source kernel and owned return')
            # Compare to exact linear A^-1, not a falsely linear rounded map.
            t = geo.transpose(scaled)
            exact = [Fraction(a)-sum(Fraction(c*b, 52) for c, b in zip(row, t))
                     for a, row in zip(scaled, geo.m)]
            need(max(abs(Fraction(a)-b) for a, b in zip(output, exact)) <= 2, 'source error in output-grid units')
            cases += 1
    return cases


def histories(geo):
    rng = random.Random(197)
    stationary = []
    for rounds in range(1, 7):
        radius = (13**rounds-1)//2
        for _ in range(8):
            modes = [rng.randrange(-radius, radius+1) for _ in range(8)]
            x = geo.mul(modes)
            z = x
            for _ in range(rounds):
                z, _ = geo.forward(z, 0)
            need(not any(z) and max(map(abs, x)) <= 2*(13**rounds-1), 'stationary growing zero fiber')
        x = geo.mul([radius]*8)
        z = x
        for _ in range(rounds-1):z, _ = geo.forward(z, 0)
        need(any(z), 'history depth discriminator')
        b = budget(rounds)
        need(b['minimum_history_states'] == 13**(8*rounds), 'sharp history alphabet')
        stationary.append({'rounds': rounds, 'zero_fiber_states':13**(8*rounds),
                           'sufficient_input_bound':2*(13**rounds-1),
                           'packed_bits':b['minimum_packed_bits']})
    # Source-sized changing signed-permutation frames: retain only each tag,
    # reconstructing each earlier output from the final state while reversing.
    framed = 0
    for rounds in (2, 4, 6):
        original = [rng.randrange(-1000, 1001) for _ in range(112)]
        z = list(original); log = []
        for _ in range(rounds):
            permutation = list(range(112)); rng.shuffle(permutation)
            signs = [rng.choice((-1, 1)) for _ in range(112)]
            u = [s*z[j] for s, j in zip(signs, permutation)]
            packet = geo.encode(u, 0)
            out = [0]*112
            for i, j in enumerate(permutation):out[j]=signs[i]*packet['y'][i]
            z = out; log.append((permutation, signs, packet['tag']))
        for permutation, signs, tag in reversed(log):
            out = [s*z[j] for s, j in zip(signs, permutation)]
            u = geo.recover(out, 0, tag)
            z = [0]*112
            for i, j in enumerate(permutation):z[j]=signs[i]*u[i]
        need(z == original, 'changing-frame reverse recovery')
        framed += 1
    for t in range(1, 9):
        for g in range(3):
            for side in (1, 3, 13**4):
                got = budget(t, 1, g, side)
                num, den = 13**(8*t), (1 << (112*g))*side
                need(got['minimum_history_states'] == (num+den-1)//den, 'precision/side-state conservation arithmetic')
    return {'stationary':stationary,'changing_frame_roundtrips':framed,
            'budget_cases':72,'eighteen_same_grid_rounds':budget(18)}


def noncommuting_volume_controls():
    def nearest(v, b):
        return (1 if v >= 0 else -1)*((2*abs(v)+b)//(2*b))
    def step(z, frame):
        a, b = z
        if frame == 0:a += b
        else:b += a
        a, b = a-3*nearest(a, 2), b-5*nearest(b, 4)
        if frame == 0:a -= b
        else:b -= a
        return a, b
    results = []
    for bound, frames in ((64, (0, 1)), (128, (0, 1)), (256, (0, 1, 0))):
        counts = Counter()
        for a in range(-bound, bound+1):
            for b in range(-bound, bound+1):
                z = a, b
                for frame in frames:z = step(z, frame)
                counts[z] += 1
        maximum = max(counts.values())
        expected = 60 if bound == 64 else 8**len(frames)
        need(maximum == expected, 'finite-window noncommuting volume control')
        results.append({'input_bound':bound,'frames':list(frames),'inputs':(2*bound+1)**2,
                        'maximum_fiber_in_window':maximum,'unbounded_maximum':8**len(frames)})
    return results


def rejections(geo):
    good = geo.encode([13 if i == 0 else 0 for i in range(112)], 1)
    cases = []
    def reject(name, packet):
        try:geo.decode(packet)
        except (ValueError, TypeError):cases.append(name)
        else:raise ValueError('invalid packet accepted: '+name)
    for name, key, value in (('wrong-source','source_sha256','0'*64),
                             ('wrong-fiber','fiber_states',-1),
                             ('wrong-bound','worst_case_states',1),
                             ('wrong-bits','tag_bits',0),
                             ('negative-tag','tag',-1),
                             ('out-of-fiber-tag','tag',good['fiber_states']),
                             ('boolean-guard','g',True)):
        packet=deepcopy(good);packet[key]=value;reject(name,packet)
    packet=deepcopy(good);packet['y'][0]=0.5;reject('float-output',packet)
    packet=deepcopy(good);packet['y'].pop();reject('missing-owner',packet)
    # Changing precision on an existing same-grid packet is not refinement.
    packet=geo.encode([13 if i==0 else 0 for i in range(112)],0);packet['g']=5
    reject('absolute-guard-is-not-relative-refinement',packet)
    return cases


def authenticate_source(root):
    sources=load(ROOT/'SOURCES.json')
    for row in sources['files']:
        need(hashlib.sha256((Path(root)/row['path']).read_bytes()).hexdigest()==row['sha256'],
             'canonical source hash: '+row['path'])
    normal=load(Path(root)/'research/coded-native-caller/NORMALIZERS.json')
    need(normal['mode_columns']==load(ROOT/'FIXTURE.json')['mode_columns'], 'literal source columns')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root')
    parser.add_argument('--suite',choices=('all','core'),default='all')
    args=parser.parse_args();geo=Geometry()
    result={'status':'PASS_PRECISION_STATE_FRONTIER','source_facts':source_facts(geo),
            'scalar_intervals':scalar_candidates(geo),'recovery':frontier_suite(geo),
            'rejections':rejections(geo)}
    if args.suite=='all':
        result['unchanged_kernel_calls']=source_kernel(geo)
        result['histories']=histories(geo)
        result['noncommuting_volume_controls']=noncommuting_volume_controls()
    if args.source_root:authenticate_source(args.source_root)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
