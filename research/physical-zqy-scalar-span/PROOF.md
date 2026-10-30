# Physical scalar-span separation at every positive tensor width

THU New Media Research Center (@thu-nmrc), with substantial OpenAI Codex
assistance. Apache-2.0. Event and history semantics follow Mark/Matarener's
[#5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427); native words
and phase conventions retain the source authors listed in README.md.

## 1. Precisely the interface being tested

Fix the literal inputs in SOURCES.json: Cao Yifan's final #4610 forward and
backward words, and Dillon's #5402 backward coupled-provider word. All 632
original input fields are independent. Owned entry fields are also independent
until the literal word clears them. No new helper relation is imposed.

For each word, collect every nonzero field version immediately after an event
at which that field occupies the unique full nine-axis frame. Grant retention
of every such version over the entire execution, even past the intended exit.
The grant ignores its ordinary storage cost and chronology, making an
exclusion stronger within this grammar. Different versions may be combined
with arbitrary complex scalars, possibly depending on tensor width f.

Write Y for original fields L112 through L223. A pure-Y observation is any
linear field expression depending only on these 112 original fields. Its
coefficients need not be identity operators. The target b=Z Q Y in the
#5415/#5419 interface is relevant because it is a nonzero pure-Y observation
when its current Y=Dy is referred back to this call's input. The statement
below concerns direct scalar combinations of retained full-frame versions.

**Theorem.** At every integer f>=1, for each of the three frozen words, the
complex scalar span of the granted versions contains no nonzero pure-Y
observation. This includes width-dependent complex scalar coefficients.

**Boundary.** Versions are not independently preprocessed by arbitrary free
left monomial maps before combination. Such a module closure, partial-frame
versions, changed words, new paid queries, supplied observations, different
providers and caller-level changes remain outside the theorem. In particular,
this does not prove that every endogenous ZQY observer is impossible.

## 2. Literal phase algebra

For a nine-bit invertible binary map G, the retained native convention is

    K_G |x> = i^{q_G(Gx)} |Gx>,
    Q_G = I + G^{-T} G^{-1},

where q_G has diagonal coefficients (Q_G)jj in Z/4 and off-diagonal
coefficients 2(Q_G)ij. `monomial.native` evaluates all 512 signed columns.
Composition, inverse and complex conjugation retain these columns literally.
For a backward warp the operator is the inverse transpose of the forward
operator, hence its complex conjugate, not a permutation with discarded phase.
The separately implemented phase audit compares 147,456 native signed columns
and 36,864 product columns with the retained Clifford evaluator.

Every native map and every product used here sends |0> to |0> with coefficient
one. Thus projective aliases in this set cannot hide a nontrivial global phase.
The 72 native labels contain 58 distinct signed operators. Across the three
replays, including inverse/conjugate products, there are exactly 215 operators
A0,...,A214, with A0=I. Each is lifted as the SAME one-column operator on all
f columns. Independent per-column controls are not silently granted.

A literal logical row is

    sum_{input r, operator j} c[r,j] A_j^{tensor f} input_r.

Scalar ADD/COPY/CLEAR and scale events act exactly on these rows. Paid climbs
change only the frame. Warps left-multiply by the actual signed operator.
All recorded versions occupy a common invertible physical full-frame map;
removing that common map preserves linear dependence and the input-support
property. Forward and raw backward frames are treated in their respective
conventions. The source frames and event order are checked during replay.

## 3. Exact group-coordinate projection ranks

Temporarily regard the 215 distinct signed operators as formal coordinates.
Let V be the version span and let pi delete all Y coordinates, retaining X,
all original helpers and all owned entry coordinates. Exact Fraction
elimination gives:

| Frozen word | Full-frame versions | dim V | dim pi(V) |
|---|---:|---:|---:|
| #5402 backward | 4,891 | 546 | 546 |
| #4610 backward | 5,019 | 554 | 554 |
| #4610 forward | 4,968 | 554 | 554 |

These are exact rational ranks, not floating tolerances. Rank is unchanged by
extension to C. Since the two ranks agree, pi is injective on V. Appending the
original pure-Y identity row increases each rank by one, so the checker can
detect a supplied observation. Actual operator identities must still be
handled; distinct one-column operators are not necessarily linearly independent.

## 4. Width one: a real physical relation, with a separate rank argument

The 215 actual one-column matrices have rank exactly 214. There is an exact
four-term relation in the deterministic replay enumeration:

    A157 + A51 - A156 - A49 = 0.

The verifier checks this equality at every matrix coordinate. A changed
absolute phase breaks it. A rank-214 minor modulo p=998244353 under
`i -> 911660635` proves a rank LOWER bound over Q(i). The exact displayed
relation gives the matching upper bound, so the remaining 214 matrices after
eliminating A157 form a C-basis.

Substitute A157=A156+A49-A51 in every version. In this physical quotient,
modular elimination of the non-Y projection gives lower bounds 546,554,554.
The exact ranks in section 3 give upper bounds of the same sizes for the
entire quotient version spaces. Projection rank cannot exceed the rank of
the space. Therefore the actual width-one projection is injective in all
three cases. This excludes nonzero pure-Y observations at f=1.

No conclusion is obtained merely from modular nonmembership. A rational
solution can have a denominator divisible by the test prime; that shortcut
would be invalid. Here modular computations certify nonzero minors only,
and exact rational upper bounds complete the argument. An additional,
separately implemented exact rational physical-quotient audit corroborates
these ranks without modular inference.

## 5. Width two and all larger widths

For the actual signed columns, form the Hermitian Hilbert-Schmidt Gram
matrix

    H_ij = Tr(A_i^* A_j),
    G_ij = H_ij^2.

The square is literal, not an absolute-value square: G is the Gram matrix of
A_i tensor A_i. Entries are Gaussian integers. Modulo p=1000000009 with
`i -> 569522298`, the 215-by-215 matrix has full rank and determinant
298401053. Thus its Gaussian-integer determinant is nonzero, and the 215
literal tensor squares are C-linearly independent. This finite certificate
uses no large tensor matrices or numerical singular-value threshold.

For f>2, apply the linear functional ell(T)=<0|T|0> to each of the final f-2
operator tensor factors. Every A_j has ell(A_j)=1. A putative relation among
A_j^{tensor f}, with any width-dependent coefficients, would therefore give
the same relation among A_j^{tensor 2}. Independence at width two makes all
coefficients zero. Hence these 215 operator lifts are independent at every
f>=2. Section 3 is consequently the actual physical rank computation at
all such widths. Together with section 4, this proves the theorem.

## 6. Consequence and remaining construction work

This resolves the actual-phase scalar-span question left open by #5427's
formal-word native test, including its width-one check. It does not copy
that predecessor's caller-level or paid-response-reuse conclusions into a
stronger grammar. It does not change a paid or productive histogram, install
a supplier, improve kappa or audit the multiplication framework.

A constructive continuation must change an explicit premise. The smallest
nearby one is to allow the concrete Z-ABI monomial maps on separately retained
versions, then prove a phase-correct pure-Y witness at the actual current-Y
cut. Another is a changed native schedule that saves pure Ry before Dx is
mixed in. Such constructions must retain all independent input directions,
owned returns, lifetime and the complete observer/termination bill.

## 7. A separate concrete Z-ABI left-image theorem

The constructive continuation also tests a larger, explicitly finite family
on the #5402 backward history. Let Kp_i be its 112 physical port normalizers
and Km_a its eight physical mode normalizers. In addition to no preprocessing,
grant each retained version any ONE left image from

    T = { I, Kp_i, Km_a, Km_a^{-1} Kp_i }.

There are 1,017 listed entries and 1,012 distinct signed maps; seed inverses
already occur among the seeds. This is a bank of allowed left images, not
closure under arbitrary products of its generators. Each version may receive
its own allowed image before scalar combination. Each selected one-column
map is lifted identically on all f columns; per-column choices are outside
this finite family.

The source ABI has

    Z = diag(Km_a^{-1}) M^T diag(Kp_i) / 2,
    W = diag(Kp_i^{-1}) M diag(Km_a) / 2,
    M^T M = 56 I8,   ZW = 14 I8.

Thus its termwise composite maps Km_a^{-1}Kp_i are included. The target b is
nonzero for independent native-return Y=Dy. A later caller Y contaminated by
X is not silently identified with this pure-original-Y target.

`abi_closure.py` authenticates the two additional pinned JSON inputs and
checks the normalizers literally, with phases. Each seed is a real signed
orthogonal linear permutation K|x>=i^{phi(x)}|Gx> satisfying

    phi(x) - wt(x) + wt(Gx) = 0 mod 4.

The full-frame kernel is R[y,x]=alpha*(-i)^{wt(x xor y)}. Orthogonality and
the displayed signed-weight relation give KR=RK, including phase. Hence
physical preprocessing and logical left multiplication agree:
R^{-1}KR=K. The same holds for the raw backward common frame and seed
products. These normalizers are not admitted as free merely from a frame tag.
The separate checker verifies 61,440 seed/address conditions.

Only 59 of the 215 signed operators occur in the backward provider's full-frame
versions. The literal products T A, over the 1,012 maps T and these 59 operators
A, are all 59,708 distinct maps. All have zero-state coefficient one, so they
are pairwise nonproportional. No left-image support collision occurs.

Consequently the translated spaces T V form a direct sum in formal product
coordinates. Their non-Y projections form the same direct sum: left multiplication
does not change the original input owner. The exact base 546/546 projection
certificate therefore makes the entire finite left-image projection injective.

For completeness, a classical separating-functional argument supplies a
rigorous width bound without a huge Gram computation. For each pair of
nonproportional vectors v_i,v_j choose a linear functional ell_ij with
ell_ij(v_j)=0 and ell_ij(v_i)!=0. The tensor product over j!=i is a functional
on tensor degree N-1 that vanishes on all v_j^{tensor(N-1)} except v_i.
Thus N pairwise projectively distinct matrices have independent tensor powers
at degree N-1. The common zero-state anchor extends independence to every
larger degree, as in section 5. Apply this with N=59,708.

**Fixed-ABI theorem.** At every f>=59,707, the span of the granted 1,012 left
images of every retained backward-provider full-frame version contains no
nonzero pure-Y observation. Arbitrary width-dependent complex scalar
coefficients are allowed. In particular, this fixed family cannot supply b
by an identity valid at all widths, or throughout a consecutive infinite tail.

No small-width nonmembership claim is made for this enlarged family. Further
products, arbitrary monomial left maps, new paid observations, changed native
words and different input/return contracts remain outside the result. The
checker consumes the primary exact rank certificate; it is not a substitute
for replaying that certificate. This extension changes neither paid jobs nor
productive targets and supplies no new kappa.
