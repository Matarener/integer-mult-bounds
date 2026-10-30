# Validation and execution boundaries

Environment: CPython 3.12.14, macOS arm64, standard library only. The coordinator
ran the registered package after the separate verifier agent's development
checks. Both registered warning-strict, isolated normal and optimized commands
passed and printed identical complete JSON reports. [RESULT.json](RESULT.json)
is that deterministic report with its success marker retained.

```sh
python3 -B scripts/research_package.py --package research/nonsplit-frobenius-characters
```

The registered manifest contains these direct commands:

```sh
python3 -I -W error -B research/nonsplit-frobenius-characters/verify.py
python3 -I -W error -O -B research/nonsplit-frobenius-characters/verify.py
```

`--json` prints the full report as one JSON object. Explicit exceptions retain
the checks under optimization. Five live source inputs are authenticated before
model import. The reused field/matrix module is separately hash-checked and
compiled from those exact bytes, avoiding stale bytecode for that dependency.

## Finite coverage

Six tiny complete matrix domains cover F4/F2, F9/F3, F8/F2, F27/F3,
F2 x F4 over F2, and F3 x F9 over F3. The checker examines 40,487 matrices,
22,854 invertible matrices and all 14 algebra automorphisms in those domains.
All 2,851 normalized autotopisms obtained from their full unit groups are
checked by products; the autotopism normalization theorem supplies completeness
of that parametrization, rather than an enumeration of every pair of matrices.

Two complete nilpotent substitution domains cover all six automorphisms of
F4[x]/x^2 over F2 and all 144 automorphisms of F9[x]/x^3 over F3, using coefficient
Frobenius and every allowed polynomial substitution. Their multiplication
matrices and determinants are checked independently.

Over the extension ground field F9, independent polynomial-remainder arithmetic
checks all 6,561 F81 products and all 80 nonzero norm determinants. The nilpotent
fixture checks 80 linear and eight nonlinear substitutions on F81[x]/x^3;
it does not enumerate that full 12,960-element automorphism group. The explicit
x -> u x witness has determinant beta^7 of order eight. A deliberately incorrect
extra residue-degree exponent produces only four squares. Further controls
check coefficient Frobenius on F9[x]/x^9 over F3 and an odd-degree F27 component
swap, both by literal ground-field matrices.

All 512 nonzero determinant triples over F9 are tested on a proper-subgroup
fixture: 128 are accepted with literal covariant coefficient checks and 384
are rejected. A nonlinear automorphism catches omission of the inverse-input
transposes. Independent changes in all three tensor factors are checked;
different determinant cosets produce different labels. Fourteen changed or
malformed certificates and eight presentation/type mismatches are rejected,
including equal-dimensional but different algebras and a separately valid
alternate field presentation.

## Review and limitations

Separate Codex agents implemented the model, wrote the proof and implemented
the independent checker. The coordinator reviewed the proof and implementation,
and an implementation agent independently reviewed the final proof/API agreement.
These are automated checks, not independent human review or proof-kernel acceptance.
The independent verifier shares only the retained ground-field primitive; its
extension arithmetic, elimination, multiplication-table and coefficient checks
are separate from the constructor. The classical/local character proofs are
retained dependencies.

The source-binding baseline passed after materializing tracked files omitted
from the sparse checkout. No selected scientific replay, previous full package
suite, Lean, Docker, native supplier, physical pricing, arbitrary nonsplit tensor
recognition or complete multiplication theorem was run or established. Different
field presentations require an explicit checked field isomorphism outside this
API. No polynomial-in-log(q) performance claim is made.

Committed-byte, source-history, official export and Git-free publication evidence
is reported with the exact published commit in the PR. Hosted CI is separate
from the local scientific checks and does not establish the general theorem.
