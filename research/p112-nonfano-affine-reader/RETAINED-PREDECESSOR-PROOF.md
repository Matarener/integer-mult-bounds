# A three-target support transfer can fail

Let A,B,C be three disjoint nonempty sets of scalar ports, with |A| >= 2.
Write a,b,c for their indicator vectors. Choose s in A and put

    w = a+b+c-e_s,
    q12=a+b, q13=a+c, q23=b+c, q123=a+b+c,
    u12=(a+b-c-w)/2, u13=(a-b+c-w)/2,
    u23=(-a+b+c-w)/2, u123=w.

Here e_s is the coordinate vector at s. In every field of characteristic other
than two these four terms satisfy the exact, unmasked identity

    u12 q12^T + u13 q13^T + u23 q23^T + u123 q123^T
        = aa^T+bb^T+cc^T.                                      (1)

Indeed the three terms without w contribute the three diagonal outer products;
their mixed terms cancel. The coefficient of w is
`q123-(q12+q13+q23)/2=0`. This works for arbitrary w; the displayed w makes
one reader differ inside A. Outside A union B union C both factors vanish.

**Theorem.** No field of characteristic two admits four indexed rank-one
terms with the same target in (1) and with both supports contained term by
term in these four query and reader supports. New coefficients may be
arbitrary, and an old nonzero is allowed to become zero. Neither a span nor a
matroid-preservation hypothesis is imposed on the proposed new factors.

This is a failure of the actual support-transfer method. It is not a lower
tariff, an obstruction to the target's original three terms, or a statement
about transfers that split a term into several new terms.

## Four ports force the contradiction

Choose x in A other than s, y in B and z in C. Restrict both rows and columns
of the target and the factors to the ordered ports (x,s,y,z). The source
matrix Q and twice the reader matrix U are

    Q = [1 1 0 1]       2U = [ 0  0 -2  2]
        [1 1 0 1]            [ 1  1 -1  0]
        [1 0 1 1]            [ 0 -2  0  2]
        [0 1 1 1]            [-2  0  0  2].

Their product `U Q^T` is

    T = [1 1 0 0]
        [1 1 0 0]
        [0 0 1 0]
        [0 0 0 1].

Put v=(1,1,0,0), e=(0,0,1,0), f=(0,0,0,1). For any proposed support-shrinking
completion over a field E, its four query columns Q12,Q13,Q23,Q123 obey

    supp(Q12) subset {x,s,y}, supp(Q13) subset {x,s,z},
    supp(Q23) subset {y,z}.

The four reader rows impose the span requests

    v in span(Q23,Q123),      e in span(Q13,Q123),
    f in span(Q12,Q123),      v in span(Q12,Q13,Q23).             (2)

The first request, read at x and s, forces the first two coordinates of
Q123 to be the same nonzero value alpha. The second request, read at y,
forces its y coordinate beta to be nonzero, because Q13 is zero there.
Likewise its z coordinate gamma is nonzero. Thus

    Q123 = alpha v + beta e + gamma f,    alpha beta gamma != 0.

In the first request the coefficient of Q123 is 1/alpha. To cancel its
nonzero y,z coordinates the coefficient of Q23 is also nonzero. Therefore
Q23 is a nonzero multiple of beta e+gamma f. The other two pair requests
similarly give

    Q12 ~ alpha v+beta e,
    Q13 ~ alpha v+gamma f,
    Q23 ~ beta e+gamma f.                                     (3)

This derivation also shows that all entries allowed in these query supports
are forced nonzero, and that their x,s entries are forced equal. It does not
assume those facts in advance.

If E has characteristic two, the linear functional on span(v,e,f) defined by

    L(v)=1/alpha, L(e)=1/beta, L(f)=1/gamma

annihilates all three vectors in (3), since 1+1=0. But L(v) is nonzero.
The last request in (2) is impossible. This proves the theorem over every
characteristic-two field, including infinite extensions, and for arbitrary
support shrinkage. Any purported transfer on a larger port set would restrict
to these four ports, so outside directions cannot repair the contradiction.

The given matrices supply a completion over every other characteristic.
Consequently this fixed four-term support-completion problem is solvable
exactly in characteristics other than two. No classification theorem or
finite-field census is needed for that quantified statement.

## What changes relative to the earlier results

The seven query/target directions are the familiar non-Fano configuration
`a,b,c,a+b,a+c,b+c,a+b+c`, with three independent targets marked. The
characteristic obstruction itself is standard; no literature priority is
claimed. The added point is the explicit nonconstant actual reader that
forces all four requests (2) in one exact literal factorization.

[PR3505](https://github.com/CrocSwap/integer-mult-bounds/pull/3505) gives a
sufficient full-matroid characteristic-two representation condition for the
actual-reader floor. [PR3506](https://github.com/CrocSwap/integer-mult-bounds/pull/3506)
shows that every two-target marking of the non-Fano configuration still
admits selective transfer. Neither statement says that every three-target
factorization admits selective transfer. This example shows that the latter
extension is false even with four terms. It does not contradict either floor.
The concurrent five-term/two-target classification is a separate question.

[PR3475](https://github.com/CrocSwap/integer-mult-bounds/pull/3475) prices all
seven subset-sum query rays with readers in span(a,b,c). Here u123=w is not
in that span, because its value changes inside A. Thus these actual readers
leave that hypothesis. No previous target-span exclusion is republished as
the result. Exact comparison heads and proof hashes are in COMPARISONS.json;
they are comparisons, not runtime or proof dependencies of this proof.

For a positive control, take w=a+b+c everywhere instead. There is then no
special reader at s. The pair-reader rows have integral coefficients and
reduce directly modulo two. That unsplit factorization admits transfer even
though the edge triple loses rank. The nonconstant reader is essential to
the displayed contradiction.

## The literal tariff experiment

Use the pinned 112 P112 labels and Tekalign's PR3370 sixteen-group partition.
Each group has binary identity Gram matrix; consecutive ports form complete
planes. Its alternating halves give 32 disjoint indicators. For a scalar
vector t, cl(t) contains both ports in every plane touched by supp(t). Charge
an actual term by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

If the complete group sizes for a,b,c are m_A,m_B,m_C, the original three
terms cost m_A+m_B+m_C. Each indicator touches every plane of its own
orthonormal group, so this follows directly from its identity Gram matrix.
The whole retained indicator bill is twice 112, namely 224.

The bounded experiment enumerates each of the 32 choices of a, each unordered
pair b,c distinct from a, and each single switched port s in supp(a).
There are `sum_a |supp(a)| * choose(31,2) = 112*465 = 52,080` cases. Swapping
b,c only swaps the first two term charges, so there is no omitted asymmetric
case. The actual four reader supports in this order are

    {s} union C, {s} union B, A, (A minus {s}) union B union C.

Both implementations compute their rectangular complete-plane Gram tariffs.
The best excess over the original bill is +4, attained in 24 cases. The
lexicographically selected witness uses target indices [24,6,25], switched
port 10 and charges [4,4,4,8]: bill 20 versus 16. Its complete operator has
12,544 checked entries and factor ranks (3,4). Appending the untouched
indicator terms gives bill 228. No case in this declared domain saves cost.

The primary computes binary ranks after replacing each support by a binary
label basis. The separate implementation enumerates the entire label span
S and the reader annihilator R-perp, then uses

    rank pairing(S,R) = log2 |S| - log2 |S intersect R-perp|.

This identity follows from rank-nullity for the pairing map on S. The finite
ambient dimension is nine, so both sets have at most 512 elements. The two
full streams agree on SHA256
`1e8adb51b6c2f54541777e82694019983ca3b6f338149f00f9884ad70a015003`.
RESULT.json specifies the full histogram, iteration order and selected witness.
The stream appends bytes `[a,b,c,s,original,C12,C13,C23,C123]` per case.

Finite field controls corroborate the support argument. Normalizing four
query scales and using the forced repeated source row leaves columns
`(1,1,a,0),(1,1,0,b),(0,0,1,c),(1,1,d,e)` with five nonzero parameters.
The primary tests all 1, 243 and 16,807 cases over GF2, GF4 and GF8. The three
pair requests survive in respectively 1,9,49 cases; none passes the last
request. A separate implementation exhausts all 4,096 raw GF2 source arrays,
including arbitrary support deletion, and all 243 normalized GF4 arrays by
direct span enumeration. The written proof, rather than these finite tests,
establishes impossibility over every characteristic-two field.

The census does not optimize arbitrary w, several switched ports, other
query rays, more terms, coefficients with new supports or different labels.
Failure of this transfer method does not predict a saving. Acquisition,
native scalar execution, frames, dirty restoration, ownership, hosting,
stock, precision, physical consumers, all-size/compiler and outer theorem
obligations remain separate. There is no supplier or new kappa claim.
Independent human and formal proof-kernel review are unclaimed.
