# A rank-four P112 representation counterexample

Four disjoint literal pieces of binary support ranks **4,5,6,6** sum to a
nonzero P112 root-code word over every characteristic-zero field. Their
support sizes are 6,12,20,18, and their code intersection has dimension exactly
one. The coefficient values are integers -1 and 1. This answers PR3418's
explicit first-rank-four question by a counterexample.

[WITNESS.json](WITNESS.json) lists every site, label, coefficient, binary basis
and the exact nonzero joint-rank minor. [PROOF.md](PROOF.md) proves the identity
and field transfer. [RESULT.json](RESULT.json) records the checked values.
Only this new scoped package is added.

The witness needs no Weyl-chamber premise or pending predecessor theorem.
PR3418's conditional rank-three exclusion is credited context. Combined under
its stated premise, the first-rank boundary is three versus four. This package
alone proves the literal counterexample and exact one-dimensional intersection.
No decoder, complete caller, supplier, new kappa or selected-frontier change
is claimed.

## Reproduce

From the repository root with Python 3.12 and its standard library:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-four-piece-rank4
python3.12 -O -W error -B research/p112-four-piece-rank4/verify.py
python3.12 -O -W error -B research/p112-four-piece-rank4/independent.py
python3.12 -O -W error -B research/p112-four-piece-rank4/test_controls.py
```

Set TMPDIR to an owned external directory if the control fixtures must stay
in a particular session directory. The controls remove their temporary files.
The primary and separate implementation share authenticated inputs and the
literal witness, with distinct geometry/rank/determinant paths as described
in the proof. Actual optimized CLI controls include one acceptance and seven
rejections. Independent human and formal proof-kernel review are unclaimed.

[SOURCES.json](SOURCES.json) pins the two canonical live inputs at main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`. No unmerged object or network access
is required. The package verifiers run from a Git-free source export containing
the package and both inputs. The repository launcher additionally uses Git
for task provenance. [VERIFY.json](VERIFY.json) declares the exact live inputs
and bounded commands. There is no third-party mathematical dependency.

## Open next questions

Does this one-direction witness satisfy any actual remaining caller's quotient
and independence conditions? That determines whether the representation can
help a decoder. Start by pinning one actual caller and deriving its required
code-intersection dimension. No caller is bound here; a complete paid consumer
and physical invoice also remain unknown. Do not count the intersection-one
witness as a higher-dimensional caller solution. The structured question is
in [TASK.json](TASK.json).

## Credit and scope

Nick Petalas/PR3418 supplied the precise open rank-four question and conditional
rank-three boundary. PR3397/3405, PR3161/3162, the root-simplex package,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage keep their
scientific attribution. New work is Apache-2.0.

The original card is `complex-rank-shape-decoder`, priority revision six. This
is a declared side result about a representation boundary, without a new
physical decoder or paid profile. Its scoped value is settling the proposed
extension exactly. No further construction round is reserved. Human/formal
review, Lean, Docker and the selected cold replay are unrun.
