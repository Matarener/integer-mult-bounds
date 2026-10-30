# Independent acquisition, preservation and allowance audit

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

This audit receives the source word and coefficient matrix only after the package's source authentication. `cost.py` imports no predecessor executable. It separately recounts every event of the retained words and checks the candidate's literal acquisition and restoration events. Indices below are zero based; intervals exclude their right endpoint.

## The current query is not free at the recovery cut

In the canonical PR #2707 word, the eight-register `B1_current_query` body begins at event 696 and ends at 1593. Its registers F0 through F7 have their final CLEAR-to-identity events at 1585 through 1592. The first stage-2 future map is event 1714. Thus this actual query has been retired before the future recovery cut. `ACQUISITION.json` records each register's initialization, last accumulation, last read and retirement.

Copying its eight values into separate initialized owned registers would require at least the explicit proposed acquisition of eight CLEARs and eight unit ADDs (80 scalar allowance), followed by cleanup or output restoration. This is a conservative price for that proposed copying schedule, not a universal lower bound. Eight selected Z_U destinations have eligible delayed definitions, but that eligibility does not implement or validate a retained-query decoder.

The selected candidate does not retain or reacquire Q1. It preserves the original prefix, including the paid Q1 computation and retirement, and reads the actual corrected W fields. Consequently the source prefix's T contribution and the residual `Q2(X_T) - M21 Q1(Y)` are still present. The separate residual and full symbolic replay checks are required for the algebraic assertion; this audit checks that all of those literal inputs and prefix operations were retained.

## All real inputs and output restorations are paid

`selected_acquisition` checks the candidate recovery window [1694,2498). It contains exactly one acquisition of each of the 104 actual W sources: all 96 U ports and all eight T ports. Each acquisition has an immediately preceding CLEAR in the current frame, a unit copy from the actual W source, the forward stage-2 map for that port, and its negative line operation. These 104 source copies therefore retain 104 CLEARs, 104 unit ADDs, 104 cover maps and 104 H1 children. The scalar part of acquisition alone is 1040. Eight distinct query hosts additionally receive their explicit query-frame CLEARs, costing 16 scalar allowance.

All temporary roles use ten distinct existing Z_U output banks: Z1, Z2, Z3, Z4, Z5, Z6, Z8, Z9, Z10 and Z11. Their original CLEAR/X-copy definitions have no intervening source-word use and are delayed. The candidate restores every definition with its charged CLEAR and X copy in [2498,2518), immediately before the literal 1195-event source suffix. This accounts for 20 restoration events and scalar allowance 100 already included in the full count. These ten definitions are moved, not eliminated.

The source interval [1714,2628) is replaced; all other events are retained literally except those ten delayed definitions. The candidate prefix contains 1694 events after deferral. No candidate event writes a borrowed X or Y bank. The future window has no private BEGIN/END body and contains no private-query or borrowed-Y input. Outside the ten hosts its only writes are the eight paid response deposits into owned W banks. All 224 owned output banks remain required. The full package replay must separately verify exact values, phase frames, borrowed-input preservation and output completion.

## Independent scalar recount

| Whole literal word | Unit ADD | Quarter ADD | CLEAR | Scalar allowance | H1 | Wrappers | Maps | Private peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PR #3985 | 1920 | 896 | 536 | 27184 | 224 | 448 | 352 | 16 |
| PR #4015 | 1920 | 896 | 416 | 26944 | 224 | 448 | 352 | 16 |
| Paired-source candidate | 1820 | 896 | 416 | 26144 | 224 | 448 | 352 | 16 |

The inherited scalar tariff is 8 per unit ADD, 12 per quarter ADD, and 2 per CLEAR. Thus the candidate's total is `1820*8 + 896*12 + 416*2 = 26144`. Its complete word has 3713 events, compared with 3813 in PR #4015. The independently checked two-symbol identity has 48 pairs agreeing in three supported rows and four pairs agreeing in two. The future query's 416 unit ADDs become 316; the whole-word change against PR #4015 is exactly 100 fewer unit ADDs and scalar allowance 800 less. No native or map savings are claimed.

The second scratch host E does not supply an additional CLEAR saving against PR #4015. Its terminal standalone cleanup disappears only because its tenth delayed output definition provides the charged restoration. The whole-word CLEAR count is still 416. This distinguishes the actual 800 saving from an incorrectly claimed 802 saving.

## Falsification controls and scope

Eight independent controls reject a borrowed-Y substitution, omission of a T source, omission of a source CLEAR, reversal of a source map, a free query initialization, omission of an output restoration CLEAR, an unpriced half ADD and a native line inside a private scope. These controls establish sensitivity of this acquisition/cost checker; they do not replace the full symbolic replay or native-kernel checks.

The counted reduction is a constructive logical scalar allowance. Physical address movement, frame/tag access, native workspace exclusivity, producer coverage, recursive weighted cost and both supplier caps remain unpaid or unproved here. Arithmetic reassociation changes the numerical operation graph, so PR #4043's unchanged-graph precision transfer cannot simply be reused. A decoder-specific precision and range certificate remains necessary. No decrease of selected kappa, no global physical dominance and no completed recursive supplier follow from this audit.

Predecessor credit: PR #2707 supplies the canonical complete source word and tariff; PR #3985 supplies the recovery-fusion comparison; PR #4015 supplies streamed recovery and delayed output hosting. Exact source heads and byte pins are recorded by the integrated package's provenance manifest. The new contribution is the paired-query arithmetic reduction, while this independent audit establishes its charged acquisitions, full U/T retention, literal prefix/suffix preservation and exact scalar difference.
