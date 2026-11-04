import RankNine.T1Stage3
import RankNine.T3Decode

/-! Reading stage-3 records (`t1lean/st3.py`; data only, not used by any proof: a wrong decoder can only make
`St3.ok` fail). -/

namespace RankNine

open RankNine.T2

def rframes : Rd (List (List ℕ)) := do
  let n ← rnat
  let mut acc : Array (List ℕ) := #[]
  for _ in [0:n] do
    let mut F : Array ℕ := #[]
    for _ in [0:8] do
      F := F.push (← rnat)
    acc := acc.push F.toList
  pure acc.toList

def rBr : Rd Br := do
  let σ ← rnat
  let d ← rT1
  let XF ← rframes
  let s ← rnat
  let X ← rlist
  let Y ← rlist
  let nJ ← rnat
  let mut J : Array (List ℤ) := #[]
  for _ in [0:nJ] do
    J := J.push (← rints)
  let dd ← rint
  pure { σ, d, XF, s, X, Y, J := J.toList, dd }

def rSt3 : Rd St3 := do
  let m0 ← rnat
  let zm ← rnat
  let BIG ← rframes
  let d0 ← rT1
  let nB ← rnat
  let mut B : Array Br := #[]
  for _ in [0:nB] do
    B := B.push (← rBr)
  pure { m0, zm, BIG, d0, B := B.toList }

def parseSt3 (s : String) : St3 := (rSt3.run (parseNats s)).1

end RankNine
