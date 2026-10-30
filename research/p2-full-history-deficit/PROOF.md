# The complete fixed caller needs at least 225 new returns

The model is the frozen p2 caller of Dugongue's PR4948 and Chris R's PR4978.
Keep all 39 observed bank fields, all original paid inputs and all required
outputs. Ordinary operations are scalar row operations and left actions from
the full columnwise monomial Clifford algebra. All storage, COPY and owned
reset may be free. New paid returns may be arbitrary linear fields, may use
older new returns, and have the same capacity as one original field. Changing
an original paid input, observing a native internal prefix, changing capacity,
using noncolumnwise maps or changing target credit is outside this contract.

At every width f>=72, the complete target needs at least 225 new returns.
In the enlarged arbitrary-linear-oracle model, 240 returns suffice. The exact
minimum between these bounds is open. This is not a native 240-call word.

## 1. Source and algebra

Use n=17 axes: shared axis 0, first fresh axes 1..8 and second fresh axes 9..16.
Write D1,D3 for the two rank-eight Gaussian blocks and Q for the shared rank-one
Gaussian. Put D=D1 D3 and

    C_s = diag(K_s)^-1 F^T diag(K_s),  s=1,3.

The literal source gives C_s^2=I, [C_s,D_s Q]=0 and [C_s,D_t]=0 for s!=t.
The signed K words are monomial. Their binary linear parts G_i are orthogonal.
The verifier checks all 112 signed commutations with the full local Gaussian,
including absolute phase. It also checks the actual transpose and (F^T)^2=I.
The source scalar coefficients stay outside tensor powers.

There are 448 independent original main fields and 816 independent autonomous
helper outputs. Snapshots add no independent input or target credit. On a
restriction to main inputs, the autonomous helper outputs vanish. This does
not grant native internal helper states as observations.

Let H be the finite projective monomial Clifford group on 17 axes. At fixed f,
let A be the span of its tensor lifts, with the phase factors retained in its
multiplication. The credited pointwise theorem in PR5526 gives dim(A)=h=|H|
for f>=72. It also makes different full-Clifford projective classes linearly
independent at these widths. Thus distinct left H cosets give disjoint free
A-modules. Multiplication by a Clifford unitary is injective on A.

This uses the full fixed Clifford universe, not a width-dependent alphabet.
The pinned uniform-alphabet addendum and owned-reset clarification apply.
No inverse-uncompute cost is used in the lower bound.

## 2. All four banks, before the coupled argument

`OBSERVATIONS.json` records all 156 bank coefficients in the 39 observations.
The D-right and credited D-left normal forms agree on every coefficient.
The union of the D-right term families is:

| Original bank | Term families |
|---|---|
| 0 | I; Q^-1; C1 Q^-1; Q^-1 C1 D1 |
| 1 | I; D1; C1 Q D1 |
| 2 | I; Q^-1; C1 Q^-1; D1; Q^-1 C1 D1; D; C3 C1 D; Q^-1 C1 D; Q^-1 C3 D |
| 3 | I; D1; D; C3 Q D |

The four diagonal targets have grades 9,9,17,17. The actual transpose has
104 zero-diagonal columns and eight diagonal entries equal to 12. All 5,832
nonzero native pair coefficients are checked. Each zero-diagonal column has
52 late words of grade 7 on its own fresh block. Adding the other untouched
rank-eight block gives grade 15. Left monomial factors preserve grade.

For the 104 zero-diagonal columns, bank 0 therefore has grades {0,1,7}; bank 2
has grades {0,1,7,8,15,16}. This gives 208 grade-separated target columns.
The other 240 columns have explicit target-grade terms. Thus 208 is the largest
set obtained by this columnwise grade-absence test. Grade presence does not
mean recovery. The coupled argument below also excludes the eight remaining
columns in each negative bank.

## 3. Coupled rows exclude all 112 columns of each negative bank

Consider E_s=Q^-1 C_s D_s, or E_s=Q^-1 C_s D when both blocks are present.
Its (i,j) entry is a nonzero scalar times

    W_ij = Q^-1 K_i^-1 K_j D_s

on a supported pair. For fixed j, these words lie in distinct left H cosets
as i varies. Here is a direct invariant proof.

A monomial left factor preserves the row space of the X block of a symplectic
matrix. In these source words the X block has an invertible linear part T,
so its row space has unique form [I,R]. For W_ij,

    R = E_s + u_ij u_ij^T,  u_ij=G_j^-1 G_i e0,          (1)

where E_s is the diagonal mask of the fresh Gaussian axes. For both blocks,
replace E_s by the mask of all 16 fresh axes. All 112 vectors G_i e0 are
distinct. Thus the u_ij are distinct at fixed j. Over F2 the diagonal of
u u^T is u, so (1) gives distinct cosets. The same proof works in either
embedded fresh block. All signs and scalar phases leave this invariant fixed.

Every row i of F^T has a nonzero entry in at least one zero-diagonal column j.
Suppose an A-linear combination of the E_s rows has no grade-7 (or grade-15)
component on those 104 columns. In a fixed such column, distinct cosets prevent
cancellation between different i. A nonzero scalar and a Clifford word are
injective on its left coefficient a_i. Thus each supported a_i is zero.
The row witnesses cover all i, so every a_i is zero.

For original bank 0, the other observations have grades 0 or 1. Its target
module has grade 9. The preceding argument proves that its full 112h-dimensional
target module intersects the available history only at zero, including the
eight selected columns. This is stronger than the 104-column grade test.

## 4. The last positive bank forces at least one more return

Set the original bank-1 input to zero; this restriction only helps a decoder.
Separate bank 0 from banks 2 and 3, granting independent use of their projected
histories. This enlarges the available module and is valid for a lower bound.
Write x,z for the 112-field inputs in banks 2 and 3, and T_-=D Q^-1, T_+=D Q.
All observations before D3 have grade at most 9 in these columns.
Every later high-layer observation lies in the A-span of these three row banks:

    Arow = Q^-1 C3 D x,
    Brow = Q^-1 C1 D x + D z,
    Crow = (I-C3 C1)D x - C3 T_+ z.                    (2)

The third paid response is Arow-Brow. The verifier checks (2), the zero
coefficients of the other two original inputs, and the membership of every
high-layer observation. Old terms added at final bridges have grade at most 9.

Let a,b,c be row vectors over A, and ask when a*Arow+b*Brow+c*Crow belongs to
the module of the two prescribed targets T_-x and T_+z. Its z coefficient of
grade 16 is b*D. No other term can cancel that grade there, so b=0. In its x
coefficient, a*Arow has grade-15 off-diagonal components. The other remaining
x term has grade 16. Section 3 therefore gives a=0. What remains is allowed
only if

    c L = 0,  where L=I-C3 C1.                         (3)

Let r be the complex rank of right multiplication by L on row vectors A^112.
The kernel in (3) has dimension 112h-r. Since C3 is invertible, its T_+z image
has the same dimension. The two-target module has dimension 224h. Its deficit
modulo this enlarged history is therefore 112h+r. Bank 0 adds another 112h.
The complete selected target deficit is at least

    224h+r.                                            (4)

The source proves r>0. In entry L_(0,0), the k=0 term of C3 C1 is literally
identity with coefficient 12^2=144. Every other supported k has a nonidentity
binary linear part in the 17-axis product

    K_(3,0)^-1 K_(3,k) K_(1,k)^-1 K_(1,0).

The finite checker verifies this for every supported k. No such term is
projectively identity. Thus the identity coefficient of L_(0,0) is -143.
Pointwise Clifford faithfulness makes L nonzero for every f>=72, so r>0.

One new same-capacity return adds a cyclic A-module of dimension at most h.
This remains true for arbitrary linear returns outside the Clifford span and
for feedback among new calls. Existing paid input expressions remain fixed.
To cover (4), q*h>=224h+r. Since q is an integer and r>0,

    q >= 225.                                          (5)

This proof does not compute r/h. It must not be read as an exact minimum of 225.

## 5. A 240-return upper bound in the enlarged oracle model

The literal F^T is an involution with trace 96 and dimension 112. Therefore
P=(I-F^T)/2 is an idempotent of rank eight. Factor it over Q as P=UV with eight
columns in U. Then

    P_s=diag(K_s)^-1 P diag(K_s)=U_s V_s,
    I-C3 C1=2P1+2P3-4P3 P1.                            (6)

The entries of U_s,V_s lie in A. Ask an arbitrary linear oracle for the 112
negative targets in bank 0 and the 112 negative targets in bank 2. Ask also
for the eight rows V1 D x and the eight rows V3 D x. Ordinary A operations
assemble L D x from (6). Subtract it from Crow and apply -C3 to obtain T_+z.
The first positive bank is already available: its FULL1 X row is
-C1 D1 Q times that original input, so multiplication by -C1 recovers it.
All original helper outputs stay as in the frozen caller. Total: 240 returns.

This is an explicit linear-oracle construction with 16 factored repair rows.
It is not a native supplier or a claim that these rows cost one H1 each.
The exact optimum in this enlarged model remains in [225,240].

## 6. Price and approximation consequences

The source declares the optimistic invoice

    Ppaid={1:4754,2:824,3:1020,4:254,5:80,8:224},
    T={4:56,7:14,8:94,9:876,17:224}.

Adding only 225 rank-one jobs is the cheapest allowed tariff relaxation.
The nine concave-order hinges are all positive, with final rank-mass deficit
129. Thus every increasing power tariff r^t, 0<t<=1, fails. The checker derives
all hinges exactly. No numerical root is needed, and all omitted finite work
can still be free. These are frozen source invoice declarations, not a new
physical word census.

For approximation, use only the 208 columns whose target coefficient support
is disjoint from the complete history. The credited history/Gram theorem gives

    ||error||_op^2 >= lambda_f (1-q/208)_+,
    lambda_f=1/9 for f>=72; lambda_f=125/126 for f>=84.

At q<=36 this is at least 5375/6552 from width 84. At q<=95 it is at least
14125/26208. The predecessor's reference-tariff margin below 37 and its
all-power profitable-return cap of 95 are credited premises, not newly priced
roots here. The algebraic 224-column result does not itself prove the same
quantitative angle bound on 224 columns. No such extension is claimed.

## Open next questions

The remaining exact optimization is the rank of right multiplication by
I-C3 C1 on A^112, including the width-dependent phase cocycle, and whether
that dimension bound is attained by cyclic generators. This controls the
remaining gap between 225 and the 240-return construction. The finite native
grade census alone cannot determine that module rank.

A productive escape must change an original paid input, the observation set,
the ordinary alphabet, target credit or the supplier tariff. Bind a literal
changed caller and its complete bill before claiming that it evades this result.

## Attribution

Dugongue supplies PR4948 and its native source. Chris R / Clear1nsight supplies
PR4978, the two mandatory clarifications and the independent D-left interpreter.
Ali Romman supplies PR5526 and the earlier PR5449 history-dimension formulation.
josecarlosgonzalezroque-design supplies the PR5570 bridge audit and source-binding
handoff. Retain Cao Yifan, Cinna Davis, DLamdata, zxv and the native, controller,
Clifford and interval lineage. The rank-nullity and idempotent factorization
arguments are classical. New full-bank and coupled-module analysis: Ali Romman
with substantial OpenAI Codex assistance. Apache-2.0.
