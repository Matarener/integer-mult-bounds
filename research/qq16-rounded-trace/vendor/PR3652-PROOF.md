# Independent polynomial and grid proof

This checks the sufficient numerical theorem of Nick Petalas's PR3303, head
`f9031ff1412c9a4e62a38306009ae9c334cfc34e`. It does not introduce that theorem
as a new construction. The input, tensor-native, bridge, cover and endpoint
premises are those stated in the README and the pinned source proofs.

## Independent representation

Put `t=lambda-1 >= 0` and `z=2^t`. Associate to each field a nonnegative rational
polynomial p and a finite family of integer affine grid exponents `(b,g)`:

```text
every real/imaginary component has magnitude <= 2^P h p(z),
every component is in h*2^(-max_(b,g)(g+b*t)) Z.
```

The known-zero field has an empty polynomial/grid family. Each of the 704
persistent input fields starts with p=1 and exponent 0; the eight private
fields start zero. Polynomials retain individual degree coefficients. There
is no assumption that different input fields or errors are independent.

Addition adds coefficient vectors and takes the union of grid families.
Deleting a line dominated in both slope and intercept by another line does
not change their maximum for t>=0. For a dyadic c=n/d in lowest terms,
multiply p by |c| and add `log2(d)-v2(n)` to every intercept. A zero result
has the canonical empty representation. This grid rule follows from exact
divisibility by powers of two, including negative coefficients and negative
intercepts. Owned CLEARs produce zero; no borrowed/data CLEAR is permitted.

The constant-product lowering forms shifted copies of the original integer
components and sums them before division. Each partial has magnitude bounded
by `|n| p(z)` and retains the original grid. The audit observes that bound,
the final integer numerator (with its stronger divisibility), and the divided
result. It therefore includes intermediates that a completed-scalar-only
ledger would miss.

## Native interiors at arbitrary depth

For sign epsilon in {−1,1}, one Gaussian coordinate line on x=a+ib, y=c+id
forms the four pair sums/differences and then

```text
(a+c-epsilon*(b-d), b+d+epsilon*(a-c),
 a+c+epsilon*(b-d), b+d-epsilon*(a-c)) / 2.
```

If each entry component is bounded by L, pair components are bounded by 2L,
cross numerators by 4L and outputs by 2L. Pair/cross additions preserve the
incoming dyadic grid; output halves refine it by at most one bit. This
argument is sign-independent. It concerns component capacity, not the
sharper Hilbert norm of a completed unitary line.

PR3303 PROOF.md's corresponding displayed second output is `(d+i*s)/2`.
The pinned source defines `C_q=(1+i)I/2+(1-i)T_q/2`, giving `(s-i*d)/2`
instead. Multiplication of that second output by i gives the displayed
variant. The distinction matters for the operator, but not for these
component magnitude/grid inequalities or operation counts. The source proof
file is pinned as provenance; exact sign-sensitive fixtures check the formula
used here. No predecessor source is edited.

At tensor depth lambda, a rank-one active-axis factor executes lambda such
coordinate lines, one in each layer. Before line j, earlier outputs multiply
the component envelope by at most `2^(j-1)` and refine the grid by j−1.
Consequently the following polynomial observations bound every intermediate
line, and the last row bounds all completed outputs:

| Observation | Polynomial | Grid family replacing `(b,g)` |
|---|---|---|
| Pair interiors | `2*z*p` | `(b+1,g)` |
| Cross interiors | `4*z*p` | `(b+1,g)` |
| Completed lambda-line factor | `2*z*p` | `(b+1,g+1)` |

For example j−1<=t and j<=lambda give both the pair grid and its magnitude
bound. Apply this rule r times for a rank-r recipe. The exponent is not a
lambda-fold repetition of the entire producer, and scalar coefficients act
once at their literal source locations.

Each authenticated nine-axis monomial has an exhaustively checked bijective
binary image and quarter-turn phase data, hence is a signed permutation of
real/imaginary components. Its tensor lift preserves the uniform grid and
magnitude. Each used full-cover action has an independently reconstructed
two-sided 73-axis owner inverse. Recover the old owner first, then undo the
owner-dependent XOR translation in every layer. Thus it is a bijection for
every lambda and preserves a bound uniform over owners. This does not
reprove the inherited native/bridge operator identities or cover closure.

## Source induction and constants

The new loader reads only pinned data files. It expands raw F0 and B1 program
records, visiting every retained core and sweep itself; original Python
loaders/expanders/dispatchers are not imported. The event hashes independently
agree with PR3303. Source-address hashes distinguish the actual program
locations. All 712 field representations survive the stage boundary intact.

Induction over the literal operations and the preceding local rules proves
the invariant at all primitive observations. The independently derived
certificate gives:

```text
53,118 events; 270,288 primitive observations;
maximum polynomial degree = 19;
global grid maximum = 71 + 19*t;
max_observation p(1) = 35714190970741142696015664337123072062513575/4
                    < 2^143.
```

For z>=1, nonnegative coefficients imply `p(z)<=p(1)*z^degree(p)`.
Every observed component is therefore strictly below
`2^P h * 2^(143+19*t)` in magnitude. With quantum
`q=h*2^(-71-19*t)`, each is an integer number of q units of magnitude strictly
below `2^(P+214+38*t)`. Signed width `W=P+215+38*t` suffices. Integer-product
partials and native cross numerators are observations too. Every exact right
shift has the required divisibility. No rounding, overflow or underflow
relative to this exact reference is required on the stated input domain.

These maxima describe the positive envelope, not sharp reachable amplitudes
or minimum grid widths. Small exact Gaussian tests corroborate the local
rules; the induction supplies the universal quantifier over lambda.

## Numeric reference bill and limits

The independent traversal prices every literal source event. Per N complex
coordinates, a scalar operation acts on 2N real components; a tensor monomial
pays 4N copies and at most 2N sign changes. A coordinate Gaussian line pays
4N real additions, 2N halves and 4N component copies. There are 11,076 active
axis factors, hence `110760*lambda*N` Gaussian operations. Only those factors
multiply by lambda. Literal scalar products, ADDs, private clears and
monomial counts do not.

Summing the independent numeric counters, including `2N+12` final reusable
scratch clears, gives `483082*N+12` at lambda=1. Subtracting `110760*N` yields
the complete stated numeric-reference expression
`(372322+110760*lambda)*N+12`. The 528 covers separately pay 4N conceptual
real-component transfers each. At most 712 complex fields, one reusable
complex cover buffer and twelve scalar words give `1426*N+12` numeric words.
Every published counter key is compared; diagnostic labels are not counted
as arithmetic operations.

For an actual recursive caller its cost must additionally include the cost
of each W-bit numeric operation, physical transfers and source access,
address/sign/control computation, instruction and layout preparation,
entry-format admission, owned/borrowed lifetimes and restoration, recursive
children and F17 consumption. Those functions are unknown here. This numeric
reference expression supplies neither their recurrence nor a favorable
complete supplier moment. Literal common-coordinate helper return and native
functional endpoint proofs remain inherited or outside the statement.
