# Exact covariance of the archived P104 native recipes

All statements concern the two frozen PR2586 inputs in SOURCES.json, at nine
address bits. The ground field is Q(i), and arrays have 512 complex entries.
The word and native archive are ywz65's work. This package supplies a separate
finite verification of their native change-of-chart identities. It does not
construct a new native word or strengthen the original native invoice.

## Canonical charts and the precise claim

Write computational basis vectors as |x>, for x in F_2^9. For an independent
ordered frame W=(w_0,...,w_(r-1)), complete these columns greedily with the
standard basis e_0,...,e_8. Let G be the resulting binary matrix, A=G^-1,
and Q=I+A^T A over F_2. Set

    q(x) = sum_j Q_jj x_j + 2 sum_(j<k) Q_jk x_j x_k  modulo 4,
    H_W |x> = i^q(x) |A x>.

The phases use the binary representatives 0 and 1 of Q. Define

    C(a,b) = ((a+b+i(a-b))/2, (a+b-i(a-b))/2).

For 0<r<9, the physical chart is

    Delta_W = H_W^-1 C_0^-1 ... C_(r-1)^-1 H_W.

At r=0 it is I, and at r=9 it is the product of all nine inverse C gates.
These special cases are part of the retained canonical convention. This is
the conjugate of the canonical Gamma chart in the pinned
`research/p104-native-channel/vendor/clifford_exact.py`, independently
reconstructed in `chart`. That predecessor executable is never imported.
The inverse matrix is reconstructed by enumerating the completed binary
basis rather than calling its elimination or Clifford compiler.

A stored recipe has the literal order

    U = M_left C_0 ... C_(k-1) M_right.

Each M maps |x> to i^p(x) |B x+b>, using its archived address rows, offset,
linear Z4 phase, quadratic binary rows and constant Gaussian phase. The
verifier validates bijectivity and all numeric ranges before computing its
operator. All arithmetic is integral or Gaussian dyadic, with no numerical
tolerance and no floating point.

The certified finite theorem is

    U = Delta_new Delta_old^-1

for every one of the 1,245 archived records, as operators on every vector in
Q(i)^512. Their 2,070 occurrences are each matched to the literal word's
recorded old frame, new frame and positive rank. Their chronological incoming
frames, all ADD common-frame constraints, private frame lifetimes and final
frames are checked. This covariance theorem does not itself prove the scalar
word's dirty restoration or zero erasure values. Those are separate obligations.

## Complete operator comparison

Use P(p,x,z)=i^p X^x Z^z, so

    P(p,x,z)|v> = i^(p+2 z.v)|v+x>,
    P(p,x,z) P(q,u,w) = P(p+q+2 z.u, x+u, z+w).

Phases are reduced modulo 4 and binary sums are XOR. A signed tableau records
the exact conjugates of the nine X_j and nine Z_j, including their phases.
For a one-coordinate C,

    C X C^-1 = X,
    C Z C^-1 = -Y = i^3 XZ.

Its inverse sends Z to Y=i XZ. These formulas follow directly from the
stated two-by-two matrix. `c_table` uses those identities. For every monomial
appearing in an actual recipe or canonical chart, `monomial_table` reconstructs
its candidate Pauli images, then checks each identity on all 512 computational
columns. In particular, for M|v>=i^q(v)|a(v)>, conjugation has address difference
`a(v+x)+a(v)` and phase difference `p+q(v+x)-q(v)+2 z.v`.
The check compares these with the proposed output Pauli at every v. No
inference from rank, unsigned symplectic data, or a few sampled inputs is used.
The product law then composes the exact signed actions through each circuit.

Here is why those 18 identities determine an operator up to a scalar.
If invertible U and V have the same signed conjugation action, V^-1 U
commutes with every Z_j and X_j. Commuting with all Z_j makes V^-1 U diagonal
in the computational basis, because distinct addresses have different joint
Z eigenvalues. Commuting with every X_j makes its diagonal entries equal
along every cube edge. The cube is connected, so V^-1 U=lambda I. All factors
here are unitary and hence invertible. No external irreducibility theorem is
needed for this finite argument.

Finally the checker compares the complete, exact nonzero column U|0> with
V|0>. Equality forces lambda=1. The column is stored as Gaussian integer
numerators over one power of two. Removing only common factors of two gives
a unique representation for a nonzero dyadic column. The stored receipt
contains a digest of each fully compared tableau and anchor, alongside frames,
rank and occurrences. Digests summarize the comparisons; the verifier does not
accept an identity by comparing hashes of operators.

This criterion is established predecessor mathematics. In particular,
Tekalign's PR3218 supplies a separate Pauli-plus-anchor comparator and proof.
The present contribution is its independent implementation and exhaustive
application to the PR2586 corpus required by PR3406's stated proof dependency.

## Connection to the Newton source theorem

PR3406 at `18a054fd585ab4b2010770ec83cba0c9f28184e3` proves its sharp source
criterion under these exact native identities. This certificate supplies that
finite inherited premise. With the other hypotheses and proof of that pending
result retained, its entrance remains 4 B_9 on 104 independent Y inputs,
2 B_9 on 78 independent N inputs, and B_9 on the other 176 public inputs.
Here B_9 is the Gaussian Newton module introduced for this application by
Clear1nsight/PR3382. This does not independently recertify every other lemma or
turn that conditional restricted-state contract into an actual-caller theorem.

The result is author-checked exact arithmetic, with a separately implemented
comparison path and independent dense controls. It has no human or proof-kernel
review. Physical storage, owners, routing, rounded recursive children, actual
input preparation, a favorable complete bill, tensor-depth transfer and the
selected multiplication theorem remain outside scope. No new kappa is claimed.
