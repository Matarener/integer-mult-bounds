# Class-C campaign coverage through dimension dominance

**Scoped correction and conditional scheduling result; no geometric span pass.**
The source tables list particular covers, rather than their full upward closure
in flat dimension. PR #3315's initial audited head `c4fe4244b52bb9111b9117aba066229316fc58ab`
correctly finds a three-configuration literal cover
of the 16 coverable HARD rows. That is not the geometric campaign minimum:
**`6554` at target `T=7`, together with `5555` at `T=8`, would suffice** if both
complete uniform span checks passed. Row 37 remains outside this implication.

There is also a concrete correction to that head's all-row statement. Its named
literal set `{5544,5555,6554}` covers only **55 of the 64** table-coverable rows,
missing **4,5,6,17,20,28,33,66,69** (zero-based `row_idx`, exactly as in the CSV).
The literal minimum over all 70 source rows is four configurations, versus
three over the HARD subset. Both implementations independently find these
minima. The PR's vendored `rows70.csv` and the original help-package file have
the same Git blob, `ee12fc8e3c528a509a06274c3ed264508c2c06a8`.

After our advance claim, the author adopted dimension closure at head
`240e7f68c6be0cd7193abdd1d686ec5b90ab5355`, explicitly credited the observation,
and left the same-target substitution lemma as an open premise in the
[correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/2954#discussioncomment-19006436).
This package discharges that implication and retains threshold-aware certificates.
It does not describe the amended checker as still using literal incidence.

With the proved dimension transfer, **two configurations suffice conditionally
for all 64 table-coverable rows**: `6554@T6` and `5555@T8`.
This does not prove that either requested span bound is true, that a census will
finish, or that this plan is fastest. In particular, a lower target can increase
work or expose a crack; no CPU-hour saving is claimed.

## Precise implication and proof

Use the model in [DreamingOfClouds' discussion #2954](https://github.com/CrocSwap/integer-mult-bounds/discussions/2954).
For a binary flat `V` in `F_2^9`, let `Lambda(V)` be the P112 lines whose binary
labels lie in `V`. Thus `V subset W` directly implies `Lambda(V) subset Lambda(W)`.
For four
flats define `X(V)=union_i Lambda(V_i)` and

```
H(V) = { h : rank_F2(labels(Off(h) minus X(V))) <= 7 }.
```

A complete *uniform* span certificate for dimension tuple `b` at target `T`
means `dim_R span H(W) <= T-1` for **every** four-flat tuple `W` of those
dimensions. It is not a sampled pair, one orbit representative, or one shard.
We inherit the source row/config coverage assertions and Lemma B's implication:
a row with dimension `d` is excluded by such a bound at `T <= d` on a cover of
its required basis. We do not re-prove Lemma B or the original weight census.

**Extension lemma.** Sort both dimension tuples decreasingly. If `c_i <= b_i`
for all four indices, any tuple `V` of dimensions `c` can be extended, after a
permutation of roles, to `W_i` with `V_i subset W_i` and `dim W_i=b_i`.
All target dimensions are at most six, below the ambient nine. This model has
no requirement that the four flats be mutually disjoint. The union and `H`
are symmetric in the four roles.

Then `X(V) subset X(W)`. For every direction `h`, its residual labels outside
`X(W)` are a subset of those outside `X(V)`. Removing labels cannot increase
binary rank. Thus **`H(V) subset H(W)`**, and consequently the real span of
`H(V)` has no larger dimension. A uniform target certificate transfers to every
source tuple at the **same** threshold `T`.

The source's size budget remains explicit: for
`g(1..7)=(1,2,4,8,12,20,36)`, `sum g(6554)=52` and `sum g(5555)=48`.
Both meet the inherited budget `<=52`. The tempting single target `6555`
exceeds it (56). If a future model adds coupled-flat constraints, a particular
prescribed extension, or different access rules, this lemma needs reassessment.

This proof uses only a listed cover and flat extension; it does **not** require
the unpublished weight-multiset-to-config generator to be complete. The
geometric `s4z.c` consumes directions and flat dimensions, not the row CSVs;
recovering that generator remains a separate question.

## Exact campaign and source reconciliation

`RESULT.json` records all 169 ordered comparisons within the 13 listed
configurations, every resulting row incidence, both complete campaign witness
lists, and the exhaustive minimum-cover solutions. In each row witness, the
`source` cover is literally in that row; the `target` dominates it; the target
budget is at most 52; and `threshold <= d`.

| Target | Literal rows | Rows after dimension transfer | HARD rows after transfer |
|---|---:|---:|---:|
| 6554 | 39 | 62 | 15 |
| 5555 | 21 | 27 | 9 |
| Union | — | 64 | 16 |

The original #2954 totals are `6554:62`, `5555:27`, `6544:40`, `5554:23`,
`6543:16`. Our closure reproduces **all five**, so their earlier coverage
information retains credit. The new contribution is the explicit implication,
the correction to the recent literal scheduling claim, threshold-aware row
certificates, and independently implemented replay.

For the HARD table, assign every row except 35 and 37 to `6554@T7`, then row 35
(`d=8`) to `5555@T8`. For all table-coverable rows, `6554@T6` handles 62 rows;
rows 35 and 45 (`d=8`) go to `5555@T8`. Rows `3,12,24,37,54,61` have no listed
cover and remain unresolved here. No RRC assertion is needed for the all-row
implication. Calling the 17 rows HARD merely preserves the source classification;
its RRC exclusions remain under audit.

Within this **listed-alphabet dominance model**, two target configurations are
minimal: row 35 can be served only by 5555, and row 36 only by 6554. This is not
a minimum over all geometric proofs, unlisted configurations, or alternative
packing mechanisms. The literal HARD minimum is three, with four different
minimizers, not a unique named triple.

The target checker argument orders would be `(a,b,c,d)=(4,6,5,5)` for 6554 and
`(5,5,5,5)` for 5555. This package does not launch those expensive campaigns.
Using `T=8` for both fails the required implication on HARD rows 7,8,13, whose
`d=7`; the receipt explicitly rejects that tempting weakening.

## Reproduction and evidence

```sh
python3.12 -B research/class-c-dominance-campaign/verify.py
python3.12 -B research/class-c-dominance-campaign/independent.py
python3.12 -B scripts/research_package.py --package research/class-c-dominance-campaign
```

Standard library only; each direct check takes less than a second on the local
Mac. `verify.py --write` regenerates the deterministic receipt. Ordinary replay
compares the complete regenerated object to its committed bytes and checks
four rejecting certificate mutants: weaker threshold, false dominance, invented
source cover, and over-budget target. Positive controls retain valid extension
and both admissible target budgets.

The separately written `independent.py` uses injective permutations of flat
roles, not the primary sorted-coordinate test, and independently enumerates
minimum covers. It compares the complete incidence object and checks both
threshold plans. It shares source data and the stated model; it is not an
independent geometry, RRC, human, or proof-kernel audit. Both scripts use explicit
exceptions, so their acceptance checks remain active under `-O`.

The two CSVs and help README are verbatim copies from DreamingOfClouds' commit
`1b25759bff5486293a9083ebbe0097b5f6642e08`. Exact original paths, SHA256 and Git
blob IDs are in `SOURCES.json.external_inputs`. Every replay authenticates the
three files. They are external byte pins, not generic runner Git-provenance rows;
the runner separately pins the selected record and originating task card at
main `463113d675af7410ac91d53a4fed51ec6494eb9a`. No pending Git objects are needed
for the direct scripts.

## Limits and credit

No actual four-flat span bound, new residue exclusion, exhaustive config-list
completeness, RRC proof, global decoder floor, physical/native consumer, supplier,
new kappa, or selected-frontier update is claimed. The conditional row coverage
and cardinality function are inherited. The full `s4z` campaign, historical
geometry censuses, selected cold replay, Lean and Docker were not run. This
small scheduling audit neither admits nor refutes those mathematical premises.

Credit **DreamingOfClouds** for the help package, original coverage counts,
geometry, Lemma B/kill criterion, and #2816/#2826/#2862 lineage;
**muatfannajm-dot / PR #3315** for the literal table audit and explicit
completeness handoff; **Tekalign / PR #2975 and #3000** for the separate
requirement and mask-filter accelerations; and the retained source contributors.
Written by **Krzysztof Wojt with substantial OpenAI Codex assistance**, including
Luna agents for source/overlap extraction and the separate combinatorial check.
Apache-2.0; original input attribution is retained.

## Open next questions

1. Can either required uniform span bound actually be proved or falsified?
   Start with a bounded exact witness search for 6554 at T=7 (T=6 for all rows)
   and 5555 at T=8; stop at a real crack before proposing a full campaign.
   Geometry and direction-list completeness remain separate inherited premises.
2. What exact rule generated the sparse row/config incidence list?
   Obtain its original generator and test completeness; `s4z.c` does not contain
   that row-weight rule. This package only closes the missing monotone implication.
3. Does a smaller target at a weaker permitted threshold cost less in practice?
   Compare bounded identical slices with exact coverage preserved. Two target
   configurations alone do not prove a runtime advantage over three.
