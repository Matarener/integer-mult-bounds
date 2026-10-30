"""Discriminating exact checks of the two structural proof steps.

These finite cases check identities and failure modes; the general proofs
remain PROOF.md and SHIFTED-LOG.md.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import comb, prod, factorial
import unittest
import intervals as E
import compiler


def exact_splits(rank, cutoff):
    q, r = divmod(rank, cutoff)
    return [cutoff]*q + ([r] if r else [])


def polynomial(ranks):
    """Formal coefficients of symbols X_rank, before evaluating X_rank=rank^t."""
    return Counter(ranks)


def linear(*terms):
    out = Counter()
    for multiplier, values in terms:
        for key, count in values.items():
            out[key] += multiplier*count
    return {key: count for key, count in out.items() if count}


class NetTaxMath(unittest.TestCase):
    def test_literal_gap_identity_and_target_credit_control(self):
        targets, paid = [1, 4, 4, 9], [1, 1, 8]
        for v in (1, 2, 3):
            T = [prod(word) for word in product(targets, repeat=v)]
            P = [prod(word) for word in product(paid, repeat=v)]
            J, L = 2**v, 5**v
            split_paid = [part for rank in P for part in exact_splits(rank, J)]
            completions = [K for K in T if K < L]
            split_completion = [part for K in completions
                                for part in exact_splits(L-K, J)]
            final_targets = polynomial([max(K, L) for K in T])
            final_paid = polynomial(split_paid+split_completion)
            raw_gap = linear((1, polynomial(T)), (-1, polynomial(P)))
            original_tax = linear((1, polynomial(split_paid)), (-1, polynomial(P)))
            completion_tax = linear((1, polynomial(split_completion)),
                                    (-1, polynomial([L]*len(completions))),
                                    (1, polynomial(completions)))
            direct = linear((1, final_targets), (-1, final_paid))
            decomposed = linear((1, raw_gap), (-1, original_tax), (-1, completion_tax))
            self.assertEqual(direct, decomposed)
            # Omitting the new target moment is a genuine incorrect identity.
            missing_credit = linear((1, raw_gap), (-1, original_tax),
                                    (-1, polynomial(split_completion)))
            self.assertNotEqual(direct, missing_credit)
            self.assertEqual(sum(T)-sum(P),
                             sum(max(K, L) for K in T)-sum(split_paid+split_completion))

    def test_paid_tax_against_literal_splits(self):
        C, t = Q(1, 2), Q(1, 2)
        for u in (C, Q(3, 4), Q(3, 2), Q(3)):
            h = E.scale(E.qpower(t, t/C), C)
            monotone = (max(C/u, h[0]), max(C/u, h[1]))
            jensen = (E.power(2, C) if u == C else E.scale(
                E.mul(E.power(2, u), E.qpower(1-C/u, u/C-1)), C/u))
            for J in range(1, 13):
                for R in range(J+1, 65):
                    charge = E.moment(Counter(exact_splits(R, J)), t)
                    tax = E.sub(charge, E.power(R, t))
                    scale = E.mul(E.power(R, t+u), E.power(J, -u))
                    # Each coefficient is valid independently, including u=C
                    # and u large enough that h dominates C/u.
                    for coefficient in (monotone, jensen):
                        bound = E.mul(coefficient, scale)
                        self.assertLess(tax[1], bound[0])

    def test_completion_net_tax_against_literal_splits(self):
        C, t = Q(1, 2), Q(1, 2)
        h = E.scale(E.qpower(t, t/C), C)
        for J in range(1, 9):
            for L in range(J+1, 25):
                universal = E.sub(E.add(E.mul((Q(L),)*2, E.power(J, -C)),
                                       E.scale(E.mul(h, E.power(J, t)), 2)),
                                  E.power(L, t))
                for K in range(1, L):
                    literal = E.sub(E.add(E.power(K, t),
                                         E.moment(Counter(exact_splits(L-K, J)), t)),
                                    E.power(L, t))
                    if 4*K == J and 4*((L-K) % J) == J:
                        # Both maxima rho^t-rho are attained at rho=1/4;
                        # this is exact equality, independently of rounding.
                        self.assertLessEqual(literal[0], universal[1])
                        self.assertLessEqual(universal[0], literal[1])
                    else:
                        self.assertLess(literal[1], universal[0])
                    # Including target credit matters: completion can cost
                    # far less than its entire paid charge.
                    if K == L-1:
                        paid = E.moment(Counter(exact_splits(L-K, J)), t)
                        self.assertLess(literal[1], paid[0])

    def test_rational_interval_reference_points(self):
        self.assertLess(E.log_bounds(2)[0], Q('0.693147180559945309417232121459'))
        self.assertGreater(E.log_bounds(2)[1], Q('0.693147180559945309417232121458'))
        for base, exponent, exact in ((4, Q(1, 2), 2), (9, Q(1, 2), 3),
                                      (Q(1, 4), Q(-1, 2), 2)):
            lo, hi = E.qpower(base, exponent)
            self.assertLessEqual(lo, exact)
            self.assertGreaterEqual(hi, exact)

    def test_convex_order_against_nonbernoulli_inventory(self):
        # A genuine three-point law with mean1/2. Iterated chord domination
        # bounds it by Binomial(n,1/2), including its actual variance.
        law = [(Q(0), Q(1, 4)), (Q(1, 2), Q(1, 2)), (Q(1), Q(1, 4))]
        for n in range(1, 5):
            for p in (1, 2, 5, 8):
                actual = sum(prod(w for _, w in word)*(1+sum(x for x, _ in word))**p
                             for word in product(law, repeat=n))
                chord = sum(Q(comb(n, k), 2**n)*(1+k)**p for k in range(n+1))
                self.assertLessEqual(actual, chord)

    def test_weighted_polynomial_identity_and_shift_control(self):
        p, q, A, B0, beta = 7, Q(3, 5), Q(4, 5), Q(5, 2), Q(6, 5)
        _, _, numerator, denominator = compiler.weighted_coefficients(p, q, A, B0, beta)
        for G in range(0, 10):
            falling = [prod(range(G-j+1, G+1)) for j in range(p+1)]
            lhs = sum(comb(G+1, k)*q**k*(1-q)**(G+1-k)*(A+k)**p
                      for k in range(G+2))
            self.assertEqual(lhs, sum(x*y for x, y in zip(numerator, falling)))
            self.assertEqual((B0+beta*G)**p,
                             sum(x*y for x, y in zip(denominator, falling)))
        # Dropping the final paid round (G rather thanG+1) is false atG0.
        self.assertNotEqual(numerator[0], A**p)

    def test_target_credit_is_invalid_for_paid_log_mean(self):
        J, L, K, t = 4, 25, 1, Q(1, 2)
        paid = E.moment(Counter(exact_splits(L-K, J)), t)
        net = E.sub(E.add(E.power(K, t), paid), E.power(L, t))
        self.assertGreater(paid[0], net[1])
        # Every completion piece here has rankJ. Its full paid moment,
        # rather than the smaller net tax, multiplies lnJ exactly.
        literal_log = E.scale(E.log_bounds(J), 12)
        wrong_log = E.mul(net, E.log_bounds(J))
        self.assertGreater(literal_log[0], wrong_log[1])

    def test_bell_coefficients_against_independent_newton_differences(self):
        p, A, B0, beta = 7, Q(4, 5), Q(5, 2), Q(6, 5)
        law = {Q(0): Q(1, 4), Q(1, 2): Q(1, 2), Q(1): Q(1, 4)}
        moments = [sum(weight*x**i for x, weight in law.items()) for i in range(p+1)]
        _, _, numerator, _ = compiler.moment_coefficients(p, moments, A, B0, beta)
        distribution = {Q(0): Q(1)}
        values = []
        for G in range(p+1):
            changed = Counter()
            for x, a in distribution.items():
                for y, b in law.items():
                    changed[x+y] += a*b
            distribution = changed
            values.append(sum(weight*(A+x)**p for x, weight in distribution.items()))
        newton = []
        while values:
            newton.append(values[0]/factorial(len(newton)))
            values = [b-a for a, b in zip(values, values[1:])]
        self.assertEqual(numerator, newton)
        # Bernoulli moments reduce exactly to the earlier weighted theorem.
        q = Q(3, 5)
        self.assertEqual(compiler.moment_coefficients(p, [Q(1)]+[q]*p, A, B0, beta),
                         compiler.weighted_coefficients(p, q, A, B0, beta))

    def test_concentration_and_capped_mass_perturbation(self):
        v, rho, raw_mean, epsilon = 3, Q(3, 2), Q(3, 4), Q(1, 10)
        p = 9
        bounds = compiler.concentrated_moments(p, v, raw_mean, rho, epsilon)
        for i in range(1, p+1):
            capped = sum(Q(comb(v, k), 2**v)*min(Q(1), rho*k/v)**i
                         for k in range(v+1))
            for actual_excess in (Q(0), epsilon/2, epsilon):
                final = (capped+actual_excess)/(1+actual_excess)
                self.assertLessEqual(final, bounds[i])
                self.assertLessEqual(bounds[i], 1)


if __name__ == '__main__':
    unittest.main()
