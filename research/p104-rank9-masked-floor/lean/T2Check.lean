import RankNine.T2Decode
open RankNine RankNine.T2 RankNine.T2M RankNine.Facts

/-! Evaluate the T2 table hypotheses on the files `t1data/t2reps.txt` (the 9 representatives `R`), `t1data/t2w.txt`
(witnesses `W`), and per representative `k` the stage-3 record `t1data/t2-<k>/head.txt`, `br-<i>.txt` (one branch at
a time, `St3.ok_eq`) and the pair certificates `t1data/t2-<k>/pairs.txt` (`T2R.ok_eq`).  `T2FACTS OK` means
`t2wOK R flData W = true` and `flClosed flData = true`; `T2 k OK` means `r.ok (R.getD k 0) flData = true` for the decoded
record `r`.  Together: the hypothesis of `t2Pair_of_ex`. -/

def checkT2 (R : List ℕ) (k : ℕ) : IO Bool := do
  let dir := s!"t1data/t2-{k}"
  let hd := parseSt3 (← IO.FS.readFile s!"{dir}/head.txt")
  let nums := parseNats (← IO.FS.readFile s!"{dir}/head.txt")
  let nB := nums.getLast?.getD 0
  let mut σs : List ℕ := []
  for i in [0:nB] do
    let s ← IO.FS.readFile s!"{dir}/br-{i}.txt"
    σs := σs ++ [(parseNats s).headD 0]
  let c := R.getD k 0
  let h := hd.okHead σs && hd.m0 == c
  IO.println s!"T2HEAD {k} d0={hd.d0.okX hd.BIG} pins={pinsOK hd.d0 hd.f0 hd.PL0} zm={subset104 hd.zm (pinZ hd.d0.zm hd.PL0)} zmC={hd.zm == c} head={h} branches={nB}"
  let mut prev : List ℕ := []
  let mut ok := h
  for i in [0:nB] do
    let b := parseBr (← IO.FS.readFile s!"{dir}/br-{i}.txt")
    let r := b.ok hd.m0 hd.zm prev
    if !r then IO.println s!"T2BR {k} {i} FAIL okX={b.d.okX b.XF} xf={xfOK b.XF b.d.m b.σ prev} pins={pinsOK b.d b.f b.PL} s={b.s}"
    ok := ok && r
    prev := prev ++ [b.σ]
  let (Y, P) := parsePairs (← IO.FS.readFile s!"{dir}/pairs.txt")
  let r : T2R := { st := hd, Y, P }
  let hp := r.okPairs c flData
  IO.println s!"T2PAIRS {k} {hp} partners={P.length}"
  IO.println (if ok && hp then s!"T2 {k} OK" else s!"T2 {k} FAIL")
  pure (ok && hp)

/-- test of the pair certificates alone, with Gram set `zm = c` (as in the records: `st.zm = c`) -/
def checkPairs (R : List ℕ) (k : ℕ) : IO Unit := do
  let c := R.getD k 0
  let (Y, P) := parsePairs (← IO.FS.readFile s!"t1data/t2-{k}/pairs.txt")
  let hp := flData.all fun c' => P.any fun p => p.1 == c' && pcOK2 c c c' Y p.2.1 p.2.2.1 p.2.2.2
  IO.println s!"T2PAIRS0 {k} {hp} partners={P.length}"

def checkT2All (ks : List ℕ) (pk : List ℕ := []) : IO Unit := do
  let R := parseList (← IO.FS.readFile "t1data/t2reps.txt")
  let W := parseW (← IO.FS.readFile "t1data/t2w.txt")
  let a := t2wOK R flData W
  let b := flClosed flData
  IO.println s!"T2FACTS t2wOK={a} flClosed={b} reps={R.length} W={W.length}"
  IO.println (if a && b then "T2FACTS OK" else "T2FACTS FAIL")
  for k in pk do
    checkPairs R k
  for k in ks do
    let _ ← checkT2 R k

#eval checkT2All [] [0, 1, 2, 3, 4, 5, 6, 7, 8]
