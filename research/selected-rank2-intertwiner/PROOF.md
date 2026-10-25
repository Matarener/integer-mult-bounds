# One selected sequential child pair: exact coupling and cost

All maps below are linear over Q(i), and hence over any characteristic-zero
extension containing i. The inherited coordinate kernel is
`C_q=((1+i)I+(1-i)X_q)/2`. This note uses primary Clifford/native circuit
algebra together with the operator-space viewpoint from linear systems:
the ADD is a coupling channel whose transfer map must be retained.

## Exact boundary and the intervening region

Pin the selected source archive and member hashes in `verify.py`. In the
forward phase-B word, events 12806 and 13402 act on register195 by the
recipes `A:0→2` and `B:2→252`. Their ranks are1 and1. The available direct
recipe `C:0→252` has rank2. Let `D:2→559` denote the next donor521 child,
at event14191, of rank2. Frame vectors are

```
0: []       2: [30]       252: [224,30]       559: [416,19,13].
```

There are597 inclusive events:139 climbs and458 scalar ADDs. The only
interior operation touching195 or521 is event12807,
`L195 += (1/2) L521`. The other594 interior events have neither register as
source or target. The verifier reads every event, not just a same-target
subsequence. These operations commute with the two-register macro because
they act on disjoint registers; they remain in their recorded order and are
carried unchanged. No source, centre or dirty helper is silently deleted.

Let x,y be arbitrary physical values of195 and521 at entry. No zero or
clean-donor premise is imposed. The exact local boundary map is

```
M(x,y) = (B A x + (1/2) B y, y).
```

Fresh sparse Gaussian-rational evaluation of the serialized left/right
monomials and the coordinate kernel checks every one of512 basis columns.
It proves `BA=C`, including scalar global phases; equality of frame endpoints
alone is not used as proof. Thus

```
M = [[C, B/2], [0,I]].                         (1)
```

Linearity makes the complete512-column check a proof of the entire finite
operator identity. It also checks1024 basis inputs of the two-register
boundary, inverses on arbitrary donor vectors, and the maps below.

The missing transport has a particularly small witness. Set `x=0,y=e_0`.
The correct target is
`((1+i)e_0+(1-i)e_224)/4`; replacing the pair by C and retaining an ordinary
ADD gives `e_0/2`. Moreover `rank(B-I)=256` over Q(i), computed by exact
Gaussian elimination. This ordinary matrix rank measures a defect; it is
not a native-child tariff or a Fourier width.

## Unique transport, in both orderings

After applying C to x, an ordinary ADD with donor transformed by J gives
`Cx+Jy/2`. Equation(1) for every y forces **J=B**. The donor can be restored
immediately by B inverse. Alternatively, move the ADD before C. Its donor
must be transformed by `J=C^-1 B=A^-1`, also uniquely. These are equalities
of operators, without a commutativity assumption on distinct frames.

If restoration is deferred until donor521's next touch, the intervening
source trace has no other521 operation. In the first ordering its required
next child is uniquely `D B^-1=T559 T252^-1`; in the second it is
`D A=T559 T0^-1`. Both exact maps have eight nonzero entries in every column.
Any monomial--width-r coordinate child--monomial factorization has at most
`2^r` nonzeros per column: the two monomials only permute/phase entries and
the child branches into at most `2^r` positions. Thus each correction needs
r≥3 in this particular one-child normal form. The separately serialized
`CORRECTION.json` and `EARLY-CORRECTION.json` give width3 factorizations;
the fresh checker verifies all512 columns, including phases. The width is
therefore exactly3. Their generation used the credited inherited Clifford
compiler; replay does not import or trust that compiler.

After the corrected next child, donor521 again has exactly its original
value and frame559, before its following scalar use. Its later work and
existing dirty-return wrappers are preserved. The target ends in frame252
and its original subsequent ADD is preserved. This is a valid boundary
identity, not a claim that new hosting or a complete supplier is admitted.

## A different joint-macro class also fails

Allow any number of vector registers, arbitrary coordinate-uniform scalar
linear mixing between them, and **one invocation of any fixed linear
operator Q on one whole vector register**. Grant scalar work for free.
Clean auxiliary registers start at zero; dirty auxiliary values are arbitrary
independent inputs, with no free input-dependent pre-encoding. The specified
boundary and restoration must hold. All mixing is fixed and linear. A single
call on a larger concatenated register is outside this class. All coordinate-independent scalar operations
before the invocation collapse to `P tensor I`, and those after it to
`R tensor I`. The invocation is
`I + E_jj tensor (Q-I)`. Therefore the complete map is

```
(RP) tensor I + (R E_jj P) tensor (Q-I).
```

Every input-output vector block lies in `span{I,Q}`. Fixing clean auxiliaries
to zero or requiring dirty auxiliaries to be restored cannot enlarge this
span for the x,y boundary blocks. Equation(1) requires I,B,C all to lie in
that space. But rows `(output,input)=(0,0),(30,0),(224,0)` give, in columns
I,B,C, the exact minor

```
[1, (1+i)/2, i/2  ]
[0, 0,       -i/2 ]
[0, (1-i)/2, 1/2  ],
```

whose determinant is `(1+i)/4 ≠ 0`. Thus this entire scalar-mixing/one-call
class is excluded, even when Q is not a Clifford child. This is not a
no-go theorem for arbitrary joint native macros: coordinate-dependent
permutations or quadratic phases between mixing operations fall outside
`P tensor I`; several coupled operator calls or a different joint primitive
also change the contract. The current prescribed child normal-form adapters
are already absorbed into A,B,C. Treating *new* adapters as scalar mixing
would invalidate this argument.

## Uniform lifting, rather than a sampled input claim

For every positive column multiplicity f, define the inherited tensor lifts
`A_f=A^tensor f`, and likewise B,C,D. Tensor functoriality gives
`B_f A_f=C_f`, `C_f A_f^-1=B_f`, and the two correction identities for all f.
All claims also tensor with an arbitrary identity spectator. The dependency
separation of the source word remains valid for these lifts.

The minor for I,B_f,C_f uses input0 in every factor, and output patterns
`(0,...,0)`, `(30,0,...,0)`, `(224,0,...,0)`. Its determinant is

```
((1+i)/4) * ((-1+i)/4)^(f-1),
```

which never vanishes. The one-call scalar-mixing obstruction therefore holds
for all f. Each deferred correction column has `8^f=2^(3f)` nonzeros; the
factorwise recipe supplies width3f and the same support bound forces width
at least3f in the monomial/one-child class. This is a uniform algebraic
identity and obstruction for the stated tensor lifts. It does not discharge
the repository's inherited all-size compiler, hosting or analytic assumptions.

## Positive finite native fusion and its uniform channel bill

The transfer has an explicit Pauli decomposition, checked on every column:

```
B = a I + b P,    a=(1+i)/2, b=(1-i)/2,
P e_x = (-1)^parity(96 & x) e_(x xor224).
```

`P^2=I`, since parity(96&224)=0. Thus (1) has a legal finite implementation:
apply C to the target, then accumulate `(a/2)y` and `(b/2)Py`, restoring the
donor. With rational scalar ADDs only, a literal schedule is

```
x <- Cx
x += y/4;  y <- i y;   x += y/4;  y <- -i y
y <- P y
x += y/4;  y <- -i y;  x += y/4;  y <- i y
y <- P y
```

The six source transforms are four scalar unit phases and two signed-XOR
monomials. Each signed XOR is one address permutation plus one sign phase;
calling it one monomial map does not identify it with one scalar CPU operation.
This schedule has four rational array ADDs, six monomial source maps, no new
register, one rank2 target child, and an exactly restored arbitrary dirty
donor. The full1024-column boundary replay verifies this schedule. These are physical
coordinate ADDs in a new macro: the target/donor intermediate frame labels
are not all equal. It is not a drop-in replacement sequence admitted by the
inherited standard scalar-word common-frame checker. A compiler admitting
this new coupled boundary must be supplied before changing the selected word. Its
rank-only recursive expression saves `2-2^(1-a)>0`; the finite arithmetic
increases from one to four array ADDs plus the six stated maps. This is a
constructive finite result, not merely an optimistic endpoint match.

For every f the same idea expands as

```
B_f = sum over S subset {1,...,f} of a^(f-|S|) b^|S| P_S,
```

where P_S applies P in factors S. Every coefficient is nonzero. The
`2^f` masks are distinct, so every column of B_f has exactly `2^f` nonzeros.
Consider the explicit accumulation contract: the donor is changed only by
invertible monomial maps and is restored; the target accumulates k scalar
multiples of monomial images of the original donor. Every counted ADD source
must be one such image: no uncounted source additions, precomputed donor
mixtures or additional source registers supplying mixtures are granted. Target monomial charts may be
inserted, but there is no feedback from the target into the donor and no
additional operator call on the donor. Each accumulation contributes at
most one entry per input column to the donor-to-target block. Consequently
**k≥2^f**. The displayed expansion attains this number of Gaussian scalar
channels. It is a sharp result for this accumulation alphabet, not a bound
for all native programs or coupled algorithms.

Splitting each Gaussian coefficient into real and imaginary rational parts
gives at most `2^(f+1)` rational ADDs and `4*2^f-2` monomial source maps (the
empty-set term needs no P_S/undo pair). Coefficients have an explicit common
denominator `2^(f+1)` and integer numerators of O(f) bits, so their preparation
and arithmetic precision must be charged; they are not fixed-size constants.
For lane volume V=`2^(9f)` times any spectator multiplicity, the schedule
uses at least `V 2^f` coordinate accumulation operations in this literal
array-ADD model, with the stated upper number of array passes. The inherited
volume-linear child expression is `A V (r f)^(1-a)` for a fixed positive A.
Thus this literal expansion cannot have a fixed O(V) adapter invoice or
improve that expression uniformly as f grows: `2^f/f^(1-a)` is unbounded.
This is an asymptotic comparison under the explicit array-cost contract,
not a claimed universal complexity lower bound. A complete selected finite
invoice, encoding costs, hosting and all-size admission are still unproved.

## Fully charged optimistic screen and decision

The pinned selected moment source assigns a width-r child the normalized
recursive charge `r^(1-a)` (a common positive factor `m^(a-1)/W` is omitted).
For multiplicity f all expressions acquire the common positive factor
`f^(1-a)`. The selected positive exponent lies in0<a<1.

| Scheme | Original paid ranks | Replacement paid ranks | Increase in normalized recursive charge |
|---|---|---|---|
| Restore donor immediately, either ordering |1,1|2,1,1|`2^(1-a)`|
| Restore at next donor child, either ordering |1,1,2|2,1,3|`3^(1-a)-1`|

Both increases are strictly positive for0<a<1. This compares inherited
available recursive charge expressions; it is not a lower bound on optimal
runtime. The latter replacement increases paid rank mass4→6; immediate
restoration increases it2→4. Unchanged597-region work is retained. Each
scheme retains one coefficient-1/2 ADD and uses no new vector register.
It includes every changed donor child and the eventual donor restoration.
The next unrelated target and donor operations stay unchanged.

A complete new finite invoice is unnecessary to reject these two optimistic
screens: grant all altered monomial wrappers, routing, scalar arithmetic,
precision and descriptors zero extra cost, and the recursive expression
already worsens. Their actual changed finite costs and hosting are **unknown,
not zero**; this is not a physically admitted replacement. No new global
profile, cold supplier replay or improved κ follows.

**Decision: retain the positive finite Pauli schedule, but stop its literal
exponential-channel lift as a fixed-cost adapter proposal; stop these two
retiming implementations and the scalar-only
one-call class.** The next justified constructive question must change one
of these explicit contracts, for example coordinate-dependent coupled
adapters or simultaneous use of several operators with a complete bill.
A larger endpoint-match census alone does not reopen this candidate.
