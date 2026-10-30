# Validation evidence

Python3.12, standard library, macOS; main base
`32890bc5de034ab8fc93ac88ead7279a6a416d04`.

- Normal complete actual-return gate:
  `python3.12 -I -B research/physical-block-core-return/verify.py --write`:
  PASS in8.131s. Both retain/regather schedules, all numerical margins and
  seven controls pass. The explicit generation run performs the full science
  and writes RESULT.json. A prior8.481s attempt passed both physical schedules
  but correctly failed an oracle discriminator whose +16 perturbation stayed
  in the same coarse p4 output bin; +64 fixes that test. No failed receipt was
  retained.
- `python3.12 -B scripts/research_package.py --package research/physical-block-core-return --check-only`:
  PASS metadata and pins. Combined registered scientific commands are not
  redundantly rerun after the normal gate and final optimized export replay.
- `python3.12 -I -O -B research/physical-block-core-return/test_integrity.py`:
  PASS four real CLI source rejections (modified/missing main predecessor,
  changed retained layout, changed adapted fixture) and two strict receipt
  type rejections (bool count and integer schedule flag). Rejections occur
  before scientific execution in a Git-free copy.
- Independent peer source review found no numerical/ownership blocker and
  tested200 signed-rational stage pairs against the explicit recurrence and
  the actual receipt's margins. Its one receipt-equality concern was fixed:
  replay compares canonical JSON, and the bool/int controls above now pass
  independently. This is agent review, not human or formal-kernel acceptance.

The final committed export is intended for one optimized complete typed-receipt
replay; the exact publication head, export hash and result are recorded in the
external handoff after export. Scientific adapter/oracle bytes are unchanged
since the normal gate; subsequent edits only tighten receipt typing and name
the after-control preparation-bank census explicitly.

```
python3.12 -B scripts/check_research_commit.py --package research/physical-block-core-return --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/physical-block-core-return --ref HEAD --input-ref 32890bc5de034ab8fc93ac88ead7279a6a416d04 --output /tmp/physical-block-core-return.tar
python3.12 -B scripts/export_research_package.py check /tmp/physical-block-core-return.tar
# In a new Git-free extraction of the checked archive:
python3.12 -I -O -B research/physical-block-core-return/verify.py
```

The normalized complex crop is `[0,-1/16,0,0,0,0,0,0]` in both schedules.
Retain pays29,995,126 operations and22,910 owner cells; regather pays30,220,120
and22,478. Common exact supplied-factor physical preparation pays946,116
operations separately. Including preparation owner, original page/source and
live count descriptors at each return gives28,923 versus28,491 retained cells;
the arbitrary ambient spectator is a shared excluded frame. These are
read/write/unit-move counters, not Python instruction counts. Both schedules
include the unused scalar-boundary owner and do not subtract erased capacity.
The preparation owner after isolated disk rejection has a separately labelled
high-water count; do not confuse it with its earlier capacity at each return.

The explicit return-path peak bound1091789/65536 is below the work limit32768
and the sufficient disk threshold64. First-pass and block headroom, actual
production factor consistency, old-H coefficient intervals and original-S
perturbation remain separate premises. The changed1/64 boundary diagonal is
a stated supplied-factor calibration. No equality with scalar BandedSolve,
net speedup over scalar Core, recursive invoice saving or new κ is claimed.
No Lean, Docker, historical full suite or selected-frontier replay was run.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
