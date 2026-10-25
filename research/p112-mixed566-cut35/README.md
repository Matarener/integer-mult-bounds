# Conditional P112 mixed566 common cut 35

For every characteristic-zero field, three arbitrary residual vectors of
binary support ranks at most5,6,6 span at most one dimension of the shortened
P112 root-evaluation code outside ONE arbitrary common cut of size at most35.
This extends [PR3353](https://github.com/CrocSwap/integer-mult-bounds/pull/3353)'s
sufficient bound34. Sharpness and actual caller applicability remain open.

[PROOF.md](PROOF.md) handles all E6 and D6 branches. The new finite lemma
classifies sixty rank-five near-axis closures and bounds their full-D6-plane
coverage with two large rank-six axis sections by45. A separate four-root-basis
implementation agrees. The retained sharp A2 incidence20 lemma closes the E6
equality that stopped the predecessor proof. [RESULT.json](RESULT.json) binds
the exact counts, closure digests and all branch inequalities.

## Reproduce

From the repository root with Python3.12 and the standard library:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-mixed566-cut35
python3 -W error -B scripts/check_research_commit.py --package research/p112-mixed566-cut35 --check-source-history
```

Direct Git-free commands also work after exporting this package and its five
explicit live inputs in VERIFY.json:

```sh
python3 -W error -B research/p112-mixed566-cut35/verify.py
python3 -W error -B research/p112-mixed566-cut35/independent.py
python3 -O -W error -B research/p112-mixed566-cut35/test_verify.py
```

For a read-only export, set TMPDIR to a private writable directory for the
controls. Default replay writes nothing into the package. CHECKS.json records
the actual checked environment and commands. No third-party package, pending
Git object, native compiler, Lean or Docker is required.

## Sources and limits

Canonical baseline is6f100d4bb5083f8c35d96fd95a539811c62f245c, priority revision6.
SOURCES.json pins the geometry and four inherited proofs on that main. The
prior PR3353 at9677b4bcdc77f1e22a2891b6ff1b150c7f008395 motivates the open
question but is not an executable or mathematical dependency. All needed
premises are stated and independently source-bound here.

The standard Weyl-chamber theorem, global live capacities12/20, rank-five/six
concentration, small-fiber capacity, four-puncture capacity18, pair-union28 and
E6 incidence remain inherited. Their historical heavy replays are unrun.
No current caller exclusion, full C5, physical consumer or supplier, complete
multiplication theorem, new kappa or selected-frontier update is claimed.
Internal computational checks are distinct from independent human review.

The card scope is explicitly changed from decoder synthesis to the predecessor's
support-shortening handoff. The card's packing-ceiling positive control passes;
its five-percent construction gate is not claimed. The general selected
baseline command stopped because sparse checkout omits unrelated selected
packages, and no full selected replay was attempted. ENGINEERING.md records
the code review, rejected hypothesis and bounded runtime deviations.

## Open next questions

Does the same theorem hold at cut36, or is there a literal counterexample with
actual coefficients? This would locate the next support boundary. Start by
classifying equality in the E6 incidence84 and D6 union82 coverage46 cases.
The missing step is compatibility of binary supports with one common cut and
the two-by-three coefficient matrix. A separately reconciled actual caller is
also needed before claiming a decoder exclusion. No further round is reserved.

Credit PR3353/3325/3299/3295/3324/3292, the retained sharp A2 incidence20 and
PR3278/3269/3267/3260/3262, DreamingOfClouds/PR3154, David Arias, joaqcoo and
the root-simplex/E8/P112 lineage. Apache-2.0.
