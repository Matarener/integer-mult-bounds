# One block-scale scan term at the exact F0/B_1_2 entry width

The selected conditional kappa remains **0.001672660197076918**. This note
does not change it.

## Why this term

Pinned main `6f100d4bb5083f8c35d96fd95a539811c62f245c` records Arham Tahir's
common block-scale scan in `research/qq16-block-scale-scan`. Its stated
invoice is evaluated at the published finite-format example `W=456`,
`w=453`, `p=122`. A search of that tree finds no evaluation at decoder
width `W=532`. The pair-kernel coefficient `26744256` and the named-field
bit coefficient `493696` are the submitted #3374 terms and are left
untouched. The incorporated scalar-ADD count `5408*N*D` does not depend on
`W`, so repeating it would reprint that receipt. The scan polynomial does
depend on the entry width, and it is the term priced here.

## Inherited width

The literal producer is exact **F0 followed by B_1_2**, and the consumer is
ywz65's PR2707 decoder, which reads X in F17 and Y in `F17 C_q^{-1}`. Nick
Petalas's entry contract, at `lambda=1`, `f=64`, `e=0`, `beta=64`, gives

```text
Q0 = 80, b = 79, k = 137, Qmax = 497, E = 15, W = 532.
```

The scan proof binds `p=k` and `w=W-3`. At this width that is `w=529` and
`p=137`, with `0 <= p < w`. The largest emitted exponent is `w-1-p=391`,
which lies in the scan proof's stated range `[0, w]`.

## The scan polynomial

The pinned formula, for `q` signed `w`-bit components and reserve `p`, is

```text
G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3,
S(n) = sum_{0 <= i < n} popcount(i).
```

One owner-local line scans `q=2D` real components once. The `D` coefficient
is `8w` and the remaining term is `2w - 2p + S(w-p) + 3`. The same proof's
gate roles (absolute-value ripples, magnitude ORs, leading-bit hits,
constant-bit ORs, low ORs, and three flag gates) sum to this polynomial.
At `w=529` and `p=137`, `S(392)=1628`, so one scan costs

```text
4232 D + 2415
```

gates. The unchanged 336-line decoder, one scan per line per owner, costs

```text
1421952 N D + 811440 N
```

gate evaluations. The published control `w=453`, `p=122` still costs
`3624 D + 1984` per line and `1217664 N D + 666624 N` for 336 lines.

These counts are irreversible AND/XOR/OR/NOT evaluations in the scan
model. Wires, constants and fan-out stay free there. The count is an exact
invoice of that construction, with redundant gates retained.

## Which physical bill changes

The term that changes is the **common block-scale scan subtotal** of the
F17 zero-retention decoder's direct Boolean arithmetic bill. At the
published `W=456` example that subtotal is `1217664 N D + 666624 N`. At the
exact entry width `W=532` it is `1421952 N D + 811440 N`. Scalar ADDs,
wrappers, maps, addressing, movement and cleanup stay unpaid. The pair
kernel and the 464-field bit count stay the submitted #3374 coefficients.

## Stop

Stop after this one scan term and this one parameter tuple. A scan subtotal
is not a complete consumer, a recursive rank tariff, or a new kappa.
