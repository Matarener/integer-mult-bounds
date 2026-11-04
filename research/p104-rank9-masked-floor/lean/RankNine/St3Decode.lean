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

def rpins : Rd (List (ℕ × ℕ × RCert)) := do
  let n ← rnat
  let mut acc : Array (ℕ × ℕ × RCert) := #[]
  for _ in [0:n] do
    let v ← rnat
    let k0 ← rnat
    let C ← rrc
    acc := acc.push (v, k0, C)
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
  let f ← rnat
  let PL ← rpins
  pure { σ, d, XF, s, X, Y, J := J.toList, dd, f, PL }

def rSt3 : Rd St3 := do
  let m0 ← rnat
  let zm ← rnat
  let BIG ← rframes
  let d0 ← rT1
  let f0 ← rnat
  let PL0 ← rpins
  let nB ← rnat
  let mut B : Array Br := #[]
  for _ in [0:nB] do
    B := B.push (← rBr)
  pure { m0, zm, BIG, d0, f0, PL0, B := B.toList }

def parseSt3 (s : String) : St3 := (rSt3.run (parseNats s)).1

def parseBr (s : String) : Br := (rBr.run (parseNats s)).1

/-- the head part of `St3.ok`, with the list `σs` of all branch supports -/
def T2.St3.okHead (st : St3) (σs : List ℕ) : Bool :=
  st.d0.okX st.BIG && st.d0.m == st.m0 && pinsOK st.d0 st.f0 st.PL0 && subset104 st.zm (pinZ st.d0.zm st.PL0) &&
  st.BIG.all (fun E => frameOK E && (subM E st.m0).all fun τ => τ == 0 || decide (τ ∈ σs))

/-- `St3.ok` is the head check and the branch checks in order (`brsOK` unfolds one branch at a time), so the
`#eval` can read the branches one file at a time. -/
theorem T2.St3.ok_eq (st : St3) : st.ok = (st.okHead (st.B.map Br.σ) && brsOK st.m0 st.zm [] st.B) := rfl

end RankNine
