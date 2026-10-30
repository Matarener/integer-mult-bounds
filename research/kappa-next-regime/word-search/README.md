# Three last-use covectors improve the R437 local bit supplier

The production word in `candidate/WORD.json.gz` changes the literal R437 bit
supplier from PR3647. Its complete local recursive profile is

```text
{1:1322, 2:1342, 3:74, 4:46, 5:103, 6:10, 7:18}.
```

Relative to the pinned R437 word, the exact change is

\[
\Delta=2H_1-2H_2-3H_3+3H_4+H_5-H_6.
\]

Rank mass remains 5,113. The word keeps all 437 helpers, 659 arbitrary local
input columns, 636 rational frames, source/target endpoints and nine paid
rank-seven COPY captures. It removes three scalar ADDs from A and three from
the emitted cleanup C. The complete native record stream contains 27,126
records and 24,202 ADDs, including all 527 scatter readers. The exact global
endpoint and complete physical owner invoice are separate results of the
parent continuation; this local package does not infer them from a histogram.

## Why leaving the carrier until cleanup helps

Suppose several target accumulators need `target ^= a` and `target ^= b`, and
helper `a` has no remaining observation after those consumers. First perform
`a ^= b`, then let each consumer read the aggregate once. The helper retains
its arbitrary initial dirty value. Its inverse operation is included in the
literal FULL cleanup C, after the productive observations finish.

This saves an intermediate undo and can let `b` skip a frame. It does not clear
dirty input or omit restoration. The ordinary H1–H5 interleaved interface
continues to hold, including the exact `C = U^-1` requirement. All three
changes share this mechanism, with different frame costs. `PROOF.md` gives
the exact observer and cleanup argument.

The successful aggregates, in current compact R437 register numbering, are:

| Aggregate | Existing rational frame | Removed consumers of the second source | Local profile change |
|---|---:|---|---|
| `463 ^= 322` | 122, rank 2 | 241, 340, 349 | `+H1 - H2 - H3 + H4` |
| `469 ^= 271` | 184, rank 2 | 444, 413 | `+H2 - 2H3 + H4` |
| `468 ^= 371` | 391, rank 6 | 413 | `+H1 - 2H2 + H4 + H5 - H6` |

The second change also raises the existing birth `469 ^= SOURCE92` from frame
94 to frame 184. SOURCE92's ordered frame path is unchanged; its existing
climb happens earlier. The full monotone trace checks its subsequent reads.
No SOURCE scalar operation changes. The three improvements compose exactly:
the seven nonempty subsets were each replayed, and the combined tariff equals
the sum of the three individual tariffs.

## Fixed production construction

`construct_bit_candidate.py` is the deterministic production applier. It has
no optimizer dependency. It authenticates the original PR3647 compressed and
canonical word, verifies all six removed scalar preimages and the one changed
birth, checks the three last-use observation lists, inserts the three literal
gates and regenerates C. It preserves the source's grouped gates except at the
actual insertion cuts. B and D are byte-equivalent JSON values; every field
other than A and C is unchanged.

```sh
python3 -B research/kappa-next-regime/word-search/construct_bit_candidate.py
```

The emitted word has canonical SHA256
`3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0`
and the recorded gzip SHA256
`ee42c58fb0cd23bad942ec472c7fb4f87db8261ce6ee4b2bc7e812212d8b836e`.
Regenerated gzip containers should be compared by canonical content if the
Python/zlib environment differs. Immutable source archives retain byte pins.

The scalar counts are A 2,130; B 934; C 2,629; D 17,982. The grouped A/C counts
are 2,086 and 2,585 because insertion cuts split some grouped multi-source
instructions. A group count is not the primitive ADD invoice.

## Completed native and independent checks

The unchanged PR3647 tools were run freshly on this production word:

```sh
python3 -B research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/vendor/xcheck_p.py research/kappa-next-regime/word-search/candidate/WORD.json.gz
python3 -B research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/vendor/export_records.py research/kappa-next-regime/word-search/candidate/WORD.json.gz FRESH_NATIVE/records
python3 -B research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/code/local_counter.py FRESH_NATIVE
```

`native/RESULT.json` records the exact executed commands, source hashes, outputs
and logs. The geometry audit checks all 636 closed rational frames. The local
word checker passes all 659 dirty input columns and H1–H5, as well as
`U_block_form`, `J_identity`, `K_equals_D` and `C_is_U_inverse`. The independent
record checker verifies every MOVE, common-frame ADD, nine COPY/ERASE
lifecycles, and all 881 columns of the five-stage controlled composition.

The emitted local forward and reverse L1 bounds are 49,347 and 1,113,510.
The five-stage payload bound is 93 bits, within its retained 104-bit charge.
The nine-stage and enclosing physical budgets must use these newly computed
values; a predecessor's numeric bound is not substituted. The record checker
is the source's independent Python checker, not a relabelled C++ receipt.

`candidate/PATH-DELTA.json` records the six changed helper paths. Every other
register's ordered path remains unchanged. The companion width thread completed
an independent review of this exact production word without importing the
discovery optimizer. Its receipt is
`../width-search/COMPOSED-WORD-INDEPENDENT-NATIVE-REVIEW.json`. In addition to
the scalar and frame checks, it reconstructs exact rational 8-by-8 projectors
and 16-by-16 gauge identities for all 26 distinct transitions on the changed
paths, including the nine new transition pairs. All nine complete raw COPY
rows, including arbitrary dirty columns, agree exactly with the source.
Missing-aggregate, stale-cleanup, underpaid-frame and missing-compensation
controls reject. Separate software/agent implementations are not independent
human review or a formal verification of integer multiplication.

## Actual nested physical protocol on the T35 template

The source-bound `physical_probe.py` adapts PR3967's retained fixed-role probe
to the exact new word and the complete 35-replica owner catalogue. It selects
the newly freed rank-42 IDLE at stage 6, replica 1, role 209, family 1,097
(request 965,276), then the COPY at stage 0, replica 1, frame 515
(request 4,518). This specifically exercises an owner changed by the pooling
construction and its explicit replica-indexed raw-field code.

```sh
python3 -B research/kappa-next-regime/word-search/physical_probe.py --output FRESH_PHYSICAL/PHYSICAL-PROBE.json
```

The explicit output path keeps the source package read-only. Omitting it
writes beside the script. `REPLAY-DEPENDENCIES.json` lists the nine internal
inputs and the unchanged external source authentication closure; beyond the
complete retained physical-caller tree and its pinned source-manifest files,
no additional external repository dependency is introduced.

`PHYSICAL-PROBE.json` records a passing actual two-level CALL/RETURN protocol,
with grants `2048 -> 1344 -> 147`. The native rank-42 and common rank-7 forward
adapters contain 7,666 and 4,936 commands. Exact ancestor coefficients at child
coordinates 0 and 146 both equal 2. The projected gap exponents are
`2*(2048-1344)=1408` and `2*(2048-147)=3802`.

The probe executes the complete 65-event COPY window at local positions
`[22011,22076)`, including all 63 actual private-result readers and the final
ERASE. The borrowed COPY source remains unchanged; consumers receive the
distinct returned private result. Both physical returns restore their parked
parents, program bytes, tape heads, numerical registers, output ports and
leased scratch. All borrowed fixtures are freed, and the final owned parking
marker is erased. The maximum number of scratch leases is ten.

The original wrong-parent, foreign-program and wrong-source gates reject.
The original obsolete-rank-34 and foreign-COPY-field controls also reject, as
do the added obsolete-rank-26 descriptor and foreign-replica-2 COPY field.
Every rejection happens before an invalid child handoff is accepted. The
unchanged source provenance loader authenticates the retained caller and bank
codec before execution.

This remains an explicitly controlled 46-bit payload with controlled child
outputs. It executes two physical calls and two returns, not the complete
GL64 residual payload or the full global macro word. The receipt retains
`complete_GL64_payload_executed=false`, `stock_is_controlled_fixture=true`,
`numerical_decode_disabled=true` and a zero complete-macro count. The finite
probe closes the selected actual source/owner/replica-to-runtime binding; it
does not discharge the inherited all-size realization assumptions.

## Discovery and scope of negative searches

The search began from the earlier complex receiver construction, then pivoted
to R437 when the refreshed PR3959 composition showed that the bit supplier
binds. No already-realized complex saving is counted here.

| Completed R437 screen | Cases | Outcome |
|---|---:|---|
| A source pairs with fixed old contacts | 4,391 | No positive candidate |
| A transposed receiver pairs with fixed old contacts | 2,091 | No positive candidate |
| B source pairs with fixed old contacts | 2,099 | No positive candidate |
| B transposed receiver pairs with fixed old contacts | 699 | No positive candidate |
| All the same pair graphs with joint frame assignment | 9,280 | No positive candidate |
| B last-use covectors, undo in C | 678 | No positive candidate |
| A last-use covectors, undo in C | 105 | Three positive candidates, all composed above |
| Equal-compensation two-helper prefix conjugations | 62 | No admitted width candidate |

The joint search added 118 exact rank-three and four rank-five flats to the
existing catalogue. They were generated by rational closure of graph lower
and upper bounds and checked against the 111 root lines. The existing scalar
graph's optimum did not change over this finite 758-frame catalogue. None of
the production word's gates uses an added frame; the production keeps only
the original 636 frames.

The pair catalogue admits all gaps in these words, observer-free consecutive
clusters of at most eight pairs, and the stated exact source/receiver identity.
These are bounded failed searches, not exclusions of other scalar graphs,
arbitrary rational subspaces, more carriers or changed interfaces. The price
optimizer uses floating arithmetic to nominate an explicit frame assignment;
all positive candidates then receive exact scalar and rational-path checks.
The complete admitted endpoint requires a separate exact price enclosure.

`DISCOVERY-SOURCE-VERSIONS.json` preserves the exact source version used by the
earlier 636-frame B-receiver pilot. A later debug-only assignment records
lower/upper bounds for diagnostics. The historical source is retained by its
byte hash under `source-versions/`; the old receipt is not rewritten. All
enriched searches and positive production discovery use the current source.

The prefix-conjugation experiment was also checked with exact rational
annihilators. Of its 62 named graphs, 35 have a zero entrance ceiling, ten have
a one-dimensional ceiling and 17 have a three-dimensional ceiling before other
constraints. Surviving directions need not contain a published root line.
Consequently the finite root-frame failure is not a universal obstruction to
nonroot rational entrance frames. No such generalized native width contract
is admitted here.

## Open next questions

1. Can a different last-use collection or a longer covector eliminate further
   paid stops after this composed word? A new search must use the current word
   and cannot recount these three events.
2. Can one of the surviving nonroot entrance directions be expressed by a
   complete native frame, compensation and owner contract? The current word
   schema stores frames as root-label subsets; extending it requires actual
   rational-basis transport and a full changed-width invoice.
3. Which all-size SOURCE, compiler, hosting and precision assumptions inherited
   from the selected construction can be discharged? Finite local/native and
   physical probes do not resolve those premises.

## Attribution

The dirty shared-covector mechanism is credited to Nick Petalas and the retained
joint-frame research. PR3647's R437 composition is credited to ai-nanachi, with
Ali Romman's PR1043 helper470 deletion and the original eumemic /
DreamingOfClouds punctured producer. Retain Dylan Crow's exporter/native work,
DaysSky's staged hosting, Sagar Thakrar's owner work, and all contributors and
notices in the source package. The preceding complex receiver continuation
also credits dataisfire and the full predecessor chain. New construction,
search, integration and explanation use substantial OpenAI assistance under
the user's direction. New material is Apache-2.0.
