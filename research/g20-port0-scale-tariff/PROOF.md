# One G20 port-0 marker and the proved unit-scale tariff

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

This is a scoped interface audit of one authenticated route marker. It is not
a new ordinary BIT saving, a physical tape execution, or a selected-frontier
change.

## 1. The marker

The frozen extract is taken from the route-marker manifest of PR #5805 at
`b895ae7770a97276ae0e9c13fb0c51cbed4fd00a`. That manifest has
`17 * 2 * 111 * 2 = 7548` markers. The checked marker is

```
event 21502, call 1, stage 1, owner 0, owner bank 0, port 0, phase ENTRY
```

with direction `inverse` and word digest
`af5261a8c087e8c2917cdc280302d07d75b8fe098e31581d21c1ba2d53b42313`.
Its word is the eight operations `SCALE[7,1/2], ..., SCALE[0,1/2]`.
The same owner, stage and port has RETURN twin event `36518`, whose word is
`SCALE[0,2], ..., SCALE[7,2]`.

Write `E` for the elementary RIGHT factor of one operation, using the
predecessor convention `ADD[i,j,a] = I + a e_i e_j^T` and
`SCALE[i,u] = diag(1,...,u,...1)`. On row vectors, `SCALE[i,u]` multiplies
coordinate `i` by `u`, and `ADD[i,j,a]` replaces coordinate `j` by
`j + a * i`. The RIGHT product of the ENTRY word is `(1/2) I_8`. The RIGHT
product of the RETURN word is `2 I_8`. Either order of the two words is the
identity on `Q^8`. Algebraic restoration of this cover therefore holds for
this owner round trip. The other 119 ambient coordinates do not occur in
either word.

The predecessor multiplies every local factor by `N f = 127 f^2` named
cover-kernel calls, with `N = 127 f`. This ENTRY word therefore contributes
`8 * 127 f^2` named calls of coefficient `1/2`. The predecessor states that
each such call keeps a positive coefficient-specific tariff `C_kind(a)`, and
that no physical leaf tariff is asserted.

## 2. Which proved machine can price coefficient 1/2

The retained in-place `unit_scale` contract in
`research/signed-dyadic-scaling/PROOF.md` sends a Boolean fibre

```
(p, x, z) -> (p, a*x mod Q, z)
```

for `a` in `{2, 1/2, -1, -2, -1/2}`, odd positive `Q`, and volume
`V = P Q S`. Its published conservative bill, from that package's README, is
`2048 V` transitions and `64 V` visited cells, including both signed stages,
owner installation and cleanup.

Coefficient `1/2` is in that set, and so is the RETURN coefficient `2`.
The unit ordered shear prices only the modular updates `(y+x) mod Q` and its
inverse, at most `442 V` transitions. The runtime affine shear prices
`y + c x + C mod Q` for integer `0 <= c,C < Q`, at `1024 V` transitions and
`64 V` cells. Neither shear is a scaling of one coordinate by `1/2`.

## 3. Exact rational image and modular image

Take input `3` and modulus `5`. The exact rational images are

```
2 * 3 = 6,    (1/2) * 3 = 3/2.
```

The modular unit-scale images are

```
2 * 3 mod 5 = 1,    3 * (2^{-1} mod 5) mod 5 = 4.
```

These pairs differ. The ENTRY word is an exact rational map `Q^8 -> Q^8`.
The proved machine is a permutation of residue fibres. Agreement on odd-modulus
residues is a further interpretation, already named in the predecessor as
local-ring invertibility. It is not the identity proved by multiplying the
RIGHT word over `Q`.

## 4. Conditional count, and why it is not an invoice

Assume, in addition to everything already proved, that each of the
`8 * 127 f^2` named calls is one sequential in-place `unit_scale` fibre of
the same volume `V`. The retained bill then supplies at most

```
8 * 127 * 2048 f^2 V = 2080768 f^2 V
```

transitions, and at most `64 V` visited cells if the scratch is reused.
The same shape with eight doublings prices the RETURN twin.

The marker does not supply `P`, `Q`, `S`, a tape origin, or a head position.
Its predecessor address formula is the chosen layout

```
half*N^2 + row*N + active[i]*f + lane
```

and that layout note says it is not the retained literal physical head map.
Cache copy and clear, carry, low-type commit, padding and tape movement do
not occur as opcodes in this word. Their absence leaves those presentation
costs unknown. Unknown costs stay out of the `2080768 f^2 V` expression.
The expression is a conditional fibre count under an extra presentation
hypothesis. It is not a charge against the PR #5708 finite fee, and it does
not change ordinary BIT or kappa.

## 5. The other markers do not inherit this coefficient match

The same manifest histogram has `202640` ADD factors and `73916` SCALE
factors, matching the published selected-word totals. Of the SCALE factors,
`6868` have coefficient in `{±4, ±1/4}`, outside the proved unit-scale set.
Of the ADD factors, `45560` lie outside unit shear `±1`, and `25840` of those
are the non-integral coefficients `{±1/2, ±3/2}`. An integer coefficient still
needs a residue presentation and a `Q`-dependent representative before the
affine-shear bill applies. A uniform `C_kind(a)` for every G20 marker is not
available from these three kernels.

## 6. What was checked

`verify.py` recomputes the word digests, both rational products, both
restoration orders, the marker-count product, the histogram partition, the
integer `2080768`, and the presence of the contract sentences in the pinned
files. Three mutated extracts must fail: a wrong digest, a `1/4` scale, and
a histogram with the family gap removed. `oracle.py` repeats the products,
the witness and the family totals without importing `verify.py`.

No fixed-tape interpreter was run. The `7548`-row manifest was not rebuilt
from `GLOBAL.jsonl`. `make frontier5599-verify` was not run. The five
framework assumptions remain.
