#!/usr/bin/env python3
"""Bounded exact price gate only; no scientific execution during preparation.

Source census is MOVE dimensions and declared helper endpoints, not an
interpreter or a new native/endpoint proof. Apache-2.0; Codex assisted.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

B = Path(__file__).resolve().parent
S = B/'sources'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def combine(*terms):
    out = Counter()
    for multiplier, polynomial in terms:
        for rank, count in polynomial.items():
            out[rank] += multiplier*count
    return Counter({r:n for r,n in out.items() if n})


def canonical(n, debt):
    """PR5554 (2),(3), including the separate small-n branch."""
    need(type(n) is int and n >= 0, 'nonnegative integer FULL count')
    if n <= 2:
        return combine((n,debt),(1,{1:312-104*n,1+8*n:-208})) if n else Counter({1:104})
    a, d = (n-3)//2, (n-2)//2
    nonlocal_bill = Counter({1:104*(n-3),1+8*n:-208})
    for length in (a,d):
        for k in range(2,length+2):
            nonlocal_bill[8*k] += 208
            nonlocal_bill[8*k+1] -= 208
    return combine((n,debt),(1,nonlocal_bill))


def ratio_difference(n, debt):
    return combine((n,canonical(n+1,debt)),(-(n+1),canonical(n,debt)))


def census(word):
    need(word['public'] == 735 and len(word['program']) == 25140,
         'pinned current public/event declarations')
    dimensions = list(map(len,word['frames']))
    paid = Counter(abs(dimensions[e[3]]-dimensions[e[2]])
                   for e in word['program'] if e[0] == 'MOVE')
    live = set(word['live'])
    helpers = Counter(dimensions[word['final'][i]]-dimensions[word['initial'][i]]
                      for i in range(735) if i not in live and i-112 not in live)
    need(min(paid)>0 and min(helpers)>0, 'positive declared MOVE/helper ranks')
    return paid, helpers


def invoice(paid, helpers, omit_query=False, omit_idle=False):
    # Independent source-path-length census from authenticated pricing.py.
    p = Counter({r:18*n for r,n in paid.items()})
    t = Counter({r:18*n for r,n in helpers.items()})
    t[145] += 208
    if not omit_query:
        p[1] += 15*104
    for length in (7,8):
        for j in range(1,length+1):
            t[1+8*(j+1)] += 208
            if not omit_idle:
                p[8*(j+1)] += 208
    return p,t


def bind_receipt(receipt, paid, targets):
    need(paid == Counter({int(r):n for r,n in receipt['paid'].items()}),
         'complete paid receipt')
    need(targets == Counter({int(r):n for r,n in receipt['targets'].items()}),
         'complete target receipt')


def rejected(function, label):
    try:
        function()
    except (ValueError,KeyError,TypeError,IndexError):
        return 'rejected'
    raise ValueError('negative control accepted '+label)


def main():
    pins = json.loads((B/'INPUTS.json').read_text())
    for relative, expected in pins['files'].items():
        need(hashlib.sha256((B/relative).read_bytes()).hexdigest() == expected,
             'source SHA256 '+relative)
    capture = json.loads((S/'CAPTURE.json').read_text())
    need(capture['canonical_main'] == pins['canonical_main'], 'source canonical main')
    captured = {a['key']:a for a in capture['sources']}
    for key, origin in pins['captured_texts'].items():
        entry = captured[key]
        raw = entry['content'].encode()
        need(entry['sha'] == origin['git_blob'] == blob(raw), 'captured Git blob '+key)
        need(entry['display_url'] == origin['url'], 'captured source URL '+key)
        need(raw == (S/(key+'.txt')).read_bytes(), 'exact extracted source '+key)
    controls = {}
    raw = captured['handoffresult']['content'].encode()
    controls['corrupted_captured_source'] = rejected(
        lambda:need(blob(raw+b' ') == pins['captured_texts']['handoffresult']['git_blob'],
                    'corrupted Git blob'), 'source corruption')
    qualification = json.loads((S/'ENGINE-QUALIFICATION-INPUTS.json').read_text())
    pair = json.loads((S/'ENGINE-QUALIFICATION-PAIR.json').read_text())
    need(qualification['files']['outputs/economic-sensitivity-feasibility-20261025/interval_math.py']
         == pins['files']['sources/interval_math.py'], 'prior exact engine identity')
    need(pair['complete_output_equal'] is True and pair['scientific_fields_excluded'] == 0
         and pair['result_sha256'] == hashlib.sha256((S/'ENGINE-QUALIFICATION-RESULT.json').read_bytes()).hexdigest(),
         'prior qualification complete output custody')
    word_raw = (S/'WORD.json.gz').read_bytes()
    custody = json.loads((S/'WORD-CUSTODY.json').read_text())['words'][0]
    need(custody['git_blob'] == blob(word_raw) == pins['word_git_blob'] and
         custody['sha256'] == hashlib.sha256(word_raw).hexdigest(), 'current word byte custody')
    word = json.loads(gzip.decompress(word_raw))
    p,h = census(word)
    need(p == Counter({1:2211,2:458,3:496,4:93,5:164,6:18,7:14}) and
         h == Counter({4:83,5:5,8:15,9:424}), 'independent current word census')
    L = combine((1,p),(-1,h))
    P,T = invoice(p,h)
    receipt = json.loads((S/'handoffresult.txt').read_text())['result']
    bind_receipt(receipt,P,T)
    need(sum(P.values()) == receipt['paid_calls'] == 66852 and
         sum(T.values()) == receipt['productive_fields'] == 12814 and
         sum(r*(T[r]-P[r]) for r in set(P)|set(T)) == receipt['rank_mass_surplus'] == 760,
         'complete cardinalities and rank surplus')
    need(sum(r*n for r,n in L.items()) == 1720 == 17*104-48,
         'net local mass identity')
    need(combine((1,P),(-1,T)) == canonical(18,L), 'full source bill equals all-n canonical n18')
    explicit17 = combine((17,L),(1,{1:1456,137:-208}),
                         (1,{r:s for k in range(2,9) for r,s in [(8*k,416),(8*k+1,-416)]}))
    need(canonical(17,L) == explicit17 and (17-3)//2 == (17-2)//2 == 7,
         'n17 balanced sides and exact k2..8 expression')
    for side in ('paid','targets'):
        mutant = deepcopy(receipt)
        key = '1' if side == 'paid' else '9'
        mutant[side][key] += 1
        controls['altered_'+side] = rejected(lambda:bind_receipt(mutant,P,T), side)
    for label,kwargs in [('omitted_query',{'omit_query':True}),('omitted_idle',{'omit_idle':True})]:
        bp,bt = invoice(p,h,**kwargs)
        controls[label] = rejected(lambda:bind_receipt(receipt,bp,bt), label)

    spec = importlib.util.spec_from_file_location('qualified_interval_engine', S/'interval_math.py')
    im = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(im)
    power = lru_cache(None)(im.power)

    def evaluate(polynomial,c,divisor=1):
        lo=hi=Q(0)
        for rank,count in sorted(polynomial.items()):
            a,b = power(rank,c)
            lo += count*(a if count>0 else b)
            hi += count*(b if count>0 else a)
        return lo/divisor,hi/divisor

    def display(pair):
        return im.interval(*pair)

    def ratio_certificate(n,c,debt=L):
        left=evaluate(ratio_difference(n-1,debt),c)
        right=evaluate(ratio_difference(n,debt),c)
        need(left[1]<0<right[0], 'strict ratio minimizing certificate')
        return left,right

    results=[]
    alternative = combine((1,L),(1,{1:37,11:2}))
    for n in (1,2,3,16,17):
        need(ratio_difference(n,L) == ratio_difference(n,alternative),
             'J polynomial independent of every local debt')
    for c in (Q(33,10000),Q(6600001,2000000000)):
        need(0<c<=Q(17,5000), 'isolated-tail theorem range')
        j16,j17=ratio_certificate(17,c)
        bound=evaluate(explicit17,c,17)
        small=[evaluate(canonical(n,L),c,n) for n in (1,2)]
        need(all(x[0]>bound[1] for x in small), 'special n1,n2 cannot beat n17')
        need(bound[0]>Q(1683,25000), 'single ideal tail misses target point')
        residual=(bound[0]-Q(1683,25000),bound[1]-Q(1683,25000))
        controls['nonsaturating_neighbor_'+str(c)] = rejected(
            lambda:ratio_certificate(18,c), 'wrong neighboring minimizer')
        d16=combine((1,canonical(17,L)),(-1,canonical(16,L)))
        need(d16 != ratio_difference(16,L), 'E objective is distinct from E/n objective')
        controls['wrong_ratio_objective_'+str(c)] = rejected(
            lambda:need(d16 == ratio_difference(16,L), 'wrong finite-difference objective'),
            'minimum invoice substituted for minimum ratio')
        controls['sign_wrong_'+str(c)] = rejected(
            lambda:need(-j17[0]>0, 'negated positive J17'), 'sign wrong')
        results.append({'C':str(c),'t':str(1-c),'ratio_minimizing_FULL_count':17,
                        'J16':display(j16),'J17':display(j17),
                        'special_n1_ratio':display(small[0]),'special_n2_ratio':display(small[1]),
                        'B_current_required_further_net_discount_per_FULL':display(bound),
                        'isolated_tail_strict_upper':'0.06732',
                        'residual_after_optimistic_single_tail_upper':display(residual),
                        'isolated_tail_target_point_exclusion':True})
    growth = receipt['nonrecursive']['tensor_native_growth_bound']
    need('sum of local ranks is 5894' in growth and
         'sum of local ranks is 5894' in (S/'handoffpricing.txt').read_text(), 'source growth text')
    need(sum(r*n for r,n in p.items()) == 6013, 'actual local declared paid rank mass')
    bit=Q(receipt['ordinary_BIT']['admitted'])
    need(bit == Q(17,5000) > Q(6600001,2000000000) > Q(33,10000), 'inherited BIT target budget only')
    result={'schema':'successor-price-gate/v1','status':'PASS_SCOPED_EXACT_ECONOMIC_GATE',
            'reviewed_head':pins['current_head'],'local_paid':dict(p),'local_helpers':dict(h),
            'local_paid_count':sum(p.values()),'local_helper_count':sum(h.values()),
            'local_paid_rank_mass':6013,'local_helper_rank_mass':sum(r*n for r,n in h.items()),
            'local_paid_minus_helpers':dict(L),'complete_paid':dict(P),'complete_targets':dict(T),
            'complete_paid_count':66852,'complete_target_count':12814,'complete_rank_surplus':760,
            'n17_numerator_coefficients':dict(explicit17),
            'all_n_coverage':'PR5554 PROOF sections2/3: strict discrete convexity on every n>=0, J increments strictly positive; exact J16/J17 plus explicit special n1/n2 comparisons.',
            'J_independent_of_local_debt':True,'price_points':results,
            'funded_target':'33/10000','declared_tested_point':'6600001/2000000000',
            'tested_point_is_new_funding_certificate':False,'source_admitted_BIT':str(bit),
            'growth_text_gap':{'source_claimed_rank_sum':5894,'recounted_paid_rank_mass':6013,
                               'status':'STATIC_DESCRIPTION_MISMATCH_NOT_A_DISPROOF_OF_GROWTH_THEOREM'},
            'scope':'One isolated helper terminal-tail change with consistent target loss, no new target/controller/fusion; all-n controller relaxation under source hypotheses. Two exact target points only; no larger-C changed-family exclusion.',
            'coordination_hold':'No released candidate; 2832 skipped points are parent5561 aggregate, not candidates; no scan.',
            'coverage_excluded':['native semantics','arbitrary-input endpoints','owned lifetime legality','precision and ordinary routes','compiler strictification','54 strict and4 functional outer inequalities','physical construction'],
            'controls':controls,'physical_witness':False,'new_kappa':None,'stop':True}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
