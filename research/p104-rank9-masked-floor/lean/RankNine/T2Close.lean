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
  PD : List ℕ
  PR : List ℕ
  SG : List ℕ
  n : ℕ

def od (C : Cert) (e : ℕ) : ℕ := C.OD.getD e 1000000000
def mk (C : Cert) (e : ℕ) : ℕ := C.MK.getD e 0
/-- the product relation of a list of relation indices -/
def relL (C : Cert) (l : List ℕ) : List ℕ := l.flatMap fun a => C.RS.getD a []


/-- `x` uses only classes fixed before step `i` -/
def trivB (C : Cert) (i x : ℕ) : Bool :=
  (List.range C.n).all fun k => !x.testBit k || decide (C.FO.getD k 1000000000 < i)

/-- xor of the masks of a list of signed edges, from `a` -/
def xm (C : Cert) (a : ℕ) (l : List ℕ) : ℕ := l.foldl (fun a q => a ^^^ mk C (q / 2)) a

def asg (C : Cert) (i q : ℕ) : Bool := decide (od C (q / 2) < i)

def unas (C : Cert) (i : ℕ) (r : List ℕ) : List ℕ := r.filter fun q => !asg C i q

/-- peel `[0, e, r₁, r₂, …]` -/
def peelOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  match unas C i (relL C (s.drop 2)) with
  | [q] => decide (q / 2 = s.getD 1 0) && decide (od C (s.getD 1 0) = i) &&
      trivB C i (xm C 0 ((relL C (s.drop 2)).filter (asg C i)) ^^^ mk C (s.getD 1 0))
  | _ => false

/-- fix `[2, k, r₁, r₂, …]` -/
def fixOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  decide (C.FO.getD (s.getD 1 0) 1000000000 = i) && decide (s.getD 1 0 < C.n) &&
    (unas C i (relL C (s.drop 2))).isEmpty &&
    trivB C i (xm C 0 (relL C (s.drop 2)) ^^^ 2 ^ (s.getD 1 0))

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

theorem rp_relL (hrel : ∀ r ∈ C.RS, rp v r = 1) (l : List ℕ) : rp v (relL C l) = 1 := by
  induction l with
  | nil => simp [relL, rp]
  | cons a l ih =>
    have h : rp v (C.RS.getD a []) = 1 := by
      rw [List.getD_eq_getElem?_getD]
      cases hx : C.RS[a]? with
      | none => simp [rp]
      | some r => exact hrel r (List.mem_of_getElem? hx)
    unfold relL at ih ⊢
    rw [List.flatMap_cons]
    unfold rp at h ih ⊢
    rw [List.map_append, List.prod_append, h, ih, one_mul]

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
def peelB (C : Cert) (i : ℕ) (s : List ℕ) : Bool := peelOK C i s && bitsB C i (mk C (s.getD 1 0))

theorem filter_not_asg_nil {i : ℕ} {r : List ℕ} (h : r.filter (fun q => !asg C i q) = []) :
    ∀ q ∈ r, asg C i q = true := by
  intro q hq
  by_contra hc
  have : q ∈ r.filter (fun q => !asg C i q) := List.mem_filter.mpr ⟨hq, by simpa using hc⟩
  rw [h] at this
  simp at this

theorem peel_sound {i : ℕ} (hrel : ∀ r ∈ C.RS, rp v r = 1) (hW : WF C) (hI : Inv C v i) {s : List ℕ}
    (hok : peelB C i s = true) : v (s.getD 1 0) = cval (cls C v) C.n (mk C (s.getD 1 0)) := by
  unfold peelB at hok
  rw [Bool.and_eq_true] at hok
  obtain ⟨hp, hbits⟩ := hok
  unfold peelOK at hp
  split at hp
  next q hq =>
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hp
    obtain ⟨⟨he, _⟩, htr⟩ := hp
    have h1 := rp_relL C v hrel (s.drop 2)
    unfold rp at h1
    rw [prod_split (sv v) (asg C i)] at h1
    have hq' : (relL C (s.drop 2)).filter (fun q => !asg C i q) = [q] := hq
    rw [hq'] at h1
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one] at h1
    have hpa := prod_asg C v hI hW ((relL C (s.drop 2)).filter (asg C i)) 0
      (fun q hq => (List.mem_filter.mp hq).2) (by simp)
    rw [cval_zero, one_mul] at hpa
    rw [hpa] at h1
    set X := xm C 0 ((relL C (s.drop 2)).filter (asg C i))
    set e := s.getD 1 0
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
  have h1 := rp_relL C v hrel (s.drop 2)
  have hpa := prod_asg C v hI hW (relL C (s.drop 2)) 0 hall (by simp)
  rw [cval_zero, one_mul] at hpa
  unfold rp at h1
  rw [h1] at hpa
  have hfx : cval (cls C v) C.n (2 ^ (s.getD 1 0)) = cval (cls C v) C.n (xm C 0 (relL C (s.drop 2))) := by
    apply cval_fix
    intro k hk' hb
    have := List.all_eq_true.mp htr k (List.mem_range.mpr hk')
    rw [Nat.xor_comm, hb] at this
    simp at this
    exact hI.2.2 k hk' this
  rw [← cval_single (cls C v) C.n _ hk, hfx]
  exact hpa.symm

/-! ## Components: pending edges `v e = pw (v root) σ`, resolved by one equation -/

def pd (C : Cert) (e : ℕ) : ℕ := C.PD.getD e 1000000000
def pr (C : Cert) (e : ℕ) : ℕ := C.PR.getD e 0
def sg (C : Cert) (e : ℕ) : ℕ := C.SG.getD e 0

/-- signed power -/
def pw (r : K) (σ : ℕ) : K := if σ % 2 = 0 then r else r⁻¹

/-- root `[4, root]` -/
def rootOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  decide (pd C (s.getD 1 0) = i) && decide (pr C (s.getD 1 0) = s.getD 1 0) && decide (sg C (s.getD 1 0) % 2 = 0)

/-- link `[3, m, p, r₁, …]`: only `m` and `p` (pending, same root) are unknown; `σ m` from `σ p` -/
def linkOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  let m := s.getD 1 0; let p := s.getD 2 0; let R := relL C (s.drop 3)
  decide (pd C m = i) && decide (pd C p < i) && decide (pr C m = pr C p) &&
    trivB C i (xm C 0 (R.filter (asg C i))) &&
    match unas C i R with
    | [a, b] => (decide (a / 2 = m) && decide (b / 2 = p) && decide ((sg C m + a + sg C p + b + 1) % 2 = 0)) ||
                (decide (a / 2 = p) && decide (b / 2 = m) && decide ((sg C m + b + sg C p + a + 1) % 2 = 0))
    | _ => false

/-- exponent count of a pending part: `(#r, #r⁻¹)` -/
def cnt (C : Cert) (l : List ℕ) : ℕ × ℕ :=
  l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) (0, 0)

/-- equation `[1, root, mode, k, r₁, …]`: the unknown part lies in the component of `root`; mode 0: exponent
`±1`, the root gets the mask of the assigned part; mode 1: exponent `±2`, trivial assigned part, new class `k`. -/
def eqOK (C : Cert) (i : ℕ) (s : List ℕ) : Bool :=
  let root := s.getD 1 0; let R := relL C (s.drop 4); let U := unas C i R
  let X := xm C 0 (R.filter (asg C i)); let c := cnt C U
  decide (pd C root < i) && decide (pr C root = root) && decide (sg C root % 2 = 0) &&
    U.all (fun q => decide (pd C (q / 2) < i) && decide (pr C (q / 2) = root)) &&
    (if s.getD 2 0 = 0 then
      (decide (c.1 = c.2 + 1) || decide (c.2 = c.1 + 1)) && bitsB C i X
    else
      (decide (c.1 = c.2 + 2) || decide (c.2 = c.1 + 2)) && trivB C i X && decide (s.getD 3 0 < C.n) &&
        decide (C.CO.getD (s.getD 3 0) 1000000000 = i) && decide (C.RT.getD (s.getD 3 0) 0 = root))

/-! ## Soundness of links and equations -/

theorem pw_inv (r : K) (x : ℕ) : (pw r x)⁻¹ = pw r (x + 1) := by
  unfold pw; by_cases h : x % 2 = 0
  · rw [if_pos h, if_neg (by omega)]
  · rw [if_neg h, if_pos (by omega), inv_inv]

theorem pw_mod (r : K) (x y : ℕ) (h : x % 2 = y % 2) : pw r x = pw r y := by
  unfold pw; rw [h]

/-- value of a signed pending edge -/
theorem sv_pend {r : K} {q : ℕ} (h : v (q / 2) = pw r (sg C (q / 2))) : sv v q = pw r (sg C (q / 2) + q) := by
  unfold sv
  by_cases hq : q % 2 = 0
  · rw [if_pos hq, h]; exact pw_mod r _ _ (by omega)
  · rw [if_neg hq, h, pw_inv]; exact pw_mod r _ _ (by omega)

def PInv (i : ℕ) : Prop := ∀ e, pd C e < i → v e = pw (v (pr C e)) (sg C e)

/-- the assigned part of a relation is trivial once its mask is -/
theorem asg_part_one {i : ℕ} (hW : WF C) (hI : Inv C v i) {R : List ℕ} (htr : trivB C i (xm C 0 (R.filter (asg C i))) = true) :
    ((R.filter (asg C i)).map (sv v)).prod = 1 := by
  have hpa := prod_asg C v hI hW (R.filter (asg C i)) 0 (fun q hq => (List.mem_filter.mp hq).2) (by simp)
  rw [cval_zero, one_mul] at hpa
  rw [hpa]; exact triv_cval C v hI htr

theorem link_sound {i : ℕ} (hrel : ∀ r ∈ C.RS, rp v r = 1) (hW : WF C) (hI : Inv C v i) (hP : PInv C v i)
    {s : List ℕ} (hok : linkOK C i s = true) :
    v (s.getD 1 0) = pw (v (pr C (s.getD 1 0))) (sg C (s.getD 1 0)) := by
  unfold linkOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
  obtain ⟨⟨⟨⟨hm, hp⟩, hpr⟩, htr⟩, hmt⟩ := hok
  set m := s.getD 1 0; set p := s.getD 2 0; set R := relL C (s.drop 3)
  have h1 := rp_relL C v hrel (s.drop 3)
  unfold rp at h1
  rw [prod_split (sv v) (asg C i), asg_part_one C v hW hI htr, one_mul] at h1
  have hvp := hP p hp
  rw [← hpr] at hvp
  set r := v (pr C m)
  have key : ∀ a b : ℕ, a / 2 = m → b / 2 = p → (sg C m + a + sg C p + b + 1) % 2 = 0 →
      sv v a * sv v b = 1 → v m = pw r (sg C m) := by
    intro a b ha hb hpar hab
    have hsb : sv v b = pw r (sg C p + b) := by rw [← hb] at hvp ⊢; exact sv_pend C v hvp
    rw [hsb] at hab
    have hsa : sv v a = pw r (sg C p + b + 1) := by rw [← pw_inv]; exact eq_inv_of_mul_eq_one_left hab
    unfold sv at hsa; rw [ha] at hsa
    by_cases hq : a % 2 = 0
    · rw [if_pos hq] at hsa; rw [hsa]; exact pw_mod r _ _ (by omega)
    · rw [if_neg hq] at hsa; rw [← inv_inv (v m), hsa, pw_inv]; exact pw_mod r _ _ (by omega)
  have hU : (R.filter fun q => !asg C i q) = unas C i R := rfl
  rw [hU] at h1
  split at hmt
  next a b hab =>
    rw [hab] at h1
    simp only [List.map_cons, List.map_nil, List.prod_cons, List.prod_nil, mul_one] at h1
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hmt
    rcases hmt with ⟨⟨ha, hb⟩, hpar⟩ | ⟨⟨ha, hb⟩, hpar⟩
    · exact key a b ha hb hpar h1
    · exact key b a hb ha hpar (by rw [mul_comm]; exact h1)
  next => simp at hmt

theorem cnt_prod {r : K} (hr : r ≠ 0) : ∀ (l : List ℕ) (c : ℕ × ℕ),
    (∀ q ∈ l, sv v q = pw r (sg C (q / 2) + q)) →
    r ^ c.1 * r⁻¹ ^ c.2 * (l.map (sv v)).prod =
      r ^ (l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) c).1 *
      r⁻¹ ^ (l.foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) c).2 := by
  intro l
  induction l with
  | nil => intro c _; simp
  | cons q l ih =>
    intro c hl
    rw [List.foldl_cons, ← ih _ (fun q' h' => hl q' (by simp [h']))]
    rw [List.map_cons, List.prod_cons, hl q (by simp)]
    unfold pw
    split_ifs with h
    · simp only; ring
    · simp only; ring

theorem eq_sound {i : ℕ} (hrel : ∀ r ∈ C.RS, rp v r = 1) (hW : WF C) (hI : Inv C v i) (hP : PInv C v i)
    (hv : ∀ e, v e ≠ 0) {s : List ℕ} (hok : eqOK C i s = true) :
    (s.getD 2 0 = 0 → v (s.getD 1 0) * v (s.getD 1 0) = 1 ∧
      v (s.getD 1 0) = cval (cls C v) C.n (xm C 0 ((relL C (s.drop 4)).filter (asg C i)))) ∧
    (s.getD 2 0 ≠ 0 → v (s.getD 1 0) * v (s.getD 1 0) = 1) := by
  unfold eqOK at hok
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hok
  obtain ⟨⟨⟨⟨hpd, hpr⟩, hsg⟩, hU⟩, hmode⟩ := hok
  set root := s.getD 1 0; set R := relL C (s.drop 4)
  set X := xm C 0 (R.filter (asg C i))
  set r := v root
  have hr : r ≠ 0 := hv root
  have h1 := rp_relL C v hrel (s.drop 4)
  unfold rp at h1
  rw [prod_split (sv v) (asg C i)] at h1
  have hpa := prod_asg C v hI hW (R.filter (asg C i)) 0 (fun q hq => (List.mem_filter.mp hq).2) (by simp)
  rw [cval_zero, one_mul] at hpa
  rw [hpa] at h1
  have hsvU : ∀ q ∈ unas C i R, sv v q = pw r (sg C (q / 2) + q) := by
    intro q hq
    obtain ⟨hq1, hq2⟩ := hU q hq
    have := hP _ hq1
    rw [hq2] at this
    exact sv_pend C v this
  have hc := cnt_prod C v hr (unas C i R) (0, 0) hsvU
  simp only [pow_zero, one_mul] at hc
  have hU' : (R.filter fun q => !asg C i q) = unas C i R := rfl
  rw [hU', hc] at h1
  set c := cnt C (unas C i R) with hcdef
  have hcc : c = (unas C i R).foldl (fun c q => if (sg C (q / 2) + q) % 2 = 0 then (c.1 + 1, c.2) else (c.1, c.2 + 1)) (0, 0) := rfl
  rw [← hcc] at h1
  -- h1 : cval X * (r ^ c.1 * r⁻¹ ^ c.2) = 1
  have hrr : ∀ a b : ℕ, r ^ (b + a) * r⁻¹ ^ b = r ^ a := by
    intro a b; rw [pow_add, inv_pow]; field_simp
  have hrr' : ∀ a b : ℕ, r ^ b * r⁻¹ ^ (b + a) = r⁻¹ ^ a := by
    intro a b; rw [pow_add, inv_pow, inv_pow, inv_pow]; field_simp
  split_ifs at hmode with hm0
  · simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hmode
    obtain ⟨hc12, hbits⟩ := hmode
    have hsq := cval_sq_of C v hI (bits_of C hbits)
    have hrX : r = cval (cls C v) C.n X := by
      rcases hc12 with h | h
      · rw [h, add_comm, hrr 1, pow_one] at h1
        have := eq_inv_of_mul_eq_one_right h1
        rw [this, inv_eq_self hsq]
      · rw [h, add_comm, hrr' 1, pow_one] at h1
        have := eq_inv_of_mul_eq_one_right h1
        rw [← inv_inv r, this, inv_inv]
    refine ⟨fun _ => ⟨by rw [hrX]; exact hsq, hrX⟩, fun h => absurd hm0 h⟩
  · simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hmode
    obtain ⟨⟨⟨⟨⟨hc12, htr⟩, _⟩, _⟩, _⟩⟩ := hmode
    rw [triv_cval C v hI htr, one_mul] at h1
    refine ⟨fun h => absurd h hm0, fun _ => ?_⟩
    rcases hc12 with h | h
    · rw [h, add_comm, hrr 2] at h1; rw [← pow_two]; exact h1
    · rw [h, add_comm, hrr' 2, inv_pow] at h1
      rw [← pow_two]; exact inv_eq_one.mp h1

end RankNine.T2
