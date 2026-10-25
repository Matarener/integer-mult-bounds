# Independent audit and the sharp one-axis monomial cutoff

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.

## Source and decision

This reviews Sections 2, 3 and 5 of Ali Romman's
[PR5369 proof](https://github.com/aliromman/integer-mult-bounds/blob/18354f41de4dc7bfda4692e814cf1d91a6d619ef/research/native-tensor-cutoff/PROOF.md).
The reviewed source is retained unchanged on base main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`, at
`research/native-tensor-cutoff/PROOF.md`, Git blob
`2d92f17cd8e1064028656cd4ff06c1d38f14ebc0`, SHA256
`b2d31ea52b652f43cc8576affde6092a884d2832820221a43933e7e27dc07041`.
The central ledger records archival intake with scientific review open.

**Scoped assessment:** the phase-character construction, affine separation
and fixed-residue conclusion follow under the written hypotheses. No gap was
found in these implications. The proof below spells out the factorization and
quantifier steps used in that assessment. This is a separate agent-assisted
mathematical audit, not independent human review or formal-kernel acceptance.
It does not validate the predecessor's entire executable checker.

**Additional result:** for the one-axis monomial group, the evaluation rank is
`2 min(f+1,4)` at every positive width f. The least common stabilization
threshold is 3; widths **3,4,5,6** form a complete fixed-program test, with
both four tests and maximum width six necessary. This is a specialization
and sharpening of the source's sufficient window 6,7,8,9. It is not a
correction to that sufficient theorem. No global literature priority is claimed.

## Audit of the general argument

Use the source's exact group: on x in F2^n,

    U(A,t,c,a,b)e_x = i^(c + sum a_j x_j + 2 sum b_jk x_j x_k) e_(Ax+t).

Here A is invertible, c and a_j are modulo four, b_jk modulo two, and the
phase is evaluated at the input. Coefficients of the group algebra element
P are fixed complex scalars outside tensor powers. The same P is used at
every test width. The recipe is independent of width. Those premises are
needed for the four-width implication.

### 1. Binary Gram factorization is sufficient, including singular forms

For any symmetric binary n-by-n matrix B, congruence elimination gives a
direct sum of a one-dimensional identity blocks, b hyperbolic pairs and a
zero radical. To justify the elimination: a vector with self-pairing one
splits off a one-dimensional nondegenerate summand. Once all self-pairings
are zero, a nonzero pairing splits off a hyperbolic pair; repeat until only
the radical remains.

Realize the identity blocks on a separate a-dimensional orthonormal space.
If b>0, the even-weight subspace E of F2^(2b+1) is alternating and
nondegenerate. Indeed E-perp is the span of the all-ones vector, which has
odd weight and does not lie in E. Choose a symplectic basis by successively
pairing a nonzero vector with a vector having pairing one, then passing to
their orthogonal complement. This realizes the b hyperbolic pairs.
Map the radical to zero. Undo the congruence to obtain B=YY^T with at most
a+2b+1 <= n+1 columns (a columns if b=0). No nonsingularity of B is assumed.

### 2. Gram parity and the two-copy correction have different jobs

Given a phase character (r,u,v), start with 0,e_1,...,e_n. Its Gram matrix
is I. Let M have diagonal u mod two and off-diagonal v. Append columns of a
factorization M+I=YY^T. This supplies the desired pair statistics and the
parity of every coordinate count, but not yet its residue modulo four.

If w is the resulting coordinate-count vector modulo four, each u_j-w_j
is even. Set z_j=(u_j-w_j)/2 modulo two and append z twice when z is nonzero.
This adds 2z_j to each coordinate count and zero to each pair count modulo
two. The tuple still contains the original affine basis. Its length is at
most (n+1)+(n+1)+2=2n+4. For ANY prescribed f>=2n+4 with f=r modulo four,
pad with zero points to length f. Coordinate and pair statistics stay fixed;
the constant statistic becomes f modulo four=r. Padding is valid even if
the intermediate tuple has a different length residue.

Thus every phase character is realizable at the appropriate member of the
four-width window. The executable audit uses complete small multisets instead
of this Gram construction; it does not test an independently rewritten copy
of the same factorization algorithm.

### 3. The chosen tuple isolates the affine bucket

Select a bucket (A,t) with a nonzero coefficient function on the diagonal
phase subgroup D. Fourier inversion on
`D = (Z/4)^(n+1) x (Z/2)^(n(n-1)/2)` supplies a character chi with nonzero
coefficient sum. Take its spanning tuple X and put Y=AX+t componentwise.
If another affine map agrees on all of X, it agrees on an affine basis and
is the same map. Therefore the (Y,X) matrix entry is exactly that nonzero
Fourier sum: other buckets cannot cancel it.

The source's sequential sparse Fourier choices are also sufficient: if all
two or four choices on one coefficient coordinate gave zero remaining
tables, inverse Fourier transformation on that coordinate would give the
zero original table. Retain one nonzero table at each stage. There are
O(n^2) coordinates, at most four trials each, with at most s stored terms.
This verifies the stated O(s n^2) exact scalar-operation count. It is not a
bit-complexity bound or a polynomial bound on circuit expansion.

### 4. The residue statement and all-width statement use different quantifiers

For a FIXED residue r, define

    beta(A,t,a,b) = sum_c alpha(A,t,c,a,b) i^(r c).

At any specified f>=2n+4 with f=r modulo four, beta=0 implies a zero
operator by collecting terms. Conversely, a nonzero beta has a nonzero
Fourier coefficient over (a,b). Step 2 realizes that character at this
specified f with constant statistic r, and Step 3 gives a nonzero entry.
Thus the kernel at each such f is exactly the constant-phase relation.

For a single fixed P, zero operators at the four consecutive widths imply
beta=0 for all four r. Fourier inversion on c then gives every alpha=0.
Allowing a different P_f at each width invalidates this last inference:
`[iI] - i^f[I]` is a nonzero group-algebra element that evaluates to zero at
that f. This is an explicit control, not a counterexample to the source.

The central projectors `C_r=sum_c i^(-r c)[i^c I]` show why every residue is
needed. This step and the source's phase grammar were inspected as dependencies
of Sections 2/3/5. Section 4's growing-width projector family and Section 6's
complexity reduction were not audited here.

## Sharp one-axis theorem

For n=1 there is no quadratic pair and GL_1(F2)={1}. The group has exactly
32 elements U(t,c,a), with t in F2 and c,a in Z/4. Write

    P = sum_(t,c,a) alpha(t,c,a) [U(t,c,a)],
    beta_r(t,a) = sum_c alpha(t,c,a) i^(r c).

For a binary tuple x of length f and weight k, its output tuple under
U(t,c,a) is x+t (componentwise), with phase i^(fc+ak). As f>0, the t=0 and
t=1 outputs are distinct. Hence the two translation buckets have disjoint
matrix-entry supports, and evaluation on each bucket is the Fourier map

    (beta_r(t,a))_(a=0..3) -> (sum_a beta_r(t,a) i^(a k))_(k=0..f),
    r = f mod 4.

Every weight 0,...,f occurs. The distinct rows are min(f+1,4) rows of the
invertible four-point Fourier matrix, so each bucket has that rank. The map
alpha -> beta_r is onto. Consequently

    rank rho_f = 2 min(f+1,4)                         (f>=1).

For f>=3, the rank is eight and the kernel is exactly beta_r=0. At f=2 it
is six, so no threshold below three has this stabilization property.

Fourier transformation in c splits the 32-dimensional group algebra into
four eight-dimensional residue sectors. The widths 3,4,5,6 provide rank eight
in every sector and therefore have joint rank 32. The first two positive
consecutive windows have ranks 26 (1..4) and 30 (2..5). The verification
computes those ranks from literal operator entries using Gaussian rational
elimination, without using weights to generate the entries.

Both the number of tests and maximum width six are sharp. The central
projectors above exclude any set missing a residue. More strongly, consider

    R = sum_(c,a=0..3) i^(-2c-3a) [U(0,c,a)] = C_2 Q_3,
    Q_3 = sum_a i^(-3a)[U(0,0,a)].

R has sixteen nonzero coefficients. Its diagonal entry on a weight-k tuple
is 16 exactly when f=2 modulo four and k=3 modulo four; it is zero otherwise.
It vanishes at ALL positive f<6: at f=2 no weight-three tuple exists, and
the other widths have the wrong central residue. At f=6 the tuple
`(1,1,1,0,0,0)` has entry 16. No test set with maximum width below six can
therefore certify all-width equality. Normalizing R by 16 is optional.

This is the monomial subgroup, not PR5376's full Clifford group. The
one-axis full-Clifford cutoff and the all-axis least monomial cutoff are
separate questions. In particular, a shortest affinely spanning realization
of every phase character need not give the least faithful tensor width.
For n=1 even one input point distinguishes the only two affine maps; the
general affine-span requirement is sufficient but unnecessarily strong.

## Complete small character enumeration and its limits

For a tuple, reduce every positive point multiplicity m to
`1+((m-1) mod 4)`. This preserves its support, all phase statistics and
affine span, and weakly decreases its length. Therefore enumerating
`{0,1,2,3,4}^(2^n)` contains a shortest spanning tuple for every character.
The verifier exhausts this domain for n=1,2,3, then evaluates every chosen
witness and zero-padded witness against the literal phase generators.

| Axes | Multisets | Characters | Spanning supports | Affine maps | Largest shortest length for residues 0,1,2,3 |
|---:|---:|---:|---:|---:|---|
| 1 | 25 | 16 | 1 | 2 | 8,5,6,7 |
| 2 | 625 | 128 | 5 | 24 | 8,9,6,7 |
| 3 | 390625 | 2048 | 149 | 1344 | 8,9,10,7 |

Every spanning support is also checked against every affine map, independently
of the tuple minimization. Receipt digests bind the complete sorted minima
tables. These are exact finite character-realization minima; the table is
NOT a claim of least representation cutoff for n=2 or n=3.

The trust base includes Python integers/Fraction, this verifier, its phase
grammar, and the written argument above. Neither predecessor executable is
imported. Source hashes authenticate the reviewed text; they do not validate
its implementation or any mathematical proposition automatically.

## Remaining review obligations

The coNP reduction, general circuit compiler, native composition/inversion
implementation, event8814 adapter and actual caller remain outside this audit.
No physical stock, movement, precision, paid invoice, supplier admission,
selected cold replay or complete multiplication theorem has been checked.
The selected conditional result is unchanged. The two concrete next steps are
an independent Section 6 audit and an actual implementation-to-grammar audit;
neither requires extending this small census.

Ali Romman retains the general four-width theorem and witness construction.
Jose Manuel's phase-sector and native recipe work, ywz65's binary-stream
affine-basis argument, Chris R's tensor-separation work, and the retained
source authors keep their attribution. Symmetric-form elimination, finite
Fourier inversion and Fourier projectors are classical tools; this package
claims a scoped review and explicit one-axis specialization, not those tools.
