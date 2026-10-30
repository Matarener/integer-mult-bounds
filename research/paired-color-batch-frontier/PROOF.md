# Exact batch/color tradeoff for paired targets

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Model and theorem

There are `m >= 1` colors and two distinct targets of each color. A grouping
partitions all `2m` targets into nonempty batches of size at most three.
Targets can be reordered without restriction in this mathematical model.
Write `B` for its number of batches and `I` for its number of color incidences:
each color present in each batch contributes one. Each batch uses the same
fixed reservoir width. For positive prices `A,C`, its declared bill is

```text
E = A B + C I.
```

The exact undominated frontier is

```text
B_min = ceil(2m/3),
B_min <= B <= m:     I_min(B) = 2m-B.
```

In particular, batch count and color incidence cannot both attain their
separate minima when `m >= 3`: the minima are `B_min` and `m`, and `I=m`
requires at least `m` batches. The assertion excludes `m=1,2`, when
`B_min=m` and both minima are attained together.

## Lower bound

Let `u` be the number of colors whose two targets occur in one batch. Each
of these colors contributes one incidence. Every other color contributes
two, because it has exactly two targets. Consequently `I=2m-u`.

A capacity-three batch cannot contain two whole color pairs: that would
require four targets. Thus `u <= B`, giving `I >= 2m-B`. Independently,
capacity gives `B >= ceil(2m/3)`, and every color occurs somewhere, so
`I >= m`. If `B>m`, the grouping is dominated by putting each pair in its
own batch, which has `(B,I)=(m,m)`.

## Attainment at every integer frontier point

Fix `ceil(2m/3) <= B <= m`, and put `s=m-B`. Put a whole pair of each of
the first `B` colors into its own batch. There are `B` batches of size two.
The remaining `s` colors have `2s` targets. The capacity condition implies

```text
2s = 2m-2B <= B.
```

Place these `2s` targets in `2s` distinct batches, one additional target
per batch. In particular, the two targets of any remaining color use
distinct batches. No batch has more than three targets, all targets occur
exactly once, and exactly `B` colors are unsplit. Thus `I=2m-B`.

Every listed point is undominated: reducing `B` increases the minimum `I`.
This proves the full frontier, including an explicit construction.

## Exact positive-price optimum

For every grouping, an attaining frontier grouping is at least as cheap.
On the frontier,

```text
E(B) = 2m C + (A-C) B.
```

If `A<C`, its unique optimal pair of statistics is `(m,m)`; each batch is
one whole pair. If `A>C`, its unique optimal pair is
`(ceil(2m/3), 2m-ceil(2m/3))`. If `A=C`, every frontier point ties, and
non-frontier points are more expensive. These conclusions cover arbitrary
positive real prices; the checker uses exact rational instances.

## Sharp exchange-only consequence

Cinna Davis's CRT.md section 3 uses three reservoir placements and their
three inverses per batch. Section 4 uses twelve H-bit shuttle exchanges
per occupied color. Taking these counts as the declared exchange-only
tariff, fix the same H in every batch and price one H-bit exchange as one
unit: `A=6`, `C=12`. Additions, preparation, routing and repair are excluded
from this sub-bill. The optimal exchange bill is `18m`.

Even the best grouping among those using the minimum number of batches
has bill `24m-6 ceil(2m/3)`. The ratio to the unrestricted optimum satisfies

```text
(24m-6 ceil(2m/3))/(18m)
  = 4/3 - ceil(2m/3)/(3m)
  <= 10/9.
```

Equality holds exactly when `3` divides `m`. The case `m=3` is explicit:
write the two targets of color `a` as `a0,a1`, and similarly for `b,c`.

```text
minimum batches: {a0,a1,c0}, {b0,b1,c1}     B=2, I=4, E=60
minimum bill:    {a0,a1}, {b0,b1}, {c0,c1}  B=3, I=3, E=54
```

Repeating this family gives equality for every positive multiple of three.
Thus minimizing batch count can impose an avoidable penalty of exactly
`10/9`, even after color occupancy is optimized within that batch count.
Equivalently, the better grouping removes one tenth of the former exchange
sub-bill in these examples.

## Application boundary

unpaidmoon's PR #5538 prices occupied colors, but does not optimize the
joint batch/color statistics. This proof adds that optimization for the
stated paired-target, capacity-three model. It does not revisit the
predecessor's color count or production numbers.

The same-width premise matters: shrinking H with the number of targets
changes the objective. The unrestricted grouping premise also matters:
actual CRT batches obey tree, control-reservoir, chronology and placement
rules. Placement can change the position-mod-K colors themselves. This
proof neither constructs a valid physical regrouping nor asserts that a
current production layout has this color multiset or capacity. A full
cost comparison must also retain all other operations and their prices.

No new kappa, native operator, supplier admission, selected-frontier
change, formal proof-kernel result or complete multiplication theorem
follows. The ingredients are elementary partition counting; no claim of
literature priority for general colored packing is made.
