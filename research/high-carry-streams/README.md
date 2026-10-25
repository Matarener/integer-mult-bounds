# Direct signed carry streams for selected BIT routes

PR2915 implements a negative high-field carry by repeating sign/shift/sign,
up to twelve complete primitive calls for a carry of −4. This package adds an
opt-in physical kernel that performs the same rotation with two sequential
buckets. It uses encoded counters, preserves complete prefix/suffix coordinates,
returns a distinct owned output and clears its private state. The existing +1
path remains in use: replacing it exposed a small setup regression on tiny
packets. Frozen sources and the default adapter remain unchanged.

On the 486-bit −4 fixture, complete kernel traffic falls from **1,105,367 to
54,064 tape operations (95.1%)**. A complete signed-scale route falls from
**881,379 to 410,237 operations (53.5%)**. Every read, write and unit movement
between entry and return is counted, including setup, rewinds, bucket erasure
and native intervals. Initial fixture creation and disposal of the returned
output are outside the measured interval; output disposal stays paid by the
caller. No mathematical coverage is dropped between the two implementations.

The source proof gives `O(BQS + I)` physical work for a complete B×Q×S packet
and encoded modulus width I, hence `O(BQS)` for the reached canonical high bank.
The direct kernel requires at most **eight additional scratch roles** and no
numerical words. Borrowed source and occupied scratch roles are additional to
that local inventory. This is not a total backing-capacity or supplier proof.

## Exact evidence

- **96 complete kernel pairs:** all eight signed carries, Q in 3,5,7,9,25,81,
  unit/nonunit suffixes, multiple prefixes, wrapping and zero-residue cases.
  Every independent input column, borrowed count, source and dirty lease is
  checked; success leaves only the distinct output lease owned.
- **Seven complete route pairs:** dyadic/scalar/noncommuting words, signed low
  carries, two high radix digits, multiple old prefixes and spectators, and
  the unchanged zero-high-width branch. Native calls are unchanged and remain
  in the measured totals. All seven complete pairs pass the original independent
  coordinate oracle with the new adapter.
- **2,056 split identities and controls:** exact separate modular arithmetic;
  wrong direction also rejected on all-zero payloads; trailing input in active
  and identity cases; one scratch role too few; extra endpoint-preserving I/O;
  invalid carries, zero modulus and source corruption.
- **Actual selected registry exposure:** 1,123 chart types, 2,246 orientations,
  q=3 and identity low class, using source occurrence multiplicities. Carries
  take **34,450,048 old full-field primitive calls → 11,858,368 kernel calls**.
  These different primitives have different prices. This is one finite low-class
  specialization, not a distribution over all low classes, a runtime ratio or
  executed selected GL64 payloads.

[PROOF.md](PROOF.md) gives the all-width coordinate argument, role lifetimes,
complete cost decomposition and explicit inherited scope. [KERNEL.json](KERNEL.json),
[ROUTES.json](ROUTES.json) and [CATALOGUE.json](CATALOGUE.json) retain complete typed
receipts; replay compares their contents as well as their digests in
[RESULT.json](RESULT.json). [BENCHMARK.json](BENCHMARK.json) records three alternating
fresh-process Python 3.12 pairs on identical inputs: median instrumented kernel
execution is **19.68×** faster and complete signed-scale route execution **2.13×**
faster. Including process startup gives **2.75×** and **1.47×**, respectively.
These are instrumented reference fixtures, not multiplication timings.

## Reproduce and use

From the repository root with standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/high-carry-streams
```

Expected: all four `PASS_HIGH_CARRY_*` suites and successful registered replay.
The control suite runs with optimization enabled. The same committed verifiers
can run from a source export with all declared inputs present. The generic
metadata/pin launcher additionally needs Git history. [VALIDATION.md](VALIDATION.md)
records actual checks and environments.

In an authenticated PR2915 namespace, construct `adapter.CarryAdapter` instead
of `stage.Adapter`, with the same native backend, registry and capacity. Its
`StagePool` and enclosing `route_packet` interface are unchanged. The replacement
uses no runtime module patch; test-only observers patch the fixture namespace
to compare the two adapters. This adapter has not been combined with PR3330's
optional frame scheduler in this package, and their measured savings must not
be added. The changed carry map is independent of that schedule.

Base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6,
OS assignment seed **6**. [TASK.json](TASK.json) records three candidates,
changed card scope, bounded coverage and stopping rule. [SOURCES.json](SOURCES.json)
pins every executable/archive input before predecessor loading.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19007093).

No new κ, recursive child profile, selected frontier, complete fitted GL64
execution or supplier admission is claimed. Source-level proof and exact finite
replay do not discharge inherited native, numerical-capacity, whole-caller stock,
physical backing, analytic or formal-refinement obligations. Concurrent
[PR3340](https://github.com/CrocSwap/integer-mult-bounds/pull/3340)'s fitted-B1 bridge
addresses a separate boundary and is not used as an assumption here.

## Open next questions

1. Can one reached dyadic scale/carry pair be executed with fewer complete
   passes? First derive its actual prefix/suffix permutation and full bucket,
   scratch and restoration bill. The present kernel deliberately changes only
   bounded translations.
2. Before adoption, independently review this kernel and join its eight-role
   reserve and actual encoded width to one enclosing caller. The remaining
   stock/backing and native-refinement obligations prevent a component benchmark
   from serving as a whole-supplier admission. Structured handoffs are in TASK.json.

## Credit

Tekalign (`tekuuu`), with substantial OpenAI Codex assistance in source analysis,
implementation, proof, verification and writing. New material is Apache-2.0;
no independent human or formal-kernel review is claimed.

Jose Manuel (`jmbarrancoml`) supplied PR2915's executor, kernel vocabulary and
registry, PR2899's backend, and the retained physical source chain. The execute
lifecycle is adapted with attribution, rather than attributed as a new algorithm.
David Arias supplied PR2753's recursive caller. The physical observer follows
this account's PR3330. Credit Nick Petalas, commdata2338, Sagar Thakrar, Arham
Tahir, ywz65, Ross Richardson and Krzysztof Wójt for the predecessor cost,
countdown, physical-lifetime and caller work, and the PR2157/PR589/PR555 lineage
for the retained factor words and geometry. Original notices remain in the
unchanged authenticated archives.
