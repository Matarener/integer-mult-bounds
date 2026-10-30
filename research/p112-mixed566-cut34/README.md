# Conditional mixed-rank P112 shortening at common cut 34

For three arbitrary residual pieces of binary support ranks at most 5,6,6,
the restricted P112 root code meets their span in dimension at most one
after deletion of ONE common set of at most 34 coordinates, over every
characteristic-zero field. [PROOF.md](PROOF.md) improves PR3325's conditional
sufficient threshold 33 by one. No sharpness, caller or kappa claim follows.

The new step handles equality in the union 82 branch. Rank-six concentration
and the inherited four-puncture capacity reduce the total support budget to 48.
Any 48-site cover must then give the rank-five piece 12 singleton sites, forcing
it onto a large axis too. Two axes cover at most 47 sites, a contradiction.
The inherited pair-union 28 bound gives the stronger 46 recorded by the replay.
The 84/85/86 branches and E6 remain strictly excluded; the 86 case is new here.

## Reproduce

Python 3.12 and the standard library suffice, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-mixed566-cut34
```

The three registered scripts also run in a committed Git-free source export:

```sh
python3 -W error -B research/p112-mixed566-cut34/verify.py
python3 -W error -B research/p112-mixed566-cut34/independent.py
python3 -O -W error -B research/p112-mixed566-cut34/test_verify.py
```

Use a private writable TMPDIR for the failure controls on a read-only export.
The primary script reads without writing. Its optional `--output PATH` writes
only outside the repository. Controls create private byte copies and never
change retained inputs. [RESULT.json](RESULT.json) records the exact new
inequalities and model counts; CHECKS.json records the performed commands.

## Sources, evidence and limits

Scientific baseline is canonical main 6f100d4bb5083f8c35d96fd95a539811c62f245c,
priority revision 6. SOURCES.json binds the exact live geometry and proofs
from PR3325/3299/3324. Their original capacities, concentration, pair-union,
four-puncture, E6 incidence and Weyl premises remain inherited and conditional.
Authentication of those bytes is separate from mathematical admission.

The new replay checks all 3780 unordered orthogonal root pairs, including 168
union 86 cases; all 896 union 82 ordered axes and their four orthogonal frame
punctures; 26-zero parabolic counts; and all eight axis assignments per branch.
A separate root constructor and bitmask checker agrees without predecessor
imports. It also enumerates all 4693 support-size triples after refinement.
Six optimized behavioral/source groups include actual corrupt executable-input
and input-to-provenance reclassification rejection.

This is a geometric side result answering PR3325's explicit Open next question.
It does not meet the decoder card's 5% complete-supplier improvement gate.
The family decision is to finish this implication and stop. No current caller,
full C5, global decoder floor, physical/native program, dirty restoration,
consumer invoice, supplier, multiplication theorem, selected frontier or kappa
changes. Historical heavy suites, selected cold replay, Lean, Docker and
human/proof-kernel review are unrun.

Engineering choices and scoped Python deviations are in ENGINEERING.md.
Credit Nick Petalas/PR3325/3299/3295/3324/3292, PR3278/3267/3260/3262/3269,
David Arias's quadratic model, DreamingOfClouds/PR3154, joaqcoo and the retained
E8/P112/root-simplex lineage. Substantial AI assistance was used for drafting
and checks. No independent human review is claimed. Apache-2.0.

## Open next questions

Does common cut 35 hold? First resolve E6's equality 86 and the new D6 retained-site
budgets, or construct literal support/coefficient data. Failure of this proof
at 35 is not a counterexample or sharpness result.

Which current caller needs this exact contract? Pin its support ranks, ONE
common cut and surviving code dimension before applying the theorem. Neither
caller reconciliation nor the physical invoice is supplied here. The structured
questions and blockers are in TASK.json. No further round is reserved.
