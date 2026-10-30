# All-order exclusion of the coupled star query frame

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Result and scope

The constant-loss frame in PR5631 passes the earlier stage-rank and
intersection cuts at arbitrarily large sizes. This package permits arbitrary
matrix coupling inside every good stage pair. It excludes every call order,
every coupled channel dimension, and every odd leaf count g>=3 for this
frame. It also supplies a small exact proof format for other matrix searches.

This is a theorem in the binary normalized model. It is not a reduction of
all complex or dyadic native callers to that model. It gives no new kappa.
Other query frames and connector contracts remain open.

Let F be any field of characteristic two. Let W have positive dimension d.
The main space is W_0 plus W_1 plus ... plus W_g, with W_0 the core. Let
E_j select W_0 and W_j. On these two blocks put

    T_j = [[I,I],[I,I]].

All other blocks of T_j are zero. Split each good stage into two calls.
Their projectors P_j and P'_j have sum E_j, are orthogonal, and their
queries R_j and R'_j have sum T_j. Require P_j R_j = R_j P_j = R_j and
P'_j R'_j = R'_j P'_j = R'_j. These conditions cover every compatible
split at full stage rank. No separate-port restriction is imposed.

The four remaining queries are F_C, G_C, F_(I+C), G_(I+C), where C is any
idempotent on W. F_H has block H from each leaf input to the core output.
G_H has block H from the core input to each leaf output. All other blocks
are zero. These are the connector queries of the source star frame, after
an arbitrary common channel basis change. Their stage projectors are not
used in the exclusion. They can be thin calls. There can be arbitrary
constant basis changes already absorbed into the displayed matrices.

For odd g, the sum of all queries is I: the sum of the T_j has identity
diagonal and identity core/leaf cross blocks; the four connectors cancel
the cross blocks. Thus the frame passes the query-sum condition.

For the native equal-rank instance, d=2q, rank A_j=rank C=q. Each good
projector has rank 2q, each query has rank q, N=2q(g+1), and L=2g+4.
The theorem is stronger than that instance: its algebra does not use the
ranks of A_j or C.

**Theorem.** No order of these calls has an endpoint with the central
involution Q on every main field and the declared independent good-stage
projectors E_j, if g>=3 is odd. This holds for every d>0 and every F of
characteristic two. Failure already occurs in a mixed first derivative.

## 2. All coupled splits have a matrix parameterization

Since the two projectors are orthogonal and sum to E_j, both act inside
W_0 plus W_j. Also P_j T_j = T_j P_j = R_j. The centralizer of T_j has
block form

    P_j  = [[A_j+B_j, B_j], [B_j, A_j+B_j]],
    R_j  = [[A_j, A_j],     [A_j, A_j]],
    P'_j = E_j + P_j,        R'_j = T_j + R_j.

To see completeness, write a general four-block matrix and equate its
products with T_j on the two sides. Its two diagonal blocks are equal,
and its two off-diagonal blocks are equal. Idempotence is equivalent to

    A_j^2 = A_j,
    A_j B_j + B_j A_j = B_j.

For example, in a basis with T_j=[[0,I],[0,0]], the projector is
[[A_j,B_j],[0,A_j]]. This also gives rank P_j=2 rank A_j. These are full
matrix parameters. Their entries can mix every channel. They are not
scalar choices or copies of a one-port calculation.

## 3. Necessary chronology equations

Put Q=1+e and z_j=1+d_j, with e^2=d_j^2=0. After normalization a good
call is (I+d_j P)(I+e R). Calls act in listed order, with later factors
on the left. The query sum is I. The coefficient of e*d_j is

    E_j + sum_(i in stage j) [P_i, sum_(k later than i) R_k].

The desired endpoint has coefficient E_j. Therefore its defect must be
zero. This is PR5631's mixed chronology condition. The bracket is AB+BA
in characteristic two. An exact local matrix word supplies a separate
check of this formula in the verifier.

For each good stage j, retain only defect blocks whose row and column
are not both in {0,j}. A nonzero retained block involves stage j and
one other leaf k. A query at a third leaf contributes zero to this block:
its only nonzero rows and columns are at the core and that third leaf.
A connector contributes H or zero, independent of the number of leaves.
Thus these retained equations depend only on the relative order of the
two good stages and the four connectors.

Choose any three good stages. Delete every other good call from the order.
The retained equations on those three stages do not change. Rename the
three stages in order of first occurrence. If a stage's second labelled
call occurs first, replace A_j by I+A_j and leave B_j unchanged. This
preserves all local equations and exchanges the two calls. Consequently
there are exactly

    10! / (2^3 * 3!) = 75600

order types to check. This finite reduction is independent of g and d.
It is the step that turns a finite order certificate into an unbounded
length and matrix-size theorem.

## 4. Exact certificates in a free algebra

Use the free associative algebra F2<A0,B0,A1,B1,A2,B2,C>. A word records
the order of its factors. In particular A0*B1 and B1*A0 are different
words. The equations are the six local relations in Section 2, C^2+C,
and the retained chronology blocks from Section 3.

For each of the 75600 order types, ORDER-CERTIFICATES.json.gz gives
explicit finite words u_l,v_l and equation indices i_l such that

    sum_l u_l * equation_(i_l) * v_l = 1.

The separate checker expands this sum and cancels equal words modulo two.
There are 72020 witnesses of degree at most two and 3580 of degree at most
three. The largest has 77 terms. No SAT or numerical solver is needed to
check them. The search code uses finite linear algebra on words to find
these identities; the checker does not import that code.

If a tuple of matrices solved the equations, evaluation of each witness
would give 0=I_d. This is impossible for d>0. Evaluation preserves word
order, so no commutativity of the matrices is assumed. Since F contains
F2, the same identities work over every characteristic-two field.
This proves the theorem.

For a short example, put all first good calls before all connectors, and
put second good calls in reverse order. Four retained equations are

    I + A0 + A1 + B1 = 0,
    B1 = 0,
    I + A0 + A2 + B2 = 0,
    I + A1 + A2 + B2 = 0.

Their sum is I=0. The other order types need the certificates above;
this example is not used as a substitute for their complete coverage.

## 5. What the search removes

The source relaxed profile has 2q jobs of rank 1+8g and 2gq jobs of rank
9, against 2g+4 full calls and their complete independent helper bill.
For q=104 and g=1023, the PR5599 bill gives a positive relaxed moment at
saving .003125. The exact integer-power enclosure is in RESULT.json.
This exceeds the selected .00310045 but is not an attainable caller.
The theorem excludes every coupled split and every order of this frame,
including large cases that were not individually instantiated.

The preliminary eight-call, 720-field price screen also failed a frame
condition. If rank-q square-zero queries sum to I_N, their Gram complement
has rank h=qL-N and identity q by q diagonal blocks. Factoring it gives
rank-q idempotents E_i on an h-dimensional space with sum I_h. For even L,
the complements I_h-E_i also sum to I_h. Hence L(h-q)>=h. The proposed
q=104,L=8,N=720 has h=112 and 8(h-q)=64, so it is impossible.

A separate useful test is the three-occurrence lemma. If square-zero
matrices R_i sum to a diagonal projector E and are supported on diagonal
projectors P_i, each coordinate where E=1 must occur in at least three
P_i. With two occurrences, their rows are a and e_j+a and their columns
are b and e_j+b. Square zero gives a*b=0, but
(e_j+a)*(e_j+b)=1+a*b because a_j=b_j. This is a contradiction. One
occurrence also contradicts square zero. Thus 3 rank E <= sum rank P_i.
This covers arbitrary coupled queries whose local projectors commute.
For paired stages at full rank, group the two orthogonally supported
queries. Their sum is square zero and supported on the target stage
projector. The same test applies. Rank loss requires another argument;
the star theorem above supplies one for the declared frame.

## 6. Verification boundary and next routes

The order reduction and free-algebra evaluation argument are written
proofs. The executable checker verifies the complete finite order cover
and every exact identity. A different matrix implementation checks the
local identities, query frame and mixed coefficient formula on coupled
noncommuting examples. The one-leaf case is a genuine full polynomial
word and is retained as a positive control. Corrupted certificates and
changed query data must fail. No proof assistant or independent human
acceptance is claimed.

This theorem does not exclude a different query Gram frame, a different
connector map, more connector queries interleaved with good calls, nonfull
stage ranks, different main outputs, noninvolutive stages, helper feedback,
or arbitrary complex/dyadic callers. It does not price or certify a new
native multiplication algorithm. A future search can change one of these
premises, or use the same free-algebra certificate format on another exact
frame before it allocates large matrices and a complete native bill.

Credit Cinna Davis / 1337isnot1337 for the controller, simplex and private
projector lineage; PR5617 for stage/intersection cuts; PR5631 for the
constant-loss star and mixed chronology equation; and the P104, helper,
native, compiler and outer-framework authors retained by those sources.
Free associative algebras and linear combinations of polynomial equations
are standard tools. The all-order coupled-frame reduction and its exact
witnesses are the contribution of this package.
