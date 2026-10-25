# The fixed `L/2` firing set is not monotone in length

**Theorem for `n = 4` at lengths 14 and 16, plus a finite `n = 5` census. No new κ.**

Selected conditional κ stays `0.001672660197076918`. This does not decide `f(7)` and does not run `survey(7, 18)`.

## Definitions

The walk is `q_0 = 0`, `q_{i+1} = q_i XOR e_{w_i}` on `F_2^n`. A word of even length `L` is simple when its `L` prefix states are distinct, and restored when the walk returns to `0`. It is universal when those states sum to `F_2^n`. Counts in this note are canonical first-occurrence words, matching #3699 and #3733.

For a nonzero linear functional, let `s` and `t` be the sizes of the two level sets inside the prefix-state set, and let `d = (s - t) / 2`. The collision excess is the sum, over the two level sets, of `C(k, 2)` minus the number of realized nonzero differences. The fixed substitution uses

```
base(n, L) = (L/2) * (L/2 - 1) - (2^{n-1} - 1)
```

instead of `base + d^2`. The functional fires when `base < excess <= base + d^2`.

The firing set at `(n, L)` is the set of masks that fire on at least one canonical universal word.

## Affine 3-flat excess

A level set of a nonzero linear functional on `F_2^4` is an affine 3-flat. Translation and linear isomorphism do not change difference excess, so every such flat has the same subset excesses as `F_2^3`.

On the full 8-point flat, each of the 7 nonzero differences occurs in exactly 4 pairs. The excess is `C(8, 2) - 7 = 21`. Deleting one point removes exactly one pair from each difference, so a 7-point subset has excess `C(7, 2) - 7 = 14`.

The 6-point maximum is not a one-line multiplicity count. There are `C(8, 6) = 28` subsets. `verify.py` evaluates every one, and every smaller size, and obtains

| `k` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| max excess | 0 | 0 | 0 | 0 | 3 | 3 | 8 | 14 | 21 |

## Theorem

Every 14-point subset of `F_2^4` is sound for every nonzero linear functional, and so is the full 16-point space.

The complement of a 14-point set has two points. They lie in one level set or in different level sets, so the split is `(8, 6)` or `(7, 7)`. The excess is therefore at most

```
max(21 + 8, 14 + 14) = 29.
```

`base(4, 14) = 7 * 6 - 7 = 35`, and `29 < 35`. The false-prune inequality never holds.

The full space splits as `(8, 8)`. Its excess is `21 + 21 = 42`. `base(4, 16) = 8 * 7 - 7 = 49`, and `42 < 49`.

The simple-word census is not an extra hypothesis of this bound. It shows the bound is not vacuous: there are 392 canonical simple restored words at `(4, 14)`, every one universal, and 112 at `(4, 16)`, every one universal. None of them fires.

## Monotonicity fails at `n = 4`

Recomputed canonical firing sets:

| `L` | closed | universal | false prunes | firing masks |
|---:|---:|---:|---:|---|
| 8 | 29 | 22 | 44 | 9 of 15 |
| 10 | 110 | 110 | 190 | 10 of 15 |
| 12 | 314 | 314 | 150 | 13 of 15 |
| 14 | 392 | 392 | 0 | none |
| 16 | 112 | 112 | 0 | none |

The sets at lengths 8, 10 and 12 are strictly nested. Lengths 14 and 16 are empty, so the length-12 set is not contained in the length-14 set.

One witness is enough to see the drop. The canonical word `010201031213` has prefix states

```
0, 1, 3, 2, 6, 7, 5, 4, 12, 14, 10, 8
```

and returns to 0. Mask `1` splits them as `(8, 4)`, so `d = 2`, and the excess is 24. Then `23 < 24 <= 27`, and the mask fires. #3733 records 16 such words at `(4, 12)`. The theorem says the same mask fires on no 14-point set at all.

## `n = 5` does not copy that drop through length 16

The same enumerator reproduces the published per-mask tables at `(5, 12)` and `(5, 14)`, then classifies `(5, 16)`:

| `L` | closed | universal | false prunes | firing set |
|---:|---:|---:|---:|---|
| 12 | 3695 | 828 | 2856 | 24 masks, all of weight at most 3 except `11010` |
| 14 | 33922 | 24787 | 56686 | all 25 masks of weight at most 3 |
| 16 | 267890 | 263140 | 447912 | the same 25 masks |

So on this range the `n = 5` firing set is still monotone: the length-12 set is a proper subset of the length-14 set, and the length-16 set is equal to it. Mask `11010` is the unique weight-3 mask silent at length 12. It fires on 170 canonical words at length 14 and on 1728 at length 16. No weight-4 or weight-5 mask fires at either length.

The flat cap does not yet apply. A level set in `F_2^5` has 16 points, and a simple word of length 16 uses only 16 of the 32 vectors, so class sizes are not forced up against that cap.

## What is not claimed

The `n = 4` statement is a proof for every 14-point and 16-point set, not only for walks. The `n = 5` statement is a finite census of canonical walks. Neither one repairs a retained seven-label exclusion, and neither one says the firing set eventually becomes empty for every `n`.
