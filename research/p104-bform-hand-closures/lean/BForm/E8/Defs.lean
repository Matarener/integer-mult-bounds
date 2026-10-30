import Mathlib
import BForm.E8.Data

/-!
# Computable layer of the frame argument

Integer data are lists; the finite facts are Boolean functions checked by `decide +kernel`.
-/

namespace BForm.E8

def r8 (p : ℕ) : List ℤ := r8Data.getD p []
def dotZ (a b : List ℤ) : ℤ := (List.zipWith (· * ·) a b).sum
/-- frame coefficient `u(p,f) = ⟨p,f⟩/4` (doubled D8 coordinates, norm 8) -/
def uu (p f : ℕ) : ℤ := dotZ (r8 p) (r8 f) / 4
def fr (fi t : ℕ) : ℕ := (frData.getD fi []).getD t 0
def blk (fi b q : ℕ) : ℕ := ((blkData.getD fi []).getD b []).getD q 0
def pt (c : ℕ) : List ℤ := ptData.getD c []
def nv (m : ℕ) : List ℤ := nData.getD m []
def fmask (m : ℕ) : ℕ := fmaskData.getD m 0

/-- the class of a coefficient vector: index of the point `u / λ` (40 for `u = 0`) and `λ` -/
def clsOf (u : List ℤ) : ℕ × ℤ :=
  if u.all (· == 0) then (40, 0) else
    let g : ℤ := if u.all (fun a => a % 2 == 0) then 2 else 1
    let s : ℤ := match u.find? (· != 0) with | some a => if a < 0 then -1 else 1 | none => 1
    let l := s * g
    let v := u.map (· / l)
    let code := (List.zipWith (fun a e => (a + 1).toNat * e) v [1, 3, 9, 27]).sum
    (ptCode.getD code 40, l)

/-- the four frame coefficients of port vector `rp` on block `b` of frame `fi` -/
def uvec (fi b : ℕ) (rp : List ℤ) : List ℤ :=
  [0, 1, 2, 3].map fun q => dotZ rp (r8 (fr fi (blk fi b q))) / 4

def clsList (fi b : ℕ) : List ℕ := r8Data.map fun rp => (clsOf (uvec fi b rp)).1

def maskOf (cl : List ℕ) (fl : ℕ) : ℕ :=
  (cl.zipIdx).foldl (fun acc (c, p) => if c == 40 || fl.testBit c then acc ||| 2 ^ p else acc) 0

def clsSpec (u : List ℤ) : Bool :=
  let (c, l) := clsOf u
  (c == 40 && u.all (· == 0)) || (c < 40 && l != 0 && u == (pt c).map (l * ·))

/-- membership test of the port set `Z_{T,m}` -/
def zt (fl c : ℕ) : Bool := c == 40 || fl.testBit c

/-- C11: for every normal, the port set has at most 39 ports or is (pointwise) one of the 128 masks. -/
def checkT (fi b : ℕ) : Bool :=
  let cl := clsList fi b
  (r8Data.all fun rp => clsSpec (uvec fi b rp)) &&
  fmaskData.all fun fl =>
    cl.countP (zt fl) ≤ 39 ||
      (let k := maskData.idxOf (maskOf cl fl)
       k < 128 && (cl.zipIdx).all fun (c, p) => (maskData.getD k 0).testBit p == zt fl c)

/-! Small universal checks. -/

def r8Len : Bool := r8Data.length == 104 && fmaskData.length == 680 && maskData.length == 128 &&
  (List.range 104).all fun p => (r8 p).length == 8

/-- C1: `2 p = Σ_t u(p, f_t) f_t` for every frame -/
def frameIdOK : Bool := (List.range 13).all fun fi => (List.range 104).all fun p => (List.range 8).all fun k =>
  2 * (r8 p).getD k 0 == ((List.range 8).map fun t => uu p (fr fi t) * (r8 (fr fi t)).getD k 0).sum

/-- C2: each frame is orthogonal of norm 8 -/
def frameOrthoOK : Bool := (List.range 13).all fun fi => (List.range 8).all fun k => (List.range 8).all fun l =>
  ((List.range 8).map fun t => (r8 (fr fi t)).getD k 0 * (r8 (fr fi t)).getD l 0).sum == if k == l then 8 else 0

/-- C3: the frames partition the ports -/
def partOK : Bool :=
  ((List.range 104).all fun p => frameOf.getD p 0 < 13 && posOf.getD p 0 < 8 &&
      fr (frameOf.getD p 0) (posOf.getD p 0) == p) &&
  ((List.range 13).all fun fi => (List.range 8).all fun t =>
      fr fi t < 104 && frameOf.getD (fr fi t) 0 == fi && posOf.getD (fr fi t) 0 == t)

/-- C5: blocks are increasing 4-lists in `0..7`, and every three positions lie in a block -/
def blkOK : Bool := (List.range 13).all fun fi =>
  ((List.range 14).all fun b => ((blkData.getD fi []).getD b []).length == 4) &&
  ((List.range 14).all fun b => (List.range 4).all fun q => blk fi b q < 8 && (q == 3 || blk fi b q < blk fi b (q + 1))) &&
  ((List.range 8).all fun t1 => (List.range 8).all fun t2 => (List.range 8).all fun t3 =>
    (List.range 14).any fun b => ((blkData.getD fi []).getD b []).contains t1 &&
      ((blkData.getD fi []).getD b []).contains t2 && ((blkData.getD fi []).getD b []).contains t3)

/-- C8: points have length 4 and include the unit vectors -/
def ptOK : Bool := ((List.range 40).all fun c => (pt c).length == 4) &&
  [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]].all fun e => (List.range 40).any fun c => pt c == e

/-- C9: normals are non-zero and `fmask m` is the set of points orthogonal to `nv m` -/
def nOK : Bool := (List.range 680).all fun m =>
  (nv m).length == 4 && (nv m).any (· != 0) &&
  (List.range 40).all fun c => (fmask m).testBit c == (dotZ (pt c) (nv m) == 0)

def pf (i j : ℕ) : List (ℕ × ℕ) := (pfData.getD i []).getD j []

/-- C10: every three points lie in the hyperplane of some normal -/
def pfOK : Bool := (List.range 40).all fun i => (List.range 40).all fun j =>
  ((pf i j).all fun (m, msk) => m < 680 && msk == fmask m) &&
  (List.range 40).all fun k => (pf i j).any fun (_, msk) => msk.testBit i && msk.testBit j && msk.testBit k

/-! Labels.  A label `z ∈ F₂⁹` is a 0/1 list of length 9. -/

def pbits (t : ℕ) : List ℕ := (List.range 9).map fun k => if (portBits.getD t 0).testBit k then 1 else 0
def par (t : ℕ) (l : List ℕ) : Bool := (List.zipWith (· * ·) (pbits t) l).sum % 2 == 1
def lists9 : List (List ℕ) := (List.replicate 9 [0, 1]).sections
def zero9 : List ℕ := List.replicate 9 0

/-- C6/C13: frame pattern of every non-zero label -/
def labOK (l : List ℕ) : Bool :=
  let D := fun fi => (List.range 8).filter fun t => !par (fr fi t) l
  ((List.range 104).countP fun t => par t l) ≥ 44 &&
  ((List.range 13).all fun fi => (D fi).length == 0 || (D fi).length == 8 ||
      ((D fi).length == 4 && (List.range 14).any fun b => D fi == (blkData.getD fi []).getD b [])) &&
  (2 ≤ (List.range 13).countP (fun fi => (D fi).length == 0) || 5 ≤ (List.range 13).countP (fun fi => (D fi).length == 4))

def labsOK : Bool := lists9.all fun l => l == zero9 || labOK l

def ozOf (l : List ℕ) : ℕ := (List.range 104).foldl (fun acc t => if par t l then acc ||| 2 ^ t else acc) 0

/-- C12: mask `k` has at most 55 ports, and for every label the odd ports outside it number 0, at least 5, or
contain the port with that label -/
def maskOK (oz : ℕ) (l : List ℕ) (M : ℕ) : Bool :=
  let D := oz ^^^ (oz &&& M)
  let c := (List.range 104).countP fun t => D.testBit t
  c == 0 || 5 ≤ c || (List.range 104).any fun t => D.testBit t && pbits t == l

def maskSizeOK : Bool := maskData.all fun M => (List.range 104).countP (fun t => M.testBit t) ≤ 55

def masksOKFor (ls : List (List ℕ)) (ks : List ℕ) : Bool := ls.all fun l => l == zero9 ||
  (let oz := ozOf l
   ((List.range 104).all fun t => oz.testBit t == par t l) && ks.all fun k => maskOK oz l (maskData.getD k 0))

end BForm.E8
