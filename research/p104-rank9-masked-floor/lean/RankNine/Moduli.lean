import RankNine.Basic

/-!
# Certificate checker for the T1 moduli step (squares + propagation)

Pairs of lines are encoded by natural numbers (codes); `N : ℕ → K` is the symmetric frame-sum quantity.
A relation `(x, p, y, q)` means `N x * N p = N y * N q`.  A certificate is a list of steps that derive facts
`(u, v)` meaning `N u ^ 2 = N v ^ 2`:
* `seed i j oi oj`: relations `(x, p, y, q)` and `(x, q, y, p)` (after orientation) give `x ~ y` (needs `N p, N q ≠ 0`);
* `prop i o k`: relation `(x, p, y, q)` and fact `k = (x, y)` give `p ~ q` (needs `N x ≠ 0`);
* `trans k l`, `symm k`: equivalence.
`run_sound` proves that every derived fact is true.
-/

namespace RankNine

variable {K : Type*} [Field K]

abbrev Rel := ℕ × ℕ × ℕ × ℕ

def holds (N : ℕ → K) (r : Rel) : Prop := N r.1 * N r.2.1 = N r.2.2.1 * N r.2.2.2

/-- the 8 equivalent orientations of a relation -/
def orient : ℕ → Rel → Rel
  | 0, (x, p, y, q) => (x, p, y, q)
  | 1, (x, p, y, q) => (p, x, y, q)
  | 2, (x, p, y, q) => (x, p, q, y)
  | 3, (x, p, y, q) => (p, x, q, y)
  | 4, (x, p, y, q) => (y, q, x, p)
  | 5, (x, p, y, q) => (q, y, x, p)
  | 6, (x, p, y, q) => (y, q, p, x)
  | _, (x, p, y, q) => (q, y, p, x)

theorem orient_holds (N : ℕ → K) (o : ℕ) (r : Rel) (h : holds N r) : holds N (orient o r) := by
  obtain ⟨x, p, y, q⟩ := r
  simp only [holds] at h
  unfold orient
  split <;> simp only [holds] <;>
    first
    | linear_combination h
    | linear_combination (-1 : K) * h

theorem getD_prop {α : Type*} (P : α → Prop) (l : List α) (d : α) (hd : P d) (hl : ∀ x ∈ l, P x) (i : ℕ) :
    P (l.getD i d) := by
  induction l generalizing i with
  | nil => simpa using hd
  | cons a l ih =>
    cases i with
    | zero => simpa using hl a (by simp)
    | succ i => simpa using ih (fun x hx => hl x (by simp [hx])) i

inductive Step
  | seed (i j oi oj : ℕ)
  | prop (i o k : ℕ)
  | trans (k l : ℕ)
  | symm (k : ℕ)

def dRel : Rel := (0, 0, 0, 0)

def stepFact (rels : List Rel) (cov : List ℕ) (facts : List (ℕ × ℕ)) : Step → Option (ℕ × ℕ)
  | .seed i j oi oj =>
    match orient oi (rels.getD i dRel), orient oj (rels.getD j dRel) with
    | (x, p, y, q), (x', q', y', p') =>
      if x' = x ∧ q' = q ∧ y' = y ∧ p' = p ∧ p ∈ cov ∧ q ∈ cov then some (x, y) else none
  | .prop i o k =>
    match orient o (rels.getD i dRel), facts.getD k (0, 0) with
    | (x, p, y, q), (u, v) => if u = x ∧ v = y ∧ x ∈ cov then some (p, q) else none
  | .trans k l =>
    match facts.getD k (0, 0), facts.getD l (0, 0) with
    | (u, v), (v', w) => if v' = v then some (u, w) else none
  | .symm k =>
    match facts.getD k (0, 0) with
    | (u, v) => some (v, u)

def run (rels : List Rel) (cov : List ℕ) : List Step → List (ℕ × ℕ) → Option (List (ℕ × ℕ))
  | [], facts => some facts
  | s :: ss, facts =>
    match stepFact rels cov facts s with
    | none => none
    | some f => run rels cov ss (facts ++ [f])

def Fact (N : ℕ → K) (f : ℕ × ℕ) : Prop := N f.1 ^ 2 = N f.2 ^ 2

theorem stepFact_sound (N : ℕ → K) (rels : List Rel) (cov : List ℕ) (facts : List (ℕ × ℕ))
    (hrel : ∀ r ∈ rels, holds N r) (hcov : ∀ c ∈ cov, N c ≠ 0) (hf : ∀ g ∈ facts, Fact N g)
    (s : Step) (f : ℕ × ℕ) (h : stepFact rels cov facts s = some f) : Fact N f := by
  have hR : ∀ i o, holds N (orient o (rels.getD i dRel)) := fun i o =>
    orient_holds N o _ (getD_prop (holds N) rels dRel (by simp [holds, dRel]) hrel i)
  have hF : ∀ k, Fact N (facts.getD k (0, 0)) := fun k =>
    getD_prop (Fact N) facts (0, 0) (by simp [Fact]) hf k
  cases s with
  | seed i j oi oj =>
    have h1 := hR i oi; have h2 := hR j oj
    simp only [stepFact] at h
    revert h h1 h2
    generalize orient oi (rels.getD i dRel) = r1
    generalize orient oj (rels.getD j dRel) = r2
    obtain ⟨x, p, y, q⟩ := r1; obtain ⟨x', q', y', p'⟩ := r2
    intro h h1 h2
    simp only at h
    split_ifs at h with hc
    obtain ⟨rfl, rfl, rfl, rfl, hp, hq⟩ := hc
    cases h
    simp only [holds] at h1 h2
    simp only [Fact]
    -- h1 : N x * N p = N y * N q, h2 : N x * N q = N y * N p
    have hpq : N p * N q ≠ 0 := mul_ne_zero (hcov p hp) (hcov q hq)
    have : N x ^ 2 * (N p * N q) = N y ^ 2 * (N p * N q) := by
      calc N x ^ 2 * (N p * N q) = (N x * N p) * (N x * N q) := by ring
        _ = (N y * N q) * (N y * N p) := by rw [h1, h2]
        _ = N y ^ 2 * (N p * N q) := by ring
    exact mul_right_cancel₀ hpq this
  | prop i o k =>
    have h1 := hR i o; have h2 := hF k
    simp only [stepFact] at h
    revert h h1 h2
    generalize orient o (rels.getD i dRel) = r1
    generalize facts.getD k (0, 0) = g
    obtain ⟨x, p, y, q⟩ := r1; obtain ⟨u, v⟩ := g
    intro h h1 h2
    simp only at h
    split_ifs at h with hc
    obtain ⟨rfl, rfl, hx⟩ := hc
    cases h
    simp only [holds] at h1
    simp only [Fact] at h2 ⊢
    exact propagate (hcov u hx) h2 h1
  | trans k l =>
    have h1 := hF k; have h2 := hF l
    simp only [stepFact] at h
    revert h h1 h2
    generalize facts.getD k (0, 0) = g1
    generalize facts.getD l (0, 0) = g2
    obtain ⟨u, v⟩ := g1; obtain ⟨v', w⟩ := g2
    intro h h1 h2
    simp only at h
    split_ifs at h with hc
    subst hc
    cases h
    simp only [Fact] at h1 h2 ⊢
    exact h1.trans h2
  | symm k =>
    have h1 := hF k
    simp only [stepFact] at h
    revert h h1
    generalize facts.getD k (0, 0) = g1
    obtain ⟨u, v⟩ := g1
    intro h h1
    simp only at h
    cases h
    simp only [Fact] at h1 ⊢
    exact h1.symm

theorem run_sound (N : ℕ → K) (rels : List Rel) (cov : List ℕ)
    (hrel : ∀ r ∈ rels, holds N r) (hcov : ∀ c ∈ cov, N c ≠ 0) :
    ∀ (steps : List Step) (facts out : List (ℕ × ℕ)), (∀ g ∈ facts, Fact N g) →
      run rels cov steps facts = some out → ∀ g ∈ out, Fact N g := by
  intro steps
  induction steps with
  | nil => intro facts out hf h; simp only [run, Option.some.injEq] at h; subst h; exact hf
  | cons s ss ih =>
    intro facts out hf h
    simp only [run] at h
    split at h
    · exact absurd h (by simp)
    · rename_i f hs
      have hfs := stepFact_sound N rels cov facts hrel hcov hf s f hs
      exact ih (facts ++ [f]) out (fun g hg => by
        rcases List.mem_append.mp hg with hg | hg
        · exact hf g hg
        · simp at hg; subst hg; exact hfs) h

end RankNine
