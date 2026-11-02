import RankNine.Floor

/-!
# Symmetry transport

A permutation `π` of the 104 lines that preserves orthogonality and the label products (the group of order 384,
finite fact FO) carries a masked rank-9 decoder to a masked rank-9 decoder of the same cost:
`cost_perm` (cost), `diag_perm`, `mask_perm`, `inv_perm` (left inverses), `dec_perm` (the factorisation).
Lines are natural numbers `< 104` in the certificates; `pn π` extends `π` by the identity beyond 104.
-/

namespace RankNine.Tr

open Matrix BForm

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type*} [Field K]

/-- the cost is invariant under a permutation of the lines that preserves the label products -/
theorem cost_perm (π : Equiv.Perm (Fin 104))
    (hlab : ∀ t s, E8.labK (π t) ⬝ᵥ E8.labK (π s) = E8.labK t ⬝ᵥ E8.labK s)
    (P Q : Matrix (Fin 104) C9 K) :
    cost E8.labK (P.submatrix π id) (Q.submatrix π id) = cost E8.labK P Q := by
  unfold cost
  refine Finset.sum_congr rfl fun j _ => ?_
  have hR : ∀ (X : Matrix (Fin 104) C9 K) (a : Fin 104),
      a ∈ rowSupp X j ↔ π.symm a ∈ rowSupp (X.submatrix π id) j := by
    intro X a
    unfold rowSupp
    rw [Finset.mem_filter, Finset.mem_filter]
    simp only [Finset.mem_univ, true_and, Matrix.submatrix_apply, id, Equiv.apply_symm_apply]
  let e1 := Equiv.subtypeEquiv π.symm (hR P)
  let e2 := Equiv.subtypeEquiv π.symm (hR Q)
  have key : block E8.labK (rowSupp (P.submatrix π id) j) (rowSupp (Q.submatrix π id) j) =
      Matrix.reindex e1 e2 (block E8.labK (rowSupp P j) (rowSupp Q j)) := by
    ext ⟨a, ha⟩ ⟨b, hb⟩
    rw [Matrix.reindex_apply, Matrix.submatrix_apply]
    show E8.labK a ⬝ᵥ E8.labK b = E8.labK (π a) ⬝ᵥ E8.labK (π b)
    exact (hlab a b).symm
  rw [key, Matrix.rank_reindex]

/-- `π` on natural-number line indices (identity beyond 104) -/
def pn (π : Equiv.Perm (Fin 104)) (x : ℕ) : ℕ := if h : x < 104 then (π ⟨x, h⟩ : ℕ) else x

theorem pn_fin (π : Equiv.Perm (Fin 104)) (v : Fin 104) : pn π v = π v := by
  simp [pn, v.2]

theorem pn_lt (π : Equiv.Perm (Fin 104)) {x : ℕ} (h : x < 104) : pn π x < 104 := by
  simp [pn, h]

theorem diag_perm (π : Equiv.Perm (Fin 104)) (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) :
    ∀ x < 104, A (pn π x) ⬝ᵥ B (pn π x) ≠ 0 :=
  fun x hx => hdiag _ (pn_lt π hx)

theorem mask_perm (π : Equiv.Perm (Fin 104)) (horth : ∀ x y : Fin 104, orth (π x) (π y) = orth x y)
    (A B : ℕ → Fin 9 → K) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) :
    ∀ x < 104, ∀ y < 104, orth x y = true → A (pn π x) ⬝ᵥ B (pn π y) = 0 := by
  intro x hx y hy ho
  refine hmask _ (pn_lt π hx) _ (pn_lt π hy) ?_
  have := horth ⟨x, hx⟩ ⟨y, hy⟩
  rw [pn_fin π ⟨x, hx⟩, pn_fin π ⟨y, hy⟩, this]
  exact ho

theorem inv_perm (π : Equiv.Perm (Fin 104)) (A : ℕ → Fin 9 → K) (Al : Matrix (Fin 9) (Fin 104) K)
    (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1) :
    Al.submatrix id π * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A (pn π v) i) = 1 := by
  ext i k
  have := congrFun (congrFun hA i) k
  rw [Matrix.mul_apply] at this
  rw [Matrix.mul_apply, ← this]
  simp only [Matrix.submatrix_apply, Matrix.of_apply, id, pn_fin]
  exact Equiv.sum_comp π (fun w => Al i w * A w k)

theorem dec_perm (π : Equiv.Perm (Fin 104)) (A B : ℕ → Fin 9 → K) (P Q : Matrix (Fin 104) C9 K)
    (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ) :
    Matrix.of (fun v s : Fin 104 => Mx (fun x => A (pn π x)) (fun x => B (pn π x)) v s) =
      P.submatrix π id * (Q.submatrix π id)ᵀ := by
  ext v s
  have := congrFun (congrFun h (π v)) (π s)
  simp only [Matrix.of_apply] at this
  simp only [Matrix.of_apply, Mx, pn_fin]
  rw [show A (π v) ⬝ᵥ B (π s) = Mx A B (π v) (π s) from rfl, this]
  simp [Matrix.mul_apply]

/-- dead rows transport: if `A x ⬝ u = 0` on the image `π(m)`, the transported rows vanish on `m` -/
theorem dead_perm (π : Equiv.Perm (Fin 104)) (A : ℕ → Fin 9 → K) (u : Fin 9 → K) (m : ℕ)
    (hm : ∀ x, m.testBit x = true → x < 104) (hZ : ∀ x < 104, m.testBit x = true → A (pn π x) ⬝ᵥ u = 0) :
    ∀ x, m.testBit x = true → (fun y => A (pn π y)) x ⬝ᵥ u = 0 :=
  fun x hx => hZ x (hm x hx) hx

end RankNine.Tr
