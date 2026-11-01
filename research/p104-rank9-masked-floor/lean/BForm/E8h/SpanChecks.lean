import BForm.E8h.SpanData
import BForm.E8h.Checks

/-!
# Finite facts for SpanFact

Port sets are 104-bit masks.  `atLeast5 s` certifies 5 set bits by clearing the highest bit (found by binary search) four times.
-/

namespace BForm.E8h

open BForm.E8 (r8 dotZ pbits par lists9 zero9)

def nm (j : ℕ) : ℕ := nMask.getD j 0
def pm (j : ℕ) : ℕ := pMask.getD j 0
def mm (j : ℕ) : ℕ := mMask.getD j 0

/-- one binary-search step for the highest set bit -/
def hbStep (m w s : ℕ) : ℕ := if 2 ^ (m + w) ≤ s then m + w else m

/-- the highest set bit of `0 < s < 2^128`, by binary search (equals `Nat.log2 s`) -/
def hb (s : ℕ) : ℕ :=
  hbStep (hbStep (hbStep (hbStep (hbStep (hbStep (hbStep 0 64 s) 32 s) 16 s) 8 s) 4 s) 2 s) 1 s

/-- clear the highest set bit -/
def clr (s : ℕ) : ℕ := s ^^^ 2 ^ hb s

/-- `s` has at least 5 set bits -/
def atLeast5 (s : ℕ) : Bool :=
  s != 0 && clr s != 0 && clr (clr s) != 0 && clr (clr (clr s)) != 0 && clr (clr (clr (clr s))) != 0

def bitsN (s : ℕ) : ℕ := (List.range 104).countP fun t => s.testBit t

/-- the odd-port masks: every label once, in the order of `lists9` -/
def oOK : Bool :=
  oData.map Prod.fst == lists9 &&
  oData.all fun lm => decide (lm.2 < 2 ^ 104) && (List.range 104).all fun t => lm.2.testBit t == par t lm.1

/-- inner product of port `t` with positive root `j` -/
def dp (t j : ℕ) : ℤ := ps t * dotZ (pr (pl t)) (pr j)

/-- the root masks; inner products of a port and a root on another line are `0` or `±4` -/
def maskOK : Bool :=
  nMask.length == 120 && pMask.length == 120 && mMask.length == 120 &&
  (List.range 120).all fun j => decide (nm j < 2 ^ 104) && (List.range 104).all fun t =>
    (nm j).testBit t == (dp t j != 0) && (pm j).testBit t == decide (0 < dp t j) &&
    (mm j).testBit t == decide (dp t j < 0) && (pl t == j || dp t j == 0 || dp t j == 4 || dp t j == -4)

/-- (F) every non-zero label has at least 44 odd ports; those with fewer than 47 are listed in `oBad` -/
def o44OK : Bool := oData.all fun lm => lm.1 == zero9 || (44 ≤ bitsN lm.2 && (47 ≤ bitsN lm.2 || oBad.contains lm))

/-- E7 case for the normal `N`: the odd ports off the hyperplane number 0, at least 5, or exactly one port
whose label is `l` -/
def rootCond (l : List ℕ) (s : ℕ) : Bool :=
  l == zero9 || s == 0 || atLeast5 s || (s == 2 ^ hb s && decide (hb s < 104) && pbits (hb s) == l)

def rootSpanJ (j : ℕ) : Bool := oData.all fun lm => rootCond lm.1 (lm.2 &&& nm j)

/-- port mask of `r_a + ε r_b` for orthogonal positive roots `a, b` -/
def nv (a b : ℕ) (pos : Bool) : ℕ :=
  (nm a ^^^ nm b) ||| (if pos then (pm a &&& pm b) ||| (mm a &&& mm b) else (pm a &&& mm b) ||| (mm a &&& pm b))

/-- D7 case, labels with fewer than 47 odd ports: the odd ports off the hyperplane number 0 or at least 5 -/
def d7Cond (s : ℕ) : Bool := s == 0 || atLeast5 s

def d7SpanA (a : ℕ) : Bool := (List.range 120).all fun b =>
  dotZ (pr a) (pr b) != 0 || oBad.all fun lm => d7Cond (lm.2 &&& nv a b true) && d7Cond (lm.2 &&& nv a b false)

end BForm.E8h
