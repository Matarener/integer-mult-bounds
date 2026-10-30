# No common-chart hand-off in the omitted owned-holder states

This is a source-bound obstruction to one successor hand-off template. It is
not an impossibility theorem for owned temporary registers or early cleanup.
No improved multiplication bound is claimed. Submission refresh found that
Ali Romman had independently published this same source domain and public-pair
mechanism in PR5579. This reconstruction corroborates that result; it is not
the novel claim of this package. See README.md for the distinct cost and
exceptional-delivery results.

## Source and exact scope

The input is PR5569's `research/p104-priced-handoff/WORD.json.gz` at commit
`af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf`. Its compressed SHA-256 is
`12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f`.
It has 735 arbitrary public inputs, 743 physical role IDs, 25,140 events,
104 live main ports and 527 productive helpers. Eight owned lifetimes use
roles 735 through 742, with peak live owned storage one.

The omitted predecessor domain comprises states in which an owned register
contains a nonzero coefficient of a productive helper's original input.
The existing screen skipped 2,832 distinct helper/holder/window geometries.
Our checker replays *every* source event boundary, including MOVE boundaries,
and imposes no touched-symbol or first/last-use restriction. It finds 5,252
helper/boundary pairs, 2,832 distinct full-holder geometries, and 2,340 distinct
public-holder geometries.

We retain the chronological scalar events, their operand roles and contact
charts, including COPY and the boundaries of owned lifetimes. MOVE events may
be relocated, added, deleted or replaced within the resulting scalar-contact
windows, provided public transports remain ascending. At a cut we ask whether
one common chart can accommodate the nominated helper and every public role
that currently contains its original input symbol. All restrictions on owned
register charts are dropped in this test. We also allow every binary subspace
as a putative contact chart, not merely a listed source frame.

The theorem excludes this single-common-chart successor hand-off at every
state in the omitted domain. It does not exclude earlier synthesis, changed
scalar contacts, multiple-chart cleanup networks, or different boundary maps.

## The window lemma

Fix a boundary immediately after a source event. For a public role `r`, let
`A_r` be its preceding scalar-contact chart, or initial chart if there is no
preceding contact. Let `B_r` be its following scalar-contact chart, or final
chart if there is no following contact. A contact introduced at a chart `F`
within this window must satisfy

```
A_r subseteq F subseteq B_r.
```

This follows from ascending public transports and unchanged scalar-contact
boundaries. It does not depend on how many transports are inserted or where
they occur in the window.

Consequently, if required roles `a,b` have a binary vector `v` with

```
v in A_a,   v not in B_b,
```

there is no common chart for those two roles, and therefore none for the
entire required set. Indeed, a common chart would imply
`A_a subseteq F subseteq B_b`, contradicting this vector.

This elementary pair obstruction is stronger than the failure of a search
over a chosen frame list: it rules out every possible common subspace `F`.

## Exact source certificate

The checker interprets every source scalar operation over the rational numbers
on formal independent public-input symbols. INIT zeros the owned row; COPY
copies into an empty owned row; CLEAR erases it under the source ownership
contract. MOVEs preserve these normalized symbolic rows. Source transports,
ownership and common scalar charts are checked along the way. At the end all
743 output rows must equal the declared public map or the cleared owned row.
No public input is set to zero.

After every event, for every productive helper symbol present in an active
owned row, the checker reconstructs all public holders. The nominated helper
role is also included whether or not its current coefficient is nonzero.
The preceding and following scalar contacts supply each holder's window.
For every one of the 5,252 helper/boundary pairs, a pair of public holders and
a separating binary vector satisfy the window lemma. Thus the obstruction
persists even if the owned holders may be moved at zero cost to arbitrary
charts or ignored altogether.

Boundaries between consecutive events have constant symbolic rows and the same
adjacent scalar contacts; MOVE-only changes do not introduce an unexamined
window. Hence the event-boundary enumeration covers all temporal cuts in this
fixed-contact domain. The initial and final states have no active owned field.

The receipt records the counts, per-owned-role census, sample witnesses and a
SHA-256 of the deterministically reconstructed complete witness list. The
optional `--witnesses PATH` flag emits every witness. Each witness contains the
two public role IDs, their relevant boundary frames, and the missing vector.
Verifying it needs only binary span membership and the reconstructed source
windows; no optimization solver or floating-point comparison is used.

## Positive and negative controls

On the pinned PR5561 predecessor, after event 15443 the known helper706/173
cleanup has

```
row706 = input706 + (1/2) row173.
```

Both scalar windows contain frame559 of dimension8, strictly between
helper706's initial and final dimensions0 and9. The same window checker accepts
that common chart. This is the published positive example behind PR5569,
not a new contribution.

Four corruption controls reject changed source bytes, the zero vector in
place of a separating vector, substitution of an owned role for a required
public holder, and a reversed public transport window. These run under normal
and optimized Python, without relying on `assert` statements.

Source role173 is a productive helper because61 is absent from the live-port
list. PR5569's prose calls it a main Y register; our computation uses the actual
source role classification. This descriptive discrepancy does not invalidate
its cleanup identity or the positive control.

## What this result changes

Simply extending the predecessor's common-chart scan to its omitted owned
holder states cannot produce an improvement while those scalar contacts remain
fixed. The next useful test must change a hypothesis: synthesize a copy before
an incompatible public contact, change a scalar dependency, or design and fully
price a cleanup network with several contact charts. Additional coefficient
search at the obstructed common chart cannot help.

The result has no tariff or global optimality claim. It does not assert that
the inherited conditional P104 construction is admitted, that arbitrary owned
erasure is free outside that contract, or that every productive-helper design
has the same obstruction.

## Attribution

PR5569: GamingPuzzled, successor hand-off and omitted-domain identification.
PR5561: DreamingOfClouds, free helper endpoints and source word.
PR5551: thu-nmrc, coupled contacts. PR5544/5545: Ali Romman, P104 caller and
local verifier. Retain the native, Clifford, compiler, geometry, precision and
analytic predecessor credits in those packages. The window lemma is elementary;
the contribution is its exact application to the formerly omitted source domain.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agent checks. Apache-2.0. No proof-kernel or independent human acceptance is claimed.
