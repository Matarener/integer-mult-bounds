# An in-place entrance completion for the actual P104 projection

The omitted P104 completion can execute at the original WORD entrance using
eight existing dirty output banks as accumulators. The new prefix supplies
the required output frames, restores every temporarily modified Y source,
and needs no additional Gaussian query bank. Follow it by the exact PR3446
projection to obtain the original word's complete endpoint map.

The omitted section changes from **473 native calls to 145**, at the same
rank mass **889**. Its native power tariff strictly improves for every
exponent `0 <= s < 1`. This is a local result. The resulting full dual profile
still rejects the selected target under the inherited five-forward/four-dual
consumer, even before its other nonnegative charges. The decision is to
retain the local interface and **pause dependent supplier construction within
that consumer model**. No selected-frontier update is proposed.

## What is new

[PR3462](https://github.com/CrocSwap/integer-mult-bounds/pull/3462) already
establishes the residual factorisation `R=CA/2`, its rank eight, and an abstract
dirty-helper completion. [PR3469](https://github.com/CrocSwap/integer-mult-bounds/pull/3469)
already supplies isolated omitted-bank endpoint adapters. This package binds
scalar acquisition to the original common empty frame, uses required output
storage in place of a private query bank, and interleaves exact native maps
with a concrete restored-source schedule.

The mathematical idea comes from Dumas and Grenet's
[In-place accumulation of fast multiplication formulae](https://arxiv.org/abs/2307.12712),
ISSAC 2024. Their general accumulation method is credited, rather than claimed
as new. The P104 contribution is its source-specific placement, exact Gaussian
domain, native phases, dirty compensation, and consumer-budget consequence.

The eight pivot outputs are `X0, X33, X101, X102, X11, X12, X15, X24`.
Their rows of C form the identity. For basis dirt b and other output dirt n,
the scalar section performs

\[
n\leftarrow n-C_Nb,\qquad b\leftarrow b+AY/2,\qquad n\leftarrow n+C_Nb.
\]

The final step uses the updated basis, so the dirt cancels correctly. The
whole pre-subtraction finishes before any basis update. Each of 103 active Y
fields is halved, used for its A column, and immediately doubled back. Y1 is
unused by this prefix, but remains required by the projection.

## Exact scope

The local prefix accepts the 93 omitted physical fields in B9 and all 104 Y
fields in 4B9, with their actual WORD entrance frames. Y must be temporarily
writable. Every Y returns in its entrance frame before the retained word
starts; all 93 outputs reach the required full final frame. The eight basis
banks are updated outputs, not borrowed helpers required to keep their
original contents.

For a common sufficient domain on which both complete programs execute
literally and exactly, take **104 Y fields in 4B9, all 78 N fields in 2B9,
and the other 176 public fields in B9**. This is not a minimal-domain claim.
The symbolic verifier proves every scalar increment is a B9 combination of
independent input variables and every private erasure is zero. With the
pinned PR3382 module and PR3416 native-covariance lemmas, this gives an
arbitrary-input implication on that product domain. The finite physical
fixture independently checks the new prefix; it does not rerun all
historical native correctness proofs.

`PROGRAM.json` contains the 1,238-operation prefix and 4,027 retained original
event indices. `NATIVE.json` contains its 53 distinct native recipes. Normal
verification reads and checks both exported artifacts, including their
agreement with regeneration, and executes the published schedule.

## Evidence and reproduction

Run from the repository root with Python 3.12 and no third-party packages.

```sh
python3.12 -B scripts/research_package.py --package research/p104-inplace-entrance
```

| Check | Coverage |
|---|---|
| Full symbolic endpoint comparison | All 128,164 coefficients of the 358-field map and all 358 final frames |
| Projection reconstruction | Separate graph and bitset implementations, 4,027 events, no omitted-bank reads or writes |
| New native certification | 53 maps, signed Pauli images, exact global-phase anchors, independent wrapper enumeration, and minimal ranks |
| Independent literal physical fixture | 93 dirty outputs plus 104 restored Y fields, all 100,864 Gaussian coordinates compared before hashes |
| Literal native arithmetic | 145 calls and 227,584 completed signed-floor pairs, each compared with its integral ideal output |
| Negative controls | Dirty preconditioning, source restoration, N100/Y1 divisibility, odd halves, module entrance, and wrong native phase |
| Cost implications | Exact native/scalar inventories, scalar width envelope, concavity comparison, and rational consumer rejection |

The complementary implementations are `primary.py`, `native.py`,
`physical.py`, and `invoice.py`. The compiler and separate Pauli/phase checker
are authenticated predecessor inputs. The physical and invoice engines import
no predecessor executable. `verify.py` captures source and implementation
bytes, rejects typed artifact drift, compares full arrays, and checks that
inputs remain unchanged. Normal and optimised replay are registered.

See [PROOF.md](PROOF.md), [COSTS.md](COSTS.md), and [RECEIPT.json](RECEIPT.json)
for the derivation and exact evidence. Timings are not proof fields.
Proof-assistant verification and independent human acceptance are unclaimed.

## Decision and alternatives

A simple clean-query entrance alternative would keep the 52 direct rank-eight
X maps, finish 41 other outputs, and take eight query fields from empty to full
and back. Its profile is `52H8 + (41 + 16)H9`, with rank mass 929, which is
40 above the omitted section. The dirty-output method avoids those query
return maps and preserves mass 889. It improves the local native tariff, but
the inherited consumer still fails its favourable relaxation.

This changes the scalar network and the placement of native calls. It is
outside [PR3594](https://github.com/CrocSwap/integer-mult-bounds/pull/3594)'s
fixed four-read commuting-retiming family. It does not materialise the
coefficient caller left open by [PR3577](https://github.com/CrocSwap/integer-mult-bounds/pull/3577).
The actual caller here is the WORD entrance followed by PR3446's projection.

## Open next questions

1. Can a changed **complete consumer or coverage law** use this local word and
   pass its own favourable cost screen? First supply a source-bound bill that
   explicitly changes a failed assumption, including the replacement cost.
   Actual owners, idle coverage, and finite widths remain blockers.
2. Can a changed scalar/native network reduce the remaining full dual tariff
   enough to alter that decision? First price the complete proposed delta,
   including source acquisition, return maps, and unchanged forward calls.
   A more concentrated abstract histogram is not a realised replacement word.
3. Is there an independently specified caller that benefits after width,
   routing, and monomial costs? First identify its actual physical banks,
   entrance frames, allowed temporary writes, and required observables. The
   local identity supplies no global ownership or all-size transfer theorem.

These are reopening questions, not automatic follow-on implementation tasks.
Structured questions and the stopping rule are in [TASK.json](TASK.json).

## Sources and credit

Canonical scientific base is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`,
priority revision 6. [SOURCES.json](SOURCES.json) pins the exact inputs and
historical task/selected record. All frozen predecessors remain unchanged.
The canonical investigation is
[Discussion 2750, comment 19014226](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19014226).

Credit Nick Petalas's PR3462 factorisation and PR3469 adapters, Hiroki
KUMAZAKI's PR3446 projection, the PR3382/3416 exact-module and native proofs,
ywz65's PR2586 WORD, and their geometry, channel, compiler, and rounded
arithmetic predecessors. Credit Dumas and Grenet for the general in-place
accumulation method. Credit Jose Manuel's original Discussion 2619 budget
finding and Vasek's PR2744 source/coverage audit, retaining Ross Richardson's
PR2458 forward profile and the paired-chain coverage lineage. PR3554/3577
supplied the assigned caller questions. No new rank-eight or lattice theorem
is claimed here.

Prepared by Clear1nsight with substantial OpenAI assistance from a root agent
and three concurrent specialist agents. New work is Apache-2.0. Archival
retention, successful replay, and scientific supplier admission are distinct.
