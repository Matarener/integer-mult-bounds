# Shortest zero-phase tuples when n is two modulo four

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and boundary

Let n=4k+2, k>=0. A tuple x_1,...,x_f in F_2^n has zero
nonconstant quadratic phase when

    sum_t x_tj = 0 mod 4,
    sum_t x_tj x_tl = 0 mod 2  for j<l.

Repeated points are permitted. Its affine span must be all of F_2^n.
The minimum possible length is exactly

    F(n) = 2n+2.

In particular the first new dimension beyond the small two-axis case is
n=6, where the minimum is 14. The proof is uniform in k. The finite
checks below corroborate it; they do not enumerate all tuples at n=6.

This answers the zero-character part of the other-axis-residues question
in [Ali Romman's PR #5635](https://github.com/CrocSwap/integer-mult-bounds/pull/5635).
It does not assert that every phase character has a full-span tuple at
length 2n+2, or identify the complete representation-kernel cutoff.

## 1. The code associated with a tuple

For each j let c_j=(x_1j,...,x_fj) be its binary coordinate row. Let C
be their binary span. The phase conditions imply that C is doubly even,
meaning every codeword has weight divisible by four. Indeed each generator
has weight divisible by four, pairwise intersections have even size, and

    wt(a+b) = wt(a)+wt(b)-2|supp(a) intersect supp(b)|.

The generators are pairwise orthogonal. Bilinearity makes the entire span
self-orthogonal, so the displayed identity proves the weight assertion
inductively. Conversely, a doubly even row span has precisely the required
weight and intersection conditions.

Full affine span is equivalent to rank(C)=n and 1_f not belonging to C.
A dependence between the homogeneous rows (1_f,c_1,...,c_n) is exactly a
nonzero affine equation vanishing at every tuple point. This is the
code/phase interface used in #5635 and Joseph Anglada's #5542, credited
here as a predecessor lemma.

## 2. A two-coset Gauss-sum obstruction

Suppose a tuple of length at most N=2n+1 exists. Append zero points to
reach length N. The n rows stay independent and generate a doubly even
code C in F_2^N. Self-orthogonality gives dim C-perp=N-n=n+1.
Every word of C has even weight, so 1_N belongs to C-perp. Since N is
odd, 1_N is not in C. Hence

    C-perp = C direct-sum <1_N>.

For any x in F_2^N, sum i^wt(x+c) over c in C. Double evenness gives

    sum_(c in C) i^wt(x+c) = i^wt(x) sum_(c in C) (-1)^(x dot c).

The inner character sum is zero unless x belongs to C-perp, and equals
2^n otherwise. Summing by cosets of C therefore leaves exactly two
contributing cosets, C and 1_N+C. Consequently

    (1+i)^N = sum_(x in F_2^N) i^wt(x) = 2^n (1+i^N).

But n=4k+2 gives N=8k+5. The left side is -2^n(1+i), whereas the right
side is +2^n(1+i). This contradiction excludes every f<=2n+1.

The coset calculation is classical binary coding theory. The new step
here is its application to the n=2 mod 4 zero-phase boundary, which the
cited #5635 result leaves open. No new coding classification is claimed.

## 3. An attaining tuple of length 2n+2

On each of k disjoint eight-column blocks use the four rows

    11111111
    10101010
    11001100
    11110000

and on six final columns use the two rows

    111100
    110011.

All other entries of each row are zero. There are 4k+2=n independent
rows and 8k+6=2n+2 columns. Each eight-column block has independent,
doubly even, mutually orthogonal rows. The final two rows have weights
four and intersection two. Disjoint blocks preserve these properties.
Thus the columns give a zero-phase tuple.

The final block's row span consists of 000000 and three weight-four
words, and does not contain 111111. The all-one word on all columns
therefore cannot lie in the full row span. The homogeneous rank is n+1,
so the tuple has full affine span. This attains the lower bound.

At n=6 the six rows are the four displayed eight-column rows extended
by six zeroes and the two displayed six-column rows preceded by eight
zeroes. This is a completely explicit 14-column witness.

## 4. First visibility of the cited zero-phase residual

This corollary uses, without re-proving or replaying, #5635 Sections 3-4.
In that grammar let A_n be its cuspidal affine cancellation element. Its
coefficient at the identity is Psi(1)>0, and it annihilates every tuple
of proper affine span. Let E_r be its diagonal Fourier projector onto
zero nonconstant phase and width residue r modulo four. Set P_r=A_n E_r.
These are fixed group-algebra elements over Q(i); their coefficients
stay outside tensor powers.

For each r the first positive matching width where P_r is visible is

    L_r = 2n+2 + ((r-(2n+2)) mod 4).

Below L_r every tuple surviving E_r has proper affine span by Section 2,
so A_n kills it. At a wrong residue E_r is zero. At L_r append zero
points to the Section 3 witness. This preserves both phase and full
affine span. Only the identity affine map fixes this ordered tuple, so
its diagonal coefficient under P_r is Psi(1)>0. Further groups of four
zero points show visibility at every larger matching width.

Thus for n=6 these first-visible widths are (16,17,14,15), in residue
order (0,1,2,3). They are thresholds for this zero-phase residual, not
claimed thresholds for the complete representation kernel. In particular,
P_r lies outside the central ideal I_r yet vanishes at every smaller
matching positive width, giving a necessary test-width obstruction.
No all-character upper certificate is supplied.

## Verification and limits

The standalone checker constructs this new family, evaluates its literal
phase generators and homogeneous ranks, exhausts all ordered two-axis
tuples through length six, and checks the exact Gaussian-integer
contradiction. Its source proof is authenticated but no predecessor
executable is imported or run. The corollary inherits #5635's cuspidal
cancellation lemma and Green's classical character theorem as cited
mathematical inputs. It does not expand a large affine group.

There is no new kappa, physical native caller, paid invoice, compiler,
precision, tape, stock or complete multiplication theorem. Independent
human and formal proof-kernel review are unclaimed. The selected frontier
and all five framework assumptions retain their status.

Credit Ali Romman #5635/#5529/#5369/#5622, Joseph Anglada #5542, Hiroki
KUMAZAKI #5522, Mihir Srivastava #5521, Jose Manuel, ywz65, Chris R and
the retained native/phase lineage. The length-eight doubly-even code,
finite-field character orthogonality and Gauss-sum method are classical.
