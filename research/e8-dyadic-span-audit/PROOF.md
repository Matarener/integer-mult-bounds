# Certificate-to-field argument

@CubeJerry, with substantial OpenAI Codex assistance.
Apache-2.0. This is a written proof supported by exact finite certificates,
not a formal proof-kernel result. The audited theorem is Nick Petalas's
PR6198 statement, retained verbatim in `predecessor/PR6198-PROOF.md`.

## 1. A certificate valid in every allowed field

Let D = Z[1/2], A an m-by-n integer matrix, J an ordered set of r distinct
column indices, E an r-by-n matrix over D, and C an r-by-m matrix over D.
Suppose

    E = C A,       E[:,J] = I_r,       A = A[:,J] E.              (1)

For every field K of characteristic different from two there is a unique
unital map D -> K. Apply it entrywise to (1). The middle identity makes
the rows of E independent over K. The first identity puts them in the
row space of A; the last puts every row of A in their span. Thus A has
rank exactly r over K, with the same explicit basis and reconstruction.
This also proves the row-module identities over D before specialization.

In the artifact a dyadic number is `[n,e]`, meaning n/2^e. The verifier
requires reduced pairs and bounded integer entries. It decodes each row
to a common power-of-two denominator and checks (1) by integer products.
For example, E=C A is checked as

    denominator(C_i) * numerator(E_i,j)
      = denominator(E_i) * sum_k numerator(C_i,k) * A_k,j.

No rank oracle, floating point, determinant, modular elimination, inverse
Gram matrix or assertion disabled by Python `-O` participates in acceptance.
The rational generator is only a way to find the witness. Its correctness
is not needed once (1) has been checked on the intended input matrix.

## 2. Binding the root inventory and domain

PR2819's pinned `checks/e8lib.py` describes norm-two roots: two signed
unit coordinates, or eight coordinates +/-1/2 with an even number of
minus signs. Doubling gives exactly the norm-eight points in

    {x in (2Z)^8 : sum(x) is divisible by 4}
      union {x in (2Z+1)^8 : sum(x) is divisible by 4}.            (2)

To see completeness, an even norm-eight vector has exactly two entries
of absolute value two. An odd vector of norm eight has all eight entries
of absolute value one; the sum condition is precisely even sign parity.
Every coordinate has absolute value at most two. `geometry.py` enumerates
(2) by a meet-in-the-middle norm budget, then chooses one sign per line.
The result has 240 signed roots and 120 lines, each with norm eight.
This independent ordering is not the predecessor's ordering. Keys in this
artifact always use this ordering; their matrices are rebuilt on every run.

Fix F=(2,2,0,0,0,0,0,0). Integer dot products select orthogonal roots.
Distinct lines have dot product 0 or +/-4; norms are eight. Hence the
orthogonality relation is unchanged in every permitted field. The following
whole matrix families are certified by (1), without choosing a tested prime:

* The 63 roots orthogonal to F: rank seven.
* Every other line U: anchors (F,U) rank two, common orthogonal roots rank six.
* Every unordered pair U,V of the 56 nonorthogonal neighbors of F:
  anchors (F,U,V) and their common orthogonal roots. All 1,540 pairs are
  included. Exactly 1,512 have anchor/complement ranks 3/5; the other 28
  have ranks 2/6. Thus the rational admissibility condition and its exclusion
  are preserved in all the fields, and no projected-direction test determines
  which triples get certified.

The ordinary coordinate dot product on K^8 is nondegenerate. The common
orthogonal rows are contained in the kernel of the anchor matrix. Its
dimension is eight minus the certified anchor rank. The certified complement
rank equals that dimension, so containment is equality. These are precisely
S1, S2 and S3prime. It is unnecessary for the anchor subspace itself to be
nondegenerate: for F and U=(2,0,2,0,0,0,0,0), the anchor Gram determinant
is 48, which vanishes in characteristic three, although a two-column anchor
minor is four. F+U is a nonzero vector in the anchor plane's radical modulo
three. The ambient kernel argument still applies. This concrete control
rejects the stronger, incorrect premise that all anchor Gram matrices must
be invertible.

## 3. Projected directions

For a doubled root U nonorthogonal to F and different from F, form

    V_U = 8 U - (U dot F) F.

This is sixteen times the projected vector w_u in PR6198's norm-two
convention. The greatest common divisor of its coordinates is a power
of two; sign and gcd normalization are therefore units over D and over K.
The 56 projections have exactly 28 normalized directions, each with two
preimages. This inventory is independently constructed from the lattice.

For each of the C(28,3)=3,276 distinct triples, (1) certifies rank three.
Every direction and every pair occurs in a triple, so none vanishes and
no two become proportional in K. Originally proportional projections stay
proportional because their proportionality factors are dyadic units.
There are therefore exactly 28 directions in K, with no three in a plane:
the claimed W2 conclusion. This is an all-field consequence of integer
identities, not a statement inferred from tested characteristics.

## 4. Explicit transport rather than an orbit search

For every one of the 120 representative targets R, the checker constructs
a matrix Q with integer entries and verifies

    Q^T Q = 16 I,        Q F = 4 R,
    {Q x / 4 : x a signed doubled root} = {all signed doubled roots}.  (3)

Thus T=Q/4 is an invertible isometry over D and every allowed K, takes F
to R, and permutes the root lines. Equations (3) are checked directly for
each target, including all 28,800 signed-root images. No transitivity theorem
or breadth-first traversal is trusted by the checker.

For clarity, the construction behind these small certificates is elementary.
A coordinate permutation followed by an even number of sign flips sends
F to any two-coordinate root; call this map P.
For an odd target R, first send F to the even root A matching R's first two
signs. Then h=A-R is an odd doubled root, h dot h=8 and h dot A=4.
The dyadic reflection H=I-hh^T/4 satisfies H A=R. Set T=HP. The program
checks its complete action anyway. An unused coordinate supplies a second
sign flip when needed to keep P's sign parity even.

Transport preserves orthogonality, independence and the dot-product
projection. It bijects each fixed-anchor domain with the corresponding
domain at the target. Hence Sections 2 and 3 prove the four audited facts
for every anchor, exactly as quantified in PR6198.

## 5. What this does not prove

The result is independent corroboration and a different explicit certificate
of four source-specific geometric claims. The additional 56 witnesses check
their dependent-triple boundary. The certificate does not establish the
remaining characteristic assumptions of PR2819's rank-nine classification,
its SAT encodings or refutations, or any punctured E8 configuration.
It supplies no physical word, native realization, paid invoice or new κ.
The five assumptions of the selected multiplication result remain unchanged.
The trust boundary includes this finite domain specification, the small
integer checker, Python's exact integers, and this written specialization
and transport argument; no complete theorem has been formalized in Lean.
