# Independent normalization, recovery and cost audit

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. The Gaussian tensor and physical Fourier arguments remain credited
to Jose Manuel and their retained contributors; the CRT implementation and
argument remain credited to Tekalign. This note checks their proposed outer
composition, under their stated contracts.

The proposed normalization and eventual recovery margin are correct. Three
details are essential: the final factor is S²; repeated target sizes need a
distinct prime for every source axis; and scaled coefficients cannot remain
in the Gaussian disk format. The root recurrence must also use a strict
exponent above both the complex-moment endpoint and the ordinary routing
exponent. None of those obligations is discharged by a finite numerical
example.

## Exact source boundary

The default checker authenticates all 35 unique regular files in the immutable
outer proof-reference bundle, its archive and its manifest. It checks literal
source facts for TensorPlan, the CRT width override, normalized Fourier maps,
the scalar continuation and the retained prime-gap premise. No source module
is imported. The source review uses PR3935 at
f687fa171ef760fa98a4be1289717b47dd4ee0b3 and canonical
12fa8c5c844be21bfefb38a19503fbd867a11244. The nine cited source blobs and their
SHA-256 values are listed in outer_check.py and its receipt. These are source
references, not a claim to freeze or execute their complete import closure.
Seven of these independently pinned blobs also occur in the 35-file bundle;
the optional Git comparison additionally checks the tensor word adaptation
and arithmetic note.

The actual TensorPlan API in tensor_plan.py, lines 112–128, has
axes=D−1, dimensions=D and d=D+1, with restoration exponent
gamma=D(2u+ceil(log2(32p))+1). Its final target axis is always the long axis.
The tensor engine's boundary procedure takes the half-disk input, restores
by the exact gamma shift, and checks the complete disk-grid output. Its
opposite flag conjugates both boundaries. The cited tensor proof gives
the endpoint R F± with both Fourier maps divided by S.

The CRT source, PROOF.md lines 8–25 and crt_converter.py lines 263–266, maps
coefficient k to coordinates mu_i k mod s_i, where
mu_i=(product of preceding s_j)^(-1) mod s_i. This is a group isomorphism,
so it carries cyclic convolution to tensor convolution. The converter accepts
an explicit opaque record_bits override on the inverse. Passing its default
Gaussian record width after changing the coefficient representation is not
an admissible implicit conversion.

The synthetic Fourier source explicitly uses two normalized transforms,
F+F−=I/M, and gives an exact whole-transform rounded endpoint. The new root
must be bound at that actual exact-grid interface. Merely replacing its
printed exponent does not replace the retained ComposedRoot implementation.
The separate global binding and outer construction own that replacement.

## Shape and distinct source primes

For sufficiently large input bit length n, put b=ceil(log2 n), p=6b and
m=ceil(n/b). Choose the power of two T with

    4n/b <= T < 8n/b.

Write L_T=log2 T, D=floor(p^(997/1000)), d=D+1 and
ell=ceil(L_T/D). Choose D target widths in {ell−1,ell}, summing to L_T,
with the final width ell. This is possible: D ell−L_T is an integer between
zero and D−1, and specifies the number of short axes among the first D−1.
Eventually ell−1 is positive and exceeds every required logarithmic
microbox/halo width. These are eventual statements, not admissions at small p.

For every axis choose a distinct prime

    (1−1/(2d)) t_i < s_i < (1−1/(4d)) t_i.

This stricter interval implies both actual TensorPlan ratio guards:
4d(t_i−s_i)>s_i and (2d−1)(t_i−s_i)<s_i. It also gives

    S/T > (1−1/(2d))^D >= 1−D/(2d) > 1/2.

Thus S>T/2>=2n/b>2m−2, so the product of the two m-digit polynomials has
no cyclic alias. The source lengths are odd, pairwise coprime and below
their target lengths.

One short-interval prime is not enough when a target size repeats. Retain
the Baker–Harman–Pintz exponent 21/40 as an analytic prime-gap premise.
Subdivide each required interval into D disjoint pieces of comparable
length Theta(t_i/(dD)). Eventually each piece is longer than the permitted
prime gap, because

    t_i^(19/40)/(dD) -> infinity.

Indeed log2(t_i)=Theta(p^(3/1000)), whereas log(dD)=O(log p). This provides
at least D distinct primes for each repeated target size. The two intervals
for t and t/2 are disjoint. Trial division, interval scanning and selection
use poly(t_max,p) bit operations and storage; that is 2^o(p). The analytic
prime-gap constant and the other production conditions give an unspecified
finite cutoff. This note does not claim an effective practical cutoff.

## The three normalized endpoints

Use the tensor group G=product_i Z/s_i Z, of order S. Define

    F±x(k) = S^(-1) sum_j exp(±2pi i sum_i j_i k_i/s_i) x(j),
    R x(j) = x((t_i j_i mod s_i)_i),
    A± = R F±.

Each t_i is a unit modulo s_i. Substitution in the Fourier sum gives
F+ R=R^(-1) F+. Pointwise multiplication commutes with R. Therefore

    A+((A−x)(A−y))
      = R F+ R ((F−x)(F−y))
      = F+((F−x)(F−y))
      = (x * y)/S².

The final step follows from character orthogonality: the three normalized
maps contribute S^(-3), and the character sum contributes S. No additional
R or reflection remains. Interchanging the signs everywhere gives the
same convolution identity.

The checker evaluates every bilinear input/output coefficient for four
finite groups, using exact integer arithmetic in cyclotomic quotient rings.
It has 12,788 coefficient cases. Mutants using S rather than S², omitting
the final R, or using the wrong final Fourier sign are distinguished.
This finite check supplements the displayed all-group derivation.

## Error, format and exact integer recovery

Scale each base-2^b input digit by 2^(−b−2); each input has complex norm
strictly below 1/4 and lies on the p grid. Write h=2^(−p) and retain the
source-bound three-call Gaussian error

    E = 2^gamma (D p² + 4 sqrt(2) M + 22 + 2D) h,
    M=T/r, r=2^ell.

The exact normalized transforms contract sup norm. If the first two
computed transforms have errors at most E, their rounded pointwise product
w=Q_p(tilde a tilde b) obeys

    ||w|| <= (1/4+E)² + 2h,
    ||w−ab|| <= E/2 + E² + 2h.

The term 2h safely dominates the complex error of componentwise p-grid
truncation. When the first displayed bound is below 1/2, the third tensor
call is admitted. Applying its error bound and the contraction of A+ gives

    ||tilde z − (x*y)/S²|| <= 3E/2 + E² + 2h.

Consequently sufficient exact-recovery conditions are

    E <= 1/256,
    (1/4+E)²+2h < 1/2,
    S² 2^(2b+4) (3E/2+E²+2h) < 1/2.

After exact multiplication by S² 2^(2b+4), round each component to its
nearest integer. The real component is the exact digit convolution; the
imaginary component is zero. The strict inequality avoids all tie choices.
Then apply inverse CRT with the declared integer record format and perform
ordinary base-2^b carries in coefficient order.

For clarity, a safe implementation widens before scaling. Since
S<T<=2^(b+3) and the restored tensor output has modulus below one, signed
component width p+4b+12 suffices for its exact scaled p-grid numerator.
Rounding divides that integer numerator by 2^p; the resulting integer
coefficient is below m(2^b−1)²<2^(3b), so signed width 3b+1 suffices.
Use inverse CRT with record_bits=3b+1 for the recovered real coefficient;
check that every rounded imaginary component is zero before dropping it.
Do not treat the scaled value as a p+2-bit disk-grid component. Retain a fixed
number of widened scalar words and pay each copy, shift, multiplication,
rounding scan and erasure. The finite checker tests scalar recovery, inverse
CRT and carries on 27 complete small inputs; it does not execute these
physical tape operations.

The outer join uses a convenient more conservative encoded gate. Put
H=D p²+32+2D, so E<2^gamma T H h. For b>=8, T<=2^b and E<=1/256 imply

    S²2^(2b+4) (3E/2+E²+2h)
      < S²2^(2b+4)(2E+2h)
      < 64 H 2^(gamma−b).

Thus b>=gamma+ceil(log2 H)+9 makes the recovered error strictly below 1/8.
It also gives E<1/256 and p>=gamma+A+ceil(log2 H)+8, the actual tensor
error admission, since A=log2(T/r)<=b and p=6b. The checker checks the exact
algebra and three finite instances of this gate; those instances likewise
are not production tensor plans.

Here is an explicit sufficient eventual arithmetic bound. For
alpha_G=floor(p^(1/1000)), u=alpha_G² and D=floor(p^(997/1000)),

    gamma/p <= 2p^(−1/1000) + (log2 p+7)p^(−3/1000).

For p>=2^7000, divide the logarithm into intervals
1000q<=log2 p<1000(q+1), q>=7. The right side is at most

    2/2^7 + 8007/2^21 = 40775/2097152 < 1/12.

Both terms decrease from one interval to the next. Hence gamma<=b/2.
For b>=32,

    D p²+22+2D <=216b³+12b+32<=2^b,
    M<=T<8*2^b/b<=2^b,
    E<7*2^(gamma−5b),
    S²2^(2b+4)<2^(4b+10)/b².

The exact checker verifies the recovery inequalities for b=32 and 33
under this sufficient gamma cap. For b increasing by two, the three
positive scaled error terms decrease by factors at most 1/2, 1/1024
and 1/16, before the additional b^(-2) decrease. Thus the bound holds for
all larger b. These two arithmetic witnesses are not production tensor
plans. The enormous p threshold here addresses this error estimate only;
prime supply and every other retained production admission still apply.

## Complete outer bill and strict exponent gaps

Put V=T Theta(p)=Theta(n). Charge three full Gaussian tensors and three
CRT conversions, including their padded boxes, all gathers, coefficient
catalogues, numerical validation, parent copies, child-return consumption,
scratch erasure and head return. The CRT bill includes three full-support
router calls and six padding passes, not two conversions or two routes.
Source setup and fixed native compilation/storage remain charged once per
fixed constructed instance.

The root recurrence uses

    C=0.001730980255989036959962,
    tau=332353/332929,
    sigma=0.99826995, eta=10^(−6), alpha_H=0.99827.

One has 1−C<sigma and tau<sigma<alpha_H. The source recurrence exponents
(1−eta)sigma+eta tau and (1−eta)sigma+eta are both below alpha_H.
The complete finite moment at C and its monotonicity are inherited from
the separate joint-bound admission; this checker does not re-prove that
supplier's all-size restoration. Using sigma=1−C would violate tau<sigma.

With epsilon=997/1000, the complete Fourier exponent is

    Phi=1−epsilon(1−alpha_H)=0.99827519.

The retained full-support router has
beta=41544341/41616125<Phi. The Gaussian work after its separate logarithmic
allowance has exponent 0.9981<Phi. Positive gaps absorb the router's extra
logarithms separately from the Gaussian logarithms. The coefficient-page
and prime setup is poly(t_max,p)=2^o(p), which the exponential packet pays.

For pointwise products and final S² scaling, retain the physical scalar
word product's Karatsuba recurrence, with its source restoration and fixed
leaf implementation. Since 3^5<2^8, log2(3)<8/5. A fixed number of O(p)-bit
products per coefficient therefore costs O(S p^(8/5))=O(V p^(3/5)).
This includes exact real/imaginary products, the final scale and their
outputs. Nearest-integer extraction and streaming carries cost O(Sp).
This scalar exponent is strictly below Phi; quadratic per-coefficient
multiplication would not fit the claimed bill and cannot be substituted.

Under the named source and replacement-root contracts the complete result is

    O(n (log n)^Phi loglog n), with O(n) working space

plus fixed source/native storage and the stated high-water backing convention.
Because

    1−Phi−1/580 = 1949/2900000000 > 0,

the extra loglog n fits within the strict power gap, giving the conditional
target O(n (log n)^(1−1/580)). This is a source-relative written implication,
not a finite-execution proof of a new multiplication theorem.

## Reproduction and limits

Run the checker with the standard library:

    python3 -I -B research/complex-pooled-full-admission/outer_check.py
    python3 -I -O -B research/complex-pooled-full-admission/outer_check.py

Optionally pass --source-repo /path/to/checkout to authenticate the nine
cited blobs through their exact Git commits, and --out /path/to/receipt to
save the result. The published evidence was generated with that additional source
check. All mathematical checks use explicit guards that remain active under
optimization.

The finite certificate covers the stated groups, exact rational cost gaps,
the sufficient recovery bounds, interval-ratio fixtures and thirteen rejecting
controls. It does not execute the Gaussian tensor, prime selection at
production sizes, an integer tape wrapper, or the replacement root. The
all-width primitive, common-cohort construction, source-faithful coefficient
pages, precision, physical restoration and cutoff contracts remain the
explicit premises of the written outer join.

## Recorded Git and portable scopes

`evidence/OUTER-CHECK.json` additionally records nine exact Git-blob comparisons
from the original source checkout. `evidence/OUTER-CHECK-PORTABLE.json` records
the default Git-free check against the complete 35-file reference bundle.
The registered outer suite compares its freshly generated portable receipt in
full; it does not claim to repeat the optional historical Git-object checks.
All coefficient, recovery, exponent and rejection checks are identical.
