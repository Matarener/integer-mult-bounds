# Finite geometric inputs and the inherited strict dimension screen

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The support-capacity proof follows PR3166. The prefix counting relaxation is
DreamingOfClouds' Lemma S in PR2962; its strict dimension-24 consequence is
used here as an inherited one-sided input, not claimed as new E8 geometry.

## 1. Root model, scalar ranks and binary labels

Let E be the complete 120-line standard E8 inventory, with norm-two rational
representatives r_x. Let C={E(h):h in K^8}, where E(h)(x)=(r_x,h), and let
u_x be the fixed nonzero labels in the nine-dimensional nondegenerate
binary pairing space. The scalar field K has characteristic zero in the
arguments concerning root-subsystem cardinalities and dimensions below.

The exact model checks identify every standard root line, all integer Gram
products, and the dense identity

    beta(u_x,u_y)=1 iff x=y or (r_x,r_y)=0.

The scalar code and the binary label space are different objects. Write
w(q)=rank_F2{u_x:q(x)!=0}. Its possible values on nonzero words are the
integers 1 through 9, independently of the scalar field.

For any rational root subset, its matrix rank is unchanged between Q and
any characteristic-zero K: a nonzero rational minor stays nonzero, and
every vanishing rational minor stays zero. To bound a selected root set
of rank r, let T_Q be its rational span. Choose a rational functional
vanishing on T_Q and nonzero on every root outside T_Q; finitely many
proper hyperplanes can be avoided. Its vanishing root set is exactly the
roots in T_Q. The stabilizer of that real point in the finite Weyl group
is parabolic, with precisely those roots. Thus the root set in T_Q is
Weyl-conjugate to a standard parabolic subsystem of rank r. This proves
that a maximum over all simple-root subsets bounds every selected root
set, rather than only standard-position subspaces. The capacities are

| root rank r | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| maximum number N_r of root lines | 0 | 1 | 3 | 6 | 12 | 20 | 36 | 63 | 120 |

The finite parabolic inventory checks all 256 subsets of the pinned simple
basis. Every root has integral simple coordinates of one sign, and each
subset's span membership is exact. The table records maxima by the number
of independent selected simple roots; it is not a table of floating
dimensions. The proper rank-seven cases above 42 roots consist only of
E7 with 63 roots, whose perpendicular is a root line.

In particular every nonzero E(h) has at least 57 nonzero coordinates. Its
zero root rows have scalar rank at most seven, hence number at most 63.
If h is not a root normal, there are at most 42 zero root rows: an E7 zero
set would force h onto its one-dimensional root perpendicular. These
consequences remain valid for arbitrary characteristic-zero K. Here is the
support-pattern transfer used when a normal is not rational. Let T_Q be
the rational kernel of all rows vanishing on h. Its extension to K
contains h. Every designated nonzero root row is a nonzero functional on
T_Q: if it vanished on T_Q, it would also vanish on T_Q tensor K and hence
on h. Avoiding their finitely many proper rational hyperplanes produces a
rational normal with exactly the same zero/nonzero root pattern. If this
pattern contains an E7 subsystem, its rank seven forces the original
K-normal into the same one-dimensional K-root perpendicular. Thus the
root versus nonroot distinction used above also transfers. No ordering
or positive-valued norm on K is assumed.

## 2. Fourier proof of the binary support capacities

The root labels are the odd-weight vectors u in F2^9 for which
binom(weight(u),2) is odd. Equivalently, write

    u(x)=(x_1,...,x_8,1+sum_i x_i), x in V=F2^8,
    Q(x)=sum_{i<j} x_i*x_j.

Then the root labels are exactly u(x) with Q(x)=1. This description gives
the 84 weight-three and 36 weight-seven labels. The polar form

    B(x,y)=Q(x+y)+Q(x)+Q(y)

has matrix I+J, where J is the all-ones 8 by 8 matrix. It is nondegenerate:
(I+J)^2=I over F2 because J^2=8J=0. This B is the polar form on V used in
Fourier summation; it is not being identified without a coordinate change
with the original nine-dimensional pairing beta.

The exact 256-value quadratic inventory has 120 ones and 136 zeros, so

    G(Q)=sum_{x in V}(-1)^Q(x)=16.

Completing the square gives the full Fourier identity, for every y in V,

    sum_{x in V}(-1)^(Q(x)+B(x,y)) = 16*(-1)^Q(y).          (2.1)

Indeed Q(x)+B(x,y)=Q(x+y)+Q(y), and translation permutes V.

Take a binary subspace T of the label space with dimension w, where
1<=w<=8. If it has no odd-weight vector, it contains no root labels.
Otherwise its odd slice is an affine (w-1)-flat. Under the affine map u(x)
this slice corresponds to A=x_0+U in V, with dim U=w-1. Put

    D=U^perp_B, n=dim D=9-w.

The indicator of A and (2.1) yield

    S_A:=sum_{x in A}(-1)^Q(x)
        =16/2^n * sum_{y in D}(-1)^(Q(y)+B(x_0,y)).        (2.2)

The restricted function

    f(y)=Q(y)+B(x_0,y), y in D,

is quadratic and, crucially, has f(0)=0. There is no additional constant
sign in (2.2).

Here is the precise Gauss-sum bound needed. If a zero-constant quadratic
function f on an n-dimensional binary space has polar rank r, then r is
even. If f is nonzero on its polar radical, translation by a radical
element with f-value one negates its Gauss sum, so that sum is zero.
Otherwise f descends to a nondegenerate quadratic function on a space of
dimension r. Its Gauss sum has square 2^r, and pulling back through the
radical gives

    G(f)=plus/minus 2^(n-r/2).

For completeness, the square identity follows by putting y=x+t in the
double sum G(f)^2: the inner linear-character sum over x vanishes unless
t is in the polar radical. In the nondegenerate quotient only t=0
survives, giving 2^r.

If r=0, the zero-constant f is linear. It has Gauss sum 2^n when f=0 and
zero otherwise; a negative sum is impossible. If r>=2, then

    G(f)>=-2^(n-1).                                      (2.3)

Thus for w=5,6,7, equation (2.2) gives S_A>=-8. The number of root labels
in T is (|A|-S_A)/2, at most

    (2^(w-1)+8)/2 = 2^(w-2)+4,

namely 12, 20 and 36. For w<=4, the trivial |A|=2^(w-1) bound gives
1, 2, 4 and 8. For w=8, the dual dimension n is one. Its polar rank is
zero, so its zero-constant quadratic function has a nonnegative Gauss
sum. Hence S_A>=0 and at most 2^7/2=64 labels are roots.

We obtain the support bounds

| binary rank w | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| maximum support bound g(w) | 0 | 1 | 2 | 4 | 8 | 12 | 20 | 36 | 64 | 120 |

Only upper bounds are needed in the dimension proof. Explicit affine-flat
attainers may additionally certify their sharpness; searching for such
attainers does not replace this uniform Fourier argument. Omitting the
condition f(0)=0 would invalidate the special w=8 conclusion, since a
constant-one function on a one-dimensional space has negative Gauss sum.

The same quadratic description gives the full binary character spectrum.
The character omega=(1,...,1) sees every root label, so |O_omega|=120.
Every other nonzero character induces a nonconstant affine linear form on
V; (2.1) makes its root cut size 60+4 or 60-4. Complementary characters
z and z+omega exchange these sizes. Thus the 511 nonzero characters have
sizes 56, 64 and 120 with multiplicities 255, 255 and 1 respectively.

## 3. Full codewords and the root remainder input

The retained PR3755 exact rank witnesses certify that each O_z spans all
eight scalar root dimensions. If a nonzero codeword E(h) had w(E(h))<=8,
a nonzero binary annihilator z would force h to annihilate all roots in
O_z, contradiction. Thus every nonzero full-E8 codeword has binary weight
nine. This fact must not be substituted with a punctured P112 statement.

For a root a, Off(r_a) consists of a and its 56 nonself neighbors. The
neighbor labels lie in u_a^perp, while u_a itself does not, since
beta(u_a,u_a)=1. The neighbor labels span that full dimension-eight
hyperplane: adding u_a gives the weight-nine support of E(r_a).

The finite root-character comparison checks all 120*511 pairs. The
matching character u_a intersects Off(r_a) exactly at a. Every other
character intersects the nonself remainder in at least 24 points. For
each root, the nonself remainder cut-size distribution over nonzero
characters is

    0:1, 24:126, 28:256, 32:126, 56:2.

The sole zero cut is the character u_a. This is the inherited full-E8
remainder input used by the eligible-root classification; it is separate
from the new relative nonroot 27-cut certificate.

## 4. Necessary prefix inequalities for every scalar basis

Let S be any K-subspace of K^E containing C. Put n=dim S and choose an
arbitrary scalar basis q_1,...,q_n, sorted so its weights satisfy

    1<=w_1<=...<=w_n<=9.

For a prefix J={1,...,n-r}, let X_J be the union of those basis supports.
At a coordinate x outside X_J, evaluation on every codeword uses only
the r remaining scalar basis coefficients. Hence the root row
functional h |-> (r_x,h) lies in the span of r scalar functionals. The
root rows outside X_J therefore have rank at most r. For r=0,...,7 the
root capacities in section 1 imply

    |X_J|>=120-N_r.

Since |X_J|<=sum_{i=1}^{n-r}|supp q_i|<=sum_{i=1}^{n-r}g(w_i), every
basis obeys

    sum_{i=1}^{n-r}g(w_i)>=120-N_r, r=0,...,7.              (4.1)

The eight right sides, starting with the prefix that leaves seven
entries, are 57, 84, 100, 108, 114, 117, 119 and 120. Prefixes leaving
at least eight entries have no stronger constraint from ambient rank.

This is a necessary cardinality relaxation. It forgets actual root
positions, overlaps between supports and scalar coefficient compatibility.
A feasible weight multiset need not be a realizable basis. Conversely,
infeasibility of a budget under (4.1) is a valid lower bound for every
actual basis, including bases with arbitrary characteristic-zero entries.

## 5. Exact finite dynamic-programming coverage

For each fixed n, enumerate all nondecreasing integer weight sequences
in 1,...,9 satisfying (4.1). Both implementations use the exact state

    (prefix length, last weight, min(120,sum of prefix capacities)).

The prefix sum can be capped at 120 because every required right side
is at most 120. Future constraints depend only on this state and the
remaining weights; no omitted geometric information is used by the
relaxation.

The primary implementation runs forward under bill budget 72. At a
fixed prefix length it retains the smallest paid bill for each
(last weight,capped capacity) pair. This is safe dominance: the cheaper
path can take every suffix available to the more expensive path with the
same state. Before adding weight w it also uses the necessary lower
bound that all future weights are at least w. It rejects a completed
prefix precisely when that prefix fails its required inequality.

The separate implementation runs backward, minimizing the full bill
from every state, and reconstructs an attaining relaxed profile. Its
induction is direct: try every allowed next weight, reject exactly the
failed prefix inequalities, and take the minimum over the remaining
suffixes. Neither checker imports a predecessor PASS receipt.

The finite strictness obligation comprises all 49 dimensions

    n=24,25,...,72.

Both implementations reject every sequence of bill at most 72 under
(4.1) for each of these dimensions. Their integrated replay checks all
49 dimensions and the n=23 boundary controls; the universal range is
not inferred from a sample.
For n=73,...,120 no finite search is needed: a basis has n nonzero
members, each of positive integer weight, so its bill is at least n>=73.
Together these facts give the inherited strict screen

    S contains C and dim S>=24 => c(S)>=73.                (5.1)

As boundary controls, the relaxation at n=23 has minimum 72, with weight
multiset

    1^13,5,6^9,

and has no sequence of bill at most 71. At n=24 its relaxed minimum is 73,
with multiset 1^14,5,6^9. These are controls on the integer relaxation,
not asserted actual E8 bases. In particular the n=23 profile explains
why this counting relaxation alone does not prove strict 73 there.

## 6. Source and scope

PR2962, exact head f6e68c9838e21b263223ae61273e381d2c0b92c7,
research/decoder-certificate-ceilings/README.md section 3 and
checks/lemmaS_dp.py, supplies the one-sided Rado/prefix counting method.
Its advertised Lemma S states c(S)>=72 for dim S>=23. The strict
dimension 24 consequence above is obtained from the same necessary
integer constraints and is credited accordingly. The new coupled proof
uses its one-unit slack; it does not rebrand the underlying one-sided
counting argument as new.

PR3166, exact head 7c2a62363ad4945e8803fedea6ead78e1ad412b2,
research/e8-d0-root-swaps/PROOF.md section 4, supplies the Fourier support
argument, parabolic scalar bounds and full remainder context. PR3755
supplies the explicitly bound full-root model and rank witnesses. Their
finite inputs remain distinguished from the later coupled scalar-basis
and marked-coefficient implications.

No positive-characteristic extension of the scalar root-capacity table,
general L120 theorem, physical supplier, shared COPY bill or new
multiplication exponent follows from these finite inputs alone.
