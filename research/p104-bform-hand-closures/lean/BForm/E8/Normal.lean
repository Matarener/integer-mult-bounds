import Mathlib

/-!
# A normal through three points

Linear algebra behind the frame argument: if `A ≠ 0` and `v w ⬝ᵥ A ≠ 0`, the points orthogonal to `A` lie in the
span of three independent points of the family whose span misses `v w`; a non-zero vector orthogonal to those
three points is then orthogonal to every point orthogonal to `A` and not to `v w`.
-/

namespace BForm.E8

open Matrix Module

variable {K : Type*} [Field K]

/-- The dot product with `N` as a linear functional. -/
def dotL (N : Fin 4 → K) : (Fin 4 → K) →ₗ[K] K where
  toFun x := N ⬝ᵥ x
  map_add' x y := dotProduct_add N x y
  map_smul' c x := by simp [dotProduct_smul]

theorem exists_three {ι : Type*} (v : ι → Fin 4 → K) (hspan : Submodule.span K (Set.range v) = ⊤)
    (hfin : (Set.range v).Finite) (A : Fin 4 → K) (w : ι) (hw : v w ⬝ᵥ A ≠ 0) :
    ∃ i j k : ι, (∀ c, v c ⬝ᵥ A = 0 → v c ∈ Submodule.span K {v i, v j, v k}) ∧
      Submodule.span K {v w, v i, v j, v k} = ⊤ := by
  classical
  set S : Set (Fin 4 → K) := v '' {c | v c ⬝ᵥ A = 0}
  have hSker : Submodule.span K S ≤ LinearMap.ker (dotL A) := by
    rw [Submodule.span_le]; rintro _ ⟨c, hc, rfl⟩
    have hc' : v c ⬝ᵥ A = 0 := hc
    show A ⬝ᵥ v c = 0
    rw [dotProduct_comm]; exact hc'
  have hwS : v w ∉ Submodule.span K S := fun h => hw (by
    have := hSker h; simpa [dotL, dotProduct_comm] using this)
  obtain ⟨b, hbS, hbspan, hbli⟩ := exists_linearIndependent K S
  have hwb : v w ∉ Submodule.span K b := by rwa [hbspan]
  have hli2 : LinearIndepOn K id (insert (v w) b) := LinearIndepOn.id_insert hbli hwb
  have hsub : insert (v w) b ⊆ Set.range v := by
    rintro _ (rfl | hx)
    · exact ⟨w, rfl⟩
    · obtain ⟨c, _, rfl⟩ := hbS hx; exact ⟨c, rfl⟩
  obtain ⟨B, hBr, hiB, hrB, hBli⟩ := exists_linearIndepOn_id_extension hli2 hsub
  have hBtop : Submodule.span K B = ⊤ := by
    rw [eq_top_iff, ← hspan]; exact Submodule.span_le.mpr hrB
  have hBfin : B.Finite := hfin.subset hBr
  haveI : Fintype B := hBfin.fintype
  have hBcard : hBfin.toFinset.card = 4 := by
    have h1 := finrank_span_set_eq_card hBli
    rw [hBtop, finrank_top, Module.finrank_fin_fun] at h1
    rw [Set.toFinset_card] at h1
    rw [Set.Finite.card_toFinset]; convert h1.symm
  have hwB : v w ∈ B := hiB (Set.mem_insert _ _)
  set C := hBfin.toFinset.erase (v w)
  have hC : C.card = 3 := by
    rw [Finset.card_erase_of_mem (by simpa using hwB), hBcard]
  obtain ⟨x, y, z, -, -, -, hCe⟩ := Finset.card_eq_three.mp hC
  have hmemC : ∀ u, u ∈ C ↔ u ∈ B ∧ u ≠ v w := fun u => by simp [C]; tauto
  have hrange : ∀ u ∈ C, ∃ c, v c = u := fun u hu => hBr ((hmemC u).mp hu).1
  obtain ⟨i, hi⟩ := hrange x (by rw [hCe]; simp)
  obtain ⟨j, hj⟩ := hrange y (by rw [hCe]; simp)
  obtain ⟨k, hk⟩ := hrange z (by rw [hCe]; simp)
  have hCxyz : ∀ u, u ∈ B ∧ u ≠ v w ↔ u = x ∨ u = y ∨ u = z := fun u => by
    rw [← hmemC, hCe]; simp
  refine ⟨i, j, k, ?_, ?_⟩
  · intro c hc
    have h1 : v c ∈ Submodule.span K S := Submodule.subset_span ⟨c, hc, rfl⟩
    rw [← hbspan] at h1
    refine Submodule.span_mono ?_ h1
    intro u hu
    have huB : u ∈ B := hiB (Set.mem_insert_of_mem _ hu)
    have hne : u ≠ v w := fun h => hwb (h ▸ Submodule.subset_span hu)
    rcases (hCxyz u).mp ⟨huB, hne⟩ with h | h | h <;> simp [h, hi, hj, hk]
  · rw [eq_top_iff, ← hBtop]
    refine Submodule.span_mono ?_
    intro u hu
    by_cases h : u = v w
    · simp [h]
    · rcases (hCxyz u).mp ⟨hu, h⟩ with h | h | h <;> simp [h, hi, hj, hk]

/-- A non-zero vector orthogonal to three points, the three spanning with `v w` the whole space. -/
theorem normal_ok (N : Fin 4 → K) (hN : N ≠ 0) (a b c d : Fin 4 → K) (ha : N ⬝ᵥ a = 0) (hb : N ⬝ᵥ b = 0)
    (hc : N ⬝ᵥ c = 0) (htop : Submodule.span K {d, a, b, c} = ⊤) :
    (∀ u ∈ Submodule.span K {a, b, c}, N ⬝ᵥ u = 0) ∧ N ⬝ᵥ d ≠ 0 := by
  have hle : ∀ s : Set (Fin 4 → K), (∀ u ∈ s, N ⬝ᵥ u = 0) → Submodule.span K s ≤ LinearMap.ker (dotL N) :=
    fun s hs => Submodule.span_le.mpr fun u hu => by simpa [dotL] using hs u hu
  refine ⟨fun u hu => by simpa [dotL] using hle {a, b, c} (by simp [ha, hb, hc]) hu, fun hd => hN ?_⟩
  have h := hle {d, a, b, c} (by simp [hd, ha, hb, hc])
  rw [htop] at h
  funext m
  have := h (Submodule.mem_top (x := Pi.single m 1))
  simpa [dotL, dotProduct_single] using this

end BForm.E8
