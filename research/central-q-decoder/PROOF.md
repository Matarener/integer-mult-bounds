# Exact paid closure of the central-Q terminal

This is a constructive all-width decoder theorem and a source-bound implementation.
It closes the algebraic output interface. Its explicit additional Gaussian charges
are not funded by the previous whole-K p19 planning invoice, so it supplies no new κ.
No independent human review, Lean kernel audit or full multiplier admission is claimed.

## 1. Fixed contract and construction

Let V be a finite-dimensional complex Hilbert space. Let Q and D be invertible
operators with QD = DQ. Let C_1,...,C_m be explicitly executable invertible
ordinary recodings. Define P = C_m ... C_1, in chronological stage order.
The incoming terminal is the actual operator W = Q⁻¹ P D on an arbitrary input x.
There is no commutation hypothesis between Q and any C_j, or between two C_j.

**Theorem 1 (complete terminal repair).** Execute, in this chronological order:

1. Q on the terminal field;
2. C_m⁻¹, C_(m−1)⁻¹, ..., C_1⁻¹ on that field;
3. Q on the result.

The endpoint is DQx, and the additional Gaussian bill is two rank-one jobs per
owner, independent of m. Stopping before step 3 gives Dx with one rank-one job.
All unrelated original fields are preserved.

Proof. After the first step the field is PDx. The reversed inverse word gives
Dx. The last step gives QDx = DQx. Equivalently, with operator products acting
rightmost first,

    (Q P⁻¹ Q)(Q⁻¹ P D) = QD = DQ.

The inverse stage order is essential. This is a universal operator identity,
not an extrapolation from width-one tests. A Gaussian is paid at both occurrences
of Q; Q² being monomial does not permit commuting either Q past P.

The positive terminal PDQx needs only the ordinary inverse word. When all C_j
are involutions, as in the pinned whole-K construction, the inverse word uses
the same codes in reverse chronological order. It does not reverse individual
native erasures, borrow original helpers or reinterpret a coupled output as an
independent Gaussian target.

## 2. Actual native realization of each ordinary inverse code

The pinned PR #5464 root cube has 512 owners and a rational symmetric matrix K.
The checker reconstructs every entry of K² = I and Kᵀ = K. Each row has twelve
entries of magnitude 1/4 and sixty-four of magnitude 1/16; its absolute row and
column sums are 7. The actual normalized code is

    C = diag(L_i⁻¹) K diag(L_i).

The source input-Y and output-X words supply the actual L_i and L_i⁻¹.
Every word consists of an invertible binary permutation and a real linear sign.
The checker validates all 512 inverse pairs, rather than substituting an identity
normalizer or a commuting abstract code. Therefore C² = I and C is unitary.

At every positive address width f, apply each L_i independently to its f digit
columns and sum their phase exponents. Apply the scalar K coefficient once to
an entire field, not its f-th power. Adjacent lifted normalizers cancel, so the
same C² = I and unitarity statements hold at all widths. Fresh stages use the
explicit embedding (central axis 0, followed by their own 24 axes). The terminal
identity itself does not need freshness; only a separately claimed target-rank
invoice may need it.

To evaluate C in place, clear 512 owned fields; apply L to the main bank;
accumulate K times that unchanged bank into the owned bank; swap the banks;
apply L⁻¹ to the new main bank; clear the old bank. All source reads finish
before any source is replaced. There is no alias between owned and main fields.
Arbitrary initial owned contents are cleared explicitly, and all owned fields
return to zero. Other independent cohorts are untouched.

Per stage and per 512-owner cube this emits 38,912 scalar ADDs, 1,024 complete
normalizer maps, 512 field SWAPs and 1,024 CLEARs. Each complete normalizer map
is exactly two pinned P/D primitives. Peak owned storage is 512 fields and is
reused across stages and disjoint cubes. The recipe and fully expanded event
iterator bind all coefficients, owner indices, stage embeddings and clears.
The paid repair is 1,024 H1 jobs for a full-rank terminal cohort, or 512 H1 jobs
if its central target rank is dropped. These are extra charges beyond the caller.

This executable source adapter is bound to the emitted root cube. The universal
argument applies to any cube with the same proved interface; all-family physical
geometry and absolute-phase validity remain the pinned upstream proof's claims.
This package does not pretend to replay all 2,744 cubes or an entire p19 caller.

## 3. A literal alternative to recursive Q calls

For one digit bit the Gaussian is

    (a,b) ↦ (((1+i)a+(1−i)b)/2, ((1−i)a+(1+i)b)/2).

Apply it on each central bit, with all other coordinates and owners as spectators.
This gives Q_f = C_e raised to its f-fold tensor product. The inverse conjugates
the coefficients. `q_pass` executes this exact Gaussian-integer/dyadic rule and
retains absolute phases. A separate dense Hamming-distance formula verifies it
for widths 1 through 6.

If N is the total number of complex scalar cells in the cohort, the two Q passes
use fN two-cell butterflies. The one-pass option uses fN/2. They require no
external Gaussian oracle, but cost O(fN) scalar work plus actual arithmetic and
movement. The factor f is variable. This implementation is not a fixed finite
ordinary word and is not priced at zero in the κ calculation. No unit-cost
arbitrary-precision, constant-size machine word or fixed-tape tariff is assumed.

## 4. Exact precision and stable rounding

**Theorem 2 (exact dyadic grid).** Suppose the terminal input has Gaussian-integer
coordinates divided by 2^g. A full decoder with m whole-K code stages has every
prefix on a dyadic grid of exponent at most

    g + 4m + 2⌈f/2⌉.

For the one-pass option, g + 4m + ⌈f/2⌉ suffices.

Proof. Each scalar code coefficient has denominator dividing 16, so an entire
out-of-place stage, including partial sums, costs at most four fractional bits.
Signed monomial maps change none. For k central butterfly layers, every matrix
coefficient is ((1+i)/2)^k times a unit Gaussian integer. Since (1+i)^2 = 2i,
the coefficients have denominator dividing 2^⌈k/2⌉. This covers every partial
Q pass. Add the stage and Gaussian bounds in chronological order. A simpler
implementation may reserve g + 4m + 2f bits instead. Exact-grid claims do not
remove limb-operation or storage costs.

**Theorem 3 (energy and forward error).** Every complete code and Q layer is
unitary. At exact code-accumulation prefixes, the combined main/owned Euclidean
norm is at most √50 times the main input norm, hence less than 8 times it.
No factor 7^m is needed for this combined Euclidean bound.

Proof. A partial K accumulation has entrywise absolute row and column sums at
most 7. Its spectral norm is at most √(7·7) = 7, by Cauchy–Schwarz applied with
absolute row/column weights. The immutable source bank has norm M and the
partial owned bank has norm at most 7M. Combine them in quadrature. Signed
monomial maps and swaps preserve energy; clearing removes energy. At the end
of each code, KᵀK = I restores the main norm to M. Repeat stage by stage.
The bound starts after the explicit initial CLEAR of arbitrary owned dirt.

For a rounded implementation, use exact widened accumulators inside a code
stage and round once per final real/imaginary coordinate. Round once per
coordinate after each one-bit Q layer. If the output grid spacing is 2^−B,
round-to-nearest gives local Euclidean error at most √N·2^−B. There are
L = 2f + m such unitary layers, or L = f + m for the one-pass option. Therefore

    final error ≤ incoming error + L√N·2^−B.

Proof. Write each rounded layer as z_(j+1) = U_j z_j + e_j. Telescoping expands
the final error into transported e_j terms and the transported initial error.
Every suffix is unitary, so the triangle inequality gives the displayed bound.
For desired additional error ε, the exact sufficient check is
L²N ≤ ε²·2^(2B). This avoids any floating acceptance criterion.

A sufficient signed component payload reserves the fractional grid plus enough
integer bits for 8 times the input Euclidean norm, with sign and guard bits.
That norm may depend on problem size; this is not a constant-word claim.
The rounded implementation theorem describes a schedule, while the supplied
native sparse interpreter itself uses exact arithmetic. No complete caller
rounding, storage or tape audit is inferred from this decoder theorem.

## 5. The complete repair charge and the κ boundary

The inherited ideal whole-K p19 model has 19 negative cohorts per owner. Their
stage counts are 19, then two each of 1 through 9, totaling 109 code evaluations.
Repairing the whole word uses 38 H1 jobs per owner, compared with 218 for the
explicit naive strategy that repairs each stage separately. This saves 180
H1 jobs against that comparator, not against the selected multiplier.

The model's original rank-mass surplus is 18 per owner. Full repair changes it
to −20. Dropping one central target rank in each negative cohort costs 19 H1
jobs and loses 19 target ranks, again giving −20. Exact outward rational moment
checks reject both repaired profiles at the selected κ = 0.003027288235, the
open numerical-headroom claim 0.0030272882489783, and 0.00344412.

Among these two repair options the one-pass option always has the better
concave moment for 0 < t < 1: its improvement over full repair at target rank
r > 1 is 1 + (r−1)^t − r^t > 0. This follows by integrating t x^(t−1) over
[r−1,r], whose integral is strictly less than 1. Thus choosing some full repairs
cannot rescue the displayed model if all one-pass repairs already fail at the
same t. This comparison is scoped to these explicit repairs, not all callers.

The arithmetic pins an inherited planning inventory. It does not assert that a
complete p19 physical controller has now been emitted. The useful positive
result is the exact, fully charged terminal decoder; profitable assembly remains
open and is not hidden inside its hypotheses.

## 6. Attribution, overlap and limits

The two-sided inverse identity and unitary error telescoping are elementary
classical algebra and numerical analysis, not claims of new general theorems.
The contribution is their concrete native-code adapter, chronological emitter,
actual lifted sparse replay, precision schedule and fully charged comparison.

Credit THU New Media Research Center / PR #5464 for whole-K native data; Ali Romman
/ #5439 for odd-E8 geometry; Dugongue / #4929 and #5467 for preceding coded work;
Dillon Amburgey for the physical normalizers and coded caller; Cinna Davis / #4470
and Ryanson Jonathan / #4516 for the controller lineage; zxv for the unchanged
outward moment engine; Cao Yifan, Jacob Alan Sussman, Chris R / Clear1nsight and
the retained native, compiler and analytic contributors. The previous local
programmable-stage release is an unpublished local predecessor, not a fabricated
GitHub PR. Its payload was preserved.

The refreshed #5464 terminal-support appendix has head
fc5e6f611eb7a1121be23d6748ecceb61533041e. It excludes a fixed finite ordinary
postdecoder on its stated distinct-fresh single-cohort grammar. The present
construction pays Gaussian work (or uses width-dependent butterflies), so it
respects that boundary. Overlap review was bounded, not a priority guarantee.
New implementation and exposition: Dugongue with substantial OpenAI Codex
assistance from one solo worker, Apache-2.0.
