# Complete two-pivot caller readers and exact retiming bills

**Scoped caller result; no new κ or selected-frontier change.**

**Reviewer guide:** the [evidence index](EVIDENCE-INDEX.md) maps each retained
receipt to its replay role, distinguishes mathematical inputs and status-only
dependencies from archival-only receipts, and lists the loaded source modules.
All retained files, including archival evidence, remain required by the hash gate.

## Result

For every integer `q>=2` and `f>=1`, the displayed complete caller on
`n=2q+2` independent arbitrary banks has ambient arity `m=(4q+4)f` and
`H_(2f)=n^2+2, H_(4f)=1`. Its rank mass is exactly full stock plus `8f`.
Both dirty pivot inputs and every public-input reader are included. This
repairs the tempting prefix-only invoice, whose `2qf` deficit is consumed
by its complete tail.

Within the fixed ordinary native-product chart compiler, a six-bank word
has matching mass/stock `72f`. A certificate of 36 edge-disjoint odd
Eulerian subgraphs proves its all-chart lower bound `72f`. An eight-bank
word has matching mass/stock `128f`; no general n=8 lower bound is claimed.

Separate triangular and balanced changed eight-bank words have complete
baseline mass `138f` against stock `128f`. Saved exact quadratic choices
reduce each to `130f`. This is a useful local rank reduction, still an
unfavorable invoice. No optimizer is imported or trusted by replay.

## Proof and exact coverage

The [all-q construction and complete reader proof](source/caller/HANDOFF-FAMILY-PROOF.md)
uses a noncommutative scalar invariant, including raw-a repair, actual
source swaps and the two affine pivot readers. The
[tail derivation](source/native-frames/HANDOFF-FAMILY-TAIL-PROOF.md) retains
the ordinary factory supports. The registered command reconstructs q=2,3,4
fixtures on all original independent columns and checks both literal
inverse orders. The written induction supplies all q; finite fixtures
alone do not quantify over q.

The [fixed-compiler proof](FIXED-CHART-PROOF.md) derives the complete
chronological physical-word-to-graph cost identity for every chart choice.
The exact signed chart certificate checks every declared graph edge,
odd parity, Eulerian degree and global edge disjointness. A duplicate-cycle
mutant rejects. Triangular and balanced source circuits are independently
decoded into exact affine X-character monomials with Z4 phases. All four
f residue classes are retained, including the once-per-bank global phase.
Every saved retiming is recompiled from its fixed choices, compared with
the complete target, and checked in both inverse orders. Omitting a paid
query rejects. No broad search is rerun.

## Limits

The n=6 floor concerns exactly the retained ADD/ADDRESS/bank-SWAP
skeleton and native-product chart compiler. It is not a lower bound on
changed callers, source handoffs or nonmonomial charts. The retimed arity
invoices still need literal selected-native lowerings, contracting splits,
precision, source/COPY scans, chronological integral owners, storage and
fixed-tape realization before recursive supplier admission.

## Reproduce

From the repository root, on Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/two-pivot-caller-readers
python3.12 -B scripts/check_research_commit.py --package research/two-pivot-caller-readers --check-source-history
```

The registered manifest runs `verify.py` normally and with `-O`. Its direct
portable equivalent is `python3 -B verify.py` (or `python3 -O -B verify.py`)
from this package. The direct command needs only standard-library Python,
no Git/network and no original Ross-specific directory. `--json` prints the
complete replay summary. It writes no package files.

[BINDINGS.json](BINDINGS.json) retains every consumed original source/data
byte hash and explicitly records the path-only adaptations. Original versions
of adapted scripts remain under `original/`. Other source bytes and historical
receipts remain unchanged. Those receipts retain their old absolute provenance
paths; they are data, not required filesystem locations. The replay adapter
resolves only the explicitly retained original source inventory. Original lane
notes are archival and keep their original scope and attribution.

The source loader hashes and compiles the **same bytes**, never loads `.pyc`,
and compiles historical implementations with `optimize=0` in both parent
Python modes, preserving inherited assertions. Mathematical receipt comparison
omits only the enumerated provenance fields in `verify.py`; all such retained
input bytes are checked separately. A changed-source control rejects. Hashes
provide integrity against the trusted publication, not external authentication
or mathematical correctness. Git/source-history, export integrity, finite
replay, written proof, hosted CI and supplier admission remain separate.

## Related work and credit

Ross Richardson with substantial OpenAI Codex assistance, including separate
mathematical checking contexts and this packaging adapter. No independent
human or formal-kernel review is claimed. New work is Apache-2.0.

The Gaussian-dyadic compiler is inherited unchanged from icekylinx's PR531
through Rohan Arun's kernel92 composition. The exact original notices and
source ancestry are retained in `source/vendor/credits/`; they preserve
DreamingOfClouds, Dugongue, eumemic and the geometry/compiler lineage.

Chris R / Clear1nsight's PR3987 and ToikY's PR4002 retain credit for generic
native-lift phase/cocycle normalization and the need for exact signed/global
phase witnesses. This package makes no generic normalization priority claim.
Chris R's PR3989 and PR4045 are related explicit interface/volume-cost results;
their different fixed sources and theorems are neither imported nor claimed
as new here. These named overlaps were read at exact heads:

| PR | Exact head | Contributor |
|---|---|---|
| [#3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987) | `fc536202fdaa924158789a5ef59ac079bbe21922` | Clear1nsight |
| [#4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002) | `d593941ea0a4926021cba9d01fe60500579e464f` | ToikY |
| [#3989](https://github.com/CrocSwap/integer-mult-bounds/pull/3989) | `7b6dda7ab6ed10d608ecba357ac2f6924166d38b` | Clear1nsight |
| [#4045](https://github.com/CrocSwap/integer-mult-bounds/pull/4045) | `91afbb643f7f4ccf6f34b685ecd959eb790a0f94` | Clear1nsight |

[RELATED-WORK.json](RELATED-WORK.json) separately inventories the already
published PRs 3630/3632/3645/3649/3655 and separate BIT PRs 4021/4023.
Their publication is not supplier admission. This contribution neither
constructs BIT nor duplicates those results. The recent-PR/live-discussion
overlap has explicit partial coverage, not a proof of novelty.

## Open next questions

Can an explicitly completed changed pivot/factory/reader word remove the unfavorable rank mass without granting a free original-input reader? Keep every original bank independent and write the complete H/L terminal map before optimizing its paid native word. No favorable complete changed caller, compatible positive BIT supplier or complete joint outer transfer is supplied here.
The same question, relevance, feasible first step and blockers are in
[TASK.json](TASK.json).
