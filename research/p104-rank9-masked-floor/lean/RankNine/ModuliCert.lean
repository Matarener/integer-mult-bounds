import RankNine.Moduli

/-!
# Flat encodings of moduli certificates and the per-type check

`checkModuli rels cov steps quads` runs the certificate and checks that every quadruple
`(r, [(c₀, f₀), …, (c₃, f₃)])` has facts `(r, cᵢ)` at index `fᵢ - 1` (or `fᵢ = 0` and `cᵢ = r`).
`checkModuli_sound`: if the check passes, all four entries of every quadruple have the square of `N r`.
-/

namespace RankNine

variable {K : Type*} [Field K]

def mkStep (t a b c d : ℕ) : Step :=
  if t = 0 then .seed a b c d else if t = 1 then .prop a b c else if t = 2 then .trans a b else .symm a

def decodeSteps : List ℕ → List Step
  | t :: a :: b :: c :: d :: rest => mkStep t a b c d :: decodeSteps rest
  | _ => []

def decodeRels : List ℕ → List Rel
  | x :: p :: y :: q :: rest => (x, p, y, q) :: decodeRels rest
  | _ => []

/-- one quadruple entry: code `c` and fact pointer `f` (0 = the root itself) -/
def entryOK (out : List (ℕ × ℕ)) (r c f : ℕ) : Bool :=
  if f = 0 then c = r else out.getD (f - 1) (0, 0) = (r, c)

/-- a quadruple: root code and four (code, fact pointer) entries -/
abbrev Quad := ℕ × List (ℕ × ℕ)

def quadsOK (out : List (ℕ × ℕ)) (quads : List Quad) : Bool :=
  quads.all fun q => q.2.all fun e => entryOK out q.1 e.1 e.2

def checkModuli (rels : List Rel) (cov : List ℕ) (steps : List Step) (quads : List Quad) : Bool :=
  match run rels cov steps [] with
  | some out => quadsOK out quads
  | none => false

theorem entryOK_sound (N : ℕ → K) (out : List (ℕ × ℕ)) (hout : ∀ g ∈ out, Fact N g) (r c f : ℕ)
    (h : entryOK out r c f = true) : N c ^ 2 = N r ^ 2 := by
  unfold entryOK at h
  split_ifs at h with hf
  · simp at h; rw [h]
  · simp only [decide_eq_true_eq] at h
    have := getD_prop (Fact N) out (0, 0) (by simp [Fact]) hout (f - 1)
    rw [h] at this
    exact this.symm

theorem checkModuli_sound (N : ℕ → K) (rels : List Rel) (cov : List ℕ) (steps : List Step) (quads : List Quad)
    (hrel : ∀ r ∈ rels, holds N r) (hcov : ∀ c ∈ cov, N c ≠ 0) (h : checkModuli rels cov steps quads = true) :
    ∀ q ∈ quads, ∀ e ∈ q.2, N e.1 ^ 2 = N q.1 ^ 2 := by
  unfold checkModuli at h
  split at h
  · rename_i out hout
    have hf := run_sound N rels cov hrel hcov steps [] out (by simp) hout
    intro q hq e he
    simp only [quadsOK, List.all_eq_true] at h
    exact entryOK_sound N out hf q.1 e.1 e.2 (h q hq e he)
  · exact absurd h (by simp)

end RankNine
