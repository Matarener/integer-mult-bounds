# The exact two-axis native tensor cutoff is six

Prepared for Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex
assistance, including a separately assisted derivation and review.
New work is Apache-2.0. This is an algebraic result for the precise monomial
class below, not a physical supplier, a cost improvement, or a new
multiplication bound.

## 1. Class, definitions, and quantified result

We specialize Ali Romman's
[native tensor cutoff theorem](../native-tensor-cutoff/PROOF.md), Sections
1–5, to two binary address axes. Retain its input-phase convention and
fixed external scalar coefficients. Let $X=\mathbb F_2^2$, with addresses
ordered as $(00,10,01,11)$, or equivalently $(0,1,2,3)$. The native group
consists of

$$
 U(g,q)e_x=i^{q(x)}e_{g(x)},\qquad
 q(x)=c+a_1x_1+a_2x_2+2b x_1x_2\pmod4,
$$

where $g\in\operatorname{AGL}(2,2)$, $c,a_1,a_2\in\mathbb Z/4$, and
$b\in\mathbb Z/2$. Write $D_q=U(1,q)$ and use the factorization
$U(g,q)=gD_q$: the phase acts first. This is the predecessor's exact
Gaussian affine/quadratic monomial grammar. Hadamard gates and other
nonmonomial operators are excluded.

There are 128 diagonal phases and 24 affine permutations. Each group
element has a unique factorization $gD_q$, so $|G|=3072$. Indeed, the
affine permutation and four phase values determine it, and evaluation at
$0,e_1,e_2,e_1+e_2$ recovers the displayed coefficients. The predecessor
proves closure and inversion for this grammar. The faithful action of
$\operatorname{AGL}(2,2)$, of order $4\cdot6=24$, on its four addresses
identifies it with $S_4$. Its sign character is denoted $\operatorname{sgn}$.

Work over $k=\mathbb Q(i)$ or $\mathbb C$. For every positive integer
$f$, extend $\rho_f([U])=U^{\otimes f}$ linearly to $k[G]$. In
particular, $\rho_f(\sum\alpha_U[U])=\sum\alpha_U U^{\otimes f}$; the
external coefficients are not tensorized. Put $z=[iI]$, and let
$I_r=(z-i^r[1])$ be the two-sided ideal of $k[G]$, for
$r\in\{0,1,2,3\}$.

**Theorem.** Set

$$
 (L_0,L_1,L_2,L_3)=(8,9,6,7).
$$

For every positive integer $f$, with $r=f\bmod4$,

$$
 \ker\rho_f=I_r\quad\Longleftrightarrow\quad f\ge L_r. \tag{1}
$$

Consequently the least integer $F\ge1$ such that
$\ker\rho_f=I_{f\bmod4}$ for **every** $f\ge F$ is $F=6$.
This is periodic stabilization after the central scalar relation; it does
not assert that the four different residue kernels are equal.

More exactly, a set $T$ of positive integer widths detects every
nonzero $P\in k[G]$, in the sense that

$$
 (\forall f\in T,\ \rho_f(P)=0)\ \Longrightarrow\ P=0, \tag{2}
$$

if and only if, for each residue $r$, it contains some
$f\equiv r\pmod4$ with $f\ge L_r$. Thus $6,7,8,9$ suffice,
four widths are necessary, and no test set contained in $1,\ldots,8$
suffices. This improves the predecessor's sufficient two-axis window
$8,9,10,11$ to its least possible common cutoff. It does not improve
its general-axis theorem.

## 2. Fourier fibers and the exact faithfulness criterion

Write a residual as

$$
 P=\sum_{g,c,a_1,a_2,b}\alpha_{g,c,a_1,a_2,b}[gD_q].
$$

At widths congruent to $r$, combine its constant phases by

$$
 \beta_{g,a_1,a_2,b}
   =\sum_{c=0}^3\alpha_{g,c,a_1,a_2,b}i^{rc}.
$$

The unique normal forms $[gD_{0,a_1,a_2,b}]$ form a basis of
$k[G]/I_r$, of dimension $24\cdot32=768$. Equivalently,
$P\in I_r$ exactly when every $\beta$ vanishes. This also follows
by taking the one-coordinate Fourier transform on the central $C_4$.

For $\chi=(u_1,u_2,v)\in(\mathbb Z/4)^2\times\mathbb Z/2$, define

$$
 b_g(\chi)=\sum_{a_1,a_2,b}\beta_{g,a_1,a_2,b}
                  i^{u_1a_1+u_2a_2+2vb}. \tag{3}
$$

The finite Fourier transform is invertible over both fields in question.
Thus all $b_g(\chi)$ vanish exactly when $P\in I_r$. Conversely,
for a fixed $r$, arbitrary values of the 768 quantities $b_g(\chi)$
are realized by an element of this quotient.

Let $\mathbf x\in X^f$ be an ordered input tuple, with multiplicities
$m=(m_{00},m_{10},m_{01},m_{11})$. Its nonconstant phase character is

$$
 \chi_{\mathbf x}=
 (m_{10}+m_{11}\bmod4,\ m_{01}+m_{11}\bmod4,\ m_{11}\bmod2).
 \tag{4}
$$

For any ordered output tuple $\mathbf y$, direct substitution gives

$$
 \langle e_{\mathbf y},\rho_f(P)e_{\mathbf x}\rangle
   =\sum_{g:\,g\mathbf x=\mathbf y}b_g(\chi_{\mathbf x}). \tag{5}
$$

Let $H_{\mathbf x}$ be the pointwise stabilizer of the addresses
appearing in $\mathbf x$. If $\mathbf y=g_0\mathbf x$, the sum in
(5) runs over $g_0H_{\mathbf x}$. If at least three distinct addresses
appear, $H_{\mathbf x}$ is trivial: a permutation of four points
fixing three fixes the fourth. Such a tuple exposes each
$b_{g_0}(\chi_{\mathbf x})$ separately.

If at most two distinct addresses appear, their pointwise stabilizer
contains a transposition of two unused addresses. Consequently

$$
 \sum_{h\in H_{\mathbf x}}\operatorname{sgn}(h)=0. \tag{6}
$$

For example, multiplying the summation set by that transposition pairs
its even and odd members. Suppose a character $\chi_*$ has no
length-$f$ realization using at least three addresses. The nonzero
Fourier assignment

$$
 b_g(\chi)=
 \begin{cases}\operatorname{sgn}(g),&\chi=\chi_*,\\0,&\text{otherwise}
 \end{cases}
$$

then makes every entry (5) zero by (6). It represents a nonzero element
of $k[G]/I_r$. We have proved the **equivalence**

$$
 \ker\rho_f=I_r
 \quad\Longleftrightarrow\quad
 \text{every one of the 32 characters has a length-$f$
 realization using at least three distinct addresses}. \tag{7}
$$

The necessity is essential. Merely improving a construction of an
affinely spanning tuple would establish a sufficient cutoff, not its
optimality. Here necessity follows from the special $S_4$ sign
character; no analogous necessity is asserted for larger axis counts.

## 3. Exact minimum width for each character

Fix $r$ and $\chi=(u_1,u_2,v)$. Let
$h=m_{11}\bmod4$. Equation (4) and the total length residue imply
that $h\in\{v,v+2\}$ and the residue vector of $m$ is

$$
 a(h)=\bigl((r-u_1-u_2+h)\bmod4,
              (u_1-h)\bmod4,
              (u_2-h)\bmod4,h\bigr), \tag{8}
$$

with all four representatives chosen in $\{0,1,2,3\}$. Every
admissible multiplicity vector is uniquely $a(h)+4t$, with
$t\in\mathbb Z_{\ge0}^4$. An initially zero coordinate requires at
least four added copies to become positive. Therefore the exact minimum
length having at least three positive coordinates is

$$
 \ell(r,\chi)=\min_{h\in\{v,v+2\}}
 \left(\sum_j a_j(h)
       +4\max\bigl(0,3-|\{j:a_j(h)>0\}|\bigr)\right). \tag{9}
$$

This bound is attained: raise exactly the needed zero coordinates by
four and leave the others unchanged. All candidate lengths are
congruent to $r$. Adding four copies of address $00$ preserves
the character, residue, and support condition. It follows that for a
positive $f\equiv r$, a spanning realization exists **exactly** when
$f\ge\ell(r,\chi)$. This formula and padding prove an all-width
statement, without extrapolation from a finite census.

## 4. Analytic upper bounds and their sharpness

First take $r=2$. The two vectors in (8) are entrywise partners
$a'=(a+2)\bmod4$. Write $S=\sum_j a_j$; then
$S\in\{2,6,10\}$. If $S=10$, at least three entries are at
least two, since otherwise $S\le3+3+1+1=8$. For
$k=|\{j:a_j\ge2\}|$, the partner sum is
$S'=S+8-4k\le6$. It is congruent to two, so we may replace $a$
by its partner and assume $S=2$ or $6$.

If $S=6$ and the support has at least three entries, it already
gives the desired six-point tuple. Otherwise its only possible pattern
is a permutation of $(3,3,0,0)$; its partner is a permutation of
$(1,1,2,2)$, with sum six and full support. If $S=2$, its
pattern is either $(2,0,0,0)$, whose partner is $(0,2,2,2)$,
or $(1,1,0,0)$, for which adding four to one zero gives sum six
and three positive entries. Thus **every** character has a six-point
spanning realization at residue two.

Adding one, two, or three copies of $00$ changes only the constant
phase character. It gives a realization of every same nonconstant
character at widths seven, eight, or nine, respectively. Four-copy
padding then proves the upper bounds

$$
 \max_\chi\ell(0,\chi)\le8,\quad
 \max_\chi\ell(1,\chi)\le9,\quad
 \max_\chi\ell(2,\chi)\le6,\quad
 \max_\chi\ell(3,\chi)\le7. \tag{10}
$$

For sharpness choose $\chi_0=(0,0,0)$. Its two vectors (8) are
$(r,0,0,0)$ and $((r+2)\bmod4,2,2,2)$. Substituting in (9)
gives the following two candidate lengths and their minima:

| Residue $r$ | Candidate from $h=0$ | Candidate from $h=2$ | $\ell(r,\chi_0)$ |
|---|---:|---:|---:|
| 0 | 12 | 8 | 8 |
| 1 | 9 | 9 | 9 |
| 2 | 10 | 6 | 6 |
| 3 | 11 | 7 | 7 |

These attain all four upper bounds in (10). Equation (7) now proves
(1). In particular residue one still has extra kernel at width five,
so no $F\le5$ can be a common stabilization cutoff, whereas every
width at least six meets its own residue threshold.

## 5. Four explicit residuals and the exact test-set criterion

The necessity witnesses can be given as fixed elements of $k[G]$,
independent of the evaluated width. For a diagonal character
$(r,\chi)=(r,u_1,u_2,v)$, put

$$
 E_{r,\chi}=\frac1{128}\sum_{c,a_1,a_2,b}
       i^{-(rc+u_1a_1+u_2a_2+2vb)}[D_q],\qquad
 A_{\mathrm{sgn}}=\sum_{g\in\operatorname{AGL}(2,2)}
       \operatorname{sgn}(g)[g],
$$

and define $P_r=A_{\mathrm{sgn}}E_{r,\chi_0}$. The diagonal factor
evaluates to the projector onto tuples with total length congruent to
$r$ and nonconstant character $\chi$, by finite Fourier
orthogonality. The order of multiplication is part of this definition:
the phase projector acts on the input before the affine permutation.

Each $P_r$ is nonzero in $k[G]$. In its expansion, each of the
3072 unique normal forms $[gD_q]$ has a nonzero coefficient, a
Gaussian unit times $1/128$. There are no collisions between terms.
At a wrong-residue width its phase projector vanishes. At a
matching-residue width below $L_r$, every surviving tuple uses at
most two addresses, so (6) annihilates it. At every matching-residue
width at least $L_r$, choose a three-address realization of
$\chi_0$; its pointwise stabilizer is trivial, and

$$
 \langle e_{\mathbf x},\rho_f(P_r)e_{\mathbf x}\rangle=1. \tag{11}
$$

Concrete threshold multiplicities, in the address order fixed above,
are $(2,2,2,2)$, $(1,0,4,4)$, $(0,2,2,2)$, and
$(1,2,2,2)$ for $r=0,1,2,3$, respectively. For example,
$P_1$ vanishes at **every** positive width one through eight, but
has the entry (11) equal to one at width nine on the input/output
tuple $(0,2,2,2,2,3,3,3,3)$.

If a test set $T$ contains a threshold-reaching width in every
residue and $\rho_f(P)=0$ on $T$, (1) gives $P\in I_r$
for all four $r$. The four-coordinate Fourier transform in $c$
then forces every $\alpha_{g,c,a_1,a_2,b}=0$. Conversely, if $T$
has no threshold-reaching width in some residue $r$, the fixed
nonzero residual $P_r$ vanishes on every width in $T$. This proves
the necessity and sufficiency in (2), including for arbitrary finite
or infinite sets of positive widths.

## 6. Application boundary, evidence, and attribution

All statements apply entrywise to complete matrices over $k[G]$.
Consequently the predecessor's register-program endpoint interface can
use widths $6,7,8,9$ for this two-axis grammar, provided the same
recipes, scalar coefficients, and program are used at all widths.
Every independent dirty input and every specified returned role must
still be represented in the endpoint matrix; this result does not
license omitting borrowed-role restoration or other outputs. Expansion
of a program into group-algebra entries may be expensive. No new
physical execution or efficient circuit-expansion claim follows.

The executable evidence in this package checks the finite residue and
character arithmetic and the explicit residual witnesses using exact
arithmetic. The all-width conclusion is proved by (5)–(9) and the
padding argument, not by sampling tensor widths. The normal forms,
finite Fourier inversion, and $\operatorname{AGL}(2,2)\cong S_4$
argument are the mathematical interface linking that finite evidence
to the theorem. They are not a proof-kernel certificate or an
independent human acceptance of the result.

Ali Romman's predecessor supplies the native grammar, Fourier-separation
method, four-residue obstruction, general sufficient cutoff, and
register interface, and explicitly asks for the least stabilized width.
Its retained PR #2250 source and notices credit Jose Manuel
(@jmbarrancoml) and Douglas Colkitt; Chris R (@Clear1nsight) retains
credit for the earlier finite-alphabet separation lineage. These inputs
remain unchanged. Classical finite Fourier theory and the alternating
representation of $S_4$ supply the tools used here. The addition is
the exact two-axis criterion (7), sharp multiplicity formula (9), and
its four optimal thresholds and test-set characterization. Mihir's
[adjacent one-axis/general review](https://github.com/CrocSwap/integer-mult-bounds/discussions/5354#discussioncomment-19174027)
explicitly leaves axis counts at least two outside its scope; this
result addresses that distinct two-axis case.

The least cutoff for $n\ge3$, sharper general-axis bounds, and
extensions beyond the monomial grammar remain open here. In particular,
neither the selected nine-axis frontier nor its admitted physical
suppliers, costs, or multiplication exponent are changed by this proof.
