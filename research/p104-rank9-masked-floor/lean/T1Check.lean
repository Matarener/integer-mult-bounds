import RankNine.T1Decode
open RankNine.T2

/-! Evaluate the T1 table check `T1D.ok` on record files `t1data/T1_<k>.txt` (log line per type). -/

def checkOne (k : ℕ) : IO Unit := do
  let s ← IO.FS.readFile s!"t1data/T1_{k}.txt"
  let d := parseT1 s
  IO.println s!"T1CHECK {k} ok={d.ok} check={check d.C} glue={glue1OK d.C d.EI d.ER d.EC d.DS d.nE d.m d.T d.r0} cov={cov1OK d.EI d.ER d.EC d.nE d.zm d.C.NE} fr={t1FramesOK d.DS d.m} zfr={zFramesOK d.zFT d.m} zent={(List.range d.zn).all (entryOK d.m 104 d.zG d.zVT d.zFT d.zEN)} zedges={zEdges d} m={d.m} zm={d.zm}"

#eval checkOne 0
