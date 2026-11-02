import RankNine.T2Zero

/-!
# T2 zero step from an UNSAT fact (Mark 2026-11-02: finite facts as certified logs)

`Unsat cl n`: the clauses `cl 0, …, cl (n-1)` (bit-mask clauses as in `Zero.lean`) have no satisfying assignment.
This is a **finite fact**: it is not proved in Lean.  `dimacs` prints the clause list in DIMACS form (variable
`i` of the masks is DIMACS variable `i + 1`) for `#eval`; the printed file is checked by CaDiCaL + an LRAT checker
(drat-trim / cake_lpr), and the log records its sha256.

`t2_zero_unsat`: the clause entries of kinds 0–3 (definitions, expansions, zero entries, goal) are true for the
actual matrix (`zentry_sound`), so an UNSAT fact for them gives: every listed edge is non-zero.
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- finite fact: the clause list `cl 0, …, cl (n-1)` is unsatisfiable -/
def Unsat (cl : ℕ → ℕ × ℕ) (n : ℕ) : Prop := ∀ z : ℕ → Prop, ¬ ∀ j < n, CSat z (cl j)

/-- set bits of `x` -/
def bitsOf (x : ℕ) : List ℕ := (List.range (Nat.log2 x + 1)).filter x.testBit

/-- one DIMACS clause line -/
def dimacsLine (c : ℕ × ℕ) : String :=
  String.intercalate " " ((bitsOf c.1).map (fun i => toString (i + 1)) ++
    (bitsOf c.2).map (fun i => "-" ++ toString (i + 1)) ++ ["0"])

/-- DIMACS text of the clause list (`nv` = number of variables) -/
def dimacs (cl : ℕ → ℕ × ℕ) (n nv : ℕ) : String :=
  s!"p cnf {nv} {n}\n" ++ String.intercalate "\n" ((List.range n).map (fun j => dimacsLine (cl j))) ++ "\n"

/-- **T2 zero step from an UNSAT fact.** -/
theorem t2_zero_unsat (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (m s0 G : ℕ)
    (hs0 : s0 < 104 → ∀ x, m.testBit x = true → Mx A B x s0 = 0) (VT FT EN : BT (List ℕ))
    (hFT : ∀ fi, FT.get [] fi ≠ [] → ExpOK A B m (FT.get [] fi)) (n : ℕ)
    (hall : ∀ j < n, entryOK m s0 G VT FT EN j = true) (hunsat : Unsat (fun j => clOf G (EN.get [] j)) n)
    (ER EC GV : BT ℕ) (nE : ℕ)
    (hG : (List.range nE).all (fun e => decide (ER.get 0 e < 104) && (decide (ER.get 0 e = EC.get 0 e) ||
      (G.testBit (GV.get 0 e) && VT.get [] (GV.get 0 e) == [0, ER.get 0 e, EC.get 0 e]))) = true) :
    ∀ e < nE, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0 := by
  intro e he hz
  have hge := List.all_eq_true.mp hG e (List.mem_range.mpr he)
  simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, beq_iff_eq] at hge
  obtain ⟨hlt, hge⟩ := hge
  rcases hge with hd | ⟨hb, hv⟩
  · rw [← hd] at hz; exact hdiag _ hlt hz
  have hgoal : ∃ i, G.testBit i = true ∧ zSem A B VT i := ⟨_, hb, (zSem_z A B VT _ _ _ hv).mpr hz⟩
  have key : ∀ j, j < n → CSat (zSem A B VT) (clOf G (EN.get [] j)) := by
    intro j
    induction j using Nat.strong_induction_on with
    | _ j ih =>
      intro hj
      exact zentry_sound A B hdiag hmask m s0 G hs0 VT FT EN hFT hgoal j
        (hall j hj) (fun i hi => ih i hi (by omega))
  exact hunsat (zSem A B VT) key

end RankNine.T2
