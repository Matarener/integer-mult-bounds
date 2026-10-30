#!/usr/bin/env python3
"""Replay the exact paired-stage bounds and the chronology controls.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from itertools import permutations, product
from pathlib import Path
import types
from chronology import add, outer, mul, rank, family, mixed, need

HERE = Path(__file__).resolve().parent


def literal(us, vs, ps, labels, chosen=None):
    n = len(ps[0]); identity = [1 << i for i in range(n)]
    word = {0: identity}
    for u, v, p, label in zip(us, vs, ps, labels):
        factors = [{0: identity, 1: outer(u, v, n)}]
        if chosen is None or chosen == label:
            bit = 1 << (label + 1) if chosen is None else 2
            factors.append({0: identity, bit: p})
        for factor in factors:
            nxt = {}
            for a, x in factor.items():
                for b, y in word.items():
                    if a & b:
                        continue
                    key = a | b
                    nxt[key] = add(nxt.get(key, [0]*n), mul(x, y))
            word = nxt
    return word


def power_interval(r, precision=48):
    value = pow(r, 997) << (precision*1000)
    lo, hi = 0, r << precision
    while lo < hi:
        mid = (lo + hi + 1)//2
        if pow(mid, 1000) <= value:
            lo = mid
        else:
            hi = mid-1
    need(pow(lo, 1000) <= value < pow(lo+1, 1000), 'root enclosure')
    return lo, lo if pow(lo, 1000) == value else lo+1


def interval(poly, powers):
    lo = hi = 0
    for r, c in poly.items():
        a, b = powers[r]
        lo += c*(a if c >= 0 else b)
        hi += c*(b if c >= 0 else a)
    return {'lower_numerator': lo, 'upper_numerator': hi, 'denominator': 1 << 48}


def moment(profile, m, loss):
    poly = {r: 2*m*(profile['helpers'].get(str(r), 0)-profile['paid'].get(str(r), 0)) for r in range(1, 10)}
    poly[17] = 104*(2*m-6+loss)
    poly[25] = 104*(4-loss)
    return {r: c for r, c in poly.items() if c}


def run():
    context = json.loads((HERE/'SOURCE-CONTEXT.json').read_text())
    for source in context:
        need(hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256'], 'source bytes')
    old = types.ModuleType('old_cuts')
    exec(compile((HERE/'inputs/PR5617-cuts.py').read_text(), 'PR5617-cuts.py', 'exec'), old.__dict__)
    profiles = json.loads((HERE/'inputs/PR5617-RESULT.json').read_text())['complete_prices']
    # Enumerate every rank-two projector on four binary coordinates.
    projectors = []
    for rows in product(range(16), repeat=4):
        rows = list(rows)
        if rank(rows) == 2 and mul(rows, rows) == rows:
            projectors.append(rows)
    pairs = 0; counts = {}
    for p in projectors:
        for q in projectors:
            e = add(p, q)
            if mul(e, e) == e:
                r = rank(e); intersection = rank(mul(p, q))
                need(mul(p, q) == mul(q, p) and r == 4-2*intersection, 'pair parity')
                counts[r] = counts.get(r, 0)+1; pairs += 1
    need(len(projectors) == 560 and set(counts) == {0, 2, 4}, 'complete projector census')
    witnesses = []
    for g in [3, 5, 7, 15, 31, 511]:
        candidate, ps, labels = family(g); n = candidate['n']
        for u, v, p in zip(candidate['u'], candidate['v'], ps):
            r = outer(u, v, n)
            need(rank(p) == 2 and mul(p, p) == p and mul(p, r) == mul(r, p) == r, 'full-call compatibility')
        screen = old.audit(candidate)
        need(screen['status'] == 'PASS_NECESSARY_CUTS_ONLY', 'predecessor cuts')
        loss = 4*(g+2)-sum(len(a['outputs']) for a in candidate['axes'])
        need(loss == 8, 'constant loss')
        defects = mixed(candidate, ps, labels)
        need(len(defects) == g-1 and set(defects.values()) == {4}, 'chronology rejection')
        if g <= 7:
            for c in range(g+2):
                word = literal(candidate['u'], candidate['v'], ps, labels, c)
                e = [0]*n
                for p, label in zip(ps, labels):
                    if label == c: e = add(e, p)
                need(rank(add(word.get(3, [0]*n), e)) == defects.get(c, 0), 'independent mixed coefficient')
        witnesses.append({'g': g, 'n': n, 'loss': loss, 'prior_intersection_cuts': len(screen['intersections']), 'mixed_rejections': len(defects)})
    # The first copy has three private stages and two repair queries.
    candidate, ps, labels = family(3)
    indices = [i for i, u in enumerate(candidate['u']) if u < 16]
    orders = 0
    for order in permutations(indices):
        c = {'n': 4, 'u': [candidate['u'][i] for i in order], 'v': [candidate['v'][i] for i in order]}
        p = [ps[i][:4] for i in order]; labs = [labels[i] for i in order]
        need(mixed(c, p, labs), 'all-order obstruction control')
        orders += 1
    # Two complete three-query units give a positive six-query word.
    us = []; vs = []; ps = []; labels = []
    for label, (u, v) in enumerate([(1, 2), (2, 1), (3, 3)]):
        for shift in [0, 2]:
            us.append(u << shift); vs.append(v << shift)
            ps.append([1 << j if shift <= j < shift+2 else 0 for j in range(4)])
            labels.append(label)
    need(mixed({'n': 4, 'u': us, 'v': vs}, ps, labels) == {}, 'positive chronology')
    word = literal(us, vs, ps, labels)
    need(set(word) == set(range(16)) and all(a == [1, 2, 4, 8] for a in word.values()), 'full positive word')
    bad = us.copy(); bad.pop()
    try:
        mixed({'n': 4, 'u': bad, 'v': vs[:-1]}, ps[:-1], labels[:-1])
    except ValueError:
        pass
    else:
        raise ValueError('deleted query accepted')
    powers = {r: power_interval(r) for r in list(range(1, 10))+[17, 25, 4089]}
    prices = {}
    for name, p in profiles.items():
        c = {r: p['paid'].get(str(r), 0)-p['helpers'].get(str(r), 0) for r in range(1, 10)}
        need(sum(r*v for r, v in c.items()) == 1720, 'complete linear price')
        need(all(sum(v*max(r-j, 0) for r, v in c.items()) <= 0 for j in range(1, 10)), 'concave price')
        last_even, last_odd = (47, 89) if name.startswith('PR5599') else (50, 93)
        results = {}
        for loss, last, first, step in [(2, last_even, 4, 1), (4, last_odd, 5, 2)]:
            for m in [first, last, last+step]:
                poly = moment(p, m, loss)
                need(max(r for r, v in poly.items() if v < 0) < min(r for r, v in poly.items() if v > 0), 'sign separation')
                bound = interval(poly, powers)
                need(bound['upper_numerator'] < 0 if m <= last else bound['lower_numerator'] > 0, 'exact range endpoint')
                results[f'loss_{loss}_m_{m}'] = bound
        g = 511; poly = {r: 2*(g+2)*(-v) for r, v in c.items()}
        poly[9] += 208*g; poly[1+8*g] = 208
        bound = interval(poly, powers); need(bound['lower_numerator'] > 0, 'positive relaxed price')
        results['invalid_star_relaxation_g511'] = bound
        prices[name] = results
    return {'status': 'PASS_PAIRED_STAGE_CHRONOLOGY_CUT', 'projectors': len(projectors), 'idempotent_pairs': pairs, 'pair_ranks': {str(k): v for k, v in counts.items()}, 'witnesses': witnesses, 'all_relative_orders_g3': orders, 'positive_full_word_coefficients': len(word), 'prices': prices, 'limits': {'new_kappa': False, 'native_replay': False, 'independent_review': False, 'formal_kernel': False, 'source_history_preflight': False}}


if __name__ == '__main__':
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    import sys
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'recorded result differs')
    print(result['status'])
