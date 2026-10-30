# Query-price threshold for the productive-helper path reduction

zxv's [PR5554](https://github.com/CrocSwap/integer-mult-bounds/pull/5554)
(`research/kappa-architecture-frontier`) reduces every FULL/QUERY mask of the
rank-b productive-helper path to one canonical invoice per FULL count. That
reduction assumes each QUERY stage costs `v` rank-one jobs. Its Open next
question 3 asks what happens under a changed query law. This package answers
that question for one changed law: each QUERY stage costs `w*v` rank-power
units, with every other term of #5554's equation (1) unchanged.

**Result (scoped proof).** Write `f(z)=z^t` with `f(0)=0`, `t=1-C` in `(0,1)`,
`b>1`, and

`g_k(b,t) = b^t + (bk+b+1)^t - (bk+2b)^t`, so `w*(b,t) := g_1 = b^t + (2b+1)^t - (3b)^t`.

1. If `1 <= w <= w*`, the canonical reduction holds at every FULL count `n`,
   for all pair counts, splits and masks, with minimum
   `C_n^w = C_n + (w-1) v Q_n`, where `C_n` is #5554's (2)/(3) and
   `Q_n = |n-3|` is its query count. Convexity, the three-sign exclusion (4),
   the price frontier (5)/(6) and the three-value ratio gate all transfer
   with `c_n` replaced by `c_n + (w-1)|n-3|`.
2. If `w > w*`, the canonical invoice is strictly beaten at every `n >= 6`,
   by at least `2v(w - w*)`. #5554's cap and frontier must not be transferred.
3. If `w < 1`, the infimum is `-infinity` at every `n`: each empty pair
   inserted next to a side end bit 0 gains `2v(1-w)`.

At b=8 the tolerance `w*-1` is small:

| C | `w* = 8^t+17^t-24^t` |
|---:|---:|
| .0031 | 1.03522543106 |
| .0034 | 1.03859829952 |
| .004 | 1.04532506534 |
| .01 | 1.11121543014 |

So at C=.0034 a per-QUERY surcharge above about .0386 rank-one units per port
already breaks the canonical form. In that case 11 side pairs survive. A
rank-two query (`w=2^t`, near 2) is far outside this range for t near one.
No new κ, supplier admission or selected-frontier change is claimed.

## Proof

Use #5554's notation. With query price `w`, the bill is

`E_w = E_1 + (w-1) v Q`, with `Q = 2p+1-n` QUERY stages,

because only the rank-one query term changes. Every move of #5554's §2 keeps
`n` fixed. Classify each move by its effect on `Q`.

* **Delete a 00 pair, and move a side FULL into an empty unpaired
  position.** Each deletes one pair and two QUERY stages: `Q` falls by 2. #5554
  shows `Delta E_1 <= 0`. Hence `Delta E_w = Delta E_1 - 2v(w-1) <= 0` for `w >= 1`.
* **Replace 01 by 10, and balance the sides.** `Q` is unchanged, so the
  #5554 signs hold verbatim.
* **Split 11 into 10,10** at preceding FULL count `k`. `Q` rises by 2. Divided
  by `2v` the change is `w + f(bk+2b) - f(bk+b+1) - f(b) = w - g_k`.

`g_k` is strictly increasing in k. Indeed
`g_k = f(b) - integral over [bk+b+1, bk+2b] of t z^(t-1) dz`; the integrand
decreases and the interval moves right. So the split is non-increasing for
every `k >= 1` exactly when `w <= g_1`. Only `k=0` needs a new move.

After the 00 deletions and 01 replacements, a side pair with `k=0` is the
first pair on a side whose end bit is 0. **New move:** replace end bit 0 and
first pair 11 by end bit 1 and first pair 10. `n`, `Q`, and the FULL count
preceding every later window are unchanged. The window term changes from
`2f(b) - f(1+2b)` to `f(2b) - f(1+2b)`. The change `2v(f(2b) - 2f(b))` is
negative by strict subadditivity. Apply it once per side, then split every
remaining 11 pair; each now has `k >= 1`. None of these moves creates a 00 or
01 pair or a `k=0` 11 pair. Then #5554's FULL relocation and balancing
finish at the canonical mask. Its query count is `n-3` for `n >= 3` (p=n-2),
and `3-n` for `n <= 2` (p=1). This proves part 1's minimum.

For convexity, `D_n` gains `(w-1)v(Q_(n+1)-Q_n)`: `-(w-1)v` for `n<3`, and
`+(w-1)v` for `n>=3`. Only `D_3-D_2` changes, and it gains `2(w-1)v >= 0`. So
`C_n^w` stays strictly convex. #5554's ratio argument uses only strict
increase of `D_n`. The maximum defining `lambda` still exists:
`c_1^w = 2w - 2(1+b)^t < 0` because `w <= g_1 < b^t`, and `c_n^w/n -> w > 0`.

**Sharpness (part 2).** For `n >= 6` the canonical right side has
`ceil((n-3)/2) >= 2` pairs. Its outer pairs, read inward, are 10 at `k=1`
then 10 at `k=2`. Merge them into one 11 pair at `k=1`. Later windows keep
preceding count 3. The window terms change from `W(2,0)+W(3,0)` to `W(2,1)`,
with `W(h,e)=f(bh)+e f(b)-f(1+b(h+e))`. This is a change of `f(b)+f(2b+1)-f(3b)
= g_1` per `2v`. Two QUERY stages disappear. The total change is
`2v(g_1 - w) < 0`.

**Part 3.** Insert a 00 pair between a side's end bit 0 and its first pair.
Its window has `h=e=0` and contributes `-f(1) = -1`; earlier counts are
unchanged; two QUERY stages are added. The change is `2v(w-1)`, negative for
`w<1`, and the insertion repeats without bound. Every n has a mask whose
left end bit is 0, so the infimum is `-infinity` at every n. The verifier
checks this gain for `n <= 2` only.

## Evidence and reproduction

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/path-query-price-threshold/verify.py
```

Expected: `PASS_PATH_QUERY_PRICE_THRESHOLD masks_p_le=6 block_ranks=2 exponents=4 checks=456`
(about 7 s on CPython 3.12). The script pins the bytes of #5554's `PROOF.md`
and its equation (1). For b in {2, 8} and t in {1/2, 9/10, 4983/5000,
999/1000}, it does the following with 60-digit decimal arithmetic:

* evaluates the literal equation (1), with QUERY price w, on every mask with
  p <= 6 pairs and every split;
* at w in {1, (1+g_1)/2, g_1 - 10^-40}, confirms that no such mask beats the
  canonical invoice, and that the canonical value is attained whenever its own
  p fits;
* at w = g_1 + 1/100, confirms the n=6 merge identity `2(w-g_1)` and a gap of
  at least that size for each `6 <= n <= 9`;
* confirms that `g_k` increases for `k < 64` and that the outer 00 pair gains
  `2(1-w)` at w = 99/100.

These are finite controls on the written proof. They are not an all-p search
or a proof-kernel check.

## Limitations

* This is a scoped proof about #5554's relaxed raw invoice family with one
  changed tariff. It covers no native word, compiler closure, BIT/outer
  funding or physical query realization.
* It changes only the query price. Query rank as a target, query helper
  credit, the idle law and nonautonomous outputs remain outside scope.
* #5554's exchange proof, inherited from #5405/#5409, is cited as a premise
  and not re-verified here. Independent human or proof-kernel review has not
  been run.

## Open next questions

1. **Minimum for w > w\*.** Which masks are optimal once 11 pairs survive? A
   guess is that the outer pairs become 11 up to an index fixed by
   `g_k >= w`. First step: extend the exchange argument with 11 pairs ordered
   by `k` and compare with the brute-force minima.
2. **Query law with target credit.** If a rank-q query also earns a rank-q
   target, the per-pair balance changes. Does the reduction survive?
3. **Fee at the frontier.** At C=.0034, does a surcharge below `w*-1` move
   #5554's optimal FULL count 16 for the #5551 bill? Its ratio gate now
   includes `(w-1)|n-3|`.

## Credit

Produced by Nick Petalas. The path family, equation (1), the canonical
reduction and the price frontier are zxv's #5554. It builds on Ali Romman's
#5405/#5409 exchange and convexity proofs and the credited predecessors listed
there. The query-price parameter, the threshold `w*`, the new k=0 move, the
sharpness witness and the unboundedness below `w=1` are new here. Apache-2.0.
