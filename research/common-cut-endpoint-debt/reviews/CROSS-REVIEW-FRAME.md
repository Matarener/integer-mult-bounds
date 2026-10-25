# Independent mathematical review of the current-cut theorem

Verdict: PASS within the explicit unary current-cut endpoint model. No
mathematical correction is requested for the inspected frozen version.
This is a read-only source/proof review; no checker replay was performed.
It adds a companion review and does not modify either frozen core.

## Exact inspected files

The sibling `c07-frame` package was inspected at these hashes:

| File | SHA-256 |
| --- | --- |
| `check.py` | `47a80ba1a095d50fdc260377105ff4be41b6ece2d6e4a746f4ee4cda537e467c` |
| `PROOF.md` | `bf80994ec63c2d7bdf2801aaaf321c7682cf315a23ad220e55a83c3f25f2b166` |
| `CHECKS.json.gz` | `8cfc135e92affc914d05d5b769fedc761272e9adb840ee021b72507697806a14` |
| decompressed receipt | `63cf04dbd77a0d0920ffdb5a34d242849a31d478d100efa53d335ed26095738c` |
| `OUTPUT-INVENTORY.json` | `e52d4610724b07123700666345987e19f2f98ce52d99dc0a240dc2eb3cfba288` |

I read the entire current proof and checker, the retained endpoint producer,
and the relevant exact product/phase and path routines. Reading the frozen
receipt confirms all eight A/B inverse-pre common corners are `[1,0]`, and
all four C corners are `[0,0]`. This is inspection of retained evidence,
not an independent execution of its 322 phase evaluations or other tests.

## Exact phase and source identity

The product convention and the cut identities agree with the independent
counterexample construction. In conventional matrix order,

```
D_X=C_p F_past,
H=D_X^-1 M D_X,
J=C_p H C_p^-1=F_past^-1 M F_past.
```

Because `P_s=pre_s^-1` acts only on the common plane and its own fresh
block, it commutes with every earlier fresh Fourier factor as an actual
operator. The displayed telescoping therefore cancels adjacent actual
inverse factors without commuting an arbitrary M through a Fourier factor.
The counterexample exchanging past and future directions is admitted by
this argument. No absorbing-past inference remains.

The first-factor implication has the correct inverse convention:
`post S pre=T` gives `T pre^-1 R=post S R`. A retained Pauli decoration of
T is a paid monomial and does not change row support. The fixed source
`S R` ranks consequently constrain every admitted normalizer with that
source identity; selecting twelve saved winners is not substituted for the
universal source implication. The exact Gaussian checks separately certify
the chosen phase-bearing local first factors and their literal lowerings.

The full-native forward-path identity also retains phase. Since
`C_p^2=X_p` and all coordinate translation C gates commute,
`F_global X_p=(product_s F_s) C_q C_p^-1`. The common factor is left of the
same source pre-operator on both sides; no commutation of pre with it is
assumed. This certifies one full-native coefficient path. It does not imply
clearance of other arbitrary input coefficients in a changed caller.

## Written all-L and all-f claims

For the inverse-pre common-F form
`[[G,0],[G+G^-T,G^-T]]`, direct block multiplication gives
`B(F_fresh P R)=diag(G_CC,(G^-T)_FF)`. Complementary principal nullity then
gives native rank `m-4+2 rank(G_CC)`. The proof correctly uses inverse(pre),
not pre.

With identity insertions and disjoint fresh supports, the common corner of
the chronological product is the product of the local common corners.
Earlier fresh components cannot re-enter the common block through a later
local factor, because that factor is identity on the earlier fresh block.
The saved A/B corner is the same idempotent `diag(1,0)` at every repeated
stage; the C corner vanishes. Thus the claimed identity-insertion attainment
holds for all L, rather than only the listed finite L values. This corner
product argument is expressly not used after arbitrary inserted mixing.

The corrected general bound instead uses `s(UV)<=s(U)s(V)` and the fact that
every monomial has row support one. The exact factored endpoint has first
factor support `2^3` or `2^5`, and each subsequent fresh factor support
`2^5`. This proves the asserted deficit for every L in the declared endpoint
expression. Tensoring the local factors over f columns multiplies their
logarithmic support exponents by f; intervening monomials may still mix all
tensor addresses. No tensor-product restriction on those monomials is needed.

The separate unary-completion floor also follows by row support when the
intermediate endpoint is non-Clifford: a product of native children with
total rank R and monomials has support at most `2^R`. A deficit d requires
`R>=df`. The proof does not assign a Clifford B-rank to a non-Clifford map.
Its 32f sum is a necessary separate-unary rank floor, not a repair recipe or
whole recursive invoice. The later `-8L-8` calculation is correctly tied to
the stipulated old paired schedule and excludes its L=1 fixture.

## Arbitrary-input and finite evidence scope

The free group-ring two-column check establishes the noncommuting B1 word
at L=3 on arbitrary inputs. The general-L theorem is conditional on its
stated ordered endpoint expression; it is not presented as a newly built
general-L scalar caller. Likewise, the forward path is a coefficient of an
arbitrary-input block, not a claim that a complete new caller is diagonal.

For Clifford operator equality, complete signed Pauli images determine the
operator up to global phase, and one complete exact nonzero Gaussian column
fixes that phase. The source uses this sufficient criterion. It does not
claim enumeration of every ordinary basis column at dimension 17 or 47.
The m=17 Gaussian witnesses and all finite signed-tableau checks remain
distinct from the written all-L exact cancellation argument.

The fresh controls independently test signed-image and global-phase gates:
right input Z fixes the zero column while changing signed images, whereas
global i preserves signed images and changes the phase column. Each expected
failure checks its exact named error, and the same candidate with that guard
deleted executes outside the catch. Captured source buffers execute with
`optimize=0`; the wrapper preserves complete type-sensitive historical
receipt comparisons. No source loader or coverage problem was identified
in this bounded review.

Physical scans, phase arithmetic, raw helper returns, ownership, precision,
full caller construction and a stronger multiplication bound remain outside
the theorem. These exclusions are consistent with the counterexample proof
and are necessary to the stated scope.
