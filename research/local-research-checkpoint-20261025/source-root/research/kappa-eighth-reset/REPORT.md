# First mechanism reassessment at κ = 2^-8

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

Follow-up: the [shared-source design pass](SHARED-SOURCE.md) tests static
caches, one encoded pair, and the first four-source central cancellation.
None supplies a target-strength construction under its stated contract.

**No new supplier or multiplication exponent.** The active milestone is
κ=1/256. This bounded pass revisits two previously budget-rejected mechanisms.
Neither earns a construction run under its stated implementation model.
The retired 40-call inventory and its repair campaign remain retired.

The useful distinction is that the fractional-cycle tensor still fails an
optimistic budget, whereas the small folded-cube code now passes that first
screen but fails when source access is charged. The second rejection covers
overcomplete scalar factorizations as well as rank-minimal ones, for the
specific labels and copied-source contract tested here.

## Target and decision rule

The [budget](budget.json), reproduced by `budget.py`, uses coarse bit and
complex savings 9/2000, admitted bit saving 21/5000, and κ=1/256. It includes
the retained bit stopping wrapper. All displayed assembly inequalities
pass with assumed valid suppliers and finite bridge; those assumptions are
not supplied by this diagnostic. No extension of the 1/32 admission guard
is needed at this point.

Only failures depending on the old, larger target are candidates for
reconsideration. Algebraic incompatibility, rank-capacity exhaustion and
uniform-word obstructions do not disappear at a smaller saving. This pass
does not reopen the sunflower packets, matched encoders, common-frame
terminal decoder, coordinate-Fourier replacement, or retired inventory.

## Candidate 1: the existing fractional-cycle tensor

The [higher-rank diagnostic](../higher-rank-sixteenth/REPORT.md) already
constructed compatible rank-five rational labels in dimension 110 from
the ten-point triple core and an eleven-cycle. Its proposed two-axis
compiler has ambient width 110². Grant zero auxiliary roles, zero central
loss and ideal batching within all retained data macros.

At saving **1/256**, its exact normalized moment lies near

`1.00039349214631 > 1`.

This exponent is below even the necessary admitted saving 1/255, so the
failure cannot be fixed just by tightening the illustrative 0.0045 budget.
Every additional role under this ledger contributes a moment greater than
one; adding those roles to an already failing normalized bill cannot help.

**Decision:** do not reopen this tensor under the specified two-axis
compiler. A different cover or data path is a different proposal, not
excluded by this screen. The arithmetic does not reject every fractional
block representation.

## Candidate 2: folded five-cube with explicit rational labels

Take the 16 vertices x in F2^4, adjacent when their difference is one of
`1,2,4,8,15` in bit-mask notation. Let the binary scalar matrix be
`C=I+Adj`. Exact elimination gives rank_F2(C)=6 and rank_Q(C)=16.
This is the q=5 member of the
[previous folded-cube family](../interaction-family-design/REPORT.md).

For an explicit address geometry, form the rational Gram matrix G with
diagonal 2, entries zero on graph edges, and entries one on distinct
nonadjacent pairs. Its rational rank is six. Select principal indices
`0,1,2,3,4,8`; their Gram block is invertible. Let u_j be column j
restricted to those rows and H the inverse principal block. Exact checking
gives

`u_i^T H u_j = G_ij`.

Thus `P_j = u_j (u_j^T H)/2` are rational rank-one idempotents in dimension
six, and adjacent projectors annihilate. They are not all commuting. Every
projector identity and required annihilation is checked directly.

This supplies a scalar code and compatible labels. It does not supply
a complete reversible network or a complex counterpart.

### The initial budget now passes

Use the retained shared-cover accounting, with v=16, d=6, r=1. A
conservative central factorization needs at least six channels. If one
charges each channel only the generic rank-one minimum, the optimistic
ledger has R=6, L=6 and a raw moment at saving 0.0045 of

`0.98543158128130 < 1`.

This is why this candidate merits a source-access check at the new target.
It was not reasonable to promote the old 0.08 rejection to an all-saving
obstruction.

### Actual source access consumes the putative gain

Consider any binary scalar factorization C=AB with K nonzero central
channels. K>=6 follows from rank(C)=6. If B has support S_j on channel j,
the retained conservative producer assembles those sources at a frame
containing all their label images and copies the channel out. Its loss is
at least

`L >= sum_j rank_Q{u_i : i in S_j}`.

Every one of the 16 source indices must occur in some S_j, since C has
nonzero diagonal. These conditions allow arbitrary factors, cancellation
in the final scalar product, and K greater than six. They do not cover
producers that change source frames during collection, perform additional
intermediate recoding, or share production/readout across this contract.

For these particular rational labels, the maximum number of distinct
source labels that can lie in a rank-t subspace is:

| t | 1 | 2 | 3 | 4 | 5 | 6 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Maximum source support | 1 | 2 | 4 | 6 | 10 | 16 |

The finite certificate establishes the upper bounds by reduction modulo
101. It enumerates all 6,885 subsets of at most five labels and counts the
labels in each generated modular span. Any rational support of rank at
most five lies in one of these modular spans. Rational rank checks on
attaining supports show that each bound is attained over Q too. The
finite-field step therefore certifies rational upper bounds; it is not
used as an unverified substitute for rational dependence.

Suppose total span cost were at most ten. With at least six nonempty
channels, no channel could have rank six. For 1<=t<=5 the table satisfies

`support(t) <= (9t-5)/4`.

Consequently the sum of all source-support sizes would be at most

`(9L-5K)/4 <= (90-30)/4 = 15`.

That cannot cover 16 inputs, even before allowing for overlaps. Therefore
**L>=11**. An independent enumeration of rank-cost partitions at budget
ten and K>=6 also gives maximum total support 15.

The shared-cover rank deficit is `2vr-3L`. Even granting minimum data paths
and no other loss, it is now at most

`32-33 = -1`.

Thus this geometry with this copied-source compiler cannot produce a
positive rank deficit, let alone the desired exponent. Changing auxiliary
stock does not repair a nonpositive deficit under the same complete bill.

### The target-specific missing cost

At minimum stock R=6, the optimistic 0.0045 moment passes with L=9 but
fails with L=10. Extra roles with the retained cost also cannot rescue
the failing L=10 relaxation. Thus the target permits at most nine integer
loss units in this favorable model, while the source-coverage proof
requires at least eleven. The lower bound eleven is not an implementation
known to attain eleven; an actual compiler may cost more.

**Decision:** no scalar-factor search or frame-scheduling search under
this source-copy contract. Merely allowing more central channels does not
evade the rejection. A different label geometry or paid producer mechanism
would need a fresh admission test.

## What to carry forward

The smaller target does make the initial numerical budget less demanding.
For the two concrete candidates tested here, it does not supply a legal
implementation. The next mechanism should address how information enters
and leaves the computation, with those costs included from the outset.

The useful next design question is an explicit operation that changes the
conservative source-collection/readout contract or recursive boundary.
It must name the operation removed, price its replacement, and preserve
arbitrary inputs and the required final restoration. A stronger rank gap
in an abstract scalar matrix is insufficient evidence to fund another
construction search. Earlier closed common-frame and matched-encoder
proposals remain closed; no concrete replacement is selected by this pass.

This is the endpoint of the agreed two-candidate reassessment, not an
automatic continuation to a wider graph, label, or solver search. No
complex supplier, finite bridge, uniform recursion, or new κ is claimed.

## Reproduction

```sh
python3 -B research/kappa-eighth-reset/budget.py
python3 -B research/kappa-eighth-reset/reprice.py
```

The checker uses Python's standard library and the existing exact rational
power enclosure code. It verifies the matrix identities, scalar ranks,
all required label annihilations, modular span bounds with rational
witnesses, coverage arithmetic, and target moments. Bounds are checked
with exact arithmetic; decimals are display aids. The source hashes are
recorded in `repricing.json`. This is a written scoped proof and finite
audit, not a Lean formalization or a verification of the multiplication
theorem.
