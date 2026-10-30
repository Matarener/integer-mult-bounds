# Compact certificates with rectangular payload types

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and credit

Let K be a field. A finite set of types t has independently chosen
finite-dimensional spaces V_t, which may have dimension zero. Each arrow a
has a declared source s(a) and target t(a), and denotes an arbitrary linear
map X_a:V_s(a)->V_t(a). Different arrows are independent, including arrows
with identical endpoints. A register has one fixed type and an arbitrary
independent initial value. Scalar ADD and SWAP require equal register types;
SCALE acts within one register; QUERY adds c X_a v_src to v_dst with matching
types. APPLY is permitted only for an endomorphism of the register's type.
Every register is retained in the complete endpoint. Scalars are central.

**Typed bridge.** A program with r registers and q unary occurrences has
r+q dependency states. For two programs on the same registers, let
D=2r+q_left+q_right. Equality for every choice of the V_t and X_a is
equivalent to a reachable-row closure certificate with at most D rows.
Exact arithmetic finds either such a certificate or a shortest nonzero
typed coefficient path w of length k. In the latter case a literal
rectangular substitution with zero/one entries distinguishes the endpoints,
using dimension

    d_t = number of visits to type t along w,
    sum_t d_t = k+1.

Here k is at most the larger unary dependency depth of the two programs,
and at most D-1. Types not visited by w have dimension zero. If all type
spaces must be nonzero, add one unused coordinate to each unvisited type.
This is a constructive upper bound, not a minimum-dimension theorem for
arbitrary counterexamples.

The equal-space dependency compiler and closure method are zxv's
[PR5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), whose
proof is pinned in SOURCES.json. Its classical weighted-automata and
noncommutative PIT credit remains with Kiefer and Raz–Shpilka. Expanded
typed block-polynomial identities already occur in Philipp / mightyOil's
[PR1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294), following
Charles Bethin's PR1278. Krzysztof Wójt's PR5262 supplies a different,
inverse-aware equal-space model. No new general PIT algorithm, first typed
path algebra, or literature priority is claimed. The present contribution
is the typed compact interface, per-type path-witness construction, and
rerunnable implementation with complete dirty boundaries.

## 1. Typed dependency representation

Create one leaf atom x_i for each original register. Maintain each current
register as a scalar row of atoms of its own type. At a unary occurrence,
first read the entire old source row e. Introduce an atom z_j=X_a e, of
type t(a), with dependency row e supported on atoms of type s(a). APPLY
replaces its register row by the new unit row; QUERY adds c times that row.
Scalar operations update rows directly. This also specifies self queries:
they read the pre-instruction value. Dependencies point only to older atoms.
Thus exactly r+q atoms suffice without expanding paths.

Let U be the final register rows. Define T_a to have dependency row e in
row j precisely when atom j was introduced with label a, and zero elsewhere.
Let V project leaf atoms to their original input register and other atoms
to zero. Induction on the dependency order gives

    coefficient of w=a_1...a_k in endpoint (o,i)
        = (U T_a1 ... T_ak V)_(o,i).

Matrix product order is literal: QP applies P first. A row supported on
atoms of type t(a) becomes a row supported on type s(a) after multiplication
by T_a; a mismatched arrow gives zero. Therefore every nonzero path has
the declared endpoint types. Empty paths are identities within one type.

For a pair of programs take block diagonal transitions, concatenate their
final rows with a minus sign on the right, and stack their leaf projections.
The two compiled leaf copies project to the same original input roles.
They do not create additional independent payloads. This gives D states.

## 2. Closure certificate and decision

A certificate supplies reachable rows B_j=U_o T_w, an initial-span matrix H,
and closure matrices C_a satisfying

    U = H B,      B T_a = C_a B for every a,      B V = 0.

These finite equations imply U T_w V=0 for every path by induction. Typed
paths form the basis of the free path algebra. Evaluating each arrow in its
declared rectangular block preserves addition, scalar multiplication and
composable products, so all complete endpoint blocks agree in every dimension.

Conversely, if every typed coefficient is zero, the reachable row space is
annihilated by V and stable under all T_a. Choose a basis of reachable rows.
It has at most D elements and supplies H and C_a. The next section proves
that a nonzero coefficient contradicts universal equality, completing both
directions of the theorem.

The producer processes independent rows breadth first, starting with U's
rows, and enqueues every composable arrow successor. A dependent candidate
is expressed using earlier accepted rows of no greater path length. Its
successors are therefore spanned by their successors. Induction on length
shows no shortest nonzero coefficient is lost by rejecting dependent rows.
The search accepts at most D rows, so a discovered path has length at most
D-1. Acyclic atom dependencies also bound its length by the program's maximum
unary dependency depth. Exact elimination constructs all displayed coordinates.

The checker reconstructs the path rows and checks only the three equations;
it performs no elimination and does not need basis independence. A negative
certificate checks a nonzero coefficient and constructs the matrices below.
It does not certify shortestness. Shortestness is a property of the producer
and the proof, supplemented by explicit-word comparisons in the finite tests.

## 3. Rectangular path witnesses

Take a nonzero coefficient c in output o, input i and composable word
w=a_1...a_k. Let t_0 be the output type and t_j=s(a_j), so
a_j:t_j->t_(j-1) and t_k is the input type. For each t choose a basis

    {e_j : 0<=j<=k and t_j=t}

of V_t. These basis vectors are distinct even when a type repeats. Define

    N_a e_(j+1) = e_j if a_(j+1)=a,
    N_a e_l = 0 on every remaining basis vector.

Equivalently, N_a is the sum of the matching rectangular matrix units.
Every factor decreases the global path index by exactly one. Thus a product
N_u has its (e_0,e_k) entry equal to one exactly when u=w. Shorter products
cannot traverse k steps; longer products vanish. Repeated vertices and
repeated arrow labels do not create shortcuts because coordinates retain
their global indices. Consequently input e_k in register i and zero in every
other register gives discrepancy c in output register o at coordinate e_0.
This proves the displayed dimension formula. For k=0 all arrows are zero,
the visited type has one coordinate, and the empty coefficient is detected.

For a directed chain through distinct types every type must be nonzero for
its monomial to be nonzero. The construction uses exactly one coordinate at
each vertex. This observation does not assert a sharp general witness bound
when types repeat or different monomials interact.

## 4. Tensor substitution and executable boundary

A positive typed identity can be evaluated at X_a=G_a^(tensor f) for each
positive f, with register type space V_t^(tensor f). Rectangular composition
still commutes with tensor powers. Scalar c stays c, outside the tensor power;
the procedure never tensors an entire sum. This is an algebraic substitution
corollary, not native implementation or a complete supplier invoice.

The theorem is over arbitrary fields. The executable uses exact Q only and
rejects excess resource sizes. It admits at most sixteen registers, eight
types, sixteen arrows, and 128 instructions per side, hence D<=288. Input
scalar encodings have at most 160 characters and 512 numerator/denominator
bits. Certificate scalars have at most 4096 characters and 8192 bits. A
larger certificate is explicitly refused by the producer. The unbounded
field-operation theorem does not claim executable success beyond these caps.
Program validation rejects mismatched types instead of coercing spaces.

The checker shares the compiler, arithmetic, path reconstruction and witness
routine with the producer. Those components, the input transcription and
Python remain trusted. Explicit-word expansion and literal rectangular matrix
execution are separately implemented finite oracles. The proof is written
mathematics, not a proof-assistant theorem or independent human review.

No relations between arrows, affine offsets, external aliases, nonlinear
operations or rounded endpoints are covered. Dirty restoration is checked
algebraically because every role is retained. Physical storage, native
delivery, precision, all-size compiler uniformity and the complete signed
invoice remain separate obligations. No new kappa is claimed.
