# Unlimited linear corrections cannot repair the frozen helper-572 seam

This contribution was produced by Nick Petalas. It proves a scoped obstruction
on the selected PR6030 word: after overwriting helper 572 at cut 13637, arbitrary
finite linear recoding inside the declared chart-595 and chart-603 regions
cannot preserve the protected original outputs and retain any nonzero public
response to the new independent input.

This extends JoyboyBrian's [PR6088](https://github.com/CrocSwap/integer-mult-bounds/pull/6088)
from two added ADDs to arbitrary linear bank maps. Increasing the scalar
correction count in these regions cannot repair the split. A changed transport,
window, prefix or storage contract is needed. No new kappa is claimed.

## Result and evidence

[PROOF.md](PROOF.md) specifies the complete contract and proves the theorem.
The first bank has six fields. Only field 572 moves to the second bank before
field 709 enters. Six protected output equations force the transmitted form to
recover the displaced old helper value; a single linear channel then cannot
also carry the new independent input.

The exact standard-library certificate derives eight independent source forms
from the prefix, with a minor determinant `1/32`, and a six-row protected suffix
minor of determinant `8`. It checks the complete original-input boundary
identities, every public response of the erased 778 and V-final 740 columns,
and the source chronology. The proof uses these finite facts to cover every
finite correction length and arbitrary rational coefficients.

The verifier also enumerates 722 rank-one products over the fields of orders
2, 3 and 5, checks a two-channel positive scope control and a singular minor,
and rejects four changed schedule/original-input fixtures and changed source
bytes. These controls corroborate the rank argument; the universal rational
statement is the written proof. No predecessor census or theorem is replayed.
The generated JSON receipt binds the package files and exact source hash.
Default execution writes nothing.

## Reproduce

From the repository root, using the standard-library CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-unrestricted-572-seam/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-unrestricted-572-seam/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-unrestricted-572-seam
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-unrestricted-572-seam --check-source-history --check-modes
```

Another CPython 3.12 path may be substituted. Expected scientific marker:
`PASS_P104_UNRESTRICTED_572_SEAM`. The registered normal and optimized checks
have separate 60-second limits. Metadata and committed-byte checks require a
Git checkout. The direct verifier requires only its package and declared word.

## Scope and sources

Scientific base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`,
priority revision 8. The selected record gives conditional kappa `0.003125804`.
The current source-binding orientation passes; it is not a selected cold replay.
[SOURCES.json](SOURCES.json) pins the exact selected word and historical task
provenance. [TASK.json](TASK.json) records the changed scope and next questions.

The immediate question source is JoyboyBrian's PR6088 at
`6e6236ec763d2aa3eac40201c9634051c583320c`,
`research/p104-noncarrier-two-add-seam/PROOF.md`. Its finite pair result is cited
context. The general carrier exclusions of apoursh PR6067 and Jonathan Capalbo
PR6069 are distinct because they preserve original rows at each atomic update.
JosieElliston PR6108 documents the remaining cross-time gap. The earlier PR6040
unit-injection census is retained as lineage. This contribution changes the
correction model; it does not retarget that census to another word or group.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279693).
Live handoffs, open/account PRs and local reservations were checked. Merged PR
and main-tree searches included helper 572, unrestricted recoding, two-chart
seams and arbitrary correction lengths. The overlap helper reported complete
remote pagination with 338 open PRs and 5,959 Discussion records, but only
78 of 8,623 local note paths were materialized. Direct main-tree searches
supplemented that sparse coverage. Unpublished work and historical code diffs
remain outside this bounded check; no global novelty certificate is claimed.

No selected native/compiler/caller/outer cold replay, Lean or Docker run is
needed for this scalar obstruction. No physical construction, cost improvement,
new supplier or complete multiplication theorem is supplied. All five selected
framework assumptions remain. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

- Can a second independent transferred form repair this split at favorable
  complete cost? First specify its legal source/destination frames and solve
  all original-input equations. The missing transport, normalization,
  restoration and full paid/target invoice are blockers.
- Can a pre-cut save or changed chronological window avoid the obstruction?
  First pin that changed boundary and its owned lifetime, then derive its
  independent source forms and protected-output minor. The present frozen
  two-region certificate does not transfer automatically.

## Engineering limits

The verifier uses Build the Lever and Prove It Works: the two source-bound
minors and all boundary equations are reproducible from one declared input.
No recursive call exists. Loops are bounded by the fixed 22,803 events, 799
fields, 771 input columns, eight response columns, 722 finite-field products
and at most `8!` determinant summands. Every function is below 60 lines.
Explicit failure checks remain enabled under optimization.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py`: Python's
Fraction, JSON and dictionary operations allocate during execution. The scope
is this offline fixed-input certificate. The authenticated dimensions bound
state and snapshots by fewer than ten `799*771` coefficient entries, plus the
fixed word and eight-column suffix. No concurrent work or growing input stream
is accepted. Warning-strict normal/optimized registered replay is the diagnostic
check. A fixed-capacity rational representation would be required before reuse
in a runtime that forbids dynamic allocation.

Credit JoyboyBrian for the seam and question, apoursh, Jonathan Capalbo,
JosieElliston, Matarener, flyingviper, Ali Romman, DreamingOfClouds and their
retained P104/native/caller predecessors. The fixed-word chronology and rank
factorization methods are standard; the new contribution is this source-bound
unbounded-length obstruction and its compact certificate. Apache-2.0.
