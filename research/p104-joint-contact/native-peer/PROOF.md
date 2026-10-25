# Four exact interfaces and the positive-width implication

For each added pair F->G, the expected base operator is the chronological circuit for Phi_F^{-1}, followed by Phi_G. The pinned compiler emits ordinary right and left monomials with a single positive rank-r child between them. The expected and emitted circuits are independently evaluated as 512-by-512 complex matrices. Every coordinate, including its sign and phase, agrees exactly.

The arithmetic representation is a complete dense vector of Gaussian integer numerators with one denominator 2^d. P/X permute addresses; D and phase multiply by exact powers of i. A signed C_q uses

```
C_q^s = ((1+s i) I + (1-s i) X_q)/2, s in {+1,-1}.
```

The retained independent engine applies these formulas directly, without a vendor tableau/state matrix comparison. Canonical common powers of two are removed only at the column endpoint, so exact vector equality implies equality on every input vector. Each column has squared norm one and exactly 2^r nonzero coordinates, binding the stated rank to actual dense support under ordinary monomial boundaries.

For a positive field width f, tensoring the proven base equality gives equality of the factorwise operators on all f digit columns. The base global phase i^theta tensors to i^(f theta); it is not dropped or replaced by i^theta. External owner ADD/SCALE coefficients occur once outside these tensor powers. When both fields have the same declared chart, transport intertwines these scalar operations. Therefore these four newly emitted chart transitions preserve the parent word's typed induction at every positive width, subject to the inherited implementation/recursive-service premises.

This implication is only for the four added interfaces. It does not prove the old common interfaces, all-column native cost implementation, the whole physical caller or its raw inverse transpose, rounded machine work, erasure or final analytic recovery. The underlying compiler and literal source definitions are credited reused code. The arithmetic execution is the exact unchanged PR5548 implementation, reused to cover new pairs.
