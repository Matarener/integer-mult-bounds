# Boundary-arithmetic row-field movement

Scoped lemma for one layout step of the #4100 Gaussian caller. No new κ.
The selected conditional result stays `0.001672660197076918`.

## Caller

The sentence under audit is the boundary-arithmetic movement, not the union
schedule's head travel.

- `research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md`, "Batched right-hand
  sides do not add a large transpose", and the earlier exposure step: pad only
  the exposed field to its next power of two, at a factor below two, and remove
  that padding before the next axis. Move only that polynomial-width row field,
  at `O(log p)` times the boundary volume, not a transpose of the long spectator
  field. Scan each factor page once per right-hand-side batch.
- `research/unconditional-batched-crt/GAUSSIAN.md` repeats the removal claim:
  temporary padding of the one exposed polynomial row field is removed before
  the next axis and never accumulates as `2^g`.
- `research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md` step 5 charges
  the same movement to the boundary-algebra row and says it is not part of the
  union movement.

PR #4327 audits the union schedule's tape-head bound and leaves
boundary-arithmetic batching uncovered. PR #1731's rectangular review says
partial-batch padding is negligible. It does not prove the factor, the level
count, or the removal alternative. This note proves those three layout claims.
It does not prove the Strassen or rectangular exponent, the carving identity
that turns the movement into `O(V d W^{τ-1}/B)`, conditioning, or any ledger
row of #4100.

## Lemma 1 — the row-field pad factor is below two

For an integer `a ≥ 1`, let `M(a) = 2^{ceil(log2 a)}`. Then `a ≤ M(a) < 2a`,
and `M(a)` is a power of two.

If `a` is a power of two, `M(a) = a < 2a`. Otherwise `2^{k-1} < a < 2^k` for
`k = ceil(log2 a)`, so `M(a) = 2^k = 2 · 2^{k-1} < 2a`.

Thus padding the exposed field from `a` real positions to `M(a)` multiplies
that field by a factor strictly less than two. The factor `2` is not attained
for any finite `a`.

## Lemma 2 — batches in `[W, 2W]` add no cells when `R ≥ W`

Let `W ≥ 1` and `R ≥ 0` be integers.

- If `R = 0`, there are no batches and no added cells.
- If `R ≥ W`, write `R = qW + r` with `q ≥ 1` and `0 ≤ r < W`. When `r = 0`,
  use `q` batches of width `W`. When `r > 0`, use `q − 1` batches of width `W`
  and one batch of width `W + r`. Then `W < W + r ≤ 2W − 1`, every batch lies
  in `[W, 2W]`, the widths sum to `R`, and the number of added cells is `0`.
- If `0 < R < W`, the only batch is padded from `R` to `W`. The number of added
  cells is `W − R < W`. The ratio `W/R` may exceed `2`.

PHASE-LAYOUT calls `R` superpolynomial and uses a polynomial bandwidth `W`.
Under `R ≥ W`, which is the asymptotic regime that hypothesis names, the final
batch does not need padding. "Padded once at constant cost" is not an `O(1)`
record-move bound. The proved added volume in the small-`R` case is less than
one full batch.

## Lemma 3 — moving only the short field costs `O(log a)` passes

Let the exposed field have length `a ≥ 1` and let the orthogonal index have
length `N ≥ 1`. The orthogonal index may contain the batch coordinate and any
spectator coordinates. The boundary volume of real records is `V = a N`.
Pad the exposed field to `M = M(a)` and let `V+ = M N`. Store the padded
records row-major: row `r`, then the orthogonal index.

Merge adjacent row blocks by the lockstep schedule. At a stage whose current
block holds `span` original padded rows, a node is two adjacent blocks. Pass 1
copies the two children apart. Pass 2 writes, for each orthogonal position,
the first child's `span` records and then the second child's `span` records.
Each pass moves every padded record once. There are `log2(M)` stages because
`M` is a power of two and `span` doubles from `1` to `M`. The forward movement
is therefore exactly

```text
2 · log2(M) · V+
```

record-moves. The reverse schedule, splitting each suffix-major chunk back
into the two children, has the same count and restores row-major order. The
number of stages is `ceil(log2 a)`. It depends on `a` and not on `N`, the
batch width, the spectator length, or the number of axes `g`.

By Lemma 1, `V+ < 2V`, so the forward count is strictly less than
`4 · ceil(log2 a) · V` when `a ≥ 2`, and it is `0` when `a = 1`. In all cases
the forward-plus-undo count is strictly less than `8 · max(1, ceil(log2 a)) · V`.
When `a` is polynomial in `p`, `ceil(log2 a) = O(log p)`, which is the stated
movement bound: `O(log p)` times the boundary volume.

A transpose whose stages instead follow the orthogonal index has
`ceil(log2 M(N))` stages. Whenever `N > M(a)`, that is strictly more stages
than the short-field schedule. A spectator of length `2^g` is the long index
this schedule does not transpose.

After the solve, drop the `M − a` pad rows. Undo uses the real field length
only in the sense that the pad rows are not part of the tensor address: they
are tape cells deleted before the next axis. The real record count returns
to `V`.

## Lemma 4 — removal does not accumulate across axes

Process axes of lengths `a_1, ..., a_g` one at a time. While axis `i` is
exposed, the live volume multiplier is `M(a_i) / a_i < 2`. After its pad cells
are deleted, the multiplier returns to `1`. The peak multiplier over the whole
sequence is therefore below `2`, and the final multiplier is `1`, for every
`g` and every tuple of lengths.

If the pad coordinate is retained, the final multiplier is
`∏_i M(a_i) / a_i`. For `a_i = 3`, this is `(4/3)^g`, which is unbounded in
`g` and already greater than `2` at `g = 3`. Lemma 1 says each factor is
below `2`, so the retained product is below `2^g`, but it still grows
exponentially whenever every factor is at least `4/3`. The sentence "never
accumulates as `2^g`" is the removal schedule. It is false for the retained
schedule.

## Lemma 5 — one factor-page scan per batch

Under the partition in Lemma 2, the number of factor-page scans is the number
of batches. It is not the right-hand-side count `R`, except in the special
case where every batch has width `1`. It is not multiplied by `g`: each axis
is a separate window, and this count is inside one axis.

## What remains inherited

The identity "Strassen `W^ω` per `W` right-hand sides gives
`O(V W^{ω−1} polylog p)`", and #4100's later form
`O(V d W^{τ−1}/B polylog p)`, need the carving, the relation between the
exposed length and `W`, and the exponent `τ`. PHASE-LAYOUT already assigns
stability and the no-pivot factor theorem to the phase-assembly branch.
#4100's Gaussian paragraph uses `τ = 45/16`, while its union-schedule ledger
uses `τ_eff = 2 + 10^{-64}`. This layout lemma does not choose between them.

A finite execution of the schedule corroborates the exact move count, the
padding inequality, and the removal alternative. The statements above are
integer identities for every positive size named in their hypotheses, not
sample checks.
