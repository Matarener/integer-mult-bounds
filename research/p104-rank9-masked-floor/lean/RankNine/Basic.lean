import Mathlib

/-!
# Field lemmas behind the hand route of step T1 (rank-9 masked floor on P104)

* `square_lemma`: two expansion relations on a "square" force `a² = d²`.
* `propagate`: a relation `x p = y q` with `x² = y²` gives `p² = q²`.
* `quad_cases`: four entries with equal squares and sum 1 are all `1/4`, or three are `1/2` and one is `-1/2`.
* `cocycle_peel`: the peeling step for a multiplicative cocycle (one unknown edge in a relation).
All over an arbitrary field (`quad_cases` needs characteristic 0), so they hold over ℝ and ℂ alike.
-/

namespace RankNine

variable {K : Type*} [Field K]

theorem square_lemma {a b c d : K} (hb : b ≠ 0) (hc : c ≠ 0)
    (h1 : a * b = c * d) (h2 : a * c = b * d) : a ^ 2 = d ^ 2 := by
  have h : a ^ 2 * (b * c) = d ^ 2 * (b * c) := by
    calc a ^ 2 * (b * c) = (a * b) * (a * c) := by ring
      _ = (c * d) * (b * d) := by rw [h1, h2]
      _ = d ^ 2 * (b * c) := by ring
  exact mul_right_cancel₀ (mul_ne_zero hb hc) h

theorem propagate {x y p q : K} (hx : x ≠ 0) (hxy : x ^ 2 = y ^ 2)
    (h : x * p = y * q) : p ^ 2 = q ^ 2 := by
  have h2 : x ^ 2 * p ^ 2 = x ^ 2 * q ^ 2 := by
    calc x ^ 2 * p ^ 2 = (x * p) ^ 2 := by ring
      _ = (y * q) ^ 2 := by rw [h]
      _ = y ^ 2 * q ^ 2 := by ring
      _ = x ^ 2 * q ^ 2 := by rw [hxy]
  exact mul_left_cancel₀ (pow_ne_zero 2 hx) h2


/-- Four entries with equal squares and sum `1`: either all are `1/4`, or the common square is `1/4`. -/
theorem quad_cases [CharZero K] {a b c d : K} (hb : b ^ 2 = a ^ 2) (hc : c ^ 2 = a ^ 2)
    (hd : d ^ 2 = a ^ 2) (hs : a + b + c + d = 1) :
    (a = 1 / 4 ∧ b = 1 / 4 ∧ c = 1 / 4 ∧ d = 1 / 4) ∨ a ^ 2 = 1 / 4 := by
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp hb with rb | rb <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp hc with rc | rc <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp hd with rd | rd <;>
  simp only [rb, rc, rd] at hs ⊢
  · left; refine ⟨?_, ?_, ?_, ?_⟩ <;> linear_combination hs / 4
  all_goals first
    | (right; have ha : a = 1 / 2 := by linear_combination hs / 2
       rw [ha]; norm_num)
    | (right; have ha : a = -1 / 2 := by linear_combination hs / 2
       rw [ha]; norm_num)
    | (exfalso; have : (0 : K) = 1 := by linear_combination hs
       exact zero_ne_one this)

/-- Peeling: in a relation `∏ r = 1` where every factor but one is `1`, that factor is `1`. -/
theorem cocycle_peel {G : Type*} [CommGroup G] (r : G) (others : List G)
    (hrel : r * others.prod = 1) (hoth : ∀ g ∈ others, g = 1) : r = 1 := by
  have : others.prod = 1 := List.prod_eq_one hoth
  simpa [this] using hrel

end RankNine
