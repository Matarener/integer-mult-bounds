# The sharp five-site supplement for a six-flat and a seven-flat

## Statement

Let $\Phi$ be the E8 roots normalized to squared norm two. Work with their
120 unoriented lines, choosing one rational representative on each line.
Let $F$ be any eight mutually orthogonal root lines and put
$P=\Phi/\{\pm1\}\setminus F$. Thus $P$ has 112 lines.

Let $L$ be the E8 lattice and $V=L/2L$. A root line $r$ has label

$$
    \ell(r)=(1,\bar r)\in\mathbf F_2\oplus V.
$$

For a binary linear space $U\subseteq\mathbf F_2\oplus V$, write
$\Lambda(U)=\{r\in P:\ell(r)\in U\}$. For a characteristic-zero field
$K$, define

$$
 c_h(r)=\langle r,h\rangle,\qquad
 C=\{c_h:h\in K^8\},\qquad
 \operatorname{Off}(h)=\{r\in P:c_h(r)\ne0\}.
$$

Write $w(S)=\dim_{\mathbf F_2}\operatorname{span}\ell(S)$ for a site
set, and $w(p)=w(\operatorname{supp}p)$ for a piece.
For a finite-dimensional piece space $T$, let
$\operatorname{cost}_w(T)=\min_{\mathcal B}\sum_{p\in\mathcal B}w(p)$,
where the minimum ranges over its bases.

**Theorem.** For every nonzero $h\in K^8$ and binary spaces $U_6,U_7$
of dimensions at most six and seven,

$$
 \left|\operatorname{Off}(h)\setminus
       \bigl(\Lambda(U_6)\cup\Lambda(U_7)\bigr)\right|\ge5.       \tag{1}
$$

The constant five is attained on the fixed puncture in the pinned source.
Equivalently, no nonzero word in $C$ is a sum of one piece of binary
support rank at most six, one of rank at most seven, and an arbitrary
piece supported on at most four sites. The pieces may overlap and have
arbitrary coefficients and cancellations; independence is unnecessary.
In particular, support-rank bounds $3,6,7$ cannot represent a nonzero
word, since a rank-three support has at most four sites.

The standard real Weyl-chamber theorem is the classical input in the
root-rigidity step below. All subsequent support bounds and the new
deleted-quarter argument are analytic binary linear algebra. No printed
flat census, decoder normalization, correction bound or supplier premise
is used.

## 1. Bind the quadratic space and the literal labels

Use the standard realization

$$
 L=\{x\in\mathbf Z^8:\textstyle\sum_i x_i\in2\mathbf Z\}
   \ \cup\
   \{x\in(\mathbf Z+\tfrac12)^8:\textstyle\sum_i x_i\in2\mathbf Z\}.
$$

It is even and unimodular. For example, its integral part is $D_8$;
the displayed half-integral coset makes an index-two extension of
$D_8$, whose determinant is four. Therefore $L$ has determinant one.
The form

$$
 q(\bar x)=\langle x,x\rangle/2\bmod2,\qquad
 B(\bar x,\bar y)=\langle x,y\rangle\bmod2
$$

is well defined on the eight-dimensional binary space $V$, and $B$
is nondegenerate. Here $B(x,y)=q(x+y)+q(x)+q(y)$.

The ambient signed sum is

$$
                    \sum_{x\in V}(-1)^{q(x)}=16.               \tag{2}
$$

One direct proof, fixing its sign, uses the following four lattice vectors,
with coordinate indices $0,\ldots,7$:

$$
 2e_7,\quad e_0+e_1+e_2+e_3,\quad
 e_0+e_1+e_4+e_5,\quad e_0+e_2+e_4+e_6.
$$

Their residues are independent, each has $q=0$, and all mutual pairings
are even. For independence, every nonempty combination of the last three
has a nonzero even/odd coordinate pattern with coordinate seven even, so
it is neither all even nor all odd and cannot belong to $2L$.
The remaining vector $2e_7$ is not in $2L$, because $e_7\notin L$.
They span a totally singular four-space $R$. Nondegeneracy gives
$R^\perp=R$. Summing over cosets of $R$, every coset other than $R$
cancels by a nonzero character of $R$; the coset $R$ contributes 16.
This proves (2).

The 120 root lines give 120 distinct residues with $q=1$. Indeed, if
two nonparallel roots $\alpha,\beta$ had the same residue, then
$(\alpha-\beta)/2\in L$, but its squared norm is
$1-\langle\alpha,\beta\rangle/2\in\{1/2,1,3/2\}$, impossible in the
even lattice $L$. Equation (2) says that there are exactly
$(256-16)/2=120$ value-one vectors. Thus root lines are in bijection
with the $q=1$ vectors of $V$.

The source representatives are doubled roots. Their integral coordinates
in the doubled simple-root basis give exactly the same lattice residues;
the common doubling changes no support. The nine-bit label's leading
one is the low bit in the source files. The pinned source geometry uses
the following doubled simple roots:

    (1,-1,-1,-1,-1,-1,-1, 1)
    (2, 2, 0, 0, 0, 0, 0, 0)
    (-2,2, 0, 0, 0, 0, 0, 0)
    (0,-2, 2, 0, 0, 0, 0, 0)
    (0, 0,-2, 2, 0, 0, 0, 0)
    (0, 0, 0,-2, 2, 0, 0, 0)
    (0, 0, 0, 0,-2, 2, 0, 0)
    (0, 0, 0, 0, 0,-2, 2, 0).

After dividing by two these form a lattice basis of $L$; their Gram
determinant is one. Hence their coordinate residues identify $V$ with
$\mathbf F_2^8$. PR2816's alternative label map pairs a root modulo two
against a unimodular root basis. Unimodularity makes that an invertible
linear change of the eight residue coordinates. The leading bit remains
one. Root ordering, root signs and this label change preserve every
support-rank statement here. Exact retained inputs and byte bindings are
listed in [SOURCES.json](SOURCES.json).

## 2. Three global support capacities

We reproduce the signed argument of PR3269 and PR3300 so that the
capacities used in the proof do not depend on a census receipt.

A nonempty support whose nine-bit labels have rank at most $d$ lies in
the leading-one section of its binary span. Forgetting the leading bit
identifies this section with an affine space $a+H\subseteq V$ of
dimension at most $d-1$. Lower-dimensional affine spaces may be
extended. Thus it suffices to count the value-one points of $q$ on
affine spaces.

Let $k=\dim H$, let the polar restriction to $H$ have rank $2r$,
and let $R_H=H\cap H^\perp$ have dimension $t=k-2r$.
Nondegeneracy of the ambient polar form gives $t\le8-k$. Put

$$
                    S(a+H)=\sum_{x\in H}(-1)^{q(a+x)}.
$$

Polarization and character cancellation give

$$
 S(a+H)^2
   =2^k\sum_{z\in R_H}(-1)^{q(z)+B(a,z)}.                     \tag{3}
$$

The exponent on $R_H$ is linear. If nonzero, then $S=0$.
Otherwise $|S|=2^{k-r}$.

There is a useful sign refinement when $k+t=8$. In the latter case
$H=R_H^\perp$, and $q_a(x)=q(x)+B(a,x)$ vanishes on $R_H$.
Cosets of $R_H$ outside $H$ cancel, so

$$
 \sum_V(-1)^{q_a(x)}=\sum_H(-1)^{q_a(x)}.
$$

Translating $q$ by $a$ and using (2) shows

$$
                         S(a+H)=+16.                         \tag{4}
$$

This is a positive signed value, not merely an absolute-value bound.
The number of roots in $a+H$ is $(2^k-S(a+H))/2$.

For $k=4$, polar ranks zero, two and four give at most $8,12,10$
value-one points, respectively: in the rank-zero, unbalanced case
(4) gives zero points rather than sixteen. For $k=5$, polar rank
zero is impossible; rank two gives at most sixteen by (4), and rank
four gives at most twenty. For $k=6$, polar ranks four and six give
at most thirty-two and thirty-six. Therefore

| Binary support rank at most | 5 | 6 | 7 |
|---|---:|---:|---:|
| Full-root support size at most | 12 | 20 | 36 |

All three bounds remain true after puncturing. Also a support of rank
$d$ has at most $2^{d-1}$ sites from the leading-one coordinate alone.

We will also use the ambient Walsh identity, an immediate translation
of (2):

$$
 \sum_{x\in V}(-1)^{q(x)+B(y,x)}=16(-1)^{q(y)}.              \tag{5}
$$

## 3. A small codeword is a scalar root word

We need the following standard E8 consequence of the real Weyl-chamber
theorem:

$$
 |\operatorname{Off}(h)|<70
       \quad\Longrightarrow\quad h\text{ is a scalar root direction}.
                                                                    \tag{6}
$$

Here is the argument and its finite root-system input. Move a real
nonzero normal into a closed fundamental Weyl chamber. Its perpendicular
roots are generated by the simple roots on which it vanishes.
A subsystem on at most six simple nodes has at most 36 root lines,
by the ADE root counts. The same bound holds for any root set of
rational span at most six: all roots in that span form a root
subsystem of rank at most six. For the displayed simple-root order, deleting
one node gives

| Deleted node | Remaining type | Root lines |
|---:|---|---:|
| 0 | $D_7$ | 42 |
| 1 | $A_7$ | 28 |
| 2 | $A_6+A_1$ | 22 |
| 3 | $A_4+A_2+A_1$ | 14 |
| 4 | $A_4+A_3$ | 16 |
| 5 | $D_5+A_2$ | 23 |
| 6 | $E_6+A_1$ | 37 |
| 7 | $E_7$ | 63 |

The table follows by deleting nodes in that Dynkin diagram and using
the usual ADE root counts; it is not an inference from a search maximum.
Only the last face can contain more than 42 root lines. Its normal is
the root $e_6+e_7$: it is perpendicular to the first seven displayed
simple roots. Below 70 nonzero live sites means at least 43 live
perpendicular roots, so the moved normal is this root direction.
This argument is uniform over the puncturing frame.

For arbitrary characteristic-zero $K$, let $Z\subseteq P$ be the live
rational root representatives annihilated by $h$. Rational matrix rank is unchanged after extension
to $K$, so their rational span has dimension at most seven.
The live roots span eight dimensions: in the norm-two convention their
outer-product sum is $28I_8$ (the full-root sum is $30I_8$, and the
orthogonal frame contributes $2I_8$). Thus a nonzero $h$ has at
least one nonzero live evaluation.
Its rational annihilator contains a rational vector with exactly the
same root zeros: every additional nonzero-root equation cuts out a
proper rational hyperplane, and finitely many such hyperplanes do not
cover a rational vector space. Apply the real argument to this vector.
Its full perpendicular roots form an $E_7$ system. The live set
$Z$ itself has at least 43 lines, more than the rank-six bound
36, so $Z$ spans dimension seven. Its one-dimensional rational
annihilator contains $h$ after scalar extension. This proves (6)
over $K$, without ordering $K$ or sampling a finite field.

For a root $v$, a different root line has pairing $0$ or $\pm1$.
Consequently

$$
 \operatorname{Off}(v)
    =\{r\in P:B(\bar v,\bar r)=1\}
        \ \cup\ \bigl(\{v\}\cap P\bigr).                      \tag{7}
$$

The full nonself neighborhood has 56 lines, from (5) with one constraint.
If $v\notin F$, it has exactly four nonorthogonal frame neighbors:
$\sum_{f\in F}\langle v,f\rangle^2=2\langle v,v\rangle=4$.
If $v\in F$, its other frame partners are orthogonal. Hence the live
root-word support sizes are 53 and 56, respectively.

## 4. A large rank-seven residual forces a full 32-root completion

Suppose a root normal $v$ satisfies

$$
 R\subseteq\operatorname{Off}(v),\qquad |R|\ge29,\qquad
 \operatorname{rank}_{\mathbf F_2}\ell(R)\le7.                \tag{8}
$$

The rank is exactly seven, since rank six supports at most twenty
points. Its leading-one section is a unique affine six-space $A$.
Write $v$ also for its residue when it occurs inside $B$ or $q$.

If $B(v,\cdot)$ varied on $A$, its value-one slice would be an
affine five-space with at most twenty roots. Equation (7) permits at
most one further root, the self line $v$, so $|R|\le21$, a
contradiction. If the value were constantly zero, there would be at
most the self line. Thus

$$
                         A\subseteq\{x:B(v,x)=1\}.            \tag{9}
$$

The perpendicular plane to the direction of $A$ contains $v$.
Choose an independent vector $s$ in it and write

$$
                A=\{x:B(v,x)=1,\ B(s,x)=\theta\}.
$$

Equation (5) gives

$$
 \sum_{x\in A}(-1)^{q(x)}
  =4\sum_{a,b\in\mathbf F_2}
        (-1)^{q(av+bs)+a+b\theta}
  =4\sum_{a,b}(-1)^{b(q(s)+\theta)+abB(v,s)}.                \tag{10}
$$

If $B(v,s)=1$, this sum is eight, so $A$ has 28 roots.
If $B(v,s)=0$, it is zero or sixteen, so $A$ has 32 or 24.
Condition (8) forces the 32 case. Set $u=s+q(s)v$. Then

$$
 q(u)=0,\quad B(v,u)=0,\quad
             A=\{x:B(v,x)=1,\ B(u,x)=1\}.                    \tag{11}
$$

In particular $u,v$ are independent. The parallel affine six-space

$$
 A_C=\{x:B(v,x)=1,\ B(u,x)=0\}
$$

has exactly 24 roots, again by (10). Denote that root set by $C_v$.
It has binary label span $W_C$ of dimension seven, since 24 is
larger than the rank-six capacity twenty. The self label $\ell(v)$
does not belong to $W_C$, because $B(v,v)=0$ while every
leading-one point in $W_C$ satisfies $B(v,x)=1$.

The original residual spans the entire seven-space of (11).
Thus any rank-seven label space containing $R$ is precisely that
space; it contains none of $C_v$, and it does not contain the
live self line $v$.

## 5. The deleted quarter has six-flat capacity sixteen

**Quarter lemma.** Any binary label space $W$ of dimension at most six
contains at most sixteen roots of $C_v$. If it contains $\ell(v)$,
it contains at most twelve roots of $C_v$.

For the first assertion, enlarge $W\cap W_C$, if necessary, to a
hyperplane in $W_C$. Its leading-one section is either empty or a
proper affine hyperplane of $A_C$, so it adds a constraint
$B(s,x)=\theta$ with $s\notin\langle v,u\rangle$.
The resulting affine five-space has 32 points. Its signed quadratic
sum is

$$
 \frac{16}{8}\sum_{a,b,c\in\mathbf F_2}
       (-1)^{q(av+bu+cs)+a+c\theta}.                         \tag{12}
$$

Using $q(v)=1,q(u)=0,B(v,u)=0$, the exponent simplifies to

$$
 c(q(s)+\theta)+acB(v,s)+bcB(u,s).
$$

The $c=0$ contribution is four. The $c=1$ contribution is zero
if either coupling is one, and otherwise it is $+4$ or $-4$.
Hence (12) is eight, sixteen or zero. The root count is respectively
twelve, eight or sixteen. This proves the bound sixteen.

If $\ell(v)\in W$, the fact $\ell(v)\notin W_C$ gives
$\dim(W\cap W_C)\le5$. The global rank-five capacity from section 2
then gives the stronger bound twelve. This proves the lemma.

## 6. Prove the five-site floor

Suppose, contrary to (1), that

$$
 \operatorname{Off}(h)\subseteq
       \Lambda(U_6)\cup\Lambda(U_7)\cup E,\qquad |E|\le4.
$$

The global capacities give $|\operatorname{Off}(h)|\le20+36+4=60<70$.
By (6), rescale $h$ to a root $v$. The residual

$$
 R=\operatorname{Off}(v)\setminus(\Lambda(U_6)\cup E)
$$

has at least $53-20-4=29$ sites and lies in $U_7$.
Section 4 therefore identifies $U_7$ with the full 32-root completion.
Its deleted quarter $C_v$ and any live self line must be covered by
$\Lambda(U_6)\cup E$.

Let $f=|C_v\cap F|$. Equation (7) and the frame identity give
$f\le4$; if $v\in F$, then $f=0$.

If $f\le3$, at least 21 live quarter roots must be covered.
The quarter lemma and $E$ cover at most $16+4=20$, a contradiction.

It remains to consider $f=4$. Then $v\notin F$, the live quarter
has twenty sites, and the self line $v$ must also be covered.
If $\ell(v)\in U_6$, the stronger quarter bound leaves capacity
at most $12+4=16<20$. If $\ell(v)\notin U_6$, then $v\in E$.
Since $v\notin C_v$, at most three sites of $E$ remain available
for the quarter, giving $16+3=19<20$.

Every case is impossible. This proves (1).

For the equivalent piece statement, the supports of the rank-six and
rank-seven pieces lie in their binary label spans. The remaining
piece supplies at most four sites. Conversely, a hypothetical cover
allows the codeword to be partitioned among these three support sets.
Thus the two formulations are equivalent, with no restriction on
coefficients or overlap.

## 7. A literal five-site coefficient partition

Use the fixed frame
$e_0\pm e_1,e_2\pm e_3,e_4\pm e_5,e_6\pm e_7$.
Take $v=e_0+e_2$, $w=e_0-e_2$, and $a=e_0+e_1+e_2+e_3$.
The live support of $c_v$ is a disjoint union $X\sqcup Y\sqcup E_5$:

* $X$ consists of the 32 half-integral root lines with equal
  coordinates zero and two. Equivalently its residues satisfy
  $B(v,x)=1,B(w,x)=0$.
* $Y=\{e_0\pm e_j,e_2\pm e_j:j=4,5,6,7\}$, sixteen lines.
  It is the section $B(v,x)=B(w,x)=B(a,x)=1$.
* The remaining five lines are

$$
 E_5=\{e_1-e_2,\ e_1+e_2,\ e_0-e_3,\ e_0+e_3,\ v\}.
$$

These descriptions follow directly from the two-coordinate and
half-integral root forms. The four deleted frame neighbors are
$e_0\pm e_1,e_2\pm e_3$.
Thus $|X|=32,|Y|=16,|E_5|=5$ and their union is exactly
$\operatorname{Off}(v)$, which has 53 sites.

The residues $v,w,a$ are independent: $v+w=2e_0$ is nonzero
modulo $2L$, and the odd coordinates one and three of $a$ put it
outside their span. The two affine equations give $w(X)\le7$,
while $|X|>20$ gives $w(X)=7$. The three independent equations give $w(Y)\le6$,
while $|Y|>12$ gives $w(Y)=6$. The labels of the first four
lines of $E_5$ sum to zero, since $2e_i$ has the same residue
for every $i$. Consequently $w(E_5)\le4$; five distinct
leading-one labels cannot have rank at most three, so $w(E_5)=4$.

Define each of three pieces to equal $c_v$ on its displayed set
and zero elsewhere. They are nonzero, disjoint and sum to $c_v$
over every characteristic-zero field, with support ranks $7,6,4$.
In the doubled source convention the scalar value is
$R\mathbin{\cdot}V/4$, where $R=2r$ and $V=2v$.
This is an actual rational coefficient witness, rather than just a
support mask. It attains the five-site supplement in (1).

Splitting $E_5$ into its first four sites and $\{v\}$ gives
four independent pieces of ranks $7,6,3,1$, with sum $c_v$.
Their span intersects $C$ in exactly one dimension: every codeword
in their span vanishes on the 59 live roots perpendicular to $v$;
those roots span dimension seven, because a root subsystem of
rank at most six has at most 36 lines. Its normal is therefore $v$.
The displayed basis is also a minimum-weight basis. More generally,
let disjoint-support nonzero pieces $p_1,\ldots,p_m$ form a basis.
A linear combination has support equal to the union of the supports
whose coefficients are nonzero, so its weight is at least that of
each participating $p_j$. The coefficient matrix of any other basis
is invertible. A nonzero term in its determinant matches its rows
bijectively to distinct columns with nonzero coefficients. Summing
the corresponding lower bounds gives a total weight at least
$\sum_j w(p_j)$. For these four pieces the minimum is therefore
$7+6+3+1=17$. This supplies a genuine nearby $d=1$,
$\operatorname{cost}_w(T)=17$, T-space with slack nine.
It supplies no marked decoder or correction-invoice counterexample.

## 8. Scope, source dependencies and credit

The exact earlier one-extra-site check is PR2816 at
`4c32ac3b88d63ad06d2b30e526aa07a12929db36`,
in `research/one-sided-decoders-all-m/checks/cover761.py`.
For a 53-site root target it retains seven-flat sections of size at
least 32 and six-flat sections of size at least 20. Those thresholds
are sound for its question: covering with one further site needs
at least 52 sites from the two flats, whose target capacities are
32 and 20. Its printed minimum of nine uncovered sites ranges over
that pruned domain. It is not a global minimum over all six/seven-flat
pairs. The present literal 32-plus-16 partition leaves five sites and
does not enter the predecessor's six-section domain. Thus it is a
counterexample to interpreting the printed nine as a global bound, while the
predecessor's no-one-extra-site theorem remains valid.

The new ingredients are the root-specific 32-point completion, the
deleted-quarter capacity sixteen and its self-line refinement, and the
resulting sharp six/seven-flat supplement theorem. The signed character
method and global capacities are credited to PR3269 and PR3300, with the
full arguments reproduced above. David Arias's retained
`masked-root-star-assembly` is earlier E8 quadratic-model work credited
by those sources. The E8 root code, frame, labels and
root-rigidity lineage come from PR2816, PR3154 and the retained
PR3161/3162 geometry, including joaqcoo's earlier decoder formulation.
PR2816 already records the numerical 32-point root-target capacity;
the present argument identifies the completion and its deleted quarter.
Exact heads and source files are recorded in [SOURCES.json](SOURCES.json).

[CALLERS.md](CALLERS.md) gives the nine literal PR3154 implications.
They are statements about independent pieces and their code intersection.
The support theorem alone does not validate N8, the source's global branch
reduction, C1 as a whole or supplier admission. [UNIFORM.md](UNIFORM.md)
adds the complete root-word equality classification. [D1.md](D1.md) uses
additional retained matched-cut inputs to derive the actual d=1 invoices
and the stated singleton-pivot consumer, including all actual-basis surplus.
[D2.md](D2.md) separately closes the actual d=2 invoices.
Actual d>=3 invoices and global normalization remain separate.

The mathematical proof uses the standard Weyl-chamber theorem; finite
coordinate checks corroborate its declared E8 inputs and the literal
witness rather than replacing that theorem. Any formal cores have only
their separately stated scope. Neither executable success nor a partial
formalization would constitute a proof-kernel verification of the entire
argument.

New work is by conorholds with substantial OpenAI Codex assistance.
Predecessor authorship and licensing remain as recorded in the retained
sources.
