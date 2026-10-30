# A paid floor for confined two-clique relay networks

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Let G=A disjoint-union B be a finite set of binary port labels in a binary
space with a symmetric bilinear form, with both classes nonempty. Assume

    <p_i,p_j> = 1 if i,j belong to the same class, and 0 otherwise.

In particular every label has self-pairing one. Let W be the span of G.
All source coordinates are independent over Q. No source is initialized to
zero. Write e_i for the unit source row and X(g)=span_Q{e_i:p_i in g}.

A finite ordered REL network consists of moves mu=1,...,M with binary frames

    L_mu strictly contained in g_mu contained in W,
    v_mu = l_mu + sum_(nu<mu) a_mu,nu v_nu,
    l_mu in X(g_mu),
    a_mu,nu != 0 only if L_nu is contained in g_mu.

Coefficients are arbitrary rationals. These are the source-availability and
chronological arrival constraints of PR6170's REL relaxation, confined to W.
The sum permits any number of earlier parents, branching, merging, resets,
cancellation and public re-ascents. Public transport and other scalar work
are granted free for this lower bound. The paid bill is

    P = sum_mu (dim g_mu - dim L_mu).

A receiving column u_mu may be arbitrary except

    u_mu(j) != 0 only if L_mu is contained in Q_j = p_j^perp.

Set C=sum_mu u_mu v_mu^T and Gamma_ji=<p_j,p_i>, interpreted as the rational
number zero or one. Correctness of the pattern requires C_ji=delta_ji
whenever Gamma_ji=1. Thus H=C Hadamard-product Gamma=I_|G|. No condition
is imposed on the two off-diagonal class blocks of C.

## Theorem

Every such network satisfies

    rank_Q(H)
      <= sum_mu [dim pi(g_mu) - dim pi(L_mu)]
      <= P,                                                   (1)

where pi:W -> F2^2 sends every A port to (1,0) and every B port to (0,1).
Consequently every correct network has P>=|G|. Equality is attainable in
REL. For two four-port cliques the exact minimum is eight.

The first inequality is a statement about the complete network, including
all relayed source content. It is not a rank bound on each term separately.

## The rational subspace representation

Choose representative ports a in A and b in B. Define

    pi(x) = (<a,x>,<b,x>).

The Gram assumption gives the asserted values on G. Since G spans W, this
also proves that every p_j in a fixed class has the same pairing functional
on W. For j in A it is the first coordinate of pi, and for j in B the second.

Represent the five binary subspaces of F2^2 by rational subspaces of Q^2:

| Binary subspace S | T(S) over Q |
| --- | --- |
| zero | zero |
| span(1,0) | span_Q(1,0) |
| span(0,1) | span_Q(0,1) |
| span(1,1) | span_Q(1,1) |
| F2^2 | Q^2 |

This representation preserves all inclusions and dimensions. Write
T_g=T(pi(g)) and t_j=(1,0) or (0,1) according to the class of j.
Three properties follow.

1. If p_i is in g, then t_i is in T_g.
2. If L is contained in Q_j, then the rational functional t_j^T annihilates
   T_L. For a coordinate functional, binary and rational annihilation have
   exactly the same zero cases in the table.
3. For L contained in g, T_L is contained in T_g and

       dim T_g - dim T_L = dim pi(g) - dim pi(L)
                         <= dim g - dim L.                    (2)

The last inequality is the rank bound on the induced map g/L -> pi(g)/pi(L).
In particular radical-only frame drops contribute zero to the first bill
in (1), although they can cost positive P.

## Cumulative information invariant

For a rational source row v define the 2-by-|G| packet B(v) whose ith column
is t_i v(i). Its two rows are the A and B restrictions of v. For a local
source row l in X(g), every column of B(l) lies in T_g by property 1.

We inductively construct a subspace D_mu of rational source rows. It obeys

    z^T B(v_nu) is in D_mu for every nu<=mu
      and every rational functional z annihilating T_Lnu,     (3)

and has dimension at most the first mu summands of (1). Initially D_0=0.

For move mu, take any z annihilating T_gmu. The local contribution vanishes.
Every permitted earlier parent nu has T_Lnu contained in T_gmu. Therefore
z also annihilates T_Lnu, and (3) for the earlier parent gives

    z^T B(v_mu) = sum_(nu<mu) a_mu,nu z^T B(v_nu) in D_(mu-1). (4)

Extend a basis of ann(T_gmu) to a basis of ann(T_Lmu). There are exactly
dim T_gmu - dim T_Lmu new functionals. Adjoin their rows z^T B(v_mu) to
D_(mu-1) to form D_mu. Equation (4) proves (3) for all functionals in the
larger annihilator. Old invariants are retained because D only grows.
Its dimension rises by at most that many new functionals. This proves the
dimension bound without counting relayed content a second time.

At the final boundary, the jth row of H is

    H_j,* = sum_mu u_mu(j) t_j^T B(v_mu).

Every nonzero coefficient has L_mu contained in Q_j. Property 2 and (3)
place each summand in D_M. All rows of H therefore lie in D_M. This proves
the first inequality of (1); (2) proves the second. If H is the identity,
its row rank is |G|, proving the floor for every finite network.

## Attainment and the shared-cost issue

A simple attaining REL network uses one move per port, with
g_i=span_F2(p_i), L_i=0, v_i=e_i and u_i=e_i. Every move has gap one and
all availability constraints hold. It realizes C=I and P=|G|. This is an
abstract REL realization, not a physical P104 word.

For equal classes of size four, match their indices and use four moves

    g_i=span(p_Ai,p_Bi), L_i=0,
    v_i=u_i=e_Ai+e_Bi.

Each gap is two. The endpoint C=[[I_4,I_4],[I_4,I_4]] has rank four,
while H=I_8 and P=8. Low completion rank alone does not save paid cost.

An explicitly relayed attaining network splits each move through the
intermediate line span(p_Ai+p_Bi). The first move introduces v_i, and the
second carries it unchanged to zero. Both gaps are one. Only the second
move contributes to the endpoint. Its individual Hadamard term has rank
two although its own gap is one. Summing independent per-move rank bounds
would fail here; the cumulative invariant charges both moves once.

## Application and limits

The actual P104 fixture uses

    A=(73,239,336,502), B=(81,247,328,494),
    W=span_F2(81,502,239,73).

The verifier checks membership in the pinned port definition, the complete
eight-by-eight Gram table and all subspaces of this four-dimensional W.
It constructs both attaining networks above. It does not recount PR6170's
four-space census or replay any predecessor word, invoice or claimed floor.

This closes the confined-chain part of PR6170 P104-LEMMAS.md section 11.5
and permits more general confined relay graphs as well. It does not settle
that source's outside-reaching case. On frames outside W, two ports in one
class need not have the same pairing functional. Property 2 can then fail.
The result also does not assert a rational inclusion representation of a
higher-dimensional binary quotient lattice. The rank-two representation
above is an essential hypothesis, not a model of the whole E8 interface.

The rank and dimension arguments are classical linear algebra. The new
contribution is their cumulative application to this REL question, allowing
the cost sharing that the source explicitly leaves open. Independent human
and formal proof-kernel review are unclaimed. No native realization,
complete physical invoice, supplier admission or multiplication theorem
follows. The selected frontier remains unchanged.
