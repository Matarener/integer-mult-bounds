# Scope correction for the h=8 BIT receiver census

**No new κ.** PR5285's recorded search does not by itself establish its full-family closure
statement. It covers **43,122 distinct puncture-set/receiver pairs out of
344,019,474** in its declared generator-input domain. Exactly one puncture set
has every receiver choice represented. This package supplies an independent,
source-bound coverage certificate and a concrete omitted input; it does not
find a better word or disprove the claimed optimum.

The frozen [PR5285 README](../bit-h8-receiver-census/README.md) describes
sampling in its stage table but closes the entire h=8 family in its final
section. Its [TASK.json](../bit-h8-receiver-census/TASK.json) likewise says the
family is closed as a source of gain. Those statements need the qualification
below. Original sources and the selected frontier are unchanged. The main
ledger records PR5285 as **archive-only, partially reviewed**, with independent
scientific review open; this correction does not change that disposition.

## Exact recorded coverage

The independently reconstructed finite rule has 120 ordered root lines, 30
orthogonal four-frames and 18 eligible punctures. Testing all 48,620 nine-element
subsets for distinct frames and affine binary rank nine produces exactly the
17,478 sets listed in Stage A. Each has nine receiver entries in `{1,2,3}`,
giving `17,478 * 3^9 = 344,019,474` possible input pairs.

| Retained stage | What the coverage checker establishes |
| --- | --- |
| A | All 17,478 sets, one default receiver vector each. |
| B | 200 of those sets, draw indices 0..30 each. Draw 0 repeats A. The other 6,000 draws give 5,991 distinct explicit keys; nine draws repeat a key. All 6,000 draw vectors match the retained sampling rule. |
| C | All 19,683 receiver vectors of PR589's one puncture set, with no missing or duplicate vector. |
| Tuning | 52 distinct receiver vectors of that same set, all already represented in C. This is not an exhaustive tuner search. |

After normalizing default receivers and taking the union:

| Distinct receiver vectors represented per set | Number of sets |
| --- | ---: |
| 1 | 17,278 |
| 30 | 8 |
| 31 | 191 |
| 19,683 | 1 |

Thus `17,278 + 8*30 + 191*31 + 19,683 = 43,122` pairs are represented;
**343,976,352 pairs are absent from these tables**. An independent
inclusion-exclusion check obtains the same count as
`17,478 + (19,683 - 1) + 5,962`: Stage A, the new C choices, and distinct B
choices outside PR589's set. Those 5,962 choices differ from their defaults.

Counts project away node-optimization effort. A row at one effort is generously
counted as covering its pair regardless of effort; this cannot create evidence
of exhaustive coverage at a fixed effort. Counts refer to recorded input keys,
not distinct output circuits, successful unseen words, or undocumented runs.
Different inputs may produce the same word or profile. A proved equivalence
reduction could also eliminate omitted inputs; the counts do not rule that out.

The seed-95 witness is the admitted puncture set
`(10,15,43,51,52,53,83,92,106)`. Its sole recorded receiver vector is
`322111322`. The allowed vector **`322112322`**, changing line 53's receiver,
is absent from A/B/C and tuning. This is an omitted generator input, **not a
counterexample to optimality**: no word was generated or priced for it.

## What follows, and what remains open

The justified conclusion is: **the documented stages found no new installed BIT
record**. The reported Stage-A optimum concerns default receivers, and the
exhaustive receiver stage concerns PR589's set alone. Neither the Cartesian
product nor all tuning/transfer choices were exhausted. Extending the conclusion
requires an explicit bound or equivalence argument eliminating the omitted domain, or additional
source-bound evidence with its own cost and stopping rule. This package does not
recommend launching that large census.

The predecessor's 0.1% improvement gate is its chosen stopping criterion; failing
that gate is not proof that no smaller gain or different legal transfer exists.
Its additive compact436 estimates remain estimates, not constructed transfers.
The reported receiver improvements, collision with helpers 413/469, and
successful partial GL464+470 transfer retain their original credit and scope.
Their prices, complete producer words and transfer checks are **not replayed
here**, and no defect in those results is asserted. The complex supplier's
binding role and the selected five framework assumptions are unchanged.

There is also a concrete **effort-provenance mismatch** within the same census:
the saved `producer/run_stageC.py` calls `one.evaluate(P, 552, sel, 50)`, while
the producer README says NODEOPT 2000 and the main verifier's three C spot
replays use 2000. The new checker reads the two call sites as syntax, without
executing predecessor code. The historical run setting is unresolved: the CSV
does not record it. This does not show that the table's prices or the successful
spot checks are false, or that 50 and 2000 necessarily produce different words.

## Method and reproducibility

Base: `13be6ac685845c1ff671f5d26e7166165abd998e` (canonical main, 2026-10-25).
Audited PR5285 head: `440550b43428ef856ce217ec682111ba65ac93dc`; the source
files are retained at the base. [SOURCES.json](SOURCES.json) gives exact Git-blob
and SHA256 pins, including the original plan, Hamming generators, D4 partition,
tables and relevant source descriptions. Selected-record and task-catalogue pins
are provenance, not runtime dependencies.

The new standard-library implementation imports no predecessor Python. It emits
the positive-leading Hamming root representatives directly, uses exact integer
dot products, reconstructs the plan's eligible cells, and uses binary pivot
elimination for the affine-rank rule. It authenticates inputs before parsing,
checks every table key, and compares the entire derived [RESULT.json](RESULT.json).
It allocates only the observed keys and 19,683 receiver vectors, not the full
344-million-pair product. A finite domain replay is not a formal proof of the
integer-multiplication theorem.

From the repository root, with Python 3.12 and no third-party packages:

```sh
python3.12 -B scripts/research_package.py --package research/h8-census-coverage
```

Expected: normal and optimized runs print
`PASS_H8_CENSUS_COVERAGE represented=43122 unrepresented=343976352 full_joint_coverage=false no_new_kappa`;
the controls pass and the launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
For a direct or Git-free replay, run `verify.py` and `test_verify.py` with
`python3.12 -I -O -B`. [VERIFY.json](VERIFY.json) declares the complete closure.
Runtime is several seconds on the measured host.

The 16 tests comprise a separate inclusion-exclusion/default-normalization
control and 15 rejection controls: missing/duplicate set or receiver coverage,
failed rows, invalid labels, inconsistent sampling, duplicate tuning, invalid
plan receivers, an inadmissible puncture set with valid labels, overlapping
partition blocks, source-byte drift, false full-coverage and falsely reconciled
effort receipts. Normal and `-O` execution are reproducibility checks, not two
independent mathematical implementations. See [VALIDATION.md](VALIDATION.md)
for executed commands and portable-export evidence.

## Open next questions

1. Can a source-derived bound exclude the omitted receiver domain without a
   large census? First identify a receiver-independent cost bound that remains
   valid under tuning and the actual compact436 transfer. No such implication
   is supplied by this coverage certificate; a sparse sample is insufficient.
2. Which NODEOPT value produced the retained C table? Obtain the original
   invocation/log or a source-bound regeneration receipt, then reconcile the
   driver and description outside the frozen archive. A few equal spot replays
   cannot identify the historical invocation.

## Task, attribution and license

Research-consolidation assignment seed **95**, drawn once with operating-system
randomness; task `scope-navigation`, refined to this single closure discrepancy.
[TASK.json](TASK.json) records the three candidate scopes, overlap limitations,
stopping rule and local claim. No new receiver search was performed. The finite
domain enumeration and complete table inventory are the completed experiment.

Prepared for **@CubeJerry with substantial OpenAI Codex assistance** in analysis,
implementation and verification. Credit **Mark / Matarener (PR5285)** for the
original census, tables, price checks and transfer evidence; **eumemic (PR555,
PR543 and PR493 lineage)** for the generator, plan and geometry; and
**DreamingOfClouds (PR589)** for the tuned word. Retain the compact436/controller,
Clifford, analytic and other predecessor credits in the original packages.
New work is Apache-2.0. No independent human review, proof-kernel acceptance,
new supplier, new κ or selected-result promotion is claimed.
