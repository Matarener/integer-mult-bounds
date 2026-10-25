# Fuse dyadic scale and carry streams in the reached BIT route

A positive dyadic scale and its adjacent low-carry correction can share one
**two-pass affine stream operation**. The opt-in adapter replaces the reached
PR2915 fragments `double^k; translate(c)` and `translate(c); half^k`, for k=1,2.
It preserves the complete source permutation, spectators, borrowed inputs,
output ownership and dirty scratch leases. PR3343's direct-carry implementation
is the incumbent comparison, so its earlier savings are already included.

On the 486-bit A=4,c=-4 kernel fixture, the full physical tape bill falls from
**163,764 to 55,881 operations (65.9% less)**. The complete ×4
scale route falls from **344,457 to 174,573 (49.3% less)**. These are literal
reads, writes and unit moves on reference fixtures, including encoded setup
and internal cleanup. Fixture provisioning and final returned-output disposal
are outside the measured interval; the written caller recurrence charges disposal.
These are component operation counts, not multiplication runtime measurements.

## Construction and paid boundary

The kernel implements x->Ax+c mod Q, or its inverse, for A in {2,4}, |c|<=4 and
odd Q>=3. It splits the source into A monotone residue streams and bounded
head/tail fragments, then weaves them directly in translated output order.
Inverse mode exchanges the split and merge. Unbounded cardinalities stay on
encoded Count tapes; only bounded residues enter finite control. Q<A and
carry wrap at Q=3 are covered.

[PROOF.md](PROOF.md) gives the all-parameter column identity, complete local
O(BQS+I) tape bill, ownership/cleanup argument and unchanged enclosing recursive
children. At most **17 additional free scratch roles**, zero numerical words
and 3V occupied payload cells including the borrowed source are needed.
The fixed scratch reserve is larger than the incumbent's. Whole-caller backing,
stock, native refinement and source-level all-size premises remain dependencies.

The adapter fuses only contiguous same-field fragments and preserves every
native B1 call. Standalone scales retain their original implementation: the raw
c=0 fused setup loses on some tiny fixtures. All 36 such raw-kernel regressions
are retained in the evidence; none has nonzero c in the completed test domain.
There is no claim of a universal numerical speed ratio. No new child profile,
supplier admission, selected frontier or kappa is established.

## Exact evidence and reproduction

Use standard-library CPython 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/dyadic-affine-streams
```

Expected: four `PASS_DYADIC_AFFINE_*` markers and successful registered replay.
The controls also run with Python optimization enabled. Normal verification
compares complete typed results and never regenerates certificates.

- **504 raw kernel pairs / 37,044 columns:** Q in {3,5,7,9,17,25,81}, (B,S) in
  {(1,1),(2,3)}, A in {2,4}, c in {-4,...,4}, both directions. The oracle maps
  every input column independently; random Boolean contents are supplementary.
- **Six complete route pairs:** noncommuting words, signed fractional ADDs,
  old prefixes, spectator suffixes, native intervals, two high radix digits and
  the skipped zero-high boundary. Only the opt-in adapter changes.
- **Actual selected catalogue:** all 1,123 chart types, both orientations and
  retained occurrence multiplicities, at the explicitly labelled q=3 identity
  low class. This is source specialization, not selected GL64 payload execution
  or a census over every low class.
- **16,308 independent fragment cases and 1,152 bounded-residue identities:**
  wrong offset/direction, all-zero column detection, trailing input, insufficient
  inventory, invalid compiled arguments, changed sources and an endpoint-preserving
  extra-read control. The 17-role peak is both attained and tested one role short.

[AFFINE.json](AFFINE.json), [ROUTES.json](ROUTES.json), [CATALOGUE.json](CATALOGUE.json)
and [RESULT.json](RESULT.json) retain exact results. [BENCHMARK.json](BENCHMARK.json)
records three alternating fresh-process pairs on identical kernel/route inputs.
Timing evidence is separate from deterministic scientific receipts.
[VALIDATION.md](VALIDATION.md) states the actual environment and publication checks.
Finite replay corroborates the written proof; it is not formal verification of
the full multiplication theorem or independent human review.

Base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6,
OS assignment seed **1**. [TASK.json](TASK.json) records three candidates, the
scope change, bounded completed domain and stopping rule. [SOURCES.json](SOURCES.json)
pins every executable/archive input before predecessor imports.
[Canonical coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19020895).

## Open next questions

1. Join the 17-role local peak and 3V occupied payload to actual enclosing leases,
   recursive frames and physical backing. The first step is one complete caller's
   fixed reserve ledger; the existing universal reserve/refinement premises remain
   blockers to supplier adoption.
2. Before extending to signed slopes or ADDs, derive one explicit source/consumer
   map and a full cost bill. Negation and native intervals are unchanged and may
   dominate remaining routes. Another static fusion count alone is insufficient.

## Credit

Tekalign (`tekuuu`), with substantial OpenAI Codex assistance in derivation,
implementation, source analysis, verification and writing. New work is
Apache-2.0. Original sources, frozen evidence and notices remain unchanged.

Jose Manuel (`jmbarrancoml`) supplied PR2915's reached route, affine compiler,
scaling loops and lifecycle, PR2899's native backend and the retained source
chain. David Arias supplied PR2753's physical caller. The direct-carry incumbent
is this account's PR3343, whose released scale/carry question is answered here.
Credit Nick Petalas for the ordinary wrapper and local scaling/scratch invoices,
Arham Tahir for countdown/sign accounting, Sagar Thakrar for setup/source audits,
commdata2338 for ordered ADDs, Krzysztof Wojt for local composition, ywz65 for
parking, and the PR2157/PR589/PR555 word/geometry/native lineage preserved in
those immutable sources. This package adds the fused affine kernel, local
fragment dispatcher, paid proof and independent before/after comparisons.
