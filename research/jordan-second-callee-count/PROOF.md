# Exact optimal-callee counts for a two-dimensional Jordan block

Prepared for NicholasStone with OpenAI Codex assistance. Apache-2.0.

## Result

Let F = F_q be any finite field, let lambda be nonzero, and put

    N = [[0,1],[0,0]],   P = lambda I + N.

Use the unchanged ordinary wrapper with chronological operations

    D -= H; F_P; D += H; F_Q; D = -D; D += H,
    F_T(H,D) = (T D, T^-1 H).

The second map Q must be invertible. Call it optimal when the rank of the
wrapper error relative to interchange J(H,D)=(D,H) is minimal over all such Q.

**Theorem.** The exact number of optimal second maps is

    1          if lambda^2 = 1;
    q^2        if lambda^2 != 1 and lambda^2 = -1;
    q(q-1)     if lambda^2 != 1 and lambda^2 != -1.

The order of these cases matters in characteristic 2, where 1=-1. In that
characteristic every lambda != 0,1 belongs to the third case. In the regular
case lambda^2 != 1, write A=P^2-I. All optimal second maps are uniquely

    Q = P + A S,
    S = [[a,b],[c,-a]],   a^2+bc = 0,
    lambda^2 + (lambda^2+1)c != 0.                    (1)

If lambda^2+1 is nonzero, the excluded parameters are exactly the q matrices

    c0 = -lambda^2/(lambda^2+1),
    S_a = [[a, -a^2/c0], [c0, -a]],   a in F.        (2)

Each regular-case optimal Q agrees with interchange on q^2 of the q^4
input pairs. This is optimal agreement, not agreement on all inputs.

## Attribution and the inherited reduction

Nick Petalas's [PR5228](https://github.com/CrocSwap/integer-mult-bounds/pull/5228),
`research/optimal-second-callees/PROOF.md`, classifies all optimal second
callees using a square-zero endomorphism and an invertibility filter.
Its README explicitly leaves nonscalar filtered counting open, beginning
with one nonsemisimple block. Jerry Chen / CubeJerry's
[PR2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950) supplies
the already-known optimum and the attainer Q=P. These are predecessor
results, not new claims here.

For clarity, the small amount of inherited algebra needed here is recorded.
Put R=Q-P, x=D-H and y=P^-1 H+P x. Direct execution gives

    H' = Q P^-1 H + Q P x,
    D' = H' - Q^-1 P x.

For e1=H'-D and e2=D'-H this yields

    e1 = A x + R y,      Q(e2-e1)=R x.

Both the input change to (x,y) and the output change to (e1,Q(e2-e1)) are
invertible. Therefore the error rank equals the rank of

    M = [[A,R],[R,0]].                                (3)

The minimum is rank A, since A is a submatrix and Q=P attains that lower
bound. If A is invertible, block elimination gives

    rank M = 2 + rank(R A^-1 R).

Writing R=A S gives R A^-1 R=A S^2. Thus optimality is equivalent to
S^2=0, subject to Q being invertible. Since A is invertible, different S
give different Q. This is the invertible-A specialization of PR5228.

## Square-zero matrices over every characteristic

For a two-by-two matrix S, S^2=0 is equivalent to

    S = [[a,b],[c,-a]],    a^2+bc=0.                  (4)

Indeed, im S is contained in ker S, so det S=0. Cayley-Hamilton gives
S^2-(tr S)S=0; for nonzero S with S^2=0 this forces tr S=0, and S=0 has
zero trace as well. Conversely the square of the displayed matrix is
(a^2+bc)I. No division by 2 is used.

For each fixed c there are exactly q solutions (a,b):

* If c=0, a^2=0 forces a=0, while b is arbitrary.
* If c is nonzero, a is arbitrary and b=-a^2/c is uniquely determined.

Consequently there are q^2 square-zero matrices, and the lower-left entry c
has q preimages for every field element. This uniform fiber count is the
counting step used below.

## The determinant filter

Assume lambda^2 != 1, so A is invertible. Since N^2=0,

    P^-1 = lambda^-1 I - lambda^-2 N,
    B := P^-1 A = P-P^-1
       = (lambda-lambda^-1)I + (1+lambda^-2)N.

For square-zero S, both tr S and det S vanish, and tr(NS)=c. The
two-dimensional identity det(I+T)=1+tr T+det T therefore gives

    det Q = det P det(I+B S)
          = lambda^2 [1 + (1+lambda^-2)c]
          = lambda^2 + (lambda^2+1)c.                (5)

If lambda^2+1=0, this determinant is the fixed nonzero value lambda^2, so
all q^2 parameters survive. Otherwise (5) vanishes at precisely the nonzero
value c0 in (2). The fiber over c0 has exactly q elements, yielding q^2-q
survivors and the complete rejection family (2).

In fact, when lambda^2+1 != 0 the determinant map from the entire square-zero
parameter set to F is uniform: every determinant value has exactly q
preimages. Thus each prescribed nonzero determinant occurs for q optimal Q.
In the exceptional case every optimal Q has determinant lambda^2.

For an alternative direct calculation, with d=lambda^2-1 one has

    Q = [[lambda+d a+2 lambda c, 1+d b-2 lambda a],
         [d c,                   lambda-d a]].

Expanding this determinant and substituting a^2+bc=0 also gives (5).

## The boundary lambda^2=1

Here A=2 lambda N. In characteristic 2, A=0 and the minimum error rank is
zero; (3) has rank zero only when R=0. Thus Q=P is the unique optimum.

In odd characteristic, A has rank one. Equality rank M=rank A requires both
im R contained in im A and ker A contained in ker R: otherwise adjoining R
to A horizontally or vertically would already raise the rank. These two
containments force R=beta N. Deleting the zero rows and columns of (3)
leaves

    [[2 lambda,beta],[beta,0]].

If beta is nonzero its determinant is -beta^2 and its rank is two, exceeding
the minimum one. Hence beta=0 and again Q=P is the unique optimum.
This completes the theorem for every nonzero lambda over every finite field.

## Scope

The contribution is the explicit filtered count, determinant distribution
and rejection family for one two-dimensional nonscalar Jordan block. The
result is also invariant under simultaneous change of basis: conjugating P
and Q preserves wrapper error rank and gives a bijection of optimal maps.
The generic rational-canonical-data counting question and Jordan blocks of
size at least three remain open here. The finite verifier corroborates the
written proof; it is not a proof-kernel formalization. No implementation cost,
supplier, improved kappa or complete multiplication theorem is claimed.

## Open next questions

* For P=J_3(lambda), count the filtered square-zero parameters, first with
  lambda^2 != 1. Every nonzero square-zero 3x3 matrix has rank one, so writing
  S=u v^T with v^T u=0 may make the determinant filter tractable.
* Determine how this filtered count combines across several Jordan blocks;
  off-diagonal parts of S couple the blocks and prevent a naive product rule.
