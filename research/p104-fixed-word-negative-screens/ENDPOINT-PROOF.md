# Two finite scalar exclusions on the selected PR6030 word

This proof concerns only the authenticated PR6030 scalar word. It supplies
necessary-condition failures for two specified rewrite classes. It supplies no
new kappa, complete supplier, global P104 optimum, or universal impossibility.
Every source productive endpoint and the source word remain unchanged.

Prepared by Jonathan Capalbo (jon314159), with OpenAI Codex assistance.
Apache-2.0. Credit PR5827 and Ali Romman for the earlier endpoint-resynthesis
mechanism, PR6030 and DreamingOfClouds for the selected word, and all retained
P104/native/ownership/compiler authors. Rational elimination and linear-span
invariance are standard facts, not new general theorems.

## Exact source semantics

Use one independent rational coordinate for every arbitrary public input. The
770 public rows start as distinct coordinate vectors. An owned role enters at
INIT with zero scalar row under the source's retained owned contract. ADD,
SCALE and COPY act literally on these rows. MOVE changes the canonical chart
but leaves the decoded scalar row unchanged. CLEAR ends the owned lifetime.

Both modules replay all 22,803 events and verify every final row and chart:
the prescribed 104 source-to-target additions, restoration of all other public
rows, and cleared owned roles. Thus 770 arbitrary public columns and all 799
final roles are checked. This scalar check does not re-prove the source native
frame construction or discharge its framework assumptions.

All operations use exact rational arithmetic. No modular rank failure,
floating-point tolerance, sampled input or heuristic span decision is used.

## Endpoint-combination screen

For each role, consider consecutive MOVE events

`A -> B` and `B -> C`.

There are 2,664 such pairs in the complete word. Exclude a pair if its receiver
is read, scaled, copied, initialized or cleared strictly between the MOVEs.
Exactly 1,900 pairs are excluded. Each of the remaining 764 has only incoming
ADDs there; none has an empty interior contact list.

Let r be the receiver. Its first legal endpoint window runs from the slot just
after its last preceding contact to the slot just before the first MOVE. Its
second window runs from just after the second MOVE to just before its next
contact. A slot is the state before an event. The receiver has no contact in
the interior of either window, and is respectively at charts A and C. Windows
at the ends of the word use the initial or final slot.

At each original interior ADD, capture the donor's row at that exact version,
and multiply it by the original coefficient. Their sum is Delta, the net
incoming functional. Using the sum, instead of testing each donor separately,
permits cancellation and splitting a replacement between both endpoints.

For a window at chart F, form S_F from:

1. every other live role's row at F at the beginning of the window; and
2. every other role's row when a MOVE arrives at F during the window.

Retain departed or cleared values optimistically. Exclude r throughout. Each
source value has a label containing endpoint side, slot and role, so two
versions of one role cannot overwrite one another.

**Accumulated-span lemma.** Every actual unchanged donor row available at F
anywhere in the window lies in the rational span of S_F.

Proof: proceed through the original events. Same-chart ADD and SCALE remain
in the existing span. COPY into a zero owned role does too; INIT adds zero.
CLEAR and departure cannot enlarge the accumulated span. Every MOVE arrival
is explicitly included. No read of r occurs inside the window, so hypothetical
receiver ADDs there cannot alter the other original donor values. This proves
the inclusion by induction.

A replacement that changes only the receiver's incoming endpoint ADDs and
replaces the two MOVEs by a direct transition must therefore satisfy

`Delta in span_Q(S_A union S_C)`.

This grants rational coefficients, free retention and the complete union of
the two banks. It is at least as permissive as the specified dyadic endpoint
ADD rewrite. The condition fails for all 764 pairs. In 693 cases, some original
input coordinate in Delta is absent from every generator. In the remaining
71, exact echelon elimination leaves a nonzero residue outside the row span.

The elimination checker independently reconstructs Delta as its recorded
linear combination plus residue. The residue has zero coefficients at every
echelon pivot. A nonzero row-span vector must have a nonzero pivot coordinate,
so a nonzero such residue proves nonmembership. Complete interval records and
hashes of the exact target and generator rows are in the deterministic receipt.

The conclusion excludes precisely these 764 endpoint-ADD rewrites of the
fixed word. It does not cover receiver scaling/recoding, modified other-role
programs, intermediate receiver reads, new owned lifetimes, changed endpoints,
new targets or cross-invocation reuse. It does not say that every positive
scalar identity would have a valid native implementation.

PR5827 already supplies one earlier constructive example of endpoint
resynthesis, and that construction is inherited by PR6030. This new finite
screen checks the broader linear-combination condition on the remaining
eligible intervals of the current word. It does not invalidate that earlier
construction or prove its mechanism exhausted on other words.

## Five private-query output seams

The nominated zero-based MOVE events and roles are:

| Event | Role | Source chart | Destination chart |
| ---: | ---: | ---: | ---: |
| 12805 | 798 | 267 | 1091 |
| 13495 | 773 | 1031 | 597 |
| 13510 | 781 | 518 | 240 |
| 13563 | 782 | 517 | 243 |
| 13592 | 779 | 477 | 1090 |

Each is an owned nested rank-four transport. Immediately after the MOVE, test
its nonzero decoded output row against every other live role at the same chart.
Exclude the queried role itself. A second, more favorable test additionally
grants free identification of chart presentations whose binary spans agree.

All five values fail both exact rational row-span tests. The receipt includes
the target rows, donor rows, charts, reductions and nonzero residues. This
excludes only immediate output reconstruction from those banks. It does not
exclude a changed continuation, earlier observations, a different native
monomial, new storage, or another query/target contract. No private query is
removed and no hypothetical deletion is priced.

## Controls and reproducibility

The endpoint controls include a two-source positive, missing-coordinate and
correlated-span negatives, a cross-bank cancellation that fails in either bank
alone, the same role at distinct endpoint versions, rejection of duplicate
version labels, and a trace whose correct net contribution depends on donor
versions and original ADD coefficients. Private-query controls include a
dyadic positive, an independent-column negative, explicit nondyadic-witness
labeling, receiver exclusion, and equal versus unequal binary-subspace
presentations.

All checks use explicit exceptions and remain active under Python `-O`.
`endpoints.run(word)` and `private_queries.run(word)` return deterministic
JSON-ready dictionaries without file writes, local paths, runtime measurements
or environment fields. Authentication, source binding and expected-receipt
comparison are performed by the package wrapper.
