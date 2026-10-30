"""Exact signed two-frame support certificate; Python standard library.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The determinant/support reduction is credited to Nick Petalas (PR2910),
apoursh (PR6089) and Josie Elliston (PR6111); this independently written
census removes both positivity filters from the latter question.

All addresses use the rational basis (A,B,P), not physical matrix entries.
The six count variables are (A,B,P,Q,R,S), with Q=A+B-P. No predecessor
code, theorem checker, nonstandard dependency, Git or network is imported.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json

ZERO = (Fraction(0),) * 3
A = (Fraction(1), Fraction(0), Fraction(0))
B = (Fraction(0), Fraction(1), Fraction(0))
P = (Fraction(0), Fraction(0), Fraction(1))
Q = (Fraction(1), Fraction(1), Fraction(-1))
OLD = (A, B, P, Q)
TARGETS = ((1, 0, 1), (2, 1, -1), (0, 1, 1), (1, 2, -1))
TOTAL = (4, 4, 0)
EXPECTED_FREE = {
    (1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 2), (1, 1, 1, 1, 2, 1),
    (2, 1, 1, 1, 1, 1), (1, 2, 1, 1, 1, 1),
    (1, 1, 2, 1, 1, 1), (1, 1, 1, 2, 1, 1),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(left, right):
    return tuple(x + y for x, y in zip(left, right))


def minus(left, right):
    return tuple(x - y for x, y in zip(left, right))


def times(scale, vector):
    return tuple(scale * x for x in vector)


def matrix(vector):
    """Map basis coordinates to the physical rational symmetric matrix."""
    a, b, p = vector
    return ((a + Fraction(p, 2), Fraction(p, 2)),
            (Fraction(p, 2), b + Fraction(p, 2)))


def determinant_twice(vector):
    a, b, p = vector
    return 2*a*b + (a+b)*p


def trace(vector):
    return sum(vector)


def signed_rank_one(vector):
    # Nonzero symmetric real rank-one matrices are positive OR negative
    # semidefinite. Trace may have either sign. The zero matrix is excluded.
    return vector != ZERO and determinant_twice(vector) == 0


def positive_rank_one(vector):
    return signed_rank_one(vector) and trace(vector) > 0


def positive_definite(vector):
    return determinant_twice(vector) > 0 and trace(vector) > 0


def old_address(counts):
    a, b, p, q = counts[:4]
    return (a+q, b+q, p-q)


def residual(counts):
    return minus(TOTAL, old_address(counts))


def profiles(limit=7):
    """All nonnegative counts with r,s>=1 and total<=limit; no PSD filter."""
    def compositions(total, slots):
        if slots == 1:
            yield (total,)
            return
        for first in range(total + 1):
            for rest in compositions(total-first, slots-1):
                yield (first,) + rest
    for length in range(2, limit+1):
        for c in compositions(length-2, 6):
            yield c[:4] + (c[4]+1, c[5]+1)


def target_splits(counts, target):
    """None means every split has a support; otherwise return exact X=rR.

    Eliminate S=(M-X)/s from each bounded call subset. Integer arithmetic
    forms (s*i-r*j) X = r*s*(target-old_subset)-r*j*M. Nonzero coefficients
    pin X exactly; a zero coefficient is free iff the right side is zero.
    Candidate membership checks signed rank-one only, before any sign test.
    """
    r, s = counts[4:]
    M = residual(counts)
    pinned = set()
    for old in product(*(range(c+1) for c in counts[:4])):
        remainder = minus(target, old_address(old))
        for i in range(r+1):
            for j in range(s+1):
                denominator = s*i-r*j
                numerator = minus(times(r*s, remainder), times(r*j, M))
                if denominator == 0:
                    if numerator == ZERO:
                        return None
                else:
                    X = tuple(Fraction(x, denominator) for x in numerator)
                    if signed_rank_one(X) and signed_rank_one(minus(M, X)):
                        pinned.add(X)
    return pinned


def classify(counts, targets=TARGETS):
    constrained = []
    for target in targets:
        values = target_splits(counts, target)
        if values is not None:
            if not values:
                return set()
            constrained.append(values)
    return None if not constrained else set.intersection(*constrained)


def direct_support(counts, R, S, targets=TARGETS):
    """Independent literal subset-sum route; no elimination or residual code."""
    sums = {ZERO}
    for count, address in zip(counts, OLD+(R,S)):
        sums = {plus(before, times(k, address)) for before in sums for k in range(count+1)}
    return all(target in sums for target in targets)


def exact_total(counts, R, S):
    total = ZERO
    for count, address in zip(counts, OLD+(R,S)):
        total = plus(total, times(count, address))
    return total


def inventory():
    free, pinned, empty, indefinite = [], [], [], []
    cases = list(profiles())
    require(len(cases) == 462 and len(set(cases)) == 462, 'complete count domain')
    require({sum(c) for c in cases} == set(range(2,8)), 'all lengths 2 through 7')
    for counts in cases:
        M = residual(counts)
        if determinant_twice(M) < 0:
            indefinite.append(counts)
        choices = classify(counts)
        if choices is None:
            free.append(counts)
            require(positive_definite(M), 'every unconstrained family has definite residual')
        elif not choices:
            empty.append(counts)
        else:
            for X in sorted(choices):
                R = times(Fraction(1,counts[4]),X)
                S = times(Fraction(1,counts[5]),minus(M,X))
                # Positivity is an OUTPUT, never a candidate filter.
                require(positive_rank_one(R) and positive_rank_one(S), 'pinned split positivity')
                require(exact_total(counts,R,S) == TOTAL, 'pinned determinant identity')
                require(direct_support(counts,R,S), 'pinned literal support corroboration')
                pinned.append((counts,R,S))
    require(set(free)==EXPECTED_FREE, 'exact seven free families')
    require(len(pinned)==32, 'exact signed pinned split inventory')
    require(len(indefinite)==20 and all(c in empty for c in indefinite),
            'all twenty previously omitted indefinite residuals excluded by support')
    return cases, free, pinned, empty, indefinite


def controls():
    checks=0
    # All four negative old directions, and non-coordinate rational negatives,
    # really enter the candidate predicate; zero and rank-two matrices do not.
    for v in OLD:
        for scale in (Fraction(-1),Fraction(-2,3),Fraction(-7,2)):
            require(signed_rank_one(times(scale,v)), 'negative frame silently filtered')
            checks+=1
    for x,y,c in ((1,2,Fraction(-1,3)),(2,-3,Fraction(-5,7))):
        physical=(c*x*x,c*y*y,c*x*y)
        v=(physical[0]-physical[2],physical[1]-physical[2],2*physical[2])
        require(signed_rank_one(v) and trace(v)<0, 'negative rotated rank-one fixture')
        checks+=1
    require(not signed_rank_one(ZERO),'zero rank-one mutant')
    require(not signed_rank_one(plus(A,B)),'rank-two mutant')
    checks+=2
    # Literal coordinate word at length nine: replace one A by 2A,-A.
    # This shows the excluded negative premise is not globally impossible.
    R,S=times(2,A),times(-1,A)
    counts=(1,2,2,2,1,1)
    require(exact_total(counts,R,S)==TOTAL and direct_support(counts,R,S),
            'nine-call signed positive control')
    choices=classify(counts)
    require(choices is None or R in choices,'nine-call signed split absent')
    word=((R,0),(S,0),(P,0),(A,1),(Q,1),(B,2),(P,2),(B,3),(Q,3))
    for width in (4,6):
        endpoint=[ZERO]*width
        for address,role in word:
            endpoint[role]=plus(endpoint[role],address)
        require(tuple(endpoint)==TARGETS+(ZERO,)*(width-4),'signed coordinate word endpoint')
        damaged=list(endpoint)
        damaged[0]=minus(damaged[0],S)
        require(tuple(damaged)!=TARGETS+(ZERO,)*(width-4),'omitted negative call mutant')
        checks+=2
    checks+=2
    # Original eight-call endpoint survives; wrong target changes free list.
    require(direct_support((1,1,2,2,1,1),A,B),'eight-call positive control')
    require(classify((1,1,1,1,1,1),(times(9,A),)+TARGETS[1:]) != None,
            'changed target leaves free-family claim unchanged')
    checks+=2
    # Direct support checks that the twenty indefinite residuals are truly
    # allowed inputs. Rational split X=v v^T/(v^T M^-1 v) can have either sign.
    signed_cases=accepted=0
    for counts in profiles():
        M=residual(counts)
        if determinant_twice(M)>=0:
            continue
        m=matrix(M); d=m[0][0]*m[1][1]-m[0][1]*m[1][0]
        for x,y in ((1,0),(0,1),(1,1),(1,-1),(1,2),(2,1),(1,-2),(2,-1)):
            denominator=m[1][1]*x*x-2*m[0][1]*x*y+m[0][0]*y*y
            if not denominator:
                continue
            c=d/denominator
            physical=(c*x*x,c*y*y,c*x*y)
            X=(physical[0]-physical[2],physical[1]-physical[2],2*physical[2])
            Y=minus(M,X)
            require(signed_rank_one(X) and signed_rank_one(Y),'indefinite split parameterization')
            require(trace(X)*trace(Y)<0,'indefinite split needs opposite signs')
            R=times(Fraction(1,counts[4]),X);S=times(Fraction(1,counts[5]),Y)
            signed_cases+=1
            if direct_support(counts,R,S):accepted+=1
    require(signed_cases>0 and accepted==0,'indefinite direct-support control')
    return checks,signed_cases


def run():
    cases,free,pinned,empty,indefinite=inventory()
    checks,signed_cases=controls()
    serial={'free':free,'pinned':[(c,tuple(map(str,R)),tuple(map(str,S))) for c,R,S in pinned],
            'empty':empty,'indefinite':indefinite}
    digest=sha256(json.dumps(serial,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'profiles':len(cases),'free_families':len(free),'pinned_splits':len(pinned),
            'empty_profiles':len(empty),'indefinite_profiles':len(indefinite),
            'negative_pinned_splits':0,'signed_controls':signed_cases,'controls':checks,
            'inventory_sha256':digest}
    print('PASS_SIGNED_TWO_FRAME_SUPPORT '+json.dumps(result,sort_keys=True))
    return result


if __name__=='__main__':
    run()
