# Residue-assisted Gaussian recovery

This extends Mason Hale's existing certified Gaussian multiplier with a
paid low-residue lane. A short exact packed multiplication supplies each
convolution coefficient modulo 2^k. Numerical recovery can then use an
error radius below 2^(k−1), rather than below 1/2, while recovering the
same exact integer coefficients and final product.

On the retained source box (5,7,13), target box (8,16,32), α = 5 and
64-bit digits, the regenerated uniform certificates give:

| Residue bits k | Rounded Gaussian precision p | Bound on each packed child input | Additional exact packed products |
|---:|---:|---:|---:|
| 0, ordinary recovery | 208 | — | 0 |
| 8 | 200 | 5,456 bits | 1 |
| 16 | 192 | 9,096 bits | 1 |
| 24 | 184 | 12,736 bits | 1 |

The 16-bit lane is implemented end to end. The uniform proof covers **every
pair of nonnegative inputs up to 14,592 bits**, declared at that supported
width, using the actual Gaussian numerical path and one paid exact product
whose two inputs have at most 9,096 bits each. The original inputs are not
multiplied to produce the answer. Reference products and schoolbook
coefficients appear only in the verifier after recovery.

The comparison is against the least precision accepted by the same fixed
uniform certificate. Mason Hale's published configuration used p = 256;
its existing spare precision is not credited to the new modular lane.
The source-box and Gaussian enclosure precision Q = 448 are unchanged.
These are precision and exact-child contracts, not measured total speedups
or a new κ. The extra exact product and packing/lifting work must be paid.

PROOF.md proves the universal residue-lattice decoder and carry-free
Kronecker lane, exact child-size bounds, transfer of the preserved operator
certificate to lower p, both source-normalization factors and complete
all-input recovery. The Gaussian matrices, interval arithmetic, FFT,
permutations and numerical backend remain unmodified vendored source.
The proof and tests explicitly retain the source's p > 100 domain.

Evidence in RESULT.json includes 21,168 exact modular-convolution cases,
six fresh source precision-constructor checks, nine complete Gaussian
products, 1,836 actual Gaussian line calls and all 1,485 recovered
coefficients checked independently. All nine reported numerical radii
exceed 1/2, so the ordinary radius guard rejects those intervals; the
new residue classes enable their certified recovery. That does not rule
out a tighter ordinary numerical certificate. Four semantic control groups
include real slot spill, spacing and precision failures, the residue trust
boundary, and actual Git-free source/receipt corruptions, normally and
with assertions disabled.

Reproduce with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/modular-gaussian-recovery
```

Outside Git, run `verify.py`, `test_hybrid.py` and
`python3.12 -O -B test_hybrid.py` in the extracted directory. Inputs are
authenticated before importing the Gaussian backend. No private library,
network download, external Python package or foreign Git history is needed.

## Open next questions

1. Does the smaller exact lane pay for its precision reduction in a fully
   charged selected caller? Freeze the real transform/pointwise costs and
   compare their saving with the exact child, packing, extraction and
   residue-lifting costs. The arithmetic reference does not settle that bill.
2. Can the fast physical Gaussian backend expose the same certified
   coefficient interval? Start from one full PR3878/PR3851 caller, retaining
   all layouts, norms and both final source factors. The present backend is
   Mason Hale's dense reference; no native/tape adapter is supplied.
3. Which residue width is best after all costs? The 8/16/24-bit rows give
   concrete alternatives. Test against the ordinary 208-bit certificate,
   rather than comparing with the original overprovisioned 256-bit choice.
   Full all-size recurrence and base-case scheduling remain separate work.

Prepared by Dugongue with substantial OpenAI Codex assistance. The complete
informal proof and finite uniform source-bound certificate have no new
Lean/kernel or independent human review. NOTICE.md preserves predecessor
credit; classical modular reconstruction and Kronecker substitution are
not claimed as new inventions or first use in this project.
