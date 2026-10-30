# Nine literal C1 piece profiles excluded

## Exact source and statement

Use the P112 evaluation code $C$ and binary support weight

$$
       w(p)=\dim_{\mathbf F_2}
              \operatorname{span}\{\ell(r):p(r)\ne0\}
$$

from [PROOF.md](PROOF.md), over an arbitrary characteristic-zero field.
Let independent pieces $p_1,\ldots,p_n$ span $T$, and put $D=T\cap C$.

For each row below there is no such independent family with the displayed
weight upper bounds and $\dim D\ge d$.
The displayed $t$ and slack are the literal source tags, with
$n=d+t$ and $\text{slack}=\sum W-8d$.
The theorem uses only the independent-piece and intersection hypotheses;
it does not require a minimum basis or a decoder realization.

| Source $t$ | $d$ | Slack | Weight bounds $W$ | Small supports remaining after the deletion | Site cap |
|---:|---:|---:|---|---|---:|
| 2 | 1 | 7 | $7,6,2$ | one rank-two piece | 2 |
| 2 | 1 | 8 | $7,6,3$ | one rank-three piece | 4 |
| 2 | 2 | 6 | $7,7,6,2$ | one rank-two piece | 2 |
| 2 | 2 | 7 | $7,7,6,3$ | one rank-three piece | 4 |
| 3 | 1 | 7 | $7,6,1,1$ | two rank-one pieces | 2 |
| 3 | 1 | 8 | $7,6,2,1$ | rank-two and rank-one pieces | 3 |
| 3 | 2 | 6 | $7,7,6,1,1$ | two rank-one pieces | 2 |
| 3 | 2 | 7 | $7,7,6,2,1$ | rank-two and rank-one pieces | 3 |
| 3 | 2 | 8 | $7,7,6,2,2$ | two rank-two pieces | 4 |

All nine are recorded survivors in DreamingOfClouds's
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154),
pinned at
`708f0ad8928c383de8294aea3c126e9461d2066d`.
Their exact source files are

    research/p112-reduction-to-conjectures/checks/CONJG2/NOTES.md
    research/p112-reduction-to-conjectures/checks/CONJG2/land_e2_k8.out
    research/p112-reduction-to-conjectures/checks/CONJG2/land_e3_k8.out.

The two output files are retained byte-for-byte under this package's
inputs and authenticated by [SOURCES.json](SOURCES.json). The first
records 35 profiles and the second 280. Those are the source's recorded
lists, not a claim about the number currently unresolved by every
subsequent public theorem.

## Dimension-deletion lemma

Suppose $T$ is spanned by independent pieces. Their coefficients identify
$T$ with $K^n$. If $\dim(T\cap C)\ge d$, imposing zero coefficients
on any chosen $d-1$ pieces leaves a nonzero codeword.

Indeed, restrict the corresponding $d-1$ coordinate functionals to
$D=T\cap C$. Their common kernel has dimension at least
$\dim D-(d-1)\ge1$. A nonzero vector in that kernel is a nonzero
codeword because the original pieces are independent. This argument
allows $\dim D>d$; equality is unnecessary.

Each table row has exactly $d$ designated rank-seven pieces.
For $d=1$, choose any nonzero word in $D$.
For $d=2$, set the coefficient of one designated rank-seven piece
to zero by the lemma. In both cases the resulting nonzero word is a
linear combination of

* one piece of binary support rank at most seven;
* one piece of binary support rank at most six;
* the displayed small pieces, whose union has at most four sites.

The site cap follows from the labels' leading one:
a rank-one, rank-two or rank-three support has at most $1,2,4$ sites.
Taking linear combinations does not enlarge any piece's support, and
aggregating the small pieces has support contained in their union.
Arbitrary overlap and cancellation are permitted.

The nonzero word therefore contradicts the theorem of
[PROOF.md](PROOF.md). This proves every row of the table.
There is no quotient-normalization step and no inference from a failed
support search.

## What the caller theorem establishes

The source CONJG2 section3 uses $T$ as the low-weight subspace,
$d=\dim(T\cap C)$, $e=\dim T-d=t$, and slack
$\operatorname{cost}(T)-8d$. A minimum basis of that $T$, if it has
one of the nine displayed profiles, is an independent family satisfying
the exact hypotheses just excluded. Thus these nine profiles cannot
occur as such a minimum basis.

This implication does not assume the source's N8 correction cap, the
completeness of the 35/280 lists, or its global peeling and branch-coverage
arguments. It is valid for each displayed piece family in isolation.
It also does not show that an arbitrary actual decoder basis is adapted
to $T$. A basis-surplus unit can change the number of actual low and
high members; no argument about those members' restricted dual rows is
needed here.

Consequently this caller argument supplies nine literal T-level exclusions
with a uniform geometric mechanism. [D1.md](D1.md) separately proves the
complete actual d=1 marked/unmarked invoices and stated singleton consumer
using the additional retained matched-cut geometry. [D2.md](D2.md) extends the actual invoice to d=2. Complete C1, actual
d>=3 invoices, global normalization and supplier admission remain outside
the package result.
It does not certify a present global survivor count.

## Boundary and further work

The sharp partition in [PROOF.md](PROOF.md) has piece ranks $7,6,4$.
Splitting its five-site remainder into four sites and the root singleton
gives ranks $7,6,3,1$, independent pieces, code intersection dimension
one, minimum basis cost seventeen, and slack nine. Minimum cost follows
from the disjoint-support determinant matching argument in that proof.
Hence the primary obstruction cannot simply be
extended from four small sites to five, or used to discard that nearby
T-level boundary. That fixture is not an actual marked decoder.

The actual d=1 argument in D1.md retains all basis-surplus scenarios and
closes the cost-seventeen invoice without excluding its feasible T-space.
The remaining higher-d profiles require further shared-cover or coefficient
arguments. This caller inventory does not certify a current global survivor count.

Credit DreamingOfClouds for the source reduction, notation, filters and
recorded profiles; credit PR2816 and the retained E8/P112 lineage for the
piece model and earlier circuit/quotient methods. The new dimension-deletion
application is by conorholds with substantial OpenAI Codex assistance.

## Appendix: inherited four-six pencil composition

There is also a useful direct composition of the earlier coordinate-kernel
and root-pencil method. Credit Nick Petalas's PR3171, head
`95b683196950efea6f3d7ac66745e00dba73425e`,
`research/p112-quotient-parity/PROOF.md`, and DreamingOfClouds's PR2816,
head `4c32ac3b88d63ad06d2b30e526aa07a12929db36`, for the retained
root-rigidity and circuit/pencil lineage. This appendix records a caller
composition, not a new geometric mechanism.

**Four-six-plus-nine lemma.** Suppose an independent piece family has four
designated pieces of binary support rank at most six. Suppose every other
piece is supported in one common set E of at most nine live sites. Its span
cannot meet C in dimension at least two.

Choose a two-dimensional subspace D of that intersection, and restrict the
four designated piece-coordinate functionals to D. For any two of these
functionals, their joint kernel is zero: a nonzero vector there would be a
codeword supported on the other two rank-six pieces and E, hence on at most
`20+20+9=49<53` sites. Each single functional is consequently nonzero and
has a one-dimensional kernel, and the four kernel lines are distinct.
On each kernel line a nonzero codeword is supported on three rank-six
pieces and E, hence on at most `3*20+9=69<70` sites. Root-direction
rigidity identifies each with an E8 root line, including frame roots.
Injectivity of root evaluation puts four distinct root lines in the same
two-dimensional normal space. This is impossible: a rank-two subsystem of
the simply laced E8 root system is A1+A1 or A2 and has at most three
projective root lines. The argument works over any characteristic-zero
field by the same rational-line transfer as the retained pencil method.

More generally, for d>=2, if the original code intersection has dimension at least d,
first kill any d-2 chosen piece coordinates. The dimension-deletion lemma
leaves an intersection of dimension at least two. The preceding lemma then
applies whenever the remaining pieces consist of four rank-at-most-six
pieces and pieces supported in a common set of at most nine sites.

For the pinned PR3154 outputs, deleting the heaviest d-2 pieces and applying
this criterion selects two literal t2 rows and 83 literal t3 rows. In t2
the four remaining pieces all have rank at most six. In t3 the five
remaining pieces include four of rank at most six and one of rank at most
four; the latter has support at most eight, so can serve as E. These are
implications for the literal recorded profiles, not 85 currently open
cases or 85 first closures. They neither establish completeness of those
historical lists nor bypass the actual-basis and normalization obligations
for higher-d invoices.
