# Attribution and source references

New work: MatShep, with substantial OpenAI Codex assistance (actual GPT-6.1
Sol/xhigh for derivation, code, exact checking and documentation). A brief
actual GPT-6 Astra/high publication sanity check is separate; it is not an
independent human, proof-kernel or full multiplication-theorem review.
All new files are Apache-2.0, under the repository license.

Ali Romman's PR5526 supplies the general pointwise Clifford/phase theorem and
open sharp-width/spectral question. MatShep's PR5549 and PR5594 supply the
one-qubit results and unreserved larger-qubit question. They are prior context,
not executable dependencies or certificates for this computation. The proof
and replay here are self-contained, with no imported predecessor code.

DLamdata's PR5547 and josecarlosgonzalezroque-design's PR5570 are distinct
independent AI-assisted scoped audits. Retain Dugongue, Chris R/Clear1nsight,
Cao Yifan, Cinna Davis, zxv, Krzysztof Wojt, Nick Petalas and the credited
native/controller/history/Clifford/analytic lineage. Classical finite-group
regular representations, Pauli normalizers, spectral projectors and the Schur
product theorem retain their classical status.

Exact pending-source context pins (not required at replay time):

- PR5526, Ali Romman, head`45f7de73b168721cdf7ec8c1769b1b594493716a`, `research/clifford-pointwise-faithfulness/PROOF.md`, SHA256`45483e4b5f604a5e70602c5caaa4394d4a0d0d1a6d0b6e8a93b836d50b23f764`.
- PR5549, MatShep, head`7f104c00852346f0d07c4e87e830284e8daab67b`, `research/full-clifford-one-qubit/README.md`, SHA256`a38fccb6b1196821f00442f03e376b884f07b40ba7ddf99ae42d3cefa9afbec8`.
- PR5594, MatShep, head`bb6598a1622f74eeb73aeacc290224ef388b717d`, `research/full-clifford-one-qubit-spectrum/PROOF.md`, SHA256`1a7432f859600b7933d02e74a99c5ff584596596efe67049041e0c3b2f8f61aa`.

No selected-frontier or supplier promotion is implied by local verification.

JoyboyBrian's PR5051, exact head 0960807a68ff46acbe6510c8867912ef2324ee71,
already independently enumerates all 11,520 two-qubit projective Cliffords
for partial signed-Pauli contracts. This submission's enumeration is a new
implementation of that classical finite alphabet; the new result is its
tensor Gram spectrum, threshold and conditioning, not the group count.
No PR5051 executable or proof is imported.
