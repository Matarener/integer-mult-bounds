# Exact P112 three-target subset-sum reader tariff

Every finite recoding of three distinct literal PR3370 indicators using the
seven nonzero subset-sum query rays, with readers in the same triple span,
has minimum actual-reader tariff equal to the sum of their complete-group
sizes. The statement holds over every coefficient field. This closes
that elementary joint dictionary without improving the mathematical frontier.
Disjoint replacements of this kind retain the original whole-K tariff 224.
No new kappa or selected-frontier change is claimed.

The [proof](PROOF.md) reduces arbitrary repetitions, scalings and term counts
to 729 minimal reader-support patterns per geometry type. Exact computations
cover all 4,960 indicator triples through 800 types and 583,200 actual binary
rectangular-rank bills. The primary rational solve and packed-rank verifier
and the separate integer-minor/coordinate-matrix replay agree on every
receipt row and the complete bill stream digest. RESULT.json records the
exact per-type minimum, multiplicity, minimizer count and digest.

This answers the larger-joint-block question in
[PR3463](https://github.com/CrocSwap/integer-mult-bounds/pull/3463) for one
explicit dictionary. Its pair-span theorem did not cover triples.
[PR3383](https://github.com/CrocSwap/integer-mult-bounds/pull/3383) bounds query
self-cost rather than this actual-reader tariff. The one-external-dimension
pair-target families in PR3398/3414 and the concurrent worker-2 continuation
are different identities. None is silently treated as a supplier admission.

## Replay

Use standard-library Python 3.12, with a private existing TMPDIR for disposable
control copies. Direct verifiers are read-only, work without Git, and emit
no generated artifacts. `verify.py --emit` prints the recomputed receipt.

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-three-target-dictionary
python3.12 -I -O -Werror -B research/p112-three-target-dictionary/verify.py
python3.12 -I -O -Werror -B research/p112-three-target-dictionary/independent.py
python3.12 -O -Werror -B research/p112-three-target-dictionary/test_controls.py
```

The seven behavioral groups include a half-integral three-term factorization
checked at all 12,544 literal matrix entries, a deleted-term rejection,
binary-versus-rational rank separation, invalid capacity and geometry inputs,
all subset/axis span requests over F3 and F5, and real optimized CLI rejections
for changed minimum, Boolean receipt value,
duplicate key, both source drifts and missing input. The controls return to a
passing positive copy. Assertions are not needed for the verifier's contracts.
The registered runner supplies its own private bytecode namespace.

SOURCES.json pins canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6, the original card, selected record and one live label input.
The unchanged attributed PR3370 fixture is included locally with exact source
commit, blob and SHA256, so no pending Git object is needed for replay.
The selected-source binding/arithmetic baseline and the card's ceiling positive
control passed in a separate source export. Neither was a full selected replay.

## Limits and decision

Queries are restricted to seven rays. Readers are constant linear combinations
of the three target indicators and zero elsewhere. Arbitrary directions,
external dimensions, nonconstant or global readers, larger joint blocks and
shared native operations are excluded. The bound is finite and specific to
the retained literal geometry. It is not a universal recoding obstruction.

Pause this dictionary. Another construction round needs an exact lower-cost
factorization under a changed contract. Native acquisition, coefficients,
frames, dirty restoration, ownership, hosting, stock, precision, all-size
compiler obligations, complete supplier and outer transfer remain open.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker,
hosted CI and the full selected cold replay were not run.

## Engineering constraints

Build the Lever led to the exact enumeration and rerunnable receipt. Prove It
Works led to a code-disjoint full replay and literal operator/CLI controls.
Test Behavior, Not Implementation led to omission and corruption tests at the
published verifier boundary. Power of Ten led to explicit input/matrix bounds,
finite enumeration, enabled contracts under optimization and no recursion.
All scientific functions remain below 60 physical lines.

Managed Python allocation is a scoped rule-3 deviation. Primary state has at
most 800 records, 729 seven-entry patterns and 729 live byte-sized bills; each
Gram matrix is at most 24 by 24, and the independent minor checker has at most
eight 3-vectors. Input reads are capped at 1 MiB, source metadata and fixture
at 32 KiB. Python/library allocations cannot be disabled. The replay enforces
these bounds; a production backend would use fixed buffers after a real caller
is specified. The independent reader trusts only authenticated bounded source
bytes for its geometry sizes and reads the bounded published receipt.

The duplicate-key callback and unittest discovery are rule-8/9 deviations with
fixed named targets and synchronous lifetimes. Source sorting uses fixed key
callbacks on 112 records. Control subprocesses are synchronous and capped at
90 seconds; each owns a temporary directory removed on every exit. No native
pointers, preprocessing, recursion or persistent background work is introduced.
No shared configuration or predecessor scientific code changes.

## Open next questions

Can an explicit query outside the seven rays give a cheaper literal triple
factorization? First write its exact operator and actual reader bill. No such
witness or physical caller is supplied. TASK.json records relevance and blockers;
no further dictionary census or native construction is reserved.

## Sources and credit

Nick Petalas. Apache-2.0. Credit Tekalign/PR3370 for the unchanged sixteen-group
fixture and rank-32 fit; Philippe Van Velzen/PR3345 for the expanded-identity
argument; PR3383/3398/3414/3429/3447/3463 for the query/reader distinction and
immediate handoff. Matarener/Mark, ctoth, ywz65, Sagar Thakrar, Cinna Davis,
Adam Gall, Jeremy Diviney and the retained P112/E8/native/compiler/supplier
lineage retain their predecessor credit. Frozen source bytes and original
notices are preserved. No literature priority is claimed.

Coordination joins the existing
[P112 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587).
Entry overlap covered 381 open PR bodies and 2,306 Discussion records with
complete pagination on 2026-10-18 at 02:57-58 UTC. Submission covered 382 open
PR bodies and 2,311 Discussion records at 03:05-06 UTC, without warnings.
Predecessor claims, campaign contributions and peer reservations were checked.
Historical diffs and unpublished work are not comprehensively covered; no match
is not a novelty proof. The canonical fetch found no guidance or input delta.
