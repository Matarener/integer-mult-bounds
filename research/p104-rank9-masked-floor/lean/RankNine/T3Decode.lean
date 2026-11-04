import RankNine.T3Tab
import RankNine.T1Decode

/-! Reading T3 records (`t1lean/t3data.py`; data only, not used by any proof). -/

namespace RankNine

open RankNine.T2

def rint : Rd ℤ := do
  let n ← rnat
  pure (if n % 2 = 0 then ((n / 2 : ℕ) : ℤ) else -(((n + 1) / 2 : ℕ) : ℤ))

def rints : Rd (List ℤ) := do
  let n ← rnat
  let mut acc : Array ℤ := #[]
  for _ in [0:n] do
    acc := acc.push (← rint)
  pure acc.toList

def rrc : Rd RCert := do
  let X ← rlist
  let nN ← rnat
  let mut N : Array (List ℤ) := #[]
  for _ in [0:nN] do
    N := N.push (← rints)
  let No ← rints
  let D ← rint
  let pm ← rnat
  pure { X, N := N.toList, No, D, pm }

def rT3 : Rd T3D := do
  let f ← rnat
  let zm ← rnat
  let sm ← rnat
  let OL ← rlist
  let O ← rlist
  let nb ← rnat
  let mut bad : Array (ℕ × ℕ) := #[]
  for _ in [0:nb] do
    let a ← rnat
    let b ← rnat
    bad := bad.push (a, b)
  let nT ← rnat
  let mut T : Array PCert := #[]
  for _ in [0:nT] do
    let v ← rnat
    let w ← rnat
    let k0 ← rnat
    let k1 ← rnat
    let C ← rrc
    T := T.push { v, w, k0, k1, C }
  let nL ← rnat
  let mut LT : Array (ℕ × ℕ × RCert) := #[]
  for _ in [0:nL] do
    let v ← rnat
    let k0 ← rnat
    let C ← rrc
    LT := LT.push (v, k0, C)
  let U ← rnat
  let s1 ← rnat
  let s2 ← rnat
  let ks ← rnat
  let kt ← rnat
  let Cs ← rrc
  let Ct ← rrc
  let nG ← rnat
  let mut GC : Array (ℕ × ℕ × RCert) := #[]
  for _ in [0:nG] do
    let s ← rnat
    let k0 ← rnat
    let C ← rrc
    GC := GC.push (s, k0, C)
  let BsL ← rlist
  pure { f, zm, sm, OL, O, bad := bad.toList, T := T.toList, LT := LT.toList, U, s1, s2, ks, kt, Cs, Ct,
         GC := GC.toList, BsL }

def parseT3 (s : String) : T3D := (rT3.run (parseNats s)).1

end RankNine
