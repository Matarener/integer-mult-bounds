# SPDX-License-Identifier: Apache-2.0
"""Finite-control owner-cover gate supply, with exact counting certificates.

Chris R / Clear1nsight with substantial OpenAI Codex assistance.
This is an offline source-cost proof checker, not a physical matrix sampler.
"""
from fractions import Fraction
from math import prod
from collections import Counter
import sys


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def order(n):
    return prod((1 << (k-1)) - int(k > 1 and k % 2) for k in range(1, n+1))


def certificate():
    n, head, tail = 73, 9, 64
    choices = [(1 << (tail-j-1)) - (1 << (j+1)) for j in range(head)]
    frame_lower = prod(choices)
    gamma, completions = order(n), order(tail)
    head_probability = Fraction(frame_lower * completions, gamma)
    relative_density = head_probability * (1 << (head*head))
    gl_prob = lambda k: prod(Fraction((1 << i)-1, 1 << i) for i in range(1,k+1))
    event_lower = {"add_6_8": relative_density*gl_prob(8)/4,
                   "add_8_6": relative_density*gl_prob(6)/4}
    need(relative_density > Fraction(1,2), 'every head has at least half uniform mass')
    need(all(x > Fraction(1,32) for x in event_lower.values()), 'uniform gate supply')
    need(736*event_lower['add_6_8'] > 4, 'four missing target6 source8 gates')
    need(736*event_lower['add_8_6'] > 1, 'one missing target8 source6 gate')
    need(672*event_lower['add_6_8'] > 4, 'service-only target6 source8 supply')
    need(672*event_lower['add_8_6'] > 1, 'service-only target8 source6 supply')
    return {
        'dimension':n,'head_dimension':head,'tail_dimension':tail,
        'tail_choice_lower':choices,'tail_frame_lower':frame_lower,
        'gamma':gamma,'suffix_completions':completions,
        'head_probability_lower':head_probability,
        'relative_uniform_density_lower':relative_density,
        'gate_probability_lower':event_lower,
        'coarse_gate_probability_lower':Fraction(1,32),
        'owner_word_occurrences':736,'service_owner_word_occurrences':672,
        'coarse_owner_supply_per_gamma':Fraction(736,32),
        'coarse_service_supply_per_gamma':Fraction(672,32),
        'deficits_per_gamma':{'add_6_8':4,'add_8_6':1},
        'strict_inequalities':True,
    }


def _reduce_prefix(rows, k):
    """Check the exact source leading-block event; reject an outside pivot."""
    rows=list(rows)
    for j in range(k):
        pivot=next((i for i in range(j,k) if (rows[i] >> j)&1),None)
        if pivot is None:
            return None
        if pivot != j:
            for target,source in ((j,pivot),(pivot,j),(j,pivot)):
                rows[target] ^= rows[source]
        for i in range(len(rows)):
            if i != j and (rows[i] >> j)&1:
                rows[i] ^= rows[j]
    return rows


def event(rows, target, source):
    need((target,source) in ((6,8),(8,6)), 'named gate class')
    work=_reduce_prefix(rows, source)
    return work is not None and bool((work[source] >> source)&1) and bool((work[target] >> source)&1)


def _orthogonal(rows):
    return all(((a&b).bit_count()&1)==(i==j)
               for i,a in enumerate(rows) for j,b in enumerate(rows))


def _transvection(rows, support):
    need(support.bit_count()%2 == 0, 'isotropic transvection direction')
    # Left multiplication by I + u u^T. Its square is I for even-weight u.
    total=0
    for i,row in enumerate(rows):
        if (support >> i)&1:
            total ^= row
    return tuple(row ^ (total if (support >> i)&1 else 0)
                 for i,row in enumerate(rows))


def source_checks(cohort):
    """Call only after the containing runtime authenticated its source closure."""
    cohort.monomial_api()
    reference=sys.modules['phase_recipe'].reference
    word=reference.binary_word
    witnesses={}
    rows=tuple(1<<i for i in range(73))
    # Deterministic orthogonal witnesses, not evidence for the counting theorem.
    seed=7
    for step in range(160):
        positions=[]
        while len(positions)<4:
            seed=(1103515245*seed+12345)&0x7fffffff
            p=(seed>>9)%13
            if p not in positions:
                positions.append(p)
        rows=_transvection(rows,sum(1<<i for i in positions))
        need(_orthogonal(rows),'actual orthogonal witness')
        for target,source in ((6,8),(8,6)):
            key=f'add_{target}_{source}'
            if key not in witnesses and event(rows,target,source):
                gates=Counter(word({'matrix_rows':rows,'offset':0}))
                need(gates[('add',target,source)]>=1,'literal source emits guaranteed gate')
                need(Counter(reversed(word({'matrix_rows':rows,'offset':0})))==gates,
                     'inverse execution preserves gate histogram')
                witnesses[key]={'step':step,'matrix_rows':rows,'gate_multiplicity':gates[('add',target,source)]}
        if len(witnesses)==2:
            break
    need(len(witnesses)==2,'both real orthogonal source witnesses')
    identity=tuple(1<<i for i in range(73))
    need(not event(identity,6,8) and not event(identity,8,6),'identity rejects false universal per-owner claim')
    need(not word({'matrix_rows':identity,'offset':0}),'identity has no gates')
    c=certificate()
    # The named source cover counts prefixes with precisely these orders.
    import importlib.util
    cover_path=cohort.ROOT/'research/physical-complex-controller/cover.py'
    spec=importlib.util.spec_from_file_location('qq16_gate_cover_source',cover_path)
    cover=importlib.util.module_from_spec(spec);spec.loader.exec_module(cover)
    need(tuple(order(n) for n in range(74))==cover.group_orders(73),'authenticated cover order match')
    need(all(cover.is_orthogonal(w['matrix_rows']) for w in witnesses.values()),'source orthogonal admission')
    return {'witnesses':witnesses,'identity_negative_control':True,
            'source_group_orders_match':True,'count_certificate':c}


def jsonable(value):
    if isinstance(value,Fraction):
        return {'numerator':value.numerator,'denominator':value.denominator}
    if isinstance(value,dict):
        return {k:jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [jsonable(v) for v in value]
    return value
