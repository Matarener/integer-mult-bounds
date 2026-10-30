import CarrierCode.Word

/-!
# Decoding codes and the scoped carrier cost floor (Lemma 4 consequences and Corollary 5 of PROOF.md)

The finite search of the package is used only through `CodeFact`: every 8-dimensional decoding code over `K` on the
ports has minimum weight at least 49, in rows (vectors of the code) and in columns (any linear functional evaluated
on the decoding vectors).  It is established by the certificate replay in `verify.py`, not here.  The frame capacity
`Capacity` (at most 36 ports in a subspace of dimension at most 7) is checked by enumeration in `verify.py`.
-/

namespace CarrierCode

open Module

attribute [local instance] Classical.propDecidable

variable {K : Type*} [Field K] {L : Type*} [Fintype L] (port : L → V9)

/-- `W` is a decoding code with decoding vectors `w`. -/
def IsDecoding (W : Submodule K (L → K)) (w : L → L → K) : Prop :=
  ∀ ℓ, w ℓ ∈ W ∧ w ℓ ℓ = 1 ∧ ∀ m, m ≠ ℓ → Conflict (port m) (port ℓ) → w ℓ m = 0

/-- The statement certified by the search (Theorem 3 with the weight facts of `verify.py`). -/
def CodeFact (K : Type*) [Field K] : Prop :=
  ∀ (W : Submodule K (L → K)) (w : L → L → K), IsDecoding port W w → finrank K W = 8 →
    (∀ v ∈ W, v ≠ 0 → 49 ≤ (Finset.univ.filter fun m => v m ≠ 0).card) ∧
    (∀ φ : (L → K) →ₗ[K] K, (∃ ℓ, φ (w ℓ) ≠ 0) → 49 ≤ (Finset.univ.filter fun ℓ => φ (w ℓ) ≠ 0).card)

/-- Lemma 4 as used: at most 36 ports in a subspace of dimension at most 7 (checked in `verify.py`). -/
def Capacity : Prop :=
  ∀ S : Frame, finrank (ZMod 2) S ≤ 7 → (Finset.univ.filter fun m => port m ∈ S).card ≤ 36

/-- A frame holding at least 49 ports has dimension at least 8. -/
theorem root_dim (hcap : Capacity port) (F : Frame) (s : Finset L) (hs : 49 ≤ s.card)
    (hF : ∀ m ∈ s, port m ∈ F) : 8 ≤ finrank (ZMod 2) F := by
  by_contra h
  have h1 := hcap F (by omega)
  have : s ⊆ Finset.univ.filter fun m => port m ∈ F := fun m hm => by simp [hF m hm]
  have := Finset.card_le_card this
  omega

/-- The dot-product form on `F₂⁹`. -/
def dotForm : LinearMap.BilinForm (ZMod 2) V9 := Matrix.toBilin' 1

theorem dotForm_apply (x y : V9) : dotForm x y = x ⬝ᵥ y := by
  simp [dotForm, Matrix.toBilin'_apply', dotProduct]

/-- `dim B + dim B^⊥ = 9` for the dot product on `F₂⁹`. -/
theorem finrank_add_orth (B : Frame) :
    finrank (ZMod 2) B + finrank (ZMod 2) (dotForm.orthogonal B) = 9 := by
  have h := dotForm.finrank_add_finrank_orthogonal' B
  have hker : LinearMap.ker dotForm = ⊥ := by
    rw [eq_bot_iff]
    intro x hx
    rw [Submodule.mem_bot]
    funext i
    have := congrArg (fun f => f (Pi.single i 1)) (LinearMap.mem_ker.mp hx)
    simp only [dotForm_apply, LinearMap.zero_apply] at this
    simpa [dotProduct_single] using this
  rw [show (dotForm.ker : Submodule (ZMod 2) V9) = LinearMap.ker dotForm from rfl, hker, inf_bot_eq,
    finrank_bot, add_zero, Module.finrank_fin_fun] at h
  exact h

/-- A frame orthogonal to at least 49 ports has dimension at most 1. -/
theorem landing_dim (hcap : Capacity port) (B : Frame) (s : Finset L) (hs : 49 ≤ s.card)
    (hB : ∀ ℓ ∈ s, ∀ b ∈ B, b ⬝ᵥ port ℓ = 0) : finrank (ZMod 2) B ≤ 1 := by
  have hperp : ∀ ℓ ∈ s, port ℓ ∈ dotForm.orthogonal B := by
    intro ℓ hℓ
    rw [LinearMap.BilinForm.mem_orthogonal_iff]
    intro b hb
    rw [dotForm_apply]
    exact hB ℓ hℓ b hb
  have h8 := root_dim port hcap _ s hs hperp
  have := finrank_add_orth B
  omega

/-- Corollary 5, one chain.  A delivered vector `v` of a code with `CodeFact` has at least 49 live coordinates, so a
root frame holding their ports has dimension at least 8; at least 49 receivers in frames inside `q_ℓ^⊥` force the
lowest frame `B` of the chain to dimension at most 1; the chain's paid descent is at least 7. -/
theorem chain_cost (hcap : Capacity port) (W : Submodule K (L → K)) (w : L → L → K)
    (hfact : (∀ v ∈ W, v ≠ 0 → 49 ≤ (Finset.univ.filter fun m => v m ≠ 0).card) ∧
      (∀ φ : (L → K) →ₗ[K] K, (∃ ℓ, φ (w ℓ) ≠ 0) → 49 ≤ (Finset.univ.filter fun ℓ => φ (w ℓ) ≠ 0).card))
    (v : L → K) (hvW : v ∈ W) (hv : v ≠ 0) (φ : (L → K) →ₗ[K] K) (hφ : ∃ ℓ, φ (w ℓ) ≠ 0)
    (root B : Frame) (hroot : ∀ m, v m ≠ 0 → port m ∈ root)
    (hrecv : ∀ ℓ, φ (w ℓ) ≠ 0 → ∀ b ∈ B, b ⬝ᵥ port ℓ = 0) :
    7 ≤ finrank (ZMod 2) root - finrank (ZMod 2) B := by
  have h1 := root_dim port hcap root _ (hfact.1 v hvW hv) (fun m hm => hroot m (by simpa using hm))
  have h2 := landing_dim port hcap B _ (hfact.2 φ hφ) (fun ℓ hℓ => hrecv ℓ (by simpa using hℓ))
  omega

/-- With a conflict clique of size 8, the decoding vectors of an 8-dimensional decoding code span it. -/
theorem span_of_clique (W : Submodule K (L → K)) (w : L → L → K) (hW : IsDecoding port W w)
    (h8 : finrank K W = 8) (T : Fin 8 → L) (hT : Function.Injective T)
    (hcl : ∀ i j, i ≠ j → Conflict (port (T i)) (port (T j))) :
    Submodule.span K (Set.range w) = W := by
  have hle : Submodule.span K (Set.range w) ≤ W :=
    Submodule.span_le.mpr (by rintro _ ⟨ℓ, rfl⟩; exact (hW ℓ).1)
  have hli : LinearIndependent K (fun i => w (T i)) := by
    rw [Fintype.linearIndependent_iff]
    intro g hg j
    have := congrFun hg (T j)
    simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at this
    rw [Finset.sum_eq_single j] at this
    · simpa [(hW (T j)).2.1] using this
    · intro i _ hij
      rw [(hW (T i)).2.2 (T j) (fun h => hij (hT h).symm) (hcl j i (Ne.symm hij)), mul_zero]
    · simp
  have h8' : 8 ≤ finrank K (Submodule.span K (Set.range w)) := by
    have h1 := finrank_span_eq_card hli
    have h2 : Submodule.span K (Set.range fun i => w (T i)) ≤ Submodule.span K (Set.range w) :=
      Submodule.span_mono (by rintro _ ⟨i, rfl⟩; exact ⟨T i, rfl⟩)
    have := Submodule.finrank_mono h2
    simp only [Fintype.card_fin] at h1
    omega
  exact Submodule.eq_of_le_of_finrank_eq hle (le_antisymm (Submodule.finrank_mono hle) (by omega))

/-- Corollary 5.  Let `W` be an 8-dimensional decoding code with decoding vectors `w`, under `CodeFact` and
`Capacity`, and let `v : Fin 8 → (L → K)` be a basis of `W`.  Suppose chain `c` carries `v c` down from a root frame
holding the ports of its support to a lowest frame `B c` that lies in `q_ℓ^⊥` for every partner `ℓ` whose decoding
vector uses `v c` (nonzero coordinate).  Then every chain pays at least 7, and the eight chains at least 56. -/
theorem carriers_cost (hcode : CodeFact port K) (hcap : Capacity port) (W : Submodule K (L → K)) (w : L → L → K)
    (hW : IsDecoding port W w) (h8 : finrank K W = 8) (hspan : Submodule.span K (Set.range w) = W)
    (v : Basis (Fin 8) K W)
    (root B : Fin 8 → Frame) (hroot : ∀ c m, (v c : L → K) m ≠ 0 → port m ∈ root c)
    (hrecv : ∀ c ℓ, v.repr ⟨w ℓ, (hW ℓ).1⟩ c ≠ 0 → ∀ b ∈ B c, b ⬝ᵥ port ℓ = 0) :
    (∀ c, 7 ≤ finrank (ZMod 2) (root c) - finrank (ZMod 2) (B c)) ∧
      56 ≤ ∑ c, (finrank (ZMod 2) (root c) - finrank (ZMod 2) (B c)) := by
  have hfact := hcode W w hW h8
  have each : ∀ c, 7 ≤ finrank (ZMod 2) (root c) - finrank (ZMod 2) (B c) := by
    intro c
    -- the coordinate functional of `v c`, extended from `W` to the ambient space
    obtain ⟨φ, hφ⟩ := LinearMap.exists_extend (v.coord c)
    have hφw : ∀ ℓ, φ (w ℓ) = v.repr ⟨w ℓ, (hW ℓ).1⟩ c := by
      intro ℓ
      have := congrArg (fun f => f ⟨w ℓ, (hW ℓ).1⟩) hφ
      simpa using this
    have hvc : (v c : L → K) ≠ 0 := by
      intro h0
      exact v.ne_zero c (Subtype.ext (by simpa using h0))
    have hex : ∃ ℓ, φ (w ℓ) ≠ 0 := by
      by_contra hno
      push Not at hno
      have hzero : ∀ x ∈ W, φ x = 0 := by
        intro x hx
        rw [← hspan] at hx
        induction hx using Submodule.span_induction with
        | mem y hy => obtain ⟨ℓ, rfl⟩ := hy; exact hno ℓ
        | zero => simp
        | add a b _ _ ha hb => simp [ha, hb]
        | smul a b _ hb => simp [hb]
      have h1 : φ (v c) = 1 := by
        have := congrArg (fun f => f (v c)) hφ
        simpa using this
      rw [hzero _ (v c).2] at h1
      exact zero_ne_one h1
    exact chain_cost port hcap W w hfact (v c) (v c).2 hvc φ hex (root c) (B c) (hroot c)
      (fun ℓ hℓ => hrecv c ℓ (by rwa [← hφw]))
  refine ⟨each, ?_⟩
  calc 56 = ∑ _c : Fin 8, 7 := by simp
    _ ≤ _ := Finset.sum_le_sum fun c _ => each c

end CarrierCode
