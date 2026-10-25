#!/usr/bin/env python3
"""Independent projective/word oracle; no BFS or predecessor code imports.

ToikY with substantial OpenAI Codex assistance, Apache-2.0. The right-vector
alphabet and predecessor question retain Nick Petalas/Wentao Li's credit.
Finite checks corroborate PROOF.md; they do not prove its quantified claims.
"""
import itertools
import json


def require(value, message):
    if not value:
        raise ValueError(message)


def prime(p):
    return type(p) is int and p >= 2 and all(p % d for d in range(2, int(p**0.5) + 1))


def multiply(a, b, p):
    return ((a[0]*b[0]+a[1]*b[2]) % p, (a[0]*b[1]+a[1]*b[3]) % p,
            (a[2]*b[0]+a[3]*b[2]) % p, (a[2]*b[1]+a[3]*b[3]) % p)


def determinant(a, p):
    return (a[0]*a[3]-a[1]*a[2]) % p


def apply(a, t, p):
    return ((a[0]*t[0]+a[1]*t[1]) % p, (a[2]*t[0]+a[3]*t[1]) % p)


def lines(p):
    require(prime(p), "the finite oracle implements prime fields only")
    return [(1, x) for x in range(p)] + [(0, 1)]


def zero_census(components, p):
    return [sum((phi[0]*apply(m, t, p)[0]+phi[1]*apply(m, t, p)[1]) % p == 0
                for m in components)
            for phi in lines(p) for t in lines(p)]


def triple_word(components, p):
    """Common paid rows e1/e2/e1; compare literal products, not receipts."""
    require(prime(p), "prime-field implementation boundary")
    word = [[], [], []]
    for m in components:
        a, b, c, d = m
        require(determinant(m, p) != 0, "invertible-target premise")
        r = 0 if d else 1
        pivot = (d-r*b) % p
        require(pivot != 0, "nonunit third-factor pivot")
        f = (c-r*a)*pow(pivot, -1, p) % p
        e = determinant(m, p)*pow(pivot, -1, p) % p
        factors = [(1, 0, r, 1), (1, b, 0, pivot), (e, 0, f, 1)]
        require(multiply(multiply(factors[0], factors[1], p), factors[2], p) == tuple(m), "complete three-factor product")
        for stage, factor in zip(word, factors):
            stage.append(factor)
    for stage, right in zip(word, [(1, 0), (0, 1), (1, 0)]):
        for m in stage:
            if right == (1, 0):
                require(m[1] == 0 and m[3] == 1, "e1 factor shape")
            else:
                require(m[0] == 1 and m[2] == 0, "e2 factor shape")
    return word


def product(word, p):
    result = [(1, 0, 0, 1)] * len(word[0])
    for stage in word:
        result = [multiply(a, b, p) for a, b in zip(result, stage)]
    return result


def classify(components, p):
    if all(m == components[0] for m in components):
        return 0, 0
    # A single paid factor leaves a common K input line unchanged after
    # the free endpoint. Equality here is literal vector equality.
    one = any(len({apply(m, t, p) for m in components}) == 1 for t in lines(p))
    if one:
        return 1, 1
    two = 0 in zero_census(components, p)
    return (2 if two else 3), 2


def run():
    binary = [m for m in itertools.product(range(2), repeat=4) if determinant(m, 2)]
    records = []
    for components in itertools.product(binary, repeat=3):
        cost, delta = classify(components, 2)
        word = triple_word(components, 2)
        require(product(word, 2) == list(components), "full product-field endpoint")
        records.append(dict(components=[list(m) for m in components], cost=cost, delta=delta))

    prime_rows = []
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        irreducible = [(a, b) for a in range(p) for b in range(p)
                       if all((x*x+a*x+b) % p for x in range(p))]
        require(len(irreducible) == p*(p-1)//2, "quadratic counting argument")
        a, b = irreducible[0]
        alpha = (0, -b % p, 1, -a % p)
        components = [(1, (-t*b) % p, t, (1-t*a) % p) for t in range(p)] + [alpha]
        require(all(determinant(m, p) for m in components), "extension representative invertibility")
        zeros = zero_census(components, p)
        require(set(zeros) == {1}, "one forbidden component at every projective pair")
        word = triple_word(components, p)
        require(product(word, p) == components, "attaining three-factor witness")
        prime_rows.append(dict(p=p,components=p+1,polynomial=[b,a,1],projective_pairs=(p+1)**2,zero_components_per_pair=1,word=[[[*m] for m in stage] for stage in word]))

    # The predecessor's proposed F3^3 test cannot refute the invertible claim:
    # check all possible nonzero first-column triples, not sampled matrices.
    vectors = [v for v in itertools.product(range(3), repeat=2) if any(v)]
    column_triples = 0
    for images in itertools.product(vectors, repeat=3):
        require(any(all((phi[0]*v[0]+phi[1]*v[1]) % 3 for v in images) for phi in lines(3)), "F3^3 common-row guarantee")
        column_triples += 1

    upper_cases = 0
    for p in [2, 3, 5, 7]:
        for matrix in itertools.product(range(p), repeat=4):
            if determinant(matrix, p):
                require(product(triple_word([matrix], p), p) == [matrix], "literal upper word")
                upper_cases += 1

    canonical = [(1,0,0,1),(0,1,1,1),(1,1,1,0)]
    require(classify(canonical, 2) == (3,2), "canonical obstruction")
    require(0 not in zero_census(canonical, 2), "all nine pivots obstructed")
    require(classify(canonical[:2], 2)[0] <= 2, "removing a component removes this floor")
    word = triple_word(canonical, 2)
    require(product(word[:2], 2) != canonical, "dropped paid factor must fail")
    require(product(list(reversed(word)), 2) != canonical, "reversed paid word must fail")
    require(len(set(canonical)) > 1, "componentwise-free relaxation is outside the common-free model")
    for bad in [4,6,9]:
        try:
            lines(bad)
        except ValueError:
            pass
        else:
            raise ValueError("composite-modulus arithmetic was mislabelled a field")
    try:
        triple_word([(1,0,0,0)],2)
    except ValueError:
        pass
    else:
        raise ValueError("singular target admitted outside the stated upper theorem")
    return dict(records=records,prime_witnesses=prime_rows,first_column_triples_F3=column_triples,upper_word_matrices=upper_cases,canonical=dict(components=canonical,cost=3,delta=2,zero_census=zero_census(canonical,2),word=word),controls=dict(drop_component=True,drop_factor=True,reverse_factors=True,componentwise_free_is_changed=True,composite_moduli_rejected=[4,6,9],singular_outside_premise=True))


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True))
