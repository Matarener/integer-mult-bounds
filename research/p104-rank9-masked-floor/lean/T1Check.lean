import RankNine.T3Decode
open RankNine RankNine.T2

/-! Evaluate the table checks on the record files `t1data/T1_<k>.txt`, `t1data/T3_<k>.txt`: one log line per type.
`FLOOR k OK` means exactly the hypotheses of `floor_of_records` for type `k`. -/

def checkOne (k : ℕ) : IO Unit := do
  let d1 := parseT1 (← IO.FS.readFile s!"t1data/T1_{k}.txt")
  let d3 := parseT3 (← IO.FS.readFile s!"t1data/T3_{k}.txt")
  let m := typeMask.getD k 0
  let a := d1.ok
  let b := d3.ok m
  let c := d1.m == m
  let e := d3.zm == d1.zm
  IO.println s!"T1CHECK {k} t1ok={a} t3ok={b} mask={c} zm={e} check={check d1.C} glue={glue1OK d1.C d1.EI d1.ER d1.EC d1.DS d1.nE d1.m d1.T d1.r0} cov={cov1OK d1.EI d1.ER d1.EC d1.nE d1.zm d1.C.NE} fr={t1FramesOK d1.DS d1.m} zfr={zFramesOK d1.zFT d1.m} zent={(List.range d1.zn).all (entryOK d1.m 104 d1.zG d1.zVT d1.zFT d1.zEN)} zedges={zEdges d1}"
  IO.println (if a && b && c && e then s!"FLOOR {k} OK" else s!"FLOOR {k} FAIL")

#eval checkOne 0
