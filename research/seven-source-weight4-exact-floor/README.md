# Seven-source weight-at-most-four connector: exact 218-call minimum

**Finite census and construction in the fixed connector alphabet; no new κ.**
This independently audits [PR #4079](https://github.com/CrocSwap/integer-mult-bounds/pull/4079)
(nightangelflowerwin-ops, head `39a1fd620d1c702b72ab080ec11b090ea9ce98b7`) and
settles its open question #1. The answer is no: no length-20 restored source
path covers all 98 masks. The exact minimum is **218** complete calls, not
216.

## Model

The model is the fixed one-root dirty F2 connector contract of
[universal-connector-boundary](../universal-connector-boundary/README.md)
(PR #943), used unchanged by PR #2397, PR #3780 and PR #4079. A source word
`w` of length `L` is restored when each source occurs an even number of times.
Its prefix parities `q_0..q_{L-1}` give the available masks
`D(w) = {q_a ^ q_b}`. The targets are the 98 nonzero seven-bit masks of
weight at most four. A target with exactly two readouts must lie in `D(w)`.
Any other target needs an even number of readouts, so at least four.

## Results

| Statement | Status here |
|---|---|
| L=14: max 70/98, 2 classes | Python and C census agree (matches #4079) |
| L=16 (4,2⁶): max 79/98, 56 classes | C census (matches #4079); Python checks the witness |
| L=18 (6,2⁶): max 85/98, 51 classes | C census (matches #4079's 85) |
| L=18 (4,4,2⁵): max 91/98, 54 classes | C census (matches #4079's 91) |
| 6-source 12-event ceiling 48/56; 14-event (4,2⁵) ceiling 54/56 (14 classes) | Python and C census agree |
| **L=20 excluded** | new; see below |
| **L=22 cover exists** | new; Python checks the witness |
| **Minimum complete calls = 218** | new; follows from the rows above |

**L ≤ 20 is excluded.** Delete source `s` from a word. Each covered mask
that avoids `s` stays covered in the projection, so
`cov ≤ ceiling(projection) + 42`. Every restored profile with seven
sources and `L ≤ 20` has a deletion onto (2⁶) (≤ 48 + 42 = 90) or onto
(4,2⁵) (≤ 54 + 42 = 96), except (4,4,4,2⁴). For that profile, any full
cover projects onto one of the 8,576 full-56 (4,4,2⁴) classes. All
8,576 × C(20,4) = 41,550,720 lifts by four copies of a seventh source reach
at most **95/98**.

**L = 22 attains full coverage** with profile (6,6,2⁵):

```text
0 6 1 6 2 3 0 6 3 4 6 2 3 5 6 3 4 6 1 3 5 3
```

It needs 22 source calls plus 196 readout calls, **218** in total. This
lift is one of 572 found from the 32 full-56 (6,2⁵) classes.

**The floor of 218 holds for any even number of readouts per mask.** For a
word of length `L` covering `c` targets, the cost is at least
`L + 196 + 2(98 − c)`. With the bounds above, L = 14, 16, 18 and 20 cost at
least 226, 228, 218 and 218, and L ≥ 22 costs at least 218. The exact L=18
maximum of 91 raises the L=18 floor to 228. #4079 states 216 = 20 + 196. That
figure assumes L = 20 is attainable, and it counts only two readouts per mask.

## Audit of PR #4079

All of #4079's numerical maxima reproduce: 70, 79 (56 classes), 85, 91,
and the 54-coverage 6-source words named in its open question. Its
`verify.py` checks the L=12 and L=14 censuses and one witness per maximum. It
does not replay the L=16 maximum or the 14-event (4,2⁵) ceiling 54/56. That
ceiling is the step that excludes (4,4,2⁵) at L=18. The census here supplies
both. #4079 deduces the floor of 216 calls from `L ≥ 20`. That deduction is
valid but not sharp, because L = 20 is impossible.

## Reproduce

Registered replay (standard library, about 2 s):

```sh
python3 -I -B research/seven-source-weight4-exact-floor/verify.py
```

It recomputes the 48 and 54 projection ceilings and the L=14 census in Python,
with histograms required to equal the native rows. It enumerates every
profile with `L ≤ 20`, checks all witnesses and closed-form class counts, and
verifies the call-floor arithmetic. Controls include #3780's published
1,447,295,850-class domain, PR #2397's 144-call weight-≤3 cover, an
unrestored word rejection and an order-swap mutation.

Native census (about 1.5 minutes single-threaded; needs `cc`; not registered,
because package CI is stdlib-only). Write output outside the checkout:

```sh
python3 research/seven-source-weight4-exact-floor/run_census.py OUT_DIR --check
```

This rebuilds [CENSUS.json](CENSUS.json) from [census.c](census.c) and requires
byte equality. The weight-≤3 (4,4,2⁵) row reproduces #3780's 54 full
covers as a control.

## Scope and limits

- The upper bounds at L=16, L=18 and for (4,4,4,2⁴) come from one native
  enumeration, `census.c`. The Python replay independently covers only the
  cheaper censuses. A second implementation of the 1.4×10⁹-class and
  41.5×10⁶-lift steps would complete the independent check.
- These are exhaustive finite enumerations in the stated contract, not
  a formal proof. Changing the alphabet (pair-source calls, extra connectors,
  free frames) is outside scope.
- This is a side result in an excluded fixed alphabet. It changes no supplier,
  interface price, selected record or κ.

## Open next questions

1. **Independent native replay of the (4,4,4,2⁴) L=20 exclusion.** The
   L=20 step rests on one implementation. A second code path, such as a
   two-stage 5-source projection (51,975 classes) followed by lifts, would
   remove that single point of failure. No blocker.
2. **Does any downstream package rely on 216?** Search for uses of #4079's
   216 floor and replace them with 218. The first step is the overlap search
   on `seven-source` and `weight-<=4`.

## Credit

Predecessors: nightangelflowerwin-ops (PR #4079, PR #3780), commdata2338
(PR #2397), Cinna Davis / 1337isnot1337 (PR #2229, PR #2236) and Ross
Richardson (PR #943, connector contract). Prepared by Nick Petalas with
AI assistance. Apache-2.0.
