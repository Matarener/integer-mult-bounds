# All-cut coordinate stability for the actual P104 word

This is a source-specific finite-template lemma for the original conditional
kappa candidate in PR5551. It supplies explicit error and range constants. It
does not prove a recursive child implementation, a Turing-tape implementation,
the complete multiplication theorem, scientific admission or a new kappa.
The five selected framework premises remain.

## 1. Exact program and the chosen owned COPY implementation

The source is PR5551 head `1123635a6f63f23638df9459c994160e5e649d30`.
Its immutable WORD container SHA256 is
`48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446`.
There are 735 arbitrary public fields, eight owned positions with local peak
occupancy one, and 25,310 events. All 735 independent inputs are retained.

For numerical implementation, realize each of the eight COPY operations as
`owned += source` after its declared INIT. The actual coefficient is one and
the two fields have the same chart. The exact source trace proves the owned
destination is zero, so this gives the same exact value and every public and
owned endpoint. Source ADD and COPY have the same scalar tariff at this
coefficient. All MOVE requests, charts, scalar coefficients and ordering remain;
no recursive child, field or ordinary scalar charge is added.

`RESIDUAL-WORD.json.gz` makes this implementation concrete: exactly the eight
COPY opcodes become ADD. The frozen source is unchanged. This choice matters
under perturbation: an arbitrary residual in the owned destination before COPY
is carried by ADD. It must not be silently replaced by zero in a derivative
calculation. For example, a residual before source event 13491 in owned field
735 reaches public output 112 with coefficient one. Assignment-COPY would
erase that response. The checker preserves all eight such nonzero responses.
INIT and CLEAR erase only owned fields under the retained ownership premise.

## 2. Two exhaustive exact scalar matrices

At each of 25,311 semantic cuts, let A be the logical input-to-state matrix on
the 735 public inputs. The forward interpreter uses exact sparse integer
vectors with a shared dyadic denominator. Every row-l1 norm is maintained.
It proves

```
max_cut ||A||_infinity = 131072 = 2^17.
```

Equality occurs after 24,096 events in role 93, whose row is exactly
`-65536*x86 -65536*x93`. All 743 final rows are checked, including owned zeros.

At a cut, let R map arbitrary residuals in all current 743 positions to final
public outputs. Reverse ADD updates a source response column by the exact
coefficient times the destination response column; SCALE multiplies its
column; owned resets drop their column. COPY uses the chosen ADD derivative,
retaining its owned response. Exact changes in absolute coefficients maintain
all 735 output row-l1 sums. The result is

```
max_cut ||R||_infinity = 135415/4.
```

The equality row is output 205 after 24,297 events, with 111 nonzero terms
retained in RESULT. Maximum exact entry denominator exponents over all cuts
are four forward and seventeen backward. Both whole endpoint matrices are
checked independently in the two directions.

The separately written peer uses ordinary Fraction arithmetic and no parent
imports. It exhausts all cuts again and obtains the same maxima, complete
maximizer rows, denominator witnesses and endpoints. These are author-side
independent implementations, not human or formal-kernel acceptance.

## 3. All intervals, including intervals ending before the final output

Final-output suffix bounds alone do not control perturbed intermediate ranges.
Use a separate all-interval majorant. Start e_r=0 in every position. At every
scalar step update

```
ADD/COPY d += q*s: e_d = max(e_d, e_s + ceil(log2(abs(q)))) + 1;
SCALE r *= q:      e_r = max(0, e_r + ceil(log2(abs(q))));
INIT/CLEAR r:      e_r = 0.
```

MOVE is logical identity. All actual coefficients are nonzero dyadic numbers.
For each row and every possible earlier starting cut, its interval row-l1
norm is bounded by 2^e_r. Indeed an ADD row norm is at most the previous
destination norm plus |q| times the source norm. The new identity interval
has norm one; this explains the zero floor for SCALE and owned resets.
Triangle inequality bounds all earlier starts simultaneously. Induction
therefore proves the invariant without enumerating quadratically many intervals.

The maximum computed exponent is 296, so every scalar interval is bounded by
Gamma=2^296. This is an upper bound, not an exact interval maximum. The analogous
denominator recurrence is max(d_d,d_s+den(q)) for ADD, d_r+den(q) for SCALE,
and zero for owned resets. It gives the valid uniform denominator exponent 54.
The independent appendix checks this recurrence and an exhaustive small fixture.

## 4. Canonical chart factors and arbitrary spectator records

Use component sup norm: the maximum of |Re z| and |Im z| over every coordinate
and every field. The retained canonical frame code is a monomial conjugate of
dim(F) normalized C gates. A C gate has coefficients (1+i)/2 and (1-i)/2;
its induced real-component row norm is at most two, as is its inverse.
P, quadratic D, X and scalar phases are exact permutations/sign rotations and
have norm one. For positive integer f, put N=2^f. Thus

```
||Phi_F||_infinity, ||Phi_F^-1||_infinity <= N^dim(F).
```

Each gate is applied factorwise to f complete columns; exterior real scalar
coefficients are applied once. No scalar sum is tensor-powered. Identity on any
number of complete spectators does not change this induced norm.

At semantic cuts, the physical matrix is diagonal(Phi_current) times the
logical scalar matrix times diagonal(Phi_initial^-1). The largest initial
chart has dimension five; all current/final charts have dimension at most nine.
The exact prefix bound is therefore 2^17*N^14 and the final-output suffix
bound is (135415/4)*N^18. Every physical semantic interval is bounded by
Gamma*N^18, with denominator exponent at most 54+18f.

A lowered native MOVE is monomial / rank-r Gaussian / monomial, r<=9. Its
normalized C factorization can be used for norm analysis, regardless of whether
the implementation uses a recursively supplied complete Gaussian job.
The actual old/new dimensions give prefix exponent at most twenty and suffix
exponent at most twenty-seven at native-factor interior cuts. For an arbitrary
interval with two such interior endpoints a safe bound is Gamma*N^36 and
denominator exponent 54+36f. An interval wholly inside one MOVE satisfies the
smaller direct bound N^9. These statements concern the declared native factors;
they do not bound unexamined internal bodies of a recursive child.

There is also a sharper bound using the retained active-fiber method. In the
maximum of the individual fields' Hilbert norms, unitary chart changes and
complete partial native factors are isometries. The exact scalar row-l1 bounds
therefore apply directly, without powers of N: the prefix and final suffix
constants are 2^17 and 135415/4, and every interval is bounded by 2^296.
These are not joint-state Hilbert norms over all fields.

For coordinate errors, fix an external spectator address. A local active fiber
has 2^(9f) complex coordinates. A component bound delta gives its field Hilbert
norm at most sqrt(2*2^(9f))*delta; an output component is at most that output
field's Hilbert norm. Thus a single conversion factor
`A9(f)=2^ceil((9f+1)/2)` bounds the local physical prefix/suffix/interval norms
by `2^17*A9(f)`, `(135415/4)*A9(f)` and `2^296*A9(f)`, respectively. This is
valid at complete C-factor/butterfly-pair cuts, including disjoint pairs partly
processed, which still form a unitary direct sum. A scalar scratch accumulator
is handled by its separate local guard, not described as a unitary field.
No factor for the number of fields or external spectator records is dropped.

The general unitary/fiber argument is credited to the retained Ross Richardson
and Adam Gall lineage, also used in `p104-retimed-internal-grid` and
`p104-retimed-error-recovery` for the older 358-input partial word. The new
binding here is the complete 735-input word, actual residual-preserving COPY,
exhaustive cut constants, all-interval range and full caller application.

## 5. Error layers and finite fixed integer ranges

There are two distinct applications; their costs must not be interchanged.

At completed-service interfaces, assume the retained Gaussian service returns
a complete field with component error at most delta. Ordinary dyadic scalar
linear forms are evaluated in a wider exact integer accumulator and rounded
once. Errors are injected after semantic instructions/complete Gaussian
returns, including an optional simultaneous input and output rounding layer.
The conservative layer count is K=25312. Actual native monomial adapters are
isometries. By linearity, even adversarial correlated errors obey

```
final component error <= K*(135415/4)*N^18*delta.
```

Since ceil(log2(K*135415/4))=30, delta=2^-p and
`p >= requested_output_bits + 18f + 32` suffice with slack. This specifies the
required child-return error ABI; it does not prove how that child implements it.

Alternatively, a literal flat C-butterfly realization has at most
`K(f)=21688+5894f` rounded layers, including input/output. For this mathematical
realization the bound is K(f)*(135415/4)*N^27*delta. Its direct-butterfly runtime
is NOT charged by, or substituted for, the recursively priced child invoice.

Both applications have a finite intermediate range, not just a final-error
bound. If input component magnitude is at most 2^b, p fraction bits are used,
and k=ceil(log2 K), every rounded native-factor state has magnitude at most

```
2^(b+17+20f) + 2^(k+296+36f-p).
```

Thus `I=2+max(0,b+17+20f,k+296+36f-p)` magnitude bits, plus a sign bit, suffice.
At service-only cuts replace 20/36 by 14/18. This uses the all-interval bound
for accumulated perturbations, rather than using a final suffix as a bound on
an intermediate state. An alternative is p>=k+296+36f+2, which makes that
noise term at most 1/4.

With the sharper active-fiber bound, put a=ceil((9f+1)/2). One may instead use
`p >= requested_output_bits+30+a+2` at completed services and
`I=2+max(0,b+17+a,ceil(log2 K)+296+a-p)` magnitude bits plus a sign. Literal
butterfly layers use their stated K(f). The earlier chart-product estimates
remain valid conservative alternatives; no runtime saving is inferred from
these smaller sufficient precision constants.

The largest scalar magnitude is 65537/2 and the largest dyadic denominator is
2^16. A fixed additional 35-bit exact-accumulator allowance covers numerator
multiplication, denominator alignment and addition before the one rounding.
It is a local arithmetic allowance beyond the stored-state range above; it is
not itself a global overflow proof. All widths and layer counts are fixed
functions of b,p,f, independent of data and spectator volume.

## 6. Scope of the application

This proves a concrete finite local source/error interface and explicit
coordinate range. It does not derive the recursively compiled all-size word,
price literal butterflies as recursive services, create a tape lowerer, or
prove analytic recovery. A complete caller application must additionally bind
all helper/main whole-job adapters, query scratch, routes, idles, boundaries,
parent parking, simultaneous stocks and the existing recursive error theorem.
Large constants are absorbed only by fresh outer input thresholds; they are
not silently absorbed into the efficiency gap at a fixed carrier N.

Credit Ali Romman, Gareth Davidson, David Arias, Cinna Davis, Cao Yifan, zxv,
Jacob Alan Sussman and the full geometry/native/compiler/precision lineage
retained in PR5551. New work prepared for thu-nmrc with substantial OpenAI Codex
assistance, including independent subagents. Apache-2.0.
