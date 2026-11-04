import RankNine.St3Decode
import RankNine.T3Decode
open RankNine RankNine.T2

/-! Evaluate `St3.ok` for the stage-3 records `t1data/st3-<k>/head.txt`, `br-<i>.txt` (one branch at a time,
`St3.ok_eq`).  `ST3 k OK` means exactly the hypothesis `st.ok = true` of `St3.sound` for the decoded data, with
`st.m0` the type mask.  `FLOOR3 k OK` means exactly the hypotheses of `floor_of_st3`: `ST3 k OK`, the T3 record
`t1data/T3_<k>.txt` has `d3.ok m = true`, and `d3.zm = st.zm` (= the type mask, or the mask without the line `u` of
NOTE §4 in the 7 poor types, where `u` is the special line `d3.U` of T3). -/

def checkSt3 (k : ℕ) : IO Unit := do
  let hd := parseSt3 (← IO.FS.readFile s!"t1data/st3-{k}/head.txt")
  let nums := parseNats (← IO.FS.readFile s!"t1data/st3-{k}/head.txt")
  let nB := nums.getLast?.getD 0
  let mut σs : List ℕ := []
  for i in [0:nB] do
    let s ← IO.FS.readFile s!"t1data/st3-{k}/br-{i}.txt"
    σs := σs ++ [(parseNats s).headD 0]
  let m := typeMask.getD k 0
  let h := hd.okHead σs && hd.m0 == m
  IO.println s!"ST3HEAD {k} d0={hd.d0.okX hd.BIG} pins={pinsOK hd.d0 hd.f0 hd.PL0} zm={subset104 hd.zm (pinZ hd.d0.zm hd.PL0)} head={h} branches={nB}"
  let mut prev : List ℕ := []
  let mut ok := h
  for i in [0:nB] do
    let b := parseBr (← IO.FS.readFile s!"t1data/st3-{k}/br-{i}.txt")
    let r := b.ok hd.m0 hd.zm prev
    if !r then IO.println s!"ST3BR {k} {i} FAIL okX={b.d.okX b.XF} xf={xfOK b.XF b.d.m b.σ prev} pins={pinsOK b.d b.f b.PL} s={b.s}"
    ok := ok && r
    prev := prev ++ [b.σ]
  IO.println (if ok then s!"ST3 {k} OK" else s!"ST3 {k} FAIL")
  let d3 := parseT3 (← IO.FS.readFile s!"t1data/T3_{k}.txt")
  let b3 := d3.ok m
  let bz := d3.zm == hd.zm
  IO.println s!"FLOOR3CHK {k} st3={ok} t3={b3} zm={bz} zmFull={hd.zm == m} U={d3.U}"
  IO.println (if ok && b3 && bz then s!"FLOOR3 {k} OK" else s!"FLOOR3 {k} FAIL")

#eval checkSt3 212
