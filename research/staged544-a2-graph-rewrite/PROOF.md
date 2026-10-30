# Consecutive A2 graph rewrites with fixed staged544 boundaries

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Scope and statement

The inputs are the exact `43base` and `43extra` PR3734 BORROW-WORDs at
`fa041037a3374eaa08feeca0b26a5d6893194147`. The domain consists of consecutive
nonzero ADD pairs in A **after** `prelude_events`, B strictly inside the intervals
cut by native warp positions, and restore. A prelude, native warp, or intervening
scalar instruction is not crossed. The two ADDs involve three distinct registers
and form a directed path. Every other event, scalar coefficient, entrance/exit
frame, caller state, role and native map is fixed. This is a change of event graph,
not a retiming of two retained ADDs.

For every such pair, replace it by the reversed pair plus the exact central ADD
below, at each of its three possible positions. Jointly choose **all** common
binary subspaces for the three ADDs, subject to monotone register frames and fixed
neighbouring frames. The output records every compatible flag and separately
reports rejection by exact whole-word boundary checks. Every compatible flag
already has a non-improving recursive invoice for every `0<a<1`; extra scalar
implementation costs cannot turn these into gains. The finite literal inverse
three-to-two motif census contains exactly one block per provider; its unique
legal contracted frame assignment removes one forward and one cleanup ADD,
with the entire paid profile unchanged. No further consecutive inverse motif
remains after this one contraction. This does not rule out nonconsecutive A2
identities, longer graph changes, changed boundaries, or other root systems.

## Exact group identity and sign convention

An ADD `(t,s,c)` updates `x_t <- x_t + c x_s`, so its matrix is
`T_ts(c)=I+c E_ts`. A chronological list `[g,h]` acts as `H G`, not `G H`.
For distinct `i,j,k`, let `g=(i,j,a)`, `h=(j,k,b)`. Then

```
[g,h] = [h,(i,k,-ab),g].
```

Indeed `H G=I+aE_ij+bE_jk`, whereas `G H` also contains `ab E_ik`; the negative
central gate cancels that term. For the opposite chronological orientation,
`g=(j,k,a)`, `h=(i,j,b)`, the central coefficient is `+ab`.
`E_ik` commutes with both simple-root matrices, so the central ADD may occupy
any of the three positions. These equalities are identities over the rational
polynomial ring in `a,b`; they apply to arbitrary initial values in all three
registers, including dirty helpers. The independent control computes all six
register permutations, two orientations and three central positions in that
polynomial ring. Wrong sign, omitted central gate and replacing `ab` by `a+b`
are rejected. Actual source coefficients are separately checked with exact
rational matrices in the production census.

The new root joins two existing registers and allocates no helper or buffer.
It adds one forward scalar ADD. Literal inverse cleanup adds one ADD when the
new target is a non-target register, and zero when the new target is a target.
The latter is legitimate only under the retained hygiene rule that a non-target
never reads a target. All full-word hygiene checks remain enabled.

## Exhaustive framed search

For each of the three touched registers, extract its frame immediately before
its first old event and its first fixed frame after its last old event. Call
these `P_r,Q_r`. Include that successor climb in both local invoices. Thus no
boundary charge is silently removed. Native entry and centre/target cut checks
are fixed checks; allowing a positive successor climb at such a cut is only an
optimistic relaxation, and the full word auditor identifies any such candidate
as inadmissible.

A replacement event touching registers `r,s` must use a common subspace `U`
satisfying

```
current(r) + current(s) <= U <= Q_r intersect Q_s.
```

Enumerate every intermediate binary subspace in this interval, update both
current frames, then recurse to the next event. Every legal flag follows a
unique recursion branch. Conversely, every branch respects the stated local
monotone constraints. The enumerator repeatedly adjoins an ambient vector and
closes its span; every finite-dimensional intermediate subspace is reachable
by adjoining a basis. Deduplication uses its complete point set. A resource
check rejects quotient dimensions above four instead of silently pruning them;
all inspected intervals obey the bound. Independent controls enumerate all
subsets of the nonzero quotient vectors, close them by explicit XOR sets and
compare the resulting subspace collections.

The cost is one rank-`dim(U)-dim(current)` recursive child for every nonzero
climb, plus the complete fixed-successor climbs. Zero climbs cost no child.
All other register climbs cancel. The production verifier nevertheless rebuilds
and prices the **entire** word for each legal flag and checks equality to the
local delta. The independent checker computes the local rank invoice from the
retained auditor's event chains and independently represented point sets.

An initial dimension-only relaxation ignores subspace incidence while retaining
event ordering and dimension bounds. It contains apparently favorable cells.
They are nominations only: none survives exact geometry with a favorable price.
This demonstrates why optimizing rank numbers alone would give a false gain.

For the inverse census, each consecutive triple is considered at each possible
central position. Removing that position leaves the reversed original pair;
its endpoints and rational central coefficient must agree with the derived
identity. Comparing rational values avoids assuming canonical numerator and
denominator encodings. This census finds exactly the A1858 block in each provider, described below.
No search over separated triples is claimed.

## Constructive inverse rewrite

The unique triple at zero-based A index 1858 is, in chronological order,

```
457 <- 457 - 475
456 <- 456 + 457
456 <- 456 + 475
```

All three operations use the common frame span(82,42). It equals

```
456 <- 456 + 457
457 <- 457 - 475
```

at the same frame. The two-register endpoint is `(x456+x457, x457-x475)`;
register475 is unchanged, so arbitrary dirty inputs are preserved exactly.
The exhaustive two-event frame search has exactly this one legal assignment.
Both source providers' complete 723-input ordinary/dual/reverse semantics and
cleanup-boundary checks are replayed for this contracted word. The inverse
cleanup has 5223 events instead of 5224. A has 4078 events instead of 4079.
The paid profile remains `{1:2440,2:725,3:224,4:102,5:20,8:8}`. No helper,
buffer or native map is added or deleted. The replacement occurs after the A
prelude, so every existing native event and B warp index is unchanged.

A second complete scan of the contracted word finds no consecutive literal
inverse A2 motif. This is one fixed-point check, not a claim about every possible
sequence involving expansions or other rewrites. The canonical edited-word and
cleanup digests are retained, together with the exact replacement gates and
source input pins, so the construction is reproducible without storing another
copy of the frozen supplier. This is a concrete scalar simplification with no
recursive-moment or kappa improvement; it is not the PR3863 rank exchange.

The exact same single A1858 contraction is additionally checked on both
PR3945 words at 91f81d131252db704f945891da1ea54e29d46b8b. Their actual source
profiles, full ordinary/dual/reverse dirty semantics before and after, and all
unchanged top-level fields are checked independently. In particular, native
operators and their scalar normalization are byte-identical to their own
PR3945 baselines. The complete expansion census above remains scoped to the
older PR3734 words. No PR3945 graph-wide expansion result is inferred.

## Exact all-exponent sign certificate

Write `[r]` for one rank-`r` child and `p=1-a`, so `0<p<1`. The only signed
profile differences are zero and

```
2[1]-[2],  4[1]-2[2],  [1]+[2]-[3],  3[1]-[3].
```

For positive `x,y`, strict subadditivity gives
`(x+y)^p < x^p+y^p`. Therefore each nonzero difference has strictly positive
moment; zero is an exact tie. Their rank masses are all zero, so a common width
normalization multiplies these inequalities by the same positive factor. This
argument covers the entire open exponent interval, not a floating-point sample.
The source-specific histogram is retained in each RESULT. No unclassified sign
is converted into a negative theorem: the verifier fails if one appears.

## Composition, cleanup and validation boundary

All root identities are exact on arbitrary dirty rational symbols. The graph
change happens wholly inside a scalar segment and preserves its full boundary
operator. Thus composing with the unchanged surrounding native/free-operator
program preserves the full operator. For B, every subsequent native warp's
numeric list position increases by one while its chronological placement after
the same old events is preserved. The verifier regenerates literal cleanup
from the entire edited forward word. It separately compares the non-target
projection of every before/after block, which is the part inverted by cleanup;
target outputs are omitted exactly as specified by the inherited contract.

Every compatible candidate is checked by exact local matrices; every legal
candidate receives full chronological invoice/hygiene checks and regenerated
cleanup. Both baseline full 723-input free-operator programs and deterministic
edited whole-word samples are replayed in ordinary and dual orientations, with
reverse pullback and cleanup-boundary checks. **Edited whole-word interpreter
coverage is sampled**, while universal coverage of the enumerated candidates
uses the exact local matrix composition and inverse-cleanup argument. This is
not a native Clifford phase proof or a full multiplication theorem.

## Costs and limits

The ledger lists both complete source profiles, all candidate profiles, helper
widths, live and dirty inputs, primitive counts, native maps, correction counts,
added scalar/cleanup operations and finite coefficient heights. No new register
is created. All unchanged inherited charges remain inherited; unknown physical
hosting, owner chronology, uniform precision/stock/tape, all-size compilation,
outer admission and analytic/BIT obligations are explicitly unknown. Since the
recursive change already does not improve, assigning any nonnegative cost to
the added operations cannot rescue this particular proposal. This is a stop
rule for this finite graph domain, not for changed interfaces in general.

## Predecessor credit

Dataisfire supplies the literal PR3734 words. The retained frame trace and
subspace representation come from PR3886; the scalar/dirty semantic auditor
credits Sagar Thakrar, roger-sato and Arham Tahir in its original notices.
Jeremy Kothe's retained rank-profile rewrites and the PR3941/3942/3957/3964/3970
fixed-graph investigations motivate changing the graph. Dugongue's PR3863
provides the paid `2+2 -> 1+3` implementation target and overhead discipline;
this package does not claim to realize that target or to originate its budget
certificate. Full upstream notices are retained in vendor/SOURCE-CREDITS.md.
