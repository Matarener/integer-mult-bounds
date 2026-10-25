# Independent audit of BIT COPY support propagation

**The support step requested by PR4200's handoff is valid in its stated model.
No new supplier or κ is claimed.**

This adds a separately written paired-execution proof and code-disjoint checks
of one premise of Ross Richardson's unchanged-total COPY floor, at predecessor
head `ddfc3133cbdf548e163c867d5671f8f01dd5d5ae`. The earlier seven-rank floor,
projection argument and original construction remain predecessor work.

## Exact scope

Fix the intersection L of one private branch's visited frames. Compare the
same fixed public trace with and without that branch's read increments,
keeping all initial public values, including arbitrary correlated dirt, equal.
Every nonzero difference stays in a register whose frame contains L if every
ordinary dependency edge U→W preserves `L⊆U ⇒ L⊆W`. This local condition is
sufficient; it need not be necessary for a particular whole trace with dead
or cancelling edges. Upward MOVEs and same-frame scalar ADDs satisfy it.

The proof covers every finite fixed trace. Cancellation, including over F2,
can remove a difference but cannot create one without a differing input.
It separately states the extra linearity/unchanged-q and closed-walk tariff
premises needed to recover the credited predecessor corollary. Hidden
data-dependent guards count as dependencies; adaptive schedules are not
silently admitted. See [PROOF.md](PROOF.md).

## Evidence

- The separate source checker authenticates the original compressed word and
  geometry, checks all 38,927 operation/frame records, 636 exact rational span
  ranks and 111 final cap equalities. It binds the public suffix
  `[24069,25768)` to 760 upward MOVEs and 939 same-frame ADDs, with no COPY and
  unchanged source registers 471..479. It checks 6,470 cap/root equalities.
- Its finite two-register closure has 283 states and 1,780 transitions, four
  accepted cancellation cases, and six nonzero-q executions illustrating the
  two forbidden hypothesis relaxations.
- A code-disjoint oracle checks 1,632 closed private walks, 34,208 symbolic
  states and 317,824 transitions in coordinate and rational noncoordinate
  frame families in Q³. Independent dirty columns, cancellations, a downward
  MOVE and an unequal-frame ADD are explicit controls.

The two relaxation examples are outside the original model; they are not
predecessor defects. The source checker does not recompute complete root
closures, R/K or recipient/projected-recipient ranks, all 660 scalar endpoint
columns, physical MOVE semantics, or a complete tariff. Those remain separate
predecessor evidence or open obligations. The finite checks corroborate the
written theorem; they do not prove its universal quantifier.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/bit-copy-support-audit --check-only
python3.12 -B scripts/research_package.py --package research/bit-copy-support-audit
```

Six registered commands run the two checkers and a separate Fraction rank cross-check in normal and strict optimized
modes. [REVIEW-FILE-MAP.json](REVIEW-FILE-MAP.json) resolves original report
filenames and explicitly separates historical CLI hashes from current bindings.
Standalone, Git-free receipts can be written outside the package:

```sh
python3.12 -I -B research/bit-copy-support-audit/source_check.py --output /tmp/bit-support-primary.json
python3.12 -I -O -W error -B research/bit-copy-support-audit/independent_oracle.py --out /tmp/bit-support-oracle.json
```

The checks import no predecessor implementation. Minimal untouched data,
audited proof and notice/credit documents are in `source/`; text sources use a
`.txt` suffix so their original relative references are understood as references
to the original publication. [SOURCE-PINS.json](SOURCE-PINS.json) binds the
original source head, paths, Git blobs and SHA256 values. A retained source
commit in this PR's own ancestry makes reproduction independent of an unmerged
branch cache. [SOURCES.json](SOURCES.json) records that availability separately
from the original attribution. The selected record and catalogue remain pinned
historical provenance at canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`.

## Open next questions

A changed public dependency or mixed-total construction needs its own complete
word and bill. Begin with one literal arbitrary-input candidate, list every
dependency including guards, and price acquisition, transport, return, owners
and the actual caller. No such candidate is supplied here. Ross Richardson's
active mixed-total investigation is separate from this completed proof audit.
Native interfaces, precision, the complete recursive invoice and the outer
multiplication theorem remain open; this audit does not alter the frontier.

## Credit

Ross Richardson/PR4200 supplies the unchanged-total closed-walk obstruction,
branch projection argument and requested proof-review task. Retained R438
credit belongs to Ali Romman, Sagar Thakrar and the DreamingOfClouds/eumemic
PR589/PR555 lineage. The distinct direct-decoder floor remains Russell
Seligmann's PR757 and Cody Harris's PR761 work, following Joel
Pulikkan/GamingPuzzled's PR620; it is not a result of this audit. Original
notices and fuller attribution are preserved in `source/`.

Prepared for ToikY with substantial OpenAI Codex assistance, including separate
proof/source-check, oracle and review agents. This is written proof and exact
finite agent-checked evidence, not human or formal-kernel acceptance. New work
Apache-2.0; retained sources keep their original authorship and notice.
