import RankNine.Data

/-!
# List-level definitions for P104

Lines are indices `0 … 103`; `root i` is the integer root of line `i` in A8 coordinates.  Two lines are orthogonal
iff their roots have dot product `0`.  Everything here is computable so that finite facts are checked by
`decide +kernel`.
-/

namespace RankNine

def root (i : Nat) : List Int := rootData.getD i []

def dotL : List Int → List Int → Int
  | a :: as, b :: bs => a * b + dotL as bs
  | _, _ => 0

def dot (i j : Nat) : Int := dotL (root i) (root j)

def orth (i j : Nat) : Bool := dot i j == 0

def frame (f : Nat) : List Nat := frameData.getD f []

/-- a list of lines is a frame: 8 distinct lines, pairwise orthogonal -/
def isFrame (l : List Nat) : Bool :=
  l.length == 8 && l.all (· < 104) && l.Nodup && (l.all fun a => l.all fun b => a == b || orth a b)

theorem frameData_frames : frameData.all isFrame = true := by decide +kernel

theorem frameData_length : frameData.length = 759 := by decide +kernel

theorem typeMask_length : typeMask.length = 387 := by decide +kernel

end RankNine
