# A representation obstruction to cheaper actual-reader decoders

## Statement and scope

Take a finite indexed collection of n binary labels, partitioned into positive
even groups. Every group's binary Gram matrix is the identity. Pair consecutive
ports in each group into complete planes. The two alternating halves of each
group give disjoint indicator vectors. Select k distinct indicators b_j and
let m_j be the size of the complete group containing b_j. Two indicators may
come from the same group. Cross-group pairings are unrestricted.

For a scalar port vector x, cl(x) includes both labels of every plane meeting
supp(x). The additive actual-reader tariff is

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Let F be any field, and suppose finitely many arbitrary F-valued port vectors
satisfy

    T = sum_j b_j b_j^T = sum_i u_i q_i^T.

The factors may have external directions, nonbinary coefficients, zero terms,
parallel columns and cancellations outside all selected supports. Form the
labelled vector configuration consisting of every q_i and every distinguished
b_j. Its column matroid records the rank of every indexed subset, including
zeros and parallel copies.

**Theorem.** If this labelled column matroid has a representation over any
field E of characteristic two, then

    sum_i C(u_i,q_i) >= sum_j m_j.

The original indicator terms attain equality. By transposition the same
conclusion holds when the augmented reader/target configuration has such a
representation. Thus a strictly cheaper realization requires BOTH augmented
matroids to be nonrepresentable over every characteristic-two field.

This is a sufficient obstruction to a saving. Full matroid representability
is not asserted necessary for a support-preserving transfer. Only some rank
conditions enter the proof, and a transfer can preserve them while changing
other subset ranks. In particular, the separate batch-12 five-term non-Fano
investigation addresses selective transfer beyond this sufficient hypothesis.
No impossibility claim is made for that domain.

## Transfer source zeros and reader spans separately

Write Q_i and B_j for the labelled E-representatives. The B_j are independent
because the original nonempty disjoint indicators are independent. At a source
port p, let Z_p consist of the indices i for which q_i(p)=0.

We first choose an E-linear functional f_p such that

    f_p(B_j) = b_j(p), and f_p(Q_i)=0 for i in Z_p.

If p is outside every selected indicator, f_p=0 suffices. Otherwise exactly one
b_j(p) is one. The original coordinate functional is zero on every other b_h
and on the queries in Z_p, and is one on b_j. Therefore

    b_j is outside span({b_h:h!=j} union {q_i:i in Z_p}).

This is an indexed-subset rank condition, so it holds for B_j, the other B_h
and the Q_i in Z_p. Define a functional on their span by zero on that latter
span and one on B_j, then extend it to the ambient representation space. This
constructs the requested f_p. Set q'_i(p)=f_p(Q_i). Every original query zero
survives, separately for each term.

At a reader port p, set I_p={i:u_i(p)!=0}. The original operator identity gives

    sum_(i in I_p) u_i(p) q_i = sum_j b_j(p) b_j.

Outside the selected indicators set every new reader value to zero. On the
support of b_j, the equality says b_j belongs to span({q_i:i in I_p}). Rank
preservation implies B_j belongs to span({Q_i:i in I_p}). Choose coefficients
u'_i(p) on precisely that allowed index set expressing B_j, assigning zero
to all other indices. Some allowed coefficients may also be zero.

Applying the source functional f_r to this equality, for every pair of ports
p,r, proves

    sum_i u'_i(p) q'_i(r) = sum_j b_j(p) b_j(r).

Thus the target operator is unchanged and both supports shrink term by term.
Plane closure preserves inclusion. Deleting rows and columns cannot increase
binary rank, so C(u'_i,q'_i)<=C(u_i,q_i).

This argument uses no bound on query count, target count, representation rank
or external dimension. It does not require a common external seed, a query
inside the target span, or a totally unimodular coefficient matrix. Numeric
coefficients and dependencies not needed for the two requests need not be
preserved by a more general transfer, but full rank preservation suffices here.

## Expanded rank proves the tariff

Expand each scalar port to its two plane coordinates. Replace a scalar matrix
entry M_pr by M_pr times the binary 2-by-2 Gram block between the planes at
p and r, interpreted over E. This is an E-linear map of scalar matrices.

The expansion of T is a diagonal matrix with two ones for every selected
indicator port. A diagonal scalar entry contributes I2. Two distinct scalar
ports in one indicator lie in different planes of an orthonormal group, so
their Gram block is zero. The two ports of one plane lie in different halves,
so their scalar T entry is zero. All remaining scalar T entries are zero.
Hence the expanded rank is

    2 sum_j |supp(b_j)| = sum_j m_j.

The expansion of each u'_i(q'_i)^T factors through its complete-plane Gram
matrix, by selecting, repeating and scaling plane rows and columns. Its rank
over E is at most the rank of that binary matrix over E. Binary matrices have
the same rank over F2 and every characteristic-two extension, since their
nonzero minors remain nonzero in an extension field. The latter rank is
C(u'_i,q'_i). Rank subadditivity and support containment prove the theorem.

Each original b_j term has complete-group identity Gram matrix and tariff m_j,
so the floor is sharp. The complete retained P112 partition has 112 ports and
whole tariff 224. No smaller tariff or new multiplication exponent is derived.
The expanded-rank argument retains Philippe Van Velzen's and PR3345's credit.

## Near-regular configurations give non-TU examples

A sufficient algebraic certificate is a rational-function matrix A(t) all of
whose nonzero square minors have the form

    +/- t^a (1-t)^b, with integer a,b.

These are standard near-unimodular matrices. Interpret their entries in the
ring Z[t,t^-1,(1-t)^-1]. Specializing t to any s!=0,1 in any field keeps every
nonzero minor nonzero and every zero minor zero. In particular t=omega in
GF4, with omega^2+omega+1=0, gives the required characteristic-two
representation. This elementary specialization argument is self-contained;
it does not invoke a classification or recognition theorem for matroids.
The terminology follows Whittle and Hall, Mayhew and van Zwam, cited in the
README. No new matroid representation theorem is claimed.

Here is the explicit rank-five certificate used in the replay. Let e_1,...,e_5
be the coordinate columns. The eleven query columns are

    e1,e2,e3,e4,e5,
    e1-e5, e1-t e5, e2-e5, e3-e5, e4-e5, e2-e3.

Append the four distinguished target columns e1,e2,e3,e4. Only one matrix
entry depends on t, so every square determinant is a polynomial of degree at
most one. Its values at t=0 and t=1 determine it exactly over Z. Both checkers
exhaust all 15,503 square minors and obtain only

    0, +/-1, +/-t, +/-(1-t).

That finite exhaustive polynomial certificate proves unchanged subset ranks
for this entire one-parameter family over every field with s!=0,1. The
primary additionally compares all 32,768 subset ranks at rational s=2,3,-1
and at GF4 omega. The separate checker uses permutation determinants and
hereditary independent-set ranks, with no primary imports.

The four columns e1,e5,e1-e5,e1-s e5 form four distinct projective points on a
rank-two line. Every pair is independent when s!=0,1. Over F2 a rank-two
space has only three nonzero directions, so this U2,4 restriction has no
binary representation. Consequently this augmented configuration is not
regular and has no projectively TU representation. This distinguishes the
example from PR3491's hypothesis. The extra edges couple all four marked
targets through e5, and the representation has rank five, so queries are not
restricted to the target span. The theorem does not rely on the possibility
of decomposing this example into independent pair replacements.

For each literal example, map e1,...,e4 to the selected indicators numbered
0,2,4,6, and map e5 to the port vector z_p=((3p mod 7)-3)/2. This map is
injective, checked by exact rank five. The supplied query configuration
therefore has exactly the certificate's labelled matroid. Each extra query
gets a deterministic arbitrary global reader. Subtract its coordinate
contribution from the five axis readers. This constructs an exact rational
factorization including outside-support cancellations. The replay builds the
new GF4 source functionals and readers and checks every operator entry, both
support inclusions and every actual rectangular tariff. The original bills
are not candidate improvements. A second sixteen-port geometry tests the
same mechanism with repeated binary labels across groups.

## Boundary and next decision

This theorem narrows a search for a cheaper factorization to configurations
without a characteristic-two representation on either side. Failure of that
hypothesis does not predict a saving or disprove a different support transfer.
Finding such a representation is not automated for arbitrary input, and this
package supplies no universal matroid-recognition algorithm.

The full target/query representation is a hypothesis, not a conclusion inferred
from a few minors or an equal rank profile. The finite certificate establishes
it only for the displayed family. General claims rely on the written proof.
Native acquisition, scalar execution, frames, dirty restoration, ownership,
hosting, stock, precision, all-size/compiler admission, complete supplier bills
and outer multiplication transfer remain unproved. Independent human and
formal proof-kernel review are unclaimed.
