# Sharp borrowed-space tariff for square-zero recoding

Let N be a nonzero square-zero n by n matrix over a field, with rank r.
To implement `diag(I+N,I_q)` using q arbitrary dirty borrowed coordinates,
the exact minimum is

    2 ceil(r/q) + 2 cross-bank shears.

Both directions require at least `ceil(r/q)+1` shears. One word attains both
bounds. It therefore minimizes every positive weighted sum of gather and
scatter counts. It preserves every original input and restores the arbitrary
borrowed baseline. No other storage or within-bank operation is allowed.
The identity update takes zero shears. With clean borrowed coordinates, the
corresponding exact count is `2 ceil(r/q)+1`.

The result also holds for finite simultaneous-translation kernels over an
elementary binary group in characteristic different from two, with r replaced
by the maximum rank over its characters. This gives an exact whole-field
count at every positive tensor width within that kernel alphabet. A compiler
builds an attaining coefficient list without a width-dependent oracle.

This is a scoped construction and lower bound. It supplies a precise storage
and ordinary-operation tradeoff for reader recoding. It does not change the
complete kappa calculation, reduce the source section's required centre bank,
or give a native producer/consumer with an admitted complete bill.

## Sources, scope and credit

Main is `6cf7a683f447b9f1e2333791907fd92be5009a63`, priority revision 7.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19186337)
follows refreshed main, priorities, the complete open-PR and Discussion cache,
and targeted searches of every tracked main research README. The older
mutable-source connector and fixed receiver-window alphabets are different.
No active conflicting claim was found. This is not a global novelty claim.

David Ganz (@Dugongue) supplies the direct application in
[PR #5634](https://github.com/CrocSwap/integer-mult-bounds/pull/5634), exact head
`0e263b0932a4a6936940d9bb8af48da269091d37`. Its
[reader proof](https://github.com/CrocSwap/integer-mult-bounds/blob/0e263b0932a4a6936940d9bb8af48da269091d37/research/gaussian-reader-recoding/reader-kernel.md)
and
[provider interface](https://github.com/CrocSwap/integer-mult-bounds/blob/0e263b0932a4a6936940d9bb8af48da269091d37/research/gaussian-reader-recoding/coded-provider.md)
are retained byte for byte in `inputs/`, including their source notices.
`SOURCE-CONTEXT.json` records the commit, path, Git blob and SHA256; the verifier
authenticates both files. No predecessor executable or unmerged Git object is
needed to replay this package. The predecessor supplies the four-shear identity,
actual rank-30 reader substitution, section conjugacy and finite-character
kernel method. Those are credited premises, not new results here.

The new work supplies the sharp all-q tariff, the grouped attaining word,
the lower bound over all words in the stated alphabet, the character-rank
extension, a rational coefficient compiler, and checks at every scalar ADD
boundary. Preserve the native, centre-code and campaign lineage in both frozen
sources. New work is by Ali Romman (@aliromman), with substantial OpenAI Codex
assistance. Apache-2.0. No independent human or proof-kernel review is claimed.

## Exact alphabet and lower bound

Write the current data and borrowed states as linear functions of the original
independent inputs x,z. The only allowed gates are

    G(A): z <- z + A x,       A has size q by n,
    S(B): x <- x + B z,       B has size n by q.

Here x and z on the right mean their current values. Coefficients are fixed
field elements. Gates can occur in any order, with arbitrary feedback; their
matrices need not come from a chosen factorization. There is no operation on
two data coordinates, on two borrowed coordinates, or on a third bank. A
within-data gate that directly applies I+N would change this alphabet.

In fact the lower bound applies to any endpoint `diag(T,I_q)`. Let k be the
number of gathers. Let C be the q by n block that maps the original data into
the current borrowed state. Initially and finally C=0. Only gathers change C.
Call their successive increments H1,...,Hk. Each has q rows and

    H1 + ... + Hk = 0.

Every intermediate C lies in the row span of H1,...,H_(k-1), of dimension at
most (k-1)q. Only scatters change the original-data block X of the current data;
each change is B C. Thus every row of T-I lies in this same span, and

    rank(T-I) <= (k-1)q.

Transpose the complete matrix product and reverse its factor order. The result
is a legal word for `diag(T^T,I_q)` in which gathers and scatters exchange
roles. The same argument gives `rank(T-I) <= (l-1)q` for l scatters. Thus
both k and l are at least `ceil(r/q)+1`. This argument uses the restoration of
arbitrary borrowed inputs and checks the full endpoint, not only clean columns.

For clean borrowed coordinates, C still starts and ends at zero, so the gather
bound remains. Each scatter changes X by a matrix of rank at most q, giving
l>=ceil(r/q). The transpose argument cannot be used: the dirty-input columns
are not constrained. This gives the different clean count stated above.

## Attaining word for every square-zero matrix

Take a rank factorization N=VL, where V has r independent columns and L has
r independent rows. Since N squared is zero, `V L V L=0`. Injectivity of V
and surjectivity of L give `LV=0`. Split V into column blocks V_i and L into
matching row blocks L_i of width q, padding the last block with zeros. Let
`s=ceil(r/q)`. Then

    N=sum_i V_i L_i,        L_i V_j=0 for all i,j.

Execute the following chronological word:

```text
G(L_1), S(V_1),
G(L_2-L_1), S(V_2),
...
G(L_s-L_(s-1)), S(V_s),
G(-L_s), S(-sum_i V_i).
```

After the ith scatter its exact state is

    z = z0 + L_i x0,
    x = (I+sum_(j<=i) V_j L_j)x0 + (sum_(j<=i) V_j)z0.

Every L_i is unchanged by a data update whose image lies in the columns of V.
Induction therefore proves the formula even though the gathers read updated
data. The last gather restores z0; the last scatter removes its contribution
from x. This proves the required full endpoint in 2s+2 shears and attains both
lower bounds. If z0=0, omit the last scatter to obtain the sharp clean word.
Changing every V_i sign constructs the inverse update.

`factor_square_zero` obtains V,L by exact rational elimination.
`compile_factors` also accepts a supplied factorization. It checks LV=0 and
uses only additions and sign changes in the schedule. If the supplied inner
dimension R exceeds rank(N), the same word has 2 ceil(R/q)+2 shears but is only
an upper bound. Optimality requires a rank factorization. The compiler is
polynomial in its explicit matrix dimensions and rational bit data; no search
over words or bases is used for construction.

## Coefficient cost and precision inside the shears

Each rectangular shear expands into one instruction `dst += c*src` per nonzero
coefficient. Its source bank stays unchanged throughout that shear. These are
coefficient ADD instructions, not a claim that an arbitrary rational multiply
or division costs one physical machine operation.

The grouped word has no more coefficient instructions than separate four-shear
commutators on the same blocks. For gathers,

    nnz(L1)+sum_(i=2)^s nnz(L_i-L_(i-1))+nnz(L_s)
      <= 2 sum_i nnz(L_i).

For scatters, `sum_i nnz(V_i)+nnz(sum_i V_i) <= 2 sum_i nnz(V_i)`.
The total is therefore at most twice the number of nonzero coefficients in V
and L. The separate construction uses 4s shears and this latter coefficient
count; the grouped construction uses only 2s+2 shears. This comparison fixes
the same supplied factorization and coefficient representation. It is not a
global minimum of scalar arithmetic or a comparison with a new factorization.

There is also a width-independent bound at every coefficient ADD boundary.
Put `j_i=||V_i||`, `d_i=||L_i||`, `J=sum j_i`, `D=max d_i`, using maximum
absolute row sum. Define

    M=max(1+2D,1+J),
    B=max(1+sum j_i d_i+J,1+D),
    C=max(1+J(2D+1),1+D).

Every scalar-prefix operator has norm at most BM. Every scalar-suffix operator
has norm at most `(1+JD)CM`. To prove this, each complete boundary has the form

    P = [[I+N_j, S_j], [L_i,I]],
    P^-1 = [[I-N_j+S_j L_i,-S_j], [-L_i,I]],

with `N_j=sum_(k<=j) V_k L_k` and `S_j=sum_(k<=j) V_k`. The formulas include
the gather boundaries, where L_i can also be zero. They follow from all
cross-products L_i V_j being zero. After the final scatter the endpoint and
its inverse have norms at most 1+sum j_i d_i, which also fit B and C. All complete
boundary norms are therefore at most B and C. A partial
coefficient expansion of one gather has norm and inverse norm at most 1+2D;
a partial scatter has the corresponding bound 1+J. This gives the prefix
and inverse-prefix bounds. Multiply the latter by the final endpoint norm,
at most 1+JD, to get the suffix bound. Empty updates have bound one.

Thus m additive rounding errors, each of maximum coordinate magnitude epsilon,
produce at most `m(1+JD)CM epsilon` final error under this coefficient-ADD model.
Actual coefficient approximation adds its input-range error. The internals of
fixed-odd arithmetic, shifts, physical routes and recursive instructions need
their own bounds. This theorem does not supply those internals or reuse an old
finite compiler reserve after changing its word.

## Exact whole-field tariff for translation kernels

Let H be an elementary binary group and let K have characteristic different
from two. Work over the commutative algebra K[H]. A matrix kernel is a fixed
coefficient list `A=sum_(v in H) A_v X_v`. In the width-f action, X_v translates
all columns simultaneously; the coefficients A_v occur outside the tensor
power. Multiplication is finite convolution, independent of f.

Suppose N squared is zero in this algebra. For each character chi:H->{1,-1},
let `N(chi)=sum chi(v)N_v` and set `r=max_chi rank N(chi)`. Then, for r>0,
the exact minimum within the translation-kernel shear alphabet is again

    2 ceil(r/q)+2.

For the lower bound, evaluate any candidate word at a character that attains
r and apply the field theorem. For construction, take rank factorizations
`N(chi)=V(chi)L(chi)` with `L(chi)V(chi)=0`. Pad them all to inner dimension r.
Apply inverse character transforms separately to V and L:

    V_v=|H|^-1 sum_chi chi(v)V(chi),
    L_v=|H|^-1 sum_chi chi(v)L(chi).

Character orthogonality gives VL=N and LV=0 in K[H]. The grouped word therefore
works over that algebra and attains the lower bound. `compile_kernel` implements
this construction over the rationals. It returns the character ranks and the
full finite coefficient word. Rational rank factorizations can introduce new
odd denominators; they are not automatically admitted by a source grid.

For simultaneous translation on full binary column addresses, every character
occurs at every f>=1: the H action is free, so its orbits are regular H-sets.
Thus equality of those operators implies equality of their character blocks.
The construction and lower bound hold at every positive width. If the address
representation omits characters, use only the occurring ones. If the permitted
ordinary maps mix characters or leave the kernel algebra, this particular
whole-field lower bound does not apply; the flattened field theorem still has
its own coordinate dimensions.

For coefficient norms, sum absolute coefficients over v before taking the row
maximum. Translations are coordinate permutations. The same B,C,M proof then
bounds every partial coefficient-and-translation ADD with no payload-volume
factor. A complete fixed-tape implementation still needs its movement and
arithmetic-interior bill.

## Application to the pinned Gaussian reader

The source sets `J=Q^2 U`, `D0=(V Q^2 U)^-1 V`, `D1=(VU)^-1 V Q^2` and
`Delta=D1-D0`. It proves `D0 J=D1 J=I`, hence `Delta J=0`. Its recoder is
`I+J Delta`. For its thirty-mode factorization, partition J and Delta into
blocks of q rows/columns. This gives an explicit coefficient-ring-preserving
upper word of `2 ceil(30/q)+2` shears, without a new Gaussian request. It uses
only coefficient sums and differences, so it does not add a new prime to the
supplied coefficient ring. At q=30 it is exactly the credited four-shear word.

The sharp count for that actual kernel depends on
`max_chi rank((J Delta)(chi))`, not on rank(E-I)=30 alone. This package does
not compute that source value, emit its actual numerical reader kernels,
or price its complete physical route. The thirty-mode example below is a
synthetic exact fixture, not the actual Gaussian reader. The source section
still needs all thirty centre fields; reducing how many are borrowed during
a recoding does not remove that separate bank from the whole caller.

The source's section conjugacy remains valid because every recoding restores
its borrowed baseline, before and after the section changes the centre state.
The verifier checks one nontrivial rational instance on every data and centre
column. No common-frame assumption is waived. The sixteen-row joined services
remain distinct from this thirty-row application.

## Verification

Python 3.12 and its standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/borrowed-space-shear-tariff
```

The registered normal and optimized commands print
`PASS_BORROWED_SPACE_SHEAR_TARIFF`. They use explicit exceptions under `-O`.
Forty-two rational cases, including changed bases and dyadic fractions, replay
2,947 coefficient ADDs on every input column, their inverses, the clean/dirty
distinction, and both scalar prefix/suffix bounds. An independent binary
matrix BFS covers all 168 GL3(F2) states and gives distance four for all three
rank-one square-zero targets. A meet-in-the-middle check uses complete balls
of 481 states at depth two and 7,111 at depth three to exclude every word of
length at most five for a rank-two target with one dirty coordinate. The
attaining compiler gives six. This is finite corroboration of the general proof.

Eight synthetic thirty-mode cases cover q=1,2,3,5,6,10,15,30. Their exact shear
counts are 62,32,22,14,12,8,6,4. Each uses 120 coefficient ADDs and has exact
scalar prefix and suffix norms three. Eight translation-kernel cases cover
group orders two and four, widths one and two, and q=1,2, with unequal character
ranks. The verifier prints their coefficient counts, denominator least common
multiples and exact interval norms. For the order-four kernel, one borrowed field takes six shears and 60
coefficient ADDs; two borrowed fields take four shears and 72 coefficient
ADDs. Thus fewer shears need not minimize scalar work. These are exact
synthetic kernel comparisons, not a priced Gaussian caller.

Ninety controls include clean-input misuse,
deleted instructions, wrong factor relations, nonsquare-zero matrices and
invalid kernels. The two frozen source documents are authenticated.

No prior full source suite, actual Gaussian-kernel numerical replay, selected
cold replay, native/outer admission, proof assistant or independent human
review was run. The general proof requires mathematical review; finite tests
do not certify a multiplication theorem.

## Open next questions

- Compute the actual pinned reader's character-rank maximum and a factorization
  within its admitted coefficient ring. This determines whether the thirty-mode
  upper bound is sharp and whether coefficient growth defeats a smaller bank.
- Bind a chosen q to an actual physical schedule. Price every coefficient scan,
  translation, route, arithmetic interior and source lifetime, then recompute
  the complete caller bill. A shear-count optimum alone does not raise kappa.
