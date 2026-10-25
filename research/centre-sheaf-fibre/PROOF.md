# Exact full kernel on the 4,080-owner block

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.

This is a scalar-information theorem for the inherited selected calls-0/4
observation model. It is not a native programme, physical sharing construction,
recursive tariff, or multiplication theorem. The finite premises below were
reconstructed in fork-hosted CPython 3.12.15 runs at scientific head
`403ef45de40e41baaf8b1f4cfddaf3ba1d57af1c`. The original source archive and
predecessor implementations are unchanged.

## 1. Fixed observation contract

Let R be the selected 8-by-112 rational reader matrix and let rho_p be its
112 involutory owner routes. The complete routes act on 73 binary coordinates;
they preserve a 17-coordinate active space and fix 56 spectators. Computation
on the active block is therefore faithful, not a projection that identifies
otherwise different routes.

Set a=0, b=6, c=85 and

    H = <rho_a rho_b, rho_a rho_c>.

Arrays x(g,p) are arbitrary rational scalars on H times the 112 ports, and
are extended by zero to all other owners. The two observations are

    Sx(g)  = sum_p R_p x(g,p),
    4Tx(z) = sum_p R_p x(z rho_p,p).

Here R_p is a column. Every touched output owner z is retained, including
owners outside H. Dropping those output equations changes the problem.
The inherited source slice and common-frame/constant-payload interpretation
remain assumptions of its physical application. No statement about arbitrary
704-field native states or the complete chronological word follows.

The separately reconstructed finite premises are

* |H|=4,080 and rank_Q(R)=8.
* R_a-R_b-R_c=0, and these three columns have rank two.
* The right cosets H rho_p partition the ports into the single class
  {0,6,85} and 109 singleton classes. Every singleton column is nonzero.
* The undirected compatibility graph on H, with right multiplications by
  rho_a rho_b and rho_a rho_c, is connected. It has 8,160 edges and a
  certified 4,079-edge spanning tree.

The primary certificate checks all 112^2 ordered coset comparisons, using
binary column matrices and rational ranks. The second implementation uses
its own archive parser, forward coefficient propagation, binary row matrices,
left-generated group closure, and nonzero minors modulo 101. Integrality of R
is checked before the modular rank test. A nonzero minor modulo 101 proves
the corresponding rational lower rank; the displayed exact relation gives
the matching upper rank for the triple.

## 2. Coset elimination theorem

For involutions, H rho_p=H rho_q exactly when rho_p rho_q belongs to H.
The coordinates contributing to an output z belong to a single such class.
For a class C, an output equation has the form

    R_C (x(z rho_p,p))_{p in C} = 0.

If R_C has independent columns, all its incoming coordinates vanish. Every
source coordinate x(g,p) appears at the output z=g rho_p, so this eliminates
that entire port class, not just one output sample.

For the selected H, 109 singleton classes consequently eliminate
109*4,080=444,720 variables. The only possible nonzero coordinates are those
on ports a,b,c. The source equations then force, uniquely at each g,

    (x(g,a),x(g,b),x(g,c)) = alpha(g) (1,-1,-1).

At z=g rho_a, the remaining output equation is

    R_a alpha(g)
      - R_b alpha(g rho_a rho_b)
      - R_c alpha(g rho_a rho_c) = 0.

Independence of R_b and R_c forces all three amplitudes to agree. Connectivity
makes alpha constant on H. Conversely, any constant amplitude satisfies every
source and output equation. Thus, with v equal to (1,-1,-1) on these three
ports at every owner of H and zero elsewhere,

    ker(S) intersect ker(T) = Q v.

This establishes the FULL 112-port kernel. The predecessor's existence of v
and its single-triple census alone did not establish this equality. Merely
checking which individual routes lie in <rho_a,rho_b,rho_c> is insufficient;
the outgoing right-coset comparisons are the essential additional test.

## 3. Cellular sheaf interpretation

Take the bipartite graph of source owners and touched output owners, with a
port edge from g to g rho_p. Give source vertices stalk ker(R), an output
vertex in class C stalk ker(R_C), and every edge stalk Q. Restriction maps
are the corresponding coordinate maps. A global section is exactly a choice
of all x(g,p) satisfying both observation equations.

The independent output stalks are zero. Eliminating their incident coordinates
reduces every remaining source and output stalk to the same one-dimensional
triple relation. Dividing each nonzero restriction by its relation coefficient
makes edge compatibility ordinary equality. The reduced graph is connected,
so its global sections form one copy of Q.

Equivalently, eliminating output amplitudes leaves the constant sheaf on the
4,080-vertex compatibility graph. Its zeroth cohomology has dimension one.
This is a local-to-global calculation, not a claim that scalar consistency
certifies chronological access, native phases, or a physical implementation.
No assertion about higher cohomology of the unreduced sheaf is needed.

## 4. Sharp information dimension and proper subblocks

There are 112*4,080=456,960 scalar variables. S has rank 8*4,080=32,640, hence
its kernel has dimension 424,320. The theorem gives

    rank(T restricted to ker(S)) = 424,319,
    rank(stack(S,T)) = 456,959.

Suppose extra LINEAR observations L allow recovery of all T from (S,L), even
by an otherwise arbitrary nonlinear decoder. Equal (S,L) observations must
give equal T, so ker(S) intersect ker(L) is contained in ker(T). Rank-nullity
on ker(S) therefore requires at least 424,319 additional scalar observations.
A linear quotient of ker(S) by Qv attains that count abstractly. This existence
statement supplies neither an efficient decoder nor a recursive cost.

For every proper subset B of H, extend a supported common-kernel vector by
zero to H. It must equal t v. Since v is nonzero at every owner of H and B
omits at least one owner, t=0. Therefore all proper subblocks have zero common
kernel and require 104|B| additional linear observations under the same
whole-output contract. The result also holds on left translates of H.
It does not decide equally sized arbitrary owner sets, unions of several
cosets, other triples' subgroups, or the global support minimum.

## 5. Primitive integer fibres and their limitation

R is integral. Stack S and 4T into an integer matrix A. Since v has a coordinate
one, every integer vector in its rational kernel is an integer multiple of v.
Thus ker_Z(A)=Zv. Every nonempty nonnegative integer fibre is precisely

    {n0+t v : t is an integer and lower <= t <= upper},
    lower = max_{v_i=1}(-n0_i),
    upper = min_{v_i=-1}(n0_i).

All zero coordinates of v remain fixed. Unit moves by v and -v connect this
interval, so {v} is a Markov basis, with both move directions permitted.
For the polynomial-to-Laurent-monomial map specified by A, the toric ideal
is principal, generated by z^(v+) - z^(v-). Indeed, every integer kernel
relation is t v, and a difference of positive integer powers factors by that
binomial. This is classical rank-one lattice-ideal reasoning.

The primitive move has 4,080 positive and 8,160 negative unit entries, hence
support 12,240 and sum(v)=-4,080. Adding a fixed total-count row therefore
kills the kernel over Q and Z. More generally, an extra linear resource row
w retains it exactly when w*v=0. This explicitly prevents interpreting an
information-preserving coefficient move as a free legal scheduling move.
No operation-count, ownership, or conservation constraint is silently dropped.
These fibre moves preserve both observations at each move. A physical programme
may temporarily leave the fibre and later restore its outputs; such programmes
are not excluded by this integer statement.

## 6. Decision, evidence, and credit

The known witness spans all invisible directions on this fixed block. Its
abstract information saving is exactly one out of 424,320 coordinates, not
an unexplored large family of savings. No recursive child is shown removable.
The decision is NARROW and COMPLETE for this information question. A larger
construction requires a named changed block or consumer, actual returned-state
contract, and a favourable fully charged cost screen before expansion.

The source-dependent primary and independent implementations passed normally
and under -O on GitHub's fork-hosted Ubuntu 24.04.5 / CPython 3.12.15 runner.
The source archive, both relevant member hashes, query ordering, H=R/4,
faithful active restriction, coset partition, and graph premises were checked.
The independent direct residual calculation checks all 4,080 touched outputs
of v and detects exactly three failures when one owner is removed. Eight
small-group tests cover full matrices, all six nonempty proper subblocks,
512 binary coefficient assignments, signs, routes, and the total-count row.
These are separate same-author implementations, not independent human review.
The committed receipt hook additionally compares typed results and rejects
receipt/JSON mutations. Its final publication replay is recorded on the PR.

Credit Matarener/#3656 for the subgroup and witness; David Charbonneau/#3147
for the investigation; Ross Richardson/#3071 for the model and extractor;
Sagar Thakrar/#3291 and Sudarsh Chaturvedi/#3168 for the corrected graph/census
lineage; ywz65 and Aaron Wang/navinor for the observation/centre lineage; and
all original selected-source notices. The earlier circle-elision proposals
are not reopened; #3151 and #3194 retain their distinct obstruction credit.

The mathematical formulation uses established theory from Jakob Hansen and
Robert Ghrist, Toward a spectral theory of cellular sheaves, Journal of Applied
and Computational Topology 3 (2019), 315-358, DOI 10.1007/s41468-019-00038-7;
and Persi Diaconis and Bernd Sturmfels, Algebraic algorithms for sampling from
conditional distributions, Annals of Statistics 26(1) (1998), 363-397,
DOI 10.1214/aos/1030563990. No literature-wide novelty is claimed.
