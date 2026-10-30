# Exact-producer width of one F17 decoder arithmetic bill

The selected conditional kappa remains **0.001672660197076918**. This note
does not change it.

## Why this is not a stock-coefficient package

On the pinned main, the selected ordinary BIT parent reserve is already
derived: Adam Gall's package gives the conditional coefficient 8194, Nick
Petalas's ceiling-free refinement gives 6748, and the later lcm-reserve
package binds `269241600 |GL_64(F_q)| q^(4096(w-1))` to the same depth
recurrence. The complex `m=73` shape coefficients `A`, `B` and `rho` are
already recorded as unbound. Repeating those derivations is not a new fact.
The open joint-query obligation is the one taken below.

## Pinned producer and consumer

The literal producer is the exact full-cover word **F0 followed by B_1_2**
in the retained joint-query certificate, as used by Nick Petalas's
producer-entry contract and by the #2965 defect transfer. The consumer of
its completed charts is ywz65's PR2707 zero-retention decoder. At the
completed B1 cut that word reads X in chart F17 and Y in chart
`F17 C_q^{-1}`, and it returns the original 224 logical arrays **in F17**.
F17 means the product of the signed Fourier lines on address axes 0 through
16. This package does not replay the producer or the decoder word.

## Inherited exact entry

Under the entry contract's hypotheses (exact producer arithmetic, the
inherited helper contract, `h=73` address axes, and positive tensor depth),
post-B1 fields satisfy

```text
B = 17628*H < 2^(e+15),
Q0 = f + ceil(lambda/2) + 6 + 9*lambda,
```

whenever `H <= 2^e`. The displayed `17628` is the predecessor's triangle
bound. This note checks the slack `17628 < 2^15`, which is what makes
`B < 2^(e+15)` follow from `H <= 2^e`. For an original-input error `H 2^{-beta}`,
that contract sets the decoder's relative target to `b = beta+15` and quotes
PR2807's width

```text
k = beta+37 + ceil_log2(lambda) + floor(73 lambda / 2),
Qmax = Q0 + 3k + 6,
W = Qmax + e + 35.
```

At `lambda=1`, `f=64`, `e=0`, `beta=64` this is

```text
Q0 = 80, b = 79, k = 137, Qmax = 497, E = 15, W = 532.
```

`E = e+15` is the entry exponent in PR2807's notation `B <= 2^E`. The same
proof's completed-field majorant is `32369 B`. Because `32369 < 2^15` and
`B < 2^E`, that majorant is strictly below `2^(E+15)`, so the inherited
overflow argument still applies at this `E`.

## Pair inputs at this width

PR2807 bounds every common-grid component by `2^(Qmax+E+16) = 2^(W-4)` and
every pair numerator by `2^(Qmax+E+18) = 2^(W-2)`, strictly. Signed `w`-bit
integers hold absolute values strictly below `2^(w-1)`. The choice

```text
w = W-3, L = w+2 = W-1
```

therefore stores the components and the numerators. At `W=532` this is
`w=529`, `L=531`. The published `W=456` control is the same rule:
`w=453`, `L=455`.

PR2811's runtime-exponent circuit, for `k = bit_length(L-2)`, has

```text
24 L k + 52 L + 4 * 2^k + 4 k + 4
```

gates. The control is `k=9` and **124,028** gates. There are 336 lines and
at most `lambda D / 2` pairs per line per owner, so the kernel coefficient
is `gates * 168`. The control coefficient is `124028 * 168 = 20836704`,
matching the published `20836704 lambda N D` subtotal.

At `L=531`, `k = bit_length(529) = 10` and the gate count is **159,192**.
The kernel subtotal is at most

```text
159192 * 168 * lambda * N * D = 26744256 lambda N D
```

gate evaluations. PR2807's named-field representation uses at most
`2 * 464 * N * D * W` data bits. At this width that coefficient is

```text
2 * 464 * 532 = 493696,
```

so at most `493696 N D` data bits for the 224 borrowed arrays, 224 outputs
and sixteen private arrays.

These two coefficients are sufficient conditional upper bounds in the
incorporated gate and register models. They are not tape time, not a
recursive rank tariff, and not a complete machine invoice.

## Dirty-helper ledger does not supply the width

The rounded-producer envelope is the registered intermediate
magnitude/dirty-state ledger for this same literal producer. It bounds the
noisy all-cut B1 norm by `2^(delta+80) H` and states that component
representation, the entry grid, and subsequent F17 consumption are unknown.
PR2807 states that a norm bound alone does not determine the adaptive line
exponent: inputs `2^{-j}` can have bounded norm and arbitrarily negative
exponent. Substituting `E = delta+80` into `W` is therefore not licensed.
The missing bound is a proved entry grid `2^{-Q0} Z` for the actual dirty
helpers. `dirty_width_supplied` is false.

## What remains outside the bill

Scans, the 2,704 scalar ADDs, wrappers, cover maps, address arithmetic,
movement, cleanup and a later endpoint adapter are unpaid here. A caller
that does not accept F17 outputs still needs its own frame conversion.
The entry contract already says that adapter is a separate invoice.
