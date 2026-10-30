# Whole-matrix synthesis saves 3,577 events in the selected P104 prefix

**Completed local circuit result. No new κ.** On the selected PR6030 word,
replacing its first scalar-only block reduces the complete word from **22,803
to 19,226 events** and its complete local scalar allowance from **189,428 to
142,778**. Every entry of the block's arbitrary-input matrix is unchanged.
All frame changes, copies, initializations, erasures, helper endpoints and paid
recursive calls retain their original order and values. The selected record
remains κ = 781451/250000000 = 0.003125804.

The contribution is a reproducible construction and exact certificate for one
local module, not adoption of a new supplier or an implementation benchmark.
It addresses Matarener's [PR5975](https://github.com/CrocSwap/integer-mult-bounds/pull/5975)
open question 2, global ordinary re-synthesis. PR5975 preserves the original
dependency graph through peephole passes; Nick Petalas's
[PR5999](https://github.com/CrocSwap/integer-mult-bounds/pull/5999) shares one
form through a dirty output on PR5907. Here, whole-row sharing and sparse
elimination rebuild the entire 567-role prefix matrix on **PR6030**, crossing
the original internal dependencies while retaining both boundaries. PR6030
already includes its own substantial ordinary-event rewrite. These savings
are measured against that actual selected word, not the older PR5907 counts.
Classical elimination and row sharing are not claimed as new algorithms.

## Frozen object and construction

Base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`.
The input is `research/p104-helper470-twin-rung-removal/WORD.json.gz`, SHA256
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.
The selected source head is `772dd10a5859a1d15f4851feb371519789213ad8`, with
portability repair `746ee5e1160ae64a15a81b2a432d5566142db850`; the word is
unchanged by that repair. [SOURCES.json](SOURCES.json) pins every live input
and the historical selected record, source manifest, review, pricing formula,
task card and predecessor notes by Git blob and SHA256.

Use zero-based event indices. Event 0 is `INIT 778 3`. Events **[1,9896)**
are 9,895 ADD/SCALE instructions in frame 3 (the empty binary basis); event
9896 is the first MOVE. All 567 touched roles are available in that frame.
The other 232 roles are untouched. No observation, COPY, CLEAR or native call
occurs inside this interval. Owned role 778 is live throughout it.

[synthesize.py](synthesize.py) forms the exact sparse rational matrix M of
this interval, starting with independent symbolic values for all 567 roles,
including role 778. It then:

1. Greedily subtracts a dyadic multiple of one whole output row from another
   when this removes at least two nonzero entries. Ratios have magnitude below
   2^12. Deterministic tie breaks fix the result; the cap is 2,000 steps.
2. Uses sparse Markowitz-style pivots restricted to units of Z[1/2], normalizes
   every pivot explicitly, and eliminates its column from every other row.
   Failure to find a unit pivot aborts; no general synthesis guarantee is claimed.
3. Removes the final row permutation with charged exchanges. Each exchange is
   three ADDs and one SCALE by −1; there are 132, with no free renaming.
4. Reverses the elimination list and inverts each elementary operation.

The retained run has 419 sharing steps, 795,230 ordered row-pair evaluations
and 567 pivots. The output is 6,039 ADDs and 279 SCALEs. Its maximum absolute
coefficient is 4. Every SCALE is a dyadic unit, every ADD uses distinct roles
already in the same frame, and no extra role or scratch field is introduced.

The original trial without the sharing pass produced 10,122 events and was
rejected. The refined trial above was the first strict improvement; discovery
stopped there. Only this one matrix was searched. This is neither an exhaustive
circuit search nor an optimality claim. The OS track draw was 31 (complex
supplier), and OS seed 7525094595556296861 modulo three chose this object
from three documented candidates. [TASK.json](TASK.json) records the scope
change from the task card, stopping rules, overlap and checkpoints.

## Why the substitution is exact

Write the elementary elimination matrices in chronological order as E1,...,Ek.
The construction checks that Ek...E1 M = I, entry by entry. Chronological
execution of Ek^-1,...,E1^-1 therefore has matrix M. This is a statement about
arbitrary independent entry values, not a test on sample vectors or a use of
the zero value of owned role 778.

A second implementation in [verify.py](verify.py), using dense integer rows
with binary denominators rather than the synthesizer's sparse Fraction rows,
compares all **321,489** entries of the original and replacement matrices.
The remaining 232 roles are identity in both. The verifier also checks the
replacement followed by its inverse against the literal identity.

Both programs have the same matrix at the first MOVE, and the original prefix
before the cut and suffix after the cut are kept literally. Thus every later
observation agrees, including every moved field and every helper return.
All scalar operations are in one common chart. Under the inherited common-chart
native contract, this identity acts componentwise at every positive column
multiplicity; the rational scalar coefficients stay outside tensor powers.
No noncommuting native operators are reordered by this replacement.

As a separate end-to-end finite check, the authenticated, unmodified
`p104-unread-path-resynthesis/local.py` from Ali Romman's PR5827 replays both
complete words using sparse rational rows. Its separate reverse-chronology
dense integer transpose checks all 799 columns and 638,401 coefficients of
the candidate. These are credited predecessor implementations, not newly
independent human review or a formal proof of the multiplication theorem.

## Complete cost of the local replacement

For q = ±n/2^d in lowest terms, the retained real ADD allowance is
2(3 + floor(log2 n) + popcount(n) + d). A SCALE by ±2^k costs
2(|k| + [negative sign]). Every source access is an emitted ADD, and every
pivot normalization and permutation operation is included. The prefix needs
no new copy, frame transition, initialization, restoration pass or child call.

| Quantity | Source | Candidate |
|---|---:|---:|
| Prefix events | 9,895 | 6,318 |
| Prefix scalar allowance | 106,368 | 59,718 |
| Complete local word events | 22,803 | 19,226 |
| Complete local scalar allowance | 189,428 | 142,778 |
| Local routes, normalizers, adapters, lifetime envelope | 5,325,000 | 5,325,000 |
| Complete local ordinary bound | 5,514,428 | 5,467,778 |
| Retained local ordinary allowance | 10,000,000 | 10,000,000 |
| Owned labels / lifetimes / peak occupancy | 29 / 31 / 13 | 29 / 31 / 13 |

All 3,453 local paid calls are unchanged, with rank counts
`{1:2219, 2:457, 3:496, 4:100, 5:163, 6:11, 7:6, 8:1}` and rank mass 5,952.
The 562 productive helpers retain counts
`{1:14, 2:8, 3:4, 4:107, 5:14, 6:2, 7:9, 8:19, 9:385}`.
Every required scalar source contact is charged and every non-scalar event
remains identical as an ordered sequence, not just a histogram.

The inherited physical caller makes 18 forward local calls, so the exact
local scalar-allowance reduction sums to **839,700** across those calls.
Its recursive invoice remains 66,834 paid calls and 13,444 productive fields.
The fixed complete ordinary envelope remains **184,647,552 < 10^9**; the
verifier reads this caller envelope from the authenticated source receipt and
recomputes the local routing formula from the unchanged profiles. It does not charge a speculative
new recursive saving or lower that coarse caller envelope. The paid/target
moment, completion, compiler threshold and outer assembly are unchanged.
Therefore no new κ is claimed.

Both circuits satisfy the same inherited 26,000-event and coefficient bounds.
The conservative scalar growth envelope 2^(16·26000), paid native rank mass,
ownership and storage bounds can be retained. For additional diagnostics,
the exact scalar-prefix maximum row l1 norms are 695/8 before and 343/4 after;
the replacement inverse has maximum 1285/4. These are local matrices relative
to independent cut inputs, not a rounded-error or whole-machine certificate.

## Reproduce and inspect

CPython 3.12, standard library only; tested with 3.12.14. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-prefix-row-synthesis
```

Expected: both normal and optimized registered commands print
`PASS_P104_PREFIX_ROW_SYNTHESIS`, then the launcher prints
`PASS_REGISTERED_RESEARCH_PACKAGE research/p104-prefix-row-synthesis outcome=completed`.
The launcher also validates exact source provenance and declared live inputs.
Direct scoped verification works without Git after a source export:

```sh
python3.12 -B research/p104-prefix-row-synthesis/verify.py
python3.12 -O -B research/p104-prefix-row-synthesis/verify.py
```

Normal verification writes no repository files. It regenerates the candidate
and compares the entire [RESULT.json](RESULT.json) receipt. To materialize the
complete candidate, add `--emit-word /absolute/external/path/WORD.json`; the
path must be outside the checkout and absent. No compressed candidate copy is
needed. Its canonical JSON payload (sorted keys, compact separators, no trailing
newline) has SHA256
`537f6c581ee7ebc758d2bba417f6d7b98f1cb9b5fe8916a7ae707575d9b68617`.
The emitted file adds one newline. The receipt also binds the exact prefix and
the dense integer matrix. `--write` is an explicit receipt-generation mode and
refuses to overwrite an existing receipt.

The positive fixture has matrix `[[1,1/2],[3/4,-13/8]]` and a checked inverse.
Controls reject a wrong ADD sign, omitted SCALE, wrong chart, odd denominator,
unavailable source, whole-word sign fault, and byte corruption of each live
source (word, result and checker). A SCALE by two on the just-initialized owned
role passes the specialized whole-word endpoint check, as expected, but fails
our stronger arbitrary-entry block identity. This explicitly tests the extra
local obligation rather than conflating it with complete-word endpoints.
All checks use explicit exceptions and remain active under `python -O`.
Authenticated executable source is compiled from the bytes just read, so direct
verification cannot silently execute a stale predecessor bytecode cache.

Executed on 2026-10-28 with CPython 3.12.14: metadata/pins, both registered
replays, committed bytes/source history/executable modes, and the official
10-file export with all three declared inputs passed. Normal and optimized
isolated Python replays of that Git-free export with empty PATH passed in
14.31 and 12.21 seconds. All 11 files including the export manifest retained
their bytes and modes. The export was marked read-only; access-control
enforcement is not claimed. A changed result-receipt saving was rejected in
both modes. These times establish bounded replay, not a circuit runtime gain.
Hosted CI and independent scientific acceptance are not claimed.

## Scope and inherited obligations

The selected construction, frozen packages and `upstream/` are unchanged.
This package checks an exact local substitute and the complete scalar word.
It **does not rerun** the full native-map, physical-caller, compiler, precision
or outer-ledger cold replay, and it does not request supplier admission.
Unchanged interfaces and event sequences are the explicit reuse boundary;
changing any source pin, cut, chart, operand set or non-scalar event invalidates
this result. A changed synthesis output must pass the full matrix and word
checks and receive a new committed receipt.

The five selected framework assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`.
The uniform word and rounded multiplier are not materialized. No speedup on a
real implementation, stronger exponent, universally optimal circuit, or
independent human acceptance follows from these finite certificates.

## Open next questions

- **Adoption through the selected supplier pipeline.** Emit this word, bind it
  in a successor package and run the complete selected supplier/native/caller
  and precision pipeline. This would make the ordinary saving available to a
  later paid-call construction. Independent review and that integration replay
  remain blockers; the five framework assumptions are not discharged here.
- **A second disjoint scalar block.** Locate one maximal same-chart interval,
  price all permutation and source work, and test its arbitrary-entry matrix.
  A fresh overlap check and separate narrow claim are required. No other
  interval was searched, and this success gives no guarantee for another one.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI Codex assistance**;
no delegated agents or independent human review. New work is Apache-2.0.
DreamingOfClouds supplied PR6030 and PR5907; Ali Romman supplied PR5827 and
the unmodified local row/transpose checker; Mason Hale supplied PR5811.
Matarener posed the global ordinary-resynthesis question in PR5975, and
Nick Petalas's PR5999 established the earlier dirty-output sharing example.
Those predecessor results are credited, not re-certified here. Douglas
Colkitt supplied the selected application review and portability repair.
David Arias, Cinna Davis, Gareth Davidson, Pierre-Loic Doulcet and the native,
controller, compiler, BIT and analytic contributors retain all predecessor
credit and notices in the source packages. No predecessor files are vendored
or modified by this contribution.
