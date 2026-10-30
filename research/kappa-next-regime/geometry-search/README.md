# R437 five-replica packing blocks and complete word refinement

The current construction in [pool35-word/](pool35-word/RESULT.json) combines
the finite T35 owner allocation with the complete A/C word refinement from
[word-search](../word-search/README.md). Its full-fallback bit root satisfies

\[
0.001736847843363802786320 < c <
0.001736847843363802786321.
\]

The strict lower endpoint exceeds Rohan Arun's PR3959 pooled T32 endpoint by
**0.000000109192274856733636**. The two new contributions are separately
retained so their gains can be checked:

| Construction | Strict lower endpoint | Gain over preceding row |
|---|---:|---:|
| PR3959 pooled T32, original R437 word | 0.001736738651088946052684 | — |
| T35 packing, original R437 word | 0.001736740092896829241210 | 0.000000001441807883188526 |
| T35 packing, complete refined R437 word | 0.001736847843363802786320 | 0.000000107750466973545110 |

Every row includes its retained bad-class fallback envelope. These are finite
construction and price results. The parent continuation owns the replica-aware
native and physical caller, complete coefficient invoice and outer admission.
Its [complete word invoice](../COMPLETE-WORD-INVOICE.json),
[native review](../native-catalogue/WORD-REVIEW.json), and
[controlled physical probe](../word-search/PHYSICAL-PROBE.json) provide those
checks and state their limits. This directory does not independently claim
an unconditional all-size multiplication theorem.

## The change

The source is ai-nanachi's R437 word and chronological slot allocation from
PR3647, pinned through PR3959. Each of its nine calls has 437 arbitrary-dirty
helpers of width 8. Its per-replica slots have capacities 7, 14, 28, 42 with
multiplicities 666, 444, 444, 444. The window 6 allocation has one family
carrying two helpers, 209 families carrying five, and 12 empty families.

R437 has63 unused width8 places per replica. Rohan Arun's T32 pooling leaves
\(32\cdot63=403\cdot5+1\) places, requiring one exceptional partial slot.
Choosing a positive multiple of five replicas removes that residue. T35 stays
within the same15-bit physical-family index as T32:

\[
W=35\cdot888=31080,\qquad
W_{\mathrm{physical}}=31080+9=31089<2^{15}.
\]

The construction partitions35 replicas into seven groups of five. In each
group, leave the first replica's two-helper family in place. Transfer the
eight helpers in the four other replicas' two-helper families into the first
replica: three fill its partial family and five fill one empty family. This
uses only window6-to-window6 moves. Every moved helper retains its stage,
identity and width; the destination pair is inactive throughout its window.
Eight moves per group give56 moves total. All seven groups are disjoint.

The complete per-group idle delta is

\[
\Delta n_2=2,\qquad \Delta n_{26}=-5,\qquad\Delta n_{42}=3.
\]

The rank mass is unchanged. The subsequent word refinement changes only A
and its literal cleanup C. It keeps all 437 helpers, the exact boundary
frames, all source and scatter lists and the same absolute owners. Its
complete local profile is

\[
\{1:1322,\;2:1342,\;3:74,\;4:46,\;5:103,\;6:10,\;7:18\}.
\]

The local change relative to the original word is
\(2H_1-2H_2-3H_3+3H_4+H_5-H_6\). Three last-use aggregates are retained
until their explicitly emitted cleanup, saving six scalar ADDs in the full
word. See the word package for the exact gates and arbitrary-dirty restoration
proof. `build_word_pool35.py` lowers the actual changed word independently,
compares both resulting IR programs against its freshly exported native
records, and binds every call to the new local hash.

The complete current T35 bill, counted from those two native IR programs and
every absolute helper/idle owner, is:

| Paid rank | Number of children |
|---:|---:|
|1|416430|
|2|437829|
|3|23310|
|4|30030|
|5|32445|
|6|18690|
|7|28980|
|42|441|

There are315 local calls,137655 hosted helper roles,69930 idle children and
988155 paid children in total. The rank mass is1977885; the normalizer is
\(64\cdot31080=1989120\), leaving raw deficit11235. All9 private center
fields remain charged. There are no additional helper banks.

The same 15-bit family index does **not** establish an unchanged coefficient
or precision charge. Cross-replica binding changes the caller. The new word's
exact local L1 bounds are 49347 forward and 1113510 reverse. All regular
payload owners stay within one of seven disjoint groups of five replicas;
each group contains 25 forward calls, 20 reverse calls and 90 binary bridge
shear layers. Every shared private COPY payload is clean on entry and return.
Consequently the explicit block bound is

\[
P_5=2^{90}\,49347^{25}\,1113510^{20}.
\]

This is an 882-bit bound charged at 896 bits. It allows coefficient growth
across all 45 calls of a block; it does not reset the norm of regular dirty
helpers after each call. Other blocks have no payload access to that block,
so their effect is bounded by taking the maximum across blocks. A completely
sequential product over all 315 calls remains a 6171-bit fallback. The parent
invoice also charges the chosen lifted two-level coefficient explicitly.

[BLOCK-PREFIX-REVIEW-WORD.json](BLOCK-PREFIX-REVIEW-WORD.json) checks the exact
block separation, bridge rows, new IR norms and private closure. It states
the inherited local-cover/permutation and scratch contracts. This reasoning
does not supply the remaining universal physical primitive proof.

## Exact fixed-slot optimum

The new construction attains the fractional lower bound for this unchanged
R437 slot model. `fixed_slot_ceiling.py` proves the bound for **every positive
integer replica count**, every clock and every owner arrangement in that model.
The optimum is attained exactly when five divides the replica count.

For \(g_a(r)=r(64/r)^a\), let
\(A_a=g_a(42)-g_a(2)\). Relative to a maximally filled slot, leaving
\(u\) width8 places unused in a capacity\(c\) slot costs

\[
d_a(c,u)=g_a(c\bmod8+8u)-g_a(c\bmod8).
\]

The checker proves
\(5d_a(c,u)\ge uA_a\) for all nine nonzero patterns of capacities14,28,42,
uniformly for \(0<a\le1/100\). Eight comparisons are strict; equality holds
for the empty capacity42 slot. The proof uses exact outward rational
logarithm/exponential bounds and an explicit Taylor remainder. It specializes
mightyOil's PR1281 slack-concentration proof to this actual pure-width8 stock.

Every allocation has exactly63T unused places. Summing these inequalities
gives a lower bound attained by \(63T/5\) empty42 slots when5 dividesT.
The idle profile per replica is exactly

\[
\{2:2157/5,\quad4:444,\quad6:444,\quad7:666,\quad42:63/5\}.
\]

All1998T idle remainders remain positive, so the number of paid children and
the bad-class surcharge are unchanged by the rearrangement. Thus the same
bound applies to the complete moment, including fallback. At the displayed
upper endpoint the lower moment bound exceeds1, excluding that endpoint
for the whole fixed-slot family. The unchanged proof was rerun with the
refined word's actual local profile and current endpoint in
[POOL5-WORD-ALL-T-CEILING.json](POOL5-WORD-ALL-T-CEILING.json). Thus the packing
ceiling is also exact for the new word. The result does not exclude further
changed native words, helper widths, bank templates, slot capacities or
controllers.

## Files and verification

`build_pool5.py` authenticates the predecessor template, verifies its exact
replica symmetry before extending it, emits the T35 calls, and substitutes
only the56 declared helper owners. It derives the paid local profile directly
from both IR programs and checks every absolute role and idle prefix.
`pool35/` contains the full compressed template, the complete absolute owner
and idle inventories, the move list and the original word's exact price
receipt. `pool35-word/` separately retains the definitive complete word
variant. Its owner inventory, idle inventory and move list are byte-identical
to `pool35/`; its local programs, local hashes and source record hash are
regenerated from the actual changed word.

The template's `hosting.slots` and `hosting.remainders` retain the source's
per-replica metadata for provenance. The `pooling` record marks those fields
as predecessor metadata. **The new owner map is the complete `calls` array;
the new idle bill is derived from those absolute owners.** Consumers must
use `IDLE-INVENTORY.json.gz` or reconstruct the same absolute occupancy.

`review_pool5.py` imports neither the builder nor either predecessor pooling
implementation. It independently reconstructs all calls, derives the windows
from the chronological controller, verifies its exact eight-register scalar
identity, checks all137655 helper roles using coordinate bitmasks, recounts
all IR/idle children and prices the result with the separately retained
base-two interval engine. Nine semantic and endpoint controls are rejected.
This is independent implementation within one AI-assisted session, not an
independent human review or formal verification of multiplication.

Reproduce from the repository root, selecting fresh output paths:

```sh
python3 -B research/kappa-next-regime/geometry-search/build_pool5.py \
  --out research/kappa-next-regime/geometry-search/replay-pool35
python3 -B research/kappa-next-regime/geometry-search/review_pool5.py \
  --candidate "$PWD/research/kappa-next-regime/geometry-search/replay-pool35" \
  --out research/kappa-next-regime/geometry-search/replay-review.json
python3 -B research/kappa-next-regime/geometry-search/fixed_slot_ceiling.py \
  --candidate "$PWD/research/kappa-next-regime/geometry-search/replay-pool35" \
  --out research/kappa-next-regime/geometry-search/replay-ceiling.json
python3 -B research/kappa-next-regime/geometry-search/build_word_pool35.py \
  --out research/kappa-next-regime/geometry-search/replay-pool35-word
python3 -B research/kappa-next-regime/geometry-search/fixed_slot_ceiling.py \
  --candidate "$PWD/research/kappa-next-regime/geometry-search/replay-pool35-word" \
  --out research/kappa-next-regime/geometry-search/replay-word-ceiling.json
python3 -B research/kappa-next-regime/geometry-search/block_prefix_word.py \
  --candidate "$PWD/research/kappa-next-regime/geometry-search/replay-pool35-word" \
  --out research/kappa-next-regime/geometry-search/replay-word-prefix.json
```

These commands use Python's standard library. They leave predecessor scopes
and source snapshots unchanged. Output gzip containers are not mathematical
identities: the receipts bind canonical decompressed JSON. The scripts refuse
to overwrite their declared output paths. `build_word_pool35.py` deliberately
uses the retained original `pool35/` as its pinned owner input; the changed
word and fresh native records must already exist in the bundled word package.
The frozen source-manifest writers require absolute `--candidate` paths,
as used above. [REPLAY-DEPENDENCIES.json](REPLAY-DEPENDENCIES.json) inventories
the exact source closure, including both interval engines, the authenticated
physical caller and its external inputs.

## Sources and credit

- **ai-nanachi, PR3647:** R437/OQ4 native word, complete local IR, chronological
  template, original owner allocation and inherited finite invoice. The source
  keeps Ali Romman/PR1043, Sagar Thakrar/PR3700/2423/1023, eumemic,
  DreamingOfClouds, DaysSky and the native/hosting/compiler predecessor credit.
- **Rohan Arun, PR3939/3959:** cross-replica owner pooling, T32 R437 moves and
  its conditional endpoint. This continuation does not claim that mechanism
  or endpoint as new work.
- **Philipp / mightyOil, PR1281:** exact mixed-width slack-concentration
  optimum, its uniform Taylor proof and its named source lineage. The new
  all-T pure-width8 specialization uses this prior insight.
- **Chris R / Clear1nsight, PR3995:** explicit replica-indexed IR binding and
  the physical catalogue's symmetry obstruction. It is the parent native
  caller continuation's immediate interface predecessor.
- The two exact arithmetic engines are retained from
  `research/native-complex-moment552/engines/`, preserving their original
  sources and notices.

New construction, implementation and review were prepared under the user's
direction with substantial OpenAI assistance. Apache-2.0.

## Open next questions

1. Read the parent native, coefficient and physical receipts for their
   completed coverage. Finite catalogue checks and a controlled physical probe
   do not establish every inherited all-size physical primitive contract.
2. Improve the actual R437 local word or its width-8 helper inventory again.
   The complete A/C refinement demonstrates that this lever remains productive.
   Increasing T or searching more clocks cannot beat the fixed-slot optimum
   for that fixed word. Any new signature must include its dirty restoration,
   native frame and helper costs before its price becomes a construction.
3. A genuinely changed geometry must alter a hypothesis of this slot model.
   Added banks or changed phase increments require a new productive count,
   complete local/idle profile and physical routing; their costs cannot be
   imported from this T35 certificate.
