# A sharp full-precision prefix cutoff for Gaussian Newton residuals

This scoped proof concerns the literal valuation-pruned Walsh gather in
[Ali Romman's PR #5825](https://github.com/CrocSwap/integer-mult-bounds/pull/5825),
at `baea91d8c0044a0036006bdd3b4d7bce3d6cf783`. That package states the
degree-zero prefix obstruction. The new step here covers every positive
degree, identifies the exact uniform cutoff and needs no assumption on the
bulk's precision or cost. The construction and creation-precision contract
come from David Ganz / Dugongue's #5815 and #5813, as cited by #5825.
Their implementations and numerical results are not replayed here.

## Contract and theorem

Let pi = 1+i, n >= 1, N = 2^n, 0 <= R < n, 0 <= a <= n-R and p >= 0.
The exponent p is an integer. Use the integer-valued generalized binomial
polynomials, including at negative arguments, and put

```text
g(j) = i^a sum_{h=0}^R (i-1)^h binom(j-a,h),
d_j = i^j - g(j),
e_j = d_j / pi^(R+1),
Q   = p+2n-R-1.
```

The source's Newton residual theorem supplies the integral e_j. Lemma 1
below also proves that integrality directly. A Walsh leaf lambda has weight
j and beta_lambda = v_pi(e_j), with v_pi(0) = infinity. Its prescribed
creation demand is q_lambda = max(0,Q-beta_lambda). An absent leaf has
demand zero. Every prefix must be created with at least the largest demand
of its descendants. This is the named max-descendant precision contract,
not a lower bound for every circuit computing the same operator.

For a nonempty prefix v at depth d, its literal child-array ADD incidence
mass is 2^(n-d) q_v. Thus the gather ADD precision mass is at least

```text
M >= 2^n (n-R-1) (p+2n-R-1).                         (1)
```

More precisely, **every prefix at every depth 1 <= d <= n-R-1 must have
q_v >= Q**. At depth n-R there is a prefix with demand exactly zero, for
every permitted a. Consequently n-R-1 is the exact last depth through
which every prefix is uniformly forced to Q. When n-R-1 = 0, the assertion
about nonempty forced levels and the lower bound are empty, as they should be.
The root still has demand Q whenever Q > 0.

The result is independent of the fixed order of the axes. A prefix of
weight w always has possible completion weights w,w+1,...,w+n-d, regardless
of that order. A node-dependent axis order that still fixes one fresh axis
at each step has the same property and the same full binary tree counts.

## Lemma 1: the first surviving digit

For every integer t and every R >= 0,

```text
i^t - sum_{h=0}^R (i-1)^h binom(t,h)
  = (i-1)^(R+1) binom(t,R+1) mod pi^(R+2).            (2)
```

For t >= 0, this is the ordinary binomial expansion with terms of higher
degree omitted. For t < 0, work in Z[i]/(pi^(R+2)). The element u=i-1=i*pi
is nilpotent there. The finite geometric series gives the inverse of 1+u.
Raising that inverse to the positive integer -t gives the generalized
binomial expansion through degree R+1. Equivalently, the identity holds
in Z[[u]] for every integer power of 1+u, and substitution of the nilpotent
u removes every term of degree at least R+2. This justifies negative
offsets without an analytic convergence premise.

All terms omitted after degree R are divisible by pi^(R+1), so e_j is
integral. Dividing (2) by pi^(R+1), and multiplying by i^a, gives

```text
e_j = i^(a+R+1) binom(j-a,R+1) mod pi.
```

The residue field Z[i]/(pi) is F2, and every power of i maps to one.
Therefore

```text
v_pi(e_j) = 0  iff  binom(j-a,R+1) is odd.           (3)
```

This is an exact criterion. It does not estimate higher valuations.

## Lemma 2: no long gap in odd generalized binomials

Fix k >= 1. The kth forward difference of binom(t,k) is one. In integer
form, for every t in Z,

```text
sum_{r=0}^k (-1)^(k-r) binom(k,r) binom(t+r,k) = 1. (4)
```

Pascal's identity gives Delta binom(t,k) = binom(t,k-1) for every integer t.
Applying it k times proves (4). If every binom(t+r,k) in this window were
even, its left side would be even, a contradiction. Thus **every k+1
consecutive integer arguments contain an odd value**. The run of k zeros
at t=0,...,k-1 shows that this window length is sharp.

For a prefix at depth d <= n-R-1, the unprocessed count m=n-d is at least
R+1. Its completion weights contain at least R+2 consecutive values.
Apply Lemma 2 with k=R+1 and t=w-a. Lemma 1 supplies a descendant with
beta=0, hence creation demand Q. This proves the forced-level assertion.

At each such depth, there are 2^d prefixes. Each has child-array length
2^(n-d), so that depth alone contributes at least NQ. Summing the
n-R-1 nonempty forced levels proves (1). A schedule that overallocates
precision can only increase this lower bound.

## Sharp cutoff

At depth d=n-R choose any prefix of weight a; this is possible because
0 <= a <= d. Its completion weights are exactly a,a+1,...,a+R. For
0 <= t <= R, the binomial expansion terminates by degree R, so d_(a+t)=0.
Every descendant is absent and this prefix's minimum demand is zero.
This proves sharpness of the full-precision depth, not attainment of the
total mass lower bound (1). Later nonzero prefixes may add substantial mass.

## Exact full-precision counts at later levels

The same first-digit criterion supplies an independent finite check of every
later prefix. Set k=R+1 and L=2^s, where s is the bit length of k. For every
integer t,

```text
binom(t,k) is odd iff ((t mod L) AND k) = k.          (5)
```

In F2[z]/(z^(k+1)), the identity (1+z)^L=1 holds because L>k.
Thus the coefficient of z^k in (1+z)^t depends only on t mod L, also for
negative t. Expanding a nonnegative residue in binary gives a product of
factors 1+z^(2^b). The z^k coefficient is one exactly when every set bit of
k is available in that residue. This proves (5) without assuming a
nonnegative offset.

At depth d with m=n-d, the exact number of minimum-demand prefixes at Q is

```text
F_d = sum_{w=0}^d binom(d,w)
      * 1{ there exists u in {0,...,m} with
            (((w+u-a) mod L) AND k) = k }.           (6)
```

For Q>0, beta=0 is exactly the condition q_lambda=Q, so (6) counts
full-precision prefixes, rather than merely live prefixes. This formula
is used only as corroboration and a reusable exact count; it does not
claim that all live coefficients have valuation zero.

## A low-degree obstruction even with a free bulk

For n >= 4 and 1 <= R <= floor(n/2)-1, the forced-level count is at least
n/2 and Q >= p+n. Hence the residual gather alone satisfies

```text
M >= (n/2) 2^n (p+n).                               (7)
```

At p=Theta(n) this is Omega(2^n n^2) ADD precision mass, even if the bulk
and every other operation are free. More generally, n-R-1 >= epsilon*n
gives the same conclusion for fixed positive epsilon. This strengthens
the applicable low-degree part of #5825's cost obstruction by dropping
its uniform-bulk-precision premise. It makes no statement about the
high-degree heterogeneous bulk or the cost of a different residual graph.

The metered ADD precision model is not by itself a physical bit-time
theorem. Changes to the graph, arithmetic representation, divisibility
handling, normalization, or creation-demand contract can evade this
obstruction. No bound on arbitrary Gaussian algorithms, shared responses,
native suppliers or finite networks follows. All five selected framework
assumptions remain open at their existing scope. No new kappa is claimed.

## Evidence and credit

The proof above is the all-size argument. The standalone verifier constructs
Gaussian residual coefficients from their falling-factorial definition,
performs every division exactly and compares the first surviving digit with
(5). Its positive-degree census checks all offsets, including negative
j-a. It separately checks (4), enumerates every binary prefix in its tree
domain, compares (6), checks (1) and (7), and constructs the sharp zero
prefix. Eight underprecision profiles must be rejected. Finite checks
corroborate the proof; they are not formal proof-kernel acceptance.

This contribution was produced by Nick Petalas. Credit Ali Romman #5825
for the degree-zero obstruction and explicit metered graph, David Ganz /
Dugongue #5815 for the valuation-pruned residual and #5813 for its Gaussian
spectral predecessor. Their retained native, precision, ownership and
compiler contributors keep their predecessor credit. Generalized binomial
identities, finite differences and binary coefficient parity are classical
facts. No novelty is claimed for those facts separately.
