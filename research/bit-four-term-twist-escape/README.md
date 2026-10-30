# Four contributions survive the dirty degree-one twist condition

**Scoped written proof with an exact finite certificate; no new κ.**
This answers the four-contribution case of Open next question 1 in
JoyboyBrian's [PR #5490](https://github.com/CrocSwap/integer-mult-bounds/pull/5490)
(`research/bit-three-term-twist-rigidity`). That package shows that three
off-diagonal contributions in the two-sided address-twist model force the
role-s residue β = Σ U_j⁻¹ a_j to vanish. That vanishing is what excludes its
eight-call pattern.

For four contributions satisfying the same necessary conditions,
Σ a_j = 0 and Σ a_j·(U_j z) = 0 in Sym²(V) with V = M_m(F2):

| m | Result |
|---|---|
| 2 | β = 0 for all frames. The exhaustive check covers all 46,656 normalized transport triples. |
| ≥ 3 | β ≠ 0 only if all four frames equal one x ≠ 0 and U₁+U₂+U₃+U₄ = 0. Then rank β ≤ 2·rank x. |
| ≥ 3 | Sharp: a field-multiplication family with rank-one x and four distinct transports gives rank β = 2. |

So the three-term rigidity does **not** extend to four contributions once
m ≥ 3, but the escape is narrow. All four role-r frames must agree modulo
two, the transports must sum to zero, and the residue has rank at most two
for rank-one frames. [PROOF.md](PROOF.md) has the statement and the all-m
proof.

This concerns the degree-one necessary conditions in one block. It is not a
synthesized word, a realization of I_m diagonal targets, a native tariff, a
supplier or a multiplication theorem.

## Evidence

- Part 1 (m = 2) is a finite certificate. For each normalized triple, the
  verifier solves the linear system for all frames, not only rank-one
  frames, and checks β = 0 on a kernel basis.
- Part 2 (m ≥ 3) is a written proof. It uses PR5490's rank-distance lemma,
  linear Koszul syzygies and a classification of four-term rank-one tensor
  relations Σ L_j ⊗ R_jᵀ = 0 with invertible factors.
- Part 3 is checked for m = 3, 4, 5, 6 by evaluating the products in
  Sym²(V) directly. The checks also cover pairwise rank distance, the
  transport relation, rank β = 2 and a perturbed-frame negative control.
  The all-m argument is in PROOF.md.
- Controls: the three-term lemma at m = 2, unnormalized m = 2 spot checks,
  300 random m = 3 triples (none escapes), and the SHA256 of the pinned
  PR5490 proof.

## Reproduce

From the repository root:

```sh
python3.12 -I -W error -B research/bit-four-term-twist-escape/verify.py
python3.12 -I -O -W error -B research/bit-four-term-twist-escape/verify.py
python3.12 -B scripts/research_package.py --package research/bit-four-term-twist-escape
```

The expected last line is `PASS_FOUR_TERM_TWIST_ESCAPE`. Each run takes about
two seconds and uses only the standard library.

## Open next questions

1. **Can a complete pattern use the rank-two residue?** A four-term block
   leaves up to rank two in the diagonal, where PR5490's three-term blocks
   leave rank one. First choose a projector pattern with one block fed by four
   calls whose role-r frames agree mod 2. Then impose a field-family transport
   relation and check every other block and the PR5003 second-order cross
   terms before any synthesis. Native twist prices remain unknown.
2. **What happens with five or more contributions?** The rank bound comes
   from a short classification of four-term tensor relations. Start with the
   exhaustive m = 2 census at k = 5 (36⁴ normalized quadruples), then classify
   five-term relations. Frames that span two or three dimensions can now
   combine with transport relations, so the four-term case split no longer
   suffices.

Structured versions are in [TASK.json](TASK.json).

## Credit

Produced by Nick Petalas. JoyboyBrian's PR #5490 supplies the model
reduction to condition (1), the rank-distance lemma and the three-term
lemma used here. Krzysztof Wójt's PR #5003 supplies the second-order
quotient and source compatibility, and JoyboyBrian's PR #4953 the two-sided
twist model. Retain the Cinna Davis/PR2110, Ali Romman, eumemic and huxint
lineage credited there. The four-term classification, the m = 2 census and
the field witnesses are new here. Apache-2.0.
