# Sharp synchronized mixed-rank invoice envelopes

Let m be a positive even integer, let a_1,...,a_m be integers greater than
one, let p,q be integers with 0<p<q, and let lambda>0 and epsilon>=0 be real.
Define

```text
D(t) = epsilon + lambda product_(i=1)^m (a_i^(q t) - a_i^p).
```

Then D has global minimum epsilon on the whole real line. Its unique minimizer
is t=p/q, which lies inside (0,1). If epsilon=0, its only real zero has exactly
m-fold multiplicity. If epsilon>0, D is strictly positive everywhere.

## Proof

Each factor is strictly increasing. It vanishes exactly at p/q, is negative
below p/q, and is positive above p/q. All m factors therefore have the same
nonzero sign away from p/q. Their product is positive because m is even.
At p/q the product vanishes. Positivity of lambda proves both the minimum
and its unique location.

The derivative of the i-th factor at p/q is
q log(a_i) a_i^p>0. Its zero is simple. The product of m analytic functions
with simple zeros at the same point has a zero of exact multiplicity m.
Adding a positive epsilon removes all zeros, while leaving the minimizer
and the sharp lower envelope unchanged. This proves every claim.

## Exact signed invoices

Suppose lambda and epsilon are nonnegative integers, with lambda positive.
Expansion gives

```text
D(t) = epsilon + lambda sum_(S subset {1,...,m})
          (-1)^(m-|S|) (product_(i not in S) a_i^p)
                         (product_(i in S) a_i^q)^t.
```

All ranks and signed coefficients are integers. Equal subset products must be
combined before comparison. No independence or distinctness of the bases is
assumed. Put positive coefficients into the new paid histogram and negated
negative coefficients into the old paid histogram. This realizes the signed
difference as two nonnegative integer invoices. More generally, the checker
accepts any placement in paid and target histograms whose full net difference
is this polynomial. Identical arbitrary paid and target charges on both sides
cancel. This is arithmetic realization, not a physical construction.

For rational positive lambda and nonnegative epsilon, clearing their common
denominator gives the same integer-certificate form with the correspondingly
scaled envelope. The executable accepts the integer form only.

## First mixed-rank example

For m=2, a_1=2, a_2=3, p=1 and q=2,

```text
6 - 3*4^t - 2*9^t + 36^t = (4^t-2)(9^t-3) >= 0.
```

Equality holds only at t=1/2 and has exact multiplicity two. Thus the seven-job
invoice 6 H1 + H36 costs at least the five-job invoice 3 H4 + 2 H9 for every
power tariff, with equality at sqrt-rank pricing. Adding one H1 to the former
gives sharp minimum gap one for every real t. Swapping the invoices reverses
the ordering, but is not claimed to implement a cheaper physical circuit.

The ranks 4 and 9 are not powers of a common integer greater than one, since
that integer would have a prime divisor dividing both ranks. This supplies a
genuinely mixed-rank example. There are two coefficient sign changes, and
neither endpoint is zero. A closure rule using simple interior witnesses alone
cannot spend a two-root budget on this double zero. The factor certificate
supplies its multiplicity directly. This is an implication from the documented
certificate rules in #5788, not a replay or audit of its implementation.

With two distinct prime bases a,b, arbitrary 0<p<q, and offset epsilon, the
four coefficients are epsilon+a^p b^p, -b^p, -a^p, and 1 at ranks
1,a^q,b^q,(ab)^q. This gives an infinite family with the same sharp envelope.

## Checker soundness and scope

`envelope.py` parses both complete invoice histograms and identical declared
contracts. It forms new-paid minus new-targets minus old-paid plus old-targets.
It separately expands the supplied factors by repeated sparse multiplication,
combines collisions, and requires exact coefficient equality. The theorem then
justifies its reported envelope, minimizer and zero multiplicity. A matching
contract string does not establish that either invoice describes a circuit.

The verifier has no numeric root search, logarithm approximation or predecessor
executable dependency. `verify.py` corroborates expansion independently by a
literal subset formula, executes exact rational-power checks at exponents whose
denominators divide q, tests target debits, and rejects mutated certificates.
It does not use finite samples as the proof of a continuum claim.

The executable bounds factors to an even count from two through eight, bases
to 2..64, q to 2..16, expanded ranks to 10^9, histogram counts to 10^60,
each histogram to 4096 keys, and each input to one MiB. Sparse multiplication
has at most 256 terms per step; all loops have finite bounds from these
capacities. The mathematical theorem has no such finite capacities. Managed
Python allocation is a Power of Ten deviation, bounded here by input and
support capacities; standard-library parser allocation is not statically
preallocated. The isolated registered normal and optimized runs use the same
explicit checks, which remain active without assertions. No shared modules
or source pins are changed.

## Predecessors and remaining obligations

Ali Romman's [#5788](https://github.com/CrocSwap/integer-mult-bounds/pull/5788)
poses the explicit touching-root continuation and supplies the general-rank
root-budget context. Its proof and limitations are cited, not reverified.
The signed-invoice interface is due to zxv, the moment-order context to
mightyOil and predecessors, and the specialized T16 crossing work to woklerx.
The factor expansion and elementary sign argument are standard algebra and
calculus. The contribution is their exact synchronized-envelope application,
integer invoice family and portable certificate checker; no literature
priority for these elementary methods is claimed.

There is no source-bound physical bill, native implementation, ownership or
restoration proof, compiler admission, new kappa or complete multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.

New work produced by Nick Petalas. Apache-2.0.
