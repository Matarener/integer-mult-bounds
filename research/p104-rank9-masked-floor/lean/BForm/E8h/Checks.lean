import BForm.E8h.Data
import BForm.E8.Defs

/-!
# Small finite facts about the positive roots of E8

Integer data are lists, the facts are Boolean functions checked by `decide +kernel`.  Each check is small
(at most 120 × 104 short dot products).
-/

namespace BForm.E8h

open BForm.E8 (r8 dotZ)

def pr (j : ℕ) : List ℤ := posData.getD j []
def cf (j i : ℕ) : ℕ := (coefData.getD j []).getD i 0
def rf (i j : ℕ) : ℕ := (reflData.getD i []).getD j 0
def pl (t : ℕ) : ℕ := portLine.getD t 0
def ps (t : ℕ) : ℤ := portSgn.getD t 0

/-- lengths of the data -/
def lenOK : Bool :=
  posData.length == 120 && posData.all (·.length == 8) && coefData.length == 120 &&
  coefData.all (·.length == 8) && reflData.length == 8 && reflData.all (·.length == 120) &&
  portLine.length == 104 && portSgn.length == 104

/-- every positive root has norm 8 -/
def normOK : Bool := (List.range 120).all fun j => dotZ (pr j) (pr j) == 8

/-- `s_i (root j) = ± root (rf i j)`, sign `-` iff `j = i`, as `4 r_j - ⟨α_i, r_j⟩ α_i = ±4 r_k`; `rf i` is an
involution of the positive roots -/
def reflOK : Bool := (List.range 8).all fun i => (List.range 120).all fun j =>
  rf i j < 120 && rf i (rf i j) == j &&
  (List.range 8).all fun k =>
    4 * (pr j).getD k 0 - dotZ (pr i) (pr j) * (pr i).getD k 0 ==
      (if j = i then -4 else 4) * (pr (rf i j)).getD k 0

/-- every positive root is a non-negative integer combination of the simple roots -/
def coefOK : Bool := (List.range 120).all fun j => (List.range 8).all fun k =>
  (pr j).getD k 0 == ((List.range 8).map fun i => (cf j i : ℤ) * (pr i).getD k 0).sum

/-- ports are signed positive roots, on distinct lines -/
def portOK : Bool :=
  (List.range 104).all (fun t => pl t < 120 && (ps t == 1 || ps t == -1) &&
    (List.range 8).all fun k => (r8 t).getD k 0 == ps t * (pr (pl t)).getD k 0) &&
  portLine.Nodup

/-- number of positive roots supported on the simple roots `b` -/
def cnt (b : ℕ → Bool) : ℕ := (List.range 120).countP fun j => (List.range 8).all fun i => cf j i == 0 || b i

def bv (b0 b1 b2 b3 b4 b5 b6 b7 : Bool) (i : ℕ) : Bool :=
  match i with
  | 0 => b0 | 1 => b1 | 2 => b2 | 3 => b3 | 4 => b4 | 5 => b5 | 6 => b6 | _ => b7

/-- parabolic subsystems: more than 37 positive roots only for E7 (63), D7 (42) and everything -/
def paraP (b0 b1 b2 b3 b4 b5 b6 b7 : Bool) : Bool :=
  cnt (bv b0 b1 b2 b3 b4 b5 b6 b7) ≤ 37 || (b0 && b1 && b2 && b3 && b4 && b5 && b6) ||
    (b1 && b2 && b3 && b4 && b5 && b6 && b7 && cnt (bv b0 b1 b2 b3 b4 b5 b6 b7) == 42)

/-- `s_i α_i = -α_i` -/
def rfiOK : Bool := (List.range 8).all fun i => rf i i == i

/-- every root is non-orthogonal to at least 49 ports -/
def rootOK : Bool := (List.range 120).all fun j =>
  49 ≤ (List.range 104).countP fun t => dotZ (pr (pl t)) (pr j) != 0

/-- the D7 normal `ω₁ = r_a + r_b` with `r_a ⊥ r_b` -/
def d7OK : Bool := d7a < 120 && d7b < 120 && dotZ (pr d7a) (pr d7b) == 0

end BForm.E8h
