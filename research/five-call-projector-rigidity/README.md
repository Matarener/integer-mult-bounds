# Exact limits on shortest full-query callers

**No new kappa.** This package proves that a formal forward-stage caller
with n independent main fields and n+1 rank-one central queries needs at
least 1, 2 or 3 thin calls when n is 4, 6 or 8, respectively. Arbitrary
constant scalar frames are allowed. The bound does not assume that the
full-stage projectors commute. The same bounds now hold for rank-q queries
on nq fields at every positive coupled width q. Arbitrary mixing between
ports is permitted. Read [COUPLED.md](COUPLED.md) for the complete block
normal form and free associative algebra proof. Extra work fields, longer
query words, shorter finite-order stages and noncentral ordinary frames
remain open.

The first two mixed coefficients already prove these exclusions. The replay
covers the complete scalar parameter space in each of 84 site-pattern
domains. It does not enumerate a bounded set of coefficients. It also finds
and checks the full query polynomial for the unique alternating thin-site
pattern at each minimum. Its natural stage endpoint has a nonzero Jordan
defect, so that construction does not yet give independent Gaussian jobs.

Three additional written results make the scope explicit:

- A normal-form theorem classifies every shortest rank-one query tuple.
  This makes the projector test exhaustive under its stated hypotheses.
- An extreme-degree argument excludes the five-call signed endpoint
  (3,3,-2,-2) at every coupled width. Two separate triangles attain the
  six-call algebraic bound. This result requires no enumeration.
- A short-interval Gram argument proves that a faithful stage period
  p>=n-1 gives no escape for an all-full shortest query word. A literal
  native trace check then excludes the proposed eight-field order-seven
  caller. Read [PERIOD.md](PERIOD.md) for this additional theorem.
  The block Schur-complement argument in COUPLED.md extends it to every
  coupled width, including all 104 source ports at once.

The four-field all-full case has a short polynomial identity for 1. It
works in every characteristic other than two. The six- and eight-field
case proofs use exact rational elimination and hold in characteristic zero.
Read [PROOF.md](PROOF.md) for the complete statements, conventions and limits,
and [RESULT.json](RESULT.json) for the deterministic replay receipt.

## Why this changes the next experiment

The earlier eight-field/nine-full proposal had a favorable optimistic
.0034 price on the pinned PR5599 source. It now fails before native routing
or compiler work: its required query endpoint does not exist in this formal
stage model. A four-field/five-full profile was favorable only in linear
rank mass; it already fails the current selected tariff. That distinction
corrects the earlier investigation text.

The current selected record at the base commit is PR6030, conditional
kappa .003125804. The older invoice and source arguments remain pinned to
their own sources; this package does not substitute them for the current
selected caller. No selected file, source archive or other contributor's
construction changes.

The [prior research checkpoint](https://github.com/aliromman/integer-mult-bounds/tree/1fee8d07f/research/noncommuting-star-caller)
contains the minimum-query degree theorem, initialized-work limits, native
advances of orders seven and nine, and the earlier cyclic reduction lemma.
The new Gram argument closes the order-seven question that the earlier
lemma left open. Period six on eight fields remains outside the proof.
[DISCOVERY.md](DISCOVERY.md) records the tests and the separate history/border
obligations.

## Reproduce

Use Python 3.12 and the standard library. The registered replay needs no
optimizer, SymPy, network, native library, Lean or Docker.

```sh
python3 -B scripts/research_package.py --package research/five-call-projector-rigidity --check-only
python3 -B scripts/research_package.py --package research/five-call-projector-rigidity
```

Direct replay also works in a Git-free export:

```sh
python3 -I -B research/five-call-projector-rigidity/verify.py
python3 -I -O -B research/five-call-projector-rigidity/verify.py
```

The final marker is `PASS_SHORTEST_QUERY_PROJECTOR_RIGIDITY`. The replay
checks the 84 scalar domains and all 84 free-algebra domains. Literal
2-by-2 and 3-by-3 matrix controls reject commutative word multiplication.
Normal replay
does not write artifacts. The explicit `--write` mode regenerates RESULT.json.
Checks include a changed polynomial coefficient, a first-order false
positive made of actual projectors, complete alternating query endpoints,
their stage defect, and the six-call signed positive control.

SymPy discovery and the standard-library replay are separate implementations.
The replay reconstructs the original chronological products and does not
read the discovery receipts. Both were written in this author-side AI
session. This is not independent human review or a proof-kernel certificate.
The selected frontier replay was not run; this package does not change it.

## Sources and coordination

Base: canonical main `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority
revision 8. The canonical [Discussion claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19199752)
records the changed question and coverage. The latest bounded refresh read
30 Discussion roots, their latest comments, 50 open PRs and the handoff hub.
An older complete-pagination cache was also searched but was stale. Local
notes were sparse and unpublished work was not covered. No exhaustive
novelty claim follows from that overlap check.

Cinna Davis's query/controller lineage and all retained P104/native source
authors are predecessors. The earlier connector and advancing-stage work
in the linked checkpoint is by Ali Romman with OpenAI Codex assistance.
The selected source and caller retain Gareth Davidson, David Arias, Cinna
Davis, DreamingOfClouds, Jacob Alan Sussman, Cao Yifan, zxv and the full
credited native/helper/compiler/BIT lineage. This package does not claim
their source constructions or their kappa gains.

The border comparison credits Dillon's
[controller border interface](../controller-border-interface/README.md)
and Yiyang's [bounded-lane core](../bounded-lane-border-core/README.md).
Their exactification and recursive-coherence limits remain open here.
The related group-word collision work in Discussions6097/6137, two-frame
work in6111, and spectator projection in6090 have different contracts.

New proof application, exact replay and discovery records: Ali Romman with
substantial OpenAI Codex assistance. No subagents. Apache-2.0. Independent
scientific review is pending. No merge, closure or frontier update.

## Open next questions

Can the order-six native stage support the balanced eight-field caller?
First solve the exact cyclic query equation, then the complete target
endpoint. The new period theorem excludes periods seven and above in this
all-full model. Numerical failure does not exclude period six.
Physical routes, independent helpers, native phases, ordinary costs,
ownership and compiler admission remain required.

Can extra queries or initialized work pay for a complete endpoint at the
current tariff? Start with a favorable full provisional invoice, including
all thin calls and stage maps. The previous minimum-query degree theorem
still applies at its own boundary.

Does the thin-call count extend to all even n? A general invariant would
avoid repeated case checks. The present proof covers only n=4,6,8; the
observed pattern is not a universal theorem. Structured questions and
blockers are in [TASK.json](TASK.json).
