# H6 dyadic Smith factors and exactly 560 physical row repairs

**Source-bound algebraic theorem; no new kappa or paid source-coding circuit.**
Let R=Z[1/2]. For the actual 30960-port H6 matrix
`K_ts=(t_ts^3-4*t_ts)/48`, let C=I-K. Its localized Smith factors are

```
1 repeated 30400 times,
11 repeated 336 times,
209=11*19 repeated 208 times,
4807=11*19*23 repeated 16 times.
```

Consequently C is not a dyadic unimodular coding map. A dyadic matrix repair
needs rank at least 560. Exactly 560 literal physical rows can be replaced to
make C unimodular: an explicit 560-row set and finite small modular minors
certify existence. This is an algebraic row-completion theorem, without the
replacement coefficients, native frame transports or a paid ADD realization.
An arbitrary-input dirty-helper-restored implementation of `(x,h)->(Cx,h)`
by dyadic unimodular operations remains impossible over R. A stable unit completion with 560 auxiliary
directions exists algebraically, but necessarily changes their outputs and
allows helper dirt into the coded output.

## 1. Pinned premises and verification boundary

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Original Git blobs and SHA256s are recorded in `SOURCES.json`. The portable
replay reads these declared live inputs directly; committed-byte/source-history
and Git-free export gates bind the original source bytes:

- `research/niemeier-lattices/workbench/helper-routes/compensation_rank.py`:
  written degree≤6 spherical-moment decomposition and exact H6 spectrum.
- `research/h6-independent-audit/spectral/README.md` and `results.json`:
  canonical 120x240 restriction, sector dimensions, exact moment proof and
  full feature-rank justification.
- `research/h6-independent-audit/spectral/audit.py`: defines the radial basis
  `R=[x*single,x*rootroot]`, with source identity `num@R=48*R@M` and
  `M=[[9,-240],[-18,-195]]`. This identifies which coefficient multiplies the
  root-product rows. Its representative probes supplement the written moment
  proof; they do not independently prove every sector action.
- `research/niemeier-lattices/code/e8_cubed.py`: actual canonical root order
  and product row IDs.
- `research/h6-compensation-network/k_encoder/README.md`: dyadic factor/word
  contract and its independent 816-centre inventory.

These source audits are inherited, not freshly rerun here. The theorem uses
their exact all-parameter moment/sector proof, rather than promoting the
representative operator probes into a full matrix identity. Fresh checks are
the polynomial reductions, determinant/Smith arithmetic, explicit physical
row set, small modular minors and unit-completion blocks.

The actual Gram values are integers in[-4,4]. Direct reduction of
`(t^3-4t)/48` for every integer in that interval is dyadic, so K and C have
entries in R. K is symmetric. The pinned complete spectrum gives

```
char_K(z)=z^30144*(z-39)^224*(z-45)^560
          *(z^2+186z-6075)^16.
```

Symmetry gives real orthogonal diagonalizability. Therefore the monic
polynomial

```
K*(K-39I)*(K-45I)*(K^2+186K-6075I)=0
```

is an exact matrix identity. Its coefficients and all entries lie in R, so
both this identity and the characteristic polynomial reduce modulo every
odd prime. A rational spectrum without this diagonalizability argument
would not alone justify the annihilator.

## 2. Determinant and all localized Smith factors

The nontrivial C eigenvalues are -38 (224 times), -44 (560 times), and the
two shifted radial eigenvalues, whose product is
`1+186-6075=-5888=-2^8*23`, for each of 16 radial pairs. All other C eigenvalues
are 1. The 224+560+16 negative factors give a positive sign. Thus

```
det(C)=2^1472*11^560*19^224*23^16.
```

R has units ±2^k. This determinant is not a unit. In particular finite
dyadic elementary ADDs, whose determinants are 1, cannot implement C on the
same physical coordinates. Allowing unit signs or unit dyadic scalings would
still not remove the odd-prime obstruction.

Modulo 11, the characteristic multiplicity of eigenvalue 1 of K is 560;
modulo 19 it is 224; modulo 23 it is 16. In each case 1 is a **simple root of
the reduced annihilator**, checked by its nonzero derivative. Hence every
Jordan block of K at eigenvalue 1 has size 1, regardless of other roots or
Jordan blocks. Therefore

```
nullity(C mod 11)=560,
nullity(C mod 19)=224,
nullity(C mod 23)=16.
```

For a matrix over the PID R, nullity modulo p counts the Smith factors
divisible by p, while v_p(det C) counts their positive valuations. Here these
counts agree. Every nonunit elementary divisor consequently has exponent 1;
there is no higher 11-,19- or 23-power hidden in a Smith factor. No other odd
prime divides the determinant. Combining the primary factors in divisibility
order yields precisely the four displayed classes.

If C+B is unimodular and rank_Q(B)≤r, then rank(B mod 11)≤r, since all
(r+1)-minors vanish already over R. Full rank modulo 11 requires r≥560.
Changing r literal rows is a rank≤r perturbation, giving the same lower
bound for literal physical row replacement. Smith form attains rank 560
abstractly, but that observation alone does not identify 560 physical rows.
The following certificate supplies those rows.

## 3. A literal 560-row completion certificate

Number the canonical E8 roots a_0,...,a_119 in the sorted doubled-coordinate
order of the pinned source. The root-product physical row IDs are

```
2160+240*i+2*j+sign,
port=(a_i,(-1)^sign*a_j), sign=0,1.
```

The first 2160 rows are the two pure norm-four blocks. Define a set S of 280
ordered canonical root-pairs: all 120 diagonal pairs(i,i), plus both
orientations of the 80 explicit undirected pairs stored as EDGES in the
checker. S is invariant under swapping coordinates. Let J consist of both
signed b rows for each pair in S. The result stores all 560 literal row IDs.

We show that restriction to J is injective on ker(C mod p) for every
nonunit prime p. For the three relevant primes it is enough to exhibit
independent restricted kernel functions of the exact nullities from section 2.

### Prime 11: the 560 mixed functions

Take the 35 traceless quadratic polynomials

```
q_ij(b)=b_i*b_j (i<j),
q_i(b)=b_i^2-b_7^2 (i=0,...,6).
```

The full H6 functions `a_i*q(b)` and `q(a)*b_i`, zero when one block vanishes,
are the two mixed linear/traceless quadratic sectors. The pinned moment
proof gives Kf=45f exactly, so they lie in ker(C mod 11).

The 280x280 evaluation matrix of `a_i*q(b)` on S has determinant **6 modulo 11**.
This is freshly checked by complete modular elimination. Swapping the pair
coordinates permutes S and gives the same full rank for `q(a)*b_i`.
Under b->-b the first sector is even and the second is odd. The invertible
two-by-two signed-pair Hadamard transform separates them because 2 is a unit
modulo 11. Their evaluation on J therefore has rank 560. These functions span
the entire kernel, so restriction to J is injective.

### Prime 19: the 224 pure harmonic cubics

For each degree-three monomial, use its integer harmonic projection in eight
coordinates. The checker evaluates

```
10*x_i^3-3*|x|^2*x_i,
10*x_i^2*x_j-|x|^2*x_j (i!=j),
10*x_i*x_j*x_k (i,j,k distinct).
```

These are harmonic because the cubic Laplacian trace is removed with
n+2=10. Their restriction to all 120 canonical roots has exact rank 112
modulo 19, freshly checked. On the full H6 shell the moment proof gives
Kf=39f, hence these functions are in ker(C mod 19). Each block contributes 112.

S contains every diagonal(a,a). The two signed b rows for each such pair
have values `(H(a),H(a))` and `(H(a),-H(a))` on the two block sectors.
Again the signed-pair transform separates them. Thus restriction on just
these 240 of the 560 selected rows already has rank 224. It spans the full
kernel, proving injectivity on J.

### Prime 23: the 16 radial kernel functions

In the pinned radial basis `[x*single,x*rootroot]`, K acts through
`M=[[9,-240],[-18,-195]]`. Modulo 23, `(1,10)^T` is a 1-eigenvector. Its
root-product coefficient is 10, which is nonzero modulo 23. For each of eight
coordinates in either block this gives a kernel function whose root-product
restriction is 10*a_i or 10*b_i. The integer root coordinate matrix has rank 8
modulo 23. The same 240 diagonal signed rows separate the two blocks, giving
rank 16. This spans the full radical C kernel modulo 23 and proves injectivity.

### Primitive rows and row replacement

Let I be the 30400-row complement of J. If the C rows indexed by I were
dependent modulo p, extend the dependency coefficients by zero on J. That
would give a nonzero left-kernel vector vanishing on J. C is symmetric, so
this is a kernel vector, contradicting injective restriction. Thus the
untouched 30400 rows are independent modulo 11,19 and 23. For every other odd
prime C is invertible, so any subset of its rows is independent.

Over the PID R, a full-row-rank matrix generates a primitive submodule iff
its rows stay independent modulo every nonunit prime: a nonunit Smith
factor would cause a rank drop at one of its prime divisors. Consequently
the row module generated by C_I is primitive. The quotient of R^30960 by
this module is free of rank 560. Extend these 30400 existing rows to an R-basis
and insert the 560 complementary basis rows at J. The resulting matrix A is
unimodular and differs from C only on J. This proves **exactly 560 literal
physical row replacements suffice algebraically**, matching the lower bound.

If determinant 1 is required, rescale one replaced row by the inverse of
det(A), a dyadic unit. This preserves the untouched rows. Neither the
complementary coefficients nor a finite physical elementary-ADD word is
produced here. The theorem is an existence certificate, not a zero-cost
source-interface substitution or an attained native tariff.

## 4. Stable unit completion and arbitrary helper dirt

An invertible(N+r)x(N+r) dyadic matrix whose upper-left block is C requires
r≥560: modulo 11 its first N rows can gain at most r ranks from the new
columns. Smith form attains r=560. Each nonunit Smith coordinate d has the
unit block

```
[[d,1],[-1,0]], (x,h)->(d*x+h,-x).
```

The four exact ADDs `x+=h; h-=x; x+=h; x-=d*h` implement it. The checker
checks the two arbitrary input columns and determinant 1 for d=11,209,4807.
Their total local component-Horner bill is 13008, before basis changes and
all frame, copy, storage and cleanup costs. This scalar count is not a
native rank tariff. Smith basis transforms are not free. A dyadic unit on
one auxiliary output can normalize the global completion determinant if
needed; no paid implementation of that normalization or the bases is given.

The helper output changes to -x and the coded output contains the entering
helper dirt h. Within the dyadic unimodular class, a simultaneous exact endpoint `(x,h)->(Cx,h)` would have block
determinant det(C), which is a nonunit. Thus adding restored arbitrary dirty
helpers cannot by itself legalize C as a standalone unimodular coding map.
A viable new global controller must explicitly carry, cancel or repair the
560 auxiliary/residue directions, bind their source access and native frame
visits, and pay their allocation, cleanup and precision. None is supplied by
the Smith theorem or the physical-row existence certificate.

## 5. The required consumer is a new complement producer

The current native clean H6 response is Kx, whose scalar row rank is 816.
The matrix analyzed here is **C=I-K**, the compensation operator. It is not
the current clean response. Coding K itself into a full-rank unimodular
response would require at least 30960-816=30144 row repairs, already by
rational rank. Invertible source/output gauges do not change that rank
deficiency. Consequently the 560-row result cannot be applied to the native
K response by relabeling it as a C producer.

The proposed consumer would have to be a new cheap clean **complement**
word returning Cx, with explicit coded source/output frame representatives,
ordinary dirt and residue endpoint contract. All coefficients and row IDs
in this theorem use the existing canonical H6 ports; no new such gauges or
producer are emitted. The existing fullC compensation word using hundreds
of millions of edge helpers does produce C algebraically, but retaining
that cost does not deliver a useful coded interface. Even the identity term
of I-K is not a free direct source-to-target delivery under the existing
flags. Producing the complement cheaply is therefore a separate constructive
obligation, followed by the 560-direction repair/extension, restoration and
global-controller invoice. There is no claimed 560-repair supplier here.

## Verification boundary

The registered portable replay checks the small modular certificates and
explicit unit blocks under isolated optimized Python 3.12. It authenticates
the inherited exact spectral and sector sources, but does not rerun their
full original audit or construct the dense matrix. The separate checker
rederives all 240 harmonic, 560 mixed and 32 radial polynomial actions from
the stated degree-six shell moments; the inherited full spectrum premise
remains explicit. It uses all 816 coefficient positions per cubic identity.
The all-prime and primitive-completion implications are the written proof above.
The producer executes two matrix mutations and two arithmetic counterchecks;
the independent checker executes three matrix/eigenvector mutations.
Actual replacement coefficients, Smith bases and a paid physical circuit are
not supplied. Source credit and licensing remain in README.md and SOURCES.json.
This is not a formal-kernel or complete multiplication theorem.
