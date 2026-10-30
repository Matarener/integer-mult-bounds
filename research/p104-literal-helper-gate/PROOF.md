# Literal correction, helper entrance, and the #3954 gate

This is a scoped negative certificate. It does not change κ. The selected
value stays `0.001672660197076918`.

The source contract is the two-axis scaffold in
`research/p104-two-axis-compatibility/PROOF.md` at base
`12fa8c5c844be21bfefb38a19503fbd867a11244` (PR #3954). The literal-slot
identity is the one separated in `research/p104-literal-slot-defect`. This
note does not rerun either package.

## 1. Charts of one scaffold call

Order the two data banks as a pair. The retained caller uses source charts
`(T, I)` and terminal charts `(F, E)`, with `T = C_U`, `F = C_I` and
`E = F T^{-1}`. Here `I` is the identity address, so `C_I = C_0`, and

```text
C_u = ((1+i) I + (1-i) X_u) / 2.
```

On a Fourier character `z`, `C_u` acts by `1` when `u·z` is even and by `i`
when `u·z` is odd. Thus `C_0` is the identity operator, and `C_u = C_0` if
and only if `u = 0`.

For a call on address `u` and a next call on address `v`, the exit chart pair
and the next entrance chart pair are

```text
exit      = (C_0, C_u^{-1}),
entrance  = (C_v, C_0).
```

These pairs agree on both banks if and only if `C_v = C_0` and `C_u^{-1} = C_0`,
hence if and only if `u = v = 0`. Every nondegenerate line in the scaffold is
a nonzero address, so no adjacent pair of scaffold calls matches both data
banks.

`Π P_enc Π` is the operator which intertwines one call's literal encoding
`A_T = Π L_T`. It is not a rewrite of the chart pair `(C_0, C_u^{-1})` into
`(C_v, C_0)`.

## 2. Helper entrance and exit

Section 1 of the #3954 proof extends every compatibility map by identity on
the 72 arbitrary dirty helper roles of a fiber. Section 5 places two disjoint
banks of those roles in the inventory

```text
n = 104,
helper roles = 2 n · 72 = 14976,
W = 2 n^2 + 2 n · 72 = 36608.
```

The same section says that every persistent entrance other than the rank-one
data source chart is the identity, and that the completed contract is full
`F` on all `W` roles. The progress identity therefore charges `81` dimensions
on each helper role and subtracts only the `N = n^2` data-line sources:

```text
helper progress demanded = 81 · 14976 = 1213056.
```

The identity extension acts by `1` on each helper coordinate. It sends a
helper basis vector to itself and adds no helper component to a data vector.
Its contribution to helper progress is `0`. It preserves a dirty helper
state, and it does not implement the transition from the identity entrance
to the full-`F` exit.

So `Π P_enc Π`, extended in the way #3954 states, does not match a completed
helper exit to the next call's identity helper entrance.

## 3. The slot exchange is not free, and zero is already too expensive

`Π` swaps the two data slots on the `96` N-ports and fixes the `8` J-ports.
That support size is a count of coordinates, not a native tariff. The #3954
gate records the realization of `Π` inside an unknown nonnegative physical
charge. Under hypotheses (a)–(e) of that proof, with this charge set to an
integer `s ≥ 0`,

```text
P_total     = 81 W − N           = 2954432,
remaining   = P_total − 208·2312 = 2473536,
lower mass  = 208·2576 + remaining + s = 3009344 + s,
capacity    = 81 W               = 2965248,
excess      = 44096 + s > 0.
```

The moment ratio at `a = 0` is already greater than `1` when `s = 0`. Every
larger price is worse. A negative price would be a different gate; unknown
costs in that proof are not negative.

The local progress `2312` per call is the figure hypothesis (b) grants. This
note does not move any of that grant onto the boundary map. The boundary map
adds none.

## 4. What a matching pair would have to change

The conjugation identity on the two data banks remains true: on a witness
with one J port, one N port and one helper coordinate,

```text
(Π P_enc Π ⊕ I) (A_T ⊕ I) = (A_T ⊕ I) (P ⊕ I).
```

The old correction, extended in the same way, fails that identity. This is
the data-slot statement already separated from the census. It does not make
the chart pairs of section 1 equal, and it does not pay section 2.

A favorable adjacent pair needs a different chart contract or a helper word
whose proved progress can be subtracted from `1213056` without a new
nonnegative charge that puts the excess back. Neither is supplied here.
