# Sharp one-qubit full-Clifford tensor threshold

This scoped algebraic result gives pointwise tensor independence from width **5**
for the full one-qubit Gaussian-dyadic Clifford group modulo its four scalar
phases. The group has 96 exact lifts and 24 projective classes. The exact Gram
ranks at widths 1 through 9 are `4,10,20,23,24,24,24,24,24`.

This sharpens the n=1 sufficient pointwise threshold 8 in Ali Romman's
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526), at exact head
`45f7de73b168721cdf7ec8c1769b1b594493716a`, especially
[`PROOF.md` Sections 1 and 5](https://github.com/aliromman/integer-mult-bounds/blob/45f7de73b168721cdf7ec8c1769b1b594493716a/research/clifford-pointwise-faithfulness/PROOF.md).
The scope refines the formal-interface question to this smallest full-Clifford
alphabet. It does not change the selected result or supply a new kappa,
physical implementation, paid invoice or multiplication theorem.

## Argument and evidence

The exact generators are `S=diag(1,i)` and
`V=((1+i,1-i),(1-i,1+i))/2`. Both normalize the Pauli group. The enumerated
24 projective classes exhaust the one-qubit Clifford group: X has six signed
Pauli images, Z has four anticommuting signed Pauli images, and this action
determines a projective matrix. The exact scalar kernel in `Z[i,1/2]` consists
of the four Gaussian units, as in the predecessor.

For the enumerated representatives define
`H_f(g,h)=(tr(U_g* U_h)/2)^f`, the normalized tensor Gram matrix.
Exact Gaussian rational elimination gives `rank(H_4)=23` and `rank(H_5)=24`.
The latter Gram matrix is positive definite. Since
`H_(f+1)=H_f Hadamard H_1`, the Schur product theorem propagates this:
`H_f >= lambda I` implies `H_(f+1) >= lambda (I Hadamard H_1)=lambda I`.
Here `H_1` is positive semidefinite with diagonal one. Thus every width at
least 5 works; the explicit width-4 null vector in [RESULT.json](RESULT.json)
proves sharpness. The verifier computes unnormalized trace powers, which
differ from `H_f` by the nonzero scalar `2^f` and have identical ranks/kernels.

For one fixed residual in the 96-element group algebra, the predecessor's
four-residue Fourier argument therefore makes widths **5,6,7,8** sufficient
to decide vanishing at every positive width. The width-4 null vector times
the central residue-zero filter vanishes at widths 1 through 7 but not 8.
The saved witness is checked at both widths 4 and 8. Consequently no universal
test using only positive widths below 8 suffices. Fixed residual coefficients
are essential to this four-width statement.

## Reproduction and limits

Python 3.12 and the standard library suffice. From this directory:

```sh
python clifford-experiment.py
python -I -O -W error clifford-experiment.py
```

The research author ran both commands under CPython 3.12.10 on Windows; their
outputs were byte-identical, SHA256
`2163c2f6f4bbc77e126a3cc96e778fcded03512be6784b898afd21875389ce7d`.
The saved output includes every rank, null vectors and the representatives
stored as `2U`. The standalone verifier imports no predecessor executable.
It checks unitarity of all 96 elements, independently constructs 1,152 literal
tensor Gram entries at widths 4 and 5, and checks the same-residue witness.
Checks do not use removable Python assertions. Its SHA256 is
`400844199eb130c02215cd4affea736f3f80a08a7ee1f60572619bcd855b204a`.

This is author-checked exact evidence with a brief AI sanity review, not
independent human or proof-kernel acceptance. No selected cold replay,
physical supplier verification, full repository package wrapper, registered
CI replay or full theorem audit is claimed. This small package uses the
standalone commands above and does not opt into the generic replay manifest.
Canonical base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The predecessor is a mathematical source; executing this verifier does not
require its checkout or an unmerged Git object.

## Open next questions

What are the exact pointwise thresholds for larger full-Clifford groups?
They could sharpen sufficient algebraic identity tests. A first step is a
bounded exact Gram computation retaining the central residue. Group size and
exact arithmetic cost are the immediate blockers; no larger cutoff follows
from this one-qubit calculation.

## Attribution

Ali Romman retains credit for PR #5526's general theorem, phase conventions
and Fourier implication. Credit also the monomial results in
[#5521](https://github.com/CrocSwap/integer-mult-bounds/pull/5521),
[#5522](https://github.com/CrocSwap/integer-mult-bounds/pull/5522),
[#5529](https://github.com/CrocSwap/integer-mult-bounds/pull/5529) and
[#5542](https://github.com/CrocSwap/integer-mult-bounds/pull/5542), and DLamdata's
general-theorem audit [#5547](https://github.com/CrocSwap/integer-mult-bounds/pull/5547).
This result concerns the larger full-Clifford alphabet and does not repeat
those audits. Schur products, Pauli normalizers and Fourier inversion are
classical. No global literature-priority claim is made.

Prepared for MatShep with substantial OpenAI Codex assistance (GPT-6.1 Sol
research; GPT-6 Astra brief validation and publication). Apache-2.0.
