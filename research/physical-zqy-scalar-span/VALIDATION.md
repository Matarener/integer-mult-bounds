# Validation scope

Python 3.12.13, standard library only, macOS arm64. The current registered
suite consists of eight commands. All eight pass on the kernel extension.
Default replay compares frozen receipts and writes no package files.

## Current kernel checks

- `verify_kernel.py` freshly replays the actual signed native histories in
  all three frozen words: 4,891 provider-backward, 5,019 source-backward and
  4,968 source-forward distinct nonzero full-frame values. It checks the
  explicit input kernel against every operator coefficient and verifies
  `K_Y=I`. Four failure controls reject a vacuous kernel, missing X
  compensation, one corrupted coefficient and added original-Y information.
- `independent_kernel.py` imports neither `native.py`, `monomial.py` nor the
  discovery code. Its separate native/group/frame implementation regenerates
  all 4,891 provider histories, derives the 224-entry kernel using exact
  Fraction elimination of scalar augmentations, then checks the kernel
  against every original operator-valued row. The final check, rather than
  the augmentation alone, certifies the claimed identity.
- `formal_kernel.py` repeats all three identities over 72 free generator
  names, cancelling only adjacent inverses. It uses the primary event/frame
  interpreter with a different word algebra; it is corroboration rather than
  an independently implemented parser. No matrix independence or width-one
  matrix-sum relation is required.
- `phase_audit.py` compares 147,456 native columns and 36,864 product columns
  with the retained exact Clifford evaluator, including absolute-phase and
  backward-direction controls.

All four scripts pass in normal and optimized Python, with `-I -W error -B`.
Checks use explicit exceptions and remain active under `-O`. The retained
Clifford engine also contains its own assertion-based internals; literal
column comparisons and the audit's failure controls remain explicit.

The small kernel and source-bound row identities are the proof dependencies.
The 13 MB discovery module factorization is neither shipped nor required.
See KERNEL-PROOF.md for the all-width and physical-coordinate argument.
These are internal AI-assisted checks, not external human acceptance or a
proof-kernel result. Exact committed-byte, export, read-only replay and hosted
CI receipts are recorded at the publication commit in the pull request.

## Historical scalar and finite-image checks

The initial publication at `6d81d47e6d107e3c52b4583526d31e102b219bdc`
passed its then-registered six commands, its committed-byte/export checks,
a read-only Git-free replay and hosted CI. Those commands ran `verify.py`,
`phase_audit.py` and `abi_closure.py`, each normally and with optimization.
Their scalar/Gram/ABI scripts and frozen results remain byte-identical to
that commit, but the rank and ABI checks are no longer in the default suite
or dependencies of the stronger kernel theorem.

That historical result includes exact projection ranks 546/546, 554/554 and
554/554; physical width-one operator rank 214 with a four-term relation;
the width-two 215-by-215 Gram determinant 298401053 modulo 1000000009; and
1,012 left maps producing 59,708 distinct products with the explicit
finite-family guard `f>=59,707`. The optional independent Fraction width-one
audit remains available via `independent_width1.py`. Its final source replay
passed in 105.727 seconds. See PROOF.md and INTERNAL-REVIEW.md for these older
restricted statements; they are not new kernel-extension replay claims.

## Limits

The channel includes only complete-frame values of the frozen native bodies.
Original X/Y, partial-frame caches, changed words or new paid transformations
are additional information requiring their own source-bound analysis. Fixing
helpers or owned inputs alone does not remove this kernel. No approximation
or finite-precision lower bound is proved.

No fixed-tape benchmark, selected cold replay, fresh complete native admission,
new paid/productive profile, exponent, precision/tape/stock/compiler funding,
Lean, Docker or complete multiplication theorem is claimed. No dependency
installation or unrelated historical suite was run. The optional full-history
ancestry preflight was not run in the shallow checkout; source blob pins and
the ordinary committed-byte preflight are separate checks.
