# The retained passive ceiling holds from width 72

This applies the new pointwise theorem to the retained
[passive saved-query ceiling](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/passive-saved-query-ceiling/README.md).
Chris R supplies that proof and its independent source/grade audit in
[PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978).
The actual native source is Dugongue's
[PR #4948](https://github.com/CrocSwap/integer-mult-bounds/pull/4948), head
`86e474038e05f99a76d41f71d81946ad2327e4a4`.
The retained source's result holds for all sufficiently large widths.
The new conclusion supplies an explicit width and a nonzero error bound.

## Contract and source facts

Read the frozen
[proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/passive-saved-query-ceiling/evidence/frozen/pr4948-saved-query-macro-gate/PROOF.md)
with its mandatory
[uniform-alphabet addendum](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/passive-saved-query-ceiling/evidence/frozen/pr4948-saved-query-macro-gate/UNIFORM-ALPHABET-ADDENDUM.md)
and
[owned-reset clarification](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/passive-saved-query-ceiling/evidence/frozen/pr4948-saved-query-macro-gate/OWNED-RESET-CLARIFICATION.md).
All three are byte-pinned replay inputs. The following facts are inherited:

- Four original main banks have 112 independent input fields each. Nine
  macro cuts and three paid responses supply 39 observed bank fields.
- For 104 zero-diagonal source ports in original bank 0, the allowed
  coefficient words have Fourier grades 0, 1 or 7. The exact audit checks
  all 5,408 nonzero late grade-7 words. Their target `D1 Q^-1` has grade 9.
- Every allowed left code factor is a scalar sum of monomial Clifford
  words. Left multiplication by each such word preserves Fourier grade.
- Every complete one-column word belongs to the same 17-axis Clifford
  group. The finite universe is independent of width. A word containing
  a Gaussian need not be monomial; the full Clifford theorem is used.

Scalar coefficients, choices of controls and finite numbers of decoder
operations may depend on the width. The paid word and each paid input
expression stay fixed. Source scalar coefficients remain outside tensor
powers. Only a scalar inside a native operator acquires its f-th power.

## New quantitative corollary

Fix any allowed decoder at any integer width f>=72=4*17+4. Expand one
affected input-to-target coefficient into its finite Clifford words.
Combine projective copies, with their phases raised to f. Call the result
`sum_g b_g U_g^(tensor f)`, where each U_g is unitary. Fourier grade is
unchanged by scalar phase, so the grade-9 target T is not one of these
projective classes. Equation (4) of the [new proof](PROOF.md) gives

    2^(-17f) ||T^(tensor f)-sum_g b_g U_g^(tensor f)||_HS^2
        >= (1/9)(1+sum_g |b_g|^2) >= 1/9.

The operator norm error in this coefficient is at least 1/3. Set all other
independent inputs to zero and choose a unit vector which attains this
coefficient's operator norm. The corresponding complete endpoint also has
error at least 1/3 on that input, when the endpoint uses the direct-sum
Euclidean norm. This does not assert error on every input or add 104 errors
on one common input.

At every f>=84=4*17+16 the same normalized squared-error lower bound can
be replaced by 125/126. The norm error is then at least sqrt(125/126).
These constants hold uniformly over all allowed width-dependent choices.
No enumeration of the 17-axis group or dense tensor matrix is needed.

Thus this passive contract cannot provide even a uniformly small-error
version of the missing endpoint at these widths. This corollary adds no
new lower bound on reset cost. Storage, COPY, finite code work and owned
CLEAR/reset may all be granted for free, as the retained clarification says.

## Verification and limits

[verify_application.py](verify_application.py) first authenticates every
retained package file. It then runs the unchanged retained verifier, which
replays the author bank/grade calculation, the independent trace/grade
audit and the five wrapper rejection controls. Its complete output must
match [PASSIVE-REPLAY.json](PASSIVE-REPLAY.json). It computes both new exact
finite Gram bounds and compares [APPLICATION-RESULT.json](APPLICATION-RESULT.json).

The source replay establishes the finite source facts. The written proofs
establish the uniform group premise, grade preservation and the universal
quantifiers. This is not an independent human review or a formal proof
kernel. No actual new decoder, physical emission, selected cold replay,
complete pricing, supplier admission or kappa improvement is claimed.

Active feedback into later paid gates, new paid calls, changed words or
targets, other observations, native internal prefixes and noncolumnwise
payload routing change the contract. They are outside this corollary.
No active-feed task is reserved or rejected by this package.
