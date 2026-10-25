# Permutation-only pivot continuations: all-q support and moment gate

This note concerns only identity versus SWAP of the two actual carriers
before each nonfinal retained J continuation. The frozen phase-correct J,
whole-plane source swaps P_s, original core K, scalar handoff and target
`F_k J` remain fixed. Each local swap has a literal scalar/bank-word
implementation; the complete wider affine public-reader trace is a
separate caller obligation. No independently usable helper stock is
assigned to an unseparated H block.

Use `q>=2`, `k=2q+1`, `n=2q+2`, `m=4q+4`. The base carrier words are

    u1=B3 J * K_row2 = P3 N0 * K_row2,
    v1=K_row1.

At pair r, form `U=B_(2r) u` and `V=B_(2r+1) J v`. A nonfinal identity
continuation gives `(u',v')=(U,-V)` homogeneously; a swap gives
`(u',v')=(V,-U)`. The final pair keeps `(U,V)`. All affine public-reader
terms remain part of the actual caller and are not declared zero.

Track which current carrier descends from each row of K. Let d0 be the
number of odd factors `D_s=B_sJ=P_sN0` received by the path starting at
K row1, and d1 the corresponding number for the path starting at K row2.
Then

    d0+d1=q-1, d0>=1.

The first odd D5 always acts on the K-row1 path; the first even B4 acts
on the K-row2 path. This retains the base `B3J=P3N0`.

## Exact inverse coefficients

Let W0,W1 be the signed full carrier words on K rows1,2. In their current
physical bank order, the required original-t inverse coefficients are

    C0=F J Q1^-1 B2^-1 W0^-1 F^-1,
    C1=F J Q1^-1(I-B2^-1) W1^-1 F^-1,
    Q1=J^-1 B1J.

C0 is a single Clifford. C1 is the difference of two distinct Cliffords
C1a and C1b, with their complete literal phases. The public-reader L
block does not change these pivot coefficients of the joint inverse.

For each p or q half and one chunk bit, put

    Gamma_A=e0e1^T+e1e0^T+e1e1^T, A=N0^-1J.

Every successive left factor `P_s A` adds a star edge from plane1 to the
new even plane s and adds one diagonal at plane1. Every odd `P_s N0`
adds the diagonal of its new odd plane. The current common0 row is zero
after each source post, so later fresh swaps leave all preceding support
unchanged. W1 also has its initial diagonal at fresh3.

Consequently a path has left shear equal to the disjoint odd diagonals
plus a plane1 star on its selected even planes, with its plane1 diagonal
equal to the parity of the number of those even factors. W1 includes
E3; W0 does not. The associated permutation is the cycle through the
initial fresh3 (for W1) and then the monotonically increasing selected
fresh labels.

Moving that cycle through each displayed inverse coefficient simply
relabels selected labels by their predecessors. Odd predecessor
diagonals, star leaves, and the final selected label are all distinct.
The fixed left core words have binary normal forms

    J Q1^-1 B2^-1 : shear H01=e0e1^T+e1e0^T, permutation P1P2,
    J Q1^-1      : shear E0,                         permutation P1.

After the F conjugation, symmetric row/column elimination gives this
rank table on one half and one bit:

| Coefficient | Base/star blocks | Odd diagonals | Final diagonal | Rank |
| --- | --- | --- | --- | --- |
| C0 | invertible `(0,1)` block, rank2 | d0 | 1 | d0+3 |
| C1a | nonempty star rank2 and disjoint plane1 rank1 | d1 | 1 | d1+4 |
| C1b | invertible `(0,1)` block rank2 and disjoint plane2 rank1 | d1 | 1 | d1+4 |

In C0/C1b the base block is `[[1+epsilon,1],[1,0]]`, whose inverse has
top-left entry0. The star leaves therefore have zero Schur complement
and add no rank. In C1a the star is nonempty because the K-row2 path
received B4 before the first optional swap; its rank is exactly2.
All odd and final diagonals in the table are disjoint from these blocks.
This proves, for every q and f,

    arity(C0)=(2d0+6)f,
    arity(C1a)=arity(C1b)=(2d1+8)f.                  (1)

The finite producer independently checks actual Gaussian Clifford B
ranks for all511 schedules at q2..10. It saves full signed homogeneous
words, both physical inverse coefficients, their all-f tensor units and
their actual native output-image bases for optimal q6..10 schedules.
Those image overlaps are descriptive; they do not prove a shared-query
invoice. Dropping the base B3J changes the checked inverse operator.

## The difference C1 cannot hide its support exponent

The two C1 rays are distinct, and their quotient is unitarily similar
to B2^-1. Its normalized one-coordinate trace has modulus1/16; the
producer checks the exact64-address active three-plane fixture. Tensor
products have overlap modulus `16^-f`, with all once-per-field phases
retained. Both C1 terms have equal row amplitude scale from (1).

If `r1=2d1+8` and `D=2^(mf)`, then

    ||C1||_F^2 >= 2D(1-16^-f) >= (15/8)D,
    maximum_entry_magnitude(C1)^2 <= 4*2^(-r1f).

Hence C1 has at least `(15/32)D*2^(r1f)` nonzero entries in total, and
some row has at least `(15/32)2^(r1f)` nonzeros. This is a max-row/global
claim, not an every-row claim. C0 has exactly `2^((2d0+6)f)` entries in
every row. Thus a complete cleanup at this same cut requires

    total native arity + binary ADD count
        >= max(2d0+6,2d1+8)f-O(1).                  (2)

The finite sum was not assigned a native rank from its constituents.
Its support lower bound is a separate norm/overlap proof.

## Optimal routing support bound

Every integer d0 in `[1,q-1]` is attained by a single swap after the
path has received d0 odd factors; keep identity at the other cuts.
Balancing the two quantities in (2), with d1=q-1-d0, gives

    r*(q)=min_schedule max(2d0+6,2d1+8)
         =2ceil(q/2)+6.                             (3)

Their sum is always `2q+12`. That sum is **not** a lower bound on joint
native cost, since one paid query can affect more than one output.
Equation (3) shows at least one inverse coefficient has support exponent
linear in q; both cannot be sublinear. At q8, r*=14 first becomes less
than the prefix's native deficit16, but this alone is not a favorable
moment or a completed native tail.

## Exact all-q optimistic moment exclusion

This paragraph additionally assumes the parent's source-bound full-scan
transfer premises and the equal-volume, separately charged prefix sites
in `COST-SCOPE.md`. The prefix has `h=n^2-q` H2 calls. Its normalized
moment is `h*(1/n)^(1-b)`. By (2), admissible cleanup native mass is at
least r*. For `0<p=1-b<1`, subadditivity of the positive p power gives

    sum_i(r_i/m)^p >= (sum_i r_i/m)^p >= (r*/m)^p.

Even a single rank-r* cleanup query is therefore an optimistic lower
bound on the cleanup moment. It need not be a realizable two-carrier
word. We prove that the favorable envelope

    h*n^(b-1)+(r*/(2n))^(1-b)

is strictly greater than the available stock n at `b0=1/600`, for every
integer q>=2.

Use `exp(x)>=1+x` and `x^(1-b)>=x` for `0<x<1`. The moment minus n is
at least

    [-q+r*/2+(h/600)ln n]/n.                         (4)

For q2..7, r*>=2q, and the logarithmic term is positive. For q8..10,
`ln n>=ln16>8/3`; the exact integer comparisons are

    q8:  2528>1800,
    q9:  3128>1800,
    q10: 3792>3600.

They are precisely `8h>1800(q-ceil(q/2)-3)` and make (4) positive.
For q>=11, `ln n>=ln24>3` and `r*/2>=q/2+3`, so (4) is greater than

    (12q^2-279q+1812)/(600n),
    12q^2-279q+1812=12(q-93/8)^2+3045/16>0.

The logarithmic bounds are rationally certified by the positive series
`ln x=2 sum_j z^(2j+1)/(2j+1)`, `z=(x-1)/(x+1)`: it gives
`ln2>2/3`, `ln3>1`, and therefore `ln24=3ln2+ln3>3`. No floating-point
root or finite tail cutoff is part of this all-q proof.

The envelope increases with b, so the required strict component moment
fails for every `b>=1/600` in this architecture. This is a component-b
ceiling. The retained batched-complex layer requires `lambda'>sigma=1-b`,
and the retained assembly has `kappa<epsilon(1-lambda')`, `epsilon<1`,
so `kappa<b` in that specified transfer. Another outer transfer needs
its own separately proved relation before interpreting the component
ceiling as a kappa exclusion.

The scalar/base/source architecture, declared cut, equal volumes and
literal full-bank scan premises are essential. Cross-cut query fusion,
partial/local scans, genuinely operator-valued coupled bridges, changed
core/delivery maps and changed terminal owner/input/target contracts
remain outside this result. It is not a global multiplication lower
bound or a new kappa.
