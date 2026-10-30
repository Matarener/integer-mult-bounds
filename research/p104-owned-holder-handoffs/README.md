# Close the owned-holder gap in the P104 handoff screen

This package proves a finite obstruction for the complete P104 words of
PR #5561 and PR #5569. At all 5,252 event boundaries where an owned scratch
register holds a productive helper input, two public holders have incompatible
frame anchors. This includes all 2,832 points omitted by the predecessor scan.
No common frame can contain all the public holders at such a cut.

The result rules out a single common-frame successor reset at every one of
these cuts, with the scalar event order and its scalar frames fixed. It allows
any binary subspace as the new frame, not just a listed source frame. It also
allows any number of extra common-frame registers. It grants free removal of
all owned holders: the public holders alone still obstruct the reset.

This closes a named search gap. It does not raise kappa. It tells a new search
to change public scalar anchors or use a reset with more than one frame,
instead of spending time on cheaper scratch transport in this fixed word.

## Sources and overlap

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority 7.
The selected result is unchanged. The source-binding baseline passed after
byte-exact materialization of its files omitted by the sparse checkout.

The [claim in Discussion #5576](https://github.com/CrocSwap/integer-mult-bounds/discussions/5576)
states the bounded domain. The current PR and Discussion cache, the handoff
hub and all-state related PR search were checked before this work. These
checks do not cover unpublished work and do not prove novelty. This work does
not take the event-retime scope in #5574 or the basis and private-COPY scope
in #5125.

The submission refresh also found the concurrent claim in
[Discussion #5575](https://github.com/CrocSwap/integer-mult-bounds/discussions/5575).
That task changes the scalar realization at the owned boundary. This package
keeps that realization and all its scalar anchors fixed. The separator result
was sent there as supporting evidence. It does not close that changed-program
scope or reserve a new search.

The two compressed words are byte-exact inputs from GamingPuzzled's
[PR #5569](https://github.com/CrocSwap/integer-mult-bounds/pull/5569), head
`af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf`. `INPUTS.json` records the exact
Git object and SHA256 for each file. One is DreamingOfClouds' PR #5561 word.
The other contains GamingPuzzled's helper-706 handoff. We retain both, so the
result binds both the original omitted domain and the stronger successor.
No pending Git object or network is needed to replay this package.

## Proof

Fix a boundary after event i and a productive input h. Let S contain h's own
public register and every public register whose exact scalar row has a
nonzero coefficient of h. An immediate successor reset at one frame F must
remove the old input from every other live row before it substitutes a new
independent input. In the common-frame reset model, every register in S must
be at F. A dirty owned row may also need service; we grant that service free.
This relaxation can only help a proposed reset.

For public register j, let A_j be its last scalar frame at or before the cut,
or its initial frame if there was no scalar event. Let B_j be its next scalar
frame after the cut, or its final frame. All legal public MOVE events increase
the binary subspace. Thus, even if all MOVE stops in this interval can change,

    A_j <= F <= B_j.                                  (1)

This condition uses scalar reads as well as writes. Omitting a read would
permit a false frame window. For an owned descending register the inequalities
would reverse. We do not need either owned inequality for the obstruction.

The certificate gives public holders j,k and a binary vector v at each cut,
with

    v in A_j,  v not in B_k.                           (2)

Equations (1) and (2) contradict A_j <= F <= B_k. This excludes every F,
including unlisted subspaces and frames of the wrong or right dimension.
Extra registers cannot remove the two mandatory public constraints. A more
favorable paid tariff, free scratch cleanup, or a cheaper frame path cannot
repair this contradiction while the anchors stay fixed.

The exact scalar replay enumerates every boundary after every event, including
MOVE, INIT and CLEAR. It finds all helpers with a nonzero coefficient in any
live owned row. There are no additional cases before event zero: all owned
rows are empty. Both full source words have 5,252 cases and 2,832 touched cases.
The latter count reproduces the predecessor's omitted domain. Final scalar
rows and all public frame endpoints are checked as part of the replay.

## Verification

`verify.py` constructs the complete separator list from sparse rational rows.
A second pass uses integer rows with one binary denominator. It reconstructs
the required cuts and checks every certificate entry, with separate binary
Gaussian elimination for frame membership. Both passes check all final scalar
rows. The result receipt binds a SHA256 digest of the ordered separator list.

Controls reject a missing cut, a zero separator, a false scalar anchor and an
owned register presented as a public holder. Small frame fixtures also contain
both feasible and infeasible memberships. The normal and optimized Python
replays must reproduce `RESULT.json` exactly.

```sh
python3.12 -B scripts/research_package.py --package research/p104-owned-holder-handoffs
```

The package checks a finite scalar and frame obstruction. It does not replay
native phases, the full physical caller, compiler or outer budgets. None is
needed to exclude this necessary condition. A new positive kappa claim would
need all of them. The source's free helper endpoint contract and five framework
assumptions are not independently admitted here. Independent human review and
hosted CI are separate from the local evidence.

## Maximization and limits

The scope was extended from 2,832 selected scalar points to every owned-holder
event boundary, from listed frames to every binary subspace, and from actual
scratch costs to free scratch service. All cases still fail for public-only
reasons. This is a complete stopping rule for this common-frame reset family.

The proof does not cover moving a scalar event or its frame, a different public
basis, a new scalar prefix, a distributed reset, or a construction that retains
old-input information for a later consumer. It is not a lower bound on all
P104 constructions. The predecessor's other screened domains and its numerical
cost decisions are not independently certified by this package.

## Open next questions

1. Can a changed public scalar anchor remove a listed separator and still save
   net paid moment after all transports and target debits? Start with one
   certificate cut, publish the changed events, and check the full suffix.
   The event-retime and basis scopes already have active researchers.
2. Can a reset at several frames preserve later uses of the old input and return
   all owned fields at lower net cost? A concrete caller and complete invoice
   are missing. A static span calculation alone will not answer this question.

## Attribution

GamingPuzzled (Joel Pulikkan), PR #5569 and the successor-handoff method in
#5472; DreamingOfClouds, PR #5561 and #5553; thu-nmrc, PR #5551; Ali Romman,
PR #5544/#5545; Gareth Davidson (bitplane), David Arias (DavidAriasC), Cinna
Davis (1337isnot1337), Cao Yifan (intqwq), zxv, Jacob Alan Sussman and the
retained productive-helper, native and compiler lineage. The input words are
unchanged. The scalar semantics follow the published P104 contract; no source
interpreter is copied or imported.

New proof and verifier: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Two arithmetic passes do not constitute independent human review.
