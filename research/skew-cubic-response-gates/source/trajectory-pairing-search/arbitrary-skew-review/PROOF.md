# Independent all-q suffix isolation and inventory review

I find no defect in the rank argument in the pinned
`root-joint/ARBITRARY-SKEW-GATE-PROOF.md`. Its full dynamic row/column
isolation premise can be established for every q>=2 directly from the
repeating suffix in the pinned `caller-joint/joint_prefix.py`, independently
of J's support. The proof below is an all-parameter operator derivation.
The accompanying executable checks are separate finite corroboration.

This review binds the suffix starting at the query3 source post, the stated
folded-base occurrence inventory, and the deletion of the D_u tail. It is
not a new all-q selected-native compiler or a blanket result for altered
scalar topology, more replacement sites, frame retiming, or different
owner/input/output contracts. The parent source checks the full complete
q2/q3 words for36 wider-support X-character kernels; those finite checks do
not constitute an exhaustive test of all general Gaussian Cliffords.

## Actual cuts and the transported column/dual row

Use the parent's notation. Let i be just after the first edited source post
at query3, physically bank2, and let j_r be just after the source post at
query2r, physically bank1. Write A for the propagated column that starts as
e2 at i, and B for the propagated inverse dual row that starts as e2^T.
An ADD d+=c*s updates

    A_d += c*A_s,       B_s -= c*B_d.

A unary G on bank b updates A_b=G*A_b and B_b=B_b*G^-1. A literal BANK_SWAP
swaps the same two components in both lists. Thus BA=I throughout. These
are operators on arbitrary original fields, not evaluations on clean inputs.

At the first cut the source operator P3 itself has already acted. It is
*not* included in A; it reappears explicitly in L=C*T_q*P3 below. This fixes
the left/right convention for the two edited unary sites.

For the base step, query3's pre-continuation fanout copies the physical
source perturbation to every future c bank, then the source continuation
J3 acts on bank2. The following scalar skeleton has the literal sequence

    bank2 += bank0;
    bank3 += bank1; bank1 -= bank3;
    SWAP(bank2,bank3);
    bank0 -= b2; bank1 += c2.

The stage4 scalar entrance subtracts bank1 from every future c bank. The
raw-a restoration subtracts b_l from bank0 for l>=3, then the held-source
cleanup subtracts bank0 and every future b_l from bank3. Substitution in
the displayed A/B update rules gives, just before query4's source query,

    A_1=I, A_3=J3,              B_3=J3^-1,

with every other component zero. In particular the q-1 future-c column
copies cancel at the scalar entrance; inverse-row terms -J3^-1 on raw a
and on future b fields cancel at the held-source cleanup. There is no
promise on those fields and no omitted public dependency.

Query4 applies J3 on bank1, subtracts bank3, swaps banks1/3, then applies
P4 on bank1. Hence at j_2 the only nonzero components are

    A_1=T2=P4*J3,              B_1=T2^-1.

For the induction assume at j_r only A_1=T_r and B_1=T_r^-1 are nonzero.
Let o=2r+1. All ordinary odd-stage operations act on zero perturbation
components except the already-paid fresh N_o on bank1, giving X=N_o*T_r.
In the nonfinal diagonal encoder, next-c += bank1, the existing J_o source
continuation on bank1, and the three literal SWAPs leave

    A_1=X, A_3=J_o*X,          B_3=X^-1*J_o^-1,

with all other components zero. The scalar b/future-c readers at this cut
have zero components in this particular transported direction; they are
still present on arbitrary physical inputs. The next even query applies
J_o on bank1, subtracts bank3 and swaps banks1/3. Its source post P_(2r+2)
therefore leaves only

    A_1=T_(r+1)=P_(2r+2)*J_o*N_o*T_r,
    B_1=T_(r+1)^-1.

No step interchanges J with any fresh transform, whether completed or
future. Indeed this isolation induction uses only invertibility of each
literal J_s, not its skew square. It proves the full forward-column and
inverse-row isolation at every j_r, not merely a source-row rank condition.

## The actual deletion correction

At the final later cut j_q, all subsequent prefix events avoid bank1 except
the last fresh progress N_k, k=2q+1. This includes the final odd source and
delivery, public b/c isolation, and final independent-a query. The tail
events before D_u recovery act only on bank3 and completed public fields.
Consequently deleting the one D_u recovery gives one current-bank factor,
and the entire deletion defect outside that bank is identity. Its current
operator is

    C=N_k^-1 (F_k D_u^-1 F_k^-1) N_k
      =F_(2q) D_u^-1 F_(2q)^-1.

This is a physical-cut equality; D_u is not inverted as a free primitive.
For the two edits U at the old P3 site and V at the old P_(2q) site, the
exact isolated equation therefore gives

    V=L U^-1 R,
    L=C*T_q*P3,              R=T_q^-1*P_(2q).

All original fields and public reader terms outside that one direction are
retained by the full row/column isolation. Different scalar mixes, other
tail deletions, or changes before these cuts require another derivation.

## Exact L telescope and phase

Set B_s=P_s N0^-1 J, D_r=(B_(2r) B_(2r-2)...B4) B3 J.
From the transport recurrence,

    F_(2r)^-1 T_r = B_(2r) F_(2r-2)^-1 T_(r-1),
    F4^-1 T2 = B4 F3^-1.

For example the first identity uses only P_(2r)'s commutation with the
earlier disjoint N factors, N_(2r)^-1 P_(2r)=P_(2r) N0^-1, and
F_(2r-1)^-1 N_(2r-1)=F_(2r-2)^-1. No commutation of J occurs.
Unrolling cancels exactly the even B product in D_r^-1, so

    L_r=F_(2r) J^-1 B3^-1 F3^-1 P3
       =-F_(2r) N0 P3 F3^-1 P3
       =-F_(2r) F2^-1
       =-N_(2r) N_(2r-1)...N3.

The minus sign is the literal scalar from J^-2=-I. It is not discarded as
a phase gauge. This gives ell=4q-4 and rho=nu(T_q)=nu(R). The recurrence
implies rho<=sum_(r=2..q)nu(J_(2r-1))+2(q-2) by native rank subadditivity.

These equations are pointwise identities on the full field. Thus their
all-f use requires the actual whole-field J_f^2=-I, as in the source,
not merely the single-coordinate equation before an uncorrected tensor
power. The finite corroboration uses the exact frozen tensor-family algebra
and four phase residues. The abstract induction is valid for any actual
Gaussian Clifford J_f satisfying that phase-correct equation, regardless
of support or whether its rank is an integral multiple of f.

## Complete paid inventory and rank conclusion

The fixed folded source removes one initial shared J exposure and the
query2 source J, with a charged native N2 in place of the latter source
star. After D_u deletion, the complete chronological J table is:

* two occurrences of J0 (one is inverse and has the same native rank);
* one occurrence of J_(2r), r=1,...,q;
* two occurrences of J_(2r+1), r=1,...,q.

This includes the final independent-a J_k and the final original-k J_k
tail: neither is omitted. The total is3q+2. Every J_(2r-1), r=2,...,q,
in the transport bound has a distinct paid even-query occurrence. Removing
one such count leaves2q+3=n+1. The two edited sites were P3/P_(2q), so
they do not remove any of these J queries.

There are k(n-1)+1 prefix N calls (all fresh calls plus the folded uniform
source N2) and q-1 reverse-current N calls. Their full mass is
A=2[k(n-1)+q]=n(2k-1). In particular no reverse-current public reader
is free and no source-response cost is counted only once merely because
its register is also a public owner.

The rest of the parent's rank algebra is sound. If r=nu(FJ), d=r-2k and
a_s=nu(J_s), then a_s>=d by FJ=(F F_s^-1)J_s F_s. For the retained
Q recovery W, W(FJ)=F N0 P1 has full arity m=2k+2, so nu(W)>=2-d.
From V=L U^-1 R, rank subadditivity in both rearrangements gives

    nu(U)+nu(V)>=|ell-rho|>=ell-rho.

Thus even a charged nonmonomial U is allowed in the lower bound. Cancelling
the q-1 transport occurrences against the paid table gives

    complete mass >= A+2q+(n+1)d+nu(W) >= n*r.

Under the same equal-volume full-bank normalization, when the parent rank
is positive and all positive recursive children are proper relative to it,
the normalized positive-exponent moment also cannot improve: for
0<sigma<=1 and0<a/r<1, (a/r)^sigma>=a/r. If a claimed child is not proper,
the recurrence interface is invalid rather than rescued by this inequality.
The unweighted rank gate does not establish the corresponding conclusion
for heterogeneous bank volumes or altered source-access weights.

## What was independently executed

The event-only recorder invokes the unchanged pinned source generator,
without constructing a second full original-input matrix. Its suffix from
the first edited site agrees event-for-event/operator-for-operator with
the current repaired q2/q3 source. For q2..8, two actual wider-support skew
families from the parent's receipt independently pass every even-cut full
column/inverse-row isolation, the exact T recurrence, L including sign, and
the complete occurrence counts. These finite checks corroborate, rather
than replace, the preceding arbitrary-operator induction.

The complete wider-support all-q default caller/native lowering and outer
supplier transfer are not newly compiled by this review. The rank theorem
is established for the specified repeating suffix, complete inventory and
phase-correct target contract; using it after a new topology or endpoint
change would require rechecking those premises. No new kappa or BIT claim
is made. Source files and frozen prior packages are untouched.
