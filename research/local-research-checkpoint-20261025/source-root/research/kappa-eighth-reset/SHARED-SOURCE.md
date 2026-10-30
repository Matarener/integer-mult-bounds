# Shared sources: a bounded encoded-interface test

Douglas Colkitt, with OpenAI Codex assistance. 2026-10-10. Apache-2.0.

**No new supplier or κ.** Static source caches are already covered by the
previous factorization screen. Two actual changes to source encoding also
fail in the models below: one pair, and the smallest central-null quartet.
These are local admission tests, not complete compiled networks.

This follows the [two-candidate reassessment](REPORT.md). Delaying scalar
cleanup, moving targets to center frames, and matched encode–decode circuits
were already closed in earlier reports; none is rerun here. The experiment
retains the characteristic-dependent central/side identity and instead
changes what the central producer receives from the original sources.

## Fixed accounting and favorable allowances

Use the folded-five-cube code C and its sixteen rational rank-one labels in
dimension six. C has binary rank six; its columns are distinct and nonzero.
The side contribution is S=I+C over F2. All original side injections may
happen before source recoding. The altered central producer may subsequently
use the new coordinates, and inverse recoding restores the sources at the
full frame. These chronological allowances are favorable to the proposals;
no full producer circuit or complete tape implementation is supplied.

The retained shared cover has ambient width 18 and rank deficit

    Δ = 32 − 3(L_center + L_extra).

Here L_extra includes extra source transitions or transformed dependent
copies, even when they are reused for arbitrarily many reads. Copies do not
earn independent-role capacity. All rank obstructions below grant optimal
other paths and arbitrary scalar factorizations of the remaining central
map. The producer after recoding remains conservative: each channel's frame
contains the images of every source frame from which it collects a value.

The preceding audit established maximum original-label support by span rank

    rank:     1  2  3  4   5   6
    support:  1  2  4  6  10  16.

The new checker re-establishes those bounds. With at least six nonempty
channels and total rank at most nine, their support capacities sum to at
most eleven. At rank ten they can sum to fifteen. This is an optimistic
coverage bound: repeated coverage is counted repeatedly, and an arbitrary
scalar factorization attaining it is not asserted.

## Static caches do not enlarge the earlier model

Copy source i from its rank-one frame to zero, costing one rank unit,
and reuse it for all central outputs. Charge no return on the erased copy.
This is just a singleton channel in an overcomplete factorization of C,
which the previous screen already allowed. Hence total loss remains at
least eleven, and Δ≤−1.

An independent subset check considers all 65,536 cached-source choices.
For each it computes the binary rank of the remaining columns, lower-bounds
the uncached collection loss from the support table, and adds one per cache.
The best resulting lower bound is eleven. This confirms an application of
the existing obstruction; it is not a new mathematical exclusion.

## One encoded pair

Choose distinct i,j. At their common rank-two span M, replace x_i by
x_i+x_j, retaining x_j. The central coefficient of coordinate j becomes
C_j+C_i; all other columns stay unchanged. All columns remain nonzero and
the code still has rank six. The original side map plus this recoded central
map still equals I. Undo the row addition at the full frame after all reads.

Allow the other fifteen original inputs to be injected before their sources
move. Whichever new line is assigned to the encoded input, those unchanged
fifteen labels must still be covered. At least six central channels are
needed. The support bound above therefore gives L_center≥10.

Three variants distinguish costs that must not be conflated:

* **Contract the original encoded source to a line.** Its path has ranks
  1,1,5 instead of the minimum five; the other source has ranks 1,4.
  The extra charge is two, giving combined loss at least twelve.
* **Keep the original at M and lower a dependent copy to a line.** Grant
  free reuse and erasure. This costs only one extra rank unit, giving total
  loss at least eleven. This cheaper option also fails to save rank.
* **Read the encoded input at M without contraction.** Grant zero extra
  source rank and ideal batching of every data path. With six auxiliary
  roles and center loss ten, the zero-gauge lower-bound moment already is
  `1.00227037021713 > 1` at saving **1/256**, below the saving required for
  κ=1/256. Additional zero-gauge stock cannot fix it. This last rejection
  is target-specific and assumes the stated zero-gauge compiler, unlike
  the preceding nonpositive-deficit conclusions.

All 240 ordered pairs are checked with exact rational projectors, binary
central/side identities, and inverse source restoration. These are local
controls and optimistic cost screens, not a full framed producer replay.

## The first central cancellation: four sources

There are no dependent pairs or triples of scalar columns. There are
exactly sixty dependent four-sets. Each has scalar rank three and its four
rational address lines span a nondegenerate three-space M.

For a quartet and a chosen pivot p, set z_i=x_i+x_p for its other three
members, retaining z_p=x_p. Since the four scalar columns sum to zero,
the pivot's central coefficient disappears. The other three central
columns remain independent. This actually eliminates a central input;
it is not just a delayed cleanup operation.

All four sources can move to M and later to the full frame monotonically,
paying 2+3 ranks each, equal to their minimum five. The row additions and
their final inverses are pointwise at those common frames. The twelve
untouched scalar columns still have rank six.

The obstacle is the cost of the three surviving encoded streams. First
keep them at M. Any conservative factorization needs at least six channels.
Its restriction to these three inputs has rank three, so a nonsingular
minor matches the three inputs to three distinct collecting channels.
Each of those channels has frame rank at least three. The other three
nonempty channels cost at least one each. Thus L_center≥12.

Now grant one independently transformed copy of each encoded stream, of
frame dimensions t_1,t_2,t_3 in {0,1,2,3}, reused for every consumer. Its
transform from M costs at least 3−t_i. No inverse transformation or new
independent stock is charged for that copy.

If every t_i is positive, the same matching argument gives

    L_center ≥ 3 + t_1+t_2+t_3,
    L_extra  ≥ 9 − t_1−t_2−t_3,
    L_center + L_extra ≥ 12.

If any t_i=0, allow that zero-frame copy to broadcast directly, without
counting it as a positive-rank channel. The twelve untouched inputs alone
still require six channels and loss at least ten by the support bound.
The zero-frame copy costs at least three, giving total loss at least thirteen.
Thus **all 64 dimension choices fail**, including uncontracted readout.

The checker verifies all sixty quartets, all four pivot choices, exact
common-span projectors, scalar identities and source restoration, and the
64 cost bounds. The best lower bound twelve gives Δ≤−4. Arbitrary dirty
workspace cannot improve this favorable bound: even a free implementation
of its restoration would not remove the charged source/copy and center
costs. No physical arbitrary-workspace implementation is asserted here.

## Decision

Stop this local source-recoding family here. The first real scalar
cancellation exists, but the surviving summaries are wider; lowering them
separately merely moves that cost from collection to the copies.

This does not rule out several interacting recodings, a joint operation on
multiple encoded streams, cancellation-aware nonconservative frames, or
a different recursive interface. None is a surviving construction from
this pass. A further run needs an explicit joint operation that avoids the
separate per-stream conversion bill, with a complete restoration contract.
Increasing the number of these independently lowered blocks is not yet
justified by a favorable budget. The retired inventory remains retired.

Reproduce the finite checks with:

```sh
python3 -B research/kappa-eighth-reset/shared_source.py
```

`shared-source.json` pins the checker and its matrix/rank dependencies.
These are exact finite checks plus the scoped arguments above, not a Lean
formalization or an independent verification of the multiplication theorem.
