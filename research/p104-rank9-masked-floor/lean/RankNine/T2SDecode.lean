import RankNine.T2Decode
import RankNine.T2Sym

/-! Reading T2 records by orbits (`t1lean/t2s.py`, `t1lean/t2pair.py`; data only, not used by any proof). -/

namespace RankNine

open RankNine.T2 RankNine.T2S

def rEW : Rd (List (ℕ × ℕ × ℕ × ℕ)) := do
  let n ← rnat
  let mut acc : Array (ℕ × ℕ × ℕ × ℕ) := #[]
  for _ in [0:n] do
    let t ← rnat
    let i ← rnat
    let g ← rnat
    let k ← rnat
    acc := acc.push (t, i, g, k)
  pure acc.toList

def rIt : Rd It := do
  let b ← rBr
  let ctx ← rnat
  let EW ← rEW
  pure { b, ctx, EW }

/-- head: `zm`, `BIG`, `d0`, `f0`, `PL0`, `EW0`, `G`, number of items (items and pairs are read separately) -/
def rT2SHead : Rd (ℕ × List (List ℕ) × T1D × ℕ × List (ℕ × ℕ × RCert) × List (ℕ × ℕ × ℕ × ℕ) × List ℕ × ℕ) := do
  let zm ← rnat
  let BIG ← rframes
  let d0 ← rT1
  let f0 ← rnat
  let PL0 ← rpins
  let EW0 ← rEW
  let G ← rlist
  let n ← rnat
  pure (zm, BIG, d0, f0, PL0, EW0, G, n)

def parseT2SHead (s : String) := (rT2SHead.run (parseNats s)).1

def parseIt (s : String) : It := (rIt.run (parseNats s)).1

/-- `itsOK` checked one item at a time (`HP` is computed from the item headers) -/
theorem T2S.itsOK_cons (m0 zm : ℕ) (HP : List (ℕ × ℕ)) (G : List ℕ) (j : ℕ) (it : It) (r : List It) :
    itsOK m0 zm HP G j (it :: r) = (it.ok m0 zm HP G j && itsOK m0 zm HP G (j + 1) r) := rfl

end RankNine
