/-
  Gate-operand parity between the pinned symbolic checker operator and the
  pinned record exporter operator, machine-checked for all register counts,
  all source lists and all initial valuations.

  The two operators are the pinned ones of the PR589 checker/exporter boundary:

  * Sym (`research/e8-bit-p111-tuned/code/xcheck_p.py`): accumulate the XOR of
    the listed sources read before the gate, then write the destination once.
  * Exp (`research/e8-bit-carrier-skeleton/code/bit/export_records.py`): one
    `ADD(d, s)` per listed source, replayed sequentially over current values.

  This file depends only on Lean's core library.  It is the kernel-checked
  companion of the bounded census in the gate-operand parity contract package:
  the contract below is proved for every source list, not only on a bounded
  census domain.
-/
import Init

namespace GateParity

/-! ### Core boolean and list helpers -/

/-- Explicit boolean XOR (avoids any notation ambiguity). -/
def bxor (a b : Bool) : Bool := Bool.xor a b

theorem bxor_false (b : Bool) : bxor false b = b := by cases b <;> rfl

theorem bxor_assoc (a b c : Bool) : bxor a (bxor b c) = bxor (bxor a b) c := by
  cases a <;> cases b <;> cases c <;> rfl

theorem bxor_comm (a b : Bool) : bxor a b = bxor b a := by cases a <;> cases b <;> rfl

theorem bxor_self (a : Bool) : bxor a a = false := by cases a <;> rfl

theorem bxor_false_right (a : Bool) : bxor a false = a := by cases a <;> rfl

/-- If `bxor a b = b` then `a` is false. -/
theorem bxor_eq_right {a b : Bool} (h : bxor a b = b) : a = false := by
  calc a = bxor a false := (bxor_false_right a).symm
       _ = bxor a (bxor b b) := by rw [bxor_self]
       _ = bxor (bxor a b) b := bxor_assoc a b b
       _ = bxor b b := by rw [h]
       _ = false := bxor_self b

/-- Cancellation of the middle term. -/
theorem bxor_mid (a b c : Bool) : bxor a (bxor b (bxor a c)) = bxor b c := by
  cases a <;> cases b <;> cases c <;> rfl

/-- XOR fold of a boolean list. -/
def xfold (l : List Bool) : Bool := l.foldr bxor false

theorem xfold_nil : xfold [] = false := rfl

theorem xfold_cons (a : Bool) (l : List Bool) : xfold (a :: l) = bxor a (xfold l) := rfl

theorem xfold_append (a b : List Bool) : xfold (a ++ b) = bxor (xfold a) (xfold b) := by
  induction a with
  | nil => exact (bxor_false (xfold b)).symm
  | cons x t ih => rw [List.cons_append, xfold_cons, ih, xfold_cons, bxor_assoc]

theorem map_congr_mem {f g : Nat → Bool} {l : List Nat} (h : ∀ x ∈ l, f x = g x) :
    l.map f = l.map g := List.map_congr_left h

/-! ### Parity counts -/

/-- Parity predicates over `Nat`, kept local so the file needs no Mathlib. -/
def EvenCount (n : Nat) : Prop := n % 2 = 0

def OddCount (n : Nat) : Prop := n % 2 = 1

instance (n : Nat) : Decidable (EvenCount n) := inferInstanceAs (Decidable (n % 2 = 0))

instance (n : Nat) : Decidable (OddCount n) := inferInstanceAs (Decidable (n % 2 = 1))

theorem oddCount_of_not_evenCount {n : Nat} (h : ¬ EvenCount n) : OddCount n := by
  have hlt : n % 2 < 2 := Nat.mod_lt n (by omega)
  unfold EvenCount at h
  unfold OddCount
  omega

theorem oddCount_succ_iff (n : Nat) : OddCount (n + 1) ↔ ¬ OddCount n := by
  unfold OddCount
  constructor
  · intro h hn
    omega
  · intro h
    have hlt : n % 2 < 2 := Nat.mod_lt n (by omega)
    omega

theorem decide_oddCount_succ (n : Nat) :
    decide (OddCount (n + 1)) = !decide (OddCount n) := by
  by_cases h : OddCount n
  · have hn : ¬ OddCount (n + 1) := fun h' => (oddCount_succ_iff n).mp h' h
    rw [decide_eq_false_iff_not.mpr hn, decide_eq_true_eq.mpr h]
    rfl
  · have hn : OddCount (n + 1) := (oddCount_succ_iff n).mpr h
    rw [decide_eq_true_eq.mpr hn, decide_eq_false_iff_not.mpr h]
    rfl

theorem count_cons_eq (x y : Nat) (l : List Nat) :
    (x :: l).count y = l.count y + (if y = x then 1 else 0) := by
  by_cases h : y = x
  · subst h
    rw [List.count_cons_self]
    simp
  · rw [List.count_cons_of_ne (fun hxy => h hxy.symm)]
    simp [h]

theorem count_insert_two (x y : Nat) (a b : List Nat) :
    ((x :: a) ++ (x :: b)).count y = (a ++ b).count y + (if y = x then 2 else 0) := by
  simp only [count_cons_eq, List.count_append]
  split <;> omega

theorem evenCount_of_count_insert_two {x y : Nat} {a b : List Nat}
    (h : EvenCount (((x :: a) ++ (x :: b)).count y)) : EvenCount ((a ++ b).count y) := by
  rw [count_insert_two] at h
  unfold EvenCount at *
  split at h <;> omega

/-- A member of `t` is not the absent `d`. -/
theorem ne_of_mem_not_mem {x d : Nat} {t : List Nat} (hx : x ∈ t) (hd : d ∉ t) : x ≠ d := by
  intro h
  subst h
  exact hd hx

/-- A nonempty list splits at a first occurrence of `x`. -/
theorem exists_first_split {x : Nat} : ∀ {l : List Nat}, x ∈ l →
    ∃ a b, l = a ++ (x :: b) ∧ x ∉ a
  | [], h => by simp at h
  | y :: t, h => by
      by_cases hyx : y = x
      · subst hyx
        exact ⟨[], t, rfl, by simp⟩
      · have hxy : x ≠ y := fun hxy => hyx hxy.symm
        have hxt : x ∈ t := by
          rcases List.mem_cons.mp h with h' | h'
          · exact absurd h' hxy
          · exact h'
        obtain ⟨a, b, hab, hxa⟩ := exists_first_split hxt
        refine ⟨y :: a, b, ?_, ?_⟩
        · rw [hab, List.cons_append]
        · intro hmem
          rcases List.mem_cons.mp hmem with h' | h'
          · exact hxy h'
          · exact hxa h'

/-- A nonempty list splits after a last occurrence of `d`. -/
theorem exists_last_split {d : Nat} : ∀ {l : List Nat}, d ∈ l →
    ∃ p t, l = p ++ (d :: t) ∧ d ∉ t
  | [], h => by simp at h
  | y :: t, h => by
      by_cases hdt : d ∈ t
      · obtain ⟨p, t', hsplit, hnt⟩ := exists_last_split hdt
        exact ⟨y :: p, t', by rw [hsplit, List.cons_append], hnt⟩
      · have hy : y = d := by
          rcases List.mem_cons.mp h with h' | h'
          · exact h'.symm
          · exact absurd h' hdt
        subst hy
        exact ⟨[], t, rfl, hdt⟩

/-! ### The all-even parity lemma

If every register occurs an even number of times in a list, the XOR fold of any
valuation over that list is `false`.  The proof is the pairing argument: remove
the first occurrence of the head register and its next occurrence, which is a
shorter list with the same all-even property, and apply strong induction on the
length. -/

theorem allEvenCount_xfold (l : List Nat) (h : ∀ r, EvenCount (l.count r))
    (v : Nat → Bool) : xfold (l.map v) = false := by
  have main : ∀ n, ∀ l : List Nat, l.length = n → (∀ r, EvenCount (l.count r)) →
      ∀ v : Nat → Bool, xfold (l.map v) = false := by
    intro n
    refine Nat.strongRecOn n ?_
    intro m ih l hlen h v
    match l with
    | [] => rfl
    | x :: t =>
        have hc := h x
        rw [count_cons_eq] at hc
        have hc' : EvenCount (t.count x + 1) := by simpa using hc
        have hxodd : OddCount (t.count x) := oddCount_of_not_evenCount (by
          intro he
          unfold EvenCount at he hc'
          omega)
        have hxpos : 0 < t.count x := by
          unfold OddCount at hxodd
          omega
        have hxmem : x ∈ t := List.count_pos_iff.mp hxpos
        obtain ⟨a, b, hab, hxa⟩ := exists_first_split hxmem
        have hlen2 : (a ++ b).length < m := by
          rw [← hlen, hab]
          simp [List.length_append, List.length_cons]
          omega
        have halleven : ∀ y, EvenCount ((a ++ b).count y) := by
          intro y
          have hcy := h y
          rw [hab] at hcy
          exact evenCount_of_count_insert_two hcy
        have hid : xfold ((x :: t).map v) = xfold ((a ++ b).map v) := by
          rw [hab]
          simp only [List.map_append, List.map_cons, xfold_cons, xfold_append]
          rw [bxor_mid]
        rw [hid]
        exact ih (a ++ b).length hlen2 (a ++ b) rfl halleven v
  exact main l.length l rfl h v

/-- For the indicator valuation of a register, the XOR fold is the parity of
that register's multiplicity. -/
theorem xfold_indicator (r : Nat) (l : List Nat) :
    xfold (l.map (fun x => decide (x = r))) = decide (OddCount (l.count r)) := by
  induction l with
  | nil => rfl
  | cons s t ih =>
      rw [List.map_cons, xfold_cons, ih]
      by_cases hsr : s = r
      · rw [hsr, List.count_cons_self, decide_oddCount_succ]
        have hd : decide (r = r) = true := decide_eq_true_eq.mpr rfl
        rw [hd]
        cases decide (OddCount (t.count r)) <;> rfl
      · rw [List.count_cons_of_ne (a := r) hsr]
        have hdec : decide (s = r) = false := decide_eq_false_iff_not.mpr hsr
        rw [hdec, bxor_false]

/-! ### The two gate operators -/

/-- One sequential exporter step: `ADD(d, s)` over current values. -/
def step (d : Nat) (x : Nat → Bool) (s : Nat) : Nat → Bool :=
  fun r => if r = d then bxor (x d) (x s) else x r

/-- The pinned exporter operator: one `ADD(d, s)` per listed source, in order. -/
def exp (d : Nat) (srcs : List Nat) (v : Nat → Bool) : Nat → Bool :=
  srcs.foldl (step d) v

/-- The pinned checker operator: pre-gate XOR accumulation, then one write. -/
def sym (d : Nat) (srcs : List Nat) (v : Nat → Bool) : Nat → Bool :=
  fun r => if r = d then bxor (v d) (xfold (srcs.map v)) else v r

theorem step_self (d : Nat) (x : Nat → Bool) (s : Nat) : step d x s d = bxor (x d) (x s) := by
  simp [step]

theorem step_ne {r d : Nat} (h : r ≠ d) (x : Nat → Bool) (s : Nat) :
    step d x s r = x r := by
  simp [step, h]

theorem exp_cons (d : Nat) (s : Nat) (srcs : List Nat) (v : Nat → Bool) :
    exp d (s :: srcs) v = exp d srcs (step d v s) := rfl

theorem exp_append (d : Nat) (a b : List Nat) (v : Nat → Bool) :
    exp d (a ++ b) v = exp d b (exp d a v) := by
  simp only [exp, List.foldl_append]

theorem exp_ne {r d : Nat} (h : r ≠ d) (srcs : List Nat) (v : Nat → Bool) :
    exp d srcs v r = v r := by
  induction srcs generalizing v with
  | nil => rfl
  | cons s t ih => rw [exp_cons, ih, step_ne h]

theorem sym_d (d : Nat) (srcs : List Nat) (v : Nat → Bool) :
    sym d srcs v d = bxor (v d) (xfold (srcs.map v)) := by
  simp [sym]

theorem sym_ne {r d : Nat} (h : r ≠ d) (srcs : List Nat) (v : Nat → Bool) :
    sym d srcs v r = v r := by
  simp [sym, h]

/-- Destination-free gates: the exporter only ever adds pre-gate values, so the
sequential accumulation equals the checker's single write. -/
theorem exp_dest_free {d : Nat} (srcs : List Nat) (h : d ∉ srcs) (v : Nat → Bool) :
    exp d srcs v d = bxor (v d) (xfold (srcs.map v)) := by
  induction srcs generalizing v with
  | nil => exact (bxor_false_right (v d)).symm
  | cons s t ih =>
      have hdt : d ∉ t := fun hmem => h (List.mem_cons.mpr (Or.inr hmem))
      have hsd : s ≠ d := fun hsd => h (hsd ▸ List.mem_cons_self ..)
      have hstep : (step d v s) d = bxor (v d) (v s) := step_self d v s
      rw [exp_cons, ih hdt, hstep, List.map_cons, xfold_cons]
      have hmap : t.map (step d v s) = t.map v :=
        map_congr_mem (fun x hx => step_ne (ne_of_mem_not_mem hx hdt) v s)
      rw [hmap, bxor_assoc]

/-- In a split `p ++ [d] ++ t` with `d` absent from `t`, the exporter state at
`d` is exactly the XOR fold of the valuation over `t`. -/
theorem exp_split_d {d : Nat} (p t : List Nat) (h : d ∉ t) (v : Nat → Bool) :
    exp d (p ++ (d :: t)) v d = xfold (t.map v) := by
  rw [show p ++ (d :: t) = (p ++ [d]) ++ t from (List.append_assoc p [d] t).symm,
    exp_append]
  have hz : exp d (p ++ [d]) v d = false := by
    rw [exp_append]
    simp only [exp, List.foldl_cons, List.foldl_nil, step_self, bxor_self]
  have hmap : t.map (exp d (p ++ [d]) v) = t.map v :=
    map_congr_mem (fun x hx => exp_ne (ne_of_mem_not_mem hx h) (p ++ [d]) v)
  rw [exp_dest_free t h, hmap, hz, bxor_false]

/-! ### The exact agreement contract -/

/-- The exact agreement condition of the pinned checker/exporter operators: the
destination is absent from the source list, or the list splits at the
destination with every register in the prefix occurring an even number of times
and no destination in the suffix. -/
def Contract (d : Nat) (srcs : List Nat) : Prop :=
  d ∉ srcs ∨ ∃ p t, srcs = p ++ (d :: t) ∧ d ∉ t ∧ ∀ r, EvenCount (p.count r)

/-- **Main theorem.**  The pinned checker operator `sym` and the pinned exporter
operator `exp` agree on every initial valuation exactly for the source lists
satisfying `Contract`. -/
theorem sym_eq_exp_iff_contract (d : Nat) (srcs : List Nat) :
    Contract d srcs ↔ ∀ v : Nat → Bool, sym d srcs v = exp d srcs v := by
  constructor
  · intro hc v
    funext r
    rcases hc with hfree | ⟨p, t, hsplit, hdt, heven⟩
    · by_cases hrd : r = d
      · rw [hrd]
        rw [sym_d, exp_dest_free srcs hfree]
      · rw [sym_ne hrd, exp_ne hrd]
    · subst hsplit
      by_cases hrd : r = d
      · rw [hrd]
        rw [sym_d, exp_split_d p t hdt]
        have hp : xfold (p.map v) = false := allEvenCount_xfold p heven v
        have hmap : (p ++ (d :: t)).map v = p.map v ++ (v d :: t.map v) := by simp
        rw [hmap, xfold_append, xfold_cons, hp]
        cases (v d) <;> cases (xfold (t.map v)) <;> rfl
      · rw [sym_ne hrd, exp_ne hrd]
  · intro h
    by_cases hmem : d ∈ srcs
    · obtain ⟨p, t, hsplit, hdt⟩ := exists_last_split hmem
      by_cases hall : ∀ r, EvenCount (p.count r)
      · exact Or.inr ⟨p, t, hsplit, hdt, hall⟩
      · exfalso
        obtain ⟨r, hr⟩ := Classical.not_forall.mp hall
        have hodd : OddCount (p.count r) := oddCount_of_not_evenCount hr
        have hv := congrFun (h (fun x => decide (x = r))) d
        rw [hsplit, sym_d, exp_split_d p t hdt] at hv
        have hmap : (p ++ (d :: t)).map (fun x => decide (x = r))
            = p.map (fun x => decide (x = r)) ++ (decide (d = r) :: t.map (fun x => decide (x = r))) := by
          simp
        rw [hmap, xfold_append, xfold_cons, xfold_indicator, xfold_indicator] at hv
        rw [bxor_mid] at hv
        have hcancel : decide (OddCount (p.count r)) = false := bxor_eq_right hv
        have htrue : decide (OddCount (p.count r)) = true := decide_eq_true_eq.mpr hodd
        rw [hcancel] at htrue
        cases htrue
    · exact Or.inl hmem

/-! ### Kernel-evaluated examples -/

example : sym 0 [1, 2] (fun r => r = 1) 0 = exp 0 [1, 2] (fun r => r = 1) 0 := by
  decide

example : sym 0 [1, 1] (fun r => r = 1) 0 = exp 0 [1, 1] (fun r => r = 1) 0 := by
  decide

example : ¬ (sym 0 [0, 0] (fun _ => true) 0 = exp 0 [0, 0] (fun _ => true) 0) := by
  decide

example : ¬ (sym 0 [1, 0] (fun _ => true) 0 = exp 0 [1, 0] (fun _ => true) 0) := by
  decide

example : sym 0 [0] (fun _ => true) 0 = exp 0 [0] (fun _ => true) 0 := by
  decide

end GateParity

/-! ### Kernel axiom reports for the registered audit -/

#print axioms GateParity.sym_eq_exp_iff_contract
#print axioms GateParity.allEvenCount_xfold
#print axioms GateParity.xfold_indicator
#print axioms GateParity.exp_dest_free
#print axioms GateParity.exp_split_d
