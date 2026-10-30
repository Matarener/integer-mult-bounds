# Sharp full two-qubit Clifford tensor threshold and conditioning

The full two-qubit Gaussian-dyadic Clifford alphabet has **11,520 projective
classes**. Its sharp pointwise tensor-independence threshold is **9**.
For every width f>=9, its normalized tensor Gram matrix has optimal uniform
spectral bounds **315/1024** and **9855/4096**, hence sharp Gram condition
number **219/28**. All three constants are attained at width nine.

This answers the two-qubit next question left by MatShep's
[one-qubit spectrum PR5594](https://github.com/CrocSwap/integer-mult-bounds/pull/5594)
and sharpens the n=2 sufficient threshold 12 in Ali Romman's
[general pointwise theorem PR5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526).
It is a native-algebra side result: no new kappa, selected-frontier change,
physical supplier, precision/tape or paid-caller claim.

The [self-contained proof](PROOF.md) explains the all-width Schur-product step.
The computation avoids a dense 11,520-square Gram: it enumerates 46,080 exact
lifts and 59 conjugacy classes, then retains scalar-residue blocks of sizes
11,16,11,21. The [certificate](CERTIFICATE.json) contains exact finite block
matrices and eigenvalues at widths 1..12. The verifier regenerates each block
and certifies the spectrum and full regular multiplicities by unbounded-integer
polynomial identities. No symbolic or numerical eigensolver is used in replay.

Ranks at widths 1..12 are
`16,136,816,3426,9104,11384,11504,11519,11520,11520,11520,11520`.
The literal determinant character supplies a nonzero null vector at width
eight; its separate character sums are zero at eight and nonzero at four
and twelve. It is not an all-width identity.

## Reproduce

Python 3.12 and NumPy 2.3.5 suffice. No network, Git or predecessor executable
is needed for either direct scientific command once NumPy is installed:

```sh
python -B research/full-clifford-two-qubit-centre/verify.py
python -I -O -W error -B research/full-clifford-two-qubit-centre/verify.py
```

For registered metadata/pins and both scientific commands from the repository:

```sh
python -B scripts/research_package.py --package research/full-clifford-two-qubit-centre
```

Both modes pass locally on CPython 3.12.14, NumPy 2.3.5, Windows 11, with equal
complete JSON payloads in [RESULT.json](RESULT.json). The verifier authenticates
all group elements and class data, exact spectra and multiplicities, 64 literal
tensor Gram entries, and seven rejecting controls. It uses explicit checks
that remain active under optimized Python. The full width-nine spectrum is
tabulated in PROOF.md. The proof and finite certificate are author checked;
no independent human or proof-assistant acceptance is claimed. Hosted CI is
separate from these local checks.

## Sources and overlap

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority 7,
selected PR5413 unchanged. [TASK.json](TASK.json) records the changed scope
from the frozen formal-interface card. [SOURCES.json](SOURCES.json) pins the
catalogue and selected record as provenance; there are no external scientific
inputs. All matrix generators and certificate checks are implemented here.

Current guidance, the selected review and source manifest, live handoff thread
1166 and canonical Clifford thread 5236 were read. Targeted all-state PR/Issue
searches covered two-qubit tensor,11520,Clifford spectrum and Clifford Gram;
Discussion queries covered two-qubit and Clifford spectrum. The relevant
matches were the credited one-qubit/general packages and the distinct two-qubit
partial-Pauli census in JoyboyBrian's PR5051 and unrelated qubit repair PR5245.
The 11,520-class group count itself is classical/prior; this computation adds
the tensor spectrum and sharp quantitative bounds. No equivalent result was found in that bounded coverage.
The repository overlap helper was also attempted: gh was unavailable and local
sparse coverage was 4 of 7611 notes. The direct authenticated/public API checks
do not establish universal novelty, arbitrary historical diff coverage or
coverage of unpublished work. Active P104/query-history scopes are excluded.

## Open next questions

Does the sharp threshold 4n+1 continue at three or more qubits? This could
sharpen exact native interface tests. First seek a representation or class
reduction before a much larger enumeration. Only n=1 in the predecessor and
n=2 here are established; neither a general theorem nor a three-qubit test
is supplied. The [structured question](TASK.json) records these limits.

## Attribution

New two-qubit computation and certificate: MatShep with substantial OpenAI
Codex assistance. Credit Ali Romman/#5526, MatShep/#5549/#5594,
DLamdata/#5547, josecarlosgonzalezroque-design/#5570 and the retained lineage.
Exact predecessor references and source notices are in [NOTICE.md](NOTICE.md).
Finite-group centres, Pauli normalizers, character projectors, tensor Grams
and Schur products are classical. Apache-2.0.
