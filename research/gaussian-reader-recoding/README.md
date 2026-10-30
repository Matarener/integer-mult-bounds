# Gaussian reader repair with an arbitrary borrowed centre

**The proved result repairs an actual rank-30 Gaussian reader mismatch with no additional Gaussian request or centre bank. A funded κ ≥ 0.0035 has not been established.** The construction preserves every arbitrary borrowed centre baseline; it does not assume clean centre data and does not reverse an erasure.

For the retained fixed and moving readers D₀,D₁ of the same section J, set Δ=D₁−D₀. Since D₀J=D₁J=I, one has ΔJ=0. The four chronological ordinary shears

    z += Δa;
    a += Jz;
    z -= Δa;     using the updated a
    a -= Jz

implement exactly

    (a,z) ↦ ((I+JΔ)a,z).

Their inverse changes only the two data-shear signs. The resulting recoding converts the actual fixed-reader section into the moving-reader section by an explicit whole-state conjugacy. All scalar kernels, translations and their finite implementation costs remain charged. A separate worker reviewed the proof and the all-width realization.

## Mathematical deliverable

- [reader-kernel.md](reader-kernel.md) gives the four-shear borrowed-centre implementation, inverse, section conjugacy, actual rank-30 substitution, uniform finite-translation-kernel theorem and precisely scoped norm bounds.
- [coded-provider.md](coded-provider.md) proves the actual fixed/moving-reader recoder and transported-reader identities, plus a baseline-preserving reflection factor. It follows the construction into the retained source services and keeps the thirty-row and sixteen-row interfaces distinct.
- [retirement.md](retirement.md) gives an explicit Gaussian two-helper endpoint reconstruction, four removed H1 requests with both H4 target debits, and a proved four-port entry syzygy. Its concrete profile is stated without claiming it profitable.
- [consumer.md](consumer.md) proves a clean-bank post-swap tile, a complete three-tile Gaussian word, a complete complementary-C two-call word, and an explicit chirped two-sided monomial equivalence of the nine-axis Gaussian. The complete invoices and compatibility scope accompany each construction.

This README is the fifth mathematical document. All proofs are informal. No numerical pricing, mathematical computation, solver, source replay, Lean run or web search was performed. Local source words were viewed only as text. The publication helpers outside this directory transport frozen document bytes and do not evaluate mathematics.

## Exact scope of the reader repair

The actual source data are

    J=Q²U,    D₀=(VQ²U)⁻¹V,    D₁=(VU)⁻¹VQ².

The retained rank-30 source supplies both inverses in their admitted scalar/finite-translation classes. The recoder K=I+J(D₁−D₀) has the explicit square-zero inverse K⁻¹=I−J(D₁−D₀), satisfies KJ=J and D₀K=D₁, and converts the complete section swap by

    S(J,D₁)=diag(K⁻¹,I) S(J,D₀) diag(K,I).

Each outside recoding uses the existing arbitrary centre and returns it unchanged, even when the intervening section has changed its value. There is no extra owned-bank reserve for these recodings. The source's actual common-frame, ROW, spectator and translation realization is required; differently routed frames are not silently identified.

The new kernel theorem constructs one finite coefficient list valid at every positive tensor width from finite character inverses. It does not expand a Gaussian into exponentially many per-column terms or assume a width-dependent inverse oracle. The proof separates coordinate norms at shear boundaries from the additional primitive-interior bounds required by a rounded implementation.

## Funding status

No complete Gaussian supplier above 0.0035 is proved by these notes. The rank-30 recoder repairs one reader mismatch. The retained sixteen-row joined D25 forwards use a different reader and a different data/centre split, so this thirty-row correction is not substituted as their missing inverse. A source's completed output frame F_t also does not provide an input conjugation through the preceding F_(t−1) on newly fresh axes.

The two completed consumer words have explicit independent Gaussian targets, but their supplied paid profiles do not fund the intended exponent. The new two-helper retirement similarly removes four H1 requests while debiting two H4 targets; no further entry requests are deleted merely because their arguments satisfy a relation across different Gaussian directions.

The prior four-partial-helper BIT retirement retains its proved gain 72(1+3^t−4^t)>0, but ordinary BIT admission above 0.0035 was not completed there. Both that admission and a compatible funded Gaussian provider are needed before a whole multiplication κ claim. Neither is inserted here as an assumed unknown gadget.

## Predecessor credit and coverage

The primary reader constructions use `research/reciprocal-native-responses` and its rank-30 annex, `research/centre-code-services`, `research/native-centre-capture` and `research/centre-metric-encoders`. Their retained notices give campaign-lane credit and explicit predecessor PR3133, PR3148, PR2588 and PR2226. The moving section and fixed-reader phase inverse are predecessors; the new contribution is the exact recoding connection and its borrowed-centre implementation. No owning PR is inferred where the source does not name one.

The Gaussian provider and controller notes retain Dillon Amburgey PR5402; Chris R / Clear1nsight PR5407/PR5413; Ali Romman PR5383/PR5398 and the centre/reciprocal lineage; Cinna Davis PR4694/PR4698 and controller work; Cao Yifan; DaysSky; Nick Petalas; Ryanson Jonathan; zxv; Jacob Alan Sussman; Dugongue and all source-specific Clifford, native, compiler, stock, precision and analytic contributors. The earlier BIT result retains ai-nanachi PR5512, Ali Romman PR5421, compact436/PR4326, PR4760/PR4814, DreamingOfClouds PR589, eumemic PR555, rohanarun and the complete source lineage.

The source comparison is offline at retained main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, with earlier local proof manuscripts and linked Schur-elimination/symplectic transport precedents. No current-PR, worldwide-priority, independent-human, formal-kernel or selected-frontier acceptance claim is made.

Prepared for Dugongue with substantial OpenAI Codex assistance from one coordinator and three workers. New text is offered under Apache-2.0; predecessor notices and attribution remain unchanged.
