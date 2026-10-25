/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Actual shared-piece algebra, with explicit operation premises

This deliberately small file imports only Lean Init. Associativity,
commutativity and the numerical embedding laws are ordinary theorem
parameters. Instantiation by a characteristic-zero ring, the E8 geometry
and the passage from actual coefficient expansions remain outside Lean.
-/

namespace SixSevenSupplement

theorem shared_piece_cross_product
    {R : Type} (mul : R → R → R)
    (assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c))
    (comm : ∀ a b, mul a b = mul b a)
    (alpha beta ma mb A B C D : R)
    (hA : mul alpha ma = A) (hB : mul alpha mb = B)
    (hC : mul beta ma = C) (hD : mul beta mb = D) :
    mul A D = mul B C := by
  have interchange (a b c d : R) :
      mul (mul a b) (mul c d) = mul (mul a c) (mul b d) := by
    rw [assoc a b (mul c d), ← assoc b c d, comm b c,
        assoc c b d, ← assoc a c (mul b d)]
  calc
    mul A D = mul (mul alpha ma) (mul beta mb) := by rw [hA, hD]
    _ = mul (mul alpha beta) (mul ma mb) := interchange alpha ma beta mb
    _ = mul (mul alpha beta) (mul mb ma) := by rw [comm ma mb]
    _ = mul (mul alpha mb) (mul beta ma) := (interchange alpha mb beta ma).symm
    _ = mul B C := by rw [hB, hC]

theorem no_shared_piece_at_two_root_self_sites
    {R : Type} (mul : R → R → R)
    (assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c))
    (comm : ∀ a b, mul a b = mul b a)
    (embed : Nat → R) (inject : ∀ {a b}, embed a = embed b → a = b)
    (minusOne : R)
    (squareZero : mul (embed 0) (embed 0) = embed 0)
    (squareOne : mul (embed 1) (embed 1) = embed 1)
    (squareMinusOne : mul minusOne minusOne = embed 1)
    (squareTwo : mul (embed 2) (embed 2) = embed 4)
    (alpha beta ma mb e : R)
    (he : e = embed 0 ∨ e = embed 1 ∨ e = minusOne)
    (haa : mul alpha ma = embed 2) (hab : mul alpha mb = e)
    (hba : mul beta ma = e) (hbb : mul beta mb = embed 2) : False := by
  have hdet := shared_piece_cross_product mul assoc comm alpha beta ma mb
    (embed 2) e e (embed 2) haa hab hba hbb
  rw [squareTwo] at hdet
  rcases he with he | he | he
  · rw [he, squareZero] at hdet
    have bad : (4 : Nat) = 0 := inject hdet
    cases bad
  · rw [he, squareOne] at hdet
    have bad : (4 : Nat) = 1 := inject hdet
    cases bad
  · rw [he, squareMinusOne] at hdet
    have bad : (4 : Nat) = 1 := inject hdet
    cases bad

#print axioms shared_piece_cross_product
#print axioms no_shared_piece_at_two_root_self_sites

end SixSevenSupplement
