# An explicit kernel of every retained full-frame native history

The new source-specific fact is simple: every raw-backward retained full-frame value is unchanged when the original logical X and Y inputs are shifted by the same arbitrary vector, with all helpers fixed. For the raw-forward word, shifting Y alone is invisible. These identities hold coefficient by coefficient in the native operator algebra. They remove the need for a monomial-independence assumption in this observation question.

## Exact statement

Use the frozen words and the source-bound event/frame semantics in native.py and SOURCES.json. The 632 persistent original roles are 112 X, 112 Y and 408 independent helpers. Retain every nonzero full-nine-dimensional-frame value throughout the entire word, even after an intended exit. Repeated identical values may be deduplicated. The source has no full-frame persistent input at entry. Zero values add no information.

Write H_f for this complete retained channel at any positive digit width f. The sparse scalar kernel certificate is

    backward: K v = (v, v, 0),
    forward:  K v = (0, v, 0),
    H_f K = 0,    K_Y = I_112.

For #5402 raw backward the channel contains 4,891 distinct nonzero values. The final #4610 raw-backward and raw-forward channels contain 5,019 and 4,968. The direct checker verifies the identity separately for each of them. KERNEL.json explicitly stores all 632 rows of the backward kernel; the forward version changes its X block to zero. Helpers and owned inputs are not identified with Y or surrendered: their change is zero.

It follows that every change of arbitrary Y can be accompanied by a change of X that leaves every retained value unchanged. In particular:

* No arbitrary address-linear combination of the retained values can equal a nonzero function only of the original Y. The left operators may be computationally expensive and need not be native monomials.
* Any postprocessor whose data consist only of this full-frame channel cannot exactly determine a nonconstant function of arbitrary Y. The ambiguity is between two valid independent-input instances with identical observations. Original helper values can also be supplied: they are the same in those instances.

The source question's b=ZQY_return, with the specified native return Y_return=Dy, is a nonzero pure-original-Y map. Nonzeroness follows from ZW=14I and invertibility of D,Q. The theorem therefore excludes recovering that target from the frozen channel alone. A later caller Y already mixed with X has a different meaning.

## Direct certificate and all-width proof

A logical history row has the form

    H_j = sum_(input s, native word g) a_(j,s,g) g x_s,

with rational scalar coefficients and literal native operators. The direct verifier freshly replays each frozen source and checks

    a_(j,X_i,g) + a_(j,Y_i,g) = 0   (backward),
    a_(j,Y_i,g) = 0                 (forward)

for every history, original index i and literal operator g. These are exactly H_j K=0. Thus a backward channel factors through X-Y and the helper inputs; a forward channel factors through X and the helper inputs. K_Y=I prevents the vacuous zero-kernel argument.

The actual-operator checker cancels coefficients of identical signed native monomials before numerical matrix evaluation. A separate formal checker repeats all three row identities using 72 free generator names and only adjacent inverse cancellation; it makes no actual-operator identification. Thus the kernel identities also survive any consistent invertible assignment of those letters, with forward and backward observation families interpreted separately. It does not use the width-one four-term linear relation, modular nonmembership, a tensor Gram rank, or an inverse of an operator polynomial. Absolute phases remain part of the literal operators, rather than being absorbed into exterior owner coefficients.

A composition or inverse identity between literal one-column native operators remains valid under their columnwise f-fold tensor lift, with spectator axes fixed. Extending this multiplicative assignment linearly, while keeping the rational owner coefficients unchanged, evaluates the same coefficientwise zero at every positive f. The owner kernel K is a scalar matrix between fields; it is not tensor-powered. Independence of different lifted operators is unnecessary.

For arbitrary left address operators A_j, multiplying the row identities gives

    (sum_j A_j H_j) K = 0.

If that sum were a nonzero Y-only linear map T, its product with K would instead be T because K_Y=I, a contradiction. For nonlinear postprocessing, compare an input z with z+Kv. Their whole channels coincide while their Y values differ by arbitrary v. This proves exact nonidentifiability without an approximation or precision lower bound.

## Physical coordinates and exact boundary

The source rows use logical native input coordinates. Every physical original input differs by its own invertible birth-frame factor on the right, and a logical complete frame has one common full-frame factor on the left. In raw backward this common factor is R inverse with the retained conjugated native letters. It must not be silently replaced by the forward R.

Applying the individual birth-frame maps to the kernel's input components gives the corresponding physical input displacement. Those maps do not mix original-field labels or X/Y/helper roles, and the Y displacement remains arbitrary. The full-frame left factor maps a zero logical history difference to zero. This conversion proves the physical ambiguity; it does not claim that preparing the compensating physical inputs is free or scalar-only.

The #5402 WORD is the raw native body. Its eight output caches are still partial-frame data until the provider boundary exchanges and clears them. They are not zero at the WORD endpoint and are not included as full-frame observations. The theorem does not describe the whole machine state as Y-blind. Lower-frame current Y, original X, partial cache reads, extra paid transformations, a changed word, or a relation restricting X and Y can supply different information and are outside this channel. Fixing the helpers or owned inputs alone does not remove this particular kernel, because their displacement is zero. A provider-boundary extension must explicitly check which new values are supplied; the native-body certificate does not replace that check.

The result concerns exact recovery on arbitrary source inputs. A finite-precision approximation lower bound, a profitable new supplier and the complete multiplication theorem require separate arguments. No new kappa or scientific acceptance is claimed by replay success.

## Verification and discovery

Run verify_kernel.py, formal_kernel.py and independent_kernel.py in normal and optimized Python. The direct checker checks all three channels, the 224 nonzero backward kernel entries, all 632 original rows and four failure controls: a vacuous zero kernel, a missing X compensator, a corrupted signed history coefficient, and an added original/lower-frame Y side observation.

Discovery first found a 474-row operator-module container for #5402, with non-Y unit upper triangle in discovery order. All 1,438 container terms turned out scalar, giving the simple kernel above. A separately written implementation checked the full container factorization and independently regenerated the scalar kernel from augmented histories, then verified it against the original operator-valued rows. The large discovery decomposition is not a runtime or proof dependency of the small direct certificate. Triangular elimination and kernel nonidentifiability are standard linear algebra; the source-specific complete-channel identities and their physical interpretation are the contribution.

Prepared by THU New Media Research Center (@thu-nmrc), with substantial OpenAI Codex multi-agent assistance. Retain Mark/Matarener's #5427 event/version semantics, Dillon's #5402 provider, Cao Yifan's #4610 word, the Cinna Davis/Dugongue/zxv/Chris R native, phase, controller and compiler lineages, and their Apache-2.0 notices.
