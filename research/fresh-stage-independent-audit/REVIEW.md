# Independent audit of fresh-stage terminal separation

This review concerns Sections 2–6 of Ali Romman's PR #5408,
`research/fresh-stage-code-separation`, at source head
`256126eeb1607c0bf52996c3d90490f2b786b94a`. The audit starts from canonical
main `32890bc5de034ab8fc93ac88ead7279a6a416d04` and leaves the frozen source
unchanged. It is an independently derived mathematical and executable review
with substantial OpenAI Codex assistance, not independent human review,
proof-kernel acceptance, or a new priority claim for the underlying theorem.

**Outcome:** the fresh-stage argument proves the stated lower bound for
`J_f = Q^(-tensor f) B_f Q^(tensor f)`, and for the correspondingly conjugated
inverse. One sentence in source Section 1 incorrectly extends this bound to
the **bare** `B_f^-1`. The actual negative-bank decoder in Section 6 has the
required conjugation, so that application is unaffected by this finding.

## 1. Finding: the bare inverse has a constant ADD implementation

Source Section 1 says, “It also applies to B_f^-1”. Read literally, this is
false. The correct replacement is `Q^(-tensor f) B_f^-1 Q^(tensor f)`.

For the allowed one-stage case, put `D_f = diag_i(K_i^(tensor f))`. Then

    C_f = D_f^-1 (A tensor I) D_f,
    C_f^-1 = D_f^-1 (A^-1 tensor I) D_f,
    A^-1 = (A + 12I)/13.

The last equality follows by multiplying out `A(A+12I)=13I`. The frozen
112-by-112 matrix has zero diagonal and exactly 52 nonzero entries per row.
Thus each row of `A^-1` has 53 nonzero terms: its diagonal coefficient is
`12/13`, and its other coefficients are `+1/26` or `-1/26`.

COPY the 112 inputs into an owned normalized bank and apply `D_f`. Keep a
separate 112-field output bank and one reusable scaled-term temporary. For
each output owner, COPY and SCALE its first term into its output field, then
accumulate its other 52 terms using 52 binary scalar ADDs. Preserve the
normalized inputs until all outputs have been formed. Apply `D_f^-1` to the
outputs, COPY them to their destinations, and CLEAR the owned scratch.
The two surrounding `D_f` maps are monomial address maps. This gives the exact
bare inverse using `112*52 = 5,824` ADDs for every positive `f`, in the same
owner-field scalar/monomial word model used by the source. No Gaussian gate
is used. The number of elementary tape operations or required arithmetic
precision is not asserted to be constant.

At `k=1, f=2,925`, the erroneous extension would require
`2f-24k = 5,826` ADDs. The 5,824-ADD construction is a strict counterexample.
Its verification only needs the finite owner matrix and the signed monomial
normalizers; constructing an exponentially large tensor matrix is unnecessary.
Even without the source sparsity, dense mixing gives the width-independent
upper bound `112*111` ADDs. The source already supplies its own smaller
896-ADD code-evaluation recipe; 5,824 is an independently checked sufficient
upper bound, not a new or optimal recoding algorithm.

This finding does not provide a cheap negative-bank decoder: that decoder is
`Q^(-tensor f) B_f^-1 Q^(tensor f)`. It also does not give a favorable recursive
invoice, address the physical realization of denominator 13, or alter kappa.

## 2. Independent subgroup and path argument

Write the address space as `W = E direct-sum V_1 ... direct-sum V_k`, where
`E=<e>` is one-dimensional over `F2`. A member of `H_s` preserves `E+V_s`
and fixes every other private space pointwise. This preservation condition,
as well as the pointwise condition, matters in computing the intersection.

An element common to `H_k` and the group supported on the earlier spaces
fixes every private basis vector: the earlier group fixes `V_k`, and `H_k`
fixes the other private spaces. Its image of `e` belongs both to `E+V_k`
and to `E+V_1+...+V_(k-1)`, hence to `E`. Invertibility forces that image
to be the sole nonzero vector `e`. The intersection is therefore trivial.

From `F_k...F_1=F'_k...F'_1`, the quotient `(F'_k)^-1 F_k` lies in this
intersection. Remove the equal last factors and induct. This proves unique
ordered factorization without commuting any stages. It works in any chosen
order of distinct private blocks, but does not establish uniqueness for words
that revisit a block. Over a larger common space the intersection can be
nontrivial; over a field larger than `F2`, even its one-dimensional general
linear group need not be trivial.

For fixed initial and final owners, equality of complete binary path maps
therefore implies equality of each local factor. At the last factor, cancel
the known final-owner normalizer on the left. Distinct values of `G_i e`
imply distinct `G_i`, so the previous owner is determined. Repeat backwards.
Thus different owner paths have distinct complete binary maps. This alone
does not claim that arbitrary sums of their matrix entries cannot cancel.
The coordinate contraction below supplies the needed stronger conclusion.

## 3. Powers and the selected path

The source polynomial gives `(A-I)(A+13I)=0`. Since its roots are distinct
and nonzero, the exact projectors

    P_1=(A+13I)/14,       P_-13=(I-A)/14

give `A^a=P_1+(-13)^a P_-13` for every integer `a`, including negative ones.
Consequently `A^a=alpha_a A+(1-alpha_a)I`, with
`alpha_a=(1-(-13)^a)/14`. For a nonzero integer `a`, `(-13)^a` is never 1,
so `alpha_a` is nonzero. This also follows for `C_s,f` from its explicit
block-diagonal monomial conjugacy, with owner coefficients outside the tensor.

At every stage choose the alternating owners `j_s=s mod 2`. Its off-diagonal
coefficient is `-alpha_(a_s)/2`, so its complete coefficient is nonzero for
all allowed powers. Its first local map sends `e` to a vector other than
`e`: otherwise the distinct port images of owners 0 and 1 would coincide.
That image is nonzero, so it has a nonzero component in the first private
space. All subsequent stages fix that component. The full selected map
therefore moves `e`, for both parities of `k`. Tiny nonzero coefficients cause
no issue in this exact argument; no finite-precision stability is inferred.

## 4. Central conjugation and row support

Let `M|x>=s(x)|Gx>` with `s(x)` in `{+1,-1}`. Set
`a=(1+i)/2`, `b=(1-i)/2`; then `Q=aI+bT_e` and `Q^-1=bI+aT_e`.
Using `ab=1/2`, `b^2=-i/2`, and `a^2=i/2` gives

    Q^-1 M Q |x> = (1/2)[s(x)|Gx> - i s(x+e)|Gx+Ge>
                       + i s(x)|Gx+e> + s(x+e)|Gx+Ge+e>].

Invertibility and `Ge!=e` imply that `Ge` and `e` are linearly independent
over `F2`. All four destinations are distinct, with coefficient modulus
`1/2`. The adjoint is `Q^-1 M^-1 Q`, and `G^-1e!=e`, so every row also has
exactly four entries. In particular its row absolute sum is 2 and row
Euclidean norm is 1. The support of each tensor-power row is exactly `4^f`.
These assertions apply to each selected monomial conjugate, not to the sum
over owner paths.

For a fixed owner block, the tensor identity that is actually available is

    J_f = sum_path c_path (Q^-1 M_path Q)^(tensor f).

It follows by composing tensor powers along each path before summing paths.
Replacing this expression by the tensor power of a width-one owner sum
would introduce different cross terms and is not used.

## 5. Marker contraction and the ADD bound

Every path map is orthogonal over `F2`. Its images of the `8k` private basis
vectors are orthonormal, so their span is nondegenerate of codimension one.
Its orthogonal complement has exactly one nonzero vector, namely the image
of `e`. Thus agreement on those private basis vectors determines the entire
map. This argument explicitly handles the characteristic-two setting; it
does not assume that an arbitrary codimension-one span is nondegenerate.

Choose the selected map `G_*`. For each private basis vector `x_l`, set
`y_l=G_*x_l` and `ell_l(N)=(Q N Q^-1)[y_l,x_l]`. On a path term this is
the signed monomial entry at `(y_l,x_l)`, hence zero or `+1/-1`. All selected
entries are nonzero; every other path has at least one zero by the preceding
map determination and path uniqueness. Contracting `m=8k` tensor factors
therefore leaves exactly

    c_* eta (Q^-1 M_* Q)^(tensor (f-m)),   eta in {+1,-1}.

Each marker functional uses at most two output indices and two input indices
because each row and column of `Q` and `Q^-1` has support two. Fix an output
row on the remaining tensor factors. The contraction draws on at most `2^m`
original rows. If each original row has support at most `S`, projecting away
its marker input coordinates leaves at most `S` possible remaining input
coordinates. The union over the selected rows has at most `2^m S` elements;
the additional summation over marker input choices does not introduce an
extra factor `2^m`. Cancellation can only reduce this union.

The isolated row has `4^(f-m)` entries. Therefore
`S >= 2^(2f-3m)` for `f>=m`. Initially each independent input or clean-workspace
row has support at most one. SCALE, monomial maps, COPY and CLEAR preserve
this maximum, and one binary ADD increases it by at most a factor two.
After `g` ADDs, `S<=2^g`, even with arbitrary owner mixing and workspace.
This gives `g>=max(0,2f-24k)`; when `f<m`, its nonnegative version is trivial.

The same proof permits any shorter marker list isolating the path and gives
`g>=max(0,2f-3m)`. The contraction is a mathematical certificate, not a free
instruction. Independent inputs, a linear input-independent schedule, binary
ADDs, and initially uncorrelated workspace are essential interface premises.
An unpriced correlated history or a paid nonmonomial operation is not covered.
For the constant-in-width exclusion, `k` is fixed independently of `f`.

## 6. Binding the sixteen saved negative banks

The frozen `GAUGE.json` lists negative roles 0 through 15, each with operator
`Q^-1 B_i D_i`. Their left-to-right code words contain distinct stages and
only exponents `+1/-1`; the lengths and supplied marker sizes are:

| Negative roles | Stage count | Marker count | ADD offset |
| --- | ---: | ---: | ---: |
| 0, 8 | 2 | 1 | 3 |
| 1, 9 | 3 | 1 | 3 |
| 2, 10 | 4 | 1 | 3 |
| 3, 11 | 5 | 2 | 6 |
| 4, 12 | 6 | 1 | 3 |
| 5, 13 | 7 | 2 | 6 |
| 6, 14 | 8 | 1 | 3 |
| 7 | 9 | 2 | 6 |
| 15 | 18 | 2 | 6 |

The finite-state certificate has a sufficient state: current owner and one
shared bit per marker. Before a stage, that stage's private input bits have
never been touched. After it, its prescribed private output bits will never
be touched again. No other historical data can affect the next local map.
Counting paths with nonnegative integer multiplicities thus loses no candidate.
Allowing every nonzero `A` edge and every diagonal is a superset of the support
of every `A^a`. If exactly one path survives these constraints, the alternating
path's nonzero coefficient proves isolation for all the allowed powers.
The independent checker in this package uses the local relation
`G_j(input)=G_i(output)` and a complete layered relation count; it does not
import the predecessor evaluator. Finite counts corroborate this invariant,
while the all-length subgroup and contraction arguments remain written proofs.

For a word printed left to right, inversion reverses its algebraic factors
and negates their powers. Its execution order is therefore the printed order
with negated powers. Renaming the fresh private blocks in that order fixes
`e` and commutes with `Q`; it preserves the marker and support arguments.
This binds the length-specific certificates to the actual bank words, not
just to abstract positive powers of a repeated stage.

If the required job is `Q^-1 D_i`, the unique linear postdecoder on an
arbitrary emitted bank is

    (Q^-1 D_i)(Q^-1 B_i D_i)^-1 = Q^-1 B_i^-1 Q.

Invertibility of `D_i` justifies the cancellation. Independent additional
inputs cannot alter this restriction of an exact linear decoder; correlated
retained histories can. Thus each of the sixteen saved negative-bank
interfaces has the uniform bound `max(0,2f-6)`, with the stronger offsets
listed above. These lower bounds cannot be added across banks.

The endpoint identity, fresh-stage embeddings, and original input interface
are inherited from the saved PR4933 caller. This review checks their supplied
data and their mathematical implication, not the complete native producer,
supplier, compiler, outer construction, or its arithmetic and movement bill.
There is no other finding in Sections 2–6 under these explicit premises.

## Attribution and limits

Ali Romman / PR5408 owns the reviewed fresh-stage separation and short-marker
result. Dillon / PR4933 supplied the normalizers, one-stage support argument
and typed caller; Cinna Davis / PR5065 supplied the two-stage predecessor;
Dugongue / PR4929 supplied the center-free code. The retained Cao Yifan /
intqwq, Cinna Davis / 1337isnot1337, zxv, Jacob Alan Sussman, Ryanson Jonathan,
and native/controller contributors retain their source credit and notices.
This package contributes the independent audit and the explicit bare-inverse
scope counterexample. It claims no original discovery of the inherited
polynomial, four-point identity, scalar code, or support-growth principle.
It supplies no new frontier value, full cost admission, human approval, or
formal proof acceptance.
