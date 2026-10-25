# Complete physical chirp middle map

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I supply an encoded numerical consumer for the retained chirp identity.
I credit Chafik Boukhalfa's PR479 additive residue schedule and Ross
Richardson's PR948 symbolic checks. I retain their source pins and distinguish
this algorithmic argument from the finite evidence in EVIDENCE.md.

## Contract

Put r=2^ell. The caller supplies d-1 axis flags; flag 0 means length r/2,
and flag 1 means length r. The final axis has length r. Write
M=product(t_i:i<d)=2^A and T=Mr. The caller supplies C independent rows,
in natural tensor order with the last coordinate contiguous. I require
p>=16, 2<=ell<p, C>=1, d>=2 and p-A>=13.

For each axis, the caller supplies an odd integer 0<s_i<t_i as an ell-bit
unsigned LSB-first word. The numerical ports use the inherited canonical
Count encoding. Each payload coefficient uses two LSB-first signed p+2-bit
words and denominator 2^p. The caller must establish coefficient modulus
at most .6. I check format, extent, source bounds and parameter admission;
I use the norm bound as an input hypothesis.
The caller supplies distinct external tapes, disjoint from the owner's
scratch and child roles.

Define the normalized negative-sign Fourier map F_t and
`(Q_freq z)_j=z_(-s_i*j_i mod t_i)_i`. I return a p-grid approximation y to
Q_freq F_t x, in the same natural output order, with

    ||y-Q_freq F_t x||_infinity < (4 sqrt(2) M + 22) 2^-p,
    ||y||_infinity < .601.

I preserve the borrowed payload, source words, flags and numerical ports,
including their origin heads. The caller must consume the protected output
before reusing the owner. I erase the owned state and consume child returns.
I use a fixed number of tapes and a finite alphabet; I keep variable-length
axis records, basis entries and payloads on those tapes.

## Encoded residue producer

I use PR479's residue and state invariant, with modulus q=2r:

    c_i = -s_i(r/t_i) mod q,
    v_i = c_i*j_i^2 mod q,
    Delta_i = c_i*(2*j_i+1) mod q,
    E = sum_i v_i mod q.

For an ordinary coordinate increment I add Delta_i to E and v_i, add
2c_i to Delta_i and increment j_i. On wrap I subtract v_i from E,
reset j_i and v_i to zero and restore Delta_i=c_i. The identities
`(j+1)^2-j^2=2j+1` and `2(j+1)+1=(2j+1)+2` prove the ordinary step;
the subtraction proves the carry step. I emit E before each advance.
Thus I emit `-sum_i s_i*j_i^2(r/t_i) mod 2r`, and a complete rollover
restores E=0 and the initial axis records.

In `chirp_odometer.py`, I store five fixed-width ell+1-bit fields per axis:
radix, index, value, difference and coefficient. I reverse the axis-record
order once through the retained Parking serializer. The fastest axis then
occupies the first state record. During a carry I visit consecutive records,
rewrite only the current fixed-width record, and rewind only the prefix I
visited. I keep the persistent state outside the scalar multiplier's roles.

Over one cube, I visit

    sum_i T / product(t_j:j>i) < 2T

axis records, because t_i>=2. The return traversal costs at most the same
order of record movement. Each visit uses O(ell) bit operations: modular
addition needs at most one modulus subtraction, and modular subtraction
uses an ordered difference. I charge O(CT ell) for complete residue walks.
I also charge descriptor validation, initial record reversal and the global
plan compilation; the conservative polynomial setup term below includes
the setup comparisons and encoded cardinality calculations.

I validate complete binary packets before allocating decoded data roles.
That scan costs linear time in the packet size and permits cleanup after
ordinary malformed-input rejections. I do not claim transactional recovery
from arbitrary injected faults inside a child operation.

## Numerical dyadic powers

Let L=ell+1, h=2^-p and

    Q=p+ceil(log2 L)+4, h_Q=2^-Q.

For the admitted range, 16<=Q<=2p and ell+1<=Q. I compile PR3709's
authenticated TwiddlePlan once at length 2r. I request only indices 2^k,
0<=k<ell, and append the exact final factor -1 for bit ell. I obtain
positive-phase inward approximations to exp(2*pi*i*2^k/(2r)), since
PR479's E already includes the negative chirp sign. I use the exact +i
quarter-turn branch where applicable.

The retained directed Machin/Taylor proof gives modulus at most one and
complex error below 2h_Q for each approximate factor. I start from one,
scan the L basis entries and E's bits in parallel, and multiply each
selected factor with the actual Karatsuba word engine. I truncate each
complete complex product once on the Q grid. I use neither an indexed
phase lookup nor a per-coefficient transcendental routine.

For disk operands, multiplication by an inward factor preserves the disk.
I bound its new error by `(2+sqrt(2))h_Q<4h_Q`. After at most L factors,
I truncate to the p grid. Hence the final phase a_hat satisfies

    |a_hat-exp(2*pi*i*E/(2r))|
      < 4L h_Q + sqrt(2) h
      <= (1/4+sqrt(2))h < 2h,
    |a_hat| <= 1.

I include the exact half-turn factor in this upper bound, although it
introduces no phase error. I generate the numerical kernel once per full
packet and retain it for the convolution and final endpoint multiplication.

## Cyclic convolution and exact width recovery

Let zeta=exp(pi*i/r), `(D_± f)_(j,k)=zeta^(±k) f_(j,k)`, and let iota
group the contiguous last coordinate into a polynomial record. In source08,
the authors prove that substituting x_d=zeta*y identifies cyclic reduction
modulo x_d^r-1 with negacyclic reduction modulo y^r+1. They obtain

    D_- iota^-1 C_ring(iota D_+ f, iota D_+ g) = (f*g)/T.

I use the same p+2-bit component format on both sides, so iota requires
only a shape interpretation. In `cyclic_engine.py` I execute two input
twists, PR3709's full ring convolution, exact width recovery and the output
untwist. The ring consumer already includes its final exact M scale.
I apply no further r, M or T normalization.

Each computed twist uses an inward p-grid phase, an exact dyadic complex
product and one p-grid truncation. I bound its error by less than 4h
and preserve the operand's modulus. The ring consumer contributes
`E_ring=4sqrt(2)Mh`. If the smaller input norm is at most eta, its
returned norm is less than eta+E_ring, measured at the computed twisted
operands. The parameter gap gives E_ring<.001: squaring the equivalent
positive inequality gives `32*1000^2<2^26`.

For eta<=.7, I therefore obtain a ring return of norm below .701. Its
fractional precision remains p and its signed width is p+A+2. I read each
signed numerator and write the identical integer in p+2 bits. The signed
writer checks representability; the norm bound ensures that only redundant
high sign bits disappear. I perform no numerical truncation in this pass.
I consume the ring consumer's payload and width ports before reuse.

I propagate the two input-twist errors through bilinear contraction and
add the ring error and final untwist error. The complete cyclic error is
less than `(4sqrt(2)M+12)h`. I add the 12h after the normalized ring
interface, without another factor M. Inward untwisting preserves the
computed ring-output norm.

## The complete chirp sandwich

For the numerical kernel a_hat, I execute

    x0 = Q_p(conjugate(a_hat) * x),
    y0 = C_cyclic(a_hat, x0),
    y  = Q_p(conjugate(a_hat) * y0).

I preserve ||x0||<=.6. At the actual twisted inputs to the ring call,
I therefore obtain norm below `.6+E_ring<.601`. Exact width recovery,
untwisting and the final inward endpoint product preserve that bound.

In source07's chirp/permutation identity, the authors establish

    conjugate(a) * [a *convolution* (conjugate(a)*x)] / T = Q_freq F_t x.

I compare the computed sequence with that identity. I charge less than 2h
for the kernel, less than 4h for each endpoint and the cyclic error above.
Bilinear contraction gives total error below `(4sqrt(2)M+22)h`.
I retain the kernel across the child call and reuse it by a paired scan;
the complete operation preserves the natural tensor order.

## Complete physical invoice

Write N=CT and V=2(p+2)N. Let T_F denote one complete inherited Fourier
call. I charge the whole middle map at

    3 T_F + O(N(ell+1)p^(8/5) + r p^3 + (A+p+log(C+1))^3).

For kernel synthesis I execute at most 4N(ell+1) scalar word products.
The two endpoints add 8N, and the three cyclic twists add 12N. PR3709's
ring product adds N(12(ell+1)+8). Its proof charges the actual shrinking
Karatsuba recurrence, signed codecs, exact recovery and restoration.
I charge scans and additions at O(N(ell+1)p), plus O(Nell) residue work.
The inherited ripple counters add amortized linear traversal cost; I do
not scan the full A-bit address at each coefficient.

For the small power table I charge O(ell p^3) directed setup. The cyclic
twiddle table and ring FFT tables contribute O(rp^3). I include encoded
plan compilation and cardinality arithmetic in the conservative cubic
metadata term. I count these setup costs even though the complete outer
packet can amortize them.

If A=Theta(p), M pays setup; fixed powers of log(C+1) are O(C), so I
need no upper bound on C. At ell=Theta(p^(1-epsilon)), epsilon=.997, the
new online power per V is `8/5-epsilon=.603`. In corrected PR3709 and
its retained PR3640, the full Fourier power is

    Phi=1-(997/1000)*(1-99827101/100000000)=.99827619697.

I use Phi for the complete caller, rather than the primitive exponent
332353/332929. Under the inherited Fourier hypotheses I obtain the same
conditional O(Vp^Phi) allowance for this middle map. I establish no new
selected exponent or complete integer-multiplication theorem here.

I retain a constant number of full packets, one basis tape, one twist table
and O(dell) axis-state bits. I include nested child owners and the scalar
continuation stack in O(V) space for one call. During owner reuse, the host
Tape backing arrays retain the largest prior blank extent; their high-water
storage is O(max V over those calls). I erase their bodies and restore
their heads before return. Diagnostic host counters do not select operations
and can be omitted from the physical program.

## Verification and remaining obligations

I executed the complete p16, ell2, A1 caller against an exact staged oracle
and a separate dense Fourier sum. I also executed it with the original
reduced q2 setup, before adding the exact setup specialization described in
EVIDENCE.md; I obtained the same payload hash. The registered fixture
retains the physical data, root, normalization and restoration execution.

The tests do not constitute an independent proof review. The full Fourier
cost still assumes the retained supplier, native-refinement and hosting
premises. I have not executed production GL64/O73 here. Gaussian expansion,
compression, mixed-radix CRT movement and final integer recovery remain
separate interfaces. I retain source07/source08 attribution and PR3709's
nested notices, including Mason Hale's certified interval reference.
