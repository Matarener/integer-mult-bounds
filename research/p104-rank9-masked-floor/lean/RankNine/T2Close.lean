import Mathlib

/-!
# T2.3: exact closure certificates for a ratio cocycle (any field)

Edge values `v : ℕ → K`, all non-zero.  A relation is a list of signed edges `q` (edge `q / 2`, inverted when `q` is
odd) whose product is `1`.  The gauge edges (a spanning tree and one diagonal) have value `1`.  A certificate is a
list of steps; step `i` (from `1`) assigns edges or classes:
* **peel** `[0, r₁, r₂, e]`: in the relation `RS r₁ ++ RS r₂` only `e` is unassigned (once); then `v e` is the
  product of the assigned part;
* **class** `[1, k, root, o₁, o₂, m₁, p₁, a₁, b₁, s₁, …]`: members `m` linked to an earlier member `p` by the
  relation `RS a ++ RS b` (only `m`, `p` unassigned, assigned part trivial), sign `s` (`v m = v root ^ (±1)`);
  the odd relation `RS o₁ ++ RS o₂` gives `v root ^ 2 = 1`; the class value is `c k = v root`;
* **fix** `[2, k, r₁, r₂]`: a fully assigned relation whose class mask, up to classes fixed earlier, is `{k}`:
  `c k = 1`.
Invariant: every assigned edge has `v e = Π_{k ∈ MK e} c k` (`cval`), every created class has `c k ^ 2 = 1`, every
fixed class has `c k = 1`.  At the end every needed edge has a mask made of fixed classes, so `v e = 1`.
-/

namespace RankNine.T2

variable {K : Type*} [Field K]

/-- value of a signed edge -/
def sv (v : ℕ → K) (q : ℕ) : K := if q % 2 = 0 then v (q / 2) else (v (q / 2))⁻¹

/-- product of a relation -/
def rp (v : ℕ → K) (r : List ℕ) : K := (r.map (sv v)).prod

/-- class value of a mask -/
def cval (c : ℕ → K) (n m : ℕ) : K := ((List.range n).map fun k => if m.testBit k then c k else 1).prod

theorem prod_split (f : ℕ → K) (p : ℕ → Bool) (l : List ℕ) :
    (l.map f).prod = ((l.filter p).map f).prod * ((l.filter fun q => !p q).map f).prod := by
  induction l with
  | nil => simp
  | cons a l ih =>
    by_cases h : p a = true
    · simp [List.filter_cons, h, ih, mul_assoc]
    · simp [List.filter_cons, h, ih]; ring

theorem cval_xor (c : ℕ → K) (n m₁ m₂ : ℕ)
    (hc : ∀ k < n, (m₁.testBit k = true ∨ m₂.testBit k = true) → c k * c k = 1) :
    cval c n (m₁ ^^^ m₂) = cval c n m₁ * cval c n m₂ := by
  unfold cval
  rw [← List.prod_map_mul]
  congr 1
  apply List.map_congr_left
  intro k hk
  have hn := hc k (List.mem_range.mp hk)
  rw [Nat.testBit_xor]
  cases h1 : m₁.testBit k <;> cases h2 : m₂.testBit k <;> simp [h1, h2] at hn ⊢
  exact hn.symm

theorem cval_zero (c : ℕ → K) (n : ℕ) : cval c n 0 = 1 := by
  simp [cval]

theorem cval_sq (c : ℕ → K) (n m : ℕ) (hc : ∀ k < n, m.testBit k = true → c k * c k = 1) :
    cval c n m * cval c n m = 1 := by
  rw [← cval_xor c n m m (fun k hk h => hc k hk (by tauto)), Nat.xor_self, cval_zero]

theorem cval_fix (c : ℕ → K) (n m₁ m₂ : ℕ) (hc : ∀ k < n, (m₁ ^^^ m₂).testBit k = true → c k = 1) :
    cval c n m₁ = cval c n m₂ := by
  unfold cval
  congr 1
  apply List.map_congr_left
  intro k hk
  have hk' := List.mem_range.mp hk
  have := hc k hk'
  rw [Nat.testBit_xor] at this
  cases h1 : m₁.testBit k <;> cases h2 : m₂.testBit k <;> simp_all

theorem cval_single (c : ℕ → K) (n k : ℕ) (hk : k < n) : cval c n (2 ^ k) = c k := by
  unfold cval
  induction n with
  | zero => omega
  | succ n ih =>
    rw [List.range_succ, List.map_append, List.prod_append]
    by_cases e : k = n
    · subst e
      have : ∀ j ∈ List.range k, (2 ^ k).testBit j = false := by
        intro j hj; rw [Nat.testBit_two_pow]; have := List.mem_range.mp hj; simp; omega
      rw [List.map_congr_left (fun j hj => by rw [this j hj])]
      simp [Nat.testBit_two_pow]
    · rw [ih (by omega)]
      simp [Nat.testBit_two_pow, e]

/-! ## Certificate data and checks -/

/-- the data: relations `RS`, order `OD` (step index of each edge, gauge edges 0), masks `MK`, class roots `RT`,
class creation steps `CO`, fix steps `FO`, number of classes `n`. -/
structure Cert where
  RS : List (List ℕ)
  OD : List ℕ
  MK : List ℕ
  RT : List ℕ
  CO : List ℕ
  FO : List ℕ
  n : ℕ

def od (C : Cert) (e : ℕ) : ℕ := C.OD.getD e 1000000000
def mk (C : Cert) (e : ℕ) : ℕ := C.MK.getD e 0
def rel (C : Cert) (a b : ℕ) : List ℕ := C.RS.getD a [] ++ C.RS.getD b []


/-- `x` uses only classes fixed before step `i` -/
def trivB (C : Cert) (i x : ℕ) : Bool :=
  (List.range C.n).all fun k => !x.testBit k || decide (C.FO.getD k 1000000000 < i)

/-- xor of the masks of a list of signed edges, from `a` -/
def xm (C : Cert) (a : ℕ) (l : List ℕ) : ℕ := l.foldl (fun a q => a ^^^ mk C (q / 2)) a

def asg (C : Cert) (i q : ℕ) : Bool := decide (od C (q / 2) < i)

def unas (C : Cert) (i : ℕ) (r : List ℕ) : List ℕ := r.filter fun q => !asg C i q

/-- peel `[0, r₁, r₂, e]` -/
def peelOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  match unas C i (rel C (s.getD 1 0) (s.getD 2 0)) with
  | [q] => decide (q / 2 = s.getD 3 0) && decide (od C (s.getD 3 0) = i) &&
      trivB C i (xm C 0 ((rel C (s.getD 1 0) (s.getD 2 0)).filter (asg C i)) ^^^ mk C (s.getD 3 0))
  | _ => false

/-- fix `[2, k, r₁, r₂]` -/
def fixOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  decide (C.FO.getD (s.getD 1 0) 1000000000 = i) && decide (s.getD 1 0 < C.n) &&
    (unas C i (rel C (s.getD 2 0) (s.getD 3 0))).isEmpty &&
    trivB C i (xm C 0 (rel C (s.getD 2 0) (s.getD 3 0)) ^^^ 2 ^ (s.getD 1 0))

/-! ## Soundness -/

variable (C : Cert) (v : ℕ → K)

def cls (k : ℕ) : K := v (C.RT.getD k 0)

/-- the invariant before step `i` -/
def Inv (i : ℕ) : Prop :=
  (∀ e, od C e < i → v e = cval (cls C v) C.n (mk C e)) ∧
  (∀ k < C.n, C.CO.getD k 1000000000 < i → cls C v k * cls C v k = 1) ∧
  (∀ k < C.n, C.FO.getD k 1000000000 < i → cls C v k = 1)

/-- masks only use classes created no later than the edge -/
def WF : Prop := ∀ e k, (mk C e).testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 ≤ od C e

theorem rp_rel (hrel : ∀ r ∈ C.RS, rp v r = 1) (a b : ℕ) : rp v (rel C a b) = 1 := by
  have h : ∀ x, rp v (C.RS.getD x []) = 1 := by
    intro x
    rw [List.getD_eq_getElem?_getD]
    cases hx : C.RS[x]? with
    | none => simp [rp]
    | some r => exact hrel r (List.mem_of_getElem? hx)
  unfold rel rp; rw [List.map_append, List.prod_append]
  exact by rw [show (List.map (sv v) (C.RS.getD a [])).prod = 1 from h a,
    show (List.map (sv v) (C.RS.getD b [])).prod = 1 from h b, one_mul]

theorem triv_cval {i x : ℕ} (hI : Inv C v i) (h : trivB C i x = true) : cval (cls C v) C.n x = 1 := by
  rw [← cval_zero (cls C v) C.n]
  apply cval_fix
  intro k hk hb
  rw [Nat.xor_zero] at hb
  have := List.all_eq_true.mp h k (List.mem_range.mpr hk)
  rw [hb] at this
  simp at this
  exact hI.2.2 k hk this

theorem cval_sq_of {i x : ℕ} (hI : Inv C v i) (hx : ∀ k, x.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i) :
    cval (cls C v) C.n x * cval (cls C v) C.n x = 1 :=
  cval_sq _ _ _ fun k _ hb => hI.2.1 k (hx k hb).1 (hx k hb).2

theorem inv_eq_self {a : K} (h : a * a = 1) : a⁻¹ = a := inv_eq_of_mul_eq_one_right h

theorem sv_asg {i q : ℕ} (hI : Inv C v i) (hW : WF C) (hq : od C (q / 2) < i) :
    sv v q = cval (cls C v) C.n (mk C (q / 2)) := by
  have hv := hI.1 _ hq
  have hs := cval_sq_of C v hI (x := mk C (q / 2)) fun k hb => ⟨(hW _ k hb).1, lt_of_le_of_lt (hW _ k hb).2 hq⟩
  unfold sv; split_ifs
  · exact hv
  · rw [hv, inv_eq_self hs]

theorem prod_asg {i : ℕ} (hI : Inv C v i) (hW : WF C) : ∀ (l : List ℕ) (a : ℕ),
    (∀ q ∈ l, asg C i q = true) → (∀ k, a.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i) →
    cval (cls C v) C.n a * (l.map (sv v)).prod = cval (cls C v) C.n (xm C a l) := by
  intro l
  induction l with
  | nil => intro a _ _; simp [xm]
  | cons q l ih =>
    intro a hl ha
    have hq : od C (q / 2) < i := by simpa [asg] using hl q (by simp)
    have hb : ∀ k, (a ^^^ mk C (q / 2)).testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i := by
      intro k h
      rw [Nat.testBit_xor] at h
      cases h1 : a.testBit k
      · rw [h1] at h; simp at h
        exact ⟨(hW _ k h).1, lt_of_le_of_lt (hW _ k h).2 hq⟩
      · exact ha k h1
    have := ih (a ^^^ mk C (q / 2)) (fun q' h' => hl q' (by simp [h'])) hb
    rw [List.map_cons, List.prod_cons, ← mul_assoc, sv_asg C v hI hW hq, ← cval_xor]
    · simpa [xm] using this
    · intro k hk h
      rcases h with h | h
      · exact hI.2.1 k hk (ha k h).2
      · exact hI.2.1 k hk (lt_of_le_of_lt (hW _ k h).2 hq)


/-- every set bit of `x` is a class `< n` created before step `i` -/
def bitsB (C : Cert) (i x : ℕ) : Bool :=
  (List.range C.n).all (fun k => !x.testBit k || decide (C.CO.getD k 1000000000 < i)) && decide (x < 2 ^ C.n)

theorem bits_of {i x : ℕ} (h : bitsB C i x = true) :
    ∀ k, x.testBit k = true → k < C.n ∧ C.CO.getD k 1000000000 < i := by
  unfold bitsB at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range] at h
  intro k hk
  have hkn : k < C.n := by
    by_contra hc
    have : x < 2 ^ k := lt_of_lt_of_le h.2 (Nat.pow_le_pow_right (by norm_num) (by omega))
    rw [Nat.testBit_lt_two_pow this] at hk
    exact absurd hk (by simp)
  have := h.1 k hkn
  rw [hk] at this
  simp at this
  exact ⟨hkn, this⟩

/-- peel `[0, r₁, r₂, e]`, with the bit check of the new mask -/
def peelB (C : Cert) (i : ℕ) (s : List ℕ) : Bool := peelOK C i s && bitsB C i (mk C (s.getD 3 0))

theorem filter_not_asg_nil {i : ℕ} {r : List ℕ} (h : r.filter (fun q => !asg C i q) = []) :
    ∀ q ∈ r, asg C i q = true := by
  intro q hq
  by_contra hc
  have : q ∈ r.filter (fun q => !asg C i q) := List.mem_filter.mpr ⟨hq, by simpa using hc⟩
  rw [h] at this
  simp at this

theorem peel_sound {i : ℕ} (hrel : ∀ r ∈ C.RS, rp v r = 1) (hW : WF C) (hI : Inv C v i) {s : List ℕ}
    (hok : peelB C i s = true) : v (s.getD 3 0) = cval (cls C v) C.n (mk C (s.getD 3 0)) := by
  unfold peelB at hok
  rw [Bool.and_eq_true] at hok
  obtain ⟨hp, hbits⟩ := hok
  unfold peelOK at hp
  split at hp
  next q hq =>
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hp
    obtain ⟨⟨he, _⟩, htr⟩ := hp
    have h1 := rp_rel C v hrel (s.getD 1 0) (s.getD 2 0)
    unfold rp at h1
    rw [prod_split (sv v) (asg C i)] at h1
    have hq' : (rel C (s.getD 1 0) (s.getD 2 0)).filter (fun q => !asg C i q) = [q] := hq
    rw [hq'] at h1
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one] at h1
    have hpa := prod_asg C v hI hW ((rel C (s.getD 1 0) (s.getD 2 0)).filter (asg C i)) 0
      (fun q hq => (List.mem_filter.mp hq).2) (by simp)
    rw [cval_zero, one_mul] at hpa
    rw [hpa] at h1
    set X := xm C 0 ((rel C (s.getD 1 0) (s.getD 2 0)).filter (asg C i))
    set e := s.getD 3 0
    have hX : cval (cls C v) C.n X = cval (cls C v) C.n (mk C e) := by
      apply cval_fix
      intro k hk hb
      have := List.all_eq_true.mp htr k (List.mem_range.mpr hk)
      rw [hb] at this
      simp at this
      exact hI.2.2 k hk this
    rw [hX] at h1
    have hsq := cval_sq_of C v hI (bits_of C hbits)
    have hsv : sv v q = cval (cls C v) C.n (mk C e) := by
      have := eq_inv_of_mul_eq_one_right h1
      rw [this, inv_eq_self hsq]
    unfold sv at hsv
    rw [he] at hsv
    split_ifs at hsv
    · exact hsv
    · rw [← inv_inv (v e), hsv, inv_eq_self hsq]
  next => simp at hp

theorem fix_sound {i : ℕ} (hrel : ∀ r ∈ C.RS, rp v r = 1) (hW : WF C) (hI : Inv C v i) {s : List ℕ}
    (hok : fixOK C i s = true) : cls C v (s.getD 1 0) = 1 := by
  unfold fixOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.isEmpty_iff] at hok
  obtain ⟨⟨⟨_, hk⟩, hnil⟩, htr⟩ := hok
  have hall := filter_not_asg_nil C hnil
  have h1 := rp_rel C v hrel (s.getD 2 0) (s.getD 3 0)
  have hpa := prod_asg C v hI hW (rel C (s.getD 2 0) (s.getD 3 0)) 0 hall (by simp)
  rw [cval_zero, one_mul] at hpa
  unfold rp at h1
  rw [h1] at hpa
  have hfx : cval (cls C v) C.n (2 ^ (s.getD 1 0)) = cval (cls C v) C.n (xm C 0 (rel C (s.getD 2 0) (s.getD 3 0))) := by
    apply cval_fix
    intro k hk' hb
    have := List.all_eq_true.mp htr k (List.mem_range.mpr hk')
    rw [Nat.xor_comm, hb] at this
    simp at this
    exact hI.2.2 k hk' this
  rw [← cval_single (cls C v) C.n _ hk, hfx]
  exact hpa.symm

end RankNine.T2
