# Complete dirty endpoints with bounded live signs

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and scope

Consider a chronological word of L instructions on r independent roles.
The permitted instructions are rational ADD, signed QUERY, signed unary
APPLY and SWAP. An ADD is x_d <- x_d + c x_s. A QUERY is
x_d <- x_d + c z_j x_s. An APPLY is x_d <- z_j x_d. A SWAP exchanges
two roles. Here d != s, c is rational and each z_j independently belongs
to {+1,-1}. Repeated occurrences of a label use the same sign. All roles
have arbitrary initial values, and equality concerns their complete endpoint.

After instruction t, let B_t consist of labels whose first occurrence is
at most t and whose last occurrence is greater than t. Set

    k = max_(0 <= t <= L) |B_t|,       D = r^2+1.

An instruction containing a sign only once does not put it in either
adjacent frontier. Such an instruction still branches over both signs.

**Theorem.** Identity of the complete word at every sign assignment is
decidable deterministically using at most

    L * 2^(k+1) * D

candidate prefix updates and O(L * 2^(k+1) * D^3) rational arithmetic
operations. At each cut it retains at most 2^k * D actual prefix matrices.
If the word is not the identity, it returns an actual sign assignment
and hence a complete-endpoint counterexample. Rational bit complexity
is 2^k times a polynomial in the ordinary input size. In particular,
fixed r and bounded k give a polynomial-time exact test independently
of the total number n of sign labels.

The same test compares two words by appending the inverse of the second
to the first. The parameter k is measured on that concatenation, not
separately on each word. This qualification can matter substantially.

## Homogeneous prefix invariant

Let P be a complete r-by-r prefix matrix and define

    h(P) = (vec(P),1) in Q^D.

For every live assignment a on B_t, retain a set S_(t,a) of actual
prefix matrices together with their actual sign histories. Its invariant is

    span { h(P) : P in S_(t,a) }
      = span { h(P_t(e)) : e is any prefix assignment restricting to a }.

The right-hand set ranges over assignments to every label already seen,
including forgotten labels. At t=0 there is only h(I), so the invariant
holds. A basis needs at most D representatives; selection by exact
incremental Gaussian elimination can keep actual members of the set.
The normalized elimination rows are auxiliary data, never fake executions.

For a fixed next sign, left multiplication by the instruction matrix A
induces a linear map on homogeneous vectors,

    (vec(P),u) -> (vec(AP),u).

If the next sign is new, branch each representative with both choices.
If its label is live, its value is already specified by a. Constant
instructions do not branch. Apply the linear map to every representative.
Then restrict the sign key to B_(t+1), merging keys for labels that have
just reached their last occurrence. Taking the span of this union and
selecting a basis preserves exactly the displayed invariant. Forgotten
signs have no future occurrence, so this merger loses no future correlation.
No bound on the number of their possible histories is assumed.

At the last cut the frontier is empty. Define the linear map

    F(vec(P),u) = vec(P) - u vec(I).

Every complete endpoint equals I exactly when F vanishes on the final
span. It suffices to check its retained basis. Each retained vector is
h(P) for an actual assignment, so any failing basis member supplies an
actual counterexample. A differing column supplies a dirty input on which
the endpoints differ. This proves both decision and witness correctness.

The homogeneous coordinate is necessary for this implementation. Ordinary
linear span cannot distinguish the set {I} from {I,-I}. For example,
applying the same sign once to each of the five roles has endpoint zI.
Keeping only a nonhomogeneous basis can discard the negative endpoint.
The supplied semantic control requires the negative assignment to survive.

## Cost and exact arithmetic

There are at most 2^k keys before an instruction, and each has at most D
representatives. Each representative has at most two successors. Thus
there are at most 2^(k+1)D candidate updates per instruction, including
a sign occurring only once. Left multiplication costs O(r^3) operations
even for a general dense instruction matrix. The supplied elementary
updates cost only O(r). Incremental echelon reduction of a D-vector
against at most D stored rows costs O(D^2). These bounds give the theorem.
Only the previous and next layers, their elimination rows and their
actual witnesses need remain live. Besides input and schedule storage,
the space is O(2^k D^2) rationals and O(2^k D n) witness bits.

For completeness, this is also a bit-complexity claim, not just a unit-cost
field count. Let b bound the bit length of any input numerator or
denominator. Clear each instruction's denominators first. The product
of these denominators has O(Lb) bits, and products of r-by-r integer
matrices have entry length O(L(b+log(r+1))). Hence every actual prefix
has a polynomial-size rational representation. The homogeneous coordinate
has the same bound after clearing row denominators. Elimination entries
are ratios of minors of at most D such rows. The determinant expansion
bounds their bit lengths by a polynomial in D,L,b. Exact rational
arithmetic and independence tests therefore have polynomial bit cost.
Witnesses are n-bit assignments. Label indices themselves remain part
of the input encoding; sparse large indices can be renamed in order of
first occurrence before this mathematical algorithm.

## Native interpretation and comparison

This is the commuting-sign subclass specified in PR #5716, Section 1.
For the diagonal generator Z_j e_x=(-1)^(x_j)e_x, its f-fold tensor power
acts on an address tuple by the scalar

    z_j = (-1)^(x_j^(1)+...+x_j^(f)).

Every sign assignment is realized at f=1. It is also realized for every
positive f by using its binary address in the first tensor factor and
zero addresses in the remaining factors. Instructions preserve addresses,
so their complete endpoint is block diagonal with the scalar endpoints
just tested. The theorem therefore decides equality at every positive
tensor width in this exact subclass. This application uses the stated
sign semantics; it does not check another contributor's compiler.

ADD and QUERY are inverted by negating c; APPLY and SWAP are involutions.
Reverse the instruction order to invert a word. If P and Q are the two
endpoints, first executing the first word and then the inverse second word
has endpoint Q^(-1)P. It is I if and only if P=Q, on every sign assignment.
No zero role, erased output, independent resampling of repeated signs or
unpaid physical operation is introduced by this mathematical reduction.

## What is new here

PR #5716 explicitly asks for a useful restricted class with a tractable
complete-endpoint identity test. The contribution is the live-sign
restriction, the displayed source-grammar bound and the executable
counterexample-preserving test. It is a scoped answer to that question,
not a new general weighted-automaton equivalence principle or a claim
of priority for parameterized dynamic programming.

Reachable-span bases and retaining concrete witnesses are classical.
See Stefan Kiefer, [Notes on Equivalence and Minimization of Weighted
Automata](https://arxiv.org/abs/2009.01217), Section 2, especially
Propositions 2.1 and 2.2, and the Schutzenberger/Tzeng lineage cited there.
The adaptation here conditions the span on currently live signs, forgets
them only after their final occurrence and homogenizes complete matrices
to test an affine equality. The proof above is self-contained.

No small k is proved for the selected P104 caller, the CNF hardness
construction or general native affine/quadratic operators. Noncommuting
address maps and rounded arithmetic are excluded. There is no new kappa,
physical tariff, supplier admission or complete multiplication theorem.
