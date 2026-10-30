# The F′ certificate ceiling on P120 is 360/17

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped proof with an exact finite certificate. No new κ,
supplier or frontier change.**

[PR #2962](https://github.com/CrocSwap/integer-mult-bounds/pull/2962)
(DreamingOfClouds, `research/decoder-certificate-ceilings`, §2.1) proves that
every linear rank-counting certificate in its larger family **F′** gives at most
**24** on the E8 unit P120, and records as OPEN whether the sharper Theorem C
value **360/17** also bounds F′. This package settles that item for P120:

> Among all sets of `k` lines of E8, the least number of frames meeting the set
> is **765** for `k = 8` and **701** for `k = 7`. Both are attained only by
> pairwise-orthogonal sets. Hence the least feasible uniform weight is
> `y = 8/765`, and the uniform F′ ceiling on P120 is
> `2025 · 8/765 = 360/17`.

With the predecessor's fake-decoder argument, every F′ certificate on P120
gives at most 360/17 ≈ 21.18, not 24. F′ is therefore no stronger than F on
P120 under this witness, and both stop far below the targeted floor 72.

## Model (unchanged from PR #2962)

`L` is the 120 root lines of E8. A frame is a maximal set of pairwise-orthogonal
lines. There are 2025 frames, each of size 8. For a set `D` of lines, `meet(D)`
is the number of frames meeting `D`. A uniform fake decoder puts weight `y` on
every frame and costs `2025 y`. For F′ it is feasible when

```text
y · meet(D) >= min(|D|, 8)    for every set D of lines.
```

PR #2962 takes `y = 8/675` from a Bonferroni bound and gets the ceiling 24.
Its script requires only `min(|D|-1, 8)` for non-orthogonal `D`. The result
below is the same under both forms, because every binding set is a frame.

## Proof

Write `μ_k` for the least `meet(D)` over `k`-sets and `p(D)` for the number of
non-orthogonal pairs in `D`.

1. **Incidences.** Every line lies in 135 frames, every orthogonal pair in 15,
   and no non-orthogonal pair in any frame (checked).
2. **Bonferroni.** `meet(D) >= 135k - 15·(C(k,2) - p(D))`. For `k <= 6` this
   gives `μ_k >= 135, 255, 360, 450, 525, 585`.
3. **Pair caps.** A frame meets 765 frames and any 7 of its lines meet 701. By
   step 2, an 8-set with `meet <= 765` has `p <= 7`. A 7-set with `meet <= 701`
   has `p <= 4`.
4. **Orthogonal cores.** By Caro–Wei, a graph on `k` vertices with `P` edges
   has an independent set of size at least `k²/(k+2P)`. Apply it to the
   non-orthogonality graph of `D`. Every candidate 8-set then contains an
   orthogonal triple, and every candidate 7-set contains an orthogonal 4-set.
5. **Symmetry.** The reflections in the 120 roots permute the lines and the
   frames (checked), so they preserve `meet` and `p`. Under the group they
   generate, orthogonal triples form one orbit and orthogonal 4-sets form two.
6. **Search.** Every extension of each orbit representative within the pair cap
   is enumerated exhaustively. The least meet is 765 for `k = 8` and 701 for
   `k = 7`. Every minimiser has `p = 0`.
7. **Ceiling.** `8/765` exceeds `k/μ_k` for every `k <= 7`, where the bound
   uses step 2 for `k <= 6` and `7/701` for `k = 7`. For `|D| >= 9`, `meet(D) >= μ_8`. The least
   feasible uniform weight is therefore `8/765`, and a frame makes it tight.
   `2025 · 8/765 = 360/17`.

**Positive control.** The same search on E7 (63 lines, 135 frames of size 7)
reproduces the predecessor's MILP minima 55, 62 and 68 for `k = 5, 6, 7`. There
the least meet 68 is below the frame value 71, attained by sets with six
non-orthogonal pairs. So the search does find non-frame minimisers where they
exist. It also shows that uniform weights cannot reach Theorem C's 945/71 on E7.
That gap does not occur on P120.

## Reproduce

From the repository root, with the repository interpreter (CPython 3.12.15,
standard library only):

```sh
python3.12 -W error -I -B research/e8-fprime-uniform-ceiling/verify.py
python3.12 -W error -I -O -B research/e8-fprime-uniform-ceiling/verify.py
python3.12 -B scripts/research_package.py --package research/e8-fprime-uniform-ceiling
```

Expected: `PASS_E8_FPRIME_UNIFORM_CEILING mu8 765 ceiling 360/17 no_new_kappa`.
Each run takes about 35 seconds. `--emit` prints the recomputed
[RESULT.json](RESULT.json). A normal run requires byte equality with it.
The checks use `require()`, so they stay active under `-O`. A rejecting
control confirms that weight `8/766` violates a frame's constraint.

## Scope and limits

- Uniform frame weights only. A non-uniform F′ certificate is bounded by this
  witness. Whether 360/17 is the exact F′ optimum is not decided.
- P120 only. P112, where the proven F′ ceiling is still 15968/667, is not
  computed.
- Theorem C, the F′ constraint form and the fake-decoder argument are cited
  from PR #2962. They are not replayed here.
- This is a statement about certificate families. It gives no decoder floor,
  supplier, invoice or κ.

## Open next questions

1. **P112.** Does 15968/757 also bound F′ on P112? First step: the stabilizer
   of the removed frame acts on the 112 lines. Use it with these pair caps and
   orthogonal cores for `k = 7, 8`. Blocker: P112 is not line-transitive, its
   1996 maximal orthogonal sets have mixed sizes, and no generators are
   supplied here.
2. **Non-uniform optimum.** Is 360/17 the exact F′ optimum on P120? First
   step: an orbit-reduced linear program over W(E8) orbits of line sets, with
   an exact dual.
3. **E7 and E6.** On E7, uniform weights stop at 945/68 because a non-frame
   7-set meets only 68 frames. Can non-uniform weights reach 945/71 there?

## Credit

DreamingOfClouds's PR #2962 supplies the certificate families F and F′,
Theorem C, the fake-decoder argument, the F′ constraint, the Bonferroni
ceiling 24 and the E7/E6 MILP values used as a control. The charging
certificate shape is from #1977 and #798, as credited there. Those results are
cited, not rechecked. The new contribution is the exact least meets for
`k = 7, 8`, the orbit-reduced proof that frames minimise them, and the
resulting 360/17 ceiling for F′ on P120. No predecessor credit line or frozen
package is changed. Independent human and formal proof-kernel review are
unclaimed.
