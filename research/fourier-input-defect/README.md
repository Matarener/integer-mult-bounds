# The exact input price of unequal Fourier read maps

For a fixed phase-weighted permutation of the second Fourier spectrum, this
package proves the largest linear second-input space on which convolution
still works with every unrestricted first input. If tau is the read
permutation and h is the product of the two forward phases, then

    maximum complex input dimension
      = number of cycles C of tau with product_(y in C) h(y) = 1.

The sharp codimension is N minus that count. An explicit cycle basis attains
the bound. This is a scoped mathematical proof with exact finite
corroboration. It is not a paid-call saving or a new kappa.

The changed hypothesis is deliberate. Hanson Sun / bbMisk's
[PR #1477](https://github.com/CrocSwap/integer-mult-bounds/pull/1477) requires
both operands to be arbitrary and characterizes the allowed full-input
layouts. This contribution restricts the second operand, fixes the standard
first and final Fourier charts, and computes the exact price in input
dimension of a mismatched second read. The predecessor is cited rather than
audited. [PROOF.md](PROOF.md) gives the complete statement and proof.

## A nonzero sparse-input construction

For translation tau(y)=y+b with b of order d and constant h=lambda, the
maximal input space is exactly

    {v : supp(v) is contained in {x : chi(b,x)=lambda}}.

Its dimension is N/d if lambda^d=1, and zero otherwise. In G=(Z/4)^2,
b=(1,0), lambda=i permits every second input supported on x_0=1. This
four-dimensional space is maximal among all linear second-input spaces,
including dense ones, for that fixed wrapper. Every sixteen-dimensional
first input is allowed. The unequal-read wrapper returns (u*v)/256 in the
predecessor's normalization. A five-dimensional second-input space is
impossible. This is an algebraic construction; physical routing and
preparation costs remain unpriced.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fourier-input-defect/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fourier-input-defect/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fourier-input-defect
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fourier-input-defect --check-source-history
```

Substitute another CPython 3.12 executable elsewhere. The direct marker is
`PASS_FOURIER_INPUT_DEFECT`. Verification writes a generated JSON receipt to
stdout, binding the six package file hashes and an ordered classification
digest. No receipt is hand-authored or written into the checkout.

The independent rational-rank oracle realifies I-D_h P_tau. Its rank must
equal twice the asserted complex codimension. The cycle solver uses a
different representation and constructs every allowed basis vector.
Literal Fourier transforms over Gaussian integers are compared with direct
group-addition convolution, including a nonconstant split of h between the
two forward phase maps. All acceptance checks remain active under `-O`.

The fixed replay covers:

- All 6,564 permutations with fourth-root phase assignments at dimensions
  one through four, with 13,556 cycles and 3,389 balanced cycle vectors.
- All 12,324 layouts on the trivial group, Z/2, Z/4 and (Z/2)^2. These give
  25,625 accepted convolution basis pairs, 6,413 dense first operands and
  46,139 forbidden-coordinate witnesses. The dimension-three fixtures
  receive rank and kernel checks, with no Z/3 Fourier computation claimed.
- All 104 translation/constant-phase fixtures on Z/2, Z/4, (Z/2)^2 and
  (Z/4)^2, checking 1,168 time-coordinate columns against character-level
  support, plus all 64 input basis pairs for the explicit sparse example.
- Seven malformed-domain rejections and three semantic controls that
  distinguish unbalanced cycles, nonconstant balanced cycle vectors and
  the incorrect constant-vector rule.

The card's first command, `scripts/research_selected_baseline.py`, passed
with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. It was source orientation,
not a scientific replay. Hosted CI is separate from local verification.

## Scope and implementation

The written proof covers every finite abelian group with its standard
nondegenerate symmetric pairing, arbitrary permutations and arbitrary unit
complex phases. The finite replay uses fourth roots and the bounded groups
listed above. Neither claim extends to arbitrary changes of the final map,
coupled restrictions on both operands, or approximate equality.

No actual physical caller, sparse-input preparation, ownership/restoration,
movement, native circuit, precision/storage bound, stock, complete supplier
invoice, selected framework assumption, supplier admission or multiplication
theorem is established. Independent human and formal proof-kernel review are
unclaimed. No predecessor scientific replay, selected cold replay, Lean or
Docker run is part of this contribution.

The checker has no recursion, subprocesses, dynamic imports or filesystem
mutations. Exhaustive permutation/phase loops stop at dimension four;
translation and Fourier helpers stop at sixteen coordinates; rank matrices
have at most 32 rows and columns. Every function is below sixty lines. Source
reads are capped at one MiB and the source inventory at eight rows. All
arithmetic is integer or Fraction arithmetic. Power of Ten rule 3 has a
managed-runtime deviation: CPython allocates objects during execution.
The fixed domains bound live mathematical data, and fixtures are streamed.
Larger domains require a new capacity assessment. Warning-strict normal and
optimized execution and AST inspection provide the available diagnostics;
no repository-wide diagnostic configuration is changed.

## Sources and credit

[SOURCES.json](SOURCES.json) pins the unchanged predecessor README at
canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`. The runtime checks
its SHA256 without executing its scientific code. [TASK.json](TASK.json)
records the changed side-result scope under `uniform-transfer-audit`.
The selected frontier is unchanged.

This contribution was produced by Nick Petalas. Credit Hanson Sun / bbMisk
#1477 for the weighted Fourier interface, full-input boundary and
normalization, Ross Richardson #940 for its unweighted predecessor, and
the retained Fourier/construction lineage. Weighted-permutation cycle
decomposition, character orthogonality and rank-nullity are classical;
literature priority for those methods is unclaimed. Apache-2.0.

## Open next questions

Can an actual convolution caller provide a character-level sparse operand
and absorb the shifted read and phase at a favorable complete cost? Start
with one literal operand and translation, prove its support contract, then
charge preparation, movement, restoration, precision and the complete
wrapper. No such caller or invoice is supplied here. The exact dimension
formula alone does not make the changed layout a cheaper supplier.
