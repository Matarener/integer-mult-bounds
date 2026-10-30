# Exact observed coupled bills

This package proves a scoped mathematical result with exact finite
corroboration. For a nonnegative rational recurrence, the specified scalar
bill can converge even when the full coupling matrix fails contraction.
It suffices, and is necessary, to test the vertices on a path from the
forcing to an observed cost.

For A>=0, b>=0, c>=0, let H contain exactly those vertices and set
B=A[H,H], beta=b[H], gamma=c[H], r=|H|. The result is

```text
sum c^T A^k b is finite
  iff H is empty or B admits positive strict contraction weights.

otherwise an exact rational observable witness gives, for every N>=0,
  sum_(k<N) c^T A^k b >= floor(N/r) h, with h>0.

An r-cycle attains equality at every N. The universal window r is sharp.
```

[PROOF.md](PROOF.md) gives the path reduction, constructive alternatives,
exact finite total, geometric tail bound and sharpness proof.
[model.py](model.py) implements a bounded reference producer and separate
checker. The checker uses graph closure and matrix-vector identities, with
no linear solve or elimination.

## Relation to the predecessor

Ali Romman's [PR #5785](https://github.com/CrocSwap/integer-mult-bounds/pull/5785),
head `c047cb85ff5957f09afdcad3a8b16b637fbb5380`, provides the whole-matrix
M-matrix alternative and states the forcing/reachability gap. This package
extends that boundary to a specified observed bill and supplies a positive
finite-depth divergence certificate when the obstruction is applicable.
It does not recheck the predecessor's fixture, implementation or counts.
The proof includes the classical alternative so replay has no unmerged Git
dependency. The predecessor link is a scholarly citation, not a runtime input.

The source question is the forcing/reachability gap in #5785. Classical
M-matrix and nonnegative matrix theory retain their mathematical credit.
The application and certificate contract here do not claim a new
Perron-Frobenius theorem.

## Reproduce

From the repository root, run

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/observable-forced-recurrence/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/observable-forced-recurrence
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/observable-forced-recurrence --check-source-history
```

The verifier prints a generated JSON receipt bound to every package file's
SHA-256. Redirect it outside the checkout if retaining it. CPython 3.12 and
the standard library suffice. The registered normal and optimized commands
perform the same checks; no network, predecessor code or external solver is used.

The exact census covers all 4,096 two-type cases with matrix entries in
{0,1/2,1,2} and binary forcing/output vectors, and all 32,768 three-type cases
with binary matrices and binary forcing/output vectors. A separate
permutation-determinant oracle checks the principal-minor criterion, and
Cramer's rule independently checks every finite total. Additional fixtures
check hidden unstable components, exact tails, divergence bounds and critical
cycle sharpness. Forged-certificate and input-boundary controls remain active
under optimized execution. The receipt reports the enumerated outcomes.
Every census case also compares the first seven literal full-matrix terms
with the restricted terms and checks the corresponding prefix bound.

## Scope and limitations

The written proof holds in every finite dimension. The reference code accepts
one to eight types and nonnegative rational input parts of at most 16 bits.
It is a reference certificate implementation, not a complexity or performance
claim. Its exact finite census corroborates the proof; it does not substitute
for the quantified argument. Independent human and formal proof-kernel review
are unclaimed.

No complete source recurrence has been bound, and no supplier, native action,
compiler, restoration, stock, precision, tape or outer theorem is admitted.
An unstable upper-bound matrix cannot by itself disprove an actual caller.
No new kappa or selected-frontier change is claimed.

The task's generic baseline binding control passed at canonical main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
This is an explicit change from the decoder card's physical itinerary to an
analytical budget lemma. It can prevent an invalid negative inference from
an irrelevant unstable block and can certify an actual observed divergence.
Binding every real child, adapter and restoration cost is still required.

## Open next questions

1. Bind one complete source recurrence, its forcing and every genuinely billed
   output to this criterion. Begin with a declared type graph and justify
   each nonnegative coefficient and cost. Missing source/cost bounds are the
   blocker; an abstract passing certificate is not a supplier result.
2. For a divergent observed bill, determine its exact polynomial or exponential
   growth rather than the universal linear lower bound. Begin with a chain
   of critical strongly connected components. No such growth classification
   is proved here.

## Implementation bounds

All matrix loops have the explicit eight-type bound. The exhaustive verifier
fixes dimensions two and three. There is no recursion, dynamic evaluation,
network access or subprocess creation. Functions stay below 60 physical lines.
Checks use explicit exceptions so optimization does not remove them.

Power-of-Ten rule 3 has a managed-runtime deviation: Python allocates Fraction
and container objects during arithmetic. The scope is this finite reference
replay. Enforced type/input bounds and fixed census grids bound live state;
no census history is retained. The checker caps certificate vector parts at
8,192 bits. Static inspection and both registered replays check these controls.
A fixed-capacity arithmetic backend is a follow-up only if this becomes a
production implementation. Rule 9's test callbacks have exactly one of the
16 explicit rejection calls as their target and do not escape the verifier.
The registered warning-as-error runs supply the interpreted diagnostics.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.

The question and whole-matrix alternative come from Ali Romman #5785.
The classical M-matrix, nonnegative-matrix, path-expansion and Cramer's-rule
ingredients retain their prior mathematical credit. #5785's historical fixture
credits Nick Petalas, Ali Romman, David Ganz / Dugongue, Jose Manuel and their
retained predecessor lineage; that fixture is not an input to this package.
