# Occupied colors, not all K residues, are the macros

## Statement

CRT.md §4 colors targets by current position modulo `K` and charges one
switch layer as `O(K)` colors. The macros that the same paragraph prices
are the occupied colors. On every batch cut by the pinned #4174 layout,

```text
c ≤ r ≤ r_max,
```

where `r` is the number of active targets, `c` is the number of distinct
residues modulo `K`, and `r_max` is that layout's batch cap. Empty residues
are not macros. A same-color pair is one macro.

At the recomputed production point `d = 65536`, `ell = 24`, alternating
widths `24/23`, this cap is `r_max = 5` and `K = 196608`. The color factor
in the §4 layer sentence may be `5` rather than `196608`. The ratio is the
exact rational `196608/5`. No new κ is claimed. #4100 is not accepted.

## Definitions

A batch is a finite set of active target positions. Its target count is `r`.
For an integer `K ≥ 1`, the occupied-color count is

```text
c = |{ position mod K : position is an active target }|.
```

The pinned layout, transcribed from
`research/pr4100-guard-coloring/vendor/pr4174_allocator.py`
(`Layout.__init__`), sets

```text
logarithm = ceil(log2(p + 2)),
G = 64 (ell + logarithm),
K = 64 G,
r_max = L // (100 G),
H = r_max G,
```

with `L` the total width and `p` the precision parameter passed to the
constructor. The constructor cuts each right-child stream into consecutive
groups of at most `r_max` axes, so every batch it emits has `r ≤ r_max`.

## Lemma 1

For any batch and any `K ≥ 1`, `0 ≤ c ≤ min(r, K)`. Also `c = r` if and
only if the `r` residues are pairwise distinct.

Proof. The residue map sends the `r` targets onto a set of size `c`, so
`c ≤ r`. The codomain has `K` residues, so `c ≤ K`. The map is bijective
onto its image exactly when no two targets share a residue, which is
`c = r`.

## Lemma 2

Every batch emitted by the pinned layout satisfies `c ≤ r_max`.

Proof. The layout's own cut gives `r ≤ r_max`. Lemma 1 gives `c ≤ r`.

A collision does not increase the macro count. If two targets differ by a
nonzero multiple of `K`, then `c < r`, so the occupied-color bill is
strictly smaller than one macro per target. The `(K−1)`-bit guard
separation that lets those two targets share one macro is the lemma in
`research/pr4100-guard-coloring`; it is cited, not replayed.

## Substitution into the §4 cost line

CRT.md §4 says the coloring "uses `O(K)=O(ell+log p)` colors", that one
color costs `O(V H^(1-a)+V)`, and that with `K` colors and `H≤L=O(p)` one
switch layer costs `O(V p^(1-a) (ell+log p))`. The factor `ell+log p` is
the `O(K)` color count. Replacing that count by the occupied-color count
replaces the layer bound by

```text
O(c (V H^(1-a) + V)),    c ≤ r_max.
```

On a layout whose `r_max` and `H` are fixed integers, the color factor is
the integer `r_max`, not the integer `K`, whenever `r_max < K`.

## Production corollary

Take `d = 65536`, `ell = 24`, and `p = 6L`, which is the constructor call
in `research/pr4100-guard-coloring/verify.py`. Alternating widths `24, 23,
24, 23, ...` give

```text
L = 1540096,  logarithm = 24,  G = 3072,
K = 196608,   r_max = 5,       H = 15360,
y-bit count = 1494016.
```

These are the production row of that package's table. Lemma 2 gives
`c ≤ 5` on every batch, while the written sentence multiplies by
`K = 196608`. The color factors are in the exact ratio

```text
K / r_max = 196608/5.
```

The same constructor with every width `23` (nominal `ell = 24`) gives
`L = 1507328`, the same `K = 196608`, and `r_max = 4`. That is the table's
uniform-`23` row. Its color ratio is the integer `196608/4 = 49152`.

## What this does not say

The §5 product `O(V p^(1-a) ell^2 polylog p)` still hides `K` inside the
polylogarithmic factor. This note does not rewrite that line and does not
rerun the 104,864-plan census. It does not build the literal many-target
tape macro, does not change a selected supplier, and does not accept #4100.
The selected conditional exponent stays `605457647/200000000000`.
