# A hint-free check of the GL3 length-eight refutation

**Claim type: an independent finite check of a saved unsatisfiability
certificate. No new κ.** It closes the gap #4331 left open: no checker
independent of drat-trim had accepted the length-eight refutation.

## Object

The GL3 certificates in
[PR #4331](https://github.com/CrocSwap/integer-mult-bounds/pull/4331) (ToikY,
from Brian Ross's lineage and #4242) come with saved RUP proofs from Glucose.

- **Length seven.** #4331 checks its CNF with a separately written LRAT
  interpreter. The hints come from drat-trim, which it treats as untrusted.
- **Length eight.** The drat-trim conversion to LRAT hit #4331's 512 MiB
  output limit. #4331 says it "supplies **no independent length-eight
  acceptance**". Only drat-trim itself had accepted it.

## Results

| Formula | Variables / clauses | Proof lines | Result |
| --- | --- | --- | --- |
| length 7 | 18,882 / 61,138 | 39,177 | **verified**: 11,728 additions RUP-checked, 27,449 deletions; `rupcheck.c` in 1.7 s, and `rupcheck.py` in CI in about 140 s |
| length 8 | 30,591 / 97,770 | 587,886 | **verified**: 281,714 additions RUP-checked in order, the last one the empty clause, 306,172 deletions; `rupcheck.c` in 191 s, 57 MB |

The inputs are #4331's files, matched to the SHA256 values in its
`CERTIFICATES.json`.

## Method

`rupcheck.c`, and its Python port `rupcheck.py`, check the proof **forward**.

- **Each addition.** Assume its negation and propagate units over the CNF and
  every earlier addition, with two watched literals. A conflict is required.
- **The end.** The proof must add the empty clause.
- **No outside help.** No LRAT hints are read, and no solver or drat-trim
  code is used.

**Why ignoring deletions is sound.** Every stored clause is entailed by the
CNF. Originals are entailed trivially, and each addition is entailed because
it passed its check. Extra clauses can only strengthen propagation; they
cannot make a non-entailed clause pass. The only cost is speed.

**Soundness evidence.**

- **Semantic controls on length seven.** Dropping core formula clause 100
  makes the same proof fail at addition 136. Flipping one literal of the
  first addition is rejected.
- **Fuzzing against brute force.** On random 3-CNFs, every satisfiable
  formula rejected every random proof, and every unsatisfiable formula
  accepted a tree-shaped refutation. In CI, `verify.py` runs 400 such
  formulas; locally the C checker passed 1,200 more.

## Not covered

- **What the formulas mean.** This is #4331's encoding audit and the earlier
  PR4214, PR4223 and PR4230 audits. This package checks only that these CNFs
  are unsatisfiable.
- **The minimum-nine theorem.** That needs normalization, support, compiler
  equivalence, padding and the nine-call witness. #4331's open question 2
  lists them.
- **Formal verification of this checker.** Its soundness rests on the code
  above, the controls and the fuzz.

## Reproduce

```sh
python3.12 -B research/gl3-length8-rup-check/verify.py
git fetch origin pull/4331/head:pr4331
git show pr4331:research/gl3-lrat-independent-check/source/length8.cnf > length8.cnf
git show pr4331:research/gl3-lrat-independent-check/source/length8.rup.gz | gzip -dc > length8.rup
cc -O2 -Wall -o rupcheck research/gl3-length8-rup-check/rupcheck.c && ./rupcheck length8.cnf length8.rup
```

`verify.py` prints `PASS_GL3_LENGTH8_RUP_CHECK` in about 3 minutes, using
only the standard library. It replays length seven in Python, runs the
controls and the fuzz, and checks that `evidence/RUP-RUNS.txt` was recorded
for this `rupcheck.c` and for the pinned length-eight inputs. The length-eight
run itself is local evidence; CI does not repeat it.

## Open next questions

None from this check. #4331's open question 1, an independently checked
length-eight certificate, is answered by the run above. Its questions 2 and
3, the model theorem and kernel formalization, remain.

## Credit

The encodings, certificates and saved proofs are Brian Ross's lineage, with
#4242 and #4331 by ToikY. Glucose4 and PySAT produced the proofs. RUP checking
is an established technique; drat-trim (Marijn Heule, Nathan Wetzler) is not
used here. Prepared by Ryanson Jonathan with substantial Claude Code (Claude
Opus 5.5) assistance. Apache-2.0.
