# Characteristic-two representation obstructs a cheaper reader bill

For the fixed complete-plane additive tariff, a cheaper exact decoder must
have augmented query/target and reader/target column matroids that cannot be
represented over any characteristic-two field. [PROOF.md](PROOF.md) proves
this implication for arbitrary finite term counts, arbitrary selected indicator
counts and external directions on both factors, over any coefficient field.
The hypotheses are a finite partition of binary labels into positive even
Gram-I groups and the stated complete-plane rectangular rank tariff.
Original indicator terms attain the floor. The retained P112 whole bill is 224.
This is a scoped negative theorem, with no new supplier or kappa.

The proof transfers coordinate functionals and active reader spans separately
to a characteristic-two representation. Every old zero survives on both
factors. The expanded target then has rank equal to the original bill.
The representation criterion is sufficient for this transfer. It is not
asserted necessary: preserving only the relevant requests can work while
changing other subset ranks.

## What this adds

[PR3491](https://github.com/CrocSwap/integer-mult-bounds/pull/3491) uses
projectively TU query coefficients inside the target span.
[PR3489](https://github.com/CrocSwap/integer-mult-bounds/pull/3489) transfers
at most four terms on two targets using six-point configurations. The present
proof isolates their representation ingredient without count or external-span
bounds. The characteristic-two expanded-rank ingredient itself is inherited,
not republished as a new result.

An explicit near-regular rank-five family has eleven queries, four targets and
one external direction. Its U2,4 restriction forbids a binary representation,
so it lies outside the regular/TU class. A GF4 representation still exists.
The proof and exact polynomial-minor certificate establish this for the whole
one-parameter family, specialized at any s!=0,1 over any field. This supplies
nonregular external-direction examples of the new criterion.

DreamingOfClouds' [PR2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111)
puts a TU signing hypothesis on the binary pairing matrix instead. It is a
different sufficient condition. The separate five-term non-Fano investigation
in this campaign concerns selective request preservation beyond full matroid
representation. This package does not claim to settle that question or infer
a cheaper decoder when its own criterion fails. Exact comparison heads, paths,
blobs and hashes are in [COMPARISONS.json](COMPARISONS.json). They are comparison
receipts, not inherited runtime dependencies or ancestry pins.

## Recomputed evidence

The written proof supplies the arbitrary finite quantifiers. The finite replay
provides an explicit certificate and controls:

- All 15,503 square minors of the displayed 5-by-15 augmented configuration are
  exactly 0, +/-1, +/-t or +/-(1-t). Only one entry contains t, so values at zero
  and one determine every determinant polynomial, with no interpolation guess.
- All 32,768 subset ranks agree at rational parameters 2,3,-1 and GF4 omega.
  The rank-stream SHA256 is
  `d3b3b7c5e9e5b1427111a7fa9fbfc705c85976f429da8b5649e8b113fad1b5ab`.
  All 16,384 ordered source/reader feasibility requests agree as well.
- Six rational/GF4 operator pairs pass 76,800 entry comparisons. Three use the
  literal P112 labels and three use a sixteen-port geometry with repeated labels
  across groups. Both support inclusions and every actual rectangular tariff
  are checked. Each literal original has 504 external query entries and 985
  external reader entries, with exact cancellation. Its bill is 95, and the
  transferred bill is 35, above the selected four-target floor 32. These are
  demonstration inputs, not proposed improvements. Literal terms attain 32.
- Both implementations check all 50,176 entries of expanded I224 and its
  selected rank-32 diagonal restriction. Original full literal terms cost 224.
- Three behavioral groups include actual reader omission, domain/capacity
  rejection, a collapsed four-point-line representation, six real optimized CLI
  corruptions and a restored positive replay.

The separate checker imports no primary code. It uses permutation determinants,
a GF4 multiplication table and hereditary independent-set ranks, rather than
Bareiss elimination, polynomial field multiplication and incremental bases.
It corroborates minors, every subset rank, the support-request stream, the
nonbinary U2,4 witness and expanded entries. It does not independently rebuild
the six portwise factor transfers. Independent human review is unclaimed.

## Reproduction

Use standard-library CPython 3.12. TMPDIR should name an existing owned output
directory for disposable test copies. No Git or pending source is needed by the
three scientific scripts when their declared label input is present.

```sh
python3.12 -I -O -Werror -B research/p112-matroid-reader-transfer/verify.py
python3.12 -I -O -Werror -B research/p112-matroid-reader-transfer/independent.py
python3.12 -I -O -Werror -B research/p112-matroid-reader-transfer/test_controls.py
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-matroid-reader-transfer
```

`verify.py --emit` prints the recomputed receipt without overwriting RESULT.json.
The registered wrapper also checks Git provenance. Use ordinary import mode
for the repository's committed-byte/history and export helpers:

```sh
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-matroid-reader-transfer --ref HEAD --check-source-history
python3.12 -Werror -B scripts/export_research_package.py export --package research/p112-matroid-reader-transfer --ref HEAD --output /chosen/owned/output/package.tar
python3.12 -Werror -B scripts/export_research_package.py check /chosen/owned/output/package.tar
```

The retained PR3370 fixture is included unchanged and hash-authenticated.
SOURCES.json records its published origin and immediate copy source. The live
canonical label input is pinned and declared in VERIFY.json. The self-contained
proof does not assume a pending executable, source archive or Git object.

## Engineering constraints

Build the Lever produced the rerunnable certificate and separate checker.
Prove It Works requires actual committed bytes and a Git-free export replay.
Test Behavior, Not Implementation shaped the omitted-reader and real CLI
corruption controls. Power of Ten gives explicit capacities, no recursion,
optimization-resistant contracts and the following bounded deviations.

Python managed allocation is a rule-3 deviation. The primary's largest indexed
collection has 32,768 entries, each with at most five five-coordinate basis
vectors. Parameters and dimensions in the driver are fixed. Exact solves have
at most 16 equations and 15 unknowns, minors have size at most five, and port
operators have at most 112 ports and eleven terms. Reads are capped at 1 MiB,
fixture reads at 32 KiB and receipt reads at 64 KiB. No user-supplied size or
parameter expands a census. The separate checker has at most 4,944 independent
subsets including the empty set, 32,768 rank bytes and permutations of at most
five coordinates. Library/runtime allocations cannot be disabled. A production
implementation would need a fixed-buffer backend; this package is a finite
scientific checker.

The fixed-file importlib load, JSON duplicate-key callback and unittest dispatch
are rule-8/9 deviations, bounded to one local verifier, one callback and three
fixed tests with synchronous lifetimes. No plugin or arbitrary import name is
accepted. Private CLI fixtures copy at most sixteen regular package files of
at most 1 MiB each and one bounded input; symlinks and subdirectories reject.
Seven subprocesses each have a sixty-second timeout. Temporary directories
close on every exit. A production backend would use direct typed calls; a test
framework rewrite would not improve the scientific result.

Functions stay below sixty physical lines. Ruff 0.17.1 checks target py312 with
E,F,I,B,UP,SIM,RUF,C4,PIE,PERF,PTH,RET and formatting, without suppressions.
Shared runner/export code and frozen predecessors are unchanged.

## Limits and family decision

Narrow this additive support-tariff search to configurations outside the theorem,
and still test selective support transfer. No new native construction round is
justified until an exact cheaper literal factorization is supplied. Full matroid
recognition is not implemented. Failure of the sufficient hypothesis is neither
a lower-cost witness nor evidence that support transfer is impossible.

Source acquisition, coefficients, frames, dirty restoration, ownership, hosting,
stock, precision, all-size/compiler admission, complete supplier costs and outer
multiplication transfer remain open. The selected conditional kappa stays
0.001672660197076918. Independent human and formal proof-kernel review are
unclaimed. No Lean, Docker, hosted CI or full selected cold replay is claimed.

## Open next questions

Can a literal saving survive both nonrepresentability and a selective-transfer
check? [TASK.json](TASK.json) gives its relevance, feasible first step and
blockers. This session reserves no further construction or larger census.

## Sources and credit

Nick Petalas. Apache-2.0. Credit Tekalign/PR3370 for the retained partition;
Philippe Van Velzen for the integral floor and Arham Tahir/PR3345 for its
source-bound expanded-identity corroboration; DreamingOfClouds/PR2111 for the
pairing-signing precedent; PR3463, PR3472, PR3475, PR3489 and PR3491 for the
immediate query/reader, external-span and representation boundaries. Matarener,
ctoth, ywz65, Sagar Thakrar, Cinna Davis, Adam Gall, Jeremy Diviney and the
retained P112/E8/native/compiler/supplier lineage retain their original credit.
Frozen bytes and notices are unchanged. No literature priority is claimed.

Near-unimodular matrices and their specialization are standard. See Hall,
Mayhew and van Zwam, [The excluded minors for near-regular matroids](https://dillon128.github.io/HMZ11.pdf),
sections 2.1-2.3, following Whittle's representation work. The elementary
specialization used here is proved in PROOF.md; no classification theorem is
needed. Coordination uses the existing
[P112 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587).
Entry overlap covered 410 open PR bodies and 2,332 Discussion records with
complete pagination at 03:48-49 UTC on 2026-10-18. Handoffs, peer reservations
and prior campaign results were inspected. Historical diffs and unpublished
work are not comprehensively covered; no match is not proof of novelty.
