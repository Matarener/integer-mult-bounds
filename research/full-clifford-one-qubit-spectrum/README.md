# Sharp one-qubit Clifford tensor conditioning

For the **full 24-class projective one-qubit Clifford alphabet**, this package
gives the exact normalized tensor-Gram spectrum at every positive width.
For every `f>=5` its sharp uniform Riesz bounds are **3/8 and 15/8**, and its
Gram spectral condition number is at most **5**. All three constants are
attained at widths 5 and 6. The corresponding synthesis condition number
is at most `sqrt(5)`. This is an algebraic result with no new kappa.

The [proof](PROOF.md) defines the normalization and gives a four-residue
finite spectral certificate plus an exact recurrence, establishing all
widths rather than extrapolating a rank census. It also derives the best
normalized squared Hilbert-Schmidt distance when one target class is absent:
the optimal uniform floor from width 5 is **45/56**, attained at width 5.
That Hilbert-Schmidt sharpness does not claim operator-norm sharpness.

Ali Romman's [PR5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526),
head `45f7de73b168721cdf7ec8c1769b1b594493716a`, explicitly leaves the best
spectral constant open and supplies the general Gram/error framework.
MatShep's [PR5549](https://github.com/CrocSwap/integer-mult-bounds/pull/5549),
head `7f104c00852346f0d07c4e87e830284e8daab67b`, already establishes the sharp
one-qubit independence threshold 5; this package adds quantitative spectral
and approximation bounds. It does not repeat that rank result as new work.

## Reproduction and evidence

Python 3.12 and its standard library suffice. From the repository root:

```sh
python -B scripts/research_package.py --package research/full-clifford-one-qubit-spectrum
```

The registered normal and optimized commands both execute the exact science
and compare the complete recomputed JSON with [RESULT.json](RESULT.json).
The verifier can also run directly in an export without Git:

```sh
python -I -W error -B research/full-clifford-one-qubit-spectrum/verify.py --check-saved
python -I -O -W error -B research/full-clifford-one-qubit-spectrum/verify.py --check-saved
```

The self-contained [verifier](verify.py) checks all 96 exact lifts and their
24 signed-Pauli actions, four joint spectral projector systems, the exact
four-step recurrence, direct Gram reconstruction at widths 1..32, and a
separate Newton characteristic-polynomial calculation at widths 1..10.
It independently builds **1,728 literal tensor Gram entries** at widths
4, 5 and 6; checks rational extremal eigenvectors at 5 and 6; and checks
the exact inverse and every omitted-class optimizer at widths 5..8.
Literal tensor residuals corroborate the omitted-class minima at 5 and 6.

Seven semantic controls reject a stronger lower bound, a smaller upper bound,
extension to width 4, treating scalar-phase copies as independent, an altered
imaginary Gram entry, the wrong recurrence sign, and a stronger missing-class
floor. No check relies on removable Python assertions. The saved LF-formatted scientific receipt has SHA256
`939f5ce89deb07462057af7013ffcec78f11495126c05f4f4cbb17cea774049c`.
The research author's normal and optimized CPython 3.12.10 Windows outputs
were byte-identical. Hosted CI and independent human/formal acceptance are
separate from these author checks.

[SOURCES.json](SOURCES.json) records canonical base
`5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision 7 and precise
predecessor provenance. These historical files are not executable inputs:
the verifier imports no predecessor code or third-party package. The
[task metadata](TASK.json) explicitly records the scope change from the
formal-interface card to the prior package's open quantitative question.
The selected #5413 record was read; its physical cold replay is unrelated
to this isolated algebraic package and was not run.

## Limits

Coefficients at a single width may be arbitrary complex numbers and may
depend on that width. Scalar phases enter with their actual f-th powers.
The alphabet must have one representative per projective class. This
package supplies no larger-qubit extrapolation, physical native circuit,
paid invoice, supplier, precision/tape result, selected-frontier change or
full multiplication theorem. The selected framework assumptions remain.

## Open next questions

The next question is a symmetry-reduced exact spectrum for the full two-qubit
alphabet. First reduce by Pauli or other group symmetry and retain central
residues; its 11,520 projective classes block the present naive dense method.
No such computation or new threshold is claimed here. Structured relevance,
first step and blocker are in TASK.json; no follow-up is reserved.

## Attribution

Ali Romman retains credit for PR5526's general tensor/Gram and approximation
framework, scalar phases and explicit open question. MatShep's PR5549 supplies
the enumeration representation and prior rank threshold. Credit the distinct
core-theorem audit by DLamdata in PR5547 and paid-return bridge audit by
josecarlosgonzalezroque-design in PR5570, and their retained predecessor lineage.
Schur products, spectral projectors, Pauli normalizers and least squares are
classical; no global literature-priority claim is made.

Prepared for MatShep with substantial OpenAI Codex assistance: GPT-6.1 Sol
research and verification. Any publication requires the separately recorded
GPT-6 Astra brief review. This is not independent human or proof-kernel
acceptance. Apache-2.0.
