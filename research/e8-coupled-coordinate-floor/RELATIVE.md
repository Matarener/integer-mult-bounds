# A sharp relative 27-deletion bound on an E8 neighbor set

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This is a written characteristic-zero theorem supported by two exact finite
certificates. Its E8 instantiation is not claimed to be formally verified.

## 1. Model and statements

Let E be all 120 unoriented root lines of E8. Choose norm-two representatives
r_x in Q^8 and retain the fixed binary labels u_x in the nondegenerate
nine-dimensional pairing space (Lambda,beta). Thus

    beta(u_x,u_y)=1 iff x=y or (r_x,r_y)=0.

Let K be any field of characteristic zero. Set

    E(h)=((r_x,h))_{x in E},       C=E(K^8),
    U(q)=span_F2{u_x:q(x)!=0},     w(q)=dim_F2 U(q),
    O_z={x:beta(z,u_x)=1},
    H_v=E minus O_{u_v},          W_v=u_v^perp.

Here H_v consists of the 56 nonself root lines nonorthogonal to r_v, and
its labels lie in the binary hyperplane W_v. A scalar normal h is a
**root normal** if it is proportional over K to some r_a. A word is
**deficient** if w(q)<=8. Transposes elsewhere in the decoder model are
ordinary transposes; no complex conjugation is used.

**Theorem R (relative nonroot deletion bound).** Suppose h in K^8 is
nonzero and is not a root normal. If d is supported on H_v and
E(h)+d is deficient, then

    |supp(d)|>=27.                                         (R)

The bound is sharp. More precisely, for every nonzero binary character z,

    Off(h) intersect O_z subset H_v
        => |Off(h) intersect O_z|>=27,                     (R')

where Off(h)={x:(r_x,h)!=0}. The minimum in (R') is attained by a rational
nonroot normal. Taking d=-E(h) on this intersection and zero elsewhere
gives a deficient word with exactly 27 correction coordinates.

**Corollary E (eligible-root classification up to 23 neighbors).** Let
A subset H_v have |A|<=23, let D' be any scalar subspace supported on A,
and suppose

    q=E(h)+d, h!=0,d in D', w(q)<=8.

Then h=c r_a for some a in A and c!=0, and

    U(q)=u_a^perp,       w(q)=8,
    d(a)=-2c!=0,
    d(x)=0 for every x!=a orthogonal to r_a.                (E)

Thus the SAME vector d in the actual coefficient space D' is a root-swap
eligibility witness for a. The assertion does not enlarge D' to the full
coordinate space supported on A, and makes no binary-rank assumption on A.

The number 23 is sharp for this eligible-root-only classification: a
24-coordinate neighbor correction can create a deficient root word whose
own root coordinate is not corrected. Section 6 supplies such a word. This
is a classification boundary, not a counterexample to the COPY floor.

## 2. Reduction to a finite relative cut statement

If q=E(h)+d has w(q)<=8, choose a nonzero z in U(q)^perp. Then q vanishes
on O_z, and therefore

    Off(h) intersect O_z subset supp(d) subset H_v.         (1)

It suffices to prove (R'). Two different exact finite methods do so. Both
start from the complete standard E8 root inventory and its integer Gram
matrix, rather than a floating-rank test or a sampled coefficient grid.

The first method classifies all scalar zero patterns by standard parabolic
subsystems. The second fixes v and classifies the exact scalar kernels
forced by (1), with a separate complete parabolic treatment of one
exceptional character. Their independently constructed minima agree at 27.

## 3. Certificate by all parabolic zero patterns

For a rational nonzero h, its root zero set

    Z(h)={x:(r_x,h)=0}

is Weyl-conjugate to a standard parabolic root subsystem. One proof takes
the stabilizer of h in the finite real reflection group: it is parabolic,
and its roots are exactly the roots perpendicular to h. This is the same
classical parabolic argument used in PR3166, PROOF section 4; no new
classification theorem is asserted here.

Choose the pinned eight-root simple basis from that source. For every
proper simple-root subset J, let Z_J be all root lines in its scalar span.
There are 255 proper subsets. Exactly one has rank 7 and 63 root lines: E7,
whose perpendicular is a root line. It cannot be Z(h) for a nonroot normal.
The remaining 254 subsets cover all possible nonroot zero patterns up to
Weyl action; repeated isomorphic types cause no omission or difficulty.

The executable certificate checks the simple-root coordinate signs of all
120 roots and builds each Z_J by its exact simple-coordinate support. An
independent nullspace implementation checks the equivalent membership
criterion against the same fixed simple basis. In particular Z_J is a
standard parabolic root set, not an arbitrary root set of that cardinality.

After a Weyl transformation taking Z(h) to Z_J, the distinguished v may
become any root v'. The transformation also induces an invertible binary
isometry on Lambda, so z becomes some nonzero z'. Accordingly, enumerate
all 120 choices v' and all 511 choices z' for each retained J. Write

    F_J=E minus Z_J.

The pair (v',z') is admissible exactly when

    F_J intersect O_{u_{v'}} intersect O_{z'} is empty.      (2)

For an admissible pair, its required correction set is exactly
F_J intersect O_{z'}, and (2) puts that set inside H_{v'}. The exact
integer-mask scan records

    254*120*511 = 15,575,280 comparisons,
    30,492 admissible pairs,
    minimum |F_J intersect O_{z'}| = 27.                  (3)

These are integer set intersections. The scan is not a numerical
optimization over possible h: Weyl/parabolic completeness has already
reduced every scalar support pattern to the finite inventory.

For sharpness, an attaining entry has simple subset 191, a 37-line zero
subsystem, root index 113, character 463, and standard-coordinate normal

    h=(0,0,0,0,0,1,1,2).

The cofactor kernel computation verifies that this nonroot normal has the
required exact zero pattern and the 27 listed correction coordinates. Root
indices and characters here use the declared A8 pair-then-triple ordering
bound to the standard-coordinate inventory. This witness is stored with
the full deleted-index list in the certificate; its existence does not
depend on a floating norm comparison.

## 4. Independent certificate by fixed-root kernel strata

Fix the root at index 0. Every h in (1) annihilates the rows on
O_{u_v} intersect O_z. Compute the exact rational kernel

    T_z=ker_Q rows(O_{u_v} intersect O_z).

For all 511 nonzero characters, the kernel-dimension counts are

| dimension | characters |
|---:|---:|
|0|256|
|1|198|
|2|56|
|8|1|

Dimension 0 admits no nonzero h. For dimension 1 there is only one
projective normal. All 198 such normals are root normals, with required
cut sizes 24, 28, 32 in multiplicities 63, 72, 63 respectively.

For dimension 2 choose a rational basis b_0,b_1. Every root x in O_z
induces a form

    L_x(s,t)=(r_x,b_0)s+(r_x,b_1)t.

Each nonzero form has exactly one projective zero ray; these finitely many
rays are the complete critical strata. On their complement, every
nonzero form stays nonzero, so all remaining scalar normals have exactly
the same support on O_z. This proves completeness over every
characteristic-zero K, including nonrational projective ratios. Each of
the 56 two-dimensional kernels has one critical root ray requiring one
deletion, one critical nonroot ray requiring 27, and a generic stratum
requiring 28. A rational nonroot witness for the generic stratum is
constructed outside its finitely many critical and root rays.

The sole large kernel is verified explicitly, rather than skipped. In
the odd-weight A8 label model let omega=(1,...,1), so O_omega=E. Its
character is

    z=omega+u_v,
    O_z=H_v,
    O_{u_v} intersect O_z is empty.

At index 0 this is character 3, since u_v=508 and omega=511. Its kernel is
all eight scalar dimensions. To handle it, enumerate the same 255 proper
simple-root subsets and all 120 root positions, excluding the verified
root-normal E7 case. The maximum number of zero roots in a neighbor set is
21, hence every nonroot normal has at least 56-21=35 nonzero neighbor
coordinates. A generic rational normal realizing the maximizing zero
pattern is constructed and checked. Thus this exceptional character
cannot reduce the 27 minimum. Any other kernel of dimension greater than
two causes the checker to reject; no unclassified stratum is accepted.

This method also checks an exact root-reflection spanning tree connecting
all 120 root positions. Along an edge |(r,w)|=1, reflection in
r-sign(r,w)w sends r to plus/minus w. Its action is checked to permute
the complete root inventory. The recorded 56 distinct reflections give
6,720 root-image checks. Thus the fixed-root result transports to every v.

## 5. Binary transport and arbitrary characteristic-zero fields

A Weyl root permutation preserves the integer Gram products up to the
signs used to choose line representatives. Those signs do not change
orthogonality or B_d, so the dense binary pairing is preserved. Because
the labels span the full nondegenerate nine-dimensional binary space,
the root-label permutation extends to an invertible binary isometry:
pair any transported label relation with every transported root label;
all pairings vanish, and nondegeneracy forces the transported relation
to be zero. The inverse permutation gives invertibility. It therefore
also permutes all 511 nonzero characters. This justifies transporting the
scalar zero set, the neighbor condition and the binary cut simultaneously.

For general K of characteristic zero, only scalar zero/nonzero patterns
enter the argument. Let the rows vanishing on h define their rational
kernel T_Q. Its scalar extension contains h. Every designated nonzero
row is a nonzero functional on T_Q; otherwise it would also vanish on h.
Avoiding finitely many proper rational hyperplanes gives a rational
normal with exactly the same root zero set. If that set were E7, its
rank 7 would force the original K-normal to the same K-root line,
contrary to the nonroot hypothesis. Thus a rational nonroot support
pattern occurs in the 254 retained parabolic cases. This is the rational
zero-pattern transfer from PR3166, applied to the new relative cuts.

Equivalently, in the fixed-root method the rational kernels T_z extend
to K with unchanged dimensions, and the one-/two-dimensional critical
form classification remains exact. These arguments neither put an
ordering on K nor use positivity of a K-valued norm. No extension of
Theorem R to positive characteristic is inferred from the rational
certificate.

Equations(1) and(3), or the independent kernel certificate, now prove(R).

## 6. Eligible-root consequence and its 24-coordinate boundary

For the corollary, Theorem R excludes every nonroot h because |A|<=23<27.
Write h=c r_a. The full E8 nonself root remainder has minimum nonzero
binary character cut 24, as recomputed in PR3166. Hence for every
z!=u_a,

    |Off(r_a) intersect O_z|>=24.                          (4)

The matching cut is Off(r_a) intersect O_{u_a}={a}. Any annihilator of q
would require canceling its cut inside A. By(4), every nonzero annihilator
must be u_a. Therefore its annihilator has dimension exactly one, so
w(q)=8 and U(q)=u_a^perp. Vanishing at a gives d(a)=-2c!=0, proving
a in A. At any other root orthogonal to r_a, both E(h) and q vanish,
giving d(x)=0. This is precisely the actual-space eligibility assertion(E).

The following exact word shows why this classification stops at 23. In
the declared standard-coordinate/A8 ordering take

    v=a=0,  r_v=(0,1,-1,0,0,0,0,0),
    u_v=508,  z=12,
    A_minus={1,2,44,45,46,47,48,49,50,51,52,53},
    A_plus ={8,9,65,66,67,68,69,70,71,72,73,74},
    A=A_minus union A_plus.

All 24 roots in A are nonself neighbors of v. Their root products with
r_v are+1 on A_minus and-1 on A_plus. Moreover

    Off(r_v) intersect O_z=A,
    beta(z,u_v)=0,
    d=-sum_{x in A_minus}delta_x+sum_{x in A_plus}delta_x,
    q=E(r_v)+d=E(r_v)-E(r_v)|_A.

Thus q vanishes on O_z and w(q)<=8, while v is not in A and
q(v)=(r_v,r_v)=2. The root's own coordinate has not been canceled, so
this is not an eligible root hole for the actual correction space.

The coefficient normalization matters: the stored standard rows are
R_x=2r_x, so E(r_v)(x)=(R_x,R_v)/4, not (R_x,R_v)/2. Therefore each
displayed correction coefficient is exactly+1 or-1 and q(v)=2 as stated.
There is no hidden factor-of-two rescaling of the root or its hole.

This word disproves only the stronger eligible-root-only classification
at 24 neighboring coordinates. It is not an exact all-pairs decoder and
does not contradict COPY>=72. It also does not weaken the sharp nonroot
bound 27: its scalar normal is the root r_v.

## 7. Credit and evidence boundary

PR3166 supplies the weighted root-swap definition, full remainder 24 input,
the standard simple-root coordinates and the characteristic-zero
parabolic/zero-pattern argument. PR3755 supplies the fixed full-E8
root/label binding and singleton context. The new finite statement is
the relative nonroot minimum 27 under the requirement that all deleted
coordinates lie in one root's nonself neighbor set. The two finite
methods above certify it by different complete reductions; their matching
outputs do not constitute independent human review.

The relative theorem strengthens the neighbor-supported partial-quotient
consumer's root-only input from 13 to 23 coordinates. Its later COPY proof
must still retain the actual-basis deficit and low-rank exit arguments;
the relative cut bound alone is not a decoder theorem. No positive-
characteristic, physical supplier, shared COPY, masked-universality or
multiplication-exponent conclusion is asserted here.

## 8. A different threshold: mixed weight at most seven needs 29 neighbors

The eligible-root classification above stops at 23, but the coupled
consumer needs less than that classification for every weight-eight
word. The following sharper low-weight statement extends the raw neighbor
consumer to 28 coordinates without extending Corollary E.

**Theorem L (low mixed words).** If d is supported on H_v, h is nonzero,
and w(E(h)+d)<=7, then |supp(d)|>=29. The bound is attained by a root
normal and a 29-coordinate neighbor correction. This remains a statement
about corrected words, not a decoder counterexample at 29 coordinates.

For a nonroot normal, the global perpendicular-root bound already gives
|Off(h)|>=78. A word of binary weight at most seven has at most 36 support
coordinates. Therefore at least 78-36=42 coordinates must be canceled.
No additional nonroot projective census is needed for Theorem L.

It remains to consider h=c r_a. Scaling by c!=0 does not change any
support, so take h=r_a. Put

    T_{v,a}=Off(r_a) intersect O_{u_v},
    Z_{v,a}=span_F2{u_x:x in T_{v,a}}^perp.

The correction is zero on O_{u_v}. Any support annihilator of E(r_a)+d
must consequently belong to Z_{v,a}. A word of weight at most seven
has an annihilator of dimension at least two. Thus every independent
pair z,t in that annihilator requires cancellation of

    Off(r_a) intersect (O_z union O_t).                     (5)

All these required coordinates must lie in H_v. The exact all-position
certificate root_low_primary.py checks the following complete cases for
all 120*120 ordered pairs (v,a).

* If a=v, the forced support is {a}, of label rank one. Every allowed
  character lies in u_a^perp. Its restriction to the 56-line nonself
  remainder is injective on any two-dimensional allowed character
  space: the remainder's annihilator is F2 u_a, and u_a is not in
  u_a^perp. Thus z,t,z+t all cut that remainder nontrivially. Each cut
  has at least 24 coordinates. Writing N(s)=H_a intersect O_s for these
  remainder cuts, their union has size
  (|N(z)|+|N(t)|+|N(z+t)|)/2, hence at least 36.
* If a!=v and (r_a,r_v)!=0, the forced label rank is seven. Its
  annihilator is exactly one two-dimensional space, with three nonzero
  characters. The certificate checks that (5), for a basis of that
  space, is contained in H_v and has exactly 29 coordinates. After
  canceling them, the remaining root support has binary rank exactly
  seven. All 6,720 ordered neighbor pairs have these properties.
* If (r_a,r_v)=0, the forced label rank is eight. Its annihilator has
  dimension one, so a corrected word cannot have weight at most seven.
  This accounts for the remaining 7,560 ordered pairs.

The self-root case accounts for 120 ordered pairs. These counts exhaust
all 14,400 pairs. The independent root_low_audit.py fixes one pivot and
enumerates all root normals and every two-dimensional allowed character
space: 10,851 distinct planes, with minimum required union 29. The
root-reflection transport in section 5 gives its all-pivot interpretation.
These are binary annihilator spaces and exact support unions, not a grid
of scalar coefficients. Root evaluations have unchanged zero patterns
over every characteristic-zero K, so the argument covers all such fields.
Together with the nonroot bound 42, this proves Theorem L and its stated
attainment.

Here is why Theorem L is enough for the stronger coupled result. Let
A subset H_v, |A|<=28, and let D' be the actual partial coordinate space
after left proportional merging, as in EXTENSIONS.md. Every pure D' word
has weight at most eight, and Theorem L says every mixed word has weight
at least eight. Write gamma=c(D') and let r be the scalar rank of the
normal directions of all mixed weight-eight words. These normals may
now include nonroot normals; they are not globally asserted eligible.

If gamma>=8, simply r<=8<=gamma. If gamma<=7 and dim D'>=2, choose a
minimum basis of D'. The union of its supports has at most 21 coordinates.
Indeed each basis weight is at most six. If one is six, the other weights
sum to at most one, giving the capacity bound 20+1. Otherwise every
weight is at most five, where the displayed capacity table satisfies
g(w)<=3w, so the union has size at most 3gamma<=21. Every vector of the
same D' is supported on this union. Corollary E therefore applies to
every mixed weight-eight word, now with an effective support set of at
most 21 neighbors. Its same-space eligibility assertion and PR3166
Theorem A give r<=gamma. Thus in every case relevant to the partial
consumer,

    r<=c(D'),       r<=8.                                  (6)

The actual-basis count in EXTENSIONS.md needs only the absence of mixed
words of weight at most seven and (6), rather than eligible-root shape
for every weight-eight word. It gives every basis bill at least 72 and,
when dim D'>=2, makes every actual bill-72 basis's low members span D'.
The dim D'<=1 cases instead use PR3755's rank-at-most-nine theorem.

For neighbor support the free-pivot cut is always exactly D', with no
support-size or root-only assumption: a cut word E(h)+d supported on H_v
has E(h)=0 on O_{u_v}, whose root rows have scalar rank eight, so h=0.
Low members are supported on H_v and cannot carry u_v in their binary
support spans. Consequently every rebated actual equality-basis coordinate
annihilates this cut, as required by the generic coupling lemma. This
completes the raw neighbor-supported COPY>=72 theorem through 28
coordinates. It does not extend the eligible-root-only classification
past 23, and it makes no claim that the COPY floor fails at 29.


## 9. Completing the nonroot low-word boundary: 55 is sharp

The coarse nonroot lower bound 42 used in Theorem L is sufficient for the
28-neighbor consumer. A separate exact calculation sharpens it to 55:
if h is nonroot, d is supported on H_v and w(E(h)+d)≤7, then
|supp(d)|≥55. Equality occurs. Thus any mixed low word arising with
29 through 54 neighbor corrections has a root normal. This does not
extend the decoder invoice past 28 by itself.

For the first complete reduction, take each of the 254 nonroot parabolic
zero patterns Z_J and every root v, and form the forced binary support

```
F=(E minus Z_J)∩O_{u_v}.
```

Over all 30,480 ordered pattern/pivot cases its label rank is eight in
30,474 cases and seven in six cases. A weight-at-most-seven corrected
word needs at least two independent support annihilators, all of which
must annihilate F. The rank-eight cases are therefore impossible. In
each rank-seven case the allowed character space is exactly two-dimensional;
its unique plane requires canceling at least 55 neighbor coordinates,
with equality attained.
`neighbor_primary.low_weight_run` checks all cases and an explicit
nonroot normal, correction set and attained remaining binary rank seven.
Weyl/binary transport and characteristic-zero zero-pattern transfer are
exactly those justified in sections 3 and 5.

A second algorithm uses the fixed-root scalar kernels T_z from section 4.
Any two-dimensional binary annihilator plane has a nonzero character z
other than the sole complement character. Thus its scalar normal lies
in a kernel of dimension at most two; the omitted dimension-eight kernel
cannot by itself supply a plane. For each two-dimensional T_z, classify
the projective zeros of the linear forms from **all 120 root rows**, and
one generic stratum avoiding those zeros. Dimension-one kernels have one
ray. This is a complete support-pattern classification for every possible
two-annihilator word, including nonrational scalar ratios; it is not a
claim that all scalar normals are covered.

The separate implementation obtains 169 distinct relevant root-support
patterns, enumerates their allowed binary planes (10,963 in total), and
minimizes the required union of the two character cuts. It finds root
minimum 29 and nonroot minimum 55. The complement character is included
when enumerating allowed binary planes; it is omitted only as a scalar
kernel entry because every plane also has another nonzero character.
Both minima have explicit rational attaining words of binary weight seven.

The primary nonroot attainer uses the same normal
h=(0,0,0,0,0,1,1,2), root index 113 and simple subset 191 as the relative
27 witness. Its required plane has nonzero characters 224,303,463 and
55 deleted coordinates, stored in RESULT.json. Set d=−E(h) on those
coordinates and zero elsewhere. The checker binds the exact zero pattern,
neighbor containment and remaining label rank, so sharpness is an actual
word rather than a feasible cardinality profile.

These calculations complete the natural geometric threshold table:

| Scalar normal | Corrected binary weight ≤8 | Corrected binary weight ≤7 |
|---|---:|---:|
| nonroot | 27 neighbor deletions, sharp | 55 neighbor deletions, sharp |
| root | 1 via a matching hole; nonmatching cut starts at 24 | 29 neighbor deletions, sharp |

The still-open next invoice case is therefore a root-normal low-direction
problem beginning at 29, not a generic nonroot low-direction search.
