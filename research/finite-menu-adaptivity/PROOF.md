# Finite-menu adaptivity for an exact linear endpoint

This scoped proof was produced by Nick Petalas. The polynomial root bound,
finite-union argument, Cartesian fiber bound and weighted matroid greedy
method are classical. The contribution is their explicit application to the
finite-template exact helper interface, with a bounded witness constructor
and a rank-sensitive finite-grid certificate. No priority is claimed for
those general mathematical methods.

Sagar Thakrar / thakrarsagar's [PR1133](https://github.com/CrocSwap/integer-mult-bounds/pull/1133),
retained `rational-lift-descent-seed95/PROOF.md`, already uses the same
N(d-1)+1 polynomial-avoidance bound for support descent. That bound is
credited and reused below, not claimed as new. The new application concerns
full endpoint menus; the support-descent theorem is not replayed or audited.

## Exact interface

Let K be an infinite field, d,m positive integers, and T:K^d -> K^m linear.
Fix a finite menu A_1,...,A_N of linear maps with the same domain and codomain.
A selector s:K^d -> {1,...,N} may be arbitrary, with no computability,
continuity or observation restriction. Its output is A_{s(x)}x. Coefficients
inside the A_j are fixed independently of x.

Every arbitrary initial helper coordinate belongs to the domain. Every
required dirty restoration coordinate belongs to the codomain. A fixed
program can have temporary scratch, provided its complete specified output
is a linear function of this domain and its required initial scratch state
is fixed. This theorem asserts no physical legality of any such program.

## Finite-menu obstruction

**Theorem 1.** The selector can satisfy A_{s(x)}x=Tx for every x in K^d if
and only if A_j=T for at least one j.

The reverse implication uses a constant selector. For the forward direction,
suppose every D_j=A_j-T is nonzero and choose a nonzero row l_j of each D_j.
The polynomial product P(x)=product_j l_j(x) is nonzero because K[x_1,...,x_d]
is an integral domain. A nonzero polynomial over an infinite field cannot
vanish at every point. This last fact follows by induction on the number
of variables, using the univariate root bound for each coefficient.
There is therefore an x with every l_j(x) nonzero. Each D_j x is nonzero,
contradicting the selector's claimed endpoint at that x.

An equivalent proof says that finitely many proper linear subspaces cannot
cover a vector space over an infinite field. This is a classical lemma;
its use here concerns a complete arbitrary-input endpoint, not the
information available to a branching controller.

**Cost corollary.** Fix any finite menu of globally legal programs for one
input/output contract. Let B be any allowed set of their complete invoices,
including physical charges already required by that contract. If a selector
uses only entries with invoices in B and achieves T on every input, one
fixed entry with an invoice in B already achieves T. This holds for a scalar
budget or for several simultaneous resource bounds. It proves no new lower
bound on the fixed programs themselves. It prevents finite-menu selection
alone from escaping an already established fixed-menu exclusion.

Apply the corollary only when the fixed entry is legal for the full input
domain. A native operation legal only on its selected branch does not meet
this premise. An instruction-count bound with a finite fixed-coefficient
alphabet gives finitely many words. A paid-call bound alone does not give
a finite menu if unbounded free arithmetic is allowed.

## Explicit rational counterexample

**Theorem 2.** Over Q, when every D_j is nonzero, some integer
0 <= t <= N(d-1) makes x(t)=(1,t,t^2,...,t^(d-1)) a counterexample to every
menu entry simultaneously. Every coordinate has magnitude at most
max(1,[N(d-1)]^(d-1)); for d=1 take x=(1) separately.

A chosen nonzero row of D_j gives a nonzero polynomial l_j(x(t)) of degree
at most d-1. At most N(d-1) distinct integers can be roots of any of those
N polynomials. The N(d-1)+1 tested integers contain a common nonroot.
Testing the entire D_j x(t), rather than just that row, is also sound.
The implementation stops at its first simultaneous counterexample. It
uses exact rational arithmetic and does not enumerate branch predicates.

The number of curve tests cannot be reduced in general for this curve and
test order. Take d=3, N=4, T=0, with the four scalar-output rows equal to
the coefficient vectors of (t-2j)(t-2j-1), j=0,1,2,3. Every t=0,...,7 is
a root of some row, and t=8 is a common nonroot. The returned vector is
(1,8,64). This sharpness example concerns general linear endpoints; it
claims no optimality of a physical helper program or of all witness methods.

## Rank-sensitive Cartesian-grid obstruction

Let S_i be nonempty finite subsets of a field K and s_i=|S_i|. Here K may
be finite. For a nonzero defect D_j of rank r_j, define

    W_j = max product_{i in B} s_i,

where B ranges over the r_j-element independent column bases of D_j.
Then

    |ker(D_j) intersect product_i S_i| <= product_i s_i / W_j.

To prove this, fix all coordinates outside one such B. The independent
columns in B make the remaining coordinates uniquely determined if a
solution exists. There are product_{i outside B} s_i outside assignments.
Choose B with the largest product to obtain the bound.

The union bound now gives **Theorem 3**:

    sum_j 1/W_j < 1

implies that some point of the Cartesian grid defeats every menu entry,
regardless of the selector. For equal sizes s this becomes
sum_j s^(-r_j)<1. In particular, N entries each having defect rank at
least r cannot cover such a grid when N<s^r. The proof also bounds the
fraction of successful grid points by min(1,sum_j 1/W_j).

The weighted basis can be found greedily: scan columns in nonincreasing
s_i order, accepting an independent column. This is maximum-weight basis
greedy for the column matroid with additive weights log(s_i). More directly,
after every prefix the greedy set has the rank of that prefix. Hence its
k-th accepted size is at least the k-th largest size of any independent
basis, and multiplying proves the required optimum. No numerical logarithms
are needed by the implementation. Zero-rank defects are excluded here;
an entry with D_j=0 is already a full exact endpoint.

The strict inequality is necessary. Over Q take T=I_3 and the two invertible
shears

    A_+(x,y,z)=(x,y,z+x+y),
    A_-(x,y,z)=(x,y,z+x-y).

Every point of {-1,1}^3 lies in the success set of at least one shear, but
neither shear equals I_3. Both defects have rank one, W=2, and the sum is
exactly one. They preserve the first two outputs even off the grid. Thus
discarding the arbitrary dirty third output would also invalidate the
complete-endpoint claim.

## Boundaries and implications for helper research

Finite fields do not satisfy Theorem 1. Over F_p the p+1 fixed invertible
shears

    (x,y,z) -> (x,y,z+x-a*y), a in F_p,
    (x,y,z) -> (x,y,z+y)

collectively implement I_3 under a suitable selector on every input. If
y is nonzero choose a=x/y; otherwise choose the final shear. Each individual
map is different from I_3. This example changes the field premise.

Finiteness also matters over Q. The shears with every nonzero rational
normal (a,b), changing z to z+a*x+b*y, form an infinite menu. For each
(x,y) choose (a,b)=(y,-x), except choose (1,0) at (0,0). One shear acts
as identity at each point, but no fixed shear is identity on all of Q^3.

For a finite-template complex helper proposal, write every full leaf map
and its required input/output coordinates before applying Theorem 1. If
all leaves miss the endpoint, arbitrary data-dependent branching cannot
repair that menu. Theorem 2 supplies a small exact failing input when the
maps are rational. Theorem 3 can obstruct a bounded-grid claim even over
finite fields. These results can stop this specific proposed escape route
before a physical implementation campaign.

Restricted reachable inputs, approximate endpoints, rounded arithmetic,
nonlinear leaf maps, infinitely many coefficient choices, extra retained
branch outputs and a changed consumer are outside the exact interface.
The theorem neither excludes these alternatives nor asserts they are free.
It does not establish the fixed maps, an actual selected P104 menu,
compiler closure, native costs, a complete supplier or a new kappa.
