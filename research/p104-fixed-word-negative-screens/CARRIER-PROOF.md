# Fixed-word sequential combination-carrier exclusion

This note concerns the 4,033 **leaking unit-injection classes** returned by the
pinned PR6045/PR6040 census on the selected PR6030 word. It does not concern every
helper split, every injection, or every correction mechanism.

The result is a scoped negative: none of these classes admits a repair by the
sequential zero-original-value, chart-local corrections defined below, with the
original events, paid MOVEs and owned lifetimes fixed. No improved paid profile
or new κ is claimed.

## Sources and contribution

The package source manifest authenticates the PR6030 word and the unmodified
vendored files. The word originates from DreamingOfClouds's PR6030, head
`772dd10a5859a1d15f4851feb371519789213ad8`, as retained in main
`721c03822c421b7f7fcbb2598993b947c4d88419`. Its compressed SHA256 is
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.

Josie Elliston's [PR6045](https://github.com/CrocSwap/integer-mult-bounds/pull/6045),
head `23abc00773a72d8e2b4e733b46c453b0f71f6368`, supplies the leak census, suffix
columns, and exact pure-subspace interface. Its inherited census is Nick
Petalas's PR6040 extension of Matarener's PR5994 and flyingviper's PR5718 split
shape. Their notices remain in the vendored source. PR6045 identified combination
carriers as an open direction after its individual-carrier screen.

The additions here are a small-kernel global prefilter, a full first-combination
chart screen, and a dynamic affine closure for the two survivors. The latter
includes combinations enabled by earlier corrections; it does not freeze the
available carriers to those of the uncorrected trajectory. The new code and
proof were prepared with substantial OpenAI Codex assistance under Apache-2.0.

## Model

Let `R_t` map the original 770 public inputs to all live register values after
event `t` of the original word. An owned register is a temporary zero-initialized
row; CLEAR removes its row. At a selected cut `i`, replace pivot register `p` by
a new independent scalar input `z`. Put `ell(x) = (R_i x)_p`. The modified state
can be written

`R_t x + beta_t (z - ell(x))`,

with `beta_i = e_p`. The original events propagate `beta` linearly. Let `V` be
the pivot group's final chart and `O` the public output roles whose final chart
is not `V`. The leaking classes have nonzero uncorrected `beta_final` on `O`.
A successful independent-target repair needs both

`beta_final|_O = 0` and `beta_final != 0`.

We allow an inserted rank-one correction

`beta -> beta + q e_r (c^T beta)`

at any original event seam, where `q` is rational, `c^T R_t = 0`, the support of
`c` lies entirely in one current chart, and receiver `r` is already in that
chart. The correction's combined source has zero value in the **original** word
and equals `(c^T beta)(z - ell(x))` in the modified word. It preserves the
reference matrix `R_t` under the substitution `z = ell(x)`.

This is an optimistic model. A linear combination is allowed as a single
operation; every same-chart receiver is allowed, including self/noninvertible
updates; coefficients need not be dyadic; and existing owned COPY/CLEAR events
may overwrite or erase the modified signal, even when that would violate a
modified word's zero/erasure obligation. These permissions enlarge reachability.
No construction,
native lifting, or extra paid operation is inferred from a relaxed possibility.

## Baseline kernel and its premises

Write `D_t = {c : c^T R_t = 0}`. The original public-input rank stays 770:
ADD and nonzero SCALE are invertible row operations; INIT adds a zero row;
COPY into a zero destination is equivalent to ADD on `R_t`; and a CLEAR removes
a row dependent on the remaining rows. Consequently the kernel dimension is the
number of live owned registers, at most 13 for this word.

`carrier.py` explicitly transports a complete basis of `D_t`. An ADD
`row_r += a row_s` changes each kernel covector by
`c_s -= a c_r`; SCALE divides `c_r` by its nonzero coefficient; INIT adds `e_r`.
Before CLEAR it selects a kernel vector with nonzero `r` coefficient, eliminates
that coordinate from the other vectors, and drops that vector. This proves that
the removed row is dependent and that the transported basis remains complete.
MOVE changes chart membership but not the scalar rows or kernel.

The first pass independently replays every original row. It validates owned
lifetimes, every COPY destination's zero row, every operation's actual common
chart, nonzero SCALE, all MOVE endpoints and nesting, and final chart boundaries.
At every INIT/CLEAR and every globally surviving cut, it explicitly checks
kernel independence and `D_t R_t = 0`; the CLEAR dependency is checked before
removal as well. All checks raise exceptions and remain active under `python -O`.

## First two exclusions

**Global condition.** If every vector in `D_i` has zero `p` coordinate, then
`e_p` belongs to the column space of `R_i`. Thus `R_i x_0 = e_p` for some fixed
original-input vector `x_0`. Under the uncorrected suffix, `beta_t = R_t x_0`.
Every zero-original-value combination satisfies `c^T beta_t = 0`. No first
nontrivial allowed correction can occur, so a sequence of such corrections
cannot start. This excludes 4,009 classes and leaves 24.

**First chart-local condition.** For each of the 24 survivors, transport the
uncorrected signal through every later seam. At each seam compute the exact
intersection of `D_t` with each chart's coordinate subspace. If every resulting
covector annihilates `beta_t`, no first allowed correction exists. Testing a
basis is sufficient by linearity. This excludes another 22 classes.

The two surviving classes have pivot 572 and cuts after events 13637 and 13639.
Their first chart-local relation is `e_778 - e_572` at chart 595. This relation
alone does not prove that a useful repair exists.

## Dynamic affine enclosure

For each remaining cut, maintain an affine enclosure `b_t + W_t` of all signals
reachable by any finite correction sequence before that seam. Initially
`b_i = e_p` and `W_i = {0}`.

For every chart-kernel basis covector `c`, test its pairing with `b_t` and every
basis direction of `W_t`. If any pairing is nonzero, add all receiver directions
`e_r` at that chart to `W_t`. Repeat until no direction is added. A chart needs
activation only once per seam because all its receivers have then been added.
The loop terminates in finite dimension. The implementation explicitly checks
the resulting saturation property.

To prove soundness, suppose the enclosure contains every reachable signal before
one inserted correction. If `c` annihilates the enclosure, that correction acts
trivially. Otherwise the saturated direction space contains its receiver `e_r`,
so `beta + q e_r(c^T beta)` remains in `b_t + W_t`. Every allowed correction is
therefore covered, including ones made possible by preceding corrections. A
fixed-word linear event transports the enclosure to another affine enclosure.
Induction over all seams proves the necessary reachability claim. There is no
claim that every enclosed point is reachable by a legal finite program.

At each of the two cuts, the first closure adds the six receiver directions
`127, 572, 581, 582, 731, 778` at chart 595. No later saturation adds a direction.
After the suffix, the correction space has dimension 5 and its projection onto
`O` also has rank 5. The affine offset belongs to that correction space. Hence

`(b_final + W_final) intersect {beta : beta|_O = 0} = {0}`.

Both classes fail the necessary nonzero independent-target condition. Combined
with the preceding two exclusions, this closes all 4,033 leaking classes in
the stated model. The census also contains 390 single-leak classes; all of them
are removed by the global condition.

## Terminal certificate and controls

The final rational basis is included in the semantic output. A separate dense
suffix implementation checks the original pivot column. A five-by-five minor
on protected roles `116, 120, 127, 134, 176` has nonzero determinant, evaluated
by the independent Leibniz formula. Solving that minor expresses the affine
offset in the final basis, and the expression is checked in all 770 output
coordinates. The wrapper compares deterministic semantic outputs; runtime and
environment metadata are separate.

Controls include a snapshot creating a kernel relation, an independent pivot
with no such relation, inverse transport through ADD/SCALE, rejection of COPY
over a nonzero row, rejection of zero SCALE, a stale MOVE and duplicate CLEAR,
and a singular terminal minor. The dynamic positive control has original rows
`x=y` and `u=v`: writing the first carrier `y-x` into `u` enables a later carrier
`v-u`, which then reaches a previously unavailable receiver. A concrete two-step
sequence is checked. The static test misses that opportunity, and the dynamic
closure includes it. An affine-offset negative control prevents replacing the
affine terminal question by an unconstrained homogeneous span question.

## Open next questions and boundaries

The result does **not** exclude programs whose combined corrections temporarily
change the original scalar map and restore it later. In particular, it is not
a theorem about arbitrary multi-time noncarrier operations. It also excludes
from its claim changed unit injections, changed original events, new or moved
paid transitions, changed owned lifetimes, new storage, and different words.
Those changes require separate source, delivery, restoration and complete
paid/target accounting. No further search along those directions is claimed
here. A useful reopening condition is a concrete changed premise with a fully
priced repair; repeating this exact fixed-word carrier search is unnecessary.
