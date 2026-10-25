# Paired complex endpoints, exact gauges and the signed B4 controller

This package verifies the chosen paired endpoints on all 112 frozen ports,
456 explicit canonical-to-chosen phase gauges, and both rank-7 residual
children at each order-three partner pair. It also proves the signed B4
controller over the Laurent ring and separately executes exact native
convolution models in dimensions 11 and 12.

These are endpoint and controller results. They do not supply a compatible
cheaper dirty local word, a complete scalar/native invoice for such a word,
or an improved multiplication bound.

## Source and input boundary

The scientific source is commit
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The actual native conventions,
compiler and signed recipe retain the PR425/433/523/531 and supplier
ancestry identified by the preserved original sources. New material has
substantial OpenAI Codex assistance and is Apache-2.0.

The checker requires four explicitly named, byte-authenticated inputs:

| Input | SHA256 |
|---|---|
| `CANONICAL-WORD.json.gz` | `addf598581d2a20e13d0c18110607515ad90b06125616a2349e53a47bb5b6c80` |
| `GLOBAL-TEMPLATE.json.gz` | `5b913207775fcd87090cfa8776e8bd2bb872426923345fe1a1a4e1ea84bfae2c` |
| historical `ORDER3-GEOMETRY.json` | `e5b1309edbeb5da14d79f1edf134c95593061666b796b5d532f00a4262533dd0` |
| `clifford_exact.py` | `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962` |

The compressed source files lie under the pinned
`research/kernel92-frame-composition/vendor/pr531/inputs/data-base/split-centres/`.
The compiler lies under that vendor's
`vendor/clifford/clifford_exact.py`.
The bytes authenticated for the compiler are exactly the bytes executed,
with `optimize=0`; outer Python `-O` therefore cannot remove its assertions.

The new checker consumes only the ports, the complete signed B4 recipe,
and the ordered 112 `(P,Q,R)` geometry contracts. It independently checks
each contract's full nine-vector orthonormality. Its contract digest uses
UTF-8 `json.dumps(contracts,sort_keys=True,separators=(',',':'))` with no
trailing newline. The companion geometry checker independently reconstructs
the same ordered contracts and digest. No active sibling module is imported.
The historical geometry's edge census and source-batched dynamic program
are not replayed by this endpoint checker.

The original `DATA-PHASES.json`, SHA256
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`,
was hash-only provenance in the historical endpoint source. It is not a
runtime input or a semantic replay claim here. Original proofs, scripts
and receipts are preserved separately, including their source-credit chain.

## Exact phase convention in every dimension

Address translations act on functions on `F_2^n`. Write X_v for
translation by v. The retained native line gate is

```
C_v^s = ((1+s i)I+(1-s i)X_v)/2,       s in {+1,-1}.
```

It fixes the uniform vector and satisfies `(C_v^s)^2=X_v` exactly.
On the translation character indexed by x it has eigenvalue 1 when
`v·x=0`, and `s i` when `v·x=1`.

Let U have an orthonormal binary basis `u_1,...,u_d`, so its orthogonal
projector is `P_U=sum_j u_j u_j^T`. Define

```
T_U = H diag(i^wt(P_U x)) H,
```

where H is normalized Walsh-Hadamard. This is an exact Gaussian-dyadic
convolution operator: the two Walsh factors give denominator `2^n`.
Every input field, source and target is arbitrary; no clean-input promise
is used.

For binary vectors a,b,
`wt(a+b)=wt(a)+wt(b)-2 wt(a intersect b)` as integers. If a and b are
orthogonal over F2, the intersection has even size, so their weights add
modulo four. Applying this repeatedly to the orthonormal basis expansion
gives

```
wt(P_U x) = sum_j wt(u_j) (u_j·x) modulo 4.
```

Consequently

```
T_U = product_j C_(u_j)^(s_j),
s_j = +1 when wt(u_j)=1 modulo 4,
s_j = -1 when wt(u_j)=3 modulo 4.
```

The uniform character has eigenvalue 1 on both sides, so there is no
undetermined global scalar. Orthogonal sums satisfy
`T_(U direct_sum V)=T_U T_V` with these exact representatives.

The characteristic vector is `c(U)=sum_j u_j`. Squaring the character
eigenvalues gives `T_U²=X_c(U)`. The phase definition and characteristic
vector are independent of the chosen orthonormal basis because they are
defined by the projector. The factorization above is stated for spaces
admitting that basis, as all finite contracts here do.

## Paired endpoints and the physical native source

Take mutually orthogonal nondegenerate P,Q,R whose direct sum is the
ambient space. The source entrance and terminal are P and P+R; the
target entrance and terminal are Q and Q+R. Exact phase additivity gives

```
T_(P+R) T_P^-1 = T_R,
T_(Q+R) T_Q^-1 = T_R.
```

Define `K=T_Q T_P^-1`. A hypothetical exact dirty forward shear therefore
has the boundary

```
[ T_R       0  ].
[ T_R K     T_R ]
```

The endpoint identities themselves do not construct that dirty shear.
All T operators commute because they are diagonal in the same translation
character basis. Hence

```
T_R K = T_I T_P^-2 = T_I X_c(P),
K^-1 = X_(c(P)+c(Q)) K,
X_c(P) K = T_(P+Q),
X_c(Q) K^-1 = T_(P+Q).
```

The backward call therefore uses the coefficient `-K^-1`, not `+K` or
`-K` without its characteristic translation. Conjugating the source
bank of a `-K` shear by `X_(c(P)+c(Q))` before and after the call implements
the required inverse kernel. Those are actual paid address operations.

The retained physical source gate is `C_p^+`. For a one-dimensional
chosen entrance P,

```
T_P (C_p^+)^-1 = I       if wt(p)=1 modulo 4,
T_P (C_p^+)^-1 = X_p     if wt(p)=3 modulo 4.
```

All 112 retained p have the second case. The receipt emits and verifies
all 112 nonzero adapters and executes an omitted-adapter defect at each
port. They are not free changes of notation. If another physical entrance
also uses a positive native gate, its analogous conversion must likewise
be supplied and paid.

The checker independently computes projector kernels in local dimension
9 at all 112 ports for common dimensions k=2 and k=3. These are 224
contracts in explicit orthonormal charts, with 672 comparisons between
the independent projector definition and signed native products. The
residual dimensions in these auxiliary charts are 7 and 6 respectively.
These charts are separate from the order-three partner contracts, whose
P and Q are each one-dimensional and whose R always has dimension 7.

## Canonical frames are separate literal operators

Let `A_U` be the pinned compiler's actual `canonical_frame(U)`. Define
the left adapter

```
M_U = T_U A_U^-1.
```

For the finite selected family the checker reconstructs all distinct
axis lists among P,Q,P+R,Q+R,R. There are exactly 456. It proves rank zero
for every M_U, emits its affine address map, quadratic and linear phases,
global Gaussian-unit phase and literal inverse, and verifies

```
M_U A_U = T_U,
M_U^-1 T_U = A_U.
```

This is a finite verified property of the selected canonical
representatives. No theorem that arbitrary compiler charts agree with
the chosen phase is assumed.

Complete signed Pauli images determine a Clifford operator up to scalar:
the quotient of two such operators commutes with every Pauli and is
therefore scalar. Comparing the exact nonzero zero-address column fixes
that scalar. Every adapter, inverse bridge and child lowering is checked
by both data, including actual global phase.

For each canonical source or target residual, the checker additionally
verifies the ordered bridge

```
A_U A_E^-1 = M_U^-1 T_R M_E.
```

Thus an unfused implementation first applies M_E, then the chosen rank-7
child, then M_U^-1. Across the 224 separate residuals this is 448
canonical-interface map occurrences. Each chosen rank-7 child itself has
two explicit monomial lowering legs, giving another 448 occurrences.
The 456 distinct recipes are not a claim that a complete program pays
each recipe only once. Actual occurrences, inverse occurrences, physical
source adapters, reuse and any justified fusion belong in the eventual
word's invoice.

The two chosen residuals at each order-three pair are compared exactly
with T_R and lowered independently. Both lowerings have native rank 7,
for 224 full-phase residual-child checks. Arbitrary sources and targets
retain their declared invertible diagonals; unchanged physical source
values are not claimed.

Every monomial recipe denotes
`|x> -> i^phi(x) |Gx+b>`. It requires paid address and phase work.
It may be implemented with a charged destination array, or in place by
phasing coordinates and rotating permutation cycles with coordinate
swaps. The latter uses at most `N-1` swaps per map, each three complex
ADDs and one NEG, plus up to N Gaussian-unit multiplications and paid
cycle discovery. Generic cycle-leader discovery can cost quadratic
binary-address work; rank zero supplies no free physical scan or storage.
No complete wrapper execution schedule, prefix norm or rounding bound
is supplied here.

## A universal signed B4 identity

The checker reads and executes every event of the complete frozen B4
recipe. There are nine local calls, alternating

```
forward, backward, forward, backward, forward,
backward, forward, backward, forward,
```

and nine bridges with coefficients

```
1,-1,1,-1,1,-1,1,1,1.
```

A local forward call adds `z x` to y; a backward call adds `-z^-1 y`
to x. A bridge from pair b to pair a with coefficient e performs
`x_a += e x_b` and `y_b -= e y_a`. Every one of the eight input banks
starts as an independent basis column.

Exact accumulation over `Z[z,z^-1]` leaves each pair at

```
(-z^-1 y, z x).
```

The complete Laurent endpoint matrix is emitted, and all 64 entries
are compared coefficientwise. This finite symbolic calculation is an
identity in the Laurent ring, rather than testing several scalar z
values. Substituting any invertible endomorphism K gives a ring
homomorphism because the integer coefficients are central and all powers
are powers of the same K. Therefore the identity holds for arbitrary
invertible K on any module where these signed additions are defined.
No `K²=I`, commutation of unrelated stage kernels, or finite address
dimension is assumed.

The pair swap and sign turn the endpoint into `(Kx,K^-1 y)`.
The terminal translations X_c(P) and X_c(Q) then turn both factors
into `T_(P+Q)`. The code executes the swap as three ADDs and one NEG,
followed by the separate required NEG; its unfused invoice deliberately
retains both negations. It also executes both terminal translations.

## Separate native B4 models and the all-dimension argument

The finite native models have common dimension k=2 or k=3 and exactly
one fresh residual direction at each of the nine stages. Their ambient
dimensions are therefore 11 and 12. The exact Gaussian-dyadic engine
executes all 8-by-8 convolution kernels, using the actual C_v signs and
the same source recipe. Translation invariance then gives every input
address column: 16,384 and 32,768 columns respectively. These are
all-input operator identities by convolution, not that many separately
executed full-program simulations.

Before a bridge the model explicitly advances both participating pairs
to the same residual frontier. Each local call advances its two fields
by its own stage direction, and idle direction applications supply the
rest. After all bridges, each of the eight fields has received all nine
residual directions. The model's complete output is the native full
transform on every bank. Its kernel entries, exact denominators and
finite model event counts are retained.

The written extension is conditional on the stated local interfaces.
Let the nine residual spaces be mutually orthogonal and orthogonal to
P+Q, with actual chosen operators `T_(R_j)`. They commute with K and
with each other. At a pair's stage-t frontier its common residual factor
is `product_(j<=t) T_(R_j)`. Aligning that factor before each bridge
lets it factor out of both bridge updates. Induction through the exact
Laurent word therefore gives the same endpoint with every bank carrying
all nine residual factors. After the terminal translations, phase
additivity gives the full transform on

```
(P+Q) direct_sum R_0 direct_sum ... direct_sum R_8.
```

This is valid for arbitrary residual dimensions under those exact
interface and alignment premises. Any physical relocation from a local
orthonormal chart to a fresh residual block must preserve its actual
signed native factors. Negative factors require the explicitly recorded
translation alignment; the orthonormal charts and those adapters are
not declared free.

No 65-dimensional or 56-dimensional supplier is executed. In particular,
the small models do not certify a changed compensation factory, helper
chronology, native source access or a global caller at those dimensions.
The hypothetical local shears in the controller are charged as abstract
local calls; computing K inside the convolution model is not an
implementation of that shear at a claimed physical cost.

## Executed defects, deletion controls and reproduction

All defects run through production acceptance predicates. The controls
include all 112 omitted physical-source translations; a global i error
in an actual left-gauge operation; an omitted left-gauge operation;
three Laurent inverse/sign/bridge defects; and backward-translation,
backward-sign, terminal-translation and bridge-sign defects in each of
the two native models. A rejected Gaussian defect includes a nonzero
exact coordinate difference; a Laurent defect includes a nonzero
integer coefficient at a named power and bank pair.

The global-i defect preserves the signed Pauli data. Deleting the phase
comparison at the same production predicate causes actual acceptance,
which the rejection oracle detects as `expected_rejection_missing`.
Only the intended error is caught; unexpected acceptance occurs outside
the catch. An inequality between manually corrupted saved outputs is
not counted as an executed control.

Run the portable checker with a fresh output path:

```
python3 check_endpoints.py --ports CANONICAL-WORD.json.gz \
  --template GLOBAL-TEMPLATE.json.gz --geometry ORDER3-GEOMETRY.json \
  --compiler clifford_exact.py --output /tmp/fresh-ENDPOINT-CHECKS.json
```

Existing outputs are rejected before audit work. Complete normal and
optimized receipts must be byte-identical. The receipt contains no
output-location or timing fields. Finite exact replay, the Laurent-ring
proof, the written all-dimension operator argument and the separate
geometry/contact proof remain distinguishable; none is a formal-kernel
certification.
