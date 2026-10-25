# Two sharp binary bounds with different scopes

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

All vector spaces and matrices in this note are over F2. A matrix rank is an
integer. A trace is an element of F2. The two theorems have different
hypotheses. Neither theorem states a limit for every native controller.

## A. Commuting supports of rank three

Let E_1,...,E_f be pairwise commuting idempotents of rank three on a finite
vector space V. For each i, assume

    E_i R_i = R_i E_i = R_i,
    R_i is similar to J_2(0) direct-sum [1] direct-sum 0.

Here J_2(0) is the two-dimensional nilpotent Jordan block. Thus each R_i has
rank two, trace one, and is not idempotent. Suppose

    sum_i R_i = P,

where P is an idempotent that commutes with every E_i. Then

    rank(P) <= 5*f/3.                                      (A)

In particular, if P=I_n, then n<=5*f/3. The statement permits zero target
coordinates. It imposes no order on the calls and no prefix condition.

### Common coordinates and components

An idempotent has minimal polynomial dividing x(x+1). These two roots are
distinct in F2. Commuting idempotents therefore have a common eigenbasis:
split V into the kernel and image of one idempotent, then repeat the split
on each invariant part. Include P in these splits.

In this basis, E_i selects a three-element coordinate set S_i. The two-sided
support condition confines every nonzero entry of R_i to S_i times S_i.
Form a graph on the calls. Join i and j when |S_i intersect S_j|>=2.

For one connected component C, put T_C=sum_{i in C} R_i. This matrix is
diagonal. To see this, fix distinct coordinates a,b. Any call that contributes
to entry (a,b) has both coordinates in its support. All such calls belong to
one component. Their total is zero because P is diagonal. Thus the entry is
zero in that component and is zero in all other components.

A component with c calls has a support union of size at most c+2. Start at one
vertex of a spanning tree. Its support has size three. Each next vertex
shares at least two coordinates with a previous vertex and adds at most one.
Hence, when c>=3,

    rank(T_C) <= c+2 <= 5*c/3.                              (1)

### Components with one or two calls

A one-call component cannot occur: its sum would be R_i, which is diagonal
and hence idempotent over F2. This contradicts the stated Jordan type.

For two calls, the support union has size at most four. Its diagonal sum D
has trace 1+1=0, so rank(D) is even. Rank four is impossible by the following
rank-additivity fact.

Suppose A+B=D, where D is an idempotent of rank four and A,B each have rank
two. Since image(D) is contained in image(A)+image(B), equality of dimensions
gives

    image(D) = image(A) direct-sum image(B).

For x in image(A), D x=x. The decomposition A x+B x=x into these two images is
unique, so A x=x and B x=0. Thus A is identity on its image, and A^2=A.
The same argument gives B^2=B. Apply this fact to the two R terms to obtain
a contradiction. Therefore rank(T_C)<=2 for a two-call component, which is
also at most 5*c/3.

Finally, rank is subadditive. Sum the component bounds:

    rank(P) = rank(sum_C T_C) <= sum_C rank(T_C) <= 5*f/3.

This proves (A). Components can share one coordinate; the rank inequality
does not assume that their diagonal supports are disjoint.

### A sharp example

Use coordinates a,b,c,d,e and let P_x denote the coordinate projector at x.
Set

    N_1 = (b+c)(b*+c*),       N_3 = (c+d)(c*+d*),
    R_1 = P_a + N_1,
    R_2 = P_b + P_c + P_d + N_1 + N_3,
    R_3 = P_e + N_3.

The supports are abc, bcd, cde. Each term has the required Jordan type and
the sum is I_5. Thus three calls attain five outputs.

This example also satisfies the stage order condition

    [E_i, sum_{j<i} R_j] = 0.

For independent commuting stage variables D_i and q^2=0, define

    M_i = (I+(D_i+1)E_i)(I+q R_i).

The exact product M_3 M_2 M_1 is diagonal. Its entries are

    (1+q) D_1, (1+q) D_1 D_2, (1+q) D_1 D_2 D_3,
    (1+q) D_2 D_3, (1+q) D_3.

The verifier multiplies the polynomial matrices over F2 and checks every
coefficient. This abstract binary identity is not a complex Laurent lift or
a replay of a physical native caller.

## B. A finite adaptive grammar

This theorem permits an outside-support helper contribution, which theorem A
does not permit. It limits the retained state instead. No implication from
one theorem to the other is used.

A state is a binary matrix on at most three live coordinates. An isolated
coordinate has diagonal entry zero or one and no off-diagonal entry in its
row or column. Remove every isolated coordinate at once. Charge one output
for each removed diagonal one. A removed zero can represent a D-only output.
Order the remaining coordinates by the lexicographically smallest matrix
under coordinate permutations. No other change of basis is allowed.

There are two operations.

1. FULL: put the live coordinates first and add zero coordinates to reach
   four. The first three coordinates form the source support E. Add

       R = u v^T + h p^T,

   where u,v,p are nonzero vectors in that support, v^T u=p^T u=0,
   p is different from v, and h is any vector on all four coordinates.
   Charge one FULL. The conditions make u v^T a rank-one nilpotent and make
   p an independent helper input row. The source E contains the whole old
   state, so E commutes with it. Apply the stated state reduction.
2. THIN: add one zero coordinate, with total size at most four. Add any
   rank-one matrix u v^T with u and v nonzero on those coordinates.
   Charge one THIN, then apply the same state reduction.

Reject a transition if more than three live coordinates remain. Removed
coordinates cannot return as catalysts. A closed word starts and ends at the
empty state. Write g for its output count, h for its THIN count, and f for its
FULL count. Then

    3*(g-h) <= 5*f.                                        (B)

For f>0 the maximum ratio (g-h)/f is exactly 5/3.

### Complete finite certificate

The code enumerates every parameter tuple in the stated FULL alphabet and
retains its matrix. There are 315 distinct matrices. It enumerates every
nonzero u,v pair for each THIN support size. Breadth-first closure from the
empty state reaches 94 canonical states and 20,020 legal raw transitions.

For each source, target, and operation type, retaining only the largest gain
leaves 10,035 transitions. A discarded smaller gain cannot improve the
claimed bound. The verifier checks the potential on all raw transitions too.

The certificate assigns an integer z(S) to each reachable state S. For every
edge S->T with counts (g,h,f), it verifies

    z(T)-z(S) >= 3*g-3*h-5*f.                              (2)

Sum (2) along a closed word. The potentials cancel, proving (B). Each
certificate transition is also checked against the declared matrix rule.
The retained witness starts at the empty state, uses three FULL operations,
and returns there with five outputs and no THIN. This proves sharpness.

The mathematical implication from a valid potential to (B) is elementary.
The finite enumeration and the retained potential are checked by the supplied
program. This is a finite computational certificate, not proof-assistant
acceptance or a claim about an unrestricted controller grammar.

## Verification boundaries

The verifier also checks all 84 three-dimensional matrices of the stated
Jordan type and all 28,224 two-call embeddings into a four-coordinate union.
The only diagonal sum ranks are zero and two. This finite check supports the
written two-call argument; it does not replace the general proof above.

Rejected controls include a lowered tight potential, a missing reachable
state, an unpaid THIN query, a non-nilpotent native direction, and a changed
motif coefficient. The identity on three coordinates is retained as a
counterexample after the Jordan-type hypothesis is dropped.

Neither theorem permits an unproved complex reduction modulo two. Neither
proves native input access, helper restoration, supplier admission, complete
pricing, or a multiplication exponent. Those obligations remain separate.
