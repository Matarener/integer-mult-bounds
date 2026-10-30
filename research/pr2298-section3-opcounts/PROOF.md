# Proof: PR2298 §3 operation counts on mixed adjacent widths

**Scoped exact schedule invoice; no new kappa.**

## Setup

Fix an axis count `d ≥ 1` and adjacent bit-widths `{s, s+1}` (the mixed
`r/2` and `r` domain of PR2298 §3 / Colkitt's nonadjacent audit). An
**exchange** of two axis fields is realized by the elementary schedule:

| Widths | Primitives |
|---|---|
| equal `w=w` | one completed interchange |
| `|w_i-w_j|=1` | one completed interchange and one elementary bit move |

in the order of the long-first / long-last identities in PR2298 PROOF §3.

## Reversal

Exchange positions `(k, d-1-k)` for `k = 0, …, ⌊d/2⌋−1`. These pairs are
disjoint, so each uses the elementary schedule on the original widths. The
number of exchanges is exactly `⌊d/2⌋`, matching the stated bound. After these
exchanges the width list is reversed.

## Tensor map

For each axis `i ∈ {0,…,d-2}`, exchange `i` with the innermost index `d-1`
(expose), then exchange the same pair again (restore). That is `2` exchanges
per non-innermost axis and `0` for the innermost axis, hence exactly
`2(d−1)` exchanges, matching the stated bound. Widths return to the input
list.

## One-extra-bit invoice

Whenever an exchanged pair has widths differing by one, the elementary
schedule contributes exactly one interchange and one bit move. Equal-width
pairs contribute one interchange and zero bit moves.

## Finite census

Every one of the `∑_{d=1}^{8} 2^d = 510` patterns with widths in `{3,4}` is
emitted and checked. The bounds are attained: at `d=8` the all-long pattern
uses `4` reversal exchanges and `14` tensor-map exchanges. Physical
spot-checks apply the same low-level `(swap|move)` stream through the pinned
`physical.move_address` oracle and recover the reversed field coordinates.

## Limitations

Non-adjacent width gaps (`|Δw|≥2`) are outside PR2298 §3 and are rejected.
Chunk-swap time coefficients and the section-7 exposure exponent are not
re-derived here. No BIT supplier or new kappa is claimed.
