import RankNine.St3Decode
open RankNine RankNine.T2

/-! Evaluate the stage-3 check on `t1data/ST3_<k>.txt`: `ST3 k OK` means exactly the hypothesis `st.ok = true` of
`St3.sound`, with `st.m0` the type mask. -/

def checkSt3 (k : ℕ) : IO Unit := do
  let st := parseSt3 (← IO.FS.readFile s!"t1data/ST3_{k}.txt")
  let m := typeMask.getD k 0
  let a := st.d0.okX st.BIG
  let nbad := (List.range st.B.length).filter fun i =>
    !((st.B.getD i { σ := 0, d := st.d0, XF := [], s := 0, X := [], Y := [], J := [], dd := 0 }).ok st.m0 st.zm
      ((st.B.take i).map Br.σ))
  IO.println s!"ST3CHECK {k} branches={st.B.length} d0={a} mask={st.m0 == m} zm={st.zm == m} bad={nbad.take 10}"
  IO.println (if st.ok && st.m0 == m then s!"ST3 {k} OK" else s!"ST3 {k} FAIL")
