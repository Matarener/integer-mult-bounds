# Formal core

Prepared by conorholds with substantial OpenAI Codex assistance. The mathematical
lineage and retained predecessor credits are in the package's main proof and
source manifest.

`formal/QuarterCore.lean` is a partial Lean formalization of the new local
capacity and the final sparse-cover argument. It does **not** formalize the full
P112 theorem or the complete E8-to-binary-model reduction.
`formal/DimensionDeletion.lean` additionally formalizes the abstract
dimension-deletion argument for actual code subspaces and basis coefficients.

## Statements checked in Lean

The explicit four-coordinate quadratic form is
`q(x) = x₀x₁ + x₂x₃` over F₂. Binary coordinates are represented by `Bool`;
addition is `Bool.xor` and multiplication is `Bool.and`.

| Declaration | Kernel-checked content |
| --- | --- |
| `quadric4_card` | The form has exactly six one-points. |
| `quadric_hyperplane_cap` | Every nonzero four-coordinate normal and either affine offset give at most four one-points. |
| `quadric_no_affine_plane` | Four distinct one-points never sum to zero under coordinatewise binary addition; the six one-points contain no affine two-plane. |
| `quadric_pair_avoiding_section` | Every pair of distinct one-points is avoided by a nonconstant affine hyperplane section containing exactly four one-points. |
| `quarter_card` | Repeating those six points over two free radical coordinates gives 24 points. |
| `quarter_radical_cut_card` | A cut nonconstant on the radical has exactly 12 points, for every remaining normal and either offset. |
| `quarter_constant_radical_card` | A radical-constant cut has four lifts per point of the four-coordinate section. |
| `quarter_hyperplane_cap` | Every nonconstant affine linear cut of this six-coordinate quarter has at most 16 points. |
| `quarter_capacity_sharp` | An explicit normal and offset attain 16. |
| `core_cover_card_le` | For any finite core C avoided by H, a cover by L, H and E implies `C.card ≤ (C ∩ L).card + E.card`, including arbitrary overlaps. |
| `unpunctured_quarter_exceptional_floor` | An unpunctured 24-site quarter and a capacity-16 low part force at least eight exceptional sites. |
| `no_sparse_cover_of_at_most_three_deleted` | A 24-site core, at most three deletions, a capacity-16 low part, a high part avoiding the core, and four exceptional sites cannot cover the live core. |
| `no_sparse_cover_with_self` | The same obstruction with at most four deletions holds when an additional external self site must be covered, and carrying self reduces the low part's core capacity to 12. |

The finite-coordinate statements use `decide`: Lean's kernel checks the finite
reduction. They use neither `native_decide` nor an external computation as an
axiom. The capacity-16 theorem combines the two radical cases with the
capacity-four theorem. The covering theorems are general `Finset` proofs; their
sets may overlap, and the proofs preserve the separate self site. In the
self-carrying case they use the capacity-12 premise. Otherwise they erase self
from the exceptional set, leaving at most three exceptional core sites.

`formal/DimensionDeletion.lean` proves the following four additional results
over any division ring. Its results concern actual vectors and scalar
coefficients, rather than a support-union relaxation.

| Declaration | Kernel-checked content |
| --- | --- |
| `exists_nonzero_annihilating` | Any finite family of scalar linear constraints smaller than the dimension has a common nonzero kernel vector. The constraints may be dependent or zero. |
| `exists_nonzero_in_submodule_annihilating` | The vector can be required to lie in a prescribed finite-dimensional submodule; the ambient space need not be finite-dimensional. |
| `exists_nonzero_after_basis_deletion` | Deleting fewer than `dim D` basis coordinates leaves a nonzero vector of D with those coefficients zero and lying in the span of the undeleted basis vectors. |
| `exists_codeword_after_dimension_minus_one_deletions` | Given a basis of the piece span T, every choice of `d - 1` deleted pieces leaves a nonzero ambient codeword in C in the span of the undeleted pieces, where `d = dim(C.submoduleOf T) > 0`. |

Here `C.submoduleOf T` is the code intersection viewed as a submodule of T.
The last result retains code membership, nonzero ambient value, the killed
coefficients and the remaining-span membership explicitly. It therefore
formalizes the abstract dimension-deletion mechanism used by the caller
argument, without assuming the P112 theorem or a rank-capacity conclusion.

## Scope left outside Lean

The handwritten proof must still supply these identifications and premises:

* E8/P112 roots, the punctured orthogonal frame, root-code supports including
  self, and their exact binary labels; root-direction rigidity and the
  root32-completion argument.
* An affine quadratic isomorphism between the deleted full quarter and the
  explicit 24-point normal form, and containment of a rank-six label-flat
  section in one of the nonconstant affine cuts checked here.
* The frame-deletion count, avoidance by the completed rank-seven part, and
  the rank-five/capacity-12 implication when the rank-six part carries self.

These are genuine remaining formalization obligations. They are stated as
ordinary parameters in the finite-set results where relevant; no custom
axiom or theorem asserting the P112 conclusion is introduced. The formal files
also do not formalize the sharp five-site root-code witness, characteristic-zero
transfer, the exact downstream C1 row inventory, or the actual marked decoder
and full invoice bridge. The finite pair-avoidance result supplies a local
construction premise; its E8/root/frame instantiation remains outside Lean.
The additional intrinsic (7,7,5,5) theorem in D2-PROFILE.md, including
its projective-reflection and coefficient-sign argument, is also outside Lean.

## Reproduction and observed result

Checked with Lean `4.21.0`, mathlib commit
`308445d7985027f538e281e18df29ca16ede2ba3`. Existing cached oleans were used;
no `lake build`, download, or dependency update was performed.

Set `MATHLIB` to that cached mathlib checkout, `LEAN` to its Lean 4.21.0 binary,
and `PACKAGE` to this package's absolute directory. The exact compile invocation,
apart from those machine-specific directory values, is:

```sh
cd "$MATHLIB"
LEAN_PATH='.lake/build/lib/lean:.lake/packages/batteries/.lake/build/lib/lean:.lake/packages/aesop/.lake/build/lib/lean:.lake/packages/Qq/.lake/build/lib/lean:.lake/packages/proofwidgets/.lake/build/lib/lean:.lake/packages/LeanSearchClient/.lake/build/lib/lean:.lake/packages/importGraph/.lake/build/lib/lean:.lake/packages/plausible/.lake/build/lib/lean' "$LEAN" -DwarningAsError=true "$PACKAGE/formal/QuarterCore.lean"
```

Compile `formal/DimensionDeletion.lean` with the same command, replacing the
final filename. The two targeted checks were scheduled sequentially and both
exited `0` on 2026-10-18, with warnings treated as errors. The measured real
times for the completed versions were 14.93 seconds for `QuarterCore.lean`
and 20.01 seconds for `DimensionDeletion.lean`.

`#print axioms` is included for every public theorem. All seventeen report exactly
`[propext, Classical.choice, Quot.sound]`; none reports `sorryAx`, a custom axiom,
or a native-evaluation axiom. This is a passing check of the listed formal core,
not a kernel proof of the entire package theorem.

## Additional shared-piece algebraic core

`formal/SharedPiece.lean` adds two checked declarations:

* `shared_piece_cross_product`: four evaluations supplied by one piece
  satisfy A*D=B*C under explicit associative, commutative multiplication.
* `no_shared_piece_at_two_root_self_sites`: self entries2 and a common
  off-diagonal entry0,+1 or-1 contradict that identity. The injective
  natural-number embedding and the four needed square laws are explicit
  ordinary parameters, not custom axioms.

This file imports **Init only**. Its ring instantiation, identification of
root pairings and assembly with the RIGIDITY.md geometry remain outside
Lean. The identity reports no axioms; the self-site theorem reports only
`propext`. The existing seventeen declarations are unchanged and retain
exactly their earlier reported standard axioms.

The new file passes Lean4.21.0 with `--threads=1 -DwarningAsError=true`,
1.173s and measured peak RSS242.48MiB under a256MiB external watchdog.
Earlier Mathlib-import variants were stopped at the512MiB resident limit;
no success is claimed for them or for their extra kernel-vector theorem.
The final Init-only file needs no Mathlib imports or LEAN_PATH setting.
The complete d2 invoice and both new intrinsic geometric exclusions are
written proofs, not fully formalized theorems.
