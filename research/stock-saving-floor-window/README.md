# Floor-stable denominator shifts of the recorded bootstrap savings

**Finite certificate; no new κ and no stock coefficient.** On the frozen selected
bootstrap receipt, the twenty-four floor integers published by the cutoff chain
do not select one rational saving. Each branch's recorded `common_saving` may
move by a short explicit run of printed denominator units without changing any
`floor(s L_j - L_{j-1})` or `floor((1-s) L_{j-1})`.

```sh
python3 -B research/stock-saving-floor-window/verify.py
```

Expected:

```text
PASS_STOCK_SAVING_FLOOR_WINDOW native_k=-2..1 native_shifts=4 conservative_k=-86..15 conservative_shifts=102 binding=stage7_margin coefficient=unresolved no_new_kappa
```

Python 3.10+. The only live input is
`research/selected-bootstrap-stock-audit/RESULT.json`, SHA-256
`f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917`.

## Statement

Write `s` for a branch's recorded `common_saving`, with printed denominator `D`,
and write `s_k = s + k/D` for an integer `k`. Let `L_1 < ... < L_7` be that
branch's recorded cutoffs. The twelve floor values are

```text
margin_j(k) = floor(s_k L_j - L_{j-1}),
room_j(k)   = floor((1 - s_k) L_{j-1}),
```

for `j = 2..7`.

- Native branch (`bootstrap`): these twelve integers agree with `k = 0` if and
  only if `k` is in `{-2, -1, 0, 1}`. The shifts `k = -3` and `k = 2` change
  the stage-7 margin and no earlier stage.
- Conservative branch: the same holds if and only if `k` is in
  `{-86, -85, ..., 15}` (102 shifts). The shifts `k = -87` and `k = 16` change
  the stage-7 margin.

Both endpoints of each interval are forced by the stage-7 margin alone. Every
other margin and every routing room allows a strictly larger integer interval.
Dropping the stage-7 margin widens the intersection.

## Why the stage-7 margin is the whole window

Let `M = s L_7 - L_6`, `f = floor(M)`, and `{M} = M - f`, so `0 <= {M} < 1`.
A shift changes the margin by `k L_7 / D`. The floor stays `f` exactly when

```text
-{M} <= k L_7 / D < 1 - {M}.
```

The two rational slacks `{M} D / L_7` and `(1-{M}) D / L_7` are not integers.
Their floors are `2` and `1` on the native branch, and `86` and `15` on the
conservative branch, so the integer solutions are `k >= -2`, `k <= 1` and
`k >= -86`, `k <= 15` respectively. The verifier recomputes those floors from
the receipt and checks that every other constraint's integer interval properly
contains this one. It also walks outward from `k = 0` by direct floor
evaluation until the first failure, and requires the two procedures to agree.
Every integer inside the interval is evaluated, not only the endpoints.

At `k = 0` the twelve floors on each branch reproduce the published cutoff
table, including the native stage-2 integer `2851485324488315` and the native
stage-3 integer `1015784602045963452130`. The recorded identity
`common_saving = 1 - gaps.stock` holds on both branches, and every
`actual_stock_coefficient` is null. Swapping the two branches' savings does
not preserve the native window.

## What this does not establish

This does not bind a stock coefficient, a routing-width factor `W_j`, or a
producer sentence. The receipt already stores one rational in each window; the
floor table also accepts the other shifts above. Choosing `k = 0` still
requires that stored field, or a separate producer identity. The complex
`m = 73` supplier, hosting, precision, and the selected frontier are untouched.
Selected κ stays `0.001672660197076918`.

One denominator unit of native shift is the sample already reported to leave
the floors fixed, and `10^10` units is a sample already reported to move
stages 6 and 7. The new fact is the exact first failure: native `k = 2` and
`k = -3`, conservative `k = 16` and `k = -87`, all four at stage 7 only.

## Reproduce

```sh
python3 -B research/stock-saving-floor-window/verify.py
python3 scripts/research_package.py --package research/stock-saving-floor-window --check-only
python3.12 scripts/research_package.py --package research/stock-saving-floor-window
```

## Open next questions

1. Which source sentence bounds a stage-`j` routing call into `A_{j-1}` by a
   factor whose log2 is at most `floor((1-s) L_{j-1})`? The smallest room is
   still the native stage-2 integer `4777557234646`. The floor window does not
   contain that sentence. The first step is to match the retained PR185/PR387
   cover-row text with such a factor.
2. Does any identity of the frozen PR1087 assembler, other than the stored
   `common_saving` field, exclude the nonzero shifts in these windows? The
   first step is one stage-7 margin comparison at `k = 1` and `k = -2` against
   the assembler recurrence rather than against `RESULT.json`.

## Credit

The cutoff table and the two named native controls are the stock-margin chain
on the selected bootstrap receipt. The one-unit and `10^10`-unit samples, and
the request to bind a single rational from floor granularity, are the later
independent tie-out of that table. The receipt and the fourteen cutoffs are
the selected stock audit of the PR1087 assembler. This package only delimits
the integer shifts that keep those floors.

No independent human review or formal kernel is claimed. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
