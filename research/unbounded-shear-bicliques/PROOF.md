# Unbounded bipartite contacts in fixed rational shear dimension

This scoped construction and proof were produced by Nick Petalas.

## Statement

For a rational 2-by-2 matrix M, put

```text
Phi(M) = [[I_2, M], [0, I_2]],
d(Phi(M), Phi(N)) = rank_Q(Phi(N) - Phi(M)) = rank_Q(N-M).
```

For arbitrary finite sets T,A of distinct rational parameters within each set,
define

```text
E(t) = [[t, t^2], [1,  t]],   t in T,
O(a) = [[a, a^2], [0, -a]],   a in A.
```

The metric on their |T|+|A| shear operators is the shortest-path metric of
the complete bipartite graph K_(|T|,|A|), provided both sets are nonempty.
Every cross distance is one and every distinct same-part distance is two.
The two sets of operators are disjoint even if T and A overlap.

In particular, K_(n,n) occurs in 4-by-4 commuting integral shear operators
for every positive integer n. For T=A={0,...,n-1}, all matrix entries,
including those of the inverse shears, have magnitude at most
max(1,(n-1)^2). Matrix dimension stays fixed, but coefficient storage does not.

## Proof of the new realization

Direct subtraction gives the nonzero rank-one factorization

```text
E(t)-O(a) = [[t-a, (t-a)(t+a)], [1, t+a]]
          = column(t-a, 1) row(1, t+a).
```

The entry in position (2,1) is always one. Thus the difference has rank
exactly one, including when t=a. In particular, the two label families
never meet.

Within each family,

```text
det(E(t)-E(s)) =  (t-s)^2,
det(O(a)-O(b)) = -(a-b)^2.
```

Distinct rational parameters make these determinants nonzero. Therefore
the rank is two within either part and one across the parts. These are
exactly the graph distances of a nonempty complete bipartite graph.

Block multiplication gives

```text
Phi(M) Phi(N) = Phi(M+N) = Phi(N) Phi(M),
Phi(M)^(-1) = Phi(-M).
```

The nonzero block of Phi(N)-Phi(M) is N-M, so its rank is unchanged.
This transfers every label distance to the stated operator distance.
Choosing integer parameters from zero to n-1 proves the integral and
coefficient-height assertions. This argument proves the statement for all
n; finite fixtures are corroboration rather than an extrapolation. QED.

## Consequence using the predecessor's distortion theorem

For a metric d, let c_1(d) be the least D for which an L1 metric rho can
be rescaled to satisfy d <= rho <= D d. Jerry Chen / CubeJerry's
[PR907](https://github.com/CrocSwap/integer-mult-bounds/pull/907), section
"All-size family and sharp distortion", proves

```text
c_1(K_(n,n)) = 2(n-1)/n,   n >= 2.
```

That abstract theorem is cited as a predecessor result. Its cut argument
and finite examples are not replayed or claimed as new here. Applying it
to the new realization proves that the actual rational shear rank metric
in fixed operator dimension four has finite subsets with distortion
arbitrarily close to two. This replaces a fixed eight-frame witness with
an unbounded family of actual frames.

There is also an exact countably infinite example. Take both parameter
sets to be the nonnegative integers. Every finite balanced restriction has
the distortion just cited, so the whole metric has distortion at least
two. Sending every operator to a different unit vector of countable l1
gives distance two on all distinct pairs. Since the original distances
are one or two, this embedding has distortion at most two. Hence the
countably infinite example has distortion exactly two.

## Scope

The rank charge is the declared metric. This proof gives no cheaper
network, changed free operation, nonlinear gate, involutive translation,
native Clifford realization, productive target, or recursive saving.
The shear group is abelian and upper triangular. The separate common-flag
obstruction of navinor's PR825 and the signed-potential restrictions of
Jeremy Diviney's PR836 remain applicable under their own hypotheses.
In particular, failure of an L1 metric premise does not imply a coding gain.

The inherited multiplication framework, exact caller costs, dirty
restoration, compiler closure, precision and tape implementation are
outside this statement. No selected-frontier change or complete
multiplication theorem is claimed. Literature priority for these elementary
matrix identities is unclaimed.
