# Conditional κ = 0.00247755 from native tensor composition

This contribution improves the conditional construction in
[PR #4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359), pinned at
`da637c87c89482bc4c86be36bd0071b3d400dbed`, by changing its complete complex
native invoice. The proposed exponent saving is **κ = 0.00247755**, an increase
of **0.00017755**, approximately **7.7196%**, over the source's 0.0023.
These are exponent-saving comparisons, not measured running-time gains.

The result remains conditional on the source native, integer compiler,
precision, storage, analytic, ordered-movement, fixed-tape, prime-padding,
and exact-recovery hypotheses. It is a new written construction with finite
exact checks, awaiting independent review. The selected frontier is unchanged.

## What changes

Give every helper in each of the seven p3 native calls its own arbitrary
independent input. Keep its completed transform at its native width. Pay the
four retained main idle windows as complete jobs, with their exact phase
corrections, and retain the native rank-eight center calls without splitting.
This yields 3,528 productive fields and the complete raw invoice

```
targets = {5:196, 6:126, 7:392, 8:651, 9:1491, 25:448, 57:224},
paid    = {1:17409, 2:4991, 3:1568, 4:714, 5:140, 8:504, 16:448}.
```

The raw invoice has paid ranks above its smallest target, so it cannot be
passed directly to the old compiler. The new construction first composes
mixed units in lockstep: distinct copies are synchronized at each actual
paid call, and a complete inner unit supplies those jobs before any parent
resumes. Productive and paid moments multiply, while owned centers remain
separate and uncredited. This is substitution of complete native programs;
it does not assume that tensor powers distribute over addition.

Next split only oversized paid jobs into consecutive transforms on disjoint
axes. A separate rank-one tail inequality pays for every split. At tested
saving **0.00247756**, the exact certificate uses tensor power 15,000 and
cutoff `4^15000`, below the smallest target `5^15000`. The resulting finite
mixed unit satisfies strict rank separation and a strict complete moment.
The inherited integer compiler and the rational outer parameter family from
[PR #4405](https://github.com/CrocSwap/integer-mult-bounds/pull/4405) then give
the declared κ.

## Proof and evidence

- [NATIVE.md](NATIVE.md) binds all 2,856 fresh helper uses, unchanged 672 main
  endpoints, 56 native center paths, and all 896 complete idle jobs. The
  phase check retains nonzero translations; deleting them is rejected.
- [TENSOR.md](TENSOR.md) proves the chronological tensor construction,
  paid-job cutoff estimate, rank-one tail condition, and replacement
  ownership/precision accounting.
- [ENDPOINT.md](ENDPOINT.md) specifies the finite uniform rank and checks all
  nine outer cost rows, 54 retained predicates, and three functional guards.
- [RESULT.json](RESULT.json) is the deterministic exact certificate, including
  source hashes and negative controls. A separate rational interval engine
  cross-checks the moment and tail inequalities.

The finite tensor word and resulting uniform template are specified by
algorithms at astronomical fixed ranks. Their instruction lists and actual
field counts have not been emitted. This is an asymptotic construction,
not a practical implementation or a formal multiplication theorem.

The complete original PR4359 replay, independently run for PR4405, passed
all 23 stages and all 59 declared artifact comparisons. That baseline replay
does not by itself validate this new construction; its new native bindings,
proof and arithmetic are checked here.

## Reproduction

Python standard library only. Normal verification reads and compares the
saved result; it does not regenerate source artifacts.

```sh
python3 -I -O -B research/pr4359-tensor-strictification/verify.py
python3.12 -B scripts/research_package.py --package research/pr4359-tensor-strictification
```

`EXPORTED-SOURCES.json` authenticates focused unchanged source exports from
PR4359 and two small executable dependencies from PR4405 at
`873d1b3c96a83b701a5c0bba8e37a861e6672fef`. Each exported byte sequence was
compared with its immutable source Git blob. Both source PRs are unmerged;
their commits are not falsely represented as publication ancestry. The
standard `SOURCES.json` retains main-branch task and selected-result provenance.

Source construction: @zxv, PR4359. Mixed flow: Jacob Alan Sussman,
PR4268 / Theorem 1G. The outer ledger and native predecessors retain the
source documents' attribution and repository notices. New construction,
proof, verification and review were prepared for @1337isnot1337 with substantial
OpenAI Codex assistance. Apache-2.0; original notices are retained.

## Open next questions

[TASK.json](TASK.json) records first steps and blockers. Larger controllers
have promising abstract tariffs but need full native phase and endpoint
binding before any exponent claim. Smaller tensor powers, rational cutoffs,
and tighter compiler estimates may reduce the sufficient ranks. Neither
search is a premise of this submitted result.
