# The native layer of the selected #5599 word at every column multiplicity

Prepared by Mark (Matarener) with substantial Claude Code assistance. Apache-2.0.
No new κ. Assumption ID: `native_all_columns`. This is one quantified implication at the
actual selected caller, not the whole assumption and not the other four.

## 1. Setting and conventions

Selected word: `research/p104-helper-subspace-splits/WORD.json.gz` (PR #5599, Ali Romman,
κ = 62009/20000000), on canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`.
It has 25,475 events on 748 public rows over 1,089 binary frames on nine axes; 3,447 of the
events are paid chart changes `MOVE r a b`, moving row `r` from frame `a` to frame `b`, with
2,887 distinct ordered pairs `(a,b)`. A frame `W` is a list of `r = |W|` independent binary
vectors on the nine axes.

The retained physical semantics (the selected review, #5442, #5837, #5894; `p104-native-channel/PROOF.md` §2):
a register at frame `W` with logical coordinates `u` holds the physical vector
`Γ_W^{(⊗)f} u` at column multiplicity `f ≥ 1`, where `Γ_W` is the canonical chart of `W`.
Scalar coefficients stay outside the tensor power (#5837). A paid chart change from `a` to `b`
is the operator `Γ_b Γ_a^{-1}`, which the compiler lowers to a Gaussian monomial `R`, a child
`F_r = C_{e_0} ⋯ C_{e_{r-1}}` of rank `r`, and a Gaussian monomial `L`; the recipe is `L F_r R`.

Primitive definitions used by the dense engine (`dense.py`), on the basis `|x>`, `x ∈ {0,…,511}`:

```text
P(G)        |x> ↦ |Gx>                       (G an invertible binary matrix, rows G_i)
X(b)        |x> ↦ |x ⊕ b>
D(Q,α)      |x> ↦ i^{q(x)} |x>,   q(x) = Σ_{i∈x} α_i + 2 Σ_{i<j∈x} Q_ij  (mod 4)
phase(p)    i^p I
C_q         ((1+i) I + (1−i) X(q)) / 2,     C_q^{-1} = ((1−i) I + (1+i) X(q)) / 2
Γ_W         I (r=0);  F_9 (r=9);  otherwise K F_r K^{-1}, K = D(Q_W) P(G_W),
            G_W = (W completed by unit vectors) as columns, Q_W = Gram matrix of the columns
            of G_W^{-1} over GF(2) with its diagonal complemented.
```

A Gaussian monomial record `(matrix_rows G, offset b, quadratic_rows Q, linear_Z4 α, phase p)`
is the circuit `D(Q,α)`, `P(G)`, `X(b)`, `phase(p)` applied in that order, as in
`prune_native.monomial`, `native_verify.monomial` and `lift.Monomial`.

These are the conventions the selected package verifies against; the certificate below is
about the compiler's lowered recipes under exactly these conventions.

## 2. Proposition

**Proposition.** For the selected word:

1. every one of the 1,089 canonical charts `Γ_W` is unitary and every column of `Γ_W` has
   exactly `2^{|W|}` nonzero entries;
2. for each of the 2,887 distinct paid pairs `(a,b)` and each of the 540 helper pairs
   `(initial_r, final_r)` (together 2,923 distinct maps), the operator `Γ_b Γ_a^{-1}` equals,
   entry by entry on all 512 × 512 entries and including the absolute phase, the lowered
   recipe `L F_r R`; its common column support is `2^r` with `r = |dim b − dim a|`, which is
   the paid rank charged by the invoice for that move (rank mass 6,014 over the 3,447
   occurrences) and, for helpers, the strictly positive productive rank;
3. each of the 208 main adapters `Γ_{⟨q⟩} C_q^{-1}` (source) and `F_9 C_q^{-1} Γ_{final}^{-1}`
   (target) is a Gaussian monomial equal to its rank-zero recipe;
4. the certified recipes are byte-identical to the author's registered recipe payload
   (`RESULT.json` `native.recipe_payload_sha256`);
5. every one of the 3,711 distinct Gaussian monomial factors occurring in (2) and (3) is
   realized by a fixed list of at most 96 records (bound 171) `XROW`, `NOT`, `S`, `CZ`, `I` of the #5445 grammar, independent
   of `f`, which executes `m^{(⊗)f}` exactly on explicit addresses with spectators untouched.

**Corollary (all widths).** For every `f ≥ 1`, every paid chart change, helper normalizer
and main adapter of the selected word acts at column multiplicity `f` as
`(Γ_b Γ_a^{-1})^{(⊗)f} = L^{(⊗)f} F_r^{(⊗)f} R^{(⊗)f}`, where `L^{(⊗)f}` and `R^{(⊗)f}` are
the executed record lists of (5) and `F_r^{(⊗)f}` is the rank-`r` child at width `f`.
Hence the width-free rational rows of the scalar program (#5837) remain the logical
coordinates of the physical vectors at every positive column multiplicity across the whole
native layer of this word, with the paid ranks unchanged.

## 3. Proof

**(1) and the support rank.** `dense.py` builds every `Γ_W` as a dense matrix of Gaussian
integers over `2^d` by applying the primitives of §1 to the identity; `Γ_W Γ_W^† = 4^d I` is
checked by one exact matrix product per frame. A Clifford operator on nine axes maps each
basis vector to `2^r` basis vectors of equal modulus for one `r`; the verifier counts the
nonzeros of every column and requires a common power of two. This is an independent
definition of the rank: it never consults the tableau's `X`-block.

**(2) and (3).** For each pair the verifier forms `Γ_b Γ_a^{-1} = Γ_b Γ_a^†` by one exact
product of the two dense unitary matrices (no adjoint-circuit rule is used), builds the dense
matrix of the candidate recipe from its monomial records and `r` gates `C_{e_i}`, normalizes
both by dividing out common factors of two, and requires equal denominators and equal
arrays. Equal matrices have equal absolute phase; no separate phase argument is needed. The
rank identity `r = |dim b − dim a|` is the invoice rule of `local.replay`; (2) checks that the
operator's support rank, the recipe's child rank and the invoice rank coincide. For helpers
the same check uses `(initial_r, final_r)` and requires `dim final > dim initial`. For the
adapters, `is_monomial` requires denominator zero and exactly one entry from `{±1, ±i}` per
column.

**(4).** The verifier hashes `[[a,b,recipe]] + adapters` exactly as the selected `local.native`
does and compares with the registered digest. So the operators certified here are the ones
the selected package registered, not a fresh compilation that might differ.

**(5)** is the record lemma of `research/selected-monomial-tape-lift/PROOF.md`, executed on
this word's factors: the record list of a monomial is built by Gaussian elimination of `G`
(`XROW` row additions and three-`XROW` swaps), translations `NOT` for `b`, unit phases `S`
for `α`, controlled signs `CZ` for the off-diagonal of `Q`, and `I` for the global phase;
each record acts on all `f` columns at once and reads no spectator. The verifier executes
every distinct factor's list on all 512 addresses at `f = 1` and on sampled addresses at
`f = 2, 3`, comparing with the lift formula
`|X> ↦ i^{p f + Σ_j q(x_j)} |(G x_1 ⊕ b, …, G x_f ⊕ b)>`.

**Corollary.** Equal operators have equal tensor powers, and the mixed-product identity
`(AB)^{(⊗)f} = A^{(⊗)f} B^{(⊗)f}` factors the power of the recipe gate by gate
(#5442, Lemma, "group identities lift"). The direction that matters is the easy one: a
width-one identity between *products of primitives* lifts. What does **not** lift is a
width-one *linear relation with fixed external coefficients*: the verifier checks on the
first MOVE (event 9589, frame `[]` → `[11]`, active axes 0, 1, 3) that
`U = ((1+i) I + (1−i) X_{11} Z_3)/2` (the closed form of #5894) satisfies
`U^{(⊗)f} = L^{(⊗)f} C^{(⊗)f} R^{(⊗)f}` at `f = 2, 3`, while
`((1+i) I^{(⊗)f} + (1−i) (X_{11} Z_3)^{(⊗)f})/2 ≠ U^{(⊗)f}`. This is why the physical word
must execute the three factors (two record lists and one rank-one child), never the two-term
closed form, and it is the same Reynolds-type trap recorded in #5442's controls. ∎

## 4. What this does and does not discharge

Discharged for the selected word, at every `f ≥ 1`: the algebraic content of
`native_all_columns` (every paid chart change, helper normalizer and main adapter is the
tensor power of an exact group element that the physical word realizes factor by factor),
with the paid ranks of the invoice, by independent dense verification; and the record-level
realization of all monomial factors.

Still inherited: the tariff of each record (the compact-control Proposition, in its domain
`f ≤ p`), the front/back control-field reservations of the actual #5599 caller layout for every
active slot pair, spectator handling of the rank-`r` children, whole-job adapters of the
physical caller, and the four assumptions `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery`. No selected value, outer row or κ changes.

## 5. Credit

Ali Romman (#5599 word, invoice and `local.native` registration; #5565 base via Pierre-Loic
Doulcet / hexapode), Chris R / Clear1nsight (independent signed-Pauli/state interpreter lineage,
`native_verify.py`), unpaidmoon (#5837, scalar lift and the precise MOVE question), DLamdata
(#5894, coverage trace and the closed form of event 9589), zxv (#5428 target), Dugongue and
icekylinx (Clifford engine lineage), Cinna Davis (compact-control notes), and the retained
native, compiler and controller lineage credited in `research/p104-helper-subspace-splits/README.md`.
The lifting lemma and record grammar are #5442 and #5445 (Matarener). No independent human or
proof-kernel review.
