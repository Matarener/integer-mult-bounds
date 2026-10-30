# Exact all-role right-vector cost for small local products

Scoped algebraic proof with finite corroboration. No new kappa.

Let K=F_q and R=R_1 x ... x R_k, where 1<=k<=q and each R_i is an
associative central local K-algebra. Its nonunits must form a proper
two-sided ideal. For every n>=1 and every invertible M in M_n(R),

```text
cost_R(M) = delta_R(M) = rank_K(pi M|_{K^n}) <= n,
delta_R(M) = min_{T in GL_n(K)} dim_K((MT-I)K^n),
pi : R^n -> (R/K)^n.
```

K embeds diagonally in R. A paid factor is I+u y^T with u in R^n and
y in K^n. Arbitrary common GL_n(K) maps are free anywhere. No extra role
is used. The residue division algebras may differ from K and may be
noncommutative. No finite-dimensionality or nilpotence assumption is needed.

[PROOF.md](PROOF.md) gives the universal statement and attaining words.
It answers the arbitrary-role product question explicitly left open by
Nick Petalas #4787. ToikY #4334 and Nick Petalas #4601 already prove the
two-role small-product case. The new step chooses a common scalar pivot
at every Schur complement. Each component forbids a proper scalar
subspace; at most q such subspaces cannot cover the scalar row space.
This gives one common full pivot flag, followed by exactly delta column
replacements. Classical finite-vector-space counting and elimination
retain their ordinary mathematical credit.

The component hypothesis cannot be removed from an all-role theorem:
the cited two-role predecessors already give k=q+1 examples with cost
three and delta two. That is predecessor credit, not a new certificate
in this package. Necessity for individual higher-role targets is open.

## Finite evidence

The standard-library verifier imports no predecessor code. It constructs
literal common-chart words and checks their full matrix products on all
28,224 invertible three-role targets over F2 x F2. Its exact paid-cost
histogram, in cost order zero through three, is

```text
[168, 3528, 16464, 8064].
```

A separate bit-matrix implementation enumerates GL3(F2). It normalizes a
pair (A,B) by its free left map to (I,A^(-1)B). Literal paid pairs with a
common right vector give 22 distinct normalized generators, including the
identity. BFS covers all 168 normalized states. Its labels satisfy all
3,696 paid edges and 28,224 free-conjugation edges, so they certify the
actual normalized alphabet metric. Every constructor length agrees.
Left normalization transports its witnesses to all 28,224 ordered pairs.
All 1,008 base-field basis-data actions on the 168 normalized words pass.

The verifier also checks 431 distinct bounded examples on three and four
roles over (F2[e]/e^2)^2, F3^3 and (F3[e]/e^2)^3. These are samples, not
complete target censuses. They exercise every active dimension from zero
through the role count. All 6,644 basis-data actions and 18,200 literal
scalar-subspace input checks pass. The latter independently enumerate E
and check |E|=p^(n-d), rather than using the constructor's row reduction.

Eight rejection controls cover missing factors, reversal, changed
coefficients, componentwise free maps, singular targets, too many
components, nonunit inversion and an illegal paid right-vector shape.
Two additional boundary fixtures require a non-coordinate common pivot
and demonstrate the covering failure at q+1 scalar hyperplanes. Checks
use explicit exceptions and remain active under optimized Python.
The verifier writes nothing and emits a generated receipt bound to all
six package files. No receipt is handwritten or committed.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-small-local-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-small-local-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-small-local-products
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-small-local-products --check-source-history
```

Any CPython 3.12 installation may replace the local path. Expected marker:

```text
PASS_RIGHT_VECTOR_SMALL_LOCAL_PRODUCTS binary_pairs=28224 sampled_targets=431 controls=8 no_new_kappa
```

Both registered commands have 120-second limits and run the same complete
checks. SOURCES.json pins predecessor documents to canonical base
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. They are cited dependencies,
not audited deliverables. The original card is explicitly changed to this
algebraic side result in TASK.json. Its selected-baseline first command
passed after sparse inputs were materialized; it is source-binding
orientation only. No selected operator replay was run.

## Limits and implementation discipline

The all-q, all-n result is the written proof. Software corroboration uses
base fields F2 and F3, the complete binary pair domain, and the stated
three-/four-role samples. It does not enumerate extension base fields or
noncommutative local products. Singular targets, more than q components
at n>=3 and matrix blocks in a semilocal quotient are not classified.
Native coefficient preparation, frames, routing, restoration, precision,
stock and a full supplier bill remain unknown. No supplier admission,
selected-frontier change or complete multiplication theorem is claimed.
Independent human and formal proof-kernel review are unclaimed. Lean,
Docker and the selected construction's cold replay are outside scope.

The verifier has no recursion or subprocesses. Matrices have at most four
roles; local coefficient tables have at most nine elements; products have
at most three components. Scalar row searches and literal scalar inputs
have at most 3^4=81 candidates. The binary group has 168 states, its BFS
has exactly 168 iterations, and the complete pair loop has 168^2 cases.
Each sampler generates at most 80 candidates and stores at most 80 target
matrices. All functions fit within 60 lines. Python requires dynamic
allocation, a managed-runtime deviation bounded by these fixed domains.
Eight fixed negative-control callbacks are bounded local dispatch.
Warning-strict normal/optimized replay and in-memory source compilation
supply the available Python diagnostics. No shared configuration changes.

## Open next questions

1. For n>=3 and more than q components, determine which common scalar
   flags still attain delta. Start with a three-component binary
   three-role target. The present subspace count ceases to guarantee a
   row, so an individual flag criterion is needed.
2. Specify one native producer/consumer for a column replacement and
   price coefficient preparation, access, frames, restoration, precision
   and stock before implementing a supplier. Those costs are unknown.

## Credit

This contribution was produced by Nick Petalas. Credit Nick Petalas #4787
for the local arbitrary-role theorem, chart reduction and open product
question; #4601 for the two-role local-product extension; ToikY #4334 for
the field-product threshold; and Nick Petalas #4243 and Wentao Li #4099,
following #2513, for the alphabet, normal form and column lower bound.
The exact source documents and predecessor attribution are unchanged.
Apache-2.0.
