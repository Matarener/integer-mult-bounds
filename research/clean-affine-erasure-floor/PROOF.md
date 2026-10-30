# Clean workspace and erasure preserve the affine rank floor

This is a scoped written proof, with finite corroboration in `verify.py`.
It is not a complete multiplication theorem or a proof-kernel certificate.

## The changed boundary

Fix `d >= 1`, `G = AGL_d(F2)` and the formal group algebra `R = F2[G]`.
Write `H(g) = [[A,b],[0,1]]` for `g(x)=Ax+b`, and
`r(g)=rank_F2([A-I | b])`. All compositions act rightmost first.

There are `W >= 1` arbitrary input data registers. A finite circuit may
change its number of live registers. Every free instruction is an arbitrary
rectangular binary scalar matrix, acting identically on the address space.
This includes scalar mixing, singular maps, copying, zero allocation, reset
and discarding. Ancillas created in this way enter at zero. Arbitrarily many
initial dirty registers may also be present, provided the designated outputs
have the specified action for all their initial values.

A paid instruction at any current width is exactly #1333's instruction

`D_N(g)=I+([g]+1)N`, with `N=uv^T`, `v^T u=1`, `r(g)=1`.

Each occurrence costs one. The `W` designated output registers must equal
`[g_j]` times input register `j`, with no other data or dirty-input dependence.
Other outputs may contain arbitrary garbage and may be discarded. This is
an identity of the retained output rows over the full formal algebra.
Initial clean allocation and final output selection are free rectangular maps.
No nonlinear, input-dependent, address-dependent or postselected free operation
is included. The schedule is a fixed finite linear circuit.

**Theorem.** Even with this enlarged free-operation class, the exact minimum
paid-call count is `sum_j r(g_j)` for every finite tuple of affine targets.

The predecessor, Gareth Davidson's #1333, proves this value when all free
maps are invertible and every auxiliary input is arbitrary and restored.
Its direct attaining factorization is used below as a cited premise.
The new assertion is the lower bound under the changed clean/erasing boundary.

## A rectangular defect invariant

Let `epsilon:R -> F2` be augmentation, sending every `[g]` to `1`.
Extend `H` linearly to `R`, and entrywise to rectangular matrices.
For `M` of size `a` by `b`, put

`M_hat = H(M)`, `M_bar = epsilon(M) tensor I_(d+1)`,

`delta(M) = rank_F2(M_hat - M_bar)`.

These are ordinary rectangular binary matrices of size `a(d+1)` by
`b(d+1)`. Both hat and bar preserve every compatible product.
For an `a` by `b` matrix `U` and a `b` by `c` matrix `V`,

```
(UV)_hat - (UV)_bar
  = (U_hat-U_bar) V_hat + U_bar (V_hat-V_bar).
delta(UV) <= delta(U) + delta(V).
```

This uses rank subadditivity and the fact that multiplication on either
side cannot increase rank. It needs neither inverses nor square matrices.
In particular, any scalar rectangular map `S` has `S_hat=S_bar` and
`delta(S)=0`, even if it is singular. For a paid instruction,

```
epsilon(D_N(g)) = I,
D_hat - D_bar = N tensor (H(g)-I),
delta(D_N(g)) = rank(N) rank(H(g)-I) = 1.
```

The tensor-rank equality here is ordinary matrix rank over a field.
Induction through the actual sequence of compatible dimensions therefore
gives `delta(F) <= q` for every circuit operator `F` using `q` paid calls.

## Reading only the required outputs is enough

First omit initial dirty registers. Include clean allocation and final
selection in the circuit. The complete retained operator on the `W` data
inputs is then the formal square matrix `T=diag([g_1],...,[g_W])`.
It has augmentation `I`, so

```
delta(T) = rank(diag(H(g_1)-I,...,H(g_W)-I))
         = sum_j r(g_j).
```

Consequently `q >= sum_j r(g_j)`. Garbage is irrelevant because output
selection was already included as a free rectangular instruction. Clean
helpers need not be restored, and no assertion about their endpoint columns
was used.

If initial dirty registers are supplied, restrict their initial values to
zero by a scalar input embedding. A circuit correct for every dirty input
is correct under this restriction, with the same paid count. The preceding
argument applies. This is a lower-bound restriction, not a permission to
erase unknown data in a physical construction.

For the matching upper bound, use #1333, PROOF.md Section 4: each affine
`g_j` is a product of exactly `r(g_j)` displacement-one affine labels.
Apply that factorization on its coordinate projector. It is a formal
group-algebra identity, uses no auxiliary register and belongs to the
enlarged model. Thus the enlarged model has the same exact optimum.
The predecessor's factorization and original tariff are not new claims here.

## Scope of the inference

The defect inequality itself also holds for other group representations
and for a sum of paid defect ranks. This proof uses it only for the stated
binary-affine model and does not identify its rank with a recursive child
tariff or a physical cost. In particular, a free address map has nonzero
defect in general and cannot be added to the free scalar class silently.

The homogeneous representation is not faithful on `F2[G]`. Formal equality
implies the represented boundary used for the lower bound. Represented
equality alone cannot accept an attaining circuit. The upper theorem is
cited in the full formal algebra; every new clean/erasing finite fixture is
checked there and by a separate faithful regular-action interpretation.

Credit Gareth Davidson #1333 for the model, homogeneous displacement method
and direct affine factorization, and its eumemic #288, Ali Romman #468,
David Govea #720 and classical rank-method lineage. Rank subadditivity is
classical. No general literature-priority claim is made. This extension was
produced by Nick Petalas. Independent human and formal proof-kernel review
are unclaimed. Apache-2.0.
