import RankNine.T1Tab

/-!
# Reading T1 records (data only; not used by any proof)

A record file (`t1lean/wdata.py`) is a stream of naturals.  `parseT1` rebuilds the record `T1D`; the table
hypothesis is then checked by evaluating `T1D.ok` on it (`T1Check.lean`).  Nothing here is trusted: a wrong decoder
can only make `ok` fail, since the soundness theorem `T1D.sound` holds for every record.
-/

namespace RankNine.T2

instance {α : Type} : Inhabited (BT α) := ⟨.em⟩

/-- insert at index `e` (same addressing as `BT.get`) -/
partial def BT.ins {α : Type} : BT α → ℕ → α → BT α
  | .em, 0, a => .lf a
  | .lf _, 0, a => .lf a
  | .nd l r, 0, a => .nd (BT.ins l 0 a) r
  | .em, e, a => if e % 2 = 0 then .nd (BT.ins .em (e / 2) a) .em else .nd .em (BT.ins .em (e / 2) a)
  | .lf b, e, a => if e % 2 = 0 then .nd (BT.ins (.lf b) (e / 2) a) .em else .nd (.lf b) (BT.ins .em (e / 2) a)
  | .nd l r, e, a => if e % 2 = 0 then .nd (BT.ins l (e / 2) a) r else .nd l (BT.ins r (e / 2) a)

/-- a reader state: the remaining numbers -/
abbrev Rd := StateM (List ℕ)

def rnat : Rd ℕ := do
  let s ← get
  match s with
  | [] => pure 0
  | x :: r => set r; pure x

def rlist : Rd (List ℕ) := do
  let n ← rnat
  let mut acc : Array ℕ := #[]
  for _ in [0:n] do
    acc := acc.push (← rnat)
  pure acc.toList

def rbtn : Rd (BT ℕ) := do
  let n ← rnat
  let mut t : BT ℕ := .em
  for _ in [0:n] do
    let i ← rnat
    let v ← rnat
    t := BT.ins t i v
  pure t

def rbtl : Rd (BT (List ℕ)) := do
  let n ← rnat
  let mut t : BT (List ℕ) := .em
  for _ in [0:n] do
    let i ← rnat
    let v ← rlist
    t := BT.ins t i v
  pure t

def rT1 : Rd T1D := do
  let RS ← rbtl
  let OD ← rbtn
  let MK ← rbtn
  let RT ← rlist
  let CO ← rlist
  let FO ← rlist
  let PD ← rbtn
  let PR ← rbtn
  let SG ← rbtn
  let ST ← rbtl
  let L ← rnat
  let GA ← rlist
  let NE ← rlist
  let n ← rnat
  let EI ← rbtn
  let ER ← rbtn
  let EC ← rbtn
  let DS ← rbtl
  let nE ← rnat
  let m ← rnat
  let zm ← rnat
  let nt ← rnat
  let mut T : Array (ℕ × Bool) := #[]
  for _ in [0:nt] do
    let e ← rnat
    let b ← rnat
    T := T.push (e, b == 1)
  let r0 ← rnat
  let zG ← rnat
  let zVT ← rbtl
  let zFT ← rbtl
  let zEN ← rbtl
  let zn ← rnat
  let zGV ← rbtn
  pure { C := { RS, OD, MK, RT, CO, FO, PD, PR, SG, ST, L, GA, NE, n }, EI, ER, EC, DS, nE, m, zm, T := T.toList, r0,
         zG, zVT, zFT, zEN, zn, zGV }

/-- the naturals of a text of decimal numbers separated by any non-digits -/
def parseNats (s : String) : List ℕ := Id.run do
  let mut acc : Array ℕ := #[]
  let mut cur : ℕ := 0
  let mut inNum := false
  for c in s.toList do
    if c.isDigit then
      cur := 10 * cur + (c.toNat - '0'.toNat); inNum := true
    else if inNum then
      acc := acc.push cur; cur := 0; inNum := false
  if inNum then acc := acc.push cur
  return acc.toList

def parseT1 (s : String) : T1D := (rT1.run (parseNats s)).1

end RankNine.T2
