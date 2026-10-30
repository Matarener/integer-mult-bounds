# Proof: complete Boolean paid inventory for Norm∘F_(2,1)

**Scoped interface construction on the unchanged PR2808 Boolean fixture; no new kappa.**

## Setup

Let `G=(Z/3Z)^2` and `a=(2,1)`. The weighted reversal `(P x)_i=a_i x_{1-i}`
satisfies `P^2=2I≠I`. By Theorem 1 of `weighted-wrapper-contract`, equal calls
to `F_a` in the ordinary body

```text
D -= H; F; D += H; F; D = -D; D += H
```

fail to realize interchange `J`. Formula (5) counts exactly **9** correct
address pairs out of **81**.

## Normalization identity

Let `T=diag(1,2)` and `P'=TP`, so `P'(x0,x1)=(2 x1, 2 x0)`. Then `(P')^2=I`.
Define output post-scales

```text
Norm(H',D') = (H'_0, 2 H'_1), (2 D'_0, D'_1).
```

A direct expansion gives `Norm∘F_a = F_{P'}`. Substituting this callee for both
wrapper calls meets Theorem 1, so the word equals `J` on all of `G×G`.

## Unchanged PR2808 Boolean fixture

The executable evidence runs Nick Petalas's authenticated
`outer.body_ordinary` on Boolean origin bit-planes exactly as in
`weighted-wrapper-contract/runtime_check.py`: volume `V_addr=81`,
`planes=7`, `prefixes=rows=stock=gap=suffix=1`, weights `(2,1)` twice.
Origin labels occupy codes `1..81` across seven planes; padding uses the
pinned `padding.complete` contract.

Raw `F_a` (no Norm) recovers **9/81** agreements with `J`. Metered
`Norm∘F_a` recovers **81/81**. Wrong-scale controls (`scale∈{0,1}`) remain
strictly below 81.

## Complete paid inventory

Meters are taken from the live Boolean callee plus the pinned padding contract
with `added=0` (`rows=stock=1`):

| Line item | Closed form | Count |
|---|---|---:|
| scale | `2 · V_addr · (2·planes)` | **2268** |
| inverse | `2 · V_addr · (2·planes)` | **2268** |
| source_access | `V_addr · (2·planes)` | **1134** |
| restoration | payload `V_addr·(2·planes)` + rowcount `2·(2·planes)` | **1162** |
| frame_copy | pad_in + pad_out + callee_copy = `3·V_addr·(2·planes)` | **3402** |

Here `2·planes=14` is the number of callee invocations. Pad in/out each copy
`V_addr` cells per call by `padding.transform` with `added=0` and
`scan_rows(..., mode="copy")`. Frame rewinds equal the call count (**14**).
Forward weight multiplies (**2268**) are disclosed but are part of the proposed
`F_a` map, not an extra Norm charge.

Algebraic scale-only `4V=36` from the deferred modular census is the
**per-plane** scale subtotal (`2268/7=324=4·81`); this package binds the full
Boolean traffic.

## Limitations

This prices one concrete weighted callee on one Boolean fixture. It does not
admit a BIT supplier, change the selected κ, implement a physical tape
inventory beyond the pinned padding copies, or bind PR2753 Incoming / outer
`F_I`. Changing the wrapper word would require a separate proof.
