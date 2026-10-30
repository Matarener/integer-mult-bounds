#!/usr/bin/env python3
"""Exact all-group collision refutation; standard library, no group sampling."""
import itertools
import json

IDENTITY = 9


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL ' + message)


def multiply(a, b):
    return sum((sum(((a >> (2*i+t)) & 1) * ((b >> (2*t+j)) & 1)
                    for t in range(2)) % 2) << (2*i+j)
               for i in range(2) for j in range(2))


PROJECTORS = tuple(n for n in range(16)
                   if multiply(n, n) == n and ((n & 1) ^ ((n >> 3) & 1)))


def expand(projectors):
    terms = {0: IDENTITY}
    for position, n in enumerate(projectors):
        terms = {mask: product for old, coefficient in terms.items()
                 for mask, product in ((old, multiply(coefficient, IDENTITY ^ n)),
                                       (old | (1 << position), multiply(coefficient, n)))}
    return terms


def cancellation_rules(k):
    words = [tuple(i for i in range(k) if mask >> i & 1) for mask in range(1 << k)]
    index = {word: mask for mask, word in enumerate(words)}
    rules = set()
    for a, u in enumerate(words):
        for b, v in enumerate(words[:a]):
            prefix = suffix = 0
            while prefix < min(len(u), len(v)) and u[prefix] == v[prefix]:
                prefix += 1
            while suffix < min(len(u), len(v)) and u[-1-suffix] == v[-1-suffix]:
                suffix += 1
            for left, right in ((u[prefix:], v[prefix:]),
                                (u[:-suffix], v[:-suffix]) if suffix else (u, v)):
                c, d = index[left], index[right]
                if (a, b) != (c, d):
                    rules.add((a, b, c, d))
                    rules.add((c, d, a, b))
    return tuple(sorted(rules))


class CollisionProblem:
    def __init__(self, k, cancellation=True, minimum=3):
        self.k = k
        self.target_a = 1 << k
        self.target_b = self.target_a + 1
        self.rules = cancellation_rules(k) if cancellation else ()
        self.short = tuple(mask for mask in range(1 << k) if mask.bit_count() < minimum)
        self.nodes = 0

    def solve(self, projectors):
        require(len(projectors) == self.k, 'wrong word length')
        terms = expand(projectors)
        equations = tuple(tuple(mask for mask, value in terms.items() if value >> entry & 1)
                          + ((self.target_a,) if entry == 0 else
                             (self.target_b,) if entry == 3 else ()) for entry in range(4))
        return self.search(equations, list(range((1 << self.k) + 2)))

    def search(self, equations, partition):
        self.nodes += 1
        require(self.nodes <= 200000, 'explicit search-node cap exceeded')
        parent = partition[:]

        def root(a):
            while parent[a] != a:
                a = parent[a]
            return a

        def union(a, b):
            a, b = root(a), root(b)
            if a == b:
                return False
            parent[max(a, b)] = min(a, b)
            return True

        while True:
            changed = False
            for a, b, c, d in self.rules:
                if root(a) == root(b):
                    changed = union(c, d) or changed
            if any(root(0) == root(1 << i) for i in range(self.k)):
                return None
            if root(self.target_a) == root(self.target_b):
                return None
            if any(root(target) == root(mask) for target in (self.target_a, self.target_b)
                   for mask in self.short):
                return None
            residual = []
            for equation in equations:
                odd = set()
                for node in equation:
                    node = root(node)
                    odd.symmetric_difference_update((node,))
                if len(odd) % 2:
                    return None
                if len(odd) == 2:
                    changed = union(*odd) or changed
                elif odd:
                    residual.append(tuple(sorted(odd)))
            if not changed:
                break
        if not residual:
            return parent
        equation = min(residual, key=lambda item: (len(item), item))
        first = equation[0]
        # Every true equality class has even parity, so first has a partner.
        for partner in equation[1:]:
            branch = parent[:]
            a, b = root(first), root(partner)
            branch[max(a, b)] = min(a, b)
            witness = self.search(equations, branch)
            if witness is not None:
                return witness
        return None


def exact_endpoint(pattern, projectors):
    coefficients = {}
    for mask, coefficient in expand(projectors).items():
        word = ''.join(label for i, label in enumerate(pattern) if mask >> i & 1)
        coefficients[word] = coefficients.get(word, 0) ^ coefficient
    return {word: value for word, value in coefficients.items() if value}


def main():
    require(PROJECTORS == (1, 3, 5, 8, 10, 12), 'rank-one projector inventory')
    # Independent outer-product characterization, not a second trace filter.
    outer = {sum(((u >> i) & 1)*((v >> j) & 1) << (2*i+j)
                 for i in range(2) for j in range(2))
             for u in (1, 2, 3) for v in (1, 2, 3) if (u & v).bit_count() % 2}
    require(set(PROJECTORS) == outer, 'outer-product inventory mismatch')
    require(multiply(3, 5) != multiply(5, 3), 'matrix order control')
    # Independently authenticate every generated rule as a single context law.
    for k in range(7):
        words = [tuple(i for i in range(k) if mask >> i & 1) for mask in range(1 << k)]
        for a, b, c, d in cancellation_rules(k):
            valid = False
            for u, v, s, t in ((words[a], words[b], words[c], words[d]),
                               (words[c], words[d], words[a], words[b])):
                for split in range(len(u) + 1):
                    context = u[:split]
                    valid |= u == context + s and v == context + t
                    context = u[split:]
                    valid |= u == s + context and v == t + context
            require(valid, 'invalid cancellation rule')
    require(CollisionProblem(6).solve((1, 1, 1, 8, 8, 8)) is not None,
            'solver rejected six-call true endpoint')
    require(CollisionProblem(4, minimum=2).solve((1, 1, 8, 8)) is not None,
            'solver rejected preceding four-call true endpoint')
    require({m: v for m, v in expand((1, 5, 5, 3, 10)).items() if v}
            == {8: 12, 14: 12, 15: 3, 22: 8, 23: 2},
            'written collision example coefficients')
    require(exact_endpoint('xyxyxy', (1, 1, 1, 8, 8, 8)) == {'xyx': 1, 'yxy': 8},
            'six-call positive endpoint')
    relaxed = CollisionProblem(4, cancellation=False)
    require(relaxed.solve((1, 5, 1, 10)) is not None, 'missing-cancellation control did not reopen')
    shortened = CollisionProblem(2, minimum=1)
    require(shortened.solve((1, 8)) is not None, 'short-target control did not reopen')
    require(CollisionProblem(5).solve((1, 5, 5, 3, 10)) is None,
            'written five-call collision example')
    results = []
    for k in range(6):
        problem = CollisionProblem(k)
        tested = 0
        for projectors in itertools.product(PROJECTORS, repeat=k):
            require(problem.solve(projectors) is None, 'surviving collision relaxation ' + str(projectors))
            tested += 1
        require(tested == 6**k, 'incomplete projector enumeration')
        results.append({'calls': k, 'tuples': tested, 'nodes': problem.nodes, 'survivors': 0})
    print('PASS_DIAGONAL_PAIR_FIVE_CALL_COLLISIONS ' + json.dumps(results, sort_keys=True))


if __name__ == '__main__':
    main()
