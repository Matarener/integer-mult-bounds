# Exact normalized products and their Fourier composition

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I give an algorithmic proof for the program in this directory. The finite
checks in EVIDENCE.md exercise the implementation; they do not prove the
quantified statement or discharge the inherited Fourier supplier premises.

## 1. Contract and mathematical statement

Write `D_p={2^-p(a+ib): a,b in Z, a²+b²<=2^(2p)}` and let `Q_p`
truncate each real component toward zero on that grid. Fix integers
`A>=1`, `C>=1`, `p>=2`, `1<=ell<p`, `r=2^ell`, `M=2^A`.
For each of `CM` records, the caller supplies two polynomials with `r`
coefficients in `D_p`, in `C[X]/(X^r+1)`. The caller supplies complete
packets in the same record order. Each Gaussian coefficient occupies two
LSB-first, two's-complement words of width `p+2`.

`RingProduct.run` returns exactly `Q_p(uv/r)` for each record, in the same
format and order. The caller must establish the disk precondition; the
program checks dimensions, precision, extent and ownership but does not
validate the input disk. Each output coefficient lies in `D_p`, since the
normalized negacyclic product averages `r` signed products of unit-disk
numbers and component truncation can only decrease its modulus.

The caller borrows the two external input tapes and four canonical numerical
ports. It receives one protected output tape and must consume that tape
before reusing the owner. The program rewinds borrowed ports and erases its
scratch, continuation and child-output tapes. The runtime uses a fixed finite
alphabet and a fixed number of tape roles, independent of the parameters.
The host implementation retains blank backing storage up to the greatest
extent previously visited; the space claim counts those physical extents.

Let `V=2(p+2)CMr`. I derive the general product bound

    time = O(CMr(ell+1)p^(8/5) + r p^3 + (A+p+log(C+1))^3),
    space = O(V).

The second term charges the actual twiddle producer. The exponential packet
size pays both setup terms under the outer hypothesis `A=Theta(p)`.
I make no HH-rate
claim for this product, and I do not infer a new integer-multiplication
exponent from this interface alone.

## 2. Concrete scalar multiplication

`ring_words.py` uses the inherited canonical binary `Count` representation
as a magnitude tape, together with one finite sign bit. It implements signed
copy, addition, subtraction, two's-complement parsing/writing and shifts by
sequential scans. In particular, a shift appends its low zeros and copies
the old digits once; it does not repeat a growing one-bit shift. Its nearest
integer operation reads the highest discarded bit, rounds the magnitude
half up and restores the sign. I exclude ties in Section 4.

`word_product.py` evaluates a three-child Karatsuba recursion iteratively.
At width `n>16`, put `k=ceil(n/2)` and split `a=a0+2^k a1`,
`b=b0+2^k b1`. Each child has width `k`, including the difference child:

    z0=a0*b0, z2=a1*b1, d=(a1-a0)*(b1-b0),
    cross=z0+z2-d=a0*b1+a1*b0,
    a*b=z0+2^k cross+2^(2k) z2.

The program stores the sign of `d` in the finite continuation header and
multiplies its absolute operands. Those operands fit in `k` bits. At a leaf
it calls schoolbook `Count.product` only on operands of at most 16 bits.
For arbitrary-width online payload arithmetic, `Arithmetic.multiply` calls
this actual word engine and consumes its complete `2n`-bit result.

The owner serializes eleven fixed canonical roles through inherited
`Parking`, using four bits per saved symbol and a finite phase/sign header.
It closes scratch leases before descent, keeps child results on a separate
handoff tape, and restores the saved parent only after clearing the child
roles. The parent frames contain O(n) symbols at that parent's width.
Consequently `T(n)<=3T(ceil(n/2))+O(n)` and the live stack has geometric
total length O(n). With a fixed leaf cutoff, the usual dyadic majorant gives
`T(n)=O(n^log2(3))=O(n^(8/5))`; the strict inequality follows from
`3^5=243<256=2^8`. I charge frame copying, serialization, restoration and
zero filling in the O(n) term. No child scans a root-width padded frame.

## 3. Certified inward twiddles

For a dyadic stage length `2<=L<=2^Q`, `Q>=16`, the producer returns
`L/2` values approximating `exp(-2*pi*i*k/L)`, or their conjugates for
the opposite direction. Put

    h=2^-Q, T=Q+64, J=Q+8,
    R=Q+ceil(log2 T)+12, U=2^R, B=2^Q.

All arithmetic in `twiddle_setup.py` uses signed `Count` tapes and directed
integer division. I use schoolbook multiplication and division here and
charge them as setup. The producer computes the fixed-point intervals below.

For `x=5,239`, enclose each of the first `J` terms of the alternating
arctangent series by its floor divided by U and the next grid point. Add
the signed intervals and pad both ends by one R-grid ulp. Since
`R<=2Q+18<4J+2`, the alternating tail is less than
`5^-(2J+1)<2^-(4J+2)<1/U`. Each arctangent interval has width at most
`J+2` ulps. Machin's identity gives a pi interval of width at most
`20(J+2)` ulps.

The runtime also checks that the entire interval lies in `(3U,4U)`.
For this guard, the elementary series bounds give
`pi>16(1/5-1/375)-4/239=281476/89625>25/8` and `pi<16/5`.
Moreover `20(J+2)/U<=5/1024` for Q>=16. Thus both strict guards hold.

At index k, use `t=floor(pi_lower*k/(L/2))/U`. Then `0<=t<4`, and
the angular error is less than `[20(J+2)+1]/U<20T/U`. Starting from
`lo0=hi0=U`, propagate the nonnegative Taylor term intervals by

    lo_(j+1)=floor(lo_j*t_num/(U*(j+1))),
    hi_(j+1)=ceil (hi_j*t_num/(U*(j+1))).

If `w_j=hi_j-lo_j`, directed rounding gives
`w_(j+1)<=4w_j/(j+1)+2`. From w0=0, the first bounds are 2,6,10,12;
the same recurrence keeps subsequent widths at most 16. Sum the first
`2T` terms with phases `+cos,+sin,-cos,-sin`. Each component includes T
terms, so its interval width is at most 16T ulps. The omitted remainder is
less than `4^(2T)/(2T)!<=(16/T)^T<2^-(Q+12)` for T>=80, because
`16/T<=1/5<1/4` and `2T>Q+12`. In R-grid units that is at most 2T.
Cosine and sine are 1-Lipschitz. I pad each endpoint by 24T ulps to cover
the angle and tail errors; the resulting width is at most 64T ulps.

For an interval entirely above zero, take the lower endpoint and truncate
to the Q grid. For one entirely below zero, take the upper endpoint and
truncate its magnitude. For an interval crossing zero, choose zero. Each
component then has the true sign and no greater absolute value than the
true component. Thus the Gaussian twiddle has modulus at most 1. Since
`64T/U<=h/64`, its component error is at most `65h/64` and its complex
error is less than 2h. The exact k=0 and k=L/4 branches use `(1,0)` and
`(0,1)` before applying the direction sign. Lengths 2 and 4 need no pi
calculation; every other nontrivial index has an initialized pi interval.

The arctangent denominator has O(J) bits: the largest fixed base is 239.
The Taylor operands have O(R) bits, the angle product has O(R+log L)
bits, and the accumulators need O(R+log T) bits. Thus each twiddle uses
O(Q) scratch cells and O(Q^3) bit steps, including O(Q) schoolbook
divisions and multiplications. The stages have geometric table lengths;
three transforms together generate O(r) twiddles at cost O(r Q^3).
The caller stores each stage table once, rewinds it per group and consumes
the protected producer output before the next call.

## 4. Three normalized transforms and exact recovery

Set `N=2r`, `m=ell+1`,

    s=ceil(log2(12m+2))+3,
    Q=2p+2m+s.

The plan has `16<=Q<=8p`. For the upper bound, m<=p and
`ceil(log2(12p+2))+3<=4p` for p>=2; verify the latter at 2 and compare
the factor 16 growth on its exponential side with its linear right side.
Hence the twiddle admission `log2 L<=Q` holds for every stage.

The caller lifts each p-grid input exactly to the Q grid and pads each
record with r zeros. It computes two normalized DIF transforms, multiplies
matching frequency records and computes a normalized opposite DIT transform.
DIF uses descending stage lengths and returns bit-reversed frequency order;
DIT consumes that same order with ascending lengths and returns natural
coefficient order. The matching permutation needs no materialized reversal.

Write inputs as `(a+ib)/B`, `(c+id)/B` and a twiddle as `(u+iv)/B`.
For DIF, the exact real numerators before final truncation are
`(a+c)/2` and `[u(a-c)-v(b-d)]/(2B)`, with the analogous imaginary
expressions. For DIT, form `R=uc-vd`, `I=ud+vc` and truncate
`(Ba±R)/(2B)`, `(Bb±I)/(2B)`. Pointwise multiplication truncates
`(ac-bd)/B`, `(ad+bc)/B`. These are integer-word formulas for output
numerators. `fft_arithmetic.py` performs one truncation per component after
the complete butterfly numerator. Premature H or twiddle truncation would
change the endpoint; the verifier contains an executed counterexample.

Each exact butterfly with an inward twiddle preserves the unit disk and is
nonexpansive in the maximum complex modulus across its two inputs. Component
truncation preserves the disk. The replacement of a true twiddle costs less
than 2h per output; truncation costs less than `sqrt(2)h`. Thus each stage
adds less than 4h error. Each forward transform differs from its ideal by
less than 4mh. The product of two disk elements is 1-Lipschitz in each
argument, and its final truncation costs less than 2h. After the final
opposite transform, the total error is strictly less than `(12m+2)h`.

The normalized inverse of the product of the two normalized forward
transforms is the ordinary length-N convolution divided by N². Zero padding
prevents wrap because the product degree is at most 2r-2. Its coefficients
are Gaussian integers divided by `2^(2p)N²`. Multiplying the error by
that denominator gives

    error < (12m+2) 2^(2p+2m-Q) = (12m+2)2^-s <=1/8.

The program therefore recovers the exact integer coefficients by nearest
integer rounding of each Q-grid numerator divided by 2^s. It checks the
last coefficient is zero, buffers the lower r coefficients and subtracts
the upper r coefficients. Finally it truncates by 2^(p+ell), giving exactly
the required p-grid numerators of `uv/r`. The integer buffer has width
`2p+ell+3`; the bound `r*2^(2p)` on each ordinary complex coefficient
leaves sign and carry headroom. Butterfly multiplicands fit in Q+3 bits;
their raw scalar sums have O(Q) bits, including at most 4B² in magnitude.

## 5. Sequential movement and complete cost

`RingProduct.stage` scans each group in order. It buffers the first half,
reads the second half and twiddle table together, writes the two output
halves to fixed buffers, concatenates them and clears those buffers before
the next group. It retains a constant number of complete packet tapes.
It uses neither indexed payload lookup nor a host list of Gaussian values.
Each of the 3m stages executes `CMN/2` butterflies and four scalar products
per butterfly. The pointwise pass executes `CMN` products of Gaussian
values, four scalar calls each. The total is exactly

    CMN(6m+4) scalar calls.

Each call costs O(p^(8/5)). I charge packet movement, signed codecs,
truncation, recovery and repeated loop metadata at O(CMrmp). The inherited
`indices(N)` yields the same encoded index and uses ripple increment and
decrement. Summed carry/borrow lengths give O(N+log(N+1)) for the whole
loop, rather than a full-index scan at each iteration. Recovery does compare
its index with r-1, at O(ell) per coefficient; ell<p pays that scan. The
per-record padding product multiplies the encoded sizes r and Q+2 at cost
O(log(p)(ell+log(p))), which fits beside its O(rp) output scan.

I conservatively allow O((A+p+log(C+1))³) for global plan compilation,
cardinality products, counter setup and stage/group calculations. The
complete time bound also includes O(rp³) twiddle setup. If A=Theta(p),
M pays both setup terms; fixed powers of log(C+1) are O(C), so I need no
upper bound on C. I include table storage, all packet buffers, scratch
pools, borrowed packets and the scalar continuation stack in the space
bound. Their metadata extent O(A+p+log(C+1)) also fits in O(V).

For `ell=Theta(p^(1-epsilon))`, after dividing by V the online exponent is
`8/5-epsilon`. At epsilon=997/1000 it is 603/1000. In the pinned PR3640
proof, the primitive exponent is `tau=332353/332929`, the relaxed native
exponent is `alpha=99827101/100000000`, and the complete Fourier exponent is
`Phi=1-(997/1000)(1-alpha)=99827619697/100000000000`.
I compare the product with Phi; I do not substitute tau for the full transform
cost. Setup also fits because M=2^Theta(p).
This is a specialization of the full invoice, not a selected-frontier
update. At epsilon=1/40 the same product exponent exceeds 1; this proof
does not justify substituting it into that conservative parameter regime.

## 6. Actual Fourier/product/opposite composition

`convolution_engine.py` executes two calls to the authenticated PR3640
forward `W-/M`, this exact normalized product, one opposite `W+/M`, and
one exact multiplication by M using its inherited grid-boundary adapter.
The public Fourier plan imposes its own admission, including ell>=2.
Let f,g denote the original disk-valued polynomial packets. Source06 gives

    M (W+/M) [ ((W-/M)f) ((W-/M)g) / r ] = (f*g)/(rM).

Each Fourier call returns one p-grid truncation of its exact normalized
map, with error less than `sqrt(2)2^-p`; its normalized map preserves the
coefficient maximum norm. Normalized negacyclic multiplication has norm
at most 1 and is 1-Lipschitz in each disk operand. Its final truncation adds
the same error. Propagating the two forward errors, product truncation and
opposite truncation gives strict error less than `4sqrt(2)M2^-p` from the
ideal normalized convolution. The final multiplication by M is exact.

The caller receives both the Gaussian payload and a canonical width port,
with width `p+2+A` and unchanged fractional precision p. It must consume
both before reuse. The scaled output need not lie in the unit disk. A later
consumer needs a quantitative margin before narrowing to p+2 bits.

If one complete normalized Fourier call costs `T_F`, I charge the whole
composition at `3T_F+T_product+O(CMr(p+A))`, plus the same global
descriptor allowance. The final term includes the widened output copy.
Under A=Theta(p), that term and the output storage fit in O(V). If the
inherited Fourier hypotheses give `T_F=O(Vp^Phi)` with Phi as above, the
epsilon=.997 specialization above gives the same complete conditional
allowance for this convolution caller.

The product proof uses no T74 supplier inequality. The composition inherits
PR3640's all-size supplier, native-refinement and hosting premises and its
conditional Fourier cost. I have executed a complete small composition
with the actual direct/literal q2 Fourier child. I have not executed the
production GL64/O73 path here or proved the remaining Gaussian expansion,
CRT conversion and final integer recovery join.

## 7. Attribution and proof boundary

I retain PR3640's complete official export and its nested notices unchanged.
I use the standard Karatsuba identity and radix-two DIF/DIT Fourier algorithms.
Mason Hale's PR2313 (`190637e62401516c72b267859c0dd51cac607f6d`) provides
the separately implemented Machin/Taylor interval reference; I authenticate
its `intervals.py` as a check-only input. Dugongue's PR2790
(`1a9b88273535cbe93cb6cb7ca95f38fdcfe548f3`) supplies an operand-preserving
quadratic multiplication/ABI precedent. I import no Lean theorem from it.
Source06 retains Nussbaumer/Quandalle, Harvey/van der Hoeven and OpenAI
attribution. I claim neither independent human review nor formal-kernel
verification of this Python implementation and proof.
