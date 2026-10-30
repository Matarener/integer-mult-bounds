# Residue-assisted Gaussian coefficient recovery

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
This is an informal proof and a source-bound uniform finite-box certificate,
not a new formal-kernel audit or an all-size fast multiplication theorem.

## 1. The positive result and its exact scope

**Theorem 1 (hybrid recovery).** Let a and b be nonempty finite nonnegative integer
coefficient arrays, of lengths L and K, and let c be their ordinary
convolution. Fix k ≥ 1 and M = 2^k. There is an explicit procedure which
computes all residues c_j mod M with one paid multiplication of packed
integers of lengths at most

\[
 k+(L-1)w,\quad k+(K-1)w,\qquad
 w=2k+\lceil\log_2\min(L,K)\rceil.
\]

If, in addition, a numerical computation supplies real centers x_j and
certified radii R_j with |x_j−c_j| ≤ R_j < M/2, the procedure recovers every
c_j exactly by rational floor/ceiling arithmetic. No direct convolution or
original-input product is required to supply the answer. The exact child
is an additional charged computation, not a free congruence oracle.

**Theorem 2 (instantiated all-input certificate).** On Mason Hale's retained
source box (5,7,13), target box (8,16,32), α = 5, 64-bit digits and outward
interval grid Q = 448, the new program uses rounded payload precision
p = 192 and a 16-bit residue lane. For **every pair of nonnegative inputs
of at most 14,592 bits**, declaring that supported width, it returns their
exact product. The paid residue multiplication has both inputs bounded by
9,096 bits. Every Gaussian stage, pointwise product, inverse CRT ordering,
normalization and carry operation is actually executed in the reference.

For comparison, the least p accepted by the **same frozen uniform error
certificate** without a residue lane is 208. The original package chose
p = 256; its already available 48 spare bits are not credited to the new
modular mechanism. The new mechanism buys a further 16 payload bits at the
explicit price of the additional exact lane. Neither 208 nor 192 is claimed
to be an information-theoretic minimum or optimal for other certificates.

Theorem 1 is universal in the array lengths and interval data. Theorem 2
is universal over inputs in one supported box, using a regenerated finite
operator certificate. It does not extend the Gaussian backend to arbitrary
outer geometries or establish a new asymptotic exponent.

## 2. Exact low-residue convolution without slot carry

Put A_i = a_i mod M and B_i = b_i mod M and m = min(L,K). Form

\[
 A_*=\sum_{i=0}^{L-1} A_i2^{wi},\qquad
 B_*=\sum_{i=0}^{K-1} B_i2^{wi}.
\]

**Lemma 3 (slot bound).** The coefficient
d_j = Σ_(i+v=j) A_i B_v satisfies

\[
 0\le d_j\le m(M-1)^2 < m2^{2k}
 \le2^{2k+\lceil\log_2m\rceil}=2^w.
\]

Consequently the base-2^w expansion of the exact product A_*B_* has
digits exactly d_j: distributivity gives Σ_j d_j2^(wj), and every
coefficient is already a legal digit. There is no carry into another slot.
Extracting slot j and reducing modulo M therefore gives c_j mod M, since
reduction modulo M respects every summand and product. This proves the
residue assertion without requiring pairwise coprimality between M and
any Gaussian source length. ∎

**Lemma 4 (child size).** Since 0 ≤ A_i < 2^k, the packed number satisfies

\[
 A_*\le(2^k-1)\sum_{i=0}^{L-1}2^{wi}
 <2^{k+(L-1)w}.
\]

For L = 1 this is immediate. For L > 1, divide by the highest power and
bound the remaining geometric tail by 1/(1−2^(-w)); the result is strictly
below 2^k because w ≥ 2k and k ≥ 1. Equivalently, its highest nonzero
slot has at most k bits and all lower bits lie below that slot. This
proves the bit-length bound. The proof for B_* is identical. ∎

At L = K = 228 and k = 16, w = 32+8 = 40 and each child input has
at most 16+227·40 = 9,096 bits, strictly below the declared 14,592-bit
outer inputs. In the maximal-input test this bound is attained. Zero
operands, leading zeroes and partial final digits only shorten the
actual packed operands. The algorithm pads to the supported declared
width; it does not claim strict shrinkage relative to every tiny operand's
actual bit length. Smaller actual problems need their own base cases in
an all-size recursive algorithm.

## 3. Recovery in a residue lattice

**Lemma 5 (unique lift).** For M > 0, r ∈ {0,...,M−1} and a closed interval
[x−R,x+R] with 0 ≤ 2R < M, there is at most one integer congruent to r
modulo M inside the interval. Any two such integers differ by a nonzero
multiple of M, so their distance is at least M, larger than the interval.
If the true coefficient c lies in the interval and c ≡ r mod M, it is
therefore the unique one. ∎

The constructive decoder calculates

\[
 q_- = \left\lceil\frac{x-R-r}{M}\right\rceil,\qquad
 q_+ = \left\lfloor\frac{x+R-r}{M}\right\rfloor.
\]

It requires q_- = q_+ and returns r+Mq_-. Rational integer floor/ceiling
arithmetic handles negative centers and coefficients as well. Equality
2R = M is deliberately rejected: a closed interval can then contain two
representatives. Lemma 3 supplies the true class; Lemma 5 completes
Theorem 1. A numerical interval is **not authentication for a residue**:
different, incorrect classes can have representatives in the same broad
interval. The exact lane's correctness is essential, and the controls
explicitly demonstrate this trust boundary instead of claiming that all
corrupted residues can be detected by numerical recovery alone.

## 4. Reusing the original matrices at a lower payload precision

The unmodified backend prepares outward interval matrices at Q bits.
Their entries, Gaussian cutoffs, Neumann terms, residual operator enclosure,
phase enclosures and selected coordinate maps depend on s,t,α,Q, not on
the rounded payload precision p. Only admission and runtime quantization
depend on p. The source inspection establishes that separation; the replay
also rebuilds all three source lines freshly at p = 192 and p = 208 and
compares their matrices and error certificates exactly.

For a line of power-of-two target length t, the source certificate has

\[
 U_i(p)=A_i2^{-p}+B_i,\qquad
 A_i=2(\log_2t_i+2)2^{2\alpha^2}.
\]

There are two matrix extractions and log₂ t_i normalized butterfly levels;
each contributes 2·2^(-p), amplified once by 2^(2α²). Every remaining
outward-enclosure and direct-operator residual term is independent of p.
Thus, from an existing certificate at p₀,

\[
 U_i(p)=U_i(p_0)+A_i(2^{-p}-2^{-p_0}).
\]

The new precision_view checks p > 100, α² < p ≤ p₀, the original integer
and θ domains, the Q > p+2α²+32 guard and the residual bound at the new p.
It copies the line's control fields while sharing the unchanged prepared
matrices. It does not modify the original source or accept unchecked
extrapolation to a larger p. This proves the precision-transfer formula
within the checked domain, rather than treating an arbitrary mutable
object as a certified Gaussian operator.

## 5. Complete normalized-output error and both source factors

Retain the original source transform U = RF, where F is the normalized
negative Fourier map on the CRT product group and R multiplies each
frequency index by its retained invertible target residue. The opposite
map is U⁺ = RF⁺. The source proof establishes F⁺R = R⁻¹F⁺ and
(Ra)(Rb) = R(ab), so

\[
 U^+((Uu)(Uv))=F^+((Fu)(Fv))=(u*v)/S^2,
 \qquad S=\prod_i s_i.
\]

Both factors of S remain. Digit embedding uses u_j = a_j2^(-b−2) and
v_j = b_j2^(-b−2), so the exact recovery scale is

\[
 L_{\rm rec}=S^2 2^{2b+4}.
\]

This is the predecessor's normalization, not a new Fourier identity. The
new decoder changes its allowed recovery radius, not these factors.

Let E(p) = Σ_i U_i(p). Exact source-axis operators are contractions, so
the tensor errors add once over actual axes; they are not reamplified by
each later axis's internal Gaussian scale. The original certified inputs
are in the quarter disk. E(p) < 1/100 keeps forward results below .26;
their rounded product and opposite-stage inputs stay inside the admitted
unit disk. The preserved numerical backend establishes all internal
extraction/disk conditions on this margin. Its local product error is
at most 2·2^(-p)+8·2^(-Q). The complete normalized convolution therefore
has error at most

\[
 3E(p)+2\,2^{-p}+8\,2^{-Q}.
\]

The uniform recovered-coefficient radius is

\[
 \mathcal R(p)=L_{\rm rec}
 [3E(p)+2\,2^{-p}+8\,2^{-Q}].
\]

Ordinary recovery requires R(p) < 1/2; the new sufficient test is
R(p) < 2^(k−1). The actual run also checks its smaller data-dependent
radius against the uniform bound, verifies that zero lies in each scaled
imaginary interval, and enforces the elementary nonnegative coefficient
bound before carrying. No direct reference answer supplies an interval
center, coefficient or digit.

For the frozen three-axis box, ΣA_i = 36·2^50. All terms in R(p) are
exact rationals. The computed certificate gives

\[
 .333<\mathcal R(208)<.334,\qquad
 21834<\mathcal R(192)<21835<32768.
\]

The test also checks rejection one payload bit below each admitted point.
Since the coefficient of 2^(-p) is positive, R(p) strictly decreases with
p. This establishes the least accepted p **for this fixed certificate and
frozen domain**, not a lower bound for other numerical methods.

## 6. Exact output, universal input coverage and the cost boundary

The source size is S = 5·7·13 = 455. At most 228 base-2^64 digits per input
give product degree at most 454. Therefore there is no cyclic wrap, CRT
orders every coefficient bijectively, and Lemmas 3 and 5 recover the
ordinary convolution in its original digit order. The carry recurrence

\[
 d_j=(c_j+q_j)\bmod 2^{64},\qquad
 q_{j+1}=\lfloor(c_j+q_j)/2^{64}\rfloor
\]

preserves positional value. Draining the remaining carry returns exactly
the product. Every input has digit magnitudes below 2^64, so the uniform
disk and error bounds hold for **all** pairs in the admitted 14,592-bit
range, including zero. This proves Theorem 2 using the regenerated finite
operator bounds and the preserved interval/backend proof premises.

The full arithmetic invoice is three complete Gaussian tensor transforms,
S rounded pointwise products, one exact packed multiplication, linear
packing/extraction and the final recovery/carry scans. For general digit
arrays the new modular lane has L+K packed input slots and L+K−1 extracted
slots. Their integer lengths and the exact multiplication's output size
are charged by w above. Preparing the Gaussian certificates is additional.
The Q = 448 enclosure arithmetic is unchanged; lower rounded payload
precision is not by itself a measured runtime or space reduction for
this dense interval implementation.

**Corollary 6 (sufficient whole-cost improvement).** In any fully priced
compatible implementation, if the reduction in the three transform and
pointwise-product costs from p₀ to p exceeds the **sum** of the packed
child cost, packing/extraction and added residue-lifting costs, the hybrid
has smaller total cost. This follows by adding the displayed complete
invoices. No such inequality is asserted here for the selected suppliers.
The new result supplies the exact recovery/size contracts needed to
evaluate it; it does not supply an unpriced oracle or a new κ.

The finite replays check 21,168 modular convolution cases, six fresh source
precision constructors, and nine complete Gaussian products in 1D/2D/3D.
All 1,485 coefficients are independently checked only after recovery.
The actual radii of all nine products exceed 1/2, so the old ordinary
radius guard rejects these reported intervals; every new modular radius
is admissible. This is an executed changed recovery contract, not a claim
that no tighter ordinary certificate could succeed.
