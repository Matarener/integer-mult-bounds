# Complete ordinary handoff tail for all q

This is a written all-parameter proof of the tail in `handoff_family_tail.py`.
The exact serialized fixtures q=2,3,4 additionally replay all original
columns, actual signed-plane phases and both literal inverse orders. This
is not a formal-kernel proof or a claim that the stated bill is optimal.

Assume q>=2, n=2q+2 banks and k=2q+1 fresh stages, each of two chunks of
length f>=1. The ambient dimension is m f, with m=4q+4=2n. Let N0 and
each fresh Nj be the actual operator `i Hp_f Hq_f`, so Nj^2=-I. The global
i is one i for the whole chunk pair, not i^f. Let Pj swap the common plane
and fresh plane j. Put F=product_(j=1..k) Nj and E=N0 F. E commutes with
every Pi and Nj, including all Gaussian phases.

The prefix in `../caller/handoff_family.py` finishes every original public
bank with E applied to its own arbitrary input. Two carriers remain. Its
affine recurrence is written below, retaining all public readers; this is
the caller interface the present tail requires.

Use completed-E coordinates `(u,h=Nv)` for the two carrier quantities.
A nonfinal handoff pair r, for 2<=r<q, has

    u' = P_(2r+1) (h-A_r),
    h' = -N P_(2r) u + A_r,
    A_r = a + sum_(l=r+1..q) b_l.

Every reader a,b_l is already available as E times its raw input. The
final pair has physical carrier values `F P_(2q) u` and
`F P_(2q+1)(h-a)`; it has no retained continuation. Two N queries turn
F into E on those two carriers. Their ordinary ADDRESS inverse factors
and one scalar a ADD therefore expose E times `(u,h)`.

Reverse each nonfinal recurrence in descending r. Subtract A_r from h',
apply N and then `P_(2r)^-1`; the result is u because N^2=-I. Independently
apply `P_(2r+1)^-1` to u' and add A_r to recover h. Swap the two bank roles.
This uses exactly one native-2f query per reversed pair and only literal
public ADD readers otherwise. It retains every original public column.

At the base, remove P3 from u and swap the carriers so they are
`(p,qfield)=(Nv1,y1)`. Let t,c1 be the two raw pivot inputs, let
`S=a+sum_(r=1..q)b_r`, and put `Q_i=N^-1 P_i N`. The exact first-three-
query base identities are

    p = N[(P2+Q1-I)t + (I-P2)c1] + (P1-2I+Q2) S,
    qfield = N[(Q1-I)t+c1] + (P1-2I) S + b1.

These identities explicitly include the public-to-pivot coupling. They
are stronger than a homogeneous H factorization. Apply this literal core:

    p -= qfield; p += b1;
    p = Q2^-1 p; p -= S;
    qfield += p; qfield += 2S-b1;
    qfield = P1^-1 qfield; qfield -= S; qfield -= p;
    p += qfield;
    p = N^-1 p; qfield = N^-1 qfield.

After the first line, p is `Q2[N(t-c1)+S]`, because `Q2 N=N P2`.
After its Q2 inverse and S subtraction it is `N(t-c1)`. The next line
turns qfield into `P1(Nt+S)`. Its P1 inverse and two subtractions give
Nc1. The last ADD gives Nt on p, and the two N inverses recover the two
original pivot inputs in the completed-E chart. Thus all n outputs are
exactly E times their own independent original inputs.

The physical target E is full native on every ambient plane. All steps
are invertible with no zero helper: reverse the saved event list, negate
every ADD and invert each full unary operator. The producer checks both
inverse orders, not only a one-sided symbolic cancellation. The public
reader omission mutant is nonzero.

The tail bill is two H2 queries to enter the completed chart, q-2 H2 for
the reversed pairs, two final H2 queries, and one H4 for Q2^-1:

    tail: (q+2) H2 + H4,       rank mass 2q+8.

All ADDRESS, bank swaps, native adapters and individual public ADD scans
are separately recorded in the fixture events. The prefix includes all
per-stage idle progress and costs `n k+q+2` H2. Therefore this direct
complete word has `(n^2+2) H2+H4`, rank mass `2n^2+8` against stock
`n m=2n^2`. Its D is -8 for every q. Grouping native children or retiming
the fixed trace may change moments and rank mass; the parent owns those
separate exact screens. This proof does not call an unpriced factory free.

For reference, direct carrier factorization has distinct fresh-native
supports `{5,9,13,...}` and `{3,7,11,...}` after alignment with the fixed
J core, with total q planes. The producer verifies this closed form on
the saved fixtures. Charging each displayed N separately would miss
cancellations, but directly clearing the actual residual still grows
with q. This is a scoped property of the ordinary handoff grammar. It is
not a bound on the changed bit-linear ADDRESS encoder, other native
interfaces, or every joint terminal correction.
