# Independent Gaussian-domain and collector review

Clear1nsight, with substantial OpenAI assistance. This checker was derived
from the task's written proposal and the authenticated source word, native
recipe data and literal signed-floor definition. Its initial implementation
was completed before reading the primary `model.py` or `PROOF.md`. It imports
neither of those files nor any predecessor executable. This is a separate
implementation and mathematical review within the same assisted contribution;
it is not independent human review or proof-kernel verification.

## Source and execution boundary

`independent.py` authenticates all three input files against its own literal
SHA256 constants and exact byte lengths, with bounded reads. `WORD.json`
supplies the exact fifteen events, numbered
2025 through 2039 inclusive. `NATIVE.json.gz` supplies both separately archived
rank-seven recipes at events 2031 and 2033, including their four distinct
wrappers. `lifting.py` supplies the signed-floor convention and the input
address phase convention. It is authenticated but is not imported or executed.
The predecessor authors and exact source heads are recorded in `SOURCES.json`.

The checker implements an exact mathematical numerator oracle separately
from the integer floor map. Its finite replay concerns this authenticated
scalar-reference convention. It is not a C++ native build, a compiler
admission, a whole-word execution or a physical-owner implementation.

## Independent derivation of the domain

Let pi = 1+i. For an array on the r-dimensional Boolean cube, use its unique
multilinear expansion

    f(x) = sum_S a_S product_(j in S) x_j.

The coefficients are obtained by ordinary Boolean Mobius inversion. Define
B_r by `a_S / pi^|S|` being Gaussian integral for every S. The independent
encoder first multiplies coefficient S by `pi^|S|`, then applies the Boolean
zeta transform. Its decoder performs Mobius inversion followed by exact
Gaussian division. This is a different implementation strategy from a tensor
pair-sweep encoder. The two strategies describe the same explicit matrix E.

Write a coordinate pair as `(a, a+d)`. The exact C map gives

    (a + d/pi, a + d/pi + i*d).

In the normalized Newton coordinates `(c0,c1)`, this is

    (c0,c1) -> (c0+c1, i*c1).

The inverse is `(c0,c1) -> (c0+i*c1, -i*c1)`. These are integral invertible
Gaussian matrices. Tensoring them with the untouched coordinates proves that
each C_j and its inverse preserve B_r. The statement is an intertwining
identity `C_j E = E T_j`; it does not say `C_j E = E C_j`.

For necessity, suppose f and all products C_T f, with T a subset of the
coordinate set, take Gaussian integral values. Evaluation at the all-zero
address yields

    (C_T f)(0) = sum_(S subset T) a_S / pi^|S|.

Mobius inversion on the subsets T expresses each `a_T / pi^|T|` as an integer
linear combination of these integral evaluations. Thus f belongs to B_r.
This proves the exact maximal domain for all partial-coordinate products.
Any integral module invariant under every C_j is a submodule of B_r, and the
previous construction shows that B_r itself is such a module. No maximality
for a single gate, one completed word or input-dependent cancellation follows.

The checker preserves the distinction with `f = pi*x0*x1`. Its four values
are `(0,0,0,pi)`, which lie outside B_2. Each single coordinate step at the
entrance is exactly integral: C_0 gives `(0,0,1,i)`, and C_1 gives `(0,1,0,i)`.
A C_1 step following C_0 has a nonintegral exact result and the
literal floor pair rejects the equality check. Single-gate integrality is
therefore insufficient for the proposed phase-complete contract.

## Why signed floors are exact on this domain

For an integer t, put `epsilon(t) = t - 2*floor(t/2)`; it equals zero or one,
including for negative t. Put `d = a-b` and let J be multiplication by i
(or by -i for the inverse). The second output of the literal pair differs
from the exact C output by

    (epsilon(Jd) - epsilon(d))/2,

component by component. Rotation exchanges the two parity bits; signs do
not change parity. The difference vanishes exactly when the real and
imaginary components of d have the same parity. This is equivalent to pi
dividing d. The first output has the same defect because both versions then
add Jd.

This proof applies to every signed integer entrance satisfying the condition.
It justifies the all-input exactness claim; tests on basis columns alone
could not establish it for an arbitrary nonlinear floor map. The executable
also checks all 450 combinations of the two directions and real/imaginary
differences in [-7,7], including negative odd values.

## Exact wrapper closure

The source sends address x to A*x+b over F_2 and multiplies its value by a
power of i evaluated at the input x. Its exponent consists of a global
constant, linear coefficients modulo four, and twice a quadratic Boolean
polynomial. All four source wrapper permutations and phases are reconstructed
on all 512 addresses; each map is checked to be a bijection.

An invertible affine Boolean map is generated by bit swaps, bit flips and
CNOTs. The phase alphabet is generated by global i, S_j=`i^x_j`, and
CZ_jk=`(-1)^(x_j*x_k)`. In normalized Newton coordinates the nontrivial
two-coordinate formulas, in coefficient order `(a,b,c,d)` for
`1, x, y, xy`, are

    CNOT_(x -> y): (a, b+c+pi*d, c, -(1-i)*c-d)
    CZ:           (a, b, c, i*a-(1-i)*(b+c)-d).

For one coordinate,

    X: (a,b) -> (a+pi*b, -b)
    S: (a,b) -> (a, i*a+i*b).

Each formula is Gaussian integral. X, CNOT and CZ square to the identity;
S has order four. Bit swaps merely permute equal-degree Newton coefficients,
and global i is a unit. This proves preservation in both directions for the
entire literal wrapper alphabet. The independent checker reconstructs every
displayed matrix from its complete small coefficient basis and verifies the
stated orders. It does not assume that an arbitrary Boolean permutation or
arbitrary phase preserves B_r: the cubic phase `(-1)^(x0*x1*x2)` applied to
the constant-one vector is a rejecting control.

The earlier phase witness `(1,i)` is accepted here. Its normalized Newton
coefficients are `(1,i)`, and C sends it exactly to `(pi,0)`. This supplies
the changed premise relative to a lattice lacking phase closure.

## Actual collector verification

The forward recipe U and the separately archived return V are used as
written. The checker first applies their exact rational numerator matrices
to all 512 standard complex coordinate vectors. Every column satisfies
`VU = I`, with the common denominator `2^14` handled as an integer identity.
These maps are complex linear, so the complete complex basis proves this
finite operator identity on all complex arrays.

It then runs the literal signed-floor recipes on 1,024 signed generators of
the full Z-module B_9: one real and one imaginary encoder column at each
of the 512 coordinates, with alternating signs. Every one of the 3,670,016
pair applications is compared with the separate rational pair formula;
every outbound array is decoded successfully, and every return equals its
entrance exactly. The signed-floor theorem and the generator closure proof,
rather than extrapolation from these fixtures, justify the universal claim.

Three additional dense signed cases supply five nonzero source arrays and
an arbitrarily dirty query in B_9. They execute the exact source event list,
check Newton divisibility after each array operation and each transport
prefix, and compare the query with `query + U*sum(sources)`. All five sources
are checked unchanged. The private C is exactly zero before the ERASE event.
These verification snapshots are not claimed as storage in an efficient
execution of the collector.

Two composition controls preserve the lattice but fail the endpoint: replacing
the return recipe by the forward recipe, and multiplying one actual return
wrapper by i. Both are rejected when the private field fails to erase. Thus
lattice preservation is not being substituted for source-operator correctness.

## Interfaces and excluded conclusions

The local source uses eleven unit-coefficient whole-array ADDs, two rank-seven
transports, four literal wrappers, one private zero allocation and its exact
erasure. The current checker does not replace the separately archived V by a
paired inverse when counting those wrappers. The actual execution-order cycle
counts are 64, 128, 160 and 64, totaling 416. The inherited one-zero-scratch
cycle implementation therefore uses 2,464 swaps. A full cost ledger must retain
source access, query writes, arithmetic, permutation execution and private
storage, plus any encoder, decoder or physical movement actually needed by a
caller. Unit ADD closure does not provide the preceding source arrays for free.

For an integral array z, `z/4` belongs to B_r exactly when z belongs to 4B_r.
The rank-one example `z=(4,0)` is in B_1 while the integral array `z/4=(1,0)`
is outside it. The checker rejects its attempted exact C step. Constancy in
the other coordinates lifts this counterexample to B_9. This is an interface
restriction; the selected fifteen-event collector does not execute a quarter
ADD.

Encoding arbitrary coefficient data by E changes the logical map to
`E^-1 U E`. The explicit `CE != EC` control prevents a claim of an unchanged
logical caller merely from having an invertible codec. No preparation of
this entrance by the preceding full word, downstream consumption, physical
owner realization, recursive tariff, precision improvement, supplier
admission or new kappa is established by this local theorem.

## Replay

From a repository containing the authenticated input paths:

```sh
python3 -I -O -B research/p104-clifford-exactness/independent.py
```

Alternatively pass `--repo /path/to/source-root`. The module API is
`verify_independent(word_path, native_path, lifting_path)`, returning a
deterministic JSON-compatible receipt without writing files. All contracts
use explicit exceptions and remain active under `-O`. The receipt contains
source hashes, exact generator matrices, complete-column hashes, actual
wrapper plans, dense collector checkpoints and the rejecting controls;
it contains no absolute path, wall-clock or timing-dependent field.
