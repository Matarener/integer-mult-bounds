# Exact sum and fixed parity checks under uniform coefficient error

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Fix N >= 2, a binary m by N matrix H, and a real R >= 0. The unknown
coefficient vector is c in Z^N. A decoder receives a real vector y with
|y_i-c_i| <= R, the exact integer S=sum_i c_i, and H(c mod 2).
It must recover c for every such input. The rows of H are fixed before c
and y are known. The decoder itself can be nonlinear and computationally
unbounded. Giving it S for free strengthens the interface being tested.

The exact classification is:

1. For 0 <= R < 1/2, recovery needs no parity checks.
2. For 1/2 <= R < 1, recovery is possible if and only if the binary matrix
   obtained by appending the all-ones row to H has column rank N.
   Consequently the minimum is exactly N-1 parity checks.
3. For R >= 1, recovery is impossible for every H, including the matrix
   revealing all N coordinate parities.

The endpoints concern a closed error promise. At R=1/2 the first obstruction
already applies, and at R=1 the second applies. When N=1 the exact sum is
the unknown coefficient, so the classification is intentionally restricted
to N >= 2.

## Below half a unit

Distinct integer vectors have coordinate distance at least one. Their closed
radius-R boxes are disjoint when 2R<1. Rounding each y_i to its nearest
integer therefore recovers c, without using S or H.

## Necessity in the middle interval

Suppose the augmented matrix has rank less than N. It has a nonzero binary
kernel vector v. The all-ones row implies that v has even weight 2k, with
k>=1. Partition its support into disjoint sets A and B of size k.
Let c and d be the zero/one indicator vectors of A and B, respectively.

Then c and d are distinct, have the same exact sum k, and have the same
syndrome because c-d reduces to v modulo two. For y=(c+d)/2, both errors
are at most 1/2. Thus the same complete observation admits two answers for
every R>=1/2. The ambiguity uses nonnegative coefficients and a known sum;
it does not depend on cancellation between large signed inputs.

No choice of decoding algorithm can distinguish that pair. This is a
worst-case information obstruction, rather than failure of the implemented
decoder or a numerical search.

## Sufficiency in the middle interval

Suppose the augmented matrix has rank N. The supplied syndrome, together
with S mod 2, determines the full coordinate parity vector r=c mod 2 by
binary linear algebra. For a fixed parity r_i, consecutive possible integers
are two apart. Since R<1, at most one of them is within R of y_i.
The promise supplies existence. Recover every coordinate this way.

Equivalently, if c and d were two candidates, their difference would be
even in each coordinate and have absolute value at most 2R<2. It must be
zero. This argument covers arbitrary real observations and all integer
magnitudes, not merely the rational bounded domain of the implementation.

The augmented matrix has at most m+1 independent rows, so m>=N-1.
Taking the first N-1 coordinate parities attains equality: the last parity
is S minus their sum, modulo two. Dense linear checks cannot use fewer
bits than these coordinate checks in this fixed-sketch model.

## The unit-radius obstruction

Take c=(0,2,0,...,0), d=(2,0,0,...,0), and y=(1,1,0,...,0).
Both coefficients have sum two, every coordinate parity agrees, and the
maximum error is exactly one. Every binary-linear syndrome therefore
agrees as well. Recovery fails for every R>=1.

## Consequence for a precision-saving proposal

The selected construction retains an analytic integer-recovery obligation.
Its selected review and zxv's PR6062 discuss strict half-unit recovery.
The proposed changed contract here grants an exact sum and seeks to relax
the uniform absolute-error tolerance using a small fixed parity sketch.
The theorem rules out a sublinear number of checks for that unrestricted
coefficient interface as soon as the allowed error reaches 1/2. It does
not bound the cost of computing N-1 checks or prove that they are affordable.
The result fixes the target for such a proposal before implementation work.

This is not a lower bound for integer multiplication. Actual convolution
coefficients can satisfy additional restrictions, and a caller may provide
other information. Sparse or probabilistic errors, adaptive checks, nonlinear
checks, odd moduli, relative-error contracts, and stronger exact measurements
are different interfaces. None is excluded. No selected assumption is
discharged and no new kappa is claimed.

## Evidence and background

The proof uses standard binary linear algebra and lattice separation. Those
methods and coding-theoretic ideas are not claimed as new. The contribution
is this sharp changed recovery contract and its explicit coefficient
ambiguities, with an attaining decoder, in the present research programme.
The selected source and PR6062 supply context rather than mathematical
premises. PR6182 studies a deterministic rounded native inverse and selected
coordinate tags; its rounded map and collision families are not used here.

The checker enumerates every binary row space through N=6 and independently
tests equal-weight zero/one coefficient pairs. Unique reduced row forms and
the Gaussian-binomial count establish the finite inventory. A separate
bounded decoder uses elimination. Closed-boundary fixtures, omitted-check
ambiguities, unit-radius ambiguities and invalid inputs are tested under
ordinary and optimized Python. These finite checks corroborate the written
all-input proof; they do not establish its infinite quantifiers.
