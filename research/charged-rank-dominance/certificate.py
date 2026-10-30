# SPDX-License-Identifier: Apache-2.0
"""Exact rational sufficient budgets for paid concave-profile replacements.
Dugongue, with substantial OpenAI Codex assistance. See PROOF.md.
"""
from fractions import Fraction as F

def need(condition, message):
    if not condition:
        raise ValueError(message)

def budget(old, new, lower, upper):
    need(type(lower) is F and type(upper) is F and 0 < lower <= upper < 1,
         'exact saving interval inside (0,1)')
    need(len(old) == len(new) and len(old) >= 3, 'profile dimensions')
    need(all(type(x) is int and x >= 0 for x in old + new), 'nonnegative integer counts')
    need(old[0] == new[0] == 0, 'rank-zero counts excluded')
    d = [n-o for o,n in zip(old,new)]
    T = len(d)-1
    caps = [sum(min(r,k)*v for r,v in enumerate(d)) for k in range(T+1)]
    need(caps[T] == 0, 'rank mass changed')
    need(all(c <= 0 for c in caps), 'concave order not certified')
    coeff = [0]*(T+1)
    for k in range(1,T):
        coeff[k] += 2*caps[k]
        coeff[k-1] -= caps[k]
        coeff[k+1] -= caps[k]
    need(coeff[1:] == d[1:], 'min-basis identity')
    curvature = [F(0)] + [4*lower/(3+2*lower)] + [
        lower*(1-upper)/(F(k+1)*(1+upper*k)) for k in range(2,T)]
    credits = [-caps[k]*curvature[k] for k in range(1,T)]
    credit = sum(credits,F(0))
    return dict(caps=caps, signed_delta=d,
                curvature_lower=[str(x) for x in curvature],
                credit_by_k=[str(x) for x in credits],
                rank_one_credit=str(credit),
                maximum_strict_integer_charge=(credit.numerator-1)//credit.denominator)

def admissible(old,new,lower,upper,overhead):
    """Positive ranks only; each added rank r is charged by its full rank mass."""
    need(type(overhead) is dict and all(type(r) is int and r >= 1 and
         type(n) is int and n >= 0 for r,n in overhead.items()), 'overhead ranks/counts')
    result = budget(old,new,lower,upper)
    charge = sum(r*n for r,n in overhead.items())
    need(charge < F(result['rank_one_credit']), 'positive overhead exceeds proved credit')
    return result | {'charged_rank_mass':charge}
