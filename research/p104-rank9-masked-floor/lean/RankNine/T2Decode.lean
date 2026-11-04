import RankNine.St3Decode
import RankNine.T2Main

/-! Reading T2 records (`t1lean/st3.py` with `KIND=T2`, `t1lean/t2pair.py`; data only, not used by any proof: a wrong
decoder can only make a check fail). -/

namespace RankNine

open RankNine.T2

def rfix (n : ℕ) : Rd (List ℕ) := do
  let mut acc : Array ℕ := #[]
  for _ in [0:n] do
    acc := acc.push (← rnat)
  pure acc.toList

def rintsFix (n : ℕ) : Rd (List ℤ) := do
  let mut acc : Array ℤ := #[]
  for _ in [0:n] do
    acc := acc.push (← rint)
  pure acc.toList

/-- pairs file: `Y` (8 lines), the number of partners, then per partner `c'`, `X` (8), `J` (64 entries), `dd` -/
def rPairs : Rd (List ℕ × List (ℕ × List ℕ × List (List ℤ) × ℤ)) := do
  let Y ← rfix 8
  let n ← rnat
  let mut P : Array (ℕ × List ℕ × List (List ℤ) × ℤ) := #[]
  for _ in [0:n] do
    let c ← rnat
    let X ← rfix 8
    let mut J : Array (List ℤ) := #[]
    for _ in [0:8] do
      J := J.push (← rintsFix 8)
    let dd ← rint
    P := P.push (c, X, J.toList, dd)
  pure (Y, P.toList)

def parsePairs (s : String) := (rPairs.run (parseNats s)).1

def rW : Rd (List (ℕ × ℕ × ℕ)) := do
  let n ← rnat
  let mut acc : Array (ℕ × ℕ × ℕ) := #[]
  for _ in [0:n] do
    let c ← rnat
    let g ← rnat
    let k ← rnat
    acc := acc.push (c, g, k)
  pure acc.toList

def parseW (s : String) := (rW.run (parseNats s)).1

def parseList (s : String) : List ℕ := (rlist.run (parseNats s)).1

/-- the pair part of `T2R.ok` -/
def T2.T2R.okPairs (r : T2R) (c : ℕ) (FL : List ℕ) : Bool :=
  FL.all fun c' => r.P.any fun p => p.1 == c' && pcOK2 r.st.zm c c' r.Y p.2.1 p.2.2.1 p.2.2.2

/-- `T2R.ok` is the stage-3 check, the type mask and the pair part (so the `#eval` can check them separately) -/
theorem T2.T2R.ok_eq (r : T2R) (c : ℕ) (FL : List ℕ) :
    r.ok c FL = (r.st.ok && r.st.m0 == c && r.okPairs c FL) := rfl

end RankNine
