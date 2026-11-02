import RankNine.PartialFrame

/-!
# T2.3 relations from partial frames

A non-degenerate partial frame `F` (dead inside part `D`), a dead row `t` orthogonal to the outside lines and a
column `s` with `M t s = 0`: when only two inside lines `a, b` give a non-zero product `M t f * M f s`, the expansion
of `M t s` gives the six-term relation
`M t a * M a s * M b b = - M t b * M b s * M a a`
(`μ_ta μ_as = - μ_tb μ_bs`).  The Gram matrix satisfies the same relation, so the ratios `M / G` have product `1`
around the 6-cycle `t–a, a–s, b–b / t–b, b–s, a–a`: these are the stored relations of the closure certificates
(`RankNine/T2Close.lean`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] {ι : Type*}

theorem frame_relation (A B : ι → Fin 9 → K) (u : Fin 9 → K) (F : Fin 8 → ι) (D : Finset (Fin 8))
    (hnd : LinearIndependent K (Fin.cons u (fun l => B (F l)) : Fin 9 → Fin 9 → K))
    (hdead : ∀ k ∈ D, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) (t : ι) (ht : A t ⬝ᵥ u = 0)
    (hout : ∀ k, k ∉ D → A t ⬝ᵥ B (F k) = 0) (s : ι) (hts : A t ⬝ᵥ B s = 0)
    (a b : Fin 8) (ha : a ∈ D) (hb : b ∈ D) (hab : a ≠ b)
    (hz : ∀ k ∈ D, k ≠ a → k ≠ b → (A t ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) = 0) :
    (A t ⬝ᵥ B (F a)) * (A (F a) ⬝ᵥ B s) * (A (F b) ⬝ᵥ B (F b)) =
      -((A t ⬝ᵥ B (F b)) * (A (F b) ⬝ᵥ B s) * (A (F a) ⬝ᵥ B (F a))) := by
  have h := partial_expansion A B u F D hnd hdead hdiag hoff t ht hout s
  rw [hts] at h
  have hsub : ({a, b} : Finset (Fin 8)) ⊆ D := by
    intro k hk; simp at hk; rcases hk with rfl | rfl <;> assumption
  rw [← Finset.sum_subset hsub (fun k hk hk' => by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at hk'
    rw [hz k hk hk'.1 hk'.2, zero_div]), Finset.sum_pair hab] at h
  have ha0 := hdiag a
  have hb0 := hdiag b
  have key : (A t ⬝ᵥ B (F a)) * (A (F a) ⬝ᵥ B s) * (A (F b) ⬝ᵥ B (F b)) +
      (A t ⬝ᵥ B (F b)) * (A (F b) ⬝ᵥ B s) * (A (F a) ⬝ᵥ B (F a)) =
      ((A t ⬝ᵥ B (F a)) * (A (F a) ⬝ᵥ B s) / (A (F a) ⬝ᵥ B (F a)) +
        (A t ⬝ᵥ B (F b)) * (A (F b) ⬝ᵥ B s) / (A (F b) ⬝ᵥ B (F b))) *
      ((A (F a) ⬝ᵥ B (F a)) * (A (F b) ⬝ᵥ B (F b))) := by
    field_simp <;> ring
  rw [← h, zero_mul] at key
  linear_combination key

end RankNine
