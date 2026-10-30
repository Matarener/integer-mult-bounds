# A cancellation certificate for the five-call diagonal-pair obstruction

## Statement and scope

Let G be any group, L any set of group labels, and a,b distinct elements,
neither expressible as a product of zero, one or two labels from L. Over
F2[G], let D_N(g) = (I-N) + [g]N, where N is a rank-one idempotent 2 by 2
matrix over F2 and g belongs to L. Then **no product of at most five calls is
diag([a],[b])**.

This is a computer-assisted theorem: the written argument below proves that
an actual realization survives the finite collision relaxation; the registered
exact verifier exhausts and rejects that relaxation. It is not a handwritten
classification of all projector tuples, a proof-kernel result, a finite-group
sample, or a theorem for other fields or widths.

In particular, when a=xyx and b=yxy satisfy the stated shortest-word and
distinctness hypotheses for L={x,y}, the minimum is exactly six. The upper
bound is D_E00(x) D_E00(y) D_E00(x) D_E11(y) D_E11(x) D_E11(y).
This is the formal register model of Wentao Li (#4089), as used by Nick
Petalas (#6038) and Josie Elliston (#6048). No native tariff, supplier or
multiplication bound is inferred.

## Free scalar changes of basis

The stated product form also covers arbitrary invertible scalar basis changes
between paid calls. Write such a circuit as

    S0 D_N1(g1) S1 ... D_Nk(gk) Sk,
    Si in GL_2(F2).

Let Ci=S0 ... S_(i-1). The identity S D_N(g) S^-1 = D_(S N S^-1)(g)
moves each scalar factor to the right, giving

    D_(C1 N1 C1^-1)(g1) ... D_(Ck Nk Ck^-1)(gk) S,
    S=S0 ... Sk.

Conjugation preserves rank-one idempotence, so every resulting projector is
in the six-element inventory. The group-algebra augmentation [g] -> 1 sends
every paid factor to I and sends diag([a],[b]) to I. Thus any successful
circuit has S=I. Free scalar changes of basis therefore add no missing
terminal factor or extra cases. This normalization does not admit free
address-dependent maps, clean auxiliary registers, COPY or ERASE.

## The missing group implication

Write the chronological labels of a k-call candidate as g_1,...,g_k. They
are positional symbols, not presumed distinct. For a subset U of positions,
let w_U be its increasing sequence and g_U its group product. If two such
sequences have a common prefix p, then

    g_(pu) = g_(pv) if and only if g_u = g_v.

The same equivalence holds for a common suffix. These are cancellation and
multiplication in G; they hold in every group, including groups with torsion
and arbitrary relations. In particular inserting one nonidentity letter
between a fixed prefix and suffix cannot preserve the group element.
The certificate uses both implications, only when all sequences involved
are chronological subsets of the candidate. It does not presume that these
rules decide the word problem.

A concrete five-call tuple has projectors, in row-major bit encoding,

    (1,5,5,3,10) = (E00, [[1,0],[1,0]], [[1,0],[1,0]],
                   [[1,1],[0,0]], [[0,1],[0,1]]).

Its matrix coefficients are

    T00 = [g1 g2 g3 g4]
    T01 = [g1 g2 g3 g4] + [g1 g2 g3 g5]
    T10 = [g4] + [g2 g3 g4]
    T11 = [g4] + [g2 g3 g5] + [g2 g3 g4].

The required zero T10 forces g4=g2 g3 g4, hence g2 g3=e. Consequently
T00=[g1 g4], so a has a two-label expression, contrary to the hypothesis.
Separate choices of cancellation classes for different coefficients miss
this shared implication. The finite certificate propagates it jointly.

## Why the finite relaxation contains every realization

Drop identity-labelled calls first. Therefore all remaining g_i are
nonidentity and k is still at most five. Expand the product exactly as

    product_i D_Ni(gi) = sum_U [g_U] P_U,
    P_U = product_i (N_i if i in U else I-N_i),

with every product in increasing position order. Each of the four matrix
entries gives an equation over F2[G]. Move [a] into the 00 equation and [b]
into the 11 equation. Every equation must now be zero.

The solver has one node for each subset U and two extra nodes A,B for a,b.
A partition stores only equalities forced or chosen so far. Initially all
nodes are separate. A genuine realization supplies a coarser partition by
actual group value. Every solver step preserves at least one branch
compatible with that realization:

1. **Cancellation closure.** For every common-prefix or common-suffix rule,
   if its premise nodes have been equated, equate its conclusion nodes.
   The group equivalences above justify this. The reverse rules are valid
   multiplication by the common prefix or suffix.
2. **Forbidden equalities.** Reject if the empty subset equals a singleton,
   if A=B, or if A or B equals a subset of size at most two. These contradict
   respectively g_i != e, a != b, or the shortest-label hypothesis.
3. **Parity equations.** Replace each equation node by its current partition
   class, retaining precisely classes with odd multiplicity. An actual
   group-value class must occur evenly because the elements [g] form a
   basis of F2[G]. If exactly two classes remain, their equality is forced.
   If an odd number remain, no partition into even multiplicities exists.
4. **Exhaustive partner branching.** Otherwise choose the first class in a
   shortest nonempty residual equation. In any actual completion its
   group-value class has even multiplicity, so at least one of the other
   remaining classes has that same value. Branch over every such partner
   and equate them. At least one branch retains the actual realization.

Every branch strictly merges two classes; closure also only merges classes.
Thus the search terminates. It may accept partitions unrealizable by groups,
because it omits many group implications, but this only weakens a rejection.
If every branch rejects, no actual realization of that projector tuple
exists. The node cap fails the verifier rather than declaring a rejection.

## Finite coverage

A nonzero rank-one idempotent over F2 is u v^T with v^T u=1. The six 2 by 2
possibilities have row-major bit encodings 1,3,5,8,10,12. The verifier obtains
them by idempotence and trace one, then independently checks the outer-product
inventory. It evaluates all 6^k tuples for each k=0,...,5, without identifying
or omitting symmetry classes. There are 9,331 tuples in total.

Every label sequence, in every group and every label set, is covered by the
positional-symbol argument for its projector tuple. No assignment of x,y,
no finite group, and no determinant/degree invariant is enumerated. The
computed zero survivors, together with the sound relaxation argument,
establish the scoped theorem.

## Controls and remaining proof obligations

The six-call direct construction is checked by exact free-word coefficients.
Removing cancellation reopens the four-call tuple (1,5,1,10), demonstrating
that support and coefficient parity alone do not prove the result. Relaxing
the target length hypothesis reopens the two-call tuple (E00,E11). The
explicit five-call example above is checked by the same refutation engine.
The verifier independently authenticates every generated cancellation rule as a
single common-context law, checks the displayed coefficient expansion, and
accepts the actual four- and six-call constructions in the collision solver.
It uses explicit checks, which remain active under Python -O.

The proof still depends on the correctness and successful completion of the
small Python certificate. Independent human or proof-assistant review has
not been claimed. The six-projector inventory and characteristic-two parity
are essential scope restrictions; extension to other fields or widths
requires new reasoning.
