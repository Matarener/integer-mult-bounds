# Exhaustive check of #4373's carve Schur bandwidth, with an exact formula

**Claim type:** an exact structural lemma for every eliminated set, checked on every layout of
every path `n ≤ 15` for bandwidth `b ∈ {1, 2, 3}`. **No new κ.** It independently confirms
unpaidmoon's [#4373](https://github.com/CrocSwap/integer-mult-bounds/pull/4373), at head
`479a03d7967594e30427a8b2f9783cc10673a001`, and imports nothing from it.

## Lemma: boundary-order bandwidth of any carve

Take a bandwidth-`b` matrix on the path `0..n−1` with generic entries. Eliminate a set `E`
whose pivot blocks are invertible, and write the Schur complement on the survivors in
boundary order. Group `E` into components: consecutive eliminated indices at distance at most
`b` belong to the same component. Then

    bw(E) = max( max over components C of  #{survivors in [min C − b, max C + b]} − 1 ,
                 max over survivor pairs u < v with v − u ≤ b of their boundary distance ).

**Proof.** By the fill-path lemma (Rose–Tarjan), survivors `u` and `v` couple in the Schur
complement exactly when they are adjacent, or are joined through eliminated vertices only.
They are joined in the second way exactly when both touch one component `C`. Inside a
component, consecutive indices are at most `b` apart. So the survivors touching `C` are
exactly those in `[min C − b, max C + b]`, and their boundary-order span is that count minus
one. A survivor pair with no eliminated index between them keeps its original distance.
Generic entries make every structurally possible fill nonzero. Particular entries can only
cancel fill, so in every case `bw(E)` is an upper bound.

**Corollaries.**

- **#4373's theorem.** With at least `b` survivors between consecutive interiors, each
  interior run is its own component. Its rims lie in the separators, so it touches at most
  `2b` survivors. Hence `bw ≤ 2b − 1`, with equality exactly when some interior has `b`
  survivors on both sides (and trivially at `b = 1`). An interior at the end of the path gives
  at most `b`, matching #4373's prefix remark.
- **Necessity.** If separators hold only `b − 1` survivors, components merge into chains.
  - With `k` singleton interiors and `b` survivors at each end, a chain has
    `bw = 2b − 1 + (k − 1)(b − 1)`, which is unbounded.
  - #4373's own chain has `b = 2` and one survivor at each end. Its bandwidth equals `k`, as
    stated.

## Evidence

`verify.py` computes the formula and an actual Schur complement, from random band entries over
the prime field `2^61 − 1`. For **196,512 layouts** (every nonempty proper eliminated subset of
every path `n = 1..15`, for each of `b = 1, 2, 3`) it checks:

- the formula equals the Schur bandwidth;
- on the 84,491 layouts that satisfy #4373's separation hypothesis, the cap `2b − 1` holds;
- among those, the two-sided criterion decides exactly which layouts attain the cap.

It also checks two controls:

- the under-separated chains for `b = 2, 3` and `k = 1..8`, against the formula above, and
  #4373's `b = 2` chain;
- #4285's 7×7 bandwidth-2 witness, recomputed in exact rationals: far entry `−1/432`,
  bandwidth `3 = 2b − 1`, and both inverse norms `488/389`.

The field computation witnesses generic fill. The upper bound for real Gaussian entries is the
lemma's structural direction.

## Not covered

- Inverse norms beyond the #4285 witness.
- Circular phase cells. The lemma is linear; #4286 covers the circular case.
- Window widths in #4100's narrow solver (#4373's open question 1).
- Whether real Gaussian entries produce every possible fill. Only the upper bound matters for
  #4100.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/carve-schur-bandwidth-census --check-only
python3.12 -B scripts/research_package.py --package research/carve-schur-bandwidth-census
```

The verifier prints `PASS_CARVE_SCHUR_BANDWIDTH_CENSUS` in about 50 seconds, using only the
standard library.

## Open next questions

1. **Does the retained carve ever produce merged components?**
   - *Why it matters:* the formula prices any layout. Where a separation shortfall occurs at
     holes or cell cuts, it gives the exact width.
   - *First step:* run the formula on #4100's carve layouts with holes and cuts marked.
   - *Blocked by:* a concrete layout generator for the caller.

## Credit

- The theorem, its application to `GAUSSIAN.md` and the chain example are unpaidmoon's
  (#4373).
- The one-interval cap and the 7×7 witness are jwr's (#4285).
- The carve and the `O(W)` claim are #4100's `GAUSSIAN.md`.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
