# Audit of the HALO.md polynomial locality witness (#4100)

**Scoped proof audit plus a finite exact certificate. No new κ.** This checks
one auxiliary lemma of the proposed unconditional construction in
[#4100](../unconditional-batched-crt/README.md). It does not accept the
construction, recertify its cost ledger, or check the Gaussian matrix itself.

## The proposition and its caller

[HALO.md](../unconditional-batched-crt/HALO.md) supplies the locality step that
[GAUSSIAN.md](../unconditional-batched-crt/GAUSSIAN.md), "Core locality and
explicit enumeration of corrections", uses for the narrow inverse direction.
Its hypotheses: H is a periodic matrix of physical bandwidth W<p, and H and
each contiguous principal section have 2-norm and inverse 2-norm at most
p^10. GAUSSIAN.md and
[INVERSE-CONDITIONING.md](../unconditional-batched-crt/INVERSE-CONDITIONING.md)
supply those bounds from the row gap. With Q=I-p^-20 H*H and J=ceil(p^42),

    P = p^-20 sum_{j<J} Q^j H*.

HALO.md claims (1) P has bandwidth <=(2J+1)W<p^45, (2) ||P-H^-1||_2 <= p^10
exp(-p^2), and (3) a row at distance A=ceil(p^48) from a section edge equals
the global row exactly. It then bounds the core error by g p^(10g) exp(-p^2)
and the sparse correction cost by O(V[d/g + d g A^3/L + d A p^2/L] polylog p),
with L=2^ceil(400 log2 p).

## Result

All three implications hold as stated. The written proof:

1. **Error.** H*H has spectrum in [p^-20, p^20], so Q is Hermitian with
   spectrum in [0, 1-p^-40]. Since p^-20 (I-Q)^-1 H* = (H*H)^-1 H* = H^-1 and
   Q commutes with H*H, the truncated series satisfies the exact identity

       P - H^-1 = -Q^J H^-1.

   Hence ||P-H^-1||_2 <= (1-p^-40)^J p^10 <= exp(-J p^-40) p^10 <= p^10 exp(-p^2).
   The p^10 factor is correct. Bounding the tail term by term, without this
   identity, gives the weaker p^30 exp(-p^2), which is still enough downstream.
2. **Bandwidth.** H* has bandwidth W and Q has bandwidth 2W, so Q^j H* has
   bandwidth (2j+1)W. The largest term, j=J-1, gives exactly **(2J-1)W**,
   which is below HALO.md's (2J+1)W. With W<=p-1, (2J+1)W <= (2p^42+1)(p-1) < p^45.
3. **Row exactness.** A section changes row i of H*H only when i is within W
   of the section edge, and row i of H* likewise. Row r of Q^j H* reads rows of
   Q within 2W(j-1) of r and rows of H* within 2Wj. So row r of the section
   polynomial equals the global row whenever its distance to the edge exceeds
   **(2J-1)W**. That radius is sharp: on every instance below, some row at
   distance exactly (2J-1)W differs. A=ceil(p^48) is far larger than the radius,
   so the claim holds with a wide margin.
4. **Core error constant (minor).** On a core box, the per-axis difference
   between the section inverse and the global inverse row is at most
   ||H_sec^-1-P_sec|| + ||P-H^-1|| <= 2p^10 exp(-p^2). The telescoping sum
   then gives 2g p^(10g) exp(-p^2), up to the norm of P (also at most p^10 up
   to a factor 1+exp(-p^2)), not g p^(10g) exp(-p^2). The extra factor 2 is
   absorbed by the stated 2^-Cp margin. No downstream inequality changes.
5. **Parameters.** L >= p^400 > 4A. The two sparse exponents are
   epsilon+beta+144-400 and epsilon+50-400. Both are negative for epsilon,
   beta<1. The cost expression is the per-group bound
   (gA/L)V(gA^2+p^2) summed over d/g groups.

Nothing in this lemma needs the Gaussian structure beyond the stated norm and
bandwidth bounds, so the audit applies at its GAUSSIAN.md caller exactly when
those hypotheses hold there. This package does not re-derive them.

## Executable evidence

[verify.py](verify.py) uses only the standard library and exact rationals.

- **Source binding.** It checks that HALO.md still states six exact phrases:
  J, the bandwidth, the error, A, L and the core error.
- **Five instances.** These are cyclic H=I-E, with E having band W and entries
  ±1/(8W), for (n,W,J) = (16,1,2), (16,1,3), (20,1,4), (24,2,2) and (26,2,3),
  with c^2=5 standing in for p^20. Each instance checks:
  - c^-2 I < H^T H < c^2 I exactly, for H and for its section, by an LDL^T
    positive-definiteness test;
  - the identity P-H^-1 = -Q^J H^-1 exactly;
  - ||Q^J H^-1||_2^2 < c^2 (1-c^-4)^(2J), by an exact positive-definiteness
    certificate;
  - the bandwidth of P is exactly (2J-1)W;
  - section rows agree exactly beyond the radius (2J-1)W, and at least one
    row at distance exactly (2J-1)W differs.
- **Three controls.** Exactness one step inside the radius fails on every
  instance. c^2=1 is rejected by the spectral check. The unbanded
  INVERSE-CONDITIONING example E[i,0]=1/4 gives P full cyclic bandwidth.
- **Parameters.** For every integer 2<=p<=64, it checks (2J+1)(p-1) < p^45 and
  < A, and L >= p^400 > 4A, at the real J, A and L. It also checks the
  sparse exponents.

```text
PASS_HALO_LOCALITY_WITNESS source_phrases=6 instances=5 controls=3 parameter_p=2..64 (63) no_new_kappa
```

## Reproduce

From the repository root (CPython 3.12, standard library only):

```sh
python3.12 -B scripts/research_package.py --package research/halo-locality-witness-audit --check-only
python3.12 -B scripts/research_package.py --package research/halo-locality-witness-audit
python3.12 -B research/halo-locality-witness-audit/verify.py
```

The verifier runs in under one second.

## Limitations

- The instances use scaled parameters (c^2=5, J<=4, W<=2), not c=p^10 and
  J=ceil(p^42). The all-size statement rests on the written argument above.
  The finite instances test the argument's exact identities and the sharp
  radius; they do not replace it.
- The norm and bandwidth hypotheses at the Gaussian caller are not
  re-derived here. These are GAUSSIAN.md's row-gap estimate and
  INVERSE-CONDITIONING.md.
- The source-driven enumeration, the halo cost ledger rows, the tensor
  rounding budget and the broad forward direction are not audited.
- This is not a formal proof-kernel check, and it is not an independent
  human review.

## Open next questions

1. **Does GAUSSIAN.md's row-gap estimate survive truncation, rounding and
   alias removal at the narrow reference matrix?** HALO's hypotheses depend on
   it. A first step is to evaluate the sharp PR1673 row estimate
   ||N-I||_inf <= exp(-2a theta)+5exp(-2a) on exact rounded rows for a
   moderate p and theta=1/(4p^2).
2. **Is GAUSSIAN.md's source-driven enumeration of the 2g enlarged
   rectangles charged correctly when one address lies in many rectangles?**
   This is the remaining cost obligation in the same correction step.

## Credit

Produced by Nick Petalas. The audited lemma and its caller are Cinna Davis's
#4100 package, which retains its own predecessor attribution in
[NOTICE.md](../unconditional-batched-crt/NOTICE.md). The row-gap input traces
to PR1673's capped-phase audit. New work is Apache-2.0.
