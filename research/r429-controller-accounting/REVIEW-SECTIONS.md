# B03 independent mathematical review

**Finding:** the alternating row-section obstruction is correct. Its scope is
the specified common-endpoint word, with the original input gauge retained.
The argument does not prove a paid terminal-decoder lower bound. The fresh
independent checker also reproduces the complete archived root-line census
and gives useful exact strengthening of its classification.

This is a written mathematical proof plus finite exact arithmetic verification,
prepared by Ross Richardson with substantial OpenAI Codex assistance. It is
not a formal-kernel proof or independent human review. The historical
scientific pin is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`; the inspected
current checkout is `12fa8c5c844be21bfefb38a19503fbd867a11244`.

## 1. Row-section theorem and its exact premises

Let \(J\) be an \(n\)-by-\(n\) matrix over a field. Let the \(2k+1\) matrices
\(A_0,\ldots,A_{2k}\) be invertible. For each \(s\), let \(P_s\) be a physical
**row** set such that
\[
e_p^T A_s=e_p^T J\quad(p\notin P_s).
\]
Set \(P=\bigcup_s P_s\) and preserve the ordered word
\[
E=A_{2k}A_{2k-1}^{-1}\cdots A_2A_1^{-1}A_0 .
\]
Then \(e_p^TE=e_p^TJ\) for every \(p\notin P\).

Indeed, write
\[
T_i=A_{2i}A_{2i-1}^{-1}
   =I+(A_{2i}-A_{2i-1})A_{2i-1}^{-1}.
\]
Right multiplication cannot create a nonzero row from a zero row. Thus
\(e_p^TT_i=e_p^T\) outside \(P_{2i}\cup P_{2i-1}\). For \(p\notin P\),
successively multiplying the row vector \(e_p^T\) by the factors
\(T_k,\ldots,T_1\) leaves it unchanged; multiplication by \(A_0\) then gives
\(e_p^TJ\). No commutation of the factors is used.

The proof only requires the odd-indexed inverses for the algebraic identity;
the stated invertibility of every stage retains the reversible-interface
contract. There is no requirement that \(J\) be invertible. There is no
\(RW=0\), involution, finite quotient-order, fixed-section or identical-stage
premise. The general theorem is valid in every characteristic. The actual
R438 application and all rank numbers below are over \(\mathbb F_2\).

The repair equation \(J=(I+Q_s)A_s\), with \(Q_s\) supported on \(P_s\),
implies the required agreement directly by taking rows outside \(P_s\).
The proof concerns rows, so a column-supported repair is not interchangeable.
Nor can the order \(A_{2i}A_{2i-1}^{-1}\) be reversed.

The finite checker tests every \(J\in M_2(\mathbb F_2)\), every sequence in
\(\operatorname{GL}_2(\mathbb F_2)\), and lengths \(1,3,5\): 127,968 cases,
including 990 cases with at least one uncovered row. These finite tests
support the implementation; the preceding written proof supplies the
all-parameter statement.

## 2. Exact coverage consequence

Let
\[
D=\{p:e_p^TJ\ne e_p^T\}.
\]
Identity restoration requires **\(D\subseteq P\)**, not merely a large
cardinality for \(P\). In particular,
\[
|D|\le |P|\le\sum_s|P_s|.
\]
If every stage changes at most \(r>0\) rows, the odd stage count \(L=2k+1\)
must be at least the least odd integer not smaller than \(\lceil |D|/r\rceil\).
This is a necessary condition only.

The independent R438 reconstruction gives \(n=111\),
\(J=I+KR\), \(\operatorname{rank}J=108\), and \(J_{pp}=0\) for every \(p\).
Thus \(D\) is all 111 physical rows. Nine stages with at most three repaired
rows each leave at least \(111-27=84\) diagonal entries unequal to identity.
With the same three-row budget, identity is impossible at every odd stage
count below **37**. At exactly 37 stages, all repair sets must have size
three and form a disjoint partition of the 111 rows. No 37-stage construction
or sufficiency assertion is supplied.

The nullity-three fact also independently confirms why fewer than three
row replacements cannot make this \(J\) invertible: replacing \(r\) rows
increases rank by at most \(r\).

## 3. Diagonal discrepancies and defect rank

The count 84 is not a rank bound. For a smallest explicit counterexample,
over \(\mathbb F_2\) take
\[
J=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
A_s=J,\quad P_s=\varnothing .
\]
For any odd alternating stage count, \(E=J\). Both diagonal entries differ
from identity, but
\[
E-I=\begin{pmatrix}1&1\\1&1\end{pmatrix}
\]
has rank one.

The actual fixed R438 data allow a separate, precise rank statement.
The checker reconstructs the \(111\)-by-9 scatter matrix \(K\) and the
9-by-111 reader matrix \(R\) directly from the frozen word's `D`, `A`, `ret`
and `scatter` data, without importing the historical producer. Both have
rank nine. The 511 nonzero binary vectors \(a\) have the following
\(|\operatorname{supp}(Ka)|\) histogram:

```
48:4, 49:12, 50:32, 51:50, 52:76, 53:52, 54:24, 55:5,
56:5, 57:24, 58:52, 59:76, 60:50, 61:32, 62:12, 63:4, 111:1.
```

Consequently, deleting any at most 47 rows of \(K\) leaves column rank nine.
Otherwise some nonzero \(a\) would have its support inside the deleted set,
contradicting the minimum support 48. For \(U=P^c\),
\[
(E-I)_U=(J-I)_U=K_U R .
\]
When \(|P|\le47\), this has rank nine because \(R\) has full row rank.
Also \(E-J\) is supported on \(P\), so
\[
9\le\operatorname{rank}(E-I)
 \le\operatorname{rank}(J-I)+|P|
 =9+|P|.
\]
For the nine three-row stages this yields **\(9\le\operatorname{rank}(E-I)
\le36\)**.

There is an additional conditional equality. If every stage obeys the
**same-reader premise**
\[
A_s-I=W_sR
\]
for the same actual \(R\), then products and inverses preserve the form
\(I+VR\):
\[
(I+UR)(I+VR)=I+(U+V+URV)R,\qquad
A^{-1}-I=-A^{-1}WR .
\]
Thus \(E-I=VR\), whose rank is at most nine. Combined with the preceding
lower bound, its rank is **exactly nine** for \(|P|\le47\).
This equality is conditional on the displayed common-reader premise; the
broader row-section theorem does not require it.

These are scalar-augmentation ranks. They provide no native factorization,
snapshot count, physical frame width, decoder tariff, precision theorem
or source-access bound. In particular, rank nine does not replace the
actual routed defect's separately derived operator channels.

## 4. Native constant-input witness

Retain the historical exact binary VALUE semantics and the native ADDRESS
interface in which layout changes act as permutations of each VALUE
function's ADDRESS arguments. On the subspace of functions constant on
ADDRESS, every such permutation acts as identity. An exact copied snapshot
copies that same constant; literal cleanup and source preservation remain
the ordinary interface obligations.

For any uncovered family \(p\), take the source VALUE function on that
physical family to be constantly one, all other source families constantly
zero, and all other arbitrary public inputs to be zero. This is an allowed
specialization of a contract that claims correctness on arbitrary inputs.
The scalar-augmentation coefficient of its own output is
\(E_{pp}=J_{pp}=0\), whereas terminal identity requires one. This witnesses
failure of identity restoration on an actual input under that native
constant-subspace contract.

This reasoning preserves the original input gauge. Relabelling the output
as already encoded, deleting a terminal permutation, changing the observer
contract, or using a non-permutation VALUE operation changes the premises.
Rounded/nonlinear implementations require their own invariant-subspace
argument. No arbitrary-input *positive* native supplier or restoration
claim follows from this negative specialization.

## 5. Independent full finite root-line census

The census has a different domain from the all-field row theorem. It covers
the actual binary \(R,K,J\), physical three-row deletions, the 120 E8 root
return lines, and the specified common-intersection two-tier block alphabet.
It does not cover arbitrary return normals or arbitrary native circuits.

The checker independently derives each of the nine old retained query cap
normals by exact rational elimination of its actual final `A`-stage frame.
The 111 physical lines together with those nine normal lines agree exactly
with the separately authenticated complete 120-line geometry.

For nonzero binary output direction \(a\) and candidate return normal \(u\),
define

* \(d(a,u)=\{p:(Ka)_p=1,\ u\cdot r_p\ne0\}\), the rows that must be deleted;
* \(M(u)=\{j:u\cdot n_j=0\}\), the old query caps containing the return line.

A template can be used after deletion \(P\) only if
\(d(a,u)\subseteq P\). A block of old query coordinates \(S\) can use it only
if
\[
\operatorname{supp}(a)\subseteq S\subseteq M(u).
\]
The output directions must span the entire block for its mixing to be
invertible. Enumerating every \(a\ne0\) and all 120 root lines, with at most
three required deletions, produces exactly 111 eligible templates.
Each requires one distinct physical deleted row, and **every template has
\(M(u)=\operatorname{supp}(a)\)**.

Therefore a fixed block \(S\) can use only the direction \(a=1_S\). Its
output rank is at most one, so invertibility forces \(|S|=1\). Among all
111 templates there is exactly one singleton:

```
output / input block mask: 32 = 1 << 5
required deleted row:      80
return normal:             (0, 1, 0, -1, -1, 0, -1, 0)
```

To enumerate admissible sections, the checker computes the left kernel of
\(I+RK\), multiplies its three basis rows by \(R\), and obtains a complete
left-kernel matrix \(C\) of \(J\). A three-row set \(P\) allows an invertible
row replacement precisely when the three columns \(C_P\) are independent:
the unchanged 108 rows of \(J\) are independent exactly when no nonzero
left-kernel vector vanishes on \(P\).

All \(\binom{111}{3}\) candidate subsets are inspected. Exactly **70,626**
are admissible. Exactly **2,270** contain row 80; these are all and only the
positive sections, and every one admits only block mask 32. The original
block-rank condition is evaluated for every admitted section, in addition
to the preceding simplifying classification. All eligible-direction ranks
are three, as in the archived receipt; that fact alone does not imply a
feasible three-channel block.

An explicit positive witness is \(P=\{1,2,80\}\). Its section labels are
\((4,2,1)\), so it is admissible. The direction \(a=32\) has 63 supported
output rows, and exactly row 80 has nonzero inner product with the displayed
return normal. The normal lies inside old query cap 5. Removing row 80
therefore makes this singleton geometry feasible. Omitting that deletion
reintroduces the actual incompatibility. In particular, this counterexample
prevents the historical no-nonempty-block result for \(P=\{0,1,2\}\) from
being generalized to all sections.

This is a geometric singleton witness only. The old query is an arbitrary
dirty total. Its extraction, compensation, literal cleanup, owners, routing
and complete controller cost remain separate obligations.

## 6. Reproduction, controls and source boundaries

`check_sections.py` uses Python's standard library, exact integers,
`Fraction`, and two gzip JSON inputs. Its CLI is directly portable:

```
python3 -I -O -B check_sections.py \
  --word /path/to/r438-t154.json.gz \
  --geometry /path/to/bitE8-r865.json.gz \
  --output /fresh/path/CHECKS.json
```

The output must not already exist. It contains the complete reconstructed
matrices, all 111 templates, all 2,270 positive sections and the finite
proof checks. Source authentication occurs before interpretation.

Mathematical controls use constructed matrices after authentication, so
they cannot pass merely because a source hash changed:

* An even two-stage word of identical swap matrices is identity and fails
  the claimed inheritance of \(J\).
* Omitting the inverse in a three-stage word of an order-three matrix
  changes its endpoint to identity.
* Reversing the ordered numerator/inverse pair changes an explicitly
  uncovered physical row.
* A singular odd-indexed stage is rejected when its inverse is requested.
* The explicit row-80 geometry has one and only one incompatible supported
  row; omitting that deletion invalidates the singleton.
* The two-diagonal, rank-one example rejects the proposed rank interpretation.

The fresh census's candidate count, complete template array, complete
eligible-direction rank histogram, section count and complete positive
array match the historical `ROOT-LINE-SECTION-DECODER.json` exactly.
That historical receipt was used only for this separate post-run comparison,
not as an input to the independent checker. The fresh input is the raw
R438 word plus the full geometry. `SOURCES.json` records exact byte hashes;
`VALIDATION.json` records actual commands, runtimes and output comparisons.

The parent owns the global controller, full arbitrary-input restoration,
returned-owner accounting and publication integration. None is inferred
from these row and root-line calculations.
