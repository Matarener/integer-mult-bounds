import RankNine.T2SDecode
open RankNine RankNine.T2 RankNine.T2M RankNine.T2S RankNine.Facts

/-! Evaluate `T2SR.ok (R.getD k 0) flData` on the files `t1data/t2s-<k>/head.txt`, `it-<i>.txt` (one item at a time,
`T2S.itsOK_cons`; the list `HP` of item supports is read first), and `t1data/t2-<k>/pairs.txt`.  `T2S k OK` means
exactly that conjunction for the decoded record. -/

def checkT2S (R : List ℕ) (k : ℕ) : IO Bool := do
  let dir := s!"t1data/t2s-{k}"
  let (zm, BIG, d0, f0, PL0, EW0, G, n) := parseT2SHead (← IO.FS.readFile s!"{dir}/head.txt")
  let c := R.getD k 0
  let mut HP : Array (ℕ × ℕ) := #[]
  for i in [0:n] do
    let it := parseIt (← IO.FS.readFile s!"{dir}/br-{i}.txt")
    HP := HP.push (it.b.σ, it.ctx)
  let HPl := HP.toList
  let h1 := d0.m == c && stabOK c G && flClosed flData && d0.okX BIG && pinsOK d0 f0 PL0 &&
    subset104 zm (pinZ d0.zm PL0)
  let h2 := BIG.all (fun E => frameOK E && (subM E c).all fun τ =>
    τ == 0 || EW0.any fun w => w.2.2.2 == 0 && wOK HPl G n 0 0 τ w)
  IO.println s!"T2SHEAD {k} head={h1} big={h2} items={n} G={G.length}"
  let mut ok := h1 && h2
  for i in [0:n] do
    let it := parseIt (← IO.FS.readFile s!"{dir}/br-{i}.txt")
    let r := it.ok c zm HPl G i
    if !r then IO.println s!"T2SIT {k} {i} FAIL okX={it.b.d.okX it.b.XF} pins={pinsOK it.b.d it.b.f it.b.PL} s={it.b.s} ctx={it.ctx}"
    ok := ok && r
  let (Y, P) := parsePairs (← IO.FS.readFile s!"t1data/t2-{k}/pairs.txt")
  let hp := pairsOK zm c flData Y P
  IO.println s!"T2SPAIRS {k} {hp}"
  IO.println (if ok && hp then s!"T2S {k} OK" else s!"T2S {k} FAIL")
  pure (ok && hp)

def checkT2SAll (ks : List ℕ) : IO Unit := do
  let R := parseList (← IO.FS.readFile "t1data/t2reps.txt")
  let W := parseW (← IO.FS.readFile "t1data/t2w.txt")
  let a := t2wOK R flData W
  IO.println s!"T2FACTS t2wOK={a} reps={R.length} W={W.length}"
  for k in ks do
    let _ ← checkT2S R k

#eval checkT2SAll []
