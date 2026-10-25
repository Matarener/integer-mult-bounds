# Proof: dual-scale Norm∘F_(4,1) Boolean inventory at p=3,w=2

**Scoped interface construction on the precision-blind PR2808 Boolean fixture; no new kappa.**

## Setup

Let `p=3`, `w=2`, `G=(Z/9Z)^2` and `a=(1+p^{w-1},1)=(4,1)`. The weighted
reversal `(P_a x)_i=a_i x_{1-i}` satisfies `P_a²=4I≠I`, so
`P_a²−I=3I`. By Theorem 1 of `weighted-wrapper-contract`, equal calls to
`F_a` in the ordinary body fail to realize interchange `J`. Formula (5)
counts exactly **729** correct address pairs out of **6561**.

## Single-factor Norm obstruction

The predecessor Boolean invoice for `a=(2,1)` on `(Z/3Z)^2` uses one shared
scale factor `s` on coordinates `(H'_1,D'_0)`. The induced one-bank map is
`P'=(a_0,s)=(4,s)`. Involutory weighted form requires `a_0·s≡1` and the
`D'`-matching condition `s²≡1`, i.e. `4s≡1` and `s²≡1` modulo 9. No such
`s∈Z/9Z` exists. Hence the single-factor Norm pattern cannot admit the
wrapper on this precision-blind fixture without enlarging scale support
beyond those two coordinates or changing the scale algebra.

## Dual-scale Norm identity

Keep the same two-coordinate support `(H'_1,D'_0)` but allow asymmetric
scales `(s_{H1},s_{D0})=(7,4)`. After `F_a`,

```text
H_raw = (4 D_1, D_0),   D_raw = (H_1, 7 H_0),
Norm: H' = (4 D_1, 7 D_0),   D' = (4 H_1, 7 H_0).
```

This equals `F_{P'}` for `P'=(4,7)`. Since `4·7≡1 (mod 9)`, `(P')²=I`.
Theorem 1 then makes the ordinary word equal `J` on all of `G×G`.

## Unchanged PR2808 Boolean fixture

The executable evidence runs Nick Petalas's authenticated
`outer.body_ordinary` with `q=3`, `w=2` on Boolean origin bit-planes:
volume `V_addr=6561`, `planes=13`, `prefixes=rows=stock=gap=suffix=1`,
weights `(4,1)` twice. Origin labels occupy codes `1..6561` across thirteen
planes; padding uses the pinned `padding.complete` contract.

Raw `F_a` (no Norm) recovers **729/6561**. Metered dual-scale `Norm∘F_a`
recovers **6561/6561**. Algebraic remap controls fail strictly below 6561 for
shared scale `(2,2)` (the predecessor factor), identity `(1,1)`, zero `(0,0)`,
and swapped dual `(4,7)`; one live Boolean shared-`(2,2)` control likewise
stays imperfect.

## Complete paid inventory

Meters are taken from the live Boolean callee plus the pinned padding contract
with `added=0` (`rows=stock=1`):

| Line item | Closed form | Count |
|---|---|---:|
| scale | `2 · V_addr · (2·planes)` | **341172** |
| inverse | `2 · V_addr · (2·planes)` | **341172** |
| source_access | `V_addr · (2·planes)` | **170586** |
| restoration | payload `V_addr·(2·planes)` + rowcount `2·(2·planes)` | **170638** |
| frame_copy | pad_in + pad_out + callee_copy = `3·V_addr·(2·planes)` | **511758** |

Here `2·planes=26` is the number of callee invocations. Scale support stays
exactly two coordinates; only the scale values are asymmetric.

## Limitations

This prices one concrete precision-blind weighted callee on one Boolean
fixture. It does not admit a BIT supplier, change the selected κ, implement a
physical tape inventory beyond the pinned padding copies, or bind PR2753
Incoming / outer `F_I`. It does not reprint the `(M=3,a=(2,1))` meters.
Changing the wrapper word would require a separate proof.
