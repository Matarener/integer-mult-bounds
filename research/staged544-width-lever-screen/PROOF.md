# Proof: priced width screen for the staged544 fixed-T360 ideal

All numbers are printed by `verify.py`. Units are per owner replica; one
"helper-call" is one helper in one of the nine calls.

## 1. Model and sign lemma

Inventory per replica (PR3734 head `fa041037`, PR3815 head `77ffbf28`): `9 s_w`
helper-calls of hosted width `w`, with `s = {4:26,5:2,6:18,7:53,8:96,9:213}`;
idle bins `B = {8:672,16:448,32:448,48:448}`; local per-call profile
`n = {1:2440,2:725,3:224,4:102,5:20,8:8}`; 896 live rank-73 families. A
packing puts each helper-call into one bin; a bin pattern `p` (counts `p_w`) of
capacity `c` leaves `l_p = c - sum_w w p_w >= 0`, paid as one rank-`l_p` child
when `l_p > 0`. With `h(l) = l^(1-a)` and `h(0) = 0`,

`F(a) = 9 sum_r n_r h(r) + sum_p y_p h(l_p) - 896 h(73)`.

As in PR3815, `F(a) = 73^(-a) (sum N_r r (73/r)^a - 65408)`, where `N_r` is
the full paid histogram (local children and bin remainders), and every paid rank
is below 73, so `F` has one root and "root < a" iff `F(a) > 0`. This holds for
every inventory and local profile below (all paid ranks stay at most 48), for
integer or fractional `y`, and for any clock: the clock only restricts `y`.

`V(s', a) = min sum_p y_p h(l_p)` over `y >= 0` with `sum_p y_p p_w = 9 s'_w`
for every width and `sum_{p in c} y_p = B_c`. The ideal ceiling of an
inventory `s'` and profile `n'` is the root of
`9 sum n'_r h(r) + V(s', a) - 896 h(73)`.

`h` is enclosed outwardly (`h_lo <= h <= h_hi`, width below 1e-85): `ln l`
from the `atanh` series with a geometric tail bound, `exp(-u)` from alternating
partial sums, and outward rounding to 1e-90.

## 2. Staged544 ceiling bracket

The ten patterns found by HiGHS equal PR3815's basis. Their exact primal is
`y >= 0`; the smallest entry is 7. With `h_hi`, `F(a_lo) <= -1.31e-19` at
`a_lo = 0.001730578437266246818740`. Solving the same basis for `(pi, mu)` with
`h_lo` at `a_hi = 0.001730578437266246818741` gives `F(a_hi) >= 5.28e-20`.
This reproduces PR3815's bracket with an independent enclosure. It is not a
new result.

## 3. Weak-duality screen, prices and the monotone-price lemma

`(pi_4..pi_9, mu)` is PR3815's basis dual (its `ceiling_certificate.py` solves
it), here solved exactly with `h_lo` at `a_hi`. Let `pi_w` (w = 1..9) and
`mu_c` satisfy

(D) `sum_w pi_w p_w + mu_c <= h_lo(l_p)` for **every** pattern of widths 1..9
in every bin (318,840 patterns).

Then for any inventory `s'` over widths 1..9 (fractional or not) and any
local profile `n'`, every packing satisfies

`F'(a_hi) >= 9 sum_r n'_r h_lo(r) + 9 sum_w pi_w s'_w + sum_c mu_c B_c - 896 h_hi(73).`   (*)

Proof: multiply (D) by `y_p >= 0`, sum, and use the two equality constraints.
Moving `z` helper-calls from width `w` to `v < w` changes the right side of (*)
by `z (pi_v - pi_w)`; changing the local profile changes it by
`9 sum (n'_r - n_r) h_lo(r)`.

**Two extensions.** `verify.py` uses two duals that agree on widths 4..9:

- the *cheapest* extension `pi_1 = pi_2 = pi_3 = pi_4` (printed as
  `helper_pi`), used for the lemma below;
- the *tight* extension: `pi_3`, then `pi_2`, then `pi_1` raised to the
  largest values keeping (D). Its limiting patterns are:
  `3 + 5*9 = 48` limits `pi_3`, `2 + 5*9 = 47` (leftover 1) limits `pi_2`, and
  `1 + 4 + 3*9 = 32` limits `pi_1`. It gives the 4->v prices.

Both satisfy (D) on all 318,840 patterns with minimum reduced cost exactly 0,
by enumeration and by an unbounded-knapsack recursion over used volume.

**Slack lemma.** If (D) holds on the 2,551 width-4..9 patterns and
`pi_4 <= -3`, the cheapest extension satisfies (D) on all width-1..9 patterns.
Proof: take a pattern `p` with `s` helpers of width at most 3 and total width
`v <= 3s`, leftover `l`. Removing them gives a width-4..9 pattern `p'` with
leftover `l + v`. Since `h` is concave with `h(0) = 0` and `h(1) = 1`,
`h(l + v) - h(l) <= h(v) <= v`. So
`RC(p) = RC(p') + h(l) - h(l + v) - s pi_4 >= RC(p') + s(-pi_4 - 3) >= 0`.
Here `pi_4 = 1 - h(5)` and the margin `-pi_4 - 3 = 0.986093083432664503980103`
dwarfs the enclosure width. The 318,840-pattern enumeration is a second check
of this lemma and is needed only for the tight extension.

**Monotone-price lemma (free reductions).** The cheapest extension is
nonincreasing in width and every `pi_w <= 0`. So any width reduction (to any
width `>= 1`, or unhosting) with an unchanged local profile keeps
`F(a_hi) >= 5.28e-20 > 0`: it keeps the ideal ceiling below `a_hi`. Under the
conservation of section 4 such a move is not realizable; the lemma is a
statement about the model, not a staging closure.

**Prices.** The value `V` is convex in the right-hand side, so a price is a lower
bound for every further unit in that direction; inside the listed range the
same basis stays primal feasible and the price is exact.

| move | exact price at a_hi | closed form | range (helper-calls per replica) |
|---|---|---|---|
| 9->8, 8->7, 7->6, 6->5 | 0.987736781185353068089966 | `(h(48)-h(3)-5h(5))/20` | 28, 30, 28, 28 |
| 5->4 | 1 | `h(1)-h(0)`; `[9,9,9,5]` and `[9,9,9,4]` are both basic | 18 |
| 4->3 | 0.991791369039984911721564 | `h(5)-h(3)-1` | 324/5 |

The 6..9 closed form is PR3682's 8->7 width shadow (`price.py`); the dual is
affine on widths 5..9, so the same price holds for every step there. For 4->3,
add the column `[3,9^5]` (48-bin), which has reduced cost 0 under the tight
extension. Moving `k` units along `+[3,9^5] - [4,9,9,9] + [9,9,9] - [9^5]`
keeps every bin and width row except `3` and `4` fixed, all four columns are
tight, and the basic entries `y[4,9,9,9] = 234` and `y[9^5] = 324/5` stay
nonnegative for `k <= 324/5`. By complementary slackness the change in `V` is
exactly `k (pi_3 - pi_4) = k (h(5) - h(3) - 1)`. `verify.py` checks the
tightness, the cost and the range in exact arithmetic. HiGHS gives
0.9877367811860, 1.0 and 0.9917913690369 for single units of 8->7, 5->4 and
4->3, agreeing to about 3e-12.

## 4. Per-call conservation and staging screens

Per call, local paid rank minus hosted helper width is 1856 on both pinned
(inventory, local) pairs: staged544 `5134 - 3278` and PR3682 `5135 - 3279`.
With the bins this gives total paid rank `9*1856 + sum c B_c = 65088 =
896*73 - 320` per replica. PR3605 states the same conservation for its two
staging units ("the local rank mass falls by 2, exactly matching the
owned-width decrease"). The three pinned T360 profiles (PR3682 finite, PR3734
finite, PR3815 clock fill) all total 23,431,680 = 65088 x 360; the last two
share one (inventory, local) pair, so for them this is implied arithmetic.
The conservation is observed, not proved. Where it holds, a reduction with an
unchanged local profile is not realizable: each width unit must remove one unit
of local paid rank.

**Screens.** By (*), a width unit `w -> w-1` together with a local change of
saving `S` changes `F` by at least `price - S`, exactly within the ranges:

- *Documented signature.* PR3605 derives the per-helper staging delta
  `3H1 + H2 - 2H3`, i.e. `{1:+3,2:+1,3:-2}` (one pivot and two donor climbs).
  PR3734's local change from PR3682 is the same delta (`verify.py` checks it).
  All three observed units are 8->7 moves; for the other widths the screen assumes the same signature.
  Its saving is `2h(3) - 3 - h(2) = 0.991001081580029037511288`. The gain per
  width unit is +0.003264300394675969421322 for 6..9,
  -0.008998918419970962488711 for 5->4 and -0.000790287459955874210276 for
  4->3.
- *Rank-1 deletion (hypothetical).* A single-child decrement `r -> r-1`
  saves `h(r) - h(r-1) <= h(1) = 1` by concavity, with equality for deleting a
  rank-1 child. Gain at most 0.012263218814646931910033 for 6..9, 0 for 5->4
  (in any amount) and 0.008208630960015088278435 for 4->3. No staging with this
  compensation is known and its realization is not priced.

The gap between the two is `1 - 0.991001... = 0.008998918419970962488711` per
unit. Local rewrites that also merge children (for example PR3682's
`{1:-2,2:-2,3:+2}`) save at zero rank change and are priced by the local term
of (*); they are a separate local-word lever.

## 5. PR3682 -> staged544 split (exact at a_hi)

At fixed `a`, `F(s, n) = 9 sum n_r h(r) + V(s) - 896 h(73)` is additively
separable in inventory and local profile, so the 2x2 interaction is
identically 0. `verify.py` solves all four corners exactly (each primal
`y >= 0`, dual feasible on 2,551 patterns, enclosure gap below 1e-70). They
share one basis, so the width part (one 8->7 per call, inside the range 30)
equals 9 x the price:

- width part: +8.889631030668177612809695088162;
- local part: -8.919009734220261337601597266358, a saving of
  0.991001081580029037511288 per call;
- total -0.029378703552083724791902178195, or 0.003264300394675969421322
  per call (the documented-signature gain).

Either change alone breaks the conservation. The width-only change moves the
ideal root down to about 0.0016821 and the local-only change moves it up to
about 0.0017788 (HiGHS, float).

## 6. Scope

This is a clock-free, fractional relaxation with fixed idle bins. Sections 3 and 4
are exact statements about it. Template, stock and clock (chronological)
effects are not modeled. The conservation is observed, not derived, and the
documented signature is observed, not proved forced. `mu` is used only as a
subgradient bin price. The first-order conversion `dF/da ~ 184132` is floating
point. No kappa, supplier or admission claim is made.
