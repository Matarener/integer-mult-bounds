# The fixed L/2 firing set at n = 5 beyond length 16

**Claim type: a scoped proof for L ≥ 26, plus an independent census through
L = 24. No new κ.** It answers #4322's open question 1: at `n = 5` the first
length at which every functional is sound is **26**. The selected conditional
κ stays `0.001672660197076918`.

## Object

[PR #4322](https://github.com/CrocSwap/integer-mult-bounds/pull/4322)
(unpaidmoon) shows that the fixed `L/2` substitution's firing set is not
monotone in length at `n = 4`: it is empty at `L = 14, 16` by a flat-excess
cap. At `n = 5` it found the firing set still monotone through `L = 16`.

Its open question 1 asks: **for n = 5, which even length first makes every
functional sound?**

The model is #4322's:

- canonical first-occurrence words;
- simple restored prefix walks on `F_2^n`, universal when the difference set
  of the prefix states is all of `F_2^n`;
- a nonzero mask fires when `base < excess ≤ base + d²`, with
  `base = (L/2)(L/2−1) − (2^(n−1) − 1)`.

## Results

**1. Soundness from L = 26 (proof).** At `n = 5` a level set is an affine
4-flat. By enumerating all `2^16` subsets of `F_2^4`, the maximum excess of a
`k`-subset is:

| k | 0–3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| max excess | 0 | 3 | 3 | 8 | 14 | 21 | 21 | 30 | 40 | 51 | 63 | 76 | 90 | 105 |

A split `(s, t)` therefore has excess at most `e(s) + e(t)`. This cap is at
most `base(5, L)` for every split exactly from `L = 26`. So every functional
is sound on **every** 26-, 28-, 30- or 32-point subset, not only on walks. At
`L = 24` the cap leaves only the `(8, 16)` split. A firing word there must
contain an entire level set of its mask.

**2. Census through L = 24.**

| L | closed | universal | false prunes | firing masks |
|---:|---:|---:|---:|---|
| 12 | 3,695 | 828 | 2,856 | 24 |
| 14 | 33,922 | 24,787 | 56,686 | 25 (all of weight ≤ 3) |
| 16 | 267,890 | 263,140 | 447,912 | 25 |
| 18 | 1,737,048 | 1,737,048 | 1,812,996 | **28**: adds `27, 29, 30` (weight 4) |
| 20 | 9,019,738 | 9,019,738 | 5,357,220 | **30**: adds `15, 23` |
| 22 | 35,938,056 | 35,938,056 | 11,569,998 | **30**: every mask but `31` |
| 24 | 103,944,140 | 103,944,140 | 14,151,156 | **28**: `15` and `23` fall silent again |

- **Not monotone at n = 5 either.** The firing set stays nested through
  `L = 22`. At `L = 24` the weight-4 masks `15` and `23`, which fired at 20
  and 22, fall silent, and the all-ones mask `31` never fires. By the cap,
  every word that fires at `L = 24` contains an entire level set of its mask.
- **Answer.** Something still fires at `L = 24`, and the cap proves every
  functional sound from `L = 26`. So the first all-sound length at `n = 5` is
  **26**. This is two steps later than the length-14 collapse at `n = 4`.

**Agreement with the predecessors.** The census reproduces the published
per-mask rows exactly: #3699's `(4,8)`, `(4,10)` and `(5,12)`, #3733's
`(4,12)` and `(5,14)`, both on main, and #4322's new `(5,16)` row. It also
confirms #4322's `n = 4` silence at `L = 14, 16`.

## Method and independence

Nothing is imported from #4322.

- **`verify.py`**, standard library, rebuilds the 16-point flat caps, and
  reruns the census itself for every `n = 4` case and for `n = 5` at
  `L = 12, 14, 16`. That includes #4322's full `(5,16)` row, in about 50
  seconds.
- **`census.c`** is a separate C enumerator for the lengths Python cannot
  reach. Its recorded runs in `evidence/CENSUS-RUNS.txt` are bound to the
  source by SHA256. They match every published row and the Python census at
  `(5,16)`, and give the new lengths 18, 20, 22 and 24.
- **The C runs are local evidence.** CI reads them and does not recompile.
  `(5,22)` took about 17 minutes and `(5,24)` about 56 CPU-minutes.
- **Vendored file.** #4322's `verify.py` is vendored byte-identically only
  for its literal `EXPECTED_5_16` row, which is read with `ast.literal_eval`
  and never run.

## Not covered

- `(7, 18)` and `(7, 20)`, and `n ≥ 6`.
- Any change to a retained seven-label exclusion.

## Reproduce

```sh
python3.12 -B research/f7-firing-n5-length-census/verify.py
cc -O2 -o census research/f7-firing-n5-length-census/census.c && ./census 5 24
```

The first prints `PASS_F7_FIRING_N5_LENGTH_CENSUS` in about a minute.

## Open next questions

None for `n = 5`: open question 1 is decided. #4322's open question 3, whether
a larger `n` repeats a collapse after its firing set fills, now has a second
data point. At `n = 5` the set shrinks from 30 to 28 masks at `L = 24` and is
empty from 26.

## Credit

The model, the `n = 4` theorem and the open question are unpaidmoon's (#4322),
building on Nick Petalas's #3699 and #3733, Nicholas Stone's #2973 and the
PR943 walk. Prepared by Ryanson Jonathan with substantial Claude Code (Claude
Opus 5.5) assistance. Apache-2.0.
