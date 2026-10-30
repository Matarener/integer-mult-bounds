# Shape constant A = 0 for the selected m=73 complex stock divisor

## Claim

Let C(w) be the per-level divisor candidate given by the selected m=73 complex
producer's finite stock invoice: the product of the fixed group order
|Sp(72,2)| and the fixed 14,826 physical families, whose bit length B_bits = 2642
was already bound by `research/selected-stock-envelope-m73` (PR #3113). Under the
finite-stock-as-C reading already named in
`research/selected-coarse-depth-stock/PROOF.md`,

```text
log_2 C(w) <= A * w + B
```

holds for every atom width w >= 1 with **A = 0** and **B = 2642**.

The leaf reserve constant rho in

```text
sigma <= (43/26) * (1 - s) * (A + B) + rho
```

remains unbound. Selected kappa is unchanged.

## Ordinary contrast (why A is positive for BIT)

For the selected ordinary BIT producer (PR #2084 / `selected-bit-parent-reserve`),
the level divisor is realized over the local ring:

```text
|GL_m(Z/q^w Z)| = |GL_m(F_q)| * q^{m^2 (w-1)}.
```

The factor q^{m^2(w-1)} is an atom-width digit tower. With m = 64 it yields the
source-bound linear envelope

```text
log_q W_q(w) < 4096 w + 1 <= 4097 w,
```

so any shape bound log_q C(w) <= A w + B for that producer requires A >= 4096.
The same tower appears as W(w) = W_0 q^{m^2(w-1)} in `notes/three-stage-cover-bit.tex`,
with the m^2(w-1) digits charged in the row reserve.

## Complex case (why A = 0)

1. **No digit-tower cover.** The pinned complex cover note
   `notes/three-stage-cover-complex.tex` contains neither W(w) nor q^{m^2(w-1)}
   nor a Z/q^w local-ring realization. Its Sp(U) → O lifts are parametrized by
   u ∈ U and c ∈ F_2 — binary parameters inside a finite orthogonal group, not
   atom-width digits.
2. **Finite role counts retained.** The same note states that the full finite
   role counts are retained in the scalar guard and row stock, and that group
   elements are specified by binary matrices.
3. **Selected stock factors are w-free.** The selected invoice charges a fixed
   Sp(72,2) order and a fixed family split 14336 + 480 + 8 + 2 = 14826. Neither
   factor depends on atom width w. Their combined bit length is the already-bound
   B_bits = 2642.
4. **Zero slope.** For every pair of atom widths w1 < w2 the charged stock bit
   length is the same constant 2642, so the discrete slope of log_2 C is zero.
   Hence A = 0 and B = 2642 satisfy the shape inequality at every probed w.

## Composition consequence

Substituting A = 0 and B = 2642 into the retained composition gives

```text
sigma <= (43/26) * (1 - s) * 2642 + rho.
```

This is not a closed envelope: rho is still unbound, and adopting the finite
stock as uniform C(w) remains the physical/compiler admission named in the
coarse-depth proof. Historical m=120 coefficient 57604 and external slack 252
are not substituted.

## What this package does not claim

- It does not recompute |Sp(72,2)| or the 2642-bit decomposition as a new result.
- It does not bind rho or prove a numerical sigma.
- It does not change selected kappa, suppliers, frontiers, or cutoffs.
- It does not identify the ordinary BIT m=64 producer with the complex m=73 producer.
